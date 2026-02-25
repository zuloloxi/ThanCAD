import p_ggen, p_gnum
prg = p_ggen.prg
try:
    from osgeo import gdal, gdalconst, gdal_array as gdalnumeric
except ImportError:
    def isOsgeoLoaded(): return False, "OSGEO/GDAL library was not found/loaded or numpy version is older than required.\nPlease install OSGEO python bindings or newer numpy and and retry."
    def readWv2pBand(infile, typecode1): import osgeo     #Trigger ImportError only when a function is called
    def readWv2mBands(infile): import osgeo     #Trigger ImportError only when a function is called
    def readQb2mBands(infile): import osgeo     #Trigger ImportError only when a function is called
    def readTerrasarBand(infile, typecode1=p_gnum.Complex64): import osgeo     #Trigger ImportError only when a function is called
    def extract1Band(indataset, i, name): import osgeo     #Trigger ImportError only when a function is called
    def convertCol16to8(band, col1, col2): import osgeo     #Trigger ImportError only when a function is called
    def convertComplex2Int16(prev): import osgeo     #Trigger ImportError only when a function is called
    def writeBands(band, size, fnim): import osgeo     #Trigger ImportError only when a function is called
else:
    def isOsgeoLoaded(): return True, ""
    def readWv2pBand(infile, typecode1=p_gnum.UnsignedInt16):
        "Read the gray band of a Worldview 2 panchromatic image and return it as numarray."
        indataset = gdal.Open(infile, gdalconst.GA_ReadOnly)
        print("indataset=", indataset)
        if indataset is None:
            terr = 'Cannot open %s' % (infile,)
            return None, None, terr
        ba, ar, terr = extract1Band(indataset, 1, "gray", typecode1)
        if ba is None:
            terr = "%s:\nProbably not a panchromatic WorldView Image" % (terr,)
            return None, None, terr
        return [ar], (ba.XSize, ba.YSize), ""


    def readWv2mBands(infile):
        "Read the red, green, blue bands of Worldview 2 multispectral image and return them as numarrays."
        indataset = gdal.Open(infile, gdalconst.GA_ReadOnly)
        if indataset is None:
            terr = 'Cannot open %s' % (infile,)
            return None, None, terr
        band = []
        for i,name in (5, "red"), (3, "green"), (2, "blue"):
            ba, ar, terr = extract1Band(indataset, i, name)
            if ba is None:
                terr = "%s:\nProbably not a multispectral WorldView Image"
                return None, None, terr
            band.append(ar)
        return band, (ba.XSize, ba.YSize), ""


    def readQb2mBands(infile):
        "Read the red, green, blue bands of Quick Bird2 2 multispectral image and return them as numarrays."
        indataset = gdal.Open(infile, gdalconst.GA_ReadOnly)
        if indataset is None:
            terr = 'Cannot open %s' % (infile,)
            return None, None, terr
        band = []
        for i,name in (1, "red"), (2, "green"), (3, "blue"):
            ba, ar, terr = extract1Band(indataset, i, name)
            if ba is None:
                terr = "%s:\nProbably not a multispectral WorldView Image"
                return None, None, terr
            band.append(ar)
        return band, (ba.XSize, ba.YSize), ""


    def readTerrasarBand(infile, typecode1=p_gnum.Complex64):
        "Read the gray band of a Worldview 2 panchromatic image and return it as numarray."
        indataset = gdal.Open(infile, gdalconst.GA_ReadOnly)
        print("indataset=", indataset)
        if indataset is None:
            terr = 'Cannot open %s' % (infile,)
            return None, None, terr
        ba, ar, terr = extract1Band(indataset, 1, "complex gray", typecode1)
        if ba is None:
            terr = "%s:\nProbably not a TerraSAR Image" % (terr,)
            return None, None, terr
        return [ar], (ba.XSize, ba.YSize), ""


    def extract1Band(indataset, i, name, typecode1=None):
        "Extract 1 band from a GDAL image object."
#        prg("Extracting band %d (%s)" % (i, name))
        ba = indataset.GetRasterBand(i)
        if ba is None:
            terr = 'Cannot load band number %d (%s)' % (i, name)
            return None, None, terr
#       prg("%s size= %d  %d" % (name, ba.XSize, ba.YSize))
        ar = ba.ReadAsArray(0, 0, ba.XSize, ba.YSize)
        if typecode1 is not None:
            if p_gnum.typecode(ar) != typecode1:
                terr = 'Band number %d (%s) data is not %r' % (i, name, typecode1)
                return None, None, terr
        return ba, ar, ""


    def convertCol16to8(band, col1, col2):
        "Change 16bit colour to 8bit colour."
