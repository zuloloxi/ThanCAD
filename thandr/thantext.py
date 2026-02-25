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

This module defines the text element.
"""

from math import sin, cos, fabs, pi, atan2, hypot
from itertools import islice
from tkinter.font import Font
from thanopt import thancadconf
from p_ggen import thanUnicode
from p_gmath import PI2
from thanvar import Canc
from thantrans import T
from .thanelem import ThanElement
from .thanline import ThanLine
try: import pyx
except ImportError: pass


class ThanText(ThanElement):
    "A simple line of horizontal text."
    thanTkCompound = 100       # The number of Tkinter objects that make the element. 100=compound (lines etc.)
    thanElementName = "TEXT"   # Name of the element's class

    def thanSet(self, text, c1, size, theta):
        "Sets the attributes of the text."
        self.size = self.h1 = float(size)      # Temporary ..
        self.w1 = len(text)*self.size          # ..dimensions
        self.setBoundBoxRect(c1[0], c1[1], self.w1, self.h1, theta)
        self.tempSize = True    # In some (all?) GUIs, the GUI must be active in order..
                                # ..to determine the dimensions of the text
        self.text = text
        self.cc = list(c1)
        self.theta = theta % PI2       # Radians assumed
#       self.thanTags = ()             # thanTags is initialised in ThanElement


    def thanRename(self, text):
        "Rename the text, calculate temp size."
        self.text = text
        #self.h1 is here probably the correct height as reported by font
        self.w1 = len(text)*self.h1          # Temporary dimensions
        self.tempSize = True
        self.setBoundBoxRect(self.cc[0], self.cc[1], self.w1, self.h1, self.theta)


    def thanIsNormal(self):
        "Returns False if the text is degenerate (it is blank)."
        return len(self.text.strip()) > 0                  # Degenerate text  (if blank, it can not be selected)


#    def thanClone(self):
#        "Makes a geometric clone of itself."
#        el = ThanText()
#        el.thanSet(self.text, self.cc, self.size, self.theta)
#        return el


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.cc = self.thanRotateXy(self.cc)
        self.theta += self.rotPhi
        self.theta %= PI2
        self.setBoundBoxRect(self.cc[0], self.cc[1], self.w1, self.h1, self.theta)


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        cbig = list(self.cc)
        cbig[0] += self.w1*cos(self.theta)
        cbig[1] += self.w1*sin(self.theta)
        cbig = self.thanMirrorXy(cbig)
        self.cc = self.thanMirrorXy(self.cc)

        self.theta = atan2(cbig[1]-self.cc[1], cbig[0]-self.cc[0]) % PI2
        self.setBoundBoxRect(self.cc[0], self.cc[1], self.w1, self.h1, self.theta)


    def thanPointMir(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        cbig = list(self.cc)
        cbig[0] += self.w1*cos(self.theta)
        cbig[1] += self.w1*sin(self.theta)
        cbig = self.thanPointMirXy(cbig)
        self.cc = self.thanPointMirXy(self.cc)

        self.theta = atan2(cbig[1]-self.cc[1], cbig[0]-self.cc[0]) % PI2
        self.setBoundBoxRect(self.cc[0], self.cc[1], self.w1, self.h1, self.theta)


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        self.cc = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.cc, cs)]  #works for python2,3
        self.size *= scale
        self.w1 *= scale
        self.h1 *= scale
        cscs = [cs[0], cs[1], cs[0], cs[1]]
        self.thanXymm[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.thanXymm, cscs)]  #works for python2,3


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        self.cc = [cc1+dd1 for (cc1,dd1) in zip(self.cc, dc)]  #works for python2,3
        dcdc = [dc[0], dc[1], dc[0], dc[1]]
        self.thanXymm[:] = [cc1+dd1 for (cc1,dd1) in zip(self.thanXymm, dcdc)]  #works for python2,3


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type in otypes nearest to xcu, ycu."
        if "ena" not in otypes: return None            # Object snap is disabled
        if "end" in otypes:
            return fabs(self.cc[0]-ccu[0])+fabs(self.cc[1]-ccu[1]), "end", self.cc
        return None


    def thanExplode(self, than=None):
        """Transform the text to a set of lines

        thanExplode(), which is inherited by ThanElement, does not explode text
        to lines; it does nothing (in the future, it will explode a multiline
        text to single line texts). This is in order to
        avoid user confusion, who are acquainted with other leading Cad.
        """
        if than is None: return True               # Explode IS implemented
        return self.__explode(than)
    def __explode(self, than):
        "Transform the line to a set of smaller 2-point lines; do the job as a generator."
        lines = than.font.than2lines(self.cc[0], self.cc[1], self.h1, self.text, self.theta, mirrory=True)
        for lin in lines:
            cp = []
            for x, y in lin:
                c1 = list(self.cc)
                c1[:2] = x, y
                cp.append(c1)
            e1 = ThanLine()
            e1.thanSet(cp)
            if e1.thanIsNormal(): yield e1


    def thanLength(self):
        """Returns the "length" of the text."""
        return max((self.w1, self.h1))

    def thanArea(self):
        "Returns the area of the bounding rectangle of the text."
        return self.w1*self.h1


    def thanTkGet(self, proj):
        "Gets the attributes of the text interactively from a window."
        un = proj[1].thanUnits
        size = proj[2].thanGudGetPosFloat(T["Text Size: "], 10.00)
        if size == Canc: return Canc                     # text cancelled
        st = "%s(%s): " % (T["Rotation angle"], un.anglunit)
        theta = proj[2].thanGudGetFloat(st, 0.00)
        if theta == Canc: return Canc                     # text cancelled
        c1 = proj[2].thanGudGetPoint(T["Text location: "])
        if c1 == Canc: return Canc                       # Text cancelled
        text = proj[2].thanGudGetText(T["Text to be drawn: "], "")
        if text == Canc: return Canc                     # text cancelled
        self.thanSet(text, c1, size, un.unit2rad(theta))
        return True                                      # Text OK

    _canvasfonts = {}
    _canvasfamilyfactor = {}
    def thanTkDraw1(self, than, rectangle=False):
        "Draws rotated text in ThanCad line font."
        if self.tempSize:  # The GUI is active: time to compute the dimension of the text accurately
            self.w1, self.h1 = than.font.thanCalcSizexy(self.text, self.size)
            self.tempSize = False
            self.setBoundBoxRect(self.cc[0], self.cc[1], self.w1, self.h1, self.theta)
#           FIXME: When user changes font of a layer, then all texts of this layer should have tempsize=True
        x1, y1 = than.ct.global2Local(self.cc[0], self.cc[1])
        w, h = than.ct.global2LocalRel(self.w1, -self.h1)    # Ensure h>0 (local y-axis is positive downwards)
        if h < 4 or rectangle:                               # Size too small to be seen; draw rectangle instead
            tags = self.thanTags + ("nocomp",)
            h = -h
            cost = cos(-self.theta)        # Opposite y-axis changes the sign of the angle
            sint = sin(-self.theta)
            xb = x1 + w*cost
            yb = y1 + w*sint
            g2l = than.ct.global2Local
            wpList = [ (x1, y1),
                       (xb, yb),
                       (xb - h*sint, yb + h*cost),
                       (x1 - h*sint, y1 + h*cost),
                     ]
            than.dc.create_polygon(wpList, outline=than.outline, fill="", tags=tags)
        elif self.theta == 0.0 and False:                                #Use canvas fonts for speed
            #bounds = than.dc.bbox(id)  # returns a tuple like (x1, y1, x2, y2)
            #width = bounds[2] - bounds[0]
            #height = bounds[3] - bounds[1]
            #family = "Times New Roman"
            #family = "Arial"
            family = "Liberation Sans"
            #family = "Liberation Mono"
            #family = "Carlito"
            #family = "Courier new"
            #family = "Comic Sans MS"
            #family = "URW Chancery L"
            if family not in self._canvasfamilyfactor:
                fo = Font(family=family, size=-100)
                fm = fo.metrics(window=than.dc)
                #print(fm)
                w=fo.measure("w", displayof=than.dc)
                #print(w, fo.measure("A", displayof=than.dc), fo.measure("O", displayof=than.dc))
                #print(fo.actual(displayof=than.dc))
                self._canvasfamilyfactor[family] = 100/w
                    #i = than.dc.create_text(0, 0, text=self.text, anchor="sw", font=fo)
                    #than.dc.update()
                    #x1, y1, x2, y2 = than.dc.bbox(i)
                    #print("bbox=", x2-x1, y2-y1)
                    #than.dc.delete(i)
                    #than.dc.update()
                #self._canvasfamilyfactor[family] = fm['ascent'] / (fm['ascent']-fm['descent'])
                #self._canvasfamilyfactor[family] = (fm['linespace']+fm['descent']) / (fm['ascent'])
                #self._canvasfamilyfactor[family] = (fm['linespace']) / (fm['ascent']-(100-fm['ascent']))
                #self._canvasfamilyfactor[family] = (fm['linespace']) / (fm['ascent']*fm['ascent']/100)
                #self._canvasfamilyfactor[family] = (100) / (fm['ascent']*fm['ascent']/100)
                #self._canvasfamilyfactor[family] = 100 / (fm['ascent']-fm['descent'])

                #self._canvasfamilyfactor[family] = fm['linespace'] / (fm['ascent']*0.85)
                #self._canvasfamilyfactor[family] = fm['linespace'] / (fm['ascent']-fm['descent']*0.45)
            #hp = int(h*1.38+0.5)        #Canvas bug?
            #hp = int(h+0.5)
            hp = int(h*self._canvasfamilyfactor[family]+0.5)        #Canvas bug?
            #print("text h=", h, "hp=", hp)
            if hp not in self._canvasfonts:
                #self._canvasfonts[hp] = Font(family=thancadconf.thanFontfamilymono, size=-hp)
                self._canvasfonts[hp] = Font(family=family, size=-hp)
            tags = self.thanTags + ("nocomp",)
            than.dc.create_text(x1, y1, text=self.text, anchor="sw", angle=self.theta/pi*180,
                font=self._canvasfonts[hp], fill=than.outline, tags=tags)
        else:      # Draw text - ThanFont does not distinguish between theta==0 and theta!=zero
            than.font.thanTkPaint(than, x1, y1, h, self.text, self.theta, self.thanTags)


    def thanExpDxf(self, fDxf):
        "Exports the text to dxf file."
        fDxf.thanDxfPlotSymbol3(self.cc[0], self.cc[1], self.cc[2], self.size, self.text, self.theta/pi*180.0)


    def thanExpThc1(self, fw):
        "Save the aligned dimension in thc format."
        f = fw.formFloat
        fw.writeNode(self.cc)
        fw.writeln(f % self.size)
        fw.writeln(f % self.theta)
        fw.writeTextln(self.text)


    def thanImpThc1(self, fr, ver):
        "Read the aligned dimension from thc format."
        c1 = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        size  = float(next(fr))         #May raise ValueError, StopIteration
        theta = float(next(fr))         #May raise ValueError, StopIteration
        text = fr.readTextln()           #May raise StopIteration
        print("ThanText: text=", text)
        self.thanSet(text, c1, size, theta)


    def thanExpPilold(self, than):
        "Exports the text to a PIL raster image, using the pil text mechanism and fonts."
        x1, y1 = than.ct.global2Locali(self.x1, self.y1)
        than.dc.text((x1, y1), self.text, font=than.font, fill=than.outline)


    def thanExpPilchaos(self, than):
        "Exports rotated text (in ThanCad line font) into a PIL raster image; due to PIL bug the width of the lines are chaotic."
        xa, ya = than.ct.global2Local(self.cc[0], self.cc[1])
        w, h = than.ct.global2LocalRel(self.w1, -self.h1)     # Ensure h>0  (local y-axis is positive downwards)
        if h < 1: return                                      # Size too small to be seen; draw rectangle instead
        than.thanFont.thanPilPaint(than, xa, ya, h, self.text, self.theta)


    def thanExpPil(self, than):
        "Exports rotated text (in ThanCad line font) into a PIL raster image; works around PIL chaotic width bug."
        xa, ya = self.cc[0], self.cc[1]
        h = self.h1
        lines = than.font.than2lines(xa, ya, h, self.text, self.theta, mirrory=True)
        e = ThanLine()
        for cp in lines:
            e.thanSet([(c[0], c[1], 0) for c in cp])
            e.thanExpPil(than)


    def thanPlotPdf(self, than):
        "Plots rotated text (in ThanCad line font) into a PDF file."
        xa, ya = than.ct.global2Local(self.cc[0], self.cc[1])
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
            print(p)
            than.dc.stroke(p)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property.
        Like circle and arc, the size of the font is changes (in case that the
        transformation has scale."""
        cc = list(self.cc)
        cc[:3] = fun(cc[:3])

        th = self.theta
        cr = list(self.cc)
        s = min(self.size, 1.0)                   #Avoid zero size
        cr[0] += s * cos(th)
        cr[1] += s * sin(th)
        cr = fun(cr[:3])
        theta = atan2(cr[1]-cc[1], cr[0]-cc[0])   #Note that python ensures than atan2(0,0) = 0!!!

        th = theta + 0.5*pi
        cr = list(self.cc)
        cr[0] += self.size*cos(th)
        cr[1] += self.size*sin(th)
        cr = fun(cr[:3])
        size = hypot(cr[1]-cc[1], cr[0]-cc[0])

        self.thanSet(self.text, cc, size, theta)


    def thanList(self, than):
        "Shows information about the text element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        t = ('%s"%s"' % (T["Text: "], thanUnicode(self.text)),
             "%s: %s" % (T["Insertion point"], than.strcoo(self.cc)),
             T["Size: %s    Angle: %s\n"] % (than.strdis(self.size), than.strdir(self.theta)),
            )
        than.write("\n".join(t))
