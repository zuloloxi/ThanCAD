# -*- coding: iso-8859-7 -*-

##############################################################################
# ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2013 Thanasis Stamos, March 25, 2013
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers

This module contains some routine to aid ThanCad with the tk library.
"""
import sys
from p_ggen import path

def deficon(win):
    "Decorates the window with the thancad icon."
    b = "@"+(path(sys.path[0])/"thancad24.xbm")
    try: win.iconbitmap(b)
    except: pass
