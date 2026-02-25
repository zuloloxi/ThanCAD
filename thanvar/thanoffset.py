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

This module computes the offset of a line.
"""

import copy
from itertools import islice
from p_gvec import Vector2
from p_gmath import thanSegSeg


def thanOffsetLine(ca, dis):
    "Offset line ca by distance dis on the right side (dis>0) or on the left side (dis<0)."
    if dis == 0.0 or len(ca) < 2: return list(ca)      # Nothing to do: just copy
    va = Vector2(ca[0][0], ca[0][1])
    vb = Vector2(ca[1][0], ca[1][1])
    n1 = (vb-va).normal()
    vf = [va+n1*dis]
    vf[0].cargo = ca[0][2:]
    for cc in islice(ca, 2, None):
        va = vb
        vb = Vector2(cc[0], cc[1])
        n2 = (vb-va).normal()
        diag = (n1+n2)*0.5
        kapa = dis / (diag|n1)
        vf.append(va+kapa*diag)
        vf[-1].cargo = cc[2:]
        n1 = n2
    vf.append(vb+n1*dis)
    vf[-1].cargo = ca[-1][2:]

    if True:                               # Set False for debugging
        i = 0
        while i < len(vf)-2:
            cca = vf[i].x, vf[i].y
            ccb = vf[i+1].x, vf[i+1].y
            for j in range(i+2, len(vf)-1):
                cc1 = vf[j].x, vf[j].y
                cc2 = vf[j+1].x, vf[j+1].y
                ct = thanSegSeg(cca, ccb, cc1, cc2)
                if ct is None: continue
                if i==0 and j+1==len(vf)-1:
                    vv = Vector2(ct[0], ct[1])
                    vv.cargo = vf[0].cargo
                    vf[0] = vv
                    vf[-1] = copy.copy(vv)
                else:
                    vv = Vector2(ct[0], ct[1])
                    vv.cargo = vf[j].cargo
                    vf[i+1:j+1] = [vv]
                    i -= 1
                break
            i += 1

    return [[v.x, v.y]+list(v.cargo) for v in vf]


def minicadDriver(c):
    "A routine to let the algorithm be used from within MiniCad."
    cs = []
    for item in c.find_all():
        typ = c.type(item)
        if typ == "line":
            cs1 = c.coords(item)
            cs1 = list(zip(islice(cs1, 0, None, 2), islice(cs1, 1, None, 2)))  #works for python2,3
            if cs:
                if   cs[-1] == cs1[0]: cs.append(cs1[1])
                elif cs[-1] == cs1[1]: cs.append(cs1[0])
            else:
                cs = cs1
    if not cs:
        print("no line found")
        return
    dis = 50.0
    cs1 = thanOffsetLine(cs, dis)
    c.create_line(cs1, fill="green")
