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

This module defines the architectural Floor Plan Design. The FPD is computed using
Stamos' automated simulated annealing algorithm. No state of the FPD is retained
the algorithm is run without prior state. The only state is the position of the FPD
in the drawing (multiple FPDs may be drawing on the same ThanDrawing).
"""

from thantrans import T, Tarch
from .thanobject import ThanObject


class ThanFplan(ThanObject):
    thanObjectName = "FLOORPLAN"    # Name of the objects's class
    thanObjectInfo = "Automated floor plan."
    thanVersions = ((1,0),)

    def __init__(self):
        "Set initial values to the floorplan origin."
        self.xor = self.yor = 0.0

    def run(self, proj, v):
        "Run the automatic floor plan design algorithm."
        import thanpackages.fplan
        thanpackages.fplan.simroom.thancadMain(proj, v, self.xor, self.yor)
        self.xor += v.entWidth*1.20
        if self.xor > 3.01*1.20*v.entWidth:
            self.xor = 0.0
            self.yor -= v.entHeight*1.2

    def thanList(self, than):
        "Shows information about the FloorPlan object."
        c = list(than.elevation)
        c[:2] = self.xor, self.yor
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %s\n" % (Tarch["Next floor plan position:"], than.strcoo(c)))

    def thanExpThc1(self, fw):
        "Saves the origin of the next floor plan to a .thc file."
        fw.writeBeg("origin")
        fw.pushInd()
        fw.writeNode((self.xor, self.yor))
        fw.popInd()
        fw.writeEnd("origin")

    def thanImpThc1(self, fr, ver, than):
        "Reads the origin of the next floor plan from a .thc file."
        fr.readBeg("origin")
        cp = fr.readNode()
        self.xor, self.yor = cp[:2]
        fr.readEnd("origin")
