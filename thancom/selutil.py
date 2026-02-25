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
This module provides various high level selection routines.
"""

from thanvar import Canc
from thantrans import T
import thandr
from . import thancomsel


def thanSel1line(proj, statonce, strict=True, options=()):
    """Selects 1 line and return immediately.

    The argument strict is not used and it is there for compatibility
    with thanSel1Order."""
    return thancomsel.thanSelect1(proj, statonce, filter=lambda e: isinstance(e, thandr.ThanLine), options=options)


def thanSel2linsegsold(proj, statonce, strict=True):
    "Selects 2 line segments; i.e. lines with only 2 nodes."
    while True:
        elems = []
        proj[2].thanCom.thanAppend(statonce, "info1")
        res = thancomsel.thanSelectGen(proj, standalone=False)
        if res == Canc: return Canc
        for elem in proj[2].thanSelall:
            if isinstance(elem, thandr.ThanLine) and len(elem.cp) == 2: elems.append(elem)
        if len(elems) == 2: break
        if not strict and len(elems) > 1: return elems[:2]
        proj[2].thanCom.thanAppend(T["Two single segment lines are required (%d found). Try again.\n"]%len(elems), "can")
        proj[2].thanGudResetSelColor()                   # Unmarks the selection
        proj[2].thanGudSetSelRestore()                   # Restores previous selection
        proj[2].thanUpdateLayerButton()                  # Show current layer again
    return True


def thanSel2linsegs(proj, statonce1, statonce2, options=()):
    "Selects 2 line segments; i.e. lines with only 2 nodes."
    while True:
        gps = thanSel1line(proj, statonce1, strict=True, options=options)
        if gps == Canc: return Canc
        if any(gps==o1[:1] for o1 in options): return gps, None, None, None # Option given
        if len(gps.cp) == 2: break
        proj[2].thanPrter(T["A single segment line is required. Try again."])
    gpsnear = proj[2].thanSel1coor                    # This is the first point in the 'break' command
    selold = proj[2].thanSelold

    while True:
        rel = thanSel1line(proj, statonce2, strict=True)
        if rel == Canc:
            selall = set((gps,))
            proj[2].thanGudSetSelElem(selall)         # The current selection (cutting edges) #Subsequent thanmodcanc() will correct it
            proj[2].thanGudSetSeloldElem(selold)      # The selection before the command trim started
            return Canc
        if len(rel.cp) == 2: break
        proj[2].thanPrter(T["A single segment line is required. Try again."])
    relnear = proj[2].thanSel1coor                    # This is the first point in the 'break' command

    gr = [gps, rel]
    selall = set(gr)
    proj[2].thanGudSetSelElem(selall)         # The current selection (cutting edges)
    proj[2].thanGudSetSeloldElem(selold)      # The selection before the command trim started
    return gps, rel, gpsnear, relnear


def thanSel2linesOrder(proj, statonce1, statonce2):
    "Selects 2 lines with predefined order."
    gps = thanSel1line(proj, statonce1, strict=True)
    if gps == Canc: return Canc
    selold = proj[2].thanSelold
    rel = thanSel1line(proj, statonce2, strict=True)
    if rel == Canc:
        selall = set((gps,))
        proj[2].thanGudSetSelElem(selall)    # The current selection (cutting edges) #Subsequent thanmodcanc() will correct it
        proj[2].thanGudSetSeloldElem(selold) # The selection before the command trim started
        return Canc
    gr = [gps, rel]
    selall = set(gr)
    proj[2].thanGudSetSelElem(selall)         # The current selection (cutting edges)
    proj[2].thanGudSetSeloldElem(selold)      # The selection before the command trim started
    return gr


def thanSelMultlines(proj, nsel, statonce1, strict=False, name="LINE"):
    """Selects (at least) nsel lines.

    If strict == True then the user must select exactly nsel lines, otherwise it is an error.
    If strict == False then the user must select at least nsel lines, otherwise it is an error."
    """
    if strict: atl = T["Exactly"]
    else:      atl = T["At least"]
    clas = thandr.thanElemClass[name]
    while True:
        elems = []
        proj[2].thanCom.thanAppend(statonce1, "info1")
        res = thancomsel.thanSelectGen(proj, standalone=False, filter=lambda elem: isinstance(elem, clas))
        if res == Canc: return Canc
        for elem in proj[2].thanSelall:
            assert isinstance(elem, clas), "filter does not work?"
        elems = proj[2].thanSelall
        if len(elems) == nsel: break
        if not strict and len(elems) >= nsel: break
        proj[2].thanCom.thanAppend(T["%s %d line(s) are required (%d found). Try again.\n"]%(atl, nsel, len(elems)), "can")
        proj[2].thanGudResetSelColor()                   # Unmarks the selection
        proj[2].thanGudSetSelRestore()                   # Restores previous selection
        proj[2].thanUpdateLayerButton()                  # Show current layer again
    return elems


def thanSelMultquads(proj, nsel, statonce1, strict=False, name="LINE"):
    """Selects (at least) nsel closed lines with 5 points (quadrilaterals).

    If strict == True then the user must select exactly nsel lines, otherwise it is an error.
    If strict == False then the user must select at least nsel lines, otherwise it is an error."
    """

    def filter1(elem):
        if not isinstance(elem, thandr.ThanLine): return False
        if not elem.thanIsClosed(): return False
        try: elem.cpori
        except: pass
        else: return False   #Ignore splines
        if len(elem.cp) != 5: return False
        #Check if it is convex here
        return True


    if strict: atl = T["Exactly"]
    else:      atl = T["At least"]
    clas = thandr.thanElemClass[name]
    while True:
        elems = []
        proj[2].thanCom.thanAppend(statonce1, "info1")
        res = thancomsel.thanSelectGen(proj, standalone=False, filter=filter1)
        if res == Canc: return Canc
        #for elem in proj[2].thanSelall:
        #    assert isinstance(elem, clas), "filter does not work?"
        elems = proj[2].thanSelall
        if len(elems) == nsel: break
        if not strict and len(elems) >= nsel: break
        proj[2].thanCom.thanAppend(T["%s %d line(s) are required (%d found). Try again.\n"]%(atl, nsel, len(elems)), "can")
        proj[2].thanGudResetSelColor()                   # Unmarks the selection
        proj[2].thanGudSetSelRestore()                   # Restores previous selection
        proj[2].thanUpdateLayerButton()                  # Show current layer again
    return elems


def thanSelectCrosClear(proj, c1, c2, filter):
    "Select and get elements in crossing widnow, and then clear selection without user intervention."
    proj[2].thanGudSetSelExternalFilter(filter)                 # Set filter
    proj[2].thanGudSetSelSave()                                 # Save old selection
    res = proj[2].thanGudGetSelCros(c1[0], c1[1], c2[0], c2[1]) # Select crossing
    proj[2].thanGudSetSelcurClear()                             # Clears current selection (which is already inside selall)
    elems = proj[2].thanSelall
    proj[2].thanGudSetSelExternalFilter(None)                   # Reset filter
    proj[2].thanGudSetSelRestore()                              # Restores previous selection
    return elems


def thanSelMultLinsegs(proj, nsel, statonce, options=()):
    "Selects nsel line segments; return line segents neareast to the cursor when clicked."
    than = proj[2].than
    g2l = than.ct.global2Local
    elems = []
    cnear = []
    for isel in range(nsel):
        if isel == 0:
            gps = thanSel1line(proj, statonce[isel], strict=True, options=options)
            if gps == Canc: return Canc, Canc
            if any(gps==o1[:1] for o1 in options): return gps, None # Option given
        else:
            gps = thanSel1line(proj, statonce[isel], strict=True)
            if gps == Canc:
                than.dc.delete("e0")                  #Remove temporary lines
                return Canc, Canc
        gpsnear = proj[2].thanSel1coor                # This is the first point in the 'break' command
        cn, i, t = gps.thanPntNearest2(gpsnear)
        elems.append(gps)
        cnear.append((cn, i, t))
        xy1 = [g2l(c1[0], c1[1]) for c1 in gps.cp[i-1:i+1]]
        temp = than.dc.create_line(xy1, fill="blue", tags="e0")  #Create temporary line with tag 'selx'

    selold = proj[2].thanSelold
    selall = set(elems)
    proj[2].thanGudSetSelElem(selall)         # The current selection (cutting edges)
    proj[2].thanGudSetSeloldElem(selold)      # The selection before the command trim started
    than.dc.delete("e0")                      #Remove temporary lines
    return elems, cnear

    #            cla = proj[1].thanLayerTree.thanCur
    #            tags = "e0", cla.thanTag, "e"+str(len(cp))


if __name__ == "__main__":
    print(__doc__)
