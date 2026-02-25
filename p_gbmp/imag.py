import sys, base64, io
from PIL import Image
try:
    from PIL.Image import DecompressionBombError
except ImportError:
    class DecompressionBombError(Exception): pass    #Support for older versions of PILLOW 

import p_ggen, p_gfil, p_gtkwid
from p_gtkwid import Twid as T

def imageSetmaxpixels(n=None):   #Thanasis2018_04_05
    "Change the default max pixel size (int(1024 * 1024 * 1024 // 4 // 3))."
    if n is None: 
        Image.MAX_IMAGE_PIXELS = int(1024 * 1024 * 1024 // 4 // 3)  #default
    else:
        n = int(n)
        if n >= 1024: Image.MAX_IMAGE_PIXELS = n


def image2Bytes(im, format="jpeg"):
    "Translate image to .jpeg or other format saved in memory file."
#    if im.mode != "RGB":
#        im = im.convert("RGB")
    fw = io.BytesIO()
    im.save(fw, format)
    return fw.getvalue()


def bytes2Image(bytes):
    "Read image from binary bytes."
    fr = io.BytesIO(bytes)
    im = Image.open(fr)
    return im


def writeBytesB64(bytes, fw):
    "Write binary bytes encoded to base64 text."
    t = base64.b64encode(bytes)
    fw.write("<BASE64>\n")
    nl = 80
    for i in xrange(0, len(t), nl):
        fw.write("%s\n" % (t[i:i+nl],))
    fw.write("</BASE64>\n")


def readBytesB64(fr):
    "Read binary bytes encoded as base64 text."
    for dline in fr:
        break
    else:
        raise ValueError("Expected '<BASE64>' but found end of file.")
    dline = dline.strip().upper()
    if dline != "<BASE64>": raise ValueError("Expected '<BASE64>' but found '%s'" % (dline,))
    dlines = []
    for dline in fr:
        dline = dline.strip()
        if dline.upper() == "</BASE64>": break
        dlines.append(dline)
    else:
        raise ValueError("Expected '</BASE64>' but found end of file.")
    return base64.b64decode("".join(dlines))


def imageOpenold(fi):
    "Get an image from a file and report errors."
    try:
        im = Image.open(fi)
        if im.size[0] < 2 or im.size[1] < 2: raise ValueError(T["Image is probably corrupted: size is less than 2 pixels"])
        im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised..
        return im, ""        #..it also slows down the open as it is force to read the image
    except (IOError, ValueError) as e:
        im = None                 #This deletes image if it was half loaded
        return im, str(e)

#When the PIL image mode is I;16S it means that the (TIFF) file has the pixels
#as 16 bits Signed integers. Although PIL reads the TIFF tags, it does not
#load the image; it complains that the mode is not recognised.
#A workaround is to explicitly set mode to "I" before loading the image.
#The result is that the image loads, and strangely the getpixel() and the
#tostring() methods now return 32bit signed integer!.
#THIS CODE WHICH IS A DIRTY HACK, MUST BE REVISITED EVERY TIME A NEW PIL
#IS RELEASED.
#Please also see im2num in p_gnum

def imageOpen(fi):
    "Get an image from a file and report errors."
    try:
        im = Image.open(fi)
        if im.size[0] < 2 or im.size[1] < 2: raise ValueError(T["Image is probably corrupted: size is less than 2 pixels"])
        if im.mode == "I;16S": im.mode = "I"
        im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised..
        return im, ""        #..it will also slow down the open as it is forced to read the image
    except (IOError, ValueError, RuntimeError, DecompressionBombError) as e:
        im = None                 #This deletes image if it was half loaded
        return im, str(e)


def inpImage(mes, initialfile=""):
    "Open an image with PIL."
    while True:
        fn = p_ggen.inpStrB(mes, initialfile)
        im, ter = imageOpen(fn)
        if im is not None: return p_ggen.path(fn), im
        ter = "Error while accessing %s:\n%s\nTry again." % (fn, ter)
        p_ggen.prg(ter, "can1")


def xinpImage(win, mes, initialfile="", initialdir=None):
    "Open an image with PIL."
    if initialdir is None: _, _, initialdir = p_gfil.openfileWinget()
    while True:
        fn = p_gtkwid.thanGudGetReadFile(win, "", mes, initialfile=initialfile, initialdir=initialdir)
        if fn is None: sys.exit()
        im, ter = imageOpen(fn)
        if im is not None: return fn, im
        ter = "Error while accessing %s:\n%s\nTry again." % (fn, ter)
        p_gtkwid.thanGudModalMessage(win, ter, "Open failed", icon=p_gtkwid.ERROR)


def levels(im, imin, imax, gam=1.0):
    "Perform GIMP like levels."
    gam = 1.0/gam
    fact = 255.0 / (imax-imin)
    beta = 255**(1-gam)

    def lev(i):
        if i <= imin: i = imin
        if i >= imax: i = imax
        i = fact * (i-imin)
        i = beta * i**gam
        return int(i)
    return im.point(lev)


from math import pi, cos, sin
def rotateFrame(im, xp, yp, th, resample=Image.NEAREST, invisible=True):
    "rotate PIL image and compute the coordinates of the rotated frame."
    if invisible:
        if im.mode != "RGBA":
            print("Convert to RGBA")
            im = im.convert("RGBA")
    thr = th*pi/180.0
    c = cos(thr); s = sin(thr)
    b, h = im.size
    print(b, h)

    b1 = -b/2
    h1 = -h/2
    b3 = b+b1
    h3 = h+h1
    xx = [b1, b3, b3, b1, b1]
    yy = [h1, h1, h3, h3, h1]
    cr = [(x*c-y*s, x*s+y*c) for x, y in zip(xx, yy)]
    xr, yr = unzip(cr)
    xm = min(xr)
    ym = min(yr)
    assert xm<0 and ym<0
    xr = [x-xm for x in xr]
    yr = [y-ym for y in yr]
    bn = max(xr)
    hn = max(yr)
    imr = im.rotate(th, resample=resample, expand=True)
    print(imr.size)
    print(bn, hn)
    cr = [(xp+(x-xm), yp+hn-(y-ym)) for x, y in cr]
    return imr, cr


def unzip(aa):
    for a in aa:
        break
    else:
        return []
    z = [[x] for x in a]
    for a in aa:
        for i,x in enumerate(a):
           z[i].append(x)
    return z
