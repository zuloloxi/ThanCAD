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
from p_gsar import SimilarTransformation, similar2lsm, similar3lsm, similarReadt, Projection
from p_gmath import Polynomial1_2DProjection
from p_ggen import prg, doNothing
from p_gvec import Vector3
try:                from thantrans import Tmatch
except ImportError: from p_gtwid import Twid as Tmatch
from cline import Cline
from icp2 import icp2, icp2d_3d, icp3
import firstpol, firstsim, var
from var import ICPconverged


def doMatchOpt(is3d, gps, relori, disint, disrange, threshold, maxsteps,
    centrApprox, iazim, distApprox, update=doNothing,
    prt=prg, prtbo=prg, prter=prg, strd=var.strdis, stra=var.strang):
    "Do the mathing of 2d/2d or 3d/3d with options."
    if is3d: gps = Cline(gps)
    else:    gps = Cline(gps, zcommon=0.0)
#---Uncomment the following line to increase accuracy:
#    if len(rel) > len(gps): gps, rel = rel, gps
    trac = SimilarTransformation()          # Identity transformation
    if centrApprox or distApprox:
        if is3d: rel = Cline(relori)
        else:    rel = Cline(relori, zcommon=0.0)
        if centrApprox:
            print "doMatchopt: is3d=", is3d, "centrApprox=", centrApprox
            tra1, er, erh = firstsim.matchCentroid(gps, rel, iazim, disint, disrange)
        else:
            tra1, er, erh, _ = firstsim.matchDotdist1(is3d, gps, rel)
        if tra1 == None:
            prter("ICP first approximation failed.")
            return None, None, None
        trac.chain(tra1)
        prt("Errxy=%s  Errz=%s phi=%s" % (strd(er), strd(erh), stra(-trac.gon[-1])))
    else:
        tra1 = None

#---Try icp

#    disint=0.2, disrange=50000*0.2, threshold=0.01, maxsteps=50
    prt("ICP2:")
    erpp = erp = erbest = 1.0e30
    tracbest = grbest = None
    for icp in xrange(maxsteps):
        if is3d:
            rel = Cline(trac.calc(c1) for c1 in relori)
            gr = icp3(rel, gps, disint, disrange, update)
            if gr == None:
                prter("ICP matching failed. Probably due to poor initial approximation.")
                break
            tra, er, erh = similar3lsm(gr)
        else:
            rel = Cline((trac.calc2d(c1[:3]) for c1 in relori), zcommon=0.0)
            gr = icp2(rel, gps, disint, disrange, update=update)
            if gr == None:
                prter("ICP matching failed. Probably due to poor initial approximation.")
                break
            tra, er, erh = similar2lsm(gr)
        if tra == None:
            prter("ICP Least Square Method failed. Probably due to very low number of nodes.")
            break
        prt("Errxy=%s  Errz=%s phi=%s" % (strd(er), strd(erh), stra(-tra.gon[-1])))
        tracp = trac.invert()
        trac.chain(tra)
        if er < erbest: erbest = er; tracbest = trac.clone(); tracpbest = tracp; grbest = gr
        if ICPconverged(er, erp, erpp, threshold, icp, prter): break
        erpp, erp = erp, er
    else:
        prter("WARNING: ICP HAS NOT CONVERGED AFTER %d STEPS!" % maxsteps)
    if tracbest != None:
        prtbo("Best Errxy=%s" % strd(erbest))
        prtbo("Overall Phi=%s   scale=%.5f   dx=%s   dy=%s" % (stra(-tracbest.gon[2]),
                               tracbest.am, strd(tracbest.cu[0]), strd(tracbest.cu[1])))
#       I need original xr, yr, zr in gr
        for i,(xg,yg,zg,xr,yr,zr,wxy,wz) in enumerate(grbest):
            xr, yr, zr = tracpbest.calc((xr, yr, zr))
            grbest[i] = xg,yg,zg,xr,yr,zr,wxy,wz
    return tra1, tracbest, grbest


