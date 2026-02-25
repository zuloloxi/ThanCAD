"""
21/5/2011
This program reads a USGS DEM (which is stored as .tif file) and writes
it to .syn file.
The USGS DEM file (.tif) is created from the .adf files using the script gdal.py

The explanations for the tif tags were found in:
http://www.awaresystems.be/imaging/tiff/tifftags.html
http://www.awaresystems.be/imaging/tiff/tifftags/gdal_nodata.html

Checking the pixels of the .tif file, the following constant seems to be the
None equivalent:
-340282346638528859811704183484516925440.000
This number also appears as the 42113 tag which is the GDAL_NODATA.
If this tag is absent then there is no "NODATA" value; all pixels have
valid values.

THIS PROGRAM NEEDS MORE TESTING
"""
docusgs = __doc__

from math import hypot, floor, ceil
from PIL import Image
from math import fabs
from p_gmath import thanNear2, thanNearx, linint
import p_ggen, p_gbmp, p_gnum, p_gvarcom
from .dtmvar import ThanDTMDEM
from .deciphererdasdem import decipherErdasAscDem


class ThanDEMusgs(ThanDTMDEM):
    "An object that uses a DEM stored in USGS TIF file to compute elevations."

    def __init__(self, nodatadef=None):
        "Some initial values to make the object variables clear."
        self.nodatadef = nodatadef       #Default nodata value if not set by function prop()
        self.X0, self.Y0 = 0.0, 0.0      #Object coordinates of the upper left pixel of the tif
        self.DX, self.DY = 1.0, 1.0      #Distance x and y between adjacent pixel in object coordinates
        self.nxcols, self.nyrows = 0, 0  #Image size in pixels
        self.GDAL_NODATA = nodatadef     #Special pixel value that means that the pixel has unknown elevation
        self.filnam = ""                 #Pathname of the tif file.
        self.im = None                   #Tif file which stores the DTM
        self.xymma = p_gvarcom.Xymm()    #The coordinates of the lower left and the upper right nodes of the DEM in object coordinates
        self.thanCena = (0.0, 0.0, 0.0)  #Centroid of the DEM in object coordinates


    def clone(self):
        "Make a distinct copy of self."
        d = ThanDEMusgs(nodatadef=self.nodatadef)
        d.X0, d.Y0 = self.X0, self.Y0    #Object coordinates of the upper left pixel of the tif
        d.DX, d.DY = self.DX, self.DY    #Distance x and y between adjacent pixel in object coordinates
        d.nxcols, d.nyrows = self.nxcols, self.nyrows  #Image size in pixels
        d.GDAL_NODATA = self.GDAL_NODATA #Special pixel value that means that the pixel has unknown elevation
        d.filnam = self.filnam           #Pathname of the tif file.
        if self.im is None: d.im = None  #Tif file which stores the DTM
        else:               d.im = self.im.copy()
        d.xymma = p_gvarcom.Xymm()    #The coordinates of the lower left and the upper right nodes of the DEM in object coordinates
        d.xymma.includeXymm(self.xymma)
        d.thanCena = tuple(self.thanCena)  #Centroid of the DEM in object coordinates
        return d


    def thanNew(self, X0, Y0, XB, YB, DX, DY, mode, nodata=None, native=True):
        "Create a new dem which contains no values."
        if nodata is not None: self.GDAL_NODATA = nodata  #if nodata is None, leave the value provided py __init__()
        self.X0 = round(X0/DX) * DX
        self.Y0 = round(Y0/DY) * DY
        self.DX = DX
        self.DY = DY
        if nodata is not None: self.GDAL_NODATA = nodata  #if nodata is None, leave the value provided py __init__()
        #thanPixelCoor() has now enough info to work
        jxa, iya = self.thanPixelCoor((self.X0, self.Y0, 0.0), native=True)    #Up, left point of the window     #Note these are integers
        assert jxa==0 and iya==0
        jxb, iyb = self.thanPixelCoor((XB, YB, 0.0), native=True)              #Down, right point of the window  #Note these are integers
        self.nxcols, self.nyrows = jxb+1, iyb+1
        if self.GDAL_NODATA is None: self.im = Image.new(mode, (self.nxcols, self.nyrows), 0)
        else:                        self.im = Image.new(mode, (self.nxcols, self.nyrows), self.GDAL_NODATA)
        #filnam is the default value ("") set by __init__()
        self.xymma[:] = self.X0, self.Y0-self.DY*(self.nyrows-1), self.X0+self.DX*(self.nxcols-1), self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""


    def thanSet(self, filnam, im=None):
        "Set the tif image which contains the DEM."
        if im is None:
            im, terr = p_gbmp.imageOpen(filnam)
            if im is None: return False, terr
        try:
            self.X0, self.Y0, self.DX, self.DY, self.nxcols, self.nyrows, self.GDAL_NODATA = prop(im, self.nodatadef)
        except ValueError as why:
            return False, why
        self.thanSetFilnam(filnam, force=True)
        self.im = im
        self.xymma[:] = self.X0, self.Y0-self.DY*(self.nyrows-1), self.X0+self.DX*(self.nxcols-1), self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""


    def makeXymm(self, xymm, dx, dy, filnam=""):
        "Make a new dem from a bounding rectangle and approximate steps."
        self.X0, self.Y0 = xymm[0], xymm[3]        #Object coordinates of the upper left pixel of the tif

        self.nxcols = int(round((xymm[2] - xymm[0])/dx)) + 1   #Image size in pixels
        self.nyrows = int(round((xymm[3] - xymm[1])/dy)) + 1   #Image size in pixels
        self.DX = (xymm[2] - xymm[0]) / (self.nxcols-1)   #Distance x and y between adjacent pixel in object coordinates
        self.DY = (xymm[3] - xymm[1]) / (self.nyrows-1)   #Distance x and y between adjacent pixel in object coordinates

        self.GDAL_NODATA = -999999.0              #Special pixel value that means that the pixel has unknown elevation

        self.thanSetFilnam(filnam, force=True)
        self.im = Image.new("F", (self.nxcols, self.nyrows), self.GDAL_NODATA)   #Tif image which stores the DTM
        self.xymma[:] = self.X0, self.Y0-self.DY*(self.nyrows-1), self.X0+self.DX*(self.nxcols-1), self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""


    def thanSetFilnam(self, fn, force=True):
        "Set the file name of the DEM image; if it exists and force=False do not set it."
        if not force and self.filnam != "": return
        self.filnam = fn.strip()
        if self.filnam != "": self.filnam = p_ggen.putSufix(self.filnam, ".tif").abspath()  #Pathname of the tif file.


    def thanGetFilnam(self):
        "Return the name of the file that stores the dem."
        return self.filnam


    def getpixel(self, jx, iy):
        "Return the pixel value"
        return self.im.getpixel((jx, iy))


    def putpixel(self, jx, iy, z):
        "Return the pixel value"
        return self.im.putpixel((jx, iy), z)


    def thanCentroidCompute(self):
        "Compute the centroid of all lines."
        self.thanCena = ((self.xymma[0]+self.xymma[2])*0.5,
                         (self.xymma[1]+self.xymma[3])*0.5,
                         0.0)                               #This is to aid ThanCad

    def thanXymm(self, native=False):
        "Return the min and max x and y coordinates."
        return self.xymma


    def thanCen(self, native=True):
        "Return the coordinates of the centroid."
        return self.thanCena  #Note that this is a tuple


    def thanDxy(self):
        "Return the DX, DY of the dem."
        return self.DX, self.DY


    def than2Num(self, native=False, centroidundulation=True):  #The optional arguments are for compatibility with ThanDEMsrtm.than2Num
        "Return the DEM as a numpy array."
        return p_gnum.im2num(self.im)


    def thanGetSize(self):
        "Return the pixel size of the DEM."
        return self.nxcols, self.nyrows


    def thanSave(self, fn=""):
        "Save the DEM to the tif image file."
        if fn.strip() == "":
            fn = self.filnam
        else:
            fn = p_ggen.putOptSufix(fn, ".tif")
            self.thanSetFilnam(fn, force=False)
        self.im.save(fn)


    def thanPointZ(self, cp, native=False):
        "Calculate the z coordinate of a point with bilinear interpolation."
