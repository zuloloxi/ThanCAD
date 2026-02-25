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

This module defines the hatch element.
"""

from math import fabs, hypot, pi
try: import pyx
except ImportError: pass
import p_ggeom, p_gindplt
from p_ggen import iterby2
from p_gmath import dpt, thanNear2
from thanvar import Canc, thanCleanLine2, thanPilLine, ThanDelay
from thantrans import T
from . import thanintall
from .thanelem import ThanElement
from .thanline import ThanLine
from .thanutil import thanPntNearest2, thanSegNearest, thanPerpPoints


class ThanHatch(ThanElement):
    "A hatch enclosed by a closed polygon."
    thanTkCompound = 100       # The number of tkinter objects that make the element. 100=compound (lines etc.)
    thanElementName = "HATCH"    # Name of the element's class

    def thanSet (self, cp, itype, dise, thetae):
        "Sets the attributes of the hatch."
        self.cp = thanCleanLine2(cp)
        if not thanNear2(self.cp[0], self.cp[-1]):
            self.cp.append(list(self.cp[0]))  #Make the polygon closed
        if len(self.cp) > 0:
            xp = [c1[0] for c1 in self.cp]
            yp = [c1[1] for c1 in self.cp]
            self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])
        self.itype = itype
        self.dise = dise
        if self.dise <= 0.0: self.dise = 0.5
        self.thetae = dpt(thetae)
#        self.thanTags = ()            # thanTags is initialised in ThanElement


    def thanReverse(self):
        "Reverse the sequence of the nodes."
        self.cp.reverse()


    def thanIsNormal(self):
        "Returns False if the line is degenerate (it has only one point)."
#       if len(cp) == 2 and it is closed then it is degenerate and this function returns false
#       if len(cp) == 3 and it is closed then it is degenerate polygon but
#       a good line, so this function returns True
        if len(self.cp) < 4: return False   # Return False if enclosed polygon is degenerate
        #if self.dise <= 0: return False  #Warning: in thanSet(), self.dise is set to a positive
        it = iter(self.cp)
        c1 = next(it)
        for c2 in it:
            if not thanNear2(c1, c2): return True
        return False      # All line points are close together


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        self.thanRotateXyn(self.cp)
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.thetae = dpt(self.thetae+self.rotPhi)
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        self.thanMirrorXyn(self.cp)
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])


    def thanPointMir(self):
        "Mirrors the element within XY-plane with respect to predefined point."
        self.thanPointMirXyn(self.cp)
        xp = [c1[0] for c1 in self.cp]
        yp = [c1[1] for c1 in self.cp]
        self.setBoundBox([min(xp), min(yp), max(xp), max(yp)])


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        for cc in self.cp:
            cc[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(cc, cs)]  #works for python2,3
        cscs = [cs[0], cs[1], cs[0], cs[1]]
        self.thanXymm[:] = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.thanXymm, cscs)]  #works for python2,3


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        for cc in self.cp:
            cc[:] = [cc1+dd1 for (cc1,dd1) in zip(cc, dc)]  #works for python2,3
        dcdc = [dc[0], dc[1], dc[0], dc[1]]
        self.thanXymm[:] = [cc1+dd1 for (cc1,dd1) in zip(self.thanXymm, dcdc)]  #works for python2,3


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


    def thanExplode(self, than=None):
        "Transform the line to a set of smaller 2-point lines."
        if than is None: return True               # Explode IS implemented
        return self.__explode(than)
    def __explode(self, than):
        "Transform the hatch to lines; do the job as a generator."
        if not than.fillModeOn:   #In this case we draw only the outline
            for cha in iterby2(self.cp):
                e1.thanSet(cha)
                if e1.thanIsNormal(): yield e1
        else:
            chi = tuple(self.cp[0][2:])
            hp = p_gindplt.HatchPolygon(self.cp)
            for cha in hp.hatchlines(self.dise, self.thetae):
                e1 = ThanLine()
                cha = [tuple(c)+chi for c in cha]
                e1.thanSet(cha)
                if e1.thanIsNormal(): yield e1


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
        return p_ggeom.spin(self.cp)

    def thanTkDraw1(self, than):
        "Draws the hatch lines to a Tk Canvas."
        g2l = than.ct.global2Local
        if not than.fillModeOn:   #In this case we draw only the outline
            xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp]
            temp = than.dc.create_line(xy1, fill=than.outline, dash=than.dash, tags=self.thanTags)
        elif self.itype == 0:   #Solid
            xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp[:-1]]
            temp = than.dc.create_polygon(xy1, outline=than.outline, fill=than.outline, tags=self.thanTags)
        else:
            w = than.tkThick
            hp = p_gindplt.HatchPolygon(self.cp)
            for cha in hp.hatchlines(self.dise, self.thetae):
                xy1 = [g2l(c1[0], c1[1]) for c1 in cha]
                temp = than.dc.create_line(xy1, fill=than.outline, dash=than.dash, tags=self.thanTags, width=w)


    def thanExpDxf(self, fDxf):
        "Exports the line to dxf file."
        if not fDxf.than.fillModeOn:   #In this case we draw only the outline
            xp = [c1[0] for c1 in self.cp]
            yp = [c1[1] for c1 in self.cp]
            zp = [c1[2] for c1 in self.cp]
            fDxf.thanDxfPlotPolyline3(xp, yp, zp)
        elif self.itype == 0:   #Solid
            #FIXME: perhaps modify p_gdxf.solid to accept z coordinate
            hp = p_gindplt.HatchPolygon(self.cp)
            for a, b, c in hp.hatchsolids():
                fDxf.thanDxfPlotSolid3(a[0], a[1], b[0], b[1], c[0], c[1])
        else:
            #FIXME: report width of polyline
            hp = p_gindplt.HatchPolygon(self.cp)
            for cha in hp.hatchlines(self.dise, self.thetae):
                xp = [c1[0] for c1 in cha]
                yp = [c1[1] for c1 in cha]
                zp = [self.cp[0][0] for c1 in cha]
                fDxf.thanDxfPlotPolyline3(xp, yp, zp)


    def thanExpThc1(self, fw):
        "Save the hatch in thcx format."
        f = fw.formFloat
        fw.writeAtt("type", str(self.itype))
        fw.writeln((f+f) % (self.dise, self.thetae))
        fw.writeNodes(self.cp)


    def thanImpThc1(self, fr, ver):
        "Read the line from thcx format."
        temp = fr.readAtt("type")  #May raise ValueError, IndexError, StopIteration
        (itype,) = map(int, temp)     #May raise ValueError, IndexError, StopIteration
        dise, thetae = map(float, next(fr).split()) #May raise ValueError, IndexError, StopIteration   #works for python2,3
        #If dise<=0, it is set to an arbitrary value in thanSet()
        cp = fr.readNodes()
        self.thanSet(cp, itype, dise, thetae)


    def thanExpSyk(self, than):
        "Exports the line to syk file."
        if not than.fillModeOn:   #In this case we draw only the outline
            than.write("%15.3f  %s\n" % (self.cp[0][2], than.layname))
            for cp1 in self.cp:
                than.write("%15.3f%15.3f\n" % (cp1[0], cp1[1]))
            than.write("$\n")
        else:
            for cha in p_gindplt.hatlines(self.cp, self.dise, self.thetae):
                than.write("%15.3f  %s\n" % (self.cp[0][2], than.layname))
                for cp1 in cha:
                    than.write("%15.3f%15.3f\n" % (cp1[0], cp1[1]))
                than.write("$\n")


    def thanExpBrk(self, than):
        "Exports the line to brk file."
        if not than.fillModeOn:   #In this case we draw only the outline
            for cp1 in self.cp:
                than.ibr += 1
                than.write(than.form % (than.ibr, cp1[0], cp1[1], self.cp[0][2]))
            than.write("$\n")
        else:
            hp = p_gindplt.HatchPolygon(self.cp)
            for cha in hp.hatchlines(self.dise, self.thetae):
                for cp1 in cha:
                    than.ibr += 1
                    than.write(than.form % (than.ibr, cp1[0], cp1[1], self.cp[0][2]))
                than.write("$\n")


    def thanExpPil(self, than):   #Thanasis2021_10_03
        "Exports the line to a PIL raster image; respects dashed lines."
        if not than.fillModeOn:   #In this case we draw only the outline
            thanPilLine(than, self.cp)
        elif self.itype == 0:   #Solid
            g2l = than.ct.global2Local
            xy1 = [g2l(c1[0], c1[1]) for c1 in self.cp[:-1]]
            temp = than.dc.polygon(xy1, outline=than.outline, fill=than.outline)
        else:
            hp = p_gindplt.HatchPolygon(self.cp)
            for cha in hp.hatchlines(self.dise, self.thetae):
                thanPilLine(than, cha)


    def thanPlotPdf(self, than):
        "Plots the line to a pdf file."
        #FIXME: report width of polyline
        #FIXME: respect dashed lines
        if len(self.cp) < 2: return
        g2l = than.ct.global2Local
        hp = p_gindplt.HatchPolygon(self.cp)
        for cha in hp.hatchlines(self.dise, self.thetae):
            xy1 = [g2l(c1[0], c1[1]) for c1 in cha]
            ca = xy1[0]
            cb = xy1[1]
            p = pyx.path.line(ca[0], ca[1], cb[0], cb[1])
        than.dc.stroke(p)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property."""
        cp = [list(cc) for cc in self.cp]
        for cc in cp: cc[:3] = fun(cc[:3])
        self.thanSet(cp, self.itype, self.dise, self.thetae)


