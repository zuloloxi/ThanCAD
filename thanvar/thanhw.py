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

This module defines a small shortlived info window.
"""

from tkinter import Toplevel, Label, Tk
import p_gtkwid


class InfoWin(Toplevel):
    "Button to be used in toolbar and show help on button."
    def __init__(self, *args, **kw):
        helpt = kw.pop("help", "")
        pos = kw.pop("position", None)
        Toplevel.__init__(self, *args, **kw)
        self.__cron = None
        self.overrideredirect(True)
        self.withdraw()
        lab = p_gtkwid.ThanLabel(self, text=helpt, bg="lightyellow")
        lab.grid()
        self.bind("<ButtonPress>", self.destroy) # In case of bug we should be able to delete it
        if pos is None:
            par = self.master
            par.update()
            x = par.winfo_rootx() + 50
            y = par.winfo_rooty() + 50
            pos = x, y

        self.geometry("%+d%+d" % tuple(pos))
        self.deiconify()
        self.__cron = self.after(3000, self.destroy)

    def destroy(self, evt=None):
        Toplevel.destroy(self)


if __name__ == "__main__":
    root = Tk()
    w = InfoWin(root, help="hello")
    root.mainloop()
