from math import fabs
from tkinter import Tk, Toplevel, Canvas, Frame, Button, Menu, ALL, GROOVE, Image
from PIL import Image as Imagepil
from p_ggen import thanUnicode
from p_gtkwid import (thanicon, thanGudOpenReadFile, thanGudGetSaveFile, thanGudModalMessage,
    thanGudAskOkCancel, can2im)
from p_gtkem import dxfinter, pilinter
import p_gfil
from .thanopt import ThanOptions
from .vistrans import T

##############################################################################
##############################################################################

class WinCoor:
    "Provides coordinate systems as windows."

    def __init__(self, *args):
        if len(args) == 4:
            self.win = [float(x) for x in args]
        elif len(args) == 1:
            self.win = list(args[0].win)
        else:
            raise TypeError("1 or 4 arguments expected")
        if self.win[2] == self.win[0]: self.win[2] = self.win[0] + 1   #Thanasis2009_02_15:empty lines
        if self.win[3] == self.win[1]: self.win[3] = self.win[1] + 1   #Thanasis2009_02_15:empty lines


    def middle(self):
        return (self.win[0]+self.win[2])*0.5, (self.win[1]+self.win[3])*0.5

    def coor(self, other, otherpoint):
        dother = otherpoint[0]-other.win[0], otherpoint[1]-other.win[1]
        dother = dother[0]/(other.win[2]-other.win[0]), dother[1]/(other.win[3]-other.win[1])
        dother = dother[0]*(self.win[2]-self.win[0]), dother[1]*(self.win[3]-self.win[1])
        dother = dother[0]+self.win[0], dother[1]+self.win[1]
        return dother

    def rcoor(self, other, dother):
        dother = dother[0]/(other.win[2]-other.win[0]), dother[1]/(other.win[3]-other.win[1])
        dother = dother[0]*(self.win[2]-self.win[0]), dother[1]*(self.win[3]-self.win[1])
        return dother

    def resize(self, factx, facty):
        w = self.win; factx *= 0.5; facty *= 0.5
        d = (w[2]-w[0])*factx, (w[3]-w[1])*facty
        self.win = w[0]-d[0], w[1]-d[1], w[2]+d[0], w[3]+d[1]

    def reratio(self, other):
        t = other.win; w = self.win
        factx, facty = fabs((t[2]-t[0])/(w[2]-w[0])), fabs((t[3]-t[1])/(w[3]-w[1]))
        fact = min((factx, facty))
        self.resize(factx/fact-1, facty/fact-1)

    def recenter(self, ce):
        d = (self.win[2]-self.win[0])*0.5, (self.win[3]-self.win[1])*0.5
        self.win = ce[0]-d[0], ce[1]-d[1], ce[0]+d[0], ce[1]+d[1]


##############################################################################
##############################################################################

class ThanZoomPanCoor:
    "Represents three coordinate systems for use in zoom and pan (Tkinter canvas)."

    def __init__(self, dc):
        dc.update()
        px = dc.winfo_width()
        py = dc.winfo_height()

        self.margin = 0.02

        self.pix = WinCoor(0, py-1, px-1, 0)
#        self.can = WinCoor(0, py, px, 0)
        self.wor = WinCoor(0, 0, px-1, py-1)

    def onSize(self, dc, zoom, regen):
        dc.update()
        px = dc.winfo_width()
        py = dc.winfo_height()
        w = self.pix.win
        if px == w[2]+1 and py == w[1]+1: return
        worp = self.wor
        w1 = self.wor.coor(self.pix, (0, py-1))
        w2 = self.wor.coor(self.pix, (px-1, 0))
        self.pix = WinCoor(0, py-1, px-1, 0)
        self.wor = WinCoor(w1[0], w1[1], w2[0], w2[1])
        if zoom: self.zoomwin(worp, dc, regen)

