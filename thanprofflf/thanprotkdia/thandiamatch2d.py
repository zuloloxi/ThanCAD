# -*- coding: iso-8859-7 -*-

##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

Curve Matching Algorithms, Dimitra Vassilaki, PhD Candidate
Lab of Photogrammetry, NTUA, 2008-2013
This module displays a dialog for the user to define the necessary elements
and options for 2d curves global matching.
"""

import sys, copy, ConfigParser, Tkinter

import p_gtkuti, p_gtkwid, p_ggen
from thantrans import Tmatch, T
from thandiaicp import ThanICPcom


class ThanMatch2d(ThanICPcom):
    "Dialog for the pen thickness which the elements of a layer are plotted with."

    def __init__(self, master, vals=None, cargo=None, *args, **kw):
        "Extract initial rectification parameters."
        self.thanValsInit = vals           # This is structure not a scalar
        self.thanProj = cargo
        self.thanGps = []
        self.thanRel = []
        kw.setdefault("title", Tmatch["Global Matching of 2D Curves"])
        kw.setdefault("buttonlabels", (T["Execute"], T["Cancel"]))
        ThanICPcom.__init__(self, master, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()
        self.thanValsDefICP(v)   # Common ICP parameters
        v.radAlign = 0
        v.radAzim = 0
        v.gps = []
        v.rel = []
        return v


    def thanValsRead(self, v):
        "Reads the values from a file with specific suffix."
        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".m2d")
        if not fn.exists(): return
        c = ConfigParser.SafeConfigParser()
        c.read(fn)
        tv = {}
        for (key,tit,wid,vld) in self.thanWids: tv[key] = tit, vld

        self.thanValsReadICP(c, tv, v)   # Common ICP parameters

        sec = "PREALIGNMENT"
        try:
            test = int(c.get(sec, "type"))
            if 0 <= test <= 2: v.radAlign = test
        except:
            pass

        sec = "AZIMOUTH APPROXIMATION"
        try:
            test = int(c.get(sec, "type"))
            if 0 <= test <= 5: v.radAzim = test
        except:
            pass


    def thanValsWrite(self, v):
        "Write the values to a file with specific suffix."
        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".m2d")
        c = ConfigParser.SafeConfigParser()
        if fn.exists(): c.read(fn)
        tv = {}
        for (key,tit,wid,vld) in self.thanWids: tv[key] = tit, vld

        self.thanValsWriteICP(c, tv, v)   # Common ICP parameters

        sec = "PREALIGNMENT"
        if not c.has_section(sec): c.add_section(sec)
        c.set(sec, "type", str(v.radAlign))

        sec = "AZIMOUTH APPROXIMATION"
        if not c.has_section(sec): c.add_section(sec)
        c.set(sec, "type", str(v.radAzim))

        try: c.write(fn.open("w"))
        except: pass


    def body(self, win):
        self.thanWids = []
        self.colfra = "blue"
#        self.option_add("*font", _fo)
        self.fraLogo(win, 0, theme=Tmatch["Curve Matching Algorithms"], year="2008-2013")
        self.fraICP(win, 1)
        self.fraSel(win, 2, Tmatch["Select the\nreference line"], Tmatch["Select the line to be moved\ntowards the reference line"], "2d")
        self.fraApprox(win, 3)
        self.fraAzimouth(win, 4)
        win.columnconfigure(0, weight=1)
        for (key,tit,wid,vld) in self.thanWids:
            setattr(self, key, wid)

        if self.thanValsInit == None:
            self.thanValsInit = self.thanValsDef()
            self.thanValsRead(self.thanValsInit)
        self.thanValsSaved = copy.deepcopy(self.thanValsInit)
        self.thanSet(self.thanValsInit)


    def fraApprox(self, win, ir):
        "Select prealignment method."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["PREALIGNMENT:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "radAlign"
        tit = "PREALIGNMENT"                          #Tmatch["PREALIGNMENT"]
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=1, sticky="wesn")
        wid = rad.add_button(text=Tmatch["Centroid method"])
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=Tmatch["Distance method"])
        wid.grid(row=1, column=0, sticky="w")
        wid = rad.add_button(text=Tmatch["None"])
        wid.grid(row=0, column=1, sticky="w", padx=50)
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, rad, val))

        fra.columnconfigure(1, weight=1)


    def fraAzimouth(self, win, ir):
        "Select azimouth approximation method."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["AZIMOUTH APPROXIMATION:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "radAzim"
        tit = "AZIMOUTH APPROXIMATION"
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=1, sticky="wesn")
        wid = rad.add_button(text=Tmatch["Average of first and last node"])
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=Tmatch["Exhaustive search of all azimouths"])
        wid.grid(row=1, column=0, sticky="w")
        wid = rad.add_button(text=Tmatch["Average azimouth of whole curve"])
        wid.grid(row=0, column=1, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, rad, val))

        fra.columnconfigure(1, weight=1)


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
        ret, vs = ThanICPcom.validate(self, strict)
        if not ret and strict: return ret

        if len(self.thanGps) != 1:
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["1 reference line must be selected"], T["Error in data"])
                return ret
        vs.gps = self.thanGps
        if len(self.thanRel) != 1:
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["1 slave line must be selected"], T["Error in data"])
                return ret
        vs.rel = self.thanRel
        if len(self.thanGps) != len(self.thanRel):
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["The number of reference and slave lines must be the same"], T["Error in data"])
                return ret
        self.result = vs
        return ret
