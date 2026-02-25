from math import hypot
PLINECLOSED   = 1
PLINE3        = 8
PLINEVERTEX3  = 32
PLINEWHOKNOWS = 128

class ThanDxfLin:
    "Mixin to export lines to .dxf file."

#===========================================================================

    def __init__(self):
        "Some Initialisation for polyvertex."
        self.__firstVertex = 1

#===========================================================================

    def thanDxfPlotLine(self, xp, yp):
        "Plots many line segments."
        p = self.thanDxfPlot
        p(xp[0], yp[0], 3)
        for i in range(1, len(xp)): p(xp[i], yp[i], 2)

#===========================================================================

    def thanDxfPlotLine3 (self, xp, yp, zp):
        "Plots many 3d line segments."
        p = self.thanDxfPlot3
        p(xp[0], yp[0], zp[0], 3)
        for i in range(1, len(xp)): p(xp[i], yp[i], zp[i], 2)

#===========================================================================

    def thanDxfPlotPolyline (self, xgram, ygram, zgram1=0.0):      #Thanasis2024_01_23: added zgram1
        "Plots a 2d polyline."
        ig = len(xgram)
        if ig < 2: return

        self.thanDxfWrEntry(0, 'POLYLINE')
        self.thanDxfWrLinatts()

        (px, py, pz) = self.thanDxfTop3(xgram[0], ygram[0], zgram1)             #Thanasis2024_01_23
        px = py = 0.0   #According to dxf12 manual page 23, these must be zero  #Thanasis2024_01_23
        self.thanDxfWrEntry(66, 1)
        self.thanDxfWrXyz(px, py, pz)
        self.thanDxfWrEntry(70, PLINEWHOKNOWS)
        self.thanDxfWrPlineWidth()

        for i in range(ig):
            (px, py) = self.thanDxfTop(xgram[i], ygram[i])
            self.thanDxfWrEntry(0, 'VERTEX')
            self.thanDxfWrLinatts()
            self.thanDxfWrXy(px, py)

        self.thanDxfWrEntry(0, 'SEQEND')
        self.thanDxfSetNow(px, py)

#===========================================================================

    def thanDxfPlotPolyline3 (self, xgram, ygram, zgram):
        "Plots a 3d polyline."
        ig = len(xgram)
        if ig < 2: return

        self.thanDxfWrEntry(0, 'POLYLINE')
        self.thanDxfWrLinatts()

        (px, py, pz) = self.thanDxfTop3(xgram[0], ygram[0], zgram[0])
        px = py = 0.0   #According to dxf12 manual page 23, these must be zero  #Thanasis2024_01_23
        self.thanDxfWrEntry(66, 1)
        self.thanDxfWrXyz(px, py, pz)
        self.thanDxfWrEntry(70, PLINE3)
        self.thanDxfWrPlineWidth()

        for i in range(ig):
            (px, py, pz) = self.thanDxfTop3(xgram[i], ygram[i], zgram[i])
            self.thanDxfWrEntry(0, 'VERTEX')
            self.thanDxfWrLinatts()
            self.thanDxfWrXyz(px, py, pz)
            self.thanDxfWrEntry(70, PLINEVERTEX3)

        self.thanDxfWrEntry(0, 'SEQEND')
        self.thanDxfSetNow3(px, py, pz)

#===========================================================================

    def thanDxfPlotPolyVertex (self, xx, yy, ic, bulge=0.0):
        "Plots a 2d polyline, vertex by vertex."

#-------polyline beginning-----------------------------------------

        if self.__firstVertex:
            self.thanDxfWrEntry(0, 'POLYLINE')
            self.thanDxfWrLinatts()

            (px, py) = self.thanDxfTop(xx, yy)
            self.thanDxfWrEntry(66, 1)
            self.thanDxfWrXy(px, py)
            self.thanDxfWrEntry(70, PLINEWHOKNOWS)
            self.thanDxfWrPlineWidth()

            if bulge != 0.0:
                self.thanDxfWrEntry(42, bulge)

            self.thanDxfWrEntry(0, 'VERTEX')
            self.thanDxfWrLinatts()
            self.thanDxfWrXy(px, py)

            self.thanDxfSetNow(px, py)
            self.__firstVertex = 0

#-------polyline end----------------------------------------

        elif ic >= 999:
            self.thanDxfWrEntry(0, 'SEQEND')
            self.__firstVertex = 1
            return

#-------polyline point---------------------------------------

        else:
            (px, py) = self.thanDxfTop (xx, yy)
            self.thanDxfWrEntry(0, 'VERTEX')
            self.thanDxfWrLinatts()
            self.thanDxfWrXy(px, py)
            self.thanDxfWrPlineWidth()

            if bulge != 0.0:
                self.thanDxfWrEntry(42, bulge)

            self.thanDxfSetNow(px, py)

#==========================================================================

    def thanDxfPlotPolyVertex3 (self, xx, yy, zz, ic):
        "Plots a 3d polyline, vertex by vertex."

