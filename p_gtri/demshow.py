from PIL import Image
import p_gnum, p_ggen, p_gbmp
import demusgs, dembil


def togray(fn, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None):
    "Convert values hmin-hmax integer range 0-255; reserve the first values."
    a, GDAL_NODATA = decipher(fn, GDAL_NODATA)
    if a == None:
        print GDAL_NODATA            #GDAL_NODATA has the error message
        return None
#    print "GDAL_nodata=", GDAL_NODATA
    if hmax == None: hmax = p_gnum.max(a.flat)
    valid = p_gnum.not_equal(a, GDAL_NODATA)
    if hmin == None: hmin = min(p_gnum.compress(valid.flat, a.flat))
    print "hmin=%.3f   hmax=%.3f" % (hmin+0.0, hmax+0.0)
    reserved = int(255.0*reserve)
    avail = 255.0 - reserved
    s = avail/(hmax-hmin)
    if invert:
        b = p_gnum.where(valid, reserved + avail - (a-hmin)*s, 0)
    else:
        b = p_gnum.where(valid, reserved + (a-hmin)*s, 0)
    c = b.astype(p_gnum.UnsignedInt8)
#    print "%r" % (p_gnum.typecode(c),)
    im1 = p_gnum.num2im(c)
    return im1, hmin, hmax


def decipher(fn, GDAL_NODATA):
    "Try to guess the DEM."
    if fn.lower().endswith(".bil"):
        dem = dembil.ThanDEMbil()
        ok, terr = dem.thanSet(fn)
        if ok: return dem.than2Num(), dem.GDAL_NODATA
    dem = demusgs.ThanDEMusgs()
    ok, terr = dem.thanSet(fn)
    if ok: return dem.than2Num(), dem.GDAL_NODATA
    im, terr = p_gbmp.imageOpen(fn)
    if im != None: return p_gnum.im2num(im), GDAL_NODATA
    return None, terr


def torgb(fn, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None):
    "Convert values hmin-hmax integer range 0-255; reserve the first values; output colour code."
    im, hmin, hmax = togray(fn, invert, reserve, GDAL_NODATA, hmin, hmax)
    rgb = [p_ggen.wavelen2rgb(380.0+(780.0-380.0)/255.0*i, 255.0) for i in xrange(256)]
    rgb[0] = 0, 0, 0
    r = [rgbx[0] for rgbx in rgb]
    g = [rgbx[1] for rgbx in rgb]
    b = [rgbx[2] for rgbx in rgb]
    imr = im.point(r)
    img = im.point(g)
    imb = im.point(b)
    im = Image.merge("RGB", (imr, img, imb))
    return im, hmin, hmax


def tograyfile(fn, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None, fnout="q1.bmp"):
    "Convert values hmin-hmax integer range 0-255; reserve the first values; save to file."
    im, hmin, hmax = togray(fn, invert, reserve, GDAL_NODATA, hmin, hmax)
    im.save(fnout)


def torgbfile(fn, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None, fnout="q1.bmp"):
    "Convert values hmin-hmax integer range 0-255; reserve the first values; output colour code; save to file."
    im, hmin, hmax = torgb(fn, invert, reserve, GDAL_NODATA, hmin, hmax)
    im.save(fnout)
