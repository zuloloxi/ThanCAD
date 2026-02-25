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
This module processes commands for educational/research purposes.
"""
import thandr, thanobj
from thanvar import Canc
from thantrans import T, Tarch
import thantkdia
from .thancommod import thanModEnd
from thanpackages.biocityplan.thandiabcplan import ThanBcplan


def thanEduRect(proj):
    "Draws a closed line in the shape of a rectangle associates with text."
    c1 = proj[2].thanGudGetPoint(T["First point: "])
    if c1 == Canc: return proj[2].thanGudCommandCan() # Rectangle cancelled

    c2 = proj[2].thanGudGetRect(c1, T["Second point: "])
    if c2 == Canc: return proj[2].thanGudCommandCan() # Rectangle cancelled
    x1, y1 = c1[:2]
    x2, y2 = c2[:2]
    if x2 > x1: x1, x2 = x2, x1
    if y2 > y1: y1, y2 = y2, y1
    c1[:2] = x1, y1
    c2 = list(c1); c2[:2] = x2, y1
    c3 = list(c1); c3[:2] = x2, y2
    c4 = list(c1); c4[:2] = x1, y2

    elem = thandr.ThanLine()
    elem.thanSet([c1, c2, c3, c4, c1])
    elem.thanTags = ("e0", )
    elem.thanTkDraw(proj[2].than)
    win = thantkdia.ThanElemtext(proj[2], [None, ""], cargo=proj)
    proj[2].thanTkSetFocus()
    if win.result is None:
        proj[2].thanCanvas.delete("e0")
        return proj[2].thanGudCommandCan()
    try: elem.thanCargo
    except: elem.thanCargo = {}
    elem.thanCargo["edu"] = win.result[1]
    proj[2].thanCanvas.delete("e0")
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)

    proj[1].thanEdus.add(elem)
    proj[2].thanGudCommandEnd()


def thanEduEdit(proj):
    "Edit the associated text with a ThanCad element."
    proj[2].thanSelems.clear()
    proj[2].thanSelems.update(proj[1].thanEdus)
    elem = proj[2].thanGudGetSnapElem(T["Choose site to edit: "])
    proj[2].thanSelems.clear()
    if elem == Canc: return proj[2].thanGudCommandCan()
    t = elem.thanCargo["edu"]
    win = thantkdia.ThanElemtext(proj[2], [None, t], cargo=proj)
    proj[2].thanTkSetFocus()
    if win.result is None: return proj[2].thanGudCommandCan()
    elem.thanCargo["edu"] = win.result[1]
    proj[2].thanGudCommandEnd()



def thanEduFplan(proj):
    "Compute an automated floorplan."
    t = thantkdia.ThanFplan(proj[2], vals=None, cargo=proj)
    v = t.result
    del t
    if v is None: return proj[2].thanGudCommandCan()   # Floor plan was cancelled
    fps = proj[1].thanObjects["FLOORPLAN"]
    if len(fps) == 0: fps.append(thanobj.ThanFplan())
    fps[0].run(proj, v)
    thanModEnd(proj)    # 'Reset color' has already been called, but it is called again for only 2..
                        # ..elements, so it is fast

def thanEdubiocityplan(proj):
    "Asks the user to create bioclimatic city plan."
    bcps = proj[1].thanObjects["BIOCITYPLAN"]
    if len(bcps) == 0: bcps.append(thanobj.ThanBiocityplan())
    bcp = bcps[0]
    t = ThanBcplan(proj[2], vals=bcp.toDialog(proj), cargo=proj)
    v = t.result
    del t
    if v is None: return proj[2].thanGudCommandCan()     # City plan was cancelled
    bcp.fromDialog(proj, v)
    bcps[0] = bcp
    proj[1].thanTouch()                    #Drawing IS modified
    if v.doPrepro:
        dtmobjs = proj[1].thanObjects["DTMLINES"]
        if len(dtmobjs) == 0: return proj[2].thanGudCommandCan(T["Can't preprocess: No DTM has been defined!"])
        dtm = dtmobjs[0].dtm
        proj[2].thanPrt(Tarch["Please wait, preprocessing may take several minutes.."])
        bcp.pc.pol.build_cache(dtm, proj[2].thanPrt)
        bcp.pc.repairState()
        fn = proj[0].parent / proj[0].namebase + ".cache"
        proj[2].thanPrt("%s %s  ..." % (Tarch["Saving preprocessing results to"], fn))
        try:
            with open(fn, "w") as fw:
                bcp.pc.pol.write_cache(fw)
        except Exception as why:
            proj[2].thanPrter("%s %s: %s" % (Tarch["Warning: Could not save preprocessing results to"], fn, why))
        return proj[2].thanGudCommandEnd()
    else:
        if bcp.pc.pol.cache.roadenx is None: return proj[2].thanGudCommandCan(Tarch["Please do preprocessing and retry."])
        for i in range(v.entMult):            #Run multiple times
            bcp.run(proj)
            bcp.tkDraw(proj, bcp.pc.state)     #thanTouch is implicitly called
            bcp.wrState(proj)
        return proj[2].thanGudCommandEnd()
