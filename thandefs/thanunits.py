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

This module provides for ThanCad drawings units customisation.
"""

from math import pi
from p_gmath import PI2
import p_ggen


class ThanUnits:
    "Object to aid in converting and printing units."

    angltran = dict(deg=180/pi, grad=200/pi, rad=1.0)
    distran  = dict(m=1.0, ft=12.0*2.54)
    _dis2num = dict(m=0, ft=1)
    _dis2text = p_ggen.dictInvert(_dis2num)
    _ang2num = dict(deg=0, rad=1, grad=2)
    _ang2text = p_ggen.dictInvert(_ang2num)
    _ori2num = {3:0, 12:1, 9:2, 6:3}
    _ori2text = p_ggen.dictInvert(_ori2num)
    _dir2num = {+1:0, -1:1}
    _dir2text = p_ggen.dictInvert(_dir2num)


    def __init__(self):
        "Set default values for printting and converting."
        self.distunit = "m"                 # Unit of distance measurements
        self.distdigs = 3                   # Number of digits to display for distance values
        self.anglunit = "deg"               # Unit of angular measurements
        self.angldigs = 4                   # Number of digits to display for angular values
        self.angldire = 1                   # Anti-clockswise angles are positive
        self.anglzero = 0.0                 # Zero is at 0.0 radians angle from the x-axis in the anticlockwise direction
        self.thanRecreate()

    def thanRecreate(self):
        "Recreates the transformation functions."
        self.radcoef = self.angltran[self.anglunit]
        if self.angldigs >= 0: self.formang = "%%.%df%s" % (self.angldigs, self.anglunit)
        else:                  self.formang = "%%d%s"    % (self.anglunit,)
        if self.distdigs >= 0: self.formdis = "%%.%df" % (self.distdigs, )
        else:                  self.formdis = "%d"

    def rad2unit(self, th):
        "Convert angle from rad to user defined units."
        return ((th*self.angldire) % PI2) * self.radcoef

    def rad2unitdir(self, th):
        "Convert direction angle from rad to user defined units."
        return (((th-self.anglzero)*self.angldire) % PI2) * self.radcoef

    def unit2rad(self, th):
        "Convert angle from user defined units to rad."
        return (th*self.angldire/self.radcoef) % PI2

    def unit2raddir(self, th):
        "Convert direction angle from user defined units to rad."
#        (th-st)*si * co = x => (th-st)*si = x/co => th-st = x/co / si => th = x/co / si + st =>
#        th = x/co * si + st => th = x*si/co+st
        return (th*self.angldire/self.radcoef + self.anglzero) % PI2

    def strang(self, th):
        if self.angldigs >= 0: return self.formang % self.rad2unit(th)
        else:                  return self.formang % int(self.rad2unit(th))

    def strdir(self, th):
        if self.angldigs >= 0: return self.formang % self.rad2unitdir(th)
        else:                  return self.formang % int(self.rad2unitdir(th))

    def strdir(self, th):
        if self.angldigs >= 0: return self.formang % self.rad2unitdir(th)
        else:                  return self.formang % int(self.rad2unitdir(th))

    def strdis(self, d):
        if self.distdigs >= 0: return self.formdis % d
        else:                  return self.formdis % int(d)

    def strcoo(self, cc):
        "Prints the n coordinates of a point."
        t = [self.strdis(c1) for c1 in cc]
        return " ".join(t)

    def thanConfig(self, distunit=None, distdigs=None, anglunit=None, angldigs=None, angldire=None, anglzero=None):
        "Checks and sets various options."
        if distunit is not None:
            if distunit not in self.distran: raise ValueError("Valid distance units: "+", ".join(self.distran.keys())) #works for python2,3
            self.distunit = distunit
        if distdigs is not None:
            self.distdigs = int(distdigs)
            if self.distdigs < -1 or self.distdigs > 15: raise ValueError("Invalid distance digits: %d" % self.distdigs)
        if anglunit is not None:
            if anglunit not in self.angltran: raise ValueError("Valid angle units: "+", ".join(self.angltran.keys()))  #works for python2,3
            self.anglunit = anglunit
        if angldigs is not None:
            self.angldigs = int(angldigs)
            if self.angldigs < -1 or self.angldigs > 15: raise ValueError("Invalid angle digits: %d" % self.angldigs)
        if angldire is not None:
            angldire = int(angldire)
            if angldire not in (1, -1): raise ValueError("Angle direction should be 1 or -1.")
            self.angldire = angldire
        if anglzero is not None:
            anglzero = int(anglzero)
            if anglzero not in (3,12,9,6): raise ValueError("Angle zero should be 3, 12, 9 or 6 (o'clock).")
            self.anglzero = ((3-anglzero)*pi/6) % PI2
        self.thanRecreate()

    def thanExpThc(self, fw):
        "Export units to .thc file."
        fw.writeBeg("UNITS")
        fw.pushInd()
        fw.writeAtt("distance", "%s %d" % (self.distunit, self.distdigs))
        i = int(3.0 - self.anglzero * 6.0/pi+0.1) % 12
        if i == 0: i = 12
        fw.writeAtt("angle", "%s %d %d %d" % (self.anglunit, self.angldigs, self.angldire, i))
        fw.popInd()
        fw.writeEnd("UNITS")

    def thanImpThc(self, fr):
        "Import units from .thc file."
        fr.readBeg("UNITS")
        distunit, distdigs = fr.readAtt("distance")
        anglunit, angldigs, angldire, anglzero = fr.readAtt("angle")
        fr.readEnd("UNITS")
        self.thanConfig(distunit, distdigs, anglunit, angldigs, angldire, anglzero)


def test():
    "Tests the ThanOpt class."
    op = ThanUnits()
    op.thanConfig(anglzero=12, angldire=-1)
    while True:
        th = p_ggen.inpFloat("Give angle in radians: ", ("",))
        if th == "": break
        for un in op.angltran:
            op.thanConfig(anglunit=un)
            th1 = op.rad2unit(th)
            print("in", un, ":", th1, op.strang(th))

    while True:
        th = p_ggen.inpText("Give angle and unit: ", ("",))
        if th == "": break
        th, un = th.split()
        th = float(th)
        op.thanConfig(anglunit=un)
        th1 = op.unit2rad(th)
        print("in rad :", th1, op.strang(th1))

    a = 120.498
    print("meters:", op.strdis(120.498))
    op.thanConfig(distdigs=3)
    print("meters:", op.strdis(120.498))
    op.thanConfig(distdigs=-1)
    print("meters:", op.strdis(120.498))

if __name__ == "__main__": test()
