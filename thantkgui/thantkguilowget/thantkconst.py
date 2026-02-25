##############################################################################
# ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2013 Thanasis Stamos, March 25, 2013
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers

It implements various constants for the TkGui of ThanCad.
"""

from thandefs import ThanId


__idState = ThanId()
THAN_STATE_NONE      = __idState.new()
THAN_STATE_INTERRUPT = __idState.new()
THAN_STATE_POINT     = __idState.new()
THAN_STATE_POINT1    = __idState.new()
THAN_STATE_LINE      = __idState.new()
THAN_STATE_LINE2     = __idState.new()
THAN_STATE_POLAR     = __idState.new()
THAN_STATE_CIRCLE    = __idState.new()
THAN_STATE_ARC       = __idState.new()
THAN_STATE_RECTANGLE = __idState.new()
THAN_STATE_RECTRATIO = __idState.new()
THAN_STATE_TEXT      = __idState.new()
THAN_STATE_MOVE      = __idState.new()
THAN_STATE_ROADP     = __idState.new()
THAN_STATE_ROADR     = __idState.new()
THAN_STATE_SPLINEP   = __idState.new()
THAN_STATE_ELLIPSEB  = __idState.new()
THAN_STATE_SNAPELEM  = __idState.new()
#THAN_STATE_UNFOCUSED = __idState.new()

THAN_STATE_DRAGFOLLOWS = __idState.new()    # Drom this state on, all states are for dragging

THAN_STATE_PANDYNAMIC  = __idState.new()
THAN_STATE_ZOOMDYNAMIC = __idState.new()

THAN_STATE_DRAG2BEGIN = __idState.new()
THAN_STATE_DRAGFIRST  = __idState.new()
THAN_STATE_DRAGGING   = __idState.new()
del __idState

thanCursor = {
#               THAN_STATE_SELECT1    : "dot",
#               THAN_STATE_SELECT1    : "center_ptr",
#               THAN_STATE_SELECT1    : "draped_box",
#               THAN_STATE_SELECT1    : "middlebutton",
#               THAN_STATE_SELECT1    : "target",
#               THAN_STATE_SELECT1    : "gobbler",
#               THAN_STATE_SELECT1    : "gumby",
               THAN_STATE_POINT1     : "dotbox",
               THAN_STATE_PANDYNAMIC : "hand2",
               THAN_STATE_ZOOMDYNAMIC: "sb_h_double_arrow"
             }

if __name__ == "__main__":
    print __doc__
