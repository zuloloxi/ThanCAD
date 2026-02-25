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
Lab of Photogrammetry, NTUA, 2009-2013
This module displays a dialog for the user to define the necessary elements
and options for single pair of lines lines of different dimensionality, global matching.
"""

import sys, copy, ConfigParser, Tkinter
from tkMessageBox import ERROR
import p_gtkuti, p_gtkwid, p_ggen
from p_gsar import readProj
from thanvar import thanfiles
from thantrans import Tmatch, T
from thandiaicp import ThanICPcom
from transf import TransfMixin


class ThanMatch23(ThanICPcom, TransfMixin):
    "Dialog for the pen thickness which the elements of a layer are plotted with."

    def __init__(self, master, vals=None, cargo=None, *args, **kw):
        "Extract initial rectification parameters."
        self.thanValsInit = vals           # This is structure not a scalar
        self.thanProj = cargo
        self.thanGps = []
        self.thanRel = []
        self.projection = None
        kw.setdefault("title", Tmatch["Global Matching of Curves of different Dimensionality"])
        kw.setdefault("buttonlabels", (T["Execute"], T["Cancel"]))
        ThanICPcom.__init__(self, master, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()
        self.thanValsDefICP(v)   # Common ICP parameters
        v.radProject = 1
        v.radProjApprox = 0
        v.entNx = 0.0
        v.entNy = 0.0
        v.entNz = 0.0
        v.entFilcof  = "<Undefined>"
        v.radTransfApprox = 1
        v.gps = []
        v.rel = []
        return v


    def thanValsRead(self, v):
        "Reads the values from a file with specific suffix."
        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".m23")
        if not fn.exists(): return
        c = ConfigParser.SafeConfigParser()
        c.read(fn)
        tv = {}
        for (key,tit,wid,vld) in self.thanWids: tv[key] = tit, vld

        self.thanValsReadICP(c, tv, v)   # Common ICP parameters

        sec = "PROJECTION TYPE"
        try:
            test = int(c.get(sec, "type"))
            i = self.thanProjectFromlib(test)
            if i >= 0: v.radProject = i
        except:
            raise
            pass

        sec = "PURE PROJECTION APPROXIMATION"
        try:
            test = int(c.get(sec, "type"))
            if 0 <= test <= 3: v.radProjApprox = test
        except:
            pass
        try:
            test = c.get(sec, tv["entFilcof"][0])
            v.entFilcof = test
        except:
            pass
        for key in "entNx entNy entNz".split():
            tit, val = tv[key]
            try:
                test = c.get(sec, tit)
                test = val.thanValidate(test)
                if test != None: setattr(v, key, test)
            except:
                pass

        sec = "PURE TRANSFORMATION APPROXIMATION"
        try:
            test = int(c.get(sec, "type"))
            if 0 <= test <= 3: v.radTransfApprox = test
        except:
            pass


    def thanValsWrite(self, v):
        "Write the values to a file with specific suffix."
        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".m23")
        c = ConfigParser.SafeConfigParser()
        if fn.exists(): c.read(fn)
        tv = {}
        for (key,tit,wid,vld) in self.thanWids: tv[key] = tit, vld

        self.thanValsWriteICP(c, tv, v)   # Common ICP parameters

        sec = "PROJECTION TYPE"
        if not c.has_section(sec): c.add_section(sec)
        c.set(sec, "type", str(self.thanProjectTolib(v)))

        sec = "PURE PROJECTION APPROXIMATION"
        if not c.has_section(sec): c.add_section(sec)
        c.set(sec, "type", str(v.radProjApprox))
        c.set(sec, tv["entFilcof"][0], str(v.entFilcof))
        c.set(sec, tv["entNx"][0], str(v.entNx))
        c.set(sec, tv["entNy"][0], str(v.entNy))
        c.set(sec, tv["entNz"][0], str(v.entNz))

        sec = "PURE TRANSFORMATION APPROXIMATION"
        if not c.has_section(sec): c.add_section(sec)
        c.set(sec, "type", str(v.radTransfApprox))

        try: c.write(fn.open("w"))
        except: pass


    def body(self, win):
        self.thanWids = []
        self.colfra = "blue"
#        self.option_add("*font", _fo)
        self.fraLogo(win, 0, theme=Tmatch["Curve Matching Algorithms"], year="2009-2013")
        self.fraICP(win, 1)
        self.bodyProject(win, 2, self.thanWids)
        self.fraSel(win, 3, Tmatch["Select the\nsecondary (3D) line"], Tmatch["Select the\nreference (2D) line"], "23")
        self.fra1ProjApprox(win, 4)
        self.fra1TransfApprox(win, 5)
        win.columnconfigure(0, weight=1)
        for (key,tit,wid,vld) in self.thanWids:
            setattr(self, key, wid)

        if self.thanValsInit == None:
            self.thanValsInit = self.thanValsDef()
            self.thanValsRead(self.thanValsInit)
        self.thanValsSaved = copy.deepcopy(self.thanValsInit)
        self.thanSet(self.thanValsInit)
        self._projApproxDet()


    def fra1ProjApprox(self, win, ir):
        """Select the 1st approximation method for the "pure" projection."""
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["PURE PROJECTION APPROXIMATION:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=6)

        key = "radProjApprox"
        tit = "First Approximation of pure projection"    #Tmatch["First Approximation of pure projection"]
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=1, sticky="wesn", columnspan=6)
        wid = rad.add_button(text=Tmatch["Projection to XY-plane (aerial/satellite images)"], command=self._projApproxDet)
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=Tmatch["Projection to known plane (lidar)"], command=self._projApproxDet)
        wid.grid(row=0, column=1, sticky="w")
        wid = rad.add_button(text=Tmatch["Known projection coefficients"], command=self._projApproxDet)
        wid.grid(row=1, column=1, sticky="w")
        wid = rad.add_button(text=Tmatch["Exhaustive search for projection plane"], command=self._projApproxDet)
        wid.grid(row=1, column=0, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tmatch[tit], rad, val))

        tit = "File of projection coefficients"           #Tmatch["File of projection coefficients"]
        self.thanLabProjCoef = Tkinter.Label(fra, anchor="w", text=Tmatch[tit])
        self.thanLabProjCoef.grid(row=2, column=1, sticky="we")
        key = "entFilcof"
        fildir = thanfiles.getFiledir()
        wid = p_gtkwid.ThanFile(fra, extension=".cof", initialdir=fildir, mode="r",
            command=self._validateReadCoefs, title=Tmatch[tit], width=20, relief=Tkinter.RAISED)
        wid.grid(row=2, column=2, sticky="we", columnspan=5)
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, wid, val))

        tit = "Normal unit vector of projection plane"    #Tmatch["Normal unit vector of projection plane"]
        self.thanLabN = Tkinter.Label(fra, anchor="w", text=Tmatch[tit]+":")
        self.thanLabN.grid(row=3, column=1, sticky="we")
        c = "nx", "ny", "nz"
        k = "entNx", "entNy", "entNz"
        self.thanLabNx = []
        for i in xrange(3):
            tit = c[i]
            lab = Tkinter.Label(fra, text=tit)
            lab.grid(row=3, column=2+2*i, sticky="e")
            self.thanLabNx.append(lab)
            key = k[i]
            wid = p_gtkwid.ThanEntry(fra, width=6)
            wid.grid(row=3, column=3+2*i, sticky="w")
            val = p_gtkwid.ThanValFloat(-1.0, 1.0)
            self.thanWids.append((key, tit, wid, val))


    def _projApproxDet(self):
        "Hide/show details according to the projection choice of the user."
        rad = getattr(self, "radProjApprox")
        i = rad.thanGet()
        if i == 0 or i == 3:
            self.thanLabProjCoef.grid_forget()
            wid = getattr(self, "entFilcof")
            wid.grid_forget()
            self.thanLabN.grid_forget()
            for wid in self.thanLabNx: wid.grid_forget()
            for key in "entNx", "entNy", "entNz":
                wid = getattr(self, key)
                wid.grid_forget()
        elif i == 1:
            self.thanLabProjCoef.grid_forget()
            wid = getattr(self, "entFilcof")
            wid.grid_forget()
            self.thanLabN.grid(row=3, column=1, sticky="we")
            for i,wid in enumerate(self.thanLabNx): wid.grid(row=3, column=2+2*i, sticky="e")
            for i,key in enumerate(("entNx", "entNy", "entNz")):
                wid = getattr(self, key)
                wid.grid(row=3, column=3+2*i, sticky="w")
        elif i == 2:
            self.thanLabProjCoef.grid(row=2, column=1, sticky="we")
            wid = getattr(self, "entFilcof")
            wid.grid(row=2, column=2, sticky="we", columnspan=5)
            self.thanLabN.grid_forget()
            for wid in self.thanLabNx: wid.grid_forget()
            for key in "entNx", "entNy", "entNz":
                wid = getattr(self, key)
                wid.grid_forget()


    def fra1TransfApprox(self, win, ir):
        """Select the 1st approximation method for the "pure" 2D transformation."""
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["PURE TRANSFORMATION APPROXIMATION:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "radTransfApprox"
        tit = "First Approximation of pure 2D transformation"     #Tmatch["First Approximation of pure 2D transformation"]
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=1, sticky="wesn")

        wid = rad.add_button(text=Tmatch["None (identity transformation)"])
        wid.grid(row=0, column=0, sticky="w")
        wid = rad.add_button(text=Tmatch["2D similarity approximation"])
        wid.grid(row=1, column=0, sticky="w")
        wid = rad.add_button(text=Tmatch["Distance algorithm"])
        wid.grid(row=0, column=1, sticky="w", padx=100)
        wid = rad.add_button(text=Tmatch["2D polynomial approximation"])
        wid.grid(row=1, column=1, sticky="w", padx=100)
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, rad, val))

        fra.columnconfigure(1, weight=1)
        fra.columnconfigure(2, weight=1)


    def _validateReadCoefsold(self, fn, strict=True):
        "Reads and validates the coefficients from a file."
        if not fn: return False
        icodp = self.thanProjectTolib()
        projection = Projection(icodp)()
        try:
            fr = open(fn)
            projection.read(fr)
            fr.close()
        except (IOError,ValueError), why:  # Open error, conversion to float error, file too short
            if strict: p_gtkuti.thanGudModalMessage(self, "%s:\n\n%s" % (p_gtkuti.thanAbsrelPath(fn), why), T["Read failed"], ERROR)   # (Gu)i (d)ependent
            return False
        except StopIteration, why:  # Open error, conversion to float error, file too short
            if strict: p_gtkuti.thanGudModalMessage(self, "%s:\n\n%s" % (p_gtkuti.thanAbsrelPath(fn), "End of file."), T["Read failed"], ERROR)   # (Gu)i (d)ependent
            return False
        self.projection = projection
        return True


    def _validateReadCoefs(self, fn, strict=True):
        "Reads and validates the coefficients from a file."
        if not fn: return False
        try:
            fr = open(fn)
            projection = readProj(fr)
            fr.close()
        except (IOError,ValueError), why:  # Open error, conversion to float error, file too short
            if strict: p_gtkuti.thanGudModalMessage(self, "%s:\n\n%s" % (p_gtkuti.thanAbsrelPath(fn), why), T["Read failed"], ERROR)   # (Gu)i (d)ependent
            return False
        except StopIteration, why:  # Open error, conversion to float error, file too short
            if strict: p_gtkuti.thanGudModalMessage(self, "%s:\n\n%s" % (p_gtkuti.thanAbsrelPath(fn), "End of file."), T["Read failed"], ERROR)   # (Gu)i (d)ependent
            return False
        self.projection = projection
        return True


    def validate(self, strict=True):
        """Returns true if the value chosen by the user is valid.

        If strict == True, then if an error is found, an error message is displayed,
        self.result is unchanged, and False is rerurned to the caller.
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
        icodp = self.thanProjectTolib(vs)
        self.projection = None
        if vs.radProjApprox == 2:
            if not self._validateReadCoefs(vs.entFilcof, strict=strict): # vs.projection = self.projection  # self.projection is set by _validateReadCoefs()
                ret = False
                if strict:
                    self.initial_focus = self.entFilcof
                    return ret

        if len(self.thanGps) != 1:
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["1 reference line must be selected"], T["Error in data"])
                return ret
        vs.gps = self.thanGps
        if len(self.thanRel) != 1:
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["1 projected line must be selected"], T["Error in data"])
                return ret
        vs.rel = self.thanRel
        if len(self.thanGps) != len(self.thanRel):
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["The number of reference and slave lines must be the same"], T["Error in data"])
                return ret
        self.result = vs
        return ret


    def apply(self):
        "Last settings - after successful validation and after the window has been closed."
        self.result.projection = self.projection  # This could not be set by validate because otherwise
                                                  # self.thanValsSaved would never equal self.result
        self.thanValsWrite(self.result)
        self.result.radProject = self.thanProjectTolib(self.result)  #This is probably not needed as the information is passed through projection


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
        del self.thanLabProjCoef, self.thanLabN, self.thanLabNx
        ThanICPcom.destroy(self)


if __name__ == "__main__":
    root = Tkinter.Tk()
    win = ThanMatch23(root, None)
    print win.result.anal()
