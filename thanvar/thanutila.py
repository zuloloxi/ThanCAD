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

This module defines various functions needed by other ThanCad's modules.
"""

from math import hypot, fabs
import tkinter
from p_gmath import thanNear2, thanNear3
import p_gtkwid, p_ggen
from thanopt import thancadconf
from thantrans import Tmatch


def thanCleanLine2(c):
    "Clean zero lengthed segments (in 2 dimensions) of a continuous multiline."
    if len(c) < 2: return [list(c1) for c1 in c]
    cn = [list(c[0])]
    for c1 in c:
        if thanNear2(cn[-1], c1): continue
        cn.append(list(c1))
    return cn


def thanCleanLine2t(c, t):
    """Clean zero lengthed segments (in 2 dimensions) of a continuous multiline.

    Do the same changes to parallel list of scalar parameters."""
    if len(c) < 2: return [list(c1) for c1 in c], list(t)
    cn = [list(c[0])]
    tn = [t[0]]
    for i in range(1, len(c)):
        if thanNear2(cn[-1], c[i]): continue
        cn.append(list(c[i]))
        tn.append(t[i])
    return cn, tn


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
        t = open(fn).read()
    except Exception as why:
        t = Tmatch["Error while reading file %s:\n%s"] % (fn, why)
    font1 = tkinter.font.Font(family=thancadconf.thanFontfamilymono, size=thancadconf.thanFontsizemono)
    p_gtkwid.thanGudHelpWin(proj[2], t, title, font=font1, width=60)


def thanExtendNodeDims(cs, cful):
    "Extend the dimensions of each node of cs, to have the same dimensions as cful."
    ns = len(cs[0])
    if len(cful) <= ns: return [list(c1) for c1 in cs]  #Ensure that points are lists and not tuples
    cp = []
    for c1 in cs:
        c2 = list(cful)
        c2[:ns] = c1[:ns]
        cp.append(c2)
    return cp


def thanCumulDis(cp):
    "Find the cumulative distances of a line defined by nodes."
    ts = [hypot(hypot(cb[0]-ca[0], cb[1]-ca[1]), cb[2]-ca[2])
          for ca, cb in p_ggen.iterby2(cp)
         ]
    ts.insert(0, 0.0)
    for i in range(1, len(ts)):
        ts[i] += ts[i-1]
    return ts


def thanNearElev(elev1, elev2, elevtol=0.001):
    "Return True if elevations are alsmost the same."
    return fabs(elev2-elev1) < elevtol
