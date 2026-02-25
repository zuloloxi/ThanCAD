from math import radians
import io
import p_ggen, p_ggeod
from .pet import pathElementTree


def readKmz(fn, greece=False):
    """Read google Keyhole Markup Language Terrasar data and extract 3d points (placemarks).

    The file is compressed with zip.
    If greece is True then points outside Greece are ignored, and the GRS80
    geodetic coordinates are transformed to EGSA87 grid coordinates."""
    from zipfile import ZipFile
    FILEOFCONTENT = "doc.kml"
    try:
        zr = ZipFile(fn)
    except Exception as e:
        terr = "%s can not be accessed:\n%s" % (fn, e)
        return None, terr
    try:
        files = zr.namelist()
        if FILEOFCONTENT not in files:
            terr = "The '%s' was not found in the compressed file %s:\nThis file may not be a Google kmz file." % (FILEOFCONTENT, fn)
            return None, terr
        co = zr.read(FILEOFCONTENT)
    except Exception as e:
        terr = "The content of zip file %s can not be accessed:\n%s" % (fn, e)
        return None, terr
    if p_ggen.Pyos.Python3:
        co = co.decode(encoding=p_ggen.thanGetEncoding(), errors="replace")
        fr = io.StringIO(co)
    else:
        fr = io.BytesIO(co)
    return readKml(fr, greece=greece)


class NamedPathElementTree(object):
    "A pair of PathElementTree and a path of the attributes 'name' of each element of pe."

    def __init__(self, pe, pathname="", colmap=None):
        "Create the object."
        self.pe = pe
        self.pathname = pathname
        if colmap is None: self.colmap = {}
        else:              self.colmap = colmap.copy()

    def iterFolders(self):
        """Iterate through folders of current folder/document and all subfolders and subdocuments.

        The kml files may contain a document and or many folders. Each folder
        may contain
        a document and or other folders. Each document may contain a document
        and other folders. We are interested in all folders, but not the documents."
        """
        self.colmap.update(readcols(self))
        print ("pe.tag=", self.pe.tag())
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

    def find(self, t):
        "Find child in parent."
        f = self.pe.find(t)
        if f is None: return None
        try: name = f.textr("name")
        except IndexError: name = "(noname)"
        np = "/".join((self.pathname, name))
        nf = NamedPathElementTree(f, np, self.colmap)
        return nf

    def get(self, *args, **kw):
        "Each element may have attributes accessed with dict like methods."
        return self.pe.get(*args, **kw)

    def textr(self, *args, **kw):
        "Find child in parent, and return its text."
        return self.pe.textr(*args, **kw)


def readKml(fn, greece=False):
    """Read google Keyhole Markup Language Terrasar data and extract 3d points and polygons (placemarks).

    fn is a filename or a file object.
    If greece is True then points outside Greece are ignored, and the GRS80
    geodetic coordinates are transformed to EGSA87 grid coordinates."""
    #print("p_gimgeo:readkml entry")
    try:
        root = pathElementTree(file=fn) #may raise xml.parsers.expat.ExpatError if tree not understood by parser..
                                        #.. or xml.etree.ElementTree.ParseError if fn is not XML
    except Exception as e:
        return None, "Error opening file %s:\n%s" % (fn , e)
    nroot = NamedPathElementTree(root)
    fw = []
    try:
        for f in nroot.iterFolders():
            #print("----------------------")
            #print(f.pe.path,': name=', p_ggen.grutf2iso(f.pe.textr("name")))
            #print(f.pe.path, "pathname=", f.pathname)
            for pl in f.findall("Placemark"):
                pp = fromPlacemark1(pl, f.colmap)
                if pp.KMLTYPE == "object":
                    print("p_imgeo.readKml(): placemark {}. Unknown geometry (not Point, Polygon or Path)".format(pp.name))
                    continue
                if pp.name == "":
                    print("p_imgeo.readKml(): {} with no name and description: skipped".format(pp.KLMTYPE))
                    continue
                if greece:
                    if not pp.inGreece(): continue      #Aφαιρεί εκτός ελλάδας
                    pp.toEgsa87()
                fw.append(pp)
    except (ValueError, IndexError) as e:
        return None, "Error while reading %s:\n%s" % (fn, e)
    return fw, ""


