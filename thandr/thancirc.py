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

This module defines the circle element.
"""

from math import fabs, pi, cos, sin, tan, hypot, atan2
import bisect
from p_gmath import (PI2, thanintersect, thanNearx, thanNear2, circle3,
    circle2Line, circlettrlinesnear, circletttlinesnear)
from p_ggen import prg, frange, thanUnicode, Canc
from thanvar import thanExtendNodeDims, thanFilletCalc, thanPilCircle
from thantrans import T
from . import thanintall, thanarc
from .thanelem import ThanElement


class ThanCircle(ThanElement):
    "A Basic circle."
    thanElementName = "CIRCLE"    # Name of the element's class

    def thanSet(self, cc, r, spin=1):
        "Sets the attributes of the circle."
        self.setBoundBox([cc[0]-r, cc[1]-r, cc[0]+r, cc[1]+r])
        self.cc = list(cc)
        self.r  = r
        self.spin = spin             #By default we assume counterclockwise (1)
#        self.thanTags = ()                                 # thanTags is initialised in ThanElement

    def thanReverse(self):
        "Reverse the spin of the circle."
        self.spin = -self.spin

    def thanIsNormal(self):
        "Returns False if the circle is degenerate (zero radius)."
        if thanNearx(self.cc[0], self.cc[0]+self.r): return False    # Degenerate circle                                    # There is no degenerate image
        if thanNearx(self.cc[1], self.cc[1]+self.r): return False    # Degenerate circle                                    # There is no degenerate image
        return True

#    def thanClone(self): #inherited from ThanElement

    def than2Line(self, dt=0.0, ta=None, tb=None):
        "Represent the circle with straight line segments."
        if dt is None: return True               #than2Line IS implemented
        if ta is None:
            ta = 0.0
            tb = PI2
        cp, tp = circle2Line(self.cc[0], self.cc[1], self.r, ta, tb, dt)
        cp = thanExtendNodeDims(cp, self.cc)
        return cp, tp    #The caller may mutate these lists without problem


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.cc = self.thanRotateXy(self.cc)
        self.setBoundBox([self.cc[0]-self.r, self.cc[1]-self.r, self.cc[0]+self.r, self.cc[1]+self.r])


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        self.cc = self.thanMirrorXy(self.cc)
        self.setBoundBox([self.cc[0]-self.r, self.cc[1]-self.r, self.cc[0]+self.r, self.cc[1]+self.r])


    def thanPointMir(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        self.cc = self.thanPointMirXy(self.cc)
        self.setBoundBox([self.cc[0]-self.r, self.cc[1]-self.r, self.cc[0]+self.r, self.cc[1]+self.r])


    def thanScale(self, cs, scale):
        "Enlarges or shrinks the element with predefined basepoint and factor."
        self.cc = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.cc, cs)]  #works for python2,3
        self.r *= scale
        self.setBoundBox([self.cc[0]-self.r, self.cc[1]-self.r, self.cc[0]+self.r, self.cc[1]+self.r])

    def thanMove(self, dc):
        "Moves the element with predefined displacement in all axes."
        self.cc = [cc1+dd1 for (cc1,dd1) in zip(self.cc, dc)]   #works for python2,3
        self.setBoundBox([self.cc[0]-self.r, self.cc[1]-self.r, self.cc[0]+self.r, self.cc[1]+self.r])

    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type in otypes nearest to point ccu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        if "nea" in otypes:
            cn, rn, thet = self.thanPntNearest2(ccu)
            if thet is not None:
                if "cen" not in otypes or rn > self.r:  # If we are getting near from the outside then "nea"
                    self.thanOsnapAdd(ccu, ps, thet, "nea")
                    ps.append((fabs(cn[0]-ccu[0])+fabs(cn[1]-ccu[1]), "nea", cn))
        if "cen" in otypes:
            cn, rn, thet = self.thanPntNearest2(ccu)
            if thet is not None:
                if ("nea" not in otypes and "qua" not in otypes) or rn < self.r:  # If we are getting near from the inside then "cen"
                    ps.append((fabs(cn[0]-ccu[0])+fabs(cn[1]-ccu[1]), "cen", self.cc))
##           Snap to center only with these points on the periphery to let quad have a chance
#           cp = [ (self.xc + self.r*cos(theta1), self.yc + self.r*sin(theta1), self.zc)
#                  for theta1 in (0.25*pi, 0.75*pi, 1.25*pi, 1.75*pi) ]
#           ps = [(fabs(x-xcu)+fabs(y-ycu), "cen", self.xc, self.yc, self.zc) for (x,y,z) in cp]
        if "qua" in otypes:
            for thet in 0, 0.5*pi, pi, 1.5*pi:    # If both "nea" and "cen" are active, "qua" does not have a chance
                self.thanOsnapAdd(ccu, ps, thet, "qua")
        if cori is not None and "tan" in otypes:
            dx = (self.cc[0] - cori[0])*0.5   #this is based on the fact that the median of a right
            dy = (self.cc[1] - cori[1])*0.5   #triangle is equal to the half of the hypotenuse
            r = hypot(dx, dy)
            c = cori[0]+dx, cori[1]+dy
            for cp in thanintersect.thanCirCir(self.cc, self.r, c, r):
                thet = atan2(cp[1]-self.cc[1], cp[0]-self.cc[0]) % PI2
                self.thanOsnapAdd(ccu, ps, thet, "tan")
        if cori is not None and "per" in otypes:
            for cn in self.thanPerpPoints(cori):
                ps.append((fabs(cn[0]-ccu[0])+fabs(cn[1]-ccu[1]), "per", cn))
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
        "Finds the nearest point of this circle to a point."
        return self.thanPntNearest2(ccu)[0]

    def thanPntNearest2(self, ccu):
        "Finds the nearest point of this circle to a point and its angle."
        a = ccu[0]-self.cc[0], ccu[1]-self.cc[1]
        aa = hypot(a[0], a[1])
        #if thanNearx(aa, 0.0): thet = 0.0               #Thanasis2024_11_28:commented out
        if thanNearx(aa+self.r, 0.0+self.r): thet = 0.0  #Thanasis2024_11_28: more robust condition
        else:                                thet = atan2(a[1], a[0]) % PI2
        c = list(self.cc)
        c[0] += self.r*cos(thet)
        c[1] += self.r*sin(thet)
        return c, aa, thet


    def thanPerpPoints(self, ccu):
        "Finds the perpendicular points from ccu to the circle."
        a = ccu[0]-self.cc[0], ccu[1]-self.cc[1]
        aa = hypot(a[0], a[1])
        #if thanNearx(aa, 0.0): thet = 0.0               #Thanasis2024_11_28:commented out
        if thanNearx(aa+self.r, 0.0+self.r): thet = 0.0  #Thanasis2024_11_28: more robust condition
        else:                                thet = atan2(a[1], a[0]) % PI2
        c = list(self.cc)
        c[0] += self.r*cos(thet)
        c[1] += self.r*sin(thet)
        ps = [c]
        thet += pi
        c = list(self.cc)
        c[0] += self.r*cos(thet)
        c[1] += self.r*sin(thet)
        ps.append(c)
        return ps


    def thanTrim(self, ct, cnear):
        "Breaks the circle into multiple segments and deletes the segment nearest to cnear."
        cp = []
        for c in ct:
            cn, _, t = self.thanPntNearest2(c)
            assert cn is not None, "It should have been checked (that ct are indeed near the circle)!"
            cp.append((t, cn))    #Thanasis2024_11_28: cp -> cn
        cp.sort()
        i = 0
        while i < len(cp) and len(cp) > 1:
            if thanNear2(cp[i][1], cp[i-1][1]): del cp[i]    #Thanasis2024_11_28: check if points are identical, not that thetas are identical
            else: i += 1
        if len(ct) < 2: return None, None               # Can not trim circle with 1 point
        cn, _, t = self.thanPntNearest2(cnear)
        cpnear = t, cn
        assert cpnear[1] is not None, "It should have been checked (that cnear are indeed near the circle)!"
        i = bisect.bisect_right(cp, cpnear)
        if i == 0:
            return self.thanBreak(cp[-1][1], cp[0][1])  # User selected the segment before the first intersection (ct)
        elif i == len(cp):
            return self.thanBreak(cp[-1][1], cp[0][1])  # User selected the segment after the last intersection (ct)
        else:
            return self.thanBreak(cp[i-1][1], cp[i][1]) # User selected the segment between i-1 and i intersections (ct)


    def thanBreak(self, c1=None, c2=None):
        "Breaks a circle and produces an arc."
        if c1 is None: return True          # Break IS implemented
        cp1, r1, theta1 = self.thanPntNearest2(c1)
        assert cp1 is not None, "pntNearest should succeed (as in thancommod.__getNearPnt()"
        cp2, r2, theta2 = self.thanPntNearest2(c2)
        assert cp2 is not None, "pntNearest should succeed (as in thancommod.__getNearPnt()"
        e1 = thanarc.ThanArc()
        e1.thanSet(self.cc, self.r, theta2, theta1, self.spin)
        if not e1.thanIsNormal(): e1 = None
        return e1, None


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset circle by distance or through point."
        if through==None and distance==None: return True  # Offset is implemented
        roff = hypot(sidepoint[0]-self.cc[0], sidepoint[1]-self.cc[1])
        if not through:
            if roff < self.r: roff = self.r-distance
            else:             roff = self.r+distance
        if roff <= 0.0: return None      # Element can not be offset (degenerate)
        e = ThanCircle()
        e.thanSet(self.cc, roff, self.spin)
        if e.thanIsNormal(): return e
        return None                      # Element can not be offset (degenerate)

    def thanLength(self):
        "Returns the length of the circle."
        return 2*pi*self.r

    def thanArea(self):
        "Returns the area of the polyline."
        return pi*self.r**2

    def thanSpin(self):
        "Returns the spin of the circle."
        return self.spin

    def thanTkGetold(self, proj):
        "Gets the attributes of the circle interactively from a window."
        cc = proj[2].thanGudGetPoint(T["Center: "])
        if cc == Canc: return Canc               # Circle cancelled
        r = proj[2].thanGudGetCircle(cc, 1.0, T["Radius: "])
        if r == Canc: return Canc                # Circle cancelled
        self.thanSet(cc, r)
        return True                              # Circle OK


    def thanTkGet(self, proj):
        "Gets the attributes of the circle interactively from a window."
        cc = proj[2].thanGudGetPoint(T["Center [3p=3 points/2p=2 points/Ttr (tan tan radius)/ttt (tan tan tan)]: "],
            options=("3Points","2Points", "Ttr", "ttt"))
        if cc == Canc: return Canc               # Circle cancelled
        if cc == "3":
            cc1 = proj[2].thanGudGetPoint(T["First point on circle: "])
            if cc1 == Canc: return Canc               # Circle cancelled
            cc2 = proj[2].thanGudGetLine(cc1, T["Second point on circle: "])
            if cc2 == Canc: return Canc               # Circle cancelled
            cc3 = proj[2].thanGudGetCircle3(cc1, cc2, T["Third point on circle: "])
            if cc3 == Canc: return Canc               # Circle cancelled
            cc, r = circle3(cc1, cc2, cc3)
            if cc is None:
                proj[2].thanPrter(T["Invalid circle: points are col-linear."])
                return Canc
        elif cc == "2":
            cc1 = proj[2].thanGudGetPoint(T["First point on circle: "])
            if cc1 == Canc: return Canc               # Circle cancelled
            cc2 = proj[2].thanGudGetCircle2(cc1, T["Second anti-diametric point: "])
            if cc2 == Canc: return Canc               # Circle cancelled
            cc = list(cc1)
            cc[0] = (cc1[0]+cc2[0])*0.5
            cc[1] = (cc1[1]+cc2[1])*0.5
            r = hypot(cc2[1]-cc1[1], cc2[0]-cc1[0]) * 0.5
        elif cc == "t":
            cc, r = self.__ttr(proj)
            if cc == Canc: return Canc               # Circle cancelled
        elif cc == "ttt":
            cc, r = self.__ttt(proj)
            if cc == Canc: return Canc               # Circle cancelled
        else:
            r = proj[2].thanGudGetCircle(cc, 1.0, T["Radius (D=Diameter): "], options=("Diameter",))
            if r == Canc: return Canc                                  #Ellipse was cancelled
            if r == "d":
                r = proj[2].thanGudGetCircle(cc, 0.5, T["Diameter: "])
                if r == Canc: return Canc                                  #Ellipse was cancelled
                r = r*0.5
        self.thanSet(cc, r)
        return True                              # Circle OK


    __radius = 10.0
    def __ttrold(self, proj):
        "Gets a circle interactively with geometry: tangent, tangent and radius."
        from thancom.selutil import thanSel2linsegs
        rr = ThanCircle.__radius
        strd = proj[1].thanUnits.strdis

        res = thanSel2linsegs(proj, T["Select first single segment line tangent to circle: "],
                                    T["Select second single segment line  tangent to circle "])
        if res == Canc: return Canc, Canc               # Circle cancelled
        aa, bb, anear, bnear = res

        mes = T["Radius of circle (enter=%s): "] % (strd(rr),)
        res = proj[2].thanGudGetPosFloat(mes, default=rr, strict=True)
        if res == Canc: return Canc, Canc               # Circle cancelled
        rr = res
        ThanCircle.__radius = rr

        a, b = aa.thanClone(), bb.thanClone()
        ierr, obj = thanFilletCalc(a, b, rr, anear, bnear) # 0, (cc, rr, c.theta1*pi/180, c.theta2*pi/180)
        if ierr == 0 and b is not None:
            return obj[0], obj[1]                           # Circle OK
        if ierr == 0:
            proj[2].thanPrter(T["Radius is zero"])
        elif ierr == 1:
            proj[2].thanPrter(T["End lines are parallel and do not intersect"])
        elif ierr == 2:
            proj[2].thanPrter(T["Circle lies beyond the line segments"])
        return Canc, Canc

    def __ttr(self, proj):
        """Gets a circle interactively with geometry: tangent, tangent and radius.

        The evevation of the circle is the current elevation."""
        from thancom.selutil import thanSelMultLinsegs
        strd = proj[1].thanUnits.strdis
        rr = ThanCircle.__radius
        mes = T["Radius of circle (enter=%s): "] % (strd(rr),)
        res = proj[2].thanGudGetPosFloat(mes, default=rr, strict=True)
        if res == Canc: return Canc, Canc               # Circle cancelled
        rr = res
        ThanCircle.__radius = rr

        statonce = (T["Select first  line segment tangent to circle: "],
                    T["Select second line segment tangent to circle: "],
                   )
        elems, cnear = thanSelMultLinsegs(proj, 2, statonce)
        if elems == Canc: return Canc, Canc               # Circle cancelled

        cpa = []
        cneara = []
        for j in range(len(elems)):
            cn, i, t = cnear[j]
            cp = elems[j].cp[i-1:i+1]
            cpa.append(cp)
            cneara.append(cn)
        ce, r = circlettrlinesnear(cpa[0], cpa[1], rr, cneara)
        if ce is None:
            proj[2].thanPrter(T["Tangents do not specify a circle"])
            return Canc, Canc
        cc = list(proj[1].thanVar["elevation"])
        cc[:2] = ce
        return cc, r


    def __ttt(self, proj):
        """Gets a circle interactively with geometry: tangent, tangent and tangent.

        The evevation of the circle is the current elevation."""
        from thancom.selutil import thanSelMultLinsegs
        statonce = (T["Select first  line segment tangent to circle: "],
                    T["Select second line segment tangent to circle: "],
                    T["Select third  line segment tangent to circle: "],
                   )
        elems, cnear = thanSelMultLinsegs(proj, 3, statonce)
        if elems == Canc: return Canc, Canc               # Circle cancelled

        cpa = []
        cneara = []
        for j in range(len(elems)):
            cn, i, t = cnear[j]
            cp = elems[j].cp[i-1:i+1]
            cpa.append(cp)
            cneara.append(cn)
        ce, r = circletttlinesnear(cpa[0], cpa[1], cpa[2], cneara)
        if ce is None:
            proj[2].thanPrter(T["Tangents do not specify a circle"])
            return Canc, Canc
        cc = list(proj[1].thanVar["elevation"])
        cc[:2] = ce
        return cc, r


    def thanTkDraw1(self, than):
        "Draws the circle on a window."
        w = than.tkThick
        xc, yc = than.ct.global2Local(self.cc[0], self.cc[1])
        r, temp = than.ct.global2LocalRel(self.r, self.r)
        temp = than.dc.create_oval(xc-r, yc-r, xc+r, yc+r, outline=than.outline, dash=than.dash,
                                   fill=than.fill, tags=self.thanTags, width=w)

    def thanTkDrawAsPolygon(self, than):
        """Draws the circle on a window as a polyline.

        Here we want to work around tk bug which does not show a circle (or
        an arc) if the magnification is too big, so that the visible segment of
        the arc or circle is virtually a straight line.
        For this, when regen, an element must have the ability to tell ThanDwg
        that not all the element is drawn, only the part that is 2 screen width
        left and right, and 2 screen heights on top and bottom.
        Have a nice day, Thanasis2010_12_09.
        """
        w = than.tkThick
        xc, yc = than.ct.global2Local(self.cc[0], self.cc[1])
        r, _ = than.ct.global2LocalRel(self.r, self.r)
        n = 32
        dth = 2*pi/n
        th2 = 2*pi-dth*0.1
        xy = [(xc+r*cos(th), yc+r*sin(th)) for th in frange(0.0, th2, dth)]
        temp = than.dc.create_polygon(xy, outline=than.outline, dash=than.dash,
                                      fill=than.fill, tags=self.thanTags, width=w)

    def thanExpDxf(self, fDxf):
        "Exports the circle to dxf file."
        fDxf.thanDxfPlotCircle3(self.cc[0], self.cc[1], self.cc[2], self.r)


    def thanExpKml(self, than):
        "Exports the circle to Google .kml file."
        than.ibr += 1
        aa = than.form % (than.ibr,)
        cp, tp = self.than2Line(than.dt)    #1m resolution is hopefully enough for google maps
        than.kml.writeLinestring(aa, cp, than.layname, desc="")


    def thanExpThc1(self, fw):
        "Save the circle in thc format."
        f = fw.formFloat
        fw.writeNode(self.cc)
        fw.writeln(f % self.r)
        fw.writeln("%d" % (self.spin,))

    def thanImpThc1(self, fr, ver):
        "Read the circle from thc format."
        cc = fr.readNode()              #May raise ValueError, IndexError, StopIteration
        r = float(next(fr))             #May raise ValueError, StopIteration
        spin = int(next(fr))            #May raise ValueError, StopIteration
        if spin not in (1, 0, -1): raise ValueError("spin must 1, 0 or -1")
        self.thanSet(cc, r, spin)

    def thanExpPilworkaround(self, than):
        "Exports the circle to a PIL raster image."
#        dr, r  = than.ct.local2GlobalRel(1, 1)
        x1, y1 = than.ct.global2Locali(self.cc[0]-self.r, self.cc[1]+self.r)  # PIL needs left,upper and ..
        x2, y2 = than.ct.global2Locali(self.cc[0]+self.r, self.cc[1]-self.r)  # ..right,lower
        for i in range(*than.widtharc):
            than.dc.arc((x1-i, y1-i, x2+i, y2+i), 0, 360, fill=than.outline)


    def thanExpPil(self, than):   #Thanasis2022_09_16
        "Exports the circle to a PIL raster image; respects dashed lines."
        thanPilCircle(than, self.cc, self.r)


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

        self.thanSet(cc, r, self.spin)


    def thanList(self, than):
        "Shows information about the circle element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        t = ("%s%s" % (T["Center: "], than.strcoo(self.cc)),
             "%s%s    %s%s\n" % (T["Radius: "], than.strdis(self.r), T["Spin: "], self.spin),
            )
        than.write("\n".join(t))


def test():
    prg(__doc__)
    c = ThanCircle()
    c.thanSet(10.0, 20.0, 3.0)
    prg("circle=%s" % (c,))
    prg("degenerate=%s" % bool(not c.thanIsNormal()))
