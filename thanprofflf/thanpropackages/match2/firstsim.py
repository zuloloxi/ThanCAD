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
from math import pi
from p_gmath import dpt, avgtheta
from p_gsar import SimilarTransformation, similar2lsm, similar3lsm
from p_ggen import prg
from cline import Cline
from icp2 import icp2, erricp


def matchDotdist1(is3d, gps, rel):
    """Matches gps points to rel according to distance and checks reversed curves.

    The method uses similarity transformation to determine if the secondary
    curve is reversed. The matched pairs of coordinates are found
    using the distance algorithm and not the similarity transformation.
    """
    gpsrel = matchDotdist(gps, rel, 0.0, gps.length())
    if is3d: tra1, er, erh = similar3lsm(gpsrel)
    else:    tra1, er, erh = similar2lsm(gpsrel)
    print "MatchDistance: er=", er, "erh=", erh
    gpsrel1 = matchDotdist(gps, rel, gps.length(), 0.0)
    if is3d: tra11, er1, erh1 = similar3lsm(gpsrel1)
    else:    tra11, er1, erh1 = similar2lsm(gpsrel1)
    print "MatchDistance: er1=", er1, "erh1=", erh1
    if tra11 == None: return tra1, er, erh, gpsrel       # tra1 may be None
    if tra1 != None and er < er1: return tra1, er, erh, gpsrel
    print "MatchDistance: Secondary curve is probably reversed."
    return tra11, er1, erh1, gpsrel1


def matchDotdist(gps, rel, d1, d2):
    """Matches gps points to rel according to distance.

    It is assumed that gps line _contains_ the rel line.
    Specifically it is assumed that the whole rel line corresponds to one
    segment of gps line, the one from distance d1 to distance d2."""
    dfact = (d2-d1) / rel.length()
    gpsrel = []
    glen = gps.length()
    for x, y, z, d in rel:
        d = d1 + d*dfact
        if d < 0.0 or d > glen: continue
        gpsrel.append(gps.getPoint(d)+(x,y,z,1.0,1.0))
    return gpsrel


def matchDotdistnew(gps, gpsd1, gpsd2, rel, reld1, reld2):
    """Matches gps points to rel according to distance.

    It is assumed that gps line between gpsd1 and gpsd2
    corresponds to the rel line between reld1 and reld2."""
    gpsrel = []
    glen = gps.length()
    for rx, ry, rz, rd in rel:
        if rd < reld1: continue
        if rd > reld2: break
        gd = linint(reld1, gpsd1, reld2, gpsd2, rd)
        if gd < 0.0 or gd > glen: continue
        gpsrel.append(gps.getPoint(gd)+(rx,ry,rz,1.0,1.0))
    return gpsrel


def matchCentroid(gps, rel, iazim, disint=0.2, disrange=500000*0.2):
    "Find translation, scale, rotation with the centroid."
    am = gps.length()/rel.length()
    rel.calcCentroid_lines()
    gps.calcCentroid_lines()
    cp = [g-r for r,g in zip(rel.centroid, gps.centroid)]
    if iazim == 0:                      # Average azimouth of first and last node
        thbest = avgtheta(dpt(gps.calcAzimouth(0)-rel.calcAzimouth(0)), dpt(gps.calcAzimouth(-1) - rel.calcAzimouth(-1)))
        if thbest == None:
            thbest = avgtheta(dpt(gps.calcAzimouth(0)-rel.calcAzimouth(-1)), dpt(gps.calcAzimouth(-1) - rel.calcAzimouth(0)))
            if thbest == None: return None, None, None     # Too diferent azimuths. Approximation failed.
            prg("Centroid approximation: Secondary line is probably reversed.")
#           Note that after the angle is computed as if the secondary line were not reversed.
#           However, the sec. line after the similarity remains reversed. This is handled
#           in icp2 and icp3 with the reverse2 and reverse3 functions.
        thbest = dpt(-thbest)           # The Transformation object needs opposite angles (why???)
        trabest = SimilarTransformation(cp, [0.0, 0.0, thbest], am)
        trabest.setRotcenter(rel.centroid)
    elif iazim == 1:                    # Exhaustive search of all azimouths..
        trabest, erbest = exhaustTheta(gps, rel, disint, disrange, cp, am)
        if erbest >= 1.0e100: return None, None, None     # ICP failed in all azimuths!!
        prg("Thbest=%.5f deg     Errxy=%.1f" % (trabest.gon[2]*180/pi, erbest))
    elif iazim == 2:
        thbest = gps.calcAvAzimouth() - rel.calcAvAzimouth()
