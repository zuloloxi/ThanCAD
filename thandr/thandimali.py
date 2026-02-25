##############################################################################
# ThanCad 0.2.4 "Valencia": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2014 Thanasis Stamos, November 15, 2014
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
ThanCad 0.2.4 "Valencia": n-dimensional CAD with raster support for engineers

This module defines the dimension element.
"""

from math import hypot, atan2, fabs
from itertools import izip, islice
from p_ggen import thanUnicode
from p_gmath import thanNear2
from thanvar import Canc
from thantrans import T
from thanelem import ThanElement
from thanline import ThanLine
from thantext import ThanText

try: import pyx
except ImportError: pass


class ThanDimali(ThanElement):
    "A simple line of horizontal text."
    thanTkCompound = 100       # The number of Tkinter objects that make the element. 100=compound (lines etc.)
    thanElementName = "ALIGNEDDIMENSION"    # Name of the element's class


    def __rect(self, c1, c2, h):
        "Finds rotated rectangle with c1-c2 side and parallel side at perpendicular distance h."
        c3 = list(c2)
        c4 = list(c1)
        if thanNear2(c1, c2):
            cost = 0.0
            sint = 1.0
        else:
            cost = c2[0]-c1[0]
            sint = c2[1]-c1[1]
            w = hypot(cost, sint)
            cost /= w
            sint /= w
#        xb = xa + w*cost
#        yb = ya + w*sint
        c3[0] = c2[0] - h*sint
        c3[1] = c2[1] + h*cost
        c4[0] = c1[0] - h*sint
        c4[1] = c1[1] + h*cost
        return [list(c1), list(c2), c3, c4]


    def thanSet(self, text, c1, c2, perp):
        "Sets the attributes of the aligned dimension."
        self.text = text
        self.cp = self.__rect(c1, c2, perp)
        self.perp = perp
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])
#        self.thanTags = ()                                 # thanTags is initialised in ThanElement


    def thanIsNormal(self):
        "Returns False if the the aligned dimension is degenerate (it is blank)."
        return not thanNear2(self.cp[0], self.cp[1])  # Degenerate dimension


#    def thanClone(self): Inherited from ThanElement: deepcopy of the instance is OK


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


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        for cc in self.cp:
            cc[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in izip(cc, cs)]
        cscs = [cs[0], cs[1], cs[0], cs[1]]
        self.thanXymm[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in izip(self.thanXymm, cscs)]


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        for cc in self.cp:
            cc[:] = [cc1+dd1 for (cc1,dd1) in izip(cc, dc)]
        dcdc = [dc[0], dc[1], dc[0], dc[1]]
        self.thanXymm[:] = [cc1+dd1 for (cc1,dd1) in izip(self.thanXymm, dcdc)]


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type otype nearest to xcu, ycu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        if "end" in otypes:       # type "end" without type "int"
            for c in self.cp[2:]:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "end", c))
        if len(ps) > 0: return min(ps)
        return None


    def thanBreak(self, c1=None, c2=None):
        "Just inform that the aligned dimension can not (yet) be broken."
        return False       # Break is NOT implemented


    def thanExplode(self, than=None):
        "Transform the dimension to a set of smaller elements."
        if than is None: return True               # Break IS implemented
        return iter(self.__decompose())


    def getInspnt(self):
        "Returns the insertion point of the element."
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
        "Returns the true length (2dimensional distance) of the dimension."
        ca = self.cp[0]
        cb = self.cp[1]
        return hypot(cb[0]-ca[0], cb[1]-ca[1])

    def thanArea(self):
        "Just inform that the aligned dimension does not have area."
        return None


    def thanTkGet(self, proj):
        "Gets the attributes of the text interactively from a window."
        un = proj[1].thanUnits
        c1 = proj[2].thanGudGetPoint(T["First dimension point: "])
        if c1 == Canc: return Canc                       # Aligned dimension cancelled
        statonce = ""
        while True:
            c2 = proj[2].thanGudGetLine(c1, T["Last  dimension point: "], statonce=statonce)
            if c2 == Canc: return Canc                       # Aligned dimension cancelled
            if not thanNear2(c1, c2): break
            statonce = T["Degenerate dimension. Try again.\n"]
        cost = c2[0]-c1[0]; sint = c2[1]-c1[1]
        w = hypot(cost, sint)
        cost /= w; sint /= w
        dis = "%.2f" % w
        mes = "%s (enter=%s): " % (T["Dimension text"], un.strdis(dis))
        text = proj[2].thanGudGetText(mes, dis)
        if text == Canc: return Canc                     # text cancelled

        self.thanSet(text, c1, c2, 0.0)
        self.thanTags = ("e0", )                         # So that we know that it is temporary
        ct = [(t1+t2)*0.5 for t1,t2 in zip(c1,c2)]
        t = [0.0]*len(c1)
        t[:2] = -sint, cost
        c3 = proj[2].thanGudGetMovend(ct, T["Perpendicular location: "], elems=[self], direction=t)
        if c3 == Canc: return Canc                       # Aligned dimension cancelled
        perp = (c3[0]-ct[0])*(-sint) + (c3[1]-ct[1])*cost
        self.thanSet(text, c1, c2, perp)
        return True                                      # Text OK


    ticksize = 0.15
    textsize = 0.20
    dimscale = 10.0
    def thanTkDraw1(self, than):
        "Draws the aligned dimension in Tkinter canvas."
        for e in self.__decompose():
            e.thanTkDraw(than)

    def __decompose(self):
        "Decompose aligned dimensions to a set of ThanCad text and lines."
        elems = []
        if thanNear2(self.cp[0], self.cp[1]): return elems  # degenerate - no elements
        c1 = self.cp[3]
        c2 = self.cp[2]
        cost = c2[0]-c1[0]
        sint = c2[1]-c1[1]
        theta = atan2(sint, cost)
        w = hypot(cost, sint)
        ThanElement.thanRotateSet(c1, theta)

        temp = ThanText()
        temp.thanSet(self.text, c1, self.textsize*self.dimscale, 0.0)
        dc = [0.0] * len(c1)
        dc[0] += (w-temp.w1)*0.5
        dc[1] -= temp.h1*0.5
        temp.thanMove(dc)
        temp.thanRotate()
        temp.thanTags = self.thanTags
        elems.append(temp)

        ct = list(c1)
        ct1 = list(ct)
        ct1[0] += self.ticksize*self.dimscale
        ct1[1] -= self.ticksize*self.dimscale*0.5
        ct2 = list(ct1)
        ct2[1] += self.ticksize*self.dimscale
        cline = [[ct1, ct, ct2]]

        ct = list(c1)
        ct2 = list(ct)
        ct2[0] += (w-temp.w1-temp.h1)*0.5
        cline.append([list(ct), ct2])

        ct = list(c1)
        ct[0] += w
        ct1 = list(ct)
        ct1[0] -= (w-temp.w1-temp.h1)*0.5
        cline.append([ct1, ct])

        ct = list(ct)
        ct1 = list(ct)
        ct1[0] -= self.ticksize*self.dimscale
        ct1[1] -= self.ticksize*self.dimscale*0.5
        ct2 = list(ct1)
        ct2[1] += self.ticksize*self.dimscale
        cline.append([ct1, ct, ct2])

        for cp in cline:
            temp = ThanLine()
            temp.thanSet(cp)
            temp.thanRotate()
            temp.thanTags = self.thanTags
            elems.append(temp)
        return elems


    def thanExpDxf(self, fDxf):
        "Exports the aligned dimension to dxf file."
        for e in self.__decompose():
            e.thanExpDxf(fDxf)

    def thanExpThc1(self, fw):
        "Save the aligned dimension in thc format."
        f = fw.formFloat
        fw.writeNode(self.cp[0])
        fw.writeNode(self.cp[1])
        fw.writeln(f % self.perp)
        fw.writeTextln(self.text)


    def thanImpThc1(self, fr, ver):
        "Read the aligned dimension from thc format."
        c1 = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        c2 = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        perp = float(fr.next())          #May raise ValueError, StopIteration
        text = fr.readTextln()           #May raise StopIteration, ValueError
        self.thanSet(text, c1, c2, perp)


    def thanExpPilother(self, than):
        "Exports the text to a PIL raster image."
        x1, y1 = than.ct.global2Locali(self.x1, self.y1)
        than.dc.text((x1, y1), self.text, font=than.font, fill=than.outline)

    def thanExpPil(self, than):
        "Exports rotated text (in ThanCad line font) into a PIL raster image."
        xa, ya = than.ct.global2Local(self.c1[0], self.c1[1])
        w, h = than.ct.global2LocalRel(self.w1, -self.h1)     # Ensure h>0  (local y-axis is positive downwards)
        if h < 1: return                                      # Size too small to be seen; draw rectangle instead
        than.thanFont.thanPilPaint(than, xa, ya, h, self.text, self.theta)

    def thanPlotPdf(self, than):
        "Plots rotated text (in ThanCad line font) into a PDF file."
        xa, ya = than.ct.global2Local(self.c1[0], self.c1[1])
        w, h = than.ct.global2LocalRel(self.w1, self.h1)     # Ensure h>0  (local y-axis is positive upwards)
        if h < 0.05: return                                  # Size too small to be seen; draw rectangle instead
        lines = than.thanFont.than2lines(xa, ya, h, self.text, self.theta, mirrory=True)

        lineto = pyx.path.lineto
        moveto = pyx.path.moveto
        closepath = pyx.path.closepath
        for cp in lines:
            if len(cp) < 2: continue
            if len(cp) == 2:
                ca = cp[0][0], cp[0][1]
                cb = cp[1][0], cp[1][1]
                p = pyx.path.line(ca[0], ca[1], cb[0], cb[1])
            else:
                xy1 = [lineto(c1[0], c1[1]) for c1 in islice(cp, 1, None)]
                xy1.insert(0, moveto(cp[0][0], cp[0][1]))
                if cp[0] == cp[-1]: xy1[-1] = closepath()
                p = pyx.path.path(*xy1)
            than.dc.stroke(p)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        cp = [list(cc) for cc in self.cp[:2]]
        for cc in cp: cc[:3] = fun(cc)
        self.thanSet(self.text, cp[0], cp[1], self.perp)


    def thanList(self, than):
        "Shows information about the the aligned dimension element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s\n" % (T["Length"], than.strdis(self.thanLength())))
        t = ('%s"%s"' % (T["Text: "], thanUnicode(self.text)),
             T["Reference points: %s -:- %s"]  % (than.strcoo(self.cp[0]), than.strcoo(self.cp[1])),
             "%s%s\n" % (T["Perpendicular location: "], than.strdis(self.perp)),
            )
        than.write("\n".join(t))


if __name__ == "__main__":
    print __doc__
