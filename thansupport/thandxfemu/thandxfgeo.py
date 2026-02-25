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

class ThanDxfGeo:
    "Mixin to geometry of .dxf file."

#===========================================================================

    def __init__(self):
        "No initialisation needed."
        pass

#===========================================================================

    def thanDxfTop (self, xx, yy):
        "Transforms a 2d point to local coordinates."
        return (self.thanPXar + (xx-self.thanXar) * self.thanXfac,
                self.thanPYar + (yy-self.thanYar) * self.thanYfac)

#===========================================================================

    def thanDxfTop3 (self, xx, yy, zz):
        "Transforms a 3d point to local coordinates."
        return (self.thanPXar + (xx-self.thanXar) * self.thanXfac,
                self.thanPYar + (yy-self.thanYar) * self.thanYfac,
                self.thanPZar + (zz-self.thanZar) * self.thanZfac)

#===========================================================================

    def thanDxfSetFactor(self, ff):
        "Assigns an overall absolute scale to the output of dxf."
        ff1 = ff / self.thanFact
        self.thanXfac *= ff1
        self.thanYfac *= ff1
        self.thanZfac *= ff1

        self.thanFact = ff

#===========================================================================

    def thanDxfLocref(self, xx, yy, fx, fy):
        "Assigns relative scales to x, y output of dxf."
        self.thanXar = xx
        self.thanYar = yy
        self.thanPXar = self.thanPXnow
        self.thanPYar = self.thanPYnow
        if fx > 0: self.thanXfac = fx * self.thanFact
        if fy > 0: self.thanYfac = fy * self.thanFact

#===========================================================================

    def thanDxfLocref3(self, xx, yy, zz, fx, fy, fz):
        "Assigns relative scales to x, y, z output of dxf."
        self.thanXar = xx
        self.thanYar = yy
        self.thanYar = zz
        self.thanPXar = self.thanPXnow
        self.thanPYar = self.thanPYnow
        self.thanPZar = self.thanPZnow
        if fx > 0: self.thanXfac = fx * self.thanFact
        if fy > 0: self.thanYfac = fy * self.thanFact
        if fz > 0: self.thanZfac = fz * self.thanFact

#===========================================================================

    def thanDxfWhere(self):
        "Returns the current position of the 'pen'."
        return ((self.thanPXnow - self.thanPXar) / self.thanXfac + self.thanXar,
                (self.thanPYnow - self.thanPYar) / self.thanYfac + self.thanYar)

#===========================================================================

    def thanWhere3(self):
        "Returns the current position of the 'pen'."
        return ((self.thanPXnow - self.thanPXar) / self.thanXfac + self.thanXar,
                (self.thanPYnow - self.thanPYar) / self.thanYFac + self.thanYar,
                (self.thanPZnow - self.thanPZar) / self.thanZFac + self.thanZar )
