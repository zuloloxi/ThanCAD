##############################################################################
# ThanCad 0.1.2 "Free": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2010 Thanasis Stamos,  December 23, 2010
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
ThanCad 0.1.2 "Free": 2dimensional CAD with raster support for engineers.

This module defines functions for line simplification. Methods:
SV : "Least deviation (Stamos-Vassilaki)"
RDP: "Max distance (Ramer–Douglas–Peucker)", 
RV : "First fit (Reumann–Witkam)"
"""
from math import hypot, fabs


def lineSimplify3d(curve, ermeanmax=0.15, erabsmax=0.20, zerabsmax=0.10, method="RDP"):
    "Continuously breaks a curve into 2 line segments, until error is < ermax; select algorithm."
    if method == "SV":
        fun = lineSimplify3dSV
    elif method == "RDP":
        fun = lineSimplify3dRDP
    elif method == "RW":
        fun = lineSimplify3dRW
    else:
        raise ValueError("Unknown simplification method: {}: it should be SV, RDP or RW".format(method))
    return fun(curve, ermeanmax, erabsmax, zerabsmax)


def lineSimplify3dSV(curve, ermeanmax=0.15, erabsmax=0.20, zerabsmax=0.10):
    """Stamos-Vassilaki algorithm: Continuously breaks a curve into 2 line segments, until error is < ermax.

    Copes with closed curves.
    A curve is a list of points. A point is a tuple of a name, x, y, z
    and optionally any other number of dimensions. Only the first 3
    coordinates are taken into account in the simplification.
    """
    n = len(curve)
    if n < 3: return curve[:]
    ermean, erabs, zerabs, mmax = linearise(curve)
    if ermean <= ermeanmax and erabs <= erabsmax and zerabs <= zerabsmax: return [curve[0], curve[-1]]

    if   n >= 20: n1 = int(n/5)
    elif n >= 12: n1 = int(n/4)
    elif n >= 9:  n1 = int(n/3)
    else:         n1 = int(n/2)
    ercritmin = 1.0e101
    for m in range(n1, n-n1+1, n1):
        ermean, erabs, zerabs, mmax = linearise(curve[:m+1])
        ermean2, erabs2, zerabs2, mmax = linearise(curve[m:])
        ermean = (ermean+ermean2)*0.5
        erabs = max(erabs, erabs2)
        zerabs = max(zerabs, zerabs2)
        ercrit = ermean+0.0*erabs
        if ercrit < ercritmin:
            ercritmin = ercrit
            mmin = m
    m = mmin

    a = lineSimplify3dSV(curve[:m+1], ermeanmax, erabsmax, zerabsmax)
    b = lineSimplify3dSV(curve[m:], ermeanmax, erabsmax, zerabsmax)
    return a+b[1:]


def lineSimplify3dRDP(curve, ermeanmax=0.15, erabsmax=0.20, zerabsmax=0.10):
    """Ramer–Douglas–Peucker algorithm: continuously breaks a curve into 2 line segments, until error is < ermax.

    Copes with closed curves.
    A curve is a list of points. A point is a tuple of a name, x, y, z
    and optionally any other number of dimensions. Only the first 3
    coordinates are taken into account in the simplification.
    """
    n = len(curve)
    if n < 3: return curve[:]
    ermean, erabs, zerabs, m = linearise(curve)
    if ermean <= ermeanmax and erabs <= erabsmax and zerabs <= zerabsmax: return [curve[0], curve[-1]]
    a = lineSimplify3dRDP(curve[:m+1], ermeanmax, erabsmax, zerabsmax)
    b = lineSimplify3dRDP(curve[m:], ermeanmax, erabsmax, zerabsmax)
    return a+b[1:]


def lineSimplify3dRW(curve, ermeanmax=0.15, erabsmax=0.20, zerabsmax=0.10):
    """Reumann–Witkam algorithm: continuously breaks a curve into 2 line segments, until error is < ermax.

    Copes with closed curves.
    A curve is a list of points. A point is a tuple of a name, x, y, z
    and optionally any other number of dimensions. Only the first 3
    coordinates are taken into account in the simplification.
    """
    n = len(curve)
    if n < 3: return curve[:]
    curvenew = [curve[0]]
    m1 = 0
    while True:
        for m2 in range(m1+2, n):
            ermean, erabs, zerabs, mmax = linearise(curve[m1:m2+1])
            if not(ermean <= ermeanmax and erabs <= erabsmax and zerabs <= zerabsmax): break
        else:
            if m1 < n-1: curvenew.append(curve[n-1])
            return curvenew
        curvenew.append(curve[m2-1])
        m1 = m2 - 1


def linearise(curve):
    "Finds the error of the curve if it is simplified as a line from the first point to the last."
    if len(curve) < 3: return 0.0, 0.0, 0.0, -1    #Note, in this case, mmax is not used by the caller
    x1, y1, z1 = curve[0][1:4]
    x2, y2, z2 = curve[-1][1:4]

    dx = x2 - x1
    dy = y2 - y1
    if abs(dx)+abs(dy) < 1e-14:   # The curve may be closed (or a series of identical points)
        t = 0.0, 1.0     #Pretend that the line is vertical
        tz = 0.0         #Since tz==0.0, ze (see below) are elevation differences from point (x1,y1,z1)
        #print("t=", t)
    else:
        d = hypot(dx, dy)
        t = dx/d, dy/d
        tz = (z2-z1)/d
    n = -t[1], t[0]
    er = ermax = zermax = 0.0
    mmax = -1
    for m,c2 in enumerate(curve):
        x2, y2, z2 = c2[1:4]
        e = fabs(n[0]*(x2-x1) + n[1]*(y2-y1))
        er += e                            #Note that if all errors e are zero, then mmax=-1, but ..
        if e > ermax: ermax = e; mmax = m  #..also er==0 and caller does not use mmax
        d = fabs(t[0]*(x2-x1) + t[1]*(y2-y1))
        ze = fabs(z2 - (z1+tz*d))
        if ze > zermax: zermax = ze
    #if t == (0.0, 1.0): print("max perp distance to", curve[mmax][1:3])
    return er/len(curve), ermax, zermax, mmax
