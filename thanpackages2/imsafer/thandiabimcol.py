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

This dialog asks for BIMCOLUMN settings (or attributes).
It is meant for the IMSAFER research program.
"""

import copy
from math import pi
import tkinter
import p_gtkwid, p_ggen
from thantrans import Tcivil
#Tcivil = p_ggen.Translation(dict(__TRANSLATION__=("en", "EN", "en", "EN")))  ##############

"""
The 14 columns of the matrix correspond to:
(c1) column dimension parallel to the x-axis [b (m)]
(c2) column dimension parallel to the y-axis [h (m)]
(c3) initial mechanical percentage of reinforcement (ρ)
(c4) abscissa of the column’s section mass center [x (m)]
(c5) ordinate of the column’s section mass center [y (m)]
(c6) stiffness reduction coefficient due to cracking [λc]
(c7) initial reinforcement thickness (element strength requirements) [to (m)]
(c8) mechanical reinforcement rate of initial reinforcement [ρo]
(c9) additional coating thickness resulting from minimizing construction eccentricity [tnew (m)]
(c10) mechanical percentage of additional coating reinforcement (ρnew)
(c11) modulus of elasticity of concrete [Ec (kPa)]
(c12) modulus of elasticity of steel reinforcement [Es (kPa)]
(c13) column length [L (m)]
(c14) axial compressive load for the combination G+0.3Q (with positive sign) [N (kN)]
(c15) Max additional coating thickness allowed [tnewmax (m)]

