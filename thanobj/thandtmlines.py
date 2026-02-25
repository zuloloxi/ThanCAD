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

This module defines an object which holds a set of lines which acts as an DTM.
The lines are different and independent from the ThanLines of the ThanDrawing.
"""
import p_gtri
from thantrans import T
from .thanobject import ThanObject


class ThanDTMlines(ThanObject):
    thanObjectName = "DTMLINES"    # Name of the objects's class
    thanObjectInfo = "Set of 3D lines which behaves as a Digital Terrain Model."
    thanVersions = ((1,0),)

    def __init__(self, dxmax=20.0, dext=50.0):
        "Initialize DEM."
        self.dtm = p_gtri.ThanDTMlines(dxmax, dext)


    def thanIsNormal(self):
        "Returns False if the image the DEM was not found."
        return True           #for compatibility with thanDEMusgs

    def thanList(self, than):
        "Shows information about the DTMLines object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        scen = " ".join(map(than.strdis, self.dtm.thanCen()))   #works for python2,3
        than.write("%s %s\n" % (T["Centroid:"], scen))
        than.write("%s %s\n" % (T["Max X distance of line segments:"], than.strdis(self.dtm.thanDxmax)))
        than.write("%s %s\n" % (T["X extension for intersections  :"], than.strdis(self.dtm.thanDext)))
        than.write("%s %d\n" % (T["Original  line segments: "], self.dtm.thanNori))
        than.write("%s %d\n" % (T["Processed line segments: "], len(self.dtm.thanLines)))

    def thanExpThc1(self, fw):
        "Saves the lines of the DTM to a .thc file."
        self.dtm.thanExpThc1(fw)

    def thanImpThc1(self, fr, ver, than):
        "Reads the lines of the DTM from a .thc file."
        self.dtm.thanImpThc1(fr, ver, than)
