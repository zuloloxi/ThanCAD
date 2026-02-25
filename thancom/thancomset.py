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

Package which processes commands entered by the user.
This module processes commands for settings (for exampled layer settings)."
"""

import thantkdia
from thantrans import T

def thanFormDimstyle(proj):
    "Manipulates dimension styles."
    win = thantkdia.ThanDimstyleManager(proj[2], cargo=proj)
    if win.result is None: return proj[2].thanGudCommandCan()
    olddimstyles = dict((key, dst.thanClone()) for key,dst in proj[1].thanDimstyles.items())
    newdimstyles = win.dimstyles
    __dimstylesRestore(proj, newdimstyles)
    proj[1].thanDoundo.thanAdd("dimstyle", __dimstylesRestore, (newdimstyles, ),
                                           __dimstylesRestore, (olddimstyles, ))
    proj[1].thanTouch()
    proj[2].thanGudCommandEnd(T["Changes will be visible after the next regeneration."], "can")


def __dimstylesRestore(proj, dimstyles):
    "Replace current dimstyles with dimstyles argument."
    proj[1].thanDimstyles.clear()
    proj[1].thanDimstyles.update(dimstyles)
    proj[1].thanTouch()
