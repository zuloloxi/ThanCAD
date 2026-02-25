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

Package which creates a bioclimatic city plan.
This module provides common utilities for the package.
"""
from math import fabs, hypot, pi, cos, sin
import p_ggen, p_gchart, p_gcol
from p_gmath import thanNear2

w1 = 10.0
w2 = 100.0
def road1energy(cc):
        "Calculates the energy of 1 road."
        return road1energyDetail(cc)[-1]
        sd = e = 0.0
        d8 = 0.0
        d10 = 0.0
        for ca, cb in p_ggen.iterby2(cc):
                d = hypot(cb[0]-ca[0], cb[1]-ca[1])
                sd += d
                dz = fabs(cb[2]-ca[2])
                slope = dz*100.0/d
                if slope <= 8.0:
                    e += 0.0
                elif slope < 10.0:
                    e += d*w1*(slope-8.0)
                    d8 += d
                else:
                    e += d*w1*(10.0-8.0) + d*w2*(slope-10.0)
                    d8 += d
                    d10 += d
        return sd, d8, d10, e


def road1energyDetail(cc):
        "Calculates the energy of 1 road."
        sd = e = 0.0
        d8 = 0.0
        d10 = 0.0
        detail = [(sd, d8, d10, e)]
        for ca, cb in p_ggen.iterby2(cc):
                d = hypot(cb[0]-ca[0], cb[1]-ca[1])
                sd += d
                dz = fabs(cb[2]-ca[2])
                slope = dz*100.0/d
                if slope <= 8.0:
                    e += 0.0
                elif slope < 10.0:
                    e += d*w1*(slope-8.0)
                    d8 += d
                else:
                    e += d*w1*(10.0-8.0) + d*w2*(slope-10.0)
                    d8 += d
                    d10 += d
                detail.append((sd, d8, d10, e))
        return detail


def pminmax(hull, theta):
    "Compute min/max x/y for coordinates in rotated system by theta."
    thrad = theta*pi/180.0
    t = cos(thrad), sin(thrad)
    n = -t[1], t[0]
    px = [t[0]*c[0]+t[1]*c[1] for c in hull]
    py = [n[0]*c[0]+n[1]*c[1] for c in hull]
    return min(px), max(px), min(py), max(py)


def itercom(fr):
    "Iterates through a file ignoring comments."
    for dl in fr:
        dl = dl.strip()
        if dl == "" or dl[0] == "#": continue
        yield dl


def lineprofile(clines):
    "Creates all roads' profiles as separate charts; debugging aid; not currently used."
    dfact = 0.1
    charts = []
    for cp,pyaxis,col in clines:
        d = [0.0*dfact]
        for ca, cb in p_ggen.iterby2(cp):
            d.append(d[-1]+hypot(cb[1]-ca[1], cb[0]-ca[0])*dfact)
        zmin = min(ca[2] for ca in cp)
        ch = p_gchart.ThanChart()
        ch.curveAdd((d[0], d[-1]), (0.0, 0.0), color=col)
        ch.curveAdd((d[0], d[0]), (0.0, cp[0][2]-zmin))
        for i in range(1, len(cp)):
            ch.curveAdd((d[i], d[i], d[i-1]), (0.0, cp[i][2]-zmin, cp[i-1][2]-zmin), color=col)
        charts.append(ch)
    return charts


def _layer(dxf, lay, col):
    "Sets layer and color."
    from p_gcol import thanDxfColName2Rgb, thanRgb2DxfColCodeApprox
    rgb = thanDxfColName2Rgb[col]
    icol = thanRgb2DxfColCodeApprox(rgb)
    dxf.thanDxfSetLayer(lay)
    dxf.thanDxfSetColor(icol)


def plotline(dxf, pline1):
    "Plot a polyline to .dxf."
    x = [c[0] for c in pline1]
    y = [c[1] for c in pline1]
    dxf.thanDxfPlotPolyline(x, y)
