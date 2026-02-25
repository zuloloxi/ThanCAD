# -*- coding: iso-8859-7 -*-

##############################################################################
# ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2016 Thanasis Stamos, June 19, 2016
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers

This dialog asks for the line simplification parameters.
"""

import tkinter
import p_gtkwid, p_ggen
from thantrans import Tphot
#T = p_gtkwid.Translation(dict(__TRANSLATION__=("en", "EN", "en", "EN")))  ##############


class ThanSimplificationSettings(p_gtkwid.ThanComDialog):
    "Dialog for the line simlification algorithm."

    def __init__(self, *args, **kw):
        "Just set the title."
        proj = kw["cargo"]
        kw.setdefault("title", "%s - %s" % (proj[0].name, Tphot["Line simplification settings"]))
        p_gtkwid.ThanComDialog.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        s = p_ggen.Struct("Line simplification settings")
        s.entXYmean = 0.15
        s.entXY     = 0.20
        s.entZ      = 0.10
        s.choKeep   = True
        return s


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraTol(win, 1)
        self.fraLin(win, 2)


    def fraTol(self, win, ir):
        "Widgets for simplification settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["TOLERANCE SETTINGS:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        key = "entXYmean"
        tit = "Tolerance of mean xy error"
        lab = tkinter.Label(fra, text=Tphot[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=1, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, Tphot[tit], wid, val))

        key = "entXY"
        tit = "Tolerance of individual xy error"
        lab = tkinter.Label(fra, text=Tphot[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=2, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, Tphot[tit], wid, val))

        key = "entZ"
        tit = "Tolerance of individual z error"
        lab = tkinter.Label(fra, text=Tphot[tit])
        lab.grid(row=3, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=3, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, Tphot[tit], wid, val))
        fra.columnconfigure(2, weight=1)


    def fraLin(self, win, ir):
        "Widgets for simplification settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["SIMPLIFIED LINES:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        key = "choKeep"
        tit = "Keep original lines after simplification"
        lab = tkinter.Label(fra, text=Tphot[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanYesno(fra,width=5)
        wid.grid(row=1, column=2, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tphot[tit], wid, val))

        tit = "If the original lines are kept, the simplified lines should be put\n"\
              "into another layer (by changing the current layer)."
        lab = tkinter.Label(fra, text=Tphot[tit], anchor="w", justify=tkinter.LEFT)
        lab.grid(row=2, column=1, columnspan=2, sticky="w", pady=5)
        fra.columnconfigure(2, weight=1)


def test1():
    root = tkinter.Tk()
    proj = [ p_ggen.path("xxxx"), None, root]
    dia = ThanSimplificationSettings(root, cargo=proj)
#    root.mainloop()

if __name__ == "__main__": test1()
