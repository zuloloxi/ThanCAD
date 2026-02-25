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

This module defines the circular arc element.
"""

from math import atan2, tan, pi, fabs, cos, sin, hypot
import bisect
import tkinter
from p_ggen import prg, thanUnicode, Canc
from p_gmath import PI2, thanintersect, thanNearx, thanNear2, circle2Line
from thanvar import thanExtendNodeDims, thanPilArc
from thantrans import T
from . import thanintall
from .thanelem import ThanElement


class ThanArc(ThanElement):
    "A circular arc."
    thanElementName = "ARC"    # Name of the element's class

    def thanSet(self, cc, r, theta1, theta2, spin=1):
        "Sets the attributes of the circle."
        self.cc = list(cc)
        self.r  = r
        self.theta1 = theta1 % PI2        # radians assumed
        self.theta2 = theta2 % PI2        # radians assumed
        if self.theta2 < self.theta1: self.theta2 += PI2   # Ensure theta2>=theta1
        self.spin = spin                  #By default we assume counterclockwise (1)
        self.__boundBox()
#       self.thanTags = ()                                 # thanTags is initialised in ThanElement


    def __boundBox(self):
        """Compute a minimum rectangle that contains the arc.

        The min and max x and y occur at angles 0, 90, 180, 270 degrees, _if_
        the arc contains these angles. Of course the arc can not contain all these
        angles - it would be a circle if it did. Thus the ends of the arc are also
        candidates for min or max x or y.
        """
        xx = [self.cc[0]+self.r*cos(self.theta1), self.cc[0]+self.r*cos(self.theta2)]
        yy = [self.cc[1]+self.r*sin(self.theta1), self.cc[1]+self.r*sin(self.theta2)]
        for theta,dx,dy in (0.0, self.r, 0), (pi*0.5, 0, self.r), (pi, -self.r, 0), (pi*1.5, 0, -self.r):
            if self.thanThetain(theta)[0]:
                xx.append(self.cc[0]+dx)
                yy.append(self.cc[1]+dy)
        self.setBoundBox((min(xx), min(yy), max(xx), max(yy)))

    def thanReverse(self):
        "Reverse the spin of the arc."
        self.spin = -self.spin


    def thanIsNormal(self):
        "Returns False if the arc is degenerate (either zero radius or identical thetas)."
        if thanNearx(self.cc[0], self.cc[0]+self.r): return False # Degenerate arc
        if thanNearx(self.cc[1], self.cc[1]+self.r): return False # Degenerate arc
        return not thanNearx(self.theta1, self.theta2)       # Degenerate arc


    def than2Line(self, dt=0.0, ta=None, tb=None):
        "Represent the arc with straight line segments."
        if dt is None: return True               #than2Line IS implemented
        if ta is None:
            ta = self.theta1
            tb = self.theta2
        cp, tp = circle2Line(self.cc[0], self.cc[1], self.r, ta, tb, dt)
        cp = thanExtendNodeDims(cp, self.cc)
        return cp, tp    #The caller may mutate these lists without problem


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.cc = self.thanRotateXy(self.cc)
        self.theta1 += self.rotPhi
        self.theta2 += self.rotPhi
        self.theta1 %= PI2        # radians assumed
        self.theta2 %= PI2        # radians assumed
        if self.theta2 < self.theta1: self.theta2 += PI2   # Ensure theta2>=theta1
        self.__boundBox()


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        ca = list(self.cc)
        ca[0] += self.r*cos(self.theta1)
        ca[1] += self.r*sin(self.theta1)
        cb = list(self.cc)
        cb[0] += self.r*cos(self.theta2)
        cb[1] += self.r*sin(self.theta2)
        self.cc = self.thanMirrorXy(self.cc)
        cb, ca = self.thanMirrorXy(ca), self.thanMirrorXy(cb)
        self.theta1 = atan2(ca[1]-self.cc[1], ca[0]-self.cc[0]) % PI2
        self.theta2 = atan2(cb[1]-self.cc[1], cb[0]-self.cc[0]) % PI2
        if self.theta2 < self.theta1: self.theta2 += PI2   # Ensure theta2>=theta1
        self.__boundBox()


    def thanPointMir(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        ca = list(self.cc)
        ca[0] += self.r*cos(self.theta1)
        ca[1] += self.r*sin(self.theta1)
        cb = list(self.cc)
        cb[0] += self.r*cos(self.theta2)
        cb[1] += self.r*sin(self.theta2)
        self.cc = self.thanPointMirXy(self.cc)
        ca, cb = self.thanPointMirXy(ca), self.thanPointMirXy(cb)
        self.theta1 = atan2(ca[1]-self.cc[1], ca[0]-self.cc[0]) % PI2
        self.theta2 = atan2(cb[1]-self.cc[1], cb[0]-self.cc[0]) % PI2
        if self.theta2 < self.theta1: self.theta2 += PI2   # Ensure theta2>=theta1
        self.__boundBox()


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        self.cc = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.cc, cs)] #works for python2,3
        self.r *= scale
        self.__boundBox()


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        self.cc = [cc1+dd1 for (cc1,dd1) in zip(self.cc, dc)]  #works for python2,3
        self.__boundBox()


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type otype nearest to point xcu, ycu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        if "end" in otypes:
            for thet in self.theta1, self.theta2: self.thanOsnapAdd(ccu, ps, thet, "end")
        if "mid" in otypes:
            thet = ((self.theta2 - self.theta1)*0.5) % PI2
            thet += self.theta1
            self.thanOsnapAdd(ccu, ps, thet, "mid")
        if "nea" in otypes:
            cn, rn, thet = self.thanPntNearest2(ccu)
            if thet is not None and rn > self.r:  # If we are getting near from the outside then "nea"
                self.thanOsnapAdd(ccu, ps, thet, "nea")
        if "qua" in otypes:
            for thet in 0, 0.5*pi, pi, 1.5*pi:    # If both "nea" and "cen" are active, "qua" does not have a chance
                if not self.thanThetain(thet)[0]: continue
                self.thanOsnapAdd(ccu, ps, thet, "qua")
        if "cen" in otypes:
            cn, rn, thet = self.thanPntNearest2(ccu)
            if thet is not None and rn < self.r:  # If we are getting near from the inside then "cen"
                ps.append((fabs(cn[0]-ccu[0])+fabs(cn[1]-ccu[1]), "cen", self.cc))
        if cori is not None and "per" in otypes:
            for cn in self.thanPerpPoints(cori):
                ps.append((fabs(cn[0]-ccu[0])+fabs(cn[1]-ccu[1]), "per", cn))
        if cori is not None and "tan" in otypes:
            dx = (self.cc[0] - cori[0])*0.5
            dy = (self.cc[1] - cori[1])*0.5
            r = hypot(dx, dy)
            c = cori[0]+dx, cori[1]+dy
            for cp in thanintersect.thanCirCir(self.cc, self.r, c, r):
                thet = atan2(cp[1]-self.cc[1], cp[0]-self.cc[0]) % PI2
                if not self.thanThetain(thet)[0]: continue
                self.thanOsnapAdd(ccu, ps, thet, "tan")
        if eother is not None and "int" in otypes:
            ps.extend(thanintall.thanIntsnap(self, eother, ccu, proj))

        if len(ps) > 0: return min(ps)
        return None

    def thanOsnapAdd(self, ccu, ps, thet, snaptyp):
        "Add a new point to osnap points."
        cc = list(self.cc)
        cc[0] += self.r*cos(thet)
        cc[1] += self.r*sin(thet)
        ps.append((fabs(cc[0]-ccu[0])+fabs(cc[1]-ccu[1]), snaptyp, cc))


    def thanPntNearest(self, ccu):
        "Finds the nearest point of this arc to a point."
        return self.thanPntNearest2(ccu)[0]


    def thanPntNearest2(self, ccu):
        "Finds the nearest point of this arc to a point and its angle."
        a = ccu[0]-self.cc[0], ccu[1]-self.cc[1]
        aa = hypot(a[0], a[1])
        #if thanNearx(aa, 0.0): thet = 0.0   #Thanasis2024_11_28:commented out
        if thanNearx(aa+self.r, 0.0+self.r): thet = 0.0  #Thanasis2024_11_28: more robust condition
        else:                  thet = atan2(a[1], a[0]) % PI2
        in_, _ = self.thanThetain(thet)
        if not in_: return None, None, None
        c = list(self.cc)
        c[0] += self.r*cos(thet)
        c[1] += self.r*sin(thet)
        return c, aa, thet


    def thanAngularDist(self, iend, ccu):
        "Find the angular distance of point ccu from a endpoint of the arc."
        a = ccu[0]-self.cc[0], ccu[1]-self.cc[1]
        aa = hypot(a[0], a[1])
        #if thanNearx(aa, 0.0): return 1.0e30  #Thanasis2024_11_28:commented out
        if thanNearx(aa, 0.0): return 1.0e30   #Thanasis2024_11_28: more robust condition
        thet = atan2(a[1], a[0]) % PI2
        if self.thanThetain(thet)[0]:
            if iend == 0: return (thet-self.theta1) % PI2     #From first point
            else:         return (self.theta2-thet) % PI2     #From last point
        else:
            if iend == 0: return (self.theta1-thet) % PI2     #From first point
            else:         return (thet-self.theta2) % PI2     #From last point


    def thanPerpPoints(self, ccu):
        "Finds the perpendicular points from ccu to the arc."
        a = ccu[0]-self.cc[0], ccu[1]-self.cc[1]
        aa = hypot(a[0], a[1])
        #if thanNearx(aa, 0.0): thet = 0.0               #Thanasis2024_11_28:commented out
        if thanNearx(aa+self.r, 0.0+self.r): thet = 0.0  #Thanasis2024_11_28: more robust condition
        else:                  thet = atan2(a[1], a[0]) % PI2
        ps = []
        in_, thet1 = self.thanThetain(thet)
        if in_:
            c = list(self.cc)
            c[0] += self.r*cos(thet1)
            c[1] += self.r*sin(thet1)
            ps.append(c)
        thet += pi
        in_, thet1 = self.thanThetain(thet)
        if in_:
            c = list(self.cc)
            c[0] += self.r*cos(thet1)
            c[1] += self.r*sin(thet1)
            ps.append(c)
        return ps


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset arc by distance dis pr through point."
        if through==None and distance==None: return True  # Offset is implemented
        roff = hypot(sidepoint[0]-self.cc[0], sidepoint[1]-self.cc[1])
        if not through:
            if roff < self.r: roff = self.r-distance
            else:             roff = self.r+distance
        if roff <= 0.0: return None      # Element can not be offset (degenerate)
        e = ThanArc()
        e.thanSet(self.cc, roff, self.theta1, self.theta2, self.thanSpin())
        if e.thanIsNormal(): return e
        return None                      # Element can not be offset (degenerate)


    def getInspnt(self):
        "Returns the insertion point of the arc; the first point of the arc."
        ca = list(self.cc)
        ca[0] += self.r*cos(self.theta1)
        ca[1] += self.r*sin(self.theta1)
        return ca


    def thanLength(self):
        "Returns the length of the arc."
        return self.r * (self.theta2-self.theta1)


    def thanArea(self):
        "Returns the area of the arc."
        dth = self.theta2-self.theta1
        assert dth >= 0.0
        if dth <= pi:
            asec = dth*0.5*self.r**2
            atri = self.r*cos(dth*0.5)*self.r*sin(dth*0.5)
            return asec-atri
        else:
            dth = 2*pi - dth
            asec = dth*0.5*self.r**2
            atri = self.r*cos(dth*0.5)*self.r*sin(dth*0.5)
            return pi*self.r**2 - (asec - atri)

    def thanSpin(self):
        "Returns the spin of the arc."
        return self.spin

    def thanTrim(self, ct, cnear):
        "Breaks the arc into multiple segments and deletes the segment nearest to cnear."
        cp = []
        for thet in self.theta1, self.theta2:
            c1 = list(self.cc)
            c1[0] += self.r*cos(thet)
            c1[1] += self.r*sin(thet)
            cp.append((thet%PI2, c1))
        for c in ct:
            cn, _, t = self.thanPntNearest2(c)
            cp.append((t, cn))   #Thanasis2024_11_28: check if points are identical, not that
            assert cn is not None, "It should have been checked (that ct are indeed near the arc)!"
        cp.sort()
        i = 0
        while i < len(cp) and len(cp) > 1:
            if thanNear2(cp[i][1], cp[i-1][1]): del cp[i] #Thanasis2024_11_28: check if points are identical, not that thetas are identical
            else: i += 1
        if len(cp) < 2: return None, None               # Degenerate arc?, or full circle?
        cn, _, t = self.thanPntNearest2(cnear)
        cpnear = t, cn
        assert cn is not None, "It should have been checked (that cnear are indeed near the arc)!"
        if not self.thanThetain(t): return None, None   # No arc at the position the user has selected
        i = bisect.bisect_right(cp, cpnear)
        if i == 0:
            return self.thanBreak(cp[-1][1], cp[0][1])  # User selected the segment before the first intersection (ct)
        elif i == len(cp):
            return self.thanBreak(cp[-1][1], cp[0][1])  # User selected the segment after the last intersection (ct)
        else:
            return self.thanBreak(cp[i-1][1], cp[i][1]) # User selected the segment between i-1 and i intersections (ct)


    def thanBreak(self, c1=None, c2=None):
        "Breaks an arc to 2 arcs."
        if c1 is None: return True                       # Break IS implemented
        cp1, r1, thet1 = self.thanPntNearest2(c1)
        assert cp1 is not None, "pntNearest should succeed (as in thancommod.__getNearPnt()"
        cp2, r2, thet2 = self.thanPntNearest2(c2)
        assert cp2 is not None, "pntNearest should succeed (as in thancommod.__getNearPnt()"

        _, thet1 = self.thanThetain(thet1)
        _, thet2 = self.thanThetain(thet2)
        if thet2 < thet1: thet2, thet1 = thet1, thet2    # Ensure thet1 < thet2

        e1 = self.thanClone()          #e1 gets the identity of self
        e1.thanSet(self.cc, self.r, self.theta1, thet1)
        if not e1.thanIsNormal(): e1 = None
        e2 = self.thanClone()          #e2 gets the identity of self ..
        if e1 is not None: e2.thanUntag()  #.. but it loses it if e1 is not None
        e2.thanSet(self.cc, self.r, thet2, self.theta2)
        if not e2.thanIsNormal(): e2 = None
        return e1, e2


    def thanThetainold(self, th):
        """Finds if th is between self.theta1 and self.theta2; th must be 0<=th<2pi.

        Note that 0<=self.theta1<2pi and:
        1. if 0=<self.theta2<2pi and self.theta1 <= self.theta2 OK
        2. else 2pi<=self.theta2<4pi (and of course self.theta1 < self.theta2)
        """
        if self.theta1 <= th      <= self.theta2: return True, th
        if self.theta1 <= th+PI2  <= self.theta2: return True, th+PI2
        if thanNearx(0.0, self.r*tan(self.theta1-th)): return True, self.theta1
        if thanNearx(0.0, self.r*tan(self.theta2-th)): return True, self.theta2
        return False, th


    def thanThetain(self, th):
        """Finds if th is between self.theta1 and self.theta2; th must be 0<=th<2pi.

        Note that 0<=self.theta1<2pi and:
        1. if 0=<self.theta2<2pi and self.theta1 <= self.theta2 OK
        2. else 2pi<=self.theta2<4pi (and of course self.theta1 < self.theta2)
        """
        if self.theta1 <= th      <= self.theta2: return True, th
        if self.theta1 <= th+PI2  <= self.theta2: return True, th+PI2

        #Thanasis2024_11_29:
        #Check if angle th is close to either end of the arc (angles self.theta1 and self.theta2)
        #We compute the delta theta (0<=dth<2π). This should be small if th is actually close to
        #theta1 or theta2. Thus if dth > pi, it means that the actual small angle dth is negative
        #and we compute it as dth=dth-2pi.
        #If |dth| ~= zero, the it is close the one end. However this is not
        #robust if the radius is very small or very large, thus we check that
        #the length of the corresponding chord s=r*|dth| which is about zero.
        #Since checking that something is close to zero has little meaning without
        #context, we check if r+s is close r.
        dth = (th - self.theta1) % PI2
        if dth > pi: dth -= PI2
        if thanNearx(self.r+self.r*fabs(dth), self.r+0.0): return True, self.theta1

        dth = (th - self.theta2) % PI2
        if dth > pi: dth -= PI2
        if thanNearx(self.r+self.r*fabs(dth), self.r+0.0): return True, self.theta2
        return False, th


    def thanTkGet(self, proj):
        "Gets the attributes of the arc interactively from a window."
        than = proj[2].than
        g2l = than.ct.global2Local
        cc = proj[2].thanGudGetPoint(T["Center: "])
        if cc == Canc: return Canc                # Arc cancelled
        r = proj[2].thanGudGetCircle(cc, 1.0, T["Radius: "])
        if r == Canc: return Canc                 # Arc cancelled
        temp = than.dc.create_oval(g2l(cc[0]-r, cc[1]-r), g2l(cc[0]+r, cc[1]+r),
            outline="blue", tags=("e0",), outlinestipple="gray50")

        theta1 = proj[2].thanGudGetPolar(cc, r, T["First point direction angle: "])
        than.dc.delete("e0")
        if theta1 == Canc: return Canc            # Arc cancelled
        than.dc.create_line(g2l(cc[0], cc[1]), g2l(cc[0]+r*cos(theta1), cc[1]+r*sin(theta1)), fill="blue", tags=("e0",))

        theta2 = proj[2].thanGudGetArc(cc, r, theta1, T["Last point direction angle: "])
        than.dc.delete("e0")
        if theta2 == Canc: return Canc            # Arc cancelled
        if proj[1].thanUnits.angldire == -1:
            theta1, theta2 = theta2, theta1
        self.thanSet(cc, r, theta1, theta2)
        return True                               # Arc OK


    def thanTkDraw1(self, than):
        "Draws the arc to a Tk Canvas."
        w = than.tkThick
        xc, yc = than.ct.global2Local(self.cc[0], self.cc[1])
        r, temp = than.ct.global2LocalRel(self.r, self.r)
        theta1 = self.theta1 * 180.0/pi
        theta2 = self.theta2 * 180.0/pi
        dth = (theta2-theta1) % 360.0
        temp = than.dc.create_arc(xc-r, yc-r, xc+r, yc+r, start=theta1, extent=dth,
            style=tkinter.ARC, outline=than.outline, fill=than.fill, dash=than.dash, tags=self.thanTags, width=w)


    def thanExpDxf(self, fDxf):
        "Exports the arc to dxf file."
        fDxf.thanDxfPlotArc3(self.cc[0], self.cc[1], self.cc[2], self.r,
            self.theta1/pi*180.0, self.theta2/pi*180.0)


    def thanExpKml(self, than):
        "Exports the arc to Google .kml file."
        than.ibr += 1
        aa = than.form % (than.ibr,)
        cp, tp = self.than2Line(dt=than.dt)    #1m resolution is hopefully enough for google maps
        than.kml.writeLinestring(aa, cp, than.layname, desc="")


    def thanExpThc1(self, fw):
        "Save the arc in thc format."
        f = fw.formFloat
        fw.writeNode(self.cc)
        fw.writeln(f % self.r)
        fw.writeln((f+f) % (self.theta1, self.theta2))
        fw.writeln("%d" % (self.spin,))


    def thanImpThc1(self, fr, ver):
        "Read the arc from thc format."
        cc = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        r = float(next(fr))             #May raise ValueError, StopIteration
        t1, t2 = map(float, next(fr).split()) #May raise ValueError, IndexError, StopIteration   #works for python2,3
        spin = int(next(fr))            #May raise ValueError, StopIteration
        if spin not in (1, 0, -1): raise ValueError("spin must 1, 0 or -1")
        self.thanSet(cc, r, t1, t2, spin)


    def thanExpPilWorkaround(self, than):
        "Exports the arc to a PIL raster image."
        x1, y1 = than.ct.global2Locali(self.cc[0]-self.r, self.cc[1]+self.r)  # PIL needs left,upper and ..
        x2, y2 = than.ct.global2Locali(self.cc[0]+self.r, self.cc[1]-self.r)  # ..right,lower
        t2 = -int(self.theta1/pi*180.0+0.5)
        t1 = -int(self.theta2/pi*180.0+0.5)
        for i in range(*than.widtharc):
            than.dc.arc((x1-i, y1-i, x2+i, y2+i), t1, t2, fill=than.outline)


    def thanExpPil(self, than):   #Thanasis2022_09_16
        "Exports the arc to a PIL raster image; respects dashed lines."
        thanPilArc(than, self.cc, self.r, self.theta1, self.theta2)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        cc = list(self.cc)
        cc[:3] = fun(cc[:3])

        cr = list(self.cc)
        cr[0] += self.r
        cr = fun(cr[:3])
        r = hypot(cr[1]-cc[1], cr[0]-cc[0])

        ths = [self.theta1, self.theta2]
        for i,th in enumerate(ths):
            cr = list(self.cc)
            cr[0] += r * cos(th)
            cr[1] += r * sin(th)
            cr = fun(cr[:3])
            ths[i] = atan2(cr[1]-cc[1], cr[0]-cc[0])   #Note that python ensures than atan2(0,0) = 0!!!

        self.thanSet(cc, r, ths[0], ths[1], self.spin)


    def thanExtend(self, cp, iend=1, method=0):
        """Return a new arc extending self so that endpoint iend corresponds to cp.

        If method is 0 or 1 then the new arc is the combined arc: self plus the
        net extension.
        If method is 2 then the new arc is only the net extension: it does not
        include it does not include self."""
        th = atan2(cp[1]-self.cc[1], cp[0]-self.cc[0]) % PI2
        if self.thanThetain(th)[0]: return []     #Intersection is within self; no extension is possible
        if method == 2:
            arc = ThanArc()          #The new arc has handle and tag invalidated; it will take new handle and tag by thanElementTag
            if iend == 0: theta1, theta2 = th, self.theta1     #Only the net extension
            else:         theta1, theta2 = self.theta2, th     #Only the net extension
        else:
            arc = self.thanClone()   #The new arc takes the handle (identity) of self (it also takes the tag)
            if iend == 0: theta1, theta2 = th, self.theta2     #Combined arc (includes self)
            else:         theta1, theta2 = self.theta1, th     #Combined arc (includes self)
        arc.thanSet(self.cc, self.r, theta1, theta2, spin=self.thanSpin())
        return [arc]


    def thanList(self, than):
        "Shows information about the arc element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        t = ("%s%s" % (T["Center: "], than.strcoo(self.cc)),
             "%s%s    %s%s" % (T["Radius: "], than.strdis(self.r), T["Spin: "], self.spin),
             T["Spans: %s    to: %s\n"]% (than.strdir(self.theta1), than.strdir(self.theta2)),
            )
        than.write("\n".join(t))


def test():
    prg(__doc__)
    c = ThanArc()
    c.thanSet([10.0, 20.0, -11.0], 3.0, 0.0, pi*0.5)
    prg("arc=%s" % (c,))
    prg("degenerate=%s" % bool(not c.thanIsNormal()))
