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

This module defines various functions needed by other ThanCad's modules.
"""

import tkFont
from p_gmath import thanNear2, thanNear3
import p_gtkuti
from thanopt import thancadconf


def thanCleanLine2(c):
    "Clean zero lengthed segments (in 2 dimensions) of a continuous multiline."
    if len(c) < 2: return [list(c1) for c1 in c]
    cn = [list(c[0])]
    for c1 in c:
        if thanNear2(cn[-1], c1): continue
        cn.append(list(c1))
    return cn


def thanCleanLine3(c):
    "Clean zero lengthed segments (in 3 dimensions) of a continuous multiline."
    if len(c) < 2: return [list(c1) for c1 in c]
    cn = [list(c[0])]
    for c1 in c:
        if thanNear3(cn[-1], c1): continue
        cn.append(list(c1))
    return cn

def thanShowFile(proj, fn, title=""):
    "Show the content of a text file in mono font."
    if title == "": title = fn.basename()
    else:           title = "%s: %s" % (fn.basename(), title)
    try:
        t = file(fn).read()
    except Exception, why:
        t = Tmatch["Error while reading file %s:\n%s"] % (fn, why)
    font1 = tkFont.Font(family=thancadconf.thanFontfamilymono, size=thancadconf.thanFontsizemono)
    p_gtkuti.thanGudHelpWin(proj[2], t, title, font=font1, width=60)


#The following is for compatibility with old .thc files and it should be deleted
from thandefs import ThanId



if __name__ == "__main__":
    print __doc__
