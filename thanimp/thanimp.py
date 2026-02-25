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

This module defines an object which reads a .syk, .brk, .syn, .lin  file and it
creates the appropriate ThanCad's elements to represent it in ThanCad.
"""

import cPickle
from thanvar import ThanImportError
from thantrans import T


class ThanImportBase:
    "A class to import a syk,mhk,brk,syn file based on dxf library emulation."

    def __init__(self, fDxf, dr, defaultLayer="0"):
        "Creates an instance of the class."
        self.thanCancel = 0
        self.__fullBuf = 0
        self._lindxf = 0

        self.thanDr = dr
        self.fDxf = fDxf
        self.defLay = defaultLayer

    def _waFile1(self, s):
        "Prints a warning."
        s1 = "%s %d: %s" % (T["Warning at line"], self._lindxf, s)
        self.thanDr.prt(s1, "can1")


class ThanImportSyk(ThanImportBase):
    "A class to import a syk file."

    def thanImport(self):
        "Imports a dxf file."
        self._getPolylines()


    def _getPolylines(self):
        "Reads all polylines from .syk file."
        handle = ""
        while 1:
            s = self.fDxf.readline()
            if s == "": return                    # End Of File
            self._lindxf += 1
	    if s[:15].strip() == "":
	        z1 = self.thanDr._elev[2]
	    else:
	        try:
	            z1 = float(s[:15])
   	        except (ValueError, IndexError), why:
		    why = "%s %d:\n%s" % (T["Error at line"], self._lindxf, why)
		    raise ThanImportError, why
	    lay = s[17:].strip()
	    if lay != "" and lay[0] != ".": self.defLay = lay.replace(" ", "_")
	    else:                           lay = self.defLay
	    xx = []; yy = []; zz = []

#-----------Read coordinates of polyline

	    while 1:
                s = self.fDxf.readline()
                if s == "": break                 # End Of File
                self._lindxf += 1

                s = s.strip()
                if s == "$": break
	        try:
	            sl = s.split()
		    x1 = float(sl[0])
		    y1 = float(sl[1])
	        except (ValueError, IndexError), why:
		    why = "%s %d:\n%s" % (T["Error at line"], self._lindxf, why)
		    raise ThanImportError, why
	        else: xx.append(x1); yy.append(y1); zz.append(z1)

#-----------Store the polyline

            if len(xx) < 2: self._waFile1("Polyline with 1 or 0 vertices.")
            self.thanDr.dxfPolyline(xx, yy, zz, lay, handle, None)


class ThanImportBrk(ThanImportSyk):
    "A class to import a brk file."

    def thanImport(self):
        "Imports a dxf file."
        self._getPolylines()

    def _getPolylines(self):
        "Reads all polylines from .brk file."
	handle = ""
        while 1:
	    xx = []; yy = []; zz = []

#-----------Read coordinates of polyline

	    while 1:
                s = self.fDxf.readline()
                if s == "": break                 # End Of File
                self._lindxf += 1

                if s.strip() == "$": break
	        try:
		    x1 = float(s[10:25])
		    y1 = float(s[25:40])
		    sl = s[40:55].strip()
		    if sl != "": z1 = float(sl)
		    else:        z1 = self.thanDr._elev[2]
	        except (ValueError, IndexError), why:
		    why = "%s %d:\n%s" % (T["Error at line"], self._lindxf, why)
		    raise ThanImportError, why
	        else: xx.append(x1); yy.append(y1); zz.append(z1)

#-----------Store the polyline

            if s == "" and len(xx) == 0: return    # Normal end
            if len(xx) < 2: self._waFile1("Polyline with 1 or 0 vertices.")
            self.thanDr.dxfPolyline(xx, yy, zz, self.defLay, handle, None)
	    if s == "": return      # Sentinel not found at end of file; not normal, but OK


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
        while 1:
            s = self.fDxf.readline()
            if s == "": break                     # End Of File
            self._lindxf += 1

            try:
                aa = s[:10].rstrip()
                xx = float(s[10:25])
                yy = float(s[25:40])
                zz = float(s[40:55])
                t1 = s[55:57].strip()
                validc[2] = t1 == ""
            except (ValueError, IndexError), why:
                why = "%s %d:\n%s" % (T["Error at line"], self._lindxf, why)
                raise ThanImportError, why
            if validc[2]:
                self.thanDr.dxfPoint(xx, yy, zz, self.defLay, handle, None, aa, validc)
            else:
                nzn += 1
                self.thanDr.dxfPoint(xx, yy, zz, nzLay,       handle, None, aa, validc)

        if nzn > 0:
            self.prt(T["%d points with invalid z were put into layer %s."] % (nzn, nzLay))


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
            except Exception(), why:
                raise ThanImportError, why

        if nzn > 0:
            self.prt(T["%d unknown elements were not imported"] % nzn)


if __name__ == "__main__":
    print __doc__
