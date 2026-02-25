import tkinter
from PIL import Image, ImageTk
from math import hypot, fabs
from .thansymbol import thanPoints


##############################################################################
##############################################################################

class ThanChart:
    "Represents a chart which is drawn on a canvas object."

#=============================================================================

    def __init__(self, title="Chart"):
        "Initialise chart."
        self.curves = []
        self.wx = self.wy = 0
        self.title = title

#=============================================================================

    def curveAdd(self, x, y, color="red", fill=None, style="continuous", width=1, size=6):
        "Adds a new curve to the chart."
        if len(x) != len(y): raise ValueError("Curve with len(x) != len(y)")
        if len(x) == 0:
            print("Empty curve is ignored.")
            return
        self.curves.append((x[:], y[:], color, fill, style, width, size))
#        self.minmax()

    def imageAdd(self, im, xa, ya, size=6):
        """Adds a new image to the chart.

        It is assumed that the size of the image is 'size' units. This means that the image
        will be scaled to take 'size' units on the canvas, regardless of the resolution
        and the number of pixels in the image.
        """
        b,h = im.size
        h1 = size
        b1 = int(b * size / h)
#        print "Image=", b, h, "-->", b1, h1
#        im1 = im.resize((b1, h1))
#        im1 = ImageTk.PhotoImage(im1)
        x = [xa+0.0, xa+b1]
        y = [ya+0.0, ya+h1]
        self.curves.append((x, y, "red", im, "image", 1, size))

#=============================================================================

    def minmax(self):
        "Recalculates min, max coordinates."
        self.xmin, self.ymin =  1e30,  1e30
        self.xmax, self.ymax = -1e30, -1e30
        for curve in self.curves:
            x, y = curve[0:2]
            self.xmin = min(self.xmin, min(x))
            self.ymin = min(self.ymin, min(y))
            self.xmax = max(self.xmax, max(x))
            self.ymax = max(self.ymax, max(y))

#=============================================================================

    def thanRot(self, f):
        "Rotates f degrees all images in the chart."
        for i, (xc, yc, color, im, style, width, size) in enumerate(self.curves):
            if style != "image": continue
            b, h = xc[1]-xc[0], yc[1]-yc[0]
            bor, hor = im.size
            scale = b / bor
            xa, ya = xc[0], yc[0]
            im = im.rotate(f)

            b,h = im.size
            #dpi = 100.0
            b *= scale; h *= scale
            x = [xa+0.0, xa+b]
            y = [ya+0.0, ya+h]
            self.curves[i] = (x[:], y[:], "red", im, "image", 1, 6)
        self.minmax()

    def thanConv(self, c):
        "Converts an image to c."
        for i, (xc, yc, color, im, style, width, size) in enumerate(self.curves):
            if style != "image": continue
            if c == "2":
                if im.mode == "1":
                    pass
                elif im.mode == "L":
                    print("Converting to black and white..")
                    im = im.convert("1")
                else:
                    print("Converting to gray scale..")
                    im = im.convert("L")
                    print("Converting to black and white..")
                    im = im.convert("1")
            elif c == "3":
                if im.mode == "1":
                    print("Inverting..")
                    im = im.point(finv)
                elif im.mode == "L":
                    print("Inverting..")
                    im = im.point(finv)
                    print("Converting to black and white..")
                    im = im.convert("1")
                else:
                    print("Converting to gray scale..")
                    im = im.convert("L")
                    print("Inverting..")
                    im = im.point(finv)
                    print("Converting to black and white..")
                    im = im.convert("1")
            else:
                im = im.convert(c)
            self.curves[i] = (xc, yc, color, im, style, width, size)

    def thanGetImage(self):
        "Returns the first image of the chart."
        for i, (xc, yc, color, im, style, width, size) in enumerate(self.curves):
            if style == "image": return im

