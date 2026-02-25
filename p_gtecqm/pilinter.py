import Image, ImageDraw
from p_gimdxf import thanTk2Rgb, thanRgb2DxfColCodeApprox


class Tk:
    "An object thet emulates the Tk environment for a Canvas which plots the drawing to a dxf file."

    def __init__(self, image="data001.bmp"):
        "Intialize the library dxf; this object is apparenty the library object."
        self.imname = image
        self.im = None
        self.width = None
        self.height = None

    def mainloop(self):
        "The drawing is drawn; close the dxf file."
        self.im.save(self.imname)

    def title(self, tit):
        "Plot a title above drawing area."
#        self.thanDxfPlotSymbol(20.0, self.height-(-20.0), 15, tit, 0.0)
        pass

    def columnconfigure(self, *args, **kw): pass    #For compatibility
    def rowconfigure(self, *args, **kw): pass       #For compatibility


class Canvas:
    "An object thet emulates the Tk Canvas, but plots the drawing to a dxf file."

    def __init__(self, master, background, width=600, height=400):
        """Initialize the emulated Canvas object.

        master should be the Tk object, also defined in this file.
        width and height shouyld be in cm.
        I don't rembember why I have put background with no default."
        """
        master.width = width
        master.height = height
        master.im = Image.new("RGB", (master.width, master.height))
        self.master = master
        self.imd = ImageDraw.Draw(master.im)
        self.width = master.width
        self.height = master.height
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
        col = self.__color(fill)
        self.imd.line(xy, fill=col, width=width)

    def create_text(self, x, y, fill="white", text=""):
        "Plot text."
        text = str(text).rstrip()
        if len(text) == 0: return
        col = self.__color(fill)
        self.imd.text((x, y), text, fill=col)

    def create_rectangle(self, x1, y1, x2, y2, fill=None, outline="white", width=1):
        outline = self.__color(outline)
        if fill != None:
            fill = self.__color(fill)
            self.imd.rectangle((x1, y1, x2, y2), fill=fill, outline=outline)
        else:
            self.imd.rectangle((x1, y1, x2, y2), outline=outline, width=width)

    def create_polygon(self, *args, **kw): pass     #Not yet implemented
    def create_arc(self, *args, **kw): pass         #Not yet implemented

    def __color(self, tkcol):
        "Sets color; transforms from Tk colot to dxf code color."
        if tkcol.lower() == "white": tkcol = "black"
        try:
            rgb = thanTk2Rgb(tkcol)
        except Exception:
            rgb = 0, 0, 0
        return rgb

ALL = "ALL"                                         #For compatibility
