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

This dialog asks for the point distance parameters.
"""

import tkinter
import p_gtkwid, p_ggen
from thantrans import Tphot
#Tphot = p_ggen.Translation(dict(__TRANSLATION__=("en", "EN", "en", "EN")))  ##############


class ThanPodisSettings(p_gtkwid.ThanComDialog):
    "Dialog for the point distance settings."

    def __init__(self, *args, **kw):
        "Just set the title."
        proj = kw["cargo"]
        kw.setdefault("title", "%s - %s" % (proj[0].name, Tphot["Point distance settings"]))
        super().__init__(*args, **kw)


    @staticmethod
    def thanValsDef():
        "Build default values."
        s = p_ggen.Struct("Point distance settings")
        s.radPoint  = 0
        #s.radSelect = 0
        s.chkPoint  = True
        s.chkLine   = False
        return s


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraTol(win, 1)


    def fraTol(self, win, ir):
        "Widgets for point distance settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["POINTS DISTANCE SETTINGS:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")
        fra.columnconfigure(2, weight=1)

        key = "radPoint"
        tit = "Point type"
        wid = p_gtkwid.ThanRadio(fra)
        wid.grid(row=1, column=1, columnspan=2, sticky="we")
        temp = tkinter.Label(wid, text="Point type:")
        temp.grid(row=0, column=0, sticky="w")
        temp = wid.add_button(text=Tphot["Simple point"])
        temp.grid(row=1, column=0, sticky="w")
        temp = wid.add_button(text=Tphot["Named point"])
        temp.grid(row=2, column=0, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tphot[tit], wid, val))

        #key = "radSelect"
        #tit = "Select point"
        #wid = p_gtkwid.ThanRadio(fra)
        #wid.grid(row=2, column=1, columnspan=2, sticky="we")
        #temp = tkinter.Label(wid, text="Which solutions to choose:")
        #temp.grid(row=0, column=0, sticky="w")
        #temp = wid.add_button(text=Tphot["User selects the solution"])
        #temp.grid(row=1, column=0, sticky="w")
        #temp = wid.add_button(text=Tphot["Both solutions are selected"])
        #temp.grid(row=2, column=0, sticky="w")
        #val = p_gtkwid.ThanValidator()
        #self.thanWids.append((key, Tphot[tit], wid, val))

        temp = tkinter.Label(fra, text="What to draw:")
        temp.grid(row=3, column=1, sticky="w")

        key = "chkPoint"
        tit = "Draw point"
        wid = p_gtkwid.ThanCheck(fra, text=Tphot["Draw point"]) #, anchor="w"))
        wid.grid(row=4, column=1, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tphot[tit], wid, val))

        key = "chkLine"
        tit = "Draw lines to points"
        wid = p_gtkwid.ThanCheck(fra, text=Tphot["Draw lines to point"]) #, anchor="w")
        wid.grid(row=5, column=1, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tphot[tit], wid, val))


def test1():
    root = tkinter.Tk()
    proj = [ p_ggen.path("xxxx"), None, root]
    dia = ThanPodisSettings(root, cargo=proj)
    #root.mainloop()

if __name__ == "__main__": test1()
