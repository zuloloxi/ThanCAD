# -*- coding: iso-8859-7 -*-

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

This module defines various functions in order to change the translation
on the fly.
"""

import p_ggen
from p_gtkwid import Twid
from thanopt import thancadconf
from thanengr import T
from thanmatch import Tmatch
from thanphot import Tphot
from thanarch import Tarch


def thanLangSet(lang=None):
    "Set translation language."
    if lang == None: lang = thancadconf.thanTranslateTo
    tenc = T.thanLangSet("en", lang)
    assert tenc != None, "Translation language %s not found" % lang
    p_ggen.thanSetEncoding(tenc)               #Encoding for non-unicode characters
    thancadconf.thanTranslateTo = lang
    for t in T, Tmatch, Tphot, Tarch, Twid:
        t.thanLangSet("en", lang)


thanLangSet()
