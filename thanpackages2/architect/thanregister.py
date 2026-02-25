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

The package creates automatically architectural things such as stairs.
This module registers this package to ThanCad.
"""
from . import thancomarch
from thantrans import T, Tarch


def thanRegisterCommands():
    "The commands of the package to be added to the commands of ThanCad."
    coms = ( ("archstairs", thancomarch.thanArchStairs),
           )
    abbrevs = ()
    return coms, abbrevs


def thanRegisterMenus():
    "The menus of the package to be added in ThanCad."
    m = {}
    m["Engineering"] = \
    [ ("menu", T["&Engineering"], ""),        # Menu Title
      ("-",),
      ("archstairs", Tarch["&Stairs"], Tarch["Computes and draws the plan view of a simple staircase"]),
      ("endmenu",),
    ]
    #Sequence of menus: tuples of (menuname, aftermenu, afterentry)
    #menuname is the name of the new menu (or an existing one which will be extended)
    #If menuname is a new menu, it is going to be added after existing sftermenu.
    #If aftermenu does not exist, the it is inserted just before the last menu ("help" menu)
    #If menuname exists, then the entries of menuname are added after entry afterentry.
    #If afterentry does not exist then the entries are added at the end of existing menuname.
    #afterentry is the ThanCad command that corresponds to the menu entry (because it is unique).
    seq = [("Engineering", "Draw", "urbanslope"),    #Sequnece of menus: new menu "Engineering" is next to menu "Draw"
          ]
    return seq, m


def thanRegisterTrans():
    "The translations of phrases of the package."
    #Translations: dictionary mapping of traname to tra.
    #traname is the name of the translation and tra is a ThanTranslation object.
    #If traname exists, then the corresponding ThanTranslation object is
    #updated with the entries of tra.
    return {}


def thanRegisterAfter():
    """This function is called after all plugins are loaded and ThanCad is ready to begin.

    It is useful if a translation is added to an existing, and the package wants
    to have the complete translation object.
    """
    pass
