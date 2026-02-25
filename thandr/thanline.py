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

This module defines the polyline element.
"""
from itertools import izip, islice
from math import fabs, hypot, pi, atan2
import bisect
from p_ggen import iterby2, thanUnicode
from p_gmath import dpt, PI2, thanNearx, thanNear2, thanNear3, fsign
from p_gvec import Vector2
import p_ggeom
import thanintall
from thanelem import ThanElement
from thanvar import Canc, thanCleanLine3
from thanvar.thanoffset import thanOffsetLine
from thantrans import T
try: import pyx
except ImportError: pass


class ThanLine(ThanElement):
    "A Basic simple 2d line."
    thanElementName = "LINE"    # Name of the element's class

    def thanSet (self, cp):
        """Sets the attributes of the line.
	If len(cp) == 0 or == 1, all the methods work (they produce nothing)
	except the thanBreak, thanSegNearest, thanTkContinue, thanTkDraw and others.
	Thus it is imperative to call thanIsNormal() to see if the line is degenerate
	before attempting any of the above functions.
	"""
	self.cp = thanCleanLine3(cp)        #FIXME: thanCleanLine3 cleans 3dimensional degenerate segments;..
	if len(self.cp) > 0:                #..
	    xp = [c1[0] for c1 in self.cp]  #Thus 2d algorithms may fail if deltax==deltay==0 CHECK ALL THE OPERATIONS..
	    yp = [c1[1] for c1 in self.cp]  #Is thanCleanLine still necessary (it is used in ThanRoad only)???
            self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])
#	self.thanTags = ()            # thanTags is initialised in ThanElement


    def thanReverse(self):
        "Reverse the sequence of the nodes."
        self.cp.reverse()


    def thanIsNormal(self):
        "Returns False if the line is degenerate (it has only one point)."
#       if len(cp) == 2 and it is closed then it is degenerate and this function returns false
#       if len(cp) == 3 and it is closed then it is degenerate polygon but
#       a good line, so this function returns True
        if len(self.cp) < 2: return False   # Return False if line is degenerate
	cp = iter(self.cp)
	c1 = cp.next()
	for c2 in cp:
	    if not thanNear3(c1, c2): return True
	return False      # All line points are close together


    def thanClean(self):
        "Clean zero lengthed segments."
        self.cp = thanCleanLine3(self.cp)


#    def thanClone(self):
#        "Makes a geometric clone of itself."
#        el = self.__class__()
#        el.thanSet(self.cp)
#        return el


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.thanRotateXyn(self.cp)
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        self.thanMirrorXyn(self.cp)
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])


    def thanScale(self, cs, scale):
        "Scales the ele`ment in n-space with defined scale and center of scale."
        for cc in self.cp:
            cc[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in izip(cc, cs)]
        cscs = [cs[0], cs[1], cs[0], cs[1]]
        self.thanXymm[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in izip(self.thanXymm, cscs)]


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        for cc in self.cp:
            cc[:] = [cc1+dd1 for (cc1,dd1) in izip(cc, dc)]
        dcdc = [dc[0], dc[1], dc[0], dc[1]]
        self.thanXymm[:] = [cc1+dd1 for (cc1,dd1) in izip(self.thanXymm, dcdc)]


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type otype nearest to ccu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        if "end" in otypes:       # type "end" without type "int"
            for c in self.cp:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "end", c))
        if "mid" in otypes:
            for ca, cb in iterby2(self.cp):
                c = [(ca1+cb1)*0.5 for (ca1,cb1) in izip(ca, cb)]
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "mid", c))
        if "nea" in otypes:
            c = self.thanPntNearest(ccu)
            if c != None:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "nea", c))
        if cori != None and "per" in otypes:
            for c in self.thanPerpPoints(cori):
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "per", c))
        if eother != None and "int" in otypes:
            ps.extend(thanintall.thanIntsnap(self, eother, ccu, proj))
        if len(ps) < 1: return None
        return min(ps)


    def thanPntNearest(self, ccu):
        "Finds the nearest point of this line to a point."
        return thanPntNearest2(self.cp, ccu)[0]
    def thanPntNearest2(self, ccu):
        "Finds the nearest point of this line to a point."
        return thanPntNearest2(self.cp, ccu)
    def thanPerpPoints(self, ccu):
        "Finds perpendicular point from ccu to polyline."
        return thanPerpPoints(self.cp, ccu)
    def thanSegNearest(self, ccu):
        """Finds the nearest segment of this line to a point."""
        return thanSegNearest(self.cp, ccu)


    def thanTrim(self, ct, cnear):
        "Breaks the line into multiple segments and deletes the segment nearest to cnear."
        cp = []
        for c in ct:
            cn, i, t = self.thanPntNearest2(c)
            cp.append((t, i, c))
            assert cn != None, "It should have been checked (that ct are indeed near line)!"
        cp.sort()
        cn, i, t = self.thanPntNearest2(cnear)
        cpnear = t, i, cn
        assert cpnear[2] != None, "It should have been checked (that cnear are indeed near line)!"
        i = bisect.bisect_right(cp, cpnear)
        if i == 0:
            return self.thanBreak(self.cp[0], cp[0][2])  # User selected the segment before the first intesection (ct)
        elif i == len(cp):
            return self.thanBreak(cp[-1][2], self.cp[-1])# User selected the segment after the last intesection (ct)
        else:
            return self.thanBreak(cp[i-1][2], cp[i][2])  # User selected the segment between i-1 and i intesections (ct)


    def thanBreak(self, c1=None, c2=None):
        "Breaks a line to 2 pieces; c1 and c2 may be identical."
        if c1 == None: return True                 # Report that break IS implemented
        cp1, i1, tcp1 = self.thanPntNearest2(c1)
        cp2, i2, tcp2 = self.thanPntNearest2(c2)
        if tcp2 < tcp1:
            cp1, i1, cp2, i2 = cp2, i2, cp1, i1
        assert cp1 != None and cp2 != None, "It should have been checked (that c1 and c2 are indeed near line)!"
        print "break: cp1=", cp1, "i1=", i1, "tcp1=", tcp1
        print "break: cp2=", cp2, "i2=", i2, "tcp2=", tcp2
        cs1 = self.cp[:i1]
        if len(cs1) > 0:
            cs1.append(cp1)
            e1 = ThanLine()
            e1.thanSet(cs1)
            if not e1.thanIsNormal(): e1 = None    # A tiny segment was left
        else:
            e1 = None
        cs1 = self.cp[i2:]
        if len(cs1) > 0:
            cs1.insert(0, cp2)
            e2 = ThanLine()
            e2.thanSet(cs1)
            if not e2.thanIsNormal(): e2 = None    # A tiny segment was left
        else:
            e2 = None
        return e1, e2                              # If both are None, then "break" left nothing


    def thanStraighten(self, c1=None, c2=None):
        "Straighten the line between c1 and c2; c1 and c2 may not be identical."
        if c1 == None: return True                 # Report that break IS implemented
        cp1, i1, tcp1 = self.thanPntNearest2(c1)
        cp2, i2, tcp2 = self.thanPntNearest2(c2)
        if tcp2 < tcp1:
            cp1, i1, cp2, i2 = cp2, i2, cp1, i1
        assert cp1 != None and cp2 != None, "It should have been checked (that c1 and c2 are indeed near line)!"
        assert cp1 != cp2, "It should have been checked (that c1 and c2 are not identical)!"
        print "straighten: cp1=", cp1, "i1=", i1, "tcp1=", tcp1
        print "straighten: cp2=", cp2, "i2=", i2, "tcp2=", tcp2
        assert i1>0 and i2>0, "impossible error: thanNearest2 returns i>0, or cp1==None"
        cs1 = self.cp[:i1]
        cs1.append(cp1)
        cs1.append(cp2)
        cs1.extend(self.cp[i2:])
        e = ThanLine()         #A new line is created to aid undo/redo mechanism
        e.thanSet(cs1)         #This also clears zero length segments
        return e


    def thanExplode(self, than=None):
        "Transform the line to a set of smaller 2-point lines."
        if than == None: return True               # Break IS implemented
        return self.__explode()
    def __explode(self):
        "Transform the line to a set of smaller 2-point lines; do the job as a generator."
        for i in xrange(1, len(self.cp)):
            e1 = ThanLine()
            e1.thanSet(self.cp[i-1:i+1])
            if e1.thanIsNormal(): yield e1


    def thanOffset(self, through=None, distance=None, sidepoint=None):
        "Offset line by distance disstance; to the right if distance>0 and to the left otherwise."
        if through==None and distance==None: return True  # Offset is implemented
        distance = self._offsetVecdistance(through, distance, sidepoint)
        try: cs = self.cpori     #For ThanSpline
        except: cs = self.cp
        cs = thanOffsetLine(cs, distance)
        e = self.thanClone()             #To allow subclasses to use thanOffset too
        e.thanUntag()                    #Invalidate thanTags and handle
        e.thanSet(cs)                    #thanSet has the same signature for all subclasses
        if e.thanIsNormal(): return e
        return None                      # Element can not be offset (degenerate)


    def _offsetVecdistance(self, through=None, distance=None, sidepoint=None):
        "Find vector diasatnce of offset line; offset to the right if distance>0 and to the left otherwise."
        if through==None and distance==None: return True  # Offset is implemented
        cp1, iseg, tcp1 = self.thanPntNearest2(sidepoint)
        if cp1 == None: return None      # Invalid point
        t = Vector2(*self.cp[iseg][:2])-Vector2(*self.cp[iseg-1][:2])
        n = t.normal()
        t = Vector2(*sidepoint[:2])-Vector2(*cp1[:2])
        if through:
            distance = t*n
        else:
            distance = fsign(distance, t*n)
        return distance


    def getInspnt(self):
        "Returns the insertion point of the line."
        return list(self.cp[0])


    def thanChelev(self, z):
        "Set constant elevation of z."
        for cc in self.cp:
            cc[2] = z

    def thanChelevn(self, celev):
        "Set constant elevation of z and higher dimensions."
        for cc in self.cp:
            cc[2:] = celev

    def thanLength(self):
        "Returns the length of the polyline."
        al = 0.0
        for ca, cb in iterby2(self.cp):
            al += hypot(cb[0]-ca[0], cb[1]-ca[1])
        return al

    def thanArea(self):
        "Returns the area of the polyline."
        return p_ggeom.area(self.cp)

    def thanSpin(self):
        "Returns the spin of the line, imagining that it is closed."
        a = p_ggeom.areapn(self.cp)
        if a > 0.0: return -1                #Nodes are clockwise
        if a < 0.0: return  1                #Nodes are Counter-Clockwise
        return 0

#===========================================================================

    def thanTkGet(self, proj):
        "Gets the attributes of the line interactively from a window."
        cp = []
	while True:
	    c1 = proj[2].thanGudGetPoint(T["First line point (c=continue previous): "],
	        options=("continue",))
            if c1 == Canc: return Canc                              # Line cancelled
   	    if c1 == "c":
	        proj[2].thanGudCommandBegin("continueline")
	        return Canc
	    break
        cp.append(c1)
	res = self.__tkGetn(proj, cp)
	if res == Canc: return Canc


    def thanTkContinue(self, proj):
        "Gets the attributes of the line interactively from a window."
        dc = proj[2].than.dc
	dc.delete(self.thanTags[0])
	g2l = proj[2].than.ct.global2Local
	cl = proj[2].than.dc.create_line
	fi = proj[2].than.outline
	cp = list(self.cp)
        x1, y1 = g2l(cp[0][0], cp[0][1])
	for i in xrange(1, len(cp)):
            tags = "e0", "e"+str(i+1)
            x2, y2 = g2l(cp[i][0], cp[i][1])
            temp = cl(x1, y1, x2, y2, fill=fi, tags=tags)
	    x1 = x2; y1 = y2
        res = self.__tkGetn(proj, cp)
	if res == Canc: return Canc
	self.thanTkDraw(proj[2].than)
	return res


    def __tkGetn(self, proj, cp):
        "Gets the following points of the line interactively from a window."
        cla = proj[1].thanLayerTree.thanCur
	g2l = proj[2].than.ct.global2Local
	cl = proj[2].than.dc.create_line
	delete = proj[2].than.dc.delete
	fi = proj[2].than.outline
	wpix = proj[2].than.tkThick
	c1 = cp[-1]
        while True:
            res = self.__getPointLin(proj[2], c1, len(cp))
            if res == Canc and len(cp) < 2: return Canc          # Line cancelled
            if res == Canc or res == "" or res == "c": break     # Line ended (we know that line has more than 1 point)
	    if res == "u":
		delete("e"+str(len(cp)))
	        c1 = cp[-2]
		del cp[-1]
            else:
                c1 = res
                cp.append(c1)
	        tags = "e0", cla.thanTag, "e"+str(len(cp))
                temp = cl((g2l(cp[-2][0], cp[-2][1]), g2l(c1[0], c1[1])), fill=fi, width=wpix, tags=tags)
#               print "line:thantkget:fi=", fi
	if res == "c":
	    cp.append(list(cp[0]))
#           Note that if we did: cp.append(cp[0])
#           then if we changed the coordinates of cp[0], the coordinates of cp[-1]
#           would also change. This means that the line would always be closed.
#           Also, thanClone should check for this, since the cloned line would have
#           independent coordinates in cp[0] and cp[1]. Also, all the modifications
#           (move, rotate etc.) should be careful not to apply the modification
#           to both cp[0] and cp[-1], as it would make the modification twice.

        delete("e0")
        self.thanSet(cp)
        return True        # Line OK (note that it will have at least 2 points)

    def __getPointLin(win, c1, np):
        "Gets a point from the user, with possible options."
	if np == 1:
	    stat1 = T["Next line point: "]
	    return win.thanGudGetLine(c1, stat1)
	elif np == 2:
	    stat1 = T["Next line point (undo/<enter>): "]
	    return win.thanGudGetLine(c1, stat1, options=("", "undo"))
	else:
	    stat1 = T["Next line point (undo/close/<enter>): "]
	    return win.thanGudGetLine(c1, stat1, options=("", "undo", "close"))
    __getPointLin = staticmethod(__getPointLin)

#===========================================================================

    def thanTkDraw1(self, than):
        "Draws the line to a Tk Canvas."
        g2l = than.ct.global2Local
        w = than.tkThick
        xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
        if thanNear2(self.cp[0], self.cp[-1]):   # Even if fill="", which means no fill
#            temp = than.dc.create_polygon(xy1, outline=than.outline, fill=than.fill, tags=self.thanTags, width=w)
#            temp = than.dc.create_line(   xy1,                       fill=than.outline, dash=(15,5,5,5), tags=self.thanTags, width=w)
            temp = than.dc.create_line(   xy1,                       fill=than.outline, tags=self.thanTags, width=w)
        else:
#            temp = than.dc.create_line(   xy1,                       fill=than.outline, dash=(15,5,5,5), tags=self.thanTags, width=w)
            temp = than.dc.create_line(   xy1,                       fill=than.outline, tags=self.thanTags, width=w)


    def thanExpDxf(self, fDxf):
        "Exports the line to dxf file."
        #FIXME: report width of polyline
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        zp = [c1[2] for c1 in self.cp]
        fDxf.thanDxfPlotPolyline3(xp, yp, zp)


    def thanExpThc1(self, fw):
        "Save the line in thc format."
        fw.writeNodes(self.cp)


    def thanImpThc1(self, fr):
        "Read the line from thc format."
        cp = fr.readNodes()
        self.thanSet(cp)


    def thanExpSyk(self, than):
        "Exports the line to syk file."
        than.write("%15.3f  %s\n" % (self.cp[0][2], than.layname))
        for cp1 in self.cp:
            than.write("%15.3f%15.3f\n" % (cp1[0], cp1[1]))
        than.write("$\n")


    def thanExpBrk(self, than):
        "Exports the line to brk file."
        for cp1 in self.cp:
            than.ibr += 1
            than.write(than.form % (than.ibr, cp1[0], cp1[1], cp1[2]))
        than.write("$\n")


    def thanExpPilchaos(self, than):
        """Exports the line to a PIL raster image.

        There seems to be a bug in the PIL which chaotically affects the width
        of the line. Thus, this code is not used. But it should be checked
        with future versions of PIL.
        """
        g2l = than.ct.global2Local
        xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
        if thanNear2(self.cp[0], self.cp[-1]) and not than.fill:
            than.dc.polygon(xy1, outline=than.outline, fill=than.fill) # width=than.width)
        else:
            than.dc.line(xy1, fill=than.outline, width=than.width)


    def thanExpPil(self, than):
        "Exports the line to a PIL raster image; workaround PIL bug." #2008_10_07:no longer valid."
        w = than.rwidth
        if w <= 1.5:
	    g2l = than.ct.global2Locali
            xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
	    than.dc.line(xy1, fill=than.outline)
	    return
        w2, _ = than.ct.local2GlobalRel(w*0.5, w)
        for i in xrange(1, len(self.cp)):
	    x1, y1 = self.cp[i-1][0], self.cp[i-1][1]
	    x2, y2 = self.cp[i][0], self.cp[i][1]
	    dx, dy = x2-x1, y2-y1
	    r = hypot(dx, dy)
	    if r <= 0.0: continue
            tx, ty = dx/r, dy/r
   	    nx, ny = -ty*w2, tx*w2
	    cr = (x1-nx,y1-ny), (x2-nx,y2-ny), (x2+nx,y2+ny), (x1+nx,y1+ny)
            xy1 = [than.ct.global2Locali(x1, y1) for x1,y1 in cr]
	    than.dc.polygon(xy1, outline=than.outline, fill=than.outline)


    def thanPlotPdf(self, than):
        "Plots the line to a pdf file."
	#FIXME: report width of polyline
	if len(self.cp) < 2: return
	g2l = than.ct.global2Local
	if len(self.cp) == 2:
	    ca = g2l(self.cp[0][0], self.cp[0][1])
	    cb = g2l(self.cp[1][0], self.cp[1][1])
	    p = pyx.path.line(ca[0], ca[1], cb[0], cb[1])
	else:
	    lineto = pyx.path.lineto
	    moveto = pyx.path.moveto
            xy1 = [lineto(*g2l(c1[0], c1[1])) for c1 in islice(self.cp, 1, None)]
	    xy1.insert(0, moveto(*g2l(self.cp[0][0], self.cp[0][1])))
	    if thanNear2(self.cp[0], self.cp[-1]): xy1[-1] = pyx.path.closepath()
	    p = pyx.path.path(*xy1)
	than.dc.stroke(p)


    def thanList(self, than):
        "Shows information about the line element."
        than.writecom("%s: %s" % (T["Element"], "LINE"))
        if thanNear2(self.cp[0], self.cp[-1]): oc = T["(closed)"]
        else:                                  oc = T["(open)"]
        than.write(" %s    %s %s\n" % (oc, T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        than.write("%s%s\n" % (T["Spin: "], self.thanSpin()))
        than.write("%s (%d):\n" % (T["Vertices"], len(self.cp)))
        for i,c1 in enumerate(self.cp):
            than.write("    %s\n" % than.strcoo(c1))
            if i % 20 == 19:
                c = than.read(T["Press enter to continue.."])
                if c == Canc: break


#    def __del__(self):
#        print "ThanLine", self, "is deleted"


##############################################################################
##############################################################################

class ThanLineFilled(ThanLine):
    "A closed polyline which is filled with colour."
    thanElementName = "FILLEDLINE"    # Name of the element's class

    def thanSet (self, cp, persistentfilled=False):
        "If persistentfilled is true then the line is filled even if the layer attribut fill is off."
        ThanLine.thanSet(self, cp)
        self.persistentfilled = persistentfilled
        if thanNear2(self.cp[0], self.cp[-1]):
            self.cp[-1][:2] = self.cp[0][:2]
        else:
            self.cp.append(self.cp[0][:])


    def thanTkDraw1(self, than):
        "Draws the filled line to a Tk Canvas."
        g2l = than.ct.global2Local
        w = than.tkThick
        xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
        if than.fill or self.persistentfilled: fill = than.outline
        else:                                  fill = None
        temp = than.dc.create_polygon(xy1, outline=than.outline, fill=fill, tags=self.thanTags, width=w)


    def thanExpPil(self, than):
        """Exports the filled line to a PIL raster image."""
        g2l = than.ct.global2Local
        xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
        if than.fill or self.persistentfilled: fill = than.outline
        else:                                  fill = None
        than.dc.polygon(xy1, outline=than.outline, fill=fill) # width=than.width)


    def thanExpDxf(self, fDxf):
        "Exports the filled line to dxf file; if it has 3 or 4 points then as a solid."
        if than.fill or self.persistentfilled:
            if len(self.cp) == 4:
                c1, c2, c3 = self.cp[:3]
                fDxf.thanDxfPlotSolid3(c1[0], c1[1], c2[0], c2[1], c3[0], c3[1])
                return
            elif len(self.cp) == 5:
                c1, c2, c3, c4 = self.cp[:4]
                fDxf.thanDxfPlotSolid4(c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], c4[0], c4[1])
                return
        ThanLine.thanExpDxf(self, fDxf)


    def thanList(self, than):
        "Shows information about the filled line element."
        if self.persistentfilled: ff = T["Fill: permanent"]
        else:                     ff = T["Fill: depends on layer"]
        than.writecom("%s: %s" % (T["Element"], "LINE FILLED (SOLID)"))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        than.write("%s%s\n" % (T["Spin: "], self.thanSpin()))
        than.write("%s\n" % (ff,))
        than.write("%s (%d):\n" % (T["Vertices"], len(self.cp)))
        for i,c1 in enumerate(self.cp):
            than.write("    %s\n" % than.strcoo(c1))
            if i % 20 == 19:
                c = than.read(T["Press enter to continue.."])
                if c == Canc: break


##############################################################################
##############################################################################

class ThanCurve(ThanLine):
    """A curve which is simulated by a large number of cosecutive linear segments.

    Basically an ordinary polyline, with the difference that osnap does not snap
    to the end points and midpoints of the linear segments.
    For the tangent osnap to work, it is supposed that the curve is continuous (it has
    to be, noncontinuous can not be represented by a ThanLine) and that the line segments
    which simulate the curve are dense enough to show the smooth character of the curve,
    (where the curve is indeed smooth). If the curve has some real corners, these are taken
    into account by the threshold of the difference between tagents.
    """
    thanElementName = "CURVE"    # Name of the element's class

    def thanSetToldeg(self, tol=2.0):
        "Set the toplerances of smoothness for radius and tangents to work (in decimanl degrees."
        self.thtol = tol*pi/180


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type otype nearest to xcu, ycu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        if "end" in otypes:       # type "end" without type "int"
            for c in self.cp[0], self.cp[-1]:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "end", c))
        if "mid" in otypes:
            c = self.thanMidPoint()
            ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "mid", c))
        if "tan" in otypes:
            if cori != None:
                for c in self.thanTanPoints(cori):
                    ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "tan", c))
        if "cen" in otypes:
            c, r, ctang = self.thanCenterPoint(ccu)
            print c, r
            if c != None:
                ps.append((fabs(ctang[0]-ccu[0])+fabs(ctang[1]-ccu[1]), "cen", c))
        if "nea" in otypes:
            c = self.thanPntNearest(ccu)
            if c != None:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "nea", c))
        if cori != None and "per" in otypes:
            for c in self.thanPerpPoints(cori):
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "per", c))
        if eother != None and "int" in otypes:
            ps.extend(thanintall.thanIntsnap(self, eother, ccu, proj))
        if len(ps) < 1: return None
        return min(ps)


    def thanMidPoint(self):
        "Finds the midpoint of the curve."
        alm = self.thanLength()*0.5
        ala = 0.0
        for ca, cb in iterby2(self.cp):
            alb = ala + hypot(cb[0]-ca[0], cb[1]-ca[1])
            if alb >= alm: break
            ala = alb
        else:
            assert False, "What? Half length is bigger than length?!"
        if thanNearx(ala, alb):       # In case of zero length segment
            c = [(za+zb)*0.5 for (za, zb) in zip(ca, cb)]
        else:
            c = [za+(zb-za)/(alb-ala)*(alm-ala) for (za, zb) in zip(ca, cb)]
        return c


    def thanTanPoints(self, cori):
        """Finds the tangent to the curve from cori to the curve.

        If more than 1 tangents are found, all are returned.
        """
        tantol = 0.5*pi/180               # Tolerance for difference in tangent is 0.5 degrees
        ps = []
        for ca, cb in iterby2(self.cp):
            thcurv = atan2(cb[1]-ca[1], cb[0]-ca[0])
            thtan  = atan2(ca[1]-cori[1], ca[0]-cori[0])
            dth = dpt(thcurv-thtan)
            if dth < tantol or PI2-dth < tantol or fabs(dth-pi) < tantol: ps.append(ca)
        return ps


    def thanCenterPoint(self, ccu):
        "Finds the center and the radius of the circle which is tangent to point nearest to ccu."
        cp1, i, tcp1 = self.thanPntNearest2(ccu)
        if cp1 == None: return None, None, None
        if i+1 >= len(self.cp): return None, None, None
        ca, cb, cc = self.cp[i-1:i+2]
        a = hypot(cb[0]-ca[0], cb[1]-ca[1])
        th1 = atan2(cb[1]-ca[1], cb[0]-ca[0])
        th2 = atan2(cc[1]-cb[1], cc[0]-cb[0])
        dth = dpt(th2-th1)
        if dth > pi: dth = fabs(dth-PI2)
        if dth > self.thtol: return None, None, None                # not smooth; it is a corner
        if thanNearx(dth, 0.0): return None, None, None        # Straight line, radius is infinite
        r = a / dth
        va = Vector2(ca[0], ca[1])
        vb = Vector2(cb[0], cb[1])
        vc = Vector2(cc[0], cc[1])
        t1 = (va-vb).unit()
        t2 = (vc-vb).unit()
        t = (t1+t2).unit()
        vcen = vb + r*t
        ccen = list(cb)
        ccen[:2] = vcen.x, vcen.y
        return ccen, r, cb


    def thanPerpPoints(self, ccu):
        "Finds perpendicular point from ccu to a curve represented by small line segments."
        return thanPerpPointsC(self.cp, ccu, self.thtol)


    def thanList(self, than):
        "Shows information about the curve element."
        than.writecom("%s: %s" % (T["Element"], "CURVE"))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        than.write("%s%s\n" % (T["Spin: "], self.thanSpin()))


##############################################################################
##############################################################################

from p_gmath import ThanSpline as ThanSplineC
from p_ggen import xfrangec

class ThanSpline(ThanCurve):
    """A cubic spline curve."""
    thanElementName = "SPLINE"    # Name of the element's class

    def thanSet (self, cp):
        """Sets the attributes of the cubic spile.

        The original nodes are saves and the interpolated point are passed to the
        ThanLine object.
        """
        self.cpori = thanCleanLine3(cp)
        n = len(self.cpori)
        if n > 1:
            d = sum(hypot(hypot(cb[0]-ca[0], cb[1]-ca[1]), cb[2]-ca[2]) for ca, cb in iterby2(self.cpori))/(n-1)
            cp = self.__calcC(d/5.0)  # temporarily until thanTkDraw is called
        ThanCurve.thanSet(self, cp)
        self.thanSetToldeg(20)        # Set angle tolerance for smoothness

    def thanChelev(self, z):
        "Set constant elevation of z."
        for cc in self.cp:
            cc[2] = z
        for cc in self.cpori:
            cc[2] = z

    def thanChelevn(self, celev):
        "Set constant elevation of z and higher dimensions."
        for cc in self.cp:
            cc[2:] = celev
        for cc in self.cpori:
            cc[2:] = celev

    def thanReverse(self):
        "Reverse the sequence of the nodes."
        self.cp.reverse()
        self.cpori.reverse()


    def thanTkGet(self, proj):
        "Gets the attributes of the cubic spline interactively from a window."
        g2l = proj[2].than.ct.global2Local
        g2lr= proj[2].than.ct.global2LocalRel
        l2g = proj[2].than.ct.local2Global
        dc = proj[2].than.dc
        fi = proj[2].than.outline

        cpr = []
        c1 = proj[2].thanGudGetPoint(T["First spline point:"])
        if c1 == Canc: return Canc                                  # Spline was cancelled
        cpr.append(c1)

        while True:
            c1 = proj[2].thanGudGetLine(cpr[-1], T["Second spline point: "])
            if c1 == Canc: return Canc                              # Road was cancelled
            cpr.append(c1)
            while True:
                c1, cargo = self.__getPointLin(proj[2], cpr[-2], cpr[-1], len(cpr))
                if c1 == Canc and len(cpr) < 3: return Canc         # Road was cancelled
                if c1 == Canc or c1 == "" or c1 == "c": break       # Road was ended
                if c1 == "u":                                       # Undo last point
                    if len(cpr) < 3: break
                    dc.delete("e"+str(len(cpr)))
                    del cpr[-1]
                else:                                               # Plot the new point
                    cpr.append(c1)
                    ns = len(cpr)
                    xs = [0.0]*ns; ys = [0.0]*ns
                    for i in xrange(ns): xs[i], ys[i] = g2l(cpr[i][0], cpr[i][1])
                    sp = ThanSplineC(0, xs, ys)
                    tmax = sum(sp.t)
                    xs = []
                    for t in xfrangec(0.0, tmax, 4.0):
                        xp1, yp1 = sp.splfun(t)
                        xs.append((xp1, yp1))
                    dc.delete("e0")
                    dc.create_line(xs, fill=fi, tags="e0")
            if c1 == "u":
                del cpr[-1]
            else:
                break
        if c1 == "c":
            proj[2].thanCom.thanAppend("Spline close has not yet been implemented :)\n")

        dc.delete("e0")
        self.thanSet(cpr)
        return True                              # Spline OK


    def __getPointLin(self, win, c1, c2, np):
        "Gets a point from the user, with possible options."
        if np == 3:
            stat1 = T["Next spline node (undo/<enter>): "]
            return win.thanGudGetSplineP(c1, c2, stat1, options=("undo", ""))
        else:
            stat1 = T["Next spline node (undo/close/<enter>): "]
            return win.thanGudGetSplineP(c1, c2, stat1, options=("undo", "close", ""))


    def thanTkDraw1(self, than):
        "Draws the spline to a Tk Canvas."
        dx, dy = than.ct.global2LocalRel(1.0, 1.0)
        dt = hypot(1.0, 1.0)/hypot(dx, dy)*10.0
        self.cp = self.__calcC(dt)
        ThanCurve.thanTkDraw1(self, than)


    def thanExpThc1(self, fw):
        """Save the spline in thc format.

        It differs from ThanLine beacause it saves cpori and not cp.
        On the other hand thanImpThc1 is the same as that of ThanLine."""
        fw.writeNodes(self.cpori)


    def __calcC(self, dt):
        "Calculates interpolation points on the cubic spline curve."
        ic = 0
        if thanNear3(self.cpori[0], self.cpori[-1]): ic = 1     # closed
        xs = [c[0] for c in self.cpori]
        ys = [c[1] for c in self.cpori]
        zs = [c[2] for c in self.cpori]
        try: s = ThanSplineC(ic, xs, ys, zs)
        except ZeroDivisionError: return self.cpori
        tmax = s.tmax
        del xs, ys
        cs = []
        for ts in xfrangec(0.0, tmax, dt):
            x, y, z = s.splfun(ts)
            cs.append((x, y, z))
        return cs


##############################################################################
##############################################################################

def thanPntNearest(cp, ccu):
        "Finds the nearest point of this line to a point."
        return thanPntNearest2(cp, ccu)[0]


def thanPntNearest2(cp, ccu):
        "Finds the nearest point of this line to a point."
	dmin=1e100; cp1 = None; iseg = -1; tcp1 = -1.0
	tall = 0.0
	for i in xrange(1, len(cp)):
	    a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
	    aa = hypot(*a)
	    tall += aa
	    if thanNearx(aa, 0.0): continue      # Segment has zero length
	    ta = a[0]/aa, a[1]/aa
	    b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
	    dt = ta[0]*b[0]+ta[1]*b[1]
	    if   thanNearx(dt, 0.0) : dt = 0.0
	    elif thanNearx(dt, aa)  : dt = aa
	    elif dt < 0.0 or dt > aa: continue
	    dn = fabs(-ta[1]*b[0]+ta[0]*b[1])
	    if dn < dmin:
	        cp1 = [e+(f-e)*dt/aa for (e,f) in izip(cp[i-1], cp[i])]
		dmin = dn
		iseg = i
		tcp1 = tall - aa + dt
	return cp1, iseg, tcp1


def thanSegNearest(cp, ccu):
        """Finds the nearest segment of this line to a point.

	It is an optimisation of thanPntNearest2(), if the nearest point is
	not needed.
	This function is used in thanintall in order to find the intersection
	of a line and another ThanCad element, when object snap intersection
	is enabled. We take advantage of the fact that the mouse coordinates
	ccu are already very near the line (and the other element). Thus, we
	don't check if the projection of the ccu to the line segment is indeed
	between the end of the line segment. However thanintall will ensure
	that the intersection point will belong to both elements.
	"""
        dmax=1e100
        for i in xrange(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
	    aa = hypot(*a)
	    if aa == 0.0: continue              # Segment has zero length
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dn = fabs(a[0]*b[1]-a[1]*b[0]) / aa
	    if dn < dmax: imax=i; dmax=dn
	return cp[imax-1], cp[imax]


def thanPerpPoints(cp, ccu):
        "Finds perpendicular point from ccu to polyline."
        ps = []
        tall = 0.0
        for i in xrange(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
            aa = hypot(*a)
            tall += aa
            if thanNearx(aa, 0.0): continue      # Segment has zero length
            ta = a[0]/aa, a[1]/aa
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dt = ta[0]*b[0]+ta[1]*b[1]
            if   thanNearx(dt, 0.0) : dt = 0.0
            elif thanNearx(dt, aa)  : dt = aa
            elif dt < 0.0 or dt > aa: continue
            dn = fabs(-ta[1]*b[0]+ta[0]*b[1])
            cp1 = [e+(f-e)*dt/aa for (e,f) in izip(cp[i-1], cp[i])]
            ps.append(cp1)
        return ps


def thanPerpPointsC(cp, ccu, thtol):
        "Finds perpendicular point from ccu to a surve represented by small lines."
        ps = []
        tall = 0.0
        dtp = None
        for i in xrange(1, len(cp)):
            a = cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1]
            aa = hypot(*a)
            tall += aa
            if thanNearx(aa, 0.0): dtp=None; continue    # Segment has zero length; this shouldn't happen, so I don't bother if I lose a point
            ta = a[0]/aa, a[1]/aa
            b = ccu[0]-cp[i-1][0], ccu[1]-cp[i-1][1]
            dt = ta[0]*b[0]+ta[1]*b[1]
            if   thanNearx(dt, 0.0): dt = 0.0
            elif thanNearx(dt, aa) : dt = aa
            if dt < 0.0 or dt > aa:
                if dtp != None and dt*dtp < 0.0:
                    th1 = atan2(cp[i-1][0]-cp[i-2][0], cp[i-1][1]-cp[i-2][1])
                    th2 = atan2(cp[i][0]-cp[i-1][0], cp[i][1]-cp[i-1][1])
                    dth = dpt(th2-th1)
                    if dth > pi: dth = fabs(dth-PI2)
                    if dth <= thtol:             # It is smooth enough (it is not a corner)
                        ps.append(list(cp[i-1]))
            else:
                dn = fabs(-ta[1]*b[0]+ta[0]*b[1])
                cp1 = [e+(f-e)*dt/aa for (e,f) in izip(cp[i-1], cp[i])]
                ps.append(cp1)
            dtp = dt
        return ps


if __name__ == "__main__":
    print __doc__
