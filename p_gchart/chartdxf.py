from .chart import ThanChart
from .vis import vis

class ThanChartDxf:
        "Class to emulate dxf; it takes dxf calls and produces a ThanChart at the end."

        def __init__(self):
            self.ch = ThanChart("Dxf like chart")
            self.ipenOld = 3
            self.lineActive = False
            self.px = self.py = None
            self.icol = self.icolActive = 0
            self.cols = ["red", "yellow", "green", "cyan", "blue", "magenta", "white"]

        def thanDxfPlot(self, xx, yy, ipen):
            ic = abs(ipen)
            if ic == 1: ic = self.ipen
            if ic == 999:
                if self.lineActive:
                    self.ch.curveAdd(self.px, self.py, color=self.cols[self.icol])
                vis(self.ch)
                self.__init__()
            elif ic == 2:
                if not self.lineActive:
                    self.px = [self.pxOld]
                    self.py = [self.pyOld]
                self.lineActive = True
                self.px.append(xx)
                self.py.append(yy)
                self.pxOld = xx
                self.pyOld = yy
                self.ipenOld = 2
            else:
                if self.lineActive:
                    self.ch.curveAdd(self.px, self.py, color=self.cols[self.icolActive])
                self.icolActive = self.icol
                self.lineActive = False
                self.px = self.py = None
                self.pxOld = xx
                self.pyOld = yy
                self.ipenOld = 3

        def thanDxfSetColor(self, icol):
            "Set the color."
            self.icol = (icol-1) % len(self.cols)
            if not self.lineActive: self.icolActive = self.icol

        def thanDxfPlotPolyLine(self, xx, yy):
            "Plot a polyline."
            self.thanDxfPlot(xx[0], yy[0], 3)
            for i in range(1, len(xx)):
                self.thanDxfPlot(xx[i], yy[i], 2)
