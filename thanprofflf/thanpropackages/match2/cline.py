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

This is the professional part of ThanCad which is initially commercial.
"""

from math import sqrt, fabs, atan2, hypot
from p_ggen import iterby2
from p_gmath import thanNear3

_DMIN = 0.001       # Default least distance between nodes
_DDIS = 0.2         # Default interpolation distance (or resolution) for points


class Cline(list):
    """A 3d curve represented by line segments.

    The cumulative distance is 3dimensional (it takes all x, y, z coordinates).
    This class can be used to represent 2d curves setting all the z coordinates
    to the same value."""
    __slots__ = ("centroid", )

    def __init__(self, points=None, zcommon=None, clean=False):
        """Build object, clean small segments and compute cumulative distance.

        If z != None, then the curve is 2dimensional and the z of all points
        are set to zcommon.
        It is safe if zero or 1 nodes are given."""
        if points == None: return    # readBrk or readAsc is expected
        self.__doinit(points, zcommon, clean)


    def __doinit(self, points, zcommon, clean):
        """Clean small segments and compute cumulative distance.

        If z != None, then the curve is 2dimensional and the z of all points
        are set to zcommon.
        It is safe if zero or 1 nodes are given."""
        if zcommon == None: self[:] = [ [b[0], b[1], b[2], None] for b in points]
        else:               self[:] = [ [b[0], b[1], zcommon, None] for b in points]
        if len(self) > 1:
            if clean: self.clean()
            else:     self.clean0()
        self.centroid = None
        if len(self) == 0:
            self[:] = [ [0.0, 0.0, 0.0, None] ]


    def isClosed(self):
        "Determine If the curve is closed."
        return thanNear3(self[0], self[-1])


    def length(self):
        "Returns length."
        if self[-1][3] == None: self.calcLength()
        return self[-1][3]


    def clean(self, dmin=_DMIN):
        """Erases all points whose distance is less than dmin.

        Ensure that the first and last poiiunt remain. This makes
        the test if the curve is closed easier.
        """
        dmin = dmin ** 2
        cp = self
        i = 1
        while i < len(cp)-1:
            if (cp[i][0]-cp[i-1][0])**2 + (cp[i][1]-cp[i-1][1])**2 + (cp[i][2]-cp[i-1][2])**2 < dmin:
                del cp[i]
            else:
                i += 1
        i = len(cp) - 1
        if (cp[i][0]-cp[i-1][0])**2 + (cp[i][1]-cp[i-1][1])**2 + (cp[i][2]-cp[i-1][2])**2 < dmin:
            del cp[i-1]


    def clean0(self):
        "Erases zero lengthed segments."
        cp = self
        i = 1
        while i < len(cp)-1:
            if thanNear3(cp[i], cp[i-1]): del cp[i]
            else:                         i += 1
        i = len(cp) - 1
        if thanNear3(cp[i], cp[i-1]): del cp[i-1]


    def calcLength(self):
        "Calculates distance between a, b, and cumulative distance."
        self[0][3] = 0.0
        for a, b in iterby2(self):
            d = sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2)
            b[3] = a[3] + d


    def calcCentroid_points(self, ddis=_DDIS):
        "Calculates the centroid of the line."
        from icp2 import iterdis3
        sum = [0.0, 0.0, 0.0]
        n = 0
        for a in iterdis3(self, ddis):
            for i in xrange(3): sum[i] += a[i]
            n += 1
        self.centroid = sum[0]/n, sum[1]/n, sum[2]/n


    def calcCentroid_lines(self):
        "Calculates the centroid of the line."
        if self[0][3] == None: self.calcLength()
        if len(self) < 2: return 0.0, 0.0, 0.0
        sum = [0.0, 0.0, 0.0]
        s =  0.0
        for a,b in iterby2(self):
            cc = [(a[i]+b[i])*0.5 for i in xrange(3)]
#            dd = hypot(b[0]-a[0], b[1]-a[1])
            dd = b[3]-a[3]              # 3d Distance between consecutive points
            for i in xrange(3): sum[i] += cc[i]*dd
            s += dd
        self.centroid = sum[0]/s, sum[1]/s, sum[2]/s


    def calcAzimouth(self, inode):
        "Calculates the azimouth from centroid to node."
        c = self.centroid
        a = self[inode]
        return atan2(a[1]-c[1], a[0]-c[0])


    def calcAvAzimouth(self, ddis=_DDIS):
        "Calculates the average azimouth from centroid, via unit vectors to avoid problems with angles."
        from icp2 import iterdis3
        sx = 0.0
        sy = 0.0
        c = self.centroid
        n = 0
        for a in iterdis3(self, ddis):
            dy = a[1]-c[1]
            dx = a[0]-c[0]
            dd = hypot(dx, dy)
            sx += dx/dd
            sy += dy/dd
            n += 1
        if n < 1: return 0.0
        dy = sy/n
        dx = sx/n
        dd = hypot(dy, dx)
        return atan2(dy/dd, dx/dd)


    def getPointlin(self, d, dmin=_DMIN):
        "Gets the point at distance d using linear interpolation and linear search."
        if self[0][3] == None: self.calcLength()
        dok = dmin/100.0   # If 2 points differ by this distance they are practically the same
        if d < self[0][3]-dok or d > self[-1][3]+dok:
            print d, ":", self[0][3], self[-1][3]
            raise ValueError, "Distance out of range"
        if d < self[0][3]: return tuple(self[0][:3])
        for i in xrange(1, len(self)):
            if d < self[i][3]: break
        else:
            return tuple(self[-1][:3])
        a, b = self[i-1:i+1]
        fact = (d-a[3]) / (b[3]-a[3])
        x = a[0] + (b[0]-a[0]) * fact
        y = a[1] + (b[1]-a[1]) * fact
        h = a[2] + (b[2]-a[2]) * fact
        return x, y, h


    def getPoint(self, d, dmin=_DMIN):
        "Gets the point at distance d using linear interpolation and binary search."
        if self[0][3] == None: self.calcLength()
        dok = dmin/100.0   # If 2 points differ by this distance they are practically the same
        if d < self[0][3]-dok or d > self[-1][3]+dok:
            print d, ":", self[0][3], self[-1][3]
            raise ValueError, "Distance out of range"
        if d <= self[0][3]:  return tuple(self[0][:3])
        if d >= self[-1][3]: return tuple(self[-1][:3])
        ia = 0
        ib = len(self) - 1
        while ib-ia > 1:
            i = (ia+ib)/2
            if d < self[i][3]: ib = i
            else:              ia = i
        a, b = self[ia:ia+2]
        fact = (d-a[3]) / (b[3]-a[3])
        x = a[0] + (b[0]-a[0]) * fact
        y = a[1] + (b[1]-a[1]) * fact
        h = a[2] + (b[2]-a[2]) * fact
        return x, y, h


    def readBrk(self, fr, zcommon=None, clean=False):
        "Reads the coordinates from an opened file .brk file; returns False if end of file."
        points = []
        for dline in fr:
            dline = dline.strip()
            if dline == "": continue
            if dline == "$":
                self.__doinit(points, zcommon, clean)
                return True
            dl = dline.split()
            points.append((float(dl[1]), float(dl[2]), float(dl[3])))
        self.__doinit(points, zcommon, clean)
        return False


    def readAsc(self, fr, zcommon=None, clean=False):
        "Reads the coordinates from a Datlin_opened .asc file; returns False if end of file."
        points = []
        icodp = None
        while fr.datLin(failoneof=False):
            icod = fr.datInt()
            if icodp != None and icod != icodp:
                fr.datLinbac()
                self.__doinit(points, zcommon, clean)
                return True
            self.append([fr.datFloat(), fr.datFloat(), fr.datFloat(), 0])
            icodp = icod
        self.__doinit(points, zcommon, clean)
        return False


    def dxfout(self, dxf):
        "Plots the curve into a ThanCad .dxf file."
        for x, y, z, d in self:
            dxf.thanDxfPlotPolyVertex3(x, y, z, 2)
        dxf.thanDxfPlotPolyVertex3(0, 0, 0, 999)


    def show(self, root=None):
        "Display the xy curve in a tk."
        from p_gchart import ThanChart, vis, viswin
        ch = ThanChart()
        self.add2chart(ch)
        if root == None: vis(ch)
        else:            viswin(root, ch)


    def add2chart(self, ch, *args, **kw):
        "Adds the curve to an existing ThanChart."
        xx = [a[0] for a in self]
        yy = [a[1] for a in self]
        ch.curveAdd(xx, yy, *args, **kw)


    def add2dxf(self, dxf, layer=None):
        "Adds the curve to an existing dxf object."
        if layer != None: dxf.thanDxfSetLayer(layer)
        xx = [a[0] for a in self]
        yy = [a[1] for a in self]
        dxf.thanDxfPlotPolyline(xx, yy)


##############################################################################
##############################################################################

def combine(rels, dmin=_DMIN):
    "Try to combine consecutive lines to bigger ones."
    while __combine1(rels, dmin): pass


def __combine1(rels, dmin):
    "Try to combine each curve with all of the rest."
    for i in xrange(0, len(rels)-1):
        for j in xrange(i+1, len(rels)):
            if __try2combine(rels, i, j, dmin): return True
    return False


def __try2combine(rels, i, j, dmin):
    "Try to combine curves i and j."
    dmin2 = dmin**2
    cla = rels[i]
    clb = rels[j]
    if   __eq(cla[-1], clb[0],  dmin2):
        cla.extend(clb)
    elif __eq(cla[-1], clb[-1], dmin2):
        clb.reverse()
        cla.extend(clb)
    elif __eq(cla[0],  clb[0],  dmin2):
        cla.reverse()
        cla.extend(clb)
    elif __eq(cla[0],  clb[-1], dmin2):
        clb.extend(cla)
        cla = clb
    else:
        return False

    del rels[j]
    cla.clean(dmin)
    cla.calcLength()
    rels[i] = cla
    return True


def __eq(cla, clb, dmin2):
    """If the distances of the nodes are smaller that sqrt(dmin2) then they are identical.

    Note that we talk about nodes, not interpolated points."""
    return (cla[0]-clb[0])**2 + (cla[1]-clb[1])**2 + (cla[2]-clb[2])**2 < dmin2


def testbin():
    "Tests the binary getpoint."
    c = Cline()
    c.readBrk(open("cline_test1.brk"))
    d = c.length()
    from p_ggen import xfrangec
    for d1 in xfrangec(0.0, d, 1.0):
        print d1
        x, y, z = c.getPointlin(d1)
        xb, yb, zb = c.getPoint(d1)
        if abs(x-xb)+abs(y-yb)+abs(z-zb) > 0.01:
            print d1
            print x, y, z
            print xb, yb, zb


if __name__ == "__main__":
    testbin()
