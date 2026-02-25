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

This module defines an object which reads a .syk, .brk, .syn, .lin  file and it
creates the appropriate ThanCad's elements to represent it in ThanCad.
"""

import cPickle
from p_gimdxf import ThanImportBase
from thantrans import T


class ThanImportSyk(ThanImportBase):
    "A class to import a syk file."

    def thanImport(self):
        "Imports a dxf file."
        self._getPolylines()


    def _getPolylines(self):
        "Reads all polylines from .syk file."
        handle = ""
        while True:
            s = self.thanGetDxf()
            if s == "": return                    # End Of File
            if s[:15].strip() == "":
                z1 = self.thanDr._elev[2]
            else:
                try:
                    z1 = float(s[:15])
                except (ValueError, IndexError), why:
                    self.thanEr1s(why)
            lay = s[17:].strip()
            if lay != "" and lay[0] != ".": self.defLay = lay.replace(" ", "_")
            else:                           lay = self.defLay
            xx = []
            yy = []
            zz = []
#-----------Read coordinates of polyline
            while True:
                s = self.thanGetDxf()
                if s == "": break                 # End Of File
                s = s.strip()
                if s == "$": break
                try:
                    sl = s.split()
                    x1 = float(sl[0])
                    y1 = float(sl[1])
                except (ValueError, IndexError), why:
                    self.thanEr1s(why)
                else:
                    xx.append(x1)
                    yy.append(y1)
                    zz.append(z1)
#-----------Store the polyline
            if len(xx) < 2: self.thanWarn(T["Polyline with 1 or 0 vertices."])
            self.thanDr.dxfPolyline(xx, yy, zz, lay, handle, None)


class ThanImportBrk(ThanImportSyk):
    "A class to import a brk file."

    def thanImport(self):
        "Imports a dxf file."
        self._getPolylines()

    def _getPolylines(self):
        "Reads all polylines from .brk file."
        handle = ""
        while True:
            xx = []
            yy = []
            zz = []
#-----------Read coordinates of polyline
            while True:
                s = self.thanFetDxf()
                if s == "": break                 # End Of File
                if s.strip() == "$": break
                try:
                    x1 = float(s[10:25])
                    y1 = float(s[25:40])
                    sl = s[40:55].strip()
                    if sl != "": z1 = float(sl)
                    else:        z1 = self.thanDr._elev[2]
                except (ValueError, IndexError), why:
                    self.thanEr1s(why)
                else:
                    xx.append(x1)
                    yy.append(y1)
                    zz.append(z1)
#-----------Store the polyline
            if s == "" and len(xx) == 0: break    # Normal end of file
            if len(xx) < 2: self.thanWarn(T["Polyline with 1 or 0 vertices."])
            self.thanDr.dxfPolyline(xx, yy, zz, self.defLay, handle, None)
            if s == "": break     # Sentinel not found at end of file; not normal, but OK


class ThanImportSyn(ThanImportBase):
    "A class to import 3d points from a .syn file."

    def thanImport(self):
        "Imports a dxf file."
        self._getPoints()


    def _getPoints(self):
        "Reads all points from .syn file."
        nzLay = "nohs"                            # Layer for points with invalid z
        nzn = 0
        handle = ""
        validc = [True, True, True]
        while True:
            s = self.thanGetDxf()
            if s == "": break                     # End Of File
            try:
                aa = s[:10].rstrip()
                xx = float(s[10:25])
                yy = float(s[25:40])
                sl = s[40:55]
                if sl != "": z1 = float(sl)
                else:        z1 = 0.0             #Consistency with other programs
                t1 = s[55:57].strip()
                validc[2] = t1 == ""
            except (ValueError, IndexError), why:
                self.thanEr1s(why)
            if validc[2]:
                self.thanDr.dxfPoint(xx, yy, zz, self.defLay, handle, None, aa, validc)
            else:
                nzn += 1
                self.thanDr.dxfPoint(xx, yy, zz, nzLay,       handle, None, aa, validc)
        if nzn > 0:
            self.prt(T["%d points with invalid z were put into layer %s."] % (nzn, nzLay), "info1")


class ThanImportLin(ThanImportBase):
    "A class to import elements from a Linicad file."

    def thanImport(self):
        "Imports a LiniCad file."
        self._getElems()


    def _getElems(self):
        "Reads all elements from .lin file."
        nzn = 0
        handle = ""
        while True:
            try:
                try: typ = cPickle.load(self.fDxf)
                except EOFError: break
                coords = cPickle.load(self.fDxf)
                n = len(coords)
                if n % 2 != 0: n -= 1
                xx = []
                yy = []
                zz = []
                for i in xrange(0, n, 2):
                    xx.append(float(coords[i]))
                    yy.append(float(coords[i+1]))
                    zz.append(0.0)
                if typ == "line":
                    if n < 4: continue
                    self.thanDr.dxfLine(xx, yy, zz, "lines", handle, 3)
                elif typ == "oval":
                    if n != 4: continue
                    r = fabs(yy[1]-yy[0]) / 2.0
                    xc = (xx[0]+xx[1])*0.5
                    yc = (yy[0]+yy[1])*0.5
                    self.thanDr.dxfCircle(xc, yc, 0.0, "circles", handle, 1, r)
                elif typ == "text":
                    ttext, stext = cPickle.load(self.fDxf)
                    self.thanDr.dxfText(xx[0], yy[0], zz[0], "texts", handle, 2, ttext, stext, 0.0)
                else:
                    nzn += 1
            except Exception, why:
                self.thanEr1s(why)
        if nzn > 0:
            self.thanWarn(T["%d unknown elements were not imported"] % nzn)


class ThanImportXyzIntermap(ThanImportSyk):
    """A class to import lines in xyz intergraph format.

    Sample file:
