#Envi IDL emulation library
from math import pi
from PIL import Image
import p_gnum
from p_ggen import Struct
from .ellipsoid import Ellipsoid, _ellipsoid
from .mercator import TMercator, UTMercator, Egsa87
from .lambert import LambertAzimEqualArea


_projection = {  4: "Lambert Azimuthal",
               101: "UTM",
               109: "Transverse Mercator",
               201: "EGSA87",
              }


def map_proj_init(projection, datum=None, keywords="/GCTP", center_longitude=None,
                  false_easting=None, mercator_scale=None, zone=None):
    """Utility function to create a projection object.

    It emulates the interface of IDL.
    """
    if projection not in _projection:
        print("Only the following projections are implemented:")
        for i in sorted(_projection):
            print("%d: %s" % (i, _projection[i]))
            assert 0
    key = getKeywords(keywords, valid="/GCTP /RADIANS")
    assert key.GCTP, "/GCTP keyword must specified in IDLemu"
    if projection == 4:
        pass
    elif projection == 101:
        if datum is None: datum = 8
        assert center_longitude == None, "Please do not specify center_longitude for Universal Transverse Mercator"
        assert false_easting == None, "Please do not specify false_easting for Universal Transverse Mercator"
        assert mercator_scale == None, "Please do not specify mergator_scale for Universal Transverse Mercator"
        if zone is None: zone = 34
        assert datum in _ellipsoid, "Unknown datum=%r" % datum
        assert zone == int(zone) and 1 <= zone <= 60, "Error: illegal zone=%s" % zone
        _, sgor, snor = _ellipsoid[datum]
        eoid = Ellipsoid(sgor, snor)
        return UTMercator(EOID=eoid, zone=zone)
    elif projection == 109:
        if datum is None: datum = 8
        if center_longitude is None: center_logitude = 24.0
        if false_easting is None: false_easting = 500000.0
        if mercator_scale is None: mercator_scale = 0.9996
        assert zone == None, "Please do not define zone for Transverse Mercator"
        assert datum in _ellipsoid, "Unknown datum=%r" % datum
        assert -360.0 <= center_longitude <= 360.0, "Illegal center_longitude=%r" % center_longitude
        if not key.RADIANS: center_longitude *= pi/180.0
        _, sgor, snor = _ellipsoid[datum]
        eoid = Ellipsoid(sgor, snor)
        return TMercator(EOID=eoid, k0=mercator_scale, lam0=center_logitude, falseeasting=false_easting)
    elif projection == 201:
        assert datum == None, "Please do not specify datum for EGSA87"
        assert center_longitude == None, "Please do not specify center_longitude for EGSA87"
        assert false_easting == None, "Please do not specify false_easting for EGSA87"
        assert mercator_scale == None, "Please do not specify mergator_scale for EGSA87"
        assert zone == None, "Please do not specify zone for EGSA87"
        return Egsa87()


def getKeywords(keywords, valid):
    "Create a structure with valid IDL keywords."
    ks = set(keywords.upper().split())
    key = Struct()
    for nam in valid.upper().split():
        if nam in ks:
            ks.remove(nam)
            setattr(key, nam[1:], True)
        else:
            setattr(key, nam[1:], False)
    if len(ks) > 0:
        temp = list(ks)
        temp.insert(0, "The following keyword are unknown or unimplemented:")
        assert 0, " ".join(temp)
    return key


def map_proj_forward(longitude, latitude=None, map_structure=None, keywords=""):
    """Utility function to transform geocentric to geodetic coordinates."

    It emulates the insane interface of IDL.
    """
    key = getKeywords(keywords, valid="/RADIANS")
    assert latitude != None, "longitude=(2,n) array has not yet been implemented"
    if map_structure is None: map_structure = Egsa87()
    en = map_structure.geodet2en
    n = len(longitude)
    cs = p_gnum.zeros((2, n), p_gnum.Float)
    if key.RADIANS: coef = 1.0
    else:           coef = pi/180.0
    for i in range(n):
        cs[0, i], cs[1, i] = en(longitude[i]*coef, latitude[i]*coef)
    return cs


def map_proj_inverse(x, y=None, map_structure=None, keywords=""):
    """Utility function to transform geocentric to geodetic coordinates."

    It emulates the insane interface of IDL.
    """
    key = getKeywords(keywords, valid="/RADIANS")
    assert y != None, "y=(2,n) array has not yet been implemented"
    if map_structure is None: map_structure = Egsa87()
    en = map_structure.en2geodet
    n = len(x)
    cs = p_gnum.zeros((2, n), p_gnum.Float)
    if key.RADIANS: coef = 1.0
    else:           coef = 180.0/pi
    for i in range(n):
        print("inv:", i)
        cs[0, i], cs[1, i] = en(x[i], y[i])
        cs[0, i] *= coef
        cs[1, i] *= coef
        break###################################3
    return cs


