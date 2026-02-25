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

from .thandxfext import ZDEFAULT

PLINECLOSED   = 1
PLINE3        = 8
PLINEVERTEX3  = 32
PLINEWHOKNOWS = 128


class ThanDxfLin:
    "Mixin to export lines to .dxf file."

    def __init__(self):
        "Some Initialisation for polyvertex."
        self.__firstVertex = 1

    def thanDxfPlotLine(self, xp, yp):
        "Plots many line segments."
        p = self.thanDxfPlot
        p(xp[0], yp[0], 3)
        for i in range(1, len(xp)): p(xp[i], yp[i], 2)

    def thanDxfPlotLine3 (self, xp, yp, zp):
        "Plots many 3d line segments."
        p = self.thanDxfPlot3
        p(xp[0], yp[0], zp[0], 3)
        for i in range(1, len(xp)): p(xp[i], yp[i], zp[i], 2)

    def thanDxfPlotPolyline (self, xgram, ygram):
        "Plots a 2d polyline."
        n = len(xgram)
        xg = [None]*n; yg = [None]*n
        for i in range(len(xgram)):
            xg[i], yg[i] = self.thanDxfTop(xgram[i], ygram[i])
        zg = [ZDEFAULT] * n
        self.thanDr.dxfPolyline(xg, yg, zg, self.thanLayer, None, self.thanColor)

    def thanDxfPlotPolyline3 (self, xgram, ygram, zgram):
        "Plots a 3d polyline."
        n = len(xgram)
        xg = [None]*n; yg = [None]*n; zg = [None]*n
        for i in range(n):
            xg[i], yg[i], zg[i] = self.thanDxfTop3(xgram[i], ygram[i], zgram[i])
        self.thanDr.dxfPolyline(xg, yg, zg, self.thanLayer, None, self.thanColor)

    def thanDxfPlotPolyVertex (self, xx, yy, ic, bulge=None):
        "Plots a 2d polyline, vertex by vertex."
        if self.__firstVertex:
            self.__xvert = [xx]
            self.__yvert = [yy]
            self.__firstVertex = False
        elif ic >= 999:
            self.thanDxfPlotPolyline (self.__xvert, self.__yvert)
            del self.__xvert, self.__yvert
            self.__firstVertex = True
        else:
            self.__xvert.append(xx)
            self.__yvert.append(yy)

    def thanDxfPlotPolyVertex3 (self, xx, yy, zz, ic):
        "Plots a 3d polyline, vertex by vertex."
        if self.__firstVertex:
            self.__xvert = [xx]
            self.__yvert = [yy]
            self.__zvert = [zz]
            self.__firstVertex = False
        elif ic >= 999:
            self.thanDxfPlotPolyline3(self.__xvert, self.__yvert, self.__zvert)
            self.__firstVertex = 1
            del self.__xvert, self.__yvert, self.__zvert
            self.__firstVertex = 1
        else:
            self.__xvert.append(xx)
            self.__yvert.append(yy)
            self.__zvert.append(zz)

    def thanDxfPlotLinebox (self, xx, yy, bb, hh):
        "Plots a 2d rectangle."
        xx1 = xx + bb
        yy1 = yy + hh
        self.thanDxfPolyVertex (xx,  yy,  2)
        self.thanDxfPolyVertex (xx1, yy,  2)
        self.thanDxfPolyVertex (xx1, yy1, 2)
        self.thanDxfPolyVertex (xx,  yy1, 2)
        self.thanDxfPolyVertex (xx,  yy,  2)
        self.thanDxfPolyVertex (0.0, 0.0, 999)

    def thanDxfPlot(self, xx, yy, icom):
        "Plots a line from previous point to this and some housekeeping."
#-------Check if end
        ic = abs(icom)
        if ic == 1000 or ic == 999:
            self.thanDr.thanAfterImport()
            return
#-------Plot line
        if ic == 1: ic = self.thanIpen
        self.thanIpen = ic
        (px, py) = self.thanDxfTop(xx, yy)
        if ic == 2:
            self.thanDr.dxfLine([self.thanPXnow, px], [self.thanPYnow, py], [ZDEFAULT, ZDEFAULT],
                self.thanLayer, None, self.thanColor)
        self.thanPXnow = px
        self.thanPYnow = py
#-------Check if negative
        if icom < 0: self.thanDxfLocref(0.0, 0.0, 0.0, 0.0)

    thanDxfPlot10 = thanDxfPlot    # For compatibility; see the following function

    def thanDxfPlot3(self, xx, yy, zz, icod):
        "Plots a 3D line from previous point to this."
#-------Plot line
        ic = abs(icod)
        if ic == 1: ic = self.thanIpen
        self.thanIpen = ic
        (px, py, pz) = self.thanDxfTop3(xx, yy, zz)
        if ic == 2:
            self.thanDr.dxfLine([self.thanPXnow, px], [self.thanPYnow, py], [self.thanPZnow, pz], self.thanLayer, None, self.thanColor)
        self.thanPXnow = px
        self.thanPYnow = py
        self.thanPZnow = pz
