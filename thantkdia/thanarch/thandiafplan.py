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

This module displays a dialog for the user to define the necessary elements
and options for automated floor plan architectural design.
"""

import sys, copy
import tkinter
import p_gtkwid, p_ggen, p_gvers
from thantrans import Tarch, T
from .thandiaarch import ThanArchCom
import thanvers


class ThanFplan(ThanArchCom):
    "Dialog for the pen thickness which the elements of a layer are plotted with."

    def __init__(self, *args, **kw):
        "Set title and button labels."
        kw.setdefault("title", Tarch["Automated Floor Plan Design"])
        kw.setdefault("buttonlabels", (T["Execute"], T["Cancel"]))
        ThanArchCom.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()
        self.thanValsDefArch(v)   # Common Architectural parameters
        v.entMinRooms = 5
        v.entMaxRooms = 6

        v.entMintolWidth = 2.5
        v.entMinWidth = 3.0
        v.entMaxWidth = 6.0
        v.entMaxtolWidth = 7.0
        v.entMintolHeight = 3.0
        v.entMinHeight = 3.0
        v.entMaxHeight = 7.0
        v.entMaxtolHeight = 8.0

        v.entPenaltmore = 1.0
        v.entPenalt1 = 10.0
        v.entPenalty = 1.0
        return v


    def thanValsRead(self, v):
        "Read widget values from a file."
        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".fpl")
        self.thanValsReadFile1(v, fn)

    def thanValsReadFile2(self):
        "This does the actual reading from configparser."
        self.thanValsReadArch()   # Common Architecture parameters
        self.thanValsReadSec(sec="FLOOR PLAN CONSTRAINTS", keys="entMinRooms entMaxRooms")
        self.thanValsReadSec(sec="ROOM CONSTRAINTS",
           keys="entMintolWidth entMinWidth entMaxWidth entMaxtolWidth "\
                "entMintolHeight entMinHeight entMaxHeight entMaxtolHeight")
        self.thanValsReadSec(sec="PENALTIES", keys="entPenaltmore entPenalt1 entPenalty")

    def thanValsWrite(self, v):
        "Write widget values to a file."
        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".fpl")
        self.thanValsWriteFile1(v, fn)

    def thanValsWriteFile2(self):
        "This does the actual reading from configparser."
        self.thanValsWriteArch()   # Common Architecture parameters
        self.thanValsWriteSec(sec="FLOOR PLAN CONSTRAINTS", keys="entMinRooms entMaxRooms")
        self.thanValsWriteSec(sec="ROOM CONSTRAINTS",
           keys="entMintolWidth entMinWidth entMaxWidth entMaxtolWidth "\
                "entMintolHeight entMinHeight entMaxHeight entMaxtolHeight")
        self.thanValsWriteSec(sec="PENALTIES", keys="entPenaltmore entPenalt1 entPenalty")


    def body2(self, win):
        "Create the body of the dialog in steps."
#        self.fraLogo(win, 0, theme=Tarch["Automated Floor Plan Design Algorithms"], year=2013)
        #self.fraLogo2(win, 0, year="2010-"+thanvers.tcver.copyrightyear)
        self.fraLogo2(win, 0, year="2016-"+thanvers.tcver.copyrightyear)
        self.fraGeom(win, 1)
        self.fraConstraints(win, 2)
        self.fraPenalties(win, 3)


    def fraConstraints(self, win, ir):
        "Select the room dimensions constraints."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tarch["ROOM CONSTRAINTS:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        keys = "entMintolWidth",            "entMinWidth",               "entMaxWidth",                "entMaxtolWidth"
        tits = "Min room length - hard (m)", "Min room length - soft (m)", "Max room length - soft (m)",  "Max room length - hard (m)"
            #Tarch["Min room length - hard (m)"], Tarch["Min room length - soft (m)"], Tarch["Max room length - soft (m)"], Tarch["Max room length - hard (m)"]
        ir = 1
        for key, tit in zip(keys, tits):  #works for python2,3
            val = p_gtkwid.ThanValFloat(0.10, 1000.0)
            lab = tkinter.Label(fra, text=Tarch[tit])
            lab.grid(row=ir, column=1, sticky="e")
            wid = p_gtkwid.ThanEntry(fra, width=5)
            wid.grid(row=ir, column=2, sticky="we")
            self.thanWids.append((key, tit, wid, val))
            ir += 1

        keys = "entMintolHeight",           "entMinHeight",              "entMaxHeight",               "entMaxtolHeight"
        tits = "Min room width - hard (m)", "Min room width - soft (m)", "Max room width - soft (m)",  "Max room width - hard (m)"
            #Tarch["Min room width - hard (m)"], Tarch["Min room width - soft (m)"], Tarch["Max room width - soft (m)"], Tarch["Max room width - hard (m)"]
        ir = 1
        for key, tit in zip(keys, tits):  #works for python2,3
            val = p_gtkwid.ThanValFloat(0.10, 1000.0)
            lab = tkinter.Label(fra, text=Tarch[tit])
            lab.grid(row=ir, column=4, sticky="e")
            wid = p_gtkwid.ThanEntry(fra, width=5)
            wid.grid(row=ir, column=5, sticky="we")
            self.thanWids.append((key, tit, wid, val))
            ir += 1

        wid = tkinter.Frame(fra)
        wid.grid(row=2, column=3, sticky="we")

        fra.columnconfigure(3, weight=1)


    def fraPenalties(self, win, ir):
        "Select the room and roomconfiguration penalties."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tarch["PENALTY (ADVANCED):"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        keys = "entPenaltmore", "entPenalt1", "entPenalty"
        tits = ("Number of rooms less(more) than min(max) (penalty/room)",  #Tarch["Number of rooms less(more) than min(max) (penalty/room)"]
                "Room dimension less(more) than hard min(max) (penalty/m)", #Tarch["Room dimension less(more) than hard min(max) (penalty/m)"]
                "Room dimension between soft and hard min(max) (penalty/m)" #Tarch["Room dimension between soft and hard min(max) (penalty/m)"]
               )
        expls = "(absolute)", "(normalised)", "(normalised)"                #Tarch["(absolute)"], Tarch["(normalised)"]
        ir = 1
        for key, tit, expl in zip(keys, tits, expls):  #works for python2,3
            val = p_gtkwid.ThanValFloat(0.10, 1000.0)
            lab = tkinter.Label(fra, text=Tarch[tit])
            lab.grid(row=ir, column=1, sticky="e")
            wid = p_gtkwid.ThanEntry(fra, width=5)
            wid.grid(row=ir, column=2, sticky="we")
            lab = tkinter.Label(fra, text=Tarch[expl])
            lab.grid(row=ir, column=3, sticky="w")
            self.thanWids.append((key, tit, wid, val))
            ir += 1

        wid = tkinter.Frame(fra)
        wid.grid(row=2, column=4, sticky="we")

        fra.columnconfigure(4, weight=1)


    def validate(self, strict=True, wids=None, values=None):
        "Returns true if the value chosen by the user is valid."
        ret, vs = self.validate2(strict, wids, values)
        if not ret and strict: return ret

        if vs.entMaxRooms < vs.entMinRooms:
            ret = False
            if strict:
                p_gtkwid.thanGudModalMessage(self, Tarch["Number of rooms: max < min !"], T["Error in data"])
                return ret

        self.result = vs
        return ret