#=============================================================================

    def regen(self, dc, dx, dy, xsc, ysc):
        "Regenerates all the curves into canvas dc."
        self.minmax()
        dc.delete(tkinter.ALL)
        self.__images = {}
        for xc, yc, color, fill, style, width, size in self.curves:
            xp = [ dx+x*xsc for x in xc ]
            yp = [ dy+y*ysc for y in yc ]
            if style == "continuous":
                dc.create_line(list(zip(xp, yp)), fill=color, width=width)   #OK for python 2,3
            elif style == "polygon":
                dc.create_polygon(list(zip(xp, yp)), outline=color, fill=fill, width=width)   #OK for python 2,3
            elif style == "directed":
                if size == 6: size = (6, -6)
                self.linedirected(xp, yp, size, color, width, dc)
            elif style == "dasheddot":
                if size == 6: size = (6, -6)
                self.dasheddot(xp, yp, size, color, width, dc)
            elif style == "dashedsym":
                if size == 6: size = (6, -6)
                self.dashedsym(xp, yp, size, color, fill, dc)
            elif style == "image":
                im = fill
                print("regen:size=", size, "  ysc=", ysc)
                item = dc.create_image(int(xp[0]), int(yp[0]), image=self.thanTkImage(im, int(fabs(size*ysc)+0.5)), anchor="sw")
            else:
                p = thanPoints[style]
                for (x,y) in list(zip(xp, yp)): p(dc, x, y, size, color, fill)  #OK for python 2,3

    def thanTkImage(self, im, size):
        "Returns a Tk photoimage class of im using cache."
        try: return self.__images[(id(im), int(size))]
        except KeyError: pass
        print("thanTkImage:size:", size)
        b,h = im.size
        h1 = size
        b1 = int(b * size / h)
        im1 = im.resize((b1, h1))
        im1 = ImageTk.PhotoImage(im1)
        self.__images[(id(im), size)] = im1
        return im1

#=============================================================================

    def redraw(self, dc, margin=0.02):
        "Redraws the curves into canvas dc."

        dc.delete(tkinter.ALL)

        dc.update()
        self.wx = dc.winfo_width()
        self.wy = dc.winfo_height()
        dx = (self.xmax - self.xmin)
        dy = (self.ymax - self.ymin)

        xsc = self.wx / (dx*(1+margin))
        ysc = self.wy / (dy*(1+margin))
        xsc = ysc = min(xsc, ysc)
        xmi = self.xmin - (self.wx/xsc-dx)/2
        ymi = self.ymin - (self.wy/ysc-dy)/2

        for xc, yc, color, fill, style, width, size in self.curves:
            xp = [         (x-xmi)*xsc for x in xc ]
            yp = [ self.wy-(y-ymi)*ysc for y in yc ]
            if style == "continuous":
                dc.create_line(list(zip(xp, yp)), fill=color, width=width)  #OK for python 2,3
            elif style == "continuous":
                dc.create_polygon(list(zip(xp, yp)), outline=color, fill=fill, width=width)   #OK for python 2,3
            elif style == "directed":
                if size == 6: size = (6, -6)
                self.linedirected(xp, yp, size, color, width, dc)
            elif style == "dasheddot":
                if size == 6: size = (6, -6)
                self.dasheddot(xp, yp, size, color, width, dc)
            elif style == "dashedsym":
                if size == 6: size = (6, -6)
                self.dashedsym(xp, yp, size, color, fill, dc)
            else:
                p = thanPoints[style]
                for (x,y) in list(zip(xp, yp)): p(dc, x, y, size, color, fill)  #OK for python 2,3