def fromPlacemark1(pl, colmap):
    """Return the object that one placemark represents."""
    if   pl.find("Point")      is not None: return KmlPoint.fromPlacemark1(  pl, colmap)
    elif pl.find("Polygon")    is not None: return KmlPolygon.fromPlacemark1(pl, colmap)
    elif pl.find("LineString") is not None: return KmlPath.fromPlacemark1(pl, colmap)
    else:                                   return KmlObject.fromPlacemark1( pl, colmap)


class KmlObject:
    "A KML object; mostly for reading kml files."
    KMLTYPE = "object"
    @staticmethod
    def inGreece1(al, phi):
        "Ensure that one point is in Greece."
        return 20.0 < al < 30.0
#        return 20.0 < al < 25.0      #Aφαιρεί εκτός αττικής

    @staticmethod
    def toEgsa87_1(al, phi):
        "Transform a point to EGSA87 coordinates."
        return p_ggeod.egsa87.geodetGRS802en(radians(al), radians(phi))

    def getPlacemark1Name(self, pl):
        "Get name, description from a placemark."
        try:
            self.name = pl.textr("name")
        except IndexError:
            #print "Name not found for placemark in", p_ggen.grutf2iso(pl.pathname)
            self.name = ""
        try:
            self.desc = pl.textr("description")
        except IndexError:
            print("description not found for placemark:", self.name, "in", pl.pathname)
            self.desc = ""
        self.desc =  self.desc.replace("\n", " ")
        if self.name == "": self.name = self.desc

    def getPlacemark1Atts(self, pl, colmap):
        "Get layer, color from a placemark."
        self.lay = pl.textr("styleUrl")[1:]   #Thanasis2016:12:25  added layer
        col = colmap[self.lay]
        if col == "00000000":
            self.col = None
        else:
            self.col = int(col[6:8], 16), int(col[4:6], 16), int(col[2:4], 16)  #Thanasis2016:12:25  Merry Christmas!

    @staticmethod
    def fromPlacemark1(pl, colmap):
        """Return unknown KML object that one placemark represents."""
        pp = KmlObject()
        pp.getPlacemark1Name(pl)
        return pp