#    def __del__(self):
#        print("ThanHatch", self, "is deleted")


    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type otype nearest to ccu."
        if "ena" not in otypes: return None            # Object snap is disabled
        ps = []
        if "end" in otypes:       # type "end" without type "int"
            for c in self.cp:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "end", c))
        if "mid" in otypes:
            for ca, cb in iterby2(self.cp):
                c = [(ca1+cb1)*0.5 for (ca1,cb1) in zip(ca, cb)]  #works for python2,3
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "mid", c))
        if "nea" in otypes:
            c = self.thanPntNearest(ccu)
            if c is not None:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "nea", c))
        if cori is not None and "per" in otypes:
            for c in self.thanPerpPoints(cori):
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "per", c))
        if eother is not None and "int" in otypes:
            ps.extend(thanintall.thanIntsnap(self, eother, ccu, proj))
        if len(ps) < 1: return None
        return min(ps)


    def thanTkGet(self, proj):
        "Gets the attributes of the hatch interactively from a window."
        def hatchCanc(): proj[2].thanGudSetSelDelx(); return Canc

        un = proj[1].thanUnits
        itype = 1                     #Default type: linehatch
        dise = 0.5                    #Default distance between hatch lines
        thetae = 0.25*pi              #Default angle of hatch lines with respect to x-axis (45 deg)

        cpol = self.__getClosedElem(proj)
        if cpol == Canc:  return hatchCanc()
        if cpol == "p":
            cpol = self.__getInterior(proj)
            if cpol == Canc: return hatchCanc()

        mes = "%s <%s>: " % (T["Specify distance of hatch lines (Solid)"],  un.strdis(dise))
        dise = proj[2].thanGudGetPosFloat(mes, default=dise, options=("Solid",))
        if dise == Canc: return hatchCanc() # Hatch cancelled
        if dise == "s":
            itype = 0   #Solid
            dise = 0.5
        else:
            itype = 1
            st = "%s(%s) <%s>: " % (T["Angle angle of hatch lines"], un.anglunit, un.strang(thetae))
            thetae = proj[2].thanGudGetFloat(st, default=un.rad2unit(thetae))
            if thetae == Canc:  return hatchCanc()   # Hatch cancelled
            thetae = un.unit2rad(thetae)

        proj[2].thanGudSetSelDelx()
        self.thanSet(cpol, itype, dise, thetae)
        return True


    def __getInterior(self, proj):
        "Prompt the user to select interior point of hatch."
        proj[2].thanPrt(T["Warning: Interior point method is experimental"], "can1")
        while True:
            res = proj[2].thanGudGetPoint(T["Pick interior point: "])
            if res == Canc: return res  # Hatch cancelled
            #print("getinterior(): res=", res)
            proj[2].thanGudSetSelExternalFilter(lambda e: e.than2Line(None))
            elems = proj[2].thanGudGetDisplayed()
            proj[2].thanGudSetSelExternalFilter(None)    #Delete filter
            #print("getinterior(): elems=", elems)
            clines = self.__elem2lines(proj, elems)
            #print("getinterior(): clines=", clines)
            cpol = enclosing(proj, clines, res)
            if cpol == Canc: return Canc
            if cpol is not None:
                self.thanSet(cpol, 1, 0.5, 0.25*pi)
                if self.thanIsNormal():
                    than = proj[2].than
                    g2l = than.ct.global2Local
                    xy1 = [g2l(c1[0], c1[1]) for c1 in cpol]
                    proj[2].thanGudGetSelElemx(())   #Remove all 'selx' tags, if they exist
                    temp = than.dc.create_line(xy1, fill="blue", tags="selx")  #Create temporary line with tag 'selx'
                    return cpol   #Enclosing polygon
            proj[2].thanPrt(T["Selected point is not enclosed. Try again."], "can")


    def __elem2lines(self, proj, elems):
        "Convert elements to lines."
        clines = []
        dt = proj[2].thanGudGetDt()
        for e in elems:
            clines.append(e.than2Line(dt)[0])
        return clines


    def __getClosedElem(self, proj):
        "Prompt the user to select a closed element to hatch."
        from thancom import thancomsel
        def filt2(e): return e.than2Line(dt=None)

        mes =  T["Select closed element to hatch (P=Pick interior point): "]
        while True:
            elem = thancomsel.thanSelect1(proj, mes, filter=filt2, options=("Pick",))
            proj[2].thanGudGetSelElemx(())   #thanSelect1() sets 'selx' tags: remove them
            if elem == Canc: return Canc  # Hatch cancelled
            if elem == "p": return elem
            dt = proj[2].thanGudGetDt()
            cpol = elem.than2Line(dt)[0]
            if not thanNear2(cpol[0], cpol[-1]):
                proj[2].thanPrt(T["Selected element is not closed. Try again."], "can")
                continue
            self.thanSet(cpol, 1, 0.5, 0.25*pi)
            if self.thanIsNormal():
                than = proj[2].than
                g2l = than.ct.global2Local
                xy1 = [g2l(c1[0], c1[1]) for c1 in cpol]
                proj[2].thanGudGetSelElemx(())   #Remove all 'selx' tags, if they exist
                temp = than.dc.create_line(xy1, fill="blue", tags="selx")  #Create temporary line with tag 'selx'
                return cpol   #Enclosing polygon
            proj[2].thanPrt(T["Selected element is degenerate. Try again."], "can")


    def thanList(self, than):
        "Shows information about the line element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("%s %s\n" % (T["Layer:"], than.laypath))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        than.write("%s%s\n" % (T["Spin: "], self.thanSpin()))
        than.write("%s%s    %s%s\n" % (T["Hatch line distance: "], than.strdis(self.dise),
                                       T["Hatch line angle: "],    than.strdir(self.thetae)))
        than.write("%s (%d):\n" % (T["Vertices"], len(self.cp)))
        for i,c1 in enumerate(self.cp):
            than.write("    %s\n" % than.strcoo(c1))
            if i % 20 == 19:
                c = than.read(T["Press enter to continue.."])
                if c == Canc: break


def enclosing(proj, clines, cen):
    "Find minimum enclosing polygon (loop) of point cen."
    delay = ThanDelay(proj[2])
    delay.start()
    pg = p_ggeom.geomloop.PointGraph(clines)
    try: pg.inter(delay)
    except TimeoutError: delay.stop(); return Canc
    areamin = 1.0e100
    loopmin = cpolmin = None
    delay.start()
    for loop1 in pg.iterloops():
        #print(loop1)
        if delay.quit(): delay.stop(); return Canc
        cpol = pg.index2coor(loop1)
        pol = p_gindplt.HatchPolygon(cpol)
        if not pol.inpol(cen): continue
        area = p_ggeom.area(cpol)
        if area >= areamin: continue
        areamin = area
        loopmin = loop1   #loopmin is needed only for debugging
        cpolmin = cpol
    #return loopmin
    return cpolmin