#        print "usgs: thanPointZ() 1: cp=", cp
        x = (cp[0]-self.X0) / self.DX
        y = (self.Y0-cp[1]) / self.DY
        jx = int(x)
        iy = int(y)
#        print "jx, iy=", jx, iy
        if jx < 0 or iy < 0 or jx >= self.nxcols-1 or iy >= self.nyrows-1: return None
        z00 = self.getpixel(jx, iy)
#        print "z00=", z00
        if z00 == self.GDAL_NODATA: return None
        z10 = self.getpixel(jx+1, iy)
        if z10 == self.GDAL_NODATA: return None
        z01 = self.getpixel(jx, iy+1)
        if z01 == self.GDAL_NODATA: return None
        z11 = self.getpixel(jx+1, iy+1)
        if z11 == self.GDAL_NODATA: return None
        x -= jx
        y -= iy
        z = z00*(1-x)*(1-y) + z10*x*(1-y) + z01*(1-x)*y + z11*x*y
        return z


    def thanPixelCoor(self, cp, native=False):
        "Return the pixel coordinates of the point."
        x = (cp[0]-self.X0) / self.DX
        y = (self.Y0-cp[1]) / self.DY
        jx = floor(x)
        iy = floor(y)
#        print "jx, iy=", jx, iy
        return jx, iy


    def thanObjCoor(self, jx, iy, native=False):
        "Return the object coordinates of a pixel."
        x = self.X0 + jx*self.DX
        y = self.Y0 - iy*self.DY
        z = self.GDAL_NODATA
        return x, y, z


    def iterNodes(self, validnodes=True, invalidnodes=False, xymm=None):
        "Iterate through valid and or invalid nodes of the DEM; xymm is according to ThanCad conventions."
        if xymm is None:
            jx1 = iy1 = 0
            jx2 = self.nxcols
            iy2 = self.nyrows
        else:
            cp = xymm[0], xymm[3], 0.0
            x = (cp[0]-self.X0) / self.DX
            y = (self.Y0-cp[1]) / self.DY
            jx1 = max(int(floor(x)), 0)
            iy1 = max(int(floor(y)), 0)
            cp = xymm[2], xymm[1], 0.0
            x = (cp[0]-self.X0) / self.DX
            y = (self.Y0-cp[1]) / self.DY
            jx2 = min(int(ceil(x)), self.nxcols)
            iy2 = min(int(ceil(y)), self.nyrows)
            #print "demusgs.iterNodes(): xymm = ", xymm
            #print "    ", jx1, iy1
            #print "    ", jx2, iy2
            #print "validnodes, invalidnodes", validnodes, invalidnodes
            #print "GDAL_NODATA=", self.GDAL_NODATA
        for iy in range(iy1, iy2):
            for jx in range(jx1, jx2):
                h = self.getpixel(jx, iy)      #getpixel:  im.getpixel(xy)
                x = self.X0 + jx*self.DX
                y = self.Y0 - iy*self.DY
                if h == self.GDAL_NODATA:
                    if invalidnodes: yield x, y, -10000.0
                else:
                    if validnodes: yield x, y, h


    def tofortran(self, form="f"):
        "Write the DEM in binary format that can be read by a fortran program."
        import struct
        fn = self.filnam.namebase + ".bin"
        #print fn
        fw = open(fn, "wb")
        nodata = self.GDAL_NODATA
        #print "nodata=", nodata
        if nodata is None:
            if   form == "h": nodata = -32768
            elif form == "i": nodata = -2**31
            elif form == "l": nodata = -2**31
            else:             nodata = -340282346638528859811704183484516925440.0  #Hopefully none of the data has this value!
        #print "nodata=", nodata
        dline = struct.pack("=cd", form, nodata)
        #print len(dline)
        fw.write(dline)
        dline = struct.pack("=ll", self.nxcols, self.nyrows)
        #print len(dline)
        fw.write(dline)
        dline = struct.pack("=dddd", self.X0, self.Y0, self.DX, self.DY)
        #print len(dline)
        fw.write(dline)
        jx1 = iy1 = 0
        jx2 = self.nxcols
        iy2 = self.nyrows
        f = "="+str(self.nxcols)+form
        for iy in range(iy1, iy2):
            dline = [self.getpixel(jx, iy) for jx in range(jx1, jx2)]
            dline = struct.pack(f, *dline)
            fw.write(dline)
        fw.close()


    def thanIntersegZ(self, ca, cb, native=False):
        "Compute intersections of segment with DEM lines; don't sort intersections from ca to cb."
        if thanNear2(ca, cb): return ()
        ca = tuple(ca)
        cb = tuple(cb)
        t = [cb[0]-ca[0], cb[1]-ca[1]]
        tt = hypot(t[0], t[1])
        t[0] /= tt
        t[1] /= tt
        cint = []
        rev = False

        DC = self.DX, self.DY
        C0 = self.X0, self.Y0-(self.nyrows-1)*self.DY
        c = [0.0, 0.0, 0.0]
        for i in range(2):
            j = (i+1) % 2
            if ca[i] > cb[i]: ca, cb = cb, ca; rev = not rev
            if ca[i] >= self.xymma[2+i]: return ()
            if cb[i] <= self.xymma[0+i]: return ()
            if not thanNearx(ca[i], cb[i]):
                jx = int((ca[i]-C0[i]) / DC[i])
                c[i] = max((C0[i] + jx * DC[i], self.xymma[0+i]))
                if not thanNearx(c[i], ca[i]):
                    c[i] += DC[i]
                cmax = min((cb[i], self.xymma[2+i]))
                while c[i] <= cmax or thanNearx(c[i], cb[i]):
                    c[j] = linint(ca[i], ca[j], cb[i], cb[j], c[i])
                    c[2] = self.thanPointZ(c, native=True)
                    if c[2] is not None:
                        u = ((c[0]-ca[0])*t[0] + (c[1]-ca[1])*t[1]) / tt
                        if rev: cint.append((1+u, list(c)))      #u is negative distance from cb
                        else:   cint.append((u,   list(c)))
                    c[i] += DC[i]
        return cint


    def exportText(self, fn=""):
        "Export the dem to a text file; fn may be a filename or an opened file object."
        fw = self.openText(fn, "w")
        fw.write("X0, Y0        :  %f  %f\n" % (self.X0, self.Y0))
        fw.write("DX, DY        :  %f  %f\n" % (self.DX, self.DY))
        fw.write("nxcols, nyrows:  %d  %d\n" % (self.nxcols, self.nyrows))
        fw.write("NODATA        :  %f\n" % (self.GDAL_NODATA,))
        for iy in range(self.nyrows):
            for jx in range(self.nxcols):
                z = self.getpixel(jx, iy)
                fw.write(" %f" % (z,))
            fw.write("\n")
        if p_ggen.isString(fn): fw.close()


    def openText(self, fn="", mode="r", suf=".demt"):
        "Open a dem saved in a text file;  fn may be a filename or an opened file object."
        if p_ggen.isString(fn):
            if fn.strip() == "":  #If blank name, put suffix .demt to the self.filnam
                fn = p_ggen.putSufix(self.filnam, suf)
            else:
                fn = p_ggen.putOptSufix(fn, suf)
                self.thanSetFilnam(fn, force=False)       #If self.filnam is blank, set it to fn with prefix .tif
            fw = open(fn, mode)
        else:
            fw = fn
            try: thanSetFilnam(fw.name, force=False)    #fw may not have attribute name
            except: pass
        return fw


    def importText(self, fn=""):
        "Import dem from text file; fn may be a filename or an opened file object."
        fr = self.openText(fn, "r")
        dline = next(fr)
        dl = dline.split(":", 1)
        self.X0, self.Y0 = map(float, dl[1].split())
        dline = next(fr)
        dl = dline.split(":", 1)
        self.DX, self.DY = map(float, dl[1].split())
        dline = next(fr)
        dl = dline.split(":", 1)
        self.nxcols, self.nyrows = map(int, dl[1].split())
        dline = next(fr)
        dl = dline.split(":", 1)
        self.GDAL_NODATA, = map(float, dl[1].split())
        self.xymma[:] = self.X0, self.Y0-self.DY*(self.nyrows-1), self.X0+self.DX*(self.nxcols-1), self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()

        self.im = Image.new("F", (self.nxcols, self.nyrows), self.GDAL_NODATA)   #Tif image which stores the DTM
        for iy in range(self.nyrows):
            dline = next(fr)
            dl = dline.split()
            if len(dl) != self.nxcols: raise ValueError("Line with exactly %d numbers was expected")
            for jx in range(self.nxcols):
                z = float(dl[jx])
                self.putpixel(jx, iy, z)


    def importErdasAsc(self, fn=""):
        "Import dem from an ERDAS ascii file; fn may be a filename or an opened file object."
        fr = self.openText(fn, "rb", ".asc")
        ok, terr = decipherErdasAscDem(fr)
        if not ok: return ok, terr
        X0, Y0, DX, DY, ncols, nrows, GDAL_NODATA = terr
        self.X0, self.Y0 = X0, Y0
        self.DX, self.DY = DX, DY
        self.nxcols, self.nyrows = ncols, nrows
        self.GDAL_NODATA = GDAL_NODATA
        self.xymma[:] = self.X0, self.Y0-self.DY*(self.nyrows-1), self.X0+self.DX*(self.nxcols-1), self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()

        self.im = Image.new("F", (self.nxcols, self.nyrows), self.GDAL_NODATA)   #Tif image which stores the DTM
        fr.seek(0)
        it = iter(fr)
        try:
            for iy in range(nrows):
                for jx in range(ncols):
                    x1,y1,z = map(float, next(it).split())
                    self.putpixel(jx, iy, z)
        except (ValueError, IndexError, StopIteration) as e:
            return False, "Unexpected error while reading ascii Erdas DEM for second time:\n%s" % (dline.rstrip,)
        return True, ""


    def subtract(self, gdem, dxTra=0.0, dyTra=0.0, absdif=True, hminthres=-1e100, prt=p_ggen.doNothing):
        """Subtract the value of gdem from the z-value of every grid point.

        Current DEM is translated by dxTra, dyTra before the comparison. Practically
        we add dxTra and dyTra to all self's grid points."
        hminthres is a threshold value; if any elevation is less than this it is ignored.
        """
        iy1, iy2 = 0, self.nyrows
        jx1, jx2 = 0, self.nxcols
        for iy in range(iy1, iy2):
            prt("%d/%d" % (iy, iy2))
            for jx in range(jx1, jx2):
                h = self.getpixel(jx, iy)      #getpixel:  im.getpixel(xy)
                if h == self.GDAL_NODATA: continue
                if h < hminthres:
                    self.putpixel(jx, iy, self.GDAL_NODATA)
                    continue
                x = self.X0 + jx*self.DX
                y = self.Y0 - iy*self.DY
                x += dxTra
                y += dyTra
                hg = gdem.thanPointZ((x, y, 0.0))
                if hg is None or hg<hminthres:
                    self.putpixel(jx, iy, self.GDAL_NODATA)
                else:
                    #prg("%15.3f%15.3f%15.3f%15.3f" % (x, y, h, h-hg))
                    dh = h - hg
                    if absdif: dh = fabs(dh)
                    self.putpixel(jx, iy, dh)


    def keepInsidePolygons(self, polygIn=[], polygOut=[], native=False, prt=p_ggen.doNothing):
        """Keep points that are inside polygons polygIn AND outside polygons polygOut.

        For the 2015 conferecnce in Cyprus:
            Exploitation of satellite optical and SAR data for public work studies
        Basically, some regions had clouds, while regions near the coast was unreliable
        and we had to exclude them.
        """
        def inside(cp):
            "Return True if point cp is inside polyGin AND outside polygOut."
            for pol in polygOut:
                if pol.inPol(cp): return False
            for pol in polygIn:
                if pol.inPol(cp): return True
            return False
        iy1, iy2 = 0, self.nyrows
        jx1, jx2 = 0, self.nxcols
        for iy in range(iy1, iy2):
            prt("%d/%d" % (iy, iy2))
            for jx in range(jx1, jx2):
                h = self.getpixel(jx, iy)      #getpixel:  im.getpixel(xy)
                if h == self.GDAL_NODATA: continue
                cp = self.X0 + jx*self.DX, self.Y0 - iy*self.DY, 0.0
                #cp = self.geodetGRS802User(cp)
                if inside(cp): continue
                self.putpixel(jx, iy, self.GDAL_NODATA)


    def createFromDem(self, dem, prt=p_ggen.doNothing):
        "Compute the z value of each grid point using another dem."
        iy1, iy2 = 0, self.nyrows
        jx1, jx2 = 0, self.nxcols
        for iy in range(iy1, iy2):
            prt("%d/%d" % (iy, iy2))
            for jx in range(jx1, jx2):
                x = self.X0 + jx*self.DX
                y = self.Y0 - iy*self.DY
                hg = dem.thanPointZ((x, y, 0.0))
                if hg is None:
                    self.putpixel(jx, iy, self.GDAL_NODATA)
                else:
                    self.putpixel(jx, iy, hg)


