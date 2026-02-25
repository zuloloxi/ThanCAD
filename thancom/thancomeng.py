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
This module processes commands related to engineering.
"""

from math import hypot, fabs
import copy, weakref
import p_ggen, p_gtkwid, p_gtri, p_gvec, p_gearth, p_ggeod, p_gvarcom, p_godop
import thaneng, thandr, thanobj, thantkdia
from thanopt import thancadconf
from thanvar import Canc, thanfiles, ThanLayerError, thanNearElev
from thantrans import T
from thansupport import thanTextSize, thanToplayerCurrent
from . import thancomsel, thancomview, thanundo, thancomfile
from .thancommod import thanModEnd, thanModCanc, thanModCancSel
from .selutil import thanSelMultquads


def thanGreecePerimeter(proj):
    "Draw the perimeter of Greece."
    try:
        thanToplayerCurrent(proj, "greece", current=False, moncolor="cyan")
        thanToplayerCurrent(proj, "greece/perimeter", current=True)
        thanToplayerCurrent(proj, "greece/points", current=True, moncolor="yellow", hidename=False, hideheight=False)
    except (ThanLayerError, ValueError) as e:
        terr = T["Could not create or set current layer 'greece/perimeter' or layer 'greece/points':\n{}"].format(str(e))
        return proj[2].thanGudCommandCan(terr)
    thanToplayerCurrent(proj, "greece/perimeter", current=True)
    for cp in thaneng.thanIterGreece(proj[1].geodp):
        e = thandr.ThanLine()
        e.thanSet(cp)
        proj[1].thanElementAdd(e)
        e.thanTkDraw(proj[2].than)
    thanToplayerCurrent(proj, "greece/points", current=True)
    for (nam, cp) in thaneng.thanPoints(proj[1].geodp):
        e = thandr.ThanPointNamed()
        e.thanSet(cp, nam)
        proj[1].thanElementAdd(e)
        e.thanTkDraw(proj[2].than)
    thancomview.thanZoomExt(proj)  #This also calls thanGudCommandEnd()


def thanEngGrid(proj):
    "Makes a set of crosses which indicate a grid."
    scale = proj[2].thanGudGetPosFloat(T["Engineering scale 1:x (enter=500): "], 500.0)
    if scale == Canc: return proj[2].thanGudCommandCan()                 # Grid cancelled
    c1 = proj[2].thanGudGetPoint(T["First grid corner (Quadrilateral/Elements): "], options=("quadrilateral","elements"))
    if c1 == Canc: return proj[2].thanGudCommandCan()                    # Grid cancelled
    if c1 == "q":
        cp = getquad(proj)
        if cp == Canc: return proj[2].thanGudCommandCan()                # Grid cancelled
    elif c1 == "e":
        __gridinelements(proj, scale)
        return
    else:
        c3 = proj[2].thanGudGetRect(c1, T["Other grid corner: "])
        if c3 == Canc: return proj[2].thanGudCommandCan()                # Grid cancelled
        c2 = list(c1); c2[0] = c3[0]
        c4 = list(c3); c4[0] = c1[0]
        cp = [c1, c2, c3, c4]
    grid = thaneng.ThanGrid()
    newelems = grid.thanDo(proj, scale, 0.0, 0.0, 1, cp)
    ans = proj[2].thanGudGetYesno(T["Keep grid boundary (Yes/No/<Yes>): "], default="yes")
    if ans == Canc: return proj[2].thanGudCommandCan()
    if ans:
        e = thandr.ThanLine()
        cp.append(list(cp[0]))
        e.thanSet(cp)
        proj[1].thanElementAdd(e)
        e.thanTkDraw(proj[2].than)
        newelems.append(e)

    delelems = ()
    proj[1].thanDoundo.thanAdd("enggrid", thanundo.thanReplaceRedo, (delelems, newelems, None),
                                          thanundo.thanReplaceUndo, (delelems, newelems, None))
    proj[2].thanGudCommandEnd()


def getquad(proj):
    "Get a convex quadrilateral form the user."
    than = proj[2].than
    g2l = than.ct.global2Local
    c1 = proj[2].thanGudGetPoint(T["First quadrilateral grid corner: "])
    if c1 == Canc: return Canc                   # Grid cancelled
    while True:
        c2 = proj[2].thanGudGetLine(c1, T["Second quadrilateral grid corner: "])
        if c2 == Canc: return Canc               # Grid cancelled
        temp = than.dc.create_line(g2l(c1[0], c1[1]), g2l(c2[0], c2[1]),
            fill="blue", tags=("e0",))
        while True:
            c3 = proj[2].thanGudGetLine2(c1, c2, T["Third quadrilateral grid corner (Undo): "],
                options=("undo",))
            if c3 == Canc: than.dc.delete("e0"); return Canc
            if c3 == "u": than.dc.delete("e0"); break
            temp = than.dc.create_line(g2l(c2[0], c2[1]), g2l(c3[0], c3[1]),
                fill="blue", tags=("e0","e1"))
            c4 = proj[2].thanGudGetLine2(c1, c3, T["Fourth quadrilateral grid corner (Undo): "],
                options=("undo",))
            if c4 == Canc: than.dc.delete("e0"); return Canc
            if c4 == "u": than.dc.delete("e1"); continue
            temp = than.dc.create_line(g2l(c2[0], c2[1]), g2l(c3[0], c3[1]),
               fill="blue", tags=("e0","e1"))
            than.dc.delete("e0")
            return [c1, c2, c3, c4]
        if c3 == "u": continue


def __gridinelements(proj, scale):
    "Select existing (closed) quadrilaterals and draw grids in them."
    pinakides = thanSelMultquads(proj, 1, T["Select at least 1 or more quadrilaterals to draw grid into:\n"], strict=False)
    if pinakides == Canc: return thanModCanc(proj)                       # Grid cancelled
    selold = proj[2].thanSelold

    grid = thaneng.ThanGrid()
    newelems = []
    for pin in pinakides:
        elems = grid.thanDo(proj, scale, 0.0, 0.0, 1, pin.cp)
        newelems.extend(elems)

    delelems = ()
    selelems = set(pinakides)
    proj[1].thanDoundo.thanAdd("enggrid", thanundo.thanReplaceRedo, (delelems, newelems, selelems),
                                          thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)    # 'Reset color' is not needed since the grids and numbers..
                        # are already drawn. So if a large number of elements..
                        # There is room for optimisation!


def thanEngTrace(proj):
    "Traces semiautomatically a curve in a bitmap image."
    im, cw = proj[2].thanGudGetImPoint(T["Start point of trace: "],
        ptol=thancadconf.thanBSEL//2, threshold=127)
    if cw == Canc: return proj[2].thanGudCommandCan()
    proj[2].thanImageCur = weakref.proxy(im)
    jx, iy = im.thanGetPixCoor(cw)
    res = thaneng.thanTrace(proj, jx, iy)
    if res == Canc: return proj[2].thanGudCommandCan()
    return proj[2].thanGudCommandEnd()


def __filter3(e):
    "Select a line with at least 3 points and the first 3 non-colinear."
    if not isinstance(e, thandr.ThanLine): return False
    if isinstance(e, thandr.ThanCurve): return False
    if len(e.cp) < 3: return False
    a, b, c = map(p_gvec.Vector2, e.cp[:3])    #works for python2,3
    ab = b-a
    ab = ab / abs(ab)
    bc = c-b
    bc = bc / abs(bc)
    t = fabs(ab|bc)
    return t < 0.90       #Angle should be > acos(0.9) = 25 deg


def thanEngInterchange(proj):
    "Make a highway intersection."
    from thanpackages.komb.kom import thanMainTcad
    lin1 = thancomsel.thanSelect1(proj, T["Select a line with 3 point to fit highway interchange\n"], filter=__filter3)
#    lin1 = thanSel1line(proj, T["Select a line with 3 point to fit highway interchange\n"])
    if lin1 == Canc: return proj[2].thanGudCommandCan()
    thanMainTcad(proj, lin1)
    return proj[2].thanGudCommandEnd()


def thanEngDem(proj):
    "Manage DEMs."
    mes = T["DEM: Load/Arcinfo adf directory load/load Global dem/draw Boundary/"
            "draw Nodes/draw Contours/Export nodes/eXport to code (enter=L): "]
    res = proj[2].thanGudGetOpts(mes, default="L", options=("Load", "Arcinfo", "Global",
        "Boundary", "Nodes", "Contours", "Export", "Xport"))
    if res == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
    if res == "l":
        return thanDemLoad(proj)
    if res == "a":
        return thanDemLoadAdf(proj)
    if res == "g":
        return thanDemLoadGdem(proj)
    elif res == "b":
        if thanNoDtmdems(proj, iterdtm=False): return proj[2].thanGudCommandCan(T["No DEM has been defined!"])
        elems, newport, oldport = __demdrawbou(proj, iterDtmdems(proj, iterdtm=False))
        if elems is None: return proj[2].thanGudCommandCan(T["No DEM or Global DEM frame has been loaded!"])
        proj[1].thanDoundo.thanAdd("demload", __demdrawbouRedo, (elems, newport, (), ()),
                                              __demdrawbouUndo, (elems, oldport, (), ()))
        return proj[2].thanGudCommandEnd()
    elif res == "n":
        if thanNoDtmdems(proj, iterdtm=False): return proj[2].thanGudCommandCan(T["No DEM has been defined!"])
        if thanundo.thanRetainUndo(proj, 1): return proj[2].thanGudCommandCan()     # DEM operation was cancelled
        proj[2].thanPrt(T["Please wait.."])
        for dem in iterDtmdems(proj, iterdtm=False):
            __demdrawnod(proj, dem)
        proj[2].thanRegen()
        return proj[2].thanGudCommandEnd()
    elif res == "c":
        if thanNoDtmdems(proj, iterdtm=False): return proj[2].thanGudCommandCan(T["No DEM has been defined!"])
        return proj[2].thanGudCommandEnd("Not implemented :(")
        tris = proj[1].thanObjects["TRIANGULATION"]
        if len(tris) == 0: return thanModCanc(proj, T["No triangulation has been defined!"])
        ret = plotcontours(proj, tris)
        if ret == Canc: return proj[2].thanGudCommandCan()                 # Contours cancelled
        return thanModEnd(proj)
    elif res == "e":
        if thanNoDtmdems(proj, iterdtm=False): return proj[2].thanGudCommandCan(T["No DEM has been defined!"])
        c1 = proj[2].thanGudGetPoint(T["First window corner (All): "],
            T["Please define window to select points or All\n"], options=("All",))
        if c1 == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
        if c1 != "a":
            c2 = proj[2].thanGudGetRect(c1, T["Other window corner: "])
            if c2 == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
            xymm = p_gvarcom.Xymm()
            xymm.includePoint(c1)
            xymm.includePoint(c2)
            #xymm = min(c1[0], c2[0]), min(c1[1], c2[1]), max(c1[0], c2[0]), max(c1[1], c2[1])
        fn, fw = thancomfile.thanTxtopen(proj, T["Choose .syn file to save points to"], suf=".syn", mode="w")
        if fn == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
        proj[2].thanPrt(T["Please wait.."])
        n = 0
        for demobj in iterDtmdems(proj, iterdtm=False):
            dem = demobj.dtm
            if c1 == "a":
                proj[2].thanPrt(T["Warning: Global DEMs' nodes are exported only for those frames of the global DEMs"], "can1")
                proj[2].thanPrt(T["whoich aready loaded loaded by the user through the 'dtmz' or 'dtmline' commands"])
                for cc in dem.iterNodes():
                    n += 1
                    fw.write("%-10d%15.3f%15.3f%15.3f\n" % (n, cc[0], cc[1], cc[2]))
            else:
                dem.thanGetWin(xymm)      #For GDEMs load the frames inside xymm; for other DEMs does nothing
                dxymm = dem.thanXymm()
                if not xymm.intersectsXymm(dxymm): continue
                #if dxymm[0] > xymm[2]: continue
                #if dxymm[1] > xymm[3]: continue
                #if dxymm[2] < xymm[0]: continue
                #if dxymm[3] < xymm[1]: continue
                for cc in dem.iterNodes(xymm=xymm):
                    if cc not in xymm: continue
                    #if cc[0] < xymm[0] or cc[0] > xymm[2]: continue
                    #if cc[1] < xymm[1] or cc[1] > xymm[3]: continue
                    n += 1
                    fw.write("%-10d%15.3f%15.3f%15.3f\n" % (n, cc[0], cc[1], cc[2]))
        fw.close()
        return proj[2].thanGudCommandEnd("%d points were exported to %s." % (n, fn), "info")
    elif res == "x":
        filnams = []
        for i,dtmobj in enumerate(iterDtmdems(proj, iterdem=False)):
            filnam = "dtm{}".format(i+1)
            icod, terr = dtmobj.dtm.thanExportToPython(dtmname=filnam, dir=proj[0].parent)
            if icod == 0:
                filnams.append(filnam)
                continue
            proj[2].thanPrt(T["Warning: {}"].format(terr), "can1")
        return proj[2].thanGudCommandEnd("{} dtms were exported to Python code.".format(len(filnams)), "info")
    else:
        assert 0, "Unknown option!"


def __demdrawbou(proj, demobjs):
    "Draw the boundary of all dems and zoom to see all."
    elems = []
    newport = None
    for demobj in demobjs:
        if isinstance(demobj.dtm, p_gearth.GDEM):
            dems = demobj.dtm.cgiarDem.values()   #works for python2,3
            nameprefix = demobj.dtm.name
        else:
            dems = [demobj.dtm]
            nameprefix = ""
        for dem in dems:
            elems1 = __demdrawbou1(proj, dem, nameprefix)
            elems.extend(elems1)
            if newport is None: newport = p_gvarcom.Xymm()
            newport.includeXymm(dem.thanXymm())
    if newport is None: return None, None, None
    oldport = tuple(proj[1].viewPort)             #make distict copy
    newport = proj[2].thanGudZoomWin(newport)     #Returns a tuple
    proj[1].viewPort[:] = newport
    proj[2].thanAutoRegen(regenImages=True)
    return elems, newport, oldport


def __demdrawbou1(proj, dem, nameprefix=""):
    "Draw the boundary (rectangle) and the name of one DEM."
    ca = list(proj[1].thanVar["elevation"])
    cc = list(ca)
    dxymm = dem.thanXymm()
    ca[:2] = dxymm[:2]
    cc[:2] = dxymm[2:]
    cb = list(ca)
    cb[0] = cc[0]
    cd = list(ca)
    cd[1] = cc[1]
    ce = list(ca)
    el = thandr.ThanLine()
    el.thanSet([ca, cb, cc, cd, ce])
    proj[1].thanElementAdd(el)
    el.thanTkDraw(proj[2].than)

    c1, c2 = ca, cc
    theta = 0.0
    t = thandr.ThanText()
    h = (c2[0]-c1[0])/40.0
    ca = list(c1)

    name = dem.filnam + nameprefix
    tb, th = thanTextSize(proj, name, h)
    ca[0] = (c1[0] + c2[0])*0.5 - tb*0.5
    ca[1] = (c1[1] + c2[1])*0.5 - th*0.5

    t.thanSet(name, ca, h, theta)
    proj[1].thanElementAdd(t)
    t.thanTkDraw(proj[2].than)
    return el, t


def __demdrawbouRedo(proj, elems, port, demsold, demsnew):
    "Redo the demdrawboundary command."
    if port is not None:
        proj[1].viewPort[:] = proj[2].thanGudZoomWin(port)
        proj[2].thanAutoRegen(regenImages=True)
    delelems = ()
    thanundo.thanReplaceRedo(proj, delelems, elems)
    for dem in demsold: proj[1].thanObjects["DEMUSGS"].remove(dem)
    for dem in demsnew: proj[1].thanObjects["DEMUSGS"].append(dem)


def __demdrawbouUndo(proj, elems, port, demsold, demsnew):
    "Redo the demdrawboundary command."
    if port is not None:
        proj[1].viewPort[:] = proj[2].thanGudZoomWin(port)
        proj[2].thanAutoRegen(regenImages=True)
    delelems = ()
    thanundo.thanReplaceUndo(proj, delelems, elems)
    for dem in demsnew: proj[1].thanObjects["DEMUSGS"].remove(dem)
    for dem in demsold: proj[1].thanObjects["DEMUSGS"].append(dem)


def __demdrawnod(proj, demobj):
    "Draw the nodes of the DEM."
    proj[1].viewPort[:] = proj[2].thanGudZoomWin(demobj.dtm.thanXymm())
    PN = thandr.ThanPointNamed
    ea = proj[1].thanElementAdd
    for i,cc in enumerate(demobj.dtm.iterNodes()):
        el = PN()
        el.thanSet(cc, str(i+1))
        ea(el)


def thanDemLoadold(proj):
    "Loads many USGS DEM stored in geotif format and draws them."
    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkwid.thanGudGetReadFile(proj[2], ".tif", T["Choose DEM (USGS) tif file"],
              initialdir=fildir, multiple=True)
        if fns is None: return proj[2].thanGudCommandCan()            # Image canceled
        demobjs = []
        nopened = 0
        for fi in fns:
            dem = p_gtri.ThanDEMusgs()
            ok, ter = dem.thanSet(fi)
            if ok:
                demobj = thanobj.ThanDEMusgs()
                demobj.dtm = dem
                demobjs.append(demobj)
                nopened += 1
            else:
                tit = T["Error while loading %s"] % (fi.basename(),)
                p_gtkwid.thanGudModalMessage(proj[2], ter, tit)   # (Gu)i (d)ependent
        if nopened > 0: break
    elems, newport, oldport = __demdrawbou(proj, demobjs)     #This calls thanTouch implicitelly
    for demobj in demobjs: proj[1].thanObjects["DEMUSGS"].append(demobj)
    proj[1].thanDoundo.thanAdd("demload", __demdrawbouRedo, (elems, newport, (), demobjs),
                                          __demdrawbouUndo, (elems, oldport, (), demobjs))
    proj[2].thanGudCommandEnd()


def thanDemLoad(proj):
    "Loads many USGS DEMs stored in geotif format, ESRI BIL/HDR, Erdas img, ArcInfo adf, or ERDAS ascii/txt, and draws them."
    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkwid.thanGudGetReadFile(proj[2], (".tif .bil .img .hdr .adf .asc .txt"),
              T["Choose DEM tif (USGS), bil (ESRI BIL/HDR), img (Erdas Imagine), adf (Arc/Info) or asc (ERDAS ascii) files"],
              initialdir=fildir, multiple=True)
        if fns is None: return proj[2].thanGudCommandCan()            # Image canceled
        demobjs = []
        nopened = 0
        for fi in fns:
            ext = fi.ext.lower()
            if ext == ".bil" or ext == ".hdr":
                dem = p_gtri.ThanDEMbil()
                ok, ter = dem.thanSet(fi)
            elif ext == ".img":
                dem = p_gtri.ThanDEMbil()
                ok, ter = dem.thanSet(fi)
            elif ext == ".adf":
                dem = p_gtri.ThanDEMbil()
                ok, ter = dem.thanSet(fi)
            elif ext == ".asc" or ext == ".txt":
                dem = p_gtri.ThanDEMusgs()
                ok, ter = dem.importErdasAsc(fi)
            else:
                dem = p_gtri.ThanDEMusgs()
                ok, ter = dem.thanSet(fi)
            if ok:
                demobj = thanobj.ThanDEMusgs()
                demobj.dtm = dem
                demobjs.append(demobj)
                nopened += 1
            else:
                tit = T["Error while loading %s"] % (fi.basename(),)
                p_gtkwid.thanGudModalMessage(proj[2], ter, tit)   # (Gu)i (d)ependent
        if nopened > 0: break
    elems, newport, oldport = __demdrawbou(proj, demobjs)     #This calls thanTouch implicitelly
    for demobj in demobjs: proj[1].thanObjects["DEMUSGS"].append(demobj)
    proj[1].thanDoundo.thanAdd("demload", __demdrawbouRedo, (elems, newport, (), demobjs),
                                          __demdrawbouUndo, (elems, oldport, (), demobjs))
    proj[2].thanGudCommandEnd()


def thanDemLoadAdf(proj):
    "Loads a full directory tree of ArcInfo adf DEMs, and draws them."
    fildir = thanfiles.getFiledir()
    while True:
        dir1 = p_gtkwid.xinpDir(proj[2], T["Choose directory of DEM adf (Arc/Info) files"],
              mustexist=True, default=fildir)
        if dir1 is None: return proj[2].thanGudCommandCan()            # Image canceled
        dir1 = p_ggen.path(dir1)
        dirs = list(dir1.walkdirs())
        dirs.insert(0, dir1)
        demobjs = []
        nopened = 0
        for dir1 in dirs:
            fns = dir1.files("*.adf")
            fns.extend(dir1.files("*.ADF"))
            if len(fns) == 0: continue
            for fi in fns:
                dem = p_gtri.ThanDEMbil()
                ok, ter = dem.thanSet(fi)
                if ok:
                    demobj = thanobj.ThanDEMusgs()
                    demobj.dtm = dem
                    demobjs.append(demobj)
                    nopened += 1
                    break
                else:
                    pass  #Complain only if none of the .adf files can be opened
            else:
                tit = T["Error while loading %s"] % (fi.basename(),)   #No .adf files opened: complain about the last one
                p_gtkwid.thanGudModalMessage(proj[2], ter, tit)   # (Gu)i (d)ependent
        if nopened > 0: break
    elems, newport, oldport = __demdrawbou(proj, demobjs)     #This calls thanTouch implicitelly
    for demobj in demobjs: proj[1].thanObjects["DEMUSGS"].append(demobj)
    proj[1].thanDoundo.thanAdd("demloadadf", __demdrawbouRedo, (elems, newport, (), demobjs),
                                             __demdrawbouUndo, (elems, oldport, (), demobjs))
    proj[2].thanGudCommandEnd()


def thanDemLoadSrtmold(proj):
    "Loads many parts of the SRTM as USGS DEM stored in geotif format and draws them."
    proj[2].thanPrt(T["Select rectangular area for which SRTM is needed:"])
    ca = proj[2].thanGudGetPoint(T["First window corner: "])
    if ca == Canc: return proj[2].thanGudCommandCan()      # SRTM cancelled
    cb = proj[2].thanGudGetRect(ca, T["Other window corner: "])
    if cb == Canc: return proj[2].thanGudCommandCan()      # SRTM cancelled
    xa, ya = ca[:2]
    xb, yb = cb[:2]
    xymm = min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)
    gdem = p_gearth.SRTMGDEM()
    dems, nloaded, notfound, notcovered = gdem.thanGetWin(xymm)
    demsinthancad = set(demobj.dtm for demobj in proj[1].thanObjects["DEMUSGS"])
    dems = set(dems)
    demsnew = dems.difference(proj[1].thanObjects["DEMUSGS"])
    ndup = len(dems) - len(demsnew)
    if len(dems) == 0:
        return proj[2].thanGudCommandCan(T["No SRTM DEMs were loaded (%d duplicate, %d not found)."] % (ndup, notfound))
    demobjs = []
    for dem in demsnew:
        demobj = thanobj.ThanDEMusgs()
        demobj.dtm = dem
        demobjs.append(demobj)
    elems, newport, oldport = __demdrawbou(proj, demobjs)     #This calls thanTouch implicitelly
    for demobj in demobjs: proj[1].thanObjects["DEMUSGS"].append(demobj)
    proj[1].thanDoundo.thanAdd("demload", __demdrawbouRedo, (elems, newport, (), demobjs),
                                          __demdrawbouUndo, (elems, oldport, (), demobjs))
    proj[2].thanGudCommandEnd(T["%d SRTM DEMs were loaded (%d duplicate, %d not found)."] % (len(demsnew), ndup, notfound))


def thanDemLoadGdem(proj):
    "Loads many parts of the SRTM as USGS DEM stored in geotif format and draws them."
    mes = T["Load global DEM: Srtm/srtM1usgs/Aster/aW3d30/Greekc/Vlsogreekc/tandem-xIdem/tandem-xiHem/tandem-Xdem (enter=S): "]
    res = proj[2].thanGudGetOpts(mes, default="S", options=("Srtm", "M1usgs", "W3d30", "Aster", "Greekc", "VLSO", "Idem", "Hem", "Xdem"))
    if res == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
    if   res == "s":
        name = "SRTM"
        #geodp = p_ggeod.UTMercator(EOID=p_ggeod.NAD83_1997, zone=10, north=True)
    elif res == "m":
        name = "SRTM1USGS"
    elif res == "a":
        name = "ASTER"
    elif res == "w":
        name = "AW3D30"
    elif res == "g":
        name = "GREEKC"
    elif res == "v":
        name = "VLSO_GREEKC"
    elif res == "i":
        name = "TANIDEM"
    elif res == "h":
        name = "TANIDEMHEM"
    else:
        mes = T["tandem-Xdem resolution: 90m/30m/12m (enter=9): "]
        res = proj[2].thanGudGetOpts(mes, default="9", options=("90", "30", "12"))
        if res == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
        if   res == "9":
            name = "TANXDEM90"
        elif res == "3":
            name = "TANXDEM30"
        else:
            name = "TANXDEM12"
    dtm = p_gearth.gdem(name)    #This is empty initially so that it doesn't cost much memory and time
    for demobj in proj[1].thanObjects["DEMUSGS"]:
        if isinstance(demobj.dtm, dtm.__class__):
            return proj[2].thanGudCommandCan(T["%s gdem is already loaded!"] % (dtm.name,))
    dtm.thanSetProjection(proj[1].geodp)
    demobj = thanobj.ThanDEMusgs()
    demobj.dtm = dtm
    proj[1].thanObjects["DEMUSGS"].append(demobj)
    proj[1].thanTouch()
    proj[1].thanDoundo.thanAdd("demload", __demdrawbouRedo, ((), None, (), [demobj]),
                                          __demdrawbouUndo, ((), None, (), [demobj]))
    proj[2].thanGudCommandEnd(T["%s DEM was loaded."] % (name,))


def thanDemImageDir(proj):
    "Locate the directory where missing image files for DEMs can be found."
    for elem in proj[1].thanObjects["DEMUSGS"]:
        if elem.dtm.im is None: break
    else:
        return proj[2].thanGudCommandCan(T["No image files are missing."])
    tit = T["Select directory for missing image files of DEMs"],
    fildir = thanfiles.getFiledir()
    while True:
        dn = p_gtkwid.thanGudGetDir(proj[2], tit, initialdir=fildir)
        if dn is None: return proj[2].thanGudCommandCan()        # location canceled
        dn = p_ggen.path(dn)
        nmiss = 0
        delelems = []
        newelems = []
        for elem in proj[1].thanObjects["DEMUSGS"]:
            if elem.dtm.im is not None: continue
            fi = dn / p_ggen.path(elem.filnam).basename()
            dem = p_gtri.ThanDEMusgs()
            ok, ter = dem.thanSet(fi)
            newelem = thanobj.ThanDEMusgs()
            newelem.dtm = dem
            if not ok:
                nmiss += 1
            else:
                newelems.append(newelem)
                delelems.append(elem)
        assert not (len(newelems) == 0 and nmiss == 0), "It should have been found!!"
        if len(newelems) > 0: break
        p_gtkwid.thanGudModalMessage(proj[2], T["No image files were found. Try again."], tit)
    elems, newport, oldport = __demdrawbou(proj, newelems)     #This calls thanTouch implicitelly
    for elem in delelems: proj[1].thanObjects["DEMUSGS"].remove(elem)
    for elem in newelems: proj[1].thanObjects["DEMUSGS"].append(elem)
    proj[1].thanDoundo.thanAdd("demdirectory", __demdrawbouRedo, (elems, newport, delelems, newelems),
                                               __demdrawbouUndo, (elems, oldport, delelems, newelems))
    if nmiss > 0: mes = T["Not all image files were found."]
    else:         mes = None
    proj[2].thanGudCommandEnd(mes)


def thanEngDtmmake(proj):
    "Asks the user to select lines to be used as DTM."
#    from p_gtri import ThanDTMlines
    proj[2].thanCom.thanAppend(T["Select lines to generate DTM:\n"], "info1")
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=lambda e: isinstance(e, thandr.ThanLine))
    if res == Canc: return thanModCanc(proj)     # Make dtm was cancelled
    dext = proj[2].thanGudGetPosFloat(T["Extension length (max horiz. distance of contour lines) (enter=200m): "], default=200.0)
    if dext == Canc: return thanModCanc(proj)    # DTM lines was cancelled

    dtm = p_gtri.ThanDTMlines(dxmax=dext/5, dext=dext)
    thanAddLines(dtm, proj[2].thanSelall)
    ok, ter = dtm.thanRecreate()
    if not ok: return thanModCanc(proj, T["Error creating DTM: %s"]%ter)
    dtmobj = thanobj.ThanDTMlines()
    dtmobj.dtm = dtm
    proj[1].thanObjects["DTMLINES"][:] = [dtmobj]
    proj[1].thanTouch()
#    thanToplayerCurrent(proj, "dtmlines", current=True, moncolor="white")
#    for cp in dtm.thanLines:
#        e = thandr.ThanLine()
#        e.thanSet(cp)
#        proj[1].thanElementAdd(e)
#        e.thanTkDraw(proj[2].than)
    return thanModEnd(proj, T["%d generated line segments in DTM."] % len(dtm.thanLines), "info")


def thanAddLines(self, elems):
        "Add the lines of list/set of ThanCad elements (usually the elements of selection)."
        ThanLine = thandr.ThanLine
        for e in elems:
            if isinstance(e, ThanLine): self.thanAddLine1(e.cp)


def thanNoDtmdems(proj, iterdtm=True, iterdem=True):
    "Returns true if there is at least 1 DTM or DEM."
    return len(list(iterDtmdems(proj, iterdtm, iterdem))) == 0

def iterDtmdems(proj, iterdtm=True, iterdem=True):
    "Iterate through dtms."
    if iterdtm:
        for dtm in proj[1].thanObjects["DTMLINES"]:
            if dtm.thanIsNormal():
                yield dtm
    if iterdem:
        for dem in proj[1].thanObjects["DEMUSGS"]:
            if dem.thanIsNormal():
                yield dem


def thanPointZ(proj, cp):
    "Calculate the z coordinate of a point when multiple DTMs/DEMs are available."
    return p_gtri.thanPointZ((obj.dtm for obj in iterDtmdems(proj)), cp)


def thanLineZ(proj, cp):
    "Calculate the z coordinates along the line cp when multiple DTMs/DEMs are available."
    return p_gtri.thanLineZ((obj.dtm for obj in iterDtmdems(proj)), cp)


def thanLineZendpointstoo(proj, cp):
    "Calculate the z coordinates along the line cp when multiple DTMs/DEMs are available."
    return p_gtri.thanLineZendpointstoo((obj.dtm for obj in iterDtmdems(proj)), cp)


def thanEngDtmpoint1(proj):
    "Compute the z of a user selected point."
    if thanNoDtmdems(proj): return thanModCanc(proj, T["Can't compute z: No DTM has been defined!"])
    cp = proj[2].thanGudGetPoint(T["Specify a point: "])
    if cp == Canc: return thanModCanc(proj)     # Point cancelled
    z = thanPointZ(proj, cp)
    if z is None: return thanModCanc(proj, T["Can't compute z: No DTMs/DEMs are near the selected point."])
    cp = list(cp)
    cp[2] = z
    return thanModEnd(proj, T["Point with z: %s"] % proj[1].thanUnits.strcoo(cp), "info")


def thanEngDtmline(proj):
    "Compute the z along a line."
    if thanNoDtmdems(proj): return thanModCanc(proj, T["Can't compute z: No DTM has been defined!"])
    proj[2].thanCom.thanAppend(T["Select lines to transform to 3d:\n"], "info1")
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=lambda e: isinstance(e, thandr.ThanLine))
    if res == Canc: return thanModCanc(proj)    # DTM lines was cancelled
    smooth = proj[2].thanGudGetYesno(T["Smooth profile (e.g. existing roads) (enter=No): "], default=False)
    if smooth == Canc: return thanModCanc(proj)    # DTM lines was cancelled

    prt = proj[2].thanPrter1
    nlin = 0
    for e in proj[2].thanSelall:
        if smooth: ni, cp = thanLineZ(proj, e.cp)                #This is for existing roads -> the profile is smooth
        else:      ni, cp = thanLineZendpointstoo(proj, e.cp)    #This is for any other path -> the profile is rough
        if ni == -1:
            prt(T["Can't compute z: No DTMs/DEMs are near the selected line."])
        else:
            if ni > 0: prt(T["The z of some line points couldn't be computed: %d interpolations"] % ni)
            e.thanSet(cp)
            nlin += 1
            proj[1].thanTouch()
    if nlin == 0: return thanModEnd(proj, T["No lines were transformed; they are too far away the DTMs/DEMs."])
    proj[2].thanGudSetSelDel()                         # Delete selected lines from canvas
    proj[2].thanGudDrawElemsMany(proj[2].thanSelall)   # Redraw the lines (with new coordinates)
    proj[2].thanGudSetSelElem1(proj[2].thanSelall)     # Mark the lines as selected
    return thanModEnd(proj, T["%d/%d lines were transformed to 3d."]%(nlin, len(proj[2].thanSelall)), "info")


def thanEngDtmpoints(proj):
    "Compute the z of multiple points."
    if thanNoDtmdems(proj): return thanModCanc(proj, T["Can't compute z: No DTM has been defined!"])
    proj[2].thanCom.thanAppend(T["Select points to transform to 3d:\n"], "info1")
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=lambda e: isinstance(e, thandr.ThanPoint))
    if res == Canc: return thanModCanc(proj)    # DTM lines was cancelled
    prt = proj[2].thanPrter1
    nlin = 0
    for e in proj[2].thanSelall:
        z = thanPointZ(proj, e.cc)
        if z is None:
            prt(T["Can't compute z: No DTM lines are near the selected point."])
        else:
            e.cc[2] = z
            nlin += 1
            proj[1].thanTouch()
    if nlin == 0: return thanModEnd(proj, T["No points were transformed; they are too far away the DTM."])
    proj[2].thanGudSetSelDel()                         # Delete selected lines from canvas
    proj[2].thanGudDrawElemsMany(proj[2].thanSelall)   # Redraw the lines (with new coordinates)
    proj[2].thanGudSetSelElem1(proj[2].thanSelall)     # Mark the lines as selected
    return thanModEnd(proj, T["%d/%d points were transformed to 3d."]%(nlin, len(proj[2].thanSelall)), "info")


__qpst = p_ggen.Struct(name="ThanCad quick profile settings", akly=10.0)
def thanEngQuickprofile(proj):
    "Creates a (3D) line profile into a new drawing."
    s = __qpst
    strd = proj[1].thanUnits.strdis
    while True:
        proj[2].thanPrt(T["Select 3d lines to make quick profiles:"], "info1")
        proj[2].thanPrt("Elevation scale factor={}".format(strd(s.akly)))
        res = thancomsel.thanSelectOr(proj, standalone=False, filter=lambda e: isinstance(e, thandr.ThanLine),
            optionname="settings", optiontext="s=settings")
        if res == Canc: return thanModCanc(proj)           # Profile was cancelled
        if res == "s":
            thanModCancSel(proj)   #The user did not select anything so cancel current (empty) selection
            t = T["Elevation scale factor (enter={}): "].format(strd(s.akly))
            res = proj[2].thanGudGetPosFloat(t, s.akly)
            if res == Canc:
                 proj[2].thanPrt("")   #If use pressed ESQ, then change line from the message ("Elevation scale factor ..")
            else:
                 s.akly = res
            proj[2].thanPrt("")   #Make a blank line sepration line
            continue
        break
    for e in proj[2].thanSelall:
        projnew = thaneng.thanCommonProfile(proj, [e.cp], dscale=s.akly, layers=["p1"], colors=[2])
        cb = e.cp[0]
        j = 1
        aa = ["S"+str(j)]
        xth = [0.0]
        hed = [cb[2]]
        for ca, cb in p_ggen.iterby2(e.cp):
            j += 1
            aa.append("S"+str(j))
            xth.append(xth[-1] + hypot(cb[1]-ca[1], cb[0]-ca[0]))
            hed.append(cb[2])
        cori = list(projnew[1].thanVar["elevation"])
        cori[:2] = 0.0, 0.0
        pf = thanobj.ThanProfile(aa, xth, hed, cori, dscale=s.akly)
        pfs = projnew[1].thanObjects["PROFILE"][:] = [pf]
    return thanModEnd(proj, T["%d profiles were created."]%len(proj[2].thanSelall), "info")


def thanEngTri(proj):
    "Asks the user to select lines to make triangulation from."
    mes = T["Triangulation: Make/Read/Save/draw Contours or"] + "\n" + \
          T["draw Edges/draw Triangles/draw ceNtroids (enter=c): "]
    res = proj[2].thanGudGetOpts(mes, default="C",
        options=("Make", "Read", "Save", "Contours", "Edges", "Triangles", "Ntroids"))
    if res == Canc: return thanModCanc(proj)     # Triangulation was cancelled
    if res == "m":
        return thanEngTrimake(proj)
    elif res == "r":
        fn = proj[0].parent / (proj[0].namebase + ".tri")
        try:
            fr = open(fn, "r")
        except Exception as why:
            return thanModCanc(proj, "Can not read triangulation from %s:\n%s" % (fn, why))
        tri = thanobj.ThanTri()
        tri.readtri(fr)
        fr.close()
        proj[1].thanObjects["TRIANGULATION"][:] = [tri]
        return thanModEnd(proj, "Triangulation was successfully read from %s" % fn, "info")
    elif res == "s":
        tris = proj[1].thanObjects["TRIANGULATION"]
        if len(tris) == 0: return thanModCanc(proj, T["No triangulation has been defined!"])
        fn = proj[0].parent / (proj[0].namebase + ".tri")
        try:
            fw = open(fn, "w")
        except Exception as why:
            return thanModCanc(proj, "Can not write to %s:\n%s" % (fn, why))
        tris[0].writetri(fw)
        fw.close()
        return thanModEnd(proj, "Triangulation was saved in %s" % fn, "info")
    elif res == "c":
        tris = proj[1].thanObjects["TRIANGULATION"]
        if len(tris) == 0: return thanModCanc(proj, T["No triangulation has been defined!"])
        ret = plotcontours(proj, tris)
        if ret == Canc: return proj[2].thanGudCommandCan()                 # Contours cancelled
        return thanModEnd(proj)
    elif res == "e":
        return __tridraw(proj, edges=True)
    elif res == "t":
        return __tridraw(proj, triangles=True)
    elif res == "n":
        return __tridraw(proj, centroids=True)
    else:
        assert 0, "Unknown option!"


def plotcontours(proj, tris):
    "Plots contour lines given a triangulation."
    from p_gtri import ThanYpyka
    dhl = 1.0
    dhx = 5.0
    dmax = 0.0
    dhl = proj[2].thanGudGetPosFloat(T["Contour lines small interval (enter=%.1f): "]%(dhl,), dhl)
    if dhl == Canc: return Canc                 # Contours cancelled
    dhx = proj[2].thanGudGetPosFloat(T["Contour lines big   interval (enter=%.1f): "]%(dhx,), dhx)
    if dhx == Canc: return Canc                 # Contours cancelled
    dmax = proj[2].thanGudGetFloat2(T["Max distance threshold between points, 0.0=No threshold (enter=%.1f): "]%(dmax,), dmax, limits=(0.0, None))
    if dmax == Canc: return Canc                 # Contours cancelled
    prt = proj[2].thanPrter1
    def saveis(icod, cis):
        "Draw a contour line."
        his = cis[0][2]
        if his % dhx < 0.01*dhl: thanToplayerCurrent(proj, "YX", current=True, moncolor="30")
        else:                    thanToplayerCurrent(proj, "YL", current=True, moncolor="34")
        e = thandr.ThanLine()
        e.thanSet(cis)
        if e.thanIsNormal():
            proj[1].thanElementAdd(e)
            e.thanTkDraw(proj[2].than)
    p = ThanYpyka(tris[0].ls, saveis, prt)
    dmax1 = dmax
    if dmax == 0.0: dmax1=1.0e100
    p.ypyka(dhl, dmax1)
    return True


def thanEngTrimake(proj):
    """Asks the user to select lines to make triangulation from.

    Calling thanSelectGen() with filter=... is very time consuming when dealing
    with many points, as it is the case here.
    Thus we select all the elements, which is 10 times faster, but then process
    only lines and points."""
    from thandr import ThanLine, ThanPoint, ThanPointNamed
    proj[2].thanCom.thanAppend(T["Select points/lines to generate triangulation from:\n"], "info1")
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)     # Create triangulation was cancelled

    cp = []
    for e in proj[2].thanSelall:
        if isinstance(e, ThanLine):
            for cc in e.cp:
                cp.append((None, cc[0], cc[1], cc[2]))
        elif isinstance(e, ThanPointNamed):
            cp.append((e.name, e.cc[0], e.cc[1], e.cc[2]))
        elif isinstance(e, ThanPoint):
            cp.append((None, e.cc[0], e.cc[1], e.cc[2]))
    tri = thanobj.ThanTri()
#    ok, ter = tri.make(cp, convex=False, infinite=False)
    ok, ter = tri.make(cp, convex=True, infinite=False)
    if not ok: return thanModCanc(proj, T["Error creating triangulation: %s"]%ter)
    tri.sortlinks()

    proj[2].thanCom.thanAppend("Applying break lines..\n")
    for e in proj[2].thanSelall:
        if isinstance(e, ThanLine):
            for ca, cb in p_ggen.iterby2(e.cp):
                ca = (None, ca[0], ca[1], ca[2])
                cb = (None, cb[0], cb[1], cb[2])
                tri.brkapply(ca, cb)

    n = 0
    for _ in tri.itertriangles(1.0e100): n += 1     #Find all triangles regardless their dimenions
    proj[1].thanObjects["TRIANGULATION"][:] = [tri]
    thanModEnd(proj, T["%d triangles were generated."] % n, "info")
    proj[1].thanTouch()          #Drawing has been modified


def __tridraw(proj, edges=False, triangles=False, centroids=False, aa=False):
    "Draw triangulation."
    tris = proj[1].thanObjects["TRIANGULATION"]
    if len(tris) == 0: return thanModCanc(proj, T["No triangulation has been defined!"])
    tri = tris[0]
    thanToplayerCurrent(proj, "trilines", current=True, moncolor="yellow")
    apmax = 1.0e100     #Iterate through all triangles regardless of their dimenions
    if edges:           #Draw edged as ThanLines
        for ca, cb in tri.iteredges():
            e = thandr.ThanLine()
            e.thanSet([ca, cb])
            proj[1].thanElementAdd(e)
            e.thanTkDraw(proj[2].than)
    if centroids:       #Draw centroids as points
        for ca, cb, cc in tri.itertriangles(apmax):
            cen = [(a+b+c)/3.0 for a,b,c in zip(ca, cb, cc)]  #works for python2,3
            e = thandr.ThanPoint()
            e.thanSet(cen)
            proj[1].thanElementAdd(e)
            e.thanTkDraw(proj[2].than)
    if aa:              #Count the centroids
        ntr = 0
        for ca, cb, cc in tri.itertriangles(apmax):
            cen = [(a+b+c)/3.0 for a,b,c in zip(ca, cb, cc)]  #works for python2,3
            e = thandr.ThanText()
            ntr += 1
            e.thanSet(str(ntr), cen, 1.0, 0.0)
            proj[1].thanElementAdd(e)
            e.thanTkDraw(proj[2].than)
    if triangles:       #Draw triangles as closed ThanLines
        for ca, cb, cc in tri.itertriangles(apmax):
            e = thandr.ThanLine()
            e.thanSet([ca, cb, cc, ca])
            proj[1].thanElementAdd(e)
            e.thanTkDraw(proj[2].than)
    thanModEnd(proj)


def thanEngGeodp(proj):
    """Prompt the user to enter the geodetic projection.

    Please update thandwg.thanExpKml code when adding/modifying geodetic projections to ThanCad."""
    proj[2].thanPrts(T["Current geodetic projection is "], "info1")
    proj[2].thanPrt(proj[1].geodp.pname, "info")
    mes = T["Select geodetic projection: Utm/transverse Mercator/Egsa87/Htrs07 or\nLambert conformal conic/ePsg3294/Identity (enter=E): "]
    res = proj[2].thanGudGetOpts(mes, default="E", options=("Utm", "Mercator", "Egsa87", "Htrs07", "Lambert", "P", "Identity"))
    if res is Canc: return proj[2].thanGudCommandCan()     # Geod operation was cancelled
    if res == "u":
        zone = proj[2].thanGudGetInt2(T["UTM zone (1-60) (enter=34): "], default=34, limits=(1, 60), statonce="", strict=True)
        if zone is Canc: return proj[2].thanGudCommandCan()     # Geod operation was cancelled
        res = proj[2].thanGudGetOpts(T["North/South (enter=N): "], default="N", options=("North", "South"))
        if res is Canc: return proj[2].thanGudCommandCan()     # Geod operation was cancelled
        north = res == "n"
        icodEOID = selEllips(proj)
        if icodEOID is Canc: return proj[2].thanGudCommandCan()     # Geod operation was cancelled
        Lgeodpnew = p_ggeod.params.fromUTM(icodEOID, zone, north)
    elif res == "m":
        return proj[2].thanGudCommandCan("Not yet implemented :(")
    elif res == "e":
        Lgeodpnew = p_ggeod.params.fromEgsa87()
    elif res == "h":
        Lgeodpnew = p_ggeod.params.fromHtrs07()
    elif res == "l":
        return proj[2].thanGudCommandCan("Not yet implemented :(")
    elif res == "p":
        Lgeodpnew = p_ggeod.params.fromEpsg3294()
    else:
        icodEOID = selEllips(proj)
        if icodEOID is Canc: return proj[2].thanGudCommandCan()     # Geod operation was cancelled
        Lgeodpnew = p_ggeod.params.fromGeodetic(icodEOID, angleunit=1)  #Decimal degrees)
    geodpnew = p_ggeod.params.toProj(Lgeodpnew)
    proj[1].Lgeodp = Lgeodpnew
    proj[1].geodp = geodpnew

    for obj in iterDtmdems(proj):
        if hasattr(obj.dtm, "thanSetProjection"):
            obj.dtm.thanSetProjection(proj[1].geodp)

    proj[2].thanPrts(T["Current geodetic projection is "], "info1")
    proj[2].thanPrt(proj[1].geodp.pname, "info")

    proj[1].thanTouch()
    return proj[2].thanGudCommandEnd()


def selEllips(proj):
    "Prompt the user to select geodetic ellipsoid."
    res = proj[2].thanGudGetOpts(T["Select ellipsoid: g=GRS80/w=WGS84/r=Greek87/n=NAD83 (enter=g): "], default="g", options=("g", "w", "r", "n"))
    if res is Canc: return Canc     # Geod operation was cancelled
    if   res == "g": icodEOID = 1
    elif res == "w": icodEOID = 2
    elif res == "r": icodEOID = 101
    else:            icodEOID = 102
    return icodEOID


def thanEngIsoclinal(proj):
    "Create an isoclinal line for road design."
    from .thancommod import thanModEnd, thanModCanc, thanModCancSel
    ThanLine = thandr.ThanLine
    objname = "ISOCLINAL"                  #name of object which holds the parameters
    temp = proj[1].thanObjects[objname]    #Get list of current objects (only 1 object is allowed in the list)
    if len(temp) == 0:                  #No current objects
        namobjsold = []
        obj = thanobj.ThanIsoclinal()   #New object
    else:
        namobjsold = [(objname, temp[0])]     #old list of (name, object) tuples (only 1 is allowed)
        obj = copy.deepcopy(temp[0])    #New object, copy of old
    namobjsnew = [(objname, obj)]             #new list of (name, object) tuples (only 1 is allowed)

    __isokPrintInfo(proj, obj)
    while True:
        ca = proj[2].thanGudGetPoint(T["Icoclinal start point [Settings/Close and save settings]: "], "",
            options=("Settings","Close"))
        if ca == Canc:
            return proj[2].thanGudCommandCan()   # Isoclinal cancelled
        elif ca == "s":    #New settings
            w = thantkdia.ThanDialogIsoclinal(proj[2], vals=obj.toDialog(), cargo=proj)
            if w.result is None:
                proj[2].thanPrtCan()  #Inform user that the dialog was cancelled
            else:
                temp = __isokProcessContours(proj, obj, w.result)
                if temp:
                    obj.fromDialog(w.result)
                    obj.cprocessed = temp
                    __isokPrintInfo(proj, obj)
        elif ca == "c":
            break
        else:
            cb = proj[2].thanGudGetLine(ca, T["Isoclinal Target point: "])
            if cb == Canc: proj[2].thanPrtCan(); continue
            #if ca[2] == 0.0 or cb[2] == 0.0:
            if thanNearElev(ca[2], 0.0) or thanNearElev(cb[2], 0.0):
                proj[2].thanPrt(T["Warning: start or target point has zero elevation. Isoclinal may fail."], "can1")

            if not obj.cprocessed:
                temp = __isokProcessContours(proj, obj, obj.toDialog())
                if not temp: continue
                obj.cprocessed = temp
            isok = p_godop.Isoclinal(obj.syks, obj.entEps)
            diad1, grade1, d1 = isok.findGrade(ca, cb, obj.entStart, obj.entEnd, obj.entStep)
            if d1 < 1e100: break
            proj[2].thanPrt(T["No solution found. Please try again."], "can1")

    if ca == "c":
        newelems = set()   #No isoclinal line will be created
    else:
        proj[2].thanPrt("Best grade={:.2f} %, distance to target={:.2f}".format(grade1, d1))
        #create the isoclinal line
        lin2 = ThanLine()
        lin2.thanSet(diad1)
        proj[1].thanElementTag(lin2)
        newelems = set([lin2])

    delelems = set()
    thanundo.thanReplaceRedo(proj, delelems, newelems, None, {}, namobjsold, namobjsnew)
    proj[1].thanDoundo.thanAdd("isoclinal",
        thanundo.thanReplaceRedo, (delelems, newelems, None, {}, namobjsold, namobjsnew),
        thanundo.thanReplaceUndo, (delelems, newelems, None, {}, namobjsold, namobjsnew))
    print("ThanObjects", proj[1].thanObjects[objname])
    print("namobjsold=", namobjsold)
    print("namobjsnew=", namobjsnew)
    thanModEnd(proj)


def __isokPrintInfo(proj, obj):
    "Print information of isoclinal settings."
    strd = proj[1].thanUnits.strdis
    stra = proj[1].thanUnits.strang
    statonce = "{}={}\n{}={} / {}={}\n{}={}% / {}={}% / {}={}%".format(
        T["Contour lines' layers"], obj.labLaynames,
        T["Distance tolerance to target"], strd(obj.entEps),
        T["Maximum direction change"], stra(obj.entAngle),
        T["Grade search start"],       strd(obj.entStart),
        T["Grade search end"],         strd(obj.entEnd),
        T["Grade search step"],        strd(obj.entStep))
    proj[2].thanPrt(statonce)


def __isokProcessContours(proj, obj, s):
    "Check layers and contours and save to object if successful."
    proj[2].thanPrt(T["Prosessing contour lines.."], "info1")
    lt = proj[1].thanLayerTree
    t = s.labLaynames
    lays = []
    for name1 in t.split(", "):
        lay1 = lt.thanFind(name1)
        if lay1 is None:
            proj[2].thanPrt(T["Error: could not find layer {}"].format(name1), "can")
            return False
        lays.append(lay1)
    return obj.setContoursFromlayers(lays, thandr.ThanLine, T, proj[2].thanPrt)