#=============================================================================

    def zoomwin(self, worn, dc, regen):
        "Redraws the curves into canvas dc."

        worn = WinCoor(worn)
        worn.reratio(self.pix)
        worn.resize(self.margin, self.margin)
        wcen = worn.middle()
        wce = self.wor.middle()
        dx, dy = self.pix.rcoor(self.wor, (wcen[0]-wce[0], wcen[1]-wce[1]))
        dc.move(ALL, -dx, -dy)
        wcen = self.pix.coor(self.wor, wcen)
        wcen = wcen[0]-dx, wcen[1]-dy

        w = self.wor.win; dx,  dy  = w[2]-w[0], w[3]-w[1]
        w = worn.win;     dxn, dyn = w[2]-w[0], w[3]-w[1]
        if dx > dy: sc = dx/dxn
        else:       sc = dy/dyn
        dc.scale(ALL, wcen[0], wcen[1], sc, sc)

        self.wor = worn
        if regen: self.thanRegen()

#=============================================================================

    def zoompix(self, ce, fact, dc, regen, center1):
        "Zooms with center at ce; ce is in pixels."

        if center1: ce = self.wor.coor(self.pix, ce)
        else: ce = self.wor.middle()
        w = self.wor.win; dx, dy = (w[2]-w[0])*0.5/fact, (w[3]-w[1])*0.5/fact
        self.zoomwin(WinCoor(ce[0]-dx, ce[1]-dy, ce[0]+dx, ce[1]+dy), dc, regen)

#=============================================================================

    def transeq(self):
        "Returns the coefs of the transformation equations world->canvas (which coincides with pixel."

        ww = self.wor.win; dx,  dy  = ww[2]-ww[0], ww[3]-ww[1]
        pw = self.pix.win; dxp, dyp = pw[2]-pw[0], pw[3]-pw[1]
        xsc = dxp/dx
        ysc = dyp/dy

#        x = pw[0] + (x-ww[0])*sc
        dx = pw[0] - ww[0]*xsc
        dy = pw[1] - ww[1]*ysc
        return dx, dy, xsc, ysc


##############################################################################
##############################################################################

class ChartWinx:
    "Base chart window."

    def thanInit(self, toplevel, thanZoomPanCoor, thanOptions, chart, title, *args, **kw):
        "Common initialization of chart windows."
        bg = kw.pop("bg")
        width  = kw.pop("width", 320)
        height = kw.pop("height", 240)
        toplevel.__init__(self, *args, **kw)
#        self.geometry("%dx%d%" % (width, height))
        thanOptions.__init__(self, "p_gchart")

        self.thanState = STATE_NONE
        self.__chart = chart

        self.title(title)
        self.thanCanvas = Canvas(self, bg=bg, width=width, height=height)
        self.thanCur = self.thanCanvas["cursor"]
        self.thanCanvas.grid(row=1, sticky="snwe")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.thanCanvas.bind("<Button-3>", self.__onClickr)
        self.thanCanvas.bind("<Button-1>", self.__onClick)
        self.bind("<Escape>", self.__onEscape)
        thanZoomPanCoor.__init__(self, self.thanCanvas)

        self.thanFloatMenu = self.__createFloatMenu()
        self.thanMenubar = self.__createMenubar()
        self.showMenubar.trace("w", self.__showMenubar)
        self.__showMenubar()
        self.thanToolbar = self.__createToolbar()
        self.showToolbar.trace("w", self.__showToolbar)
        self.__showToolbar()

        self.__chart.minmax()
        self.__zoomall()
        if not self.regenWhenZoomall.get(): self.thanRegen()
        self.bind("<Configure>", self.__onSize)

        self.thanImundo = []
        self.thanImredo = []
        self.thanResetModified()
        self.thanFileDefined = False
        self.protocol("WM_DELETE_WINDOW", self.thanMnuFileExit)


    def __createFloatMenu(self):
        m = Menu(self, tearoff=False)

        m1 = Menu(m, tearoff=False)
        m1.add_command(label="Rotate  90 deg", command=lambda f=90.0:  self.__rot(f))
        m1.add_command(label="Rotate 180 deg", command=lambda f=180.0: self.__rot(f))
        m1.add_command(label="Rotate 270 deg", command=lambda f=270.0: self.__rot(f))
