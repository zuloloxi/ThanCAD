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

This module defines the biolimatic City Plan object.
"""
import p_ggen
from p_gpoleod import HippoAnneal, simpol
from thantrans import T, Tarch
import thanimp, thansupport
import thanpackages.biocityplan
from .thanobject import ThanObject


class ThanBiocityplan(ThanObject):
    thanObjectName = "BIOCITYPLAN"    # Name of the objects's class
    thanOjectInfo = "Automated east-west oriented city plan."
    thanVersions = ((1,0),)

    def __init__(self):
        "Set initial values to the city plan and paraphernalia."
        self.xor = self.yor = 0.0
        self.dxor = self.dyor = None
        self.pc = HippoAnneal()

    def toDialog(self, proj):
        "Return the data in a form needed by ThanBcplan dialog."
        pc = self.pc
        v = p_ggen.Struct()
        if pc.pol.hull is None: v.refPolygon = []
        else:                   v.refPolygon = pc.pol.hull
        v.refPrepro = pc.pol.shallowClone()   #Shallow copy
        v.labDTM = len(proj[1].thanObjects["DTMLINES"]) > 0
        v.doPrepro = False
        v.entMinWidth = pc.boik1
        v.entMaxWidth = pc.boik2
        v.entMinHeight = pc.hoik1
        v.entMaxHeight = pc.hoik2
        v.entMinRoad = pc.bod1
        v.entMaxRoad = pc.bod2
        v.choBio = pc.biochange
        v.entMult = 1
        return v

    def fromDialog(self, proj, v):
        "Get parameters from ThanBcplan dialog."
        pc = self.pc
        pc.pol = v.refPrepro
        pc.pol.hull = v.refPolygon
        pc.setPar(v.entMinWidth, v.entMaxWidth, v.entMinHeight, v.entMaxHeight, v.entMinRoad, v.entMaxRoad, v.choBio)

    def tkDraw(self, proj, state):
        "Draws a city plan as produced by simulated annealing."
        pc = self.pc
        first = self.dxor is None
        if first:
            self.dxor = self.pc.pol.uxmax - self.pc.pol.uxmin
            self.dyor = self.pc.pol.uymax - self.pc.pol.uymin
            self.yor -= 2.0*self.dyor*1.2     #leave space for original DTM (it may be visible :))
        ot = list(pc.pol.iterOT(state))
#        roads = pc.pol.roadcoor(state)
        roads = ()
        tit = "Energy=%.1f,  d>8%%=%.1f,  d>10%%=%.1f" % (state.e, state.d8, state.d10)
        ts = thanimp.ThanCadDrSave(proj[1], proj[2].thanPrt)
        dxf = thansupport.ThanDxfEmu()
        dxf.thanDxfPlots(ts)
        pc.pol.todxf(dxf, title=tit, hulls=(pc.pol.hull,), iso=pc.pol.contours, ot=ot, roads=roads, xor=self.xor, yor=self.yor)
        dxf.thanDxfPlot(0,0,999)
        ts.thanAfterImport()
        proj[1].thanLayerTree.thanDictRebuild()
        proj[2].thanRegen()
        if first:
            from thancom.thancomview import thanZoomExt1
            thanZoomExt1(proj)
        self.xor += self.dxor*1.10
        if self.xor > 3.01*1.10*self.dxor:
            self.xor = 0.0
            self.yor -= self.dyor*1.2

    def run(self, proj):
        "Run the bioclimatic city plan algorithm."
        simpol.runOnce(self.pc, prt=proj[2].thanPrt)


    def wrState(self, proj):
        "Save the state of the solution."
        pref = proj[0].parent / proj[0].namebase
        simpol.wrState(self.pc, pref, prter=proj[2].thanPrter)

    def thanList(self, than):
        "Shows information about the FloorPlan object."
        c = list(than.elevation)
        c[:2] = self.xor, self.yor
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %s\n" % (Tarch["Next city plan position:"], than.strcoo(c)))


    def thanExpThc1(self, fw):
        "Saves the bioclimatic city plan to a .thc file."
        f2 = fw.formFloat + "  " + fw.formFloat
        pc = self.pc

        fw.writeBeg("location")
        fw.pushInd()
        fw.writeAtt("current", f2 % (self.xor, self.yor))
        if self.dxor is None: fw.writeAtt("delta", "_NONE_  _NONE_")
        else:                 fw.writeAtt("delta", f2 % (self.dxor, self.dyor))
        fw.popInd()
        fw.writeEnd("location")

        fw.writeBeg("parameters")
        fw.pushInd()
        fw.writeAtt("city_block_width", f2 % (pc.boik1, pc.boik2))
        fw.writeAtt("city_block_height", f2 % (pc.hoik1, pc.hoik2))
        fw.writeAtt("road_width", f2 % (pc.bod1, pc.bod2))
        fw.writeAtt("bioclimatic", "%d" % (pc.biochange,))
        fw.popInd()
        fw.writeEnd("parameters")

        fw.writeBeg("road_grid")
        fw.pushInd()
        if pc.pol.roadenx is not None:
            fw.writeAtt("computed", "%d" % (True,))
            pc.pol.writeGrid(fw)
        else:
            fw.writeAtt("computed", "%d" % (False,))
        fw.popInd()
        fw.writeEnd("road_grid")


    def thanImpThc1(self, fr, ver, than):
        "Reads the bioclimatic city plan from a .thc file."
        pc = self.pc

        fr.readBeg("location")
        self.xor, self.yor =  map(float, fr.readAtt("current"))  #works for python2,3
        self.dxor, self.dyor =  fr.readAtt("delta")
        if self.dxor == "_NONE_": self.dxor = self.dyor = None
        else:                     self.dxor, self.dyor = float(self.dxor), float(self.dyor)
        fr.readEnd("location")

        fr.readBeg("parameters")
        boik1, boik2 = map(float, fr.readAtt("city_block_width"))  #works for python2,3
        hoik1, hoik2 = map(float, fr.readAtt("city_block_height"))  #works for python2,3
        bod1, bod2 = map(float, fr.readAtt("road_width"))  #works for python2,3
        biochange = bool(int(fr.readAtt("bioclimatic")[0]))
        fr.readEnd("parameters")
        pc.setPar(boik1, boik2, hoik1, hoik2, bod1, bod2, biochange)

        fr.readBeg("road_grid")
        computed = bool(int(fr.readAtt("computed")[0]))
        if computed:
            pc.pol.readGrid(fr)
        else:
            pc.pol.roadenx = pc.pol.roadeny = None
        fr.readEnd("road_grid")
