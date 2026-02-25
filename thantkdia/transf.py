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

This module contains a mixin for the various 3d-2d and 2d-2d transformations
available to ThanCad.
"""

import tkinter
import p_gtkwid
import thandr
from thantrans import Tmatch
from thanvar import thanfiles


class TransfMixin:
    projectcode = \
        (("Central Projection (collinearity)",             31),
         ("Direct Linear Transform",                       1),
         ("Rational Polynomial Projection of first order", 2),
         ("Polynomial Projection of first order",          0),
         ("Polynomial Projection of second order",         3),
         ("Rational Polynomial Projection of second order",4),
         ("Rational Polynomial Projection of 2/1 order",   5),
         ("Direct Linear Transform",                      11),
         ("Rational Polynomial Projection of first order",12),
         ("Polynomial Projection of first order",         10),
         ("Polynomial Projection of second order",        13),
        )

    def thanProjectFromlib(self, icodp):
        "Find the projection code for the radProject widget given the library projection code."
        for ia,(_,icodpa) in enumerate(self.projectcode):
            if icodp == icodpa: return ia
        return -1

    def thanProjectTolib(self, v=None):
        "Get the projection code from the radProject widget or the values v and transform it to library projection code."
        if v is None: i = self.radProject.thanGet()
        else:         i = v.radProject
        return self.projectcode[i][1]

    def bodyProject(self, win, ir, wids, pro=True):
        "Select projection type."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["PROJECTION TYPE:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "radProject"
        tit = "Projection type"           #Tmatch["Projection type"]
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=1, sticky="wesn", pady=5)

        lab = tkinter.Label(rad, text=Tmatch["3D-2D"], fg=self.colfra)
        lab.grid(row=0, column=0, sticky="w")
        pc = self.projectcode
        if pro:                           #Professional version with FFLFs
            for i in range(3):
                wid = rad.add_button(text=Tmatch[pc[0+i][0]])
                wid.grid(row=i+1, column=0, sticky="w")
        else:                             #Professional version without FFLFs
            for i in range(3):
                wid = rad.add_button(text=Tmatch[pc[0+i][0]])
                if i > 0: wid.grid(row=i+1, column=0, sticky="w")
        for i in range(4):
            wid = rad.add_button(text=Tmatch[pc[3+i][0]])
            wid.grid(row=i+1, column=2, sticky="w")

        lab = tkinter.Label(rad, text=Tmatch["2D-2D"], fg=self.colfra)
        lab.grid(row=5, column=0, sticky="w")
        for i in range(4, 6):
            wid = rad.add_button(text=Tmatch[pc[3+i][0]])
            wid.grid(row=i+2, column=0, sticky="w")
        for i in range(4, 6):
            wid = rad.add_button(text=Tmatch[pc[5+i][0]])
            wid.grid(row=i+2, column=2, sticky="w")
        wid = tkinter.Frame(rad)
        wid.grid(row=0, column=1, sticky="we", padx=30)

        val = p_gtkwid.ThanValidator()
        wids.append((key, tit, rad, val))

        fra.columnconfigure(1, weight=1)
        fra.columnconfigure(2, weight=1)
        return fra


class FraPo:
    "A class which displays widgets for control (new projection) or check points (old projection)."

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
            raise ValueError(name)

    def frame(self, parent, win, ir, wids):
        "Create the widgets for selecting control or check points."
        self.thanProjlays = parent.thanProjlays
        fra = self.fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
#        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=parent.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=parent.colfra, text=self.Selpo)
        lab.grid(row=0, column=1, sticky="w", columnspan=2)

        key = self.widGps
        tit = "Drawing/layer of reference points"                  #Tmatch["Drawing/layer of reference points"]
        val = self.thanValGps = ThanValProjlay(parent.thanProjlays)
        lab = tkinter.Label(fra, text=Tmatch[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanCombo(fra, labels=parent.thanNames, width=30)
        wid.grid(row=1, column=2, sticky="we")
        wids.append((key, tit, wid, val))
        self.comGps = wid

        key = self.widRel
        tit = "Drawing/layer of image points"                      #Tmatch["Drawing/layer of image points"]
        val = self.thanValRel = ThanValProjlay(parent.thanProjlays)
        lab = tkinter.Label(fra, text=Tmatch[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanCombo(fra, labels=parent.thanNames, width=30)
        wid.grid(row=2, column=2, sticky="we")
        wids.append((key, tit, wid, val))
        self.comRel = wid

        wid = tkinter.Frame(fra, height=10)
        wid.grid(row=3, column=1)
        lab = tkinter.Label(fra, text=self.Stapo)
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
        cpref, _ = findPoints(lay)
        _, lay = self.thanProjlays[self.comRel.thanGet()]
        cpima, _ = findPoints(lay)
        for name in sorted(cpref.keys()):   #works for python2,3
            if name not in cpima:
                prt("Reference point %s not found in image points." % name)
        for name in sorted(cpima.keys()):  #works for python2,3
            if name not in cpref:
                prt("Image point %s not found in reference points." % name)
        return cpref, cpima


    def assignCommand(self, parent):
        "Assign update command to widgets."
        getattr(parent, self.widGps).config(command=self.updateLens)
        getattr(parent, self.widRel).config(command=self.updateLens)


    def destroy(self):
        "Break circular references."
        del self.thanProjlays
        del self.fra, self.comGps, self.comRel, self.thanStat


class ThanValProjlay(p_gtkwid.ThanValidator):
    "Find if the chosen drawing/layer has points."

    def __init__(self, projlays):
        """Just save the projlays dictionary.

        projlays is a dict from string (filename + "/" + layer pathname) to
        a tuple (proj object, layer object)."""
        p_gtkwid.ThanValidator.__init__(self)
        self.projlays = projlays

    def thanValidate(self, v):
        "Verify that string v (filname+'/'+layer pathname) exists and has points."
        proj, lay = self.projlays.get(v, (None, None))
        if proj is None:
            self.thanSetErr(1, "Project/layer %s was not found." % v)
            return None
        cps, dups = findPoints(lay)
        if len(cps) < 1:
            self.thanSetErr(2, "There are no points in drawing/layer: %s." % v)
            return None
        if len(dups) > 0:
            self.thanSetErr(3, "There are duplicate point names in drawing/layer: %s:\n%s." % (v, " ".join(dups)))
            return None
        self.thanSetErr(0, "(%d points found)" % len(cps))
        return v


class ThanValWrapper(p_gtkwid.ThanValidator):
    """This is validator object which just calls a validating function.

    The validating function must take no arguments and return a boolean value
    (true if successful), an object and an error message as a 3element tuple."""

    def __init__(self, func):
        "Save the validating function."
        p_gtkwid.ThanValidator.__init__(self)
        self.func = func

    def thanValidate(self, v):
        "Validate by calling the stored validating function."
        ok, _, ter = self.func()
        if ok:
            self.thanSetErr(0, "")
            return v
        self.thanSetErr(1, ter)
        return None


def findProjlays():
    """Find all the layers of all the projects.

    projlays is a dict from string (filename + "/" + layer pathname) to
    a tuple (proj object, layer object)."""
    projlays = {}
    for proj in thanfiles.getOpened()[1:]:
        lt = proj[1].thanLayerTree
        for lay in lt.dilay.values():   #works for python2,3
            nam = "%s/%s" % (proj[0].namebase, lay.thanGetPathname())
            projlays[nam] = (proj, lay)
    names = sorted(projlays.keys())   #works for python2,3
    return names, projlays


def findPoints(lay):
    "Find and return named point of layer."
    cpref = {}
    dups = []
    for elem in lay.thanQuad:
        if not isinstance(elem, thandr.ThanPointNamed): continue
        if elem.name in cpref: dups.append(elem.name)
        cpref[elem.name] = elem
    return cpref, dups
