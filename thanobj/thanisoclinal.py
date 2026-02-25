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

This module defines the Isoclinal object. The isoclinal computation
line is controlled by parameters which are stored in this object.
"""
from math import pi
import p_ggen
from thantrans import T
from .thanobject import ThanObject


class ThanIsoclinal(ThanObject):
    thanObjectName = "ISOCLINAL"    # Name of the objects's class
    thanObjectInfo = "Isoclinal line parameters."
    thanVersions = ((1,0),)
    atts  = "labLaynames entEps entAngle entStart entEnd entStep".split()

    def __init__(self):
        "Set default attributes of isoclinal."
        self.labLaynames  = "0"      # coma separated Layers which contains the contour lines
        self.entEps       = 60.0     # user data units
        self.entAngle     = pi*0.5   # rad
        self.entStart     =  1.0     # (%)
        self.entEnd       =  7.0     # (%)
        self.entStep      =  0.1     # (%)
        self.syks = []            #The contour polylines
        self.cprocessed = False   #True if the contour polylines have been checked
                                  #by this object and p_godop.Isoclinal object

    def toDialog(self):
        "Return the data in a form needed by ThanSimplificationSettings dialog."
        v = p_ggen.Struct("Isoclinal settings")
        for att in self.atts:
            setattr(v, att, getattr(self, att))
        return v


    def fromDialog(self, v):
        "Get the data from ThanSimplificationSettings dialog."
        for att in self.atts:
            setattr(self, att, getattr(v, att))


    def thanList(self, than):
        "Shows line simplification settings."
        yn = "No", "Yes"
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s: %s\n" % (T["Contour lines' layers"], self.labLaynames))
        than.write("%s: %s\n" % (T["Distance tolerance to target"], than.strdis(self.entEps)))
        than.write("%s: %s\n" % (T["Maximum direction change"], than.strang(self.entAngle)))
        than.write("%s: %s\n" % (T["Grade search start"],       than.strdis(self.entStart)))
        than.write("%s: %s\n" % (T["Grade search end"],         than.strdis(self.entEnd)))
        than.write("%s: %s\n" % (T["Grade search step"],        than.strdis(self.entStep)))


    def thanExpThc1(self, fw):
        "Saves the simplification settings to a .thc file."
        f = fw.formFloat
        fw.writeAttb("labLaynames", self.labLaynames)
        fw.writeAtt("entEps",   f  % (self.entEps,))
        fw.writeAtt("entAngle", f  % (self.entAngle,))
        fw.writeAtt("entStart", f  % (self.entStart,))
        fw.writeAtt("entEnd",   f  % (self.entEnd,))
        fw.writeAtt("entStep",  f  % (self.entStep,))


    def thanImpThc1(self, fr, ver, than):
        "Reads the simplification settings from a .thc file."
        self.labLaynames = fr.readAttb("labLaynames")
        self.entEps   = float(fr.readAtt("entEps")[0])
        self.entAngle = float(fr.readAtt("entAngle")[0])
        self.entStart = float(fr.readAtt("entStart")[0])
        self.entEnd   = float(fr.readAtt("entEnd")[0])
        self.entStep  = float(fr.readAtt("entStep")[0])
        self.syks.clear()
        self.cprocessed = False


    def setContoursFromlayers(self, lays, ThanLine, T, prt):
        "Collect all the lines in the layers lays, and check that they are correct."
        syks = self.syks
        syks.clear()
        nzero = nvar = 0
        for lay in lays:
            for elem in lay.thanQuad:
                if not isinstance(elem, ThanLine): continue
                cp = elem.cp
                if len(cp) < 2: continue
                zpol = cp[0][2]
                ok = True
                for ct in cp:
                    if ct[2] == zpol: continue
                    nvar += 1
                    ok = False
                    break
                if not ok: continue
                if zpol == 0: nzero += 1
                syks.append(cp)
        if nvar > 0:
            prt(T["Warning: {} polylines did not have constant elevation and were ignored."].format(nvar), "can1")
        if nzero > 0:
            prt(T["Warning: {} polylines have zero elevation."].format(nzero), "can1")
        if len(syks) < 2:
            prt(T["Error: Less than 2 valid polylines were found."], "can")
            return False
        else:
            prt(T["{} valid polylines were found."].format(len(syks)), "info1")
        return True
