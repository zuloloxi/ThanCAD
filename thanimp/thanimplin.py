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

This module defines an function which reads a .lin file (line type definitions)
and returns appropriate ThanCad's objects to represent it in ThanCad.
"""

import p_gfil
import thandefs


def thanImpLin(fr, prt=None):
    "Import a linetype definition file (.lin) and return dictionary of the linetypes."
#*BORDER,Border __ __ . __ __ . __ __ . __ __ . __ __ .
#A,.5,-.25,.5,-.25,0,-.25
    ltypes = {}
    fr = p_gfil.Datlin(fr, prt=prt, comment=";;")
    for dl in fr:
        i = dl.find(",")
        if i >= 0:
            namlt = dl[:i].strip()
            desc = dl[i+1:].strip()
            nam1 = namlt.lower()[1:]
            i = desc.lower().find(nam1)
            if i >= 0:   #If the name of the linetype is found in the description, delete it
                desc = desc[:i].strip() + desc[i+len(nam1):]
                desc = desc.strip()
        else:
            namlt = dl.strip()
            desc = 0
        if namlt[0:1] != "*":
            fr.er1("Invalid linetype name: %s" % (namlt,))
            continue
        namlt = namlt[1:].strip()
        if namlt == "":
            fr.er1("Empty linetype name")
            continue
        for dl in fr:
            dl = dl.strip()
            break
        else:
            fr.er1("Incomplete linetype definition.")
            break
        pat = dl.split(",")
        if pat[0].strip() != "A":
            fr.er1("Invalid dash patterns: %s" % (dl,))
            continue
        del pat[0]
        try:
            pat = list(map(float, pat))   #works for python2,3
        except ValueError:
            fr.er1("Invalid or unsupported dash patterns: %s" % (dl,))
            continue
        lt = thandefs.ThanLtype()
        unit = lt.thanFromDxf(namlt, desc, pat)       #Unit has a meaning when reading .dxf (not .lin)
        ltypes[lt.thanName] = lt
    return ltypes