"""
class ThanBimColumnSettings(p_ggen.Struct):
    atts = "entRhoInitial,entLamCrack,entThickTo,entRhoTo,entEc,entEs,entL,entN,entTnewMax".split(",")

    def __init__(s, *args, **kw):
        "Set default values."
        super().__init__(*args, **kw)
        s.entRhoInitial = 0.02
        s.entLamCrack   = 0.6
        s.entThickTo    = 0.0
        s.entRhoTo      = 0.0
        s.entEc         = 30.0e6
        s.entEs         = 200.0e6
        s.entL          = 3.0
        s.entN          = 1000.0
        s.entTnewMax    = 0.10

        s.entName       = "K1"
        s.entGeomB      = 0.40
        s.entGeomH      = 0.40
        s.entGeomTheta  = 0.0
        s.entGeomX      = 0.0
        s.entGeomY      = 0.0

    def toelem(self, elem, individual):
        "Update a Bim Column element with the settings."
        if elem.thanCargo is None: elem.thanCargo = {}
        for att in self.atts:
            elem.thanCargo[att] = getattr(self, att)

        if individual:   #Also update individual properties (name and geometry)
            elem.cc[0] = self.entGeomX
            elem.cc[1] = self.entGeomY
            elem.ds[1] = self.entGeomB
            elem.ds[0] = self.entGeomH
            elem.thanSet(elem.itype, self.entName, elem.cc, elem.ds, self.entGeomTheta*pi/180.0, elem.spin, cargo=elem.thanCargo)
            #elem.name  = self.entName
            #elem.ds[1] = self.entGeomB
            #elem.ds[0] = self.entGeomH
            #elem.theta = self.entGeomTheta*pi/180.0


    def fromelem(self, elem, individual):
        "Get the settings from Bim Column element."
        if elem.thanCargo is not None:
            for att in self.atts:
                if att not in elem.thanCargo: continue
                setattr(self, att, elem.thanCargo[att])
        if individual:   #Also get individual properties (name and geometry)
            self.entName      = elem.name
            self.entGeomB     = elem.ds[1]
            self.entGeomH     = elem.ds[0]
            self.entGeomTheta = elem.theta*180.0/pi
            self.entGeomX     = elem.cc[0]
            self.entGeomY     = elem.cc[1]


class ThanTkBimColumnSettings(p_gtkwid.ThanComDialog):
    "Dialog for the point distance settings."

    def __init__(self, *args, **kw):
        "Just set the title."
        self.individual = kw.pop("individual")
        proj = kw["cargo"]
        kw.setdefault("title", "%s - %s" % (proj[0].name, Tcivil["BIM Column settings"]))
        super().__init__(*args, **kw)


    @staticmethod
    def thanValsDef():
        "Build default values."
        return ThanBimColumnSettings()
        #s.entName       = "K1"
        #s.entRhoInitial = 0.02
        #s.entLamCrack   = 0.6
        #s.entThickTo    = 0.0
        #s.entRhoTo      = 0.0
        #s.entEc         = 30.0e6
        #s.entEs         = 200.0e6
        #s.entL          = 3.0
        #s.entN          = 1000.0
        #s.entTnewMax    = 0.10
        #s.entGeomB      = 0.40
        #s.entGeomH      = 0.40
        #s.entGeomTheta  = 0.0
        #s.entGeomX      = 0.0
        #s.entGeomY      = 0.0
        #return s


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraBim(win, 1)
        if self.individual: self.fraGeom(win, 2)


    def fraBim(self, win, ir):
        "Widgets for BIM column settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)
        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tcivil["BIM COLUMN SETTINGS:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        ir += 1
        tit = Tcivil["Initial reinforcement percentage [ρ]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.0, 1.0)
        self.thanWids.append(("entRhoInitial", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Stiffness reduction coefficient due to cracking [λc]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.0, 1.0)
        self.thanWids.append(("entLamCrack", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Initial coating thickness [to (m)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.0, 1.0)
        self.thanWids.append(("entThickTo", tit, wid, val))

        ir += 1
        tit = Tcivil["Reinforcement percentage of initial coating [ρo]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.0, 1.0)
        self.thanWids.append(("entRhoTo", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Modulus of elasticity of concrete [Ec (kPa)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(1e6, 100e6)
        self.thanWids.append(("entEc", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Modulus of elasticity of steel reinforcement [Es (kPa)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(10e6, 2000e6)
        self.thanWids.append(("entEs", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Column length [L (m)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.5, 20.0)
        self.thanWids.append(("entL", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Axial compressive load for the combination G+0.3Q\n(with positive sign) [N (kN)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.0, 1e6)
        self.thanWids.append(("entN", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Max additional coating thickness allowed [tnewmax (m)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.0, 10.0)
        self.thanWids.append(("entTnewMax", Tcivil[tit], wid, val))


    def fraGeom(self, win, ir):
        "Widgets for individual properties of BimColumn (name and geometry)."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)
        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tcivil["BIM COLUMN INDIVIDUAL PROPERTIES:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        ir += 1
        tit = Tcivil["Column name"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValUniqname(allowblank=False, others=(), terr=Tcivil["Name already exists: "])
        self.thanWids.append(("entName", tit, wid, val))

        ir += 1
        tit = Tcivil["Column dimension parallel to the x-axis [b (m)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.01, 10.0)
        self.thanWids.append(("entGeomB", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Column dimension parallel to the y-axis [h (m)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(0.01, 10.0)
        self.thanWids.append(("entGeomH", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Angle of lower side with respcet to x-axis [θ (deg)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(None, None)
        self.thanWids.append(("entGeomTheta", Tcivil[tit], wid, val))

        ir += 1
        key = "entGeomX"
        tit = Tcivil["Abscissa of the column’s section mass center [x (m)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(None, None)
        self.thanWids.append(("entGeomX", Tcivil[tit], wid, val))

        ir += 1
        tit = Tcivil["Ordinate of the column’s section mass center [y (m)]"]
        wid = p_gtkwid.labelentry(fra, ir, 1, tit)
        val = p_gtkwid.ThanValFloat(None, None)
        self.thanWids.append(("entGeomY", Tcivil[tit], wid, val))


def test1():
    root = tkinter.Tk()
    proj = [ p_ggen.path("xxxx"), None, root]
    dia = ThanTkBimColumnSettings(root, cargo=proj)
    #root.mainloop()

if __name__ == "__main__": test1()
