##############################################################################
# ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2025 Thanasis Stamos, May 20, 2025
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (www.gnu.org/licenses/gpl.html).
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################
"""\
ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers

Package which processes commands entered by the user.
This module processes draw commands.
"""
from math import cos, sin, hypot, atan2, pi
from p_gmath import thanNear2
import p_ggen
import thandr
from thanvar import Canc, thanCumulDis, THANBYPARENT
from thantrans import T
from thansupport import thanToplayerCurrent
from . import thanundo
from .thancommod import thanModCanc, thanModEnd
from .thancomsel import thanSelect1, thanSelectGen
from .selutil import thanSel1line


def thanTkDrawElem(proj, elemClass, fn="thanTkGet", **kw):
    "Draws an element with the help of a GUI and stores it to database."
    elem = elemClass()
    comname = elemClass.thanElementName
    crelold = proj[1].thanGetLastPoint()
    if getattr(elem, fn)(proj, **kw) == Canc: return proj[2].thanGudCommandCan()
    proj[1].thanElementAdd(elem)             # thanTouch is implicitly called
    crel = proj[1].thanGetLastPoint()
#    if elem.thanInbox(proj[1].viewPort): elem.thanTkDraw(proj[2].than)
    elem.thanTkDraw(proj[2].than)
    newelems = (elem,)
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo2, ((), newelems, (), crel),
                                        thanundo.thanReplaceUndo2, ((), newelems, (), crelold))
    proj[2].thanGudCommandEnd()


def thanTkDrawLine(proj, fn="thanTkGet", **kw):
    "Draws a line with the help of a GUI and stores it to database."
    elem = thandr.ThanLine()
    comname = "line"
    crelold = proj[1].thanGetLastPoint()
    if getattr(elem, fn)(proj, **kw) == Canc: return proj[2].thanGudCommandCan()
    proj[1].thanElementAdd(elem)             # thanTouch is implicitly called
    crel = proj[1].thanGetLastPoint()
#    if elem.thanInbox(proj[1].viewPort): elem.thanTkDraw(proj[2].than)
    elem.thanTkDraw(proj[2].than)

    proj[2].thanLineRecentTag = elem.thanTags[0]      #Most recent created line (so that we may continue it in the future)

    newelems = (elem,)
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo2, ((), newelems, (), crel),
                                        thanundo.thanReplaceUndo2, ((), newelems, (), crelold))
    proj[2].thanGudCommandEnd()


def thanTkDrawDimali(proj, fn="thanTkGet", **kw):
    "Draws an aligned dimension with the help of a GUI and stores it to database."
    #proj[1].thanLayerTree.thanCur.thanTkSet(proj[2].than)  #Thanasis2021_11_20:is this needed?
    comname = "dimali"
    crelold = proj[1].thanGetLastPoint()

    c1 = proj[2].thanGudGetPoint(T["First dimension point [Continue]: "], options=("Continue",))
    if c1 == Canc: return proj[2].thanGudCommandCan()   # Aligned dimension cancelled
    if c1 == "c":
        def filt2(e): return isinstance(e, thandr.ThanDimali)
        elem = thanSelect1(proj, T["Select dimension to continue: "], filter=filt2)
    else:
        elem = __drawdimali1(proj, c1)
    if elem is Canc: return proj[2].thanGudCommandCan()   # Aligned dimension cancelled

    newelems = [elem]
    while True:      #Get continuation of aligned dimension
        elem = __drawdimali2(proj, newelems[-1])
        if elem is Canc: break
        newelems.append(elem)

    crel = proj[1].thanGetLastPoint()
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo2, ((), newelems, (), crel),
                                        thanundo.thanReplaceUndo2, ((), newelems, (), crelold))
    proj[2].thanGudCommandEnd()


