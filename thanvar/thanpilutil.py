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

This module defines various untility functions for PIL library.
"""
from math import pi
import p_gindplt

def thanDash2Dash3(dash):
    "Transform a ThanCad dashed line to dash1, space1, dash2 for p_gindplt.plotdashdot()."
    dash1 = dash[0]
    if dash1 == 0: dash1 = 1    #dash1==0 means one point so we set the width to 1 pixel
    space1 = dash[1]
    if len(dash) > 2:
        dash2 = dash[2]
        if dash2 == 0: dash2 = 1    #dash2==0 means one point so we set the width to 1 pixel
    else:
        dash2 = dash1
    return dash1, space1, dash2


def thanPilLine(than, cha):
    "Draw a possibly dashed line on a PIL image."
    g2l = than.ct.global2Local
    xy1 = [g2l(c1[0], c1[1]) for c1 in cha]
    if len(than.dash) < 2:   #Here we don't fill, and the line is continuous
        than.dc.line(xy1, fill=than.outline, width=than.width)
        return
    #Dashed line
    def plotline(x1, y1, x2, y2):
        than.dc.line([x1, y1, x2, y2], fill=than.outline, width=than.width)
    dash1, space1, dash2 = thanDash2Dash3(than.dash)
    x = [temp[0] for temp in xy1]
    y = [temp[1] for temp in xy1]
    dashrem = p_gindplt.plotdashdot(plotline, x, y, dash1, space1, dash2)


def thanPilArc(than, cc, r, theta1, theta2):
    "Draw a possibly dashed arc on a PIL image."
    if len(than.dash) < 2:   #Here we don't fill, and the line is continuous
        x1, y1 = than.ct.global2Locali(cc[0]-r, cc[1]+r)  # PIL needs left,upper and ..
        x2, y2 = than.ct.global2Locali(cc[0]+r, cc[1]-r)  # ..right,lower
        #print("thanPilArc(): x1, y1=", x1, y1)
        #print("thanPilArc(): x2, y2=", x2, y2)
        t2 = -theta1/pi*180.0
        t1 = -theta2/pi*180.0
        than.dc.arc((x1, y1, x2, y2), t1, t2, fill=than.outline, width=than.width)
        return

    #Dashed arc
    def plotarc(xc, yc, r, theta1, theta2):
        x1 = round(xc-r); y1 = round(yc-r)
        x2 = round(xc+r); y2 = round(yc+r)
        t1 = theta1/pi*180.0
        t2 = theta2/pi*180.0
        than.dc.arc((x1, y1, x2, y2), t1, t2, fill=than.outline, width=than.width)

    dash1, space1, dash2 = thanDash2Dash3(than.dash)
    x1, y1 = than.ct.global2Local(cc[0], cc[1])
    r1, _ = than.ct.global2LocalRel(r, r)
    t2 = -theta1
    t1 = -theta2
    dashrem = p_gindplt.plotdashdotarc1(plotarc, x1, y1, r1, t1, t2, [dash1, -space1, dash2, -space1], ())


def thanPilCircle(than, cc, r):
    "Draw a possibly dashed circle on a PIL image."
    if len(than.dash) < 2:   #Here we don't fill, and the line is continuous
        x1, y1 = than.ct.global2Locali(cc[0]-r, cc[1]+r)  # PIL needs left,upper and ..
        x2, y2 = than.ct.global2Locali(cc[0]+r, cc[1]-r)  # ..right,lower
        than.dc.arc((x1, y1, x2, y2), 0.0, 360.0, fill=than.outline, width=than.width)
        return

    #Dashed arc
    def plotarc(xc, yc, r, theta1, theta2):
        x1 = round(xc-r); y1 = round(yc-r)
        x2 = round(xc+r); y2 = round(yc+r)
        t1 = theta1/pi*180.0
        t2 = theta2/pi*180.0
        than.dc.arc((x1, y1, x2, y2), t1, t2, fill=than.outline, width=than.width)

    dash1, space1, dash2 = thanDash2Dash3(than.dash)
    x1, y1 = than.ct.global2Local(cc[0], cc[1])
    r1, _ = than.ct.global2LocalRel(r, r)
    dashrem = p_gindplt.plotdashdotarc1(plotarc, x1, y1, r1, None, None, [dash1, -space1, dash2, -space1], ())
