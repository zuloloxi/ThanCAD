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

This module defines an object which reads a .syk, .brk, .syn, .lin, .lcad,
Intergrapfh .xyz, kml, kmz file. It creates the appropriate ThanCad's elements
to represent the file in ThanCad.
"""

import pickle
from math import fabs, radians
from p_gimdxf import ThanImportBase
import p_gimgeo, p_gcol
from thantrans import T


class ThanImportSyk(ThanImportBase):
    "A producer class to import a syk file."

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
                except (ValueError, IndexError) as why:
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
                except (ValueError, IndexError) as why:
                    self.thanEr1s(why)
                else:
                    xx.append(x1)
                    yy.append(y1)
                    zz.append(z1)
#-----------Store the polyline
            if len(xx) < 2: self.thanWarn(T["Polyline with 1 or 0 vertices."])
            self.thanDr.dxfPolyline(xx, yy, zz, lay, handle, None)


class ThanImportBrk(ThanImportBase):
    "A producer class to import a brk file."

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
                s = self.thanGetDxf()
                if s == "": break                 # End Of File
                if s.strip() == "$": break
                try:
                    x1 = float(s[10:25])
                    y1 = float(s[25:40])
                    sl = s[40:55].strip()
                    if sl != "": z1 = float(sl)
                    else:        z1 = self.thanDr._elev[2]
                except (ValueError, IndexError) as why:
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
    "A producer class to import 3d points from a .syn file."

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
                if sl != "": zz = float(sl)
                else:        zz = 0.0             #Consistency with other programs
                t1 = s[55:57].strip()
                validc[2] = t1 == ""
            except (ValueError, IndexError) as why:
                self.thanEr1s(why)
            if validc[2]:
                self.thanDr.dxfPoint(xx, yy, zz, self.defLay, handle, None, aa, validc)
            else:
                nzn += 1
                self.thanDr.dxfPoint(xx, yy, zz, nzLay,       handle, None, aa, validc)
        lay = self.thanDr._dr.thanLayerTree.thanFindic(self.defLay)
        if lay is not None:   #If self.defLay != "0" and no points were added, self.defLay has not been created
            lay.thanAtts["hidename"].thanValSet(False)
            lay.thanAtts["hideheight"].thanValSet(False)
        if nzn > 0:
            lay = self.thanDr._dr.thanLayerTree.thanFindic(nzLay)
            lay.thanAtts["hidename"].thanValSet(False)
            self.thanDr.prt(T["%d points with invalid z were put into layer %s."] % (nzn, nzLay), "info1")


class ThanImportLin(ThanImportBase):
    "A producer class to import elements from a Linicad .lin file."

    def thanImport(self):
        "Imports a LiniCad file."
        self._getElems()


    def _getElems(self):
        "Reads all elements from .lin file."
        nzn = 0
        handle = ""
        while True:
            try:
                try: typ = pickle.load(self.fDxf)
                except EOFError: break
                coords = pickle.load(self.fDxf)
                xx, yy, zz = self._toxyz(coords)
                if typ == "line":
                    if len(coords) < 4: continue
                    self.thanDr.dxfLine(xx, yy, zz, "lines", handle, 3)
                elif typ == "oval":
                    if len(coords) != 4: continue
                    r = fabs(yy[1]-yy[0]) / 2.0
                    xc = (xx[0]+xx[1])*0.5
                    yc = (yy[0]+yy[1])*0.5
                    self.thanDr.dxfCircle(xc, yc, 0.0, "circles", handle, 1, r)
                elif typ == "text":
                    ttext, stext = pickle.load(self.fDxf)
                    ttext = ttext.rstrip()
                    dx = len(ttext) * (stext*5/7) / 2   #length x is 5/7 of length y
                    dy = stext / 2
                    self.thanDr.dxfText(xx[0]-dx, yy[0]-dy, zz[0], "texts", handle, 2, ttext, stext, 0.0)
                else:
                    nzn += 1
            except Exception as why:
                self.thanEr1s(why)
        if nzn > 0:
            self.thanWarn(T["%d unknown elements were not imported"] % nzn)


    @staticmethod
    def _toxyz(coords):
        "Convert linicad coordinates to x, y, z."
        n = len(coords)
        if n % 2 != 0: n -= 1
        xx = []
        yy = []
        zz = []
        for i in range(0, n, 2):
            xx.append(float(coords[i]))
            yy.append(float(coords[i+1]))
            zz.append(0.0)
        return xx, yy, zz


class ThanImportLcad(ThanImportLin):
    "A producer class to import elements from a Linicad .lcad file."
    def _getElems(self):
        "Reads all elements from .lcad file."
        nzn = 0
        handle = ""
        fr = self.fDxf
        try:
            while True:
                try: typ = pickle.load(fr)
                except EOFError: break
                col = pickle.load(fr)
                coords = pickle.load(fr)
                xx, yy, zz = self._toxyz(coords)
                if typ == "text":
                    ttext, stext = pickle.load(fr)
                    ttext = ttext.rstrip()
                    dx = len(ttext) * (stext*5/7) / 2   #length x is 5/7 of length y
                    dy = stext / 2
                    self.thanDr.dxfText(xx[0]-dx, yy[0]-dy, zz[0], "texts", handle, self._toicol(col), ttext, h=stext, theta=0.0)
                elif typ == "oval":
                    outl = pickle.load(fr)         #The outline is used in ThanCad. col is the fill color which is not used
                    if len(coords) != 4: continue
                    r = fabs(yy[1]-yy[0]) / 2.0
                    xc = (xx[0]+xx[1])*0.5
                    yc = (yy[0]+yy[1])*0.5
                    self.thanDr.dxfCircle(xc, yc, 0.0, "circles", handle, self._toicol(outl), r)
                elif typ == "line":
                    if len(coords) < 4: continue
                    self.thanDr.dxfLine(xx, yy, zz, "lines", handle, self._toicol(col))
                else:
                    nzn += 1
        except Exception as e:
            self.thanEr1s(why)
        if nzn > 0:
            self.thanWarn(T["%d unknown elements were not imported"] % nzn)

    @staticmethod
    def _toicol(col):
        "Convert linicad color to dxf integer code."
        rgb = p_gcol.thanTk2Rgb(col)
        print (col, rgb, p_gcol.thanRgb2DxfColCodeApprox(rgb))
        return p_gcol.thanRgb2DxfColCodeApprox(rgb)
        #def          thanRgb2DxfColCodeApprox(rgb):


class ThanImportXyzIntermap(ThanImportBase):
    """ producerA class to import lines in xyz intergraph format.

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
        "Imports a xyz file."
        self._getPolylines()

    def _getPolylines(self):
        "Reads all polylines from .xyz file."
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
                    x1, y1, z1 = map(float, s.split(",")[:3])   #works for python2,3
                except (ValueError, IndexError) as why:
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


