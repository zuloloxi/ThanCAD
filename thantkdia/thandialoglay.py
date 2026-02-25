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

This module displays a dialog which shows all the layers and their attributes.
It lets the user edit the layers.
"""

import p_gtkwid
from thantrans import T

class ThanDialogLay(p_gtkwid.ThanDialog):
    "Displays a popup window with a list of choices; cancel/ok buttons are not required."


    def __init__(self, master,
                 objs, current, atts, cargo, widths, height, vscroll, hscroll, onclick,
                 *args, **kw):
        "Prepare the dialog."
        self.__val = dict(objs=objs, current=current, hlen=90, atts=atts, cargo=cargo, widths=widths,
                          height=height, vscroll=vscroll, hscroll=hscroll, onclick=onclick)
        p_gtkwid.ThanDialog.__init__(self, master, *args, **kw)


    def body(self, fra):
        "Create dialog widgets - Creates and shows list."
        fra.columnconfigure(0, weight=1)
        fra.rowconfigure(0, weight=1)
        self.__li = p_gtkwid.ThantkClist6(self, **self.__val)
        self.__li.grid(row=0, column=0, sticky="wesn")
        del self.__val
        return self.__li                      # This widget has the focus


    def cancel(self, *args):
        "What to do when user cancels."
        if self.__li.thanModified:
            ok = p_gtkwid.thanGudAskOkCancel(self,
            message=T["The layer hierarchy has been modified\nAbandon changes?"],
            title=T["Layers modified"])
            if not ok: return "break"
        p_gtkwid.ThanDialog.cancel(self, *args)


    def ok(self, *args):
        "What to do when user OKs."
        if self.__li.thanClipMovePending(): return "break"
        self.result = self.__li.thanLeaflayers, self.__li.thanCur
        self.__li.thanModified = False
        p_gtkwid.ThanDialog.ok(self, *args)


    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
        self.__li.destroy()
        del self.__li
        p_gtkwid.ThanDialog.destroy(self)


    def __del__(self):
        print("ThanDialogLay ThanDialog", self, "dies..")
