# -*- coding: iso-8859-7 -*-

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

This module implements an information status bar.
"""
from tkinter import Frame, Label, SUNKEN, W, E
from p_ggen import prg
from thantrans import T

class ThanStatusBar(Frame):
    "Implements a status bar."

    def __init__(self, master, **kw):
        "Initialise base classes and create status bar (as a label)."
        self.__proj = None
        Frame.__init__(self, master, **kw)
        self.thanTypeCoor = Label(self, text=T["World xyz"]+":", anchor=E, width=10)
        self.thanTypeCoor.grid(row=0, column=0, sticky="e")
        self.thanCoor = Label(self, text="", bd=1, relief=SUNKEN, anchor=W, width=30)
        self.thanCoor.grid(row=0, column=1, sticky="w")
        self.thanInfo = Label(self, text="This is ThanCad", bd=1, relief=SUNKEN, anchor=W, width=20)
        self.thanInfo.grid(row=0, column=2, sticky="we")
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self.__info = [""]
        self.__cp = None


    def setProj(self, proj):
        "Set an associated ThanCad project to the widget."
        self.__proj = proj
        self.strcoo = self.__proj[1].thanUnits.strcoo
        self.thanConfig(typ="world", every="click")


    def __coorNone(self, cp):
        "Do not display anything into the coordinate widget."
        self.__cp = tuple(cp)


    def __coorWorld(self, cp):
        "Display mouse world coordinates into the coordinate widget."
        self.__cp = tuple(cp)
        self.thanCoor.config(text=self.strcoo(cp))
        if self.__curType != "w":
            self.thanTypeCoor.config(text=T["World xyz"]+":", width=10, fg="black")
            self.thanCoor.config(fg="black")
            self.thanInfo.config(text=self.__info[-1])
            self.__curType = "w"
        self.thanCoor.update_idletasks()


    def __coorNoncart(self, cp):
        "Display mouse non-Cartesian coordinates."
        self.__cp = tuple(cp)
        cosyses = self.__proj[1].thanObjects["COSYS"]
        if len(cosyses) > 0:
            cosys = cosyses[0]
            px, py, _ = cosys.project(cp)
            self.thanCoor.config(text=self.strcoo(cp))
            self.thanCoor.config(text="%.3f %.3f" % (px, py))
            if self.__curType != "i":
                s = T["Image xy (mm)"]+":"
                self.thanTypeCoor.config(text=s, width=len(s), fg="darkgreen")
                self.thanCoor.config(fg="darkgreen")
                self.thanInfo.config(text=self.__info[-1])
                self.__curType = "i"
            return
        self.__coorWorld(cp)         #Non-cartesian system not defined: display world coordinates


    def __coorImage(self, cp):
        "Display image coordinates into the coordinate widget."
        self.__cp = tuple(cp)
        for im in self.__proj[2].thanImages:
            try:               px, py = im.thanGetPixCoor(cp) #Clipped image coordinates
            except IndexError: continue
            px, py = im.thanGetPixCoorori(cp)                 #Full image coordinates
            self.thanCoor.config(text="%d %d" % (px, py))
            if True:             #Force redrawing of the type (because the image may have changed)
                s = T["Pixel xy"]+":"
                self.thanTypeCoor.config(text=s, width=len(s), fg="blue")
                self.thanCoor.config(fg="blue")
                self.thanInfo.config(text=im.filnam)
                self.__curType = "p"
            self.thanCoor.update_idletasks()
            return
        self.__coorWorld(cp)         #No image was found: display world coordinates


    def thanConfig(self, typ=None, every=None):
        """Set what type of coordinates we show, and when do we show these coordinates.

        typ may be:   world, image, or pixel
        every may be: click, or move (that is the coors are updated for every move or click of the mouse)
        """
        if typ   is not None: self.__typ = typ[0]
        if every is not None: self.__every = every[0]

        self.__curType = None
        if self.__typ == "w":
            self.thanCoorClick = self.__coorWorld
            if self.__every == "m": self.thanCoorMouse = self.__coorWorld
            else:                   self.thanCoorMouse = self.__coorNone
        elif self.__typ == "i":
            self.thanCoorClick = self.__coorNoncart
            if self.__every == "m": self.thanCoorMouse = self.__coorNoncart
            else:                   self.thanCoorMouse = self.__coorNone
        else:
            self.thanCoorClick = self.__coorImage
            if self.__every == "m": self.thanCoorMouse = self.__coorImage
            else:                   self.thanCoorMouse = self.__coorNone


    def thanToggleCoordTyp(self, evt=None):
        "Toggle among world, internal orientation and pixel coordinates."
        if   self.__typ == "w": typ1 = "image"
        elif self.__typ == "i": typ1 = "pixel"
        else:                   typ1 = "world"
        if typ1[0] == "i" and len(self.__proj[1].thanObjects["COSYS"]) == 0:
            typ1 = "pixel" #Ignore internal orientation if it does not exist
        self.thanConfig(typ1)
        if self.__cp is not None: self.thanCoorClick(self.__cp)
        return typ1


    def thanToggleCoordUpdate(self, evt=None):
        "Toggle between auto-update on and off."
        if self.__every == "c": every1 = "move"
        else:                   every1 = "click"
        self.thanConfig(every=every1)
        return every1

    def thanInfoSet(self, text):
        "Sets a new message to the info label overwritting current."
        self.__info[-1] = text
        self.thanInfo.config(text=text)
        self.thanInfo.update_idletasks()

    def thanInfoPush(self, text):
        "Pushes a new message to the info label."
        self.__info.append(text)
        self.thanInfo.config(text=text)
        self.thanInfo.update_idletasks()


    def thanInfoPop(self):
        "Pushes a new message to the info label."
        if len(self.__info) > 1: del self.__info[-1]
        self.thanInfo.config(text=self.__info[-1])
        self.thanInfo.update_idletasks()


    def thanClear(self):
        "Clears the info label."
        del self.__info[1:]
        self.__info[-1] = ""
        self.thanInfo.config(text="")
        self.thanInfo.update_idletasks()


    def destroy(self):
        "Deletes circular references."
        del self.__proj, self.thanTypeCoor, self.thanCoor, self.thanInfo
        del self.thanCoorMouse, self.thanCoorClick, self.strcoo
        Frame.destroy(self)


def test():
    "Tests status bar."
    from tkinter import Tk
    root = Tk()
    sb = ThanStatusBar(root, ())
    sb.grid()
    root.mainloop()

if __name__ == "__main__":
    prg(__doc__)
    test()
