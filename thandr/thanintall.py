##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module computes the intersection of any pair of elements.
"""
from math import fabs, atan2
from p_gmath import PI2
from p_ggen import iterby2
from p_gmath import thanintersect


class __Inv:
    "Calls a function with inverted arguments."
    def __init__(self, func):
        self.func = func
    def __call__(self, e1, e2, ccu):
        return self.func(e2, e1, ccu)


def thanDummy(e1, e2, ccu):
    "Returns no intersections."
    return []

def thanArcArc(arc1, arc2, ccu):
    "Finds intersection of arc with arc."
    ps = []
    for cp in thanintersect.thanCirCir(arc1.cc, arc1.r, arc2.cc, arc2.r):
        th = atan2(cp[1]-arc1.cc[1], cp[0]-arc1.cc[0]) % PI2
        if not arc1.thanThetain(th)[0]: continue
        th = atan2(cp[1]-arc2.cc[1], cp[0]-arc2.cc[0]) % PI2
        if not arc2.thanThetain(th)[0]: continue
        ps.append(cp)
    return ps

def thanArcCircle(arc, circle, ccu):
    "Finds intersection of arc with circle."
    ps = []
    for cp in thanintersect.thanCirCir(arc.cc, arc.r, circle.cc, circle.r):
        th = atan2(cp[1]-arc.cc[1], cp[0]-arc.cc[0]) % PI2
        if not arc.thanThetain(th)[0]: continue
        ps.append(cp)
    return ps

def thanArcLine(arc, line, ccu):
    "Finds intersection of self with line segment c1-c2."
    if ccu == None: coors = iterby2(line.cp)
    else:           coors = (line.thanSegNearest(ccu), )
    ps = []
    for c1, c2 in coors:
        for cp in thanintersect.thanSegCir(c1, c2, arc.cc, arc.r):
            th = atan2(cp[1]-arc.cc[1], cp[0]-arc.cc[0]) % PI2
            if arc.thanThetain(th)[0]: ps.append(cp)
    return ps

def thanCircleCircle(circle1, circle2, ccu):
    "Finds intersection of circle with circle."
    return thanintersect.thanCirCir(circle1.cc, circle1.r, circle2.cc, circle2.r)

def thanCircleLine(circle, line, ccu):
    "Finds intersection of self with line segment c1-c2."
    if ccu == None: coors = iterby2(line.cp)
    else:           coors = (line.thanSegNearest(ccu), )
    ps = []
    for c1, c2 in coors:
        ps.extend(thanintersect.thanSegCir(c1, c2, circle.cc, circle.r))
    return ps

def thanLineLine(line1, line2, ccu):
    "Finds intersection of multi segment line1 with multi segment line2."
    if ccu == None:
        ps = []
        for c1, c2 in iterby2(line1.cp):
            for c3, c4 in iterby2(line2.cp):
                cp = thanintersect.thanSegSeg(c1, c2, c3, c4)
                if cp != None: ps.append(cp)
        return ps
    c1, c2 = line1.thanSegNearest(ccu)
    c3, c4 = line2.thanSegNearest(ccu)
    cp = thanintersect.thanSegSeg(c1, c2, c3, c4)
    if cp == None: return []
    return [cp]

def thanInit():
    "Initialises this module; no circular imports this way."
    from thanline  import ThanLine, ThanCurve
    from thancirc  import ThanCircle
    from thanpoint import ThanPoint
    from thanarc   import ThanArc
    from thantext  import ThanText
    from thanimpil import ThanImage

    global thanIntPair
    thanIntPair = \
{ (ThanArc,    ThanArc)    : thanArcArc,
  (ThanArc,    ThanCircle) : thanArcCircle,
  (ThanArc,    ThanImage)  : thanArcLine,
  (ThanArc,    ThanLine)   : thanArcLine,
  (ThanArc,    ThanCurve)  : thanArcLine,
#  (ThanArc,    ThanPoint)  : thanDummy,
#  (ThanArc,    ThanText)   : thanDummy,

  (ThanCircle, ThanArc)    : __Inv(thanArcCircle),
  (ThanCircle, ThanCircle) : thanCircleCircle,
  (ThanCircle, ThanImage)  : thanCircleLine,
  (ThanCircle, ThanLine)   : thanCircleLine,
  (ThanCircle, ThanCurve)  : thanCircleLine,
#  (ThanCircle, ThanPoint)  : thanDummy,
#  (ThanCircle, ThanText)   : thanDummy,

  (ThanLine,   ThanArc)    : __Inv(thanArcLine),
  (ThanLine,   ThanCircle) : __Inv(thanCircleLine),
  (ThanLine,   ThanImage)  : thanLineLine,
  (ThanLine,   ThanLine)   : thanLineLine,
  (ThanLine,   ThanCurve)  : thanLineLine,
#  (ThanLine,   ThanPoint)  : thanDummy,
#  (ThanLine,   ThanText)   : thanDummy,

  (ThanImage,  ThanArc)    : __Inv(thanArcLine),
  (ThanImage,  ThanCircle) : __Inv(thanCircleLine),
  (ThanImage,  ThanImage)  : thanLineLine,
  (ThanImage,  ThanLine)   : thanLineLine,
  (ThanImage,  ThanCurve)  : thanLineLine,
#  (ThanImage,  ThanPoint)  : thanDummy,
#  (ThanImage,  ThanText)   : thanDummy,

  (ThanCurve,   ThanArc)    : __Inv(thanArcLine),
  (ThanCurve,   ThanCircle) : __Inv(thanCircleLine),
  (ThanCurve,   ThanImage)  : thanLineLine,
  (ThanCurve,   ThanLine)   : thanLineLine,
  (ThanCurve,   ThanCurve)  : thanLineLine,
#  (ThanLine,   ThanPoint)  : thanDummy,
#  (ThanLine,   ThanText)   : thanDummy,



#  (ThanPoint,  ThanArc)    : thanDummy,
#  (ThanPoint,  ThanCircle) : thanDummy,
#  (ThanPoint,  ThanImage)  : thanDummy,
#  (ThanPoint,  ThanLine)   : thanDummy,
#  (ThanPoint,  ThanPoint)  : thanDummy,
#  (ThanPoint,  ThanText)   : thanDummy,

#  (ThanText,   ThanArc)    : thanDummy,
#  (ThanText,   ThanCircle) : thanDummy,
#  (ThanText,   ThanImage)  : thanDummy,
#  (ThanText,   ThanLine)   : thanDummy,
#  (ThanText,   ThanPoint)  : thanDummy,
#  (ThanText,   ThanText)   : thanDummy,
}

def thanIntsnap(e1, e2, ccu, proj):
    "Call the appropriate intersection function; find distance from mouse point."
    func = thanIntPair.get((e1.__class__, e2.__class__), thanDummy)
    ps = []
    for cp in func(e1, e2, ccu):
        cc = list(proj[1].thanVar["elevation"])
        cc[0] = cp[0]
        cc[1] = cp[1]
        ps.append((fabs(cc[0]-ccu[0])+fabs(cc[1]-ccu[1]), "int", cc))
    return ps

def thanInt(e1, e2, proj):
    "Call the appropriate intersection function."
    if e1 is e2: return []
    func = thanIntPair.get((e1.__class__, e2.__class__), thanDummy)
    ps = []
    for cp in func(e1, e2, None):
        cc = list(proj[1].thanVar["elevation"])
        cc[0] = cp[0]
        cc[1] = cp[1]
        ps.append(cc)
    return ps
