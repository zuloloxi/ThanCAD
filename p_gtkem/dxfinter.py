from p_gdxf import ThanDxfPlot
from p_gcol import thanTk2Rgb, thanRgb2DxfColCodeApprox
from .emuinter import EmuInter, EmuCanvas, Toplevel, ALL


class Tk(EmuInter):
    "An object that emulates the Tk environment for a Canvas which plots the drawing to a dxf file."

    def destroy1(self):
        "Just close the dxf file."
        if not self._closed:
            self.device.thanDxfPlot(0.0, 0.0, 999)
            self._closed = True

    def title(self, tit):
        "Plot a title above drawing area."
        self.device.thanDxfPlotSymbol(20.0, self.height-(-20.0), 15, tit, 0.0)

"""
class Toplevel(Tk):
    "Emulate a Toplevel windows; just a new Tk object (writting to a new dxf file)."
    def __init__(self, master):
        "Add self to toplevels, so that Tk instance can close all the toplevels."
        Tk.__init__(self)
        toplevels.append(self)

    def destroy(self):
        "Just close the dxf file."
        self.destroy1()
"""


class Canvas(EmuCanvas):
    "An object that emulates the Tk Canvas, but plots the drawing to a dxf file."

    def __init__(self, master, background, width=19.0, height=29.0):
        """Initialise the emulated Canvas object.

        master should be the Tk object, also defined in this module.
        width and height should be in cm.
        I don't remember why I have put background with no default."
        """
        super(Canvas, self).__init__(master, background, width, height)
        self.device = master.device = ThanDxfPlot()
        self.dxf = self.device                 #Convenienet name
        self.dxf.thanDxfPlots(master.filename)

    def create_line(self, xy, fill="white", width=1):
        "Plot a line."
        if len(xy) < 2: return
        self.__setColor(fill)
        ipen = 3
        for x,y in xy:
            self.dxf.thanDxfPlot(x, self.height-y, ipen)
            ipen = 2

    def create_text(self, x, y, fill="white", text=""):
        "Plot text."
        text = str(text).rstrip()
        if len(text) == 0: return
        self.__setColor(fill)
        self.dxf.thanDxfPlotSymbol(x, self.height-y, self.textsize, text, self.texttheta)

    def create_rectangle(self, x1, y1, x2, y2, fill=None, outline="white", width=1):
        "Plot a possibly filled rectangle."
        if fill is not None:
            self.__setColor(fill)
            self.dxf.thanDxfPlotSolid4(x1, self.height-y1,
                                       x2, self.height-y1,
                                       x2, self.height-y2,
                                       x1, self.height-y2)
        self.__setColor(outline)
        self.dxf.thanDxfPlot(x1, self.height-y1, 3)
        self.dxf.thanDxfPlot(x2, self.height-y1, 2)
        self.dxf.thanDxfPlot(x2, self.height-y2, 2)
        self.dxf.thanDxfPlot(x1, self.height-y2, 2)
        self.dxf.thanDxfPlot(x1, self.height-y1, 2)

    def __setColor(self, tkcol):
        "Sets color; transforms from Tk colour to dxf colour code."
        try:
            rgb = thanTk2Rgb(tkcol)
            icod = thanRgb2DxfColCodeApprox(rgb)
        except Exception:
            icod = 7
        self.dxf.thanDxfSetColor(icod)
