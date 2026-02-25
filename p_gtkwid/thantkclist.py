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

This module implements the generic compound list in Tkinter. It uses multiple
Tkinter lists.
"""


import types
from tkinter import Scrollbar, Frame, Label, EXTENDED, END, VERTICAL, HORIZONTAL
import p_ggen
from p_ggen import ThanLayerError, Canc
from .thantkutila import thanGudModalMessage
from .xinp import xinpStrB
from .thansched import ThanScheduler
from . import thanwids
from .thanwidstrans import T


_EXPAND="expand"


#############################################################################
#############################################################################

class ThantkClistBare(Frame, ThanScheduler):
    "Parallel Tk listboxes working as one; bare mechanism."

#============================================================================

    def __init__ (self, master, atts, attmain=None, labels=None, widths=None,
                  height=10, vscroll=0, hscroll=0, onclick=lambda *args: None,
                  selectmode=EXTENDED):
        "Create the parallel lists boxes, and their actions."
        Frame.__init__(self, master)
        ThanScheduler.__init__(self)

#-------Store arguments

        self.thanAtts = atts

        if attmain is None:
            if atts[0] == _EXPAND: attmain = atts[1]
            else:                  attmain = atts[0]
        self.thanAttmain = attmain

        if labels is None: labels=dict((k,p_ggen.thanUnicode(k)) for k in atts)
        self.thanLabels = labels
        if widths is None: widths = (20,)*len(atts)
        self.thanWidths = widths

        self.thanLabs = labels
        self.thanHeight = height
        self.thanVscroll = vscroll
        self.thanHscroll = hscroll
        self.thanOnclick = onclick
        self.thanSelectmode = selectmode

#-------Create widgets

        self.__thanListsCreate(self)

#-------Support for common selection in all lists

        self.thanLimain = self.thanLists[self.thanAttmain]
        self.__limaincur = None
        self.__limainpoll()

#-------Clipboard

        self.thanClipCom = None
        self.thanClipLays = []
        self.thanModified = False


    def destroy(self):
        "Break the circular references."
        del self.thanOnclick, self.thanLimain, self.__limaincur
        del self.thanLabs, self.thanLists, self.thanHsbars, self.thanVsbar
        del self.thanClipCom, self.thanClipLays
        Frame.destroy(self)

#============================================================================

    def thanListsPlace(self, ir, ic):
        "Places the widgets in the parent window."
        w = self.thanVsbar
        if w: w.grid(row=ir+1, column=ic+len(self.thanAtts), sticky="sn")

        i = 0
        for att in self.thanAtts:
            w = self.thanLabs[att]
            if w: w.grid(row=ir, column=ic+i, sticky="we")
            self.thanLists[att].grid(row=ir+1, column=ic+i, sticky="wesn")
            w = self.thanHsbars[att]
            if w: w.grid(row=ir+2, column=ic+i, sticky="we")
            i += 1
        for i in range(len(self.thanAtts)):
            self.columnconfigure(i, weight=self.thanWidths[i])
        self.rowconfigure(ir+1, weight=1)

#-------Return how many rows and columns were used

        nr = 2
        if self.thanHscroll: nr += 1
        nc = len(self.thanAtts)
        if self.thanVscroll: nc += 1
        self.thanLabRow = ir                            # Grid row of the labels
        self.thanLabCol = ic                            # Grid column of the labels
        return nr, nc

#============================================================================

    def thanListsDel(self, first, last=None):
        "Deletes data from lists."
        for li in self.thanLists.values():   #OK for python 2, 3
            if last is None: li.delete(first)
            else:            li.delete(first, last)


    def thanListsFill(self, objs):
        "Fills the lists with data."
        self.thanListLayers = objs
        for lay in objs:
            for att in self.thanAtts:
                self.thanLists[att].thanInsert(END, lay.thanAtts[att])

#============================================================================

    def __thanListsCreate(self, master):
        "Creates the lists."

#-------Create common scrollbar of lists

        sc = None
        if self.thanVscroll:
            sc = Scrollbar(master, orient=VERTICAL, command=self.__yview)
#           Change the color of inactive indicator to the color of active indicator
#           because it was confusing to change color when you pressed the button
            sc.config(background=sc["activebackground"])
        self.thanVsbar = sc

#-------process lists

        self.thanLabs = {}
        self.thanLists = {}
        self.thanHsbars = {}
        i = 0
        for att in self.thanAtts:

#-----------Create lists and labels

            lab = None
            if self.thanWidths[i] > 1:
                lab = Label(master, text=" %s" % (self.thanLabels[att],))

            li = thanwids.ThanListbox(master, selectmode=self.thanSelectmode,
                width=self.thanWidths[i],
                height=self.thanHeight, exportselection=0)

            if self.thanVscroll:
                li.config(yscrollcommand=self.__scrollset)

            sc = None
            if self.thanHscroll and self.thanWidths[i] > 1:           # attribute is only 1 character long
                sc = Scrollbar(master, orient=HORIZONTAL, command=li.xview)
#               Change the color of inactive indicator to the color of active indicator
#               because it was confusing to change color when you pressed the buuton
                sc.config(background=sc["activebackground"])
                li.config(xscrollcommand=sc.set)

#            li.bind("<Button-1>", lambda evt, att=att: self.__onListClick(evt, att))
            li.bind("<Button-1>", p_ggen.ThanStub(self.thanSchedule1, self.__onListClick, att))

            self.thanLists[att] = li
            self.thanHsbars[att] = sc
            self.thanLabs[att] = lab
            i += 1

#============================================================================

    def __yview(self, *args):
        "Scrolls all lists according to scrollbar."
        for li in self.thanLists.values():  #OK for python 2, 3
            li.yview(*args)

#============================================================================

    def __scrollset(self, *args):
        "Scrolls scrollbar and the other lists according to one list."
        self.thanVsbar.set(*args)
        for li in self.thanLists.values():   #OK for python 2, 3
            li.yview("moveto", args[0])

#============================================================================

    def __limainpoll(self):
        """Continuously propagates selections on main attribute to other attributes.

        It checks every second if user selected (clicked) the main attribute.
        If so, selects the same lines on the other attributes.
        It also checks if the user selected a nonmain attribute.
        If so, it corrects the selection of this attribute to be the same as the
        selection on the main attribute."""

        now = self.thanLimain.curselection()
        if now != self.__limaincur:
            lisel = self.thanLists.values()  #OK for python 2, 3
            self.__limaincur = now
        else:
            lisel = [ ]
            for li in self.thanLists.values():  #OK for python 2, 3
                if now != li.curselection: lisel.append(li)

        for li in lisel:
            if li != self.thanLimain: li.select_clear(0, END)
        for i in now:
            for li in lisel:
                if li != self.thanLimain: li.select_set(i)

        self.__id = self.after(250, self.__limainpoll)    # Reschedules itself for execution


    def thanPollForce(self):
        "Force selection polling."
        self.after_cancel(self.__id)                      # Cancel normal poll
        self.__limainpoll()                               # Force poll now

#============================================================================

    def thanSelGet(self):
        "Calls the user defined function with extended information."
        indexes = self.__limaincur[:]
        lays = [self.thanListLayers[int(j)] for j in indexes]
        return indexes, lays

#============================================================================

    def __onListClick(self, att, evt):
        "Calls the user defined function with extended information."
        self.update()
        self.after(250, self.__onListClick2, att, evt)

    def __onListClick2(self, att, evt):
        "Calls the user defined function with extended information."
        self.thanPollForce()                #So that the recentry cliked selection is active
        indexes = self.__limaincur[:]
        if len(indexes) < 1:                # No main selection. Select current list selection
            li = self.thanLists[att]
            indexes = li.curselection()
            if len(indexes) == 0:                              # No indexes; retry once
                if evt is None: return                         # second try; still no indexes
                self.after_cancel(self.__id)                   # Suspend ordinary mechanism
                self.after(100, self.__onListClick, att, None) # Reschedule itself for execution
                self.__id = self.after(250, self.__limainpoll) # Reschedule ordinary mechanism
                return
            for i in indexes: self.thanLimain.select_set(i)
        lays = [self.thanListLayers[int(j)] for j in indexes]
        self.thanOnclick(evt, self, att, indexes, lays)
        if att != self.thanAttmain: return "break"


#############################################################################
#############################################################################

class ThanMixinUtil:
    """Adds selection, copy/paste, and layer new/rename functionalities.

    This is for nonhierarchy parallel lists control."""

#============================================================================

    def thanSelAll(self):
        "Selects all the objects."
        self.thanLimain.select_set(0, END)

    def thanSelNone(self):
        "Deselects all the objects."
        self.thanLimain.select_clear(0, END)

    def thanSelInvert(self):
        "Inverses the selection of the objects."
        cur = self.thanLimain.curselection()
        self.thanLimain.select_set(0, END)
        for i in cur: self.thanLimain.select_clear(i)

    def thanSel1(self, i, i2=None):
        "Selects 1 or more objects."
        self.thanLimain.select_clear(0, END)
        if i2: self.thanLimain.select_set(i, i2)
        else:  self.thanLimain.select_set(i)

    def thanSelVar(self, indexes):
        "Selects various objects."
        for i in indexes: self.thanLimain.select_set(i)

#============================================================================

    def thanSelCopy(self):
        "Copies selection to the clipboard."
        indexes, lays = self.thanSelGet()
        if len(lays) > 0:                     # Something to copy
            self.thanClipLays = lays
            self.thanClipCom = "copy"

#============================================================================

    def thanSelPaste(self):
        "Moves selection to the clipboard; the actual move happens with paste."
        if not self.thanClipCom: return
        i0 = i = len(self.thanListLayers)

        for lay1 in self.thanClipLays:
            lay = lay1
            if self.thanClipCom != "move": lay = lay1.thanClone()
            name = lay.thanAtts[self.thanAttmain]
            if p_ggen.isString(lay.thanRenametest(name)):
                for j in range(1000000):
                    if p_ggen.isString(lay.thanRenametest(name+str(j))): break

            lay.thanParent = None
            self.thanListLayers.insert(i, lay)     # layer pointer
            for att in self.thanAtts: self.thanLists[att].thanInsert(i, lay.thanAtts[att])
            i += 1

        for li in self.thanLists.values(): li.see(END)  #OK for python 2, 3
        self.thanSel1(i0, END)
        self.thanModified = True

#============================================================================

    def thanLayerNew(self):
        "Makes a new layer."
        lay = self.thanListLayers[0]
        lay = lay.thanNew()

        i = len(self.thanListLayers)
        self.thanListLayers.insert(i, lay)     # layer pointer
        for att in self.thanAtts: self.thanLists[att].thanInsert(i, lay.thanAtts[att])

        for li in self.thanLists.values(): li.see(END)   #OK for python 2, 3
        self.thanSel1(i)
        self.thanModified = True

#============================================================================

    def thanLayerRen(self):
        "Renames a highlighted layer."
        (indexes, lays) = self.thanSelGet()
        i = 0
        if len(indexes) > 0: i = int(indexes[0])
        self.thanSel1(i)
        lay = self.thanListLayers[i]
        name = str(lay.thanAtts[self.thanAttmain])
        name1 = self.thanLimain.thanGetitem(i)

        for j in range(len(name1)):
            if name1[j] != ".": break
        else: assert None, "Layer name all dots!!"
        dots = ""
        if j > 0: dots = name1[:j]

        name1 = name
        while 1:
            name1 = xinpStrB(self, T["Rename Layer"]+" "+name, name1)
            if name1 is None: return Canc
            lay1 = lay.thanRenametest(name1)
            if not p_ggen.isString(lay1): break        # Check if name is valid
            thanGudModalMessage(self, lay1, T["Rename Failed"])
            return Canc

        self.thanLimain.delete(i)
        self.thanLimain.thanInsert(i, dots+name1)
        self.thanSel1(i)
        self.thanModified = True
        return lay

    def destroy(self):
        "Destroys the circlular reference of attrinutes."
        pass


#############################################################################
#############################################################################

class ThanMixinHierUtil(ThanMixinUtil):
    """Adds selection, copy/paste, and layer new/rename functionalities.

    This is for hierarchy parallel lists control."""

#============================================================================

    def thanLayerChildNew(self):
        "Makes a new child layer."
        try:
            lay = self.thanLayerChildNewHouse()   #May raise ThanLayerError
        except ThanLayerError as e:
            thanGudModalMessage(self, str(e), "New Child Layer Failed")
            return


    def thanLayerChildNewHouse(self, name=None):
        "Makes a new child layer without complaining to the user."
        (indexes, lays) = self.thanSelGet()
        if len(lays) <= 0:
            i = 0
            laypar = self.thanListLayers[0]
        else:
            i = int(indexes[0])
            laypar = lays[0]

        self.thanBranchCollapse(i)
        try:
            lay = laypar.thanChildNew(name)    #May raise ThanLayerError
        except ThanLayerError:
            self.thanBranchExpand(i)
            self.thanSel1(i)
            raise
        assert not p_ggen.isString(lay), "The previous statement here should have raised ThanLayerError, and never reach here!!"
        lay.thanAtts[_EXPAND].thanVal = " "

        laypar.thanAtts[_EXPAND].thanVal = "+"
        li = self.thanLiexpand
        li.delete(i); li.thanInsert(i, "+")

        self.thanBranchExpand(i)

        for j in range(i, len(self.thanListLayers)):
            if self.thanListLayers[j] == lay: break
        else:
            assert None, "Newly created child layer not found!"
        for li in self.thanLists.values(): li.see(j)   #OK for python 2, 3
        self.thanSel1(j)
        self.thanModified = True
        if self.thanCur == laypar:
            assert self.thanTryCur(laypar.thanChildren), "These should be leaf layers!"
        return lay

#============================================================================

    def thanSelCopy(self):
        "Copies selection to the clipboard."
        self.thanSelStore("copy")

#============================================================================

    def thanSelCut(self):
        "Copies selection to the clipboard."
        self.thanSelStore("move")
        self.thanSelDel(self.thanClipLays)
        self.thanSelNone()
        self.thanModified = True

#============================================================================

    def thanSelStore(self, com):
        "Moves selection to the clipboard; the actual move happens with paste."
        (indexes, lays) = self.thanSelGet()
        lays = [lay for lay in lays if lay != self.thanListLayers[0]] # Erases root layer from the selection

#-------Erases all the child layers from the selection

        todel = {}
        for lay in lays: todel[lay] = 0
        for lay in lays:
            par = lay.thanParent
            while par is not None:
                if par in todel: todel[lay] = 1; break
                par = par.thanParent

        if com == "move":
            self.thanClipLays = [lay for (lay, val) in todel.items() if val == 0]   #OK for python 2, 3
        else:
            self.thanClipLays = [lay.thanClone() for (lay, val) in todel.items() if val == 0]  #OK for python 2, 3

        self.thanClipCom = com

#============================================================================

    def thanSelPaste(self):
        "Pastes clipboard as toplevel layers or as children; copying or moving."
        print(self.thanClipCom)
        if not self.thanClipCom: return
        (indexes, lays) = self.thanSelGet()
        if len(lays) <= 0:
            i = 0
            laypar = self.thanListLayers[0]
        else:
            laypar = lays[0]
            i = int(indexes[0])
        self.thanBranchCollapse(i)

        try:
            laypar.thanChildAdd(self.thanClipLays)    #May raise ThanLayerError
        except ThanLayerError as e:
            thanGudModalMessage (self, str(er), T["Paste Failed"])
            return

        laypar.thanAtts[_EXPAND].thanVal = "+"
        li = self.thanLiexpand
        li.delete(i); li.thanInsert(i, "+")

        self.thanBranchExpand(i)
        self.thanSel1(i)

        self.thanClipCom = "copy"       # Move works only the first time
        self.thanClipLays = [lay.thanClone() for lay in self.thanClipLays]
        self.thanModified = True

#============================================================================

    def thanSelDel(self, lays):
        "Deletes selection if object permits it."
        for lay in lays:
            i = self.thanListLayers.index(lay)
            self.thanBranchCollapse(i)
            del self.thanListLayers[i]
            for li in self.thanLists.values(): li.delete(i)   #OK for python 2, 3
            par = lay.thanParent
            lay.thanUnlink()

#-----------If parent is childless, erase expand sign

            if par is None: continue
            if len(par.thanChildren) > 0: continue
            i = self.thanListLayers.index(par)
            li = self.thanLiexpand
            par.thanAtts[_EXPAND].thanVal = " "
            li.delete(i); li.thanInsert(i, " ")
        self.thanModified = True

    def destroy(self):
        "Destroys the circular reference of attributes."
        ThanMixinUtil.destroy(self)


#############################################################################
#############################################################################

class ThanMixinHierUtil1(ThanMixinHierUtil):
    "Cut selection is forced to be pasted to somewhere."

    def thanSelCopy(self):
        "Copies selection to the clipboard."
        if self.thanClipMovePending(): return
        ThanMixinHierUtil.thanSelCopy(self)

    def thanClipMovePending(self):
        "Checks if values in clipboard must be pasted."
        if self.thanClipCom != "move": return 0
        if len(self.thanClipLays) == 0: return 0  # No need to paste zero layers
        thanGudModalMessage(self, T["Clipboard contains nonempty layers."
            "Please paste them to the layer hierarchy."],
            T["Paste of layers pending"])
        return 1

    def thanSelCut(self):
        "Copies selection to the clipboard."
        if self.thanClipMovePending(): return
        ThanMixinHierUtil.thanSelCut(self)
        self.thanModified = True

    def destroy(self):
        "Destroys the circular reference of attributes."
        ThanMixinHierUtil.destroy(self)


#############################################################################
#############################################################################

class ThantkClistHierBare(ThantkClistBare):
    "Mixin for hierarchical values."

    def __init__(self, *args, **kw):
        "Initialise base class."
        ThantkClistBare.__init__(self, *args, **kw)

    def thanListsFill(self, root):
        "Fills the lists with data."
        assert len(root) == 1, "Only the root must be given."
        self.thanLiexpand = self.thanLists[_EXPAND]
        self.thanListLayers = [ ]                       # List entry layer pointers
        self.__initExpand(root)                         # Initialise expand attribute
        self.thanInsert2Lists(-1, root, "")             # Fill expand list
        self.thanLiexpand.bind("<Button-1>", p_ggen.ThanStub(self.thanSchedule1, self.__onclickExpand))

#============================================================================

    def thanRegen(self):
        "Deletes all the list entries and repaints them."
        print("ThanTkClist: ThanRegen triggered")
        root = [self.thanListLayers[0]]
        self.thanListLayers = []                        # List entry layer pointers
        for att in self.thanAtts:
            li = self.thanLists[att]
            li.delete(0, END)
        self.thanInsert2Lists(-1, root, "")             # Fill expand list

#============================================================================

    def __onclickExpand (self, evt):
        "Expand or collapse branches."
        li = self.thanLiexpand
        i = int(li.nearest(evt.y))
        sign = self.thanListLayers[i].thanAtts[_EXPAND].thanVal
#        sign = li.thanGetitem(i)

        if sign == "+":
            self.thanBranchExpand(i)
        elif sign == "-":
            self.thanBranchCollapse(i)

        return "break"

#============================================================================

    def thanBranchExpand (self, i):
        "Expand or collapse branches."
        li = self.thanLiexpand
        lay = self.thanListLayers[i]
        sign = lay.thanAtts[_EXPAND].thanVal
#        sign = li.thanGetitem(i)
        if sign == "+":
            self.thanSelNone()
            sign = "-"
            lay.thanAtts[_EXPAND].thanVal = sign
            li.delete(i)
            li.thanInsert(i, sign)

            m = self.thanLimain.thanGetitem(i)
            for j in range(len(m)):
                if m[j] != ".": break
            prefix = m[0:j]
            i = self.thanInsert2Lists(i, lay.thanChildren, prefix+"....")

#============================================================================

    def thanBranchCollapse (self, i):
        "Collapse branches."
        li = self.thanLiexpand
        lay = self.thanListLayers[i]
        sign = lay.thanAtts[_EXPAND].thanVal
#        sign = li.thanGetitem(i)
        if sign == "-":
            self.thanSelNone()
            sign = "+"
            lay.thanAtts[_EXPAND].thanVal = sign
            li.delete(i)
            li.thanInsert(i, sign)

            self.__delete2Lists(i, lay.thanChildren)

#============================================================================

    def __initExpand(self, layers):
        "Initialise expand attributes."
        for lay in layers:
            if len(lay.thanChildren) == 0:
                e = " "
            else:
                e = lay.thanAtts[_EXPAND].thanVal
                if e != "-": e = "+"
            lay.thanAtts[_EXPAND].thanVal = e

            if e != " ": self.__initExpand(lay.thanChildren)

#============================================================================

    def thanInsert2Lists(self, i, layers, prefix):
        "Inserts lays to the lists."
        for lay in layers:
            i += 1
            self.thanListLayers.insert(i, lay)     # layer pointer

            for att in self.thanAtts:
                li = self.thanLists[att]
                if att == self.thanAttmain:
                    li.thanInsert(i, prefix+lay.thanAtts[att])
                else:
                    li.thanInsert(i, lay.thanAtts[att])

            if lay.thanAtts[_EXPAND].thanVal == "-":
                i = self.thanInsert2Lists(i, lay.thanChildren, prefix+"....")
        return i

#============================================================================

    def __delete2Lists(self, i, layers):
        "Inserts lays to the lists."
        j = i + 1
        for lay in layers:
            del self.thanListLayers[j]           # layer pointer
            for att in self.thanAtts:
                li = self.thanLists[att]
                li.delete(j)

            if lay.thanAtts[_EXPAND].thanVal == "-":
                self.__delete2Lists(i, lay.thanChildren)

    def destroy(self):
        "Destroy circular reference of attributes."
        del self.thanLiexpand, self.thanListLayers
        ThantkClistBare.destroy(self)

#############################################################################
#############################################################################

class ThanMixinPartial:
    "Make only part of the parallel lists visible."

#============================================================================

    def __init__(self):
        "Not needed."
        pass

#============================================================================

    def thanMakePartial(self, sets=None, vlistl=2, hlen=50):
        """Arrange that only sets of lists are visible at a time.

        vlistl: Number of lists to keep always visible, from the left
        hlen  : Number of characters that can be visible on a row
        """
        self.thanVlistl = vlistl
        if sets is None:
            self.thanSetsFind(vlistl, hlen)                   # Find sets of lists
        else:
            self.thanSetsList = sets                          # Sets of lists are given
        atts = list(self.thanAtts)
        for i in range(vlistl): del atts[0]
        self.thanHideLists(atts)                              # Hide all lists
        self.thanSetI = 0
        self.thanShowLists(self.thanSetsList[self.thanSetI])  # Show first set of lists

#============================================================================

    def thanHideLists(self, setList):
        "Hides a set of lists."
        for att in setList:
            if self.thanLabs[att]: self.thanLabs[att].grid_forget()
            self.thanLists[att].grid_forget()
            if self.thanHsbars[att]: self.thanHsbars[att].grid_forget()

#============================================================================

    def thanShowLists(self, setList):
        "Shows a set of lists."
        ir = self.thanLabRow
        ic = self.thanLabCol + self.thanVlistl

        for att in setList:
            if self.thanLabs[att]: self.thanLabs[att].grid(row=ir, column=ic, sticky="w")
            self.thanLists[att].grid(row=ir+1, column=ic, sticky="wesn")
            if self.thanHsbars[att]: self.thanHsbars[att].grid(row=ir+2, column=ic, sticky="we")
            ic += 1

    def thanSetNext(self):
        "Displays next set of lists."
        if self.thanSetI >= len(self.thanSetsList)-1: return
        self.thanHideLists(self.thanSetsList[self.thanSetI])
        self.thanSetI += 1
        self.thanShowLists(self.thanSetsList[self.thanSetI])

    def thanSetPrev(self):
        "Displays previous set of lists."
        if self.thanSetI <= 0: return
        self.thanHideLists(self.thanSetsList[self.thanSetI])
        self.thanSetI -= 1
        self.thanShowLists(self.thanSetsList[self.thanSetI])

    def thanSetsFind(self, vlistl, hlen):
        "Finds sets of lists that can be shown simultaneously."
        #hl = hl1 = reduce(lambda s, x: x+s, self.thanWidths[:vlistl])
        hl = hl1 = sum(self.thanWidths[:vlistl])
        self.thanSetsList = [ ]
        setList = [ ]
        for i in range(self.thanVlistl, len(self.thanLists)):
            if hl > hlen:
                self.thanSetsList.append(setList)
                setList = [ ]
                hl = hl1
            hl += self.thanWidths[i]
            setList.append(self.thanAtts[i])

        if len(setList) > 0: self.thanSetsList.append(setList)

    def destroy(self):
        "Destroys the circlular reference of attrinutes."
        pass


if __name__ == "__main__":
    print(__doc__)
