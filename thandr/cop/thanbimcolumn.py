##############################################################################
# ThanCad 0.8.3 "Students2023": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2023 Thanasis Stamos, December 25, 2023
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
ThanCad 0.8.3 "Students2023": n-dimensional CAD with raster support for engineers

This module defines the BIM column element. It is meant to be used in structural
engineering, and for the moment it is made of reinforced concrete.
"""
from math import atan2, hypot
import copy
from .thanline import ThanLine


class ThanBimColumn(ThanLine):
    "A stuctural column; the cross section is displayed."
    thanElementName = "BIMCOLUMN"    # Name of the element's class


    def thanSet (self, itype, cc, bx, by, theta, spin=1, cargo=None):
        """Sets the attributes of the line.

        itype: 0: rectangular section
        cc   : point: coordinates of the reference point of the column: currently 
               the center of gravity of the section. The elevation of the point is
               elevation of the upper surface of the plate of the current storey.
        bx   : width of section parallel to x-axis (when theta==0)
        by   : width of section parallel to y-axis (when theta==0)
        theta: rotation of the section with respect to x-axis. For the moment zero.
        cargo: dictionary with more attributes of the columns:
               tci: width of initial coating of the column
               tca: width of additional coating of the column
        """
        self.itype = itype
        self.cc = list(cc)
        self.bx = bx
        self.by = by
        self.theta = theta
        self.spin = spin
        if cargo is None: self.thanCargo = {}
        else:             self.thanCargo = copy.deepcopy(atts)
        self.thanCargo.setdefault("tci", 0.0)
        self.thanCargo.setdefault("tca", 0.0)

        self.__rect()   #This sets self.cp
        self.__boundbox()     #Sets the minimum enclosing unrotated rectangle
#        self.thanTags = ()                                 # thanTags is initialised in ThanElement


    def thanIsNormal(self):
        "Checks if element shape is OK (i.e. it is not degenerate)."
        return self.bx>0.0 and self.by>0.0


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
        self.theta = atan2(ca[1]-cb[1], ca[0]-cb[0]) % PI2    #Mirror reverses point sequence ca->cb to cb->ca
        self.__rect()       #This sets self.cp
        self.__boundbox()   #Sets the minimum enclosing unrotated rectangle


    def thanPointMir(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        super().thanPointMir()  #calls ThanLine method: point mirrors self.cp and deals with boundbox
        self.cc = self.thanPointMirXy(self.cc)
        self.theta = (self.theta + pi) % PI2


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        super().thanScale(cs, scale)  #calls ThanLine method: scales self.cp and deals with boundbox
        self.cc[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.cc, cs)]  #works for python2,3
        self.bx *= scale
        self.by *= scale
        self.thanCargo["tci"] *= scale   #Initial    coating thickness
        self.thanCargo["tca"] *= scale   #Additional coating thickness


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        super().thanMove(dc)  #calls ThanLine method: moves self.cp and deals with boundbox
        self.cc[:] = [cc1+dd1 for (cc1,dd1) in zip(self.cc, dc)]  #works for python2,3


    def thanReverse(self):
        "Reverse the spin of the bimcolumn."
        self.spin = -self.spin

    #def thanOsnap(self, proj, otypes, ccu, eother, cori):  #Inherited from ThanLine

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
        e1.thanSet(cp)   #ThanLine() makes deep copies of the coordinates
        yield e1


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset element by distance distance; to the right if distance>0 and to the left otherwise."
        super().thanOffset(through, distance, sidepoint)  #calls ThanLine method: offsets self.cp and deals with boundbox
        ca, cb, cc = self.cp[:3]
        bx = hypot(cb[1]-ca[1], cb[0]-ca[0])
        by = hypot(cc[1]-cb[1], cc[0]-cb[0])
        factor = bx/self.bx
        self.bx = bx
        self.by = by
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
        pass









    def __rect(self, c1, c2, h):
        "Finds rotated enclosing rectangle; updates self.cp."
        c1 = list(self.cc)   #First find the non-rotated rectangle
        c1[0] -= self.bx*0.5
        c1[1] -= self.by*0.5
        c3 = list(self.cc)
        c2[0] += self.bx*0.5
        c2[1] -= self.by*0.5
        c3 = list(self.cc)
        c3[0] += self.bx*0.5
        c3[1] += self.by*0.5
        c4 = list(self.cc)
        c4[0] -= self.bx*0.5
        c4[1] += self.by*0.5

        self.cp = [c1, c2, c3, c4, list(c1)]
        self.thanRotateSet(self.cc, self.theta)  #Rotate the rectangle by self.theta
        self.thanRotateXyn(self.cp)


    def __boundBox(self):
        """Compute a minimum unrotated rectangle that contains the arc.

        It is assumed that self.cp is alread set by oreviou call to self.__rect()
        """
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])
