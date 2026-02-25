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

This module defines an object which contains a Digital Elevation Model (DEM)
stored in USGS TIF file format.
"""

import p_ggen, p_gtri
try: import p_gearth
except: pass
from thantrans import T
import thandefs
from .thanobject import ThanObject


class ThanDEMusgs(ThanObject):
    thanObjectName = "DEMUSGS"    # Name of the objects's class
    thanObjectInfo = "DEM stored in TIF files (USGS format)"
    thanVersions = ((1,0),)

    def __init__(self):
        "Some initial values to make the object variables clear."
        self.dtm = p_gtri.ThanDEMusgs()


    def thanList(self, than):
        "Shows information about the DEMusgs object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %s\n" % (T["TIF filename:"], self.dtm.filnam))
        if self.dtm.im == "GDEM": return
        if self.thanIsNormal():
            scen = " ".join(map(than.strdis, self.dtm.thanCen()))   #works for python2,3
            than.write("%s %s\n" % (T["Centroid:"], scen))
            ca = list(than.elevation)
            ca[:2] = self.dtm.X0, self.dtm.Y0
            than.write("%s %s\n" % (T["Upper left corner:"], than.strcoo(ca)))
            than.write("%s %s %s\n" % (T["X and Y distance between DEM points :"], than.strdis(self.dtm.DX), than.strdis(self.dtm.DY)))
        else:
            than.write(T["Invalid tif image or image not found.\n"])

    def thanIsNormal(self):
        "Returns False if the image the DEM was not found."
        return self.dtm.im is not None

    def thanExpThc1(self, fw):
        "Saves the name of the tif which contains the USGS DEM."
        fw.writeAtt("TIF", self.dtm.filnam)

    def thanImpThc1(self, fr, ver, than):
        "Reads the name of the tif which contains the USGS DEM, and loads it."
        self.filnam = p_ggen.path(fr.readAtt("TIF")[0])
        if self.filnam.startswith("%%%") and self.filnam.endswith("%%%"):
            self.dtm = p_gearth.gdem(self.filnam)   #May raise ValueError
            self.dtm.thanSetProjection(than.geodp)
            return
        ext = self.filnam.ext.lower()
        if ext == ".bil" or ext == ".hdr":
            self.dtm = p_gtri.ThanDEMbil()
            ok, terr = self.dtm.thanSet(self.filnam)
            if not ok:
                fr.prter("Invalid/missing bil/hdr file while reading %s: %s:\n%s" % (self.thanObjectName, self.filnam, terr))
                self.dtm.im = None
            return
        try:
            im, terr = thandefs.imageOpen(self.filnam)
            if terr != "": raise ValueError(terr)
            self.dtm.thanSet(self.filnam, im)  #This will raise ValueError is something is wrong
        except (IOError, ValueError) as why:
            fr.prter("Invalid/missing TIF while reading %s: %s:\n%s" % (self.thanObjectName, self.filnam, why))
            self.dtm.im = None
