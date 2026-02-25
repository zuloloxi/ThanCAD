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

This module defines the ellipse state, i.e. as the user moves the mouse, an ellipse
is drawn from a given point to mouse cursor, continuously.
thanasis2012_12_19: This took ridiculously short time! Hooray!
"""
from math import hypot
from p_gmath import ellipse2Line, PI2
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric


class ThanStateEllipseb(ThanStateGeneric):
    "An object which interprets mouse movements to the length of the semi-minor axis of an ellipse."

    def __init__(self, proj, x1, y1, r1, t1):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1                 #Ellipse center x
        self.__y1 = y1                 #Ellipse center y
        self.__r1 = r1                 #Semi-major axis
        self.__t1 = t1                 #Angle of major axis
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self.__dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        b = hypot(xb-self.__x1, yb-self.__y1)
        cs, _ = ellipse2Line(self.__x1, self.__y1, self.__r1, b, 0.0, PI2,self.__t1, dt=10.0)

        draggedp = self.__dragged
        self.__dragged = dc.create_line(cs, fill="blue")

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
        "Change internal coordinates according to zoom; this function should be here (in the state objects)."
        self.__x1 = x + (self.__x1-x)*fact
        self.__y1 = y + (self.__y1-y)*fact
        self.__r1 *= fact
