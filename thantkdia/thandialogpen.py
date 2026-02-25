##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module displays a dialog for the user to enter the draw the pen thickness
which the elements of a layer are plotted with.
"""


from Tkinter import *
from p_ggen import ThanStub as S
import p_gtkuti
import thanvar


class ThanPen(p_gtkuti.ThanDialog):
    "Dialog for the pen thickness which the elements of a layer are plotted with."

    def __init__(self, master, val, pentext, *args, **kw):
        "Extract initial pen thickenss."
	self.__val = str(val)
	self.pentext = pentext
	p_gtkuti.ThanDialog.__init__(self, master, *args, **kw)

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
	w = Label(f, text=" Special %s Thickenss" % self.pentext)
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
	w = Label(f, text="%s Thickenss (mm):"%self.pentext)
	w.grid(row=0, column=1, sticky="w")
	self.thanCol = Entry(f, width=12)
	self.thanCol.grid(row=0, column=2, sticky="w")
	self.__updateChosen(self.__val)
	del self.__val


    def __updateChosen(self, txtcol=None):
        "Updates the text with the chosen value."
	if txtcol == None: txtcol = self.thanCol.get()
	txtcol = txtcol.strip()
	try: thc = float(txtcol)
	except ValueError: thc = None
	if thc != None:
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
	if thc == None:
	    p_gtkuti.thanGudModalMessage(self, "Invalid ThanCad %s Thickenss"%self.pentext, "Error Message")
	    return False
	if thc in (thanvar.THANBYPARENT, thanvar.THANPERSONAL):
	    self.result = thc
	else:
	    self.result = thc
	return True

    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
	del self.thanCol
	p_gtkuti.ThanDialog.destroy(self)

    def __del__(self):
        print "ThanPen ThanDialog", self, "dies.."


if __name__ == "__main__":
    root = Tk()
    win = ThanPen(root, 0.25, "Pen", title="Choose ThanCad Pen Thickness")
    print win.result