def __drawdimali1(proj, c1):
    "Get and draw a new dimali."
    geom = p_ggen.Struct()
    statonce = ""
    while True:
        c2 = proj[2].thanGudGetLine(c1, T["Next dimension point: "], statonce=statonce)
        if c2 == Canc: return Canc      # Aligned dimension cancelled
        if not thanNear2(c1, c2): break
        statonce = T["Degenerate dimension. Try again.\n"]

    geom.t = c2[0]-c1[0], c2[1]-c1[1]
    geom.theta = atan2(geom.t[1], geom.t[0])
    w = hypot(geom.t[0], geom.t[1])
    geom.t = geom.t[0]/w, geom.t[1]/w
    geom.n = -geom.t[1], geom.t[0]

    elem = thandr.ThanDimali()
    distext = elem.strdis(proj[2].than.dimstyle, w)
    distype, disnum = elem.guesstype(c1, c2, distext)
    elem.thanSet(distype, disnum, distext, c1, c2, 0.0)
    elem.thanTags = ("e0", )                         # So that we know that it is temporary
    ct = c2  #works for python2,3
    c3 = proj[2].thanGudGetMovend(ct, T["Perpendicular location: "], elems=[elem], direction=geom.theta+pi/2)
    if c3 == Canc:  return Canc    # Aligned dimension cancelled

    mes = "%s (enter=%s): " % (T["Dimension text"], distext)
    distext = proj[2].thanGudGetText(mes, distext)
    if distext == Canc:  return Canc   # Aligned dimension cancelled
    print("distext=", distext)

    geom.perp = (c3[0]-ct[0])*geom.n[0] + (c3[1]-ct[1])*geom.n[1]

    distype, disnum = elem.guesstype(c1, c2, distext)
    elem.thanSet(distype, disnum, distext, c1, c2, geom.perp)
    proj[1].thanElementAdd(elem)             # thanTouch is implicitly called
    elem.thanTkDraw(proj[2].than)
    proj[1].thanSetLastPoint(c2)
    return elem


def __drawdimali2(proj, elemprev):
    "Get and draw a new dimali as a continuation of previous dimali."
    c1, c2, c3 = elemprev.cp[:3]
    if thanNear2(c1, c2): theta = 0.0
    else:                 theta = atan2(c2[1]-c1[1], c2[0]-c1[0])
    c1 = c3

    statonce = ""
    while True:
        c2 = proj[2].thanGudGetInclined(c1, theta, T["Next dimension point: "], statonce=statonce)
        if c2 == Canc: return Canc      # Aligned dimension cancelled
        if not thanNear2(c1, c2): break
        statonce = T["Degenerate dimension. Try again.\n"]
    w = hypot(c2[0]-c1[0], c2[1]-c1[1])
    elem = thandr.ThanDimali()
    distext = elem.strdis(proj[2].than.dimstyle, w)
    mes = "%s (enter=%s): " % (T["Dimension text"], distext)
    distext = proj[2].thanGudGetText(mes, distext)
    if distext == Canc:  return Canc   # Aligned dimension cancelled

    distype, disnum = elem.guesstype(c1, c2, distext)
    elem.thanSet(distype, disnum, distext, c1, c2, 0.0)
    proj[1].thanElementAdd(elem)             # thanTouch is implicitly called
    elem.thanTkDraw(proj[2].than)
    proj[1].thanSetLastPoint(c2)
    return elem


def thanTkDrawRect(proj):
    "Draws a closed line in the shape of a rectangle."
    c1 = proj[2].thanGudGetPoint(T["First point: "])
    if c1 == Canc: return proj[2].thanGudCommandCan()      # Rectangle cancelled
    c2 = proj[2].thanGudGetRect(c1, T["Second point: "])
    if c2 == Canc: return proj[2].thanGudCommandCan()      # Rectangle cancelled
    x1, y1 = c1[:2]
    x2, y2 = c2[:2]
    if x2 < x1: x1, x2 = x2, x1
    if y2 < y1: y1, y2 = y2, y1
    elem = thandr.ThanLine()
    c1[:2] = x1, y1
    c2 = list(c1); c2[:2] = x2, y1
    c3 = list(c1); c3[:2] = x2, y2
    c4 = list(c1); c4[:2] = x1, y2
    c5 = list(c1)

    elem.thanSet([c1, c2, c3, c4, c5])
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)
    newelems = (elem,)
    proj[1].thanDoundo.thanAdd("rectangle", thanundo.thanReplaceRedo, ((), newelems),
                                            thanundo.thanReplaceUndo, ((), newelems))
    proj[2].thanGudCommandEnd()


