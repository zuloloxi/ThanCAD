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

This module defines the generic ThanCad element. It can be also used as a null
element - this is NOT an asbtract class.
The class defines functionality to speed up the rotate operation.
"""

from math import cos, sin
import copy, json
import p_ggen
from thantrans import T


class ThanElement:
    """Base class for thancad's objects.

    This class of elements may be used whenever a dummy, or Null element
    (see python recipes), is needed. The element accepts usual commands through
    the methods but does nothing.
    """
    thanTkCompound = 1         # The number of Tkinter objects that make the element. 1=No compound object
    thanElementName = "GENERIC"    # Name of the element's class

    def __init__ (self):
        "Make the elements with invalid thanTags invalid handle."
        self.thanCargo = None   #holds dict with optional,user defined, attributes, or None if no attributes.
        self.thanUntag()

#---Dummy operations

    def thanSet(self, *args, **kw):
        "Sets the (geometric) properties of the element."
        pass


    def thanIsNormal(self):
        "Checks if element shape is OK (i.e. it is not degenerate)."
        return False


    def than2Line(self, dt=0.0, ta=None, tb=None):
        """Represent the element with straight line segments.

        If we have a curved element (for example a circle), dt is the size of
        the line segments to approximate the curve. Usually it is the size of
        20 pixels in user data units.
        The implementation of than2line() may use less size if needed.
        If dt is zero or negative, then the implementation of than2line may
        choose a default size.
        Specifically if dt<1, elements which smooth out a polyline
        (for example spline, bezier, Bspline, NURB) return the nodes of the
        original line (which is smoothed out).
        For optimization reasons, than2line() may represent part of the element
        with line segments. The implementations are free to ignore ta and tb.
        ta is the parameter which corresponds to the beginning of the part,
        and tb is the parameter which corresponds to the end of the part.
        For each element the parameter t may be different. For example t is
        angle for circles, ellipses and arcs, and t is the distance along the
        curve from the beginning of the curve for splines.
        than2line() returns a list of points which is the line segment
        representation of the lements and a list of parametes which correspond
        to the points.
        """
        if dt is None: return False       #than2Line IS NOT implemented
        assert False, "Since if dt is None we answer with False, the code should not reach here."


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        pass


    def thanMirror(self):
        "Mirror element; mirror line is defined by point c1 and unit vector t."
        pass

    def thanPointMir(self):
        "Mirror element with respect to apoint; mirror point is defined by point c1."
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
        "Return a point of type in otypes nearest to xcu, ycu."
        return None


    def thanPntNearest(self, ccu):
        "Finds the nearest point of this line to a point."
        return None

    def thanTrim(self, ct, cnear):
        """Breaks the element into multiple segments and deletes the segment nearest to cnear.

        "If self.thanBreak() returns True, then this function must me implemented."""
        if self.thanBreak():
            assert False, "Since self.thanBreak() returns True, this function must me implemented."
        assert False, "Since self.thanBreak() returns True, the code should not reach here."

    def thanBreak(self, c1=None, c2=None):
        "Breaks an element to 2 pieces."
        if c1 is None: return False       # Break is NOT implemented/possible
        assert False, "Since if dt is None we answer with False, the code should not reach here."


    def thanExplode(self, than=None):
        "Transform an element to a set of smaller elements."
        if than is None: return False     # Explode IS NOT implemented/possible
        assert False, "Since if than is None we answer with False, the code should not reach here."


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset element by distance dis; to the right if dis>0 and to the left otherwise."
        if through==None and distance==None: return False  # Offset IS NOT implemented/possible
        assert False, "Since if through&distance is None we answer with False, the code should not reach here."


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

    def thanExpKml(self, than):
        "Exports the element to Google .kml file."
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
        than.write("    %s %s\n" % (T["Layer:"], p_ggen.thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        than.write("%s: %s" % (T["Insertion point"], than.strcoo(self.getInspnt())))


    def thanExpThc1 (self, fw):
        "Save the element in thc format; attributes other than the common."
        raise ValueError("Method thanExpThc1 must be overridden")


    def thanImpThc1 (self, fw):
        "Read the element from thc format; attributes other than the common."
        raise ValueError("Method thanExpThc1 must be overridden")


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property.
        If the transformation is rigid (move, rotate, scale) the element should not change
        it shape. Otherwise the best fit."""
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
        "Checks if element may (partially) be in box xymm."
        if self.thanXymm[0] > xymm[2]: return False
        if self.thanXymm[1] > xymm[3]: return False
        if self.thanXymm[2] < xymm[0]: return False
        if self.thanXymm[3] < xymm[1]: return False
        return True


    def thanInarea(self, xymm):
        "Checks if element may (partially) be in area xymm (which may have None)."
        if xymm[2] is not None and self.thanXymm[0] > xymm[2]: return False
        if xymm[3] is not None and self.thanXymm[1] > xymm[3]: return False
        if xymm[0] is not None and self.thanXymm[2] < xymm[0]: return False
        if xymm[1] is not None and self.thanXymm[3] < xymm[1]: return False
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


    def thanIsClosed(self):
        "Returns True if the element is closed (circle, ellipse, closed line)."
        return False


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
        self.thanWriteCargo(fw)
        fw.popInd()
        fw.writeEnd(self.thanElementName)


    def thanWriteCargo(self, fw):
        "Write extra attrributes of the element - do not fail on errors."
        fw.writeBeg("CARGO")
        fw.pushInd()
        for dline in self.__cargo2string(fw):
            fw.writeln(dline)
        fw.popInd()
        fw.writeEnd("CARGO")


    def __cargo2string(self, fw):
        "Write extra attributes of the element to string - do not fail on errors."
        print("__cargo2string(): self.thanCargo=", self.thanCargo)
        if self.thanCargo is None or len(self.thanCargo) == 0: return []
        try:
            t = json.dumps(self.thanCargo, indent=4)  #may raise TypeError
        except TypeError as e:
            fw.prter("Error: illegal user defined element attributes:\n{}\nAttribytes are ignored".format(e))
            return []
        dlines = t.split("\n")
        if dlines[-1].strip() == "": del dlines[-1]    #erase last blank line
        return dlines


    def thanImpThc(self, fr, ver):
        "Read the element from thc format; common attributes."
        fr.readBeg(self.thanElementName) #May raise ValueError, StopIteration
        layname = fr.readTextln()        #May raise StopIteration, ValueError
        self.handle = int(next(fr))      #May raise ValueError, StopIteration
        self.thanImpThc1(fr, ver)
        self.thanCargo = self.thanReadCargo(fr, ver)
        fr.readEnd(self.thanElementName) #May raise ValueError, StopIteration
        return layname


    def thanReadCargo(self, fr, ver):
        "Read extra attrributes of the element."
        if ver < (0,6,0): return None   #previous versions did not have attributes
        fr.readBeg("CARGO") #May raise ValueError, StopIteration
        jsondata = []
        while True:
            dline = next(fr)
            name = dline.strip()[1:-1]
            if name == "/CARGO": break
            jsondata.append(dline)
        fr.unread()
        fr.readEnd("CARGO") #May raise ValueError, StopIteration

        if len(jsondata) == 0: return None  #element does not have any user defined attributes
        jsondata = "".join(jsondata)   #jsondata already has a \n at the end of the line
        atts = json.loads(jsondata)  #May raise JSONDecodeError which is a subclass of ValueError
        return atts

#---Rotate operations (for all elements)

    @classmethod
    def thanRotateSet (clas, cc, phi):
        "Set center and rotation angle in radians."
        clas.rotPhi = phi
        clas.cosf = cos(clas.rotPhi)
        clas.sinf = sin(clas.rotPhi)
        clas.cc = cc


    @classmethod
    def thanRotateXy(clas, ca):
        "Rotate a point."
        xa = ca[0] - clas.cc[0]
        ya = ca[1] - clas.cc[1]
        ct = list(ca)
        ct[0] = clas.cc[0] + xa*clas.cosf - ya*clas.sinf
        ct[1] = clas.cc[1] + xa*clas.sinf + ya*clas.cosf
        return ct


    @classmethod
    def thanRotateXyn(clas, cc):
        "Rotate many points in place."
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
        for i in range(0, len(cc), 2):
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
        for i in range(0, len(cn), 2):
            ca = cn[i], cn[i+1]
            dis = (ca[0] - xc)*cosf + (ca[1] - yc)*sinf
            xa = xc + dis*cosf
            ya = yc + dis*sinf
            dx = ca[0] - xa
            dy = ca[1] - ya
            cn[i]   = xa - dx
            cn[i+1] = ya - dy


    @classmethod
    def thanPointMirSet(clas, cc):
        "Set mirror parameters for world coordinates."
        clas.cc = cc


    @classmethod
    def thanPointMirXy(clas, ca):
        "Compute mirror for 1 point of world coordinates."
        xc = clas.cc[0]
        yc = clas.cc[1]
        dx = ca[0] - xc
        dy = ca[1] - yc
        ct = list(ca)
        ct[0] = xc - dx
        ct[1] = yc - dy
        return ct


    @classmethod
    def thanPointMirXyn(clas, cc):
        "Compute mirror for many points of world coordinates in-place."
        xc = clas.cc[0]
        yc = clas.cc[1]
        for ct in cc:
            dx = ct[0] - xc
            dy = ct[1] - yc
            ct[0] = xc - dx
            ct[1] = yc - dy
