from math import pi, cos, sin


PI=pi   #3.1415926535897932384626433832795,
PI4=pi/4.0


class ThanDxfDra:
    "Mixin to draw various objects."

    def __init__(self):
        "No initialisation needed."
        pass


    def thanDxfPlotBlock (self, bloc, xa, ya, xsc, ysc, thet):
        "Plots a predefined block."
        self.thanDxfWrEntry(0, 'INSERT')
        self.thanDxfWrLayer()
        self.thanDxfWrEntry(2, bloc)

        (px, py) = self.thanDxfTop(xa, ya)
        self.thanDxfWrXy(px, py)
        self.thanDxfWrEntry(41, xsc)
        self.thanDxfWrEntry(42, ysc)
        self.thanDxfWrEntry(50, thet)


    def thanDxfPlotBlock3 (self, bloc, xa, ya, za, xsc, ysc, zsc, thet):
        "Plots a 3d predefined block."
        self.thanDxfWrEntry(0, 'INSERT')
        self.thanDxfWrLayer()
        self.thanDxfWrEntry(2, bloc)

        (px, py, pz) = self.thanDxfTop3(xa, ya, za)
        self.thanDxfWrXyz(px, py, pz)
        self.thanDxfWrEntry(41, xsc)
        self.thanDxfWrEntry(42, ysc)
        self.thanDxfWrEntry(43, zsc)
        self.thanDxfWrEntry(50, thet)


    def thanDxfPlotCircle (self, xc, yc, r):
        "Plots a circle."
        self.thanDxfWrEntry(0, 'CIRCLE')
        self.thanDxfWrLinatts()

        (px, py) = self.thanDxfTop(xc, yc)
        self.thanDxfWrXy(px, py)
        self.thanDxfWrEntry(40, r)


    def thanDxfPlotCircle3 (self, xc, yc, zc, r):
        "Plots a 3d circle."
        self.thanDxfWrEntry(0, 'CIRCLE')
        self.thanDxfWrLinatts()

        (px, py, pz) = self.thanDxfTop3(xc, yc, zc)
        self.thanDxfWrXyz(px, py, pz)
        self.thanDxfWrEntry(40, r)


    def thanDxfPlotArc(self, xc, yc, r, ang1, ang2):
        """Plots an arc of circle.

        xc,yc: center of the circle
        r    : radius of circle
        ang1 : angle of the beginning of the arc
        ang2 : angle of the end of the arc"""
        self.thanDxfWrEntry(0, 'ARC')
        self.thanDxfWrLinatts()

        (px, py) = self.thanDxfTop(xc, yc)
        self.thanDxfWrXy(px, py)
        self.thanDxfWrEntry(40, r)
        self.thanDxfWrEntry(50, ang1)
        self.thanDxfWrEntry(51, ang2)


    def thanDxfPlotArc3(self, xc, yc, zc, r, ang1, ang2):
        """Plots an arc of circle.

        xc,yc: center of the circle
        r    : radius of circle
        ang1 : angle of the beginning of the arc
        ang2 : angle of the end of the arc"""

        self.thanDxfWrEntry(0, 'ARC')
        self.thanDxfWrLinatts()
        (px, py, pz) = self.thanDxfTop3(xc, yc, zc)
        self.thanDxfWrXyz(px, py, pz)
        self.thanDxfWrEntry(40, r)
        self.thanDxfWrEntry(50, ang1)
        self.thanDxfWrEntry(51, ang2)


    def thanDxfPlotEllipse(self, xc, yc, a, b, ang1, ang2, phi):
        """Plots an elliptic arc; Warning: dxf version 13!!.

        xc,yc: center of the ellipse
        a    : semi-major axis
        b    : semi-minor axis
        ang1 : angle of the beginning of the arc in decimal degrees
        ang2 : angle of the end of the arc in decimal degrees."""

        self.thanDxfWrEntry(0, 'ELLIPSE')
        self.thanDxfWrLinatts()

        (px, py) = self.thanDxfTop(xc, yc)
        self.thanDxfWrXy(px, py)

        phi *= pi/180.0
        xm = xc + a*cos(phi)
        ym = yc + a*sin(phi)
        (px, py) = self.thanDxfTop(xm, ym)
        self.thanDxfWrXy1(px, py)    #Relative coordinates of the end of the semi-major axis

        self.thanDxfWrXyzc(200, 0.0, 0.0, 1.0)  #Normal vector to the plane of the ellipse

        self.thanDxfWrEntry(40, b/a)               #eccentricity
        self.thanDxfWrEntry(41, ang1*pi/180.0)     #Start angle in radians
        self.thanDxfWrEntry(42, ang2*pi/180.0)     #End angle in radians


    def thanDxfPlotPoint(self, xp, yp):
        "Plots a point."
        self.thanDxfWrEntry(0, 'POINT')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        (px, py) = self.thanDxfTop(xp, yp)
        self.thanDxfWrXy(px, py)


    def thanDxfPlotPoint3(self, xp, yp, zp):
        "Plots a 3d point."
        self.thanDxfWrEntry(0, 'POINT')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        (px, py, pz) = self.thanDxfTop3(xp, yp, zp)
        self.thanDxfWrXyz(px, py, pz)


    def thanDxfPlotSolid4 (self, xx1, yy1, xx2, yy2, xx3, yy3, xx4, yy4):
        """Plots a solid 4node polygon.

        Note that the points must be given in clockwise order, or anti-closkwise order.
        This method then swaps 3rd and 4th point, so that the resulting dxf file
        is according to the specifications (with thAtCAD).
        """
        self.thanDxfWrEntry(0, 'SOLID')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        (px, py) = self.thanDxfTop(xx1, yy1)
        self.thanDxfWrXy(px, py)

        (px, py) = self.thanDxfTop(xx2, yy2)
        self.thanDxfWrXy1(px, py)

        (px, py) = self.thanDxfTop(xx4, yy4)
        self.thanDxfWrXyc(2, px, py)

        (px, py) = self.thanDxfTop(xx3, yy3)
        self.thanDxfWrXyc(3, px, py)


    def thanDxfPlotSolid3 (self, xx1, yy1, xx2, yy2, xx3, yy3):
        "Plots a solid triangle."
        self.thanDxfWrEntry(0, 'SOLID')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        (px, py) = self.thanDxfTop(xx1, yy1)
        self.thanDxfWrXy(px, py)

        (px, py) = self.thanDxfTop(xx2, yy2)
        self.thanDxfWrXy1(px, py)

        (px, py) = self.thanDxfTop(xx3, yy3)
        self.thanDxfWrXyc(2, px, py)

        self.thanDxfWrXyc(3, px, py)


    def thanDxfPlot3dface3(self, xx1, yy1, zz1, xx2, yy2, zz2, xx3, yy3, zz3):
        "Plots 3dface triangle."
        self.thanDxfWrEntry(0, '3DFACE')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        (px, py) = self.thanDxfTop(xx1, yy1)
        self.thanDxfWrXyz(px, py, zz1)

        (px, py) = self.thanDxfTop(xx2, yy2)
        self.thanDxfWrXyz1(px, py, zz2)

        (px, py) = self.thanDxfTop(xx3, yy3)
        self.thanDxfWrXyzc(2, px, py, zz3)

        self.thanDxfWrXyzc(3, px, py, zz3)


    def thanDxfPlot3dface4(self, xx1, yy1, zz1, xx2, yy2, zz2, xx3, yy3, zz3, xx4, yy4, zz4):
        "Plots 3dface triangle."
        self.thanDxfWrEntry(0, '3DFACE')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        (px, py) = self.thanDxfTop(xx1, yy1)
        self.thanDxfWrXyz(px, py, zz1)

        (px, py) = self.thanDxfTop(xx2, yy2)
        self.thanDxfWrXyz1(px, py, zz2)

        (px, py) = self.thanDxfTop(xx3, yy3)
        self.thanDxfWrXyzc(2, px, py, zz3)

        (px, py) = self.thanDxfTop(xx4, yy4)
        self.thanDxfWrXyzc(3, px, py, zz4)


    def thanDxfPlotSolidCircle8(self, x, y, r, i1, i2):
        """Plots integer number of eighths of a solid circle using solid polygons.

        It splits the circle in eightths, and approximates one eightth
        with a 4node polygon. It begins with the i1-th eightth and stops
        at i2-th eightth:    1 <= i1 <= i2 <= 8."""
        for ri in range(i1-1, i2):
            self.thanDxfPlotSolid4 (x, y,
                x+r*cos(PI4*ri),        y+r*sin(PI4*ri),
                x+r*cos(PI4*(ri+0.5)),  y+r*sin(PI4*(ri+0.5)),
                x+r*cos(PI4*(ri+1)),    y+r*sin(PI4*(ri+1)))