#-------polyline beginning-----------------------------------------

        if self.__firstVertex:
            self.thanDxfWrEntry(0, 'POLYLINE')
            self.thanDxfWrLinatts()

            (px, py, pz) = self.thanDxfTop3(xx, yy, zz)
            self.thanDxfWrEntry(66, 1)
            self.thanDxfWrXyz(px, py, pz)
            self.thanDxfWrEntry(70, PLINE3)
            self.thanDxfWrPlineWidth()

            self.thanDxfWrEntry(0, 'VERTEX')
            self.thanDxfWrLinatts()
            self.thanDxfWrXyz(px, py, pz)
            self.thanDxfWrEntry(70, PLINEVERTEX3)

            self.thanDxfSetNow3(px, py, pz)
            self.__firstVertex = 0

#-------polyline end----------------------------------------

        elif ic >= 999:
            self.thanDxfWrEntry(0, 'SEQEND')
            self.__firstVertex = 1
            return

#-------polyline point---------------------------------------

        else:
            (px, py, pz) = self.thanDxfTop3(xx, yy, zz)
            self.thanDxfWrEntry(0, 'VERTEX')
            self.thanDxfWrLinatts()
            self.thanDxfWrXyz(px, py, pz)
            self.thanDxfWrEntry(70, PLINEVERTEX3)
            self.thanDxfWrPlineWidth()
            self.thanDxfSetNow3(px, py, pz)


#===========================================================================

    def thanDxfPlotLinebox (self, xx, yy, bb, hh):
        "Plots a 2d rectangle."

#-------Plot line

        xx1 = xx + bb
        yy1 = yy + hh

        self.thanDxfPolyVertex (xx,  yy,  2)
        self.thanDxfPolyVertex (xx1, yy,  2)
        self.thanDxfPolyVertex (xx1, yy1, 2)
        self.thanDxfPolyVertex (xx,  yy1, 2)
        self.thanDxfPolyVertex (xx,  yy,  2)
        self.thanDxfPolyVertex (0.0, 0.0, 999)

#===========================================================================

    def thanDxfPlot(self, xx, yy, icom):
        "Plots a line from previous point to this and some housekeeping."

#-------Check if end

        ic = abs(icom)
        if ic == 1000 or ic == 999:
            self.thanDxfWrEntry(0, 'ENDSEC')
            self.thanDxfWrEntry(0, 'EOF')
            self.thanFdxf.close()
            return

#-------Plot line

        if ic == 1: ic = self.thanIpen
        self.thanIpen = ic
        (px, py) = self.thanDxfTop(xx, yy)
        if ic == 2:
            self.thanDxfWrEntry(0, "LINE")
            self.thanDxfWrLinatts()
            px1, py1 = self.thanDxfGetNow()
            self.thanDxfWrXy(px1, py1)
            self.thanDxfWrXy1(px, py)
        self.thanDxfSetNow(px, py)

#-------Check if negative

        if icom < 0: self.thanDxfLocref3(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

#===========================================================================

    thanDxfPlot10 = thanDxfPlot    # For compatibility; see the following function

    def thanDxfPlot10a(self, x, y, ipen):
        """Plots or moves the pen with 10cm steps.

        This code is for fast old pen plotters (e.g. CIL). If the distance to
        move or plot is big (e.g. 1m and more) the plotter is moving the drum
        very fast. This either ruptures the paper or causes the pen not write.
        Here we move the pen with 10cm steps, so that the drum does not have the
        time to accelerate to high speed.
        It also addresses a problem with 2bytes integers (whose biggest value
        is 32767) which were used by the old CIL plotter. A call to locref
        initialises the origin and keeps the numbers x and y small inside the CIL
        plotter.
        Note that when ipen=2 and the pen is already down, the plotter still tries
        to move it down, which wears off the pen. Hence the hack with ipen1=1.
        The value 1 in ipen, does not change the vertical position of the pen (up
        or down).
        This code was written in Fortran IV around 1982, in the 550 Prime
        computer.
        """
        ipen1=ipen
        x2, y2 = self.thanDxfPlotWhere()
        dis=hypot(x-x2, y-y2)
        if dis>10.0:  # go to 2
            k=int(dis/10.0)
            dx=(x-x2)*10.0/dis
            dy=(y-y2)*10.0/dis
            for i in range(k):
                x2 += dx
                y2 += dy
                self.thanDxfPlot(x2, y2, ipen1)
                self.thanDxfLocref(x2, y2, 1.0, 1.0)
                ipen1=1
        self.thanDxfPlot(x,y,ipen1)
        self.thanDxfLocref (x,y,1.0,1.0)

#===========================================================================

    def thanDxfPlot3(self, xx, yy, zz, icod):
        "Plots a 3D line from previous point to this."

#-------Plot line

        ic = abs(icod)
        if ic == 1: ic = self.thanIpen
        self.thanIpen = ic
        (px, py, pz) = self.thanDxfTop3(xx, yy, zz)
        if ic == 2:
            self.thanDxfWrEntry(0, "LINE")
            self.thanDxfWrLinatts()
            px1, py1, pz1 = self.thanDxfGetNow3()
            self.thanDxfWrXyz(px1, py1, pz1)
            self.thanDxfWrXyz1(px, py, pz)
        self.thanDxfSetNow3(px, py, pz)

#-------Check if negative

        if icod < 0: self.thanDxfLocref3(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


if __name__ == "__main__":
    dxf = ThanDxfLin()
