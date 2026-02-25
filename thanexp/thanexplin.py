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

This module defines an function which exports ThanCad line types to
a .lin file (line type definitions)
"""


def thanExpLin(fw, ltypes, prt):
    "Import a linetype definition file (.lin) and return dictionary of the linetypes."
#*BORDER,Border __ __ . __ __ . __ __ . __ __ . __ __ .
#A,.5,-.25,.5,-.25,0,-.25
    fw.write("""\
;;
;;  Linetype Definition file
;;  exported from ThanCad drawing
;;
""")
    for namlt in sorted(ltypes):
        lt = ltypes[namlt]
        fw.write("\n*%s,%s %s\n" % (lt.thanName, lt.thanName, lt.thanDesc))
        dash = list(lt.thanDashes)
        for i in range(1, len(dash), 2):
            dash[i] = -dash[i]
        if len(dash) > 12:
            dash = dash[:12]
            prt("%s: only the first 12 segments are exported" % (lt.thanName,))
        elif len(dash) < 1:
            dash = [1.0, 1.0]       #continuous
        t = ["%.2f" % (d1,) for d1 in dash]
        t.insert(0, "%s" % (lt.thanAlign,))
        fw.write(",".join(t))
        fw.write("\n")
