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

This module defines the 3d face element.
"""
from itertools import islice
from math import hypot, fabs
import bisect
from p_ggen import iterby2
from p_gmath import thanNear2, thanNear3, fsign
from p_gvec import Vector2
import p_ggeom
from thanvar import Canc
from thanvar.thanoffset import thanOffsetLine
from thantrans import T
from . import thanintall
from .thanelem import ThanElement
from .thanutil import thanPntNearest2, thanSegNearest, thanPerpPoints, thanPerpPointsC
try: import pyx
except ImportError: pass


class ThanFace3d(ThanElement):
    "A 3d face implemented as line, with different export for dxf."
    thanElementName = "FACE3D"    # Name of the element's class

    def thanSet (self, cp):
        """Sets the attributes of the FACE3D element."""
        assert len(cp) >= 3, "3DFACE must have at least 3 points"
        self.cp = [list(cp1) for cp1 in cp]
        if not thanNear3(self.cp[0], self.cp[-1]):
            self.cp.append(list(self.cp[0]))     #Last point coincides with first point for convenience in following methods
        assert len(self.cp) in (4, 5), "3DFACE must have 3 or 4 points"
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])
#        self.thanTags = ()            # thanTags is initialised in ThanElement


    def thanReverse(self):
        "Reverse the sequence of the nodes."
        self.cp.reverse()


    def thanIsNormal(self):
        "Returns False if the line is degenerate (it has only one point)."
        it = iter(self.cp)
        c1 = next(it)
        for c2 in it:
            if not thanNear3(c1, c2): return True
        return False      # All line points are close together


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.thanRotateXyn(self.cp)
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        self.thanMirrorXyn(self.cp)
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])


    def thanPointMir(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        self.thanPointMirXyn(self.cp)
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        for cc in self.cp:
            cc[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(cc, cs)]  #works for python2,3
        cscs = [cs[0], cs[1], cs[0], cs[1]]
        self.thanXymm[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.thanXymm, cscs)]  #works for python2,3


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        for cc in self.cp:
            cc[:] = [cc1+dd1 for (cc1,dd1) in zip(cc, dc)]  #works for python2,3
        dcdc = [dc[0], dc[1], dc[0], dc[1]]
        self.thanXymm[:] = [cc1+dd1 for (cc1,dd1) in zip(self.thanXymm, dcdc)]  #works for python2,3

    def thanPntNearest(self, ccu):
        "Finds the nearest point of this line to a point."
        return thanPntNearest2(self.cp, ccu)[0]
    def thanPntNearest2(self, ccu):
        "Finds the nearest point of this line to a point."
        return thanPntNearest2(self.cp, ccu)
    def thanPerpPoints(self, ccu):
        "Finds perpendicular point from ccu to polyline."
        return thanPerpPoints(self.cp, ccu)
    def thanSegNearest(self, ccu):
        """Finds the nearest segment of this line to a point."""
        return thanSegNearest(self.cp, ccu)

    #thanTrim(), thanBreak(): elemnet can not be broken: inherit methods from ThanElement

    def thanExplode(self, than=None):
        "Transform the line to a set of smaller 2-point lines."
        if than is None: return True               # Explode IS implemented
        return self.__explode()
    def __explode(self):
        "Transform the Face3D a set of 2-point lines; do the job as a generator."
        for i in range(1, len(self.cp)):
            e1 = ThanLine()
            e1.thanSet(self.cp[i-1:i+1])
            if e1.thanIsNormal(): yield e1


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset line by distance distance; to the right if distance>0 and to the left otherwise."
        if through==None and distance==None: return True  # Offset is implemented
        assert sidepoint is not None, "sidepoint must not be none neither in through nor in distance mode."
        distance = self._offsetVecdistance(through, distance, sidepoint)
        if distance is None: return None #sidepoint is outside (to the left or to the right) of line
        cs = self.cp
        cs = thanOffsetLine(cs, distance)
        e = self.thanClone()             #To allow subclasses to use thanOffset too
        e.thanUntag()                    #Invalidate thanTags and handle
        e.thanSet(cs)                    #thanSet has the same signature for all subclasses
        if not e.thanIsNormal(): return None # Element can not be offset (degenerate)
        if len(cs) < 3: return None # Element can not be offset (degenerate)
        if not thanNear3(cs[0], cs[-1]): cs[-1] = list(cs[0]) #Hack to get around thanOffsetLine bug
        if len(cs) not in (4, 5): return None # Element can not be offset (degenerate)
        return e


    def _offsetVecdistance(self, through=None, distance=None, sidepoint=None):
        "Find vector distance of offset line; offset to the right if distance>0 and to the left otherwise."
#        if through==None and distance==None: return True  # Offset is implemented
        assert through!=None or distance!=None, "Both distance and offset are zero; it should have been found"
        cp1, iseg, tcp1 = self.thanPntNearest2(sidepoint)
        if cp1 is None: return None      # Invalid point
        t = Vector2(*self.cp[iseg][:2])-Vector2(*self.cp[iseg-1][:2])
        n = t.normal()
        t = Vector2(*sidepoint[:2])-Vector2(*cp1[:2])
        if through:
            distance = t|n
        else:
            distance = fsign(distance, t|n)
        return distance


    def getInspnt(self):
        "Returns the insertion point of the line."
        return list(self.cp[0])


    def thanChelev(self, z):
        "Set constant elevation of z."
        for cc in self.cp:
            cc[2] = z

    def thanChelevn(self, celev):
        "Set constant elevation of z and higher dimensions."
        for cc in self.cp:
            cc[2:] = celev

    def thanLength(self):
        "Returns the length of the polyline."
        al = 0.0
        for ca, cb in iterby2(self.cp):
            al += hypot(cb[0]-ca[0], cb[1]-ca[1])
        return al

    def thanArea(self):
        "Returns the area of the polyline."
        return p_ggeom.area(self.cp)

    def thanSpin(self):
        "Returns the spin of the line, imagining that it is closed."
        return p_ggeom.spin(self.cp)


    def thanTkDraw1(self, than):
        "Draws the line to a Tk Canvas."
        g2l = than.ct.global2Local
        w = than.tkThick
        xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
#        temp = than.dc.create_polygon(xy1, outline=than.outline, fill=than.fill, tags=self.thanTags, width=w)
        temp = than.dc.create_line(   xy1, fill=than.outline, dash=than.dash, tags=self.thanTags, width=w)


    def thanExpDxf(self, fDxf):
        "Exports the line to dxf file."
        c = self.cp
        if len(c) == 4:     #We know that c[0] == c[-1]
            fDxf.thanDxfPlot3dface3(c[0][0], c[0][1], c[0][2], c[1][0], c[1][1], c[1][2],
                                    c[2][0], c[2][1], c[2][2])
        else:  #This means that len(c) == 5
            fDxf.thanDxfPlot3dface4(c[0][0], c[0][1], c[0][2], c[1][0], c[1][1], c[1][2],
                                    c[2][0], c[2][1], c[2][2], c[3][0], c[3][1], c[3][2])


    def thanExpThc1(self, fw):
        "Save the line in thc format."
        fw.writeNodes(self.cp)


    def thanImpThc1(self, fr, ver):
        "Read the line from thc format."
        cp = fr.readNodes()
        self.thanSet(cp)


    def thanExpSyk(self, than):
        "Exports the line to syk file."
        than.write("%15.3f  %s\n" % (self.cp[0][2], than.layname))
        for cp1 in self.cp:
            than.write("%15.3f%15.3f\n" % (cp1[0], cp1[1]))
        than.write("$\n")


    def thanExpBrk(self, than):
        "Exports the line to brk file."
        for cp1 in self.cp:
            than.ibr += 1
            than.write(than.form % (than.ibr, cp1[0], cp1[1], cp1[2]))
        than.write("$\n")


    def thanExpPilchaos(self, than):
        """Exports the line to a PIL raster image.

        There seems to be a bug in the PIL which chaotically affects the width
        of the line. Thus, this code is not used. But it should be checked
        with future versions of PIL.
        """
        g2l = than.ct.global2Local
        xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
        if thanNear2(self.cp[0], self.cp[-1]) and not than.fill:
            than.dc.polygon(xy1, outline=than.outline, fill=than.fill) # width=than.width)
        else:
            than.dc.line(xy1, fill=than.outline, width=than.width)


    def thanExpPil(self, than):
        "Exports the line to a PIL raster image; workaround PIL bug." #2008_10_07:no longer valid."
        w = than.rwidth
        if w <= 1.5:
            g2l = than.ct.global2Locali
            xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
            than.dc.line(xy1, fill=than.outline)
            return
        w2, _ = than.ct.local2GlobalRel(w*0.5, w)
        for i in range(1, len(self.cp)):
            x1, y1 = self.cp[i-1][0], self.cp[i-1][1]
            x2, y2 = self.cp[i][0], self.cp[i][1]
            dx, dy = x2-x1, y2-y1
            r = hypot(dx, dy)
            if r <= 0.0: continue
            tx, ty = dx/r, dy/r
            nx, ny = -ty*w2, tx*w2
            cr = (x1-nx,y1-ny), (x2-nx,y2-ny), (x2+nx,y2+ny), (x1+nx,y1+ny)
            xy1 = [than.ct.global2Locali(x1, y1) for x1,y1 in cr]
            than.dc.polygon(xy1, outline=than.outline, fill=than.outline)


    def thanPlotPdf(self, than):
        "Plots the line to a pdf file."
        #FIXME: report width of polyline
        if len(self.cp) < 2: return
        g2l = than.ct.global2Local
        if len(self.cp) == 2:
            ca = g2l(self.cp[0][0], self.cp[0][1])
            cb = g2l(self.cp[1][0], self.cp[1][1])
            p = pyx.path.line(ca[0], ca[1], cb[0], cb[1])
        else:
            lineto = pyx.path.lineto
            moveto = pyx.path.moveto
            xy1 = [lineto(*g2l(c1[0], c1[1])) for c1 in islice(self.cp, 1, None)]
            xy1.insert(0, moveto(*g2l(self.cp[0][0], self.cp[0][1])))
            if thanNear2(self.cp[0], self.cp[-1]): xy1[-1] = pyx.path.closepath()
            p = pyx.path.path(*xy1)
        than.dc.stroke(p)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        cp = [list(cc) for cc in self.cp]
        for cc in cp: cc[:3] = fun(cc[:3])
        self.thanSet(cp)


#===========================================================================

    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type otype nearest to ccu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        if "end" in otypes:       # type "end" without type "int"
            for c in self.cp:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "end", c))
        if "mid" in otypes:
            for ca, cb in iterby2(self.cp):
                c = [(ca1+cb1)*0.5 for (ca1,cb1) in zip(ca, cb)]  #works for python2,3
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "mid", c))
        if "nea" in otypes:
            c = self.thanPntNearest(ccu)
            if c is not None:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "nea", c))
        if cori is not None and "per" in otypes:
            for c in self.thanPerpPoints(cori):
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "per", c))
        if eother is not None and "int" in otypes:
            ps.extend(thanintall.thanIntsnap(self, eother, ccu, proj))
        if len(ps) < 1: return None
        return min(ps)


    def thanTkGet(self, proj):
        "Gets the attributes of the line interactively from a window."
        from thancom.thancomdraw import getpol
        cp = getpol(proj, 4)
        if cp == Canc: return Canc
        self.thanSet(cp)
        return True


    def thanList(self, than):
        "Shows information about the line element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], than.laypath))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        than.write("%s%s\n" % (T["Spin: "], self.thanSpin()))
        than.write("%s (%d):\n" % (T["Vertices"], len(self.cp[:-1])))
        for i,c1 in enumerate(self.cp[:-1]):
            than.write("    %s\n" % than.strcoo(c1))
            if i % 20 == 19:
                c = than.read(T["Press enter to continue.."])
                if c == Canc: break
