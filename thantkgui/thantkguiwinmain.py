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

This module defines a Tkinter window to display ThanCad's main window.
"""

import sys, weakref
import tkinter
import p_gtkwid, p_ggen
import thanvar, thancom
from thanvers import tcver
import thantk
from thanopt import thancadconf
from . import thanmenus
thanfiles = thanvar.thanfiles


class ThanTkGuiWinMain(tkinter.Tk):
    "Main window of tkinter GUI."

    def __init__ (self):
        "Initialise base classes and mixins and then this class."
        tkinter.Tk.__init__(self, className="ThanCad")

        self.__fonts()
        self.__position()
        self.__createControls()

        S = p_ggen.ThanStub; B = self.thanGudCommandBegin
        self.protocol("WM_DELETE_WINDOW", S(B, "quit")) # In case user closes ThanCad via window manager

        self.thanProj = (p_ggen.path("ThanCad"), None, self)  #Tuple, not list, because this is not going to change ever
        thanfiles.fillMenu(self.thanProj)
        thanfiles.addOpened(self.thanProj)                    #This is the first project (ThanCad)

        projnew = self.__fileNew()                      # Automatically create an empty drawing
        self.__openargs(projnew)                        # Open files given as arguments (if any)


    def __fileNew(self):
        "Creates a new drawing and its drawing window."
        from thancom.thancomvar import thanVarScriptDo
        from thancom.thancomfile import thanFileNewDo
        projnew = thanFileNewDo(self.thanProj)
        projnew[2].thanGudCommandEnd()

        fn, terr = p_ggen.configFile("thancad.scr", "thancad")
        if fn is None: return projnew
        try: fr = open(fn)
        except IOError: return  projnew
        thanVarScriptDo(projnew, fr)
        fr.close()
        return projnew
#       import thantest
#       thantest.thanTestCommands(thanfiles.ThanCad)


    def __openargs(self, proj):
        """Open files given as arguments (if any).

        If only 1 arguments is present and it is directory, set this directory as default."""
        from thancom.thancomfile import thanFileOpenPaths
        fns = sys.argv[1:]
        if len(fns) == 0: return
        if len(fns) == 1:
            dn = p_ggen.path(fns[0])
            if dn.isdir():
                thanfiles.setFiledir(dn)
                return
        nopened = thanFileOpenPaths(proj, fns)


    def __fonts(self):
        "Use fonts that support Greek encodings."
#       save thanFo reference. Note that p_gtkwid.thanFontRefSave() will not work well here (see source)
#       self.thanFo = tkinter.font.Font(family="Arial", size=10)          # Negative size means size in pixels; else in points
        self.thanFo = tkinter.font.Font(family=thancadconf.thanFontfamily,
                                        size=thancadconf.thanFontsize)          # Negative size means size in pixels; else in points
        self.option_add("*Font", self.thanFo)



    def __position(self):
        "Position main window at top left; Later, add code to remember the last ThanCad's position, size etc."
        xx = yy = 0
        self.thanTkPos = [(xx, yy, weakref.ref(self))]
        self.geometry("%+d%+d" % (50, 50))


    def __createControls(self):
        "Creates various controls and sets attributes."
        self.config(background="#%2xd%2xd%2xd" % (238, 92, 66))
        self.title(tcver.title)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.thanMenu = thanmenus.ThanCadTkMenu(self, main=True)
        self.thanCom = p_gtkwid.ThanScrolledText(self, width=40, height=2)
        self.thanCom.grid(sticky="swne")
        thantk.deficon(self)   # Decorates main window


    def thanGudCommandBegin(self, t):
        "The user entered a command; launch it."
        t = t.lower()
        c, fun = thancom.thanComFun(t)
        assert fun, "Unrecognised command"
        fun(thanfiles.ThanCad)


    def thanGudCommandEnd(self, t=None, mestype="can"):
        "After command is executed; not needed."
        pass


    def thanGudCommandCan(self):
        "After command is cancelled; not needed."
        pass

    def thanPrtCan(self):
        "Prints 'cancelled' to the command window."
#        from thanvar import DEFCAN
#        self.thanCom.thanAppend("%s\n" % DEFCAN, "can")
    def thanPrt(self, mes, tag="info1"):
        "Print to the command window; this is info, warnings, error etc."
#        self.thanCom.thanAppend("%s\n" % mes, tag)
    def thanPrtbo(self, mes, tag="info"):
        "Print to the command window; deault is bold info."
#        self.thanCom.thanAppend("%s\n" % mes, tag)
    def thanPrter(self, mes, tag="can"):
        "Print to the command window; default is bold error."
#        self.thanCom.thanAppend("%s\n" % mes, tag)
    def thanPrter1(self, mes, tag="can1"):
        "Print to the command window; default is bold error."
#        self.thanCom.thanAppend("%s\n" % mes, tag)


    def thanTkSetFocus(self):
        "Sets focus to itself."
        self.lift()
        self.focus_set()


    def destroy(self):
        "Deletes circular references."
        del self.thanFo, self.thanMenu, self.thanTkPos
        tkinter.Tk.destroy(self)
