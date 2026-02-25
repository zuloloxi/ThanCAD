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

This module implements an engineering grid used in surveys.
"""


from math import sqrt, fabs, pi
from p_ggen import frange, prg
import p_ggeom
from thandr import ThanLine, ThanText

#win = None
#xx1 = 0.0
#yy1 = 0.0

class ThanGrid(object):
    """A utility which plots grid points within a given rectangle.

    Normally the application need not be a class. But in the future, multiple
    drawings in various states may be open in a ThanCad server. Thus ThanGrid may
    be reentrant, which means that the global variables should actually be
    independent object variables.
    """

    def thanDo(self, proj, akl, dx, dy, ikan, cp):
        "Make grid within the given rectangle."
        self.cc1 = list(proj[1].thanVar["elevation"])
        self.proj = proj
        xp = [c[0] for c in cp]
        yp = [c[1] for c in cp]
        m = p_ggeom.MesaQuad((xp[0],yp[0]),(xp[1],yp[1]),(xp[2],yp[2]),(xp[3],yp[3]))
        self.pin(akl, xp, yp, dx, dy, ikan, m)
        del self.proj

#========================================================================

    def pin(self, akl, xp, yp, dx, dy, ikan, m):
        "Draws grid points (with coordinates) inside a convex 4-node polygon."
        xmin = min(xp)
        ymin = min(yp)
        xmax = max(xp)
        ymax = max(yp)

        ak  = akl / 10.0
        hkn = 1.0 * akl / 100.0
        hs  = 0.2 * akl / 100.0

        xarx = ak * int(xmin/ak)
        if xarx < 0.0: xarx -= ak
        yarx = ak * int(ymin/ak)
        if yarx < 0.0: yarx -= ak

#-------Find grid points inside the polygon

        for xkn in frange(xarx-ak, xmax, ak):
            for ykn in frange(yarx-ak, ymax, ak):
                if m.mesa((xkn, ykn)):
                    self.cross(xkn, ykn, hkn)
                    if akont(xp, yp, xkn, ykn) < ak or ikan == 2:
                        dk = hkn * 0.5 * 1.2
                        self.number(xkn+dk, ykn,   hs, ykn+dy, 0.0, -1)
                        self.number(xkn,    ykn+dk,hs, xkn+dx, 90.0,-1)


    def cross(self, xx, yy, h):
        "Draws a cross."
        hh = h * 0.5
        self.plot(xx-hh, yy,    3)
        self.plot(xx+hh, yy,    2)
        self.plot(xx,    yy-hh, 3)
        self.plot(xx,    yy+hh, 2)

    def plot (self, xx, yy, ipen):
        "Simulates plot function of original grid program."
        cc = list(self.proj[1].thanVar["elevation"])
        cc[:2] = xx, yy
        if ipen == 2:
            e = ThanLine()
            e.thanSet([self.cc1, cc])
            self.proj[1].thanElementAdd(e)
            item = e.thanTkDraw(self.proj[2].than)
        self.cc1 = cc

    def number(self, xx, yy, hs, a, thet, n):
        "Simulates number drawing function of original grid program."
        cc = list(self.proj[1].thanVar["elevation"])
        cc[:2] = xx, yy
        if n < 0:
            t = str(int(a))
        else:
            f = "%%%dd" % n
            t = f % a
        e = ThanText()
        e.thanSet(t, cc, hs, thet*pi/180)
        self.proj[1].thanElementAdd(e)
        item = e.thanTkDraw(self.proj[2].than)

    def __del__(self):
        "Inform that grid died for debugging reasons."
        prg("thaneng.ThanGrid %s is deleted" % self)

def akont(xp, yp, xx, yy):
    "Test if grid point is near the polygon boundary."
    am = 1.0e30
    for i in range(4):
        j = (i + 1) % 4
        ap = apos(xp[i], yp[i], xp[j], yp[j], xx, yy)
        if ap < am: am = ap
    return am

def apos(xp1, yp1, xp2, yp2, xx, yy):
    "Computes perpendicular distance of a grid point from a line."

#-----compute outward normal

    dx=xp2-xp1
    dy=yp2-yp1
    d=sqrt(dx*dx+dy*dy)
    dx=dx/d
    dy=dy/d
    an2=dx
    an1=-dy

#-----compute distance

    dx = xx - xp1
    dy = yy - yp1
    return fabs(dx*an1 + dy*an2)


if __name__ == "__main__":
    print(__doc__)
