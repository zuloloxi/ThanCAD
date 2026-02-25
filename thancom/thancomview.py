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
This module processes view commands.
"""

from p_gmath import thanNear2
from thanvar import Canc
from thantrans import T


def thanZoom(proj):
    "General zoom command."
    stat1 = T["Specify corner of window, enter a scale factor (nX or nXP), or\n"]
    stat1 += T["(All/Center/Dynamic/Extents/Previous/Scale/Window/seLection) <real time>:"]
    stat = stat1
    while True:
        res, typres, cargo = proj[2].thanGudGetPointOr(stat,
            options="All/Center/Dynamic/Extents/Previous/Scale/Window/Lection".split("/"))
        if res == Canc: return proj[2].thanGudCommandEnd() # Zoom cancelled
        if typres == "v": return thanZoomWin(proj, res)    # Zoom window implied
        if typres == "o":                                  # One of the options was return
            if res == "":  return proj[2].thanGudCommandBegin("zoomrealtime")  #Zoom real time implied
            if res == "a": return thanZoomExt(proj)
            if res == "c": return proj[2].thanGudCommandEnd(T["Zoom center has not yet been implemented."], "can")
            if res == "d": return proj[2].thanGudCommandEnd(T["Zoom dynamic has not yet been implemented."], "can")
            if res == "e": return thanZoomExt(proj)
            if res == "p": return proj[2].thanGudCommandEnd(T["Zoom previous has not yet been implemented."], "can")
            if res == "s": return thanZoomFact(proj)
            if res == "w": return thanZoomWin(proj)
            if res == "l": return thanZoomSel(proj)
            assert False, "Unknown option: "+res

        res = str(res).strip().lower()
        if res[-1:] == "x":
            try:
                f = float(res[:-1])
            except (IndexError, ValueError):
                proj[2].thanCom.thanAppend(T["Invalid zoom factor\n"], "can")
                continue
            else:
                if f != 0.0: return thanZoomFact(proj, -f)     # relative zoom factor is negative
                proj[2].thanCom.thanAppend(T["Invalid zoom factor\n"], "can")
                continue
        try:
            f = float(res)
        except ValueError:
            pass
        else:
            if f != 0.0: return thanZoomFact(proj, f)
            proj[2].thanCom.thanAppend(T["Invalid zoom factor\n"], "can")
            continue
        proj[2].thanCom.thanAppend(T["Invalid point, factor or option. Try again.\n"], "can")


def thanZoomWin(proj, first=None):
    "Zooms in a user defined window."
    if first is None:
        ca = proj[2].thanGudGetPoint(T["First window corner: "])
        if ca == Canc: return proj[2].thanGudCommandCan()  # Zoom cancelled
    else:
        ca = first
    cb = proj[2].thanGudGetRect(ca, T["Other window corner: "])
    if cb == Canc: return proj[2].thanGudCommandCan()      # Zoom cancelled
    xa, ya = ca[:2]
    xb, yb = cb[:2]

    v = proj[1].viewPort
    v[:] = min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)
    v[:] = proj[2].thanGudZoomWin(v)
    proj[2].thanAutoRegen(regenImages=True)
    proj[2].thanGudCommandEnd()


def thanZoomSel(proj):
    "Select elements and zoom to these elements."
    from .thancommod import thanModCanc, thanModEnd
    from .thancomsel import thanSelectGen
    proj[2].thanCom.thanAppend(T["Select elements to zoom to\n"])
    res = thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)
    if len(proj[2].thanSelall) < 1: return thanModEnd(proj, T["No elements to zoom to."])

    for e in proj[2].thanSelall: break
    xymm = e.thanXymm[:]
    for e in proj[2].thanSelall:
        xymm[0] = min(xymm[0], e.thanXymm[0])
        xymm[1] = min(xymm[1], e.thanXymm[1])
        xymm[2] = max(xymm[2], e.thanXymm[2])
        xymm[3] = max(xymm[3], e.thanXymm[3])
    if xymm[2]-xymm[0] == 0.0 and xymm[3]-xymm[1] == 0.0: return thanModEnd(proj, T["Nothing to zoom to."])
    v = proj[1].viewPort
    v[:] = xymm
    v[:] = proj[2].thanGudZoomWin(v)
    proj[2].thanAutoRegen(regenImages=True)
    thanModEnd(proj)

#===========================================================================

def thanZoomExt(proj):
    "Zoom to show entire drawing."
    thanZoomExt1(proj)
    proj[2].thanGudCommandEnd()


def thanZoomExt1(proj):
    "Zoom to show entire drawing without calling thanGudCommandEnd."
    dr = proj[1]
    if proj[1].xMinAct is None:
        proj[2].thanPrter(T["No elements found to zoom into"])
        return # No active (visible) elements; zoom all has no meaning
    elif thanNear2([dr.xMinAct, dr.yMinAct], [dr.xMaxAct, dr.yMaxAct]):
        proj[2].thanPrter(T["No zoom to single point"])
        return # No active (visible) elements; zoom all has no meaning
    v = dr.viewPort
    w = dr.xMinAct, dr.yMinAct, dr.xMaxAct, dr.yMaxAct
    print("ThanZoomExt(): w=", w)
    v[:] = proj[2].thanGudZoomWin(w)
    print("ThanZoomExt(): v=", v)
    proj[2].thanAutoRegen(regenImages=False)               # Zoom is possible, but another autoregen..
    w1 = dr.xMinAct, dr.yMinAct, dr.xMaxAct, dr.yMaxAct    # ..follows, thus no regenImages
    if w != w1:
        if thanNear2(w1[:2], w1[2:]):  #This means the coordinates are too big: w1 = (1e50, 1e50, 1e50, 1e50)
            proj[2].thanPrter(T["Element coordinates too big to auto zoom: %s\nPlease zoom manually"] % (w1,))
            return
        v[:] = proj[2].thanGudZoomWin(w1)          # The previous regen changed xyMinMaxAct
    proj[2].thanAutoRegen(regenImages=True)                 # This may not lead to a full regen, ..
                                                            # ..but regenImages is needed.

#===========================================================================

def thanZoomFact(proj, first=None):
    "Zoom relative or absolute to current window; relative factor is negative."
    f = 1.0
    if first is None:
        f = proj[2].thanGudGetPosFloat(T["Relative zoom factor: "], f)
        if f == Canc: return proj[2].thanGudCommandCan() # Cancelled
        f = -f                                  # relative factor
    else:
        f = first

    v = proj[1].viewPort
    w2, h2 = (v[2]-v[0])*0.5,  (v[3]-v[1])*0.5  # Zoom factor scales the drawing with respect to the..
    xm, ym = v[0]+w2,  v[1]+h2                  # ..center of the drawing window (->center of viewPort)

    if f < 0.0:
        f = -f                                  # relative factor
    else:
        w2, h2 = proj[2].thanGudGetWincm()      # absolute factor: for the moment if f==1 ..
        w2, h2 = w2*0.5, h2*0.5                 # ..it means 1cm on screen maps to 1 drawing (user) unit

    v[:] = xm-w2/f, ym-h2/f, xm+w2/f, ym+h2/f
    v[:] = proj[2].thanGudZoomWin(v)
    proj[2].thanAutoRegen(regenImages=True)
    proj[2].thanGudCommandEnd()

#===========================================================================

def thanPanRel(proj):
    "Pan relative to current window; this routine is probably obsolete."

#---Get vector distance to pan

    ca = proj[2].thanGudGetPoint(T["Pan origin: "])
    if ca == Canc: proj[2].thanGudCommandCan(); return  # pan cancelled

    cb = proj[2].thanGudGetLine(ca, T["Pan destination: "])
    if cb == Canc: proj[2].thanGudCommandCan(); return  # pan cancelled
    dx = cb[0] - ca[0]
    dy = cb[1] - ca[1]

#---Modify the viewport coordinates and regen if needed

    v = proj[1].viewPort
    v[:] = v[0]-dx, v[1]-dy, v[2]-dx, v[3]-dy
    v[:] = proj[2].thanGudZoomWin(v)
    proj[2].thanAutoRegen(regenImages=False)
    proj[2].thanGudCommandEnd()

#===========================================================================


def thanPanPage(proj, ix, iy):
    """Pan integer number of pages to the left, right, up or down.

    One page is the area of the current viewport minus 10% overlap.
    You know, thAtCAD is never going to implement this.
    Fae xoma thAtCAD (Greeklish in text).
    I hate to write trademark notices :)
    """
    proj[2].thanPanPage(ix, iy)
    proj[2].thanGudCommandEnd()

#===========================================================================

def thanPanRT(proj):
    "Pan dynamically dragging the mouse."
    v = proj[1].viewPort
    while True:
        w = proj[2].thanGudGetPanRT(T["Pan real time"])
        if w == Canc: break
        v[:] = w
        proj[2].thanAutoRegen(regenImages=False)
    proj[2].thanGudCommandEnd()


def thanZoomRT(proj):
    "Zoom dynamically dragging the mouse."
    v = proj[1].viewPort
    while True:
        w = proj[2].thanGudGetZoomRT(T["Zoom real time"])
        if w == Canc: break
        v[:] = w
        proj[2].thanAutoRegen(regenImages=False)
    proj[2].thanAutoRegen(regenImages=True)     # Regen images only if zoom realtime is finished
    proj[2].thanGudCommandEnd()

#===========================================================================

def thanRegen(proj):
    "Regenerates the current drawing."
    proj[2].thanRegen()
    proj[2].thanGudCommandEnd()


def thanRedraw(proj):
    "Ensures the relative draworder of the layers."
    proj[2].thanRedraw()
    proj[2].thanGudCommandEnd()
