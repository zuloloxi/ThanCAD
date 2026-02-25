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

This module defines objects which read spreadsheet files (.xls, .xlsx, .ods)
for points, lines, texts or surface and create the appropriate ThanCad's elements.
"""

from p_gimdxf import ThanImportBase
from thantrans import T
from p_gspread import ThanXlsReader, ThanXlsxReader


class ThanImportSpread(ThanImportBase):
    "A producer mixin class to read point coordinates etc from a spreadsheet; xls/xlsx agnostic."

    def iteraxyz_old(self, sh, rd):
        """Iterate through all the point coordinates in the xls file: aa, x, y, z.

        icod is 0 if a point was found, 1 if empty line was found or 2 if syntax
        error or empty cell."""
        ztoo = sh.ncols > 3
        for i in range(sh.nrows):
            self._lindxf = i+1
            empty = rd.isEmpty(sh, i, 0) and rd.isEmpty(sh, i, 1) and rd.isEmpty(sh, i, 2)
            if ztoo: empty = empty and rd.isEmpty(sh, i, 3)
            if empty:
                yield 1, None, None, None, None
            else:
                aa = rd.toString(sh, i, 0)
                x = rd.toFloat(sh, i, 1)
                y = rd.toFloat(sh, i, 2)
                z = rd.toFloat(sh, i, 3) if ztoo else 0.0
                icod = 2 if x is None or y is None or z is None else 0
                yield icod, aa, x, y, z


    def iteraxyz(self, sh, rd):
        """Iterate through all the point coordinates in the xls file: aa, x, y, z.

        icod is 0 if a point was found, or 1 if empty line was found or 2 if syntax
        error or empty coordinates cell, or 3 if no error but z is not defined.
        If names is not defined, name is set to blank."""
        ztoo = sh.ncols > 2
        aatoo = sh.ncols > 3
        for i in range(sh.nrows):
            self._lindxf = i+1
            if rd.toString(sh, i, 0).strip().startswith("#"): continue   #Ignore comments
            empty = rd.isEmpty(sh, i, 0) and rd.isEmpty(sh, i, 1)
            if ztoo:  empty = empty and rd.isEmpty(sh, i, 2)
            if aatoo: empty = empty and rd.isEmpty(sh, i, 3)
            if empty:
                yield 1, None, None, None, None
            else:
                noz = not ztoo or rd.isEmpty(sh, i, 2)
                x = rd.toFloat(sh, i, 0)
                y = rd.toFloat(sh, i, 1)
                z = 0.0 if noz else rd.toFloat(sh, i, 2)
                aa = rd.toString(sh, i, 3).rstrip() if aatoo else ""
                if x is None or y is None or z is None:
                    icod = 2       #One or more corrdinated ar not numbers
                elif noz:
                    icod = 3       #No z defined (z=0.0 is assumed)
                else:
                    icod = 0
                yield icod, aa, x, y, z


    def itertexts(self, sh, rd):
        """Iterate through all the text definitions: x, y, size, theta, text.

        icod is 0 if a text was found, 1 if empty line was found or 2 if syntax
        error or empty cell."""
        for i in range(sh.nrows):
            self._lindxf = i+1
            empty = rd.isEmpty(sh, i, 0) and rd.isEmpty(sh, i, 1) and rd.isEmpty(sh, i, 2) \
                and rd.isEmpty(sh, i, 3) and rd.isEmpty(sh, i, 4)
            if empty:
                yield 1, None, None, None, None, None
            else:
                x = rd.toFloat(sh, i, 0)
                y = rd.toFloat(sh, i, 1)
                sizet = rd.toFloat(sh, i, 2)
                theta = rd.toFloat(sh, i, 3)
                text = rd.toString(sh, i, 4)
                icod = 2 if x is None or y is None or sizet is None or theta is None else 0
                yield icod, x, y, sizet, theta, text


    def iterxyz(self, sh, rd):
        """Iterate through all the point coordinates in the xls file: x, y, z.

        icod is 0 if a point was found, 1 if empty line was found or 2 if syntax
        error or empty cell."""
        ztoo = sh.ncols > 2
        for i in range(sh.nrows):
            self._lindxf = i+1
            empty = rd.isEmpty(sh, i, 0) and rd.isEmpty(sh, i, 1)
            if ztoo: empty = empty and rd.isEmpty(sh, i, 2)
            if empty:
                yield 1, None, None, None
            else:
                x = rd.toFloat(sh, i, 0)
                y = rd.toFloat(sh, i, 1)
                z = rd.toFloat(sh, i, 2) if ztoo else 0.0
                icod = 2 if x is None or y is None or z is None else 0
                yield icod, x, y, z


    def iterfloats(self, sh, rd):
        """Iterate through all lines of xls file and convert all cell values to floats.

        icod is 0 if valid floats were found in a line, 1 if an empty line was found or
        2 if syntax error or empty cell."""
        for i in range(sh.nrows):
            self._lindxf = i+1
            if all(rd.isEmpty(sh, i, j) for j in range(sh.ncols)): yield 1, None
            vs = [rd.toFloat(sh, i, j) for j in range(sh.ncols)]
            if any(v is None for v in vs): yield 2, vs
            yield 0, vs


    def thanImportPoints(self):
        "Import points from a spreadsheet."
        if self.fDxf.name.endswith(".xls"): rd = ThanXlsReader()
        else:                               rd = ThanXlsxReader()
        book, sh = rd.openSpread(self.fDxf.name, 1, 2, self.thanDr.prt, self.thanEr2s) #may raise ThanImportError
        np = 0
        handle = ""
        self.defLay = "sh"    #Change default layer from "0" to "sh"
        for icod, aa, x, y, z in self.iteraxyz(sh, rd):
            if icod == 1:
                self.thanWarn(T["blank row is ignored."])
            elif icod == 2:
                self.thanWarn(T["x, y or z is not a number. Point is ignored."])
            elif aa == "":
                self.thanDr.dxfPoint(x, y, z, self.defLay, handle, None)    #Anonymous point
            else:
                validc = [True, True, True]
                if icod == 3: validc[2] = False
                self.thanDr.dxfPoint(x, y, z, self.defLay, handle, None, aa, validc)  #named point
                np += 1
        lay = self.thanDr._dr.thanLayerTree.thanFindic(self.defLay)
        if lay is not None: #this check is needed, because: in the case that self.defLay != "0"
                            # and no points were added, self.defLay has not been created and thus lay=None
            lay.thanAtts["hidename"].thanValSet(False)
            if sh.ncols > 3: lay.thanAtts["hideheight"].thanValSet(False)
        if sh.ncols > 3:
            self.thanDr.prt(T["{} points imported (out of {} spreadsheet rows)"].format(np, sh.nrows), "info")
        else:
            self.thanDr.prt(T["{} points (with no z) imported (out of {} spreadsheet rows)"].format(np, sh.nrows), "info")

        rd.closeSpread(book, sh)
        del sh, book


    def thanImportTexts(self):
        "Import texts from a spreadsheet."
        if self.fDxf.name.endswith(".xls"): rd = ThanXlsReader()
        else:                               rd = ThanXlsxReader()
        book, sh = rd.openSpread(self.fDxf.name, 1, 5, self.thanDr.prt, self.thanEr2s)
        np = 0
        handle = ""
        for icod, x, y, sizet, theta, text in self.itertexts(sh, rd):
            if icod == 1:
                self.thanWarn(T["blank row is ignored."])
            elif icod == 2:
                self.thanWarn(T["x, y, size or theta is not a number. Text is ignored."])
            else:
                self.thanDr.dxfText(x, y, 0.0, self.defLay, handle, None, text, sizet, theta)
                np += 1

        self.thanDr.prt(T["{} texts imported (out of {} spreadsheet rows)"].format(np, sh.nrows), "info")

        rd.closeSpread(book, sh)
        del sh, book


    def thanImportLines(self):
        "Import lines from a spreadsheet."
        if self.fDxf.name.endswith(".xls"): rd = ThanXlsReader()
        else:                               rd = ThanXlsxReader()
        book, sh = rd.openSpread(self.fDxf.name, 1, 2, self.thanDr.prt, self.thanEr2s)
        handle = ""
        xx = []
        yy = []
        zz = []
        for icod, x, y, z in self.iterxyz(sh, rd):
            if icod == 1:
                if len(xx) > 0:
                    self.thanDr.dxfPolyline(xx, yy, zz, self.defLay, handle, None)
                    xx = []
                    yy = []
                    zz = []
            elif icod == 2:
                self.thanEr1s(T["x, y or z is not a number."])
            else:
                xx.append(x)
                yy.append(y)
                zz.append(z)
        if len(xx) > 0:
            self.thanDr.dxfPolyline(xx, yy, zz, self.defLay, handle, None)

        rd.closeSpread(book, sh)
        del sh, book


    def thanImportSurface(self):
        """Import surface from a spreadsheet."

        The surface is defined as z values of a grid with possibly variable step.
        The first row contains the x value of each column, and the first column
        contains the y values of each row.
        The surface is imported as a set of neiboring 3dfaces.
        """

        if self.fDxf.name.endswith(".xls"): rd = ThanXlsReader()
        else:                               rd = ThanXlsxReader()
        book, sh = rd.openSpread(self.fDxf.name, 3, 3, self.thanDr.prt, self.thanEr2s)
        handle = ""
        #First line contains the x coordinates of all columns
        it = self.iterfloats(sh, rd)
        icod, xs = next(it)
        if icod == 1:
            self.thanEr1s(T["Blank row found."])
        elif icod == 2:
            if any(x is None for x in xs[1:]): #First cell may be blank or may contain anything
                self.thanEr1s(T["Some cells do not contain numbers."])
        #Second line contains the first set of z values
        icod, vsa = next(it)
        if icod == 1:
            self.thanEr1s(T["Blank row found."])
        elif icod == 2:
            self.thanEr1s(T["Some cells do not contain numbers."])
        #Iterate through 3rd line to end
        for icod, vsb in it:
            if icod == 1:
                self.thanEr1s(T["Blank row found."])
            elif icod == 2:
                self.thanEr1s(T["Some cells do not contain numbers."])
            ya = vsa[0]
            yb = vsb[0]
            for j in range(2, sh.ncols):
                xa = xs[j-1]
                xb = xs[j]
                xx = xa,       xb,     xb,     xa
                yy = ya,       ya,     yb,     yb
                zz = vsa[j-1], vsa[j], vsb[j], vsb[j-1]
                self.thanDr.dxf3dface(xx, yy, zz, self.defLay, handle, None)
            vsa = vsb

        rd.closeSpread(book, sh)
        del sh, book


class ThanImportXlsPoints(ThanImportSpread):
    "A producer class to import (topographic) points from a spreadsheet xls file."
    def thanImport(self): self.thanImportPoints()


class ThanImportXlsTexts(ThanImportSpread):
    "A producer class to import texts a spreadsheet (xls/xlsx) file."
    def thanImport(self): self.thanImportTexts()


class ThanImportXlsLines(ThanImportSpread):
    "A producer class to import lines from a spreadsheet (xls/xlsx) file."
    def thanImport(self): self.thanImportLines()


class ThanImportXlsSurface(ThanImportSpread):
    "A producer class to import a surface from a spreadsheet (xls/xlsx) file."
    def thanImport(self): self.thanImportSurface()
