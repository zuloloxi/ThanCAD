##############################################################################
# ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2025 Thanasis Stamos, May 20, 2025
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
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
ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers

This module computes the intersection of any pair of elements. It also computes
the extension of lines and arc to intersect any other element.
"""
from math import fabs, atan2, hypot
from p_gmath import PI2, thanNearx, thanNear2, converged3, thanErNear2
from p_ggen import iterby2
from p_gmath import thanintersect
from .thanutil import thanPntNearest2


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
    if ccu is None: coors = iterby2(line.cp)
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
    if ccu is None: coors = iterby2(line.cp)
    else:           coors = (line.thanSegNearest(ccu), )
    ps = []
    for c1, c2 in coors:
        ps.extend(thanintersect.thanSegCir(c1, c2, circle.cc, circle.r))
    return ps


def thanLineLine(line1, line2, ccu):
    "Finds intersection of multi segment line1 with multi segment line2."
    if ccu is None:
        ps = []
        for c1, c2 in iterby2(line1.cp):
            for c3, c4 in iterby2(line2.cp):
                cp = thanintersect.thanSegSeg(c1, c2, c3, c4)
                if cp is not None: ps.append(cp)
        return ps
    c1, c2 = line1.thanSegNearest(ccu)
    c3, c4 = line2.thanSegNearest(ccu)
    cp = thanintersect.thanSegSeg(c1, c2, c3, c4)
    if cp is None: return []
    return [cp]


def thanCurveArc(curve, arc, ccu):
    "Find the intersection of curve with a circle."
    return thanCurveCa(curve, arc, ccu, thanArcLinet)


def thanCurveCircle(curve, circle, ccu):
    "Find the intersection of curve with a circle."
    return thanCurveCa(curve, circle, ccu, thanCircleLinet)


def thanCurveCa(curve, circle, ccu, caLinet):
    "Find the intersection of curve with a circle or arc."
    ntries = 16
    cp1 = curve.cp
    tp1 = curve.tp
    ctp = [1.0e100, 1.0e100, 1.0e100]
    dm = 1.0e100
    erpp = 1.0e100
    erp = erpp/10.0
    for itry in range(ntries):
        #print
        #print
        #print "thancurveCircle() itry=", itry
        if itry == 0:
            ct, iseg1, _ = thanPntNearest2(cp1, ccu)
            if ct is None: return []
            i1, i2 = bracketNearest(cp1, iseg1)
        else:
            i1 = 0
            i2 = len(cp1)
        #print "thancurveline() i1-2=", i1, i2

        ct, iseg1 = caLinet(circle, cp1, i1, i2, ccu)
        if ct is None: return []
        #print "thancurveCircle() ctp, ct=", ctp, ct
        er = thanErNear2(ctp, ct)
        #print "errors=", erpp, erp, er
        cov = converged3(er, erp, erpp)
        if cov == 1: return [ct]    #Converged
        if cov == -1:
            #print "thanCurveLine(): iterations stopped after step %d due to instability." % (itry,)
            return []
        if thanNear2(ctp, ct):     #This usually saves one step
            #print "thanNear2() succeeded but converged3() did not"
            return [ct]

        i1, i2 = bracketNearest(cp1, iseg1)
        if itry == 0:
            dm  = sum(hypot(cp1[i+1][1]-cp1[i][1], cp1[i+1][0]-cp1[i][0]) for i in range(i1, i2-1))
            dm /= (i2-i1-1)
            #print "dm=",dm
        dm *= 0.5          #Make finer line representation of the curve
        #print "thancurveCircle() i1-2=", i1, i2, "dm=", dm
        #print "len(cp1, tp1)=", len(cp1), len(tp1)
        #print "tp1=", tp1[i1], tp1[i2-1]
        cp1, tp1 = curve.than2Line(dm, ta=tp1[i1], tb=tp1[i2-1])
        ctp = ct
        erpp, erp = erp, er
    else:
        pass
        #print "thanCurveCircle(): max number of iterations reached: %d" % (ntries,)
    return [ct]


def thanCurveLine(curve, line, ccu):
    "Find the intersection of curve with a line."
    ntries = 16
    cp1 = curve.cp
    tp1 = curve.tp
    cp2 = line.cp
    ctp = [1.0e100, 1.0e100, 1.0e100]
    dm = 1.0e100
    erpp = 1.0e100
    erp = erpp/10.0
    for itry in range(ntries):
        #print
        #print
        #print "thancurveLine() itry=", itry
        if itry == 0:
            ct, iseg1, _ = thanPntNearest2(cp1, ccu)
            if ct is None: return []
            ct, iseg2, _ = thanPntNearest2(cp2, ccu)
            if ct is None: return []
            i1, i2 = bracketNearest(cp1, iseg1)
            i3, i4 = bracketNearest(cp2, iseg2)
        else:
            i1 = 0
            i2 = len(cp1)
        #print "thancurveline() i1-4=", i1, i2, i3, i4

        ct, iseg1, iseg2 = thanLineLinet(cp1, i1, i2, cp2, i3, i4, ccu)
        if ct is None: return []
        #print "thancurveline() ctp, ct=", ctp, ct
        er = thanErNear2(ctp, ct)
        #print "errors=", erpp, erp, er
        cov = converged3(er, erp, erpp)
        if cov == 1: return [ct]    #Converged
        if cov == -1:
            #print "thanCurveLine(): iterations stopped after step %d due to instability." % (itry,)
            return []
        if thanNear2(ctp, ct):     #This usually saves one step
            #print "thanNear2() succeeded but converged3() did not"
            return [ct]

        i1, i2 = bracketNearest(cp1, iseg1)
        i3, i4 = bracketNearest(cp2, iseg2)
        if itry == 0:
            dm  = sum(hypot(cp1[i+1][1]-cp1[i][1], cp1[i+1][0]-cp1[i][0]) for i in range(i1, i2-1))
            dm /= (i2-i1-1)
            #print "dm=",dm
        dm *= 0.5          #Make finer line representation of the curve
        #print "thancurveline() i1-4=", i1, i2, i3, i4, "dm=", dm
        #print "len(cp1, tp1)=", len(cp1), len(tp1)
        #print "len(cp2,    )=", len(cp2)
        #print "tp1=", tp1[i1], tp1[i2-1]
        cp1, tp1 = curve.than2Line(dm, ta=tp1[i1], tb=tp1[i2-1])
        ctp = ct
        erpp, erp = erp, er
    else:
        pass
        #print "thanCurveLine(): max number of iterations reached: %d" % (ntries,)
    return [ct]


def thanCurveCurve(curve, eother, ccu):
    "Find the intersection of curve with another curve."
    ntries = 16
    cp1 = curve.cp
    tp1 = curve.tp
    cp2 = eother.cp
    tp2 = eother.tp
    ctp = [1.0e100, 1.0e100, 1.0e100]
    dm = 1.0e100
    erpp = 1.0e100
    erp = erpp/10.0
    for itry in range(ntries):
        #print
        #print
        #print "thancurvecurve() itry=", itry
        if itry == 0:
            ct, iseg1, _ = thanPntNearest2(cp1, ccu)
            if ct is None: return []
            ct, iseg2, _ = thanPntNearest2(cp2, ccu)
            if ct is None: return []
            i1, i2 = bracketNearest(cp1, iseg1)
            i3, i4 = bracketNearest(cp2, iseg2)
        else:
            i1 = i3 = 0
            i2 = len(cp1)
            i4 = len(cp2)
        #print "thancurvecurve() i1-4=", i1, i2, i3, i4

        ct, iseg1, iseg2 = thanLineLinet(cp1, i1, i2, cp2, i3, i4, ccu)
        if ct is None: return []
        #print "thancurvecurve() ctp, ct=", ctp, ct
        er = thanErNear2(ctp, ct)
        #print "errors=", erpp, erp, er
        cov = converged3(er, erp, erpp)
        if cov == 1: return [ct]    #Converged
        if cov == -1:
            #print "thanCurveCurve(): iterations stopped after step %d due to instability." % (itry,)
            return []
        if thanNear2(ctp, ct):     #This usually saves one step
            #print "thanNear2() succeeded but converged3() did not"
            return [ct]

        i1, i2 = bracketNearest(cp1, iseg1)
        i3, i4 = bracketNearest(cp2, iseg2)
        if itry == 0:
            dm  = sum(hypot(cp1[i+1][1]-cp1[i][1], cp1[i+1][0]-cp1[i][0]) for i in range(i1, i2-1))
            dm += sum(hypot(cp2[i+1][1]-cp2[i][1], cp2[i+1][0]-cp2[i][0]) for i in range(i3, i4-1))
            dm /= (i2-i1+i4-i3-2)
            #print "dm=",dm
        dm *= 0.5          #Make finer line representation of the curve
        #print "thancurvecurve() i1-4=", i1, i2, i3, i4, "dm=", dm
        #print "len(cp1, tp1)=", len(cp1), len(tp1)
        #print "len(cp2, tp2)=", len(cp2), len(tp2)
        #print "tp1=", tp1[i1], tp1[i2-1]
        #print "tp2=", tp2[i3], tp2[i4-1]
        cp1, tp1 =  curve.than2Line(dm, ta=tp1[i1], tb=tp1[i2-1])
        cp2, tp2 = eother.than2Line(dm, ta=tp2[i3], tb=tp2[i4-1])
        ctp = ct
        erpp, erp = erp, er
    else:
        pass
        #print "thanCurveCurve(): max number of iterations reached: %d" % (ntries,)
    return [ct]


def thanLineLinet(cp1, i1, i2, cp2, i3, i4, ccu):
    "Finds intersection of multi segment line1 with multi segment line2 near point ccu."
    d = 1.0e100
    iseg1t = iseg2t = ct = None
    for iseg1 in range(i1, i2-1):
        for iseg2 in range(i3, i4-1):
            cp = thanintersect.thanSegSeg(cp1[iseg1], cp1[iseg1+1], cp2[iseg2], cp2[iseg2+1])
            if cp is None: continue
            d1 = hypot(ccu[1]-cp[1], ccu[0]-cp[0])
            if d1 > d: continue
            iseg1t = iseg1
            iseg2t = iseg2
            d = d1
            ct = cp
    return ct, iseg1t, iseg2t


def thanCircleLinet(circle, cp1, i1, i2, ccu):
    "Finds intersection of circle with line cp1 searching from i1 to i2."
    d = 1.0e100
    iseg1t = ct = None
    for iseg1 in range(i1, i2-1):
        cps = thanintersect.thanSegCir(cp1[iseg1], cp1[iseg1+1], circle.cc, circle.r)
        for cp in cps:
            d1 = hypot(ccu[1]-cp[1], ccu[0]-cp[0])
            if d1 > d: continue
            iseg1t = iseg1
            d = d1
            ct = cp
    return ct, iseg1t


def thanArcLinet(arc, cp1, i1, i2, ccu):
    "Finds intersection of arc with line cp1 searching from i1 to i2."
    d = 1.0e100
    iseg1t = ct = None
    for iseg1 in range(i1, i2-1):
        cps = thanintersect.thanSegCir(cp1[iseg1], cp1[iseg1+1], arc.cc, arc.r)
        for cp in cps:
            th = atan2(cp[1]-arc.cc[1], cp[0]-arc.cc[0]) % PI2
            if not arc.thanThetain(th)[0]: continue
            d1 = hypot(ccu[1]-cp[1], ccu[0]-cp[0])
            if d1 > d: continue
            iseg1t = iseg1
            d = d1
            ct = cp
    return ct, iseg1t


def bracketNearest(cp, iseg):
    "Return  previous and next segment of iseg."
    i1 = iseg-1
    if i1 < 0: i1 = 0
    i2 = iseg + 3
    if i2 > len(cp): i2 = len(cp)
    return i1, i2


def thanInit():
    "Initialises this module; no circular imports this way."
    from .thanline  import ThanLine, ThanCurve
    from .thancirc  import ThanCircle
    from .thanarc   import ThanArc
    from .thanimpil import ThanImage
    from .thanface3d import ThanFace3d
    from .thanclasses import thanElemClass
    global thanIntPair, thanExtPair
    thanIntPair = \
    { ThanArc:    { ThanArc    : thanArcArc,
                    ThanCircle : thanArcCircle,
                    ThanImage  : thanArcLine,
                    ThanLine   : thanArcLine,
                    ThanCurve  : thanArcLine,
                    ThanFace3d : thanArcLine,
                  },

      ThanCircle: { ThanArc    : __Inv(thanArcCircle),
                    ThanCircle : thanCircleCircle,
                    ThanImage  : thanCircleLine,
                    ThanLine   : thanCircleLine,
                    ThanCurve  : thanCircleLine,
                    ThanFace3d : thanCircleLine,
                  },

      ThanLine:   { ThanArc    : __Inv(thanArcLine),
                    ThanCircle : __Inv(thanCircleLine),
                    ThanImage  : thanLineLine,
                    ThanLine   : thanLineLine,
                    ThanCurve  : thanLineLine,
                    ThanFace3d : thanLineLine,
                  },

      ThanImage:  { ThanArc    : __Inv(thanArcLine),
                    ThanCircle : __Inv(thanCircleLine),
                    ThanImage  : thanLineLine,
                    ThanLine   : thanLineLine,
                    ThanCurve  : thanLineLine,
                    ThanFace3d : thanLineLine,
                  },

      ThanCurve:  { ThanArc    : thanCurveArc,
                    ThanCircle : thanCurveCircle,
                    ThanImage  : thanCurveLine,
                    ThanLine   : thanCurveLine,
                    ThanCurve  : thanCurveCurve,
                    ThanFace3d : thanLineLine,
                  },

      ThanFace3d: { ThanArc    : __Inv(thanArcLine),
                    ThanCircle : __Inv(thanCircleLine),
                    ThanImage  : thanLineLine,
                    ThanLine   : thanLineLine,
                    ThanCurve  : thanLineLine,
                    ThanFace3d : thanLineLine,
                  },
    }
    eq = {}                                 #Equivalent class for a ThanCurve subclass
    for clas in thanElemClass.values():     #Create a dict for every class. Determine equivalent class of ThanCurve subclasses #works for python2,3
        if clas not in thanIntPair:
            thanIntPair[clas] = {}          #Create an empty dict for class
        if issubclass(clas, ThanCurve):
            e = clas()                      #Instantiate class
            if e.than2Line(None): eq[clas] = ThanCurve  #If than2Line() is implemented, then it is a curve..
            else:                 eq[clas] = ThanLine   #..otherwise it is just a dense line
    for clas in thanElemClass.values():    #Fill dictionary of ThanCurve subclasses  #works for python2,3
        if clas not in eq: continue    #It is not a subclass of ThanCurve: nothing to do
        d = thanIntPair[clas]
        #deq = thanIntPair[eq[clas]]
        for clas1, func1 in thanIntPair[eq[clas]].items(): #Copy dictionary of equivalent class   #works for python2,3
            if clas1 not in d: d[clas1] = func1
    for clas in thanElemClass.values():     #Add ThanCurve subclasses to all dictionaries  #works for python2,3
        d = thanIntPair[clas]
        for clas1 in thanElemClass.values():   #works for python2,3
            if clas1 in d: continue
            if clas1 not in eq: continue    #It is not a subclass of ThanCurve: nothing to do
            func1 = d.get(eq[clas1])        #Get the function for the equivalent class of clas1
            if func1 is not None: d[clas1] = func1


    thanExtPair = \
    { (ThanArc,    ThanArc)    : extArc2Arc,
      (ThanArc,    ThanCircle) : extArc2Circle,
      (ThanArc,    ThanImage)  : extArc2Line,
      (ThanArc,    ThanLine)   : extArc2Line,
      (ThanArc,    ThanCurve)  : extArc2Line,

      (ThanLine,   ThanArc)    : extLine2Arc,
      (ThanLine,   ThanCircle) : extLine2Circle,
      (ThanLine,   ThanImage)  : extLine2Line,
      (ThanLine,   ThanLine)   : extLine2Line,
      (ThanLine,   ThanCurve)  : extLine2Line,

      (ThanCurve,  ThanArc)    : extLine2Arc,
      (ThanCurve,  ThanCircle) : extLine2Circle,
      (ThanCurve,  ThanImage)  : extLine2Line,
      (ThanCurve,  ThanLine)   : extLine2Line,
      (ThanCurve,  ThanCurve)  : extLine2Line,
    }


def thanIntsnap(e1, e2, ccu, proj):
    "Call the appropriate intersection function; find distance from mouse point."
    func = thanIntPair[e1.__class__].get(e2.__class__, thanDummy)
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
    #print("tra01:", e1.__class__, e2.__class__)
    #print("tra02:", thanIntPair)
    func = thanIntPair[e1.__class__].get(e2.__class__, thanDummy)
    #print( "tra003:", func)
    ps = []
    for cp in func(e1, e2, None):
        cc = list(proj[1].thanVar["elevation"])
        cc[0] = cp[0]
        cc[1] = cp[1]
        ps.append(cc)
    return ps


def extArc2Arc(arc1, arc2, ccu):
    "Finds intersection on the extension of the first arc to the second arc."
    ps = []
    iend = __arcend(arc1, ccu)
    for cp in thanintersect.thanCirCir(arc1.cc, arc1.r, arc2.cc, arc2.r):
        th = atan2(cp[1]-arc1.cc[1], cp[0]-arc1.cc[0]) % PI2
        if arc1.thanThetain(th)[0]: continue     #Intersection is within the first arc (which must be extended)
        th = atan2(cp[1]-arc2.cc[1], cp[0]-arc2.cc[0]) % PI2
        if not arc2.thanThetain(th)[0]: continue #Intersection in not within the second arc (which is the boundary)
        d = arc1.thanAngularDist(iend, cp)
        ps.append((d, cp))
    return iend, ps


def __arcend(arc1, ccu):
    "Find the nearest arc endpoint to the point the user clicked."
    if arc1.thanAngularDist(0, ccu) < arc1.thanAngularDist(1, ccu):
        iend = 0      #Nearest end point to the point that the user clicked is first endpoint
    else:
        iend = 1      #Nearest end point to the point that the user clicked is last endpoint
    return iend


def extArc2Circle(arc1, circle, ccu):
    "Finds intersection on the extension of the arc to the circle."
    ps = []
    iend = __arcend(arc1, ccu)
    for cp in thanintersect.thanCirCir(arc1.cc, arc1.r, circle.cc, circle.r):
        th = atan2(cp[1]-arc1.cc[1], cp[0]-arc1.cc[0]) % PI2
        if arc1.thanThetain(th)[0]: continue      #Intersection is within the first arc (which must be extened)
        d = arc1.thanAngularDist(iend, cp)
        ps.append((d, cp))
    return iend, ps


def extArc2Line(arc1, line, ccu):
    "Finds intersection on the extension of the arc to the line."
    ps = []
    iend = __arcend(arc1, ccu)
    for c1, c2 in iterby2(line.cp):
        for cp in thanintersect.thanSegCir(c1, c2, arc1.cc, arc1.r):
            th = atan2(cp[1]-arc1.cc[1], cp[0]-arc1.cc[0]) % PI2
            if arc1.thanThetain(th)[0]: continue     #Intersection is within the first arc (which must be extended)
            d = arc1.thanAngularDist(iend, cp)
            ps.append((d, cp))
    return iend, ps


def extLine2Arc(line1, arc, ccu):
    "Finds intersection on the extension of the line to the arc."
    ps = []
    if len(line1.cp) < 2: return ps
    iend, c1, c2 = __linend(line1, ccu)
    for cp, u in thanintersect.thanSegCirGen(c1, c2, arc.cc, arc.r, abisline=True):
        if u <= 1.0 or thanNearx(u, 1.0): continue      #Intersection is within the line (which must be extended)
        th = atan2(cp[1]-arc.cc[1], cp[0]-arc.cc[0]) % PI2
        if not arc.thanThetain(th)[0]: continue #Intersection in not within the second arc (which is the boundary)
        d = hypot(cp[0]-line1.cp[iend][0], cp[1]-line1.cp[iend][1])
        ps.append((d, cp))
    return iend, ps


def __linend(line1, ccu):
    "Find the nearest line endpoint to the point the user clicked."
    if hypot(ccu[0]-line1.cp[0] [0], ccu[1]-line1.cp[0] [1]) < \
       hypot(ccu[0]-line1.cp[-1][0], ccu[1]-line1.cp[-1][1]):
        iend = 0
        c2, c1 = line1.cp[:2]      #First segment of polyline
    else:
        iend = len(line1.cp) - 1
        c1, c2 = line1.cp[-2:]     #Last  segment of polyline
    return iend, c1, c2


def extLine2Circle(line1, arc, ccu):
    "Finds intersection on the extension of the line to the circle."
    ps = []
    if len(line1.cp) < 2: return ps
    iend, c1, c2 = __linend(line1, ccu)
    for cp, u in thanintersect.thanSegCirGen(c1, c2, arc.cc, arc.r, abisline=True):
        if u <= 1.0 or thanNearx(u, 1.0): continue      #Intersection is within the line (which must be extended)
        d = hypot(cp[0]-line1.cp[iend][0], cp[1]-line1.cp[iend][1])
        ps.append((d, cp))
    return iend, ps


def extLine2Line(line1, line2, ccu):
    "Finds intersection of multi segment line1 with multi segment line2."
    ps = []
    if len(line1.cp) < 2: return ps
    iend, c1, c2 = __linend(line1, ccu)
    for c3, c4 in iterby2(line2.cp):
        res = thanintersect.thanSegSegGen(c1, c2, c3, c4, abisline=True, c12isline=False)
        if res is None: continue
        cp, (u,_) = res
        if u <= 1.0 or thanNearx(u, 1.0): continue      #Intersection is within the line (which must be extended)
        d = hypot(cp[0]-line1.cp[iend][0], cp[1]-line1.cp[iend][1])
        ps.append((d, cp))
    return iend, ps

def thanDummyext(e1, e2, ccu):
    "Returns no intersections."
    return 0, []

def thanExt(e1, e2, ccu, proj):
    "Call the appropriate extension function; find distance from nearest endpoint."
    func = thanExtPair.get((e1.__class__, e2.__class__), thanDummyext)
    return func(e1, e2, ccu)
