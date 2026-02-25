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

This module defines overall constants.
"""

import p_ggen
THANBYPARENT = p_ggen.Struct("<ByParent>")
THANPERSONAL = p_ggen.Struct("<Personal>")
thanMdimj    = 3                  # Number of dimensions for a point
THANLC = "__"                     # separator of layer names in dxf, and ThanCad dxf linetypes
thanFrape       = p_ggen.Struct()
thanFrape.ortho = False
thanFrape.fflf  = False
thanFrape.civil = False
thanFrape.photo = True
thanFrape.stereo= False
thanFrape.urban = True
thanFrape.architect = True
thanFrape.thermo = True


class ThanCadError(Exception): pass
class ThanDegenerateError(ThanCadError): pass