#=============================================================================

    def linedirected(self, xp, yp, r, color, width, dc):
        "Plots a continuous line with direction arrows."
        dc.create_line(list(zip(xp, yp)), fill=color, width=width)  #OK for python 2,3
        i = 1
        x1, y1 = xp[0], yp[0]
        ir = 0
        s = r[ir]
        as_ = fabs(s)
        if width <= 1:
            w1 = w2 = 1
        else:
            w1 = int(width/2); w2 = width-w1
            w1 += 1; w2 += 1

        while 1:
            dx, dy = xp[i]-x1, yp[i]-y1
            d = hypot(dx, dy)
            if as_ > d:            # Note in this case s can not be zero
                x1, y1 = xp[i], yp[i]
                as_ -= d
                i += 1
                if i >= len(xp): return
            else:
                if s > 0:
                    xt, yt = x1, y1
                    cosf = dx/d
                    sinf = dy/d
                    x1 += as_*cosf
                    y1 += as_*sinf
                    sinf = -sinf        #Note: the y-axis is inverted: angle is 180+f
                    cosf = -cosf        #Note: the y-axis is inverted: angle is 180+f
                    x0 = x1 + (s*0.5)*cosf + (s*0.5)*(-sinf)
                    y0 = y1 + (s*0.5)*sinf + (s*0.5)*(cosf)
                    x2 = x1 + (s*0.5)*cosf - (s*0.5)*(-sinf)
                    y2 = y1 + (s*0.5)*sinf - (s*0.5)*(cosf)
                    dc.create_line(( (x0, y0), (x1, y1), (x2, y2) ), fill=color, width=width)
                else:
                    x1 += dx*as_/d
                    y1 += dy*as_/d
                ir = (ir+1) % len(r)
                s = r[ir]
                as_ = fabs(s)


    def dasheddot(self, xp, yp, r, color, width, dc):
        "Plots a dashed line."
        i = 1
        x1, y1 = xp[0], yp[0]
        ir = 0
        s = r[ir]
        as_ = fabs(s)
        if width <= 1:
            w1 = w2 = 1
        else:
            w1 = int(width/2); w2 = width-w1
            w1 += 1; w2 += 1

        while 1:
            dx, dy = xp[i]-x1, yp[i]-y1
            d = hypot(dx, dy)
            if as_ > d:            # Note in this case s can not be zero
                if s > 0: dc.create_line(((x1, y1), (xp[i], yp[i])), fill=color, width=width)
                x1, y1 = xp[i], yp[i]
                as_ -= d
                i += 1
                if i >= len(xp): return
            else:
                if s > 0:
                    xt, yt = x1, y1
                    x1 += dx*as_/d
                    y1 += dy*as_/d
                    dc.create_line(((xt, yt), (x1, y1)), fill=color, width=width)
                elif s < 0:
                    x1 += dx*as_/d
                    y1 += dy*as_/d
                else:
                    dc.create_rectangle(x1-w1, y1-w2, x1+w2, y1+w1, fill=color) # This is exactly 1 dot
                ir = (ir+1) % len(r)
                s = r[ir]
                as_ = fabs(s)

#=============================================================================

    __ir = 0
    def dashedsym(self, xp, yp, r, color, fill, dc):
        "Plots a dashed line."
        i = 1
        x1, y1 = xp[0], yp[0]
        self.__ir %= len(r)
        symbol = r[self.__ir]
        try:                  sym, rsym = symbol[:2]
        except TypeError: sym, s, as_ = None, symbol, fabs(symbol)
        else:                  as_ = s = 0

        while 1:
            dx, dy = xp[i]-x1, yp[i]-y1
            d = hypot(dx, dy)
            if as_ > d:            # Note in this case s can not be zero
                if s > 0: dc.create_line(((x1, y1), (xp[i], yp[i])), fill=color)
                x1, y1 = xp[i], yp[i]
                as_ -= d
                i += 1
                if i >= len(xp): return
            else:
                if s > 0:
                    xt, yt = x1, y1
                    x1 += dx*as_/d
                    y1 += dy*as_/d
                    dc.create_line(((xt, yt), (x1, y1)), fill=color)
                elif s < 0:
                    x1 += dx*as_/d
                    y1 += dy*as_/d
                elif isinstance(sym, Image.Image):
                    dc.create_image(int(x1), int(y1), image=self.thanTkImage(sym, rsym), anchor="sw")
                elif sym is not None:
                    thanPoints[sym](dc, x1, y1, rsym, color, fill)
                else:
                    dc.create_rectangle(x1-1, y1-1, x1+1, y1+1, fill=color) # This is exactly 1 dot
                self.__ir = (self.__ir+1) % len(r)
                symbol = r[self.__ir]
                try:                  sym, rsym = symbol[:2]
                except TypeError: sym, s, as_ = None, symbol, fabs(symbol)
                else:                  as_ = s = 0

#=============================================================================

    def onSize(self, dc):
        dc.update()
        wx = dc.winfo_width()
        wy = dc.winfo_height()
        if wx != self.wx or wy != self.wy: self.redraw(dc)


##############################################################################
##############################################################################

#MODULE LEVEL FUNCTIONS


def finv(i):
    if i < 128: return 255
    else: return 0

#=============================================================================

def test1():
    "Makes some curves and shows them."
    ch = ThanChart()
    im = Image.open("pict0003.gif")
    ch.imageAdd(im, 20, 20, 100)
    from .vis import vis, visdxf
    vis(ch)


def test2():
    "Makes some curves and shows them."
    ch = ThanChart()
    xx = 0, 100, 150
    yy = 0, 100, 100
    ch.curveAdd(xx, yy, color="red", fill=None, style="directed", width=1, size=(16, -16))
    from .vis import vis
    vis(ch)


if __name__== "__main__": test2() #test2006()
