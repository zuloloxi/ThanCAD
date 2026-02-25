# -*- coding: iso-8859-7 -*-

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

This dialog defines a photogrammeric model.
"""

import sys, copy
import tkinter
from tkinter.messagebox import ERROR
import p_gtkwid, p_ggen
from thanvar import thanfiles
import thandefs
from thanopt.thancadconf import thanUndefPrefix
from thantrans import Tphot
#T = p_gtkwid.Translation(dict(__TRANSLATION__=("en", "EN", "en", "EN")))  ##############


mm = p_gtkwid.thanGudModalMessage


class ThanModel(p_gtkwid.ThanComDialog):
    "Dialog for photogrammetric model definition."

    def __init__(self, *args, **kw):
        "Just set the title."
        kw.setdefault("title", Tphot["Photogrammetric Model Definition"])
        p_gtkwid.ThanComDialog.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()
        v.entName = "123"
        v.entDesc = "A photogrammetric model"
        v.filLeft = v.filRight = p_ggen.path(thanUndefPrefix)
        return v


    def body(self, win):
        "Just add custom initial directories."
        p_gtkwid.ThanComDialog.body(self, win)
        le = self.filLeft.thanGet()
        ri = self.filRight.thanGet()
        if le != thanUndefPrefix:
            fildir = le.parent
        elif le != thanUndefPrefix:
            fildir = ri.parent
        else:
            fildir = thanfiles.getFiledir()
        self.filLeft.config(initialdir=fildir)
        self.filRight.config(initialdir=fildir)


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraModel(win, 1)


    def fraModel(self, win, ir):
        "Widgets for model definition."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["MODEL DEFINITION:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        key = "entName"
        tit = "Model Name"                         #Tphot["Model Name"]
        lab = tkinter.Label(fra, text=Tphot[tit])
        lab.grid(row=1, column=1, sticky="w")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=1, column=2, sticky="we")
        val = p_gtkwid.ThanValBlank()
        self.thanWids.append((key, tit, wid, val))

        key = "entDesc"
        tit = "Model Description"                  #Tphot["Model Description"]
        lab = tkinter.Label(fra, text=Tphot[tit])
        lab.grid(row=2, column=1, sticky="w")
        wid = p_gtkwid.ThanText(fra, height=2, width=40)
        wid.grid(row=2, column=2, sticky="wesn")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, wid, val))

        for j, w in enumerate(("Left", "Right")):
            tit = w+" image file"                  #Tphot["Left image file"]    #Tphot["Right image file"]
            key = "fil"+w
            lab = tkinter.Label(fra, anchor="w", text=Tphot[tit])
            lab.grid(row=3+j, column=1, sticky="w")
            wid = p_gtkwid.ThanFile(fra, extension="*", mode="r",
                command=self.__validateraster, title=tit, width=20, relief=tkinter.RAISED)
            wid.grid(row=3+j, column=2, sticky="we")
            val = p_gtkwid.ThanValPIL()
            self.thanWids.append((key, tit, wid, val))

        fra.columnconfigure(2, weight=1)
        fra.rowconfigure(1, weight=1)


    def __validateraster(self, filnam):
        "Validate that the raster can be accessed and it is not degenerate."
        im, terr = thandefs.imageOpen(filnam)
        if terr != "":
            mm(self, "%s:\n\n%s" % (filnam, why), Tphot["Error while reading image"], ERROR)   # (Gu)i (d)ependent
            return False
        fildir = filnam.parent
        self.filLeft.config(initialdir=fildir)
        self.filRight.config(initialdir=fildir)
        return True


def test1():
    root = tkinter.Tk()
    dia = ThanModel(root)
#    root.mainloop()

if __name__ == "__main__": test1()
