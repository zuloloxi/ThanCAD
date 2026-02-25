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

Multiple Curve Matching Algorithms, Dimitra Vassilaki, PhD Candidate
Lab of Photogrammetry, NTUA, 2008-2013
This module defines the base for the dialogs related to ICP algorithms
"""

from types import *
import Tkinter, tkFont
from thanvar import thanicon, Canc
from thantrans import Tmatch, T
import p_gtkuti, p_gtkwid, p_ggen
from thancom.selutil import thanSelMultlines

class ThanICPcom(p_gtkuti.ThanDialog):
    "An object which provides for functionality common to ICP algorithms."

    def __init__(self, *args, **kw):
        p_gtkuti.ThanDialog.__init__(self, *args, **kw)


    def thanValsDefICP(self, v):
        "Build default values."
        v.entDisInt = 0.20
        v.entDisRange = v.entDisInt*200
        v.entThres  = 0.10
        v.entSteps  = 50


    def thanValsReadICP(self, c, tv, v):
        "Reads the values from a file with specific suffix."
        sec = "ICP GENERAL PARAMETERS"
        for key in "entDisInt entDisRange entThres entSteps".split():
            tit, val = tv[key]
            try:
                test = c.get(sec, tit)
                test = val.thanValidate(test)
                if test != None: setattr(v, key, test)
            except:
                pass


    def thanValsWriteICP(self, c, tv, v):
        "Write the values to a file with specific suffix."
        sec = "ICP GENERAL PARAMETERS"
        if not c.has_section(sec): c.add_section(sec)
        for key in "entDisInt entDisRange entThres entSteps".split():
            tit, val = tv[key]
            c.set(sec, tit, str(getattr(v, key)))


    def fraLogo(self, win, ir, theme=Tmatch["Curve Matching Algorithms"], year=2013):
        "Display the logo."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")
        global pyrf, mormor, fo1
        fo1 = tkFont.Font(family="Liberation Serif", weight="bold", size=18)
#        return

        lab = Tkinter.Label(fra, image=thanicon.get("ntua3"))
        lab.grid(row=0, column=0, rowspan=3)

        wid = Tkinter.Frame(fra)
        wid.grid(row=0, column=1, rowspan=3, sticky="we")

        lab = Tkinter.Label(fra, text=theme, font=fo1, fg="blue")
        lab.grid(row=0, column=2, sticky="w")
        lab = Tkinter.Label(fra, text=Tmatch["Dimitra Vassilaki, PhD Candidate"], font=fo1, fg="blue")
        lab.grid(row=1, column=2, sticky="w")
        lab = Tkinter.Label(fra, text=Tmatch["Lab of Photogrammetry, NTUA, "]+str(year), font=fo1, fg="blue")
        lab.grid(row=2, column=2, sticky="w")

        wid = Tkinter.Frame(fra)
        wid.grid(row=0, column=3, rowspan=3, sticky="we")

        lab = Tkinter.Label(fra, image=thanicon.get("mormor"))
        lab.grid(row=0, column=4, rowspan=3)
        fra.columnconfigure(1, weight=1)
        fra.columnconfigure(3, weight=1)


    def fraICP(self, win, ir):
        "Select projection type."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["ICP GENERAL PARAMETERS:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "entDisInt"
        tit = "Interpolation Distance (m)"             #Tmatch["Interpolation Distance (m)"]
        val = p_gtkwid.ThanValFloat(1e-6, 1e6)
        lab = Tkinter.Label(fra, text=Tmatch[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=1, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        key = "entDisRange"
        tit = "Distance Range (m)"                     #Tmatch["Distance Range (m)"]
        val = p_gtkwid.ThanValFloat(1e-6, 1e6)
        lab = Tkinter.Label(fra, text=Tmatch[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=2, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        key = "entThres"
        tit = "Convergence threshold (m)"              #Tmatch["Convergence threshold (m)"]
        val = p_gtkwid.ThanValFloat(1e-6, 1e6)
        lab = Tkinter.Label(fra, text=Tmatch[tit])
        lab.grid(row=1, column=4, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=1, column=5, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        wid = Tkinter.Frame(fra)
        wid.grid(row=1, column=3, padx=30)

        key = "entSteps"
        tit = "Max number of steps"
        val = p_gtkwid.ThanValInt(1, 1000)
        lab = Tkinter.Label(fra, text=Tmatch[tit])     #Tmatch["Max number of steps"]
        lab.grid(row=2, column=4, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=5)
        wid.grid(row=2, column=5, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        fra.columnconfigure(3, weight=1)


    def fraSel(self, win, ir, tref, tsec, nlines):
        "Select primary and secondary lines to match."
        if nlines == "23":
            selref = lambda var="thanGps", mes=Tmatch["Select the reference (3D) line\n"]: self.__selref1(var, mes)
            selsla = lambda var="thanRel", mes=Tmatch["Select the projected (2D) line\n"]: self.__selref1(var, mes)
        elif nlines == "m23":
            selref = lambda var="thanGps", mes=Tmatch["Select the reference (3D) lines\n"]: self.__selrefm(var, mes)
            selsla = lambda var="thanRel", mes=Tmatch["Select the projected (2D) lines\n"]: self.__selrefm(var, mes)
        elif nlines == "m2":
            selref = lambda var="thanGps", mes=Tmatch["Select the reference lines:\n"]: self.__selrefm(var, mes)
            selsla = lambda var="thanRel", mes=Tmatch["Select the lines to be moved towards the reference lines:\n"]: self.__selrefm(var, mes)
        elif nlines == "2d":
            selref = lambda var="thanGps", mes=Tmatch["Select the reference line:\n"]: self.__selref1(var, mes)
            selsla = lambda var="thanRel", mes=Tmatch["Select the line to be moved towards the reference line:\n"]: self.__selref1(var, mes)
        else:
            assert False, "Uknown curve code: %s" % nlines

        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")
        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["SELECT LINES:"])
        lab.grid(row=0, column=1, sticky="w")

        but = Tkinter.Button(fra, text=tref,
              bg="lightcyan", activebackground="cyan", command=selref)
        but.grid(row=1, column=1, sticky="w")
        but = Tkinter.Button(fra, text=tsec,
              bg="lightcyan", activebackground="cyan", command=selsla)
        but.grid(row=1, column=4, sticky="w")

        self.thanLabGps = p_gtkwid.ThanLabel(fra, text="", width=15, relief=Tkinter.FLAT)
        self.thanLabGps.grid(row=1, column=2, sticky="w")
        self.thanLabRel = p_gtkwid.ThanLabel(fra, text="", width=15, relief=Tkinter.FLAT)
        self.thanLabRel.grid(row=1, column=5, sticky="w")
        self.__updateLens()

        wid = Tkinter.Frame(fra)
        wid.grid(row=1, column=3, sticky="we")
        fra.columnconfigure(3, weight=1)


    def __selref1(self, var="thanGps", mes=Tmatch["Select the reference (3D) line\n"]):
        "Select the 1 line."
        proj = self.thanProj
        p_gtkuti.thanGrabRelease()
        self.withdraw()
        gps = thanSelMultlines(proj, 1, mes, strict=True)
        proj[2].thanGudResetSelColor()                   # Unmarks the selection
        proj[2].thanGudSetSelRestore()                   # Restores previous selection
        proj[2].thanUpdateLayerButton()                  # Show current layer again
        if gps == Canc:
            from thantkgui.thantkcmd import DEFCAN
            proj[2].thanCom.thanAppend("%s\n" % DEFCAN, "can")
        else:
            setattr(self, var, gps)
            self.__updateLens()
        self.deiconify()
        p_gtkuti.thanGrabSet(self)


    def __selrefm(self, var, mes):
        "Select multiple lines."
        proj = self.thanProj
        p_gtkuti.thanGrabRelease()
        self.withdraw()
        gps = thanSelMultlines(proj, 2, mes, strict=False)
        proj[2].thanGudResetSelColor()                   # Unmarks the selection
        proj[2].thanGudSetSelRestore()                   # Restores previous selection
        proj[2].thanUpdateLayerButton()                  # Show current layer again
        if gps == Canc:
            from thantkgui.thantkcmd import DEFCAN
            proj[2].thanCom.thanAppend("%s\n" % DEFCAN, "can")
        else:
            setattr(self, var, gps)
            self.__updateLens()
        self.deiconify()
        p_gtkuti.thanGrabSet(self)


    def __updateLens(self):
        "Update the number of lines."
        self.thanLabGps.thanSet(Tmatch["(%d selected)"]%(len(self.thanGps), ))
        self.thanLabRel.thanSet(Tmatch["(%d selected)"]%(len(self.thanRel), ))


    def thanSet(self, vs):
        "Set new values to the widgets."
        stat = Tkinter.NORMAL
        for (key,tit,wid,vld) in self.thanWids:
            print "setting", key
            v = getattr(vs, key)
            if type(v) == FloatType or type(v) == IntType: v = str(v)
            wid.config(state=stat) # All widgets must be enabled..
            wid.thanSet(v)         # ..to change their values


    def validate(self, strict=True, wids=None, values=None):
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
        ret = True
        if values == None: vs = p_ggen.Struct()
        else:              vs = values
        if wids == None: wids = self.thanWids
        for key,tit,wid,vld in wids:
            print "validating:", key
            v1 = vld.thanValidate(wid.thanGet())
            if v1 == None:
                ret = False
                if strict:
                    tit = u'"%s":\n%s' % (tit, vld.thanGetErr())
                    p_gtkuti.thanGudModalMessage(self, tit, T["Error in data"])
                    self.initial_focus = wid
                    return ret, None
                else:
                    v1 = getattr(self.thanValsInit, key)
            setattr(vs, key, v1)
        return ret, vs


    def apply(self):
        "Last settings - after successful validation and after the window has been closed."
        self.thanValsWrite(self.result)


    def cancel(self, *args):
        "Ask before cancel."
        ret = self.validate(strict=False)     # If anything is wrong, then let it be
        if self.result.__dict__ != self.thanValsSaved.__dict__:
#            print "result=", self.result.__dict__
#            print "saved=", self.thanValsSaved.__dict__
            a = p_gtkuti.thanGudAskOkCancel(self, T["Data modified, OK to cancel?"], T["Warning"])
            if not a: return        # Cancel was stopped
        p_gtkuti.ThanDialog.cancel(self, *args)


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
        for (key,tit,wid,vld) in self.thanWids:
            delattr(self, key)
        del self.thanLabGps, self.thanLabRel
        del self.thanProj, self.thanWids, self.thanValsInit, self.thanValsSaved
        p_gtkuti.ThanDialog.destroy(self)


    def __del__(self):
        print "ThanICPcom ThanDialog", self, "dies.."