def read_tiff(filename, interleave=0, **kw):
    """Utility function to read an image from a tiff file.

    It emulates the insane interface of IDL.
    interleave:
      0:Pixel interleaved: Result will have dimensions [Channels, Columns, Rows].
      1:Scanline (row) interleaved: Result will have dimensions [Columns, Channels, Rows].
      2:Planar interleaved: Result will have dimensions [Columns, Rows, Channels].
      3:Sane interleaved: Result will have dimensions [Rows, Columns, Channels]. Thanasis extension."""
    if len(kw) > 0:
        print("the following keywords are invalid or not yet implemented:")
        for key in sorted(kw): print(key)
        assert 0
    assert 0 <= interleave <= 3, "Error: illegal value of interleav=%r" % interleave
    im = Image.open(filename)
    w, h = im.size                #width=number of columns, height=number of rows
#    print("image:", w, h, im.mode)
    if im.mode == "RGB":
        r = p_gnum.fromstring(im.tostring(), p_gnum.UnsignedInt8)
        r = p_gnum.reshape(r, (h, w, -1))   #reshape needs: a) number of rows. b) number of columns. c) number of channels (bands)
#        print("array shape=", r.shape)
#        print "image pixel=", im.getpixel((5, 6)) #getpixel needs: a) column b) row
#        print("array pixel=", r[6,5,0:3]          #array needs: a) row b) column c) channel (band))
        if interleave == 0:
            r = p_gnum.transpose(r, (2, 1, 0))
        elif interleave == 1:
            r = p_gnum.transpose(r, (1, 2, 0))
        elif interleave == 2:
            r = p_gnum.transpose(r, (1, 0, 2))
        else:
            pass      #already in the form of: p_gnum.transpose(r, (0, 1, 2))
    else:
        if im.mode == "1": im = im.convert("L")
        if im.mode == "L":
            r = p_gnum.fromstring(im.tostring(), p_gnum.UnsignedInt8)
        elif im.mode == "F":
            r = p_gnum.fromstring(im.tostring(), p_gnum.Float32)
        elif im.mode == "l":
            r = p_gnum.fromstring(im.tostring(), p_gnum.Int)
        else:
            assert 0, "Image mode %s is not supported" % im.mode
        r = p_gnum.reshape(r, (h, w))       #reshape needs: a) number of rows. b) number of columns.
#        print("array shape=", g.shape)
#        print "image pixel=", im.getpixel((5, 6))) #getpixel needs: a) column b) row
#        print("array pixel=", g[6,5])              #array needs: a) row b) column
        if interleave == 0:
            r = p_gnum.transpose(r)
        elif interleave == 1:
            r = p_gnum.transpose(r)
        elif interleave == 2:
            r = p_gnum.transpose(r)
        else:
            pass      #already in the form of: p_gnum.transpose(r, (0, 1))
    return r


def size(obj):
    """Return the size and shape of an array or a list.

    Returns a list whose elements are:
    0: number of dimensions (k)
    1: extent of dimension 0
    2: extent of dimension 1
    ...
    k: extent of dimension k-1
    k+1: Type of number that the array holds (0=undefined)
    k+2: Number of all elements in the array
    """
    if hasattr(obj, "shape"):
        s = list(obj.shape)
        n = 1
        for i in s: n *= i
        s.insert(0, len(s))
        s.append(0)
        s.append(n)
        return s
    else:
#       Assume an 1 dimensional list or tuple
        n = len(obj)
        return [1, n, 0, n]


def n_elements(obj):
    "Return the number of elements of the array or list."
    if hasattr(obj, "shape"):
        s = list(obj.shape)
        n = 1
        for i in s: n *= i
        return n
    else:
#       Assume an 1 dimensional list or tuple
        return len(obj)


def fltarr(*dims):
    "Create a floating point array, filled with zeros; /NOZERO has no effect in IDLemu."
    return p_gnum.zeros(dims, p_gnum.Float32)


def dblarr(*dims):
    "Create a double array, filled with zeros; /NOZERO has no effect in IDLemu."
    return p_gnum.zeros(dims, p_gnum.Float)


def round(x, keyword=None):
    "Returns closest integer (which may be long) to x."
    if x < 0.0: return int(x-0.5)
    else:       return int(x+0.5)


def reform(ar, *dims):
    """Changes the shape of an array without changing its elements.

    The '/OVERWRITE' does not work (nor it is necessary in python) in IDLemu."""
    return p_gnum.reshape(ar, dims)


def read_tiff_test():
    read_tiff("and1.jpg")
    read_tiff("and1g.jpg")
    read_tiff("and1b.bmp")


if __name__ == "__main__": read_tiff_test()
