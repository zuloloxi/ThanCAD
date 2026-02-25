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

This module contains some routine to aid ThanCad with the tk library.
"""
import sys
from tkinter import font
from p_ggen import path
from thanopt import thancadconf


def deficon(win):
    "Decorates the window with the thancad icon."
    b = "@"+(path(sys.path[0])/"thancad24.xbm")
    try: win.iconbitmap(b)
    except: pass


thanFonts = []
def createTags(wids=()):
    "Create standard tags and fonts in the text widgets."
    if not thanFonts:
        font1 = font.Font(family=thancadconf.thanFontfamilymono,
                          size=thancadconf.thanFontsizemono)      # Negative size means size in pixels
        font2 = font1.copy()
        font2.config(weight=font.BOLD)
        font3 = font2.copy()
        font3.config(size=thancadconf.thanFontsizemono+2)           # Negative size means size in pixels
        thanFonts[:] = font1, font2, font3
    else:
        font1, font2, font3 = thanFonts
    col = "#%2xd%2xd%2xd" % (66, 182, 33)
    for wid in wids:
        wid.config(font=font1)
        wid.tag_config("mes",   foreground="blue",      font=font2)
        wid.tag_config("com",   foreground="darkcyan",  font=font2)
        wid.tag_config("can",   foreground="darkred",   font=font2)
        wid.tag_config("can1",  foreground="darkred",   font=font1)
        wid.tag_config("info",  foreground="darkgreen", font=font2)
        wid.tag_config("info1", foreground="darkgreen", font=font1)
        wid.tag_config("thancad", foreground="white", background=col, font=font3)