def thanTkDrawPoint(proj):
    "Draws multiple points with the help of a GUI and stores them to database."
    res = proj[2].thanGudGetPoint(T["Specify a point (e=explicit z): "], options=("explicit",))
    if res == Canc: return proj[2].thanGudCommandCan() # Point cancelled
    if res != "e":
        __housepoint(proj, res)
        while True:
            res = proj[2].thanGudGetPoint(T["Specify a point (<enter>): "], options=("",))
            if res == Canc: return proj[2].thanGudCommandEnd()    # No more points
            if res == "":   return proj[2].thanGudCommandEnd()    # No more points
            __housepoint(proj, res)

    z = proj[1].thanVar["elevation"][2]                         # Get points with z given explicitly
    while True:
        res = proj[2].thanGudGetPoint(T["Specify a point xy (<enter>): "], options=("",))
        if res == Canc: return proj[2].thanGudCommandEnd()  # No more points
        if res == "": return proj[2].thanGudCommandEnd()    # No more points
        z = proj[2].thanGudGetFloat(T["Specify point z: "], z)
        if z == Canc:
            proj[2].thanPrtCan("can1")
            continue
        res[2] = z
        __housepoint(proj, res)

def __housepoint(proj, cc):
    "Create and draw the point and do housekeeping."
    elem = thandr.ThanPoint()
    elem.thanSet(cc)
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)
    newelems = (elem,)
    proj[1].thanDoundo.thanAdd("point", thanundo.thanReplaceRedo, ((), newelems),
                                        thanundo.thanReplaceUndo, ((), newelems))


gvalidc = [True, True, True]
def thanTkDrawPointNamed(proj):
    "Draws multiple points with the help of a GUI and stores them to database."
    cvis = T["Coordinate usability (for DTM, etc)"]
    res = __drawpnamed1(proj, cvis)
    if   res == Canc: return proj[2].thanGudCommandCan()      # Point cancelled
    elif res == "e":  __drawpnamed3(proj, cvis)
    else:             __drawpnamed2(proj, cvis)
    proj[2].thanGudCommandEnd()

def __drawpnamed1(proj, cvis):
    "get the first point and check for explicit z."
    while True:
        statonce = "%s: X=%r Y=%r Z=%r\n" % (cvis, gvalidc[0], gvalidc[1], gvalidc[2])
        res = proj[2].thanGudGetPoint(T["Specify a point (e=explicit z/toggle X/toggle Y/toggle Z): "],
            statonce, options=("explicit", "X", "Y", "Z"))
        if res == Canc: return res
        if res == "e": return res
        if res in ("x", "y", "z"):
            i = "xyz".index(res)
            gvalidc[i] = not gvalidc[i]
            continue
        name = proj[2].thanGudGetText0(T["Point name: "])
        if name == Canc:
            proj[2].thanPrtCan("can1")
            continue
        __housepnamed(proj, res, name)
        return ""

def __drawpnamed2(proj, cvis):
    "Get multiple points without asking for z."
    while True:
        statonce = "%s: X=%r Y=%r Z=%r\n" % (cvis, gvalidc[0], gvalidc[1], gvalidc[2])
        res = proj[2].thanGudGetPoint(T["Specify a point (toggle X/toggle Y/toggle Z): "],
              statonce, options=("", "X", "Y", "Z"))
        if res == Canc: return    # No more points
        if res == "":   return    # No more points
        if res in ("x", "y", "z"):
            i = "xyz".index(res)
            gvalidc[i] = not gvalidc[i]
            continue
        name = proj[2].thanGudGetText0(T["Point name: "])
        if name == Canc:
            proj[2].thanPrtCan("can1")
            continue
        __housepnamed(proj, res, name)