#        m1.add_command(lable="Rotate arbitrary", command=lambda f=90.0: self.__rot(f))
        m1.add_separator()
        m1.add_command(label="convert to b/w", command=lambda c="2": self.__convert(c))
        m1.add_command(label="convert to b/w inverted", command=lambda c="3": self.__convert(c))
        m1.add_separator()
        m1.add_command(label="Undo", command=self.__undo)
        m1.add_command(label="Redo", command=self.__redo)
        m1.add_separator()
        m1.add_command(label="Open", command=self.thanMnuFileOpen)
        m1.add_command(label="Save", command=self.thanMnuFileSave)
        m1.add_command(label="Save As", command=self.thanMnuFileSaveas)
        m.add_cascade(label="image", menu=m1)

        m.add_command(label="zoom in",  command=self.__zoomin)
        m.add_command(label="zoom out", command=self.__zoomout)
        m.add_command(label="zoom all", command=self.__zoomall)
        m.add_separator()
        m.add_command(label="center to", command=self.__centerto)
        m.add_separator()
        m.add_command(label="regen", command=self.thanRegen)
        m.add_command(label="cancel", command=self.__cancel)
        m.add_separator()

        m1 = Menu(m, tearoff=False)
        m1.add_checkbutton(label="zoom  when window changes", variable=self.zoomWhenConf)
        m1.add_checkbutton(label="regen when window changes", variable=self.regenWhenConf)
        m1.add_separator()
        m1.add_checkbutton(label="regen when zoom", variable=self.regenWhenZoom)
        m1.add_checkbutton(label="regen when zoom all", variable=self.regenWhenZoomall)
        m1.add_checkbutton(label="center when zoom", variable=self.centerWhenZoom)
        m1.add_separator()
        m1.add_checkbutton(label="show menu bar", variable=self.showMenubar)
        m1.add_checkbutton(label="show tool bar", variable=self.showToolbar)

        m.add_cascade(label="options", menu=m1)

        m1 = Menu(m, tearoff=False)
        m1.add_command(label="save current options as defaults", command=self.thanOptSave)
        m1.add_separator()
        m1.add_command(label="reload saved   default options", command=self.thanOptGet)
        m1.add_command(label="reload factory default options", command=self.thanOptFactory)

        m.add_cascade(label="defaults", menu=m1)
        return m

    def __createMenubar(self):
        m = Menu(self, tearoff=False)

        m1 = Menu(m, tearoff=False)
        m1.add_command(label="Exit",  command=self.thanMnuFileExit)
        m.add_cascade(label="File", menu=m1)

        m1 = Menu(m, tearoff=False)
        m1.add_command(label="zoom in",  command=self.__zoomin)
        m1.add_command(label="zoom out", command=self.__zoomout)
        m1.add_command(label="zoom all", command=self.__zoomall)
        m1.add_separator()
        m1.add_command(label="center to", command=self.__centerto)
        m1.add_separator()
        m1.add_command(label="regen", command=self.thanRegen)
        m1.add_command(label="cancel", command=self.__cancel)
        m.add_cascade(label="View", menu=m1)

        m1 = Menu(m, tearoff=False)
        m1.add_checkbutton(label="zoom  when window changes", variable=self.zoomWhenConf)
        m1.add_checkbutton(label="regen when window changes", variable=self.regenWhenConf)
        m1.add_separator()
        m1.add_checkbutton(label="regen when zoom", variable=self.regenWhenZoom)
        m1.add_checkbutton(label="regen when zoom all", variable=self.regenWhenZoomall)
        m1.add_checkbutton(label="center when zoom", variable=self.centerWhenZoom)
        m1.add_separator()
        m1.add_checkbutton(label="show menu bar", variable=self.showMenubar)
        m1.add_checkbutton(label="show tool bar", variable=self.showToolbar)
        m.add_cascade(label="Options", menu=m1)

        m1 = Menu(m, tearoff=False)
        m1.add_command(label="save current options as defaults", command=self.thanOptSave)
        m1.add_separator()
        m1.add_command(label="reload saved   default options", command=self.thanOptGet)
        m1.add_command(label="reload factory default options", command=self.thanOptFactory)
        m.add_cascade(label="Defaults", menu=m1)

        return m

    def __createToolbar(self):
        t = Frame(self, relief=GROOVE, bd=2)
        buttons = \
        ( ("zoomin",  self.__zoomin),
          ("zoomout", self.__zoomout),
          ("zoomall", self.__zoomall),
          ("move",    self.__centerto),
          ("regen",   self.thanRegen),
          ("cancel",  self.__cancel),
        )
        c = 0
        for icon, callback in buttons:
