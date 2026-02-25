# -*- coding: iso-8859-7 -*-
from math import radians
import cStringIO
import p_ggen, p_ggeod
from pet import pathElementTree


def readKmz(fn, greece=False):
    """Read google Keyhole Markup Language Terrasar data and extract 3d points (placemarks).

    The file is compressed with zip.
    If greece is True then points outside Greece are ignored, and the GRS80
    geodetic coordinates are transformed to EGSA87 grid coordinates."""
    from zipfile import ZipFile
    FILEOFCONTENT = "doc.kml"
    try:
        zr = ZipFile(fn)
    except Exception, e:
        terr = "%s can not be accessed:\n%s" % (fn, e)
        return None, terr
    try:
        files = zr.namelist()
        if FILEOFCONTENT not in files:
            terr = "The '%s' was not found in the compressed file %s:\This file may not be a Google kmz file." % (FILEOFCONTENT, fn)
            return None, terr
        co = zr.read(FILEOFCONTENT)
    except Exception, e:
        terr = "The content of zip file %s can not be accessed:\n%s" % (fn, e)
        return None, terr
    fr = cStringIO.StringIO(co)
    return readKml(fr, greece=greece)


class NamedPathElementTree(object):
    "A pair of PathElementTree and a path of the attributes 'name' of each element of pe."

    def __init__(self, pe, pathname="", colmap=None):
        "Create the object."
        self.pe = pe
        self.pathname = pathname
        if colmap == None: self.colmap = {}
        else:              self.colmap = colmap.copy()

    def iterFolders(self):
        """Iterate through folders of current folder/document and all subfolders and subdocuments.

        The kml files may contain a document and or many folders. Each folder
        may contain
        a document and or other folders. Each document may contain a document
        and other folders. We are interested in all folders, but not the documents."
        """
        self.colmap.update(readcols(self))
        #print "pe.tag=", self.pe.tag()
        if self.pe.tag() == "Folder": yield self
        for f in self.pe.findall("Folder")+self.pe.findall("Document"):
            try: name = f.textr("name")
            except IndexError: name = "(noname)"
            np = "/".join((self.pathname, name))
            nf = NamedPathElementTree(f, np, self.colmap)
            nf.colmap.update(readcols(self))
            for fchild in nf.iterFolders():
                yield fchild

    def findall(self, t):
        "Find all children in parent."
        for f in self.pe.findall(t):
            try: name = f.textr("name")
            except IndexError: name = "(noname)"
            np = "/".join((self.pathname, name))
            nf = NamedPathElementTree(f, np, self.colmap)
            yield nf

    def get(self, *args, **kw):
        "Each element may have attributes accessed with dict like methods."
        return self.pe.get(*args, **kw)

    def textr(self, *args, **kw):
        "Find child in parent, and return its text."
        return self.pe.textr(*args, **kw)


def readKml(fn, greece=False):
    """Read google Keyhole Markup Language Terrasar data and extract 3d points (placemarks).

    fn is a filename or a file object.
    If greece is True then points outside Greece are ignored, and the GRS80
    geodetic coordinates are transformed to EGSA87 grid coordinates."""
    print "p_gimgeo:readkml entry"
    try:
        root = pathElementTree(file=fn) #may raise xml.parsers.expat.ExpatError if tree not understood by parser..
                                        #.. or xml.etree.ElementTree.ParseError if fn is not XML
    except Exception, e:
        return None, "Error opening file %s:\n%s" % (fn , e)
    nroot = NamedPathElementTree(root)
    fw = []
    try:
        for f in nroot.iterFolders():
            print "----------------------"
            print f.pe.path,': name=', p_ggen.grutf2iso(f.pe.textr("name"))
            print f.pe.path, "pathname=", f.pathname
            for pl in f.findall("Placemark"):
                name, al, phi, z, col, desc = placemark1(pl, f.colmap)
                print "p_gimgeo:readkml:", name, al, phi, z
                if name == None: continue
                if greece:
                    if not (20.0 < al < 30.0): continue      #Aφαιρεί εκτός ελλάδας
#                    if not (20.0 < al < 25.0): continue      #Aφαιρεί εκτός αττικής
                if greece: x, y = p_ggeod.egsa87.geodetGRS802en(radians(al), radians(phi))
                else:      x, y = radians(al), radians(phi)
                nam = p_ggen.grutf2iso(name)
                desc =  p_ggen.grutf2iso(desc.replace("\n", " "))
                fw.append([nam, x, y, z, col, desc])
    except (ValueError, IndexError), e:
        raise
        return None, "Error while reading %s:\%s" % (fn, e)
    return fw, ""


def placemark1(pl, colmap):
    """Find coordinates, sec and color of a single placemark.

        <Placemark>
            <name>Άγιος Στέφανος</name>
            <description>Άγιος Στέφανος
Ηρώων Πολυτεχνείου 11 (πλησίον Αστυνομικού Τμήματος)
210 8140177</description>
            <LookAt>
                <longitude>23.85746599958304</longitude>
                <latitude>38.13810400263024</latitude>
                <altitude>0</altitude>
                <heading>-5.855528390761592e-010</heading>
                <tilt>44.9997370490409</tilt>
                <range>983.6913257101868</range>
                <gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
            </LookAt>
            <styleUrl>#msn_ylw-pushpin0</styleUrl>
            <Point>
                <coordinates>23.85746599958305,38.13810400263024,0</coordinates>
            </Point>
        </Placemark>
    """
    try:
        name = pl.textr("name")
    except IndexError:
        #print "Name not found for placemark in", p_ggen.grutf2iso(pl.pathname)
        name = ""
    try:
        desc = pl.textr("description")
    except IndexError:
        #print "description not found for placemark:", p_ggen.grutf2iso(name), "in", p_ggen.grutf2iso(pl.pathname)
        desc = ""
    if name == "":
        if desc == "":
            #print "No name and description for placemark in:", p_ggen.grutf2iso(pl.pathname), ": skipped"
            return None, None, None, None, None, None
        name = desc
    nam = pl.textr("styleUrl")
    col = colmap[nam[1:]]
    temp = pl.textr("Point/coordinates")
    al, phi, z = map(float, temp.split(","))
    return name, al, phi, z, col, desc


def readcols(doc):
        "Find stylemap - color association."
        col = {}
        styles = doc.findall("Style")
#        print "styles"
        for style in styles:
            nam1 = style.get("id")
            try: col1 = style.textr("LabelStyle/color")
            except IndexError: col1 = "00000000"
#            print nam1, col1
            col[nam1] = col1
        """
    <StyleMap id="msn_ylw-pushpin2">
        <Pair>
            <key>normal</key>
            <styleUrl>#sn_ylw-pushpin3</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#sh_ylw-pushpin2</styleUrl>
        </Pair>
    </StyleMap>
        """
        colmap = col.copy()     #The styles may also be used as stylemaps
        stylemaps = doc.findall("StyleMap")
#        print "stylemaps"
        for stylemap in stylemaps:
            for pair in stylemap.findall("Pair"):
                if pair.textr("key") == "normal":
                    stylenam = pair.textr("styleUrl")
                    break
            else:
                raise ValueError, "Style name not found"
            nam1 = stylemap.get("id")
            col1 = col[stylenam[1:]]
#            print nam1, stylenam, col1
            colmap[nam1] = col1
        dfn = "default_myplaces_style"     #Default value must exist
        if dfn not in colmap:
            if dfn in col: colmap[dfn] = col[dfn]
            else:          colmap[dfn] = "00000000"
        return colmap
