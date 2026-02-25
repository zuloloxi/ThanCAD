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


def readKml(fn, greece=False):
    """Read google Keyhole Markup Language Terrasar data and extract 3d points (placemarks).

    fn is a filename or a file object.
    If greece is True then points outside Greece are ignored, and the GRS80
    geodetic coordinates are transformed to EGSA87 grid coordinates."""
    try:
        root = pathElementTree(file=fn) #may raise xml.parsers.expat.ExpatError if tree not understood by parser..
                                        #.. or xml.etree.ElementTree.ParseError if fn is not XML
    except Exception, e:
        raise
        return None, "Error opening file %s:\n%s" % (fn , e)
#    doc = root.find("{http://www.opengis.net/kml/2.2}Document")
    folders = [root]
    fw = []
    while len(folders) > 0:
        f = folders.pop()
        try:
            fs = readxmldoc(f, fw, greece)
        except (ValueError, IndexError), e:
            return None, "Error while reading %s:\%s" % (fn, e)
        folders.extend(fs)
    return fw, ""


def readxmldoc(root, fw, greece=False):
    """Read the placemarks which are under this "doc" entry."""
    doc = root.find("Document")
    if doc == None: return []
    print
    print "======================================================="
    print "name=", doc.textr("name")
    print "name=", root.textr("Document/name")
    colmap = readcols(doc)
    folders = []
    iaa = 0
    for f in iterFolders(doc):
        folders.append(f)
        print "----------------------"
        print f.path, p_ggen.grutf2iso(f.textr("name"))
        for pl in f.findall("Placemark"):
            name, al, phi, z, col, desc = placemark1(pl, colmap)
            if greece:
                if not (20.0 < al < 30.0): continue      #Aφαιρεί εκτός ελλάδας
#                if not (20.0 < al < 25.0): continue      #Aφαιρεί εκτός αττικής
            if greece: x, y = p_ggeod.egsa87.geodetGRS802en(radians(al), radians(phi))
            else:      x, y = radians(al), radians(phi)
            nam = p_ggen.grutf2iso(name)
            desc =  p_ggen.grutf2iso(desc.replace("\n", " "))
            fw.append([nam, x, y, z, col, desc])
    return folders


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
    name = pl.textr("name")
    try:
        desc = pl.textr("description")
    except IndexError:
        print "description not found for placemark:", p_ggen.grutf2iso(name)
        desc = ""
    nam = pl.textr("styleUrl")
    col = colmap[nam[1:]]
    temp = pl.textr("Point/coordinates")
    al, phi, z = map(float, temp.split(","))
    return name, al, phi, z, col, desc


def iterFolders(parent):
    "Iterate recursively all Folder elements."
    folders = parent.findall("Folder")
    for f in folders:
        yield f
    for f in folders:
        for fchild in iterFolders(f):
            yield fchild


def readcols(doc):
        "Find stylemap - color association."
        col = {}
        styles = doc.findall("Style")
        print "styles"
        for style in styles:
            nam1 = style.get("id")
            try: col1 = style.textr("LabelStyle/color")
            except IndexError: col1 = "00000000"
            print nam1, col1
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
        print "stylemaps"
        for stylemap in stylemaps:
            for pair in stylemap.findall("Pair"):
                if pair.textr("key") == "normal":
                    stylenam = pair.textr("styleUrl")
                    break
            else:
                raise ValueError, "Style name not found"
            nam1 = stylemap.get("id")
            col1 = col[stylenam[1:]]
            print nam1, stylenam, col1
            colmap[nam1] = col1
        dfn = "default_myplaces_style"     #Default value must exist
        if dfn not in colmap:
            if dfn in col: colmap[dfn] = col[dfn]
            else:          colmap[dfn] = "00000000"
        return colmap
