# -*- coding: iso-8859-7 -*-
"""
10/2/2013
This program reads an ESPRI .hdr DEM (also known as bil) and makes a ThanDEMusgs
compatible object."""
docusgs = __doc__


#Taken from http://gis.stackexchange.com/questions/29632/raster-how-to-get-elevation-at-lat-long-using-python
from math import fabs
try:
    import osgeo.gdal as gdal
except ImportError:
    gdal = None
import Image
import p_ggen, p_gbmp
from demusgs import ThanDEMusgs


class ThanDEMbil(ThanDEMusgs):
    "An object that uses a DEM stored in USGS TIF file to compute elevations."

    def thanSet(self, filnam):
        "Set the tif image which contains the DEM."
        if gdal == None:
            return False, "OSEGO GDAL module has not been found"
        try: fr = open(filnam, "rb")
        except IOError, why: return False, why
        fr.close()
        dataset = gdal.Open(filnam, gdal.GA_ReadOnly)
        if dataset is None: return False, "Probably the image was not recognised"

        # Get the georeferencing metadata.
        # We don't need to know the CRS unless we want to specify coordinates
        # in a different CRS.
        #projection = dataset.GetProjection()
        geotransform = dataset.GetGeoTransform()
        # We need to know the geographic bounds and resolution of our dataset.
        if geotransform is None:
            return False, "Uknown transformation from pixels to bil data units"
        print "geotransform=", geotransform
        self.X0 = geotransform[0]
        self.DX = fabs(geotransform[1])   #Sign is automatically put in the various formulas
        self.Y0 = geotransform[3]
        self.DY = fabs(geotransform[5])   #Sign is automatically put in the various formulas
        if geotransform[2] != 0.0 or geotransform[4] != 0.0:
            return False, "Affine transformation is not yet supported"

        band = dataset.GetRasterBand(1)
        # We need to nodata value for our MaskedArray later.

        self.GDAL_NODATA = band.GetNoDataValue()
        print "nodata=", self.GDAL_NODATA
        # Load the entire dataset into one numpy array.
        image = band.ReadAsArray(0, 0, band.XSize, band.YSize)
        # Close the dataset.
        dataset = None
        self.nxcols, self.nyrows = band.XSize, band.YSize

        self.filnam = p_ggen.path(filnam).abspath()
        self.im = image
        self.xymma = self.X0, self.Y0-self.DY*self.nyrows, self.X0+self.DX*self.nxcols, self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""

    def getpixel(self, jx, iy):
        "Return the pixel value"
        return self.im[iy, jx]


def testreadbil():
    "PLEASE SEE THE IMPLEMENTATION OF .bil IN p_gtri."
    fn = "n43e005f2dtm.bil"
    bands, b, h = readWv2pBand(fn, typecode1=None)
    print "typecode=", p_gnum.typecode(bands[0])
    print bands, b, h
    gdal_nodata = -10000.0
    import Image, p_gtri
    im = p_gnum.num2im(bands[0], castint256=False)
#    im.save("q1.tif")
#    im = Image.open("q1.tif")
    im.tag = {}
    iy, jx, kz, X0, Y0, Z0 = 0, 0, 0, 0.0, 0.0, 0.0
    im.tag[33922] = iy, jx, kz, X0, Y0, Z0
    DX, DY, DZ = 1.0, 1.0, 0.0
    im.tag[33550] = DX, DY, DZ
#    im.save("q2.tif")
#    im = Image.open("q2.tif")
    print im.tag.get(33922)
    print im.tag.get(33550)
    dem = p_gtri.ThanDEMusgs()
    ok, terr = dem.thanSet(fn, im=im)
    print ok, terr


def test3():
    "Test an existing bil."
    print docusgs
    fn = "n43e005f2dsm.bil"
    dem = ThanDEMbil()
    ok, terr = dem.thanSet(fn)
    print ok, terr
    for jx in xrange(dem.nxcols):
        for iy in xrange(dem.nyrows):
#            assert dem.im[iy, jx] == dem.getpixel(jx, iy)
            h = dem.getpixel(jx, iy)
            if h < -10.0: print jx, iy, h
#            if h > 100.0: print jx, iy, h


if __name__ == "__main__":
#    testreadbil()
    test3()
