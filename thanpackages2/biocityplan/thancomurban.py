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

The package provides tools and automation for urban analysis/design.
The subpackage contains the commands which handle urban related procedures.
This module implements various urban commands.
"""
from math import hypot, atan2, pi
import collections
import p_ggen
from p_gmath import dpt
import thandr
from thanvar import Canc, thanShowFile
from thantrans import Turban, Tarch, Tmatch


def __biodirlines(e):
    "Filters elements that can be used as roads."
    from thandr import ThanLine, ThanCurve, ThanLineFilled
    if isinstance(e, ThanCurve): return False
    if isinstance(e, ThanLineFilled): return False
    return isinstance(e, ThanLine)


def thanUrbanBioazim(proj):
    "Computation of the azimuth of roads (lines) for bioclimatic analysis."
    from thancom.thancomsel import thanSelectGen
    from thancom import thanundo
    from thancom.thancommod import thanModCanc, thanModEnd
    prt = proj[2].thanPrt
    prt(Tarch["This command computes statistics of the azimuth of roads (lines) for bioclimatic evaluation of city plans."], "info")
    ncat = proj[2].thanGudGetInt2(Tarch["Number of azimuth categories (enter=4): "], default=4, limits=(2, None), statonce="", strict=True)
    if ncat == Canc: return proj[2].thanGudCommandCan()    # azimuth computation was cancelled
    prt(Tarch["Select roads to process:"])
    res = thanSelectGen(proj, standalone=False, filter=__biodirlines)
    if res == Canc: return thanModCanc(proj)               # azimuth computation was cancelled
    roads = proj[2].thanSelall
    selold = proj[2].thanSelold
    dth = 180.0/ncat
    dsum = collections.Counter()
    isum = collections.Counter()
    roadc = collections.defaultdict(set)
    for e in roads:
        for ca, cb in p_ggen.iterby2(e.cp):
            dy, dx = cb[1]-ca[1], cb[0]-ca[0]
            th = dpt(atan2(dy, dx))
            if th > pi: th -= pi
            d = hypot(dy, dx)
            n = int(th*180.0/pi/dth+0.5) % ncat     #When n == ncat, then the azimuth is in the category of the azimuth of n=0
            dsum[n] += d
            isum[n] += 1
            roadc[n].add((tuple(ca), tuple(cb)))
    proj[1].thanDoundo.thanAdd("edubiodir", thanundo.thanReplaceRedo, ((), (), roads),
                                            thanundo.thanReplaceUndo, ((), (), selold))
    fw = __openbio(proj, proj[2].thanPrter)
    if fw is not None:
        prt = lambda s, tags=(), fw=fw: fw.write("%s\n" % (s,))
    prt("Γωνία (deg)\t  Πλήθος οδών\t  Συνολικό μήκος", "info")
    for i in range(ncat):
        s = "%11.1f\t%13d\t%16.1f" % (dth*i, isum[i], dsum[i])
        prt(s.replace(".", ","), "info1")
    prt("Εύρος μετρήσεων για κάθε γωνία ± %.1f deg" % (dth*0.5,))
    fn = None
    if fw is not None:
        fn = p_ggen.path(fw.name)
        fw.close()
    __biocolor(proj, dth, ncat, roadc, fn)
    if fn is not None: thanShowFile(proj, fn, "Statistics of the azimuth of roads")
    thanModEnd(proj)


def __biocolor(proj, dth, ncat, roadc, fn):
    "Create a new drawing with the roads coloured according to azimuth."
    from thaneng.thanprofile import defDxf
    from thancom.thancomview import thanZoomExt1
    from thancom.thancomfile import thanFileSavePath
    layers = []
    colors = []
    for i in range(ncat):
        th = dth*i
        layers.append("theta%d_%03.1f" % (i, th))
        if th < 22.5:      colors.append(3)        #green
        elif th < 90-22.5: colors.append(2)        #yellow
        elif th < 90+22.5: colors.append(5)        #blue
        else:              colors.append(2)        #yellow
    projnew, dxf = defDxf(proj, layers, colors)

    for i in range(ncat):
        dxf.thanDxfSetLayer(layers[i])
        for ca, cb in roadc[i]:
            dxf.thanDxfPlot3(ca[0], ca[1], ca[2], 3)
            dxf.thanDxfPlot3(cb[0], cb[1], cb[2], 2)
    dxf.thanDxfPlot(0, 0, 999)
    projnew[1].thanLayerTree.thanDictRebuild()
#    projnew[2].geometry("%dx%d" % (640, 480))
    projnew[2].update()
    projnew[2].thanRegen()
    thanZoomExt1(projnew)
    if fn is not None:
        fn = fn.parent / fn.namebase + ".thcx"
        thanFileSavePath(projnew, fn)


def __openbio(proj, prt):
    "Open files to save the azimuth results."
    name = proj[0].namebase
    par = p_ggen.path(proj[0].parent)
    try:
        for i in range(1000):
            p = par / ("%s%03d.txt" % (name, i))
            if not p.exists():
                fw = open(p, "w")
                return fw
        raise IOError("It seems the directory is full")
    except IOError as why:
        prt("%s:\n%s" % (Tmatch["Could not write results to file."], why), "can")
        return None
