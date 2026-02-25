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

This module defines the Line Simplification object. The simplification of the
line is controlled by parameters which are stored in this object.
"""
import p_ggen
from thantrans import T
from .thanobject import ThanObject


class LineSimplification(ThanObject):
    thanObjectName = "LINESIMPLIFICATION"    # Name of the objects's class
    thanObjectInfo = "Simplification of line."
    thanVersions = ((1,0), (1,1))
    algsdesc = "Least deviation (Stamos-Vassilaki)", "Max distance (Ramer–Douglas–Peucker)", "First fit (Reumann–Witkam)"
    algs = "SV", "RDP", "RW"
    atts  = "entXYmean entXY entZ choAlg choKeep".split()

    def __init__(self):
        "Set default attributes of simplification."
        self.entXYmean = 0.15
        self.entXY     = 0.20
        self.entZ      = 0.10
        self.choAlg    = "RDP"
        self.choKeep   = True

    def toDialog(self):
        "Return the data in a form needed by ThanSimplificationSettings dialog."
        v = p_ggen.Struct("Line simplification settings")
        for att in self.atts:
            setattr(v, att, getattr(self, att))
        v.choAlg = self.algs.index(v.choAlg)    #Convert to integer position
        return v

    def fromDialog(self, v):
        "Get the data from ThanSimplificationSettings dialog."
        for att in self.atts:
            setattr(self, att, getattr(v, att))
        self.choAlg = self.algs[self.choAlg]

    def thanList(self, than):
        "Shows line simplification settings."
        yn = "No", "Yes"
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s: %s\n" % (T["Tolerance of mean xy error"], than.strdis(self.entXYmean)))
        than.write("%s: %s\n" % (T["Tolerance of individual xy error"], than.strdis(self.entXY)))
        than.write("%s: %s\n" % (T["Tolerance of individual z error"], than.strdis(self.entZ)))
        i = self.algs.index(self.choAlg)
        than.write("%s: %s\n" % (T["Simplification method"], self.algsdesc[i]))
        than.write("%s: %s\n" % (T["Keep original lines after simplification"], T[yn[self.choKeep]]))

    def thanExpThc1(self, fw):
        "Saves the simplification settings to a .thc file."
        f = fw.formFloat
        fw.writeAtt("entXYmean", f    % (self.entXYmean,))
        fw.writeAtt("entXY",     f    % (self.entXY,))
        fw.writeAtt("entZ",      f    % (self.entZ,))
        fw.writeAtt("choAlg",    "%s" % (self.choAlg,))
        fw.writeAtt("choKeep",   "%d" % (self.choKeep,))

    def thanImpThc1(self, fr, ver, than):
        "Reads the simplification settings from a .thc file."
        self.entXYmean = float(fr.readAtt("entXYmean")[0])
        self.entXY     = float(fr.readAtt("entXY")[0])
        self.entZ      = float(fr.readAtt("entZ")[0])

        if ver > (1, 0):
            self.choAlg = fr.readAtt("choAlg")[0]
            if self.choAlg not in self.algs: raise ValueError("Unknown simplification method: {}".format(self.choAlg))
        else:
            self.choAlg = "RDP"
            assert self.choAlg in self.algs, "Unknown simplification method: {}".format(self.choAlg)

        self.choKeep   = bool(int(fr.readAtt("choKeep")[0]))
