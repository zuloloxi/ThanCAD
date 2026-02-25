# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2015 Thanasis Stamos, January 18, 2015
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers

Package which creates a bioclimatic city plan.
"""
from __future__ import print_function
#from past.builtins import xrange
from p_ggen.py23 import xrange
import p_ggen, p_ganneal, p_gtri
from . import hippoanneal, roadut

USEDEM = False          #Use DEM instead of DTM
devdebug = False        #If True, execute Developer debug code


def runOnce(pc, prt=p_ggen.prg):
    "Run the simulated annealing method once."
    pc.repairState()
    sa = p_ganneal.SimulatedAnnealing(prt=prt) #animon=True, animnframe=20)
#    sa.config(tsteps=2)
    sa.anneal(pc)
    e = pc.energyState() / pc.efact
    prt("Final energy=%.3f -> %.3f" % (e, e*pc.efact))
    s = pc.state
    s.e, s.d8, s.d10 = pc.pol.energy3(s)


def makeDTM(clines):
    "Makes DTM from lines."
    dtm = p_gtri.ThanDTMlines()
    for cline1 in clines: dtm.thanAddLine1(cline1)
    dtm.thanRecreate()
    return dtm


def makeHull(clines):
    "Computes convex hull of DTM lines."
    cc = []
    for cline1 in clines: cc.extend(cline1)
    hu = p_gtri.hull(cc)
    return hu


def readSyk(fr):
    "Reads the contours of a syk file."
    lindxf = 0
    it = iter(fr)
    clines = []
    for dline in it:
        lindxf += 1
        try:
            z1 = float(dline[:15])
        except (ValueError, IndexError) as why:
            why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
            raise ValueError(why)
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                x1 = float(dline[:15])
                y1 = float(dline[15:30])
            except (ValueError, IndexError) as why:
                why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
                raise ValueError(why)
            else: cc.append([x1, y1, z1])

        if len(cc) < 2: print("Polyline with 1 or 0 vertices.")
        clines.append(cc) #-----------Store the polyline
    return clines


def wrState(pc, pref, prter=p_ggen.prg):
    "Write computed solution."
    for i in xrange(1000):
        fn = p_ggen.path("%s.state%03d" % (pref, i))
        if not fn.exists(): break
    else:
        prter("Can not open file to save state: too many state files.")
        return
    fw = open(fn, "w")
    pc.wrstate(fw)
    fw.close()