#        type1 = GDT_Int16
        type1 = gdalconst.GDT_Byte
        numtype1 = gdalnumeric.GDALTypeCodeToNumericTypeCode(type1)
        col12 = 255.0/(col2-col1)
        col1 = p_gnum.uint16(col1)
        col2 = p_gnum.uint16(col2)
        for i,ar in enumerate(band):
            band[i] = None             #In order not to leave an additional copy (not needed any more but leave it for documentation)
            ar[:] = p_gnum.where(ar<col1, col1, ar)
            ar[:] = p_gnum.where(ar>col2, col2, ar)
#            ar = numtype1((ar-col1)*col12)
            ar -= col1
            #ar *= col12    #This does NOT convert the array to float; it remains uint16
            import numpy                                        #Thanasis2016_04_03:work around for previous line(http://docs.scipy.org/doc/numpy-dev/release.html):
            numpy.multiply(ar, col12, out=ar, casting='unsafe') #the numpy *= operator has casting='same_kind' and does not work
            ar = ar.astype(numtype1)  #, casting="unsafe")  #Thanasis2016_04_03
            band[i] = ar


    def convertComplex2Int16(prev):
        "Convert an Complex64 array to Unsigned integer array."
        icc, jcc = 1598, 12069
        icc, jcc = 598, 2069
        print(prev[10, 0], prev[icc, jcc], p_gnum.typecode(prev))
        xx = p_gnum.absolute(prev)
        print(xx[10, 0], xx[icc, jcc], p_gnum.typecode(xx))
        xx += 0.5
        print(xx[10, 0], xx[icc, jcc], p_gnum.typecode(xx))
        type1 = gdalconst.GDT_UInt16
        numtype1 = gdalnumeric.GDALTypeCodeToNumericTypeCode(type1)
        print("Numpy closest type to gdalconst.GDT_UInt16 =", numtype1)
        ii = xx.astype(numtype1)
        print(ii[10,0], ii[icc, jcc], p_gnum.typecode(ii))
        return ii


    def writeBands(band, size, fnim, type1=gdalconst.GDT_Byte):
        "Write bands to a geotiff file."
#        type1 = gdalnumeric.GDALNumericTypeCodeToTypeCode(band[0].dtype)
#        type1 = gdalconst.GDT_Byte
        out_driver = gdal.GetDriverByName("GTiff")
        outdataset = out_driver.Create(fnim, size[0], size[1], len(band), type1)
        for i,ar in enumerate(band):
            outband = outdataset.GetRasterBand(i+1)
            outband.WriteArray(ar, 0, 0)
        outdataset.FlushCache()


def mapOutputLevels(ar, col1, col2):
    "Map 0-255 input levels to col1-col2 output levels."
    assert 0 <= col1 <= 255
    assert 0 <= col2 <= 255
    col12 = (col2-col1)/255.0
    col1 = p_gnum.uint8(col1)
    col2 = p_gnum.uint8(col2)
#    ar = col1+p_gnum.uint8(ar*col12)
    ar *= col12
    ar += col1
    print("oulev:", ar.dtype)
    return ar


def mapInputLevels(ar, imin, imax, gam=1.0):
    "Perform GIMP like input levels."
    assert 0 <= imin <= 255
    assert 0 <= imax <= 255
    gam = 1.0/gam
    fact = 255.0 / (imax-imin)
    #beta = 255.0**(1.0-gam)
    imin = p_gnum.uint8(imin)
    imax = p_gnum.uint8(imax)
    ar[:] = p_gnum.where(ar<imin, imin, ar)
    ar[:] = p_gnum.where(ar>imax, imax, ar)
#    ar = p_gnum.uint8(beta * (fact*(ar-imin))**gam)
    ar -= imin
    if fact != 1.0: ar **= gam
    ar *= fact
    print("inplev:", ar.dtype)
    return ar


def testHistogram():
    "Test the histogram and the conversion from 16bits to 8bits."
    fnim = "10JAN15101825-M2AS_R2C2-052299009030_01_P001.TIF"
    band, size, terr = readWv2mBands(fnim)
    print(terr)
    print("type(band[0])=", band[0].dtype)
    h, _ = p_gnum.histogram(band[0], 4096, (0, 4096))
    print("len(histogram)=", len(h))
    with open("q1", "w") as fw:
        for i in range(4096):
            fw.write("%d:  %d\n" % (i, h[i]))
    convertCol16to8(band, 150, 600)
    print("type(band[0])=", band[0].dtype)
    h, _ = p_gnum.histogram(band[0], 256, (0, 256))
    print("len(histogram)=", len(h))
    with open("q2", "w") as fw:
        for i in range(256):
            fw.write("%d:  %d\n" % (i, h[i]))
