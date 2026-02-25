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

This module defines the BIM column element. It is meant to be used in structural
engineering, and for the moment it is made of reinforced concrete.
"""
from math import atan2, hypot, pi, fabs
import copy
from p_ggen import Canc
from p_gmath import PI2, Rotator2d
from .thanline import ThanLine
from .thantext import ThanText
from .thanelem import ThanElement
from thantrans import T


class ThanBimColumn(ThanLine):
    "A stuctural column; the cross section is displayed."
    thanElementName = "BIMCOLUMN"    # Name of the element's class
    thanTkCompound = 100       # The number of tkinter objects that make the element. 100=compound (lines etc.)


    def thanSet (self, itype, name, cc, ds, theta, spin=1, cargo=None):
        """Sets the attributes of the line.

        itype: 13: rectangular section
        cc   : point: coordinates of the reference point of the column: currently
               the center of gravity of the section. The elevation of the point is
               elevation of the upper surface of the plate of the current storey.
        ds   : list or tuple of 6 elements: t3,t2,tf,tw,t2b,tfb
               t3: width of section parallel to y-axis (when theta==0)
               t2: width of section parallel to x-axis (when theta==0)
               tf: thickness of plate (parallel to y-axis)
               tw: thickness of trunk (parallel to x-axis)
               t2b: additional dimension parallel to x-axis
               tfb: additional thickness of plate or trunk (parallel to y-axis or x-axis)
        theta: rotation of the section with respect to x-axis. For the moment zero.
        cargo: dictionary with more attributes of the columns:
               tci: width of initial coating of the column
               tca: width of additional coating of the column
        """
        self.itype = itype
        self.name = name
        self.cc = list(cc)
        self.ds = list(ds)
        self.theta = theta
        self.spin = spin
        if cargo is None: self.thanCargo = {}
        self.thanCargo = copy.deepcopy(cargo)    #this also works if cargo==None

        self.__rect()   #This sets self.cp
        self.__boundBox()     #Sets the minimum enclosing unrotated rectangle
#        self.thanTags = ()                                 # thanTags is initialised in ThanElement


    def thanIsNormal(self):
        "Checks if element shape is OK (i.e. it is not degenerate)."
        bx = self.ds[1]
        by = self.ds[0]
        return bx>0.0 and by>0.0


    #def than2Line(self, dt=0.0, ta=None, tb=None):    #Inherited from ThanLine


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        super().thanRotate()   #calls ThanLine method: rotates self.cp and deals with boundbox
        self.cc = self.thanRotateXy(self.cc)
        self.theta += self.rotPhi
        self.theta %= PI2     # radians assumed


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        super().thanMirror()  #calls ThanLine method: mirrors self.cp and deals with boundbox
        self.cc = self.thanMirrorXy(self.cc)
        ca = self.thanMirrorXy(self.cp[0])
        cb = self.thanMirrorXy(self.cp[1])
        self.theta = atan2(ca[1]-cb[1], ca[0]-cb[0]) % PI2    #Note that Mirror reverses point sequence ca->cb to cb->ca
        self.__rect()       #This sets self.cp
        self.__boundBox()   #Sets the minimum enclosing unrotated rectangle


    def thanPointMir(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        super().thanPointMir()  #calls ThanLine method: point mirrors self.cp and deals with boundbox
        self.cc = self.thanPointMirXy(self.cc)
        self.theta = (self.theta + pi) % PI2


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        super().thanScale(cs, scale)  #calls ThanLine method: scales self.cp and deals with boundbox
        self.cc[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.cc, cs)]  #works for python2,3
        for i,temp in enumerate(self.ds): self.ds[i] = temp*scale
        self.thanCargo["tci"] *= scale   #Initial    coating thickness
        self.thanCargo["tca"] *= scale   #Additional coating thickness


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        super().thanMove(dc)  #calls ThanLine method: moves self.cp and deals with boundbox
        self.cc[:] = [cc1+dd1 for (cc1,dd1) in zip(self.cc, dc)]  #works for python2,3


    def thanReverse(self):
        "Reverse the spin of the bimcolumn."
        self.spin = -self.spin


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type in otypes nearest to xcu, ycu."
        ps1 = super().thanOsnap(proj, otypes, ccu, eother, cori) #calls ThanLine method: finds everything but center
        if ps1 is None: ps = []
        else:           ps = [ps1]
        if "cen" in otypes:
            ps.append((fabs(self.cc[0]-ccu[0])+fabs(self.cc[1]-ccu[1]), "cen", self.cc))
        if len(ps) > 0: return min(ps)
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
        "Transform the element to a line; lose all structure column attributes."
        if than is None: return True               # Explode IS implemented
        e1 = ThanLine()
        e1.thanSet(self.cp)   #ThanLine() makes deep copies of the coordinates
        yield e1


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset element by distance distance; to the right if distance>0 and to the left otherwise."
        super().thanOffset(through, distance, sidepoint)  #calls ThanLine method: offsets self.cp and deals with boundbox
        ca, cb, cc = self.cp[:3]
        bx2 = hypot(cb[1]-ca[1], cb[0]-ca[0])
        by2 = hypot(cc[1]-cb[1], cc[0]-cb[0])
        bx = self.ds[1]
        factor = bx2/bx
        self.ds[1] = bx2
        self.ds[0] = by2
        self.thanCargo["tci"] *= factor   #Initial    coating thickness
        self.thanCargo["tca"] *= factor   #Additional coating thickness


    #def thanLength(self):   #inherited from ThanLine
    #def thanArea(self):     #inherited from ThanLine

    def thanStraighten(self, c1=None, c2=None):
        "Straighten the line between c1 and c2; c1 and c2 may not be identical."
        if c1 is None: return False       # Report that Straighten IS NOT implemented/possible
        assert False, "Since if c1 is None we answer with False, the code should not reach here."


    def thanSpin(self):
        "Returns the spin of the element."
        return self.spin


    def thanTkGet(self, proj):
        "Gets the attributes of the element interactively from a window."
        than = proj[2].than
        g2l = than.ct.global2Local

        ca = proj[2].thanGudGetPoint(T["Corner [Center]: "], options=("Center",))
        if ca == Canc: return Canc       # Column cancelled
        if ca != "c":
            cb = proj[2].thanGudGetRect(ca, T["Other corner: "])
            if cb == Canc: return Canc   # Column cancelled
            bx = cb[0] - ca[0]
            by = cb[1] - ca[1]
            cc = list(ca)
            cc[0] = ca[0] + bx*0.5
            cc[1] = ca[1] + by*0.5
            bx = fabs(bx)
            by = fabs(by)
        else:
            cc = proj[2].thanGudGetPoint(T["Center: "])
            if cc == Canc: return Canc   # Column cancelled

            cb = proj[2].thanGudGetRect(cc, T["Corner point: "], ratioxy=(1.0,1.0))
            if cb == Canc: return Canc   # Column cancelled
            bx = fabs(cb[0] - cc[0]) * 2.0
            by = fabs(cb[1] - cc[1]) * 2.0

        while True:
            name = proj[2].thanGudGetText(T["Column name: "])
            if name == Canc: return Canc                    # Column cancelled
            name = name.strip()
            if not (" " in name or "\t" in name or "\n" in name or name==""): break
            proj[2].thanPrt(T["Invalid name"], "can1")

        ds = [by, bx, 0, 0, 0, 0]
        self.thanSet(13, name, cc, ds, 0.0, spin=1, cargo=None)
        return True


    def thanTkDraw1(self, than):
        "Draws the bimelement in tkinter canvas."
        print("thanTkdraw1(): dimstyle.thanTextsize=", than.dimstyle.thanTextsize)
        for e in self.__decompose(than.font, than.dimstyle):
            e.thanTkDraw(than)


    #def thanExpDxf(self, fDxf):  #inherited from ThanLine
    #def thanExpSyk(self, than): #inherited from ThanLine
    #def thanExpBrk(self, than): #inherited from ThanLine


    def thanExpSyn(self, than):
        "Exports the coordinates of the center to syn file."
        than.ibr += 1
        cp1 = self.cc
        than.write(than.form % (than.ibr, cp1[0], cp1[1], cp1[2]))
        #than.write(than.formnam % (self.name, cp1[0], cp1[1], cp1[2]))


    #def thanExpKml(self, than): #inherited from ThanLine
    #def thanExpPil(self, than): #inherited from ThanLine
    #def thanPlotPdf(self, than): #inherited from ThanLine

    def thanList(self, than):
        "Shows information about the structural column element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        oc = T["(closed)"]
        than.write(" %s    %s %s\n" % (oc, T["Layer:"], than.laypath))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()),
            T["Area"], than.strdis(self.thanArea())))
        than.write("%s%s\n" % (T["Center: "], than.strcoo(self.cc)))
        than.write("%s%s    %s%d\n" % (T["Theta: "], than.strang(self.theta), T["Spin: "], self.thanSpin()))
        bx = self.ds[1]
        by = self.ds[0]
        than.write("%s: %s (%sx%s):\n" % (T["Cross section"], T["rectangular"],
            than.strdis(bx), than.strdis(by)))


    def thanExpThc1(self, fw):
        "Save the BIM Column in thc format."
        f = fw.formFloat
        fw.writeAtt("SECTION", "%d" % (self.itype,))
        fw.writeTextln(self.name)
        fw.writeNode(self.cc)
        fw.writeSnode("DIMENSIONS", 6, self.ds)
        fw.writeAtt("THETA", f % (self.theta,))
        fw.writeln("%d" % (self.spin,))


    def thanImpThc1(self, fr, ver):
        "Read the BIM column from thc format."
        itype, = map(int, fr.readAtt("SECTION"))  #May raise ValueError, StopIteration
        name = fr.readTextln()              #May raise StopIteration, ValueError
        cc = fr.readNode()                  #May raise ValueError, IndexError, StopIteration
        ds = fr.readSnode("DIMENSIONS", 6)  #May raise ValueError, IndexError, StopIteration   #works for python2,3
        theta, = map(float, fr.readAtt("THETA"))  #May raise ValueError, StopIteration
        spin = int(next(fr))                #May raise ValueError, StopIteration
        if spin not in (1, -1): raise ValueError("spin must 1 or -1")
        self.thanSet(itype, name, cc, ds, theta, spin=spin, cargo=None)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        cc = list(self.cc)
        cc[:3] = fun(cc[:3])

        bx = self.ds[1]
        by = self.ds[0]

        cr = list(self.cc)
        cr[0] += bx
        cr = fun(cr[:3])
        bx2 = hypot(cr[1]-cc[1], cr[0]-cc[0])

        cr = list(self.cc)
        cr[1] += by
        cr = fun(cr[:3])
        by2 = hypot(cr[1]-cc[1], cr[0]-cc[0])

        cr = list(self.cc)
        r = hypot(bx, by)
        cr[0] += r * cos(self.theta)
        cr[1] += r * sin(self.theta)
        cr = fun(cr[:3])
        theta = atan2(cr[1]-cc[1], cr[0]-cc[0])   #Note that python ensures than atan2(0,0) = 0!!!

        ds = [by2, bx2, 0, 0, 0, 0]
        self.thanSet(self.itype, self.name, cc, ds, theta, spin=self.spin, cargo=None)

    #def thanTkDraw(self, than):   #Inherited
    #def thanClone(self):          #Inherited
    #def thanUntag(self):          #Inherited
    #def thanInbox(self, xymm):    #Inherited
    #def thanInarea(self, xymm):   #Inherited
    #def getBoundBox(self):        #Inherited
    #def setBoundBox (self, xymm): #Inherited
    #def updateBoundBox (self, xymm):  #Inherited
    #def setBoundBoxT (self, xymm):    #Inherited
    #def setBoundBoxRect(self, xa, ya, w, h, theta, center=False):  #Inherited

    def thanIsClosed(self):
        "Returns False if the BIM column is not degenerate and the first and last nodes coincide."
        if not self.thanIsNormal(): return False
        return True

    def getInspnt(self):
        "Returns the insertion point of the element."
        return list(self.cc)


    def thanChelev(self, z):
        "Set constant elevation of z."
        super().thanChelev()  #calls ThanLine method: chelevs self.cp
        self.cc[2] = z


    def thanChelevn(self, celev):
        "Set constant elevation of z and higher dimensions."
        super().thanChelev()  #calls ThanLine method: chelevs self.cp
        self.cc[2:] = celev



    #def thanExpThc(self, fw, layname):   #Inherited
    #def thanWriteCargo(self, fw):        #Inherited
    #def thanImpThc(self, fr, ver):       #Inherited
    #def thanReadCargo(self, fr, ver):    #Inherited


    def thanExtend(self, cp, iend=-1, method=0):
        "Return a new line extending self so that endpoint iend corresponds to cp."
        return []     #no extension is possible


    def thanLengthen(self, delta, ccu):
        "Return a clone of self with different length: add delta to length."
        return None   #Element can not be lengthened


    def __decompose(self, font, dimstyle):
        "Decompose bimcolumn to a set of ThanCad text and lines."
        print("__decompose(): dimstyle.thanTextsize=", dimstyle.thanTextsize)
        elems = []
        ThanElement.thanRotateSet(self.cc, self.theta)

        #text
        temp = ThanText()
        h = dimstyle.thanTextsize
        temp.thanSet(self.name, self.cc, h, 0.0)
        w1, h1 = font.thanCalcSizexy(self.name, h)

        dc = [0.0] * len(self.cc)
        dc[0] -= h1*len(self.name)*0.5
        dc[1] -= h1*0.5
        temp.thanMove(dc)
        temp.thanRotate()
        temp.thanTags = self.thanTags
        elems.append(temp)

        #Line(s)
        cline = [self.cp]

        for cp in cline:
            temp = ThanLine()
            temp.thanSet(cp)
            #temp.thanRotate()     #already rotated: see __rect()
            temp.thanTags = self.thanTags
            elems.append(temp)
        return elems


    def __rect(self):
        "Finds rotated enclosing rectangle; updates self.cp."
        c1 = list(self.cc)   #First find the non-rotated rectangle
        bx = self.ds[1]
        by = self.ds[0]
        c1[0] -= bx*0.5
        c1[1] -= by*0.5
        c2 = list(self.cc)
        c2[0] += bx*0.5
        c2[1] -= by*0.5
        c3 = list(self.cc)
        c3[0] += bx*0.5
        c3[1] += by*0.5
        c4 = list(self.cc)
        c4[0] -= bx*0.5
        c4[1] += by*0.5

        self.cp = [c1, c2, c3, c4, list(c1)]
        r = Rotator2d(self.cc, self.theta)  #Rotate the rectangle by self.theta
        r.rotateXyn(self.cp)


    def __boundBox(self):
        """Compute a minimum unrotated rectangle that contains the arc.

        It is assumed that self.cp is alread set by previous call to self.__rect()
        """
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])
