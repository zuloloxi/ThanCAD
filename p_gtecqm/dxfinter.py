from p_gdxf import ThanDxfPlot
from p_gimdxf import thanTk2Rgb, thanRgb2DxfColCodeApprox


class Tk(ThanDxfPlot):
    "An object thet emulates the Tk environment for a Canvas which plots the drawing to a dxf file."
    
    def __init__(self):
        "Intialize the library dxf; this object is apparenty the library object."
        ThanDxfPlot.__init__(self)
        self.thanDxfPlots()

    def mainloop(self):
        "The drawing is drawn; close the dxf file."
        self.thanDxfPlot(0.0, 0.0, 999)

    def title(self, tit):
        "Plot a title above drawing area."
        self.thanDxfPlotSymbol(20.0, self.height-(-20.0), 15, tit, 0.0)

    def columnconfigure(self, *args, **kw): pass    #For compatibility
    def rowconfigure(self, *args, **kw): pass       #For compatibility


class Canvas:
    "An object thet emulates the Tk Canvas, but plots the drawing to a dxf file."

    def __init__(self, master, background, width=19.0, height=29.0):
        """Initialize the emulated Canvas object.

        master should be the Tk object, also defined in this file.
        width and height shouyld be in cm.
        I don't rembember why I have put background with no default."
        """
        self.width = master.width = width
        self.height = master.height = height
        self.dxf = master
        self.textsize = 7
        self.texttheta = 0.0

    def bind(self, *args, **kw): pass               #For compatibility
    def grid(self, *args, **kw): pass               #For compatibility
    def update(self, *args, **kw): pass             #For compatibility
    def delete(self, *args, **kw): pass             #For compatibility

    def winfo_width(self):
        "Return the width of emulated Canvas."
        return self.width

    def winfo_height(self):
        "Return the height of emulated Canvas."
        return self.height

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

    def create_rectangle(self, x1, y1, x2, y2, fill=None, outline="white"):
        if fill != None:
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

    def create_polygon(self, *args, **kw): pass     #Not yet implemented
    def create_arc(self, *args, **kw): pass         #Not yet implemented

    def __setColor(self, tkcol):
        "Sets color; transforms from Tk colot to dxf code color."
        try:
            rgb = thanTk2Rgb(tkcol)
            icod = thanRgb2DxfColCodeApprox(rgb)
        except Exception:
            icod = 7
        self.dxf.thanDxfSetColor(icod)

ALL = "ALL"                                         #For compatibility
