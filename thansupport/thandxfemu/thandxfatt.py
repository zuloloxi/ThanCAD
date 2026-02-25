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
"""

class ThanDxfAtt:
    "Mixin for setting and writing attributes."

    def __init__(self):
        "Initialisation is not needed, but for compatibility."
        pass

    def thanDxfSetLayer(self, la):
        "Sets the linetype for subsequent entities."
        self.thanLayer = la

    def thanDxfSetLtype(self, lt):
        "Sets the linetype for subsequent linear entities."
        self.thanLtype = lt

    def thanDxfSetColor(self, co):
        "Sets the color for subsequent entities."
        self.thanColor = co

    def thanDxfSetPlineWidth(self, w1, w2):
        "Sets the text style for subsequent text entities."
        self.thanPlineWidth = (w1, w2)

    def thanDxfSetTstyle(self, lt):
        "Sets the text style for subsequent text entities."
        self.thanTstyle = lt