def __drawpnamed3(proj, cvis):
    "Get multiple points asking explicitly for z."
    proj[2].thanPrt(T["Points with explicit z"])
    z = proj[1].thanVar["elevation"][2]                         # Get points with z given explicitly
    while True:
        statonce = "%s: X=%r Y=%r Z=%r\n" % (cvis, gvalidc[0], gvalidc[1], gvalidc[2])
        res = proj[2].thanGudGetPoint(T["Specify a point xy (toggle X/toggle Y/toggle Z): "],
              statonce, options=("", "X", "Y", "Z"))
        if res == Canc: return    # No more points
        if res == "":   return    # No more points
        if res in ("x", "y", "z"):
            i = "xyz".index(res)
            gvalidc[i] = not gvalidc[i]
            continue
        z = proj[2].thanGudGetFloat(T["Specify point z: "], z)
        if z == Canc:
            proj[2].thanPrtCan("can1")
            continue
        name = proj[2].thanGudGetText0(T["Point name: "])
        if name == Canc:
            proj[2].thanPrtCan("can1")
            continue
        res[2] = z
        __housepnamed(proj, res, name)

def __housepnamed(proj, cc, name):
    "Create and draw the named point and do housekeeping."
    elem = thandr.ThanPointNamed()
    elem.thanSet(cc, name, gvalidc)
    proj[1].thanElementAdd(elem)              # thanTouch is implicitly called
    elem.thanTkDraw(proj[2].than)
    newelems = (elem,)
    proj[1].thanDoundo.thanAdd("point", thanundo.thanReplaceRedo, ((), newelems),
                                        thanundo.thanReplaceUndo, ((), newelems))

def __regpol(ca, cb, n):
    "Driver for regpol."
    a = regpol(n, ca[0], ca[1], cb[0], cb[1])
    return [ct+ca[2:] for ct in a]


def regpol(n,xa,ya,xb,yb):
    """Compute coordinates of regular polygon.

    Spyros Nikolaou, 1st semester student, School of Civil Engineering, NTUA.
    Athens December 26, 2021.
    More professional code with more capabilities in: p_gindplt.regularpolygon.py."""
    import math
    a = [None] * 0
    r = math.sqrt(math.pow((xb - xa) , 2) + math.pow((yb - ya) , 2))
    om = 2*math.pi/n
    phi = math.atan2(yb-ya,xb-xa)
    c = phi + om
    x = xb
    y = yb

    a.append([xa,ya])
    a.append([xb,yb])

    for z in range(2,n):
        x = x + r * math.cos(c)
        y = y + r * math.sin(c)
        c = c + om
        a.append([x,y])

    a.append([xa,ya])

    return a


def thanTkDrawRegularPolygon(proj):
    """Draws a regular polygon.

    More professional code with more capabilities in: p_gindplt.regularpolygon.py."""
    #proj[1].thanLayerTree.thanCur.thanTkSet(proj[2].than)  #Thanasis2021_11_20:is this needed?
    comname = "polreg"
    crelold = proj[1].thanGetLastPoint()

    n = proj[2].thanGudGetInt2(T["Number of regular polygon corners (enter=6): "],
        default=6, limits=(3, None))
    if n == Canc: return proj[2].thanGudCommandCan()  # Polygon cancelled
    c1 = proj[2].thanGudGetPoint(T["First polygon corner: "])
    if c1 == Canc: return proj[2].thanGudCommandCan()  # Polygon cancelled
    c2 = proj[2].thanGudGetLine(c1, T["Second corner: "])
    if c2 == Canc: return proj[2].thanGudCommandCan()  # Polygon cancelled
    cp = __regpol(c1, c2, n)

    elem = thandr.ThanLine()
    elem.thanSet(cp)
    proj[1].thanElementAdd(elem)             # thanTouch is implicitly called
    crel = proj[1].thanGetLastPoint()

    elem.thanTkDraw(proj[2].than)
    newelems = (elem,)
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo2, ((), newelems, (), crel),
                                        thanundo.thanReplaceUndo2, ((), newelems, (), crelold))
    proj[2].thanGudCommandEnd()


def thanTkDrawPolygon(proj):
    "Gets and draws a closed polyline (which is a polygon)."
    cp = getpol(proj)
    if cp == Canc: return proj[2].thanGudCommandCan()  # Polygon cancelled
    if not thanNear2(cp[0], cp[-1]): cp.append(list(cp[0]))
    elem = thandr.ThanLineFilled()
    elem.thanSet(cp, persistentfilled=False)
    proj[1].thanElementAdd(elem)          # thanTouch is implicitly called
    elem.thanTkDraw(proj[2].than)
    newelems = (elem,)
    proj[1].thanDoundo.thanAdd("polygon", thanundo.thanReplaceRedo, ((), newelems),
                                          thanundo.thanReplaceUndo, ((), newelems))
    proj[2].thanGudCommandEnd()


