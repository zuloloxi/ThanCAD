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
This module provides for hatch commands.
"""

from math import hypot
from p_ggen import iterby2, frange
import thandr
from thanvar import Canc
from thantrans import T
from .thancommod import thanModCanc, thanModEnd
from . import thanundo


def thanHatchOpen(proj):
    """Draws a hatch between 2 disjoint lines.

    If the lines have opposite direction the result is artistic.
    """
    from .selutil import thanSelMultlines
    comname = "hatchopen"
    un = proj[1].thanUnits

    lines = thanSelMultlines(proj, 2, T["Select 2 lines to create draw between:\n"])
    if lines == Canc: return thanModCanc(proj)         # open hatch was cancelled
    selold = proj[2].thanSelold
    selelems = lines
    lines = tuple(lines)

    disweb = 1.0
    nweb = 10
    c = proj[2].thanGudGetFloat2(T["Hatch lines distance [Number of hatch lines] (enter=%s): "] % un.strdis(disweb),
        default=disweb, limits=(1.0e-6, 1.0e6), options=("number",))
    if c == Canc: return thanModCanc(proj)     # open hatch was cancelled
    if c == "n":
        c = proj[2].thanGudGetInt2(T["Number of hatch lines (enter=%d): "] % nweb,
        default=nweb, limits=(2, 10000))
        if c == Canc: return thanModCanc(proj)     # open hatch was cancelled
        nweb = c
    else:
        nweb = round(lines[0].thanLength() / disweb)
        if nweb < 2: nweb = 2
        elif nweb > 10000: nweb = 10000

    d1 = lines[0].thanLength() / nweb
    d2 = lines[1].thanLength() / nweb
    it1 = _iterdis2(lines[0].cp, d1)
    it2 = _iterdis2(lines[1].cp, d2)
    newelems = []
    for i in range(nweb+1):
        c1 = next(it1)
        c2 = next(it2)
        e = thandr.ThanLine()
        e.thanSet([c1, c2])
        if e.thanIsNormal():
            proj[1].thanElementAdd(e)
            e.thanTkDraw(proj[2].than)
            newelems.append(e)

    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo, ((), newelems, selelems),
                                        thanundo.thanReplaceUndo, ((), newelems, selold))
    thanModEnd(proj)


def _iterdis2(a, dd):
    "Iterate through polyline a, returning a point every d units distance."
    darx = 0.0
    for (xa,ya,za), (xb,yb,zb) in iterby2(a):
        d = hypot(xb-xa, yb-ya)
        for d1 in frange(darx, d, dd):
            x = xa + (xb-xa)/d*d1
            y = ya + (yb-ya)/d*d1
            z = za + (zb-za)/d*d1
            yield x, y, z
        darx = dd - (d-d1)
    yield xb, yb, zb
