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
This module builds a cache using DEM instead of DTM.
"""
from math import cos, sin, pi, hypot
import p_gtri, p_ggen
from . import roadut


class RoadDEM:
    "Object to compute energy using a DEM."

    def __init__(self, hull, dtm, dx=5.0, dy=5.0, theta=0.0, prt=p_ggen.prg, devdebug=False):
        "Initialise dem."
        self.hull = hull
        self.dem = p_gtri.ThanDEMdict()
        self.dem.fromDTMlines(dtm, dx, dy, theta, hull, prt)
        self.devdebug = devdebug                                   #If True, execute Developer debug code


    ioio=0
    fww = None
    def energy(self, s):
        "Calculates the energy of the road grid described in state s, using the built cache."
        self.ioio+=1
        if self.ioio % 500 == 0: print("roadem: state:", self.ioio)
        if self.devdebug:
            print(self.ioio)
            self.fww=open("dem%04d.txt"%(self.ioio,), "w")
        sd, sd8, sd10, se = self.roadenergy(s.theta,      s.boik, s.bod)
        d, d8, d10, e     = self.roadenergy(s.theta-90.0, s.hoik, s.bod)
        if self.devdebug:
            print("dem: theta: sd, se=", sd, se, "      theta+90:", d, e)
            self.fww.close()
        sd += d
        sd8 += d8
        sd10 += d10
        se += e
        return se/sd


    def energy3(self, s):
        "Calculates the energy of the road grid described in state s, using the built cache; returns more detail."
        sd, sd8, sd10, se = self.roadenergy(s.theta,      s.boik, s.bod)
        d, d8, d10, e     = self.roadenergy(s.theta-90.0, s.hoik, s.bod)
        sd += d
        sd8 += d8
        sd10 += d10
        se += e
        return se/sd, sd8, sd10


    def roadenergy(self, theta, boik, bod):
        "Find the energy of roads along x or y axis using the built cache."
        thrad = theta*pi/180.0
        t = cos(thrad), sin(thrad)
        n = -t[1], t[0]
        pyy = [n[0]*c[0]+n[1]*c[1] for c in self.hull]
        py = min(pyy) + 0.1       #Avoid perimeter
        pymax = max(pyy) - 0.1    #Avoid perimeter
        j = jj = 0
        sd = sd8 = sd10 = se = 0.0
        while True:
            pyaxis = py + bod[jj]*0.5
            if pyaxis > pymax: break
            d, d8, d10, e = self.roadenOnthefly(pyaxis, n)
            sd += d
            sd8 += d8
            sd10 += d10
            se += e
            py += bod[jj] + boik[jj]
            j += 1
            if j < len(boik): jj = j
        return sd, sd8, sd10, se


    def roadenOnthefly(self, pyaxis, n):
        c1, c2 = p_gtri.thanPolygonLine(self.hull, pyaxis, n)
        assert c1 is not None, "There should be 2 intersections!"
        if self.devdebug:
            self.fww.write("Coordinates\n")
            self.fww.write("%15.3f%15.3f\n" % (c1[0], c1[1]))
            self.fww.write("%15.3f%15.3f\n" % (c2[0], c2[1]))
            self.fww.write("$\n")
        ni, cn = self.dem.thanLineZ((c1,c2))
        if ni == -1:
            print("==============================================================")
            print(c1)
            print(c2)
            print("n=", n)
            t = n[1], -n[0]
            from math import atan2
            theta = atan2(t[1], t[0])*180.0/pi
            print("theta=", theta, "pyaxis=", pyaxis)
            print("cn=", cn)
            print("==============================================================")
            return 0.0,0.0,0.0,0.0  # No profile was found
        if self.devdebug:
            xth = 0.0
            self.fww.write("%10.2f%10.2f %s\n" % (xth, cn[0][2], "dem"))
            for a, b in p_ggen.iterby2(cn):
                xth += hypot(b[1]-a[1], b[0]-a[0])
                self.fww.write("%10.2f%10.2f\n" % (xth, b[2]))
            self.fww.write("$\n")
            ni, ccn = self.dtmq.thanLineZ((c1, c2))
            if ni != -1:
                xth = 0.0
                self.fww.write("%10.2f%10.2f %s\n" % (xth, ccn[0][2], "dtm"))
                for a, b in p_ggen.iterby2(ccn):
                    xth += hypot(b[1]-a[1], b[0]-a[0])
                    self.fww.write("%10.2f%10.2f\n" % (xth, b[2]))
                self.fww.write("$\n")
        return roadut.road1energy(cn)


    def plot(self):
        "Plot the dem into dxf."
        import p_gdxf
        dxf = p_gdxf.ThanDxfPlot()
        dxf.thanDxfPlots()
        dxf.thanDxfSetLayer("HULL")
        x = [c[0] for c in self.hull]
        y = [c[1] for c in self.hull]
        dxf.thanDxfPlotPolyline(x, y)
        dxf.thanDxfSetLayer("DEM")
        self.dem.dxfout(dxf)
        dxf.thanDxfPlot(0,0,999)
