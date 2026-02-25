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

This module defines an object which is also a ThanTri triangulation object.
The triangulation is based on Stamos' robust triangulation algorithm
"""

import p_gtri
from thantrans import T
from .thanobject import ThanObject


class ThanTri(p_gtri.ThanTri, ThanObject):
    """This module defines an object which is also a ThanTri triangulation object.

    Some methods such as thanImpthc1() are defined in p_gtri.ThanTri."""
    thanObjectName = "TRIANGULATION"    # Name of the objects's class
    thanObjectInfo = "A nonconvex triangulation."
    thanVersions = ((1,0),)

    def thanList(self, than):
        "Shows information about the Triangulation object."
        n = 0
        for _ in self.itertriangles(): n += 1
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %d\n" % (T["Processed points: "], len(self.ls)))
        than.write("%s %d\n" % (T["Triangles       : "], n))