def thanTkDrawSolid(proj):
    "Gets and draws a closed polyline (which is a polygon)."
    prt = proj[2].thanPrt
    prt("ThanCad hint: The combination of polygons (which are closed polylines) with")
    prt("the 'fill' attribute of layers is superior to the 'solid' command.")

    lay = proj[1].thanLayerTree.thanCur
    res = False
    fillold = fillnew = None
    if not lay.thanAtts["fill"].thanVal:
        res = proj[2].thanGudGetYesno(T["Set Fill mode ON for current layer (recommended) [yes/no] <yes>:"], default="yes")
        if res == Canc: return proj[2].thanGudCommandCan()  # Solid cancelled
        if res:
            fillold = False
            if lay.thanAtts["fill"].thanInher: fillold = THANBYPARENT
            fillnew = True

    cp = getsolid(proj)
    if cp == Canc: return proj[2].thanGudCommandCan()  # Solid cancelled
    if not thanNear2(cp[0], cp[-1]): cp.append(list(cp[0]))
    elem = thandr.ThanLineFilled()
    elem.thanSet(cp, persistentfilled=True)
    proj[1].thanElementAdd(elem)          # thanTouch is implicitly called
    elem.thanTkDraw(proj[2].than)
    if res: thanToplayerCurrent(proj, lay.thanGetPathname(), current=True, fill=res)  #This sets the fill mode to the layer
    proj[1].thanDoundo.thanAdd("solid", __drawsolidRedo, (elem, fillnew),
                                        __drawsolidUndo, (elem, fillold))
    proj[2].thanGudCommandEnd()


def __drawsolidUndo(proj, elem, fill):
    "Undraws the solid and resets the fill attribute to previous value."
    thanundo.thanReplaceUndo(proj, delelems=(), newelems=(elem,))
    if fill is not None:
        lay = proj[1].thanLayerTree.thanCur
        thanToplayerCurrent(proj, lay.thanGetPathname(), current=True, fill=fill)


def __drawsolidRedo(proj, elem, fill):
    "Redraws the solid and resets the fill attribute."
    thanundo.thanReplaceRedo(proj, delelems=(), newelems=(elem,))
    if fill is not None:
        lay = proj[1].thanLayerTree.thanCur
        thanToplayerCurrent(proj, lay.thanGetPathname(), current=True, fill=fill)


def getpol(proj, nmax=-1):
    "Get a (non)convex polygon from user of at most nmax corners."
    than = proj[2].than
    g2l = than.ct.global2Local
    c1 = proj[2].thanGudGetPoint(T["First polygon corner: "])
    if c1 == Canc: return Canc                   # Polygon cancelled
    while True:
        c2 = proj[2].thanGudGetLine(c1, T["Second polygon corner: "])
        if c2 == Canc: return Canc               # Polygon cancelled
        temp = than.dc.create_line(g2l(c1[0], c1[1]), g2l(c2[0], c2[1]),
            fill="blue", tags=("e0",))
        item = [temp]
        cs = [c1, c2]
        while True:
            if len(cs) < 3: opts = ("undo", )
            else:           opts = ("undo", "")
            c3 = proj[2].thanGudGetLine2(cs[0], cs[-1], T["Next polygon corner (Undo): "], options=opts)
            if c3 == Canc:
                if len(cs) < 3: than.dc.delete("e0"); return Canc # Polygon cancelled
                c3 = ""    #If len(cs) >=3 then ESC is like if the use pressed enter
            if c3 == "u":
                if len(cs) == 2: than.dc.delete("e0"); break
                else: than.dc.delete(item[-1]); del item[-1]; del cs[-1]; continue
            if c3 == "": break
            cs.append(c3)
            temp = than.dc.create_line(g2l(cs[-2][0], cs[-2][1]), g2l(c3[0], c3[1]),
               fill="blue", tags=("e0",))
            item.append(temp)
            if nmax != -1 and len(cs) >= nmax: break
        if c3 != "u": break
    temp = than.dc.create_line(g2l(cs[-1][0], cs[-1][1]), g2l(cs[0][0], cs[0][1]),
       fill="blue", tags=("e0",))
    than.dc.delete("e0")
    return cs


