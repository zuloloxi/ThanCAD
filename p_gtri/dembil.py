"""
10/2/2013
This module reads an ESPRI .hdr DEM (also known as bil) and makes a ThanDEMusgs
compatible object.
1/5/2015
This module can also read the Erdas Imagine .img format.
The ktimatologio DEM (LSO) and DSM (VLSO) digital elevation models
come with this format. It seems that ktimatologio DEM/DSM do not define
NODATA values. It also seems that all the elevation on the sea are zero.
So it mighty be a good idea to set the NODATA value to zero (0.0) if
GetNoDataValue() return None.
"""
docusgs = __doc__


#Taken from http://gis.stackexchange.com/questions/29632/raster-how-to-get-elevation-at-lat-long-using-python
from math import fabs
try:
    import osgeo.gdal as gdal
except ImportError:
    gdal = None
import p_ggen, p_gnum
from .demusgs import ThanDEMusgs
from .demsrtm import ThanDEMsrtm


class ThanDEMbil(ThanDEMusgs):
    "An object that uses a DEM stored in USGS TIF file to compute elevations."

    def thanSet(self, filnam):
        "Set the tif image which contains the DEM."
        if gdal is None:
            return False, "OSGEO GDAL module has not been found"
        try: fr = open(filnam, "rb")
        except IOError as why: return False, why
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
        print("geotransform=", geotransform)
        self.X0 = geotransform[0]
        self.DX = fabs(geotransform[1])   #Sign is automatically put in the various formulas
        self.Y0 = geotransform[3]
        self.DY = fabs(geotransform[5])   #Sign is automatically put in the various formulas
        if geotransform[2] != 0.0 or geotransform[4] != 0.0:
            return False, "Affine transformation is not yet supported"

        band = dataset.GetRasterBand(1)
        # We need to nodata value for our MaskedArray later.
        self.GDAL_NODATA = decipherNodata(band, self.nodatadef)
        # Load the entire dataset into one numpy array.
        image = band.ReadAsArray(0, 0, band.XSize, band.YSize)
        # Close the dataset.
        dataset = None
        self.nxcols, self.nyrows = band.XSize, band.YSize

        self.filnam = p_ggen.path(filnam).abspath()
        #self.im = image
        self.im = p_gnum.num2im(image)  #Thanasis2018_10_06
        self.xymma[:] = self.X0, self.Y0-self.DY*self.nyrows, self.X0+self.DX*self.nxcols, self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""

    def getpixelxx(self, jx, iy):     #Thanasis2018_10_06
        "Return the pixel value"
        return self.im[iy, jx]

    def than2Numxx(self):     #Thanasis2018_10_06
        "Return the DEM as a numpy array."
#        return self.im.transpose()
        return self.im


class ThanDEMbilc(ThanDEMsrtm):
    "An object that uses a DEM stored in USGS TIF file to compute elevations and has conversion capabilities."

    def thanSet(self, filnam, im=None, user2geodetGRS80=None, geodetGRS802User=None):
        "Set the tif image which contains the DEM."
        if user2geodetGRS80 is not None: self.user2geodetGRS80 = user2geodetGRS80
        if geodetGRS802User is not None: self.geodetGRS802User = geodetGRS802User
        return self.thanSet2(filnam, im)


    def thanSet2(self, filnam, im=None):
        "Set the tif image which contains the DEM."
        if gdal is None:
            return False, "OSGEO GDAL module has not been found"
        try: fr = open(filnam, "rb")
        except IOError as why: return False, why
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
        print("geotransform=", geotransform)
        self.X0 = geotransform[0]
        self.DX = fabs(geotransform[1])   #Sign is automatically put in the various formulas
        self.Y0 = geotransform[3]
        self.DY = fabs(geotransform[5])   #Sign is automatically put in the various formulas
        if geotransform[2] != 0.0 or geotransform[4] != 0.0:
            return False, "Affine transformation is not yet supported"

        band = dataset.GetRasterBand(1)
        # We need to nodata value for our MaskedArray later.
        self.GDAL_NODATA = decipherNodata(band, self.nodatadef)
        # Load the entire dataset into one numpy array.
        image = band.ReadAsArray(0, 0, band.XSize, band.YSize)
        # Close the dataset.
        dataset = None
        self.nxcols, self.nyrows = band.XSize, band.YSize

        self.filnam = p_ggen.path(filnam).abspath()
        #self.im = image
        self.im = p_gnum.num2im(image)  #Thanasis2018_10_06
        self.xymma[:] = self.X0, self.Y0-self.DY*self.nyrows, self.X0+self.DX*self.nxcols, self.Y0 #WARNING: xymma must be valid node coordinates
        self.thanCentroidCompute()
        return True, ""



    def getpixelxx(self, jx, iy):     #Thanasis2018_10_06
        "Return the pixel value"
        return self.im[iy, jx]

    def than2Numxx(self):             #Thanasis2018_10_06
        "Return the DEM as a numpy array."
#        return self.im.transpose()
        return self.im


def decipherNodata(band, nodatadef):
    "Try to find the no data value."
    GDAL_NODATA = band.GetNoDataValue()
    print("ThanDEMbilx.thanSet2(): GDAL_NODATA in image=", GDAL_NODATA)
    if GDAL_NODATA is None:
        GDAL_NODATA = nodatadef  #Use default value supplied by user, if tag is not found
        print("ThanDEMbilc.thanSet2(): tag not found, using user supplied value GDAL_NODATA=", GDAL_NODATA)
    return GDAL_NODATA
