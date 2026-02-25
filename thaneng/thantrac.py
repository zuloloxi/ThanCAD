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

This module implements semiautomatic tracing of curves of a raster image.
It is the link between ThanCad and the actual implementation.
"""

import thandr
from thantrans import T
from thanvar import Canc
from thansupport import thanPan2Points
from . import tr

def thanTrace(proj, jx, iy):
    "Trace a curve from pixel coordinates xp, yp."
    im = proj[2].thanImageCur
    if im.visited is None: im.visited = tr.ThanMultiSet()
    tra = tr.ThanPilRasterTracker(im.image, im.visited)
    curvemain = []
    celev = list(proj[1].thanVar["elevation"])
    while True:
        curvemain, fcs = tra.trace(iy, jx, curve=curvemain)
        print("len curve:", len(curvemain), "number of possible directions=", len(fcs))
        print("last pixel i,j:", curvemain[-1])
        emain = __crlines(proj, [curvemain])
        if len(fcs) < 1: return
        assert len(fcs) != 1, "It should have been found!"
        eposs = __crlines(proj,  [c for n, c in fcs], "blue", curvemain[-1])
        thanPan2Points(proj, eposs[0].cp)
        proj[2].thanSelems.clear()
        proj[2].thanSelems.update(eposs)
        edir = proj[2].thanGudGetSnapElem(T["Choose direction to continue or enter to finish (point/<enter>): "],
            options=("point", ""))
        dc = proj[2].thanCanvas
        for e in eposs: dc.delete(e.thanTags[0])  #eposs has no images (to delete from proj[2].thanImages)
        proj[1].thanDelSel(eposs)
        if edir == Canc: return Canc
        if edir == "": return ""
        if edir == "p":
            eline = emain[0]
            cpp = eline.cp[-1]
            statonce = ""
            while True:
                #cw = proj[2].thanGudGetPoint("Next point or enter to finish (trace/<enter>): ", options=("trace",""))
                cw = proj[2].thanGudGetLine(cpp, "Next point or enter to finish (trace/<enter>): ",
                    statonce, options=("trace",""))
                if cw == "": return ""
                if cw == "t":
                    try:
                        jx, iy = im.thanGetPixCoor(eline.cp[-1])
                    except IndexError:
                        statonce = T["Previous point is not in image.\n"]
                        continue
                    if not im[jx, iy]:
                        statonce = T["No curve was found in previous point.\n"]
                        continue
                    break
                eline.cp.append(cw)
                dc.delete(eline.thanTags[0])
                eline.thanTkDraw(proj[2].than)
                cpp = cw
                statonce = ""
        else:
            curve = edir.thanCargo
            iy, jx = curve[1]
        for e in emain: dc.delete(e.thanTags[0]) #emain has no images (to delete from proj[2].thanImages)
        proj[1].thanDelSel(emain)


def __crlines(proj, curves, col=None, ca=None):
    "Draws a line checking for errors."
    celev = list(proj[1].thanVar["elevation"])
    imc = proj[2].thanImageCur
    than = proj[2].than
    col1 = than.outline
    if col is not None: than.outline = col
    elems = []
    for curve in curves:
        if ca is not None: curve.insert(0, ca)
        if len(curve) < 2: continue
        if curve[0] == curve[-1]: continue
        e = thandr.ThanLine()
        cp = [imc.thanGetWorldCoor(x1, y1, celev) for y1,x1 in curve]
        e.thanSet(cp)
        proj[1].thanElementAdd(e)
        item = e.thanTkDraw(proj[2].than)
        e.thanCargo = curve
        elems.append(e)
    than.outline = col1
    return elems


if __name__ == "__main__":
    print(__doc__)
