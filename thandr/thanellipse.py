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

This module defines the ellipse element.
"""
from math import fabs, cos, sin, atan2, hypot, pi
from p_ggen import Canc, thanUnicode
from p_gmath import (dpt, thanNearx, thanNear2, ellipse2Line, ellipse5Lsm, ellipse4Lsm,
                     ellipse5Fit, ellipse4Fit, PI05, PI2)
from thanvar import thanExtendNodeDims
from thantrans import T
from .thanline import ThanCurve, ThanLine
from .thanelem import ThanElement
from .thanpoint import ThanPoint


class ThanEllipse(ThanCurve):
    """An ellipse represented by a polygon."""
    thanElementName = "ELLIPSE"    # Name of the element's class

    def thanSet (self, cc, a, b, theta1, theta2, phi, full, spin=1):
        "Sets the attributes of the ellipse."
        self.a = fabs(a)
        self.b = fabs(b)
        self.cc = list(cc)
        self.full = bool(full)
        if self.a < self.b:
            self.a, self.b = self.b, self.a
            phi += PI05
            theta1 -= PI05
            theta2 -= PI05
        if self.full:
            self.theta1 = 0.0
            self.theta2 = PI2
        else:
            self.theta1 = theta1 % PI2        # radians assumed
            self.theta2 = theta2 % PI2        # radians assumed
            if self.theta2 < self.theta1: self.theta2 += PI2   # Ensure theta2>=theta1
        #self.theta1 = pi/6        ####################
        #self.theta2 = pi/2+pi/4   ####################
        #self.full = False         ####################
        self.phi = dpt(phi)
        self.spin = spin             #By default we assume counterclockwise (1)
#        self.setBoundBoxRect(cc[0], cc[1], 2.0*self.a, 2.0*self.b, self.phi, center=True)
#        self.thanTags = ()          #thanTags is initialised in ThanElement

        cp, tp = self.than2Line()    # temporarily with default dt, until thanTkDraw is called
        ThanCurve.thanSet(self, cp, tp) #This also sets boundbox
        self.thanSetToldeg(20.0)     # Set angle tolerance for smoothness (we _know_ than ellipse is smooth :))


    def than2Line(self, dt=0.0, ta=None, tb=None):
        "Represent an ellipse with straight line segments."
        if dt is None: return True               #than2Line IS implemented
        if ta is None:
            ta = self.theta1
            tb = self.theta2
        cp, tp = ellipse2Line(self.cc[0], self.cc[1], self.a, self.b, ta, tb, self.phi, dt)
        cp = thanExtendNodeDims(cp, self.cc)
        return cp, tp    #The caller may mutate these lists without problem


    def thanIsNormal(self):
        "Returns False if the ellipse is degenerate (1 or 2 zero semi-axes)."
        a = min(self.a, self.b)
        if thanNearx(self.cc[0], self.cc[0]+a): return False    # Degenerate ellipse
        if thanNearx(self.cc[1], self.cc[1]+a): return False    # Degenerate ellipse
        return True


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.cc = self.thanRotateXy(self.cc)
        self.phi = dpt(self.phi + self.rotPhi)
        self.setBoundBoxRect(self.cc[0], self.cc[1], 2.0*self.a, 2.0*self.b, self.phi, center=True)


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        cs = []
        cosf = cos(self.phi)
        sinf = sin(self.phi)
        for om in pi, 0, self.theta1, self.theta2:
            x = self.a*cos(om)
            y = self.b*sin(om)
            xt = x*cosf - y*sinf
            yt = x*sinf + y*cosf
            cs.append((self.cc[0]+xt, self.cc[1]+yt))
        ca, cb = self.thanMirrorXy(cs[0]), self.thanMirrorXy(cs[1])
        self.phi = atan2(cb[1]-ca[1], cb[0]-ca[0])
        self.cc = self.thanMirrorXy(self.cc)
        if not self.full:
            #self.__mirrorThetas(cs)
            self.theta2, self.theta1 = (-self.theta1) % PI2, (-self.theta2)%PI2  #See documetation of __mirrorThetas()
            if self.theta2 < self.theta1: self.theta2 += PI2   # Ensure theta2>=theta1
        self.setBoundBoxRect(self.cc[0], self.cc[1], 2.0*self.a, 2.0*self.b, self.phi, center=True)

    def __mirrorThetas(self, cs):
            """Compute the mirror of thetas.

            Ater running this function some times, we realised that the thetas
            become negative. Also to keep the notation that the arc is drawn,
            counterclokwise from theta1 to theta2, we swap theta1 and theta2.
            """
            print("thanMirror: original: theta1, theta2=", self.theta1*180/pi, self.theta2*180/pi)
            print("thanMirror: original: ca, cb=", cs[2], cs[3])
            ca, cb = self.thanMirrorXy(cs[2]), self.thanMirrorXy(cs[3])
            print("thanMirror: after   : ca, cb=", ca, cb)
            cosf = cos(-self.phi)
            sinf = sin(-self.phi)
            oms = []
            for xt,yt in ca, cb:
                xt = xt - self.cc[0]
                yt = yt - self.cc[1]
                x = xt*cosf - yt*sinf
                y = xt*sinf + yt*cosf
                cosom = x/self.a
                sinom = y/self.b
                oms.append(atan2(sinom, cosom)%PI2)
            self.theta2, self.theta1 = oms
            print("thanMirror: after   : theta1, theta2=", self.theta1*180/pi, self.theta2*180/pi)
            if self.theta2 < self.theta1: self.theta2 += PI2   # Ensure theta2>=theta1
            print("thanMirror: after   : theta1, theta2=", self.theta1*180/pi, self.theta2*180/pi)


    def thanPointMir(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        cs = []
        cosf = cos(self.phi)
        sinf = sin(self.phi)
        for om in pi, 0, self.theta1, self.theta2:
            x = self.a*cos(om)
            y = self.b*sin(om)
            xt = x*cosf - y*sinf
            yt = x*sinf + y*cosf
            cs.append((self.cc[0]+xt, self.cc[1]+yt))
        ca, cb = self.thanPointMirXy(cs[0]), self.thanPointMirXy(cs[1])
        self.phi = atan2(cb[1]-ca[1], cb[0]-ca[0])
        self.cc = self.thanPointMirXy(self.cc)
        #if not self.full:  #See documetation of __pointMirThetas()
        #    self.__pointMirThetas(cs)
        self.setBoundBoxRect(self.cc[0], self.cc[1], 2.0*self.a, 2.0*self.b, self.phi, center=True)

    def __pointMirThetas(self, cs):
            """Compute the point mirror of thetas.

            Ater running this function some times, we realised that the thetas
            remain the same!
            """
            print("thanPointMir: original: theta1, theta2=", self.theta1*180/pi, self.theta2*180/pi)
            ca, cb = self.thanPointMirXy(cs[2]), self.thanPointMirXy(cs[3])
            cosf = cos(-self.phi)
            sinf = sin(-self.phi)
            oms = []
            for xt,yt in ca, cb:
                xt = xt - self.cc[0]
                yt = yt - self.cc[1]
                x = xt*cosf - yt*sinf
                y = xt*sinf + yt*cosf
                cosom = x/self.a
                sinom = y/self.b
                oms.append(atan2(sinom, cosom)%PI2)
            self.theta1, self.theta2 = oms
            print("thanPointMir: after   : theta1, theta2=", self.theta1*180/pi, self.theta2*180/pi)
            if self.theta2 < self.theta1: self.theta2 += PI2   # Ensure theta2>=theta1
            print("thanPointMir: after   : theta1, theta2=", self.theta1*180/pi, self.theta2*180/pi)


    def thanScale(self, cs, scale):
        "Enlarges or shrinks the element with predefined basepoint and factor."
        self.cc = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.cc, cs)]  #works for python2,3
        self.a *= scale
        self.b *= scale
        self.setBoundBoxRect(self.cc[0], self.cc[1], 2.0*self.a, 2.0*self.b, self.phi, center=True)


    def thanMove(self, dc):
        "Moves the element with predefined displacecent in all axes."
        self.cc = [cc1+dd1 for (cc1,dd1) in zip(self.cc, dc)]   #works for python2,3
        self.setBoundBoxRect(self.cc[0], self.cc[1], 2.0*self.a, 2.0*self.b, self.phi, center=True)


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type in otypes nearest to point ccu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        #if "nea" in otypes:
        #    cn, rn, thet = self.thanPntNearest2(ccu)
        #    if thet is not None:
        #        if "cen" not in otypes or rn > self.r:  # If we are getting near from the outside then "nea"
        #            self.thanOsnapAdd(ccu, ps, thet, "nea")
        #            ps.append((fabs(cn[0]-ccu[0])+fabs(cn[1]-ccu[1]), "nea", cn))
        #if "cen" in otypes:
        #    cn, rn, thet = self.thanPntNearest2(ccu)
        #    if thet is not None:
        #        if "nea" not in otypes or rn < self.r:  # If we are getting near from the inside then "cen"
        #            ps.append((fabs(cn[0]-ccu[0])+fabs(cn[1]-ccu[1]), "cen", self.cc))
        if "qua" in otypes:
            for thet in 0, 0.5*pi, pi, 1.5*pi:    # If both "nea" and "cen" are active, "qua" does not have a chance
                self.thanOsnapAdd(ccu, ps, thet, "qua")
        #if cori is not None and "tan" in otypes:
        #    dx = (self.cc[0] - cori[0])*0.5
        #    dy = (self.cc[1] - cori[1])*0.5
        #    r = hypot(dx, dy)
        #    c = cori[0]+dx, cori[1]+dy
        #    for cp in thanintersect.thanCirCir(self.cc, self.r, c, r):
        #        thet = atan2(cp[1]-self.cc[1], cp[0]-self.cc[0]) % PI2
        #        self.thanOsnapAdd(ccu, ps, thet, "tan")
        #if cori is not None and "per" in otypes:
        #    for cn in self.thanPerpPoints(cori):
        #        ps.append((fabs(cn[0]-ccu[0])+fabs(cn[1]-ccu[1]), "per", cn))
        #if eother is not None and "int" in otypes:
        #    ps.extend(thanintall.thanIntsnap(self, eother, ccu, proj))
        if len(ps) > 0: return min(ps)
        return None


    def thanOsnapAdd(self, ccu, ps, thet, snaptyp):
        "Add a new point to osnap points."
        cp = self.thanPerimPoint(thet)
        cc = list(self.cc)
        cc[:2] = cp
        ps.append((fabs(cc[0]-ccu[0])+fabs(cc[1]-ccu[1]), snaptyp, cc))


    def thanPerimPoint(self, thet):
        "Return the coordinates of a point on the perimeter."
        x = self.a*cos(thet)
        y = self.b*sin(thet)
        sinf = sin(self.phi)
        cosf = cos(self.phi)
        xt = x*cosf - y*sinf
        yt = x*sinf + y*cosf
        return self.cc[0]+xt, self.cc[1]+yt


    def thanChelev(self, z):
        "Set constant elevation of z."
        ThanElement.thanChelev(self, z)


    def thanChelevn(self, celev):
        "Set constant elevation of z and higher dimensions."
        ThanElement.thanChelevn(self, celev)


    def getInspnt(self):
        "Returns the insertion point of the element."
        return ThanElement.getInspnt(self)


    def thanReverse(self):
        "Reverse the spin of the ellipse."
        self.spin = -self.spin


    def thanTkGet(self, proj):
        "Gets the attributes of the ellipse spline interactively from a window."
        un = proj[1].thanUnits
        cc = proj[2].thanGudGetPoint(T["Center (5=tilted through 5 points/4=horizontal through 4 points): "], options=("5", "4"))
        if cc == Canc: return Canc                                  #Ellipse was cancelled
        if cc == "5": return self.__getTiltHor(proj, 5)
        if cc == "4": return self.__getTiltHor(proj, 4)
        a = proj[2].thanGudGetCircle(cc, 1.0, T["Semi-major axis: "])
        if a == Canc: return Canc                                   #Ellipse was cancelled
        b = proj[2].thanGudGetEllipseB(cc, a, 0.0, T["Semi-minor axis: "])
        if b == Canc: return Canc                                   #Ellipse was cancelled
        mes = "%s (enter=%s): " % (T["Rotation angle (azimuth)"], un.strdir(0.0))
        phi = proj[2].thanGudGetAzimuth(cc, mes, un.rad2unitdir(0.0))
        if phi == Canc: return Canc                                 #Ellipse was cancelled
        phi = un.unit2raddir(phi)
        self.thanSet(cc, a, b, 0.0, PI2, phi, full=True, spin=1)
        return True                              # Spline OK


    def __getTiltHor(self, proj, nmin):
        "Fit a tilted or horizontal ellipse through at least 5 or 4 points respectively."
        cs = self.__getPoints(proj, nmin)
        if cs == Canc: return Canc
        x = [cc[0] for cc in cs]
        y = [cc[1] for cc in cs]
        if nmin == 5: v, terr = ellipse5Lsm(x, y)
        else:         v, terr = ellipse4Lsm(x, y)
        if v is not None:
            cc = list(cs[0])
            cc[:2] = v[2], v[3]
            self.thanSet(cc, v[0], v[1], 0.0, PI2, v[4], full=True, spin=1)
            return True
        proj[2].thanPrter(terr)
        if "define" not in terr: return Canc
        ans = proj[2].thanGudGetYesno(T["Do you want to try the best fit to ellipse (Yes/No) <No>: "], default=False)
        if not ans: return Canc
        if nmin == 5: v, terr = ellipse5Fit(x, y)
        else:         v, terr = ellipse4Fit(x, y)
        if v is not None:
            cc = list(cs[0])
            cc[:2] = v[2], v[3]
            self.thanSet(cc, v[0], v[1], 0.0, PI2, v[4], full=True, spin=1)
            return True
        proj[2].thanPrter(terr)
        return Canc


    def __getPoints(self, proj, nmin):
        "Gets nmin points or more from user and fit an ellipse if possible."
        cs = []
        while True:
            n = len(cs)
            if n == 0:
                c1 = proj[2].thanGudGetPoint(T["Point 1 of ellipse (points from a Line/Select point elements): "],
                    options=("Line", "Select"))
                if c1 == Canc: return Canc                                   #Ellipse was cancelled
                if c1 == "l": return self.__getPointsLine(proj, nmin)
                if c1 == "s": return self.__getPointsSel (proj, nmin)
                cs.append(c1)
            elif n < nmin:
                c1 = proj[2].thanGudGetPoint(T["Point %s of ellipse (Undo): "]%(n+1,), options=("u",))
                if c1 == Canc:  return Canc                                  #Ellipse was cancelled
                elif c1 == "u": del cs[-1]
                else:           cs.append(c1)
            else:
                c1 = proj[2].thanGudGetPoint(T["Point %s of ellipse (Undo/enter=finish): "]%(n+1,), options=("u",""))
                if c1 == Canc:  return Canc                                  #Ellipse was cancelled
                elif c1 == "":  break
                elif c1 == "u": del cs[-1]
                else:           cs.append(c1)
        return cs


    def __getPointsLine(self, proj, nmin):
        "Select a line which has at least nmin nodes and returns its nodes."
        from thancom import thancomsel
        while True:
            e = thancomsel.thanSelect1(proj, stat=T["Select a line which has at least %d nodes: "]%(nmin,),
                filter=lambda e: isinstance(e, ThanLine))
            proj[2].thanGudSetSelRestore()                   # Restores previous selection
            if e == Canc: return Canc
            try:    cp = e.cpori      #In case it is a spline
            except: cp = e.cp
            if thanNear2(cp[-1], cp[-1]): cp = cp[:-1]       #If closed line delete the last point (which coincides with the first)
            if len(cp) >= nmin: break
            proj[2].thanPrter(T["Line has only %d nodes. Try again."]%(len(cp),))
        return cp


    def __getPointsSel(self, proj, nmin):
        "Select point elements and return their coordinates."
        from thancom import thancomsel
        while True:
            proj[2].thanPrt(T["Select least %d point elements:"]%(nmin,))
            r = thancomsel.thanSelectGen(proj, standalone=False,
                filter=lambda e: isinstance(e, ThanPoint))
            elems = proj[2].thanSelall
            proj[2].thanGudResetSelColor()                   # Unmarks the selection
            proj[2].thanGudSetSelRestore()                   # Restores previous selection
            proj[2].thanUpdateLayerButton()                  # Show current layer again
            if r == Canc: return Canc
            if len(elems) >= nmin: break
            proj[2].thanPrter(T["Only %d point elements were selected. Try again."]%(len(elems),))
        return [e.cc for e in elems]


    def thanTkDraw1(self, than):
        "Draws the spline to a Tk Canvas."
        #dx, dy = than.ct.global2LocalRel(1.0, 1.0)
        #dt = hypot(1.0, 1.0)/hypot(dx, dy)*10.0    #This means that dt is about 10 pixels
        dt = than.thanGudGetDt()
        self.cp, self.tp = self.than2Line(dt)
        ThanCurve.thanTkDraw1(self, than)


    def thanExpThc1(self, fw):
        "Save the ellipse in thc format."
        f = fw.formFloat
        fw.writeNode(self.cc)
        fw.writeln((f+f) % (self.a, self.b))
        fw.writeln((f+f) % (self.theta1, self.theta2))
        fw.writeln(f % (self.phi,))
        fw.writeln("%d" % (self.full,))
        fw.writeln("%d" % (self.spin,))


    def thanImpThc1(self, fr, ver):
        "Read the ellipse from thc format."
        cc = fr.readNode()                   #May raise ValueError, IndexError, StopIteration
        a, b = map(float, next(fr).split()) #May raise ValueError, IndexError, StopIteration   #works for python2,3
        theta1, theta2 = map(float, next(fr).split()) #May raise ValueError, IndexError, StopIteration   #works for python2,3
        phi = float(next(fr))               #May raise ValueError, StopIteration
        full = bool(int(next(fr)))          #May raise ValueError, StopIteration
        spin = int(next(fr))                #May raise ValueError, StopIteration
        if spin not in (1, -1): raise ValueError("spin must be 1, or -1")
        self.thanSet(cc, a, b, theta1, theta2, phi, full, spin)


    def thanExpDxf(self, fDxf):
        "Exports the arc to dxf file."
        rd = 180.0 / pi
        fDxf.thanDxfPlotEllipse(self.cc[0], self.cc[1], self.a, self.b,
            self.theta1*rd, self.theta2*rd, self.phi*rd)


    def thanExpKml(self, than):
        "Exports the ellipse to Google .kml file."
        than.ibr += 1
        aa = than.form % (than.ibr,)
        cp, tp = self.than2Line(than.dt)    #1m resolution is hopefully enough for google maps
        than.kml.writeLinestring(aa, cp, than.layname, desc="")


    def thanTransform(self, fun):
        """Transform all the coordinates of the ellipse according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        cc = list(self.cc)
        cc[:3] = fun(cc[:3])
        cf = cos(self.phi)
        sf = sin(self.phi)
        cr = list(self.cc)
        cr[0] += self.a*cf
        cr[1] += self.a*sf
        cr = fun(cr[:3])
        a = hypot(cr[1]-cc[1], cr[0]-cc[0])
        phi = atan2(cr[1]-cc[1], cr[0]-cc[0])  #Note that python ensures than atan2(0,0) = 0!!!

        cr = list(self.cc)
        cr[0] -= self.b*sf       #cos(t+90) = -sin(t)
        cr[1] += self.b*cf       #sin(t+90) =  cos(t)
        cr = fun(cr[:3])
        b = hypot(cr[1]-cc[1], cr[0]-cc[0])

        ths = [self.theta1, self.theta2]
        for i,th in enumerate(ths):
            cr = list(self.cc)
            dx = self.a * cos(th)
            dy = self.b * sin(th)
            cr[0] += dx*cf - dy*sf
            cr[1] += dy*sf + dy*cf
            cr = fun(cr[:3])
            ths[i] = atan2(cr[1]-cc[1], cr[0]-cc[0])   #Note that python ensures than atan2(0,0) = 0!!!
        self.thanSet(cc, a, b, ths[0], ths[1], phi, self.full, self.spin)


    def thanList(self, than):
        "Shows information about the arc element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        t = ("%s%s" % (T["Center: "], than.strcoo(self.cc)),
             "%s%s    %s%s" % (T["Semi-major axis: "], than.strdis(self.a), T["Semi-minor axis: "], self.b),
             "%s%s    %s%s" % (T["Angle from X axis: "], than.strang(self.phi), T["Spin: "], self.spin),
             T["Spans: %s    to: %s\n"]% (than.strdir(self.theta1), than.strdir(self.theta2)),
            )
        than.write("\n".join(t))
