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
It is assumed that the cxylines are digitized in the positive
world X direction.
A center of a circle shows which point's world coordinates are given.
This point is assumed to match exactly a point in cxylines.
"""

from math import fabs, sqrt, cos, sin, atan2, pi, hypot
from p_gfil import *
from p_ggen import iterby2, RecordedError, path, xfrangec
from p_ggeom import TriLocal, MesaTri
from p_gmath import dpt
import kade, kadxf, kagys


class ThanKaor:
    "Class to make program kaor able to run into ThanCad and standalone."

    def __init__(self):
        "Initial values for common variables needed throughout the program kaor."
        self.cxylines = [] # Lines with known world coordinates (grid points). ThanCad layer kanabosxy
        self.cxlines  = [] # Lines with known x world coordinates layer. ThanCad layer kanabosx
        self.cylines  = [] # Lines with known y world coordinates layer. ThanCad layer kanabosy
        self.clines   = [] # Lines with unknown world coordinates layer. ThanCad layer plaisio
                           # They are used to limit the area for the orthorectification

        self.cor  = None # Point of origin as center of circle. ThanCad layer kanabosxy
        self.corx = None # Point of x-origin as center of circle; only when cor==None. ThanCad layer kanabosx
        self.cory = None # Point of y-origin as center of circle; only when cor==None. ThanCad layer kanabosy
        self.cwor = None # World coordinates of point of origin

        self.corners = None  # The world coordinates of the 4 corners of a defective
                             # GYS map of scale 1:5000. The first corner is the corner
                             # with smaller x and smallest y, and then counterclockwise.
        self.mapCase = None  # The kind of map that is going to rectified:
                             # NORMAL = combination of cxlines, cylines, cxylines, clines
                             # GYS5K  = Defective GYS MAP of scale 1:5000 with no
                             #          x-y gridpoints known.
                             # GYS5K-4= Defective GYS MAP of scale 1:5000 with the only
                             #          known grid points in 4 corners and nonthin else

        self.metEgsa = False # If True, the computed world coordinates are thought to be
                             # in Greek HATT datum, and they are converted to Greek EGSA datum.
        self.asMet = None    # 6 coefficients for the HATT->EGSA transformation (x-axis)
        self.bsMet = None    # 6 coefficients for the HATT->EGSA transformation (y-axis)
        self.dxMet = 0.0     # This value will be substracted from the computed x coordinates
        self.dyMet = 0.0     # This value will be substracted from the computed y coordinates
                             # (after the HATT->EGSA tranfromation if metEgsa == True)

        self.dwkan = 50.0 # distance between grid points in world coordinates (usually 50m for scale 1:500)
        self.dkan = 100.0 # distance between grid points in mm (usually 100mm for scale 1:500)
        self.thres = self.dkan/8.0  # Threshold: bigger remainder from multiple of dkan between grid points is considered error
        self.dpi  = 72.0  # Resolution of the input image in dpi (for example 300dpi)
        self.tomm = 25.4/self.dpi   # Factor for converting dots to mm

        self.cfull = []   # Computed points coordinates as tuples (pixel-x, pixel-y, world-x, world-y)
        self.frw = {}     # Opened file streams
        self.prt = None   # The function whicg prints output. For stanadlone programs
                          #   ususally prt = p_ggen.prg

        self.vdir = ( (1.0, 0.0),   # direction of world x in pixel system
                      (0.0, 1.0),   # direction of world y in pixel system                )
                    )


    def thanMain(com):
        "Main routine for standalone program."
        com.prt = prg
        frw = kade.openFiles(com)
        kade.readGen(com)
        com.tomm = 25.4/com.dpi
        kadxf.readDxf(com)

        kagys.testGys(com)
        testDistance(com)
        thm = testDir(com)
        com.vdir = ( (cos(thm),        sin(thm)),         # direction of world x in pixel system
                     (cos(thm+pi*0.5), sin(thm+pi*0.5)),  # direction of world y in pixel system
                   )
        if com.cor != None:
            com.cgridx =  [(com.cor[0], com.cor[1], com.cwor[0], com.cwor[1])]
            com.cgridy =  [(com.cor[0], com.cor[1], com.cwor[0], com.cwor[1])]
            com.cgridxy = [(com.cor[0], com.cor[1], com.cwor[0], com.cwor[1])]
        else:
            com.cgridx =  [(com.corx[0], com.corx[1], com.cwor[0], None)]
            com.cgridy =  [(com.cory[0], com.cory[1], None,        com.cwor[1])]
            com.cgridxy = []
        worldcxy(com)
#        del com.cfull[0]                              # Delete known point (it is probably duplicate)
        kade.writeFile(com)
        kade.writeGor(com)
        kade.closeFiles()


    def thanMainTcad(com, proj, v, prt):
        "Main routine, if the program is run within ThanCad."
#        frw = kade.openFiles(com)
        com.prt = prt
        fn = kade.readGenTcad(com, proj, v)
        fn = path(fn)
        fn = fn.parent / fn.namebase
        com.frw.update(opFile1e(1, 'syp', ' ', fn, 'αποτελεσμάτων'))
        com.frw.update(opFile1e(1, 'nsy', ' ', fn, 'αντιγρ. αποτελεσμάτων'))
        com.frw.update(opFile1e(1, 'gor', ' ', fn, 'γενικών δεδομένων αναγωγής'))
        com.frw.update(opFile1e(1, 'nb1', ' ', fn, 'break lines'))

        com.tomm = 25.4/com.dpi
        kadxf.readTcad(com, proj)

        kagys.testGys(com)
        if com.mapCase == "GYS4":
            worldcxy_gys4(com)
        else:
            testDistance(com)
            thm = testDir(com)
            com.vdir = ( (cos(thm),        sin(thm)),         # direction of world x in pixel system
                         (cos(thm+pi*0.5), sin(thm+pi*0.5)),  # direction of world y in pixel system
                       )
            origin(com)
            worldcxy(com)
        kade.writeFile(com)
        kade.writeGor(com)
        for fun in com.frw.itervalues(): fun.close()
        return fn


def origin(com):
    "Ensure that the origin coincides with one or two grid points."     #Thanasis2007_05_19
    cx = []
    for cline1 in com.cxylines: cx.extend(cline1)
    cy = cx[:]
    for cline1 in com.cxlines: cx.extend(cline1)
    for cline1 in com.cylines: cy.extend(cline1)

    r = (com.dkan/200.0)          # Equivalent to 0.5mm if distance of grid points is 100mm (usual)
    if com.cor != None: crx = cry = com.cor
    else:               crx = com.corx; cry = com.cory

    xongrid = False
    for c1 in cx:
        if fabs(c1[0]-crx[0]) <= r: xongrid = True; break
    yongrid = False
    for c1 in cy:
        if fabs(c1[1]-cry[1]) <= r: yongrid = True; break

    if xongrid and yongrid:
        com.cgridx =  [(crx[0], crx[1], com.cwor[0], None)]
        com.cgridy =  [(cry[0], cry[1], None,        com.cwor[1])]
        if com.cor != None: com.cgridxy = [(crx[0], crx[1], com.cwor[0], com.cwor[1])]  # Note that here crx==cry
        else:               com.cgridxy = []
    else:
        if xongrid: com.cgridx =  [(crx[0], crx[1], com.cwor[0], None)]
        else:       makeOrigc(com, 0, crx, cx)

        if yongrid: com.cgridy =  [(cry[0], cry[1], None, com.cwor[1])]
        else:       makeOrigc(com, 1, cry, cy)
        com.cgridxy = []


def makeOrigc(com, i, cr, cx):
        "Compute the world coordinates of a grid point and make it origin."
        com.prt("")
        com.prt("Warning: The known %s-coordinate of the origin (defined by a circle)" % "XY"[i])
        com.prt("         in layer KANABOS/KANABOS%s)" % "XY"[i])
        com.prt("         does not correspond to any grid point.")
        a, b = findnearest2(com, cr, i, cx)
        if a == None:
            com.prt("")
            com.prt("Error: there must be at least 2 %s grid points near the %s origin." % ("XY"[i], "XY"[i]))
            raise RecordedError
        dpix, dwor = distc(com, a, b, i)
        scale = dwor/dpix        # Always positive
        dpix = distp(com, cr, a, i)
        if i == 0:
            com.cgridx =  [(a[0], a[1], com.cwor[i]+dpix*scale, None)]
        else:
            com.cgridy =  [(a[0], a[1], None, com.cwor[i]+dpix*scale, None)]


def distp(com, a, b, i):
    "Computes the pixel coordinate distance at x or y direction of point b - point a."
    return (b[0]-a[0])*com.vdir[i][0] + (b[1]-a[1])*com.vdir[i][1]


def distc(com, a, b, i):
    "Computes the pixel and the world coordinate distance at x or y direction of grid point b - grid a."
    d = distp(com, a, b, i)
    n, rem = divmod(fabs(d*com.tomm), com.dkan)
    if rem > com.dkan*0.5: n+=1; rem = com.dkan-rem
    if rem > max(1,n)*com.thres:
        com.prt("")
        com.prt("Error: Vertical or horizontal distance of points %.1f, %.1f and %.1f, %.1f" % (a[0], a[1], b[0], b[1]))
        com.prt("       is not a multiple of %f" % com.dkan)
        raise RecordedError
    if d < 0.0: return d, -n*com.dwkan
    else:       return d,  n*com.dwkan


def worldcxy(com):
    "Compute the world coordinates of the points of cxylines."
    for cline in com.cxylines:
        for c in cline:
            x, y = computegridxy(com, c)
            com.cfull.append((c[0], c[1], x, y))
            com.cgridxy.append((c[0], c[1], x, y))
            com.cgridx.append((c[0], c[1], x, y))
            com.cgridy.append((c[0], c[1], x, y))

    for cline in com.cxlines:
            for c in cline:
                x = computegridc(com, c, 0)
                y = computec(com, c, 1)
                com.cfull.append((c[0], c[1], x, y))
                com.cgridx.append((c[0], c[1], x, y))

    for cline in com.cylines:
            for c in cline:
                x = computec(com, c, 0)
                y = computegridc(com, c, 1)
                com.cfull.append((c[0], c[1], x, y))
                com.cgridy.append((c[0], c[1], x, y))

    if com.corners:  # In case of the PLAISIO points, use known corner points as well. Also, add to the final points
        checkCorners(com)
        for g in com.cgridxy, com.cgridx, com.cgridy, com.cfull:
            for c in com.corners: g.append(c)

    for cline in com.clines:
        for c in cline:
            x = computec(com, c, 0)
            y = computec(com, c, 1)
            com.cfull.append((c[0], c[1], x, y))


def checkCorners(com):
    "Check that the coordinates of corners given by the user are not too diffrent."
    dmax = com.thres/com.dkan*com.dwkan    # Threshold in world coordinates
    for i, c in enumerate(com.corners):
        x = computec(com, c, 0)
        y = computec(com, c, 1)
#        print "corner i: world xy:", c[2], c[3], "should be about:", x, y
        if fabs(x-c[2]) > 10.0*dmax or fabs(y-c[3]) > 10.0*dmax:
            com.prt("")
            com.prt("Error:   The user supplied world coordinates of corner point %d" % (i+1,))
            com.prt("         are not consistent with the coordinates of neiboring grid point.")
            raise RecordedError
        elif fabs(x-c[2]) > dmax or fabs(y-c[3]) > dmax:
            com.prt("")
            com.prt("Warning: The user supplied world coordinates of corner point %d" % (i+1,))
            com.prt("         are not consistent with the coordinates of neiboring grid point.")


def worldcxy_gys4(com):
    """Compute the world coordinates in case of only 4 known corners.

    We interpolate points inside the region defined by the 4 corners
    and calculate the local and global coordinates. Each point belongs
    to a triangle.
    """
    pxc = [c[0] for c in com.corners]      # Pixel x coordinate of each corner
    pyc = [c[1] for c in com.corners]      # Pixel y coordinate of each corner
    xc = [c[2] for c in com.corners]       # World x coordinate of each corner
    yc = [c[3] for c in com.corners]       # World y coordinate of each corner
    xmin = min(xc)
    ymin = min(yc)
    xmax = max(xc)
    ymax = max(yc)
    x1 = int(xmin/com.dwkan + 1) * com.dwkan        # Limits for kanabos iterations
    if x1-xmin < com.dwkan*0.10: x1 += com.dwkan
    y1 = int(ymin/com.dwkan + 1) * com.dwkan
    if y1-ymin < com.dwkan*0.10: y1 += com.dwkan
    x2 = int(xmax/com.dwkan - 1) * com.dwkan
    if xmax-x2 < com.dwkan*0.10: x2 -= com.dwkan
    y2 = int(ymax/com.dwkan - 1) * com.dwkan
    if ymax-y2 < com.dwkan*0.10: y2 -= com.dwkan

    ta = TriLocal(xc[0], yc[0], xc[1], yc[1], xc[2], yc[2])    # First triangle
    ma = MesaTri(xc[0], yc[0], xc[1], yc[1], xc[2], yc[2])     # Inclusion for first triangle
    tb = TriLocal(xc[2], yc[2], xc[3], yc[3], xc[0], yc[0])    # Second triangle
    mb = MesaTri(xc[2], yc[2], xc[3], yc[3], xc[0], yc[0])     # Inclusion for second triangle

    for xw in xfrangec(x1, x2, com.dwkan):                     # Loop over all grid points
        for yw in xfrangec(y1, y2, com.dwkan):
            if ma.mesa(xw, yw):                                # Is it inside the first triangle?
                px = ta.interg(pxc[0], pxc[1], pxc[2], xw, yw) # Interpolate pixel x
                py = ta.interg(pyc[0], pyc[1], pyc[2], xw, yw) # Interpolate pixel x
                com.cfull.append((px, py, xw, yw))
            elif mb.mesa(xw, yw):                              # Is it inside the second triangle?
                px = tb.interg(pxc[2], pxc[3], pxc[0], xw, yw) # Interpolate pixel x
                py = tb.interg(pyc[2], pyc[3], pyc[0], xw, yw) # Interpolate pixel y
                com.cfull.append((px, py, xw, yw))

    for c in com.corners:        # Add corners to the points
        com.cfull.append(c)


def computegridxy(com, a):
    "Computes world coordinates of grid point a."
    cfnear = findnearest(com, a, 0, com.cgridx)
    if cfnear == None:
        com.prt("\nError: Coordinate %s of grid point %.1f, %.1f can not be computed." % ("XY"[0], a[0], a[1]))
        raise RecordedError
    x = computegridct(com, a, cfnear, 0)
    cfnear = findnearest(com, a, 1, com.cgridy)
    if cfnear == None:
        com.prt("\nError: Coordinate %s of grid point %.1f, %.1f can not be computed." % ("XY"[1], a[0], a[1]))
        raise RecordedError
    y = computegridct(com, a, cfnear, 1)
    return x, y

def computegridc(com, a, i):
    "Computes world coordinates of grid point a."
    if i == 0: cfnear = findnearest(com, a, i, com.cgridx)
    else:      cfnear = findnearest(com, a, i, com.cgridy)
    if cfnear == None:
        com.prt("\nError: Coordinate %s of grid point %.1f, %.1f can not be computed." % ("XY"[i], a[0], a[1]))
        raise RecordedError
    c = computegridct(com, a, cfnear, i)
    return c

def computegridct(com, a, cfnear, i):
    "Computes world coordinate x (i=0) or y (i=1) of grid point a (given in pixels) using full point cfnear."
    d = hypot(a[0]-cfnear[0], a[1]-cfnear[1])      #2009_03_24
    nd = int(d/com.dkan+0.5)                       #2009_03_24
    d = (a[0]-cfnear[0])*com.vdir[i][0] + (a[1]-cfnear[1])*com.vdir[i][1]
    n, rem = divmod(fabs(d*com.tomm), com.dkan)
    if rem > com.dkan*0.5: n+=1; rem = com.dkan-rem
    if rem > max(1,nd)*com.thres:                  #2009_03_24:change from n to nd
        com.prt("")
        com.prt("n=%d  rem=%f  d=%f" % (n, rem, d))
        com.prt("Error: Vertical or horizontal distance of points %.1f, %.1f and %.1f, %.1f" % (a+cfnear[:2]))
        com.prt("       is not a multiple of %f" % com.dkan)
        raise RecordedError
    if d < 0.0: c = cfnear[2+i] - n*com.dwkan
    else:       c = cfnear[2+i] + n*com.dwkan
    return c

def computec(com, a, i):
    "Computes world coordinate i of random point a (given in pixels)."
    if i == 0: cfnear1, cfnear2 = findnearest2(com, a, i, com.cgridx)
    else:      cfnear1, cfnear2 = findnearest2(com, a, i, com.cgridy)
    if cfnear1 == None:
        com.prt("")
        com.prt("Error: Coordinate %s of non-grid point %.1f, %.1f can not be computed." % \
	        ("XY"[i], a[0], a[1]))
	raise RecordedError
    cp1 = cfnear1[0]*com.vdir[i][0] + cfnear1[1]*com.vdir[i][1]
    cp2 = cfnear2[0]*com.vdir[i][0] + cfnear2[1]*com.vdir[i][1]
    cpa =       a[0]*com.vdir[i][0] +       a[1]*com.vdir[i][1]
    c = cfnear1[2+i] + (cfnear2[2+i]-cfnear1[2+i])/(cp2-cp1) * (cpa-cp1)
#    k68 =  14364.2,    9413.1,      8558.428,     -19648.291
#    if (a[0]-k68[0])**2 + (a[1]-k68[1])**2 < 0.1:
#        print "k68=", k68
#        print cfnear1
#	print cfnear2
#	print "cp1=", cp1
#	print "cp2=", cp2
#	print "cpa=", cpa
#        print cp2-cp1, "\t", cpa-cp1
    return c


def findnearest(com, a, i, cgrid_):
    "Find nearest point of cgrid[x|y] points to point c in the direction i; all coordinates in pixels."
    cfnear = []
    for cf in cgrid_:
        n = 1 - i
        d  = (a[0]-cf[0])*com.vdir[i][0] + (a[1]-cf[1])*com.vdir[i][1]
        dn = (a[0]-cf[0])*com.vdir[n][0] + (a[1]-cf[1])*com.vdir[n][1]
#       d1 = sqrt((a[0]-cf[0])**2         + (a[1]-cf[1])**2)
	cfnear.append((fabs(d)+4*fabs(dn), d, cf))
    if len(cfnear) < 0: return None
    return min(cfnear)[-1]

def findnearest2(com, a, i, cgrid_):
    "Find 2 nearests points of cfull points to point c in the direction i; all coordinates in pixels."
    cfnear = []
    for cf in cgrid_:
        n = 1 - i
        d  = (a[0]-cf[0])*com.vdir[i][0] + (a[1]-cf[1])*com.vdir[i][1]
        dn = (a[0]-cf[0])*com.vdir[n][0] + (a[1]-cf[1])*com.vdir[n][1]
#       d1 = sqrt((a[0]-cf[0])**2         + (a[1]-cf[1])**2)
	cfnear.append((fabs(d)+4*fabs(dn), d, cf))
    cfnear.sort()
    for (da1, d1, cf1), (da2, d2, cf2) in iterby2(cfnear):
        if fabs(d2-d1)*com.tomm > com.dkan*0.5:
	    return cf1, cf2
    return None, None

def testDistance(com):
    "Checks distance of points of a line."
    for cline in com.cxylines:
        i = 1
	while i<len(cline):
	    if fabs(cline[i][0]-cline[i-1][0])+fabs(cline[i][1]-cline[i-1][1]) < 4:
	        com.prt("")
	        com.prt("Warning: In the following line segment:")
		for c in cline[i-1:i+1]: com.prt("%15.3f%15.3f" % c)
	        com.prt("         Duplicate point is removed.")
		del cline[i]
	    else:
	        i += 1
        for a,b in iterby2(cline):
	    d = sqrt((a[0]-b[0])**2+(a[1]-b[1])**2) * com.tomm
	    n, rem = divmod(d, com.dkan)
	    if rem > com.dkan*0.5: n+=1; rem = com.dkan-rem
	    if rem > max(1,n)*com.thres:
	        com.prt("")
	        com.prt("Error: In the following line segment:")
		for c in a, b: com.prt("%15.3f%15.3f" % c)
	        com.prt("       Distance is not a multiple of %f mm." % com.dkan)
	        raise RecordedError
    i = 0
    while i<len(com.cxylines):
        if len(com.cxylines[i]) < 2:
	    com.prt("\nWarning: Degenerate line with less than 2 points is removed.")
            del com.cxylines[i]
        else:
            i += 1

def testDir(com):
    "Checks direction of points of a many lines."
    if com.mapCase == "GYS5K-4":
        x1, y1 = com.corners[0]
        x2, y2 = com.corners[1]
        return dpt(atan2(y2-y1, x2-x1))
    for dth in (0.0, 0.5*pi, pi, 1.5*pi):
#    for dth in (0.0, pi):
        thm = testdirdth(com, dth)
        if thm != "error": break
    assert thm != "error", "Program logic error: This error should have been found."
    return dpt(thm-dth)

def testdirdth(com, dth):
    "Checks direction of points of a many lines."
    ths = []
    for cline in com.cxylines:
        th1, erth = testdir1(cline, dth)
        if erth > pi/20:
            if dth < 1.4*pi: return "error"
	    com.prt("")
	    com.prt("Error: In the following grid line:")
	    for c in cline: com.prt("%15.3f%15.3f" % c)
            com.prt("       At least one line segment has too different a direction.")
	    raise RecordedError
        ths.append(th1)
#---dth is probably correct at this point. Check for reversed lines.
    thref = ths[0]; nr = 0
    for th in ths:
        if fabs(dpt(th-thref) - pi) <= pi/10: nr += 1
    if nr > len(ths)/2: thref = dpt(thref+pi)  # Probably this is the positive direction
    for i in xrange(len(ths)):
        if fabs(dpt(ths[i]-thref) - pi) <= pi/10:
	    com.prt("")
	    com.prt("Warning: In the following grid line:")
	    for c in com.cxylines[i]: com.prt("%15.3f%15.3f" % c)
	    com.prt("         Line is probably reversed.")
	    com.cxylines[i].reverse()
            ths[i] = dpt(ths[i]+pi)
#---Now check for big differences in mean directions.
    thm = sum(ths)/len(ths)
    erth, i = max([(fabs(th1-thm), i) for i,th1 in enumerate(ths)])
    if erth > pi/20:
        if dth < 1.4*pi: return "error"
	com.prt("")
	com.prt("Error: In the following grid line:")
	for c in com.cxylines[i]: com.prt("%15.3f%15.3f" % c)
        com.prt("       Line has too different a direction.")
        raise RecordedError
    return thm

def testdir1(cline, dth):
    "Finds the biggest difference of direction with mean direction."
    th = [dpt(atan2(b[1]-a[1], b[0]-a[0])+dth) for a,b in iterby2(cline)]
    thm = sum(th)/len(th)
    return thm, max([fabs(th1-thm) for th1 in th])


if __name__ == "__main__":
    k = ThanKaor()
    k.thanMain()
