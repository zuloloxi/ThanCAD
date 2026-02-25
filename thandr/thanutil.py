##############################################################################
# ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2016 Thanasis Stamos, June 19, 2016
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers

This module defines utilities for lines.
"""
#from past.builtins import xrange
from p_ggen.py23 import xrange
from math import hypot, fabs, atan2, pi
from p_gmath import thanNearx, PI2, dpt


def thanPntNearest(cp, ccu):
        "Finds the nearest point of this line to a point."
        return thanPntNearest2(cp, ccu)[0]


def thanPntNearest2(cp, ccu):
        "Finds the nearest point of this line to a point."
        dmin = 1.0e100
        cp1 = None
        iseg = -1
        tcp1 = -1.0
        tall = 0.0
        for i in xrange(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
            aa = hypot(*a)
            tall += aa
            if thanNearx(aa, 0.0): continue      # Segment has zero length
            ta = a[0]/aa, a[1]/aa
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dt = ta[0]*b[0]+ta[1]*b[1]
            if   thanNearx(dt, 0.0) : dt = 0.0
            elif thanNearx(dt, aa)  : dt = aa
            elif dt < 0.0 or dt > aa: continue
            dn = fabs(-ta[1]*b[0]+ta[0]*b[1])
            if dn < dmin:
                cp1 = [e+(f-e)*dt/aa for (e,f) in zip(cp[i-1], cp[i])]  #works for python2,3
                dmin = dn
                iseg = i
                tcp1 = tall - aa + dt
        return cp1, iseg, tcp1


def thanSegNearest(cp, ccu):
        """Finds the nearest segment of this line to a point.

        It is an optimisation of thanPntNearest2(), if the nearest point is
        not needed.
        This function is used in thanintall in order to find the intersection
        of a line and another ThanCad element, when object snap intersection
        is enabled. We take advantage of the fact that the mouse coordinates
        ccu are already very near the line (and the other element). Thus, we
        don't check if the projection of the ccu to the line segment is indeed
        between the end of the line segment. However thanintall will ensure
        that the intersection point will belong to both elements.
        """
        dmax=1e100
        for i in xrange(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
            aa = hypot(*a)
            if thanNearx(aa, 0.0): continue      # Segment has zero length
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dn = fabs(a[0]*b[1]-a[1]*b[0]) / aa
            if dn < dmax: imax=i; dmax=dn
        return cp[imax-1], cp[imax]


def thanPerpPoints(cp, ccu):
        "Finds perpendicular point from ccu to polyline."
        ps = []
        tall = 0.0
        for i in xrange(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
            aa = hypot(*a)
            tall += aa
            if thanNearx(aa, 0.0): continue      # Segment has zero length
            ta = a[0]/aa, a[1]/aa
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dt = ta[0]*b[0]+ta[1]*b[1]
            if   thanNearx(dt, 0.0) : dt = 0.0
            elif thanNearx(dt, aa)  : dt = aa
            elif dt < 0.0 or dt > aa: continue
            #dn = fabs(-ta[1]*b[0]+ta[0]*b[1])
            cp1 = [e+(f-e)*dt/aa for (e,f) in zip(cp[i-1], cp[i])]  #works for python2,3
            ps.append(cp1)
        return ps


def thanPerpPointsC(cp, ccu, thtol):
        "Finds perpendicular point from ccu to a curve represented by small lines."
        ps = []
        tall = 0.0
        dtp = None
        for i in xrange(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
            aa = hypot(*a)
            tall += aa
            if thanNearx(aa, 0.0): dtp=None; continue    # Segment has zero length; this shouldn't happen, so I don't bother if I lose a point
            ta = a[0]/aa, a[1]/aa
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dt = ta[0]*b[0]+ta[1]*b[1]
            if   thanNearx(dt, 0.0): dt = 0.0
            elif thanNearx(dt, aa) : dt = aa
            if dt < 0.0 or dt > aa:
                if dtp is not None and dt*dtp < 0.0:
                    th1 = atan2(cp[i-1][0]-cp[i-2][0], cp[i-1][1]-cp[i-2][1])
                    th2 = atan2(cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1])
                    dth = dpt(th2-th1)
                    if dth > pi: dth = fabs(dth-PI2)
                    if dth <= thtol:             # It is smooth enough (it is not a corner)
                        ps.append(list(cp[i-1]))
            else:
                #dn = fabs(-ta[1]*b[0]+ta[0]*b[1])
                cp1 = [e+(f-e)*dt/aa for (e,f) in zip(cp[i-1], cp[i])]  #works for python2,3
                ps.append(cp1)
            dtp = dt
        return ps
