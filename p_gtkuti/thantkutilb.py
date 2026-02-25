import weakref
import tkFont, Tkinter


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
        if t1 == tkFont.NORMAL:
            __set(kw, "weight", tkFont.NORMAL)
        elif t1 == tkFont.BOLD:
            __set(kw, "weight", tkFont.BOLD)
        elif t1 == tkFont.ROMAN:
            __set(kw, "slant", tkFont.ROMAN)
        elif t1 == tkFont.ITALIC:
            __set(kw, "slant", tkFont.ITALIC)
        elif t1 == "overstrike":
            __set(kw, "overstrike", True)
        else:
            __set(kw, "family", t1)
#    for key,val in kw.iteritems(): print key,val
    return tkFont.Font(**kw)


def __set(kw, key, val):
    "Sets the key/val in dictionary kw, if it is not already there."
    if key in kw:
        print "Option", key, "is already set to", kw[key]
        print "Option", key, "value", val, "is ignored"
        return
    kw[key] = val


#=============================================================================

def thanFontRefSave(obj, font):
    """Saves a reference of Tkinter Font, so that the font stays alive.

    When you define a Tkinter font for a Tkinter widget, the widget does not keep a reference to
    the font. Thus when the routine which created the widget goes out of scope, its local
    reference of font is destroyed, and with it, the font is destroyed.
    This routine keeps a strong reference to the font. The font lives forever, unless:
    1. the widget is destroyed 2. Another font is defined for the widget.
    The variable font may actually be anything, such as tuple of fonts, alist of fonts
    an image etc.
    WE SHOULD NOT SAVE A FONT IF obj is the root window, i.e. Tk(). Because when Tk()
    dies the font (if it is alive) is in illegal state. The font can be handled only if
    Tk() is active. 
    """
    global __fonts
    try: __fonts
    except: __fonts = weakref.WeakKeyDictionary()
    __fonts[obj] = font


def thanFontRefGet(obj):
    "Returns the font saved for the object obj."
    global __fonts
    try: return __fonts[obj]
    except: return None

#=============================================================================

__grabWins = []
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

#=============================================================================

def __testGrab():
    from thantksimpledialog import ThanDialog
    class ThanD1(ThanDialog):
      def body(self, fra):
        b=Tkinter.Button(fra, text="fork", command=self.fork)
        b.grid()
        b=Tkinter.Button(fra, text="do1", command=self.do1)
        b.grid()
      def do1(self):
        print "do1"
      def fork(self):
        return ThanD1(self)

    class ThanD2(ThanDialog):
      def body(self, fra):
        b=Tkinter.Button(fra, text="do2", command=self.do2)
        b.grid()
      def do2(self):
        print "do2"

    root.update()
    def do(): print "do"
    b=Tkinter.Button(root, text="do", command=do)
    b.grid()
    print "d1=", ThanD1(root)


def __testText2Font():
    "A test for thanText2Font."
    f = thanText2Font("Courier -12")
    print
    print f
    print
    f.config(size=14)
    print f
    print "size=", f.cget("size")
    print
    wid = Tkinter.Text(root)
    wid.grid()
    print "text font:", thanFontGet(wid)
    wid = Tkinter.Entry(root)
    wid.grid()
    print "entry font:", thanFontGet(wid)


if __name__ == "__main__": 
    root = Tkinter.Tk()
    __testText2Font()
    __testGrab()
