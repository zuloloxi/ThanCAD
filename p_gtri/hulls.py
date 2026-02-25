##############################################################################
# ThanCad 0.0.8 "DoSomething": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c)  February 23, 2008  by Thanasis Stamos
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
ThanCad 0.0.8 "DoSomething": 2dimensional CAD with raster support for engineers.

This module conmtains functions which compute the 2dimensional convex hull
of a set of lines.
"""
from p_gmath import thanNear2

def _orientation(p, q, r):
    "Result is >0 p-q-r are clockwise, <0 countercloskwise, =0 colinear."
    return (q[1]-p[1])*(r[0]-p[0]) - (q[0]-p[0])*(r[1]-p[1])

def _hulls(cp):
    "Graham scan return the upper and lower hulls."
    u = [] 
    l = []
    cp.sort()
    for p in cp:
        while len(u) > 1 and _orientation(u[-2], u[-1], p) <= 0.0:
            u.pop()
        while len(l) > 1 and _orientation(l[-2], l[-1], p) >= 0.0:
            l.pop()
        u.append(p)
        l.append(p)
    return u, l

def hull(cp):
    "Find the convex hull of a set of points using Graham scan."
    if len(cp) < 3: return None               # Degenerate convex hull
    u, l = _hulls(cp)
    if len(u) < 3 and len(l) < 3: return None # Degenerate convex hull
    if thanNear2(u[0], l[0]):
        assert thanNear2(u[-1], l[-1])
        l.reverse()
        l.pop()
        l.extend(u)
        u = l
    elif thanNear2(u[-1], l[0]):
        u.pop()
        u.extend(l)
    elif thanNear2(u[0], l[-1]):
        l.pop()
        l.extend(u)
        u = l
    elif thanNear2(u[-1], l[-1]):
        l.reverse()
        u.pop()
        u.extend(l)
    else:
        assert False, "Upper and lower hull should be continuous."
    return u
