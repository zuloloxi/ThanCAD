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
This module defines Hippodamus urban plan system.
"""
from __future__ import print_function
from math import cos, sin, pi
import itertools
import p_gimage
import p_ggen, p_gcol, p_gdxf, p_gchart, p_gmath, p_gtri, p_ggeom
from . import roadut, hippocache, roadem


class HippoUrban(object):
    "An object which contains a Hippodamus urban plan system: a grid of roads with nonuniform grid spaces."

    def __init__(self, hull, devdebug=False):
        "Initialize a hippodamus urban plan system."
        self.USEDEM = False                     #Don't use DEM; use Cache
        self.hull = hull                        #The region of the new biocityplan as a convex polygon
        self.contours = None                    #The contour lines inside hull (lines are defined by exactly 2 nodes).
        self.uxmin = self.uxmax = self.uymin = self.uymax = None   #min, max in world coordinated of hull and the contour lines
        self.cache = hippocache.HippoCache()
        self.dem = None
        self.changed = 0                                           #Changes of the object since creation. To aid ThanCad's Tk dialog.
        self.devdebug = devdebug                                   #If True, execute Developer debug code


    def __deepcopy__(self, memo):
        "This is to make shallow copy when ThanCad's Tk dialog deepcopies values of widgets."
        return self.shallowClone()


    def shallowClone(self):
        "Make a shallow copy of self."
        r = self.__class__(self.hull, self.devdebug)
        r.contours = self.contours
        r.uxmin    = self.uxmin
        r.uxmax    = self.uxmax
        r.uymin    = self.uymin
        r.uymax    = self.uymax
        r.cache    = self.cache.shallowClone()
        r.changed  = self.changed
        return r


    def __eq__(self, other):
        "Two objects are equal if the cache is the same; to aid ThanCad's Tk dialog."
        if not isinstance(other, self.__class__): return False
        return self.changed == other.changed


    def build_cache(self, dtm, prt=p_ggen.prg):
        "Create road grid every dx, dy, dtheta; cache the results."
        self.cache.build_cache(dtm, self.hull, prt)
        self.minmax(dtm, prt)
        self.changed += 1    #Object has been modified


    def build_dem(self, dtm, prt=p_ggen.prg):
        "Create a dem."
        self.dem = roadem.RoadDEM(self.hull, dtm, dx=5.0, dy=5.0, theta=0.0, prt=prt, devdebug=self.devdebug)
        self.minmax(dtm, prt)
        self.changed += 1    #Object has been modified


    def minmax(self, dtm, prt=p_ggen.prg):
        "Find contours and xy minmax."
        prt("Determining contours inside city plan..")
        m = p_ggeom.MesaHull(self.hull)
        self.contours = [lin for lin in dtm.thanLines if m.mesa(lin[0]) or m.mesa(lin[1])]
        self.uxmin = min(itertools.chain((c[0] for c in lin for lin in self.contours), (c[0] for c in self.hull)))
        self.uxmax = max(itertools.chain((c[0] for c in lin for lin in self.contours), (c[0] for c in self.hull)))
        self.uymin = min(itertools.chain((c[1] for c in lin for lin in self.contours), (c[1] for c in self.hull)))
        self.uymax = max(itertools.chain((c[1] for c in lin for lin in self.contours), (c[1] for c in self.hull)))

    def roundx(self, theta):
        "Round to fit the cache."
#        if self.USEDEM: return theta
        dth = self.cache.dx
        return round(theta/dth)*dth
    def roundy(self, theta):
        "Round to fit the cache."
#        if self.USEDEM: return theta
        dth = self.cache.dy
        return round(theta/dth)*dth
    def roundt(self, theta):
        "Round to fit the cache."
#        if self.USEDEM: return theta
        dth = self.cache.dtheta
        return round(theta/dth)*dth
    def energy(self, state):
        "Find the energy of the hippodamus urban system."
        if self.USEDEM:
            edem = self.dem.energy(state)
            if self.devdebug:
                ecac = self.cache.energy(state)
                print("dem=", edem, "cache=", ecac)
            return edem
        else:
            return self.cache.energy(state)
    def energy3(self, s):
        "Calculates the energy of the hippodamus urban system described in state s; returns more detail."
        if self.USEDEM:
            sed, sd8, sd10 = self.dem.energy3(s)
        else:
            sed, sd8, sd10 = self.cache.energy3(s)
        return sed, sd8, sd10


    def iterOT(self, state):
        "Iterate through all city blocks of the city plan (OT)."
        t = cos(state.theta*pi/180.0), sin(state.theta*pi/180.0)
        n = -t[1], t[0]
        pxmin, pxmax, pymin, pymax = roadut.pminmax(self.hull, state.theta)

#        print("bod=", state.bod)
#        print("boik=", state.boik)
#        print("hoik=", state.hoik)

        pya = pymin
        jy = jjy = 0
        while True:
            pya += state.bod[jjy]
            pyb = pya+state.boik[jjy]
            if pyb > pymax: break
            ca1, ca2 = p_gtri.thanPolygonLine(self.hull, pya, n)
            assert ca1 != None, "There should be 2 intersections!"
            cb1, cb2 = p_gtri.thanPolygonLine(self.hull, pyb, n)
            assert cb1 != None, "There should be 2 intersections!"
            pxa1 = t[0]*ca1[0]+t[1]*ca1[1]
            pxa2 = t[0]*ca2[0]+t[1]*ca2[1]
            if pxa1 > pxa2: ca1, pxa1, ca2, pxa2 = ca2, pxa2, ca1, pxa1
            pxb1 = t[0]*cb1[0]+t[1]*cb1[1]
            pxb2 = t[0]*cb2[0]+t[1]*cb2[1]
            if pxb1 > pxb2: cb1, pxb1, cb2, pxb2 = cb2, pxb2, cb1, pxb1
            px1min = max((pxa1, pxb1))
            px2max = min((pxa2, pxb2))

            px1 = pxmin
            jx = jjx = 0
            while True:
                px1 += state.bod[jjx]
                px2 = px1 + state.hoik[jjx]
                if px2 > px2max: break
                if px1 >= px1min:
                    cc = []
                    for px, py in (px1, pya), (px2, pya), (px2, pyb), (px1, pyb), (px1, pya):
                        cc.append([px*t[0]+py*n[0], px*t[1]+py*n[1]])
                    yield cc
                px1 = px2
                jx += 1
                if jx < len(state.hoik): jjx = jx

            pya = pyb
            jy += 1
            if jy < len(state.boik): jjy = jy


    def roadcoor(self, s):
        "Find road coordinates along x and y axis, in order to make a drawing; for illustration, not currently used."
        thrad = s.theta*pi/180.0
        roads = []
        self.roadcoor1(roads, self.dy, s.theta, thrad,        self.pymin, self.pymax, s.boik, s.bod)
        self.roadcoor1(roads, self.dx, s.theta, thrad-pi*0.5, self.pxmin, self.pxmax, s.hoik, s.bod)
        return roads


    def roadcoor1(self, roads, dy, theta, thrad, pymin1, pymax1, boik, bod):
        "Find road coordinates along x or y axis, in order to make a drawing; for illustration, not currently used."
        t = cos(thrad), sin(thrad)
        n = -t[1], t[0]
        py = pymin1[theta]
        pymax = pymax1[theta]
        j = jj = 0
        while True:
            pyaxis = py + bod[jj]*0.5
            pyaxis = int(pyaxis/dy+0.5)*dy
            if pyaxis > pymax: break
            c1, c2 = p_gtri.thanPolygonLine(self.hull, pyaxis, n)
            assert c1 != None, "There should be 2 intersections!"
            roads.append((c1, c2))
            py += bod[jj] + boik[jj]
            j += 1
            if j < len(boik): jj = j


    def tochart(self, ch, hulls=(), iso=(), ot=(), roads=(), colot="blue"):
        "Draw the hippodamus urban plan system into a ThanChart."
        for lines, col, _ in self.itlines(hulls, iso, ot, roads, colot):
            if lines is None: continue
            for line1 in lines:
                xx = [c[0] for c in line1]
                yy = [c[1] for c in line1]
                if lines is roads: ch.curveAdd(xx, yy, style="dasheddot", size=(12, -6, 3, -6), color=col)
                else:              ch.curveAdd(xx, yy, color=col)

    def itlines(self, hulls=(), iso=(), ot=(), roads=(), colot="blue"):
        "Iterate through the lines to be plotted."
        return [(hulls, "green", "hull"),
                (iso,   "brown", "contours"),
                (ot,    colot,   "ot"),
                (roads, "red",   "roads"),
               ]

    def topil(self, imd, ct, hulls=(), iso=(), ot=(), roads=(), colot="blue"):
        "Draw the hippodamus urban plan system into a PIL image."
        g2li = ct.global2Locali
        for lines, col, _ in self.itlines(hulls, iso, ot, roads, colot):
            if lines is None: continue
            for line1 in lines:
                cc = [g2li(c[0], c[1]) for c in line1]
                imd.line(cc, fill=col)

    def todxf(self, dxf, title="", hulls=(), iso=(), ot=(), roads=(), colot="blue", xor=0.0, yor=0.0):
        "Draw the hippodamus urban plan system into a dxf file."
        from p_gcol import thanDxfColName2Rgb, thanRgb2DxfColCodeApprox
        for lines, col, laynam in self.itlines(hulls, iso, ot, roads, colot):
            if lines is None: continue
            for line1 in lines:
                xx = [xor+c[0] for c in line1]
                yy = [yor+c[1] for c in line1]
                roadut._layer(dxf, laynam, col)
                dxf.thanDxfPlotPolyline(xx, yy)
        dy = (self.uymax-self.uymin)/100.0*5.0
        roadut._layer(dxf, "TITLE", "white")
        dxf.thanDxfPlotSymbol(xor+self.uxmin+1.0*dy, yor+self.uymax+1.0*dy, dy, title, 0.0)

    def show(self, winmain=None, title="", iso=(), ot=(), roads=(), colot="blue"):
        "Draw the hippodamus urban plan system into a ThanChart and show it on screen."
        ch = p_gchart.ThanChart(title)
        self.tochart(ch, (self.hull,), iso, ot, roads, colot)
        if winmain is None: p_gchart.vis(ch, bg="white")
        else:               p_gchart.viswin(winmain, ch, bg="white")

    def pilout(self, title="", width=600, height=400, iso=(), ot=(), roads=(), colot="blue"):
        "Create an image and draw the hippodamus urban plan system into this image."
        ct = self._pilct(width, height, (self.hull,), iso, ot, roads, colot)
        im = p_gimage.new("RGB", (width, height), (255,255,255))
        imd = p_gimage.Draw(im)
        self.topil(imd, ct, (self.hull,), iso, ot, roads)
        imd.text((5,1), text=title, fill=colot)
        return im, ct

    def _pilct(self, width=600, height=400, hulls=(), iso=(), ot=(), roads=(), colot="blue"):
        "Find the scale of the configuration to fill into an image of width x height."
        xmin = ymin = 1.0e100
        xmax = ymax = -ymin
        for lines, _, _ in self.itlines(hulls, iso, ot, roads, colot):
            if lines is None: continue
            for line1 in lines:
                for c in line1:
                    if c[0] < xmin: xmin = c[0]
                    if c[0] > xmax: xmax = c[0]
                    if c[1] < ymin: ymin = c[1]
                    if c[1] > ymax: ymax = c[1]
        assert xmin<xmax and ymin<ymax, "No hull, iso, ot, roads!"
        ct = p_gmath.ThanRectCoorTransf((xmin, ymin, xmax, ymax), (5, height-5, width-5, 5))
        return ct

    def dxfout(self, title="", iso=(), ot=(), roads=(), colot="blue", fw=None):
        "Create a .dxf file and draw the hippodamus urban plan systeminto this dxf file."
        dxf = p_gdxf.ThanDxfPlot()
        dxf.thanDxfPlots(fw)
        self.todxf(dxf, title, (self.hull,), iso, ot, roads, colot)
        dxf.thanDxfPlot(0,0,999)


    def writeGrid(self, fw):
        "Write hippodamus urban plan system to a file (like) object."
        fw.write("# Hull:\n")
        for ca in self.hull:
            ca = list(ca[:3])
            while len(ca) < 3: ca.append(0.0)
            fw.write("%f  %f   %f\n" % tuple(ca))
        fw.write("$\n")

        self.cache.write_cache(fw)

        fw.write("# Contours:\n")
        for lin in self.contours:
            assert len(lin) == 2
            ca, cb = lin
            ca = list(ca[:3])
            while len(ca) < 3: ca.append(0.0)
            cb = list(cb[:3])
            while len(cb) < 3: cb.append(0.0)
            fw.write("%f  %f   %f  %f  %f  %f\n" % tuple(ca+cb))
        fw.write("$\n")
        fw.write("# uxmin, uxmax uymin, uymax:\n%f  %f  %f  %f\n" % (self.uxmin, self.uxmax, self.uymin, self.uymax))


    def readGrid(self, fr):
        "Read Hippodamus urban system from a file (like) object."
        self.hull = []
        self.contours = []
        self.uxmin = self.uxmax = self.uymin = self.uymax = None
        it = roadut.itercom(fr)
        while True:
            dl = next(it).split()
            if dl[0] == "$": break
            ca = map(float, dl)
            self.hull.append(ca)

        self.cache.read_cache(it)

        while True:
            dl = next(it).split()
            if dl[0] == "$": break
            ca = map(float, dl)
            lin = [ca[:3], ca[3:]]
            self.contours.append(lin)
        self.uxmin, self.uxmax, self.uymin, self.uymax = map(float, next(it).split())

        self.changed += 1     #Object has been modified
