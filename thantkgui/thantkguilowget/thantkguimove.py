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

This module defines moving state, i.e. selected elements moving along with the
mouse cursor.
"""
from math import cos, sin
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric


class ThanStateMove(ThanStateGeneric):
    "An object which interprets dragging events as events as ????."

    def __init__(self, proj, x1, y1, t1):
        "initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        if t1 is None: self.__t1 = None
        else: self.__t1 = cos(t1), -sin(t1)
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x1, y1)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__zooma = dc.create_line(x1-10000, y1-10000,
                                      x1-10001, y1-10001, tags="edrag")  # sentinel element
        dc.thanTempItems.add("edrag")    # __zooma is also included


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        xa, ya = dc.coords(self.__zooma)[:2]
        xb, yb = dc.thanOrtho.orthoxy(x, y)
        xb, yb = xb-10000, yb-10000
        dxy = xb-xa, yb-ya
        if self.__t1 is not None:   #Direction is fixed
            dd = dxy[0]*self.__t1[0] + dxy[1]*self.__t1[1]
            dxy = dd*self.__t1[0], dd*self.__t1[1]
        dc.move("edrag", dxy[0], dxy[1])


    def thanOnClick(self, event, x, y, cc):
        "Well, here is what should be done when mouse clicks."
        dc = self.thanProj[2].thanCanvas
#        dc.delete(self.__zooma)    # __zooma has the tag "edrag"
        dc.delete("edrag")
        dc.thanTempItems.remove("edrag")
        dc.thanLastResult = cc, None
        dc.thanState = THAN_STATE.NONE
        dc.thanOState = ThanStateGeneric(self.thanProj)


    def thanZoomXyr(self, x, y, fact):
        "Change internal coordinates according to zoom; this function should be in the state objects."
        self.__x1 = x + (self.__x1-x)*fact
        self.__y1 = y + (self.__y1-y)*fact
