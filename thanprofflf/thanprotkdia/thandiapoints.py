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

Point based transformation Algorithms, Dimitra Vassilaki, PhD Candidate
Lab of Photogrammetry, NTUA, 2010-2013
This module displays a dialog where the user enters points and selects the
transformation type to compute from the known points.
"""

import copy, ConfigParser, Tkinter
from tkMessageBox import ERROR
import p_gtkuti, p_gtkwid, p_ggen
from p_gsar import Projection, readProj
import thandr
from thanvar import thanfiles
from thantrans import Tmatch, T
from thandiaicp import ThanICPcom
from transf import TransfMixin


class ThanPoTransf(ThanICPcom, TransfMixin):
    "Dialog for the computation of a transformation using control points."

    def __init__(self, master, vals=None, cargo=None, *args, **kw):
        "Begin the dialog."
        self.thanValsInit = vals           # This is structure not a scalar
        self.thanProj = cargo
        self.thanNames, self.thanProjlays = _findProjlays()
        self.projection = None
        self.__n23 = 6    #Number of projections
        kw.setdefault("title", Tmatch["Image Registration with Control Points"])
        kw.setdefault("buttonlabels", (T["Execute"], T["Cancel"]))
        ThanICPcom.__init__(self, master, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()
#        self.thanValsDefICP(v)   # Common ICP parameters
        v.radJob = 0
        v.radProject = 1
        v.comGps = self.thanNames[0]
        v.comRel = self.thanNames[0]
        v.filProj = "<Untitled>"
        v.comGpsch = self.thanNames[0]
        v.comRelch = self.thanNames[0]
        return v


    def thanValsRead(self, v):
        "Reads the values from a file with specific suffix."
        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".mcp")
        if not fn.exists(): return
        c = ConfigParser.SafeConfigParser()
        c.read(fn)
        tv = {}
        for (key,tit,wid,vld) in self.thanWids: tv[key] = tit, vld

        sec = "COMPUTATION TYPE"
        try:
            test = int(c.get(sec, "type"))
            if 0 <= test <= 1: v.radJob = test
        except:
            pass

        sec = "CONTROL POINTS"
        try:
            test = int(c.get(sec, "type"))
            i = self.thanProjectFromlib(test)
            if i >= 0: v.radProject = i
        except:
            pass
        for key in "comGps comRel".split():
            tit, val = tv[key]
            try:
                test = c.get(sec, tit)
                test = val.thanValidate(test)
                if test != None: setattr(v, key, test)
            except:
                pass

        sec = "CHECK POINTS"
        for key in "filProj comGpsch comRelch".split():
            tit, val = tv[key]
            try:
                test = c.get(sec, tit)
                test = val.thanValidate(test)
                if test != None: setattr(v, key, test)
            except:
                pass


    def thanValsWrite(self, v):
        "Write the values to a file with specific suffix."
        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".mcp")
        c = ConfigParser.SafeConfigParser()
        if fn.exists(): c.read(fn)
        tv = {}
        for (key,tit,wid,vld) in self.thanWids: tv[key] = tit, vld

        sec = "COMPUTATION TYPE"
        if not c.has_section(sec): c.add_section(sec)
        c.set(sec, "type", str(v.radJob))

        sec = "CONTROL POINTS"
        if not c.has_section(sec): c.add_section(sec)
        c.set(sec, "type", str(self.thanProjectTolib(v)))
        for key in "comGps comRel".split():
            tit, val = tv[key]
            c.set(sec, tit, str(getattr(v, key)))

        sec = "CHECK POINTS"
        if not c.has_section(sec): c.add_section(sec)
        for key in "comGpsch comRelch filProj".split():
            tit, val = tv[key]
            c.set(sec, tit, str(getattr(v, key)))

        try:
            c.write(fn.open("w"))
        except Exception, why:
            prt = self.thanProj[2].thanPrter
            prt(Tmatch["Error while writting %s"] % fn)
            prt(why)


    def body(self, win):
        "Build the GUI."
        self.thanWidsCon = []    #Contains the control points' widgets
        self.thanWidsCheck = []  #Contains the check points' widgets
        self.colfra = "blue"
        self.fraPocon = FraPo("CONTROL")
        self.fraPocheck = FraPo("CHECK")

        self.fraLogo(win, 0, theme=Tmatch["Image Registration with Control Points"], year="2010-2013")
        self.fraJob(win, 1)
        self.fraProject = self.bodyProject(win, 2, self.thanWidsCon)
        self.fraCheck = self.bodyCheck(win, 2)
        self.fraPocon.frame(self, win, 3, self.thanWidsCon)
        self.fraPocheck.frame(self, win, 3, self.thanWidsCheck)
        self.thanWids = self.thanWidsCon+self.thanWidsCheck    #Contains all the widgets

        self.thanLabGps = self.thanLabRel = None   #For ThanICPcom.destroy()

        win.columnconfigure(0, weight=1)
        for (key,tit,wid,vld) in self.thanWids:
            setattr(self, key, wid)

        if self.thanValsInit == None:
            self.thanValsInit = self.thanValsDef()
            self.thanValsRead(self.thanValsInit)
        self.thanValsSaved = copy.deepcopy(self.thanValsInit)

        self.fraPocon.assignCommand(self)
        self.fraPocheck.assignCommand(self)
        self.radJob.config(command=self.__updateJob)
        self.thanSet(self.thanValsInit)
        self.__updateJob()


    def fraJob(self, win, ir):
        "Select projection type."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["COMPUTATION TYPE:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "radJob"
        tit = "Computation type"                       #Tmatch["Computation type"]
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=1, sticky="wesn")

        wid = rad.add_button(text=Tmatch["Compute projection/transformation"])
        wid.grid(row=0, column=0, sticky="w")
        wid = Tkinter.Frame(rad, width=20)
        wid.grid(row=0, column=1, sticky="w")
        wid = rad.add_button(text=Tmatch["Compute error using checkpoints"])
        wid.grid(row=0, column=2, sticky="w")

        val = p_gtkwid.ThanValidator()
        self.thanWidsCon.append((key, Tmatch[tit], rad, val))    #It doesn't matter if it bleong to control widgets..
        fra.columnconfigure(1, weight=1)                    #..sinc it has no validator


    def __updateJob(self):
        "Update the number of points or any error message."
        j = self.radJob.thanGet()
        if j == 0:          #Switch to computation of transformation
            self.fraCheck.grid_forget()
            self.fraPocheck.fra.grid_forget()
            self.fraProject.grid(row=2, column=0, pady=5, sticky="we")
            self.fraPocon.fra.grid(row=3, column=0, pady=5, sticky="we")
        else:               #Switch to computation of error using check points
            self.fraProject.grid_forget()
            self.fraPocon.fra.grid_forget()
            self.fraCheck.grid(row=2, column=0, pady=5, sticky="we")
            self.fraPocheck.fra.grid(row=3, column=0, pady=5, sticky="we")


    def bodyCheck(self, win, ir):
        "Select projection type."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
#        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["TRANSFORMATION DEFINITION:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "filProj"
        tit = "File with projection/transformation coefficients"
        lab = Tkinter.Label(fra, anchor="w", text=tit)
        lab.grid(row=1, column=1, sticky="we")
        fildir = thanfiles.getFiledir()
        wid = p_gtkwid.ThanFile(fra, extension=".cof", initialdir=fildir, mode="r",
            command=lambda fn: self.__validateCof(fn)[0], title=tit, width=20, relief=Tkinter.RAISED)
        wid.grid(row=1, column=2, sticky="we")
        val = ThanValCof(self.__validateCof)
        self.thanWidsCheck.append((key, tit, wid, val))
        fra.columnconfigure(2, weight=1)
        return fra


    def __validateCof(self, fn=None):
        "Check if the file of projection coefficents is valid."
        if self.radJob.thanGet() == 0:
            return True, Projection(0)(), ""     #Return unit polynomial projection
        if fn == None: fn = self.filProj.thanGet()
        if not fn: return False, Projection(0)(), Tmatch["No file specified"]
        try:
            fr = file(fn)
        except IOError, why:  # Open error
            return False, Projection(0)(), Tmatch["Open failed:"]+"%s" % why
        try:
            L = readProj(fr)
            fr.close()
            return True, L, ""
        except Exception, why:
            return False, Projection(0)(), Tmatch["Reading failed:"]+"%s" % why


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
        cpref, cpima = self.fraPocon.updateLens()       #Make the messages in message widget  consistent
        cprefch, cpimach = self.fraPocheck.updateLens() #Make the messages in message widget  consistent
        if self.radJob.thanGet() == 0:
            ret, vs = ThanICPcom.validate(self, strict, self.thanWidsCon)
            if not ret and strict: return ret
            _, vs = ThanICPcom.validate(self, strict=False, wids=self.thanWidsCheck, values=vs)
        else:
            ret, vs = ThanICPcom.validate(self, strict, self.thanWidsCheck)
            if not ret and strict: return ret
            _, vs = ThanICPcom.validate(self, strict=False, wids=self.thanWidsCon, values=vs)

#        vs.gps = self.thanGps
#        vs.rel = self.thanRel
#        if len(self.thanGps) != len(self.thanRel):
#            ret = False
#            if strict:
#                p_gtkuti.thanGudModalMessage(self, Tmatch["The number of reference and slave lines must be the same"], Tmatch["Error in data"])
#                return ret

        self.result = vs
        return ret


    def apply(self):
        "Last settings - after successful validation and after the window has been closed."
#       The following could not be set by validate because otherwise
#       self.thanValsSaved would never equal self.result
        r = self.result
        r.cpref, r.cpima = self.fraPocon.updateLens()
        r.cprefch, r.cpimach = self.fraPocheck.updateLens()
        self.thanValsWrite(self.result)
        self.result.radProject = self.thanProjectTolib(self.result)  #This is needed here


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
#       del self.thanLabGps, self.thanLabRel, self.thanProj  #These are deleted in thanICPcom.destroy
        del self.thanWidsCon, self.thanWidsCheck
        del self.thanProjlays, self.fraProject, self.fraCheck
        self.fraPocon.destroy()
        self.fraPocheck.destroy()
        del self.fraPocon, self.fraPocheck
        ThanICPcom.destroy(self)


class FraPo:
    "A class which display widgets for control or check points."

    def __init__(self, name="CONTROL"):
        "Initialize control or check points."
        if name == "CONTROL":
            self.Selpo = Tmatch["SELECTION OF CONTROL POINTS:"]
            self.Stapo = Tmatch["Control point status"]
            self.widGps = "comGps"
            self.widRel = "comRel"
        elif name == "CHECK":
            self.Selpo = Tmatch["SELECTION OF CHECK POINTS:"]
            self.Stapo = Tmatch["Check point status"]
            self.widGps = "comGpsch"
            self.widRel = "comRelch"
        else:
            raise ValueError, name

    def frame(self, parent, win, ir, wids):
        "Select control points."
        self.thanProjlays = parent.thanProjlays
        fra = self.fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
#        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=parent.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=parent.colfra, text=self.Selpo)
        lab.grid(row=0, column=1, sticky="w", columnspan=2)

        key = self.widGps
        tit = "Drawing/layer of reference points"                  #Tmatch["Drawing/layer of reference points"]
        val = self.thanValGps = ThanValProjlay(parent.thanProjlays)
        lab = Tkinter.Label(fra, text=Tmatch[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanCombo(fra, labels=parent.thanNames, width=30)
        wid.grid(row=1, column=2, sticky="we")
        wids.append((key, tit, wid, val))
        self.comGps = wid

        key = self.widRel
        tit = "Drawing/layer of image points"                      #Tmatch["Drawing/layer of image points"]
        val = self.thanValRel = ThanValProjlay(parent.thanProjlays)
        lab = Tkinter.Label(fra, text=Tmatch[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanCombo(fra, labels=parent.thanNames, width=30)
        wid.grid(row=2, column=2, sticky="we")
        wids.append((key, tit, wid, val))
        self.comRel = wid

        wid = Tkinter.Frame(fra, height=10)
        wid.grid(row=3, column=1)
        lab = Tkinter.Label(fra, text=self.Stapo)
        lab.grid(row=4, column=1, sticky="w")
        wid = p_gtkwid.ThanScrolledText(fra, height=3, readonly=True, bg="lightpink")
        wid.grid(row=5, column=1, columnspan=2, sticky="wesn")
        self.thanStat = wid

        fra.columnconfigure(2, weight=1)


    def updateLens(self, i=None, text=None):
        "Update the number of points or any error message."
        def prt(s): self.thanStat.thanAppendf("%s\n" % s)
        self.thanStat.thanSet("")                              #Clear status widget
        self.thanValGps.thanValidate(self.comGps.thanGet())    #Produce error/info
        prt("Reference: %s" % self.thanValGps.thanGetErr())
        self.thanValRel.thanValidate(self.comRel.thanGet())    #Produce error/info
        prt("Image: %s" % self.thanValRel.thanGetErr())
        if self.thanValGps.thanGetIerr() > 0: return {}, {}    #Errors found
        if self.thanValRel.thanGetIerr() > 0: return {}, {}    #Errors found

        _, lay = self.thanProjlays[self.comGps.thanGet()]
        cpref, _ = _findPoints(lay)
        _, lay = self.thanProjlays[self.comRel.thanGet()]
        cpima, _ = _findPoints(lay)
        for name in sorted(cpref.keys()):
            if name not in cpima:
                prt("Reference point %s not found in image points." % name)
        for name in sorted(cpima.keys()):
            if name not in cpref:
                prt("Image point %s not found in reference points." % name)
        return cpref, cpima


    def assignCommand(self, parent):
        "Assign update command to widgets."
        getattr(parent, self.widGps).config(command=self.updateLens)
        getattr(parent, self.widRel).config(command=self.updateLens)


    def destroy(self):
        "Break circular references."
        del self.fra, self.comGps, self.comRel, self.thanStat


class ThanValProjlay(p_gtkwid.ThanValidator):
    "Find if the chosen drawing/layer has points."

    def __init__(self, projlays):
        "Just save the projlays mdict."
        p_gtkwid.ThanValidator.__init__(self)
        self.projlays = projlays

    def thanValidate(self, v):
        proj, lay = self.projlays.get(v, (None, None))
        if proj == None:
            self.thanSetErr(1, "Project/layer %s was not found." % v)
            return None
        cps, dups = _findPoints(lay)
        if len(cps) < 1:
            self.thanSetErr(2, "There are no points in drawing/layer: %s." % v)
            return None
        if len(dups) > 0:
            self.thanSetErr(3, "There are duplicate point names in drawing/layer: %s:\n%s." % (v, " ".join(dups)))
            return None
        self.thanSetErr(0, "(%d points found)" % len(cps))
        return v


class ThanValCof(p_gtkwid.ThanValidator):
    "Find if the chosen drawing/layer has points."

    def __init__(self, valcof):
        "Just save the projlays mdict."
        p_gtkwid.ThanValidator.__init__(self)
        self.valcof = valcof

    def thanValidate(self, v):
        ok, _, ter = self.valcof()
        if ok:
            self.thanSetErr(0, "")
            return v
        self.thanSetErr(1, ter)
        return None


def _findProjlays():
    "Find all the layers of all the projects."
    projlays = {}
    for proj in thanfiles.getOpened()[1:]:
        lt = proj[1].thanLayerTree
        for lay in lt.dilay.itervalues():
            nam = "%s/%s" % (proj[0].namebase, lay.thanGetPathname())
            projlays[nam] = (proj, lay)
    names = projlays.keys()
    names.sort()
    return names, projlays


def _findPoints(lay):
    "Find and return names point of layer."
    cpref = {}
    dups = []
    for elem in lay.thanQuad:
        if not isinstance(elem, thandr.ThanPointNamed): continue
        if elem.name in cpref: dups.append(elem.name)
        cpref[elem.name] = elem
    return cpref, dups


if __name__ == "__main__":
    root = Tkinter.Tk()
    win = ThanMatch23(root, None)
    print win.result.anal()
