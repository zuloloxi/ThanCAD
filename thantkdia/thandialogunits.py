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

With this dialog we defined units and how they are printed.
"""

import tkinter
import p_gtkwid, p_ggen
import thandefs
from thantrans import T


class ThanDialogUnits(p_gtkwid.ThanComDialog):
    "Dialog for converting and printing units."

    def thanValsDef(self):
        "Build default values."
        vs = thandefs.ThanUnits
        v = p_ggen.Struct()
        v.radDistunit = vs._dis2num["m"]    # Unit of distance measurements
        v.entDistdigs = 3                   # Number of digits to display for distance values
        v.radAnglunit = vs._ang2num["deg"]  # Unit of angular measurements
        v.entAngldigs = 4                   # Number of digits to display for angular values
        v.radAngldire = vs._dir2num[+1]     # Anti-clockwise angles are positive
        v.radAnglzero = vs._ori2num[3]      # Zero is at 0.0 radians angle from the x-axis in the anticlockwise direction
        return v


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraLength(win, 1)
        self.fraAngle(win, 2)
        self.fraOrient(win, 3)


    def fraLength(self, win, ir):
        "Widgets of EGSA87 transformation."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["LENGTH UNITS:"])
        lab.grid(row=0, column=1, columnspan=3, sticky="w")

        tit = "Length unit"                       #T["Length unit"]
        lab = tkinter.Label(fra, anchor="w", text=T[tit])
        lab.grid(row=1, column=1, sticky="e")
        key = "radDistunit"
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=2, sticky="we")
        wid = rad.add_button(text=T["meters (m)"])
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=T["feet (ft)"])
        wid.grid(row=1, column=0, sticky="w")
        val = p_gtkwid.ThanValInt(0, 1)
        self.thanWids.append((key, T[tit], rad, val))

        tit = "Decimal digits"                    #T["Decimal digits"]
        lab = tkinter.Label(fra, anchor="w", text=T[tit])
        lab.grid(row=2, column=1, sticky="e", pady=5)
        key = "entDistdigs"
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=2, column=2, sticky="we")
        val = p_gtkwid.ThanValInt(-1, 15)
        self.thanWids.append((key, T[tit], wid, val))

        fra.columnconfigure(1, weight=1)


    def fraAngle(self, win, ir):
        "Widgets of EGSA87 transformation."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["ANGLE UNITS:"])
        lab.grid(row=0, column=1, columnspan=3, sticky="w")

        tit = "Angle unit"                        #T["Angle unit"]
        lab = tkinter.Label(fra, anchor="w", text=T[tit])
        lab.grid(row=1, column=1, sticky="e")
        key = "radAnglunit"
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=2, sticky="we")
        wid = rad.add_button(text=T["degrees (deg)"])
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=T["radians (rad)"])
        wid.grid(row=1, column=0, sticky="w")
        wid = rad.add_button(text=T["gradians (grad)"])
        wid.grid(row=2, column=0, sticky="w")
        val = p_gtkwid.ThanValInt(0, 2)
        self.thanWids.append((key, T[tit], rad, val))

        tit = "Decimal digits"                    #T["Decimal digits"]
        lab = tkinter.Label(fra, anchor="w", text=T[tit])
        lab.grid(row=2, column=1, sticky="e", pady=5)
        key = "entAngldigs"
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=2, column=2, sticky="we")
        val = p_gtkwid.ThanValInt(-1, 15)
        self.thanWids.append((key, T[tit], wid, val))

        fra.columnconfigure(1, weight=1)


    def fraOrient(self, win, ir):
        "Widgets of EGSA87 transformation."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=1, column=1, rowspan=2, pady=5, sticky="nwe")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["ANGLE ORIENTATION:"])
        lab.grid(row=0, column=1, columnspan=3, sticky="w")

        tit = "Angle is zero at"                   #T["Angle is zero at"]
        lab = tkinter.Label(fra, anchor="w", text=T[tit])
        lab.grid(row=1, column=1, sticky="e")
        key = "radAnglzero"
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=2, sticky="we")
        wid = rad.add_button(text=T["at 3 o'clock"])
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=T["at 12 o' clock"])
        wid.grid(row=1, column=0, sticky="w")
        wid = rad.add_button(text=T["at 9 o' clock"])
        wid.grid(row=2, column=0, sticky="w")
        wid = rad.add_button(text=T["at 6 o' clock"])
        wid.grid(row=3, column=0, sticky="w")
        val = p_gtkwid.ThanValInt(0, 3)
        self.thanWids.append((key, T[tit], rad, val))

        tit = "Positive angle\ndirection"          #T["Positive angle\ndirection"]
        lab = tkinter.Label(fra, anchor="w", text=T[tit])
        lab.grid(row=2, column=1, sticky="e")
        key = "radAngldire"
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=2, column=2, sticky="we", pady=5)
        wid = rad.add_button(text=T["anti-clockwise"])
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=T["clockwise"])
        wid.grid(row=1, column=0, sticky="w")
        val = p_gtkwid.ThanValInt(0, 1)
        self.thanWids.append((key, T[tit], rad, val))

        fra.columnconfigure(1, weight=1)