class ThanImportKml(ThanImportBase):
    """A producer class to import lines in Google Keyhole Markup Language format, .kml filenames.

    The import procedure converts the GRS80 geodetic coordinates λ,φ of
    the .kml file to the easting, northing of the geodetic projection
    defined in the ThanCad drawing. The elevation z is not changed at
    all, and it may be orthometric or geometric as defined in the .kml
    file.
    """

    def thanImport(self):
        "Imports a kml file."
        pnts, terr = p_gimgeo.readKml(self.fDxf, greece=False)
        if pnts is None: self.thanEr2s(terr)
        self._getPoints(pnts)


    def _getPoints(self, pnts):
        "Reads all points from .kml file."
        dr = self.thanDr._dr    #This is the ThanDrawing object
        geodp = dr.geodp        #This is the geodetic projection of the drawing
        handle = ""
        validc = [True, True, True]

        nzn = 0
        for p in pnts:
            if p.KMLTYPE == "point":
                xen, yen = geodp.geodetGRS802en(radians(p.al), radians(p.phi))
                if p.col is None: icol = None
                else:             icol = p_gcol.thanRgb2DxfColCodeApprox(p.col)
                self.thanDr.dxfPoint(xen, yen, p.z, p.lay, handle, icol, p.name, validc)
            elif p.KMLTYPE == "polygon" or p.KMLTYPE == "path":
                for i in range(len(p.al)):
                    p.al[i], p.phi[i] = geodp.geodetGRS802en(radians(p.al[i]), radians(p.phi[i]))
                if p.col is None: icol = None
                else:             icol = p_gcol.thanRgb2DxfColCodeApprox(p.col)
                if len(p.al) < 3: self.thanWarn(T["KML polygon with 1 or 0 vertices."])
                self.thanDr.dxfPolyline(p.al, p.phi, p.z, p.lay, handle, icol)
            else:
                #assert 0, "Unknown KML object type '{}'".format(p.KMLTYPE)
                nzn += 1
        if nzn > 0:
            self.thanWarn(T["%d unknown KML objects were not imported"] % nzn)


class ThanImportKmz(ThanImportKml):
    """A producer class to import lines in zipped Google Keyhole Markup Language format, .kmz filenames."""

    def thanImport(self):
        "Imports a kmz file."
        pnts, terr = p_gimgeo.readKmz(self.fDxf.name, greece=False)
        if pnts is None: self.thanEr2s(terr)
        self._getPoints(pnts)
