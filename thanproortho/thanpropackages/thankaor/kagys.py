# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

This is the professional part of ThanCad which is initially commercial.
"""
from math import pi, fabs
import sys
from p_gmath import dpt, thanSegSeg, thanNear2
import p_ggen

def testGys(com):
    "Tests if this a GYS map, which does not have full grid points."
    com.mapCase = "NORMAL"
    if len(com.cxylines) > 0:
        if not com.corners:
            com.mapCase = "NORMAL"
            return
        if len(com.cxlines) == 2 and len(com.cylines) == 2:
            com.mapCase = "GYS4K"
            calcCorners(com)
            return
        com.prt("")
        com.prt("Warning: This map does not appear to be a defective GYS map of scale 1:5000")
        com.prt("         because it has grid points with known x and y.")
        com.prt("         In order to take into account the corner coordinates defined")
        com.prt("                  in .gan, there should be exactly 2 lines in KANABOSY and")
        com.prt("                  exactly 2 lines in KANABOSX.")
        com.prt("                  The corner coordinates  are ignored.")
        com.corners = None
        com.mapCase = "NORMAL"
        return
    if len(com.cxlines) != 2 or len(com.cylines) != 2:
        com.prt("")
        com.prt("Error: This appears to be a defective GYS map of scale 1:5000.")
        com.prt("       For defective GYS maps, there should be")
        com.prt("       exactly 2 polylines with known x and")
        com.prt("       exactly 2 polylines with known y.")
        raise p_ggen.RecordedError
    if not com.corners:
        com.mapCase = "GYSP"
        testDef(com)
        createCxylines(com)
        return
    if len(com.cxlines[0]) == 2 and len(com.cxlines[-1]) == 2 and \
       len(com.cylines[0]) == 2 and len(com.cylines[-1]) == 2:
        com.prt("")
        com.prt("Warning: This map appear to be a defective GYS map of scale 1:5000")
        com.prt("         with the only known coordinates in 4 corners of the map.")
        com.mapCase = "GYS4"
        calcCorners(com)
        return
    com.prt("")
    com.prt("Warning: This map appear to be a defective GYS map of scale 1:5000")
    com.prt("         which also has known coordinates at the 4 corners of the map.")
    com.mapCase = "GYS4P"
    calcCorners(com)
    testDef(com)
    createCxylines(com)


def calcCorners(com):
    "Assemble the corners' information."
    if com.cxlines[0][0][1] > com.cxlines[1][0][1]: com.cxlines.reverse()
    if com.cylines[0][0][0] > com.cylines[1][0][0]: com.cylines.reverse()
    if not thanNear2(com.cxlines[0][0], com.cylines[0][0]) or \
       not thanNear2(com.cxlines[0][-1], com.cylines[-1][0]) or \
       not thanNear2(com.cxlines[1][0], com.cylines[0][-1]) or \
       not thanNear2(com.cxlines[1][-1], com.cylines[-1][-1]):
        com.prt("")
        com.prt("Error: The polylines with known x and the polylines with known y")
        com.prt("should start and end at exactly the same (known) corners.")
        raise p_ggen.RecordedError
    com.corners[0] = com.cxlines[0][0]  + com.corners[0]
    com.corners[1] = com.cxlines[0][-1] + com.corners[1]
    com.corners[3] = com.cxlines[1][0]  + com.corners[3]
    com.corners[2] = com.cxlines[1][-1] + com.corners[2]
    for cline in com.cxlines+com.cylines:
        del cline[-1]
        del cline[0]


def createCxylines(com):
    "Creates fake lines with known x and y points."
    for c1,c2 in zip(com.cylines[0], com.cylines[1]):
        cline = []
        for ca,cb in zip(com.cxlines[0], com.cxlines[1]):
            ct = thanSegSeg(ca, cb, c1, c2)
            if ct == None:
                com.prt("")
                com.prt("Warning: possible error in the definitions of lines for defective GYS maps:")
                com.prt("         line with known y coordinates:")
                com.prt("         %.3f %.3f - %.3f %.3f" % (c1+c2))
                com.prt("         and line known x coordinates:")
                com.prt("         %.3f %.3f - %.3f %.3f" % (ca+cb))
                com.prt("         The lines do not intersect!")
                continue
            cline.append(ct)
        if len(cline) > 1: com.cxylines.append(cline)
    if len(com.cxylines) < 1:
        com.prt("")
        com.prt("Warning: The lines for defective GYS maps do not intersect:")
        com.prt("         No points with known x and y coordinates could be produced.")


def testDef(com):
    "Tests the data for defective maps."
    if len(com.cxlines[0]) != len(com.cxlines[1]):
        com.prt("")
        com.prt("Error: For defective GYS maps, the polylines with known x")
        com.prt("       should have the same number of points.")
        raise p_ggen.RecordedError
    if len(com.cylines[0]) != len(com.cylines[1]):
        com.prt("")
        com.prt("Error: For defective GYS maps, the polylines")
        com.prt("       with known y should have the same number of points.")
        raise p_ggen.RecordedError
#    if com.corners:
#        if len(com.cxlines[0]) == 2 and len(com.cylines[0]) == 2: return

    thmx = testDirDef(com.prt, com.cxlines, "x")
    thmy = testDirDef(com.prt, com.cylines, "y")
    thmy1 = thmx + pi/2
    if fabs(dpt(thmy-thmy1) - pi) <= pi/10:
        com.prt("")
        com.prt("Error: the polylines with known x, or the polylines polylines with known y,")
        com.prt("       are probably reversed.")
        raise p_ggen.RecordedError
    if fabs(dpt(thmy)-dpt(thmy1)) > pi/10 and \
       fabs(dpt(thmy+pi)-dpt(thmy1+pi)) > pi/10:
        com.prt("")
        com.prt("Error: For defective GYS maps, the polylines with known x and")
        com.prt("       the polylines with known y, should be perpendicular.")
        raise p_ggen.RecordedError


def testDirDef(prt, cxlines, txy):
    "Checks direction of points of many lines, avoiding angle wrap-around at 2pi rad."
    for dth in (0.0, 0.5*pi, pi, 1.5*pi):
#    for dth in (0.0, pi):
        thm = testDirthDef(prt, cxlines, txy, dth)
        if thm != "error": break
    assert thm != "error", "Program logic error: This error should have been found."
    return dpt(thm-dth)


def testDirthDef(prt, cxlines, txy, dth):
    "Checks direction of points of many lines."
    from kaor import testdir1
    ths = []
    for cline in cxlines:
        th1, erth = testdir1(cline, dth)
        if erth > pi/20:
            if dth < 1.4*pi: return "error"
            prt("")
            prt("Error: In the following grid line with known %s:" % txy)
            for c in cline: prt("       %15.3f%15.3f" % c)
            prt("       At least one line segment has too different a direction.")
            raise p_ggen.RecordedError
        ths.append(th1)
    if fabs(dpt(ths[0]-ths[1]) - pi) <= pi/10:
        prt("")
        prt("Error: one of the grid lines with known %s, is probably reversed." % txy)
        prt("       The program does not know which is the positive %s direction." % txy)
        raise p_ggen.RecordedError
    thm = sum(ths)/len(ths)
    erth, i = max([(fabs(th1-thm), i) for i,th1 in enumerate(ths)])
    if erth > pi/20:
        if dth < 1.4*pi: return "error"
        prt("")
        prt("Error: In the following grid line with known %s:" % txy)
        for c in cxlines[i]: prt("       %15.3f%15.3f" % c)
        prt("       This line has too different a direction.")
        raise p_ggen.RecordedError
    return thm
