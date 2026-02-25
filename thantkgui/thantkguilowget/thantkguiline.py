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

This module defines line states, i.e. as the user moves the mouse, one or more lines
are drawn from a given point to mouse cursor, continuously.
"""
from math import hypot, cos, sin
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric


class ThanStateLineold(ThanStateGeneric):
    "An object which interprets mouse movements to a line."

    def __init__(self, proj, x1, y1):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self.__dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        i1 = self.__dragged
        self.__dragged = dc.create_line(self.__x1, self.__y1, xb, yb, fill="blue")
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
        self.__x1 = x + (self.__x1-x)*fact
        self.__y1 = y + (self.__y1-y)*fact


class ThanStateLine(ThanStateGeneric):
    "An object which interprets mouse movements to a line."

    def __init__(self, proj, x1, y1):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = (dc.create_line(10000, 10000, 10001, 10001),)  # Dummy element to avoid complexity in onMotion()
        for i1 in self.__dragged:
            dc.thanTempItems.add(i1)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)

        ct = self.thanProj[2].thanCt
        dx, dy = ct.local2GlobalRel(xb-self.__x1, yb-self.__y1)
        d = hypot(dx, dy)
        text = self.thanProj[2].than.strdis(d)

        draggedp = self.__dragged
        self.__dragged = (dc.create_line(self.__x1, self.__y1, xb, yb, fill="blue"),
                          dc.create_text(xb+1, yb-1, text=text, anchor="sw", fill="blue"),
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



class ThanStateLine2(ThanStateGeneric):
    "An object which interprets mouse movements to 2 lines."

    def __init__(self, proj, x1, y1, x2, y2):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x2, y2)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = (dc.create_line(10000, 10000, 10001, 10001),)  # Dummy element to avoid complexity in onMotion()
        for i1 in self.__dragged:
            dc.thanTempItems.add(i1)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        draggedp = self.__dragged
        self.__dragged = (dc.create_line(self.__x1, self.__y1, xb, yb, fill="blue"),
                          dc.create_line(self.__x2, self.__y2, xb, yb, fill="blue"),
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
        "Change internal coordinates according to zoom; this fuction should be in the state objects."
        self.__x1 = x + (self.__x1-x)*fact
        self.__y1 = y + (self.__y1-y)*fact
        self.__x2 = x + (self.__x2-x)*fact
        self.__y2 = y + (self.__y2-y)*fact


class ThanStatePolar(ThanStateGeneric):
    "An object which interprets mouse movements to a line of constant length."

    def __init__(self, proj, x1, y1, r1):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__r1 = r1
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self.__dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        dx2 = xb - self.__x1
        dy2 = yb - self.__y1
        r = hypot(dx2, dy2)
        if r == 0:
            x2 = xb
            y2 = yb
        else:
            x2 = self.__x1 + dx2*self.__r1/r
            y2 = self.__y1 + dy2*self.__r1/r

        i1 = self.__dragged
        self.__dragged = dc.create_line(self.__x1, self.__y1, x2, y2, fill="blue")
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
        "Change internal coordinates according to zoom; this fuction should be in the state objects."
        self.__x1 = x + (self.__x1-x)*fact
        self.__y1 = y + (self.__y1-y)*fact
        self.__r1 *= fact



class ThanStateAzimuth(ThanStateGeneric):
    "An object which interprets mouse movements to a line of inclination."

    def __init__(self, proj, x1, y1, t1):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__t1 = cos(t1), -sin(t1)
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self.__dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        d = (xb - self.__x1)*self.__t1[0] + (yb - self.__y1)*self.__t1[1]
        x2, y2 = self.__x1+d*self.__t1[0], self.__y1+d*self.__t1[1]

        i1 = self.__dragged
        self.__dragged = dc.create_line(self.__x1, self.__y1, x2, y2, fill="blue")
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
        "Change internal coordinates according to zoom; this fuction should be in the state objects."
        self.__x1 = x + (self.__x1-x)*fact
        self.__y1 = y + (self.__y1-y)*fact
        self.__r1 *= fact
