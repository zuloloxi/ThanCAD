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
This module provides for the commands of the tool menu.
"""

from math import atan2, hypot
import copy
import p_ggen, p_ggeom, p_ganneal
from p_gmath import thanNear2
from p_ggeom import area
from p_gtri import hull
import thandr, thanobj, thantkdia
from thanvar import Canc
from thanopt import thancadconf
from thantrans import T
from . import thancomsel, thanundo


def thanToolSimplif(proj):
    "Simplifies a line."
    from .thancommod import thanModEnd, thanModCanc, thanModCancSel
    ThanLine = thandr.ThanLine
    name = "LINESIMPLIFICATION"
    lss = proj[1].thanObjects[name]
    if len(lss) == 0:
        objold = []
        s = thanobj.LineSimplification()
    else:
        objold = [(name, lss[0])]
        s = copy.deepcopy(lss[0])
    objnew = [(name, s)]
    strd = proj[1].thanUnits.strdis

    #def prt2(lab, val):
    #    proj[2].thanPrts(lab)
    #    proj[2].thanPrts(val, "info1")

    while True:
        i = s.algs.index(s.choAlg)
        #prt2("Max mean xy error=", strd(s.entXYmean))
        #prt2(" / Max absolute xy error=", strd(s.entXY))
        #prt2(" /\n", "")
        #prt2("Max absolute z error=", strd(s.entXYmean))
        #prt2(" / Max absolute xy error=", strd(s.entZ))
        #prt2(" /\n", "")
        #prt2("Simplification method=", s.algsdesc[i])
        #prt2("\n", "")

        statonce = "Max mean xy error: %s / Max absolute xy error: %s /\n"\
                    "Max absolute z error: %s / Keep original lines: %s /\n"\
                   "Simplification method: %s" % \
                   (strd(s.entXYmean), strd(s.entXY), strd(s.entZ), s.choKeep, s.algsdesc[i])
        proj[2].thanPrt(statonce)

        res = thancomsel.thanSelectOr(proj, standalone=False, filter=lambda e:isinstance(e, ThanLine),
              optionname="settings", optiontext="s=settings")
        if res == Canc: return thanModCanc(proj)
        if res == "s":
            thanModCancSel(proj)   #The user did not select anything so cancel current (empty) selection
            w = thantkdia.ThanSimplificationSettings(proj[2], vals=s.toDialog(), cargo=(proj, s.algsdesc, s.algs))
            if w.result is None:
                proj[2].thanPrtCan()  #Inform user that the dialog was cancelled
            else:
                s.fromDialog(w.result)
            continue
        break
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    delelems = set()
    newelems = set()
    for lin1 in elems:
        cp = __lineSimplify(lin1.cp, s.entXYmean, erabsmax=s.entXY, zerabsmax=s.entZ, alg=s.choAlg)
        lin2 = ThanLine()
        lin2.thanSet(cp)
        if s.choKeep:
            proj[1].thanElementTag(lin2)
        else:
            lin2.thanTags = lin1.thanTags
            delelems.add(lin1)
        newelems.add(lin2)

    lss[:] = [s]
    if s.choKeep: selelems = elems
    else:         selelems = newelems
    thanundo.thanReplaceRedo(proj, delelems, newelems, selelems)
    proj[1].thanDoundo.thanAdd("simplify", thanundo.thanReplaceRedo, (delelems, newelems, selelems, {}, objold, objnew),
                                           thanundo.thanReplaceUndo, (delelems, newelems, selold  , {}, objold, objnew))
    thanModEnd(proj)


def __lineSimplify(cp, ermeanmax=0.15, erabsmax=0.20, zerabsmax=0.10, alg="RDP"):
    "Approximate the line with fewer points keeping the error controlled."
    temp = [(i,)+tuple(c1) for i,c1 in enumerate(cp)]
    r = p_ggeom.lineSimplify3d(temp, ermeanmax, erabsmax, zerabsmax, alg)
    temp = [c1[1:] for c1 in r]
    return temp


__disint = 20.0
__dismin = 0.1
def thanToolInterpolate(proj):
    "Simplifies a line."
    from .thancommod import thanModEnd, thanModCanc, thanModCancSel
    global __disint, __dismin
    disint = __disint
    dismin = __dismin
    ThanLine = thandr.ThanLine
    strd = proj[1].thanUnits.strdis
    while True:
        statonce = "Interpolation XY distance=%s / Min point distance allowed=%s" % \
                   (strd(disint), strd(dismin))
        proj[2].thanPrt(statonce)
        res = thancomsel.thanSelectOr(proj, standalone=False, filter=lambda e:isinstance(e, ThanLine),
              optionname="settings", optiontext="s=settings")
        if res == Canc: return thanModCanc(proj)
        if res == "s":
            thanModCancSel(proj)   #The user did not select anything so cancel current (empty) selection
            t = T["Interpolation distance (enter=%s): "] % (strd(disint),)
            res = proj[2].thanGudGetPosFloat(t, disint)
            if res == Canc: continue
            t = T["Min point distance (enter=%s): "] % (strd(dismin),)
            res1 = proj[2].thanGudGetPosFloat(t, dismin)
            if res1 == Canc: continue
            disint = res
            dismin = res1
            continue
        break
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    delelems = set()
    newelems = set()
    for lin1 in elems:
        cp = list(iterdis2(lin1.cp, disint, dismin))
        lin2 = ThanLine()
        lin2.thanSet(cp)
        lin2.thanTags = lin1.thanTags
        delelems.add(lin1)
        newelems.add(lin2)
    selelems = newelems
    __disint = disint
    __dismin = dismin

    thanundo.thanReplaceRedo(proj, delelems, newelems, selelems)
    proj[1].thanDoundo.thanAdd("interpolate", thanundo.thanReplaceRedo, (delelems, newelems, selelems),
                                           thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)


def iterdis2(a, dd, dismin=0.0):
    "Iterate through polyline a, returning a point every d units distance."
    for a, b in p_ggen.iterby2(a):
        xa,ya,za = a[:3]
        xb,yb,zb = b[:3]
        d = hypot(xb-xa, yb-ya)
        for d1 in p_ggen.frange(0.0, d-dismin, dd):
#            print "iterdis2: %15.3f%15.3f" % (d1, d)
            x = xa + (xb-xa)/d*d1
            y = ya + (yb-ya)/d*d1
            z = za + (zb-za)/d*d1
            yield x, y, z
    yield xb, yb, zb


def thanToolHull(proj):
    "Finds the convex hull of a line."
    from .selutil import thanSelMultlines
    from .thancommod import thanModEnd, thanModCanc
    lins = thanSelMultlines(proj, 1, T["Select lines to find their convex hull:\n"])
    if lins == Canc: return thanModCanc(proj)    # Hull cancelled
    cp = []
    for lin1 in lins: cp.extend(lin1.cp)
    u = hull(cp)
    if u is None: return thanModCanc(proj, T["Degenerate convex hull."])
    elem = thandr.ThanLine()
    elem.thanSet(u)
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)
    thanModEnd(proj)


def thanToolCen(proj):
    "Finds the centroid lines."
    from .selutil import thanSelMultlines
    from .thancommod import thanModEnd, thanModCanc
    lins = thanSelMultlines(proj, 1, T["Select lines to find their centroid:\n"])
    if lins == Canc: return thanModCanc(proj)    # centroid cancelled
    n = proj[1].thanVar["dimensionality"]
    xr = range(n)
    xr3 = range(2, n)
    iterby2 = p_ggen.iterby2
    sum = [0.0]*n
    s =  0.0
    for lin1 in lins:
        for a,b in iterby2(lin1.cp):
            cc = [(a[i]+b[i])*0.5 for i in xr]
            dd = hypot(b[0]-a[0], b[1]-a[1])
            for i in xr3: dd += hypot(dd, b[i]-a[i])
            for i in xr: sum[i] += cc[i]*dd
            s += dd
    if s == 0.0: return thanModEnd(proj, T["No centroid for zero length lines."])
    for i in xr: sum[i] /= s
    elem = thandr.ThanPoint()
    elem.thanSet(sum)
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)
    thanModEnd(proj)


def thanToolDist(proj):
    "Computes the distance between 2 points shown by the user."
    c1 = proj[2].thanGudGetPoint(T["First point: "])
    if c1 == Canc: return proj[2].thanGudCommandCan()    # Distance cancelled
    c2 = proj[2].thanGudGetLine(c1, T["Next point: "])
    if c2 == Canc: return proj[2].thanGudCommandCan()    # Distance cancelled
    dx = c2[0]-c1[0]
    dy = c2[1]-c1[1]
    strdis = proj[1].thanUnits.strdis
    strdir = proj[1].thanUnits.strdir
    mes = "Dx=%s   Dy=%s   theta=%s\nD=%s" % (strdis(dx), strdis(dy),
        strdir(atan2(dy, dx)), strdis(hypot(dx,dy)))
    proj[2].thanGudCommandEnd(mes, "info")


def thanToolArea(proj):
    "Computes the area of a polygon defined by the user."
    from .thancomdraw import getpol
    cs = getpol(proj)
    if cs == Canc: return proj[2].thanGudCommandCan()    # Area cancelled
    a = area(cs)
    strdis = proj[1].thanUnits.strdis
    mes = "Area=%s" % strdis(a)
    proj[2].thanGudCommandEnd(mes, "info")


def thanToolAngle(proj):
    "Computes the angle among 3 points; the second points is the top of the angle."
    than = proj[2].than
    g2l = than.ct.global2Local

    cc = proj[2].thanGudGetPoint(T["First point (corner): "])
    if cc == Canc: return proj[2].thanGudCommandCan()      # Angle cancelled

    c1 = proj[2].thanGudGetLine(cc, T["First side (or direction angle): "])
    if c1 == Canc: return proj[2].thanGudCommandCan()      # Angle cancelled
    theta1 = atan2(c1[1]-cc[1], c1[0]-cc[0])
    r = hypot(c1[1]-cc[1], c1[0]-cc[0]) * 0.5
    than.dc.create_line(g2l(cc[0], cc[1]), g2l(c1[0], c1[1]), fill="blue", tags=("e0",))

    theta2 = proj[2].thanGudGetArc(cc, r, theta1, T["Second side (or direction angle): "])
    if theta2 == Canc:
        than.dc.delete("e0")
        return proj[2].thanGudCommandCan()  # Angle cancelled

    strang = proj[1].thanUnits.strang
    mes = "theta=%s" % strang(theta2-theta1)
    than.dc.delete("e0")
    proj[2].thanGudCommandEnd(mes, "info")


def thanToolOsnap(proj):
    "Displays a dialog for the drafting settings."
    d = thantkdia.ThanTkOsnap(proj[2], thancadconf.thanOsnapModes, thancadconf.thanBOSN, title="Drafting Settings")
    if d.result is None:
        proj[2].thanGudCommandCan()
    else:
        thancadconf.thanOsnapModes.clear()
        thancadconf.thanOsnapModes.update(d.result)
        proj[2].thanGudCommandEnd()


def thanToolId(proj):
    "Shows the coordinates of a point chosen by the user."
    c1 = proj[2].thanGudGetPoint(T["Specify point: "])
    if c1 == Canc: return proj[2].thanGudCommandCan()           # Id command was cancelled
    strcoo = proj[1].thanUnits.strcoo
    s = ["%s: %s" % (T["World xyz"], strcoo(c1))]
    cosyses = proj[1].thanObjects["COSYS"]
    if len(cosyses) > 0:
        cosys = cosyses[0]
        px, py, _ = cosys.project(c1)
        s.append("%s: %.3f %.3f" % (T["Image xy (mm)"], px, py))
    for im in proj[2].thanImages:
        try:               px, py = im.thanGetPixCoor(c1)       # Clipped image coordinates
        except IndexError: continue
        px, py = im.thanGetPixCoorori(c1)                       # Full image coordinates
        s.append("%s: %d %d" % (T["Pixel xy"], px, py))
        break
    proj[2].thanGudCommandEnd("\n".join(s), "info")


def thanToolTextfind(proj):
    "Searches for text."
    st = proj[2].thanGudGetText(T["Enter text to search for: "])
    if st == Canc: return proj[2].thanGudCommandCan()    # find was cancelled
    elems = []
    i = 0
    it = __gettext(proj, st)
    while True:
        i, stat = __getnext(proj, elems, i, st, it)           # Next ThanText to show
        if i == -1: return                                    # No elements found
        res = __getTextfindOpts(proj, elems[i][0], i, stat)
        if res == Canc: return proj[2].thanGudCommandCan()    # find was cancelled
        if res == "n": i+=1; continue
        if res == "p": i-=1; continue
        xymm = list(elems[i][0].getBoundBox())
        dx, dy = xymm[2]-xymm[0], xymm[3]-xymm[1]
        xymm[0] -= dx; xymm[2] += dx
        xymm[1] -= dy; xymm[3] += dy
        proj[1].viewPort[:] = proj[2].thanGudZoomWin(xymm)
        proj[2].thanAutoRegen(regenImages=True)
        if res == "": return proj[2].thanGudCommandEnd()

def __getnext(proj, elems, i, st, it):
    "Decide what ThanText to show to the user."
    strcoo = proj[1].thanUnits.strcoo
    if i < len(elems):               # Just return saved ThanText element
        elem, tfull = elems[i]
        stat = "'%s' at %s\n" % (tfull, strcoo(elem.cc))
        return i, stat
    for elem, tfull in it:           # Try to locate another ThanText Element:
        elems.append((elem, tfull))  # ..Element found
        i = len(elems) - 1
        stat = "'%s' at %s\n" % (tfull, strcoo(elem.cc))
        return i, stat
    if elems:                        # ..No more elements found
        stat = "'%s': %s.\n" % (st, T["No more occurrences were found"])
        i -= 1
        return i, stat
    else:                            # ..No more elements; in fact no elements have been found
        stat = "'%s': %s." % (st, T["not found"])
        proj[2].thanGudCommandEnd(stat, "can")
        return -1, None

def __gettext(proj, st):
    "Text element in active layers; generator."
    dilay = proj[1].thanLayerTree.dilay
    TT = thandr.ThanText
    PN = thandr.ThanPointNamed
    DA = thandr.ThanDimali
    for lay in dilay.values():    #works for python2,3
        if lay.thanAtts["frozen"].thanVal: continue
        for elem in lay.thanQuad:
            if isinstance(elem, TT) and st in elem.text: yield elem, elem.text
            if isinstance(elem, PN) and st in elem.name: yield elem, elem.name
            if isinstance(elem, DA) and st in elem.distext: yield elem, elem.distext

def __getTextfindOpts(proj, elem, i, statonce):
    "Gets text find options."
    if i > 0:
        stat1 = T["Press enter for zoom and finish (zoomto/next/previous) <enter>: "]
    else:
        stat1 = T["Press enter for zoom and finish (zoomto/next) <enter>: "]
    stat = statonce+stat1
    while True:
        res = proj[2].thanGudGetText(stat)
        if res == Canc: return Canc                       # find text was cancelled
        res = res.strip().lower()
        if res == "": return res
        n = len(res)
        if res == "zoomto"[:n]: return "z"
        if res == "next"[:n]:   return "n"
        if i > 0 and res == "previous"[:n]: return "p"
        stat = "Invalid option. Try again.\n" + stat1


def thanToolOptline(proj):
    "Find optimum line which passes from points and other elements."
    from .thancommod import thanModEnd, thanModCanc
    ThanLine = thandr.ThanLine
    ThanPoint = thandr.ThanPoint
    comname = "optline"
    strd = proj[1].thanUnits.strdis
    filt = lambda e: isinstance(e, ThanPoint) or isinstance(e, ThanLine)  #This includes ThanPointNamed, ThanLineFilled, ThanCurve, ThanSpline
    statonce = T["Please select points, lines, splines that the optimum line will pass through"]
    proj[2].thanPrt(statonce, "info1")
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=filt)
    if res == Canc: return thanModCanc(proj)
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    delelems = set()
    newelems = set()
    cc = []
    for e in elems:
        if isinstance(e, ThanPoint):
            cc.append(e.cc)
        else:    #ThanLine
            try:    cp = e.cpori   #To accommodate ThanSpline
            except: cp = e.cp
            cc.extend(cp)

    #test degenerate case
    if len(cc) < 2: return thanModCanc(proj, T["Objects with at least 2 distinct points are required"])
    c1 = cc[0]
    for c2 in cc[1:]:
        if not thanNear2(c1, c2): break
    else:
        return thanModCanc(proj, T["Objects with at least 2 distinct points are required"])

    p, vt, rmsey = p_ganneal.fitline_simple(cc, "auto")   #Fit a line to points
    c1, c2 = p_ganneal.fitline_endpoints(cc, p, vt)
    cp = [list(cc[0]), list(cc[0])]
    cp[0][:2] = c1
    cp[1][:2] = c2
    lin2 = ThanLine()
    lin2.thanSet(cp)
    proj[1].thanElementTag(lin2)
    newelems.add(lin2)

    selelems = elems
    thanundo.thanReplaceRedo(proj, delelems, newelems, selelems)
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo, (delelems, newelems, selelems),
                                        thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj, "RMSE={}".format(strd(rmsey)), "info1")
