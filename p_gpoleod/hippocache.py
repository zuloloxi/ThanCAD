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
This module builds a cache for an Hippodamian plan of city layouts.
"""

from __future__ import print_function
from math import cos, sin, pi, ceil, floor
import p_ggen, p_gtri
from . import roadut


class HippoCache(object):
    "A cache of road energys for an Hippodamus urban plan system."

    def __init__(self, dx=1.0, dy=1.0, dtheta=1.0, devdebug=False):
        "Initialize the cache."
        self.roadenx = self.roadeny = None      #Cached road energy in direction x (angle theta) and y (theta+90)
        self.pxmin = self.pxmax = self.pymin = self.pymax = None   #Cached min, max coordinates in local coordinates for each angle theta
        self.dx = dx                                               #Sampling Distance x and y of all computed roads in the cache
        self.dy = dy                                               #Sampling Distance x and y of all computed roads in the cache
        self.dtheta = dtheta                                       #Sampling theta for computation of road cache
        self.devdebug = devdebug                                   #If True, execute Developer debug code


    def shallowClone(self):
        "Make a shallow copy of self."
        r = HippoCache(self.dx, self.dy, self.dtheta)
        r.roadenx  = self.roadenx
        r.roadeny  = self.roadeny
        r.pxmin    = self.pxmin
        r.pxmax    = self.pxmax
        r.pymin    = self.pymin
        r.pymax    = self.pymax
        return r


    def build_cache(self, dtm, hull, prt=p_ggen.prg):
        "Create road grid every dx, dy, dtheta; cache the results."
#        self.dx = self.dy = 5.0       #Make the routine faster: for debugging
#        self.dtheta = 30.0            #Make the routine faster: for debugging
        self.roadenx = {}      #road energy in direction x (angle theta)
        self.roadeny = {}      #road energy in direction y (angle theta-90deg)
        self.pxmin = {}        #xmin of a road where x is the direction of angle theta and also the direction of the road
        self.pxmax = {}        #xmax
        self.pymin = {}        #ymin of a road where y is the direction of angle theta-90deg and also the direction of the road
        self.pymax = {}        #ymax
        prt("Building cache..")
        for theta in p_ggen.xfrange(-90.0, 90.0, self.dtheta):
            prt("theta=%f" % theta)
            thrad = theta*pi/180.0
            pymin, pymax = self.build_cache_roads(dtm, hull, self.roadenx, theta, thrad, self.dy, prt)
            pxmin, pxmax = self.build_cache_roads(dtm, hull, self.roadeny, theta, thrad-pi*0.5, self.dx, prt)
            self.pymin[theta] = pymin
            self.pymax[theta] = pymax
            self.pxmin[theta] = pxmin
            self.pxmax[theta] = pxmax


    def build_cache_roads(self, dtm, hull, roads, theta, thrad, dy, prt):
        "Create grid; direction theta with respect to x-axis, varied widths,lenths of O.T. varies lengths of roads."
        t = cos(thrad), sin(thrad)
        n = -t[1], t[0]
        py = [n[0]*c[0]+n[1]*c[1] for c in hull]
        pymin = ceil(min(py)/dy+0.1)*dy     # Avoid py exactly on boundary
        pymax = floor(max(py)/dy-0.1)*dy    # Avoid py exactly on boundary
#        prt("pymin=%.3f  -->  %.3f" % (min(py), pymin))
#        prt("pymax=%.3f  -->  %.3f" % (max(py), pymax))

        for pyaxis in p_ggen.xfrangec(pymin, pymax, dy):
            c1, c2 = p_gtri.thanPolygonLine(hull, pyaxis, n)
            assert c1 != None, "There should be 2 intersections!"
            nc, cprof = dtm.thanLineZ((c1, c2))
            if nc == -1:
                roads[theta, pyaxis] = None      # No profile was found
            else:
                roads[theta, pyaxis] = roadut.road1energy(cprof)
        return pymin, pymax


    def energy(self, s):
        "Calculates the energy of the road grid described in state s, using the built cache."
        sd, sd8, sd10, se = self.roadenergy(self.roadenx, self.dy, s.theta, self.pymin, self.pymax, s.boik, s.bod)
        d, d8, d10, e     = self.roadenergy(self.roadeny, self.dx, s.theta, self.pxmin, self.pxmax, s.hoik, s.bod)
        if self.devdebug: print("cache: theta: sd, se=", sd, se, "      theta+90:", d, e)
        sd += d
        sd8 += d8
        sd10 += d10
        se += e
        return se/sd


    def energy3(self, s):
        "Calculates the energy of the road grid described in state s, using the built cache; returns more detail."
        sd, sd8, sd10, se = self.roadenergy(self.roadenx, self.dy, s.theta, self.pymin, self.pymax, s.boik, s.bod)
        d, d8, d10, e     = self.roadenergy(self.roadeny, self.dx, s.theta, self.pxmin, self.pxmax, s.hoik, s.bod)
        sd += d
        sd8 += d8
        sd10 += d10
        se += e
        return se/sd, sd8, sd10


    def roadenergy(self, roaden, dy, theta, pymin1, pymax1, boik, bod):
        "Find the energy of roads along x or y axis using the built cache."
        py = pymin1[theta]
        pymax = pymax1[theta]
        j = jj = 0
        sd = sd8 = sd10 = se = 0.0
        while True:
            pyaxis = py + bod[jj]*0.5
            pyaxis = round(pyaxis/dy+0.5)*dy
            if pyaxis > pymax: break
            d, d8, d10, e = roaden[theta, pyaxis]
            sd += d
            sd8 += d8
            sd10 += d10
            se += e
            py += bod[jj] + boik[jj]
            j += 1
            if j < len(boik): jj = j
        return sd, sd8, sd10, se


    def write_cache(self, fw):
        "Write the cache to a file (like) object."
        fw.write("# dx dy dtheta:\n%f   %f   %f\n" % (self.dx, self.dy, self.dtheta))
        for nam, pc in ("pxmin", self.pxmin), ("pxmax", self.pxmax), ("pymin", self.pymin), ("pymax", self.pymax):
            fw.write("\n# %s:\n" % nam)
            for key in sorted(pc.keys()):   #OK for python 2,3
                fw.write("%f   %f\n" % (key, pc[key]))
            fw.write("$\n")
        for nam, pc in ("road energy x", self.roadenx), ("road energy y", self.roadeny):
            fw.write("\n# %s:\n" % nam)
            for key in sorted(pc.keys()):  #OK for python 2,3
                val = pc[key]
                fw.write("%f  %f   %f  %f  %f  %f\n" % (key[0], key[1], val[0], val[1], val[2], val[3]))
            fw.write("$\n")


    def read_cache(self, it):
        "Read HippoUrban from a file (like) object."
        self.dx = self.dy = 1.0
        self.dtheta = 1.0
        self.roadenx = {}
        self.roadeny = {}
        self.pxmin = {}
        self.pxmax = {}
        self.pymin = {}
        self.pymax = {}

        self.dx, self.dy, self.dtheta = map(float, next(it).split())

        for nam, pc in ("pxmin", self.pxmin), ("pxmax", self.pxmax), ("pymin", self.pymin), ("pymax", self.pymax):
            while True:
                dline = next(it)
                if dline == "$": break
                key, val = map(float, dline.split())
                pc[key] = val

        for nam, pc in ("road energy x", self.roadenx), ("road energy y", self.roadeny):
            while True:
                dline = next(it)
                if dline == "$": break
                key1, key2, val1, val2, val3, val4 = map(float, dline.split())
                pc[key1, key2] = val1, val2, val3, val4
