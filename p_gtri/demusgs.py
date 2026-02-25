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

from math import hypot
import Image
from p_gmath import thanNear2, thanNearx, linint
import p_ggen
from dtmvar import  ThanDTMDEM, interpolatez


class ThanDEMusgs(ThanDTMDEM):
    "An object that uses a DEM stored in USGS TIF file to compute elevations."

    def __init__(self):
        "Some initial values to make the object variables clear."
        self.X0, self.Y0 = 0.0, 0.0      #Object coordinates of the upper left pixel of the tif
        self.DX, self.DY = 1.0, 1.0      #Distance x and y between adjacent pixel in obejct coordinates
        self.nxcols, self.nyrows = 0, 0  #Image size in pixels
        self.GDAL_NODATA = None          #Special pixel value that means that the pixel has unknown elevation
        self.filnam = ""                 #Pathname of the tif file.
        self.im = None                   #Tif file which stores the DTM
        self.xymm = [0.0, 0.0, 0.0, 0.0] #The coordinates of the lower left and the upper right nodes of the DEM in object coordinates
        self.thanCen = [0.0, 0.0]        #Centroid of the DEM in object coordinates


    def thanSet(self, filnam, im=None):
        "Set the tif image which contains the DEM."
        if im == None:
            try:
                im = Image.open(filnam)
                dxp, dyp = im.size
                if dxp < 2 or dyp < 2: raise ValueError, T["Image is probably corrupted: size is less than 2 pixels"]
                im.crop((0, 0, 2, 2))   #This will trigger decode error (IOError) if image is not recognised (crop() does not alter the image)
            except (IOError, ValueError), why:
                return False, why
        try:
            self.X0, self.Y0, self.DX, self.DY, self.nxcols, self.nyrows, self.GDAL_NODATA = prop(im)
        except ValueError, why:
            return False, why
        self.filnam = p_ggen.path(filnam).abspath()
        self.im = im
        self.xymm = self.X0, self.Y0-self.DY*self.nyrows, self.X0+self.DX*self.nxcols, self.Y0 #WARNING: xymm must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""


    def thanCentroidCompute(self):
        "Compute the centroid of all lines."
        self.thanCen[0] = (self.xymm[0]+self.xymm[2])*0.5
        self.thanCen[1] = (self.xymm[1]+self.xymm[3])*0.5


    def thanPointZ(self, cp):
        "Calculate the z coordinate of a point with bilinear interpolation."
        x = (cp[0]-self.X0) / self.DX
        y = (self.Y0-cp[1]) / self.DY
        jx = int(x)
        iy = int(y)
        if jx < 0 or iy < 0 or jx >= self.nxcols-1 or iy >= self.nyrows-1: return None
        z00 = self.im.getpixel((jx, iy))
        if z00 == self.GDAL_NODATA: return None
        z10 = self.im.getpixel((jx+1, iy))
        if z10 == self.GDAL_NODATA: return None
        z01 = self.im.getpixel((jx, iy+1))
        if z01 == self.GDAL_NODATA: return None
        z11 = self.im.getpixel((jx+1, iy+1))
        if z11 == self.GDAL_NODATA: return None
        x -= jx
        y -= iy
        z = z00*(1-x)*(1-y) + z10*x*(1-y) + z01*(1-x)*y + z11*x*y
        return z


    def iterNodes(self, validnodes=True, invalidnodes=False):
        "Iterate through valid and or invalid nodes of the DEM."
        k = 0
        for iy in xrange(self.nyrows):
            for jx in xrange(self.nxcols):
                h = self.im.getpixel((jx, iy))      #getpixel:  im.getpixl(xy)
                x = self.X0 + jx*self.DX
                y = self.Y0 - iy*self.DY
                if h == self.GDAL_NODATA:
                    if invalidnodes: yield x, y, -10000.0
                else:
                    if validnodes: yield x, y, h


    def thanIntersegZ(self, ca, cb):
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
            if ca[i] >= self.xymm[2+i]: return ()
            if cb[i] <= self.xymm[0+i]: return ()
            if not thanNearx(ca[i], cb[i]):
                jx = int((ca[i]-C0[i]) / DC[i])
                c[i] = max((C0[i] + jx * DC[i], self.xymm[0+i]))
                if not thanNearx(c[i], ca[i]):
                    c[i] += DC[i]
                cmax = min((cb[i], self.xymm[2+i]))
                while c[i] <= cmax or thanNearx(c[i], cb[i]):
                    c[j] = linint(ca[i], ca[j], cb[i], cb[j], c[i])
                    c[2] = self.thanPointZ(c)
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
        raise ValueError, "Image does probably not contain a (USGS) DEM:\n%s" % (why,)
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
        GDAL_NODATA = float(im.tag.get(42113))
    except (IndexError, ValueError), why:
        GDAL_NODATA = None   #ALL pixel values are full (all contain valid values)
    nxcols, nyrows = im.size
    return X0, Y0, DX, DY, nxcols, nyrows, GDAL_NODATA


def tosynold(im, fw, fwn):
    "Write DEM in .syn format."
    X0, Y0, DX, DY, nxcols, nyrows, GDAL_NODATA = prop(im)
#    print X0, Y0, DX, DY, nyrows, nxcols
    k = 0
    nempty = 0
    for iy in xrange(nyrows):
        if iy%100 == 0: print iy, "/", nyrows
        for jx in xrange(nxcols):
            h = im.getpixel((jx, iy))      #getpixel:  im.getpixl(xy)
            k += 1
            if h == GDAL_NODATA:
                nempty += 1
                fwn.write("%-10s%15.3f%15.3f%15.3f\n" % (k, x, y, -10000.0))
                continue
            x = X0 + jx*DX
            y = Y0 - iy*DY
            fw.write("%-10s%15.3f%15.3f%15.3f\n" % (k, x, y, h))
    print nempty, "empty pixels"


def tosyn(dem, fw, validnodes, invalidnodes):
    "Write DEM in .syn format."
    for k, (x, y, h) in enumerate(dem.iterNodes(validnodes, invalidnodes)):
        if k%(dem.nxcols*100) == 0: print k, "/", dem.nxcols*dem.nyrows
        fw.write("%-10s%15.3f%15.3f%15.3f\n" % (k+1, x, y, h))


def test(im):
    "Play around."
    for key in im.tag.keys():
        print key, im.tag.get(key)
    print im.size
    print im.getpixel((10,20))


def test2(im):
    X0, Y0, DX, DY, nxcols, nyrows, GDAL_NODATA = prop(im)
    cs = [(X0,           Y0-DY*nyrows),
          (X0+DX*nxcols, Y0-DY*nyrows),
          (X0+DX*nxcols, Y0),
          (X0,           Y0),
         ]
    print "RECTANGLE:"
    for x1, y1 in cs:
        print "%15.3f%15.3f" % (x1, y1)


if __name__ == "__main__":
    print docusgs
    fn = "w001001"
    im = Image.open(fn+".tif")
    dem = ThanDEMUSGS()
    ok, ter = dem.thanSet(im)
    if not ok: raise ValueError, ter
#    test(im)
#    test2(im)
    fw = open(fn+".syn", "w")
    fwn = open(fn+"nodata.syn", "w")
    tosyn(dem, fw, validnodes=True, invalidnodes=False)
    tosyn(dem, fwn, validnodes=False, invalidnodes=True)
    fw.close()
