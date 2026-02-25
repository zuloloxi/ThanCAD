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
This module processes topography related commands.
"""
from math import hypot
from p_gmath import thanintersect
import thandr
from thanvar import Canc, thanCumulDis, THANBYPARENT
from thantrans import Tphot, T
from thantkdia import ThanPodisSettings

from . import thanundo
from .thancommod import thanModCanc, thanModEnd


__vpodis = ThanPodisSettings.thanValsDef()
def thanPointDist(proj):
    "Create a point with known distances to existing points."
    comname = "pointdist"
    than = proj[2].than
    g2l = than.ct.global2Local
    crelold = proj[1].thanGetLastPoint()

    descptype = Tphot["Simple point"], Tphot["Named point"]
    descsol = Tphot["User selects the solution"], Tphot["Both solutions are selected"]
    descyn = Tphot["no"], Tphot["yes"]

    v = __vpodis
    while True:
        #proj[2].thanPrt("%-13s: %-12s    %-25s: %s" % (Tphot["Point type"], descptype[v.radPoint],
        #    Tphot["Which solutions to choose"], descsol[v.radSelect]))
        proj[2].thanPrt("%-10s: %s" % (Tphot["Point type"], descptype[v.radPoint]))
        proj[2].thanPrt("%-10s: %s / %s: %s" % (Tphot["Draw point"], descyn[v.chkPoint],
            Tphot["Draw lines to point"], descyn[v.chkLine]))
        ca = proj[2].thanGudGetPoint(Tphot["First reference point [Settings]: "], options=("Settings",))
        if ca == Canc: return proj[2].thanGudCommandCan()

        if ca != "s": break   #New settings
        w = ThanPodisSettings(proj[2], vals=v, cargo=proj)
        if w.result is None:
            proj[2].thanPrtCan()  #Inform user that the dialog was cancelled
        else:
            v.update(w.result)

    ra = proj[2].thanGudGetCircle(ca, 1.0, Tphot["Distance to first point: "])
    if ra == Canc: return proj[2].thanGudCommandCan()
    temp = than.dc.create_oval(g2l(ca[0]-ra, ca[1]-ra), g2l(ca[0]+ra, ca[1]+ra),
        outline="blue", tags=("e0",), outlinestipple="gray50")

    cb = proj[2].thanGudGetPoint(Tphot["Second reference point: "])
    if cb == Canc: than.dc.delete("e0"); return proj[2].thanGudCommandCan()

    rb = proj[2].thanGudGetCircle(cb, 1.0, Tphot["Distance to second point: "])
    if rb == Canc: than.dc.delete("e0"); return proj[2].thanGudCommandCan()
    temp = than.dc.create_oval(g2l(cb[0]-rb, cb[1]-rb), g2l(cb[0]+rb, cb[1]+rb),
        outline="blue", tags=("e0",), outlinestipple="gray50")

    ts = thanintersect.thanCirCir(ca, ra, cb, rb)
    if len(ts) < 1: than.dc.delete("e0"); return proj[2].thanGudCommandCan(Tphot["Infeasible point"])

    if len(ts) == 1:    #Only one solution -> autoselect
        isel = 0
    else:               #Ask the use to select the solution
        temp = proj[2].thanGudGetPoint(Tphot["Click to select one of the two solutions: "])
        if temp == Canc: than.dc.delete("e0"); return proj[2].thanGudCommandCan()
        d0 = hypot(temp[1]-ts[0][1], temp[0]-ts[0][0])
        d1 = hypot(temp[1]-ts[1][1], temp[0]-ts[1][0])
        isel = 0 if d0 < d1 else 1

    than.dc.delete("e0")
    c = list(proj[1].thanVar["elevation"])          # Get elevation(s)
    c[:2] = ts[isel][:2]

    newelems = []
    if v.chkPoint:
        if v.radPoint == 0:  #draw simple point
            elem = thandr.ThanPoint()
            elem.thanSet(c)
        else:                #draw named point
            name = proj[2].thanGudGetText0(T["Point name: "])
            if name == Canc: than.dc.delete("e0"); return proj[2].thanGudCommandCan()
            elem = thandr.ThanPointNamed()
            gvalidc = [True, True, True]
            elem.thanSet(c, name, gvalidc)
        proj[1].thanElementAdd(elem)             # thanTouch is implicitly called
        elem.thanTkDraw(proj[2].than)
        newelems.append(elem)

    if v.chkLine:  #Draw lines
        cp = [tuple(ca), tuple(c)]
        __addline1(proj, cp, newelems)
        cp = [tuple(cb), tuple(c)]
        __addline1(proj, cp, newelems)

    crel = proj[1].thanGetLastPoint()
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo2, ((), newelems, (), crel),
                                        thanundo.thanReplaceUndo2, ((), newelems, (), crelold))
    proj[2].thanGudCommandEnd()


def __addline1(proj, cp, newelems):
    "Create and add a new line to the drawing."
    elem = thandr.ThanLine()
    elem.thanSet(cp)
    proj[1].thanElementAdd(elem)             # thanTouch is implicitly called
    elem.thanTkDraw(proj[2].than)
    newelems.append(elem)
