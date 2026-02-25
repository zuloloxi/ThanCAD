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
This module provides code to show lines with elevation 0."
"""
from math import fabs
from thandr import ThanLine, ThanPoint


def thanHilightZero(proj):
    "Show briefely all (currently visible) lines and point with elevation 0."
    elev2show = 0.0
    elevtol = 0.001

    filt = lambda e: isinstance(e, ThanLine) or isinstance(e, ThanPoint)
    proj[2].thanGudSetSelExternalFilter(filt)

    elzer = []
    for elem in proj[2].thanGudGetDisplayed():    #Select all lines and points currently visible
        if isinstance(e, ThanPoint):
            c1 = e.getInspnt()
            if fabs(c1[2]-elev2show) <= elevtol: elzer.append(e)
        else:
            for c1 in e.cp:
                if fabs(c1[2]-elev2show) > elevtol: break
            else:
                elzer.append(e)

    proj[2].thanGudGetSelElemx(elzer)
    proj[2].thanGudSetSelColorx()
    text = "z=" + proj[2].than.strdis(elev2show)
    dc = proj[2].thanCanvas
    ct = proj[2].thanCt
    for e in elzer:
        c1 = e.getInspnt()
        px, py = ct.global2Locali(c1[0], c1[1])
        px += -dc.canvasx(0) + dc.winfo_rootx()
        py += -dc.canvasy(0) + dc.winfo_rooty()
        t = InfoWin(help=text, position=(px, py))
    dc.after(3000, __recolor, proj, elzer)


def __recolor(proj, elzer):
    "Paint the elements with their original color."
    dilay = proj[1].thanLayerTree.dilay
    for e in elzer:
        tlay = e.thanTags[1]
        lay = dilay[tlay]
        outline = lay.thanAtts["moncolor"].thanTk
        if lay.thanAtts["fill"].thanVal: fill = outline
        else:                            fill = ""
        proj[2].thanGudGetSelElemx([e])
        proj[2].thanGudSetSelColorx(outline, fill)
