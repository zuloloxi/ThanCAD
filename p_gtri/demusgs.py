# -*- coding: iso-8859-7 -*-
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
import Image
from p_gmath import thanNear2, thanNearx, linint
import p_ggen, p_gbmp
from dtmvar import ThanDTMDEM, interpolatez


class ThanDEMusgs(ThanDTMDEM):
    "An object that uses a DEM stored in USGS TIF file to compute elevations."

    def __init__(self):
        "Some initial values to make the object variables clear."
        self.X0, self.Y0 = 0.0, 0.0      #Object coordinates of the upper left pixel of the tif
        self.DX, self.DY = 1.0, 1.0      #Distance x and y between adjacent pixel in object coordinates
        self.nxcols, self.nyrows = 0, 0  #Image size in pixels
        self.GDAL_NODATA = None          #Special pixel value that means that the pixel has unknown elevation
        self.filnam = ""                 #Pathname of the tif file.
        self.im = None                   #Tif file which stores the DTM
        self.xymma = (0.0, 0.0, 0.0, 0.0) #The coordinates of the lower left and the upper right nodes of the DEM in object coordinates
        self.thanCena = (0.0, 0.0, 0.0)  #Centroid of the DEM in object coordinates


    def thanSet(self, filnam, im=None):
        "Set the tif image which contains the DEM."
        if im == None:
            im, terr = p_gbmp.imageOpen(filnam)
            if im == None: return False, terr
        try:
            self.X0, self.Y0, self.DX, self.DY, self.nxcols, self.nyrows, self.GDAL_NODATA = prop(im)
        except ValueError, why:
            return False, why
        self.filnam = p_ggen.path(filnam).abspath()
        self.im = im
        self.xymma = self.X0, self.Y0-self.DY*self.nyrows, self.X0+self.DX*self.nxcols, self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""

    def getpixel(self, jx, iy):
        "Return the pixel value"
        return self.im.getpixel((jx, iy))


    def thanCentroidCompute(self):
        "Compute the centroid of all lines."
        self.thanCena = ((self.xymma[0]+self.xymma[2])*0.5,
                         (self.xymma[1]+self.xymma[3])*0.5,
                         0.0)                               #This is to aid ThanCad

    def thanCen(self):
        "Return the coordinates of the centroid."
        return self.thanCena


    def thanXymm(self):
        "Return the min and max x and y coordinates."
        return self.xymma


    def thanDxy(self):
        "Return the DX, DY of the dem."
        return self.DX, self.DY


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


    def iterNodes(self, validnodes=True, invalidnodes=False, xymm=None):
        "Iterate through valid and or invalid nodes of the DEM; xymm is according to ThanCad conventions."
        if xymm == None:
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
            print "demusgs.iterNodes(): xymm = ", xymm
            print "    ", jx1, iy1
            print "    ", jx2, iy2
        k = 0
        for iy in xrange(iy1, iy2):
            for jx in xrange(jx1, jx2):
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
        print fn
        fw = open(fn, "wb")
        nodata = self.GDAL_NODATA
        print "nodata=", nodata
        if nodata == None:
            if   form == "h": nodata = -32768
            elif form == "i": nodata = -2**31
            elif form == "l": nodata = -2**31
            else:             nodata = -340282346638528859811704183484516925440.0  #Hopefully none of the data has this value!
        print "nodata=", nodata
        dline = struct.pack("=cd", form, nodata)
        print len(dline)
        fw.write(dline)
        dline = struct.pack("=ll", self.nxcols, self.nyrows)
        print len(dline)
        fw.write(dline)
        dline = struct.pack("=dddd", self.X0, self.Y0, self.DX, self.DY)
        print len(dline)
        fw.write(dline)
        jx1 = iy1 = 0
        jx2 = self.nxcols
        iy2 = self.nyrows
        f = "="+str(self.nxcols)+form
        for iy in xrange(iy1, iy2):
            dline = [self.getpixel(jx, iy) for jx in xrange(jx1, jx2)]
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
        for i in xrange(2):
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
                    if c[2] != None:
                        u = ((c[0]-ca[0])*t[0] + (c[1]-ca[1])*t[1]) / tt
                        if rev: cint.append((1+u, tuple(c)))      #u is negative distance from cb
                        else:   cint.append((u,   tuple(c)))
                    c[i] += DC[i]
        return cint