def getsolid(proj, nmax=-1):
    """Get a triangle or quadrilateral in the style of thAtCAD.

    The solid is supposed to be filled with colour. In ThanCad, the 'fill'
    attribute of the current layer must be ON, in order to fill the solid.
    Solid is just a closed polyline."""
    than = proj[2].than
    g2l = than.ct.global2Local
    c1 = proj[2].thanGudGetPoint(T["First solid corner: "])
    if c1 == Canc: return Canc                   # Grid cancelled
    while True:
        c2 = proj[2].thanGudGetLine(c1, T["Second solid corner: "])
        if c2 == Canc: return Canc               # Grid cancelled
        temp = than.dc.create_line(g2l(c1[0], c1[1]), g2l(c2[0], c2[1]),
            fill="blue", tags=("e0",))
        item = [temp]
        cs = [c1, c2]
        while True:
            c3 = proj[2].thanGudGetLine2(cs[0], cs[-1], T["Third polygon corner (Undo): "],
                options=("undo",))
            if c3 == Canc: than.dc.delete("e0"); return Canc
            if c3 == "u": than.dc.delete("e0"); break
            cs.append(c3)
            temp = than.dc.create_line(g2l(cs[0][0], cs[0][1]), g2l(c3[0], c3[1]),
               fill="blue", tags=("e0",))
            item.append(temp)
            while True:
                c3 = proj[2].thanGudGetLine2(cs[-1], cs[-2], T["Fourth solid corner (Undo): "],
                    options=("undo",""))
                if c3 == Canc: than.dc.delete("e0"); return Canc
                if c3 == "u": than.dc.delete(item[-1]); del item[-1]; del cs[-1]; break
                if c3 == "":                  # Solid triangle
                    than.dc.delete("e0")
                    return cs
                cs.append(c3)
                temp = than.dc.create_line(g2l(cs[-2][0], cs[-2][1]), g2l(c3[0], c3[1]),
                   fill="blue", tags=("e0",))
                item.append(temp)
                temp = than.dc.create_line(g2l(cs[-1][0], cs[-1][1]), g2l(c3[0], c3[1]),
                   fill="blue", tags=("e0",))
                item.append(temp)
                than.dc.delete("e0")          # Solid quadrilateral
                cs[2], cs[3] = cs[3], cs[2]   # Imitate thAtCAD's sequence of coordinates
                return cs


_texset = p_ggen.Struct("Text settings")
_texset.ct    = None
_texset.size  = 10.0
_texset.theta = 0.0
def thanTkDrawText(proj):
    "Draws multiple texts with the help of a GUI and stores them to database."
    un = proj[1].thanUnits
    if _texset.ct is None: _texset.ct = list(proj[1].thanVar["elevation"])
    texset = _texset.clone()

    mes = "%s (%s, %s) <%s>: " % (T["Text location"], T["below Previous"], T["below Other"], T["below Previous"])
    res = proj[2].thanGudGetPoint(mes, options=("previous", "other", ""))
    if res == Canc: return proj[2].thanGudCommandCan()                # Text cancelled
    if res == "" or res == "p":
        pass
    elif res == "o":
        res = thanSelect1(proj, T["Select other text element to put text below: "], filter=lambda e: isinstance(e, thandr.ThanText))
        if res == Canc: return proj[2].thanGudCommandCan()             # Text cancelled
        texset.ct    = res.getInspnt()
        texset.size  = res.size
        texset.theta = res.theta
        tt = cos(texset.theta), sin(texset.theta)
        nn = -tt[1], tt[0]
        texset.ct[:2] = texset.ct[0]-1.2*texset.size*nn[0], texset.ct[1]-1.2*texset.size*nn[1]
    else:
        texset.ct = res
