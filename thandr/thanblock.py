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

This module defines the block element.
"""

from math import fabs, pi, cos, sin, tan, hypot, atan2
import bisect
from p_gmath import PI2, thanintersect, thanNearx
from p_ggen import prg, thanUnicode
from thanvar import Canc
from thantrans import T
from . import thanintall, thanarc
from .thanelem import ThanElement



class ThanInsertedBlock(ThanElement):
    "A instance of a block inserted into a drawing."
    thanElementName = "BLOCK"    # Name of the element's class

    def thanSet(self, name, cc, factors, theta):
        """Sets the attributes of the inserted block.
        factors are the scale factors for each coordinate dimension.
        theta is the rotation angle of the block within the xy plane.
        cp are the insertion points of the elements.
        """

class ThanBlock(ThanElement):
    "A block which contains other elements."
    thanElementName = "BLOCK"    # Name of the element's class
    def thanSet(self, name, elems, cc, retainlayers=False):
        """Sets the attributes of the block.

        name is the name of the block
        elems are the elements which comprise the block.
        cc is the reference point of the block.
        """
        self.name = name
        self.elems = list(elems)
        self.cc = list(cc)
        self.retain = retainlayers
        assert retainlayers is False, "retain layers has not yet been implemented :("