#            iconfun = getattr(thanicon, icon)
#            ph = PhotoImage(data=iconfun())
#            setattr(t, icon, ph)                         # Save a reference of the icon
            but = Button(t, image=thanicon.get(icon), command=callback)
            but.grid(row=0, column=c)
            c += 1

        t.grid(row=0, sticky="wn")
        t.grid_forget()
        return t

    def __onSize(self, evt):
        self.onSize(self.thanCanvas, self.zoomWhenConf.get(), self.regenWhenConf.get() or self.regenWhenZoom.get())

    def __showMenubar(self, *args):
        if self.showMenubar.get(): self["menu"] = self.thanMenubar
        else: self["menu"] = Menu(self)

    def __showToolbar(self, *args):
        if self.showToolbar.get(): self.thanToolbar.grid(row=0, sticky="wn")
        else: self.thanToolbar.grid_forget()

#============================================================================

    def __onClickr(self, event):
        "Well, here is what should be done when right mouse clicks."

        self.thanFloatMenu.post(event.x_root, event.y_root)

    def __onEscape(self, event):
        "Well, here is what should be done when user presses escape."

        if self.thanFloatMenu.winfo_ismapped():
            self.thanFloatMenu.unpost()
        else:
            self.__cancel()

#============================================================================

    def __onClick(self, event):
        "Well, here is what should be done when right mouse clicks."

#-------Initial values

        if self.thanState == STATE_NONE: return
        elif self.thanState == STATE_ZOOMIN:
            self.zoompix((event.x, event.y), self.zoomFact, self.thanCanvas, self.regenWhenZoom.get(), self.centerWhenZoom.get())
        elif self.thanState == STATE_ZOOMOUT:
            self.zoompix((event.x, event.y), 1.0/self.zoomFact, self.thanCanvas, self.regenWhenZoom.get(), self.centerWhenZoom.get())
        elif self.thanState == STATE_CENTER:
            self.zoompix((event.x, event.y), 1.0+self.margin, self.thanCanvas, False, True)

