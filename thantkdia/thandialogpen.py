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

This module displays a dialog for the user to enter the draw the pen thickness
which the elements of a layer are plotted with.
"""

from tkinter import Tk, Frame, Label, Button, Entry, GROOVE, END
from p_ggen import ThanStub as S
import p_gtkwid
import thanvar


class ThanPen(p_gtkwid.ThanDialog):
    "Dialog for the pen thickness which the elements of a layer are plotted with."

    def __init__(self, master, val, pentext, penunit, *args, **kw):
        "Extract initial pen thickness."
        self.__val = str(val)
        self.pentext = pentext
        self.penunit = penunit
        p_gtkwid.ThanDialog.__init__(self, master, *args, **kw)

    def body(self, fra):
        "Create dialog widgets."
        self.__specialVals(fra, 0, 0)
        self.__chosenValue(fra, 1, 0)
        self.thanCol.select_range(0, END)
        return self.thanCol                      # This widget has the focus


    def __specialVals(self, fra, ir, ic):
        "Shows special values."
        f = Frame(fra, bd=2, relief=GROOVE); f.grid(row=ir, column=ic, sticky="esn", ipady=4)
        f.columnconfigure(0, weight=1); f.columnconfigure(1, weight=1)
        w = Frame(f, width=5); w.grid(row=0, column=0)
        w = Label(f, text=" Special %s Thickness" % self.pentext)
        w.grid(row=0, column=1, columnspan=2, sticky="w")
        w = Frame(f, width=5); w.grid(row=0, column=3)

        but = Button(f, text=str(thanvar.THANBYPARENT), bg="gold", activebackground="yellow",
            command=S(self.__updateChosen, str(thanvar.THANBYPARENT)))
        but.grid(row=1, column=1, sticky="we", padx=5)
        but = Button(f, text=str(thanvar.THANPERSONAL), bg="darkcyan", activebackground="cyan",
            command=S(self.__updateChosen, str(thanvar.THANPERSONAL)))
        but.grid(row=1, column=2, sticky="we", padx=5)


    def __chosenValue(self, fra, ir, ic):
        "Shows the chosen value."
        f = Frame(fra, bd=0, relief=GROOVE); f.grid(row=ir, column=ic, sticky="we", ipady=4, pady=4)
        f.columnconfigure(10, weight=1)
        w = Label(f, text="%s Thickness (%s):"%(self.pentext, self.penunit))
        w.grid(row=0, column=1, sticky="w")
        self.thanCol = Entry(f, width=12)
        self.thanCol.grid(row=0, column=2, sticky="w")
        self.__updateChosen(self.__val)
        del self.__val


    def __updateChosen(self, txtcol=None):
        "Updates the text with the chosen value."
        if txtcol is None: txtcol = self.thanCol.get()
        txtcol = txtcol.strip()
        try: thc = float(txtcol)
        except ValueError: thc = None
        if thc is not None:
            txtcol = str(thc)
        elif txtcol == str(thanvar.THANBYPARENT):
            thc = thanvar.THANBYPARENT
        elif txtcol == str(thanvar.THANPERSONAL):
            thc = thanvar.THANPERSONAL
        else:
            pass
        self.thanCol.delete(0, END)
        self.thanCol.insert(0, txtcol)
        return thc

    def validate(self):
        "Returns true if the value chosen by the user is valid."
        thc = self.__updateChosen()
        if thc is None:
            p_gtkwid.thanGudModalMessage(self, "Invalid ThanCad %s Thickness"%self.pentext, "Error Message")
            return False
        if thc in (thanvar.THANBYPARENT, thanvar.THANPERSONAL):
            self.result = thc
        else:
            self.result = thc
        return True

    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
        del self.thanCol
        p_gtkwid.ThanDialog.destroy(self)

    def __del__(self):
        print("ThanPen ThanDialog", self, "dies..")


if __name__ == "__main__":
    root = Tk()
    win = ThanPen(root, 0.25, "Pen", title="Choose ThanCad Pen Thickness")
    print(win.result)
