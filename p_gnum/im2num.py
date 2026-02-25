from PIL import Image
from . import numnum

#When the PIL image mode is I;16S it means that the (TIFF) file has the pixels
#as 16 bits Signed integers. Although PIL reads the TIFF tags, its does not
#load the image; it complains that the mode is not recognised.
#A workaround is to explicitly set mode to "I" before loading the image.
#The result is that the image loads, and strangely the getpixel() and the
#tostring() methods now return 32bit signed integer!. These values can
#be converted to numeric arrays as shown in the code below..
#THIS CODE WHICH IS A DIRTY HACK, MUST BE REVISITED EVERY TIME A NEW PIL
#IS RELEASED.
#Please also see imageOpen in p_gbmp


def im2num(im):
    "Convert a PIL image to numeric array."
    w, h = im.size                #width=number of columns, height=number of rows
#    print "image:", w, h, im.mode
    if im.mode == "RGB":
        r = numnum.fromstring(im.tobytes(), numnum.UnsignedInt8)
        r = numnum.reshape(r, (h, w, -1))   #reshape needs: a) number of rows. b) number of columns. c) number of channels (bands) (here automatically -> 3)
#        print "array shape=", r.shape
#        print "image pixel=", im.getpixel((5, 6)) #getpixel needs: a) column b) row
#        print "array pixel=", r[6,5,0:3]          #array needs: a) row b) column c) channel (band)
    else:
        if im.mode == "1": im = im.convert("L")
        if im.mode == "L":
            r = numnum.fromstring(im.tobytes(), numnum.UnsignedInt8)
        elif im.mode == "F":
            r = numnum.fromstring(im.tobytes(), numnum.Float32)
        elif im.mode == "I":
            r = numnum.fromstring(im.tobytes(), numnum.Int32)
        elif im.mode == "I;16S":
            im.mode = "I"
#            r = numnum.fromstring(im.tobytes(), numnum.Int16)
            r = numnum.fromstring(im.tobytes(), numnum.Int32)
            im.mode = "I;16S"
        else:
            raise ValueError("im2num() does not support image mode '%s'" % (im.mode,))
        r = numnum.reshape(r, (h, w))       #reshape needs: a) number of rows. b) number of columns.
#        print "array shape=", g.shape
#        print "image pixel=", im.getpixel((5, 6)) #getpixel needs: a) column b) row
#        print "array pixel=", g[6,5]              #array needs: a) row b) column
    return r


def num2im(r, castint256=True):
    "Convert a 2D o3 3D dimensional (RGB) numeric array to a PIL image."
#    Image.frombytes(mode, size, data)
    n = len(r.shape)
    if n == 3:
        w, h, n = r.shape
        if n < 3: raise ValueError("Array's third dimension should be at least 3 (for RGB images)")
        if n > 3: print("num2im(): Warning: only the first 3 planes of the third dimension will be used (RGB)")
        typ = numnum.typecode(r)
        if r != numnum.UnsignedInt8: r = r.astype(numnum.UnsignedInt8)
        data = r.tostring()
        im = Image.frombytes("RGB", (h, w), data)
    elif n == 2:
        w, h = r.shape
        typ = numnum.typecode(r)
        if typ == numnum.UnsignedInt8:
            data = r.tostring()
            im = Image.frombytes("L", (h, w), data)
        elif typ in (numnum.Int, numnum.Int8, numnum.Int16, numnum.Int32):
            if castint256:
                r = r.astype(numnum.UnsignedInt8)
                data = r.tostring()
                im = Image.frombytes("L", (h, w), data)
            else:
                if typ != numnum.Int32: r = r.astype(numnum.Int32)
                data = r.tostring()
                im = Image.frombytes("I", (h, w), data)
        elif typ in (numnum.Float, numnum.Float32, numnum.Float64):
            if typ != numnum.Float32: r = r.astype(numnum.Float32)
            data = r.tostring()
            im = Image.frombytes("F", (h, w), data)
    else:
        raise ValueError("num2nim() does not support array type '%r'" % (typ,))
    return im
