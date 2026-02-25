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
This module provides for modification commands of lines.
"""

from math import hypot
from thandr import ThanLine
from thantrans import T
from thanvar import Canc
from . import thancomsel, thanundo
from .thancommod import thanModEnd, thanModCanc


def thanModMoveLinepoint(proj):
    """Moves a point of a line.

    Note that no selection is made: The selections of 1 point is not recorded.
    """
    retainz = True
    selold = proj[2].thanSelold
    iel = 0
    dodo = []             # Undo/Redo list
    mes1 = T["Select a point of a line to move"]
    dilay = proj[1].thanLayerTree.dilay
    while True:
        opts = []
        if iel > 0: opts.append("undo")
        if len(dodo) > iel: opts.append("redo")
        if len(opts) > 0: mes = "%s (%s): " % (mes1, "/".join(opts))
        else:             mes = "%s: " % mes1
        opts.append("")
        res = thancomsel.thanSelect1Gen(proj, mes, filter=lambda e: isinstance(e, ThanLine), options=opts)
        if res == Canc: break                         # Trim was cancelled/ended
        if res == "": break                           # Trim was cancelled/ended
        if res == "u":
            iel -= 1
            delelems, newelems = dodo[iel]
            proj[1].thanElementDelete(newelems, proj)
            proj[1].thanElementRestore(delelems, proj)
            continue
        if res == "r":
            delelems, newelems = dodo[iel]
            proj[1].thanElementDelete(delelems, proj)
            proj[1].thanElementRestore(newelems, proj)
            iel += 1
            continue
        c1 = proj[2].thanSel1coor
        assert c1 is not None, "thancomsel.thanSelect1Gen does not work well!"
        for elem in proj[2].thanSelall:
            if len(elem.cp) > 0: break    # Get the element
        else:
            continue
        i = min((hypot(c1[0]-cp1[0], c1[1]-cp1[1]), i) for i,cp1 in enumerate(elem.cp))[1]
        stat = ""
        if i == 0:
            cc = proj[2].thanGudGetLine(elem.cp[1], stat, statonce="", options=())
        elif i == len(elem.cp)-1:
            cc = proj[2].thanGudGetLine(elem.cp[-2], stat, statonce="", options=())  #Here it is guarnteed that at least 2 points are present in the line
        else:
            cc = proj[2].thanGudGetLine2(elem.cp[i-1], elem.cp[i+1], stat, statonce="", options=())
        if cc == Canc: continue

        en = elem.thanClone()
        if retainz: en.cp[i][:2] = cc[:2]
        else:       en.cp[i][:] = cc
        newelems = [en]
        #lay = dilay[elem.thanTags[1]]
        #for e in newelems: proj[1].thanElementTag(e, lay)
        proj[1].thanElementDelete((elem,), proj)
        proj[1].thanElementRestore(newelems, proj)

        proj[2].thanUpdateLayerButton()               # Show current layer again
        del dodo[iel:]
        dodo.append(((elem,), newelems))
        iel += 1

    #proj[2].thanGudSetSelElem(elcut)          # The current selection (cutting edges)
    proj[2].thanGudSetSeloldElem(selold)      # The selection before the command trim started
    if iel == 0: return thanModCanc(proj)     # Trim was cancelled: unselect cutting edges
    delelems = []
    newelems = []
    for i in range(iel):
        delelemsi, newelemsi = dodo[i]
        for e in delelemsi:
            if e in newelems:      #If (e) was a previously new element, then (e) was an intermediate element
                #print e, "is intermediate"
                newelems.remove(e) #which is already deleted, and there is no need to recreate it and redelete it
            else:
                #print e, "is to be deleted"
                delelems.append(e)
        #print newelemsi, "are to be added"
        newelems.extend(newelemsi)
    #print "delelems=", delelems
    #print "newelems=", newelems

    proj[1].thanDoundo.thanAdd("movelinepoint", thanundo.thanReplaceRedo, (delelems, newelems, None),
                                                thanundo.thanReplaceUndo, (delelems, newelems, None))
    thanModEnd(proj)
