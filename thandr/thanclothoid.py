# -*- coding: iso-8859-7 -*-

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

This module defines the clothoid element.
"""
from math import hypot
from p_gmath import klotXy
from .thanline import ThanCurve

class ThanClothoid(ThanCurve):
    thanElementName = "CLOTHOID"    # Name of the element's class

    def thanSet(self, cL1, theta, A, L1, L2, pr):
        "Set the parameters of the clothoid."
        assert L2 > L1, "L1>=L2: this might be relaxed, but now it is an error :)"
        self.ca = cL1                   # This is the first point of the clothoid (i.e. x,y for L=L1)
        self.theta = theta              # Azimuth of the tangent at the starting point
        self.L1 = L1
        self.L2 = L2
        self.A = A
        self.pr = pr
        self.cp = []                    # interpolated points


    def thanIsNormal(self):
        "Check if the clothoid is degenerate."
        return True


    def interp(self, dmax=1.0):
        "Find interpolation points in the clothoid so that no more than dmax difference."
        cp = []
        xcl, ycl = klotXy(self.A, self.L1, self.pr)
        dx = self.ca[0]-xcl
        dy = self.ca[1]-ycl
        for L in self.L1, self.L2:
            ccl = list(self.ca)
            ccl[:2] = klotXy(self.A, L, self.pr)
            ccl.append(L)
            cp.append(ccl)
        dx = self.ca[0]-cp[0][0]
        dy = self.ca[1]-cp[0][1]

        j = 1
        while j < len(cp):
            i = j - 1
            xm = (ccl[j][0]+ccl[i][0])*0.5
            ym = (ccl[j][1]+ccl[i][1])*0.5
            Lm = (ccl[j][-1]+ccl[i][-1])*0.5
            xc, yc = klotXy(self.A, Lm, self.pr)
            if hypot(xc-xm, yc-ym) <= dmax:
                j += 1
            else:
                ccl = list(self.ca)
                ccl[:2] = xc, yc
                ccl.append(Lm)
                cp.insert(j, ccl)
        self.thanRotateSet(self.ca, self.theta)
        self.thanRotateXyn(cp)
        self.ci = cp
        return cp


    def curveNearest2(self, ca):
        "Given an approximate nearest point of the curve, find the exact point."
        cn, i, t = self.thanPntNearest2(self.cc)
        L = cn[-1]
        cn[:2] = klotXy(self.A, L, self.pr)
        return cn, i, t
