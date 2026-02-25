# -*- coding: iso-8859-7 -*-
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

Package which creates a bioclimatic city plan.
"""
import random, copy, itertools
import Image, ImageDraw
from math import cos, sin, pi, hypot, fabs
import p_ggen, p_gchart, p_ggeom
from p_gmath import thanLineSeg3, thanNear2


class RoadGrid:
    "An object which contains a grid of road with nonuniform grid spaces."

    def __init__(self, hull):
        "Initialize a road grid."
        self.hull = hull                        #The region of the new biocityplan as a convex polygon
        self.contours = None                    #The contour lines inside hull (lines are defined by exactly 2 nodes).
        self.roadenx = self.roadeny = None      #Cached road energy in direction x (angle theta) and y (theta+90)
        self.pxmin = self.pxmax = self.pymin = self.pymax = None   #Cached min, max coordinates in local coordinates for each angle theta
        self.uxmin = self.uxmax = self.uymin = self.uymax = None   #min, max in world coordinated of hull and the contour lines
        self.dx = self.dy = 1.0                                    #Sampling Distance x and y of all computed roads in the cache
        self.dtheta = 1.0                                          #Sampling theta for computation of road cache

        self.changed = 0                                           #Changes of the object since creation. To aid ThanCad's Tk dialog.


    def __deepcopy__(self, memo):
        "This is to make shallow copy when ThanCad's Tk dialog deepcopies values of widgets."
        return self.shallowClone()


    def shallowClone(self):
        "Make a shallow copy of self."
        r = RoadGrid(self.hull)
        r.contours = self.contours
        r.roadenx  = self.roadenx
        r.roadeny  = self.roadeny
        r.pxmin    = self.pxmin
        r.pxmax    = self.pxmax
        r.pymin    = self.pymin
        r.pymax    = self.pymax
        r.uxmin    = self.uxmin
        r.uxmax    = self.uxmax
        r.uymin    = self.uymin
        r.uymax    = self.uymax
        r.dx       = self.dx
        r.dy       = self.dy
        r.dtheta   = self.dtheta
        r.changed  = self.changed
        return r


    def __eq__(self, other):
        "Two objects are equal if the cache is the same; to aid ThanCad's Tk dialog."
        if not isinstance(other, self.__class__): return False
        return self.changed == other.changed


    def build_cache(self, dtm, prt=p_ggen.prg):
        "Create road grid every dx, dy, dtheta; cache the results."
        self.dx = self.dy = 5.0       #Make the routine faster: for debugging
        self.dtheta = 30.0            #Make the routine faster: for debugging
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
            pymin, pymax = self.build_cache_roads(dtm, self.roadenx, theta, thrad, self.dy)
            pxmin, pxmax = self.build_cache_roads(dtm, self.roadeny, theta, thrad-pi*0.5, self.dx)
            self.pymin[theta] = pymin
            self.pymax[theta] = pymax
            self.pxmin[theta] = pxmin
            self.pxmax[theta] = pxmax
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

    def build_cache_roads(self, dtm, roads, theta, thrad, dy):
        "Create grid; direction theta with respect to x-axis, varied widths,lenths of O.T. varies lengths of roads."
        t = cos(thrad), sin(thrad)
        n = -t[1], t[0]
        py = [n[0]*c[0]+n[1]*c[1] for c in self.hull]
        pymin = int(min(py)/dy+1.1)*dy     # Avoid py exactly on boundary
        pymax = int(max(py)/dy-1.1)*dy     # Avoid py exactly on boundary

        for pyaxis in p_ggen.xfrangec(pymin, pymax, dy):
            c1, c2 = thanPolygonLine(self.hull, pyaxis, n)
            assert c1 != None, "There should be 2 intersections!"
            nc, cprof = dtm.thanLineZ((c1, c2))
            if nc == -1:
                roads[theta, pyaxis] = None      # No profile was found
            else:
                roads[theta, pyaxis] = self.build_cache_roadenergy(cprof)
        return pymin, pymax


    w1 = 10.0
    w2 = 100.0
    def build_cache_roadenergy(self, cc):
        "Calculates the energy of a road."
        sd = e = 0.0
        d8 = 0.0
        d10 = 0.0
        for ca, cb in p_ggen.iterby2(cc):
                d = hypot(cb[0]-ca[0], cb[1]-ca[1])
                sd += d
                dz = fabs(cb[2]-ca[2])
                slope = dz*100.0/d
                if slope <= 8.0:
                    e += 0.0
                elif slope < 10.0:
                    e += d*self.w1*(slope-8.0)
                    d8 += d
                else:
                    e += d*self.w1*(10.0-8.0) + d*self.w2*(slope-10.0)
                    d8 += d
                    d10 += d
        return sd, d8, d10, e


    def write_cache(self, fw):
        "Write RoadGrid to a file (like) object."
        fw.write("# Hull:\n")
        for ca in self.hull:
            ca = list(ca[:3])
            while len(ca) < 3: ca.append(0.0)
            fw.write("%f  %f   %f\n" % tuple(ca))
        fw.write("$\n")

        fw.write("# dx dy dtheta:\n%f   %f   %f\n" % (self.dx, self.dy, self.dtheta))
        for nam, pc in ("pxmin", self.pxmin), ("pxmax", self.pxmax), ("pymin", self.pymin), ("pymax", self.pymax):
            fw.write("\n# %s:\n" % nam)
            for key in sorted(pc.iterkeys()):
                fw.write("%f   %f\n" % (key, pc[key]))
            fw.write("$\n")
        for nam, pc in ("road energy x", self.roadenx), ("road energy y", self.roadeny):
            fw.write("\n# %s:\n" % nam)
            for key in sorted(pc.iterkeys()):
                val = pc[key]
                fw.write("%f  %f   %f  %f  %f  %f\n" % (key[0], key[1], val[0], val[1], val[2], val[3]))
            fw.write("$\n")

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


    def read_cache(self, fr):
        "Read RoadGrid from a file (like) object."
        self.hull = []
        self.dx = self.dy = 1.0
        self.dtheta = 1.0
        self.roadenx = {}
        self.roadeny = {}
        self.pxmin = {}
        self.pxmax = {}
        self.pymin = {}
        self.pymax = {}
        self.contours = []
        self.uxmin = self.uxmax = self.uymin = self.uymax = None
        it = itercom(fr)

        while True:
            dl = it.next().split()
            if dl[0] == "$": break
            ca = map(float, dl)
            self.hull.append(ca)

        self.dx, self.dy, self.dtheta = map(float, it.next().split())

        for nam, pc in ("pxmin", self.pxmin), ("pxmax", self.pxmax), ("pymin", self.pymin), ("pymax", self.pymax):
            while True:
                dline = it.next()
                if dline == "$": break
                key, val = map(float, dline.split())
                pc[key] = val

        for nam, pc in ("road energy x", self.roadenx), ("road energy y", self.roadeny):
            while True:
                dline = it.next()
                if dline == "$": break
                key1, key2, val1, val2, val3, val4 = map(float, dline.split())
                pc[key1, key2] = val1, val2, val3, val4

        while True:
            dl = it.next().split()
            if dl[0] == "$": break
            ca = map(float, dl)
            lin = [ca[:3], ca[3:]]
            self.contours.append(lin)
        self.uxmin, self.uxmax, self.uymin, self.uymax = map(float, it.next().split())

        self.changed += 1     #Object has been modified


    def iterOT(self, state):
        "Iterate through all city blocks of the city plan (OT)."
        t = cos(state.theta*pi/180.0), sin(state.theta*pi/180.0)
        n = -t[1], t[0]
        px = [t[0]*c[0]+t[1]*c[1] for c in self.hull]
        py = [n[0]*c[0]+n[1]*c[1] for c in self.hull]
        pxmin = min(px)
        pxmax = max(px)
        pymin = min(py)
        pymax = max(py)

#        print "bod=", state.bod
#        print "boik=", state.boik
#        print "hoik=", state.hoik

        pya = pymin
        jy = jjy = 0
        while True:
            pya += state.bod[jjy]
            pyb = pya+state.boik[jjy]
            if pyb > pymax: break
            ca1, ca2 = thanPolygonLine(self.hull, pya, n)
            assert ca1 != None, "There should be 2 intersections!"
            cb1, cb2 = thanPolygonLine(self.hull, pyb, n)
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


    def energy(self, s):
        "Calculates the energy of the road grid described in state s, using the built cache."
        sd, sd8, sd10, se = self.roadenergy(self.roadenx, self.dy, s.theta, self.pymin, self.pymax, s.boik, s.bod)
        d, d8, d10, e     = self.roadenergy(self.roadeny, self.dx, s.theta, self.pxmin, self.pxmax, s.hoik, s.bod)
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
            pyaxis = int(pyaxis/dy+0.5)*dy
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
            c1, c2 = thanPolygonLine(self.hull, pyaxis, n)
            assert c1 != None, "There should be 2 intersections!"
            roads.append((c1, c2))
            py += bod[jj] + boik[jj]
            j += 1
            if j < len(boik): jj = j


    def tochart(self, ch, hulls=(), iso=(), ot=(), roads=(), colot="blue"):
        "Draw the road grid into a ThanChart."
        for lines, col, _ in self.itlines(hulls, iso, ot, roads, colot):
            if lines == None: continue
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
        "Draw the road grid into a PIL image."
        g2li = ct.global2Locali
        for lines, col, _ in self.itlines(hulls, iso, ot, roads, colot):
            if lines == None: continue
            for line1 in lines:
                cc = [g2li(c[0], c[1]) for c in line1]
                imd.line(cc, fill=col)

    def todxf(self, dxf, title="", hulls=(), iso=(), ot=(), roads=(), colot="blue", xor=0.0, yor=0.0):
        "Draw the road grid into a dxf file."
        from p_gimdxf.thancolors import thanDxfColName2Rgb, thanRgb2DxfColCodeApprox
        for lines, col, laynam in self.itlines(hulls, iso, ot, roads, colot):
            if lines == None: continue
            for line1 in lines:
                xx = [xor+c[0] for c in line1]
                yy = [yor+c[1] for c in line1]
                _layer(dxf, laynam, col)
                dxf.thanDxfPlotPolyline(xx, yy)
        dy = (self.uymax-self.uymin)/100.0*5.0
        _layer(dxf, "TITLE", "white")
        dxf.thanDxfPlotSymbol(xor+self.uxmin+1.0*dy, yor+self.uymax+1.0*dy, dy, title, 0.0)

    def show(self, title="", iso=(), ot=(), roads=(), colot="blue"):
        "Draw the road grid into a ThanChart and shoi it on screen."
        ch = p_gchart.ThanChart(title)
        self.tochart(ch, (self.hull,), iso, ot, roads, colot)
        p_gchart.vis(ch, bg="white")

    def pilout(self, title="", width=600, height=400, iso=(), ot=(), roads=(), colot="blue"):
        "Create an image and draw the road grid into this image."
        ct = self._pilct(width, height, (self.hull,), iso, ot, roads, colot)
        im = Image.new("RGB", (width, height), (255,255,255))
        imd = ImageDraw.Draw(im)
        self.topil(imd, ct, (self.hull,), iso, ot, roads)
        imd.text((5,1), text=title, fill=colot)
        return im, ct

    def _pilct(self, width=600, height=400, hulls=(), iso=(), ot=(), roads=(), colot="blue"):
        "Find the scale of the configuration to fill into an image of width x height."
        from p_gmath import ThanRectCoorTransf
        xmin = ymin = 1.0e100
        xmax = ymax = -ymin
        for lines, _, _ in self.itlines(hulls, iso, ot, roads, colot):
            if lines == None: continue
            for line1 in lines:
                for c in line1:
                    if c[0] < xmin: xmin = c[0]
                    if c[0] > xmax: xmax = c[0]
                    if c[1] < ymin: ymin = c[1]
                    if c[1] > ymax: ymax = c[1]
        assert xmin<xmax and ymin<ymax, "No hull, iso, ot, roads!"
        ct = ThanRectCoorTransf((xmin, ymin, xmax, ymax), (5, height-5, width-5, 5))
        return ct

    def dxfout(self, title="", iso=(), ot=(), roads=(), colot="blue"):
        "Create a .dxf file and Draw the road grid into this dxf file."
        from p_gdxf import ThanDxfPlot
        dxf = ThanDxfPlot()
        dxf.thanDxfPlots()
        self.todxf(dxf, title, (self.hull,), iso, ot, roads, colot)
        dxf.thanDxfPlot(0,0,999)


def itercom(fr):
    "Iterates through a file ignoring comments."
    for dl in fr:
        dl = dl.strip()
        if dl == "" or dl[0] == "#": continue
        yield dl



def thanPolygonLine(cpol, pn, n):
    "Finds the intersection between convex polygon segment and line perpendicular to n, whose projection on n axis is pn."
    cts = []
    for i in xrange(len(cpol)):
        ct = thanLineSeg3(pn, n, cpol[i-1], cpol[i])
        if ct != None: cts.append(ct)
    if len(cts) == 0: return None, None
    cts.sort()
    j = 1
    while j < len(cts):
        i = j - 1
        if thanNear2(cts[j], cts[i]):
            del cts[j]
        else:
            j += 1
    assert len(cts) == 2, "There should be exactly 2 intersections"
    return cts[0], cts[1]


def lineprofile(clines):
    "Creates all roads' profiles as separate charts; debugging aid; not currently used."
    dfact = 0.1
    charts = []
    for cp,pyaxis,col in clines:
        d = [0.0*dfact]
        for ca, cb in p_ggen.iterby2(cp):
            d.append(d[-1]+hypot(cb[1]-ca[1], cb[0]-ca[0])*dfact)
        zmin = min(ca[2] for ca in cp)
        ch = p_gchart.ThanChart()
        ch.curveAdd((d[0], d[-1]), (0.0, 0.0), color=col)
        ch.curveAdd((d[0], d[0]), (0.0, cp[0][2]-zmin))
        for i in xrange(1, len(cp)):
            ch.curveAdd((d[i], d[i], d[i-1]), (0.0, cp[i][2]-zmin, cp[i-1][2]-zmin), color=col)
        charts.append(ch)
    return charts


def _layer(dxf, lay, col):
    "Sets layer and color."
    from p_gimdxf.thancolors import thanDxfColName2Rgb, thanRgb2DxfColCodeApprox
    rgb = thanDxfColName2Rgb[col]
    icol = thanRgb2DxfColCodeApprox(rgb)
    dxf.thanDxfSetLayer(lay)
    dxf.thanDxfSetColor(icol)
