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

This module displays a dialog for the user to enter object snap values.
It also has the routine to get the osnap values from the config files.
"""

from tkinter import Tk, Frame, Button, Label, Canvas, Checkbutton, IntVar, NORMAL, ACTIVE, GROOVE
import p_ggen, p_gtkwid
from thanopt import thancadconf
from thandefs.thanatt import ThanAttCol
from thanvar import thanimag
from thantrans import T
S = p_ggen.ThanStub

#############################################################################
#############################################################################

class ThanTkOsnap(p_gtkwid.ThanDialog):
    "Dialog for object snap settings."

    def __init__(self, master, val, BOSN, *args, **kw):
        "Extract initial drafting settings."
        self.__val = str(val)
        self.BOSN = BOSN
        p_gtkwid.ThanDialog.__init__(self, master, *args, **kw)

    def body(self, fra):
        "Create dialog widgets."
        self.__objectChooser(fra, 0, 0)
        f = self.__osnapTab(fra, 1, 0)
        self.__tabObj = (f, f, f)
        self.thanOsnapValSet(self.__val)
        del self.__val
        self.__selObj(2)

    def __objectChooser(self, fra, ir, ic):
        "Shows common colors."
        f = Frame(fra, bd=2, relief=GROOVE); f.grid(row=ir, column=ic, sticky="we", ipady=4, pady=4)
        f.columnconfigure(10, weight=1)
        w = Frame(f, width=5); w.grid(row=0, column=0)
        self.__butObj = [None]*3
        for i,t in enumerate(("Snap and Grid", "Polar Tracking", "Object Snap")):
            self.__butObj[i] = Button(f, text=t,  command=S(self.__selObj, i))
            self.__butObj[i].grid(row=0, column=i+1)

        self.__ibutObj = -1
        w = Frame(f); w.grid(row=0, column=4)

    def __selObj(self, i):
        "Selects the object tab to show on the window."
        if self.__ibutObj != -1:
            j = self.__ibutObj
            if j == i: return
            self.__butObj[j].config(default=NORMAL)
            self.__tabObj[j].grid_forget()
        self.__butObj[i].config(default=ACTIVE)
        self.__tabObj[i].grid(row=1, column=0, sticky="we", ipady=4, pady=4)
        self.__ibutObj = i

    def __osnapTab(self, fra, ir, ic):
        "Shows drafting settings."
        modescol = 7               # number of modes per column
        f = Frame(fra, bd=2, relief=GROOVE)
        f.columnconfigure(3, weight=1)
        w = Frame(f, width=5); w.grid(row=0, column=0)
        w = Label(f, text=" Object Snap Modes")
        w.grid(row=0, column=1, columnspan=4, sticky="w")

        but = p_gtkwid.ThanButtonIm(f, image=thanimag.ntuabig3(), title=T["National Technical University of Athens"],
            url="www.ntua.gr/en", iconsize=(480,360))
#        but = p_gtkwid.ThanButtonIm(f, image=thanimag.hannover_leibniz(), title=T["Leibniz Universitaet Hannover"],
#            url="www.uni-hannover.de/en", iconsize=(480,360))
#        but = p_gtkwid.ThanButtonIm(f, image=thanimag.valencia_uni(), title=T["La Universitat de Valencia"],
#            url="www.uv.es/uvweb/college/en/university-valencia-1285845048380.html", iconsize=(480,360))
#        but = p_gtkwid.ThanButtonIm(f, image=thanimag.oberpfaffenhofen_esa(), title=T["Columbus-Kontrollzentrum, Oberpfaffenhofen"],
#            url="http://www.esa.int/ger/ESA_in_your_country/Germany/Columbus-Kontrollzentrum_Oberpfaffenhofen_Deutschland", iconsize=(480,360))
#        im = thanimag.prague_congress_center()
#        print("__osnapTab():im=",im)
#        but = p_gtkwid.ThanButtonIm(f, image=thanimag.prague_congress_center(), title=T["Congress center, Prague"],
#            url="http://www.kcp.cz/en/homepage", iconsize=(480,360))
        but.grid(row=1, column=3, rowspan=modescol, padx=5, pady=5)

        w = Frame(f, width=5); w.grid(row=0, column=7)

        self.__osnapVal = []
        #bgc = ThanAttCol((0,50,0)).thanTk
        #bgc = ThanAttCol((0,75,0)).thanTk
        bgc = thancadconf.thanColBack
        for i,(mode,t) in enumerate(thancadconf.thanOsnapModesText):
            if mode == "ena":                          # Enabled is not really a mode
                ii = -1; j = 1
            else:
                if i >= modescol: j=3; ii = i-modescol
                else: j = 0; ii = i
                w = Canvas(f, width=28, height=28, bg=bgc)
                w.grid(row=ii+1, column=j+1, pady=4, sticky="w")
                self.__drawMode(w, mode)
            self.__osnapVal.append(IntVar())
            w = p_gtkwid.ThanCheck(f, text=t, variable=self.__osnapVal[i])
            #bgcol = w.cget("background")
            #print("bgcol=", bgcol)
            #w.config(selectcolor=bgcol)
            #print("checkbutton:",); p_gtkwid.correctForeground(w)
            w.grid(row=ii+1, column=j+2, sticky="w")

        w = Button(f, text="Select All", command=self.__selectAll)
        w.grid(row=1, column=6, sticky="we")
        w = Button(f, text="Clear All", command=self.__clearAll)
        w.grid(row=2, column=6, sticky="we")
        return f


    def __drawMode(self, dc, t):
        "Draws the symbol of mode."
        x = 14; y = 14
        b = h = self.BOSN/2
        tcol = ThanAttCol(thancadconf.thanColOsn).thanTk
        if t == "end":
            items = \
            ( dc.create_rectangle(x-b, y-h, x+b, y+h, width=3, outline=tcol, fill=""),
            )
        elif t == "mid":
            items = \
            ( dc.create_polygon(x-b, y-b, x+b, y-b, x, y+b, width=3, outline=tcol, fill=""),
            )
        elif t == "cen":
            items = \
            ( dc.create_oval(x-b, y-b, x+b, y+b, width=3, outline=tcol, fill=""),
            )
        elif t == "nod":
            items = \
            ( dc.create_oval(x-b, y-b, x+b, y+b, width=3, outline=tcol, fill=""),
              dc.create_line(x-b, y-b, x+b, y+b, width=2, fill=tcol),
              dc.create_line(x-b, y+b, x+b, y-b, width=2, fill=tcol),
            )
        elif t == "qua":
            items = \
            ( dc.create_polygon(x-b,y, x,y+b, x+b,y, x,y-b, width=2, outline=tcol, fill=""),
            )
        elif t == "int":
            items = \
            ( dc.create_line(x-b, y-b, x+b, y+b, width=2, fill=tcol),
              dc.create_line(x-b, y+b, x+b, y-b, width=2, fill=tcol),
            )
        elif t == "tan":
            bb = 0.8*b
            items = \
            ( dc.create_oval(x-bb, y-bb, x+bb, y+bb, width=3, outline=tcol, fill=""),
              dc.create_line(x-b, y-b, x+b, y-b, width=2, fill=tcol),
            )
        elif t == "nea":
            items = \
            ( dc.create_polygon(x-b, y-b, x+b, y+b, x-b, y+b, x+b, y-b, width=2, outline=tcol, fill=""),
            )
        elif t == "per":
            items = \
            ( dc.create_line(x-b, y-b, x-b, y+b, x+b, y+b, width=3, fill=tcol),
              dc.create_line(x-b, y, x, y, x, y+b, width=2, fill=tcol),
            )

    def __selectAll(self):
        "Sets all modes on."
        for iv in self.__osnapVal: iv.set(True)

    def __clearAll(self):
        "Sets all modes off."
        for iv in self.__osnapVal: iv.set(False)

    def thanOsnapValSet(self, modes):
        "Set the values of widgets according to dict modes."
        for iv in self.__osnapVal: iv.set(False)
        for i,(mode,t) in enumerate(thancadconf.thanOsnapModesText):
            if mode in modes: self.__osnapVal[i].set(True)

    def thanOsnapValGet(self):
        "Get the modes checked in the widgets."
        modes = {}
        for i,(mode,t) in enumerate(thancadconf.thanOsnapModesText):
            if self.__osnapVal[i].get(): modes[mode] = True
        return modes

    def validate(self):
        self.result = self.thanOsnapValGet()
        return True

    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
        del self.__tabObj, self.__butObj, self.__osnapVal
        p_gtkwid.ThanDialog.destroy(self)

    def __del__(self):
        print("ThanOsnap ThanDialog", self, "dies..")


if __name__ == "__main__":
    root = Tk()
    o = {"mid":1}
    a = ThanTkOsnap(root, o, title="Drafting Settings")
    print(a.result)
    del a
    print("The End.")
