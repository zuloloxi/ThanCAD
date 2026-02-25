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
This module provides the mechanism for element selection."
"""

from thanvar import Canc
from thantrans import T

#Example:
#    thanSelectOr(proj, standalone=False, filter=lambda e:isinstance(e, ThanLine),
#        optionname="settings", optiontext="s=settings")
#The option must not begin with the same letter as a standard option (w/c/l/p)

def thanSelectOr(proj, standalone=True, filter=None, optionname="", optiontext="", enter=0):
    "Select objects or general select command."
    proj[2].thanGudSetSelSave()                              # Save old selection
    selmodified = False
    stat = T["Select an element (w=window/c=crossing/l=layers/f=layer of/p=previous/%s): "] % optiontext
    opts = "", "window", "crossing", "layers", "f", "previous", optionname
    proj[2].thanSel1coor = None
    proj[2].thanCanvas.thanChs.thanPush(-2)                  # Save previous croshair; set rectangle croshair
    proj[2].thanGudSetSelExternalFilter(filter)
    first = True
    while True:
        proj[2].thanCanvas.thanChs.thanSet(-2)               # Set rectangle croshair
        proj[2].thanSelectLayButton = True                   # User can press the layer button
        com = proj[2].thanGudGetPoint(stat, options=opts)
        proj[2].thanSelectLayButton = False                  # The layer button is inactive now
        if com == Canc: break                                # Selection was cancelled
        if first and com == optionname[:1]: break
        if com == "":                                        # Selection was ended..
            if not first or enter == 0: break                # ..enter has no special meaning -> end
            c1 = proj[1].viewPort[:2]                        # ..enter means select (crossing) all in current view
            c2 = proj[1].viewPort[2:]
            res = proj[2].thanGudGetSelCros(c1[0], c1[1], c2[0], c2[1])
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        elif com == "p":                                     # Previous selection
            res = proj[2].thanGudGetSelOld()
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        elif com == "w" or com == "c":                       # Select window/crossing
            proj[2].thanCanvas.thanChs.thanSet(0)            # Set big croshair
            c1 = proj[2].thanGudGetPoint(T["First window corner: "])
            if c1 == Canc: continue
            res = __corner2(proj, c1, com)
            if res == Canc: continue
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        elif com == "l":                                     # Select layer(s)
            proj[2].thanCanvas.thanChs.thanSet(0)            # Set big croshair
            res = proj[2].thanGudGetLayerleafs(T["Select layer(s)"])
            if res == Canc: continue
            res = proj[2].thanGudGetSelLayers(res)
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        elif com == "f":                                     # Select layer(s)
            while True:
                res = proj[2].thanGudGetPoint(T["Select an element that belongs to desired layer: "])
                if res == Canc: break
                c1 = res
                res = proj[2].thanGudGetSel1(c1[0], c1[1])   # Try to select 1 element..
                if res[0] > 0: break
            if res == Canc: continue
            for e in proj[2].thanSel: break                  # Get selected element
            tlay = e.thanTags[1]
            lay = proj[1].thanLayerTree.dilay[tlay]
            res = proj[2].thanGudGetSelLayers([lay])
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        else:                                                # Select 1
            c1 = com
            res = proj[2].thanGudGetSel1(c1[0], c1[1])       # Try to select 1 element..
            if res[0] == 0:                                  # Selection of 1 element is successful
                proj[2].thanCanvas.thanChs.thanSet(0)        # Set big croshair
                res = __corner2(proj, c1, "cw")              # Selection of 1 element failed; try window/crossing
                if res == Canc: continue
                proj[2].thanSel1coor = None                  # This is the first point in the 'break' command
            else:
                proj[2].thanSel1coor = c1                    # This is the first point in the 'break' command

        proj[2].thanGudSetSelColor()
        selmodified = True
        if com == "p" and res[0] == 0:
            proj[2].thanCom.thanAppend("%s\n" % T["Invalid or empty previous selection."], "can")
        else:
            st = "%d %s (%d %s).\n" % (res[0], T["elements added"], res[1], T["duplicate"])
            proj[2].thanCom.thanAppend(st, "info")
        proj[2].thanUpdateLayerButton(selected=True)
        if first and com == "": assert enter != 0; break    #A special meaning was given to enter; it was processed; end now
        if first:
            first = False
            stat = T["Select an element (w=window/c=crossing/l=layers/f=layer of/p=previous): "]
            opts = "", "window", "crossing", "layers", "f", "previous"

    proj[2].thanCanvas.thanChs.thanPop()                     # Restore previous croshair
    proj[2].thanGudSetSelcurClear()                          # Clears current selection (which is already inside selall)
    proj[2].thanGudSetSelExternalFilter(None)                # Reset filter
    if standalone:
        from .thancommod import thanModCanc, thanModEnd
        if com == Canc: return thanModCanc(proj)
        proj[1].thanDoundo.thanAdd("select", thanModSelectRedo, (proj[2].thanSelall,),
                                             thanModSelectUndo, (proj[2].thanSelold,))
        thanModEnd(proj)
    return com


def thanSelectGen(proj, standalone=True, filter=None):
    "General select command."
    proj[2].thanGudSetSelSave()                              # Save old selection
    selmodified = False
    stat = T["Select an element (w=window/c=crossing/l=layers/f=layer of/p=previous): "]
    opts = "", "window", "crossing", "layers", "f", "previous"
    proj[2].thanSel1coor = None
    proj[2].thanCanvas.thanChs.thanPush(-2)                  # Save previous croshair; set rectangle croshair
    proj[2].thanGudSetSelExternalFilter(filter)
    while True:
        proj[2].thanCanvas.thanChs.thanSet(-2)               # Set rectangle croshair
        proj[2].thanSelectLayButton = True                   # User can press the layer button
        com = proj[2].thanGudGetPoint(stat, options=opts)
        proj[2].thanSelectLayButton = False                  # The layer button is inactive now
        if com == Canc or com == "": break                   # Selection was cancelled or ended
        if com == "p":                                       # Previous selection
            res = proj[2].thanGudGetSelOld()
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        elif com == "w" or com == "c":                       # Select window/crossing
            proj[2].thanCanvas.thanChs.thanSet(0)            # Set big croshair
            c1 = proj[2].thanGudGetPoint(T["First window corner: "])
            if c1 == Canc: continue
            res = __corner2(proj, c1, com)
            if res == Canc: continue
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        elif com == "l":                                     # Select layer(s)
            proj[2].thanCanvas.thanChs.thanSet(0)            # Set big croshair
            res = proj[2].thanGudGetLayerleafs(T["Select layer(s)"])
            if res == Canc: continue
            res = proj[2].thanGudGetSelLayers(res)
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        elif com == "f":                                     # Select layer(s)
            while True:
                res = proj[2].thanGudGetPoint(T["Select an element that belongs to desired layer: "])
                if res == Canc: break
                c1 = res
                res = proj[2].thanGudGetSel1(c1[0], c1[1])   # Try to select 1 element..
                if res[0] > 0: break
            if res == Canc: continue
            for e in proj[2].thanSel: break                  # Get selected element
            tlay = e.thanTags[1]
            lay = proj[1].thanLayerTree.dilay[tlay]
            res = proj[2].thanGudGetSelLayers([lay])
            proj[2].thanSel1coor = None                      # This is the first point in the 'break' command
        else:                                                # Select 1
            c1 = com
            res = proj[2].thanGudGetSel1(c1[0], c1[1])       # Try to select 1 element..
            if res[0] == 0:                                  # Selection of 1 element is successful
                proj[2].thanCanvas.thanChs.thanSet(0)        # Set big croshair
                res = __corner2(proj, c1, "cw")              # Selection of 1 element failed; try window/crossing
                if res == Canc: continue
                proj[2].thanSel1coor = None                  # This is the first point in the 'break' command
            else:
                proj[2].thanSel1coor = c1                    # This is the first point in the 'break' command

        proj[2].thanGudSetSelColor()
        selmodified = True
        if com == "p" and res[0] == 0:
            proj[2].thanCom.thanAppend("%s\n" % T["Invalid or empty previous selection."], "can")
        else:
            st = "%d %s (%d %s).\n" % (res[0], T["elements added"], res[1], T["duplicate"])
            proj[2].thanCom.thanAppend(st, "info")
        proj[2].thanUpdateLayerButton(selected=True)

    proj[2].thanCanvas.thanChs.thanPop()                     # Restore previous croshair
    proj[2].thanGudSetSelcurClear()                          # Clears current selection (which is already inside selall)
    proj[2].thanGudSetSelExternalFilter(None)                # Reset filter
    if standalone:
        from .thancommod import thanModCanc, thanModEnd
        if com == Canc: return thanModCanc(proj)
        proj[1].thanDoundo.thanAdd("select", thanModSelectRedo, (proj[2].thanSelall,),
                                             thanModSelectUndo, (proj[2].thanSelold,))
        thanModEnd(proj)
    return com


def thanModSelectRedo(proj, elems):
    "Re-selects the previously un-selected elements."
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(elems)


def thanModSelectUndo(proj, selold):
    "Un-selects the previously selected elements."
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(selold)


def __corner2(proj, c1, com):
    "Get the other corner of a window/crossing."
    c2 = proj[2].thanGudGetRect(c1, T["Other window corner: "], com=com)
    if c2 == Canc: return c2                                        # Selection cancelled
    if com == "c" or (com == "cw" and c2[0] < c1[0]):
        res = proj[2].thanGudGetSelCros(c1[0], c1[1], c2[0], c2[1]) # Select crossing
    else:
        res = proj[2].thanGudGetSelWin( c1[0], c1[1], c2[0], c2[1]) # Select window
    return res


def thanSelect1Gen(proj, stat, filter=None, options=()):
    """Selects 1 (breakable) element (of a certain class).

    This routine is as close to thanSelectGen as possible.
    Use the utility routine 'thanSelect1' to get the element explicitly
    """
    proj[2].thanGudSetSelSave()                              # Save old selection
    statonce = ""
    proj[2].thanSel1coor = None
    proj[2].thanCanvas.thanChs.thanPush(-2)                  # Save previous croshair; set rectangle croshair
    proj[2].thanGudSetSelExternalFilter(filter)
    while True:
        proj[2].thanCanvas.thanChs.thanSet(-2)               # Set rectangle croshair
        com = proj[2].thanGudGetPoint(stat, statonce, options=options)
        if com == Canc or com == "": break                   # Selection was cancelled or ended
        if any(com==o1[:1].lower() for o1 in options): break         # Option given
        c1 = com
        res = proj[2].thanGudGetSel1(c1[0], c1[1])       # Try to select 1 element..
        if res[0] == 0:                                  # Selection of 1 element is successful
            statonce = T["No element selected. Try again."] + "\n"
            proj[2].thanGudResetSelColor()           # Unmarks the selection
            proj[2].thanGudSetSelRestore()           # Restores previous selection (the cutting edges)
#            proj[2].thanUpdateLayerButton()         # Show current layer again; not needed: the button has not changed color
            proj[2].thanGudSetSelSave()              # Save old selection
            continue
        for elem in proj[2].thanSelall: break        # thanSelall is set()
        proj[2].thanSel1coor = c1                    # This is the first point in the 'break' command
        proj[2].thanGudSetSelColor()
#        st = "%d %s (%d %s).\n" % (res[0], T["elements added"], res[1], T["duplicate"])
#        proj[2].thanCom.thanAppend(st, "info")
        proj[2].thanUpdateLayerButton(selected=True)
        break
    proj[2].thanCanvas.thanChs.thanPop()             # Restore previous croshair
    proj[2].thanGudSetSelcurClear()                  # Clears current selection (which is already inside selall)
    proj[2].thanGudSetSelExternalFilter(None)        # Reset filter
    proj[2].thanGudResetSelColor()                   # Unmarks the selection
    proj[2].thanUpdateLayerButton()                  # Show current layer again
    return com


def thanSelect1(proj, stat, filter=None, options=()):
    "Wrapper to thanSelect1 to return the selected element explicitly."
    res = thanSelect1Gen(proj, stat, filter=filter, options=options)
    if res == Canc: return Canc                       # Select was cancelled
    if any(res==o1[:1].lower() for o1 in options): return res # Option given
    c1 = proj[2].thanSel1coor
    assert c1 is not None, "thancomsel.thanSelect1Gen does not work well!"
    for elem in proj[2].thanSelall: break             # Get the selected element
    return elem                                       # Return the element