def prop(im, nodatadef=None):
    """Get image and DEM properties; image must be tif.

    X0, Y0 is the upper left point of the image since it ties: with the pixel coordinates 0,0.
    Thus next pixel should have coordinates X0+DX, Y0+DY, etc."""
    try:
        ijkXYZ = im.tag.get(33922)       #TIFF tag: ModelTiepointTag: *I,J,K,X,Y,Z) * K, K=number of tie points, I,J=pixel location, K=pixel value, X,Y,Z=the coordinates in object space
        DX, DY, DZ = im.tag.get(33550)   #TIFF tag: ModelPixelScaleTag: DX, DY: pixel spacing  DZ: should be zero
        DX+=0.0; DY+=0.0; DZ+=0.0
    except AttributeError as why:
        raise ValueError("Image is probably not tif:\n%s" % (why,))
    except (IndexError, ValueError, TypeError) as why:
        raise ValueError("Probably not a (USGS) DEM or geotiff image:\n%s" % (why,))
    try:
        iy, jx, kz, X0, Y0, Z0 = ijkXYZ
        X0+=0.0; Y0+=0.0; Z0+=0.0
    except (IndexError, ValueError) as why:
        raise ValueError("Only one tie point (6 values which contain the origin) should be defined: %s\n%s" % (ijkXYZ, why))
    if iy != 0.0 or jx != 0.0 or kz != 0.0:
        raise ValueError("Origin in pixels should be 0.0, 0.0, 0.0: iy=%s jx=%s kz=%s" % (iy, jx, kz))
    if DZ != 0.0 or Z0 != 0.0:
        #raise ValueError, "Can not handle nonzero DZ or Z0: %s %s" % (DZ, Z0)
        p_ggen.prg("Can not handle nonzero DZ or Z0: %s %s" % (DZ, Z0), "can1")
    GDAL_NODATA = decipherNodata(im, nodatadef)
    nxcols, nyrows = im.size
    return X0, Y0, DX, DY, nxcols, nyrows, GDAL_NODATA