def linicadDriver(c):
    "A routine to let the algorithm be used from within LiniCad."
    from itertools import islice
    cs = []
    lins = []
    for item in c.find_all():
        typ = c.type(item)
        if typ == "line":
            cs = list(c.coords(item))
            cs = zip(islice(cs, 0, None, 2), islice(cs, 1, None, 2), (0.0,)*(len(cs)/2))
            lins.append(cs)
            if len(lins) >= 2: break
    else:
        print "There should be at least 2 lines"
        return
    centrApprox = False
    iazim = None
    distApprox = True
    tra1, trac, _ = doMatchOpt(lins[0], lins[1], centrApprox, iazim, distApprox)

    if centrApprox or distApprox:
        if tra1 == None: return       # First approx failed
        c.create_line([tra1.calc2d(c1)[:2] for c1 in lins[1]], fill="cyan")
    if trac == None: return           # ICP failed
    c.create_line([trac.calc2d(c1)[:2] for c1 in lins[1]], fill="yellow")


def doMatchOpt23(proj, gps3d, relori, projcode, disint, disrange, threshold, maxsteps,
                 iprojapprox, nplane, L1, itransfapprox, iazim, prt=prg, prtbo=prg, prter=prg,
                 strd=var.strdis, stra=var.strang):
    "Do the matching with options."
    rel = Cline(relori, zcommon=0.0)
    gps3d = Cline(gps3d)
    ProjectClas = Projection(projcode)
#---Uncomment the following line to increase accuracy:
#    if len(rel) > len(gps): gps, rel = rel, gps

    if iprojapprox == 0:              # Projection to XY plane
        na = Vector3(1.0, 0.0, 0.0)   # unit vector of XY plane
        nb = Vector3(0.0, 1.0, 0.0)   # unit vector of XY plane
        proj1 = var.PlaneProjection(na, nb)
        gr1, tra1 = pureTransformation(proj, itransfapprox, gps3d, proj1, rel, disint, disrange, iazim, ProjectClas, prt, strd, stra)
    elif iprojapprox == 1:            # Projection to known plane
        gps = []
        a = Vector3(nplane)
        na, nb = a.normal2()
        proj1 = var.PlaneProjection(na, nb)
        gr1, tra1 = pureTransformation(proj, itransfapprox, gps3d, proj1, rel, disint, disrange, iazim, ProjectClas, prt, strd, stra)
    elif iprojapprox == 2:            # Known projection coefficients
        gr1, tra1 = pureTransformation(proj, itransfapprox, gps3d, L1, rel, disint, disrange, iazim, ProjectClas, prt, strd, stra)
    elif iprojapprox == 3:            # Exhaustive search of all projection planes
        gr1 = None; ermin = 1e100
        for (t,na,nb) in var.iterPhiTheta():
            proj1 = var.PlaneProjection(na, nb)
            gr, tra1 = pureTransformation(proj, itransfapprox, gps3d, proj1, rel, disint, disrange, iazim, ProjectClas, prt, strd, stra)
            if gr == None: continue
            L = ProjectClas()
            er, erh, discom = L.lsm23(gr)
            if er == None: continue
            er *= (rel.length()/discom)**2
            if er < ermin:
                ermin = er
                gr1 = gr
#                var.vis23(gps3d, gps, rel, tra1, L)
            print
        if gr1 != None:
            prt("Errxy=%s" % strd(ermin))
            print "================last chart======================"
#            var.vis23(gps3d, gps, rel, tra1, L1, all=False)
    if gr1 == None:
        prter("First approximation failed.")
        return None, None

#---Try icp

    prt("ICP2:")
    erpp = erp = erbest = 1.0e30
    Lbest = None
#    L1 = None    #Thanasis2010_01_25 commented out
    L1 = tra1
    gr = gr1
    for icp in xrange(maxsteps):
        L = ProjectClas()
        er, erh, discom = L.lsm23(gr)
        if er == None:
            prter("ICP Least Square Method failed. Probably due to very low number of nodes.")
            break
#        er *= (rel.length()/discom)**2
#        prt("Errxy=%s  L[1]=%s" % (strd(er), strd(L.L[1])))
        prt("Errxy2D=%s  Errxy3D=%s  L[1]=%s" % (strd(er), strd(erh), strd(L.L[1])))
        if L1 == None: L1 = L
        if er < erbest:
            erbest = er
            erhbest = erh
            Lbest = L
            grbest = gr
        if ICPconverged(er, erp, erpp, threshold, icp, prter): break
        erpp, erp = erp, er
        gr = icp2d_3d(rel, gps3d, disint, disrange, L)
        if gr == None:
            prter("ICP matching failed. Probably due to poor initial approximation.")
            break
    else:
        prter(Tmatch["WARNING: ICP HAS NOT CONVERGED AFTER %d STEPS!"] % maxsteps)
    if Lbest != None:
        prt("Errxy2D=%s  Errxy3D=%s" % (strd(erbest), strd(erhbest)))
        fn = proj[0].parent / (proj[0].namebase+".cof")
        fw = open(fn, "w")
        Lbest.write(fw)
        fw.close()
    return L1, Lbest


