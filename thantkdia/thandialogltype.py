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

This package includes dialogs (forms to get user input) implemented with tkinter.
This module contains the dialog which asks for line type settings.
"""

import tkinter
import p_gtkwid, p_ggen
from thantrans import T
from thanvar import THANBYPARENT, THANPERSONAL
import thantk


class ThanDialogLtype(p_gtkwid.ThanComDialog):
    "Dialog for line type settings."

    def __init__(self, *args, **kw):
        "Just set the title."
        self.idialog = kw.pop("idialog", 0)    #line type settings=0, dimension style settings=1
        if self.idialog == 0: tit = T["Line type settings"]
        else:                tit = T["Dimension style settings"]
        proj = kw["cargo"]
        kw.setdefault("title", "%s - %s" % (proj[0].name, tit))
        super().__init__(*args, **kw)


    def thanValsDef(self):
        "Build default values."
        if self.uidialog == 0:
            s = p_ggen.Struct("Line type settings")
            s.butPattern = "continuous"
        else:
            s = p_ggen.Struct("Dimension style settings")
            s.butPattern = "standard"
        s.choUnit  = 0
        s.entScale = 1.0
        return s


    def body(self, win):
        "Master body."
        p_gtkwid.ThanComDialog.body(self, win)
        self.__enable()


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraSpec(win, 1)
        if self.idialog == 0: temp = self.thanProj[1].thanLtypes
        else:                 temp = self.thanProj[1].thanDimstyles
        labs = sorted((val.thanName, val.thanDesc) for val in temp.values())   #works for python2,3
        labs.insert(0, (str(THANBYPARENT), str(THANBYPARENT)))
        labs.insert(1, (str(THANPERSONAL), str(THANPERSONAL)))
        n = max(len(b[0]) for b in labs)
        if n > 30: n = 30
        f = "%%-%ds %%s" % (n, )
        self.__labs1 = []
        self.__labs2 = []
        for b in labs:
            a1 = b[0]
            a2 = b[1]
            i = a2.lower().find(a1.lower())
            if i >= 0:   #If the name of the linetype is found in the description, delete it
                a2 = a2[:i].strip() + a2[i+len(a1):]
                a2 = a2.strip()
            a2 = f % (a1, a2)           #Add the name to the description
            self.__labs1.append(a1)
            self.__labs2.append(a2)


    def fraSpec(self, win, ir):
        "Widgets for line type settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")

#        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
#        lab.grid(row=0, column=0)
#        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["LINE TYPE SETTINGS:"])
#        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        key = "butPattern"
        if self.idialog == 0: tit = "Line type (dashes)"
        else:                 tit = "Dimension style"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanButton(fra, width=30, command=self.__poppattern, anchor="w", justify=tkinter.LEFT)
        wid.grid(row=1, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))

        key = "choUnit"
        if self.idialog == 0: tit = "Line type unit"
        else:                 tit = "Dimension style unit"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanChoice(fra, labels=("mm", "user data units"), width=20)
        wid.grid(row=2, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))

        key = "entScale"
        if self.idialog == 0: tit = "Line type scale"
        else:                 tit = "Dimension style scale"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=3, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=8)
        wid.grid(row=3, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, T[tit], wid, val))
        fra.columnconfigure(2, weight=1)


    def __poppattern(self):
        "Show a popup list with the line type patterns."
        namlt = self.butPattern.thanGet()
        try:
            i = self.__labs1.index(namlt)
        except IndexError:
            if self.idialog == 0: i = self.__labs1.index("continuous")
            else:                 i = self.__labs1.index("standard")

#        self.option_add("*%s*font" % (self.winfo_name(),), thantk.thanFonts[0])
        win = p_gtkwid.ThanPoplist(self, self.__labs2, width=100, height=20, selectmode=tkinter.SINGLE,
            default=i, font=thantk.thanFonts[0])
        r = win.result
        if r is not None:
            i = win.result1
            self.butPattern.thanSet(self.__labs1[i])
        self.__enable()


    def __enable(self):
        "If byparent, disable unit and scale."
        pa = self.butPattern.thanGet()
        if pa == str(THANBYPARENT) or pa == str(THANPERSONAL):
            self.choUnit.config(state=tkinter.DISABLED)
            self.entScale.config(state=tkinter.DISABLED)
        else:
            self.choUnit.config(state=tkinter.NORMAL)
            self.entScale.config(state=tkinter.NORMAL)


def test1():
    root = tkinter.Tk()
    proj = [ p_ggen.path("xxxx"), p_ggen.Struct(), root]
    proj[1].thanLtypes = {"<BYPARENT>":"pp", "continuous":"x", "dashed":"xx", "dot":"d1"}
    dia = ThanDialogLtype(root, cargo=proj)
#    root.mainloop()

if __name__ == "__main__": test1()
