# -*- coding: iso-8859-7 -*-
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

This module defines a function for line simplification.
"""
from math import sqrt, fabs


def lineSimplify3d(curve, ermeanmax=0.15, erabsmax=0.20, zerabsmax=0.10):
    """Continuously breaks a curve into 2 line segments, until error is < ermax.

    A curve is a list of points. A point is a tuple of a name, x, y, z and optionally
    any other number of dimensions. Only the first 3 coordinates are taken into
    account in the simplification.
    """
    n = len(curve)
    if n < 3: return curve[:]
    ermean, erabs, zerabs = linearise(curve)
    if ermean <= ermeanmax and erabs <= erabsmax and zerabs <= zerabsmax: return [curve[0], curve[-1]]

    if   n >= 20: n1 = int(n/5)
    elif n >= 12: n1 = int(n/4)
    elif n >= 9:  n1 = int(n/3)
    else:         n1 = int(n/2)
    ercritmin = 1.0e101
    for m in range(n1, n-n1+1, n1):
        ermean, erabs, zerabs = linearise(curve[:m+1])
        ermean2, erabs2, zerabs2 = linearise(curve[m:])
        ermean = (ermean+ermean2)*0.5
        erabs = max(erabs, erabs2)
        zerabs = max(zerabs, zerabs2)
        ercrit = ermean+0.0*erabs
        if ercrit < ercritmin:
            ercritmin = ercrit
            mmin = m
    m = mmin

    a = lineSimplify3d(curve[:m+1], ermeanmax, erabsmax, zerabsmax)
    b = lineSimplify3d(curve[m:], ermeanmax, erabsmax, zerabsmax)
    return a+b[1:]


def linearise(curve):
    "Finds the error of the curve if it is simplified as a line from the first point to the last."
    if len(curve) < 3: return 0.0, 0.0, 0.0
    x1, y1, z1 = curve[0][1:4]
    x2, y2, z2 = curve[-1][1:4]
    dx = x2 - x1; dy = y2 - y1
    d = sqrt(dx**2+dy**2)
    if d == 0.0: return 1e100,1e100,1e100    # The line may be closed (or a series of identical points)
    t = dx/d, dy/d; tz = (z2-z1)/d
    n = -t[1], t[0]
    er = ermax = zermax = 0.0
    for c2 in curve:
        x2, y2, z2 = c2[1:4]
        e = fabs(n[0]*(x2-x1) + n[1]*(y2-y1))
        er += e
        if e > ermax: ermax = e
        d = fabs(t[0]*(x2-x1) + t[1]*(y2-y1))
        ze = fabs(z2 - (z1+tz*d))
        if ze > zermax: zermax = ze
    return er/len(curve), ermax, zermax
