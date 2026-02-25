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
from math import sqrt, hypot
from p_ggen import xfrange, iterby2, doNothing
import var


def erricp(gr):
    er = erh = 0.0
    n = 0.0; xyok = 1
    for xg,yg,zg,xr,yr,zr,_,_ in gr:
        xx, yy, zz = (xr, yr, zr)
        er += xyok*((xx-xg)**2 + (yy-yg)**2)
        erh += xyok*((zz-zg)**2)
        n += xyok
    er = sqrt(er/n); erh = sqrt(erh/n)
    return er, erh


def icp2d_3d(sidea, sideb, disint, disrange, L, update=doNothing):
    """Finds the closest pairs of a 2d line and a 3d line projected to 2d.

    sidea is the 2d polyline.
    sideb is the 3d polyline with the biggest number of points (gps).
    sideb is split into a large set of sequential equidistant points whose
    distance is disint, in world coordinates (GPS).
    The closest point of a node of sidea is seeked within distance +-disrange
    on sideb. disrange is a distance in world coordinates (gps).
    L is a projection object which projects the 3d points (GPS) of sideb to
    2d points on the same coordinate system as sidea. It has the 'project'
    which does the projection.
    """
    a = sidea
    b3d = [b1 for b1 in iterdis3(sideb, disint)]
    b = [L.project(b1) for b1 in b3d]
    if reverse2(a, b, b3d) == None: print "Can not determine if one curve is reversed"
    ia, ib = start2(a, b)
    if ia == None: return None #"Something wrong with the parallel lines: Do they overlap?"
    if sideb.isClosed():
        del b[-1]
        b.extend(b)
        del b3d[-1]
        b3d.extend(b3d)

#---Do the job

    xg, yg, zg = b3d[ib][:3]
    xr, yr, zr = a[ia][:3]
    gr = [(xg, yg, zg, xr, yr, zr, 1.0, 1.0)]
    nr = int(disrange/disint+0.5)
#    while ia < len(a)-1 and ib < len(b)-1:     # This must be enabled for partial matching
    while ia < len(a)-1 and ib < len(b):
        update()
        ia1 = ia + 1
        d = hypot(a[ia1][0]-a[ia][0], a[ia1][1]-a[ia][1])
        ib = min(ib + int(d/disint+0.5), len(b)-1)
        ib1 = mindis2(a[ia1], b, ib, nr)
        xg, yg, zg = b3d[ib1][:3]
        xr, yr, zr = a[ia1][:3]
        gr.append((xg, yg, zg, xr, yr, zr, 1.0, 1.0))
        ia = ia1
        ib = ib1
    return gr


def icp2(sidea, sideb, disint, disrange, update=doNothing):
    """Finds the icp axis of 2 almost identical polylines.

    sideb is the polyline with the biggest number of points (gps)."""
    a = sidea
    b = [b1 for b1 in iterdis2(sideb, disint)]
    if reverse2(a, b) == None:
        print "Can not determine if one curve is reversed"
#        from p_gchart import ThanChart
#        from thanvar.thanfiles import ThanCad
#        sidea.show(ThanCad[2])
    ia, ib = start2(a, b)
    if ia == None: return None #"Something wrong with the parallel lines: Do they overlap?"
    if sideb.isClosed():
        del b[-1]
        b.extend(b)

#---Do the job

    xg, yg, zg = b[ib][:3]
    xr, yr, zr = a[ia][:3]
    gr = [(xg, yg, zg, xr, yr, zr, 1.0, 1.0)]
#    fw = open("q1.syk", "w")
#    form = "%15.4f" * 8 + "\n"
#    fw.write(form % tuple(gr[-1]))

    nr = int(disrange/disint+0.5)
#    while ia < len(a)-1 and ib < len(b)-1:     # This must be enabled for partial matching
    while ia < len(a)-1 and ib < len(b):
        update()
        ia1 = ia + 1
        d = hypot(a[ia1][0]-a[ia][0], a[ia1][1]-a[ia][1])
        ib = min(ib + int(d/disint+0.5), len(b)-1)
        ib1 = mindis2(a[ia1], b, ib, nr)
        xg, yg, zg = b[ib1][:3]
        xr, yr, zr = a[ia1][:3]
        gr.append((xg, yg, zg, xr, yr, zr, 1.0, 1.0))
