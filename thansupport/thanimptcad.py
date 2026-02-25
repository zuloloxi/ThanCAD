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

This module defines an object which reads an active ThanCad drawing and
it calls user defined callbacks for each kind of element.
It works, almost identically, like thanImportDxf, which reads a .dxf file.
"""

from thandr import ThanLine, ThanCircle
from thanopt.thancon import THANLC

class ThanImportTcad:
    "A class to import elements from an active ThanCad Drawing."

    def __init__(self, proj, dr, defaultLayer="0"):
        "Creates an instance of the class."
        self.thanDr = dr
        self.thanProj = proj
        self.defLay = defaultLayer


    def thanImport(self):
        "Imports a dxf file."
        proj = self.thanProj
        dr = self.thanDr
        for layobj in proj[1].thanLayerTree.dilay.values():  #works for python2,3
            col = layobj.thanAtts["moncolor"].thanDxf()
            lay = layobj.thanGetPathname(sep=THANLC)
            for elem in layobj.thanQuad:
                handle = int(elem.thanTags[0][1:])
                if isinstance(elem, ThanLine):
                    xp = [c[0] for c in elem.cp]
                    yp = [c[1] for c in elem.cp]
                    zp = [c[2] for c in elem.cp]
                    dr.dxfPolyline(xp, yp, zp, lay, handle, col)
                elif isinstance(elem, ThanCircle):
                    dr.dxfCircle(elem.cc[0], elem.cc[1], elem.cc[2], lay, handle, col, elem.r)
        return 0                           # OK


############################################################################
############################################################################

def thanImportTcad(proj, dr, defaultLayer="0"):
    "Creates an instance of the class to do the import."
    ti = ThanImportTcad(proj, dr, defaultLayer="0")
    return ti.thanImport()


if __name__ == "__main__":
    print(__doc__)
