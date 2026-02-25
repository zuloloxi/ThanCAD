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

Package which processes commands entered by the user.
This module processes Global Points related commands.
"""
import p_gearth, p_gvarcom, p_ggen
import thandr
from thanvar import Canc
from thantrans import T
from . import thanundo
from .thancomfile import thanTxtopen


def thanTkGetGlp(proj):
    "Imports point from GLP objects."
    mes = T["Load global points from: greekGys (enter=G): "]
    res = __selectGlp(proj, mes)
    if res == Canc: return proj[2].thanGudCommandCan()     # GLP operation was cancelled, or found error
    trig, trigori, tit = res

    com = "glp"
    newelems = []
    for p in trig:
        elem = thandr.ThanPointNamed()
        elem.thanSet(p[1:4], p[0])
        proj[1].thanElementAdd(elem)     # thanTouch is implicitly called
        elem.thanTkDraw(proj[2].than)    # This also sets thanImages
        newelems.append(elem)
    if len(newelems) == 0: return proj[2].thanGudCommandCan(T["No orthoimages were loaded."])      # Region not implemented
    proj[2].thanRedraw()                 # Images regen probably violated draworder
    proj[1].thanDoundo.thanAdd(com, thanundo.thanReplaceRedo, ((), newelems),
                                    thanundo.thanReplaceUndo, ((), newelems))
    return proj[2].thanGudCommandEnd(T["{} global points were loaded."].format(len(trig)), "info")


def __selectGlp(proj, mes):
    "Let user select GLP source and rectangular region."
    res = proj[2].thanGudGetOpts(mes, default="G", options=("GYS", ))
    if res == Canc: return Canc     # GLP operation was cancelled
    if   res == "g":
        glp = p_gearth.GLPTrigGYS(proj[2].thanPrt) #This is empty initially so that it doesn't cost much memory and time
    else:
        assert 0
    #glp.thanSetProjection(proj[1].geodp)
    c1 = proj[2].thanGudGetPoint(T["First point: "], statonce=T["Select rectangular region of the global points:\n"])
    if c1 == Canc: return Canc            # Rectangle cancelled
    c2 = proj[2].thanGudGetRect(c1, T["Second point: "])
    if c2 == Canc: return Canc            # Rectangle cancelled
    xymm = p_gvarcom.Xymm()
    xymm.includePoint(c1)
    xymm.includePoint(c2)
    trig, trigori, tit = glp.thanGetPoints(xymm)
    if trig is None:
        proj[2].thanPrt(tit, "can1")
        return Canc
    elif len(trig) == 0:
        proj[2].thanPrt(T["No global points were found in this region or in this computer."], "can1")
        return Canc      # No Global Points found
    return trig, trigori, tit


def thanGlpExport(proj):
    "Imports point from GLP objects."
    mes = T["Export global points from: greekGys (enter=G): "]
    res = __selectGlp(proj, mes)
    if res == Canc: return proj[2].thanGudCommandCan()     # GLP operation was cancelled, or found error
    trig, trigori, tit = res
    n = len(trig)
    proj[2].thanPrt(T["{} global points were found."].format(n), "info")

    fn, fw = thanTxtopen(proj, mes=T["Choose trg/csv files to export the global points to"], suf=".trg", mode="w")
    if fn == Canc: return proj[2].thanGudCommandCan()     # GLP operation was cancelled, or found error
    for aa, x, y, z, hbaq in trig:
        p_gvarcom.wrTrg1(fw, aa[:30], x, y, z, hbaq)
    fw.close()
    proj[2].thanPrt(T["{} global points exported to {}"].format(n, fn), "info1")

    fn = fn.parent/fn.namebase + ".csv"
    try:
        with open(fn, "w") as fw:
            fw.write("{}\n".format(";".join(tit)))
            for temp in trigori:
                fw.write("{}\n".format(";".join(temp)))
    except OSError as e:
        proj[2].thanPrt("Could not export global points to {}:\n{}".format(fn, str(e)), "can")
    else:
        proj[2].thanPrt(T["{} global points exported to {}"].format(n, fn), "info1")

    proj[1].thanDoundo.thanAdd("glpexport", p_ggen.doNothing, (),
                                            p_ggen.doNothing, ())
    return proj[2].thanGudCommandEnd()