#============================================================================

    def __zoomin(self):
        self.thanCanvas.config(cursor="circle")
        self.thanState = STATE_ZOOMIN
    def __zoomout(self):
        self.thanCanvas.config(cursor="dot")
        self.thanState = STATE_ZOOMOUT
    def __zoomall(self):
        c = self.__chart
        self.zoomwin(WinCoor(c.xmin, c.ymin, c.xmax, c.ymax), self.thanCanvas, self.regenWhenZoom.get() or self.regenWhenZoomall.get())
    def __centerto(self):
        self.thanCanvas.config(cursor="hand1")
        self.thanState = STATE_CENTER
    def __cancel(self):
        self.thanCanvas.config(cursor=self.thanCur)
        self.thanState = STATE_NONE
    def thanRegen(self):
        dx, dy, xsc, ysc = self.transeq()
        self.__chart.regen(self.thanCanvas, dx, dy, xsc, ysc)
    def __rot(self, f):
        "Rotates f degrees all images in the chart."
        self.__chart.thanRot(f)
        self.thanImundo.append((self.__chart.thanRot, (-f,), self.__chart.thanRot, (f,)))
        self.thanImredo = []
        self.thanRegen()
        self.thanSetModified()
    def __convert(self, c):
        "Rotates f degrees all images in the chart."
        self.__chart.thanConv(c)
        self.thanImundo = []
        self.thanImredo = []
        self.thanRegen()
        self.thanSetModified()
    def __undo(self):
        "Undoes previous alteration."
        if len(self.thanImundo) <= 0: return
        unfun, unargs, refun, reargs = self.thanImundo.pop()
        unfun(*unargs)
        self.thanImredo.append((unfun, unargs, refun, reargs))
        self.thanRegen()
    def __redo(self):
        "Redoes previous undo alteration."
        if len(self.thanImredo) <= 0: return
        unfun, unargs, refun, reargs = self.thanImredo.pop()
        refun(*reargs)
        self.thanImundo.append((unfun, unargs, refun, reargs))
        self.thanRegen()

    def thanMnuFileOpen(self, evt=None):
        "Opens an existing file and corresponding window."
        while True:
            if self.thanMnuFileClose() == "break": return "break"
            filnam, fr = thanGudOpenReadFile(self, "*", "Open image file", mode="rb")
            if filnam.strip() == "": return
            try:
                print("Image=", Image)
                im = Imagepil.open(fr)
            except IOError as why:
                thanGudModalMessage(self, why, "Image file open failed")   # (Gu)i (d)ependent
                continue
            break
        self.thanFilnam = filnam
        self.thanFileDefined = True
        self.thanResetModified()
        self.thanFocus()
        self.__chart.imageAdd(im, 0.0, 0.0, 100.0)
        self.thanRegen()

    def thanMnuFileClose(self, evt=None):
        if self.thanIsModified():
            a = thanGudAskOkCancel(self, T["File modified. Ok to quit?"], T["FILE MODIFIED"])
            if not a: self.thanFocus(); return "break"
        from . import chart
        self.__chart = chart.ThanChart()
        self.thanResetModified()

    def thanMnuFileSave(self, evt=None):
        if not self.thanFileDefined: return self.thanMnuFileSaveas()
        im = self.__chart.thanGetImage()
        if im is None: return
        try: im.save(self.thanFilnam)
        except IOError as why: thanGudModalMessage(self, why, T["Error opening file"])
        else:
            self.thanFileDefined = 1
            self.thanResetModified()
        self.thanFocus()

    def thanMnuFileSaveas(self, evt=None):
        im = self.__chart.thanGetImage()
        if im is None: return
        filnam = thanGudGetSaveFile(self, "*", "Saves to a File")
        if filnam.strip() == "": return
        try: im.save(filnam)
        except IOError as why: thanGudModalMessage(self, why, T["Error opening file"])
        else:
            self.thanFilnam = filnam
            self.thanFileDefined = 1
            self.thanResetModified()
        self.thanFocus()

    def thanMnuFileExit(self, evt=None):
        if self.thanMnuFileClose() == "break": return "break"
        self.destroy()

    def thanResetModified(self): self.__modified = False
    def thanSetModified(self): self.__modified = True
    def thanIsModified(self): return self.__modified
    def thanFocus(self): self.focus_set()

    def thanSaveasPostscript(self, psfile, width=None, height=None):   #Thanasis2024_09_14
        "Plot the chart as postscript, and write the postscript to file fn."
        self.thanCanvas.postscript(file=psfile, width=width, height=height)

    def thanSaveasImage(self, imfile, width=None, height=None, bg="black"):   #Thanasis2024_09_16
        "Plot the chart as PIL image."
        im = can2im(self.thanCanvas, bg=bg, width=width, height=height)
        im.save(imfile)


class ChartWin1(Toplevel, ThanZoomPanCoor, ThanOptions, ChartWinx):
    "Secondary chart window."

    def __init__(self, chart, title, *args, **kw):
        "Initialise as Toplevel."
        self.thanInit(Toplevel, ThanZoomPanCoor, ThanOptions, chart, title, *args, **kw)

    def thanWait(self):     #Thanasis2024_09_14
        "Wait until the chart window is closed."
        self.wait_window()


class ChartWin(Tk, ThanZoomPanCoor, ThanOptions, ChartWinx):
    "Main chart window."

    def __init__(self, chart, title, *args, **kw):
        "Initialise as Tk."
        self.thanInit(Tk, ThanZoomPanCoor, ThanOptions, chart, title, *args, **kw)

    def thanWait(self):     #Thanasis2024_09_14
        "Wait until the chart window is closed."
        self.mainloop()


