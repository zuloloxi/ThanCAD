import Image
import numnum


def im2num(im):
    "Convert a PIL image to numeric array."
    w, h = im.size                #width=number of columns, height=number of rows
#    print "image:", w, h, im.mode
    if im.mode == "RGB":
        r = numnum.fromstring(im.tostring(), numnum.UnsignedInt8)
        r = numnum.reshape(r, (h, w, -1))   #reshape needs: a) number of rows. b) number of columns. c) number of channels (bands) (here automatically -> 3)
#        print "array shape=", r.shape
#        print "image pixel=", im.getpixel((5, 6)) #getpixel needs: a) column b) row
#        print "array pixel=", r[6,5,0:3]          #array needs: a) row b) column c) channel (band)
    else:
        if im.mode == "1": im = im.convert("L")
        if im.mode == "L":
            r = numnum.fromstring(im.tostring(), numnum.UnsignedInt8)
        elif im.mode == "F":
            r = numnum.fromstring(im.tostring(), numnum.Float32)
        elif im.mode == "I":
            r = numnum.fromstring(im.tostring(), numnum.Int)
        else:
            raise ValueError, "im2num() does not support image mode '%s'" % (im.mode,)
        r = numnum.reshape(r, (h, w))       #reshape needs: a) number of rows. b) number of columns.
#        print "array shape=", g.shape
#        print "image pixel=", im.getpixel((5, 6)) #getpixel needs: a) column b) row
#        print "array pixel=", g[6,5]              #array needs: a) row b) column
    return r


def num2im(r, castint256=True):
    "Convert a 2D o3 3D dimensional (RGB) numeric array to a PIL image."
#    Image.fromstring(mode, size, data)
    n = len(r.shape)
    if n == 3:
        w, h, n = r.shape
        if n != 3: raise ValueError, "Array's third dimension should be exactly 3 (for RGB images)"
        typ = numnum.typecode(r)
        if r != numnum.UnsignedInt8: r = r.astype(numnum.UnsignedInt8)
        data = r.tostring()
        im = Image.fromstring("RGB", (h, w), data)
    elif n == 2:
        w, h = r.shape
        typ = numnum.typecode(r)
        if typ == numnum.UnsignedInt8:
            data = r.tostring()
            im = Image.fromstring("L", (h, w), data)
        elif typ in (numnum.Int, numnum.Int8, numnum.Int16, numnum.Int32):
            if castint256:
                r = r.astype(numnum.UnsginedInt8)
                data = r.tostring()
                im = Image.fromstring("L", (h, w), data)
            else:
                if typ != numnum.Int32: r = r.astype(numnum.Int32)
                data = r.tostring()
                im = Image.fromstring("I", (h, w), data)
        elif typ in (numnum.Float, numnum.Float32, numnum.Float64):
            if typ != numnum.Float32: r = r.astype(numnum.Float32)
            data = r.tostring()
            im = Image.fromstring("F", (h, w), data)
    else:
        raise ValueError, "num2nim() does not support array type '%r'" % (typ,)
    return im
