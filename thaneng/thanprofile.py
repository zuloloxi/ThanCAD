##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module draws common profiles of 3d lines.
"""

from math import hypot
from itertools import izip
import p_ggen


def thanCommonProfile(proj, cps, layers=None, colors=None):
    "Creates (common) profile for one (or many similar) 3D line(s) into a new drawing."
    from thancom.thancomview import thanZoomExt
    if layers == None: layers = [str(i) for i in xrange(1, len(cps)+1)]
    dfact = 0.1
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
    for i in xrange(1, len(d)):
        dxf.thanDxfSetLayer("0")
#        z1 = max(cp[i][2] for cp in cps)
        z1 = cps[0][i][2]
        dxf.thanDxfPlot(d[i], zmin, 3)
        dxf.thanDxfPlot(d[i], z1,   2)
        for cp,lay in izip(cps, layers):
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
    from thanimp import ThanCadDrSave
    from thansupport import ThanDxfEmu
    from thancom.thancomfile import thanFileNewDo
    if colors == None: colors = range(1, len(layers)+1)

    projnew = thanFileNewDo(proj)

    ts = ThanCadDrSave(projnew[1], projnew[2].thanPrt)
    dxf = ThanDxfEmu()
    dxf.thanDxfPlots1(ts)

    dxf.thanDxfTableDef (' ', 0)
    dxf.thanDxfTableDef('LAYER', len(layers)+1)
    dxf.thanDxfCrLayer("0", 7, 'CONTINUOUS')
    for lay,col in izip(layers, colors):
        dxf.thanDxfCrLayer(lay, col, 'CONTINUOUS')
    dxf.thanDxfTableDef ('ENTITIES', 1)
    dxf.thanDxfSetColor(0)
    return projnew, dxf
