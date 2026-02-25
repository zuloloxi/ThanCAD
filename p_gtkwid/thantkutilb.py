from math import sqrt
import weakref
import tkinter, tkinter.font

__grabWins = []    #Global list for assisting thanGrabSet(), thanGrabRelease
__fonts = weakref.WeakKeyDictionary()   #global dict to assist thanFontRefSave()


def thanFontGet(wid):
    "Returns the font of Tkinter widget wid as a Font object."
    t = wid.cget("font")
    if t.strip() == "": return None
    font1 = thanText2Font(t)
    return font1


def thanText2Font(t):
    'Creates a Tkinter Font object from a string (returned from widget.cget("font")).'
    t = t.split()
    kw = {}
    for t1 in t:
        try: n = int(t1)
        except ValueError: pass
        else: __set(kw, "size", n); continue
        if t1 == tkinter.font.NORMAL:
            __set(kw, "weight", tkinter.font.NORMAL)
        elif t1 == tkinter.font.BOLD:
            __set(kw, "weight", tkinter.font.BOLD)
        elif t1 == tkinter.font.ROMAN:
            __set(kw, "slant", tkinter.font.ROMAN)
        elif t1 == tkinter.font.ITALIC:
            __set(kw, "slant", tkinter.font.ITALIC)
        elif t1 == "overstrike":
            __set(kw, "overstrike", True)
        else:
            __set(kw, "family", t1)
#    for key,val in kw.iteritems(): print key,val
    return tkinter.font.Font(**kw)


def __set(kw, key, val):
    "Sets the key/val in dictionary kw, if it is not already there."
    if key in kw:
        print("Option", key, "is already set to", kw[key])
        print("Option", key, "value", val, "is ignored")
        return
    kw[key] = val


#=============================================================================

def thanFontRefSave(obj, font):
    """Saves a reference of Tkinter Font, so that the font stays alive.

    When you define a Tkinter font for a Tkinter widget, the widget does not keep a reference to
    the font. Thus when the routine which created the widget goes out of scope, its local
    reference of font is destroyed, and with it, the font is destroyed.
    This routine keeps a strong reference to the font. The font lives forever, unless:
    1. the widget is destroyed
    2. Another font is defined for the widget.
    The variable font may actually be anything, such as tuple of fonts, a list of fonts,
    an image etc.
    WE SHOULD NOT SAVE A FONT IF obj is the root window, i.e. Tk(). Because when Tk()
    dies the font (if it is alive) is in illegal state. The font can be handled only if
    Tk() is active. 
    """
    __fonts[obj] = font


def thanFontRefGet(obj):
    "Returns the font saved for the object obj."
    return __fonts.get(obj)   #returns None if obj is not found

#=============================================================================

def thanGrabSet(win):
    "Perform a nested grab_set."
    if len(__grabWins) > 0:
        win1 = __grabWins[-1]
        win1().grab_release()
        win1().protocol("WM_DELETE_WINDOW", lambda: "break")
    win.update()
    win.grab_set()
    win1 = weakref.ref(win, __grabWinDied)
    __grabWins.append(win1)


def __grabWinDied(weakwin):
    "This is called when the window which has the grab dies."
    assert len(__grabWins) > 0 and __grabWins[-1] == weakwin, "How did this happen?"
    del __grabWins[-1]
    if len(__grabWins) <= 0: return
    win1 = __grabWins[-1]
    win1().protocol("WM_DELETE_WINDOW", win1().cancel)
    win1().lift()
    win1().focus_set()
    win1().grab_set()


def thanGrabRelease():
    "This is called when the window which has the grab dies."
    assert len(__grabWins) > 0, "How did this happen?"
    weakwin = __grabWins.pop()
    weakwin().grab_release()
    if len(__grabWins) <= 0: return
    win1 = __grabWins[-1]
    win1().protocol("WM_DELETE_WINDOW", win1().cancel)
    win1().lift()
    win1().focus_set()
    win1().grab_set()


def thanRobustDim(self=None):
    """Returns the dimensions of a toplevel window and screen in pixels and in mm.

    If it is not a toplevel widget, the toplevel widget is found.
    If Tkinter answers wrong values, it is assumed that the monitor is
    19 inches, the ratio of height/width is assumed 0.75 and the resolution
    1024 x 768.
    """
    MON = 19.0; RATIO = 0.75; RESOL = (1024, 768)
    if self is None:
        try: self = tkinter._default_root
        except: import Tkinter; self = Tkinter._default_root   #Ease the trasition to python3
    else:
        self.update_idletasks()              # _idletasks breaks WinDoze (98?) support. Skotistika
        self = self.winfo_toplevel()
    self.update_idletasks()                  # _idletasks breaks WinDoze (98?) support. Skotistika
    width  = self.winfo_screenwidth()        # Pixels
    height = self.winfo_screenheight()       # Pixels
    widthmm  = float(self.winfo_screenmmwidth())   # mm
    heightmm = float(self.winfo_screenmmheight())  # mm

    if widthmm < 2.0:
#        thanLogTk.warning("TkCoor:robustDim: Tkinter reported illegal screen dimensions: %fmm x %fmm", widthmm, heightmm)
        if heightmm < 2.0:
            widthmm = MON*25.4 / sqrt(1+RATIO**2)
            heightmm = widthmm * RATIO
        else:
            widthmm = heightmm / RATIO
    elif heightmm < 2.0:
#        thanLogTk.warning("robustDim: Tkinter reported illegal screen dimensions: %fmm x %fmm", widthmm, heightmm)
        heightmm = widthmm * RATIO

    if width < 2:
#        thanLogTk.warning("robustDim: Tkinter reported illegal screen dimensions: %dpix x %dpix", width, height)
        if height < 2:
            width, height = RESOL
        else:
            width = int(height / RATIO)
    elif height < 2:
#        thanLogTk.warning("robustDim: Tkinter reported illegal screen dimensions: %dpix x %dpix", width, height)
        height = int(width * RATIO)

    return width, height, widthmm, heightmm


#=============================================================================

def __testGrab():
    from .thantksimpledialog import ThanDialog
    class ThanD1(ThanDialog):
        def body(self, fra):
            b=tkinter.Button(fra, text="fork", command=self.fork)
            b.grid()
            b=tkinter.Button(fra, text="do1", command=self.do1)
            b.grid()
        def do1(self):
            print("do1")
        def fork(self):
            return ThanD1(self)

    class ThanD2(ThanDialog):
        def body(self, fra):
            b=tkinter.Button(fra, text="do2", command=self.do2)
            b.grid()
        def do2(self):
            print("do2")

    root.update()
    def do(): print("do")
    b=tkinter.Button(root, text="do", command=do)
    b.grid()
    print("d1=", ThanD1(root))


def __testText2Font():
    "A test for thanText2Font."
    f = thanText2Font("Courier -12")
    print()
    print(f)
    print()
    f.config(size=14)
    print(f)
    print("size=", f.cget("size"))
    print()
    wid = tkinter.Text(root)
    wid.grid()
    print("text font:", thanFontGet(wid))
    wid = tkinter.Entry(root)
    wid.grid()
    print("entry font:", thanFontGet(wid))


if __name__ == "__main__": 
    root = tkinter.Tk()
    __testText2Font()
    __testGrab()
