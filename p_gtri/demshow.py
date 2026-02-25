from __future__ import print_function
#from past.builtins import xrange
from p_ggen.py23 import xrange
from PIL import Image
import p_gnum, p_ggen, p_gbmp
from . import demusgs, dembil


def togray(fn, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None, absolute=False):
    "Convert values hmin-hmax integer range 0-255; reserve the first values."
    a, GDAL_NODATA = decipher(fn, GDAL_NODATA)
    if a is None:
        print(GDAL_NODATA)            #GDAL_NODATA has the error message
        return None
#    print "GDAL_nodata=", GDAL_NODATA
    valid = p_gnum.not_equal(a, GDAL_NODATA)
    b = a
    a = None
    if absolute: b = p_gnum.where(valid, abs(b), b)
    if hmax is None: hmax = max(p_gnum.compress(valid.flat, b.flat))
    if hmin is None: hmin = min(p_gnum.compress(valid.flat, b.flat))
    print("hmin=%.3f   hmax=%.3f" % (hmin+0.0, hmax+0.0))
    valid1 = p_gnum.less(b, hmin)
    b = p_gnum.where(p_gnum.logical_and(valid, valid1), hmin, b)
    valid1 = p_gnum.greater(b, hmax)
    b = p_gnum.where(p_gnum.logical_and(valid, valid1), hmax, b)

    reserved = int(255.0*reserve)
    avail = 255.0 - reserved
    s = avail/(hmax-hmin)
    if invert:
        b = p_gnum.where(valid, reserved + avail - (b-hmin)*s, 0)
    else:
        b = p_gnum.where(valid, reserved + (b-hmin)*s, 0)
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
    if im is not None: return p_gnum.im2num(im), GDAL_NODATA
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
