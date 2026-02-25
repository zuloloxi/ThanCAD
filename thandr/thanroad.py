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

This module defines the road element. It is a polyline with its corners rounded
with circular arcs of given radius.
"""
from math import fabs, hypot, sqrt, pi, cos, sin
from p_ggen import iterby2, iterby3, thanUnicode
from p_gmath import thanNearx, thanNear2
import p_ggeom
from thanvar import Canc, tkRoadNode, calcRoadNode, thanCleanLine2
from thantrans import T
from . import thanintall
from .thanelem import ThanElement
from .thanline import ThanLine
from .thanarc import ThanArc

############################################################################
############################################################################

class ThanRoad(ThanElement):
    "A simple 2d line with line segments and arcs."
    thanTkCompound = 100       # The number of Tkinter objects that make the element. 100=compound (lines etc.)
    thanElementName = "ROAD"   # Name of the element's class

#===========================================================================

    def thanSet(self, cpr):
        """Sets the attributes of the road.

        cpr is made of points (lists) which have 1 dimension more than simple
        points. The last dimension is the radius of the road curve.
        The radius of the first and the last point are ignored and they should
        be zero.
        """
        assert len(cpr) > 1, "Less than 2 points in ThanRoad!"
        self.cpr = thanCleanLine2(cpr)
        xp = [c1[0] for c1 in self.cpr]
        yp = [c1[1] for c1 in self.cpr]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])
#       self.thanTags = ()            # thanTags is initialised in ThanElement

    def thanIsNormal(self):
        "Returns False if the road is degenerate (only 1 node)."
        if len(self.cp) < 2: return False       # Return False if road is degenerate
        cp = iter(self.cp)
        c1 = next(cp)
        for c2 in cp:
            if not thanNear2(c1, c2): return True
        return False      # All line points are close together


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.thanRotateXyn(self.cpr)

    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        self.thanMirrorXyn(self.cpr)

    def thanMirror(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        self.thanPointMirXyn(self.cpr)

    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        for cc in self.cpr:
            cc[:-1] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(cc[:-1], cs)]  #works for python2,3
            cc[-1] *= scale     # Radius

    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        for cc in self.cpr:
            cc[:-1] = [cc1+dd1 for (cc1,dd1) in zip(cc[:-1], dc)] #works for python2,3

    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type in otypes nearest to xcu, ycu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        if "end" in otypes:       # type "end" without type "int"
            for c in self.cpr:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "end", c[:-1]))
        if "mid" in otypes:
            for ca, cb in iterby2(self.cpr):
                c = [(ca1+cb1)*0.5 for (ca1,cb1) in zip(ca, cb)]  #works for python2,3
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "mid", c[:-1]))
        if "nea" in otypes:
            c = self.thanPntNearest(ccu)
            if c is not None:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "nea", c))
        if eother is not None and "int" in otypes:
            ps.extend(thanintall.thanIntsnap(self, eother, ccu, proj))
        if len(ps) < 1: return None
        return min(ps)

    def thanPntNearest(self, ccu):
        "Finds the nearest point of this road to a point."
        return self.thanPntNearest2(ccu)[0]

    def thanPntNearest2(self, ccu):
        "Finds the nearest point of this road to a point."
        dmax=1e100; cp1 = None; iseg = -1; cp = self.cpr
        for i in range(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
            aa = hypot(*a)
            if thanNearx(aa, 0.0): continue      # Segment has zero length
            ta = a[0]/aa, a[1]/aa
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dt = ta[0]*b[0]+ta[1]*b[1]
            if   thanNearx(dt, 0.0) : dt = 0.0
            elif thanNearx(dt, aa)  : dt = aa
            elif dt < 0.0 or dt > aa: continue
            dn = fabs(-ta[1]*b[0]+ta[0]*b[1])
            if dn < dmax:
                cp1 = [e+(f-e)*dt/aa for (e,f) in zip(cp[i-1], cp[i])]  #works for python2,3
                del cp1[-1]
                dmax = dn
                iseg = i
        return cp1, iseg

    def thanSegNearest(self, ccu):
        """Finds the nearest segment of this road to a point.

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
        cp = self.cpr
        for i in range(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
            aa = hypot(*a)
            if aa == 0.0: continue              # Segment has zero length
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dn = fabs(a[0]*b[1]-a[1]*b[0]) / aa
            if dn < dmax: imax=i; dmax=dn
        return cp[imax-1][:-1], cp[imax][:-1]

    def thanBreak(self, c1=None, c2=None):
        "Breaks a line to 2 pieces."
        if c1 is None: return True          # Break IS implemented
        cp1, i1 = self.thanPntNearest2(c1)
        cp2, i2 = self.thanPntNearest2(c2)
        if i2 < i1:
            cp1, i1, cp2, i2 = cp2, i2, cp1, i1
        elif i2 == i1:
            i = i1 - 1
            d1 = hypot(cp1[0]-self.cpr[i][0], cp1[1]-self.cpr[i][1])
            d2 = hypot(cp2[0]-self.cpr[i][0], cp2[1]-self.cpr[i][1])
            if d2 < d1:
                cp1, i1, cp2, i2 = cp2, i2, cp1, i1
        assert cp1 is not None and cp2 is not None, "It should have been checked!"
        e1 = ThanRoad()
        e1.thanSet(self.cpr[:i1+1])
        e1.cpr[i1] = cp1
        e2 = ThanRoad()
        e2.thanSet(self.cpr[i2-1:])         # Note that i2-1 >= 0
        e2.cpr[0] = cp2
        return e1, e2

#===========================================================================

    def thanTkGet(self, proj):
        "Gets the attributes of the road interactively from a window."
        g2l = proj[2].than.ct.global2Local
        g2lr= proj[2].than.ct.global2LocalRel
        l2g = proj[2].than.ct.local2Global
        dc = proj[2].than.dc
        fi = proj[2].than.outline
        w = proj[2].than.tkThick
        rdef = 50.0                                             # default radius

        cpr = []; ctr = []
        c1 = proj[2].thanGudGetPoint(T["First road point:"])
        if c1 == Canc: return Canc                              # Road was cancelled
        c1.append(0.0)                                          # radius
        cpr.append(c1); ctr.append(c1)

        while True:
            c1 = proj[2].thanGudGetLine(cpr[-1], "Second road point: ")
            if c1 == Canc: return Canc                            # Road was cancelled
            c1.append(rdef)                                       # radius
            cpr.append(c1); ctr.append(c1)

            c1 = None; r1 = rdef
            proj[2].thanCom.thanAppend("%s%d\n" % (T["Radius="], r1), "info1")
            while True:
                c1, cargo = self.__getPointLin(proj[2], ctr[-2], cpr[-1], c1, r1, len(cpr))
                if c1 == Canc and len(cpr) < 2: return Canc         # Road was cancelled
                if c1 == Canc or c1 == "" or c1 == "c": break       # Road was ended
                if cargo == "r":
                    print("r:", c1)
                    res = proj[2].thanGudGetRoadR(ctr[-2], cpr[-1], c1, r1, T["New radius: "])
                    if res != Canc: cpr[-1][-1] = r1 = res
                elif c1 == "r":                                     # Get new radius
                    res = proj[2].thanGudGetPosFloat(T["New default radius: "], rdef)
                    if res != Canc: rdef = cpr[-1][-1] = r1 = res
                    c1 = None
                elif c1 == "u":                                     # Undo last point
                    if len(cpr) < 3: break
                    dc.delete("e"+str(len(cpr)))
                    del cpr[-1], ctr[-1]
                else:                                               # Plot the new point
                    c1.append(rdef)                                 # Radius
                    cpr.append(c1); ctr.append(c1)

                    xp1, yp1 = g2l(ctr[-3][0], ctr[-3][1])
                    xp2, yp2 = g2l(cpr[-2][0], cpr[-2][1])
                    xp3, yp3 = g2l(c1[0], c1[1])
                    rp2, _ = g2lr(cpr[-2][-1], 0.0)
                    tags = "e0", "e"+str(len(cpr))
                    items, ct = tkRoadNode(xp1, yp1, xp2, yp2, xp3, yp3, rp2, dc, fi, (), w, tags)
                    dc.delete(items[2])
                    ctr[-2] = l2g(*ct)
                    print("----------------------------------------------")
                    for c1 in cpr: print(c1)
                    c1 = None; r1 = rdef
                    proj[2].thanCom.thanAppend("%s%d\n" % (T["Radius="], r1), "info1")
            if c1 == "u":
                del cpr[-1], ctr[-1]
            else:
                break
        if c1 == "c":
            proj[2].thanCom.thanAppend("Road close has not yet been implemented :)\n")

        dc.delete("e0")
        self.thanSet(cpr)
        return True                              # Road OK


    def __getPointLin(self, win, c1, c2, c3, r3, np):
        "Gets a point from the user, with possible options."
        if np == 3:
            stat1 = T["Next road point (radius/undo/<enter>): "]
            return win.thanGudGetRoadP(c1, c2, c3, r3, stat1, options=("radius", "undo", ""))
        else:
            stat1 = T["Next road point (radius/undo/close/<enter>): "]
            return win.thanGudGetRoadP(c1, c2, c3, r3, stat1, options=("radius", "undo", "close", ""))

#===========================================================================

    def thanTkDraw(self, than):
        "Draws the road to a Tk Canvas."
        g2l = than.ct.global2Local
        g2lr = than.ct.global2LocalRel
        dc = than.dc
        fi = than.outline
        w = than.tkThick
        tags = self.thanTags
        xp1, yp1 = g2l(self.cpr[0][0], self.cpr[0][1])
        xp2, yp2 = g2l(self.cpr[1][0], self.cpr[1][1])

        n = len(self.cpr)
        if n < 3:
            item = dc.create_line(xp1, yp1, xp2, yp2, fill=fi, dash=than.dash, width=w, tags=tags)
            return
        for i in range(1, n-1):
            xp3, yp3 = g2l(self.cpr[i+1][0], self.cpr[i+1][1])
            rp2, _ = g2lr(self.cpr[i][-1], 0.0)
            items, ct = tkRoadNode(xp1, yp1, xp2, yp2, xp3, yp3, rp2, dc, fi, than.dash, w, tags)
            if i < n-2: dc.delete(items[2])
            xp1, yp1 = ct
            xp2, yp2 = xp3, yp3


    def getInspnt(self):
        "Returns the insertion point of the road."
        return list(self.cpr[0])

    def thanChelev(self, z):
        "Set constant elevation of z."
        for cc in self.cpr:
            cc[2] = z

    def thanChelevn(self, celev):
        "Set constant elevation of z and higher dimensions."
        for cc in self.cpr:
            cc[2:-1] = celev     #Last dimension is radius

    def thanLength(self):
        "Returns the length of the road."
        Tp = le = 0.0
        for a,b,c in iterby3(self.cpr):   #Note that this is not executed if len(cpr) < 3
            nod = calcRoadNode(a[0], a[1], b[0], b[1], c[0], c[1], b[-1])
            ab = hypot(b[0]-a[0], b[1]-a[1])
            le += ab-Tp-nod.T1+nod.LK
            Tp = nod.T1
        a, b = self.cpr[-2:]
        ab = hypot(b[0]-a[0], b[1]-a[1])
        le += ab-Tp        # Note that if len(cpr) < 3, then Tp=0.0 and le=ab
        return le

    def thanArea(self):
        """Finds the area of the curve defined by the road.

        That is if we imagine a line which joins the first and last point
        of the road.
        At first a polygon by the first, all the As end Ts of the circular arcs
        and the last node is constructed, and its area is computed. Then
        the areas between the arcs and the polygon are added.
        """
        cs = [self.cpr[0]]
        aarc = 0.0
        for a,b,c in iterby3(self.cpr):   #Note that this is not executed if len(cpr) < 3
            nod = calcRoadNode(a[0], a[1], b[0], b[1], c[0], c[1], b[-1])
            cs.append([nod.pa.x, nod.pa.y])
            cs.append([nod.pt.x, nod.pt.y])
            asec = nod.phi*0.5*nod.R**2
            atri = nod.R*cos(nod.phi*0.5)*nod.R*sin(nod.phi*0.5)
            aarc += asec-atri
        cs.append(self.cpr[-1])
        cs.append(self.cpr[0])
        return p_ggeom.area(cs) + aarc


    def thanExpDxf(self, fDxf):
        "Exports the road to dxf file."
        if len(self.cpr) < 3:
            for c1 in self.cpr:
                fDxf.thanDxfPlotPolyVertex(c1[0], c1[1], 2)
            fDxf.thanDxfPlotPolyVertex(0.0, 0.0, 999)
            return
        c1 = self.cpr[0]
        fDxf.thanDxfPlotPolyVertex(c1[0], c1[1], 2)
        for i in range(2, len(self.cpr)):
            c2 = self.cpr[i-1]
            c3 = self.cpr[i]
            r = c2[-1]
            nod = calcRoadNode(c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], r)
            dchord2 = hypot(nod.pt.x-nod.pa.x, nod.pt.y-nod.pa.y) * 0.5
            dbulge = r - sqrt(r**2 - dchord2**2)
            bulge = dbulge/dchord2 * nod.pr    # nod.pr is the sign