4.82389617, 43.70650056, 6.03, 1, 0, 2,  65, 3, 205, 4,  64
4.82397371, 43.70647268, 6.00, 1, 0, 2,  75, 3, 205, 4,  65
4.82401268, 43.70645878, 5.99, 1, 0, 2,  66, 3, 205, 4,  66
4.82405164, 43.70644487, 5.97, 1, 0, 2,  64, 3, 205, 4,  67
4.82412769, 43.70641773, 5.95, 1, 0, 2,  64, 3, 205, 4,  69

4.82435982, 43.70633794, 5.89, 1, 0, 2,  54, 3, 201, 4,  75
4.82439608, 43.70632548, 5.89, 1, 0, 2,  57, 3, 201, 4,  75
4.82443574, 43.70631266, 5.88, 1, 0, 2,  54, 3, 201, 4,  73

4.84752910, 43.69468043, 12.53, 1, 0, 2,  77, 3, 201, 4,  60
4.84757154, 43.69467380, 12.55, 1, 0, 2,  79, 3, 201, 4,  63
4.84761399, 43.69466717, 12.58, 1, 0, 2,  84, 3, 201, 4,  65
    The first 3 number are x, y, z. Here the x and y are in reality
    geodetic coordinates in the ETRS89 datum and z is orthometric heigh_horizontal>
    with the EGG07 geoid (this info is acquired by the accompanying .xml file).
    """

    def thanImport(self):
        "Imports a dxf file."
        self._getPolylines()

    def _getPolylines(self):
        "Reads all polylines from .brk file."
        handle = ""
        while 1:
            xx = []
            yy = []
            zz = []
#-----------Read coordinates of polyline
            while 1:
                s = self.thanGetDxf()
                if s == "": break                 # End Of File

                if s.strip() == "": break
                try:
                    x1, y1, z1 = map(float, s.split(",")[:3])
                except (ValueError, IndexError), why:
                    self.thanEr1s(why)
                else:
                    xx.append(x1)
                    yy.append(y1)
                    zz.append(z1)
#-----------Store the polyline
            if s == "" and len(xx) == 0: break    # Normal end of file
            if len(xx) < 2: self.thanWarn(T["Polyline with 1 or 0 vertices."])
            self.thanDr.dxfPolyline(xx, yy, zz, self.defLay, handle, None)
            if s == "": break     # Sentinel not found at end of file; not normal, but OK


if __name__ == "__main__":
    print __doc__
