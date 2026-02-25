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

This module processes commands related to the settings (or attributes) of BIM Columns.
It is meant for the IMSAFER research program.
"""
from p_ggen import Canc
from thandr import ThanBimColumn
from thantrans import Tcivil, T
from thancom import thancomsel, thanundo
from thancom.thancommod import thanModEnd, thanModCanc
from .thandiabimcol import ThanTkBimColumnSettings


__vbimcolumn = ThanTkBimColumnSettings.thanValsDef()
def thanImsBimColumnSettings(proj):
    "Add extra attributes to a BIM Column."
    comname = "imsbimcolumnsettings"
    than = proj[2].than
    g2l = than.ct.global2Local
    crelold = proj[1].thanGetLastPoint()

    while True:
        proj[2].thanPrt(Tcivil["Select BIM Columns to apply settings to:"], "info1")
        res = thancomsel.thanSelectGen(proj, standalone=False, filter=lambda elem: isinstance(elem, ThanBimColumn))
        if res == Canc: return thanModCanc(proj)
        delelems = proj[2].thanSelall
        if len(delelems) > 0: break
        proj[2].thanPrt(T["No element selected. Try again."], "can1")
    selold = proj[2].thanSelold
    for elem in delelems:
        assert isinstance(elem, ThanBimColumn), "filter does not work?"

    v = __vbimcolumn.clone()
    individual = len(delelems) == 1     #For a single Column, also show individual settings (name and geometry)
    if individual:
        for elem in delelems: break
        v.fromelem(elem, individual)             #Get individual settings (name and geometry) from single element

    newelems = []
    w = ThanTkBimColumnSettings(proj[2], vals=v, cargo=proj, individual=individual)
    v = w.result
    if v is None: return thanModCanc(proj)  #Inform user that the dialog was cancelled
    print("thanEduBimColumnSettings(): w.result=", v.anal())
    for elem in delelems:
        elem2 = elem.thanClone()
        v.toelem(elem2, individual)
        print("thanEduBimColumnSettings(): elem2.thanCargo=", elem2.thanCargo)
        newelems.append(elem2)
    __vbimcolumn.update(v)   #Keep new settings as new default

    selelems = delelems
    thanundo.thanReplaceRedo(proj, delelems, newelems, selelems)
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo, (delelems, newelems, selelems),
                                        thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)  # 'Reset color' is not needed for the new elements..
                      # since the new elements are redrawn. So if a large number of elements..
                      # (unlikely) are edited, this will slow down the command.
                      # there is room for optimisation!
