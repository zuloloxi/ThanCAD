# -*- coding: iso-8859-7 -*-
import sys
from fnmatch import fnmatch
import p_ggen


class ThanDrIgnore:
    "A class which ignores the elements read by ThanImportDxf."

    def __init__(self, prt=p_ggen.prg):
        "Just get print function."
        if prt == None: self.prt = p_ggen.doNothing   # No message will be printed
        else:           self.prt = prt

    def dxfVars    (self, v):                     pass
    def dxfVport   (self, name, x1, y1, x2, y2):  pass
    def dxfXymm    (self, x1, y1, x2, y2):        pass
    def dxfLayer   (self, name, atts):            pass
    def dxfLtype   (self, name, desc, elems):     pass
    def dxfPolyline(self, xx, yy, zz, lay, handle, col):   pass
    def dxfLine    (self, xx, yy, zz, lay, handle, col):   pass
    def dxfCircle  (self, xx, yy, zz, lay, handle, col, r):pass
    def dxfPoint   (self, xx, yy, zz, lay, handle, col):   pass
    def dxfArc     (self, xx, yy, zz, lay, handle, col, r, theta1, theta2): pass
    def dxfEllipse (self, xx, yy, zz, lay, handle, col, a, b, phia, phib, theta, full): pass
    def dxfText    (self, xx, yy, zz, lay, handle, col, text, h, theta):    pass
    def dxfBlockAtt(self, xx, yy, zz, lay, handle, col, blname, blatts):    pass
    def dxfThanImage(self, xx, yy, zz, lay, handle, col, filnam, size, ale, theta): pass
    def dxf3dface  (self, xx, yy, zz, lay, handle, col): pass


class ThanDrLayer(ThanDrIgnore):
    "A class which saves layers and ignores anything else."

    def __init__(self, *args, **kw):
        "Initialize layer container."
        ThanDrIgnore.__init__(self, *args, **kw)
        self.layer = {}

    def dxfLayer (self, name, atts):
        "Collect the layers."
        self.layer[name] = atts


class ThanDrWarn(ThanDrIgnore):
    """A class which warns about unknown object/layer pairs.

    I think that this is the safest class to derive from. If new functionality is 
    added to the library, this class will be updated. So the derived classes will
    dynamically inherit and they will produce warnings about things not implemented,
    or not accessed, or ignored.
    """

    def __init__(self, laykno=(), **kw):
        """Set known and unknown layers.

        The argument laykno is a list/tuple of layers which the user is interested in.
        (and expects). The layers may contain wild characters as understood by fnmatch().
        These layers (with the wild characters) are copied to _layknopat (pat is for pattern).
        """
        ThanDrIgnore.__init__(self, **kw)
        self._objunk = {}  # Unknown objects: objects which the user is not interested in
        self._functy = {}  # Functionality which the user is not interested in
        self._laykno = {}  # Layers which the user expects
        self._layunk = {}  # Layers which the user is not interested in
        self._layknopat = [lay.lower() for lay in laykno]  #Layers which the user expects; may contain wild chars


    def warnObj(self, lay, obj):
        "Warn once if an unknown object/layer pair is found."
        lay = lay.lower()
        if self.isLayerKnown(lay):
            m = self._objunk.get((obj, lay), 0) + 1
            self._objunk[obj, lay] = m
            if m > 1: return
            self.prt("Dxf import Warning: (duplicate) objects of type '%s'" % obj, "can1")
            self.prt("                    are ignored in layer %s." % lay, "can1")
        else:
            m = self._layunk[lay] + 1
            self._layunk[lay] = m
            if m > 1: return
            self.prt("Dxf import Warning: layer %s will be ignored." % lay, "can1")


    def isLayerKnown(self, lay):
        "Check if layer lay is known, and add it in local cache."
        lay = lay.lower()
        if lay in self._laykno: return True
        if lay in self._layunk: return False
        for laypat in self._layknopat:
            if fnmatch(lay, laypat):
                self._laykno[lay] = 0
                return True
        self._layunk[lay] = 0
        return False


    def warnFuncty(self, functyname):
        "Warn once for every unimplemented type of functionality."
        n = self._functy.get(functyname, 0) + 1
        self._functy[functyname] = n
        if n > 1: return
        self.prt("Dxf import Warning: %s will be ignored." % functyname, "can1")


    def dxfVars     (self, v):                     self.warnFuncty("Variables definition")
    def dxfVport    (self, name, x1, y1, x2, y2):  self.warnFuncty("Viewport definition")
    def dxfXymm     (self, x1, y1, x2, y2):        self.warnFuncty("Extents definition")
    def dxfLayer    (self, name, atts):            self.warnFuncty("Layer definition")
    def dxfLtype    (self, name, desc, elems):     self.warnFuncty("Line type definition")

    POLYLINE = "polyline"
    LINE     = "line"
    CIRCLE   = "circle"
    POINT    = "point"
    ARC      = "arc"
    ELLIPSE  = "ellipse"
    TEXT     = "text"
    BLOCK    = "block"
    IMAGE    = "image"
    FACE3D   = "3dface"

    def dxfPolyline (self, xx, yy, zz, lay, handle, col):                 self.warnObj(lay, self.POLYLINE)
    def dxfLine     (self, xx, yy, zz, lay, handle, col):                 self.warnObj(lay, self.LINE) 
    def dxfCircle   (self, xx, yy, zz, lay, handle, col, r):              self.warnObj(lay, self.CIRCLE) 
    def dxfPoint    (self, xx, yy, zz, lay, handle, col):                 self.warnObj(lay, self.POINT)
    def dxfArc      (self, xx, yy, zz, lay, handle, col, r, theta1,
                     theta2):                                             self.warnObj(lay, self.ARC)
    def dxfEllipse  (self, xx, yy, zz, lay, handle, col, a, b, phia,
                     phib, theta, full):                                  self.warnObj(lay, self.ELLIPSE)
    def dxfText     (self, xx, yy, zz, lay, handle, col, text, h, theta): self.warnObj(lay, self.TEXT)
    def dxfBlockAtt (self, xx, yy, zz, lay, handle, col, blname, blatts): self.warnObj(lay, self.BLOCK)
    def dxfThanImage(self, xx, yy, zz, lay, handle, col, filnam, size, 
                     scale,  theta):                                      self.warnObj(lay, self.IMAGE)
    def dxf3dface   (self, xx, yy, zz, lay, handle, col):                 self.warnObj(lay, self.FACE3D)


