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

The package creates automatically architectural things such as stairs.
The subpackage contains the commands which handle architecture related
procedures.
This module implements a rotation object.
"""

from math import cos, sin


class Similar2D(object):
    """Keeps the rotation, translation and scale."""

    def __init__(self, cu=(0.0,0.0), gon=0.0, am=1.0, rotcenter=(0.0, 0.0)):
        "Create the object; first rotation around (0,0,0), then scale around (0,0,0), then translation."
        self.cu = list(cu)
        self.gon = gon
        self.am = am
        self.setRotcenter(rotcenter)


    def setRotcenter(self, rotcenter):
        """Arrange the coefficients so that we have rotation with respect to rotcenter.

        This means that we rotate and scale around rotcenter and then we translate.
        Note that this is NOT the same transformation as before.
        Alternatively we could have a constructor which accepts the angles, the scale
        the center of rotation AND the translation, and produces the same Transformation
        object that setRotcenter() does."""
        self.a = (-self.am*rotcenter[0]*cos(self.gon) + rotcenter[0] + self.cu[0],
                  -self.am*rotcenter[1]*sin(self.gon) + rotcenter[1] + self.cu[1],
                   self.am*cos(self.gon),
                   self.am*sin(self.gon)
                 )


    def calc2d(self, cp):
        "Transform the coordinates of a 2d point."
        xr, yr = cp[:2]
        a = self.a
        cc = list(cp)
        cc[0] = a[0] + a[2]*xr + a[3]*yr
        cc[1] = a[1] + a[2]*yr - a[3]*xr
        return cc
