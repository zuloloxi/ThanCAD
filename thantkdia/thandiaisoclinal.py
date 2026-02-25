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

This dialog asks for the isoclinal line parameters, road design.
"""

#The following commented out import is in order for the test1() function
#to work as standalone.
#import sys
#sys.path.append("/home/a12/h/b/cad/thancad/work/tcadtree070")
#import thanopt             # This runs a test for the needed modules automatically
#thanopt.thanInitPregui()


from math import pi
import tkinter
import p_gtkwid, p_ggen
from thandefs import ThanDimstyle
from thantrans import T
from thanvar import Canc


class ThanDialogIsoclinal(p_gtkwid.ThanComDialog):
    "Dialog for the dimension style parameters."

    def __init__(self, *args, **kw):
        "Just set the title."
        proj = kw["cargo"]
        kw.setdefault("title", "%s - %s" % (proj[0].name, T["Isoclinal Parameters"]))
        vals = kw["vals"]
        if vals is not None:
            vals = vals.clone()
            vals.entAngle = proj[1].thanUnits.rad2unit(vals.entAngle)
            kw["vals"] = vals
        super().__init__(*args, **kw)


    #    s.entName = self.thanName
    #    s.entDesc = self.thanDesc
    #    s.choNdigits  = self.thanDigits    #decimal digits: "2"
    #    s.entTextsize = self.thanTextsize
    #    s.choTicktype = self.thanTicktypes.index(self.thanTicktype)
    #    s.entTicksize = self.thanTicksize

    def thanValsDef(self):
        "Build default values."
        s = p_ggen.Struct("Isoclinal settings")
        s.labLaynames  = "0"
        s.entEps       = 60.0     # user data units
        s.entAngle     = pi*0.5   # rad
        s.entStart     =  1.0     # (%)
        s.entEnd       =  7.0     # (%)
        s.entStep      =  0.1     # (%)
        s.entAngle     = self.thanProj[1].thanUnits.rad2unit(s.entAngle)
        return s


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraContour(  win, 0, 0)
        self.fraIsoclinal(win, 1, 0)
        self.fraGrade(    win, 2, 0)


    def fraContour(self, win, irfra, icfra):
        "Widgets for contour lines' layers' selection."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=irfra, column=icfra, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)

        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["CONTOUR LAYERS:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        lab = tkinter.Label(fra, text=T["Select the layers which contain the contour lines"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        key = "labLaynames"
        tit = "Layer names"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanLabel(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))

        ir += 1
        but = p_gtkwid.ThanButton(fra, text=T["Select new layers"], command=self.__butnew)
        but.grid(row=ir, column=2, sticky="w")


    def __butnew(self):
        "Let the user select new layers for the contour lines."
        res = self.thanProj[2].thanGudGetLayerleafs(T["Select layer(s)"])
        if res == Canc: return
        names = [lay.thanGetPathname() for lay in res]
        t = ", ".join(names)
        self.labLaynames.thanSet(t)


    def fraGrade(self, win, irfra, icfra):
        "Widgets for grade search parameters."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=irfra, column=icfra, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)

        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["GRADE SEARCH:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        lab = tkinter.Label(fra, text=T["ThanCad will try grades according to the following parameters:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        key = "entStart"
        tit = "Grade search start"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1e-6, 1e6)
        self.thanWids.append((key, T[tit], wid, val))

        ir += 1
        key = "entEnd"
        tit = "Grade search end"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, T[tit], wid, val))

        ir += 1
        key = "entStep"
        tit = "Grade search step"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, T[tit], wid, val))


    def fraIsoclinal(self, win, irfra, icfra):
        "Widgets for isoclinal parameters."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=irfra, column=icfra, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)

        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["ISOCLINAL PARAMETERS:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        key = "entEps"
        tit = "Distance tolerance\nto target"
        lab = tkinter.Label(fra, anchor="e", text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e15)
        self.thanWids.append((key, T[tit], wid, val))

        un = self.thanProj[1].thanUnits

        ir += 1
        key = "entAngle"
        tit = "Max allowed\ndirection change\nbetween segments ({})".format(un.anglunit)
        lab = tkinter.Label(fra, anchor="e", text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, un.rad2unit(pi)*0.99)
        self.thanWids.append((key, T[tit], wid, val))

    def apply(self):
        "Correct the angle to radians."
        if self.result is not None:
            self.result.entAngle = self.thanProj[1].thanUnits.unit2rad(self.result.entAngle)
        super().apply()


def test1():
    "Test the dialogs."
    root = tkinter.Tk()
    proj = [ p_ggen.path("xxxx"), p_ggen.Struct(), root]
    dia = ThanDialogIsoclinal(root, cargo=proj)
    r = dia.result
    if r is None: print(r)
    else: print(r.anal())
#    root.mainloop()

if __name__ == "__main__":
    test1()