#        fw.write(form % tuple(gr[-1]))
        ia = ia1
        ib = ib1
#    fw.close()
    return gr


def icp3(sidea, sideb, disint, disrange, update=doNothing):
    """Finds the icp axis of 2 almost identical polylines.

    sideb is the polyline with the biggest number of points (gps)."""
    a = sidea
    b = [b1 for b1 in iterdis3(sideb, disint)]
    if reverse3(a, b) == None: print "Can not determine if one curve is reversed"
    ia, ib = start3(a, b)
    if ia == None: return None #"Something wrong with the parallel lines: Do they overlap?"
    if sideb.isClosed():
        del b[-1]
        b.extend(b)

#---Do the job

    xg, yg, zg = b[ib][:3]
    xr, yr, zr = a[ia][:3]
    gr = [(xg, yg, zg, xr, yr, zr, 1.0, 1.0)]
    nr = int(disrange/disint+0.5)
#    while ia < len(a)-1 and ib < len(b)-1:     # This must be enabled for partial matching
    while ia < len(a)-1 and ib < len(b):
        update()
        ia1 = ia + 1
        d = hypot(hypot(a[ia1][0]-a[ia][0], a[ia1][1]-a[ia][1]), a[ia1][2]-a[ia][2])
        ib = min(ib + int(d/disint+0.5), len(b)-1)
        ib1 = mindis3(a[ia1], b, ib, nr)
        xg, yg, zg = b[ib1][:3]
        xr, yr, zr = a[ia1][:3]
        gr.append((xg, yg, zg, xr, yr, zr, 1.0, 1.0))
        ia = ia1
#        ib = max(ib, ib1)
        ib = ib1
    return gr


def start2(a, b):
    "Find a starting pair."
    for ia in xrange(len(a)):
        xa, ya, za = a[ia][:3]
        dd, ib = min([((x-xa)**2+(y-ya)**2, i) for i,(x,y,z) in enumerate(b)])
#        if ib > 0 and ib < len(b)-1: break  # This must be enabled for partial matching
        if ib < 0.9*len(b): return ia, ib
    return None, None   #"Something wrong with the parallel lines: Do they overlap?"


def start3(a, b):
    "Find a starting pair."
    for ia in xrange(len(a)):
        xa, ya, za = a[ia][:3]
        dd, ib = min([((x-xa)**2+(y-ya)**2+(z-za)**2, i) for i,(x,y,z) in enumerate(b)])
#        if ib > 0 and ib < len(b)-1: break  # This must be enabled for partial matching
        if ib < 0.9*len(b): return ia, ib
    return None, None   #"Something wrong with the parallel lines: Do they overlap?"


def reverse2(a, b, b3d=None):
    """A hack to see if the second line (b) is reversed.

    The problem arises if the last point of (b) is near the first point of (b),
    i.e. (b) is almost closed curve or a helix. If the first point of (a)
    corresponds to the first (or near the first) or to the last (or near the
    last point of (b), we are not sure if this is so, or it is so because
    (b) is reversed.
    Thus we seek points of (a) which corressond to points of (b) which are not
    near 10% within the start of end of (b).
    """
#    print "-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-"
    for per in xfrange(0.0, 0.81, 0.1):
        ia = int(len(a)*per)
        xa, ya, za = a[ia][:3]
        dd, ib = min([((x-xa)**2+(y-ya)**2, i) for i,(x,y,z) in enumerate(b)])
#        print "per, ia, ib, float(ib)/len(b)=", per, ia, ib, float(ib)/len(b)
        if 0.1*len(b) < ib < 0.9*len(b): break
    else:
        return None   #Can not decide if it is reversed or not

    for per in xfrange(per+0.1, 0.91, 0.1):
        ja = int(len(a)*per)
        if ja <= ia: continue      # In case len(a) is so small that per+0.1 corresponds to the same point
        xa, ya, za = a[ja][:3]
        dd, jb = min([((x-xa)**2+(y-ya)**2, i) for i,(x,y,z) in enumerate(b)])