#======================================================================

    def thaDxfPlotSolidRing(self, xc, yc, ri, re, n):
        """Plots a full solid ring using n solid polygons.

        xc, yc: coordinates of the center of the ring
        ri, re: internal and external radius of the ring
        n     : number of 4point solids (bigger means finer)"""
        dth = 2.0 * PI / n
        cosd = cos(dth)
        sind = sin(dth)
        cost = 1.0
        sint = 0.0
        x1 = xc + ri
        y1 = yc
        x3 = xc + re
        y3 = yc

        for i in range(n):
            x2   = cost*cosd - sint*sind
            sint = sint*cosd + cost*sind
            cost = x2
            x2 = xc + ri*cost
            y2 = yc + ri*sint
            x4 = xc + re*cost
            y4 = yc + re*sint
            self.thanDxfPlotSolid4(x1, y1, x2, y2, x4, y4, x3, y3)
            x1 = x2
            y1 = y2
            x3 = x4
            y3 = y4


    def thanDxfPlotSolidCircle(self, xc, yc, ri, n1):
        """Plots a full solid circle using n1 solid polygons.

        xc, yc: coordinates of the center of the circle
        ri    : radius of the circle
        n1    : number of 4point solids (bigger means finer)"""
        n = int((n1 + 1) / 2)
        dth = 2.0 * PI / (2*n)
        cosd = cos(dth)
        sind = sin(dth)
        cost = 1.0
        sint = 0.0
        x2 = xc + ri
        y2 = yc

        for i in range(n):
            x3   = cost*cosd - sint*sind
            sint = sint*cosd + cost*sind
            cost = x3
            x3 = xc + ri*cost
            y3 = yc + ri*sint

            x4   = cost*cosd - sint*sind
            sint = sint*cosd + cost*sind
            cost = x4
            x4 = xc + ri*cost
            y4 = yc + ri*sint

            self.thanDxfPlotSolid4 (xc, yc, x2, y2, x3, y3, x4, y4)
            x2 = x4
            y2 = y4


    def thanDxfPlotImage(self, filnam, x1, y1, size, scale, theta):
        "Plots a string to a .dxf file."
        (px, py) = self.thanDxfTop(x1, y1)

        self.thanDxfWrEntry(0, 'THANCAD_IMAGE')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        self.thanDxfWrXy(px, py)

        self.thanDxfWrEntry(1, filnam)
        self.thanDxfWrEntry(40, size[0])
        self.thanDxfWrEntry(41, size[1])
        self.thanDxfWrEntry(42, scale)
        self.thanDxfWrEntry(50, theta)


if __name__ == "__main__":
    dxf = ThanDxfDra()
