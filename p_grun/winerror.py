# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.1.2 "Free": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2010 Thanasis Stamos,  December 23, 2010
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
ThanCad 0.1.2 "Free": 2dimensional CAD with raster support for engineers.

This module defines a separate windows which shows active error messages. In the
future, if the user doubleclicks an error message, appropriate action will be
carried out, to correct the error (with the user's help).
"""
import Tkinter
import p_gtkwid, p_gtkuti, p_ggen


class ThanTkWinError(Tkinter.Toplevel, p_gtkuti.ThanFontResize):
    "A window with active error messages."

    def __init__(self, master, mes="", title="", modal=False, hbar=0, vbar=1, width=80, height=25,
        font=None, background="lightyellow", foreground="black"):
        "Create the Information window."
        Tkinter.Toplevel.__init__(self, master)
        self.thanResizeFont(font)
        if modal: thanGrabSet(self)
        self.title(title)
        self.thanTxtHelp = p_gtkwid.ThanScrolledText(self, readonly=True, hbar=hbar, vbar=vbar,
            background=background, foreground=foreground, width=width, height=height)

        self.thanResizeBind([self.thanTxtHelp])
        self.protocol("WM_DELETE_WINDOW", self.destroy) # In case user closes window with window manager

        self.thanAppend(mes)
        self.thanTxtHelp.grid(sticky="wesn")
        self.thanTxtHelp.tag_config("mes", foreground="blue")
        self.thanTxtHelp.tag_config("err", foreground="darkred")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.thanTkSetFocus()


    def thanAppend(self, *args, **kw):
        "Print test to the end of the window suppressing final new line."
        self.thanTxtHelp.thanAppend(*args, **kw)


    def thanPrt(self, mes, *args, **kw):
        "Print text to the window and append a final new line."
        self.thanTxtHelp.thanAppend(mes, *args, **kw)
        self.thanTxtHelp.thanAppend("\n")


    def thanPrts(self, mes, *args, **kw):
        "Print text to the window suppressing final new line."
        self.thanTxtHelp.thanAppend(mes, *args, **kw)


    def thanTkSetFocus(self):
        "Sets focus to the text widget."
        self.lift()
        self.focus_set()
        self.thanTxtHelp.focus_set()


    def destroy(self):
        "Erases circular dependencies."
        del self.thanTxtHelp
        p_gtkuti.ThanFontResize.thanDestroy(self)
        Tkinter.Toplevel.destroy(self)


    def __del__(self):
        "For debugging reasons, inform that the window releases its memory."
        print "ThanTkWinError", self, "dies.."


class ThanShellError:
    "Emulates the window with active error messages in shell mode."
    def __init__(self, master=None, mes="", **kw):
        self.thanPrt = p_ggen.prg
        self.thanPrts = p_ggen.prints
        self.update_idletasks = lambda: None
        self.thanPrts(mes)


def test():
    root = Tkinter.Tk()
    e = ThanTkWinError(root, "xxxx", "dokimi")
    e.thanAppend("\n\nAndreas\tStella\n")
    e.thanAppend("\tChildren\n")
    e.thanAppend("Warning:\txxx\n")
    e.thanAppend("\tyyy\n")

    e.thanAppend("\n\nΑνδρέας\tΣτέλλα\n")
    e.thanAppend("\tΠαιδιά")
    e.thanAppend(u"\n\nΑνδρέας\tΣτέλλα\n")
    e.thanAppend(u"\tΠαιδιά")
    del e
    root.mainloop()


if __name__ == "__main__": 
    print __doc__
    test()
