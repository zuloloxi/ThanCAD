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

This module displays a dialog for the user to print a drawing.
"""
import copy
from tkinter import Button, Label, SUNKEN, DISABLED, NORMAL
from p_gtkwid import (ThanDialog, thanGudModalMessage,
                      thanGrabRelease, thanGrabSet,
                      ThanChoice, ThanRadio, ThanFile, ThanValidator)
from thanvar import Canc, DEFCAN

from thandefs import thanplotcups
from thantrans import T


class ThanButtonCargo:
    "A button which saves the return value of the 'command' function."

    def __init__(self, master, cargo=None, command=None, **kw):
        "Trap the 'command' function."
        self.__command = command
        kw["command"] = self.__pressed
        self.__cargo = cargo
        self.__but = Button(master, **kw)

    def __pressed(self):
        "Run 'command' and save its result."
        if self.__command is None: return
        res = self.__command()
        if res == Canc: return Canc
        self.__cargo = res

    def thanSet(self, cargo):
        "Sets the saved value."
        self.__cargo = cargo

    def thanGet(self):
        "Returns the saved value."
        return self.__cargo

    def destroy(self):
        "Breaks circular references."
        del self.__command
        del self.__cargo
        self.__but.destroy()
        del self.__but

    def config(self, *args, **kw):
        "Config extra attributes and delegate others to button."
        if "cargo" in kw:
            self.__cargo = kw.pop["cargo"]
        if "command" in kw:
            self.__command = kw.pop["command"]
        self.__but.config(*args, **kw)

    def __getattr__(self, att):
        "Delegate all other attributes to button."
        return getattr(self.__but, att)


class ThanChoiceRev(ThanChoice):
    "A multiple choice widget; thanGet returns the text and not index."
    def thanSet(self, key): ThanChoice.thanSetText(self, key)
    def thanGet(self):      return ThanChoice.thanGetText(self)


class ThanDiaPlot(ThanDialog):
    "An object to provide basic plot capabilities."

    def __init__(self, master, ccups, printers, vals=None, cargo=None, *args, **kw):
        "Extract initial rectification parameters."
        self.thanValsInit = vals           # This is structure not a scalar
        self.ccups = ccups
        self.printers = printers
        self.names = sorted(self.printers.keys())  #works for python2,3
        self.thanProj = cargo
        kw.setdefault("title", T["Plot Drawing to Printer"])
        kw.setdefault("buttonlabels", (T["Save and Exit"],  T["Save and Print"], T["Cancel"]))
        ThanDialog.__init__(self, master, *args, **kw)


    def thanValsDef(self, new=None):
        "Build default values; set to new values if new are valid."
        if new is None: v = thanplotcups.ThanPlot()
        else: v = copy.deepcopy(new)
        v.thanRepair(self.thanProj)
        return v


    def body(self, win):
        "Create the widgets."
        self.thanWids = []
#        desc = [self.printers[nam]["printer-make-and-model"] for nam in self.names]
        key = "choPr"
        tit = "Printer selection"              #T["Printer selection"]
        val = ThanValidator()
        lab = Label(win, text=T[tit])
        lab.grid(row=0, column=0, sticky="e")
        wid = ThanChoiceRev(win, labels=self.names, width=40, command=self.__printeropt)
        wid.grid(row=0, column=1, columnspan=3, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        key = "radWhat"
        tit = "Plot definition"                #T["Plot definition"]
        val = ThanValidator()
        lab = Label(win, text=T[tit])
        lab.grid(row=1, column=0, rowspan=2, sticky="e")
        rad = ThanRadio(win, relief=SUNKEN, bd=1)
        rad.grid(row=1, column=1, rowspan=2, pady=10, sticky="w")
        wid = rad.add_button(text=T["Display"], command=self.__printeropt)
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=T["Window"], command=self.__printeropt)
        wid.grid(row=1, column=0, sticky="w")
        self.thanWids.append((key, tit, rad, val))

        key = "butPick"
        tit = "Pick Window"                    #T["Pick Window"]
        val = ThanValidator()
        self.q1 = wid = ThanButtonCargo(win, text=T[tit], bg="lightcyan",
            activebackground="cyan", command=self.__pick)
        wid.grid(row=1, column=3)
        self.thanWids.append((key, tit, wid, val))

        key = "filPlot"
        tit = "Plot File"                      #T["Plot File"]
        val = ThanValidator()
        lab = Label(win, text="    "+T[tit])
        lab.grid(row=2, column=2, sticky="e")
        wid = ThanFile(win, text="p.ps", extension=".ps", mode="w", initialdir=self.thanProj[0].parent,
              title=T["Plot File"], command=None)
        wid.grid(row=2, column=3, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        for i in range(3, 4):
            win.columnconfigure(i, weight=1)
        for (key,tit,wid,vld) in self.thanWids:
            setattr(self, key, wid)

        self.thanValsInit = self.thanValsDef(self.thanValsInit)   #Correct thanValsInit with default values
        self.thanValsSaved = copy.deepcopy(self.thanValsInit)
        self.thanSet(self.thanValsInit)


    def __printeropt(self, *args):
        "Show/hide printer options."
        if self.radWhat.thanGet() == 0:
            self.butPick.config(state=DISABLED)
        else:
            self.butPick.config(state=NORMAL)
#        if self.choPr.thanGetText() == self.TOFILE:
        if self.choPr.thanGet() == thanplotcups.TOFILE:
            self.filPlot.config(state=NORMAL)
        else:
            self.filPlot.config(state=DISABLED)


    def __pick(self):
        "Pick a window from user."
        thanGrabRelease()
        self.withdraw()
        win = self.thanProj[2]
        c1 = win.thanGudGetPoint(T["First window corner: "])
        if c1 != Canc:
            c2 = win.thanGudGetRect(c1, T["Other window corner: "])
        if c1 == Canc or c2 == Canc:             # Plot Window cancelled
            win.thanCom.thanAppend("%s\n" % DEFCAN, "can")
            res = Canc
        else:
            res = c1, c2
        self.deiconify()
        thanGrabSet(self)
        return res


    def thanSet(self, vs):
        "Set new values to the widgets."
        stat = NORMAL
        for (key,tit,wid,vld) in self.thanWids:
            v = getattr(vs, key)
#            if type(v) == float or type(v) == int: v = str(v)
            wid.config(state=stat) # All widgets must be enabled..
            wid.thanSet(v)         # ..to change their values
        self.__printeropt()        # Enable/disable printer options


    def validate(self, strict=True):
        """Returns true if the value chosen by the user is valid.

        If strict == True, then if an error is found, an error message is displayed,
        self.result is unchanged, and False is returned to the caller.
        If strict == True, and no errors are found, self.result is updated with
        the new values. True is returned to the caller.
        If strict == False, then if an error is found, a default value is used
        instead of the wrong one, self.results is set with the new values,
        and False is returned to the caller.
        If strict == False, and no errors are found, then, self.results is set
        with the new values, and True is returned to the caller.
        """
        ret = True
        vs = copy.deepcopy(self.thanValsSaved)
        for key,tit,wid,vld in self.thanWids:
            v1 = vld.thanValidate(wid.thanGet())
            if v1 is None:
                ret = False
                if strict:
                    tit = u'"%s":\n%s' % (tit, vld.thanGetErr())
                    thanGudModalMessage(self, tit, T["Error in data"])
                    self.initial_focus = wid
                    return ret
                else:
                    v1 = getattr(self.thanValsInit, key)
            setattr(vs, key, v1)
        self.result = vs, "save"
        return ret


    def apply2(self):
        "The user cliked OK and data has been validated; so print."
        if ThanDialog.apply2(self):
            self.ok()
            self.result = self.result[0], "apply"
            return True
        return False


    def cancel(self, *args):
        "Ask before cancel."
        ThanDialog.cancel(self, *args)


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
        for (key,tit,wid,vld) in self.thanWids:
            delattr(self, key)
        del self.thanProj, self.thanWids, self.thanValsInit, self.thanValsSaved
        ThanDialog.destroy(self, *args)


if __name__ == "__main__":
    print(__doc__)