class ThanDrLine(ThanDrWarn):
    "A class which gets only lines/polylines; it is an example of ThanDrWarn usage."

    def dxfPolyline (self, xx, yy, zz, lay, handle, col):
        "Get polyline if it is in known layers."
        if self.isLayerKnown(lay):
            self.processLine(xx, yy, zz, lay, handle, col)
        else:
            self.warnObj(lay, self.POLYLINE)


    def dxfLine     (self, xx, yy, zz, lay, handle, col):
        "Get line if it is in known layers."
        if self.isLayerKnown(lay):
            self.processLine(xx, yy, zz, lay, handle, col)
        else:
            self.warnObj(lay, self.LINE) 


    def processLine(self, xx, yy, zz, lay, handle, col):
        "What to do with the line/polyline; overwrite it."
        self.prt("Line x1=%.3f  y1=%.3f z1=%.3f ... in layer=%s" % (xx[0], yy[0], zz[0], lay), "info1")


class ThanDrSave(ThanDrIgnore):
    "A class which stores the elements read by ThanImportDxf."

    def __init__(self, **kw):
        "Creates an instance of the class."
        ThanDrIgnore.__init__(self, **kw)
        self.thanVars = {}
        self.thanVports = [ ]
        self.thanLayers = [ ]
        self.thanLtypes = [ ]
        self.thanXymm = None
        self.thanPolylines = [ ]
        self.thanLines = [ ]
        self.thanCircles = [ ]
        self.thanPoints = [ ]
        self.thanArcs = [ ]
        self.thanEllipses = [ ]
        self.thanTexts = [ ]
        self.thanBlocks = []
        self.thanImages = []
        self.than3dfaces = []


    def dxfVars(self, v):
        "Saves the variables."
        self.thanVars.update(v)

    def dxfVport(self, name, x1, y1, x2, y2):
        "Saves a View Port."
        self.thanVports.append((name, x1, y1, x2, y2))

    def dxfXymm(self, x1, y1, x2, y2):
        "Saves xmin,ymin,xmax,ymax of the dxf drawing."
        self.thanXymm = x1, y1, x2, y2

    def dxfLayer(self, name, atts):
        "Saves a layer."
        self.thanLayers.append((name, atts))

    def dxfLtype(self, name, desc, elems):
        "Saves a line type."
        self.thanLtypes.append((name, desc, elems))

    def dxfPolyline(self, xx, yy, zz, lay, handle, col):
        "Saves a polyline."
        self.thanPolylines.append((xx, yy, zz, lay, col))

    def dxfLine(self, xx, yy, zz, lay, handle, col):
        "Saves a line."
        self.thanLines.append((xx, yy, zz, lay, col))

    def dxfCircle(self, xx, yy, zz, lay, handle, col, r):
        "Saves a View Port."
        self.thanCircles.append((xx, yy, zz, lay, col, r))

    def dxfPoint(self, xx, yy, zz, lay, handle, col):
        "Saves a point."
        self.thanPoints.append((xx, yy, zz, lay, col))

    def dxfArc(self, xx, yy, zz, lay, handle, col, r, theta1, theta2):
        "Saves an arc."
        self.thanArcs.append((xx, yy, zz, lay, col, r, theta1, theta2))

    def dxfEllipse (self, xx, yy, zz, lay, handle, col, a, b, phia, phib, theta, full):
        "Saves an elliptic arc."
        self.thanEllipses.append((xx, yy, zz, lay, col, a, b, phia, phib, theta, full))

    def dxfText(self, xx, yy, zz, lay, handle, col, text, h, theta):
        "Saves a text."
        self.thanTexts.append((xx, yy, lay, col, text, h, theta))

    def dxfBlockAtt(self, xx, yy, zz, lay, handle, col, blname, blatts):
        "Saves a block insertion."
        self.thanBlocks.append((xx, yy, zz, lay, col, handle, col, blname, blatts))

    def dxfThanImage(self, xx, yy, zz, lay, handle, col, filnam, size, scale, theta):
        "Saves an ThanImage."
        self.thanImages.append((xx, yy, zz, lay, col, handle, filnam, size, scale, theta))

    def dxf3dface  (self, xx, yy, zz, lay, handle, col):
        "Saves a 3dface."
        self.than3dfaces.append((xx, yy, zz, lay, handle, col))

    def statistics(self):
        "Saves a text."
        self.prt("Contents of dxf file:", "info")
        n = ""
	if self.thanXymm == None: n = "NOT"
	self.prt("Max, min of x,y     : %s defined in dxf file" % n, "info1")

        self.prt("Number of variables : %d" % len(self.thanVars), "info1")
        self.prt("Number of view ports: %d" % len(self.thanVports), "info1")
        self.prt("Number of layers    : %d" % len(self.thanLayers), "info1")
	self.prt("Number of line types: %d" % len(self.thanLtypes), "info1")
        self.prt("Number of polylines : %d" % len(self.thanPolylines), "info1")
	self.prt("Number of lines     : %d" % len(self.thanLines), "info1")
        self.prt("Number of texts     : %d" % len(self.thanTexts), "info1")
	self.prt("Number of points    : %d" % len(self.thanPoints), "info1")
	self.prt("Number of circles   : %d" % len(self.thanCircles), "info1")
        self.prt("Number of arcs      : %d" % len(self.thanArcs), "info1")
        self.prt("Number of ellipses  : %d" % len(self.thanEllipses), "info1")
        self.prt("Number of blocks ins: %d" % len(self.thanBlocks), "info1")
        self.prt("Number of thanImages: %d" % len(self.thanImages), "info1")
        self.prt("Number of 3dfaces   : %d" % len(self.than3dfaces), "info1")


