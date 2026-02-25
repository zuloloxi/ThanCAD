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

This module defines a photogrammetric model. This is a name for the object,
a description and the left and the right image of the model.
"""
import p_ggen
from thantrans import T
from thanopt.thancadconf import thanUndefPrefix     #"<undefined>"
from .thanobject import ThanObject


class ThanPhotModel(ThanObject):
    "An object which stores photogrammetric data."
    thanObjectName = "PHOTMODEL"    # Name of the objects's class
    thanObjectInfo = "Optical photogrammetric model."
    thanVersions = ((1,0),)

    def __init__(self, model=None):
        "Create an initialised or empty model."
        if model is None:
            self.model = None
        else:
            m = self.model = p_ggen.Struct("Photogrammetric model")
            m.nam      = thanUndefPrefix
            m.desc     = ""
            m.filLeft  = thanUndefPrefix
            m.filRight = thanUndefPrefix

    def model2dialog(self):
        "Create a structure with model attributes expected by ThanCad's dialog."
        v = p_ggen.Struct()
        m = self.model
        v.entName  = m.nam
        v.entDesc  = m.desc
        v.filLeft  = m.filLeft
        v.filRight = m.filRight

    def thanList(self, than):
        "Shows information about the photogrammetric model object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        m = self.model
        than.write("%s %s\n" % (T["Model name       : "], m.nam))
        than.write("%s %s\n" % (T["Model description: "], m.desc))
        than.write("%s %s\n" % (T["Left  image: "], m.filLeft))
        than.write("%s %s\n" % (T["Right image: "], m.filRight))
