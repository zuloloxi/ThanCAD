toplevels = []
ALL = "ALL"                                         #For compatibility


class EmuInter(object):
    "An object that emulates the Tk environment for a Canvas which plots to another device/file."

    def __init__(self, filename=None):
        "Initialise toplevel tracking and other things."
        self._closed = False
        self.width = None
        self.height = None
        self.filename = filename
        self.device = None

    def mainloop(self):
        "The drawing is drawn; close the dxf file."
        self.destroy()

    def destroy(self):
        "Close the current EmuInter device/file and the device/file of all toplevels."
        self.destroy1()
        for toplevel in toplevels: toplevel.destroy1()

    def destroy1(self):
        "Close this object's device/file."
        pass

    def title(self, tit):
        "Plot a title above drawing area."
        pass

    def columnconfigure(self, *args, **kw): pass    #For compatibility
    def rowconfigure(self, *args, **kw): pass       #For compatibility


class Toplevel(object):
    "Emulate a Toplevel windows; just a new Tk object (writing to a new dxf file)."
    def __init__(self, master):
        "Add self to toplevels, so that the EmuInter instance can close all the toplevels."
        self.__bases__ = self.__bases__ + (master.__class__,)
        super(Toplevel, self).__init__()
        toplevels.append(self)

    def destroy(self):
        "Just close the dxf file."
        self.destroy1()


class EmuCanvas(object):
    "An object that emulates the Tk Canvas, but plots the drawing to another device/file."

    def __init__(self, master, background, width=19.0, height=29.0):
        """Initialise the emulated Canvas object.

        master should be the Tk object, also defined in this module.
        width and height should be in cm.
        I don't remember why I have put background with no default."
        """
        self.width = master.width = width
        self.height = master.height = height
        self.device = None
        self.textsize = 7
        self.texttheta = 0.0
        self.device = master.device

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
        pass

    def create_text(self, x, y, fill="white", text=""):
        "Plot text."
        pass

    def create_rectangle(self, x1, y1, x2, y2, fill=None, outline="white", width=1):
        "Plot a possibly filled rectangle."
        pass

    def create_polygon(self, *args, **kw): pass     #Not yet implemented
    def create_arc(self, *args, **kw): pass         #Not yet implemented

    def __setColor(self, tkcol):
        "Sets color; transforms from Tk colour to device dependent colour code."
        pass
