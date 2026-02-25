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

This package emulates the dxf library in ThanCad.
"""
from math import pi, cos, sin
from .thandxfext import ZDEFAULT


#Thanasis 2008_02_25: Instead of ZDEFAULT (which is zero) should I use
#    self.thanDr._elev[2] instead? (which is the default height of a ThanCad drawing?)
#    I think not, because that is how p_gdxf library works; if the user does
#    not specify the height, it is assumed to be zero.


PI=pi   #3.1415926535897932384626433832795,
PI4=pi/4.0


class ThanDxfDra:
    "Mixin to draw various objects."

    def __init__(self):
        "No initialisation needed."
        pass

    def thanDxfPlotBlock (self, bloc, xa, ya, xsc, ysc, thet):
        "Plots a predefined block."
        pass

    def thanDxfPlotBlock3 (self, bloc, xa, ya, za, xsc, ysc, zsc, thet):
        "Plots a 3d predefined block."
        pass

    def thanDxfPlotCircle (self, xc, yc, r):
        "Plots a circle."
        (px, py) = self.thanDxfTop(xc, yc)
        self.thanDr.dxfCircle(px, py, ZDEFAULT, self.thanLayer, None, self.thanColor, r)

    def thanDxfPlotCircle3 (self, xc, yc, zc, r):
        "Plots a 3d circle."
        (px, py, pz) = self.thanDxfTop3(xc, yc, zc)
        self.thanDr.dxfCircle(px, py, pz, self.thanLayer, None, self.thanColor, r)

    def thanDxfPlotArc(self, xc, yc, r, ang1, ang2):
        """Plots an arc of circle.

        xc,yc: center of the circle
        r    : radius of circle
        ang1 : angle of the beginning of the arc
        ang2 : angle of the end of the arc"""
        (px, py) = self.thanDxfTop(xc, yc)
        self.thanDr.dxfArc(px, py, ZDEFAULT, self.thanLayer, None, self.thanColor, r, ang1, ang2)

    def thanDxfPlotPoint(self, xp, yp):
        "Plots a point."
        (px, py) = self.thanDxfTop(xp, yp)
        self.thanDr.dxfPoint(px, py, ZDEFAULT, self.thanLayer, None, self.thanColor)

    def thanDxfPlotPoint3(self, xp, yp, zp):
        "Plots a 3d point."
        (px, py, pz) = self.thanDxfTop3(xp, yp, zp)
        self.thanDr.dxfPoint(px, py, pz, pz, self.thanLayer, None, self.thanColor)

    def thanDxfPlotSolid4 (self, xx1, yy1, xx2, yy2, xx3, yy3, xx4, yy4):
        "Plots a solid 4node polygon."
        (px, py) = self.thanDxfTop(xx1, yy1)
        self.thanDxfPlotPolyVertex(px, py, 3)
        (px, py) = self.thanDxfTop(xx2, yy2)
        self.thanDxfPlotPolyVertex(px, py, 2)
        (px, py) = self.thanDxfTop(xx3, yy3)
        self.thanDxfPlotPolyVertex(px, py, 2)
        (px, py) = self.thanDxfTop(xx4, yy4)
        self.thanDxfPlotPolyVertex(px, py, 2)
        (px, py) = self.thanDxfTop(xx1, yy1)
        self.thanDxfPlotPolyVertex(px, py, 2)
        self.thanDxfPlotPolyVertex(0, 0, 999)

    def thanDxfPlotSolid3 (self, xx1, yy1, xx2, yy2, xx3, yy3):
        "Plots a solid triangle."
        (px, py) = self.thanDxfTop(xx1, yy1)
        self.thanDxfPlotPolyVertex(px, py, 3)
        (px, py) = self.thanDxfTop(xx2, yy2)
        self.thanDxfPlotPolyVertex(px, py, 2)
        (px, py) = self.thanDxfTop(xx3, yy3)
        self.thanDxfPlotPolyVertex(px, py, 2)
        (px, py) = self.thanDxfTop(xx1, yy1)
        self.thanDxfPlotPolyVertex(px, py, 2)
        self.thanDxfPlotPolyVertex(0, 0, 999)

    def thanDxfPlot3dface3(self, xx1, yy1, zz1, xx2, yy2, zz2, xx3, yy3, zz3):
        "Plots 3dface triangle."
        (px, py, pz) = self.thanDxfTop3(xx1, yy1, zz1)
        self.thanDxfPlotPolyVertex3(px, py, pz, 3)
        (px, py, pz) = self.thanDxfTop3(xx2, yy2, zz2)
        self.thanDxfPlotPolyVertex3(px, py, pz, 3)
        (px, py, pz) = self.thanDxfTop3(xx3, yy3, zz3)
        self.thanDxfPlotPolyVertex3(px, py, pz, 3)
        (px, py, pz) = self.thanDxfTop3(xx1, yy1, zz1)
        self.thanDxfPlotPolyVertex3(px, py, pz, 3)
        self.thanDxfPlotPolyVertex3(0, 0, 999)

    def thanDxfPlotSolidCircle8(self, x, y, r, i1, i2):
        """Plots integer number of eighths of a solid circle using solid polygons.

        It splits the circle in eighths, and approximates one eighth
        with a 4node polygon. It begins with the i1-th eighth and stops
        at i2-th eighth:    1 <= i1 <= i2 <= 8."""

        for ri in range(i1-1, i2):
            self.thanDxfPlotSolid4 (x, y,
                x+r*cos(PI4*ri),        y+r*sin(PI4*ri),
                x+r*cos(PI4*(ri+0.5)),  y+r*sin(PI4*(ri+0.5)),
                x+r*cos(PI4*(ri+1)),    y+r*sin(PI4*(ri+1)))

    def thaDxfPlotSolidRing(self, xc, yc, ri, re, n):
        """Plots a full solid ring using n solid polygons.

        xc, yc: coordinates of the center of the ring
        ri, re: internal and external radius of the ring
        n     : number of 4point solids (bigger means finer)"""

        dth = 2.0 * PI / n
        cosd = cos(dth)
        sind = sin(dth)
        cost = 1.0
        sint = 0.0
        x1 = xc + ri
        y1 = yc
        x3 = xc + re
        y3 = yc

        for i in range(n):
            x2   = cost*cosd - sint*sind
            sint = sint*cosd + cost*sind
            cost = x2
            x2 = xc + ri*cost
            y2 = yc + ri*sint
            x4 = xc + re*cost
            y4 = yc + re*sint
            self.thanDxfPlotSolid4(x1, y1, x2, y2, x4, y4, x3, y3)
            x1 = x2
            y1 = y2
            x3 = x4
            y3 = y4

    def thanDxfPlotSolidCircle(self, xc, yc, ri, n1):
        """Plots a full solid circle using n1 solid polygons.

        xc, yc: coordinates of the center of the circle
        ri    : radius of the circle
        n1    : number of 4point solids (bigger means finer)"""

        n = int((n1 + 1) / 2)
        dth = 2.0 * PI / (2*n)
        cosd = cos(dth)
        sind = sin(dth)
        cost = 1.0
        sint = 0.0
        x2 = xc + ri
        y2 = yc

        for i in range(n):
            x3   = cost*cosd - sint*sind
            sint = sint*cosd + cost*sind
            cost = x3
            x3 = xc + ri*cost
            y3 = yc + ri*sint

            x4   = cost*cosd - sint*sind
            sint = sint*cosd + cost*sind
            cost = x4
            x4 = xc + ri*cost
            y4 = yc + ri*sint

            self.thanDxfPlotSolid4 (xc, yc, x2, y2, x3, y3, x4, y4)
            x2 = x4
            y2 = y4

    def thanDxfPlotImage(self, filnam, x1, y1, size, scale, theta):
        "Plots a string to a .dxf file."

        (px, py) = self.thanDxfTop(x1, y1)
        self.thanDr.dxfThanImage(px, py, ZDEFAULT, self.thanLayer, None, self.thanColor, filnam, size, scale, theta)
