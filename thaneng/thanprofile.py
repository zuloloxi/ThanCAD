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

This module draws common profiles of 3d lines.
"""

from math import hypot
import p_ggen
from thanimp import ThanCadDrSave
from thansupport import ThanDxfEmu


def thanCommonProfile(proj, cps, dscale=10.0, layers=None, colors=None):
    "Creates (common) profile for one (or many similar) 3D line(s) into a new drawing."
    from thancom.thancomview import thanZoomExt
    if layers is None: layers = [str(i) for i in range(1, len(cps)+1)]
    dfact = 1.0/dscale    # x scale factor
    d = [0.0*dfact]
    for ca, cb in p_ggen.iterby2(cps[0]):
        d.append(d[-1]+hypot(cb[1]-ca[1], cb[0]-ca[0])*dfact)
    zmin = min(ca[2] for cp in cps for ca in cp)

    projnew, dxf = defDxf(proj, layers, colors)

    dxf.thanDxfSetLayer("0")
    dxf.thanDxfPlot(d[0],  zmin, 3)
    dxf.thanDxfPlot(d[-1], zmin, 2)
    dxf.thanDxfPlot(d[0],  zmin, 3)
#    z1 = max(cp[0][2] for cp in cps)
    z1 = cps[0][0][2]
    dxf.thanDxfPlot(d[0], z1, 2)
    for i in range(1, len(d)):
        dxf.thanDxfSetLayer("0")
#        z1 = max(cp[i][2] for cp in cps)
        z1 = cps[0][i][2]
        dxf.thanDxfPlot(d[i], zmin, 3)
        dxf.thanDxfPlot(d[i], z1,   2)
        for cp,lay in zip(cps, layers):  #works for python2,3
            dxf.thanDxfSetLayer(lay)
            dxf.thanDxfPlot(d[i],   cp[i][2],   3)
            dxf.thanDxfPlot(d[i-1], cp[i-1][2], 2)
    dxf.thanDxfPlot(0, 0, 999)
    projnew[1].thanLayerTree.thanDictRebuild()
    projnew[2].thanRegen()
    thanZoomExt(projnew)
    return projnew


def defDxf(proj, layers, colors):
    "Initial definition."
    from thancom.thancomfile import thanFileNewDo
    if colors is None: colors = list(range(1, len(layers)+1))

    projnew = thanFileNewDo(proj)

    ts = ThanCadDrSave(projnew[1], projnew[2].thanPrt)
    dxf = ThanDxfEmu(None, ts)
    dxf.thanDxfPlots1()

    dxf.thanDxfTableDef (' ', 0)
    dxf.thanDxfTableDef('LAYER', len(layers)+1)
    dxf.thanDxfCrLayer("0", 7, 'CONTINUOUS')
    for lay,col in zip(layers, colors):  #works for python2,3
        dxf.thanDxfCrLayer(lay, col, 'CONTINUOUS')
    dxf.thanDxfTableDef ('ENTITIES', 1)
    dxf.thanDxfSetColor(0)
    return projnew, dxf
