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
This module processes commands for educational/research purposes.
"""


import p_ggen, p_gsar, p_gtkuti
import thandr
from thanvar import Canc
from thantrans import T, Tmatch
from thansupport import thanToplayerCurrent

from thanprofflf.thanprotkdia import ThanMatchMult2, ThanMatch23, ThanMatchMult23

mm = p_gtkuti.thanGudModalMessage


def thanEduPointProject(proj):
    "Transforms points with a computed transformation/projection."
    from thancom import thancomsel, thanundo
    from thancom.thancommod import thanModCanc, thanModEnd, thanModCancSel
    ThanLine = thandr.ThanLine
    ThanPoint = thandr.ThanPoint
    ThanPointNamed =  thandr.ThanPointNamed
#    ft = lambda e: isinstance(e, ThanLine) or isinstance(e, ThanPoint)
    prjs = proj[1].thanObjects["PROJECTION"]
    if len(prjs) == 0:
        tra1 = thanCofread(proj, Tmatch["Open file with transformation/projection coefficients"])
        if tra1 == Canc: return thanModCanc(proj) # New transformation definition was cancelled
        if tra1.icodp == 14:          #TerraSar projection
            proj[2].thanPrt(Tmatch["Warning: This projection works only with geocentric GRS80 coordinates."], "info")
            proj[2].thanPrt(Tmatch["         Use projection 15 for EGSA87 coordinates and 16 for HTRS07 coordinates."], "info")
    else:
        tra1 = prjs[0].transformation
    name = tra1.name
    while True:
        proj[2].thanPrt("%s: %s" % (Tmatch["Current transformation"], Tmatch[name]), "info1")
        proj[2].thanPrt(T["Select points to transform:"], "info1")
        res = thancomsel.thanSelectOr(proj, standalone=False,
              optionname="transformation", optiontext=Tmatch["t=new Transformation"])
        if res == Canc: return thanModCanc(proj)
        if res == "t":
            thanModCancSel(proj)   #The user did not select anything so cancel current (empty) selection
            L = thanCofread(proj, Tmatch["Open file with transformation/projection coefficients"])
            if L == Canc: continue # New transformation definition was cancelled
            if L.icodp == 14:          #TerraSar projection
                proj[2].thanPrt(Tmatch["Warning: This projection works only with geocentric GRS80 coordinates."], "info")
                proj[2].thanPrt(Tmatch["         Use projection 15 for EGSA87 coordinates and 16 for HTRS07 coordinates."], "info")
            tra1 = L
            name = tra1.name
            continue
        break
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    tra = thandr.thanobject.ThanProjection(tra1) #FIXME:This must be added to the do/undo mechanism
    prjs[:] = [tra]
    delelems = set()
    newelems = set()
    for e in elems:
        en = e.thanClone()
        en.thanTransform(tra.transform)
        proj[1].thanElementTag(en, cl=None)
        newelems.add(en)
        print "transformed point/element:", en.getInspnt()


    selelems = elems
    thanundo.thanReplaceRedo(proj, delelems, newelems, selelems)
    proj[1].thanDoundo.thanAdd("simplify", thanundo.thanReplaceRedo, (delelems, newelems, selelems),
                                           thanundo.thanReplaceUndo, (delelems, newelems, selold))
    proj[1].thanTouch()      #In case the user only changed the projection, without projecting anything
    thanModEnd(proj)


def thanEduMatch23(proj):
    """Matches a 3d polyline to a 2d polyline using ICP.

    Details in following papers (for now):
    """
    from thanprofflf.thanpropackages.match2 import doMatchOpt23
    from thancom.thancommod import thanModCanc, thanModEnd
    t = ThanMatch23(proj[2], vals=None, cargo=proj)
    v = t.result
    del t
    if v == None: return thanModCanc(proj)          # Match was cancelled
    print "thanEduMatch23(proj): projection code=", v.radProject
    L1, L = doMatchOpt23(proj, gps3d=tuple(v.gps)[0].cp, relori=tuple(v.rel)[0].cp, projcode=v.radProject,
                         disint=v.entDisInt, disrange=v.entDisRange, threshold=v.entThres, maxsteps=v.entSteps,
                         iprojapprox=v.radProjApprox, nplane=(v.entNx,v.entNy,v.entNz), L1=v.projection,
                         itransfapprox=v.radTransfApprox, iazim=1,
                         prt=proj[2].thanPrt, prtbo=proj[2].thanPrtbo, prter=proj[2].thanPrter)

    if L == None: return thanModEnd(proj)     # ICP failed
    for L2, col2, lay2 in (L1, "white", "first_approx"), (L, "green", "icp"):
        thanToplayerCurrent(proj, lay2, moncolor=col2)
        ereln = thandr.ThanLine()
        ereln.thanSet([L2.project(c1) for c1 in tuple(v.gps)[0].cp])
        proj[1].thanElementAdd(ereln)
        ereln.thanTkDraw(proj[2].than)
    proj[1].thanObjects["PROJECTION"][:] = [thandr.thanobject.ThanProjection(L)]
    thanModEnd(proj)                # 'Reset color' has already been called, but it is called again for only 1..
                                    # ..element, so it is fast


def thanEduMatchMult23(proj):
    """Matches a set of 3d polylines to a set of 2d polyline using ICP.

    April 5, 2011: Multiple match23 without first approximation was implemented.
    Details in following papers (for now):
    """
    from thanprofflf.thanpropackages.match2 import doMatchMult23Opt
    from thancom.thancommod import thanModCanc, thanModEnd
    t = ThanMatchMult23(proj[2], vals=None, cargo=proj)
    v = t.result
    del t
    if v == None: return thanModCanc(proj)          # Match was cancelled

    gps = [gps1.cp for gps1 in v.gps]
    rel = [rel1.cp for rel1 in v.rel]
    L1, L, relgps = doMatchMult23Opt(proj, gps3d=gps, relori=rel, projcode=v.radProject,
                         disint=v.entDisInt, disrange=v.entDisRange, threshold=v.entThres, maxsteps=v.entSteps,
                         iprojapprox=v.radProjApprox, nplane=(v.entNx,v.entNy,v.entNz), L1=v.projection,
                         itransfapprox=v.radTransfApprox, iazim=1,
                         ibefore=0, icorr=1, iafter=0,
                         prt=proj[2].thanPrt, prtbo=proj[2].thanPrtbo, prter=proj[2].thanPrter)

    __drawCurveCorresp(proj, relgps)

    if L == None: return thanModEnd(proj)     # ICP failed
    for L2, col2, lay2 in (L1, "white", "first_approx"), (L, "green", "icp"):
        if L2 is L1: continue     #No first approximation for the moment
        thanToplayerCurrent(proj, lay2, moncolor=col2)
        for gps1 in gps:
            ereln = thandr.ThanLine()
            ereln.thanSet([L2.project(c1) for c1 in gps1])
            proj[1].thanElementAdd(ereln)
            ereln.thanTkDraw(proj[2].than)
    proj[1].thanObjects["PROJECTION"][:] = [thandr.thanobject.ThanProjection(L)]
    thanModEnd(proj)                # 'Reset color' has already been called, but it is called again for only 1..
                                    # ..element, so it is fast


__dim = set()
def dimitra(proj, icom):
    return
    if icom in __dim: return
    __dim.add(icom)
    pr = proj[2].thanPrtbo
    if icom == "2d":
        pr("Curve Matching Algorithms, Dimitra Vassilaki, PhD Candidate", "info")
        pr("Lab of Photogrammetry, NTUA, 2008-2012", "info")
    elif icom == "23d":
        pr("Curve Matching Algorithms, Dimitra Vassilaki, PhD Candidate", "info")
        pr("Lab of Photogrammetry, NTUA, 2008-2012", "info")
    elif icom == "3d":
        pr("3D curve Matching Algorithms, Dimitra Vassilaki, PhD Candidate", "info")
        pr("Lab of Photogrammetry, NTUA, 2008-2012", "info")
    elif icom == "mid":
        pr("ICP mid axis Algorithm, Dimitra Vassilaki, PhD Candidate", "info")
        pr("Lab of Photogrammetry, NTUA, 2008-2012", "info")
    elif icom == "mult2d":
        pr("Multiple Curve Matching Algorithms, Dimitra Vassilaki, PhD Candidate", "info")
        pr("Lab of Photogrammetry, NTUA, 2008-2012", "info")


def thanEduMatch2(proj):
    "Matches 2 2d polylines using ICP."
    from thancom.thancommod import thanModCanc
    from thanprofflf.thanprotkdia import ThanMatch2d
    t = ThanMatch2d(proj[2], vals=None, cargo=proj)
    v = t.result
    del t
    if v == None: return thanModCanc(proj)          # Match was cancelled
    __eduDoMatchx(proj, is3d=False, lins=(p_ggen.any1(v.gps), p_ggen.any1(v.rel)),
        disint=v.entDisInt, disrange=v.entDisRange, threshold=v.entThres, maxsteps=v.entSteps,
        centrApprox=v.radAlign==0, iazim=v.radAzim, distApprox=v.radAlign==1)


def thanEduMatch3(proj):
    "Matches two3d polylines using ICP."
    from thancom.thancommod import thanModCanc
    from thanprofflf.thanprotkdia import ThanMatch2d
    t = ThanMatch2d(proj[2], vals=None, cargo=proj, title=Tmatch["Global Matching of 3D Curves"])
    v = t.result
    del t
    if v == None: return thanModCanc(proj)          # Match was cancelled
    __eduDoMatchx(proj, is3d=True, lins=(p_ggen.any1(v.gps), p_ggen.any1(v.rel)),
        disint=v.entDisInt, disrange=v.entDisRange, threshold=v.entThres, maxsteps=v.entSteps,
        centrApprox=v.radAlign==0, iazim=v.radAzim, distApprox=v.radAlign==1)


def thanEduMatch2commandline(proj):
    "Matches two 2d polylines using ICP."
    dimitra(proj, "2d")
    __eduMatchx(proj, is3d=False)


def thanEduMatch3commandline(proj):
    "Matches two 3d polylines using ICP."
    dimitra(proj, "3d")
    return __eduMatchx(proj, is3d=True)


def __eduMatchx(proj, is3d):
    "Matches two 2d or 3d polylines using ICP."
    from thancom.thancommod import thanModCanc
    from thancom.selutil import thanSel2linesOrder
    lins = thanSel2linesOrder(proj, T["Select lines to match. At first select the reference line:\n"],
        T["Now select the line to be moved towards the reference line:\n"])
    if lins == Canc: return thanModCanc(proj)          # Match was cancelled
    centrApprox = proj[2].thanGudGetYesno("Include 1st approximation - centroid algorithm (enter=no): ", default="no")
    if centrApprox == Canc: return thanModCanc(proj)   # Match was cancelled
    if centrApprox:
        proj[2].thanPrt("Choose azimouth approximation:", "info1")
        proj[2].thanPrt("1. Average of first and last node", "info1")
        proj[2].thanPrt("2. Exhaustive search of all azimouths", "info1")
        proj[2].thanPrt("3. Average azimouth of whole curve", "info1")
        iazim = proj[2].thanGudGetInt2("Choice (enter=1):", default=1, limits=(1, 3))
        if iazim == Canc: return thanModCanc(proj)     # Match was cancelled
        iazim -= 1
        distApprox = False
    else:
        distApprox = proj[2].thanGudGetYesno("Include 1st approximation - distance algorithm (enter=no): ", default="no")
        if distApprox == Canc: return thanModCanc(proj)   # Match was cancelled
        iazim = None
    disint = 1.0
    disrange = 200.0
    threshold = 0.2
    maxsteps = 50
    __eduDoMatchx(proj, is3d, lins, disint, disrange, threshold, maxsteps,
                  centrApprox, iazim, distApprox)


def __eduDoMatchx(proj, is3d, lins, disint, disrange, threshold, maxsteps,
    centrApprox, iazim, distApprox):
    "Matches two 2d or 3d polylines using ICP."
    from thancom.thancommod import thanModEnd
    from thanprofflf.thanpropackages.match2 import doMatchOpt
    tra1, trac, gr = doMatchOpt(is3d, lins[0].cp, lins[1].cp,
        disint, disrange, threshold, maxsteps, centrApprox, iazim, distApprox,
        proj[2].thanCanvas.update_idletasks, proj[2].thanPrt, proj[2].thanPrtbo, proj[2].thanPrter,
        proj[1].thanUnits.strdis, proj[1].thanUnits.strang)

    if centrApprox or distApprox:
        if tra1 == None: return thanModEnd(proj)     # First approx failed
        ereln = thandr.ThanLine()

        if is3d and distApprox: ereln.thanSet([tra1.calc(c1) for c1 in lins[1].cp])
        else: ereln.thanSet([tra1.calc2d(c1) for c1 in lins[1].cp])

        thanToplayerCurrent(proj, "approx1", moncolor="white")
        proj[1].thanElementAdd(ereln)
        ereln.thanTkDraw(proj[2].than)
    if trac == None: return thanModEnd(proj)     # ICP failed
    thanToplayerCurrent(proj, "icp", moncolor="green")
    ereln = thandr.ThanLine()
    if is3d: ereln.thanSet([trac.calc(c1) for c1 in lins[1].cp])
    else:    ereln.thanSet([trac.calc2d(c1) for c1 in lins[1].cp])
    proj[1].thanElementAdd(ereln)
    ereln.thanTkDraw(proj[2].than)
    if is3d:
        import thaneng
        gps = [cp[:3] for cp in gr]
        rel = [trac.calc(cp[3:6]) for cp in gr]
        thaneng.thanCommonProfile(proj, (gps, rel), ("reference", "icp"), (4, 3))
    __savesim(proj, trac, gr, lins, is3d)
    thanModEnd(proj)                # 'Reset color' has already been called, but it is called again for only 1..


def __savesim(proj, trac, gr, lins, is3d):
    "Save the similarity transformation and the point pairs that led to it."
    from p_ggen import path
    name = proj[0].namebase
    par = path(proj[0].parent)
    for i in xrange(1000):
        p = par / ("%s%03d.sim" % (name, i))
        if not p.exists(): break
    else:
        proj[2].thanCom.thanAppend("Could not write transformation to file.")
        return
    try:
        fw = open(p, "w")
        trac.write(fw)
        fw.write("\n\n#X,Y,Z of reference line,   x, y, z of secondary line,   weight xy, weight z\n")
        form = 8*"%30.20e" + "\n"
        for xg,yg,zg,xr,yr,zr,xyok,zok in gr:
            fw.write(form % (xg,yg,zg,xr,yr,zr,xyok,zok))
        fw.close()
    except IOError:
        proj[2].thanCom.thanAppend("Could not write transformation to file.")

    from p_gsar import similar2lsm, similar3lsm
    if is3d: tra, er, erh = similar3lsm(gr)
    else:    tra, er, erh = similar2lsm(gr)
    proj[2].thanPrt("Testing direct similarity transform:")
    proj[2].thanPrt("erxy=%.2f   erh=%.2f" % (er, erh))
    thanToplayerCurrent(proj, "icp_direct", moncolor="darkgreen")
    ereln = thandr.ThanLine()
    print "__savesim: is3d=", is3d
    if is3d: ereln.thanSet([tra.calc(c1) for c1 in lins[1].cp])
    else:    ereln.thanSet([tra.calc2d(c1) for c1 in lins[1].cp])
#    print "thanedu: len(lins[1]=", len(lins[1].cp), "len(ereln)=", len(ereln.cp)
#    print "thanedu: isnormal:", ereln.thanIsNormal()
    if not ereln.thanIsNormal():
        proj[2].thanPrter("ERROR: ICP LINE IS DEGENERATE.")
        return
    proj[1].thanElementAdd(ereln)
    ereln.thanTkDraw(proj[2].than)


def thanEduMatchMult2(proj):
    """Matches multiple 2d polylines using ICP.

    Details in following papers (for now):

    """
    from thancom.thancommod import thanModCanc, thanModEnd
    from thanprofflf.thanpropackages.match2 import doMatchMultOpt
    t = ThanMatchMult2(proj[2], vals=None, cargo=proj)
    v = t.result
    if v == None: return thanModCanc(proj)          # Match was cancelled
    gps = [lin1.cp for lin1 in v.gps]
    rel = [lin1.cp for lin1 in v.rel]
    is3d = False
    iafter = v.radAlignAfter
    tra1, hugps, hurel, tra1s, trac, gpsrel = doMatchMultOpt(is3d=False, gps=gps, relori=rel,
        disint=v.entDisInt, disrange=v.entDisRange, threshold=v.entThres, maxsteps=v.entSteps,
        ibefore=v.radAlignBefore, icorr=v.radMethod, iafter=iafter,
        prt=proj[2].thanPrt, prtbo=proj[2].thanPrtbo, prter=proj[2].thanPrter,
        strd=proj[1].thanUnits.strdis, stra=proj[1].thanUnits.strang)

    if hugps != None:
        thanToplayerCurrent(proj, "approx1", moncolor="cyan")
        elem = thandr.ThanLine()
        elem.thanSet([tra1.calc2d(c1) for c1 in hurel])
        proj[1].thanElementAdd(elem)
        elem.thanTkDraw(proj[2].than)

        thanToplayerCurrent(proj, "hull_gps", moncolor="darkred")
        elem = thandr.ThanLine()
        elem.thanSet(hugps)
        proj[1].thanElementAdd(elem)
        elem.thanTkDraw(proj[2].than)
        thanToplayerCurrent(proj, "hull_rel", moncolor="pink")
        elem = thandr.ThanLine()
        elem.thanSet(hurel)
        proj[1].thanElementAdd(elem)
        elem.thanTkDraw(proj[2].than)

        __drawCurveCorresp(proj, gpsrel)

    if iafter != 0 and tra1s != None:
        thanToplayerCurrent(proj, "approx1_indiv", moncolor="blue")
        for (gps1, rel1), tra1 in zip(gpsrel, tra1s):
            ereln = thandr.ThanLine()
            if is3d: ereln.thanSet([tra1.calc(c1[:3]) for c1 in rel1])
            else:    ereln.thanSet([tra1.calc2d(c1[:3]) for c1 in rel1])
            proj[1].thanElementAdd(ereln)
            ereln.thanTkDraw(proj[2].than)
        thanToplayerCurrent(proj, "approx1", moncolor="cyan")
        tra1 = tra1s[-1]
        for gps1, rel1 in gpsrel:
            ereln = thandr.ThanLine()
            if is3d: ereln.thanSet([tra1.calc(c1[:3]) for c1 in rel1])
            else:    ereln.thanSet([tra1.calc2d(c1[:3]) for c1 in rel1])
            proj[1].thanElementAdd(ereln)
            ereln.thanTkDraw(proj[2].than)

    if trac == None: return thanModEnd(proj)     # ICP failed
    thanToplayerCurrent(proj, "icp", moncolor="green")
    for gps1, rel1 in gpsrel:
        ereln = thandr.ThanLine()
        if is3d: ereln.thanSet([trac.calc(c1[:3]) for c1 in rel1])
        else:    ereln.thanSet([trac.calc2d(c1[:3]) for c1 in rel1])
        proj[1].thanElementAdd(ereln)
        ereln.thanTkDraw(proj[2].than)
    thanModEnd(proj)                # 'Reset color' has already been called, but it is called again for only 1..
                                    # ..element, so it is fast

def __drawCurveCorresp(proj, gpsrel):
    "For FFLF networks draw the correspondences."
    thanToplayerCurrent(proj, "correspondence", moncolor="orange")
    if gpsrel != None:
        for gps1,rel1 in gpsrel:
            elem = thandr.ThanLine()
            elem.thanSet([rel1[0][:3], gps1[0][:3]])
            if elem.thanIsNormal():
                proj[1].thanElementAdd(elem)
                elem.thanTkDraw(proj[2].than)


disinp = 2.0
drange = 40.0
def thanEduAxis(proj):
    """Finds the mid axis of a road, given the road edges.

    Details in following papers (for now):

    """
    from p_gmidax import midAxis
    from thancom.thancommod import thanModCanc, thanModEnd
    from thancom.selutil import thanSelMultlines
    global disinp, drange
    dimitra(proj, "mid")
    lins = thanSelMultlines(proj, 2, Tmatch["Select the 2 edges of a road:\n"], strict=True)
    if lins == Canc: return thanModCanc(proj)          # MidAxis was cancelled
    while True:
	c = proj[2].thanGudGetOpts("Go/interpolation Distance/Search range (enter=go): ",
	default="go", statonce="", options=("go", "distance", "search"))
	if c == Canc: return thanModCanc(proj)         # MidAxis was cancelled
	if c == "g":
	    break
	elif c == "d":
	    c = proj[2].thanGudGetFloat2("New interpolation distance (enter=%f): " % disinp,
	    default=disinp, limits=(1.0e-6, 1.0e6))
	    if c != Canc: disinp = c
	elif c == "s":
	    c = proj[2].thanGudGetFloat2("New search range (enter=%d): " % drange,
	    default=drange, limits=(1.0e-6, 1.0e6))
	    if c != Canc: drange = c
    prt = proj[2].thanPrter1
    nrange = max(int(drange/disinp), 10)
    prt("interpolate=%f  drange=%f  nrange=%d\n" % (disinp, drange, nrange))
    lin1, lin2 = tuple(lins)
    caxis, terr = midAxis(lin1.cp, lin2.cp, disinp, nrange, prt)
    if caxis == None: return thanModCanc(terr)
    e = thandr.ThanLine()
    e.thanSet(caxis)
    proj[1].thanElementAdd(e)
    e.thanTkDraw(proj[2].than)
#    thanToplayerCurrent(proj, "seq", moncolor="green")
#    for cs in lines:
#        e = thandr.ThanLine()
#        e.thanSet(cs)
#        proj[1].thanElementAdd(e)
#        e.thanTkDraw(proj[2].than)
#    for i,c in enumerate(seq):
#        e = thandr.ThanText()
#	e.thanSet(str(i), c, 1.0, 0.0)
#        proj[1].thanElementAdd(e)
#        e.thanTkDraw(proj[2].than)
#    thanToplayerCurrent(proj, "target", moncolor="yellow")
#    for i,c in enumerate(tar):
#        e = thandr.ThanText()
#	c = list(c)
#	c[1] -= 1.1
#	e.thanSet(str(i), c, 1.0, 0.0)
#        proj[1].thanElementAdd(e)
#        e.thanTkDraw(proj[2].than)

    thanModEnd(proj)                # 'Reset color' has already been called, but it is called again for only 2..
                                    # ..elements, so it is fast

def thanCofread(proj, tit):
    "Tries to read the coefficients of a projection from a file."
    from thancom.thancomfile import thanTxtopen
    sufs = [("ThanCad Projection", ".cof"),
            ("TerraSar Projection", ".xml"),
            ("All files", "*"),
           ]
    while True:
        fn, fr = thanTxtopen(proj, tit, suf=sufs)
        if fr == Canc: return Canc            # Cof open was cancelled
        try:
            if fn.lower().endswith(".xml"):
                ic = proj[2].thanGudGetOpts(Tmatch["Geocentric GRS80/WGS84, Egsa87 datum, Htrs07 datum (cadastre), or UTM (enter=Egsa87): "],
                    default="EGSA87",
                    statonce=Tmatch["Please select coordinate system of the 3D object coordinates:\n"],
                    options=("Geocentric", "Egsa87", "Htrs07", "Utm"))
                if ic == Canc:  return Canc   # Cof open was cancelled
                elif ic == "g": L = p_gsar.TerraSarProjection()
                elif ic == "e": L = p_gsar.TerraSarProjectionEgsa87()
                elif ic == "h": L = p_gsar.TerraSarProjectionHtrs07()
                else:
                    izone = proj[2].thanGudGetInt2(Tmatch["UTM zone (enter=10): "], 10, limits=(1, 60))
                    if izone == Canc:  return Canc   # Cof open was cancelled
                    L = p_gsar.TerraSarProjectionUtm(izone)
                fr.close()
                L.readxml(fn)
                fnc, fw = thanTxtopen(proj, Tmatch["The projection must be saved in .cof format"], suf=".cof", mode="w",
                    initialfile=fn.namebase, initialdir=fn.parent)
                if fw == Canc: return Canc    # Cof open was cancelled
                L.write(fw)
                fw.close()
            else:
                L = p_gsar.readProj(fr)
                fr.close()
            return L
        except Exception, why:
            mm(proj[2], str(why), T["Failed to read %s"] % (fn,), p_gtkuti.ERROR)   # (Gu)i (d)ependent
            fr.close()
