# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

Package which processes commands entered by the user.
This module processes commands for educational/research purposes.
"""
from math import atan2, hypot, pi
import collections
from p_gmath import dpt
import p_ggen, p_gtri
import thandr, thancomdraw
from thanvar import Canc, thanShowFile
from thantrans import T, Tarch, Tmatch
import thancomsel, thancomfile
from thancommod import thanModEnd, thanModCanc, thanModReplaceRedo, thanModReplaceUndo
from thantkdia import ThanElemtext, ThanBcplan


def thanEduRect(proj):
    "Draws a closed line in the shape of a rectangle associates with text."
    c1 = proj[2].thanGudGetPoint(T["First point: "])
    if c1 == Canc: return                 # Rectangle cancelled

    c2 = proj[2].thanGudGetRect(c1, T["Second point: "])
    if c2 == Canc: return                # Rectangle cancelled
    x1, y1 = c1[:2]
    x2, y2 = c2[:2]
    if x2 > x1: x1, x2 = x2, x1
    if y2 > y1: y1, y2 = y2, y1
    c1[:2] = x1, y1
    c2 = list(c1); c2[:2] = x2, y1
    c3 = list(c1); c3[:2] = x2, y2
    c4 = list(c1); c4[:2] = x1, y2

    elem = thandr.ThanLine()
    elem.thanSet([c1, c2, c3, c4, c1])
    elem.thanTags = ("e0", )
    elem.thanTkDraw(proj[2].than)
    win = ThanElemtext(proj[2], [None, ""], cargo=proj)
    proj[2].thanTkSetFocus()
    if win.result == None:
        proj[2].thanCanvas.delete("e0")
        return proj[2].thanGudCommandCan()
    try: elem.thanCargo
    except: elem.thanCargo = {}
    elem.thanCargo["edu"] = win.result[1]
    proj[2].thanCanvas.delete("e0")
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)
    proj[1].thanEdus[elem] = True
    proj[2].thanGudCommandEnd()


def thanEduEdit(proj):
    "Edit the associated text with a ThanCad element."
    proj[2].thanSelems.clear()
    proj[2].thanSelems.update(proj[1].thanEdus.keys())
    elem = proj[2].thanGudGetSnapElem(T["Choose site to edit: "])
    proj[2].thanSelems.clear()
    if elem == Canc: return proj[2].thanGudCommandCan()
    t = elem.thanCargo["edu"]
    win = ThanElemtext(proj[2], [None, t], cargo=proj)
    proj[2].thanTkSetFocus()
    if win.result == None: return proj[2].thanGudCommandCan()
    elem.thanCargo["edu"] = win.result[1]
    proj[2].thanGudCommandEnd()



def thanEduFplan(proj):
    "Compute an automated floorplan."
    import thantkdia, thandr.thanobject
    t = thantkdia.ThanFplan(proj[2], vals=None, cargo=proj)
    v = t.result
    del t
    if v == None: return proj[2].thanGudCommandCan()   # Floor plan was cancelled
    fps = proj[1].thanObjects["FLOORPLAN"]
    if len(fps) == 0: fps.append(thandr.thanobject.ThanFplan())
    fps[0].run(proj, v)
    thanModEnd(proj)  # 'Reset color' has already been called, but it is called again for only 2..
                      # ..elements, so it is fast

def thanEdubiocityplan(proj):
    "Asks the user to create bicoclimatic city plan."
    bcps = proj[1].thanObjects["BIOCITYPLAN"]
    if len(bcps) == 0: bcps.append(thandr.thanobject.ThanBiocityplan())
    bcp = bcps[0]
    t = ThanBcplan(proj[2], vals=bcp.toDialog(proj), cargo=proj)
    v = t.result
    del t
    if v == None: return proj[2].thanGudCommandCan()     # City plan was cancelled
    bcp.fromDialog(proj, v)
    bcps[0] = bcp
    proj[1].thanTouch()                    #Drawing IS modified
    if v.doPrepro:
        dtms = proj[1].thanObjects["DTMLINES"]
        if len(dtms) == 0: return proj[2].thanGudCommandCan(T["Can't preprocess: No DTM has been defined!"])
        dtm = dtms[0]
        proj[2].thanPrt(Tarch["Please wait, preprocessing may take several minutes.."])
        bcp.pc.pol.build_cache(dtm, proj[2].thanPrt)
        bcp.pc.repairState()
        fn = proj[0].parent / proj[0].namebase + ".cache"
        proj[2].thanPrt("%s %s  ..." % (Tarch["Saving preprocessing results to"], fn))
        try:
            with open(fn, "w") as fw:
                bcp.pc.pol.write_cache(fw)
        except Exception, why:
            proj[2].thanPrter("%s %s: %s" % (Tarch["Warning: Could not save preprocessing results to"], fn, why))
        return proj[2].thanGudCommandEnd()
    else:
        if bcp.pc.pol.roadenx == None: return proj[2].thanGudCommandCan(Tarch["Please do preprocessing and retry."])
        for i in xrange(v.entMult):            #Run multiple times
            bcp.run(proj)
            bcp.tkDraw(proj, bcp.pc.state)     #thanTouch is implicitely called
            bcp.wrState(proj)
        return proj[2].thanGudCommandEnd()

def __biodirlines(e):
    "Filters alaments that can be used as cutting edges."
    from thandr import ThanLine, ThanCurve, ThanLineFilled
    if isinstance(e, ThanCurve): return False
    if isinstance(e, ThanLineFilled): return False
    return isinstance(e, ThanLine)


def thanEduBioazim(proj):
    "Computation of the azimuth of roads (lines) for bioclimatic analysis."
    prt = proj[2].thanPrt
    prt(Tarch["This command computes statistics of the azimuth of roads (lines) for bioclimatic evaluation of city plans."], "info")
    ncat = proj[2].thanGudGetInt2(Tarch["Number of azimuth categories (enter=4): "], default=4, limits=(2, None), statonce="", strict=True)
    if ncat == Canc: return proj[2].thanGudCommandCan()    # azimuth computation was cancelled
    prt(Tarch["Select roads to process:"])
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=__biodirlines)
    if res == Canc: return thanModCanc(proj)               # azimuth computation was cancelled
    roads = proj[2].thanSelall
    selold = proj[2].thanSelold
    dth = 180.0/ncat
    dsum = collections.Counter()
    isum = collections.Counter()
    roadc = collections.defaultdict(set)
    for e in roads:
        for ca, cb in p_ggen.iterby2(e.cp):
            dy, dx = cb[1]-ca[1], cb[0]-ca[0]
            th = dpt(atan2(dy, dx))
            if th > pi: th -= pi
            d = hypot(dy, dx)
            n = int(th*180.0/pi/dth+0.5) % ncat     #When n == ncat, then the azimuth is in the category of the azimuth of n=0
            dsum[n] += d
            isum[n] += 1
            roadc[n].add((tuple(ca), tuple(cb)))
    proj[1].thanDoundo.thanAdd("edubiodir", thanModReplaceRedo, ((), (), roads),
                                            thanModReplaceUndo, ((), (), selold))
    fw = __openbio(proj, proj[2].thanPrter)
    if fw != None:
        prt = lambda s, tags=(), fw=fw: fw.write("%s\n" % (s,))
    prt("Γωνία (deg)\t  Πλήθος οδών\t  Συνολικό μήκος", "info")
    for i in xrange(ncat):
        s = "%11.1f\t%13d\t%16.1f" % (dth*i, isum[i], dsum[i])
        prt(s.replace(".", ","), "info1")
    prt("Εύρος μετρήσεων για κάθε γωνία ± %.1f deg" % (dth*0.5,))
    fn = None
    if fw != None:
        fn = p_ggen.path(fw.name)
        fw.close()
    __biocolor(proj, dth, ncat, roadc, fn)
    if fn != None: thanShowFile(proj, fn, "Statistics of the azimuth of roads")
    thanModEnd(proj)


def __biocolor(proj, dth, ncat, roadc, fn):
    "Create a new drawing with the roads coloured according to azimuth."
    from thaneng.thanprofile import defDxf
    from thancom.thancomview import thanZoomExt
    layers = []
    colors = []
    for i in xrange(ncat):
        th = dth*i
        layers.append("theta%d_%03.1f" % (i, th))
        if th < 22.5:      colors.append(3)        #green
        elif th < 90-22.5: colors.append(2)        #yellow
        elif th < 90+22.5: colors.append(5)        #blue
        else:              colors.append(2)        #yellow
    projnew, dxf = defDxf(proj, layers, colors)

    for i in xrange(ncat):
        dxf.thanDxfSetLayer(layers[i])
        for ca, cb in roadc[i]:
            dxf.thanDxfPlot3(ca[0], ca[1], ca[2], 3)
            dxf.thanDxfPlot3(cb[0], cb[1], cb[2], 2)
    dxf.thanDxfPlot(0, 0, 999)
    projnew[1].thanLayerTree.thanDictRebuild()
#    projnew[2].geometry("%dx%d" % (640, 480))
    projnew[2].update()
    projnew[2].thanRegen()
    thanZoomExt(projnew)
    if fn != None:
        fn = fn.parent / fn.namebase + ".thcx"
        thancomfile.thanFileSavePath(projnew, fn)


def __openbio(proj, prt):
    "Open files to save the azimuth results."
    name = proj[0].namebase
    par = p_ggen.path(proj[0].parent)
    try:
        for i in xrange(1000):
            p = par / ("%s%03d.txt" % (name, i))
            if not p.exists():
                fw = open(p, "w")
                return fw
        raise IOError, "It seems the directory is full"
    except IOError, why:
        prt("%s:\n%s" % (Tmatch["Could not write results to file."], why), "can")
        return None