#    texset.size = proj[2].thanGudGetPosFloat("%s (enter=%s): " % (T["Text size"], un.strdis(texset.size)), texset.size)
    texset.size = proj[2].thanGudGetSize(texset.ct, "%s (enter=%s): " % (T["Text size"], un.strdis(texset.size)), texset.size)
    if texset.size == Canc: return proj[2].thanGudCommandCan()              # Text cancelled
    mes = "%s (enter=%s): " % (T["Rotation angle (azimuth)"], un.strdir(texset.theta))
#    texset.theta = proj[2].thanGudGetFloat(mes, un.rad2unit(texset.theta))
    texset.theta = proj[2].thanGudGetAzimuth(texset.ct, mes, un.rad2unit(texset.theta))
    if texset.theta == Canc: return proj[2].thanGudCommandCan()             # Text cancelled
    texset.theta = un.unit2raddir(texset.theta)
    tt = cos(texset.theta), sin(texset.theta)
    nn = -tt[1], tt[0]
    _texset.update(texset)
    ct = _texset.ct            #This an alias!!
    newelems = []
    while True:
        #text = proj[2].thanGudGetText(T["Text: "], "")
        text = proj[2].thanGudGetTextraw(T["Text:\n"], "")
        if text == Canc: break          # Text cancelled
        if text.strip() != "":          # If blank, then advance a line (with no text)
            elem = thandr.ThanText()
            elem.thanSet(text, ct, _texset.size, _texset.theta)
            proj[1].thanElementAdd(elem)    # thanTouch is implicitly called
            elem.thanTkDraw(proj[2].than)
            newelems.append(elem)
        ct[:2] = ct[0]-1.2*_texset.size*nn[0], ct[1]-1.2*_texset.size*nn[1]
    if len(newelems) == 0: return proj[2].thanGudCommandCan()
    proj[1].thanDoundo.thanAdd("dtext", thanundo.thanReplaceRedo, ((), newelems),
                                        thanundo.thanReplaceUndo, ((), newelems))
    proj[2].thanGudCommandEnd()


def thanPointNamedReplace(proj):
    "Gets names points as point, name, height and deletes the original objects."
    elpnt = thanSelect1(proj, T["Select an unnamed point: "], filter=lambda e: isinstance(e, thandr.ThanPoint))
    if elpnt == Canc: return thanModCanc(proj)      # Point cancelled
    selold = proj[2].thanSelold
    todel = [elpnt]
    elnam = thanSelect1(proj, T["Select a text element for point name (t=type name): "],
        filter=lambda e: isinstance(e, thandr.ThanText), options=("text", ))
    if elnam == Canc: return thanModCanc(proj)      # Point cancelled
    if elnam == "t":
        nam = proj[2].thanGudGetText(T["Type point name: "], default="")
        if nam == Canc: return thanModCanc(proj)    # Point cancelled
    else:
        nam = elnam.text
        todel.append(elnam)
    while True:
        elh = thanSelect1(proj, T["Select a text element for point height (t=type height/enter=height of original point): "],
            filter=lambda e:isinstance(e, thandr.ThanText), options=("text", ""))
        if elh == Canc: return thanModCanc(proj)    # Point cancelled
        if elh == "t": break
        if elh == "": break
        try: h = float(elh.text.replace(",", "."))
        except ValueError: pass
        else: break
        proj[2].thanCom.thanAppend(T["Not a float number. Try Again.\n"], "can")
    if elh == "t":
        h = proj[2].thanGudGetFloat(T["Type point height: "], default=0.0)
        if h == Canc: return thanModCanc(proj)      # Point cancelled
    elif elh == "":
        h = elpnt.cc[2]
    else:
        todel.append(elh)

    elem = thandr.ThanPointNamed()
    cc = list(elpnt.cc)
    cc[2] = h
    elem.thanSet(cc, nam)
    proj[1].thanElementTag(elem)
    newelems = set((elem,))       #newelems must be set (not list) when its is used as selnew
    thanundo.thanReplaceRedo(proj, todel, newelems, newelems)
    proj[1].thanDoundo.thanAdd("pointreplace", thanundo.thanReplaceRedo, (todel, newelems, newelems),
                                               thanundo.thanReplaceUndo, (todel, newelems, selold))
    proj[2].thanGudCommandEnd()