class ThanDxfDrawing(ThanDrSave):
    """A class which stores and plots the elements read by ThanImportDxf.

    The object reads a dxf file and stores all its elements (the elements supported
    by ThanImportDxf.
    Then it can:
    a. Plot the draing into a new dxf file translated, scaled and rotated.
    b. Find its reference point, either the center or the lower-left point.
    c. Find text element with a given text value.
    d. Replace the text value of a text element, and optionally justify it (left, center, right).
    """

    def findRef(self, kind="min"):
        "Finds the reference point of the drawing: minx, miny in lines."
        xmin = ymin = 1e100; xmax = ymax = -1e100
        for xx, yy, zz, lay, col in self.thanPolylines:
            xmin = min((min(xx), xmin))
            ymin = min((min(yy), ymin))
            xmax = max((max(xx), xmax))
            ymax = max((max(yy), ymax))
        for xx, yy, zz, lay, col in self.thanLines:
            xmin = min((min(xx), xmin))
            ymin = min((min(yy), ymin))
            xmax = max((max(xx), xmax))
            ymax = max((max(yy), ymax))
        self.xmin = xmin; self.ymin = ymin
        self.xmax = xmax; self.ymax = ymax
        if kind == "min":
            self.xref = xmin
            self.yref = ymin
        elif kind == "center":
            xref = yref = n = 0
            for xx, yy, zz, lay, col in self.thanPolylines:
                xref += sum(xx)
                yref += sum(yy)
                n += len(xx)
            for xx, yy, zz, lay, col in self.thanLines:
                xref += sum(xx)
                yref += sum(yy)
                n += len(xx)
            self.xref = xref/max((n, 1))
            self.yref = yref/max((n, 1))
        else:
            assert 0, "Unknown reference kind: %s" % (kind,)


    def textFind(self, searchstring):
        "Finds searchstring in one of the drawing's texts."
        for i in xrange(len(self.thanTexts)):
            if self.thanTexts[i][4] == searchstring: return i
        return -1


    def textReplace(self, i, newtext, justify=None):
        "Replace the value of string i."
        cur = list(self.thanTexts[i])
        if   justify == "left":   cur[4] = newtext.ljust(len(cur[4]))
        elif justify == "center":
            print cur[4]
            cur[4] = newtext.center(len(cur[4]))
            print cur[4]
        elif justify == "right":  cur[4] = newtext.rjust(len(cur[4]))
        else: cur[4] = newtext
        self.thanTexts[i] = tuple(cur)


    def dxfOut(self, dxf, xor, yor, scale, phi, layer=None, color=None):
        "Plot all the elements of this drawing at point xor, yor scaled and rotated."
        from math import cos, sin, pi
        cs = cos(phi*pi/180)*scale
        ss = sin(phi*pi/180)*scale
        xref = self.xref; yref = self.yref
        if layer != None: dxf.thanDxfSetLayer(layer)   # Override layer
        if color != None: dxf.thanDxfSetColor(color)   # Override color

        def af(xx, yy):
            "Perform translation rotation and scale in set of coordinates."
            xx1 = []; yy1 = []
            for i in xrange(len(xx)):
                xa = xx[i] - xref; ya = yy[i] - yref
                xt = xa*cs - ya*ss
                yt = xa*ss + ya*cs
                xx1.append(xt+xor); yy1.append(yt+yor)
            return xx1, yy1

        def af1(xx, yy):
            "Perform translation rotation and scale in set of coordinates."
            xa = xx - xref; ya = yy - yref
            xt = xa*cs - ya*ss
            yt = xa*ss + ya*cs
            return xt+xor, yt+yor

        def atts(lay=None, col=None):
            "Override layer, color if necessary."
            if layer == None:
                if lay != None: dxf.thanDxfSetLayer(lay)
            if color == None:
                if col != None: dxf.thanDxfSetColor(col)
                dxf.thanDxfSetColor(0)                    # By layer

        for xx, yy, zz, lay, col in self.thanPolylines:
            atts(lay, col)
            dxf.thanDxfPlotPolyline(*af(xx, yy))

        for xx, yy, zz, lay, col in self.thanLines:
            atts(lay, col)
            dxf.thanDxfPlotLine(*af(xx, yy))

        for xx, yy, lay, col, r in self.thanCircles:
            atts(lay, col)
            xx, yy = af1(xx, yy)
            dxf.thanDxfPlotCircle(xx, yy, r*scale)

        for xx, yy, lay, col in self.thanPoints:
            atts(lay, col)
            dxf.thanDxfPlotPoint(*af1(xx, yy))

        for xx, yy, lay, col, r, theta1, theta2 in self.thanArcs:
            atts(lay, col)
            xx, yy = af1(xx, yy)
            dxf.thanDxfPlotArc(afxx, yy, r*scale, theta1+phi, theta2+phi)

        for xx, yy, lay, col, text, h, theta in self.thanTexts:
            atts(lay, col)
            xx, yy = af1(xx, yy)
            dxf.thanDxfPlotSymbol(xx, yy, h*scale, text, theta+phi)

        for xx, yy, lay, col, blname, blatts in self.thanBlocks:
            atts(lay, col)
            pass

        for xx, yy, lay, col, filnam, scalei, theta in self.thanImages:
            atts(lay, col)
            pass