def prop(im):
    """Get image and DEM properties; image must be tif.

    X0, Y0 is the upper left point of the image since it "ties: withe pixel coordinatex 0,0.
    Thus next pixel should have coordinates X0+DX, Y0+DY, etc."""
    try:
        ijkXYZ = im.tag.get(33922)       #TIFF tag: ModelTiepointTag: *I,J,K,X,Y,Z) * K, K=number of tie points, I,J=pixel location, K=pixel value, X,Y,Z=the coordinates in object space
        DX, DY, DZ = im.tag.get(33550)   #TIFF tag: ModelPixelScaleTag: DX, DY: pixel spacing  DZ: should be zero
        DX+=0.0; DY+=0.0; DZ+=0.0
    except AttributeError, why:
        raise ValueError, "Image is probably not tif:\n%s" % (why,)
    except (IndexError, ValueError), why:
        raise ValueError, "Probably not a (USGS) DEM or geotiff image:\n%s" % (why,)
    try:
        iy, jx, kz, X0, Y0, Z0 = ijkXYZ
        X0+=0.0; Y0+=0.0; Z0+=0.0
    except (IndexError, ValueError), why:
        raise ValueError, "Only one tie point (6 values which contain the origin) should be defined: %s\n%s" % (ijkXYZ, why)
    if iy != 0.0 or jx != 0.0 or kz != 0.0:
        raise ValueError, "Origin in pixels should be 0.0, 0.0, 0.0: iy=%s jx=%s kz=%s" % (iy, jx, kz)
    if DZ != 0.0 or Z0 != 0.0:
        raise ValueError, "Can not handle nonzero DZ or Z0: %s %s" % (DZ, Z0)
    try:
        GDAL_NODATA = im.tag.get(42113)
        if GDAL_NODATA != None: GDAL_NODATA = float(im.tag.get(42113))
    except (IndexError, ValueError), why:
        GDAL_NODATA = None   #ALL pixel values are full (all contain valid values)
    nxcols, nyrows = im.size
    return X0, Y0, DX, DY, nxcols, nyrows, GDAL_NODATA


def test(im):
    "Play around."
    for key in im.tag.keys():
        print key, im.tag.get(key)
    print im.size
    print self.getpixel(10,20)


def test2(im):
    X0, Y0, DX, DY, nxcols, nyrows, GDAL_NODATA = prop(im)
    print "Parameters:"
    print "X0, Y0=", X0, Y0
    print "DX, DY=", DX, DY
    print "nxcols, nyrows=", nxcols, nyrows
    print "No data=", GDAL_NODATA
    cs = [(X0,           Y0-DY*nyrows),
          (X0+DX*nxcols, Y0-DY*nyrows),
          (X0+DX*nxcols, Y0),
          (X0,           Y0),
         ]
    print "RECTANGLE:"
    for x1, y1 in cs:
        print "%15.3f%15.3f" % (x1, y1)


def test3():
    "Test an existing tif."
    print docusgs
#    fn = "w001001"
    fn = "astgtm2_n38e023_dem.tif"
#    fn = "astgtm2_n38e023_num.tif"
    im, terr = p_gbmp.imageOpen(fn)
    if im == None: assert 0, terr
    dem = ThanDEMusgs()
    ok, ter = dem.thanSet(fn, im)
    if not ok: raise ValueError, ter
    test(im)
    test2(im)
    testAthens(dem)


def testAthens(dem):
    "Test the elevations of ASTER in Athens."
    import p_gearth
    cps = [(23.7,       38.0,       42.0, "Κηφισσός λίγο πιο πάνω από Καβάλας"),
           (23.685,     37.931,      2.0, "Πειραιάς - ΖΕΑ"),
           (23.767886,  37.978815, 148.0, "Σπίτι"),
           (23.7787972, 37.976822, 186.0, "Πολ.Μηχ.ΕΜΠ"),
          ]
    for cp in cps:
        print "λ=%10.5f  φ=%10.5f   %s" % (cp[0], cp[1], cp[-1])
        h = dem.thanPointZ(cp)
        N = p_gearth.egm08Ndyn (cp[0], cp[1])
        if h == None:
            print h, N
        else:
            print "Google: %8.1f  ASTER: %8.1f     N:%.1f" % (cp[2], h, N)


if __name__ == "__main__":
    test3()
