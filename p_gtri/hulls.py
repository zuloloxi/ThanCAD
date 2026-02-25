"""This module contains functions which compute the 2dimensional convex hull
of a set of lines.
"""
from p_gmath import thanNear2

def _orientation(p, q, r):
    "Result is >0 p-q-r are clockwise, <0 counterclockwise, =0 colinear."
    return (q[1]-p[1])*(r[0]-p[0]) - (q[0]-p[0])*(r[1]-p[1])

def _hulls(cp):
    "Graham scan return the upper and lower hulls."
    u = []
    l = []
    cp = sorted(cp)
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
