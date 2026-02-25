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

Package which creates a highway interchange.
"""
import sys
from math import cos, sin, pi
from p_gmath import dpt
from p_gvec import Vector2
from p_ggen import prg, frangec

def main1():
      from p_gdxf import ThanDxfPlot
      x1, y1 = 100, 100
      x2, y2 = 500, 500
      x3, y3 = 600, 100
      A1 = A2 = A3 = 120
      R1 = 200; R2 = 100
      A, B, v1, v2, v3, v4, v5, L1, L2a, L2b, L3, LC1, LC2, th0, th1, th2, th3, th4, pr, terr = \
      calcARARA(prg, x1, y1, x2, y2, x3, y3, A1, R1, A2, R2, A3, convex=False)
      if terr is not None:
          prg("Λάθος κατά τη χάραξη του κόμβου:")
          prg(terr)
          sys.exit(1)
      dxf = ThanDxfPlot()
      dxf.thanDxfPlots1()
      defDxf(dxf)
      dxf.thanDxfSetLayer("polyg")
      dxf.thanDxfPlot(x1, y1, 3)
      dxf.thanDxfPlot(x2, y2, 2)
      dxf.thanDxfPlot(x3, y3, 2)
      dxf.thanDxfSetLayer("road")
      dxf.thanDxfPlot(x1, y1, 3)
      dxf.thanDxfPlot(A.x, A.y, 2)
      dxf.thanDxfPlot(B.x, B.y, 3)
      dxf.thanDxfPlot(x3, y3, 2)
      sxedVec(dxf, A, v1, v2, v3, v4, v5)
      sxedCurve(dxf, A1, A2, A3, R1, R2, A, B, L1, L2a, L2b, L3, LC1, LC2, th0, th1, th2, th3, th4, pr)
      dxf.thanDxfPlot(0, 0, 999)


def thanMainTcad(proj, lin1):
      "Run the program from within ThanCad."
      x1, y1 = lin1.cp[0][:2]
      x2, y2 = lin1.cp[1][:2]
      x3, y3 = lin1.cp[2][:2]
      A1 = A2 = A3 = 120
      R1 = 200; R2 = 100
      prt = proj[2].thanPrt
      A, B, v1, v2, v3, v4, v5, L1, L2a, L2b, L3, LC1, LC2, th0, th1, th2, th3, th4, pr, terr = \
      calcARARA(prt, x1, y1, x2, y2, x3, y3, A1, R1, A2, R2, A3, convex=False)
      if terr is not None:
          prt("Λάθος κατά τη χάραξη του κόμβου:", "can")
          prt(terr, "can")
          return

      import thanimp, thansupport
      ts = thanimp.ThanCadDrSave(proj[1], prt)
      dxf = thansupport.ThanDxfEmu()
      dxf.thanDxfPlots1(ts)
      defDxf(dxf)
      dxf.thanDxfSetColor(None)          #Use layer color
      dxf.thanDxfSetLayer("polyg")
      dxf.thanDxfPlot(x1, y1, 3)
      dxf.thanDxfPlot(x2, y2, 2)
      dxf.thanDxfPlot(x3, y3, 2)
      dxf.thanDxfSetLayer("road")
      dxf.thanDxfPlot(x1, y1, 3)
      dxf.thanDxfPlot(A.x, A.y, 2)
      dxf.thanDxfPlot(B.x, B.y, 3)
      dxf.thanDxfPlot(x3, y3, 2)
      ts.thanAfterImport()
      sxedVec(dxf, A, v1, v2, v3, v4, v5)
      sxedCurve(dxf, A1, A2, A3, R1, R2, A, B, L1, L2a, L2b, L3, LC1, LC2, th0, th1, th2, th3, th4, pr)
      dxf.thanDxfPlot(0, 0, 999)

      proj[1].thanLayerTree.thanDictRebuild()
      proj[1].thanTouch()
      proj[2].thanRegen()
      proj[2].thanUpdateLayerButton()


def calcARARA(prt, x1, y1, x2, y2, x3, y3, A1, R1, A2, R2, A3, convex):
    "Compute angles of  circular arcs."
    global aphi2a, thf
    x1+=0.0; y1+0.0; x2+=0.0; y2+0.0; x3+=0.0; y3+0.0
    A1+=0.0; R1+0.0; A2+=0.0; R2+0.0; A3+=0.0

    t1 = Vector2(x2-x1, y2-y1).unit()
    n1 = t1.normal()
    t2 = Vector2(x3-x2, y3-y2).unit()
    th0 = t1.atan2()
    thf = t2.atan2()
    dth = dpt(thf-th0)
    if convex:
        if dth > pi: dth = 2*pi-dth
        if n1|t2 > 0.0: pr= 1   # left turn
        else          : pr=-1   # right turn
    else:
        if dth < pi: dth = 2*pi-dth
        if n1|t2 > 0.0: pr=-1   # right turn
        else          : pr= 1   # left turn
        prt("pr=%f" % pr)

    aphi1 = A1**2/(2*R1**2); L1 = A1**2/R1
    aphi2a = A2**2/(2*R1**2); aphi2b = A2**2/(2*R2**2); L2a = A2**2/R1; L2b = A2**2/R2
    aphi3 = A3**2/(2*R2**2); L3 = A3**2/R2
    phi1 = phi2 = (dth - aphi1 - (aphi2b-aphi2a) - aphi3)*0.5
    if phi1 <= 0.0: return tuple(19*[None]+["No room for circular arcs."])
    LC1 = phi1*R1; LC2 = phi2*R2
    v1 = klotVec(A1, L1, pr).rot(th0)
    th1 = th0 + aphi1*pr
    prt("th1=%f\tphi1=%f" % (th1*180/pi, phi1*180/pi))
    v2 = circVec(R1, LC1, pr)
    prt("v2=%s" % v2)
    v2 = circVec(R1, LC1, pr).rot(th1)
    prt("v2=%s" % v2)
    th2 = th1 + phi1*pr
    v3 = (klotVec(A2, L2b, pr)-klotVec(A2, L2a, pr)).rot(th2-aphi2a*pr)
    th3 = th2 + (aphi2b-aphi2a)*pr
    v4 = circVec(R2, LC2, pr).rot(th3)
    th4 = th3 + phi2*pr
    v5 = -klotVec(A3, L3, -pr).rot(thf+pi)
    v = v1 + v2 + v3 + v4 + v5
    a, b = v.anal(t1, t2)

    A = Vector2(x2, y2) - a*t1
    B = Vector2(x2, y2) + b*t2
    return A, B, v1, v2, v3, v4, v5, L1, L2a, L2b, L3, LC1, LC2, th0, th1, th2, th3, th4, pr, None


def klotVec(A, L, pr):
    "Computes a vector for the beginning to end of a klot."
    return Vector2(L-L**5/(40*A**4), pr*(L**3/(6*A**2)-L**7/(336*A**6)))

def circVec(R, L, pr):
    "Computes a vector for the beginning to end of a circular arc."
    phi = L / R
    return Vector2(R*sin(phi), pr*R*(1-cos(phi)))

def sxedVec(dxf, A, v1, v2, v3, v4, v5):
    "Plots the vectors found."
    t = A
    dxf.thanDxfPlot(t.x, t.y, 3)

    dxf.thanDxfSetLayer("klot")
    t += v1
    dxf.thanDxfPlot(t.x, t.y, 2)

    dxf.thanDxfSetLayer("circle")
    t += v2
    dxf.thanDxfPlot(t.x, t.y, 2)

    dxf.thanDxfSetLayer("klot")
    t += v3
    dxf.thanDxfPlot(t.x, t.y, 2)

    dxf.thanDxfSetLayer("circle")
    t += v4
    dxf.thanDxfPlot(t.x, t.y, 2)

    dxf.thanDxfSetLayer("klot")
    t += v5
    dxf.thanDxfPlot(t.x, t.y, 2)

def sxedCurve(dxf, A1, A2, A3, R1, R2, A, B, L1, L2a, L2b, L3, LC1, LC2, th0, th1, th2, th3, th4, pr):
    "Plots the curve."
    DL = 3
    t = A
    dxf.thanDxfPlotPolyVertex(t.x, t.y, 3)

    dxf.thanDxfSetLayer("klot")
    for L in frangec(0, L1, DL):
        tt = t + klotVec(A1, L, pr).rot(th0)
        dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)
    dxf.thanDxfPlotPolyVertex(0, 0, 999)
    dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)

    t = tt
    dxf.thanDxfSetLayer("circle")
    for L in frangec(0, LC1, DL):
        tt = t + circVec(R1, L, pr).rot(th1)
        dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)
    dxf.thanDxfPlotPolyVertex(0, 0, 999)
    dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)

    t = tt
    dxf.thanDxfSetLayer("klot")
    for L in frangec(L2a, L2b, DL):
        tt = t + (klotVec(A2, L, pr)- klotVec(A2, L2a, pr)).rot(th2-aphi2a*pr)
        dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)
    dxf.thanDxfPlotPolyVertex(0, 0, 999)
    dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)

    t = tt
    dxf.thanDxfSetLayer("circle")
    for L in frangec(0, LC2, DL):
        tt = t + circVec(R2, L, pr).rot(th3)
        dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)
    dxf.thanDxfPlotPolyVertex(0, 0, 999)
    dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)

    t = B
    dxf.thanDxfSetLayer("klot")
    for L in frangec(L3, 0, -DL):
        tt = t + klotVec(A3, L, -pr).rot(thf+pi)
        dxf.thanDxfPlotPolyVertex(tt.x, tt.y, 2)
    dxf.thanDxfPlotPolyVertex(0, 0, 999)

def defDxf(dxf):
    "Initial definition for dxf library."
    dxf.thanDxfTableDef (' ', 0)
    dxf.thanDxfTableDef('LAYER', 4)
    dxf.thanDxfCrLayer('klot',     1, 'CONTINUOUS', frozen=False)
    dxf.thanDxfCrLayer('circle', 2, 'CONTINUOUS', frozen=False)
    dxf.thanDxfCrLayer('road',   3, 'CONTINUOUS', frozen=False)
    dxf.thanDxfCrLayer('polyg',  7, 'CONTINUOUS', frozen=False)
    dxf.thanDxfTableDef ('ENTITIES', 1)

if __name__ == "__main__": main1()
