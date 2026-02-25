##############################################################################
# ThanCad 0.1.2 "Free": 2dimensional CAD with raster support for engineers.
#
# Copyright (c) 2001-2010 Thanasis Stamos,  December 23, 2010
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.1.2 "Free": 2dimensional CAD with raster support for engineers.

This module implements various types of compound list, based on the generic
compound list.
"""

import types
from tkinter import Frame, Button
import p_ggen
from p_ggen import ThanLayerError, Canc
from . import thanwids, xinp
from .thantkclist import (ThantkClistBare, ThanMixinUtil, ThantkClistHierBare, ThanMixinHierUtil,
    ThanMixinPartial, ThanMixinHierUtil1, _EXPAND)
from .thantkutila import thanGudModalMessage, thanGudAskOkCancel
from .thanwidstrans import T


#############################################################################
#############################################################################

class ThantkClist1(ThantkClistBare):
    "Parallel Tk listboxes working as one; activates bare mechanism."
    def __init__(self, master, objs, **kw):
        "Create the parallel lists boxes, and their actions."
        ThantkClistBare.__init__(self, master, **kw)
        self.thanListsPlace(0, 0)
        self.thanListsFill(objs)

class ThantkClist11(ThantkClist1, ThanMixinUtil):
    """Parallel Tk listboxes working as one.

    Activates bare mechanism and selection capabilities
    but without button box."""


#############################################################################
#############################################################################

class ThantkClist2(ThantkClistBare, ThanMixinUtil):
    "Parallel Tk listboxes working as one; bare mechanism."

#============================================================================

    def __init__(self, master, objs, **kw):
        "Create the parallel lists boxes, bare plus selection buttons."
        ThantkClistBare.__init__(self, master, **kw)
        self.thanCreateButtons(self, 0, 0)
        self.thanListsPlace(1, 0)
        self.thanListsFill(objs)

#============================================================================

    def thanCreateButtons(self, master, ir, ic):
        "Creates utilities buttons."
        S = p_ggen.ThanStub
        fraBut = Frame(master)
        fraBut.grid(row=ir, column=ic, columnspan=len(self.thanAtts))
        but = thanwids.ThanButton(fraBut, text=T["Select All"], command=S(self.thanSchedule1, self.thanSelAll))
        but.grid(row=ir, column=0)
        but = thanwids.ThanButton(fraBut, text=T["Deselect All"], command=S(self.thanSchedule1, self.thanSelNone))
        but.grid(row=ir, column=1)
        but = thanwids.ThanButton(fraBut, text=T["Invert selection"], command=S(self.thanSchedule1, self.thanSelInvert))
        but.grid(row=ir, column=2)
        return 1, 0


#############################################################################
#############################################################################

class ThantkClist3(ThantkClistHierBare, ThanMixinHierUtil):
    "Hierarchical parallel lists."

#============================================================================

    def __init__(self, master, objs, **kw):
        "Create the parallel lists boxes, bare plus selection buttons."
#        apply(ThantkClistHierBare.__init__, (self, master), kw)
        ThantkClistHierBare.__init__(self, master, **kw)
        self.thanCreateButtons(self, 0, 0)
        self.thanListsPlace(1, 0)
        self.thanListsFill(objs)

#============================================================================

    def thanCreateButtons(self, master, ir, ic):
        "Creates utilities buttons."
        S = self.thanStub
        fraBut = Frame(master)
        fraBut.grid(row=ir, column=ic, columnspan=len(self.thanAtts))
        but = thanwids.ThanButton(fraBut, text=T["Select All"], command=S(self.thanSchedule1, self.thanSelAll))
        but.grid(row=ir, column=0)
        but = thanwids.ThanButton(fraBut, text=T["Deselect All"], command=S(self.thanSchedule1, self.thanSelNone))
        but.grid(row=ir, column=1)
        but = thanwids.ThanButton(fraBut, text=T["Invert selection"], command=S(self.thanSchedule1, self.thanSelInvert))
        but.grid(row=ir, column=2)
        return 1, 0


#############################################################################
#############################################################################

class ThantkClist4(ThantkClistHierBare, ThanMixinHierUtil, ThanMixinPartial):
    "Hierarchical partial parallel lists."

#============================================================================

    def __init__(self, master, objs, **kw):
        "Create the parallel lists boxes, bare plus selection buttons."
#        apply(ThantkClistHierBare.__init__, (self, master), kw)
        ThantkClistHierBare.__init__(self, master, **kw)
        ThanMixinPartial.__init__(self)
        self.thanCreateButtons(self, 0, 0)
        self.thanListsPlace(2, 0)
        self.thanListsFill(objs)
        self.thanMakePartial()

#============================================================================

    def thanCreateButtons(self, master, ir, ic):
        "Creates utilities buttons."
        S = self.thanStub
        fraBut = Frame(master)
        fraBut.grid(row=ir, column=ic, columnspan=len(self.thanAtts), sticky="we")
        for i in (0,1): fraBut.columnconfigure(i, weight=1)

        but = thanwids.ThanButton(fraBut, text=T["Previous set"], command=S(self.thanSchedule1, self.thanSetPrev))
        but.grid(row=0, column=0, sticky="w")
        but = thanwids.ThanButton(fraBut, text=T["Next set"], command=S(self.thanSchedule1, self.thanSetNext))
        but.grid(row=0, column=1, sticky="e")

        fraBut = Frame(master)
        fraBut.grid(row=ir+1, column=ic, columnspan=len(self.thanAtts), sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Select All"], command=S(self.thanSchedule1, self.thanSelAll))
        but.grid(row=ir, column=0)
        but = thanwids.ThanButton(fraBut, text=T["Deselect All"], command=S(self.thanSchedule1, self.thanSelNone))
        but.grid(row=ir, column=1)
        but = thanwids.ThanButton(fraBut, text=T["Invert selection"], command=S(self.thanSchedule1, self.thanSelInvert))
        but.grid(row=ir, column=2)

        return 2, 0


#############################################################################
#############################################################################

class ThantkClist5(ThantkClistHierBare, ThanMixinHierUtil1, ThanMixinPartial):
    "Hierarchical partial parallel lists."

#============================================================================

    def __init__(self, master, objs, current, **kw):
        "Create the parallel lists boxes, bare plus selection buttons."
        self.__state = 1                                   # Window is alive
        self.thanCargo = kw.pop("cargo", None)
        ThantkClistHierBare.__init__(self, master, **kw)
        ThanMixinPartial.__init__(self)
        self.thanCur = current
        print("cur1=", self.thanCur)

        self.thanCreateButtonsup(self, 0, 0)
        (nr, nc) = self.thanListsPlace(1, 0)
        self.thanCreateButtonsdown(self, 1+nr, 0)
        self.thanListsFill(objs)
        self.thanMakePartial(hlen=70)
        self.thanLeaflayers = {}

#============================================================================

    def thanInsert2Lists(self, i, layers, prefix):
        """Inserts lays to the lists.

        This is exactly the same as the overridden function in class ThantkClistHierBare
        with the exception of braces at the values, if the values
        are inherited.
        """
        for lay in layers:
            i += 1
            self.thanListLayers.insert(i, lay)     # layer pointer

            for att in self.thanAtts:
                li = self.thanLists[att]
                if att == self.thanAttmain:
                    li.thanInsert(i, prefix+str(lay.thanAtts[att]))
                elif att == _EXPAND:
                    li.thanInsert(i, lay.thanAtts[att].thanVal)
                else:
                    t = str(lay.thanAtts[att])
                    if lay.thanAtts[att].thanInher: t = "["+t+"]"
                    li.thanInsert(i, t)

            if lay.thanAtts[_EXPAND].thanVal == "-":
                i = self.thanInsert2Lists(i, lay.thanChildren, prefix+"....")
        return i

#============================================================================

    def thanCreateButtonsup(self, master, ir, ic):
        "Creates utilities buttons."
        S = self.thanStub
        fraBut = Frame(master)
        fraBut.grid(row=ir, column=ic, columnspan=len(self.thanAtts), sticky="we")
        for i in (0,1,2,3): fraBut.columnconfigure(i, weight=1)

        but = thanwids.ThanButton(fraBut, text=T["Previous set"], command=S(self.thanSchedule1, self.thanSetPrev))
        but.grid(row=0, column=0, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Next set"], command=S(self.thanSchedule1, self.thanSetNext))
        but.grid(row=1, column=0, sticky="we")

        but = thanwids.ThanButton(fraBut, text=T["Select All"], command=S(self.thanSchedule1, self.thanSelAll))
        but.grid(row=0, column=3, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Deselect All"], command=S(self.thanSchedule1, self.thanSelNone))
        but.grid(row=1, column=3, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Invert selection"], command=S(self.thanSchedule1, self.thanSelInvert))
        but.grid(row=2, column=3, sticky="we")

        but = thanwids.ThanButton(fraBut, text=T["New Layer"], command=S(self.thanSchedule1, self.thanLayerChildNew))
        but.grid(row=0, column=1, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Rename Layer"], command=S(self.thanSchedule1, self.thanLayerRen1))
        but.grid(row=1, column=1, sticky="we")
#        but = thanwids.ThanButton(fraBut, text="Delete Layer", command=S(self.thanSchedule1, self.thanSelDelete))
#        but.grid(row=3, column=1, sticky="we")

        but = thanwids.ThanButton(fraBut, text=T["Copy"], command=S(self.thanSchedule1, self.thanSelCopy))
        but.grid(row=0, column=2, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Paste"], command=S(self.thanSchedule1, self.thanSelPaste))
        but.grid(row=1, column=2, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Cut"], command=S(self.thanSchedule1, self.thanSelCut))
        but.grid(row=2, column=2, sticky="we")

        self.__cl = thanwids.ThanEntry(fraBut)
        self.__cl.thanSet(self.thanCur.thanGetPathname())
        self.__cl.grid(row=4, column=0, columnspan=3, sticky="we", pady=10)
        but = thanwids.ThanButton(fraBut, text=T["Set Current"], command=S(self.thanSchedule1, self.thanSetCur))
        but.grid(row=4, column=3, sticky="we", pady=10)

        return 1, 0


#============================================================================

    def thanLayerRen1(self, *args):
        "Renames the selected layer; updates current layer."
        lay = self.thanLayerRen()
        if lay == Canc: return
        if lay != self.thanCur: return
        self.__cl.thanSet(self.thanCur.thanGetPathname())   # Update name of current layer

    def thanSetCur(self, *args):
        indexes = self.thanLimain.curselection()
        lays = [self.thanListLayers[int(j)] for j in indexes]
        self.thanTryCur(lays)

    def thanTryCur(self, lays):
        "Try to set current layer one of the given layers (lays)."
        for lay in lays:
            if len(lay.thanChildren) == 0:     # Only leaflayers can be current
                self.thanCur = lay
                self.__cl.thanSet(self.thanCur.thanGetPathname())
                self.thanModified = True
                return True
        return False

#============================================================================

    def thanCreateButtonsdown(self, master, ir, ic):
        "Creates utilities buttons."
        S = self.thanStub
        fraBut = Frame(master)
        fraBut.grid(row=ir, column=ic, columnspan=len(self.thanAtts), sticky="we")
        for i in (0,1,2,3): fraBut.columnconfigure(i, weight=1)

        but = thanwids.ThanButton(fraBut, text=T["Cancel"], command=S(self.thanSchedule1, self.thanCancel))
        but.grid(row=0, column=0, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["OK"], command=S(self.thanSchedule1, self.thanOK))
        but.grid(row=0, column=3, sticky="we")

#============================================================================

    def thanCancel(self, *args):
        "What to do when user cancels."
        if self.thanModified:
            ok = thanGudAskOkCancel(self,
            message=T["The layer hierarchy has been modified\nAbandon changes?"],
            title=T["Layers modified"])
            if not ok: return
        self.__result = None, None
        self.__state = 0                       # window is dead

#============================================================================

    def thanOK(self, *args):
        "What to do when user OKs."
        if self.thanClipMovePending(): return
        self.__result = self.thanLeaflayers, self.thanCur
        self.__state = 0                       # window is dead
        print("***tra1")

#============================================================================

    def thanWait(self, *args):
        "Waits until user finishes."
        while self.__state:
            self.update_idletasks()
        print("***tra2")
#        self.destroy()
        del self.thanCargo
        return self.__result

    def destroy(self):
        "Break circular references."
        print("cur2=", self.thanCur)
        del self.thanCur, self.__cl
        ThantkClistHierBare.destroy(self)

    def __del__(self):
        print("clist5 recycled.")


#############################################################################
#############################################################################

class ThantkClist6(ThantkClistHierBare, ThanMixinHierUtil1, ThanMixinPartial):
    "Hierarchical partial parallel lists."

#============================================================================

    def __init__(self, master, objs, current, hlen=70, **kw):
        "Create the parallel lists boxes, bare plus selection buttons."
        self.thanCargo = kw.pop("cargo", None)
        ThantkClistHierBare.__init__(self, master, **kw)
        ThanMixinPartial.__init__(self)
        self.thanCur = current
        print("cur1=", self.thanCur)

        self.thanCreateButtonsup(self, 0, 0)
        (nr, nc) = self.thanListsPlace(1, 0)
        self.thanListsFill(objs)
        self.thanMakePartial(hlen=hlen)
        self.thanLeaflayers = {}

#============================================================================

    def thanInsert2Lists(self, i, layers, prefix):
        """Inserts lays to the lists.

        This is exactly the same as the overridden function in class ThantkClistHierBare
        with the exception of braces at the values, if the values
        are inherited.
        """
        for lay in layers:
            i += 1
            self.thanListLayers.insert(i, lay)     # layer pointer

            for att in self.thanAtts:
                li = self.thanLists[att]
                if att == self.thanAttmain:
                    li.thanInsert(i, prefix+str(lay.thanAtts[att]))
                elif att == _EXPAND:
                    li.thanInsert(i, lay.thanAtts[att].thanVal)
                else:
                    t = str(lay.thanAtts[att])
                    if lay.thanAtts[att].thanInher: t = "["+t+"]"
                    li.thanInsert(i, t)

            if lay.thanAtts[_EXPAND].thanVal == "-":
                i = self.thanInsert2Lists(i, lay.thanChildren, prefix+"....")
        return i

#============================================================================

    def thanCreateButtonsup(self, master, ir, ic):
        "Creates utilities buttons."
        S = lambda x: x
        fraBut = Frame(master)
        fraBut.grid(row=ir, column=ic, columnspan=len(self.thanAtts), sticky="we")
        for i in (0,1,2,3): fraBut.columnconfigure(i, weight=1)

        but = thanwids.ThanButton(fraBut, text=T["Previous set"], bg="#ffffdc", command=S(self.thanSetPrev))
        but.grid(row=0, column=0, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Next set"], bg="#ffffdc", command=S(self.thanSetNext))
        but.grid(row=1, column=0, sticky="we")

        but = thanwids.ThanButton(fraBut, text=T["Select All"], bg="#ffdcdc", command=S(self.thanSelAll))
        but.grid(row=0, column=3, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Deselect All"], bg="#ffdcdc", command=S(self.thanSelNone))
        but.grid(row=1, column=3, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Invert selection"], bg="#ffdcdc", command=S(self.thanSelInvert))
        but.grid(row=2, column=3, sticky="we")

        but = thanwids.ThanButton(fraBut, text=T["New Top Layer"], bg="#dcffdc", command=S(self.thanLayerTopNew1))
        but.grid(row=0, column=1, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["New Child Layer"], bg="#dcffdc", command=S(self.thanLayerChildNew1))
        but.grid(row=1, column=1, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Rename Layer"], bg="#dcffdc", command=S(self.thanLayerRen1))
        but.grid(row=2, column=1, sticky="we")
#        but = thanwids.ThanButton(fraBut, text="Delete Layer", command=S(self.thanSelDelete))
#        but.grid(row=3, column=1, sticky="we")

        but = thanwids.ThanButton(fraBut, text=T["Copy"], bg="#dcdcff", command=S(self.thanSelCopy))
        but.grid(row=0, column=2, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Paste"], bg="#dcdcff", command=S(self.thanSelPaste))
        but.grid(row=1, column=2, sticky="we")
        but = thanwids.ThanButton(fraBut, text=T["Cut"], bg="#dcdcff", command=S(self.thanSelCut))
        but.grid(row=2, column=2, sticky="we")

        self.__cl = thanwids.ThanEntry(fraBut, bg="#ffdcff")
        self.__cl.thanSet(self.thanCur.thanGetPathname())
        self.__cl.grid(row=4, column=0, columnspan=3, sticky="we", pady=10)
        but = thanwids.ThanButton(fraBut, text=T["Set Current"], bg="#ffdcff", command=S(self.thanSetCur))
        but.grid(row=4, column=3, sticky="we", pady=10)

        return 1, 0

#============================================================================

    def thanLayerRen1(self, *args):
        "Renames the selected layer; updates current layer."
        lay = self.thanLayerRen()
        if lay == Canc: return
        if lay == self.thanCur:             # Rename current layer
            self.__cl.thanSet(self.thanCur.thanGetPathname())


    def thanLayerTopNew1(self, *args):
        "Creates a new top level layer."
        laypar = self.thanListLayers[0]
        name1 = laypar.thanChildUniqName()
        while True:
            name1 = xinp.xinpStrB(self, T["Create New Top Level Layer"], name1)
            if name1 is None: return Canc
            self.thanSel1(0)
            self.thanPollForce()      # Force selection now
            try:
                lay1 = self.thanLayerChildNewHouse(name1)
            except ThanLayerError as e:    # Check if name is valid
                thanGudModalMessage(self, str(e), T["Top Level Layer can not be created"])
            else:
                break


    def thanLayerChildNew1(self, *args):
        "Creates a new child layer."
        (indexes, lays) = self.thanSelGet()
        if len(lays) <= 0:
            i = 0
            laypar = self.thanListLayers[0]
        else:
            i = int(indexes[0])
            laypar = lays[0]
        name1 = laypar.thanChildUniqName()
        while True:
            name1 = xinp.xinpStrB(self, T["Create New '%s' Child Layer"]%laypar.thanGetPathname(), name1)
            if name1 is None: return Canc
            try:
                lay1 = self.thanLayerChildNewHouse(name1)
            except ThanLayerError as e:
                thanGudModalMessage(self, str(e), T["Child Layer can not be created"])
            else:
                break


    def thanSetCur(self, *args):
        indexes = self.thanLimain.curselection()
        lays = [self.thanListLayers[int(j)] for j in indexes]
        self.thanTryCur(lays)


    def thanTryCur(self, lays):
        "Try to set current layer one of the given layers (lays)."
        for lay in lays:
            if len(lay.thanChildren) == 0:     # Only leaflayers can be current
                self.thanCur = lay
                self.__cl.thanSet(self.thanCur.thanGetPathname())
                self.thanModified = True
                return True
        return False


    def destroy(self):
        "Break circular references."
        print("ThanTkClist destroy: cur2=", self.thanCur)
        del self.thanCur, self.__cl
        ThantkClistHierBare.destroy(self)
        ThanMixinHierUtil1.destroy(self)
        ThanMixinPartial.destroy(self)


if __name__ == "__main__":
    print(__doc__)
