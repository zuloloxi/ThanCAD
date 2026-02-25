##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module defines various states, i.e. as the user clicks a point or
a highlighted elements is selected.
"""
from math import hypot
import Tkinter
from thantkconst import *
from thanvar import thanLogTk
from thantkguigeneric import ThanStateGeneric


class ThanStatePoint(ThanStateGeneric):
    "An object which interprets mouse click to points."

    def __init__(self, proj):
        "Initialize object."
        self.thanProj = proj


    def thanOnClick(self, event, x, y, cc):
        "Well, here is what should be done when mouse clicks."
        dc = self.thanProj[2].thanCanvas
        dc.thanLastResult = cc, None
        dc.thanState = THAN_STATE_NONE
        dc.thanOState = ThanStateGeneric(self.thanProj)


class ThanStateSelem(ThanStateGeneric):
    "An object which interprets mouse click to a selection of highlighted element."

    def __init__(self, proj):
        "Initialize object."
        self.thanProj = proj
        dc = self.thanProj[2].thanCanvas
        dc.thanTempItems.add("e0")


    def thanOnClick(self, event, x, y, cc):
        "Well, here is what should be done when mouse clicks."
        dc = self.thanProj[2].thanCanvas
        dc.delete("e0")
        dc.thanTempItems.remove("e0")
        dc.thanLastResult = dc.thanOsnap.selem, None
        dc.thanState = THAN_STATE_NONE
        dc.thanOState = ThanStateGeneric(self.thanProj)
