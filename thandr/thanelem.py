##############################################################################
# ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2013 Thanasis Stamos, March 25, 2013
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
ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers

This module defines the generic ThanCad element. It can be also used as a null
element - this is NOT an asbtract class.
The class defines functionality to speed up the rotate operation.
"""

from math import pi, cos, sin
import copy
from thantrans import T


class ThanElement:
    """Base class for thancad's objects.

    This class of elements may ne used whenever a dummy, or Null element
    (see python recipies), is needed. The element accepts usual commands through
    the routine but does nothing.
    """
    thanTkCompound = 1         # The number of Tkinter objects that make the element. 1=No compound object
    thanElementName = "GENERIC"    # Name of the element's class

    def __init__ (self):
        "Make the elements with invalid thanTags invalid handle."
        self.thanUntag()

#---Dummy operations

    def thanSet(self, *args, **kw):
        "Sets the (geometric) properties of the element."
        pass


    def thanIsNormal():
        "Checks if element shape is OK (i.e. it is not degenerate."
        return False


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        pass


    def thanMirror(self):
        "Mirror element; mirror line is defined by point c1 and unit vector t."
        pass


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        pass


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        pass


    def thanReverse(self):
        "Reverses the sequence of nodes, or the spin for circles and arcs."
        pass


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type otype nearest to xcu, ycu."
        return None


    def thanPntNearest(self, ccu):
        "Finds the nearest point of this line to a point."
        return None


    def thanBreak(self, c1=None, c2=None):
        "Breaks an element to 2 pieces."
        return False       # Break is NOT implemented


    def thanExplode(self, than=None):
        "Transform an element to a set of smaller elements."
        return False       # Explode is NOT implemented/possible


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset element by distance dis; to the right if dis>0 and to the left otherwise."
        return False       # Offset is NOT implemented


    def thanLength(self):
        "Returns the length of the element."
        return 0.0


    def thanArea(self):
        "Returns the area of the element."
        return 0.0


    def thanSpin(self):
        """Returns the spin of the element.

        Spin 0 means that spin is undefined for the element.
        Spin 1 is counterclockwise
        Spin -1 is clockwise."""
        return 0


    def thanTkGet(self, proj):
        "Gets the attributes of the element interactively from a window."
        pass


    def thanTkDraw1(self, than):
        "Draws the element to a Tk Canvas; does not check if element too small to display."
        pass


    def thanExpDxf(self, fDxf):
        "Exports the element to dxf file."
        pass


    def thanExpSyk(self, than):
        "Exports the element to syk file."
        pass


    def thanExpBrk(self, than):
        "Exports the element to brk file."
        pass


    def thanExpSyn(self, than):
        "Exports the element to syn file."
        pass


    def thanExpPil(self, than):
        "Exports the element to a PIL raster image."
        pass


    def thanPlotPdf(self, than):
        "Plots the line to a pdf file."
        pass


    def thanList(self, than):
        "Shows information about the generic element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        than.write("%s: %s" % (T["Insertion point"], than.strcoo(self.getInspnt())))


    def thanExpThc1 (self, fw):
        "Save the element in thc format; attributes other than the common."
        raise ValueError, "Method thanExpThc1 must be overriden"


    def thanImpThc1 (self, fw):
        "Read the element from thc format; attributes other than the common."
        raise ValueError, "Method thanExpThc1 must be overriden"


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        pass

#---Reasonable default behavior of elements


    def thanTkDraw(self, than):
        "Draws the element to a Tk Canvas; if element too small it draws a rectangle."
        length, _ = than.ct.global2LocalRel(self.thanLength(), 0.0)
#        if length > 0.6: return
        if length > 1.6:
            self.thanTkDraw1(than)
        else:
            ca = self.getInspnt()
            xa, ya = than.ct.global2Local(ca[0], ca[1])
            temp = than.dc.create_rectangle(xa, ya, xa+1, ya+1, outline="green", tags=self.thanTags)


    def thanClone(self):
        "Makes a copy of itself; the cloned copy has even same thanTags and handle."
        el = copy.deepcopy(self)
        return el


    def thanUntag(self):
        "Make the thanTags and handle invalid; probably after a .thanClone() in order to make a clone with different identity."
        self.handle = -1                                   # This is set by thanElementAdd
        self.thanTags = ("e-1",)                           # This is set by the appropriate (Tk) GUI


    def thanInbox(self, xymm):
        "Checks if element may (partialy) be in box xymm."
        if self.thanXymm[0] > xymm[2]: return False
        if self.thanXymm[1] > xymm[3]: return False
        if self.thanXymm[2] < xymm[0]: return False
        if self.thanXymm[3] < xymm[1]: return False
        return True


    def thanInarea(self, xymm):
        "Checks if element may (partialy) be in area xymm (which may have None)."
        if xymm[2] == None or self.thanXymm[0] > xymm[2]: return False
        if xymm[1] == None or self.thanXymm[1] > xymm[3]: return False
        if xymm[2] == None or self.thanXymm[2] < xymm[0]: return False
        if xymm[3] == None or self.thanXymm[3] < xymm[1]: return False
        return True


    def getBoundBox(self):
        return tuple(self.thanXymm)


    def setBoundBox (self, xymm):
        "Sets the boundary box of the element."
        self.thanXymm = list(xymm)


    def updateBoundBox (self, xymm):
        "Updates bound box so that it contains xymm."
        a = self.thanXymm
        if xymm[0] < a[0]: a[0] = xymm[0]
        if xymm[1] < a[1]: a[1] = xymm[1]
        if xymm[2] > a[2]: a[2] = xymm[2]
        if xymm[3] > a[3]: a[3] = xymm[3]


    def setBoundBoxT (self, xymm):
        "Sets the boundary box of the element with test."
        a = list(xymm)
        if a[0] > a[2]: a[0], a[2] = a[2], a[0]
        if a[1] > a[3]: a[1], a[3] = a[3], a[1]
        self.thanXymm = a


    def setBoundBoxRect(self, xa, ya, w, h, theta, center=False):
        "Finds the boundary box of a rectangle."
        t = theta
        cost = cos(t)
        sint = sin(t)
        if center:     #This means xa is the center of the rectangle
            xa -= (w*cost - h*sint)*0.5
            ya -= (w*sint + h*cost)*0.5
        xb = xa + w*cost
        yb = ya + w*sint
        xc = xb - h*sint
        yc = yb + h*cost
        xd = xa - h*sint
        yd = ya + h*cost

        self.thanXymm = [ min(xa, xb, xc, xd),
                          min(ya, yb, yc, yd),
                          max(xa, xb, xc, xd),
                          max(ya, yb, yc, yd)
                        ]

    def getInspnt(self):
        "Returns the insertion point of the element."
        return list(self.cc)


    def thanChelev(self, z):
        "Set constant elevation of z."
        self.cc[2] = z


    def thanChelevn(self, celev):
        "Set constant elevation of z and higher dimensions."
        self.cc[2:] = celev


    def thanExpThc(self, fw, layname):
        "Save the element in thc format; common attributes."
        fw.writeBeg(self.thanElementName)
        fw.pushInd()
        fw.writeTextln(layname)
        fw.writeln("%d" % self.handle)
        self.thanExpThc1(fw)
        fw.popInd()
        fw.writeEnd(self.thanElementName)


    def thanImpThc(self, fr, ver):
        "Read the element from thc format; common attributes."
        fr.readBeg(self.thanElementName) #May raise ValueError, StopIteration
        layname = fr.readTextln()        #May raise StopIteration, ValueError
        self.handle = int(fr.next())     #May raise ValueError, StopIteration
        self.thanImpThc1(fr, ver)
        fr.readEnd(self.thanElementName) #May raise ValueError, StopIteration
        return layname


#---Rotate operations (for all elements)

    @classmethod
    def thanRotateSet (clas, cc, phi):
        clas.rotPhi = phi
        clas.cosf = cos(clas.rotPhi)
        clas.sinf = sin(clas.rotPhi)
        clas.cc = cc


    @classmethod
    def thanRotateXy(clas, ca):
        xa = ca[0] - clas.cc[0]
        ya = ca[1] - clas.cc[1]
        ct = list(ca)
        ct[0] = clas.cc[0] + xa*clas.cosf - ya*clas.sinf
        ct[1] = clas.cc[1] + xa*clas.sinf + ya*clas.cosf
        return ct


    @classmethod
    def thanRotateXyn(clas, cc):
        xc = clas.cc[0]
        yc = clas.cc[1]
        cosf = clas.cosf
        sinf = clas.sinf
        for ct in cc:
            xa = ct[0] - xc
            ya = ct[1] - yc
            xt = xa*cosf - ya*sinf
            yt = xa*sinf + ya*cosf
            ct[0] = xt + xc
            ct[1] = yt + yc


    @classmethod
    def thanRotateSetp(clas, xc, yc, phi):
        clas.rotPhip = phi
        clas.cosfp = cos(clas.rotPhip)
        clas.sinfp = sin(clas.rotPhip)
        clas.xcp = xc
        clas.ycp = yc


    @classmethod
    def thanRotateXypn2(clas, cc):
        xc = clas.xcp
        yc = clas.ycp
        cosf = clas.cosfp
        sinf = clas.sinfp
        for i in xrange(0, len(cc), 2):
            xa = cc[i] - xc
            ya = cc[i+1] - yc
            xt = xa*cosf - ya*sinf
            yt = xa*sinf + ya*cosf
            cc[i]   = xt + xc
            cc[i+1] = yt + yc


    @classmethod
    def thanMirrorSet(clas, cc, t):
        "Set mirror parameters for world coordinates."
        clas.cosf = t[0]
        clas.sinf = t[1]
        clas.cc = cc


    @classmethod
    def thanMirrorXy(clas, ca):
        "Compute mirror for 1 point of world coordinates."
        xc = clas.cc[0]
        yc = clas.cc[1]
        cosf = clas.cosf
        sinf = clas.sinf
        dis = (ca[0] - xc)*cosf + (ca[1] - yc)*sinf
        xa = xc + dis*cosf
        ya = yc + dis*sinf
        dx = ca[0] - xa
        dy = ca[1] - ya
        ct = list(ca)
        ct[0] = xa - dx
        ct[1] = ya - dy
        return ct


    @classmethod
    def thanMirrorXyn(clas, cc):
        "Compute mirror for many points of world coordinates in-place."
        xc = clas.cc[0]
        yc = clas.cc[1]
        cosf = clas.cosf
        sinf = clas.sinf
        for ct in cc:
            dis = (ct[0] - xc)*cosf + (ct[1] - yc)*sinf
            xa = xc + dis*cosf
            ya = yc + dis*sinf
            dx = ct[0] - xa
            dy = ct[1] - ya
            ct[0] = xa - dx
            ct[1] = ya - dy


    @classmethod
    def thanMirrorSetp(clas, xc, yc, t):
        "Set mirror parameters for pixel coordinates."
        clas.cosfp = t[0]
        clas.sinfp = t[1]
        clas.xcp = xc
        clas.ycp = yc


    @classmethod
    def thanMirrorXypn2(clas, cn):
        "Compute mirror for many points of pixel coordinates in-place."
        xc = clas.xcp
        yc = clas.ycp
        cosf = clas.cosfp
        sinf = clas.sinfp
        for i in xrange(0, len(cn), 2):
            ca = cn[i], cn[i+1]
            dis = (ca[0] - xc)*cosf + (ca[1] - yc)*sinf
            xa = xc + dis*cosf
            ya = yc + dis*sinf
            dx = ca[0] - xa
            dy = ca[1] - ya
            cn[i]   = xa - dx
            cn[i+1] = ya - dy


#MODULE LEVEL CODE. IT IS EXECUTED ONLY ONCE

if __name__ == "__main__":
    print __doc__
