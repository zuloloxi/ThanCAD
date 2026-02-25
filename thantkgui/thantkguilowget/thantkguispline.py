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

This module defines line states, i.e. as the user moves the mouse, a spline
curve (cubic functions) is drawn from a given point to mouse
cursor, continuously.
thanasis2009_11_12: This took ridiculously short time! Hooray!
"""
from p_gmath import ThanSpline
from p_ggen import frangec
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric


class ThanStateSplinep(ThanStateGeneric):
    "An object which interprets mouse movements to addition of a node to a spline curve."

    def __init__(self, proj, x1, y1, x2, y2):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self.__dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        x, y = dc.thanOrtho.orthoxy(x, y)
        xs = (self.__x1, self.__x2, x)
        ys = (self.__y1, self.__y2, y)
        try: sp = ThanSpline(0, xs, ys)
        except ZeroDivisionError: return                 # Invalid spline
        xs = []
        for t in frangec(0.0, sp.tmax, 4.0):
            x1, y1 = sp.splfun(t)
            xs.append((x1, y1))

        draggedp = self.__dragged
        self.__dragged = dc.create_line(xs, fill="blue")

        dc.delete(draggedp)
        dc.thanTempItems.remove(draggedp)
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
        self.__x2 = x + (self.__x2-x)*fact
        self.__y2 = y + (self.__y2-y)*fact
