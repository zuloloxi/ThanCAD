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

It implements various constants for the TkGui of ThanCad.
"""

import enum


class THAN_STATE(enum.Enum):
    NONE      = 1 #enum.auto()
    INTERRUPT = 2 #enum.auto()
    POINT     = 3 #enum.auto()
    POINT1    = 4 #enum.auto()
    LINE      = 5 #enum.auto()
    LINE2     = 6 #enum.auto()
    POLAR     = 7 #enum.auto()
    AZIMUTH   = 8 #enum.auto()
    CIRCLE    = 9 #enum.auto()
    CIRCLE2   = 10 #enum.auto()
    CIRCLE3   = 11 #enum.auto()
    ARC       = 12 #enum.auto()
    RECTANGLE = 13 #enum.auto()
    RECTRATIO = 14 #enum.auto()
    TEXT      = 15 #enum.auto()
    TEXTRAW   = 16 #enum.auto()   #for text without strip()
    MOVE      = 17 #enum.auto()
    ROADP     = 18 #enum.auto()
    ROADR     = 19 #enum.auto()
    SPLINEP   = 20 #enum.auto()
    ELLIPSEB  = 21 #enum.auto()
    SNAPELEM  = 22 #enum.auto()
    #UNFOCUSED = enum.auto()

    DRAGFOLLOWS = 23 #enum.auto()    # Drom this state on, all states are for dragging

    PANDYNAMIC  = 24 #enum.auto()
    ZOOMDYNAMIC = 25 #enum.auto()

    DRAG2BEGIN = 26 #enum.auto()
    DRAGFIRST  = 27 #enum.auto()
    DRAGGING   = 28 #enum.auto()

thanCursor = {
#               THAN_STATE.SELECT1    : "dot",
#               THAN_STATE.SELECT1    : "center_ptr",
#               THAN_STATE.SELECT1    : "draped_box",
#               THAN_STATE.SELECT1    : "middlebutton",
#               THAN_STATE.SELECT1    : "target",
#               THAN_STATE.SELECT1    : "gobbler",
#               THAN_STATE.SELECT1    : "gumby",
               THAN_STATE.POINT1     : "dotbox",
               THAN_STATE.PANDYNAMIC : "hand2",
               THAN_STATE.ZOOMDYNAMIC: "sb_h_double_arrow"
             }

if __name__ == "__main__":
    print(__doc__)
