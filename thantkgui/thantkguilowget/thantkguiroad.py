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

This module defines line states, i.e. as the user moves the mouse, a road
(which is a line with circular arcs) is drawn from a given point to mouse
cursor, continuously.
"""
from thanvar import calcRoadNode, tkRoadNode, tkRoadNodeR
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric


class ThanStateRoadp(ThanStateGeneric):
    "An object which interprets mouse movements to addition of a node to a road."

    def __init__(self, proj, x1, y1, x2, y2, x3, y3, r1):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2
        self.__x3 = x3
        self.__y3 = y3
        self.__r1 = r1
        dc = self.thanProj[2].thanCanvas
        dc.thanOrtho.enable(x2, y2)               # Ortho is disabled in thanCleanup in stateless mixin
        self.__dragged = (dc.create_line(10000, 10000, 10001, 10001),)  # Dummy element to avoid complexity in onMotion()
        for i1 in self.__dragged:
            dc.thanTempItems.add(i1)
        if self.__x3 is not None:
#           hopefully everything is set, and the following event will trigger __onMotion to do the drawing work
            dc.event_generate("<Motion>", when="head", x=self.__x3, y=self.__y3, warp=1)  # Set mouse position to the previous c3 point


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
        x, y = dc.thanOrtho.orthoxy(x, y)
        draggedp = self.__dragged
        self.__dragged, ct = tkRoadNode(self.__x1, self.__y1, self.__x2, self.__y2,
                             x, y, self.__r1, dc, fill="blue", dash=(), width=1, tags=())
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


    def thanOnClickr(self, event, x, y, cc):
        "Well, here is what should be done when right mouse button clicks."
        dc = self.thanProj[2].thanCanvas
        for i1 in self.__dragged:
            dc.delete(i1)
            dc.thanTempItems.remove(i1)
        dc.thanLastResult = cc, "r"
        dc.thanState = THAN_STATE.NONE
        dc.thanOState = ThanStateGeneric(self.thanProj)


class ThanStateRoadr(ThanStateGeneric):
    "An object which interprets mouse movements to modification of the radius of an arc."

    def __init__(self, proj, x1, y1, x2, y2, x3, y3, r1):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2
        self.__x3 = x3
        self.__y3 = y3
        self.__r1 = r1
        dc = self.thanProj[2].thanCanvas
#        dc.thanOrtho.enable(x3, y3)               # Ortho is awkward here
        self.__dragged = (dc.create_line(10000, 10000, 10001, 10001),)  # Dummy element to avoid complexity in onMotion()
        for i1 in self.__dragged:
            dc.thanTempItems.add(i1)
#       hopefully everything is set, and the following event will trigger __onMotion to do the drawing work
        ro = calcRoadNode(self.__x1, self.__y1, self.__x2, self.__y2, self.__x3, self.__y3, self.__r1)
        dc.event_generate("<Motion>", when="head", x=ro.pm.x, y=ro.pm.y, warp=1)  # Set mouse position to the middle of the circular curve


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        dc = self.thanProj[2].thanCanvas
#        x, y = dc.thanOrtho.orthoxy(x, y)         # Ortho is awkward here
        ct = self.thanProj[2].thanCt
        draggedp = self.__dragged
        self.__dragged, ct = tkRoadNodeR(self.__x1, self.__y1, self.__x2, self.__y2,
                                         self.__x3, self.__y3, x, y, dc, ct, fill="blue", dash=(), width=1, tags=())
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


    def thanOnClickr(self, event, x, y, cc):
        "Well, here is what should be done when right mouse button clicks."
        self.thanOnClick(event, x, y, cc) # It is like if the user pressed left click
