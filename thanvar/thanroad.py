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

This module computes a road node with circular arc.
"""
from math import pi, sin, cos, hypot
import tkinter
import p_ggen, p_gvec
from p_gmath import dpt


def calcRoadNode(xk1, yk1, xk2, yk2, xk3, yk3, r2):
        k1 = p_ggen.Struct()
        self = p_ggen.Struct()
        k3 = p_ggen.Struct()
        k1.pk = p_gvec.Vector2(xk1, yk1)
        self.pk = p_gvec.Vector2(xk2, yk2)
        k3.pk = p_gvec.Vector2(xk3, yk3)
        self.R = r2

        self.t12 = (self.pk-k1.pk).unit()       # Εγινε έλεγχος στην checkXy
        self.t23 = (k3.pk-self.pk).unit()       # Εγινε έλεγχος στην checkXy
        a12 = self.t12.atan2()                  # Εγινε έλεγχος στην checkXy
        a23 = self.t23.atan2()                  # Εγινε έλεγχος στην checkXy

        dfkl = dpt(a23 - a12); self.pr = 1.0
        if dfkl > pi: dfkl = 2.0*pi - dfkl; self.pr = -1.0

        self.phi = dpt(dfkl)
        assert self.phi > 0, "Επρεπε να είχε βρεθεί στη self.check(): beta>0"
        assert self.phi < pi, "Well, this is impossible since dfkl<pi !!"
        self.LK = self.phi * self.R

        self.rat = a12
        at = kyklXy(self.R, self.LK, self.pr).rot(self.rat)   # This should work

        (d12, d23) = at.anal(self.t12, self.t23)        # This should work
                                                        # since beta!=0 or pi
        self.pa = self.pk - d12 * self.t12
        self.pt = self.pa + at

        self.T1 = abs(self.pa - self.pk)
        self.T2 = abs(self.pt - self.pk)

        tc = (-self.t12+self.t23).unit()
        beta = pi-dfkl
        y = self.R/sin(beta*0.5)
        self.pc = self.pk + y*tc
        self.theta1 = dpt((self.pa-self.pc).atan2())*180/pi
        self.theta2 = dpt((self.pt-self.pc).atan2())*180/pi
        if self.pr < 0.0: self.theta1, self.theta2 = self.theta2, self.theta1

        self.delta = y - self.R
        self.pm = self.pk + self.delta*tc                # Middle of circlular curve
        return self


def calcRoadNodeR(xk1, yk1, xk2, yk2, xk3, yk3, delta):
        k1 = p_ggen.Struct()
        self = p_ggen.Struct()
        k3 = p_ggen.Struct()
        k1.pk = p_gvec.Vector2(xk1, yk1)
        self.pk = p_gvec.Vector2(xk2, yk2)
        k3.pk = p_gvec.Vector2(xk3, yk3)
        self.delta = delta

        self.t12 = (self.pk-k1.pk).unit()       # Εγινε έλεγχος στην checkXy
        self.t23 = (k3.pk-self.pk).unit()       # Εγινε έλεγχος στην checkXy
        a12 = self.t12.atan2()                  # Εγινε έλεγχος στην checkXy
        a23 = self.t23.atan2()                  # Εγινε έλεγχος στην checkXy

        dfkl = dpt(a23 - a12); self.pr = 1.0
        if dfkl > pi: dfkl = 2.0*pi - dfkl; self.pr = -1.0

        beta = pi-dfkl
#       R+delta = R/sin(beta*0.5) => delta = R/sin(beta*0.5) - R =>
        self.R = delta/(1/sin(beta*0.5) - 1)

        self.phi = dpt(dfkl)
        assert self.phi > 0, "Επρεπε να είχε βρεθεί στη self.check(): beta>0"
        assert self.phi < pi, "Well, this is impossible since dfkl<pi !!"
        self.LK = self.phi * self.R

        self.rat = a12
        at = kyklXy(self.R, self.LK, self.pr).rot(self.rat)   # This should work

        (d12, d23) = at.anal(self.t12, self.t23)        # This should work
                                                        # since beta!=0 or pi
        self.pa = self.pk - d12 * self.t12
        self.pt = self.pa + at

        self.T1 = abs(self.pa - self.pk)
        self.T2 = abs(self.pt - self.pk)

        y = self.R/sin(beta*0.5)
        tc = (-self.t12+self.t23).unit()
        self.pc = self.pk + y*tc
        self.theta1 = dpt((self.pa-self.pc).atan2())*180/pi
        self.theta2 = dpt((self.pt-self.pc).atan2())*180/pi
        if self.pr < 0.0: self.theta1, self.theta2 = self.theta2, self.theta1

        self.pm = self.pk + self.delta*tc                # Middle of circlular curve
        return self


def kyklXy(R, L, pr):
    "Points on circle."
    f = L/R
    return p_gvec.Vector2(R*sin(f), (R-R*cos(f))*pr)


def tkRoadNode(x1, y1, x2, y2, x3, y3, r2, dc, fill, dash, width, tags):
    "Draws a road curve; 2 line segments and an arc between."
    nod = calcRoadNode(x1, y1, x2, y2, x3, y3, r2)
    dth = (nod.theta2-nod.theta1) % 360.0
    th = 360.0-nod.theta2
#    print "%6.1f%6.1f -> %6.1f%6.1f" % (nod.theta1, nod.theta2, th, th+dth)

    item1 = dc.create_line(x1, y1, nod.pa.x, nod.pa.y, fill=fill, dash=dash, width=width, tags=tags)
    item2 = dc.create_arc(nod.pc.x-r2, nod.pc.y-r2, nod.pc.x+r2, nod.pc.y+r2,
            start=th, extent=dth, style=tkinter.ARC, outline=fill, dash=dash, width=width, tags=tags)
    item3 = dc.create_line(nod.pt.x, nod.pt.y, x3, y3, fill=fill, dash=dash, width=width, tags=tags)
    item4 = dc.create_line(nod.pa.x, nod.pa.y, x2, y2, nod.pt.x, nod.pt.y,
            fill=fill, tags=tags, stipple="gray25")
    return (item1, item2, item3, item4), (nod.pt.x, nod.pt.y)


def tkRoadNodeR(x1, y1, x2, y2, x3, y3, xmouse, ymouse, dc, ct, fill, dash, width, tags):
    "Draws a road curve; 2 line segments and an arc between."
    delta = hypot(x2-xmouse, y2-ymouse)
    nod = calcRoadNodeR(x1, y1, x2, y2, x3, y3, delta)
    r2 = nod.R
    dth = (nod.theta2-nod.theta1) % 360.0
    th = 360.0-nod.theta2
#    print "%6.1f%6.1f -> %6.1f%6.1f" % (nod.theta1, nod.theta2, th, th+dth)

    item1 = dc.create_line(x1, y1, nod.pa.x, nod.pa.y, fill=fill, dash=dash, width=width, tags=tags)
    item2 = dc.create_arc(nod.pc.x-r2, nod.pc.y-r2, nod.pc.x+r2, nod.pc.y+r2,
            start=th, extent=dth, style=tkinter.ARC, outline=fill, dash=dash, width=width, tags=tags)
    item3 = dc.create_line(nod.pt.x, nod.pt.y, x3, y3, fill=fill, dash=dash, width=width, tags=tags)
    item4 = dc.create_line(nod.pa.x, nod.pa.y, x2, y2, nod.pt.x, nod.pt.y,
            fill=fill, width=width, tags=tags, stipple="gray25")
    rr, _ = ct.local2GlobalRel(r2, r2)
    item5 = dc.create_text(x2, y2, text="R=%d" % int(rr), fill=fill)
    return (item1, item2, item3, item4, item5), (nod.pt.x, nod.pt.y)
