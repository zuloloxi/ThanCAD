#!/usr/bin/python
# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

Package which find the optimum transaltion between SRTM and EGSA87.
"""
import p_ggen, p_ganneal
from demex import srtmerz, srtmersystz

class DEMAnnealable(p_ganneal.SAAnnealable):
    "An abstract class for objects that can be annealed."

    def prepare(self, thanPointZ, cps):
        "Make dem related initialisation."
        self.thanPointZ = thanPointZ
        self.cps = cps
        cmin = list(cps[0])
        cmax = list(cps[0])
        for cp in self.cps:
            for i in 0,1:
                cmin[i] = min(cmin[i], cp[i])
                cmax[i] = max(cmax[i], cp[i])
        dxy = min(cmax[0]-cmin[0], cmax[1]-cmin[1])*0.5   #Nyquist theorem
        if dxy < 100.0: return False, "Points span too small region."
        self.cen = [(a+b)*0.5 for a,b in zip(cmin, cmax)]
        self.cenEgsa = 485000.0, 4220000.0
        self.dxyEgsa = 400000.0
        self.dxy = self.dxyEgsa * 0.001
        self.state = p_ggen.Struct()
        self.state.dx = self.state.dy = 0.0
        self.esaved = None           #Previous cached energy
        return True, ""


    def analenergy(self):
        "It is called after every temperature step; for debugging."
#        self.dxy *= 0.7
        self.dxy *= 1.0


    def getDimensions(self):
        "Return the dimensionality of current configuration of the annealing object."
        return 2

    def energyState(self):
        "Return the (possibly cached) energy of the current configuration."
        if self.esaved != None:
            e = self.esaved
            self.esaved = None
            return e
        return self.energyStateHalf(self.state.dx, self.state.dy)

    def energyStateHalf(self, dx, dy):
        "Return the energy of the current configuration."
        dx = self.cenEgsa[0]-self.cen[0]+dx
        dy = self.cenEgsa[1]-self.cen[1]+dy
        n, e, e2 = srtmerz(self.thanPointZ, self.cps, dx, dy, dz=0.0)
        return e2

    def getState(self):
        "Return an object which fully reflects the state of the annealing object."
        return self.state.clone()

    def setState(self, state):
        "Replace current state of the anneling object with the one in variable state."
        self.state = state.clone()

    def changeState(self):
        "Randomly change the configuration of the problem."
#       changestate should not save current configuration before changing the
#       state (anneal() does this automatically)
        while True:
            while True:
                dx = self.state.dx + self.r.uniform(-self.dxy, self.dxy)
                if -self.dxyEgsa < dx < self.dxyEgsa: break
                print "dx exceeds"
            while True:
                dy = self.state.dy + self.r.uniform(-self.dxy, self.dxy)
                if -self.dxyEgsa < dy < self.dxyEgsa: break
                print "dy exceeds"
            e = self.energyStateHalf(dx, dy)
            if e < 999999.9: break
            print "State on sea!"
        self.esaved = e
        self.state.dx = dx
        self.state.dy = dy


def anneal(fw, name, thanPointZ, cps, prg):
    "Find the position of the points using simulated annealing."
    prg("GDEM: %s" % (name,), "info")
    prg("ΜΕΘΟΔΟΣ ΕΞΟΜΟΙΩΣΗΣ ΑΝΟΠΤΗΣΗΣ", "info")
    obj = DEMAnnealable()
    ok, terr = obj.prepare(thanPointZ, cps)
    if not ok:
        prg(terr, "can")
        return
    sa = p_ganneal.SimulatedAnnealing(tsteps=50, prt=prg)
    sa.anneal(obj)

    f = "%10d%15.3f%15.3f%15.3f%15.3f\n"
    f2 = "%10s%15s%15s%15s%15s\n"
    fw.write("GDEM: %s\n" % (name,))
    fw.write("ΜΕΘΟΔΟΣ ΕΞΟΜΟΙΩΣΗΣ ΑΝΟΠΤΗΣΗΣ\n")
    fw.write(f2 % ("Points", "DX", "DY", "Error Z", "Eff. error Z"))

    dx = obj.cenEgsa[0]-obj.cen[0]+obj.state.dx
    dy = obj.cenEgsa[1]-obj.cen[1]+obj.state.dy
    n, e, e2 = srtmerz(obj.thanPointZ, obj.cps, dx, dy, dz=0.0)

    fw.write("Minimum error:\n")
    fw.write(f % (n, dx, dy, e, e2))
    fw.write("Systematic and random error:\n")
    dz = srtmersystz(thanPointZ, cps, dx, dy)
    n, e, e2 = srtmerz(thanPointZ, cps, dx, dy, dz)
    fw.write(f2 % ("Points", "DX", "DY", "Systemat.er.Z", "Random er.Z"))
    fw.write(f % (n, dx, dy, dz, e))
