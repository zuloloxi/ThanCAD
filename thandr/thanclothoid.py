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

This module defines the clothoid element.
"""
from p_gmath import klotxy

class ThanClothoid(ThanCurve):
    thanElementName = "CLOTHOID"    # Name of the element's class

    def thanSet(self, cL1, theta, A, L1, L2, pr):
        "Set the parameters of the clothoid."
        assert L2 > L1, "L1>=L2: this might be relaxed, but now it is an error :)"
        self.ca = ca                    # This is the first point of the clothoid (i.e. x,y for L=L1)
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
        for L in L1, L2:
            ccl = list(self.cp)
            ccl[:2] = klotXy(self.A, L, self.pr)
            ccl.append(L)
            cp.append(ca)
        dx = self.ca[0]-cp[0][0]
        dy = self.ca[1]-cp[0][1]

        j = 1
        while j < len(cc):
            i = j - 1
            xm = (cc[j][0]+cc[i][0])*0.5
            ym = (cc[j][1]+cc[i][1])*0.5
            Lm = (cc[j][-1]+cc[i][-1])*0.5
            xc, yc = klotXy(self.A, Lm, self.pr)
            if hypot(xc-cm, yc-ym) <= dmax:
                j += 1
            else:
                ca = list(self.cp)
                ca[:2] = xc, yc
                ca.append(L)
                cc.insert(j, ca)
        self.thanRotateSet(self.cp, self.theta)
        self.thanRotateXyn(cc)
        self.ci = cc
        return cc


    def curveNearest2(ca):
        "Given an approximate nearest point of the curve, find the exact point."
        cn, i, t = self.thanPntNearest2(self.cc)
        L = cn[-1]
        cn[:2] = klotXy(self.A, L, self.pr)
        return cn, i, t
