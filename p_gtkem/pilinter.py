from PIL import Image, ImageDraw
from p_gcol import thanTk2Rgb
from .emuinter import EmuInter, EmuCanvas, Toplevel, ALL


class Tk(EmuInter):
    "An object that emulates the Tk environment for a Canvas which plots the drawing to a PIL image."
    _idatFil = [0]

    def __init__(self, filename=None):
        "Set the image name; this object is apparently the library object."
        if filename is None:
            self._idatFil[0] += 1
            filename = "data%03d.bmp" % (self._idatFil[0], )
        super(Tk, self).__init__(filename)

    def destroy1(self):
        "The drawing is drawn; save the image."
        if not self._closed:
            self.device.save(self.filename)
            self._closed = True

    def title(self, tit):
        "Plot a title above drawing area."
#        self.device.thanDxfPlotSymbol(20.0, self.height-(-20.0), 15, tit, 0.0)
        pass


class Canvas(EmuCanvas):
    "An object that emulates the Tk Canvas, but plots the drawing to a PIL image."

    def __init__(self, master, background, width=600, height=400):
        """Initialise the emulated Canvas object.

        master should be the Tk object, also defined in this module.
        width and height should be in cm.
        I don't remember why I have put background with no default."
        """
        super(Canvas, self).__init__(master, background, width, height)
        self.device = master.device = Image.new("RGB", (master.width, master.height))
        self.imd = ImageDraw.Draw(self.device)

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
        "Plot a possibly filled rectangle."
        outline = self.__color(outline)
        if fill is not None:
            fill = self.__color(fill)
            self.imd.rectangle((x1, y1, x2, y2), fill=fill, outline=outline)
        else:
            self.imd.rectangle((x1, y1, x2, y2), outline=outline, width=width)

    def __color(self, tkcol):
        "Sets color; transforms from Tk colour to dxf code color."
        if tkcol.lower() == "white": tkcol = "black"
        try:
            rgb = thanTk2Rgb(tkcol)
        except Exception:
            rgb = 0, 0, 0
        return rgb
