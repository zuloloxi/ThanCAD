# -*- coding: iso-8859-7 -*-
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

Package which processes commands entered by the user.
This module processes the line join command.
"""

from thandr import ThanLine

def thanJoinSel(proj, elems, nearx):
    """Joins consecutive lines to 1 bigger line.

    The layer of a joined line will be the layer of one of the
    original lines (randomly) that were joined. The orientation of the
    joined line will also be random.
    The join command uses the nearx function to test if two nodes
    are the same. nearx may be thanNear3 or thanNear2  thanNear2
    will join 2 lines even if they have completely different z.
    """
    newelems = set()      #New elements (joined lines)
    samelems = set()      #Lines which did not take part in a joined line
    othelems = set()      #Other elements (not lines)
    lines = set()
    for e in elems:
        if isinstance(e, ThanLine):
            e._joined = False
            lines.add(e)
        else:
            othelems.add(e)
    while len(lines) > 0:
        e = lines.pop()
        cbeg = e.cp[0]
        cend = e.cp[-1]
        for e1 in lines:
            if nearx(cbeg, e1.cp[0]):
                e = __joinhouse(e, e1, lines)
                cp1 = list(reversed(e1.cp)); cp1.pop()
                cp1.extend(e.cp)
                e.cp[:] = cp1
                lines.add(e)
                break
            elif nearx(cbeg, e1.cp[-1]):
                e = __joinhouse(e, e1, lines)
                cp1 = e1.cp[:-1]
                cp1.extend(e.cp)
                e.cp[:] = cp1
                lines.add(e)
                break
            elif nearx(cend, e1.cp[0]):
                e = __joinhouse(e, e1, lines)
                e.cp.extend(e1.cp[1:])
                lines.add(e)
                break
            elif nearx(cend, e1.cp[-1]):
                e = __joinhouse(e, e1, lines)
                cp1 = list(reversed(e1.cp)); cp1.pop(0)
                e.cp.extend(cp1)
                lines.add(e)
                break
        else:
            if e._joined: newelems.add(e)
            else:         samelems.add(e)
            del e._joined
    if len(newelems) > 0: proj[1].thanTouch()
    for e in newelems:  #We assume that all elements are ThanLine.We recreate the lines to:..
        e.thanSet(e.cp) #.. a. Delete zero lengthed segments, b. Recompute boundbox (which is wrong)
    delelems = (elems-othelems)-samelems
    return delelems, newelems, samelems, othelems


def __joinhouse(e, e1, lines):
    "House keeping for join lines."
    lines.remove(e1)
    del e1._joined
    if e._joined: return e

#Create a new joined line, initialized with current line

    en = e.thanClone()
#    en.thanTags = e.thanTags
#    en.handle = e.handle
    en._joined = True
    del e._joined
    return en


def thanJoinGapn(proj, elems, disx):
    """Joins n lines even if they have gap; links the nearest ends.

    disx is a function which find the distance of 2 points in 2
    or 3 dimensions. The running time grows as n**3. Thus it is
    not practical for big n, for example n > 50"""
    elems = list(elems)
    while len(elems) > 1:
        d = []
        nelems = len(elems)
        for k1 in range(nelems):
            e1 = elems[k1]
            for k2 in range(k1+1, nelems):
                e2 = elems[k2]
                for i in 0,-1:
                    for j in 0,-1:
                        d.append((disx(e1.cp[i], e2.cp[j]), i, j, k1, k2))
        print("thanJoinGapn(): d = ")
        for temp in d: print(temp)
        dm, i, j, k1, k2 = min(d)
        en = elems[k1].thanClone()
        e2 = elems[k2]
#        en.thanTags = e1.thanTags
#        en.handle = e1.handle
        if i == 0: en.cp.reverse()
        if j == 0: en.cp.extend(e2.cp)
        else     : en.cp.extend(reversed(e2.cp))
        del elems[k2]    #Note k2>k1 and thus k2 is the first to delete
        del elems[k1]
        elems.append(en)
    return elems
