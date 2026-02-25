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
Deciphers data from a .dxf file.
"""

import sys
import p_ggen
from p_gimdxf import ThanDrIgnore, ThanImportDxf

class KaDxf(ThanDrIgnore):
    "A class which ignores the most elements read by ThanImportDxf."
    def __init__(self, prt):
        ThanDrIgnore.__init__(self, prt)
        self.cxylines = []     # layer kanabosxy
        self.cxlines =  []     # layer kanabosx
        self.cylines =  []     # layer kanabosy
        self.clines =   []     # layer plaisio
        self.cor = None        # layer kanabosxy (point of origin as center of circle)
        self.corx = None       # layer kanabosx (point of origin as center of circle in x direction)
        self.cory = None       # layer kanabosy (point of origin as center of circle in y direction)
        self.layunk = {}
        self.laykno = {"kanabosxy":0, "kanabosx":0, "kanabosy":0, "plaisio":0}

    def warnLayer(self, lay):
        "Warn once if an unknown layer is found in the dxf file."
        n = self.layunk.get(lay, 0) + 1
        self.layunk[lay] = n
        if n > 1: return
        self.prt("\nΠροειδοποίηση: Το layer %s δεν θα ληφθεί υπόψη." % lay)

    def warnObj(self, lay):
        "Warn once if an unknown object is found in a known layer."
        n = self.laykno[lay] + 1
	self.laykno[lay] = n
	if n > 1: return
	self.prt("")
	self.prt("Προειδοποίηση: Βρέθηκαν πρόσθετα αντικείμενα στο layer %s:" % lay)
	self.prt("               Δεν θα ληφούν υπόψη.")

    def dxfPolyline(self, xx, yy, zz, lay, handle, col):
        "Selects the polylines only ic certain layers."
	lay = lay.lower()
	if   lay == "kanabosxy": self.cxylines.append(zip(xx,yy))
	elif lay == "kanabosx":  self.cxlines.append(zip(xx,yy))
	elif lay == "kanabosy":  self.cylines.append(zip(xx,yy))
	elif lay == "plaisio":   self.clines.append(zip(xx,yy))
	else:                    self.warnLayer(lay)

    def dxfCircle(self, xx, yy, zz, lay, handle, col, r):
        "Selects the circle of layer plaisio; its center is the origin point."
	lay = lay.lower()
	if lay == "kanabosxy":
	    if self.cor != None:
	        self.prt("")
	        self.prt("Warning: duplicate circle in layer kanabosxy defines")
		self.prt("         duplicate origin point. It is ignored.")
	    else:
	        self.cor = xx, yy
	elif lay == "kanabosx":
	    if self.corx != None:
	        self.prt("")
	        self.prt("Warning: duplicate circle in layer kanabosx defines")
		self.prt("         duplicate origin point in x direction. It is ignored.")
	    else:
	        self.corx = xx, yy
	elif lay == "kanabosy":
            if self.cory != None:
	        self.prt("")
	        self.prt("Warning: duplicate circle in layer kanabosy defines")
		self.prt("         duplicate origin point in y direction. It is ignored.")
	    else:
	        self.cory = xx, yy
	elif lay == "plaisio":
	    self.warnObj(lay)
	else:
            self.warnLayer(lay)

    dxfLine = dxfPolyline

    def dxfPoint   (self, xx, yy, zz, lay, handle, col):                    self.warnx(lay)
    def dxfArc     (self, xx, yy, zz, lay, handle, col, r, theta1, theta2): self.warnx(lay)
    def dxfText    (self, xx, yy, zz, lay, handle, col, text, h, theta):    self.warnx(lay)
    def dxfBlockAtt(self, xx, yy, zz, lay, handle, col, blname, blatts):    self.warnx(lay)
    def dxfThanImage(self, xx, yy, zz, lay, handle, col, filnam, scale, theta): self.warnx(lay)
    def dxf3dface  (self, xx, yy, zz, lay, handle, col):                    self.warnx(lay)

    def warnx(self, lay):
        "Make the right warning for unknown objects."
	lay = lay.lower()
        if lay in self.laykno: self.warnObj(lay)
	else: self.warnLayer(lay)

    def test(self):
        "Various tests."
	if self.cor == None:
	    if self.corx != None and self.cory != None:
		return
	    if self.corx == None and self.cory == None:
	        self.prt("")
	        self.prt("Error: No circle was found:")
	        self.prt("       A circle in layer kanabosxy is needed to define the origin point.")
		raise p_ggen.RecordedError
	    if self.corx == None:
	        self.prt("")
	        self.prt("Error: No circle was found in kanabosx:")
	        self.prt("       A second circle in layer kanabosx is needed")
		self.prt("       to define the origin point.")
		raise p_ggen.RecordedError
	    else:
	        self.prt("")
	        self.prt("Error: No circle was found in kanabosy:")
	        self.prt("       A second circle in layer kanabosy is needed to")
		self.prt("       define the origin point.")
		raise p_ggen.RecordedError
	if self.corx != None:
	    self.prt("")
	    self.prt("Warning: A circle was found in kanabosxy and it completely defines")
	    self.prt("         the origin point:")
	    self.prt("         Another circle found in layer kanabosx is duplicate and it is ignored.")
	    self.corx = None
	if self.cory != None:
	    self.prt("")
	    self.prt("Warning: a circle was found in kanabosxy and it completely defines")
	    self.prt("         the origin point:")
	    self.prt("         Another circle found in layer kanabosy is duplicate and it is ignored.")
	    self.cory = None


def readDxf(com):
    "Reads the grid point from dxf file."
    dr = KaDxf(com.prt)
    t = ThanImportDxf(com.frw["dxp"], dr)
    t.thanImport()
    dr.test()
    com.cxylines = dr.cxylines
    com.cxlines  = dr.cxlines
    com.cylines  = dr.cylines
    com.clines   = dr.clines
    com.cor      = dr.cor
    com.corx     = dr.corx
    com.cory     = dr.cory


def readTcad(com, proj):
    "Reads the grid point from an acrive ThanCad drawing."
    from thansupport import thanImportTcad
    dr = KaDxf(com.prt)
    t = thanImportTcad(proj, dr)
#    t.thanImport()
    dr.test()
    com.cxylines = dr.cxylines
    com.cxlines  = dr.cxlines
    com.cylines  = dr.cylines
    com.clines   = dr.clines
    com.cor      = dr.cor
    com.corx     = dr.corx
    com.cory     = dr.cory


if __name__ == "__main__":
    com = p_ggen.Struct()
    com.prt = p_ggen.prg
    com.frw = {}
    com.frw["dxp"] = open("d.dxp", "r")
    readDxf(com)
    for cls in "com.cxylines  com.cxlines com.cylines com.clines".split():
        com.prt(cls)
        for cl in eval(cls):
            for c in cl: com.prt("%15.3f%15.3f" % c)
            com.prt("")
    com.prt("")
    com.prt("origin")
    if com.cor != None:
        print "cor"
        com.prt("%15.3f%15.3f" % com.cor)
    else:
        print "corx, cory"
        com.prt("%15.3f%15.3f" % com.corx)
        com.prt("%15.3f%15.3f" % com.cory)
