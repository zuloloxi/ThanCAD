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

This module defines an object which is also a NonCartesian transformation object
which transforms between ThanCad's world coordinates and coordinates of the
non-cartesian system defined by 2 non-orthogonal axes.
"""
import  p_gmath
from thantrans import T
from .thanobject import ThanObject


class NonCartesian(p_gmath.NonCartesian, ThanObject):
    thanObjectName = "COSYS"    # Name of the objects's class
    thanObjectInfo = "(Non) cartesian coordinate system in 2D."
    thanVersions = ((1,0),)

    def thanList(self, than):
        "Shows information about the coordinate-system object."
        cor = list(than.elevation)
        cor[:2] = self.L[:2]
        cx = list(cor)
        cx[:2] = self.L[2:4]
        cy = list(cor)
        cy[:2] = self.L[4:]
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %s\n" % (T["Origin of X,Y axes: "], than.strcoo(cor)))
        than.write("%s %s\n" % (T["X-axis unit vector: "], than.strcoo(cx)))
        than.write("%s %s\n" % (T["Y-axis unit vector: "], than.strcoo(cy)))

    def thanExpThc1(self, fw):
        "Saves the coordinate system to a .thc file."
        for i,att in enumerate("origin unitx unity".split()):
            fw.writeBeg(att)
            fw.pushInd()
            fw.writeNode(self.L[i*2:i*2+2])
            fw.popInd()
            fw.writeEnd(att)

    def thanImpThc1(self, fr, ver, than):
        "Reads the coordinate system from a .thc file."
        for i,att in enumerate("origin unitx unity".split()):
            fr.readBeg(att)
            cp = fr.readNode()
            self.L[i*2:i*2+2] = cp[:2]
            fr.readEnd(att)