#        print "per, ja, jb, float(jb)/len(b)=", per, ja, jb, float(jb)/len(b)
        if jb == ib: continue
        if 0.1*len(b) < jb < 0.9*len(b): break
    else:
        return None   #Can not decide if it is reversed or not

    if jb == ib:
        return None   #Can not decide if it is reversed or not
    if jb < ib:
        print "Warning: Side b is probably reversed."
        b.reverse()
        if b3d != None: b3d.reverse()     # Reverse the 3d line whose projection is b
    return True


def reverse3(a, b):
    """A hack to see if the second line (b) is reversed.

    The problem arises if the last point of (b) is near the first point of (b),
    i.e. (b) is almost closed curve or a helix. If the first point of (a)
    corresponds to the first (or near the first) or to the last (or near the
    last point of (b), we are not sure if this is so, or it is so because
    (b) is reversed.
    Thus we seek points of (a) which corressond to points of (b) which are not
    near 10% within the start of end of (b).
    """
    for per in xfrange(0.0, 0.81, 0.1):
        ia = int(len(a)*per)
        xa, ya, za = a[ia][:3]
        dd, ib = min([((x-xa)**2+(y-ya)**2+(z-za)**2, i) for i,(x,y,z) in enumerate(b)])
        if 0.1*len(b) < ib < 0.9*len(b): break
    else:
        return None   #Can not decide if it is reversed or not

    for per in xfrange(per+0.1, 0.91, 0.1):
        ja = int(len(a)*per)
        if ja <= ia: continue      # In case len(a) is so small that per+0.1 corresponds to the same point
        xa, ya, za = a[ja][:3]
        dd, jb = min([((x-xa)**2+(y-ya)**2+(z-za)**2, i) for i,(x,y,z) in enumerate(b)])
        if jb == ib: continue
        if 0.1*len(b) < jb < 0.9*len(b): break
    else:
        return None   #Can not decide if it is reversed or not

    if jb == ib:
        return None   #Can not decide if it is reversed or not
    if jb < ib:
        print "Warning: Side b is probably reversed."
        b.reverse()
    return True


def mindis2(ca, b, ib, ibrange):
    "Find nearset distance of point ca to polyline b, range ib+=ibrange."
    imin = -1; dmin = 1e100
    xa, ya, za = ca[:3]
    for ib1 in xrange(max(0, ib-ibrange), min(len(b), ib+ibrange)):
        xb,yb,zb = b[ib1][:3]
        d1 = (xb-xa)**2 + (yb-ya)**2
        if d1 < dmin: dmin=d1; imin=ib1
    assert imin >= 0, "Empty range given."
    return imin


def mindis3(ca, b, ib, ibrange):
    "Find nearset distance of point ca to polyline b, range ib+=ibrange."
    imin = -1; dmin = 1e100
    xa, ya, za = ca[:3]
    for ib1 in xrange(max(0, ib-ibrange), min(len(b), ib+ibrange)):
        xb,yb,zb = b[ib1][:3]
        d1 = (xb-xa)**2 + (yb-ya)**2 + (zb-za)**2
        if d1 < dmin: dmin=d1; imin=ib1
    assert imin >= 0, "Empty range given."
    return imin


def iterdis2(a, dd):
    "Iterate through polyline a, returning a point every d units distance."
    for (xa,ya,za,_), (xb,yb,zb,_) in iterby2(a):
        d = sqrt((xb-xa)**2 + (yb-ya)**2)
        for d1 in xfrange(0.0, d, dd):
#            print "iterdis2: %15.3f%15.3f" % (d1, d)
            x = xa + (xb-xa)/d*d1
            y = ya + (yb-ya)/d*d1
            z = za + (zb-za)/d*d1
            yield x, y, z
    yield xb, yb, zb



def iterdis3(a, dd):
    "Iterate through polyline a, returning a point every d units distance."
    for (xa,ya,za,_), (xb,yb,zb,_) in iterby2(a):
        d = sqrt((xb-xa)**2 + (yb-ya)**2+(zb-za)**2)
        for d1 in xfrange(0.0, d, dd):
            x = xa + (xb-xa)/d*d1
            y = ya + (yb-ya)/d*d1
            z = za + (zb-za)/d*d1
            yield x, y, z
    yield xb, yb, zb
