# -*- coding: iso-8859-7 -*-
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

This is the professional part of ThanCad which is initially commercial.
"""
from math import pi, atan2, fabs, cos, sin, hypot
from p_gmath import dpt
from p_gsar import SimilarTransformation, similar2lsm
from p_ggen import prg, xfrange, iterby2
from p_gvec import Vector3
from p_gtri import hull
from thantrans import Tmatch
from cline import Cline
from icp2 import icp2
from match2 import match23dist1, match23similar1
import firstsim, var
from var import ICPconverged


def matchMultApproxBefore(is3d, gps, relori, ibefore, icorr, disint, disrange,
               prt=prg, prtbo=prg, prter=prg, strd=var.strdis, stra=var.strang):
    "Finds the first approximation in global multiple curves matching."
    assert not is3d, "Only 2 dimensional first approximation"  # Not really man
    if ibefore == 2:               # No prealignment before correspondence
        return None, None, None
    elif ibefore == 0:             # Prealignment using hulls and centroid before correspondence
        temp = []
        for gps1 in gps: temp.extend(gps1)
        hugps = hull(temp)
        if hugps == None:
            prter(Tmatch["Degenerate convex hull. The reference line(s) lie on a single line segment!"])
            return None, None, None
        temp = []
        for gps1 in relori: temp.extend(gps1)
        hurel = hull(temp)
        if hurel == None:
            prter(Tmatch["Degenerate convex hull. The seconadry line(s) lie on a single line segment!"])
            return None, None, None
        centrApprox = True
        distApprox = False
        if centrApprox or distApprox:
            gps = Cline(hugps)
            rel = Cline(hurel)
            if centrApprox:
                tra1, er, erh = firstsim.matchCentroid(gps, rel, 1, disint, disrange)  # Exhaustive search of all azimouths
            else:
                tra1, er, erh, _ = firstsim.matchDotdist1(is3d, gps, rel)
            if tra1 == None:
                prter("ICP of multiple global matching first approximation failed.")
                return None, hugps, hurel
            prt("Errxy=%s  Errz=%s phi=%s" % (strd(er), strd(erh), stra(-tra1.gon[-1])))
        else:
            tra1 = None
        return tra1, hugps, hurel
    elif ibefore == 1:            # Prealignment using all curves and centroid before correspondence
        gps = [Cline(gps1) for gps1 in gps]
        rel = [Cline(rel1) for rel1 in relori]
        legps, cegps = cenMult(gps)
        lerel, cerel = cenMult(rel)
        am = legps / lerel
        cp = [g-r for r,g in zip(cerel, cegps)]
        tra1, er = firstsim.exhaustThetaMult(gps, rel, disint, disrange, icorr, cerel, cp, am)
        if tra1 != None: prg("Thbest=%.5f deg     Errxy=%.1f" % (tra1.gon[2]*180/pi, er))
        return tra1, None, None


def cenMult(gps):
    """Calculate global centroid and total length of multiple curves.

    The centroid is the weighted average of the centroids of all curves.
    The weight of a curcve is the lenbth of the curve."""
    legps = 0.0
    cegps = [0.0, 0.0, 0.0]
    for gps1 in gps:
        le1 = gps1.length()
        legps += le1
        gps1.calcCentroid_lines()
        ce1 = gps1.centroid
        for i in xrange(3): cegps[i] += le1 * ce1[i]
    for i in xrange(3): cegps[i] /= legps
    return legps, cegps


def matchMultApproxAfter(is3d, gpsrel, iafter, disint, disrange, trab,
               prt=prg, prtbo=prg, prter=prg, strd=var.strdis, stra=var.strang):
    "Finds the first approximation after correspondence using individual pairs of curve."
    assert not is3d, "Only 2 dimensional first approximation"  # Not really man
    centrApprox = True
    distApprox = False
    iazim = 1
    if iafter == 1: # Full individual ICP; this also takes into account centrApparox and distApprox
        from match2 import doMatchOpt
        gr = []
        nconv = 0
        tra1s = []
        for gps,relori in gpsrel:
            _, tra1, gr1 = doMatchOpt(is3d, gps, relori, centrApprox, iazim, distApprox,
                                 prt, prtbo, prter, strd, stra)
            tra1s.append(tra1)
            if tra1 == None: continue
#            prt("Individual Errxy=%s  Errz=%s phi=%s" % (strd(er), strd(erh), stra(-tra1.gon[-1])))
            gr.extend(gr1)
            nconv += 1
        tra1, er, erh = similar2lsm(gr)
        if tra1 == None:
            prter("Mutiple curve full individual ICP as a better approximation failed.")
            tra1s = None
            trac = trab
        else:
            if nconv < len(gpsrel):
                prter("The full individual ICP converged only for %d of the %d homologous pairs." % (nconv, len(gpsrel)))
            trac = tra1
            prt("Errxy=%s  Errz=%s phi=%s" % (strd(er), strd(erh), stra(-trac.gon[-1])))
    elif iafter == 0:  # Individual centroid/distance method (no full ICP)
        if centrApprox:
            gr = []
            nconv = 0
            tra1s = []
            for gps,relori in gpsrel:
                tra1, er, erh = firstsim.matchCentroid(gps, relori, iazim)
                tra1s.append(tra1)
                if tra1 == None: continue
                prt("Individual Errxy=%s  Errz=%s phi=%s" % (strd(er), strd(erh), stra(-tra1.gon[-1])))
                rel = Cline([tra1.calc2d(c1[:3]) for c1 in relori])
                gr1 = icp2(rel, gps, disint, disrange)
                if gr1 == None: continue
                tri1 = tra1.invert()
                for i, gg in enumerate(gr1):
                    gg = list(gg)
                    gg[3:6] = tri1.calc2d(gg[3:6])
                    gr1[i] = gg
                gr.extend(gr1)
                nconv += 1
            tra1, er, erh = similar2lsm(gr)
        else:                        # distApprox is unimplemented
            tra1, er, erh, _ = firstsim.matchDotdist1(is3d, gps, rel)
        if tra1 == None:
            prter("Mutiple curve ICP first approximation failed.")
            tra1s = None
            trac = tra2
        else:
            if nconv < len(gpsrel):
                prter("The first approximation ICP converged only for %d of the %d homologous pairs." % (nconv, len(gpsrel)))
            trac = tra1
            tra1s.append(tra1)
            prt("Errxy=%s  Errz=%s phi=%s" % (strd(er), strd(erh), stra(-trac.gon[-1])))
    else:          # No approximation after correspondence
        tra1s = None
        trac = trab.clone()
    return tra1s, trac


def matchMult23Approx(gps3d, relori, L1, iapprox, searchplane, iazim,
               prt=prg, prtbo=prg, prter=prg, strd=var.strdis, stra=var.strang):
    """Finds the first approximation in global multiple 2d-3d curves matching."

    If searchplane is True, then do exhaustive angle search for the best
    projection plane."""
    relall = []
    for rel1 in relori:
        for xg,yg,zg,_ in rel1:
            a = Vector3(xg, yg, zg)
            xr = na * a
            yr = nb * a
            relall.append((xr, yr, zg))
    hurel = hull(relall)
    if hurel == None:
        prter(Tmatch["Global multiple global 3d-2d curves matching: first approximation failed:"])
        prter(Tmatch["Degenerate convex hull. The (2d) slave lines lie on a single line segment!"])
        return None, None, None

    ter = Tmatch["<No description of the error is available>"]
    L1 = hugps1 = None; ermin = 1e100
    for (t,na,nb) in var.iterPhiTheta():
        gpsall = []
        for rel1 in gps3d:
            for cg in rel1:
                a = Vector3(cg[0], cg[1], cg[2])
                xr = na * a
                yr = nb * a
                gpsall.append([xr, yr]+cg)      # Save projected _and_ 3d coordinates
        hugps = hull(gpsall)
        if hugps == None:
            if searchplane: continue
            prter(Tmatch["Global multiple global 3d-2d curves matching: first approximation failed:"])
            prter(Tmatch["Degenerate convex hull. The (projected) 3d master lines lie on a single line segment!"])
            return None, None, None

        if iapprox == 3:                  # Distance Approximation
            hugps3d = [cg[2:] for cg in hugps]
            er, L = match23dist1(hugps3d, hugps, rel, L1.__class__)
            if L == None:
                if searchplane: continue
                prter(Tmatch["Global multiple global 3d-2d curves matching: first approximation failed:"])
                prter(Tmatch["Probably the projection plane is not horizontal."])
                return None, None, None
            if er < ermin:
                ermin = er
                L1 = L
                hugps1 = hugps
                var.vis23(hugps3d, hugps, hurel, None, L)
            print
        elif iapprox in (0, 2):           # 0=unit projection: L1 is the unit projection..
            return L1, hugps, hurel       # ..2=Coefficients read from file: L1 is the read projection
        elif iapprox == 1:                # Similarity approximation
            L1 = match23similar(gps3d, rel, searchplane, iazim, L1.__class__, prt, strd)
            hugps3d = [cg[2:] for cg in hugps]
            er, L, tra1 = match23similar1(hugps3d, hugps, hurel, iazim, L1.__class__, na, nb)
            if L == None:
                if searchplane: continue
                prter(Tmatch["Global multiple global 3d-2d curves matching: first approximation failed:"])
                prter(Tmatch["Probably the projection plane is not horizontal."])
                return None, None, None
            if er < ermin:
                ermin = er
                L1 = L
                hugps1 = hugps
                var.vis23(hugps3d, hugps, hurel, tra1, L)
        if not searchplane: break

    if L1 == None: return None, None, None
    erh = 0.0
    prt("Errxy=%s  Errz=%s L[1]=%s" % (strd(ermin), strd(erh), strd(L1.L[1])))
    print "================last chart======================"
    hugps3d = [cg[2:] for cg in hugps1]
    var.vis23(hugps3d, hugps1, hurel, None, L1, all=False)
    return L1, hugps1, hurel


def doMatchMultOpt(is3d, gps, relori, disint, disrange, threshold, maxsteps,
            ibefore, icorr, iafter,
            prt=prg, prtbo=prg, prter=prg, strd=var.strdis, stra=var.strang):
    "Do multiple matching the matching with options of correspondence."
    trab, hugps, hurel = matchMultApproxBefore(is3d, gps, relori, ibefore, icorr, disint, disrange,
        prt, prtbo, prter, strd, stra)
    if trab == None: trab = SimilarTransformation()          # Identity transformation
    gps = [Cline(gps1) for gps1 in gps]
    rel = [Cline(rel1) for rel1 in relori]
    gpsrel = correspondMult(gps, rel, icorr, trab)
    if gpsrel == None:
        prter(Tmatch["Correspondence determination failed. Probably due to poor initial approximation."])
        return trab, hugps, hurel, None, None, None
    if len(gpsrel) < len(gps):
        prter(Tmatch["Only %d of the %d homologous pairs were found!"] % (len(gpsrel), len(gps)))
    tra1s, trac = matchMultApproxAfter(is3d, gpsrel, iafter, disint, disrange, trab,
               prt, prtbo, prter, strd, stra)

#---Try icp

    prt("ICP2:")
    erpp = erp = erbest = 1.0e30
    tracbest = None
    for icp in xrange(maxsteps):
        nconv = 0
        gr = []
        for gps, relori in gpsrel:
            if is3d:
                rel = Cline([trac.calc(c1[:3]) for c1 in relori])
                gr1 = icp3(rel, gps)
            else:
                rel = Cline([trac.calc2d(c1[:3]) for c1 in relori])
#                prg("doMatchMultOpt: len(gps)=%d  len(rel)=%d" % (len(gps), len(rel)))
                gr1 = icp2(rel, gps, disint, disrange)
            if gr1 != None: gr.extend(gr1); nconv += 1

        if is3d:
            if len(gr) < 3:
                prter(Tmatch["ICP multiple curve matching failed. Probably due to poor initial approximation."])
                break
            tra, er, erh = similar3lsm(gr)
        else:
            if len(gr) < 2:
                prter(Tmatch["ICP multiple curve matching failed. Probably due to poor initial approximation."])
                break
            tra, er, erh = similar2lsm(gr)
        if tra == None:
            prter(Tmatch["ICP Least Square Method failed. Probably due to very low number of nodes."])
            break
        prt("Errxy=%s  Errz=%s phi=%s  (%d/%d)" % (strd(er), strd(erh), stra(-tra.gon[-1]),
                                                   nconv, len(gpsrel)))
        trac.chain(tra)
        if er < erbest: erbest = er; tracbest = trac.clone()
        if ICPconverged(er, erp, erpp, threshold, icp, prter): break
        erpp, erp = erp, er
    else:
        prter(Tmatch["WARNING: ICP HAS NOT CONVERGED AFTER %d STEPS!"] % maxsteps)
    if tracbest != None:
        if nconv < len(gpsrel):
            prter(Tmatch["WARNING: The ICP converged only for %d of the %d homologous pairs."] % (nconv, len(gpsrel)))
            prter(Tmatch["The transformation was computed by the converged pairs."])
        prtbo("Best Errxy=%s" % strd(erbest))
        prtbo("Overall Phi=%s   scale=%.5f   dx=%s   dy=%s" % (stra(-tracbest.gon[2]),
                               tracbest.am, strd(tracbest.cu[0]), strd(tracbest.cu[1])))
    return trab, hugps, hurel, tra1s, tracbest, gpsrel


def correspondMult(gps, rel, icorr, trab):
    "Find homologous pair of curves."
    if   icorr == 0:  gpsrel = corEnd(gps, rel, trab)
    elif icorr == 1:  gpsrel = corCen(gps, rel, trab)
    elif icorr == 2:  gpsrel = corDis(gps, rel, trab)
    elif icorr == 3:  gpsrel = corICPpartial(gps, rel, trab)
    elif icorr == 4:  gpsrel = None                     #Not yet implemented
    elif icorr == 5:  gpsrel = corHybrid(gps, rel, trab)
    else: raise ValueError, "Invalid correspondence code %d" % icorr
    if gpsrel == None: return gpsrel
    assert len(gpsrel) <= len(gps)
    if len(gpsrel) < len(gps):
        prg(Tmatch["Only %d of the %d homologous pairs were found!"] % (len(gpsrel), len(gps)))
    return gpsrel


def corEnd(gps, rel, tra1):
    "Finds the correspondence between lines in gps and lines in rel using line ends."
    reler = []
    for gps1 in gps:
        ga, gt = gps1[0], gps1[-1]
        for rel1 in rel:
            er1, er2, inv = __endinvert(ga, gt, tra1.calc2d(rel1[0][:3]), tra1.calc2d(rel1[-1][:3]))
            reler.append((er1+er2, gps1, rel1, inv))
    return __minpairs(reler)


def __endinvert(ga, gt, ra, rt):
    "Finds if the curves are inverted and the distances of the ends."
    er1  = hypot(ga[0] -ra[0],  ga[1]-ra[1])
    er2  = hypot(gt[0] -rt[0],  gt[1]-rt[1])
    rt, ra = ra, rt
    err1 = hypot(ga[0] -ra[0],  ga[1]-ra[1])
    err2 = hypot(gt[0] -rt[0],  gt[1]-rt[1])
    if er1+er2 < err1+err2: return er1, er2, False
    else:                   return err1, err2, True


def __minpairs(reler):
    "Find the pairs with minimum distance."
    gpsrel = []
    while reler:
        er1, gps1, rel1, inv1 = min(reler)
        temp = []
        for r in reler:
            if gps1 is r[1] or rel1 is r[2]: continue
            temp.append(r)
        reler = temp
        if inv1: rel1.reverse()
        gpsrel.append((gps1, rel1))
    return gpsrel


def corCen(gps, rel, tra1):
    "Finds the correspondence between lines in gps and lines in rel using line centroids."
    reler = []
    for rel1 in rel: rel1.calcCentroid_lines()
    for gps1 in gps:
        gps1.calcCentroid_lines()
        ga = gps1.centroid
        for rel1 in rel:
            ra = tra1.calc2d(rel1.centroid)
            er = hypot(ga[0]-ra[0],  ga[1]-ra[1])
            reler.append((er,  gps1, rel1, False))
    return __minpairs(reler)


def corDis(gps, rel, tra1):
    "Finds the correspondence between lines in gps and lines in rel using line lengths."
    reler = []
    for gps1 in gps:
        ga = gps1.length()
        for rel1 in rel:
            ra = rel1.length()*tra1.am
            er = fabs(ga-ra)
            reler.append((er,  gps1, rel1, False))
    return __minpairs(reler)


def corICPpartial(gps, rel, tra1):
    "Finds the correspondence between lines in gps and lines in rel using line ends."
    disint=0.2; disrange=50000*disint
    reler = []
    for rel1 in rel:
        rel1x = Cline(tra1.calc2d(c1[:3]) for c1 in rel1)
        for gps1 in gps:
            gr = icp2(gps1, rel1x, disint, disrange)
            if gr == None: continue
            dis = [hypot(ga[0]-ra[0],  ga[1]-ra[1]) for (ga, ra) in iterby2(gr)]
            discom = sum(dis)
#            if discom/gps1.length() < 0.66: continue    # Curves are not near enough (or bad prealignment)
            r = [hypot(xg-xr, yg-yr) for xg, yg, zg, xr, yr, zr, wxy, wz in gr]
            er = 0.0
            for i in xrange(len(gr)-1):
                er += (r[i]+r[i+1])*0.5*dis[i]
            er = er/discom
            er *= (gps1.length()/discom)**2
            reler.append((er, gps1, rel1, False))
    return __minpairs(reler)


def corHybridold(gps, rel, tra1):
    "Finds the correspondence between lines in gps and lines in rel using line centroids."
    reler = []
    for rel1 in rel: rel1.calcCentroid_lines()
    c = tra1.calc2d
    am = tra1.am
    for gps1 in gps:
        gps1.calcCentroid_lines()
        gc = gps1.centroid
        gl = gps1.length()
        ga, gt = gps1[0], gps1[-1]
        for rel1 in rel:
            rc = c(rel1.centroid)
            erc = hypot(gc[0]-rc[0], gc[1]-rc[1])
            rl = rel1.length()*am
            erl = fabs(gl-rl)
            er1, er2, inv = __endinvert(ga, gt, c(rel1[0][:3]), c(rel1[-1][:3]))
            reler.append((max(erc, erl, er1, er2), gps1, rel1, False))
    return __minpairs(reler)


def corHybrid(gps, rel, tra1):
    "Finds the correspondence between lines in gps and lines in rel using line centroids."
    c = tra1.calc2d
    reltra = []                      #Transformed rel
    for rel1 in rel:
        rel1 = Cline(gc[:3] for gc in rel1)
        rel1.calcCentroid_lines()
        reltra.append(rel1)
    reler = []
    for gps1 in gps:
        gps1.calcCentroid_lines()
        gc = gps1.centroid
        gl = gps1.length()
        ga, gt = gps1[0], gps1[-1]
        for i, rel1 in enumerate(reltra):
            rc = rel1.centroid
            erc = hypot(gc[0]-rc[0], gc[1]-rc[1])
            rl = rel1.length()
            erl = fabs(gl-rl)
            er1, er2, inv = __endinvert(ga, gt, rel1[0][:3], rel1[-1][:3])
            reler.append((max(erc, erl, er1, er2), gps1, rel[i], False))
    return __minpairs(reler)
