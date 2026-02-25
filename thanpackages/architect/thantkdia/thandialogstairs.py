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

The package creates automatically architectural things such as stairs.
The subpackage contains the dialogs which handle architecture related
procedures.
This module contains the dialog which asks for the stairs settings.
"""

import tkinter
import p_gtkwid, p_ggen
from thantrans import Tarch
Twid = p_gtkwid.Twid


class ThanStairsSettings(p_gtkwid.ThanComDialog):
    "Dialog for the line simlification algorithm."

    def __init__(self, *args, **kw):
        "Just set the title."
        proj = kw["cargo"]
        kw.setdefault("title", "%s - %s" % (proj[0].name, Tarch["Stair case settings"]))
        kw.setdefault("buttonlabels", (Twid["OK"], Tarch["Compute"], Twid["Cancel"]))
        p_gtkwid.ThanComDialog.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        return thanValsDef()


    def body(self, win):
        "Just add compute at the end."
        p_gtkwid.ThanComDialog.body(self, win)
        self.apply2()


    def body2(self, win):
        "Create the body of the dialog in steps."
        win.columnconfigure(1, weight=1)
        self.fraSpec(win, 1)
        self.fraGeom(win, 2)
        self.fraScale(win, 3)


    def fraSpec(self, win, ir):
        "Widgets for stairs settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tarch["STAIRS SPECIFICATIONS:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        key = "entTread"
        tit = "Step tread"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=8)
        wid.grid(row=1, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, Tarch[tit], wid, val))

        key = "entRise"
        tit = "Step rise"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=8)
        wid.grid(row=2, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, Tarch[tit], wid, val))

        key = "entWidth"
        tit = "Stairs width"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=3, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=8)
        wid.grid(row=3, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, Tarch[tit], wid, val))
        fra.columnconfigure(2, weight=1)

        key = "entTotalrise"
        tit = "Stairs total rise"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=4, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=8)
        wid.grid(row=4, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, Tarch[tit], wid, val))
        fra.columnconfigure(2, weight=1)


    def fraGeom(self, win, ir):
        "Widgets for computed stairs settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-2, column=1, pady=5, sticky="wesn")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tarch["STAIRS COMPUTED GEOMETRY:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        key = "labRise"
        tit = "Actual step rise"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanLabel(fra, width=8)
        wid.grid(row=1, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tarch[tit], wid, val))

        key = "labRun"                              #Μήκος σκάλας από πρώτο ως τελευταίο ρίχτι
        tit = "Stairs run"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanLabel(fra, width=8)
        wid.grid(row=2, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tarch[tit], wid, val))
        fra.columnconfigure(2, weight=1)

        key = "labNtreads"
        tit = "Number of treads"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=3, column=1, sticky="e")
        wid = p_gtkwid.ThanLabel(fra, width=8)
        wid.grid(row=3, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tarch[tit], wid, val))
        fra.columnconfigure(2, weight=1)

        key = "labNrises"
        tit = "Number of rises"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=4, column=1, sticky="e")
        wid = p_gtkwid.ThanLabel(fra, width=8)
        wid.grid(row=4, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, Tarch[tit], wid, val))
        fra.columnconfigure(2, weight=1)


    def fraScale(self, win, ir):
        "Widgets for print scale."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-2, column=0, pady=5, sticky="wesn")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tarch["PRINT SCALE:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        key = "entScale"
        tit = "Print scale 1/"
        lab = tkinter.Label(fra, text=Tarch[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra, width=8)
        wid.grid(row=1, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-9, 1.0e9)
        self.thanWids.append((key, Tarch[tit], wid, val))
        fra.columnconfigure(2, weight=1)


    def apply2(self, *args):
        "The second of 3 buttons was pressed; just validate."
        if not p_gtkwid.ThanDialog.apply2(self): return
        r = self.result
        thanCompute(r)
        self.labNrises.thanSet(int(r.labNrises))
        self.labRise.thanSet("%.3f" % (r.labRise,))
        self.labRun.thanSet("%.3f" % (r.labRun,))
        self.labNtreads.thanSet(int(r.labNtreads))


def thanCompute(r):
    "Compute actual geometry."
    r.labNrises = round(r.entTotalrise/r.entRise)
    r.labRise = r.entTotalrise/r.labNrises
    r.labRun = r.entTread*(r.labNrises-1)
    r.labNtreads = r.labNrises-1


def thanValsDef():
    "Build default values."
    s = p_ggen.Struct("Stair case settings")
    s.entTread = 0.30           #Πάτημα
    s.entRise  = 0.17           #Ρίχτι
    s.entTotalrise  = 3.0       #Ύψος σκάλας
    s.entWidth = 1.20           #Πλάτος σκάλας
    s.entScale = 100.0

    s.labRise = ""
    s.labRun  = ""              #Μήκος σκάλας από πρώτο ως τελευταίο ρίχτι
    s.labNtreads = ""
    s.labNrises = ""
    return s


def test1():
    root = tkinter.Tk()
    proj = [ p_ggen.path("xxxx"), None, root]
    dia = ThanStairsSettings(root, cargo=proj)
#    root.mainloop()

if __name__ == "__main__": test1()
