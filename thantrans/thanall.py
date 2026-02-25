# -*- coding: iso-8859-7 -*-

##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

This module defines various functions in order to change the translation
on the fly.
"""

import p_ggen
from p_gtkwid import Twid
from thanopt import thancadconf
from thanopt.thancon import thanFrape
from thanengr import T
from thanmatch import Tmatch
from thanphot import Tphot
from thanarch import Tarch
from thancivil import Tcivil
Turban = p_ggen.Translation()
#thanTransAll = [T, Tmatch, Tphot, Tarch, Tcivil, Twid]
thanTransAll = dict(T=T, Tmatch=Tmatch, Tphot=Tphot, Tarch=Tarch, Tcivil=Tcivil, Twid=Twid)


def thanLangSet(lang=None):
    "Set translation language."
    import p_ggen
    from thanopt import thancadconf
    if lang == None: lang = thancadconf.thanTranslateTo
    tenc = T.thanLangSet("en", lang)
    assert tenc != None, "Translation language %s not found" % lang
    p_ggen.thanSetEncoding(tenc)               #Encoding for non-unicode characters
    thancadconf.thanTranslateTo = lang
    for t in thanTransAll.itervalues():
        t.thanLangSet("en", lang)


def thanLangMore():
    "Add more translations."
    import sys
    if thanFrape.urban:
        from thanpackages.urban.thantrans.urbantrans import Turban as x
        Turban.__init__(*x.thanTables)
        thanTransAll["Turban"] = Turban
    thanLangSet()

thanLangSet()
