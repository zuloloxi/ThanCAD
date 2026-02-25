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

This module defines generic state, i.e. how ThanCad reacts to events for a
defined job. This is generic state which originaly did nothing.
A small functionality was added, to show the elevation of a line or a point,
when a user clicks it.
"""

class ThanStateGeneric:
    "Default state object; does nothing."
    def thanOnMotionDrag(self, event): pass
    def thanOnReleaseDrag(self, event): pass
    def thanOnMotion(self, event, x, y): pass
    def thanOnClickr(self, event, x, y, cc): pass
    def thanZoomXyr(self, x, y, fact): pass


    def __init__(self, proj):
        "Initialize object."
        self.thanProj = proj


    def thanOnClick(self, event, x, y, cc):
        "Shows the elevation of the line or point as shortlived small infowindow."
        from thandr import ThanLine, ThanPoint
        from thanvar import InfoWin
        proj = self.thanProj
        filter = lambda e: isinstance(e, ThanLine) or isinstance(e, ThanPoint)
        proj[2].thanGudSetSelExternalFilter(filter)
        proj[2].thanGudSetSelSave()                      # Save old selection
        res = proj[2].thanGudGetSel1(cc[0], cc[1])       # Try to select 1 element..
        if res[0] > 0:
            for e in proj[2].thanSelall: break
        proj[2].thanGudSetSelExternalFilter(None)        # Reset filter
        proj[2].thanGudSetSelRestore()                   # Restores previous selection
        if res[0] == 0: return                           # Selection of 1 element is unsuccessful
        if isinstance(e, ThanPoint):
            c1 = e.getInspnt()
            text = "z=" + proj[2].than.strdis(c1[2])
        else:
            c1 = e.thanPntNearest(cc)
            if c1 is None:
                print("ThanStateGeneric.thanOnClick(): Nearest not found! It should!")
                return
            zpol = e.cp[0][2]
            text = "z=" + proj[2].than.strdis(zpol)
            for ct in e.cp:
                if ct[2] != zpol:
                    text = "z=varies"
                    break
        ct = proj[2].thanCt
        px, py = ct.global2Locali(c1[0], c1[1])
        dc = proj[2].thanCanvas
        px += -dc.canvasx(0) + dc.winfo_rootx()
        py += -dc.canvasy(0) + dc.winfo_rooty()
        proj[2].thanGudGetSelElemx([e])
        proj[2].thanGudSetSelColorx()
        t = InfoWin(help=text, position=(px, py))
        dc.after(3000, self.__recolor, e)


    def __recolor(self, e):
        "Paint the elements with their original color."
        proj = self.thanProj
        dilay = proj[1].thanLayerTree.dilay
        tlay = e.thanTags[1]
        lay = dilay[tlay]
        outline = lay.thanAtts["moncolor"].thanTk
        if lay.thanAtts["fill"].thanVal: fill = outline
        else:                            fill = ""
        proj[2].thanGudGetSelElemx([e])
        proj[2].thanGudSetSelColorx(outline, fill)
