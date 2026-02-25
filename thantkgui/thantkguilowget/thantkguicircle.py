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

This module defines circle states, i.e. as the user moves the mouse, a circle or
an arc are drawn, continuously.
"""
from math import hypot, atan2, pi
import tkinter
import p_gmath
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric


class ThanStateCircle(ThanStateGeneric):
    """An object which interprets mouse movements to a circle.

    If coef is 1   then x1,y1 is center and the radius is given dynamically.
    If coef is 0.5 then x1,y1 is center and the diameter is given dynamically.
    """

    def __init__(self, proj, x1, y1, coef):
        "Initialize object."
        self.thanProj = proj
        self._x1 = x1
        self._y1 = y1
        self.__coef = coef
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self._dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self._dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        r = hypot(xb-self._x1, yb-self._y1) * self.__coef   #If coef==0.5, draws the half circle (when the user chose diameter)
        i1 = self._dragged
        self._dragged = dc.create_oval(self._x1-r, self._y1+r, self._x1+r, self._y1-r,
                                        outline = "blue")
        dc.delete(i1)
        dc.thanTempItems.remove(i1)
        dc.thanTempItems.add(self._dragged)


    def thanOnClick(self, event, x, y, cc):
        "Well, here is what should be done when mouse clicks."
        dc = self.thanProj[2].thanCanvas
        dc.delete(self._dragged)
        dc.thanTempItems.remove(self._dragged)
        dc.thanLastResult = cc, None
        dc.thanState = THAN_STATE.NONE
        dc.thanOState = ThanStateGeneric(self.thanProj)


    def thanZoomXyr(self, x, y, fact):
        "Change internal coordinates according to zoom; this function should be in the state objects."
        self._x1 = x + (self._x1-x)*fact
        self._y1 = y + (self._y1-y)*fact


class ThanStateCircle2(ThanStateCircle):
    "An object which interprets mouse movements to a circle passing through 2 antidimetric points."

    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        xce = (xb+self._x1)*0.5
        yce = (yb+self._y1)*0.5
        r = hypot(xb-self._x1, yb-self._y1) * 0.5
        i1 = self._dragged
        self._dragged = dc.create_oval(xce-r, yce+r, xce+r, yce-r, outline = "blue")
        dc.delete(i1)
        dc.thanTempItems.remove(i1)
        dc.thanTempItems.add(self._dragged)


class ThanStateCircle3(ThanStateGeneric):
    "An object which interprets mouse movements to a circle, passing through 3 points."

    def __init__(self, proj, x1, y1, x2, y2):
        "Initialize object."
        self.thanProj = proj
        self.__cc1 = [x1, y1]
        self.__cc2 = [x2, y2]
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self.__dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        cc, r = p_gmath.circle3(self.__cc1, self.__cc2, (xb, yb))
        if cc is None: return    #Collinear points: do nothing

        i1 = self.__dragged
        self.__dragged = dc.create_oval(cc[0]-r, cc[1]+r, cc[0]+r, cc[1]-r, outline = "blue")
        dc.delete(i1)
        dc.thanTempItems.remove(i1)
        dc.thanTempItems.add(self.__dragged)


    def thanOnClick(self, event, x, y, cc):
        "Well, here is what should be done when mouse clicks."
        dc = self.thanProj[2].thanCanvas
        dc.delete(self.__dragged)
        dc.thanTempItems.remove(self.__dragged)
        dc.thanLastResult = cc, None
        dc.thanState = THAN_STATE.NONE
        dc.thanOState = ThanStateGeneric(self.thanProj)


    def thanZoomXyr(self, x, y, fact):
        "Change internal coordinates according to zoom; this function should be in the state objects."
        def conv(cc1):
            x1, y1 = cc1
            x1 = x + (x1-x)*fact
            y1 = y + (y1-y)*fact
            return [x1, y1]
        self.__cc1 = conv(self.__cc1)
        self.__cc2 = conv(self.__cc2)


class ThanStateArc(ThanStateGeneric):
    "An object which interprets mouse movements to arcs."

    def __init__(self, proj, x1, y1, r1, t1, clockwise=False):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__r1 = r1
        self.__t1 = t1
        self.__clockwise = clockwise
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = (dc.create_line(10000, 10000, 10001, 10001),)  # Dummy element to avoid complexity in onMotion()
        for i1 in self.__dragged:
            dc.thanTempItems.add(i1)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        theta1 = self.__t1 / pi * 180
        theta2 = atan2(-(yb-self.__y1), xb-self.__x1) / pi * 180
        dth = (theta2-theta1)%360.0
        if self.__clockwise: dth = -(360-dth)
        draggedp = self.__dragged
        self.__dragged = (dc.create_arc(self.__x1-self.__r1, self.__y1+self.__r1,
                                        self.__x1+self.__r1, self.__y1-self.__r1,
#                                        start=theta1, extent=(theta2-theta1)%360.0, style=tkinter.ARC,
                                        start=theta1, extent=dth, style=tkinter.ARC,
                                        outline = "blue"),
                          dc.create_line(self.__x1, self.__y1, x, y, fill="blue"),
                         )
        for i1 in draggedp:
            dc.delete(i1)
            dc.thanTempItems.remove(i1)
        for i1 in self.__dragged:
            dc.thanTempItems.add(i1)


    def thanOnClick(self, event, x, y, cc):
        "Well, here is what should be done when mouse clicks."
        dc = self.thanProj[2].thanCanvas
        for i1 in self.__dragged:
            dc.delete(i1)
            dc.thanTempItems.remove(i1)
        dc.thanLastResult = cc, None
        dc.thanState = THAN_STATE.NONE
        dc.thanOState = ThanStateGeneric(self.thanProj)


    def thanZoomXyr(self, x, y, fact):
        "Change internal coordinates according to zoom; this function should be in the state objects."
        self.__x1 = x + (self.__x1-x)*fact
        self.__y1 = y + (self.__y1-y)*fact
        self.__r1 *= fact