def decipherNodata(im, nodatadef):
    "Decipher the nodata value."
    temp = im.tag.get(42113)
    print("demusgs prop(): GDAL_NODATA in image=", temp)
    if temp is None: 
        GDAL_NODATA = nodatadef  #Use default value supplied by user, if tag is not found
        print("demusgs prop(): tag not found, using user supplied value GDAL_NODATA=", GDAL_NODATA)
    elif p_ggen.floate(str(temp)) is not None:    #Try to convert to real number
        GDAL_NODATA = p_ggen.floate(str(temp))
        print("demusgs prop(): successfuly converted to GDAL_NODATA=", GDAL_NODATA)
    elif p_ggen.floate(str(temp[0])) is not None: #Try to convert to real number, in case temp is a tuple with one value
        GDAL_NODATA = p_ggen.floate(str(temp[0]))
        print("demusgs prop(): successfuly converted to GDAL_NODATA=", GDAL_NODATA)
    else:
        GDAL_NODATA = nodatadef  #Use default value because we could not convert it to real number
                                 #if nodatadef==None then ALL pixel values are full (all contain valid values) ...
                                 #... else nodatadef is a NODATA value supplied by the user, because it is not supplied by the TIFF file
        print("demusgs prop(): could not convert, using user supplied value GDAL_NODATA=", GDAL_NODATA)

    #If user supplied value is None, or we could not decipher the value in the image
    #then we use the least height, if it is less than 9000
    #Else if the highest height is > 10000 then we use the height height
    if GDAL_NODATA is None:
        print("prop(): Trying to infer GDAL_NODATA..")
        temp = p_gnum.im2num(im)
        tempmin = temp.min()
        if tempmin <= -9000:
            GDAL_NODATA = tempmin
        else:
            tempmax = temp.max()
            if tempmax >= 10000.0: GDAL_NODATA = tempmax
        del temp
        if GDAL_NODATA is not None: print("        GDAL_NODATA set to", GDAL_NODATA)
        else:                       print("        could not infer GDAL_NODATA")
    return GDAL_NODATA
