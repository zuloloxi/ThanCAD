##############################################################################
# ThanCad 0.9.2 "Tartu": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2026 Thanasis Stamos, January 20, 2026
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
ThanCad 0.9.2 "Tartu": n-dimensional CAD with raster support for engineers

The package creates automatically architectural things such as stairs.
The subpackage contains the commands which handle architecture related
procedures.
This module implements architecture related procedures.
"""
from math import pi
import p_gmath, p_gindplt
from thantrans import Tarch
import thansupport, thanimp
from thanvar import Canc
from .thandialogstairs import thanCompute, thanValsDef, ThanStairsSettings


__vstairs = thanValsDef()
def thanArchStairs(proj):
      "Draw a plan view of a stairs case."
      from thancom import thanundo
      from thancom.thancomvar import thanModDxfRedo, thanModDxfUndo
      v = __vstairs
      thanCompute(v)
      tty = "Straight staircase", "U-shaped staircase"
      tca = "Clockwise", "Counterclockwise"
      while True:
          t = "clockwise"
          proj[2].thanPrt("%17s: %s    %s: %s" % (Tarch["Staircase type"], Tarch[tty[v.radType]], Tarch["Draw flights"], Tarch[tca[v.radClockwise]]), "info1")
          proj[2].thanPrt("%17s: %-8.3f %20s: %.3f" % (Tarch["Step tread"],   v.entTread, Tarch["Step rise"], v.entRise), "info1")
          proj[2].thanPrt("%17s: %-8.3f %20s: %.3f" % (Tarch["Stairs width"], v.entWidth, Tarch["Stairs total rise"], v.entTotalrise), "info1")
          proj[2].thanPrt("%17s: 1/%d" % (Tarch["Print scale"],  int(v.entScale)), "info1")
          ca = proj[2].thanGudGetPoint(Tarch["Staircase position - lowest axis point (s=change Settings): "], options=("settings",))
          if ca == Canc: return proj[2].thanGudCommandCan()
          if ca == "s":
              win = ThanStairsSettings(proj[2], vals=v, cargo=proj, translation=None)
              if win.result is not None:
                  v = win.result
                  thanCompute(v)
              continue

          #than = proj[2].than
          #g2l = than.ct.global2Local
          #r = max((v.entTread*(v.labNrises-1), 0.1))
          #than.dc.create_line(g2l(ca[0], ca[1]), g2l(ca[0]+r, ca[1]), fill="blue", tags=("e0",))
          #f = proj[2].thanGudGetArc(ca, r*0.5, 0.0, Tarch["Staircase rotation angle (enter=0): "], direction=False, options=("",))
          #than.dc.delete("e0")
          adef = 0.0    #Default angle
          mes = Tarch["Staircase rotation angle (enter={}): "].format(proj[2].than.strang(adef))
          f = getAngle(proj, ca, baseSize=v.entTread*(v.labNrises-1), adef=adef, mes=mes)
          if f == Canc: continue
          break

      __vstairs.update(v)
      oldcl, oldroot = thanundo.thanLtClone(proj)
      newelems = __drawstairs(proj, v, ca, f)

      lt = proj[1].thanLayerTree
      newroot = lt.thanRoot  #Please note that oldroot contains just a reference to the set of elements
      newcl = lt.thanCur     #..and thus we waste no memory here
      proj[1].thanDoundo.thanAdd("archstairs", thanModDxfRedo, (newelems, newcl, newroot, {}),
                                               thanModDxfUndo, (newelems, oldcl, oldroot, {}))
      proj[2].thanGudCommandEnd()


def getAngle(proj, ca, baseSize, adef, mes):
    "Get the angle from the user, either with the mouse or typing the angle."
    than = proj[2].than
    g2l = than.ct.global2Local
    r = max((baseSize, 0.1))
    than.dc.create_line(g2l(ca[0], ca[1]), g2l(ca[0]+r, ca[1]), fill="blue", tags=("e0",))
    f = proj[2].thanGudGetArc(ca, r*0.5, 0.0, mes, direction=False, options=("",))
    than.dc.delete("e0")
    if f == "": f = adef
    return f


def __drawstairs(proj, v, ca, f):
    "Draw the staircase to a ThanCad drawing."
    ts = thanimp.ThanCadDrSave(proj[1], proj[2].thanPrt)
    dxf = thansupport.ThanDxfEmu()
    dxf.thanDxfPlots(ts)

    if v.radType == 0:    #Straight Staircase
        p_gindplt.staircaseS(dxf, ca, f, dscale=v.entScale, bpat=v.entTread,
            hrise=v.entRise, bskal=v.entWidth, nyps=v.labNrises, trname=Tarch["TR"])
    else:                 #U-shaped Staircase
        p_gindplt.staircaseU(dxf, ca, f, dscale=v.entScale, clockwise=v.radClockwise==0, bpat=v.entTread,
            hrise=v.entRise, bskal=v.entWidth, bwell=v.entWell, blanding=v.entLanding, nyps=v.labNrises, trname=Tarch["TR"])
    dxf.thanDxfPlot(0, 0, 999)

    ts.thanAfterImport()
    proj[1].thanLayerTree.thanDictRebuild()
    proj[2].thanRegen()
    return ts.newelems


def thanArchNorth(proj):
    "Draw the architectural north symbol - for plan views."
    from thancom import thanundo
    from thancom.thancomvar import thanModDxfRedo, thanModDxfUndo
    v = __vstairs
    thanCompute(v)
    while True:
        t = "clockwise"
        proj[2].thanPrt("%17s: 1/%d" % (Tarch["Print scale"],  int(v.entScale)), "info1")
        ca = proj[2].thanGudGetPoint(Tarch["North position - center (s=change Settings): "], options=("settings",))
        if ca == Canc: return proj[2].thanGudCommandCan()
        if ca == "s":
            win = ThanStairsSettings(proj[2], vals=v, cargo=proj, translation=None)
            if win.result is not None:
                v = win.result
                thanCompute(v)
            continue
        adef = pi/2.0    #Default angle
        mes = Tarch["Staircase rotation angle (enter={}): "].format(proj[2].than.strang(adef))
        f = getAngle(proj, ca, baseSize=v.entTread*(v.labNrises-1), adef=adef, mes=mes)
        if f == Canc: continue
        break

    __vstairs.update(v)
    oldcl, oldroot = thanundo.thanLtClone(proj)
    newelems = __drawnorth(proj, v, ca, f)

    lt = proj[1].thanLayerTree
    newroot = lt.thanRoot  #Please note that oldroot contains just a reference to the set of elements
    newcl = lt.thanCur     #..and thus we waste no memory here
    proj[1].thanDoundo.thanAdd("archnorth", thanModDxfRedo, (newelems, newcl, newroot, {}),
                                            thanModDxfUndo, (newelems, oldcl, oldroot, {}))
    proj[2].thanGudCommandEnd()


def __drawnorth(proj, v, ca, f):
    "Draw the north symbol to a ThanCad drawing."
    ts = thanimp.ThanCadDrSave(proj[1], proj[2].thanPrt)
    dxf = thansupport.ThanDxfEmu()
    dxf.thanDxfPlots(ts)

    ssize = 2.50 * v.entScale / 100.0    #2.5 cm στο χαρτί
    p_gindplt.north(dxf, ca[0], ca[1], ssize, theta=f*180.0/pi-90.0)
    dxf.thanDxfPlot(0, 0, 999)

    ts.thanAfterImport()
    proj[1].thanLayerTree.thanDictRebuild()
    proj[2].thanRegen()
    return ts.newelems
