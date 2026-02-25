##############################################################################
# ThanCad 0.2.4 "Valencia": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2014 Thanasis Stamos, November 15, 2014
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.2.4 "Valencia": n-dimensional CAD with raster support for engineers

This module defines the Line Simplification object. The simplification of the
line is controlled by parameters which are stired in this object.
"""
import p_ggen
from thantrans import T
from thanobject import ThanObject


class LineSimplification(ThanObject):
    thanObjectName = "LINESIMPLIFICATION"    # Name of the objects's class
    thanObjectInfo = "Simplification of line."
    thanVersions = ("1.0",)
    atts  = "entXYmean entXY entZ choKeep".split()

    def __init__(self):
        "Set default attributes of simplification."
        self.entXYmean = 0.15
        self.entXY     = 0.20
        self.entZ      = 0.10
        self.choKeep   = True

    def toDialog(self):
        "Return the data in a form needed by ThanSimplificationSettings dialog."
        v = p_ggen.Struct("Line simplification settings")
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
        than.write("%s: %s\n" % (T["Tolerance of mean xy error"], than.strdis(self.entXYmean)))
        than.write("%s: %s\n" % (T["Tolerance of individual xy error"], than.strdis(self.entXY)))
        than.write("%s: %s\n" % (T["Tolerance of individual z error"], than.strdis(self.entZ)))
        than.write("%s: %s\n" % (T["Keep original lines after simplification"], T[yn[self.choKeep]]))

    def thanExpThc1(self, fw):
        "Saves the simplification settings to a .thc file."
        f = fw.formFloat
        fw.writeAtt("entXYmean", f    % (self.entXYmean,))
        fw.writeAtt("entXY",     f    % (self.entXY,))
        fw.writeAtt("entZ",      f    % (self.entZ,))
        fw.writeAtt("choKeep",   "%d" % (self.choKeep,))

    def thanImpThc1(self, fr, ver):
        "Reads the simplification settings from a .thc file."
        self.entXYmean = float(fr.readAtt("entXYmean")[0])
        self.entXY     = float(fr.readAtt("entXY")[0])
        self.entZ      = float(fr.readAtt("entZ")[0])
        self.choKeep   = bool(int(fr.readAtt("choKeep")[0]))

