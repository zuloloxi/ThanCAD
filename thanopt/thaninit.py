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

Package which provides for ThanCad and/or ThanCad drawings customisation.
This module provides for ThanCad initialisation.
"""

import sys                 #Module sys is guaranteed by Python
import p_ggen
from . import thanmenus2


def thanInitPregui():
    "Initial values before the gui instantiation."
    from . import thancadconf
    thancadconf.thanOptsGet()
    import thanvers
    thanvers.thancadVersInit(thancadconf.thanTranslateTo)
    import thandefs
    import thantrans
    thantrans.thanLangSetall()         #Set default language as is thancadconf (or in thancadconf.thanOptsGet())
    import thanlayer
    import thandr
    thantrans.thanLangMore()        #Add more translations
    thantrans.thanLangSetall()         #Set default language to all (and the new) translations
    import thancom
    thanmenus2.thanCreateMenus()    #Create the menus with the established translations
    thanLoadPackages()



def thanLoadPackages():
    "Load ThanCad packages (plugins)."
    import thanpackages2, thancom
    thanPackagesLoaded = []
    for pn in thanpackages2.__all__:
        p = getattr(thanpackages2, pn)
        try:
            p.thanRegisterCommands
            p.thanRegisterMenus
            p.thanRegisterTrans
        except AttributeError as why:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue
        try:
            coms, abbrevs = p.thanRegisterCommands()
            seq, m = p.thanRegisterMenus()
            trans = p.thanRegisterTrans()
        except BaseException as why:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue
        try:
            thancom.thanAddCommands(coms, abbrevs)
            thanmenus2.thanAddMenus(seq, m)
        except BaseException as why:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue
        thanPackagesLoaded.append(p)
    for p in thanPackagesLoaded:
        try:
            p.thanRegisterAfter
        except AttributeError:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue
        try:
            p.thanRegisterAfter()
        except BaseException as why:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue


def thanInitPostgui():
    "Initial values just after the gui instantiation."
    pass


def thanInitEndgui():
    "Final values just after the gui shutdown."
    from . import thancadconf
    thancadconf.thanOptsSave()
