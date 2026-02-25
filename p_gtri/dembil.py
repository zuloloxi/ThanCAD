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
import p_ggen
from demusgs import ThanDEMusgs


class ThanDEMbil(ThanDEMusgs):
    "An object that uses a DEM stored in USGS TIF file to compute elevations."

    def thanSet(self, filnam):
        "Set the tif image which contains the DEM."
        if gdal == None:
            return False, "OSGEO GDAL module has not been found"
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
            return False, "Unknown transformation from pixels to bil data units"
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
        self.xymma[:] = self.X0, self.Y0-self.DY*self.nyrows, self.X0+self.DX*self.nxcols, self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""

    def getpixel(self, jx, iy):
        "Return the pixel value"
        return self.im[iy, jx]

    def than2Num(self):
        "Return the DEM as a numpy array."
#        return self.im.transpose()
        return self.im