def testThanDrSave():
    "Test dxf import."
    from p_gimdxf import ThanImportDxf
    f = file("116.dxf", "r")
    dr = ThanDrSave()
    t = ThanImportDxf(f, dr)
    t.thanImport()
    f.close()
    dr.statistics()


def testThanDrLayer():
    "Test dxf import."
    from p_gimdxf import ThanImportDxf, ThanDrLayer, thanDxfColCode2Rgb
    fr = file("shm.dxf", "r")
    dr = ThanDrLayer()           # Instantiate the receiver object that collects the layers
    t = ThanImportDxf(fr, dr)    # Instantiate the producer object which reads the dxf file
    t.thanImport()               # Read and parse the dxf file
    fr.close()
    del t
    fw = file("shm.csv", "w")
    form = "%s\t" * 9 + "\n"
    fw.write(form % ("Name", "Autocad Color", "RGB color", "line type", "frozen",
                     "off", "locked", "lineweight", "noplot"))
    for name in dr.layer:
        atts = dr.layer[name]
        fw.write(form % (name, atts["color"], thanDxfColCode2Rgb[atts["color"]], 
                 atts["linetype"], atts["frozen"], atts["off"], atts["locked"],
                 atts["lineweight"], atts["noplot"]))
    fw.close()


def testThanDrWarn():
    "Test dxf import."
    from p_gimdxf import ThanImportDxf
    f = file("116.dxf", "r")
    dr = ThanDrWarn()
    t = ThanImportDxf(f, dr)
    t.thanImport()
    f.close()


if __name__ == "__main__": testThanDrLayer()
