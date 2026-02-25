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

This module displays a dialog for the user to enter some text associated with a
ThanCad element.
"""

from tkinter import Frame, Button, Tk
from p_ggen import prg
import p_gtkwid
from thantrans import T


class ThanElemtext(p_gtkwid.ThanDialog):
    "Dialog for the text for association text and object."

    def __init__(self, master, vals=None, cargo=None, *args, **kw):
        "Extract initial parameters."
        self.thanValsInit = vals           # This is structure not a scalar
        self.thanProj = cargo
        self.__master = master
        kw.setdefault("title", T[u"ΣΗΜΕΙΩΣΕΙΣ - ΣΧΟΛΙΑ"])
#       kw.setdefault("buttonlabels", ("Save and Exit", "Cancel", "Save and Run"))
        p_gtkwid.ThanDialog.__init__(self, master, buttonlabels=3, *args, **kw)


    def __position(self):
        "Position self."
        w = self.__master
        w.update()
        x = w.winfo_rootx() + 20
        y = w.winfo_rooty() + 15
        self.geometry("%+d%+d" % (x, y))
        del self.__master


    def destroy(self):
        "Break circular references."
        del self.thanHelp, self.thanValsInit, self.thanProj, self.thanValsSaved
        p_gtkwid.ThanDialog.destroy(self)


    def __del__(self):
        "Say that it is deleted for debugging reasons."
        prg("ThanElemtext %s is deleted." % self)


    def body(self, win):
        fra = Frame(win)
        fra.grid(row=0, column=0, sticky="we")
        but = Button(fra, text="Do nothing", background="lightcyan", activebackground="cyan")
        but.grid(row=0, column=0, sticky="w")
        fra.columnconfigure(0, weight=1)

        self.thanHelp = p_gtkwid.ThanScrolledText(win, hbar=False, vbar=True, font=None,
            background="lightyellow", foreground="black", width=80, height=25)
        self.thanHelp.grid(row=1, column=0, sticky="wesn")
        self.thanSet(self.thanValsInit)
        win.columnconfigure(0, weight=1)
        win.rowconfigure(1, weight=1)
        self.thanValsSaved = self.thanValsInit[:]
        self.__position()
        self.unbind("<Return>")
        self.thanTkSetFocus()

    def thanTkSetFocus(self):
        "Sets focus to the command window."
        self.lift()
        self.focus_set()
        self.thanHelp.focus_sette()

    def thanSet(self, vals):
        self.thanHelp.thanSet(vals[1])


    def validate(self, strict=True):
        "Returns true if the value chosen by the user is valid."
        self.result = [None, self.thanHelp.thanGet()]
        return True


    def cancel(self, *args):
        "Ask before cancel."
        if not self.validate(strict=False):   # If anything is wrong, then it must have been changed
            print("cancel: not validated")
            a = p_gtkwid.thanGudAskOkCancel(self, T["Data modified, OK to cancel?"], T["Warning"])
            if not a: return        # Cancel was stopped
        elif self.result != self.thanValsSaved: # If anything is wrong, then it must have been changed
            print(self.thanValsSaved)
            print(self.result)
            a = p_gtkwid.thanGudAskOkCancel(self, T["Data modified, OK to cancel?"], T["Warning"])
            if not a: return        # Cancel was stopped
        p_gtkwid.ThanDialog.cancel(self, *args)


    def apply2(self, *args):
        "Save the data given and run the program."
        ret = p_gtkwid.ThanDialog.apply2(self)
        if not ret: return
        self.thanValsSaved = self.result


if __name__ == "__main__":
    root = Tk()
    win = ThanElemtext(root, [None, "Dimitra"], cargo=None)
    print(win.result)
