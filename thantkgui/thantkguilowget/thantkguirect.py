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

This module defines rectangle states, i.e. as the user moves the mouse, a rectangle
is drawn from a given point to mouse cursor, continuously.
"""
from math import fabs
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric


class ThanStateRectangle(ThanStateGeneric):
    "An object which interprets mouse movements to a rectangle."

    def __init__(self, proj, x1, y1, t1, t2):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__t1 = t1               # __t1 is the command
        self.__rx = t2[0]  # __rx is the ratio by which the dx to the left is increasing with respect to the dx on the right
        self.__ry = t2[1]  # __ry is the ratio by which the dy to the bottom is increasing with respect to the dy to the top
#        print "rectangle: command: t1=", t1
        dc = self.thanProj[2].thanCanvas
#        dc.thanOrtho.enable(x1, y1)               # Ortho is crazy here!
        self.__dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self.__dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        out = "blue"; fil = "darkblue"
        if self.__t1 == "c": out = "cyan"; fil = "darkcyan"
        elif self.__t1 == "cw" and x < self.__x1: out = "cyan"; fil = "darkcyan"
        elif self.__t1 is None: out = "blue"; fil = None
        dc = self.thanProj[2].thanCanvas
#        x, y = dc.thanOrtho.orthoxy(x, y)     # ortho is crazy here
        i1 = self.__dragged
        dx = x - self.__x1
        dy = y - self.__y1
        if dx > 0.0 or self.__rx == 0.0: xx1 = self.__x1 - dx*self.__rx
        else:                            xx1 = self.__x1 - dx/self.__rx
        if dy < 0.0 or self.__ry == 0.0: yy1 = self.__y1 - dy*self.__ry  #Not that pixel y-axis is positive downwards
        else:                            yy1 = self.__y1 - dy/self.__ry
        self.__dragged = dc.create_rectangle(xx1, yy1, x, y, outline=out, fill=fil, stipple="gray25")
#       if self.__t1 is not None: dc.lower(self.__dragged)
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



class ThanStateRectratio(ThanStateGeneric):
    "An object which interprets mouse movements to a rectangle with fixed signed __t1=height/width."

    def __init__(self, proj, x1, y1, t1, cc1):
        "Initialize object."
        self.thanProj = proj
        self.__x1 = x1
        self.__y1 = y1
        self.__t1 = t1                # __t1 is the signed ratio: height/width
        self.__cc1 = cc1

        dc = self.thanProj[2].thanCanvas
        self.__dragged = dc.create_line(10000, 10000, 10001, 10001)  # Dummy element to avoid complexity in onMotion()
        dc.thanTempItems.add(self.__dragged)


    def thanOnMotion(self, event, x, y):
        "Well, here is what should be drawn each time mouse moves."
        stip = "blue"
        dx = abs(x - self.__x1)
        dy = abs(y - self.__y1)
        if dx > dy: dy = dx*self.__t1
        else:       dx = dy/self.__t1
        x2 = self.__x1+dx
        y2 = self.__y1-dy

        dc = self.thanProj[2].thanCanvas
        i1 = self.__dragged
        self.__dragged = dc.create_rectangle(self.__x1, self.__y1, x2, y2, outline=stip)
        dc.delete(i1)
        dc.thanTempItems.remove(i1)
        dc.thanTempItems.add(self.__dragged)


    def thanOnClick(self, event, x, y, cc):
        "Well, here is what should be done when mouse clicks."
#       dx = abs(x - self.__x1); dy = abs(y - self.__y1)
#       if dx > dy: dy = dx*self.__t1
#       else:       dx = dy/self.__t1
#       self.__resultCoor(self.__x1+dx, self.__y1-dy)
        dx = fabs(cc[0] - self.__cc1[0])
        dy = fabs(cc[1] - self.__cc1[1])
        if dx > dy: dy = dx*self.__t1
        else:       dx = dy/self.__t1
        cc[0] = self.__cc1[0] + dx
        cc[1] = self.__cc1[1] + dy

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
