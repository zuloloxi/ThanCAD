# -*- coding: iso-8859-7 -*-
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

Extensions to the dxf format.

These are needed because of the dreadful and unnecessary complexity of the
dxf format.
THANCADSPECIFIC: Extensions specific to ThanCad:
                 Nested layers
                 More layer attributes
THANINTELLICAD:  Extensions which, if present, do not cause
                 intellicad to complain
THANCAD:         ThanCad is able to cope with all extensions
"""

THANCADSPECIFIC = 1
THANINTELLICAD  = 1 << 1
THANCAD         = THANCADSPECIFIC | THANINTELLICAD

thanCadCodes = \
{ "linetype"   :   6,
  "color"      :  62,
  "noplot"     : 290,
  "lineweight" : 370,
  "frozen"     :  71,
  "locked"     :  72,
  "off"        :  73,
}

ZDEFAULT = 0.0

thanCadAtts = {}
for code,att in thanCadCodes.items(): thanCadAtts[att] = code   #works for python2,3
