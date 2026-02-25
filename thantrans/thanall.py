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

This module defines various functions in order to change the translation
on the fly.
"""

import p_ggen
from p_gtkwid import Twid
from thanopt import thancadconf
from thanopt.thancon import thanFrape
from .thanengr import T
from .thanmatch import Tmatch
from .thanphot import Tphot
from .thanarch import Tarch
from .thancivil import Tcivil
Turban = p_ggen.Translation()
#thanTransAll = [T, Tmatch, Tphot, Tarch, Tcivil, Twid]
thanTransAll = dict(T=T, Tmatch=Tmatch, Tphot=Tphot, Tarch=Tarch, Tcivil=Tcivil, Twid=Twid)


def thanLangSetall(lang=None):
    "Set translation language."
    if lang is None: lang = thancadconf.thanTranslateTo
    tenc = T.thanLangSet("en", lang)
    assert tenc is not None, "Translation language %s not found" % lang
    #p_ggen.thanSetEncoding(tenc) #Encoding for non-unicode characters #2015_12_15:Commmented out:Users should explicitly set the encoding for nonunicode
    thancadconf.thanTranslateTo = lang
    for t in thanTransAll.values():   #works for python2,3
        t.thanLangSet("en", lang)


def thanLangMore():
    "Add more translations."
    if thanFrape.urban:
        from thanpackages.urban.thantrans.urbantrans import Turban as x
        Turban.__init__(*x.thanTables)
        thanTransAll["Turban"] = Turban
    thanLangSetall()


def thanAddTrans(trans):
    "Adds new translations or updates transaltions."
    for nam, t in trans.items():   #works for python2,3
        if nam in thanTransAll:
            thanTransAll[nam].updateTables(t.thanTables)
        else:
            thanTransAll[nam] = t


thanLangSetall()
