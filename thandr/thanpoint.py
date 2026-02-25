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

This module defines the point element.
"""

from math import fabs, hypot
import p_ggen
from p_gmath import thanNearx
from thantrans import T
from .thanelem import ThanElement
from .thantext import ThanText
try: import pyx
except ImportError: pass

############################################################################
############################################################################

class ThanPoint(ThanElement):
    "A point."
    thanTkCompound = 100        # The number of Tkinter objects that make the element. 100=compound (Many lines etc.)
    thanElementName = "POINT"   # Name of the element's class
    psize = 10                  # Pixel size of the point

    def thanSet (self, cc):
        "Sets the coordinates of the point."
        self.cc = list(cc)
        self.wsize = self.psize                             #Working size in world coordinates
        self._setbbox()
#        self.thanTags = ()                                 # thanTags is initialised in ThanElement


    def _setbbox(self):
        "Set the boundary box of the point with current (world) size."
        r = self.wsize * 0.5
        cc = self.cc
        self.setBoundBox([cc[0]-r, cc[1]-r, cc[0]+r, cc[1]+r])


    def thanIsNormal(self):
        "Returns False if the point is degenerate (never)."
        return True                                        # There is no degenerate point


#    def thanClone(self):
#        "Makes a geometric clone of itself."
#        el = ThanPoint()
#        el.thanSet(self.cc)
#        return el


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.cc = self.thanRotateXy(self.cc)
        self._setbbox()


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        self.cc = self.thanMirrorXy(self.cc)
        self._setbbox()


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        self.cc = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.cc, cs)]  #works for python2,3
        self._setbbox()


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        self.cc = [cc1+dd1 for (cc1,dd1) in zip(self.cc, dc)]  #works for python2,3
        self._setbbox()


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type in otypes nearest to xcu, ycu."
        if "ena" not in otypes: return None            # Object snap is disabled
        if "nod" in otypes:
            return fabs(self.cc[0]-ccu[0])+fabs(self.cc[1]-ccu[1]), "nod", self.cc
        if "nea" in otypes:
            return fabs(self.cc[0]-ccu[0])+fabs(self.cc[1]-ccu[1]), "nea", self.cc
        return None


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset point by distance dis or through point."
        if through==None and distance==None: return True  # Offset is implemented
        if through:
            ccoff = list(sidepoint)
        else:
            dx = sidepoint[0]-self.cc[0]
            dy = sidepoint[1]-self.cc[1]
            dis = hypot(dx, dy)
            if thanNearx(dis, 0.0): return None  # Invalid point
            ccoff = list(self.cc)
            ccoff[0] += dx*distance/dis
            ccoff[1] += dy*distance/dis
        e = self.thanClone()             # This makes thanOffset valid..
        e.cc = ccoff                     # ..for subclasses too
        e.thanUntag()                    # Make cloned copy to have distict (and invalid) identity
        return e


    def thanTkGet(self, proj):
        "Gets the attributes of the point interactively from a window."
        raise AttributeError("Use thancom.thancomdraw.thanTkDrawPoint() instead.")


    def thanTkDraw1(self, than):
        "Draws the point on the window."
        xa, ya = than.ct.global2Local(self.cc[0], self.cc[1])
        dc = than.dc
#        print "point thanTkDraw1(): stereo = %s stereoon=%s" % (than.stereo, dc.thanStereoOn)
        if than.stereo is not None and dc.thanStereoOn:
            size = 3
            iparal = than.stereo.dpix(self.cc[2])
            dc.pointpair(xa, ya, size, iparal, tags=self.thanTags)
            self.wsize, _ = than.ct.local2GlobalRel(size, 0.0)    #Recalculate the size in world coordinates
        else:
            w = than.tkThick
            temp = than.thanPoints["chi"](than.dc, xa, ya, self.psize,
                color=than.outline, fill=than.fill, width=w, tags=self.thanTags)
            #than.dc.create_rectangle(xa, ya, xa+1, ya+1, outline=than.outline, fill=than.fill, width=w, tags=self.thanTags)
            self.wsize, _ = than.ct.local2GlobalRel(self.psize, 0.0)    #Recalculate the size in world coordinates
        self._setbbox()

    thanTkDraw = thanTkDraw1     #A point will always be visible, so it does not need the visibility mechanism

    def thanExpDxf(self, fDxf):
        "Exports the point to dxf file."
        fDxf.thanDxfPlotPoint3(self.cc[0], self.cc[1], self.cc[2])


    def thanExpSyn(self, than):
        "Exports the point to syn file."
        than.ibr += 1
        cp1 = self.cc
        than.write(than.form % (than.ibr, cp1[0], cp1[1], cp1[2]))


    def thanExpKml(self, than):
        "Exports the point to Google .kml file."
        than.ibr += 1
        cp1 = self.cc
        aa = than.form % (than.ibr,)
        than.kml.writePlacemark(aa, cp1, than.layname, desc="")


    def thanExpThc1(self, fw):
        "Save the point in thc format."
        fw.writeNode(self.cc)

    def thanImpThc1(self, fr, ver):
        "Read the point from thc format."
        c1 = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        self.thanSet(c1)

    def thanExpPil(self, than):
        "Exports the point to a PIL raster image."
        x1, y1 = than.ct.global2Locali(self.cc[0], self.cc[1])
        if than.rwidth <= 1.5:
            than.dc.point((x1, y1), fill=than.outline)
        else:
            i1, i2 = than.widtharc
            than.dc.rectangle((x1-i1, y1-i1, x1+i2, y1+i2), outline=than.outline, fill=than.fill)

        if 0:
            temp = than.thanPoints["chi"].thanPilPaint(than.dc, x1, y1, self.psize,
                color=than.outline, fill=than.fill, tags=self.thanTags)
            self.wsize, _ = than.ct.local2GlobalRel(self.psize, 0.0)    #Recalculate the size in world coordinates


    def thanPlotPdf(self, than):
        "Plots the point to a pdf file."
        g2l = than.ct.global2Local
        ca = g2l(self.cc[0], self.cc[1])
        p = pyx.path.circle(ca[0], ca[1], 0.05)
        than.dc.stroke(p)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        cc = self.cc
        cc[:3] = fun(cc[:3])
        self._setbbox()


    def thanList(self, than):
        "Shows information about the point element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], p_ggen.thanUnicode(than.laypath)))
        than.write("%s: %s\n" % (T["Insertion point"], than.strcoo(self.cc)))


class ThanPointNamed(ThanPoint):
    "A single point with attached (unique?) name plus valid attribute for the coordinates."
    thanElementName = "NAMEDPOINT"   # Name of the element's class


    def thanSet (self, c, name, validc=None):
        "Sets the coordinates and the name of the point."
        self.name = name.rstrip()
        self.height = str(c[2])    #The first call to thanTkDraw1 will set this to the correct number of digits
        self.plotname = self.plotheight = False #The first call to thanTkDraw1 will set these to the correct values
        n = len(c)
        if validc is None: validc = [True]*n
        else: validc = list(validc)
        while len(validc) < n: validc.append(True)     # Support n dimensional points
        self.validc = validc
        ThanPoint.thanSet(self, c)


    def _setbbox(self):
        "Find the boundary box of point plus name element plus z element."
        ThanPoint._setbbox(self)
        if self.plotname:
            elnam = self._crtext(self.name, 1, 1, self.wsize)
            self.updateBoundBox(elnam.getBoundBox())
        if self.plotheight:
            elh = self._crtext(self.height, 1, -1.3, self.wsize)
            self.updateBoundBox(elh.getBoundBox())


#    def thanClone(self):
#        "Makes a geometric clone of itself."
#        el = ThanPointNamed()
#        el.thanSet(self.cc, self.name, self.validc)
#        return el


    def thanTkGet(self, proj):
        "Gets the attributes of the point interactively from a window."
        raise AttributeError("Use thancom.thancomdraw.thanTkDrawPointNamed() instead.")


    def thanTkDraw1(self, than):
        "Draws the named point on the window."
        ThanPoint.thanTkDraw1(self, than)
#        print "named: thanTkDraw: than.pointPlotname=", than.pointPlotname
        self.plotname = than.pointPlotname
        if self.plotname:
            self._crtext(self.name, 1, 1, self.wsize).thanTkDraw(than)
        self.plotheight = than.pointPlotheight
        if self.plotheight:
            self.height = than.strdis(self.cc[2])
            self._crtext(self.height, 1, -1.3, self.wsize).thanTkDraw(than)

    thanTkDraw = thanTkDraw1     #A point will always be visible, so it does not need the visibility mechanism

    def _crtext(self, text, dx, dy, psize):
        "Creates a ThanCad text with the name/height of the point."
        t = ThanText()
        c1 = list(self.cc)
        c1[0] += dx*psize
        c1[1] += dy*psize
        t.thanSet(text, c1, psize, 0.0)
        t.thanTags = self.thanTags
        return t


    def thanExpDxf(self, fDxf):
        "Exports the point to dxf file."
        ThanPoint.thanExpDxf(self, fDxf)
        than = fDxf.than
        s = than.scale*than.pointsize
        fDxf.thanDxfSetLayer(than.layname+"_os")
        self._crtext(self.name, 1, 1, s).thanExpDxf(fDxf)
        fDxf.thanDxfSetLayer(than.layname+"_hs")
        self._crtext(self.height, 1, -1.3, s).thanExpDxf(fDxf)
        fDxf.thanDxfSetLayer(than.layname)


    def thanExpSyn(self, than):
        "Exports the named point to syn file."
        cp1 = self.cc
        than.write(than.formnam % (self.name, cp1[0], cp1[1], cp1[2]))


    def thanExpKml(self, than):
        "Exports the point to syn file."
        cp1 = self.cc
        aa = self.name
        than.kml.writePlacemark(aa, cp1, than.layname, desc="")


    def thanExpThc1(self, fw):
        "Save the named point in thc format."
        fw.writeNode(self.cc)
        fw.writeValid(self.validc)
        fw.writeTextln(self.name)

    def thanImpThc1(self, fr, ver):
        "Read the named point from thc format."
        cc = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        validc = fr.readValid()          #May raise ValueError, IndexError, StopIteration
        name = fr.readTextln()           #May raise StopIteration, ValueError
        self.thanSet(cc, name, validc)

    def thanExpPil(self, than):
        "Exports the point to a PIL raster image."
        ThanPoint.thanExpPil(self, than)
        self._crtext(self.name, 1, 1, self.psize).thanExpPil(than)


    def thanPlotPdf(self, than):
        "Plots the point to a pdf file."
        ThanPoint.thanPlotPdf(self, than)
        self._crtext(self.name, 1, 1, self.psize).thanPlotPdf(than)


    def thanList(self, than):
        "Shows information about the point element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], p_ggen.thanUnicode(than.laypath)))
        than.write("%s: %s\n" % (T["Insertion point"], than.strcoo(self.cc)))
        than.write("Name: %s\n" % self.name)
        than.write("%s: X=%r Y=%r Z=%r\n" % (T["Coordinate usability (for DTM, etc)"],
                                             self.validc[0], self.validc[1], self.validc[2]))


def test():
    print(__doc__)
    c = ThanPoint()
    c.thanSet((10.0, 20.0, 0.0))
    print("point=", c)
