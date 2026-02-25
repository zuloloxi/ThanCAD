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

This module defines the base for the dialogs related to arhitectural algorithms.
"""

import tkinter
from p_gtkwid import thanicon
from thantrans import Tarch
import p_gtkwid
import thanvers


class ThanArchCom(p_gtkwid.ThanComDialog):
    "An object which provides for functionality common to Architecture algorithms."

    def thanValsDefArch(self, v):
        "Build default values."
        v.entWidth = 9.0
        v.entHeight = 7.0


    def thanValsReadArch(self):
        "Read architecture common values."
        self.thanValsReadSec(sec="FLOOR PLAN CONSTRAINTS", keys="entWidth entHeight")

    def thanValsWriteArch(self):
        "Write architecture common values."
        self.thanValsWriteSec(sec="FLOOR PLAN CONSTRAINTS", keys="entWidth entHeight")


    def fraLogo(self, win, ir, theme=Tarch["Automated Floor Plan Design Algorithms"], year=None):
        "Display the logo."
        if year is None: year = thanvers.tcver.copyrightyear
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")
        self.fo1 = tkinter.font.Font(family="Liberation Serif", weight="bold", size=18)

        lab = tkinter.Label(fra, image=thanicon.get("ntua3"))
        lab.grid(row=0, column=0, rowspan=3)

        wid = tkinter.Frame(fra)
        wid.grid(row=0, column=1, rowspan=3, sticky="we")

        lab = tkinter.Label(fra, text=theme, font=self.fo1, fg="blue")
        lab.grid(row=0, column=2, sticky="we")
        lab = tkinter.Label(fra, text=Tarch["Thanasis Stamos, Research/Teaching Personnel"], font=self.fo1, fg="blue",
              anchor="center", justify="center")
        lab.grid(row=1, column=2, sticky="w")
        lab = tkinter.Label(fra, text=Tarch["School of Civil Engineering, NTUA, "]+str(year), font=self.fo1, fg="blue")
        lab.grid(row=2, column=2, sticky="w")

        wid = tkinter.Frame(fra)
        wid.grid(row=0, column=3, rowspan=3, sticky="we")

        lab = tkinter.Label(fra, image=thanicon.get("than"))
        lab.grid(row=0, column=4, rowspan=3)
        fra.columnconfigure(1, weight=1)
        fra.columnconfigure(3, weight=1)


    def fraLogo2(self, win, ir, theme=None, year=None):
        "Display the logo."
        if year is None: year = thanvers.tcver.copyrightyear
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")
        self.fo1 = tkinter.font.Font(family="Liberation Serif", weight="bold", size=18)

        if theme is None:
            theme =  "\n".join((Tarch["INTERSCIENTIFIC PROGRAM"],
                                Tarch["OF GRADUATE STUDIES (DPMS) OF NTUA"],
                                Tarch["ENVIRONMENT AND DEVELOPMENT"],
                                Tarch["Applications of environmental design on the built space"]))
            theme =  "\n".join((Tarch["OPTARCH:"],
                                Tarch["Optimization Driven Architectural Design of Structures"],
                                Tarch["No 689983 H2020-MSCA-RISE-2015"],
                                Tarch["Automated floor plan design"]))
        frb = tkinter.Frame(fra)
        frb.grid(row=0, column=0)
        lab = tkinter.Label(frb, image=thanicon.get("ntua3"))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(frb, text=Tarch["A.A. Stamos"])
        lab.grid(row=1, column=0)
        lab = tkinter.Label(frb, text=str(year))
        lab.grid(row=2, column=0)

        wid = tkinter.Frame(fra)
        wid.grid(row=0, column=1, sticky="we")

        lab = tkinter.Label(fra, text=theme, font=self.fo1, fg="blue")
        lab.grid(row=0, column=1, sticky="we")


        fra.columnconfigure(1, weight=1)


    def fraGeom(self, win, ir):
        "Select the geometry of the floor plan."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tarch["FLOOR PLAN CONSTRAINTS:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "entWidth"
        tit = "Floor plan width (m)"                #Tarch["Floor plan width (m)"]
        val = p_gtkwid.ThanValFloat(0.10, 1000.0)
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=1, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        key = "entHeight"
        tit = "Floor plan height (m)"               #Tarch["Floor plan height (m)"]
        val = p_gtkwid.ThanValFloat(0.10, 1000.0)
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=2, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        wid = tkinter.Frame(fra)
        wid.grid(row=1, column=3, padx=30)

        key = "entMinRooms"
        tit = "Min number of rooms"                 #Tarch["Min number of rooms"]
        val = p_gtkwid.ThanValInt(1, 1000)
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=1, column=4, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=1, column=5, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        key = "entMaxRooms"
        tit = "Max number of rooms"                 #Tarch["Max number of rooms"]
        val = p_gtkwid.ThanValInt(1, 1000)
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=2, column=4, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=2, column=5, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        fra.columnconfigure(3, weight=1)
