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

Curve Matching Algorithms, Dimitra Vassilaki, PhD Candidate
Lab of Photogrammetry, NTUA, 2011-2013
This module displays a dialog for the user to define the necessary elements
and options for multiple pairs of FFLFs (curves) of different dimensionality,
global matching.
"""

import sys, copy, ConfigParser, Tkinter
from tkMessageBox import ERROR
import p_gtkuti, p_gtkwid, p_ggen
from p_gmath import Projection
from thanvar import thanfiles
from thantrans import Tmatch, T
from thandiaicp import ThanICPcom
from thandiamatch23 import ThanMatch23


class ThanMatchMult23(ThanMatch23):
    "Parameters for global matching of network of FFLFs (Curves) of different dimensionality."

    def __init__(self, master, vals=None, cargo=None, *args, **kw):
        "Extract initial matching parameters."
        t = "Global Matching of Multiple Free Form Linear Features FFLFs\n"\
            "MultipleCurves of different Dimensionality"
        kw.setdefault("title", Tmatch["Global Matching of FFLF networks of different Dimensionality"])
        kw.setdefault("buttonlabels", (T["Execute"], T["Cancel"]))
        ThanMatch23.__init__(self, master, vals, cargo, *args, **kw)


    def body(self, win):
        self.thanWids = []
        self.colfra = "blue"
#        self.option_add("*font", _fo)
        self.fraLogo(win, 0, theme=Tmatch["Curve Matching Algorithms"], year="2009-2013")
        self.fraICP(win, 1)
        self.bodyProject(win, 2, self.thanWids)
        self.fraSel(win, 3, Tmatch["Select the\nreference (3D) lines"], Tmatch["Select the\nprojected (2D) lines"], "m23")
        self.fra1ProjApprox(win, 4)
        self.fra1TransfApprox(win, 5)
        win.columnconfigure(0, weight=1)
        for (key,tit,wid,vld) in self.thanWids:
            setattr(self, key, wid)

        if self.thanValsInit == None:
            self.thanValsInit = self.thanValsDef()
            self.thanValsRead(self.thanValsInit)
        self.thanValsSaved = copy.deepcopy(self.thanValsInit)
        self.thanSet(self.thanValsInit)
        self._projApproxDet()



    def validate(self, strict=True):
        """Returns true if the value chosen by the user is valid.

        If strict == True, then if an error is found, an error message is displayed,
        self.result is unchanged, and False is rerurned to the caller.
        If strict == True, and no errors are found, self.result is updated with
        the new values. True is returned to the caller.
        If strict == False, then if an error is found, a default value is used
        instead of the wrong one, self.results is set with the new values,
        and False is returned to the caller.
        If strict == False, and no errors are found, then, self.results is set
        with the new values, and True is returned to the caller.
        """
        ret, vs = ThanICPcom.validate(self, strict)
        if not ret and strict: return ret

        icodp = vs.radProject
        self.projection = None
        if vs.radProjApprox == 2:
            if not self._validateReadCoefs(vs.entFilcof, strict=strict): # vs.projection = self.projection  # self.projection is set by __validateReadCoefs()
                ret = False
                if strict:
                    self.initial_focus = self.entFilcof
                    return ret

        if len(self.thanGps) <= 1:
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["At least 2 references lines must be selected"], T["Error in data"])
                return ret
        vs.gps = self.thanGps
        if len(self.thanRel) <= 1:
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["At least 2 projected lines must be selected"], T["Error in data"])
                return ret
        vs.rel = self.thanRel
        if len(self.thanGps) != len(self.thanRel):
            ret = False
            if strict:
                p_gtkuti.thanGudModalMessage(self, Tmatch["The number of reference and projected lines must be the same"], T["Error in data"])
                return ret

        self.result = vs
        return ret


if __name__ == "__main__":
    root = Tkinter.Tk()
    win = ThanMatchMult23(root, None)
    print win.result.anal()