class ChartDxf(dxfinter.Tk, ThanZoomPanCoor):
    def __init__(self, chart, title, *args, **kw):
        c = self.__chart = chart
        c.minmax()
        self.pix = WinCoor(0.0, 0.0, 19.0, 29.0)
        self.wor = WinCoor(c.xmin, c.ymin, c.xmax, c.ymax)
        self.wor.reratio(self.pix)
        dxfinter.Tk.__init__(self)
        self.thanCanvas = dxfinter.Canvas(self, "white")
        self.thanRegen()
    def thanRegen(self):
        dx, dy, xsc, ysc = self.transeq()
        self.__chart.regen(self.thanCanvas, dx, dy, xsc, ysc)
    def transeq(self):
        "Returns the coefs of the transformation equations world->canvas (which coincides with pixel."
        ww = self.wor.win; dx,  dy  = ww[2]-ww[0], ww[3]-ww[1]
        pw = self.pix.win; dxp, dyp = pw[2]-pw[0], pw[3]-pw[1]
        xsc = dxp/dx
        ysc = dyp/dy

#        x = pw[0] + (x-ww[0])*sc
        dx = pw[0] - ww[0]*xsc
        dy = pw[1] - ww[1]*ysc
        return dx, dy, xsc, ysc


class ChartPil(pilinter.Tk, ThanZoomPanCoor):
    def __init__(self, chart, title, *args, **kw):
        c = self.__chart = chart
        self.pix = WinCoor(0.0, 0.0, 600, 400)
        self.wor = WinCoor(c.xmin, c.ymin, c.xmax, c.ymax)
        self.wor.reratio(self.pix)
        pilinter.Tk.__init__(self, 600, 400)
        self.thanCanvas = pilinter.Canvas(self, "white")
        self.thanRegen()
    thanRegen = ChartDxf.thanRegen
    transeq   = ChartDxf.transeq

#############################################################################
#############################################################################

def vis(*charts, wait=True, **kw):
    bg = kw.pop("bg", "black")
    root = ChartWin(charts[0], thanUnicode(charts[0].title+" (Main)"), bg=bg, **kw)
    wins = [root]
    if not wait: root.update()
    for ch in charts[1:]:
        c = ChartWin1(ch, thanUnicode(ch.title), root, bg=bg, **kw)
        if not wait: c.update()
        wins.append(c)           #Thanasis2024_09_14
    if wait: root.thanWait()     #Thanasis2024_09_14
    return wins

def viswin(root, *charts, wait=True, **kw):
    "The caller has already started tk."
    bg = kw.pop("bg", "black")
    wins = []
    for ch in charts:
        c = ChartWin1(ch, thanUnicode(ch.title), root, bg=bg, **kw)
        if not wait: c.update()
        wins.append(c)       #Thanasis2024_09_14
    if wait: c.thanWait()    #Thanasis2024_09_14
    return wins

def visfil(*charts, **kw):
    "The caller may already started tk with library p_gfil, or not."
    winmain, _, _ = p_gfil.openfileWinget()
    if winmain is not None:
        return viswin(winmain, *charts, **kw)
    else:
        return vis(*charts, **kw)


def visdxf(*charts):
    root = ChartDxf(charts[0], charts[0].title+" (Main)")
#    for ch in charts[1:]:
#        c = ChartWin1(ch, "Chart", root)
    root.mainloop()
def vispil(*charts, **kw):
    bg = kw.pop("bg", "black")
    root = ChartPil(charts[0], "Main Chart", bg=bg)
#    for ch in charts[1:]:
#        c = ChartWin1(ch, "Chart", root)
    root.mainloop()

STATE_NONE = 0
STATE_ZOOMIN = 1
STATE_ZOOMOUT = 2
STATE_CENTER = 3

if __name__ == "__main__":
    from . import chart
    im = Imagepil.new("L", (100, 100))
    ch = chart.ThanChart()
    ch.imageAdd(im, 0.0, 0.0, 100.0)
    del im
    root = ChartWin(ch, "Main Chart", bg="yellow")
    root.mainloop()
