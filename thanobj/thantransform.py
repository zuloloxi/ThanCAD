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

This module defines the an object which stores the default transformation (or
projective transformation) of a ThanDrawing.
"""
import p_gmath
from thantrans import T, Tmatch
import thanopt
if thanopt.thancon.thanFrape.fflf:
    from p_gsar import readProj
else:
    from p_gmath import readProj
from .thanobject import ThanObject


class ThanTransformation(ThanObject):
    thanObjectName = "TRANSFORMATION"    # Name of the objects's class
    thanObjectInfo = "Transformation between (3D) coordinate systems."
    thanVersions = ((1,0),)

    def __init__(self, transformation=None):
        "Obtain the transformartion object."
        if transformation is None: self.transformation = p_gmath.Polynomial1Projection()  # Identity: x = X, y = Y
        else:                      self.transformation = transformation
        self.inverted = None

    def transform(self, cor):
        "Transform the coordinates of a point."
        return None

    def transformn(self, corn):
        "Transform the coordinates of many points."
        return None

    def invert(self):
        "Compute the inverted transformation, save it and return it."
        return None #Return None if transformation can not be inverted, or inversion not implemented

    def invtransform(self, cta):
        "Invert the coordinates of a transformed point to get the original."
        return None

    def invtransformn(self, ctan):
        "Invert the coordinates of many transformed points to get the original."
        return None



class ThanProjection(ThanTransformation):
    thanObjectName = "PROJECTION"    # Name of the objects's class
    thanObjectInfo = "Projection of 3D to 2D coordinate system."
    thanVersions = ((1,0),)

    def transform(self, cor):
        "Transform the coordinates of a point."
        tra = self.transformation
        return tra.project(cor)

    def transformn(self, corn):
        "Transform the coordinates of many points."
        tra = self.transformation
        pr = tra.project
        return [pr(cor) for cor in corn]

    def thanList(self, than):
        "Shows information about the transformation object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s: %s\n" % (Tmatch["Transformation type"], self.transformation.name,))

    def thanExpThc1(self, fw):
        "Saves the projection coefficients to a .thc file."
        self.transformation.write(fw)

    def thanImpThc1(self, fr, ver, than):
        "Reads the projection coefficients from a .thc file."
        self.transformation = readProj(fr)
