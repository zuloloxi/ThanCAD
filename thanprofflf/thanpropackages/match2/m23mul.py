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
from p_ggen import prg
from p_gvec import Vector3
from p_gsar import SimilarTransformation, Projection
from thantrans import Tmatch
from matchmult import correspondMult
from icp2 import icp2d_3d
from cline import Cline
import var

"""
March 30, 2011
Here's the deal:
A. Find FFLFs correspondences.
   1. Find pure projection (Projection to XY plane, Projection to known plane,
         Known projection coefficients, Exhaustive search of all projection planes)
   2. Project the reference 3D FFLFs to 2D.
   3. Find 2D similarity transformation between reference 2D and secondary 2D
         using one the three:
         a. Convex hulls and similarity through centroids, lengths and
            exhaustive search for rotations (the other methods for rotation do not work
            as the hull is closed). (Similarity through distance algorithm does not
            work for closed curves).
         b. All the curves through centroids, lengths and exhaustive search for
            rotations (the other methods for rotation do not work since we do not
            know the correspondences). ((Similarity through distance algorithm does
            not because we do not know the correspondences).
        c. The unit similarity (the FFLFs are close enough).
     4. Transform the reference 2D with the similarity.
     5. Find curves correspondences (6 methods).
     Note that the similarity transformation is done only to find the
     curves correspondences.
B. After the correspondences are established, we can bring the FFLFs more close
   to each other, applying the emthods for match23:
   1. Similarity, with 3 options for the rotation.
   2. Distance algorithm.
   3. Polynomial approximation.
   Note that if we choose step 1, then this step is not neeeded, as it is essentially
   the work we did in A.
   It goes withou saying that the LSM will be applied on the data of all FFLFs together.
"""

def doMatchMult23Opt(proj, gps3d, relori, projcode, disint, disrange, threshold, maxsteps,
                 iprojapprox, nplane, L1, itransfapprox, iazim,
                 ibefore, icorr, iafter,
                 prt=prg, prtbo=prg, prter=prg, strd=var.strdis, stra=var.strang):
    """Do the matching of 3D projections to 2D with multipls FFLFs (curves).

    April 5, 2011: Multiple match23 without first approximation was implemented."""
    rel   = [Cline(rel1, zcommon=0.0) for rel1 in relori]
    gps3d = [Cline(gps1)              for gps1 in gps3d]
    ProjectClas = Projection(projcode)
#---Uncomment the following line to increase accuracy:
#    if len(rel) > len(gps): gps, rel = rel, gps

    if iprojapprox == 0:              # Projection to XY plane
        na = Vector3(1.0, 0.0, 0.0)   # unit vector of XY plane
        nb = Vector3(0.0, 1.0, 0.0)   # unit vector of XY plane
        proj1 = var.PlaneProjection(na, nb)
        tra1 = SimilarTransformation()   # Identity transformation
        tra1 = var.SimilarityAndProjection(proj1, tra1)
        tra1.calc2d = tra1.project    #Hack to make it compatible with correspondMult
        relgps = correspondMult(rel, gps3d, icorr, tra1)    #gps,rel->rel, gps to make them compatible with correspondmult
        if relgps == None:
            prter(Tmatch["Correspondence determination failed. Probably due to poor initial approximation."])
            return tra1, None, relgps
#        gr1, tra1 = pureTransformation(proj, itransfapprox, gps3d, proj1, rel, disint, disrange, iazim, ProjectClas, prt, strd, stra)
    elif iprojapprox == 1:            # Projection to known plane
        assert False, "Not yet implemented"
        gps = []
        a = Vector3(nplane)
        na, nb = a.normal2()
        proj1 = var.PlaneProjection(na, nb)
        gr1, tra1 = pureTransformation(proj, itransfapprox, gps3d, proj1, rel, disint, disrange, iazim, ProjectClas, prt, strd, stra)
    elif iprojapprox == 2:            # Known projection coefficients
        tra1 = L1
        tra1.calc2d = tra1.project    #Hack to make it compatible with correspondMult
        relgps = correspondMult(rel, gps3d, icorr, tra1)    #gps,rel->rel, gps to make them compatible with correspondmult
        if relgps == None:
            prter(Tmatch["Correspondence determination failed. Probably due to poor initial approximation."])
            return tra1, None, relgps
#        gr1, tra1 = pureTransformation(proj, itransfapprox, gps3d, L1, rel, disint, disrange, iazim, ProjectClas, prt, strd, stra)
    elif iprojapprox == 3:            # Exhaustive search of all projection planes
        assert False, "Not yet implemented"
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
    if tra1 == None:
        prter("First approximation failed.")
        return None, None

#---Try icp

    prt("ICP2:")
    erpp = erp = erbest = 1.0e30
    Lbest = None
#    L1 = None    #Thanasis2010_01_25 commented out
    L1 = tra1

    nconv = 0
    gr = []
    L = tra1
    for rel, gps3d in relgps:
        gr1 = icp2d_3d(rel, gps3d, disint, disrange, L)
        if gr1 != None:
            gr.extend(gr1)
            nconv += 1
            print len(gr1),
    print "number of points=", len(gr)
    if len(gr) < 5:
        prter("ICP matching failed. Probably due to poor initial approximation.")
        return L1, None, relgps

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
        if var.ICPconverged(er, erp, erpp, threshold, icp, prter): break
        erpp, erp = erp, er
        nconv = 0
        gr = []
        for rel, gps3d in relgps:
            gr1 = icp2d_3d(rel, gps3d, disint, disrange, L)
            if gr1 != None:
                gr.extend(gr1)
                nconv += 1
                print len(gr1),
        print "number of points=", len(gr)
        if len(gr) < 5:
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
    return L1, Lbest, relgps