#        prg("dth=%.5f deg" % (thbest*180/pi,))
#	prg("gps=%.5f deg   rel=%.5f deg" % (gps.calcAvAzimouth()*180/pi, rel.calcAvAzimouth()*180/pi))
	thbest = dpt(-thbest)           # The Transformation object needs opposite angles (why???)
        trabest = SimilarTransformation(cp, [0.0, 0.0, thbest], am)
	trabest.setRotcenter(rel.centroid)
    else:
        raise ValueError, "Unknown azimouth code"

#    rel1 = [trabest.calc2d((c1[0], c1[1], 0.0)) for c1 in rel]
    rel1 = Cline(trabest.calc2d(c1[:3]) for c1 in rel)
    gr = icp2(rel1, gps, disint, disrange)
    if gr == None: return None, None, None   # The first approximation was not good enough
    er1, erh = erricp(gr)
    return trabest, er1, erh


def exhaustTheta(gps, rel, disint, disrange, cp, am):
    "Exhaustive serach of all theta for the 1st approx with similarity (2d case)."
    erbest = 1.0e100                # ..for 2d (or in 3d assuming z is insignificant)
    disint1 = disint*20                      # Make icp2 a little faster
    disrange1 = max(disint1*40, disrange)    # Make at least +-40 points lookup
    for th in xrange(0, 360, 5):
            th = th * pi/180.0
            gon= [0.0, 0.0, th]
            tra = SimilarTransformation(cp, gon, am)
            tra.setRotcenter(rel.centroid)
            rel1 = Cline(tra.calc2d(c1[:3]) for c1 in rel)   # gps and rel should have z=0 for the 2d case.
#            from p_gchart import ThanChart, viswin
#            ch = ThanChart(title="2d-3d case in matchCentroid")
#            gps.add2chart(ch, color="magenta")
#            rel1.add2chart(ch, color="cyan")
#            viswin(ppp[2], ch)
            gr = icp2(rel1, gps, disint1, disrange1)
            if gr == None:
                prg("Theta =%.5f deg     Errxy=failed" % (th*180/pi, ))
                continue     # ICP failed; ignore this azimuth
            er1, erh = erricp(gr)
            if er1 < erbest: trabest=tra; erbest=er1
            prg("Theta =%.5f deg     Errxy=%.1f" % (th*180/pi, er1))
    return trabest, erbest


def exhaustThetaMult(gps, rel, disint, disrange, icorr, cerel, cp, am):
    "Exhaustive search of all theta for the 1st approx with similarity (2d case - multiple curves)."
    from matchmult import correspondMult
    erbest = 1.0e100                # ..for 2d (or in 3d assuming z is insignificant)
    disint1 = disint*20                      # Make icp2 a little faster
    disrange1 = max(disint1*40, disrange)    # Make at least +-40 points lookup
    for th in xrange(0, 360, 5):
        th = th * pi/180.0
        gon= [0.0, 0.0, th]
        tra = SimilarTransformation(cp, gon, am)
        tra.setRotcenter(cerel)
        gpsrel = correspondMult(gps, rel, icorr, tra)
        if gpsrel == None: continue      # correspondence failed; ignore this azimuth
        gr = []
        for gps1,rel1 in gpsrel:
            rel2 = Cline(tra.calc2d(c1[:3]) for c1 in rel1)   # gps and rel should have z=0 for the 2d case.
#            from p_gchart import ThanChart, viswin
#            ch = ThanChart(title="2d-3d case in matchCentroid")
#            gps.add2chart(ch, color="magenta")
#            rel1.add2chart(ch, color="cyan")
#            viswin(ppp[2], ch)
            gr2 = icp2(rel2, gps1, disint1, disrange1)
            if gr2 == None: continue     # ICP failed; ignore this curve
            gr.extend(gr2)
        if len(gr) < 3: continue         # ICP failed; ignore this azimuth
        er1, erh = erricp(gr)
        if er1 < erbest: trabest=tra; erbest=er1
        prg("Theta =%.5f deg     Errxy=%.1f" % (th*180/pi, er1))
    return trabest, erbest
