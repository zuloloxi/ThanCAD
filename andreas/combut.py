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

This package makes toolbars for ThanCad (in the future).
"""
import os
from tkinter import Frame, Button
from p_gtkwid import ThanToolButton, thanicon
from thantrans import T
#   circle


class Combut(Frame):

    def __init__(self, proj, *args, **kw):
        Frame.__init__(self, *args, **kw)
        self.proj = proj
        self.combut()
    def hh(self):
        self.commandAndreas("circle")
    def aa(self):
        self.commandAndreas("line")

    def bb(self):
        self.commandAndreas("point")

    def cc(self):
        os.system("firefox &")

    def __save(self):
        "Issue the save command."
        self.proj[2].thanGudCommandBegin("save")

    def combut(self):
        b = ThanToolButton(self, help=T["Circle"], text="circle",
            image=thanicon.get("circle2", foreground="blue"),
            bg="green", activebackground="lightgreen", command=self.hh)
        b.grid(row=0, sticky="we")
        b = ThanToolButton(self, help=T["Line"], text="line",
            image=thanicon.get("line1", foreground="yellow"),
            background="red", activebackground="pink", command=self.aa)
        b.grid(row=1, sticky="we")
        b = Button(self, text="point",   bg="blue",   fg="green",
        activebackground="lightblue", command=self.bb)
        b.grid(row=2, sticky="we")
        b = Button(self, text="firefox", bg="purple", fg="magenta",
            activebackground="pink", command=self.cc)
        b.grid(row=3, sticky="we")

        b = Button(self, text="", bg="purple", fg="magenta",
            activebackground="pink")
        b.grid(row=4, sticky="we")

        b = ThanToolButton(self, help=T["Save"], image=thanicon.get("floppy", foreground="blue"), bg="purple", fg="magenta",
            activebackground="pink", command=self.__save)
        b.grid(row=5, sticky="we")

        fra = Frame(self)
        fra.grid(row=4, sticky="wesn")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(6, weight=1)


    def commandAndreas(self, com):
        self.proj[2].thanTkSetFocus()
        self.proj[2].thanGudCommandBegin(com)


    def destroy(self):
        "Break circular references."
        del self.proj
        Frame.destroy(self)