def pureTransformation(proj, itransfapprox, gps3d, proj1, rel, disint, disrange, iazim, ProjectClas,
        prt, strd, stra):
        "Perform the pure transformation."
        if itransfapprox == 0:
            gr, tra1 = match23identity1(gps3d, proj1, rel, disint, disrange, ProjectClas)
#            er = 0.0; tra1 = SimilarTransformation(); L = proj1
#            for a in L.L[1:]: prt("%.20e" % a)
        elif itransfapprox == 1:
            gr, tra1 = match23similar1(gps3d, proj1, rel, disint, disrange, iazim, ProjectClas)
        elif itransfapprox == 2:
            gr, tra1 = match23dist1(gps3d, proj1, rel, ProjectClas)
        elif itransfapprox == 3:
            gr, tra1 = match23polynom2(proj, gps3d, proj1, rel, disint, disrange, iazim, ProjectClas)
        else:
            assert False, "Unknown transformation approximation: "+str(itransfapprox)
        return gr, tra1


def match23dist1(gps3d, proj1, rel, ProjectClas):
    "Using distance algorithm find a first approximation, for 1 plane projection."
    gps = Cline((proj1.project(c) for c in gps3d), zcommon=0.0)
    _, _, _, relgps = firstsim.matchDotdist1(False, rel, gps)
    gpsrel = []
    for i,c in enumerate(relgps):
        gpsrel.append(tuple(gps3d[i][:3])+c[:3]+(1.0,1.0))
    return gpsrel, None



def match23similar1(gps3d, proj1, rel, disint, disrange, iazim, ProjectClas):
    "Using similarity transformation find a first approximation, for 1 plane projection."
    gps = Cline((proj1.project(c) for c in gps3d), zcommon=0.0)
    tra1, er, erh = firstsim.matchCentroid(rel, gps, iazim, disint, disrange)
    if tra1 == None: return None, None
    print "2d-3d 1st approx: similarity approx with centroid and icp2: er=", er
    return __similar1(gps3d, proj1, rel, tra1, disint, disrange, ProjectClas)


def match23identity1(gps3d, proj1, rel, disint, disrange, ProjectClas):
    "Using identity transformation find a first approximation, for 1 plane projection."
    tra1 = SimilarTransformation()   # Identity transformation
    return __similar1(gps3d, proj1, rel, tra1, disint, disrange, ProjectClas)


def __similar1(gps3d, proj1, rel, tra1, disint, disrange, ProjectClas):
    "Using similarity transformation find a first approximation, for 1 plane projection."
    sp = var.SimilarityAndProjection(proj1, tra1)
    gr = icp2d_3d(rel, gps3d, disint, disrange, sp)
    er = 0.0
    n = 0
    for (xg, yg, zg, xr, yr, zr, xok, yok) in gr:
        xr1, yr1, zr1 = sp.project((xg,yg,zg))
        er += (xr1-xr)**2 + (yr1-yr)**2
        n += 1
    from math import sqrt
    er = sqrt(er/n)
    print "2d-3d 1st approx: pure projection+pure transformation+icp2d_3d: er=", er
#    return gr, tra1    #Thanasis2010_01_25 commented out
    return gr, sp


def match23polynom2(proj, gps3d, proj1, rel, disint, disrange, iazim, ProjectClas):
    "Using 2D polynomial similarity transformation find a first approximation, for 1 plane projection."
    gps = Cline((proj1.project(c) for c in gps3d), zcommon=0.0)
    tra1, er, erh = firstsim.matchCentroid(rel, gps, iazim, disint, disrange)
    assert tra1 != None
    L = [tra1.a[2], tra1.a[3], tra1.a[0], -tra1.a[3], tra1.a[2], tra1.a[1]]
    tra1 = Polynomial1_2DProjection(L)
    L = firstpol.epil(proj, rel, gps, disint, tra1)
    tra1 = Polynomial1_2DProjection(L)
    return __similar1(gps3d, proj1, rel, tra1, disint, disrange, ProjectClas)
