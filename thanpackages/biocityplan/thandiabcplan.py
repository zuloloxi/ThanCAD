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
and options for bioclimatic city plan design.
"""

import sys, copy
import tkinter

import p_gtkwid, p_ggen
from thanvar import Canc, DEFCAN
from thantrans import Tarch, T, Twid, Tmatch
from thantkdia import ThanArchCom
from thancom.selutil import thanSelMultlines
import thanvers


class ThanBcplan(ThanArchCom):
    "Dialog for the bioclimatic city plan."

    def __init__(self, *args, **kw):
        "Set title and button labels."
        kw.setdefault("title", Tarch["Bioclimatic City Plan Design"])
        kw.setdefault("buttonlabels", (T["Execute"], Tarch["Preprocess"], T["Cancel"]))
        ThanArchCom.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()

        v.refPolygon = []
        v.refPrepro = None    #This will cause an error if values are not given by the caller
        v.labDTM = False
        v.doPrepro = False

        v.entMinWidth = 60.0
        v.entMaxWidth = 140.0
        v.entMinHeight = 50.0
        v.entMaxHeight = 60.0
        v.entMinRoad = 12.0
        v.entMaxRoad = 14.0
        v.choBio = True
        v.entMult = 1
        return v


    def body2(self, win):
        "Create the body of the dialog in steps."
#        self.fraLogo(win, 0, theme=Tarch["Bioclimatic City Plan Design Algorithms"], year="2010-2013")
        self.fraLogo2(win, 0, year="2010-"+thanvers.tcver.copyrightyear)
        self.fraDefine(win, 1)
        self.fraParams(win, 2)


    def fraParams(self, win, ir):
        "Select the room dimensions constraints."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tarch["CITY BLOCK PARAMETERS:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        keys = "entMinWidth", "entMaxWidth"
        tits = "Min width (m)", "Max width (m)"   #Tarch["Min width (m)"], Tarch["Max width (m)"]
        ir = 1
        lab = tkinter.Label(fra, fg=self.colfra, text=Tarch["City block width (east-west):"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")
        for key, tit in zip(keys, tits):  #works for python2,3
            ir += 1
            val = p_gtkwid.ThanValFloat(1.0, 1000.0)
            lab = tkinter.Label(fra, text=Tarch[tit])
            lab.grid(row=ir, column=1, sticky="e")
            wid = p_gtkwid.ThanEntry(fra, width=5)
            wid.grid(row=ir, column=2, sticky="we")
            self.thanWids.append((key, tit, wid, val))

        keys = "entMinHeight", "entMaxHeight"
        tits = "Min height (m)", "Max height (m)"   #Tarch["Min height (m)"], Tarch["Max height (m)"]
        ir = 1
        lab = tkinter.Label(fra, fg=self.colfra, text=Tarch["City block height (north-south) < width:"])
        lab.grid(row=ir, column=4, columnspan=2, sticky="e")
        for key, tit in zip(keys, tits):  #works for python2,3
            ir += 1
            val = p_gtkwid.ThanValFloat(1.0, 1000.0)
            lab = tkinter.Label(fra, text=Tarch[tit])
            lab.grid(row=ir, column=4, sticky="e")
            wid = p_gtkwid.ThanEntry(fra, width=5)
            wid.grid(row=ir, column=5, sticky="we")
            self.thanWids.append((key, tit, wid, val))


        keys = "entMinRoad", "entMaxRoad"
        tits = "Min width (m)", "Max width (m)"   #Tarch["Min width (m)"], Tarch["Max width (m)"]
        ir = 4
        lab = tkinter.Label(fra, fg=self.colfra, text=Tarch["Road width:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")
        for key, tit in zip(keys, tits):  #works for python2,3
            ir += 1
            val = p_gtkwid.ThanValFloat(1.0, 1000.0)
            lab = tkinter.Label(fra, text=Tarch[tit])
            lab.grid(row=ir, column=1, sticky="e")
            wid = p_gtkwid.ThanEntry(fra, width=5)
            wid.grid(row=ir, column=2, sticky="we")
            self.thanWids.append((key, tit, wid, val))

        ir = 5
        key = "choBio"
        tit = "Apply bioclimatic constraints?"   #Tarch["Apply bioclimatic constraints?"]
        val = p_gtkwid.ThanValidator()
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=ir, column=4, sticky="e")
        wid = p_gtkwid.ThanYesno(fra, width=5)
        wid.grid(row=ir, column=5, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        ir += 1
        key = "entMult"
        tit = "Multiple executions of the algorithm"   #Tarch["Multiple executions of the algorithm"]
        val = p_gtkwid.ThanValInt(1, 1000)
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=ir, column=4, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=ir, column=5, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        wid = tkinter.Frame(fra)
        wid.grid(row=2, column=3, sticky="we")

        fra.columnconfigure(3, weight=1)


    def fraDefine(self, win, ir):
        "Various city plan definititions."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tarch["CITY PLAN DEFINITION:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "refPolygon"
        tit = "Polygon enclosing\ncity plan defined?"    #Tarch["Polygon enclosing\ncity plan defined?"]
        val = _Val1()
        lab = tkinter.Label(fra, text=Tarch[tit], anchor="w")
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanRef(fra, text="", reference="", readonly=True, buttontext=Tarch["Define..."], width=3,
              command=self.__selref1, textcommand=self.__textref1)
        wid.grid(row=1, column=2, sticky="w", padx=5)
        self.thanWids.append((key, tit, wid, val))

        key = "refPrepro"
        tit = "Preprocessing done?"                      #Tarch["Preprocessing done?"]
        val = p_gtkwid.ThanValidator()
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanRef(fra, text="", reference="", readonly=True, buttontext=Tarch["Import from file..."], width=3,
              command=self.__rdcache, textcommand=self.__textcache)
        wid.grid(row=2, column=2, sticky="w", padx=5)
        self.thanWids.append((key, tit, wid, val))

#        key = "labPrepro"
#        tit = "Preprocessing done?"                      #Tarch["Preprocessing done?"]
#        val = p_gtkwid.ThanValidator()
#        lab = tkinter.Label(fra, text=Tarch[tit])
#        lab.grid(row=1, column=4, sticky="e")
#        wid = p_gtkwid.ThanLabyesno(fra, width=5)
#        wid.grid(row=1, column=5, sticky="we")
#        self.thanWids.append((key, tit, wid, val))

        key = "labDTM"
        tit = "DTM defined?"                             #Tarch["DTM defined?"]
        val = p_gtkwid.ThanValidator()
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=2, column=4, sticky="e")
        wid = p_gtkwid.ThanLabyesno(fra, width=5)
        wid.grid(row=2, column=5, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        wid = tkinter.Frame(fra)
        wid.grid(row=1, column=3, sticky="we")
        fra.columnconfigure(3, weight=1)


    def __selref1(self, ref):
        "Select the 1 line."
        proj = self.thanProj
        p_gtkwid.thanGrabRelease()
        self.withdraw()
        gps = thanSelMultlines(proj, 1, Tarch["Select polygon enclosing city plan\n"], strict=True)
        proj[2].thanGudResetSelColor()                   # Unmarks the selection
        proj[2].thanGudSetSelRestore()                   # Restores previous selection
        proj[2].thanUpdateLayerButton()                  # Show current layer again
        if gps == Canc:
            proj[2].thanPrter(DEFCAN)
            text = None
        else:
            gps = [list(c) for c in gps.pop().cp]
            text = self.__textref1(gps)
        self.deiconify()
        p_gtkwid.thanGrabSet(self)
        return gps, text


    def __textref1(self, ref):
        "Check if a polygon has been defined."
        if len(ref) > 3:
            self.refPolygon.config(bg="green")
            return Twid["Yes"]
        else:
            self.refPolygon.config(bg="red")
            return Twid["No"]


    def __rdcache(self, ref):
        "Try to read the cache from a previously saved file."
        from thancom.thancomfile import thanTxtopen
        proj = self.thanProj
#        hull = self.refPolygon.thanGet()
#        if len(hull) < 4:
#            why = Tarch["1 polygon enclosing the city plan must be selected"]
#            p_gtkwid.thanGudModalMessage(proj[2], "%s:\n%s" % (Tarch["Import failed"], why),
#                title=Tarch["Import failed"], icon = p_gtkwid.ERROR)
#            return None, None
#        if ref.dtm is None:
#            why = Tarch["Can't preprocess: No DTM has been defined!"]
#            p_gtkwid.thanGudModalMessage(proj[2], "%s:\n%s" % (Tarch["Import failed"], why),
#                title=Tarch["Import failed"], icon = p_gtkwid.ERROR)
#            return None, None

        fn, fr = thanTxtopen(proj, Tarch["Please select previous file with saved preprocessing results"], suf=".cache")
        if fr == Canc: return None, None
        refnew = ref.shallowClone()        #Shallow copy
#        refnew.hull = hull
        try:
            refnew.readGrid(fr)
        except Exception as why:
            p_gtkwid.thanGudModalMessage(proj[2], "%s:\n%s" % (Tarch["Import failed"], why),
                title=Tarch["Import failed"], icon= p_gtkwid.ERROR)
            return None, None
        self.refPolygon.thanSet(refnew.hull)       #Set the enclosing polygon that was read from cache
        return refnew, self.__textcache(refnew)


    def __textcache(self, ref):
        "Check if a RoadGrid instance has cache of roads."
        if ref.cache.roadenx is not None:
            self.refPrepro.config(bg="green")
            return Twid["Yes"]
        else:
            self.refPrepro.config(bg="red")
            return Twid["No"]


    def apply2(self, *args):
        "The user pressed preprocess."
        if not ThanArchCom.apply2(self, *args): return False
        if self.refPrepro.thanGet().roadenx is not None:
            ans = p_gtkwid.thanGudAskOkCancel(self,
                message=Tarch["Preprocessing may take several minutes to complete.\nOk to proceed with preprocessing?"],
                title=Tarch["Preprocessing is already done!"], default="cancel")
            if not ans: return False
        self.result.doPrepro = True
        self.okhousekeep()


class _Val1(p_gtkwid.ThanValidator):
    "Validate that there is exactly 1 polygons defined."

    def thanValidate(self, v):
        "Validate the value v and return the correct value."
        try:
            n = len(v)
        except:
            self.thanSetErr(2, "A polygon was expected.")
            return None
        if n > 3: return v
        self.thanSetErr(1, Tarch["1 polygon enclosing the city plan must be selected"])
        return None
