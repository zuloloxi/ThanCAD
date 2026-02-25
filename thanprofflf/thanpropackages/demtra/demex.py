#!/usr/bin/python
# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

Package which find the optimum transaltion between SRTM and EGSA87.
"""
from math import sqrt
import p_ggen

def exhaust(fw, name, thanPointZ, cps, cen, dxyrange, dxy, prg):
    "Check from -dxyrange to +dxyrange with step dxy in x and y direction."
    prg("GDEM: %s" % (name,), "info")
    prg("ΜΕΘΟΔΟΣ ΕΞΑΝΤΛΗΤΙΚΗΣ ΑΝΑΖΗΤΗΣΗΣ", "info")
    f = "%10d%15.3f%15.3f%15.3f%15.3f\n"
    f2 = "%10s%15s%15s%15s%15s\n"
    fw.write("GDEM: %s\n" % (name,))
    fw.write("ΜΕΘΟΔΟΣ ΕΞΑΝΤΛΗΤΙΚΗΣ ΑΝΑΖΗΤΗΣΗΣ\n")
    fw.write(f2 % ("Points", "DX", "DY", "Error Z", "Eff. error Z"))
    er = []
    for dx in p_ggen.xfrangec(cen[0]-dxyrange, cen[0]+dxyrange, dxy):
        prg("x=%6.1f / %6.1f" % (dx, cen[0]+dxyrange))
        for dy in p_ggen.xfrangec(cen[1]-dxyrange, cen[1]+dxyrange, dxy):
            n, e, e2 = srtmerz(thanPointZ, cps, dx, dy)
            er.append((e2, n, dx, dy, e))
            fw.write(f % (n, dx, dy, e, e2))
    e2, n, dx, dy, e = min(er)
    fw.write("Minimum error:\n")
    fw.write(f % (n, dx, dy, e, e2))
    fw.write("Systematic and random error:\n")
    dz = srtmersystz(thanPointZ, cps, dx, dy)
    n, e, e2 = srtmerz(thanPointZ, cps, dx, dy, dz)
    fw.write(f2 % ("Points", "DX", "DY", "Systemat.er.Z", "Random er.Z"))
    fw.write(f % (n, dx, dy, dz, e))


def srtmersystz(thanPointZ, cps, dx, dy):
    "Compute the systematic error of SRTM Z, at points cps translated by dx, dy."
    e = 0.0
    n = 0
    for cpa in cps:
        cp = (cpa[0]+dx, cpa[1]+dy, cpa[2])
        z = thanPointZ(cp)
        if z == None: continue
        e += z-cp[2]
        n += 1
    if n == 0:
        esyst = 999999.999     #No points found, return huge error
    else:
        esyst = e/n
    return esyst


def srtmerz(thanPointZ, cps, dx, dy, dz=0.0):
    "Compute the error of SRTM Z, at points cps translated by dx, dy."
    e = 0.0
    n = 0
    for cpa in cps:
        cp = (cpa[0]+dx, cpa[1]+dy, cpa[2]+dz)
        z = thanPointZ(cp)
        if z == None: continue
        e += (cp[2]-z)**2
        n += 1
    if n == 0:
        e = e2 = 999999.999   #No points found, return huge error
    else:
        e = e2 = sqrt(e/n)
        a = 0.5 * len(cps)    #If less than a points, then this error is not reliable
        if n < a: e2 *= (a/n)**2   #If not enough points found, increase the error artificially
    return n, e, e2