def thanToCurve(proj):
    "Transforms a polyline to a curve (which has very similar properties)."
    linori = thanSel1line(proj, T["Select a line to transform to curve: "])
    if linori == Canc: return thanModCanc(proj)    # Curve cancelled
    lin = thandr.ThanCurve()
    lin.thanSet(linori.cp, thanCumulDis(linori.cp))
    lin.thanTags = linori.thanTags
    selold = proj[2].thanSelold
    delelems = [linori]
    newelems = set((lin,))       #newelems must be set (not list) when its is used as selnew
    thanundo.thanReplaceRedo(proj, delelems, newelems, newelems) #Room for optimisation here.
    proj[1].thanDoundo.thanAdd("tocurve", thanundo.thanReplaceRedo, (delelems, newelems, newelems),
                                          thanundo.thanReplaceUndo, (delelems, newelems, selold))
#  'Reset color' is not needed, but it is called for only 1 element, so it is fast:
    thanModEnd(proj, T["Line was successfully transformed to curve."])


def thanToSpline(proj):
    "Transforms a polyline to a cubic spline curve."
    linori = thanSel1line(proj, T["Select a line to transform to spline: "])
    if linori == Canc: return thanModCanc(proj)    # Curve cancelled
    lin = thandr.ThanSpline()
    lin.thanSet(linori.cp)
    lin.thanTags = linori.thanTags
    selold = proj[2].thanSelold
    delelems = [linori]
    newelems = set((lin,))       #newelems must be set (not list) when its is used as selnew
    thanundo.thanReplaceRedo(proj, delelems, newelems, newelems) #Room for optimisation here.
    proj[1].thanDoundo.thanAdd("tospline", thanundo.thanReplaceRedo, (delelems, newelems, newelems),
                                           thanundo.thanReplaceUndo, (delelems, newelems, selold))
#  'Reset color' is not needed, but it is called for only 1 element, so it is fast:
    thanModEnd(proj, T["Line was successfully transformed to cubic spline curve."])


def thanDecurve(proj):
    "Transforms a curves to lines."
    res = thanSelectGen(proj, standalone=False, filter=lambda e, cl=thandr.ThanCurve: isinstance(e, cl))
    if res == Canc: return thanModCanc(proj)    # Curve cancelled
    selold = proj[2].thanSelold
    selall = proj[2].thanSelall
    delelems = []
    newelems = []
    for elem in selall:
        try:
            elem.cpori
        except AttributeError:   #Avoid ellipse
            continue
        eln = thandr.ThanLine()
        eln.thanSet(elem.cpori)
        eln.thanTags = elem.thanTags
        delelems.append(elem)
        newelems.append(eln)

    thanundo.thanReplaceRedo(proj, delelems, newelems, selall)
    proj[1].thanDoundo.thanAdd("decurve", thanundo.thanReplaceRedo, (delelems, newelems, selall),
                                          thanundo.thanReplaceUndo, (delelems, newelems, selold))
#  'Reset color' is not needed. Room for optimisation here
    thanModEnd(proj, T["%d curves were successfully decurved."] % len(newelems))



def thanToPolygon(proj):
    "Closes lines and transforms them to polygons (filled lines)."
    res = thanSelectGen(proj, standalone=False, filter=lambda e, cl=thandr.ThanLine: isinstance(e, cl))
    if res == Canc: return thanModCanc(proj)    # Curve cancelled
    selold = proj[2].thanSelold
    selall = proj[2].thanSelall
    delelems = []
    newelems = []
    for elem in selall:
        try:
            elem.cpori
        except AttributeError:
            pass
        else:
            continue             #Avoid splines
        eln = thandr.ThanLineFilled()
        eln.thanSet(elem.cp)
        eln.thanTags = elem.thanTags
        delelems.append(elem)
        newelems.append(eln)

    thanundo.thanReplaceRedo(proj, delelems, newelems, selall)
    proj[1].thanDoundo.thanAdd("topolygon", thanundo.thanReplaceRedo, (delelems, newelems, selall),
                                            thanundo.thanReplaceUndo, (delelems, newelems, selold))
#  'Reset color' is not needed. Room for optimisation here
    thanModEnd(proj, T["%d lines were successfully transformed to polygons."] % len(newelems))
