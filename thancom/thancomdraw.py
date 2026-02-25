##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

Package which processes commands entered by the user.
This module processes draw commands.
"""
from math import cos, sin
from p_gmath import thanNear2
import p_ggen
import thandr
from thanvar import Canc
from thantrans import T
from thansupport import thanToplayerCurrent

import thanundo
from thancommod import thanModCanc, thanModEnd
from thancomsel import thanSelect1, thanSelectGen
from selutil import thanSel1line


def thanTkDrawElem(proj, elemClass, fn="thanTkGet", **kw):
    "Draws an element with the help of a GUI and stores it to database."
    elem = elemClass()
    comname = elemClass.thanElementName
    if getattr(elem, fn)(proj, **kw) == Canc: return proj[2].thanGudCommandCan()
    proj[1].thanElementAdd(elem)             # thanTouch is implicitely called
#    if elem.thanInbox(proj[1].viewPort): elem.thanTkDraw(proj[2].than)
    elem.thanTkDraw(proj[2].than)
    newelems = (elem,)
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo, ((), newelems),
                                        thanundo.thanReplaceUndo, ((), newelems))
    proj[2].thanGudCommandEnd()


def thanTkDrawRect(proj):
    "Draws a closed line in the shape of a rectangle."
    c1 = proj[2].thanGudGetPoint(T["First point: "])
    if c1 == Canc: return proj[2].thanGudCommandCan()      # Rectangle cancelled
    c2 = proj[2].thanGudGetRect(c1, T["Second point: "])
    if c2 == Canc: return proj[2].thanGudCommandCan()      # Rectangle cancelled
    x1, y1 = c1[:2]
    x2, y2 = c2[:2]
    if x2 > x1: x1, x2 = x2, x1
    if y2 > y1: y1, y2 = y2, y1
    elem = thandr.ThanLine()
    c1[:2] = x1, y1
    c2 = list(c1); c2[:2] = x2, y1
    c3 = list(c1); c3[:2] = x2, y2
    c4 = list(c1); c4[:2] = x1, y2

    elem.thanSet([c1, c2, c3, c4, c1])
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

    z = proj[1].thanVar["elevation"][2]                         # Get points with z given explicitelly
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
    z = proj[1].thanVar["elevation"][2]                         # Get points with z given explicitelly
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
    proj[1].thanElementAdd(elem)              # thanTouch is implicitely called
    elem.thanTkDraw(proj[2].than)
    newelems = (elem,)
    proj[1].thanDoundo.thanAdd("point", thanundo.thanReplaceRedo, ((), newelems),
                                        thanundo.thanReplaceUndo, ((), newelems))


def thanTkDrawPolygon(proj):
    "Gets and draws a closed polyline (which is a polygon)."
    cp = getpol(proj)
    if cp == Canc: return proj[2].thanGudCommandCan()  # Polygon cancelled
    if not thanNear2(cp[0], cp[-1]): cp.append(list(cp[0]))
    elem = thandr.ThanLineFilled()
    elem.thanSet(cp, persistentfilled=False)
    proj[1].thanElementAdd(elem)          # thanTouch is implicitely called
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
    ia = lay.thanAtts["fill"]
    res = False
    if not ia.thanVal:
        res = proj[2].thanGudGetYesno(T["Set Fill mode ON for current layer (recommended) [yes/no] <yes>:"], default="yes")
        if res == Canc: return proj[2].thanGudCommandCan()  # Polygon cancelled
    cp = getsolid(proj)
    if cp == Canc: return proj[2].thanGudCommandCan()  # Polygon cancelled
    if not thanNear2(cp[0], cp[-1]): cp.append(list(cp[0]))
    elem = thandr.ThanLineFilled()
    elem.thanSet(cp, persistentfilled=True)
    proj[1].thanElementAdd(elem)          # thanTouch is implicitely called
    elem.thanTkDraw(proj[2].than)
    if res: thanToplayerCurrent(proj, lay.thanGetPathname(), current=True, fill=res)  #This sets the fill mode to the layer
    proj[2].thanGudCommandEnd()


def getpol(proj, nmax=-1):
    "Get a (non)convex polygon from user of at most nmax corners."
    than = proj[2].than
    g2l = than.ct.global2Local
    c1 = proj[2].thanGudGetPoint(T["First polygon corner: "])
    if c1 == Canc: return Canc                   # Grid cancelled
    while True:
        c2 = proj[2].thanGudGetLine(c1, T["Second polygon corner: "])
        if c2 == Canc: return Canc               # Grid cancelled
        temp = than.dc.create_line(g2l(c1[0], c1[1]), g2l(c2[0], c2[1]),
            fill="blue", tags=("e0",))
        item = [temp]
        cs = [c1, c2]
        while True:
            c3 = proj[2].thanGudGetLine2(cs[0], cs[-1], T["Next polygon corner (Undo): "],
                options=("undo",""))
            if c3 == Canc: than.dc.delete("e0"); return Canc
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
    attribute of the cirrent layer must be ON, in order to fill the solid.
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
                cs[2], cs[3] = cs[3], cs[2]   # Imitate thAtCAD's sequence of ccordinates
                return cs


def thanTkDrawTextold(proj):
    "Draws multiple texts with the help of a GUI and stores them to database."
    un = proj[1].thanUnits
    size = proj[2].thanGudGetPosFloat(T["Text size: "], 10.00)
    if size == Canc: return proj[2].thanGudCommandCan()              # Text cancelled
    st = "%s(%s): " % (T["Rotation angle"], un.anglunit)
    theta = proj[2].thanGudGetFloat(st, 0.00)
    if theta == Canc: return proj[2].thanGudCommandCan()             # Text cancelled
    c1 = proj[2].thanGudGetPoint(T["Text location: "])
    if c1 == Canc: return proj[2].thanGudCommandCan()                # Text cancelled
    theta = un.unit2rad(theta)
    tt = cos(theta), sin(theta)
    nn = -tt[1], tt[0]
    while True:
        text = proj[2].thanGudGetText(T["Text: "], "")
        if text == Canc: return proj[2].thanGudCommandCan()          # Text cancelled
        if text.strip() == "": return proj[2].thanGudCommandEnd()    # No more texts
        elem = thandr.ThanText()
        elem.thanSet(text, c1, size, theta)
        proj[1].thanElementAdd(elem)              # thanTouch is implicitely called
        elem.thanTkDraw(proj[2].than)
        c1[:2] = c1[0]-1.2*size*nn[0], c1[1]-1.2*size*nn[1]

_ts = p_ggen.Struct("Text settings")
_ts.ct = None
_ts.size = 10.0
_ts.theta = 0.0
def thanTkDrawText2(proj):
    "Draws multiple texts with the help of a GUI and stores them to database."
    un = proj[1].thanUnits
    if _ts.ct == None: _ts.ct = list(proj[1].thanVar["elevation"])
    c1 = proj[2].thanGudGetPoint("%s (enter=%s): " % (T["Text location"], T["below previous text"]), options=("",))
    if c1 == Canc: return proj[2].thanGudCommandCan()                # Text cancelled
    if c1 == "": c1 = _ts.ct
    size = proj[2].thanGudGetPosFloat("%s (enter=%s): " % (T["Text size"], un.strdis(_ts.size)), _ts.size)
    if size == Canc: return proj[2].thanGudCommandCan()              # Text cancelled
    st = "%s (enter=%s): " % (T["Rotation angle"], un.strang(_ts.theta))
    theta = proj[2].thanGudGetFloat(st, _ts.theta)
    if theta == Canc: return proj[2].thanGudCommandCan()             # Text cancelled
    theta = un.unit2rad(theta)
    tt = cos(theta), sin(theta)
    nn = -tt[1], tt[0]
    _ts.ct = c1
    _ts.size = size
    _ts.theta = theta
    while True:
        text = proj[2].thanGudGetText(T["Text: "], "")
        if text == Canc: return proj[2].thanGudCommandCan()          # Text cancelled
        if text.strip() == "": return proj[2].thanGudCommandEnd()    # No more texts
        elem = thandr.ThanText()
        elem.thanSet(text, c1, size, theta)
        proj[1].thanElementAdd(elem)              # thanTouch is implicitely called
        elem.thanTkDraw(proj[2].than)
        c1[:2] = c1[0]-1.2*size*nn[0], c1[1]-1.2*size*nn[1]
        _ts.ct = c1


_texset = p_ggen.Struct("Text settings")
_texset.ct    = None
_texset.size  = 10.0
_texset.theta = 0.0
def thanTkDrawText(proj):
    "Draws multiple texts with the help of a GUI and stores them to database."
    un = proj[1].thanUnits
    if _texset.ct == None: _texset.ct = list(proj[1].thanVar["elevation"])
    texset = _texset.clone()

    mes = "%s (%s, %s) <%s>: " % (T["Text location"], T["below Previous"], T["below Other"], T["below Other"])
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
    mes = "%s (enter=%s): " % (T["Rotation angle"], un.strang(texset.theta))
#    texset.theta = proj[2].thanGudGetFloat(mes, un.rad2unit(texset.theta))
    texset.theta = proj[2].thanGudGetAngle(texset.ct, mes, un.rad2unit(texset.theta))
    if texset.theta == Canc: return proj[2].thanGudCommandCan()             # Text cancelled
    texset.theta = un.unit2rad(texset.theta)
    tt = cos(texset.theta), sin(texset.theta)
    nn = -tt[1], tt[0]
    _texset.update(texset)
    ct = _texset.ct            #This an alias!!
    while True:
        text = proj[2].thanGudGetText(T["Text: "], "")
        if text == Canc: return proj[2].thanGudCommandCan()          # Text cancelled
        if text.strip() == "": return proj[2].thanGudCommandEnd()    # No more texts
        elem = thandr.ThanText()
        elem.thanSet(text, ct, _texset.size, _texset.theta)
        proj[1].thanElementAdd(elem)              # thanTouch is implicitely called
        elem.thanTkDraw(proj[2].than)
        ct[:2] = ct[0]-1.2*_texset.size*nn[0], ct[1]-1.2*_texset.size*nn[1]




def thanPointNamedReplace(proj):
    "Gets names points as point, name, height and deletes the original objects."
    elpnt = thanSelect1(proj, T["Select an unnamed point: "], filter=lambda e: isinstance(e, thandr.ThanPoint))
    if elpnt == Canc: return thanModCanc(proj)      # Point cancelled
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
        elh = thanSelect1(proj, T["Select a text element for point height (t=type height/enter=no z in name): "],
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
        h = "%s" % (h, )
    elif elh == "":
        h = ""
    else:
        h = "%s" % (h, )
        todel.append(elh)

    proj[1].thanElementDelete(todel, proj)                    # Delete original elements
    elem = thandr.ThanPointNamed()
    if h == "": elem.thanSet(elpnt.cc, nam)
    else:       elem.thanSet(elpnt.cc, "%s/%s" % (nam, h))
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)
    proj[2].thanGudCommandEnd()


def thanToCurve(proj):
    "Transforms a polyline to a curve (which has very similar properties)."
    lin = thanSel1line(proj, T["Select a line to transform to curve: "])
    if lin == Canc: return thanModCanc(proj)    # Curve cancelled
    lin.__class__ = thandr.ThanCurve
    lin.thanSetToldeg()      # Set default angle tolerance for smoothness
    thanModEnd(proj, T["Line was succesfully transformed to curve."])


def thanToSpline(proj):
    "Transforms a polyline to a cubic spline curve."
    lin = thanSel1line(proj, T["Select a line to transform to spline: "])
    if lin == Canc: return thanModCanc(proj)    # Curve cancelled
    lin.__class__ = thandr.ThanSpline
    lin.thanSet(lin.cp)

    proj[2].thanCanvas.delete(lin.thanTags[0])
    lt = proj[1].thanLayerTree
    lay = lt.dilay[lin.thanTags[1]]
    if lay != lt.thanCur: lay.thanTkSet(proj[2].than)
    lin.thanTkDraw(proj[2].than)
    if lay != lt.thanCur: lt.thanCur.thanTkSet(proj[2].than)

    thanModEnd(proj, T["Line was succesfully transformed to cubic spline curve."])


def thanDecurve(proj):
    "Transforms a curves to lines."
    res = thanSelectGen(proj, standalone=False, filter=lambda e, cl=thandr.ThanCurve: isinstance(e, cl))
    if res == Canc: return thanModCanc(proj)    # Curve cancelled
    for elem in proj[2].thanSelall:
        try:
            elem.cp = elem.cpori
            del elem.cpori
        except AttributeError:
            pass
        elem.__class__ = thandr.ThanLine

        proj[2].thanCanvas.delete(elem.thanTags[0])
        lt = proj[1].thanLayerTree
        lay = lt.dilay[elem.thanTags[1]]
        if lay != lt.thanCur: lay.thanTkSet(proj[2].than)
        elem.thanTkDraw(proj[2].than)
        if lay != lt.thanCur: lt.thanCur.thanTkSet(proj[2].than)

    thanModEnd(proj, T["%d curves were succesfully decurved."] % len(proj[2].thanSelall))
