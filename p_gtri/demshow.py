from PIL import Image
import p_gnum, p_ggen, p_gbmp
from . import demusgs, dembil


def file2gray(fn, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None, absolute=False):
    """Convert numpy array values from hmin-hmax to integer range 0-255; reserve the first values."

    Read the array from an image/dem file."""
    a, GDAL_NODATA = decipher(fn, GDAL_NODATA)
    if a is None: return None, None, GDAL_NODATA #GDAL_NODATA has the error message
    return array2gray(a, invert, reserve, GDAL_NODATA, hmin, hmax, absolute)


def array2gray(a, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None, absolute=False):
    "Convert numpy array values from hmin-hmax to integer range 0-255; reserve the first values."
    b, valid, hmin, hmax = demRange(a, GDAL_NODATA, hmin, hmax, absolute)

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


def demRange(a, GDAL_NODATA=-32768, hmin=None, hmax=None, absolute=False):
    "Keep only elevation between hmin and hmax; also ignore nodata values."
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

    b = p_gnum.where(valid, b, 0)
    return b, valid, hmin, hmax


def decipher(fn, nodatadef):
    "Try to guess the DEM."
    if fn.lower().endswith(".bil"):
        dem = dembil.ThanDEMbil(nodatadef)
        ok, terr = dem.thanSet(fn)
        if ok: return dem.than2Num(), dem.GDAL_NODATA
    dem = demusgs.ThanDEMusgs(nodatadef)
    ok, terr = dem.thanSet(fn)
    if ok: return dem.than2Num(), dem.GDAL_NODATA
    im, terr = p_gbmp.imageOpen(fn)
    if im is not None: return p_gnum.im2num(im), nodatadef
    return None, terr


def file2rgb(fn, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None, absolute=False):
    """Convert numpy array values from hmin-hmax to integer range 0-255; reserve the first values; output RGB."

    Read the array from an image/dem file."""
    a, GDAL_NODATA = decipher(fn, GDAL_NODATA)
    if a is None: return None, None, GDAL_NODATA #GDAL_NODATA has the error message
    return array2rgb(a, invert, reserve, GDAL_NODATA, hmin, hmax, absolute)


def array2rgb(a, invert=True, reserve=0.0, GDAL_NODATA=-32768, hmin=None, hmax=None, absolute=False):
    "Convert numpy array values from hmin-hmax to integer range 0-255; reserve the first values; output RGB."
    im, hmin, hmax = array2gray(a, invert, reserve, GDAL_NODATA, hmin, hmax, absolute)
    if im is None: return im, None, hmax   #Error: hmax has the error message
    rgb = [p_ggen.wavelen2rgb(380.0+(780.0-380.0)/255.0*i, 255.0) for i in range(256)]
    rgb[0] = 0, 0, 0
    r = [rgbx[0] for rgbx in rgb]
    g = [rgbx[1] for rgbx in rgb]
    b = [rgbx[2] for rgbx in rgb]
    imr = im.point(r)
    img = im.point(g)
    imb = im.point(b)
    im = Image.merge("RGB", (imr, img, imb))
    return im, hmin, hmax


try:
    from matplotlib import pyplot as plt
    from matplotlib.colors import LightSource
except:
    pass

def array2hillshade(a, GDAL_NODATA=-32768, hmin=None, hmax=None, absolute=False):
    "Show the dem as hill shade view."
    a, hmin, hmax, valid = demRange(a, GDAL_NODATA, hmin, hmax)
    ls = LightSource(azdeg=315, altdeg=45)
    q = ls.hillshade(a, vert_exag=1)
    return normalise256(q), hmin, hmax


def normalise256(q):
    "Normalize to 0-255 and save."
    q *= 256
    q = q.astype('Int8')
    q = q.astype(p_gnum.UnsignedInt8)
    im1 = p_gnum.num2im(q)
    return im1


def array2hill(a, GDAL_NODATA=-32768, hmin=None, hmax=None, absolute=False):
    "Show the dem as hill view."
    a, hmin, hmax, valid = demRange(a, GDAL_NODATA, hmin, hmax, absolute)
    ls = LightSource(azdeg=315, altdeg=45)
    q = ls.shade(a, cmap=plt.cm.gist_earth, vert_exag=1, blend_mode='hsv')
    return normalise256(q), hmin, hmax
