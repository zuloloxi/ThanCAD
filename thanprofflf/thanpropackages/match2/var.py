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

This is the professional part of ThanCad which is initially commercial.
"""
from math import pi, fabs, cos, sin
from p_gmath import dpt
from p_ggen import xfrange
from p_gvec import Vector3
try:               from thantrans import Tmatch
except ImportError:from p_gtkwid import Twid as Tmatch
from cline import Cline


class PlaneProjection:
    """An object which projects 3d point into a plane defined by two
    unit vectors na, nb. The vectors na and nb are perpendicular.
    """
    def __init__(self, na, nb):
        "Store the perpendicular unit vectors which define the projection plane."
        self.na = na
        self.nb = nb

    def project(self, cc):
        "Project cc to plane na x nb."
        a = Vector3(cc[0], cc[1], cc[2])
        xr = self.na * a
        yr = self.nb * a
        return xr, yr, cc[2]


class SimilarityAndProjection:
    "An object which combines projection on a plane and 2d similarity transformation."

    def __init__(self, proj1, tra1):
        "Get the coefficients of the plane projection and transformation."
        self.proj1 = proj1
        self.tra1 = tra1

    def project(self, c):
        "Do the plane projection and transformation."
        c1 = self.proj1.project(c)
        try: return self.tra1.calc2d(c1)
        except AttributeError: return self.tra1.project(c1)


def strdis(d): return "%.3f" % d
def strang(a): return "%.5f deg" % (dpt(a)*180/pi,)


def ICPconverged(er, erp, erpp, threshold, icp, prter):
        "Test if the ICP method converged and print warnings."
        if fabs(erp-er) < threshold and fabs(erpp-erp) < threshold:
            return True
        elif er > erp and erp > erpp:
            prter(Tmatch["WARNING: ICP STOPPED DUE TO INSTABILITY AFTER %d STEPS!"] % icp)
            return True
        return False


def iterPhiTheta(dth=pi/20):
    "Iterates phi from 0 to 2*pi and theta from -pi/2 to pi/2 and produces tangential and plane unit vectors."
    for phi in xfrange(0, 2*pi, dth):
        for theta in xfrange(-pi*0.5, pi*0.5, dth):
            t = Vector3(cos(theta)*cos(phi), cos(theta)*sin(phi), sin(theta))  #projection unit vector
            na, nb = t.normal2()
            yield t, na, nb


def vis23(gps3d, gps, rel, tra1, L, all=True):
    "Visualize the approximation for 3d-2d."
    import thanvar, p_gchart
    ch = p_gchart.ThanChart()
    rel.add2chart(ch, color="yellow")
    if all:
        gps.add2chart(ch, color="green")
        if tra1 != None:
            gpssim = Cline([tra1.calc2d(c[:3]) for c in gps], dmin=0.01, zcommon=0.0)
            gpssim.add2chart(ch, color="cyan")
    gpsnew = Cline([L.project(c[:3]) for c in gps3d], dmin=0.01, zcommon=0.0)
    gpsnew.add2chart(ch, color="blue")
    p_gchart.viswin(thanvar.thanfiles.ThanCad[2], ch)
