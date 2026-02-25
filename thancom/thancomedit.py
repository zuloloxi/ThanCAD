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
This module provides for a clipboard memory, shared among all ThanCad's
drawings."
"""

import copy
import p_ggen
from thanvar import Canc
from thantrans import T
from .thancomsel import thanSelectGen
from .thancommod import thanModCanc, thanModEnd


thanClip = p_ggen.Struct("ThanCad global clipboard")
thanClip.elems = []
thanClip.ref = [0.0, 0.0, 0.0]

#=============================================================================

def thanModUndo(proj):
    "Cancels previous command, restoring the drawing/display as it were before previous command."
    com = proj[1].thanDoundo.thanUndotry()
    if com is None: proj[2].thanGudCommandEnd(T["Nothing left to undo!"], "can"); return
    proj[2].thanPrt("Undo "+com)
    proj[1].thanDoundo.thanUndo(proj)
    proj[2].thanGudCommandEnd()

def thanModRedo(proj):
    "Cancels previous command, restoring the drawing/display as it were before previous command."
    com = proj[1].thanDoundo.thanRedotry()
    if com is None: return proj[2].thanGudCommandEnd(T["Nothing left to redo!"], "can")
    proj[2].thanPrt("Redo "+com)
    proj[1].thanDoundo.thanRedo(proj)
    proj[2].thanGudCommandEnd()

#=============================================================================

def thanClipCopybase(proj):
    "Copies selected elements to clipboard, with base point."
    c1 = proj[2].thanGudGetPoint(T["Base point: "])
    if c1 == Canc: return thanModCanc(proj)             # clipboard copy with base was cancelled
    thanClipCopy(proj, c1)

def thanClipCopy(proj, c1=None):
    "Copies selected elements to clipboard."
    res = thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)            # clipboard copy was cancelled
    elems = proj[2].thanSelall
    if len(elems) == 0: return thanModCanc(proj, T["No elements found"])  # No elements selected
    if c1 is None:
        c1 = next(iter(elems)).getInspnt()
        c1[2] = proj[1].thanVar["elevation"][2] #So that z is taken from the elevation command
    selold = proj[2].thanSelold
    __clipCopyDo(proj, c1)
    proj[1].thanDoundo.thanAdd("copyclip", thanClipCopyRedo, (elems,),
                                           thanClipCopyUndo, (selold,))
    thanModEnd(proj, "%d %s." % (len(elems), T["element(s) copied to clipboard"]), "info")   # 'Reset color" is necessary here


def __clipCopyDo(proj, c1):
    "Copies selected elements to clipboard; it actually does the job."
    import time
    dcop = copy.deepcopy
    t1 = time.time()
    thanClip.elems = [dcop(e) for e in proj[2].thanSelall]
    thanClip.ref = c1
    t2 = time.time()
    #print "Copied to clipboard in", t2-t1, "secs"


def thanClipCopyRedo(proj, elems):
    "WARNING: the elements are NOT copied to clipboard; only the selection is updated."
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(elems)
    proj[2].thanCom.thanAppend(T["\nWARNING: Clipboard is unaffected."], "info")

def thanClipCopyUndo(proj, selold):
    "WARNING: the elements are NOT removed from the clipboard; only the selection is undone."
    global thanClip
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(selold)
    proj[2].thanCom.thanAppend(T["\nWARNING: Clipboard is unaffected."], "info")

#============================================================================

def thanClipCut(proj, c1=None):
    "Copies selected elements to clipboard and deletes them from the drawing."
    res = thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # clipboard cut was cancelled
    elems = proj[2].thanSelall
    if len(elems) == 0: return thanModCanc(proj, T["No elements found"])  # No elemements selected
    if c1 is None:
        c1 = next(iter(elems)).getInspnt()
        c1[2] = proj[1].thanVar["elevation"][2] #So that z is taken from the elevation command
    selold = proj[2].thanSelold
    __clipCutDo(proj, c1)
    proj[1].thanDoundo.thanAdd("cutclip", thanClipCutRedo, (elems,),
                                          thanClipCutUndo, (elems, selold))
    thanModEnd(proj, "%d %s." % (len(elems), T["element(s) copied to clipboard"]), "info")   # 'Reset color" is completely unnecessary here..
                                                                    # ..so there is room for optimisation
def __clipCutDo(proj, c1):
    "Copies selected elements to clipboard; it actually does the job."
    dcop = copy.deepcopy
    thanClip.elems = [dcop(e) for e in proj[2].thanSelall]  # Deepcopy, in case the elements are..
    thanClip.ref = c1                                       # .. "un-cut" and then changed
    __modEraseDo(proj)

def __modEraseDo(proj):
    "Erases selected elements; it actually does the job."
    import time
    t1 = time.time()
    proj[2].thanGudSetSelDel()
    proj[2].thanImages.difference_update(proj[2].thanSelall)  #Delete deleted images from thanImages
    t2 = time.time(); proj[1].thanDelSel(proj[2].thanSelall)  #thanTouch is implicitly called
    t3 = time.time()
    #print "Erase time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t2-t1, t3-t2, t3-t1)
    proj[2].thanGudSetSelClear()

def thanClipCutRedo(proj, elems):
    "Erases selected elements; it actually does the job."
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(elems)
    __modEraseDo(proj)
    proj[2].thanCom.thanAppend(T["\nWARNING: Clipboard is unaffected."], "info")

def thanClipCutUndo(proj, elems, selold):
    """WARNING: the elements are NOT removed from the clipboard.

    The elements are undeleted and the selection is undone.
    The elements' structure is considered complete.
    """
    proj[1].thanElementRestore(elems, proj)
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(selold)
    proj[2].thanCom.thanAppend(T["\nWARNING: Clipboard is unaffected."], "info")

#============================================================================

def thanClipPaste(proj):
    "Pastes clipboard elements with respect to base point."
    if len(thanClip.elems) == 0: return proj[2].thanGudCommandCan(T["No elements in clipboard"])

    ccu = list(proj[1].thanVar["elevation"])
    ccu[:2] = proj[2].thanCt.local2Global(proj[2].thanCanvas.thanXcu, proj[2].thanCanvas.thanYcu)
    dc = [b-a for a,b in zip(thanClip.ref, ccu)]   #works for python2,3
    c2 = proj[2].thanGudGetMovend(ccu, T["Insertion point"]+": ", thanClip.elems, dc)

    if c2 == Canc: return proj[2].thanGudCommandCan()           # Paste command was cancelled
    selall = proj[2].thanSelall     # No selection is made; this is the selection than select will..
                                    # ..return, if select previous is executed
    copelems = __clipPasteDo(proj, thanClip.ref, c2)
    proj[1].thanDoundo.thanAdd("pasteclip", thanClipPasteRedo, (copelems, selall),
                                            thanClipPasteUndo, (copelems, selall))
    thanModEnd(proj, "%d %s." % (len(copelems), T["element(s) copied from clipboard"]), "info")   # 'Reset color" is necessary here

def thanClipPasteorig(proj):
    "Pastes clipboard elements to the original coordinates."
    selall = proj[2].thanSelall     # No selection is made; this is the selection which select will
                                    # return, if select previous is executed
    copelems = __clipPasteDo(proj, thanClip.ref, thanClip.ref)
    proj[1].thanDoundo.thanAdd("pasteorig", thanClipPasteRedo, (copelems, selall),
                                            thanClipPasteUndo, (copelems, selall))
    thanModEnd(proj, "%d %s." % (len(copelems), T["element(s) copied from clipboard"]), "info")   # 'Reset color" is necessary here

def __clipPasteDo(proj, c1, c2):
    "Pastes the clipboard elements to the drawing, current layer."
    dc = [b-a for a,b in zip(c1, c2)]  #works for python2,3
    dcop = copy.deepcopy
    copelems = []
    dr = proj[1]
    for e1 in thanClip.elems:
        e = dcop(e1)
        e.thanMove(dc)
        e1 = proj[1].thanTagel.get(e.handle)
        #if we get the elements with cutclip, their handles have been deleted from thanTagel..
        #and when they are pasted for the first time, they keep their original handle.
        if e1 is not None: e.thanUntag()           #Invalidate tag because tag already exists in the drawing
        dr.thanElementAdd(e)
        e.thanTkDraw(proj[2].than)
        copelems.append(e)
    return copelems

def thanClipPasteRedo(proj, elems, selall):
    """Re-pastes the previously unpasted elements.

    WARNING: the previously unpasted elements are restored. The contents of the
    clipboard may be completely different.
    The elements' structure is considered complete.
    """
    proj[1].thanElementRestore(elems, proj)
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(selall)
    proj[2].thanCom.thanAppend(T["\nWARNING: Clipboard is unaffected."], "info")

def thanClipPasteUndo(proj, elems, selall):
    "Erases the previously pasted elements."
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(elems)
    __modEraseDo(proj)
    proj[2].thanGudSetSelElem(selall)
