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
ThanDxfEmu is a producer class to import a drawing as it is being created.

    The class is based on the importation of dxf files; it works like the class
    ThanImportDxf of the p_gimdxf library.
    The class sends drawing commands to the drawing object dr (self.thanDr)
    which is a receiver class instance.
    Here the receiver class is the ThanCadDrSave class.
    The class emulates the p_gdxf library so that a program which calls p_gdxf
    to create drawing (in a .dxf file), can now create the drawing into ThanCad
    in real time, with no modifications.
"""

from .thandxfini import ThanDxfEmu