class KmlPoint(KmlObject):
    "A KML point; mostly for reading kml files."
    KMLTYPE = "point"
    @staticmethod
    def fromPlacemark1(pl, colmap):
        """Find coordinates, sec and color of a single placemark representing a point.

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
        assert pl.find("Point") is not None, "p_gimgeo.rk.KPoint.fromPlacemark1(): Placemark does not represent a point"
        p = KmlPoint()
        p.getPlacemark1Name(pl)
        p.getPlacemark1Atts(pl, colmap)
        temp = pl.textr("Point/coordinates")
        p.al, p.phi, p.z = map(float, temp.split(","))
        return p

    def inGreece(self):
        "Ensure that the KmlPoint is in Greece."
        return self.inGreece1(self.al, self.phi)

    def toEgsa87(self):
        "Transform the KmlPoint to EGSA87 coordinates."
        self.al, self.phi = self.toEgsa87_1(self.al, self.phi)


class KmlPolygon(KmlObject):
    "A KML polygon; mostly for reading kml files."
    KMLTYPE = "polygon"
    @staticmethod
    def fromPlacemark1(pl, colmap):
        """Find coordinates, sec and color of a single placemark representing a polygon.
        <Placemark>
                <name>antiparos</name>
                <styleUrl>#m_ylw-pushpin</styleUrl>
                <Polygon>
                        <tessellate>1</tessellate>
                        <outerBoundaryIs>
                                <LinearRing>
                                        <coordinates>
                                                25.00928463995594,36.97946168755059,0 25.09819565299422,36.98037899435099,0 25.09378928978719,37.05062226687215,0 25.00726509350323,37.0512306971082,0 25.00928463995594,36.97946168755059,0
                                        </coordinates>
                                </LinearRing>
                        </outerBoundaryIs>
                </Polygon>
        </Placemark>
        """
        assert pl.find("Polygon") is not None, "p_gimgeo.rk.KmlPolygon.fromPlacemark1(): Placemark does not represent a polygon"
        p = KmlPolygon()
        p.getPlacemark1Name(pl)
        p.getPlacemark1Atts(pl, colmap)
        pols = list(pl.findall("Polygon/outerBoundaryIs/LinearRing"))
        if len(pols) == 0:
            print("p_imgeo.rk.KmlPolygon.fromPlacemark1(): Polygon '{}': no points found".format(self.name))
            return None
        if len(pols) > 1:
            print("p_imgeo.rk.KmlPolygon.fromPlacemark1(): Polygon '{}': more than 1 closed line: only the first is returned".format(self.name))
        coor = pols[0].pe.textr("coordinates")
        #if coor is None:
        #    print("p_imgeo.rk.KmlPolygon.fromPlacemark1(): Polygon '{}': no points found".format(self.name))
        #    return None
        tempall = coor.split()
        n = len(tempall)
        p.al  = [None]*n
        p.phi = [None]*n
        p.z   = [None]*n
        for i, temp in enumerate(tempall):
            p.al[i], p.phi[i], p.z[i] = map(float, temp.split(","))
        return p

    def inGreece(self):
        "Ensure that the KmlPolygon is in Greece."
        for i in range(len(self.al)):
            temp = self.inGreece1(self.al[i], self.phi[i])
            if not temp: return temp
        return True

    def toEgsa87(self):
        "Transform the KmlPolygon to EGSA87 coordinates."
        for i in range(len(self.al)):
            self.al[i], self.phi[i] = self.toEgsa87_1(self.al[i], self.phi[i])


class KmlPath(KmlPolygon):
    "A KML path i.e. a polyline; mostly for reading kml files."
    KMLTYPE = "path"
    @staticmethod
    def fromPlacemark1(pl, colmap):
        """Find coordinates, sec and color of a single placemark representing a polygon.
        <Placemark>
                <name>karpaqos</name>
                <styleUrl>#m_ylw-pushpin</styleUrl>
                <LineString>
                        <tessellate>1</tessellate>
                        <coordinates>
                                27.08287429220152,35.44421391946781,0 27.10164446129506,35.43724830187929,0 27.11613124730121,35.42686648091287,0 27.12559114443431,35.42850279645951,0 27.14221414131202,35.42067003012664,0 27.14619868236142,35.4078351661087,0 27.13666639151091,35.40108378204561,0
                        </coordinates>
                </LineString>
        </Placemark>
        """
        assert pl.find("LineString") is not None, "p_gimgeo.rk.KmlPolygon.fromPlacemark1(): Placemark does not represent a path"
        p = KmlPolygon()
        p.getPlacemark1Name(pl)
        p.getPlacemark1Atts(pl, colmap)
        pols = list(pl.findall("LineString"))
        if len(pols) == 0:
            print("p_imgeo.rk.KmlPath.fromPlacemark1(): Path '{}': no points found".format(self.name))
            return None
        if len(pols) > 1:
            print("p_imgeo.rk.KmlPath.fromPlacemark1(): Path '{}': more than 1 line: only the first is returned".format(self.name))
        coor = pols[0].pe.textr("coordinates")
        #if coor is None:
        #    print("p_imgeo.rk.KmlPolygon.fromPlacemark1(): Polygon '{}': no points found".format(self.name))
        #    return None
        tempall = coor.split()
        n = len(tempall)
        p.al  = [None]*n
        p.phi = [None]*n
        p.z   = [None]*n
        for i, temp in enumerate(tempall):
            p.al[i], p.phi[i], p.z[i] = map(float, temp.split(","))
        return p


def readcols(doc):
        "Find stylemap - color association."
        col = {}
        styles = doc.findall("Style")
#        print "styles"
        for style in styles:
            nam1 = style.get("id")
            try: col1 = style.textr("LabelStyle/color")
            except IndexError: col1 = "00000000"   #No colour defined
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
                raise ValueError("Style name not found")
            nam1 = stylemap.get("id")
            col1 = col[stylenam[1:]]
#            print nam1, stylenam, col1
            colmap[nam1] = col1
        dfn = "default_myplaces_style"     #Default value must exist
        if dfn not in colmap:
            if dfn in col: colmap[dfn] = col[dfn]
            else:          colmap[dfn] = "00000000"   #No colour defined
        return colmap
