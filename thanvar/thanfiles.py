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

This module maintains currently opened files and recent files.
A ThanCad project is a triad of:
1. Absolute path name where the drawing is stored.
2. The drawing object which holds the drawing in memory.
3. The window where the drawing is shown on.
The 2,3 are unique for each project. Absolute path name should also
be unique (i.e. same absolute path name mean exactly the same projects).
But, of course, if someone mounts a filesystem in between, the same
pathname might point to a different project.
ThanCad may have 2 opened projects with the same pathname simultaneously
because 2,3 will be different.
ThanCad will maintain unique pathnames (not filenames) in recent files.
"""

import p_ggen
import thandefs
from thanopt import thancadconf
from thanopt.thancadconf import thanTempPrefix

__MAXRECENT = 6
__idTemp = thandefs.ThanId(1, prefix=thanTempPrefix)
__opened = []                          # Currently opened projects
__recent = thancadconf.thanFilerecent  # Pathnames of recently saved/opened drawings
#thancadconf.thanFiledir               # Most recent directory
ThanCad = None                         # ThanCad dummy project.


def tempname():
    "Returns a file with temporary name."
    return (p_ggen.path(thancadconf.thanFiledir) / (__idTemp.new() + ".thcx")).abspath()


def isTempname1(filnam):
    "Checks if filnam is the first temporary file."
    return filnam == thanTempPrefix + "1.thcx"


def isTempname(filnam):
    "Checks if filnam is the first temporary file."
    if not filnam.startswith(thanTempPrefix): return False
    if not filnam.endswith(".thcx"): return False
    try: int(filnam[len(thanTempPrefix):-5])
    except ValueError: return False
    return True


def addOpened(proj):
    "Adds a file to the opened files list."
    if len(__opened) == 0:   #The first project ever opened is ThanCad itself
        global ThanCad
        assert ThanCad is None
        ThanCad = proj
    __opened.append(proj)
    for projother in __opened:   #Add this project to the open list of the menu of all opened projects
        projother[2].thanMenu.thanAddOpened(proj)


def delOpened(proj):
    "Removes a file from the opened files list."
    assert proj in __opened
    for projother in __opened:
        projother[2].thanMenu.thanDelOpened(proj)
    __opened.remove(proj)


def getOpened():
    "Returns all the currently opened drawings; file one is the main ThanCad window."
    return tuple(__opened)


def addRecent(fpath):
    "Adds a file to the recent files list."
    try: __recent.remove(fpath)
    except ValueError: pass
    del __recent[__MAXRECENT:]
    __recent.insert(0, fpath)
    for proj in __opened:
        proj[2].thanMenu.thanAddRecent(proj, fpath, __MAXRECENT)


def fillMenu(proj):
    "Fill the menu with currently opened projects currently recent filenames."
    m = proj[2].thanMenu
    for projother in __opened:
        m.thanAddOpened(projother)
    for fpath in reversed(__recent):
        m.thanAddRecent(proj, fpath, __MAXRECENT)


def setFiledir(fildir):
    "Sets the current directory."
    thancadconf.thanFiledir = fildir


def getFiledir():
    "Returns the current directory."
    return thancadconf.thanFiledir


if __name__ == "__main__":
    print(__doc__)
