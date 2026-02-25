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
This module the do/undo mechanism.
"""

from thantrans import T
from p_ggen import Canc


def thanUndoWarn(proj):
    "Print a warning message that the command will clear undo history."
    proj[2].thanCom.thanAppend("%s\n" % T["(Warning: This command, if completed, can not be undone)"], "can1")


def thanUndoClear(proj):
    "Clears the do/undo list of the current drawing."
    proj[1].thanDoundo.clear()


def thanActionRedo(proj, elems, actionfun, *args):
    "Select elements and performs an action function on the selected elements (with arbitrary arguments)."
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(elems)
    actionfun(proj, *args)


def thanActionUndo(proj, elems, selold, actionfun, *args):
    "Select elements and performs an action function on the selected elements (with arbitrary arguments); then reselects previously selected elements."
    "Un-rotates the previously rotated elements."
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(elems)
    actionfun(proj, *args)
    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(selold)


def thanReplaceUndo2(proj, delelems, newelems, selold=None, crelold=None):
    "Include crelold in the actions to undo."
    thanReplaceUndo(proj, delelems, newelems, selold, crelold=crelold)

def thanReplaceRedo2(proj, delelems, newelems, selelems=None, crel=None):
    "Include crel in the actions to redo."
    thanReplaceRedo(proj, delelems, newelems, selelems, crel=crel)


def thanReplaceUndo(proj, delelems, newelems, selold=None, oldvars={}, delobjs=(), newobjs=(), crelold=None):
    """Undeletes the previously deleted elements, and deletes the previously created new elements.

    The order should be: first delete elements then create the elements. This is
    because in many commands the new elements take the identity of the old
    elements, and thus the delete command will delete both :)
    """
    if selold is None: selold = proj[2].thanSelall

    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(newelems)
    proj[2].thanGudSetSelDel()
    proj[2].thanImages.difference_update(newelems) # Delete deleted images from thanImages
    proj[1].thanDelSel(newelems)                   # thanTouch is implicitly called

    proj[1].thanElementRestore(delelems, proj)     # thanTouch is implicitly called, thanImages is updated through ThanImage.thanTkDraw1()
    proj[2].thanGudSetSelElem(selold)
    proj[1].thanVar.update(oldvars)
    thanObjsRestore(proj, newobjs, delobjs)
    proj[1].thanSetLastPoint(crelold)


def thanReplaceRedo(proj, delelems, newelems, selelems=None, newvars={}, delobjs=(), newobjs=(), crel=None):
    """Redeletes the deleted elements, and recreates the new elements.

    The order should be: first delete elements then create the elements. This is
    because in many commands the new elements take the identity of the old
    elements, and thus the delete command will delete both :)
    """
    if selelems is None: selelems = proj[2].thanSelall

    proj[2].thanGudSetSelClear()
    proj[2].thanGudSetSelElem(delelems)
    proj[2].thanGudSetSelDel()
    proj[2].thanImages.difference_update(delelems) # Delete deleted images from thanImages
    proj[1].thanDelSel(delelems)                   # thanTouch is implicitly called

    proj[1].thanElementRestore(newelems, proj)     # thanTouch is implicitly called, thanImages is updated through ThanImage.thanTkDraw1()
    proj[2].thanGudSetSelElem(selelems)
    proj[1].thanVar.update(newvars)
    thanObjsRestore(proj, delobjs, newobjs)
    proj[1].thanSetLastPoint(crel)


def thanObjsRestore(proj, delobjs, addobjs):
    "Restores objects."
    for name, obj1 in delobjs:
        proj[1].thanObjects[name].remove(obj1)
    for name, obj1 in addobjs:
        proj[1].thanObjects[name].append(obj1)
    if len(delobjs)+len(addobjs) > 0: proj[1].thanTouch()


def thanLtClone(proj):
    """Clones the necessary attributes of layer tree.

    The elements are not copied at all. Only a reference to the structure
    which holds the elements of every layer is copied.
    """
    lt = proj[1].thanLayerTree
    temp = lt.thanRoot.thanClone()
    names = lt.thanCur.thanGetPathname().split("/")
    cl = temp.thanFind(names)
    assert cl is not None, "Current layer should have been found!"
    return cl, temp


def thanLtClone2(cl, root):
    """Clones the necessary attributes of layer tree.

    The elements are not copied at all. Only a reference to the structure
    which holds the elements of every layer is copied.
    """
    newroot = root.thanClone()
    names = cl.thanGetPathname().split("/")
    newcl = newroot.thanFind(names)
    assert newcl is not None, "Current layer should have been found!"
    return newcl, newroot


def thanLtRestore(proj, cl, root=None, leaflayers=None):
    """Restores a previously altered layer tree."

    This function can be used in 4 ways:
    1. Only the current layer is restored (root=None, leaflayers=None).
       This is useful when a command changes only the current layer.
    2. The current layer and the entire layer tree is restored (leaflayers=None).
       This is useful when new empty layers have been added or old
       layers have been purged.
    3. The current layer, the entire layer tree is restored and the new layers
       affects element already drawn on the screen (leaflayers=dictionary).
       This is useful when new layers have been added and elements have been
       added to them. Leaflayers is a dictionary with keys the layers and values
       the attributes of the layers which affect already drawn elements.
    4. The current layer, the entire layer tree is restored and the new layers
       affects element already drawn on the screen (leaflayers="regen").
       It is an alternative to case 3 when we do not know which leaflayers
       are affected. A regen is done.
    """
    import thanlayer
    lt = proj[1].thanLayerTree
    lt.thanCur = cl
    if root is not None:
#        lt.thanRoot.thanDestroy()
        lt.thanRoot = root
        lt.thanDictRebuild()
    if leaflayers != "regen":
        if leaflayers is None: leaflayers = {}
        draworder = thanlayer.thanlayatts.thanUpdateElements(proj, leaflayers)
        if draworder: proj[2].thanRedraw()                         # Set relative draworder
    else:
        proj[2].thanRegen()
    lt.thanCur.thanTkSet(proj[2].than)                         # Set Attributes of the current layer
    proj[2].thanUpdateLayerButton()
    proj[1].thanTouch()                                        # Drawing IS modified


def thanRetainUndo(proj, code=0):
    "Purge do/undo history."
    if code == 0:
        proj[2].thanPrter(T["WARNING: This command can not be undone, and it will purge the do/undo history."])
    else:
        proj[2].thanPrter(T["WARNING: This command will take a long time, it can not be undone, and it will purge the do/undo history."])
    ans = proj[2].thanGudGetYesno(T["Are you sure you want to proceed (enter=no): "], default=False)
    if ans == Canc: return True # User cancelled the command
    if not ans:     return True # User cancelled the command
    proj[1].thanDoundo.clear()
    return False
