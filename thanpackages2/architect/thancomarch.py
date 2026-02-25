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

The package creates automatically architectural things such as stairs.
The subpackage contains the commands which handle architecture related
procedures.
This module implements architecture related procedures.
"""
from math import pi
from thantrans import Tarch
import thansupport, thanimp
from thanvar import Canc
from .similar2 import Similar2D
from .thandialogstairs import thanCompute, thanValsDef, ThanStairsSettings


__vstairs = thanValsDef()
def thanArchStairs(proj):
      "Draw a plan view of a stairs case."
      from thancom import thanundo
      from thancom.thancomvar import thanModDxfRedo, thanModDxfUndo
      v = __vstairs
      thanCompute(v)
      while True:
          proj[2].thanPrt("%12s: %-8.3f    %17s: %.3f" % (Tarch["Step tread"],   v.entTread, Tarch["Step rise"], v.entRise))
          proj[2].thanPrt("%12s: %-8.3f    %17s: %.3f" % (Tarch["Stairs width"], v.entWidth, Tarch["Stairs total rise"], v.entTotalrise))
          proj[2].thanPrt("%12s: 1/%d" % (Tarch["Print scale"],  int(v.entScale)))
          ca = proj[2].thanGudGetPoint(Tarch["Staircase position - lowest axis point (s=change Settings): "], options=("settings",))
          if ca == Canc: return proj[2].thanGudCommandCan()
          if ca == "s":
              win = ThanStairsSettings(proj[2], vals=v, cargo=proj, translation=None)
              if win.result is not None:
                  v = win.result
                  thanCompute(v)
              continue

          than = proj[2].than
          g2l = than.ct.global2Local
          r = max((v.entTread*(v.labNrises-1), 0.1))
          than.dc.create_line(g2l(ca[0], ca[1]), g2l(ca[0]+r, ca[1]), fill="blue", tags=("e0",))
          f = proj[2].thanGudGetArc(ca, r*0.5, 0.0, Tarch["Staircase rotation angle (enter=0): "], direction=False, options=("",))
          than.dc.delete("e0")
          if f == Canc: continue
          if f == "": f = 0.0
          f -= pi*0.5    #__stairsdraw() thinks that zero angle is vertical
          fdeg = f*180.0/pi
          break

      __vstairs.update(v)
      oldcl, oldroot = thanundo.thanLtClone(proj)
      newelems = __stairsdraw(proj, v, ca, f, fdeg)
      lt = proj[1].thanLayerTree
      newroot = lt.thanRoot  #Please note that oldroot contains just a reference to the set of elements
      newcl = lt.thanCur     #..and thus we waste no memory here
      proj[1].thanDoundo.thanAdd("archstairs", thanModDxfRedo, (newelems, newcl, newroot, {}),
                                               thanModDxfUndo, (newelems, oldcl, oldroot, {}))
      proj[2].thanGudCommandEnd()


def __stairsdraw(proj, v, ca, f, fdeg):
      "Draw the stairs."
      sim = Similar2D(ca, -f)           #Similar needs closkwise angle
      tra = sim.calc2d
      bpat = v.entTread
      bskal = v.entWidth
      nyps = int(v.labNrises)

      ts = thanimp.ThanCadDrSave(proj[1], proj[2].thanPrt)
      dxf = thansupport.ThanDxfEmu()
      dxf.thanDxfPlots(ts)

      dxf.thanDxfSetLayer('SKALA__SKALA')
      dxf.thanDxfSetColor(7)

      y = -bpat
      for i in range(nyps):
          y = y + bpat
          xt, yt = tra((0.0, y))
          dxf.thanDxfPlot (xt, yt, 3)
          xt, yt = tra((bskal, y))
          dxf.thanDxfPlot (xt, yt, 2)

      xt, yt = tra((0.0, 0.0))
      dxf.thanDxfPlot (xt, yt, 3)
      xt, yt = tra((0.0, y))
      dxf.thanDxfPlot (xt, yt, 2)
      xt, yt = tra((bskal, 0.0))
      dxf.thanDxfPlot (xt, yt, 3)
      xt, yt = tra((bskal, y))
      dxf.thanDxfPlot (xt, yt, 2)

      dxf.thanDxfSetLayer ('SKALA__ARIT')
      dxf.thanDxfSetColor(2)
      hs = 0.15 * v.entScale / 100.0
      y = -bpat
      for i in range(nyps):
          y = y + bpat
          xa = bskal*0.5 + hs
          ya = y + hs*0.5
          xt, yt = tra((xa, ya))
          dxf.thanDxfPlotNumber (xt, yt, hs, float(i+1), fdeg, -1)

      __sxFora (dxf, bskal, bpat, v.entScale, nyps, tra)
      __stairsbox(dxf, v, fdeg, tra)
      dxf.thanDxfPlot (0.0, 0.0, 999)
      ts.thanAfterImport()
      proj[1].thanLayerTree.thanDictRebuild()
      proj[2].thanRegen()
      return ts.newelems


def __sxFora (dxf, bskal, bpat, scale, nyps, tra):
      "Σχεδίαση φοράς σκάλας."
      dxf.thanDxfSetLayer ('SKALA__FORA')
      dxf.thanDxfSetColor(1)
      hs = 0.15 * scale / 100.0
      y = float(nyps-1) * bpat
      b2 = bskal * 0.50

      xt, yt = tra((b2, 0.0))
      dxf.thanDxfPlotCircle(xt, yt, hs*0.25)
      dxf.thanDxfPlot(xt, yt, 3)
      xt, yt = tra((b2, y+hs*0.5))
      dxf.thanDxfPlot (xt, yt, 2)
      xt, yt = tra((b2-hs, y))
      dxf.thanDxfPlot (xt, yt, 2)
      xt, yt = tra((b2, y+hs*0.5))
      dxf.thanDxfPlot (xt, yt, 3)
      xt, yt = tra((b2+hs, y))
      dxf.thanDxfPlot (xt, yt, 2)

def __stairsbox(dxf, v, fdeg, tra):
      "Draw a box with the tread and the rise."
      dxf.thanDxfSetColor(None)
      dxf.thanDxfSetLayer ('SKALA__FORA')
      hs = 0.15 * v.entScale / 100.0
      y = 0.0 - 10.0*hs
      y2 = y + 6.0*hs
      b2 = 8.0*hs

      xt, yt = tra((0.0, y))
      dxf.thanDxfPlot(xt, yt, 3)
      xt, yt = tra((b2, y))
      dxf.thanDxfPlot(xt, yt, 2)
      xt, yt = tra((b2, y2))
      dxf.thanDxfPlot(xt, yt, 2)
      xt, yt = tra((0.0, y2))
      dxf.thanDxfPlot(xt, yt, 2)
      xt, yt = tra((0.0, y))
      dxf.thanDxfPlot(xt, yt, 2)

      xt, yt = tra((0.0, (y+y2)/2.0))
      dxf.thanDxfPlot(xt, yt, 3)
      xt, yt = tra((b2, (y+y2)/2.0))
      dxf.thanDxfPlot(xt, yt, 2)

      dxf.thanDxfSetLayer ('SKALA__ARIT')
      xt, yt = tra((hs, y+hs))
      dxf.thanDxfPlotSymbol (xt, yt, hs, Tarch["T=%.2f"] % (v.entTread,), fdeg)
      xt, yt = tra((hs, y+4.0*hs))
      dxf.thanDxfPlotSymbol (xt, yt, hs, Tarch["R=%.3f"] % (v.labRise,), fdeg)