#            fDxf.thanDxfPlotPolyArc(nod.pa.x, nod.pa.y, bulge)
            fDxf.thanDxfPlotPolyVertex(nod.pa.x, nod.pa.y, 2, bulge)

            fDxf.thanDxfPlotPolyVertex(nod.pt.x, nod.pt.y, 2)
            c1 = [nod.pt.x, nod.pt.y, 0.0]
            c1 = self.cpr[-1]
            fDxf.thanDxfPlotPolyVertex(c1[0], c1[1], 2)
            fDxf.thanDxfPlotPolyVertex(0.0, 0.0, 999)


    def thanExpThc1(self, fw):
        "Save the line in thc format."
        fw.writeSnodes("SNODES", 4, self.cpr)


    def thanImpThc1(self, fr, ver):
        "Read the line from thc format."
        cp = fr.readSnodes("SNODES", 4)
        self.thanSet(cp)


    def thanExpSyk(self, than):
        "Exports the road to syk file."
        than.write("%15.3f  %s\n" % (self.cpr[0][2], than.layname))
        for cp1 in self.cpr:
            than.write("%15.3f%15.3f\n" % (cp1[0], cp1[1]))
        than.write("$\n")


    def thanExpBrk(self, than):
        "Exports the road to brk file."
        for cp1 in self.cp:
            than.ibr += 1
            than.write(than.form % (than.ibr, cp1[0], cp1[1], cp1[2]))
        than.write("$\n")

    def thanExpPil(self, than):
        "Exports the road to a PIL raster image."
        if len(self.cpr) < 3:
            e = ThanLine()
            e.thanSet(self.cpr)
            e.thanExpPil(than)
            return
        c1 = self.cpr[0]
        for i in range(2, len(self.cpr)):
            c2 = self.cpr[i-1]
            c3 = self.cpr[i]
            nod = calcRoadNode(c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], c2[-1])
            e = ThanLine()
            e.thanSet([c1, [nod.pa.x, nod.pa.y, 0.0]])
            e.thanExpPil(than)
            e = ThanArc()
            e.thanSet([nod.pc.x, nod.pc.y, 0.0], c2[-1], nod.theta1*pi/180, nod.theta2*pi/180)
            e.thanExpPil(than)
            c1 = [nod.pt.x, nod.pt.y, 0.0]
        e = ThanLine()
        e.thanSet([c1, self.cpr[-1]])
        e.thanExpPil(than)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        cpr = [list(cc) for cc in self.cpr]
        for cc in cpr:
            ce = list(cc)
            ce[0] += cc[-1]                             #Add the radius
            cc[:3] = fun(cc[:3])
            ce[:3] = fun(ce[:3])
            cc[-1] = hypot(ce[1]-cc[1], ce[0]-cc[0])    #Recompute radius
        self.thanSet(cpr)


    def thanList(self, than):
        "Shows information about the road element."
        wr = than.write
        coo = than.strcoo
        dis = than.strdis
        cpr = self.cpr
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        wr("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        wr("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        wr(T["Vertices %d (X Y Z Radius):\n"] % len(cpr))
        wr("    %s\n" % coo(cpr[0][:-1]))
        n = len(cpr) - 1
        for i in range(1, n):
            wr("    %s %s%s\n" % (coo(cpr[i][:-1]), T["Radius: "], dis(cpr[i][-1])))
        wr("    %s\n" % coo(cpr[n][:-1]))
