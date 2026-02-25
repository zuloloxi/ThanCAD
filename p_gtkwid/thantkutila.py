import sys, os
import tkinter, tkinter.font, tkinter.ttk
from tkinter import TclError, messagebox
from tkinter.messagebox import ERROR, INFO, QUESTION, WARNING
from p_ggen import floate, isString, thanUnunicode, thanUnicode, path, Pyos
import p_gcol
if Pyos.Python3: from tkinter import filedialog
else:            import tkFileDialog as filedialog

__fontdef = None     #Default font, with different size


#============================================================================

def thanGetDefaultFont(**kw):
    global __fontdef
    if __fontdef is None:
        __fontdef = tkinter.font.Font(name="TkDefaultFont", exists=True).copy()  #Default font with different size
        __fontdef.config(size=16)
    if kw: __fontdef(**kw)
    return __fontdef


def thanSetFontsSize(s=14):
    "Set the size of default fonts."
    for t in "TkDefaultFont", "TkFixedFont", "TkMenuFont", "TkCaptionFont", "TkTextFont":
        font1 = tkinter.font.Font(name=t, exists=True)
        font1.config(size=s)   # Negative size means size in pixels
    #font1.config(family="Arial")


def correctDialogColor(master, font1):
    "Return a Frame fra and Font font1 for the standard Tk file dialog; fra MUST BE DESTROYED JUST AFTER USE."
    fra = tkinter.Frame(master)    #A widget that will take the option_add(), so that we do not alter master
    if font1 is None: font1 = thanGetDefaultFont()
    #bgcol = fra.cget("bg")
    #print("bgcol=", bgcol)
    fgcol = "darkblue"
    bgcol = "lightyellow"
    fra.option_add('*foreground', fgcol)        # set all tk widgets' foreground to col: changes color of file list
    fra.option_add('*activeForeground', fgcol)  # set all tk widgets' foreground to col: changes color of file list
    fra.option_add('*background', bgcol)  # set all tk widgets': changes all, except file list
    fra.option_add('*font', font1)  # set all tk widgets' font to font1:  changes all, except file list, menubutton and button

    style = tkinter.ttk.Style(fra)
    style.configure('TLabel',      foreground='black')
    style.configure('TEntry',      foreground=fgcol)
    style.configure('TMenubutton', foreground=fgcol, font=font1)
    style.configure('TButton',     foreground="black", font=font1)
    return fra


def thanGudGetReadFile(self, ext, tit, initialfile="", initialdir="", multiple=False, font=None):
    "Gets a filename that exists, from user."
    ext1 = thanExtExpand(ext)
    #defext = ext[0][1][1:]    # For Windows?
    defext = ext1[0][1]
    if ext is None: defext = None   #Thanasis2017_04_20:Otherwise .Open does not select files with no extension
    if not Pyos.Windows: fra = correctDialogColor(self, font)   #Thanasis2021_09_26
    while True:
        opendialog = filedialog.Open(parent=self, initialfile=initialfile,  #Thanasis2021_09_26: fra is now the parent
          initialdir=initialdir, defaultextension=defext, multiple=multiple,
          title=thanUnicode(tit), filetypes=ext1)  #Here defaultextension works ok: When the users types something
        #                           #It gets the extension specified as the first element of ext
        try:
            filnam = opendialog.show()
        except TclError as why:
            w = str(why)
            if "invalid" in w and "filename" in w: #If the initialfile is invalid then..
                initialfile = ""                   #..work around tcl/tk bug
                continue
            raise                                  #Something else happened; raise error
        break
    if not Pyos.Windows: fra.destroy()    #Thanasis2021_09_26
    if multiple:
        #print("thangudgetreadfile: multiple=", multiple, ":", filnam)
        #print("thangudgetreadfile: type(filnam)=", type(filnam))
        if not filnam: return None
        try: filnam+"x"     #Work around Windows bug: Yeah, Windows "just" works!!
        except: pass
        else: return __winfiles(filnam)
        return [thanAbsrelPath(f1) for f1 in filnam]
    return thanAbsrelPath(filnam)

import re
_splitter = re.compile(r"""{[^}]+}|[^ ]+""")
def __winfiles(filnam):
    """If files have blanks in their names they are surrounded by {}. Example below.

    "   thanasis stamos dimitra {stella  ss} andreas {stella stamoy}   "
    """
    dl = _splitter.findall(filnam)
    for i,f1 in enumerate(dl):
        if f1[0] == "{" and f1[-1] ==  "}": f1 = f1[1:-1]
        dl[i] = thanAbsrelPath(f1)
    return dl

#============================================================================

def thanAbsrelPath(f, cdir=None):
    "Returns the absolute path of f, or, if f is in current dir, the relative path to f."
    if not f: return None
    f = thanUnunicode(f)
    if cdir is None: cdir = os.getcwd()
    cdir = os.path.abspath(cdir)
    f = thanUnunicode(os.path.abspath(f))
    if os.path.commonprefix((cdir, f)) == cdir:
        n = len(cdir)
        if f[n:n+1] in "/\\": n += 1    #skip "/" or "\"   #thanasis2018_10_25
        f = f[n:]
        if f == "": f = cdir    #Otherwise blank in shown   #Thanasis2022_11_19
    return path(f)

#============================================================================

def thanExtExpand(ext):
    """Extension ext can be one of the following:

    string with no blanks: the string contains one extension and it is transformed to:
        [ (<NULL explanation>, string),
          ("All files", "*"),
        ]
    string with blanks: the string contains multiple extensions separated by
        blanks, and it is transformed to:
        [ (<NULL explanation>, ext1),
          (<NULL explanation>, ext2),
          (<NULL explanation>, ext3),
          ...
          ("All files", "*"),
        ]
    tuple of strings: The first string of the tuple is the explanation and the other
        string is the extension. It is transformed to:
        [ tuple,
          ("All files", "*"),
        ]
    list of tuples: Each tuple is a tuple of strings. The first string of the tuple is
         the explanation and the other string is the extension. No transformation.
    thanasis2011_09_25: It seems than (at least in Linux) if the extension is
    something like "xx.asc" the the open dialog does not consider it as an
    extension. In this case it should begin with *, like: "*xx.asc"
    """
#   Windoze 7 open file dialog: how does Windows7 show multiple extensions:
#   1. If ext is a list of tuples and each tuple contains a description text
#      and an extension, the  Windows7 show the first tuple (and relevant files)
#      when opening the dialog. The user may choose another tuple.
#   2. If in some (or all) tuples the description is "":
#      a. If all tuples which contain nonblank descriptions are first (before
#         the blank descriptions) in the list of tuples, then all blank tuples
#         are shown and all the files whose extension is one of the blank tuples.
#         The user may choose one of the nonblank tuples.
#      b. If the blank tuples are first (before the non blank tuples) then
#         the last of the non blank tuples is shown. The user may choose another
#         nonblank tuple or all blank tuples.
#      c. 2022_06_13: In the file explorer go to view -> options -> view tab ->
#         -> untick "hide extensions for for known file types"
#         Now Windoze shows all the blank description extensions as one entry
#         just like linux.
#         The entry "all files", must be appended at the end of the list.
#    Linux openfile dialog:
#    1. Linux always shows the first entry either blank or nonblank tuple.
#    2. All the blank tuples are shown as one entry.
    if ext is None:
        exts = [("All files", "*")]
    elif isString(ext):
        if ext.strip() == "":
            exts = [("All files", "*")]
        elif " " in ext.strip():
            exts = []
            for exta in ext.split():
                if exta[0] not in ".*": exta = "*" + exta  #in case extension is like xx.asc
                exts.append(("", exta))
            #if Pyos.Windows: exts.insert(0, ("All files", "*"))  #Thanasis2022_06_13: commented out
            #else:            exts.append(("All files", "*"))     #Thanasis2022_06_13: commented out
            exts.append(("All files", "*"))     #Thanasis2022_06_13: see explaneation above (c.)
        else:
            desc, exta = "", ext
            if exta[0] not in "*.": exta = "*" + exta   #in case extension is like xx.asc
            exts = [(desc, exta), ("All files", "*")]
    elif isString(ext[0]):
        desc, exta = ext
        if exta.strip() == "":
            exts = [(desc, "*")]
        else:
            if exta[0] not in ".*": exta = "*" + exta   #in case extension is like xx.asc
            exts = [(desc, exta), ("All files", "*")]
    else:
        exts = []
        for desc, exta in ext:
            if exta[0] not in ".*": exta = "*" + exta   #in case extension is like xx.asc
            exts.append((desc, exta))
    return exts
#    return [(thanUnicode(desc), thanUnicode(exta)) for desc, exta in exts]


def thanGudGetSaveFile(self, ext, tit, initialfile="", initialdir="", font=None):
    "Gets a filename that may exists, from user."
    ext = thanExtExpand(ext)
    kw = {}
    if Pyos.Windows: kw["defaultextension"]=ext[0][1]
    if not Pyos.Windows: fra = correctDialogColor(self, font)  #Thanasis2021_09_26
    while True:
        opendialog = filedialog.SaveAs(parent=self, initialfile=initialfile,  #Thanasis2021_09_26: fra is now the parent
          initialdir=initialdir, title=thanUnicode(tit), filetypes=ext,
          **kw)       #Thanasis2011_08_28:Here defaultextension does not work ok in Linux: When the user types something
        #             #It gets the extension ext[0], even if the user has selected another one with the widget
        try:
            filnam = opendialog.show()
        except TclError as why:
            w = str(why)
            if "invalid" in w:
                if "filename" in w:
                    initialfile = ""
                    continue
            raise
        break
    if not Pyos.Windows: fra.destroy()    #Thanasis2021_09_26
    return thanAbsrelPath(filnam)


def thanGudOpenReadFile(self, ext, tit, mode="r", initialfile="", initialdir="", encoding=None, errors=None):
    "Gets a filename that exists, from user."
    while 1:
        filnam = thanGudGetReadFile(self, ext, tit, initialfile, initialdir)
        if not filnam: return filnam, filnam
        try: fw = open(filnam, mode, encoding=encoding, errors=errors)
        except IOError as why : thanGudModalMessage(self, why, "Error opening file")
        else: return filnam, fw


def thanGudOpenSaveFile(self, ext, tit, mode="w", initialfile="", initialdir="", encoding=None, errors=None):
    "Gets a filename that exists, from user."
    while True:
        filnam = thanGudGetSaveFile(self, ext, tit, initialfile, initialdir)
        if not filnam: return filnam, filnam
        try: fw = open(filnam, mode, encoding=encoding, errors=errors)
        except IOError as why: thanGudModalMessage(self, why, "Error opening file")
        else: return filnam, fw


def thanGudGetDir(self, tit, initialdir="", mustexist=False, font=None):
    "Gets a filename that exists, from user."
    if not Pyos.Windows: fra = correctDialogColor(self, font)  #Thanasis2021_09_26
    opendialog = filedialog.Directory(parent=self,   #Thanasis2021_09_26: fra is now the parent
                 title=thanUnicode(tit), initialdir=initialdir, mustexist=mustexist)
    filnam = opendialog.show()
    if not Pyos.Windows: fra.destroy()    #Thanasis2021_09_26
    return thanAbsrelPath(filnam)

#============================================================================

def thanGudAskOkCancel(self, message, title, default="cancel"):
        "Shows message and returns true if user pressed OK; there is no default answer."
        return messagebox.askokcancel(thanUnicode(title), thanUnicode(message),
            default=default, parent=self)

def thanGudAskYesNo(self, message, title, default="yes"):
        "Shows message and returns true if user pressed OK; there is no default answer; returns boolean True or False."
        return messagebox.askyesno(thanUnicode(title), thanUnicode(message),
            default=default, parent=self)


#icons
#ERROR = "error"
#INFO = "info"
#QUESTION = "question"
#WARNING = "warning"
def thanGudModalMessage(self, message, title, icon=None, **kw):
        "Show a message and wait until user discards it."
        messagebox.showinfo(thanUnicode(title), thanUnicode(message), parent=self, icon=icon, **kw)

#===========================================================================


def thanDeficon(win, iconxbm=None):
    "Decorates the window with an icon stored in filename iconxbm."
#    When the script is run via py2exe or Freeze, sys.path[0] has an additional
#    subdirectory at its end, and thus the its parent must be used.
    if iconxbm is not None:
        if _tryIconbitmap(win, iconxbm): return  #Try in current dir (or in path if iconxbm is a pathname)
        iconxbm = path(iconxbm).basename()
        if _tryIconbitmap(win, path(sys.path[0])/iconxbm): return   #Try in the dir where the program is
        if _tryIconbitmap(win, path(sys.path[0]).parent/iconxbm): return   #py2exe or Freeze: we hope iconxbm was copied by the toexe script:)
    if _tryIconbitmap(win, path(sys.path[0]).parent/"thanapps.dir"/"than05.xbm"): return   #Try standard icon
    if _tryIconbitmap(win, path(sys.path[0]).parent/"than05.xbm"): return  #py2exe or Freeze: we hope than05.xbm was copied by the toexe script:)

def _tryIconbitmap(win, iconxbm):
    "Try to open iconxbm."
    b = "@"+iconxbm
#    print "thanDeficon:", b
    try:
        win.iconbitmap(b)
    except Exception as e:
#        print e
        return False
    else:
        return True


def thanGudPosition(self, master="parent", dx=20, dy=15):
    "Position self with respect to parent window (master='parent'), to another window/widget (master=widget) or top left of the screen (master=None)."
    if master == "parent":             #Try to find parent window
        try:    master = self.master
        except: master = None

    if master is None:                 #With respect to top left of the screen
        x = y = 0
    else:                              #With respect to parent window
        master.update()
        x = master.winfo_rootx()
        y = master.winfo_rooty()
    self.geometry("%+d%+d" % (x+dx, y+dy))


def correctForeground(wid):
    "Correct foreground color of a widget depending on intensity of backgroundcolor: either black or white."
    wid.update_idletasks()
    for act in "active", "":
        fgcol = blackorwhite(wid, act+"background")
        if fgcol is not None:
            wid[act+"foreground"] = fgcol
            #print("correctForeground: fgcol=", fgcol)
    try: wid.config(insertbackground=fgcol)     #Thanasis2024_06_28:Try to change the color of the cursor
    except: pass  #Widget does not have this property

    if fgcol == "black":
        selfg = "white"
        selbg = "gray25"
    else:
        selfg = "black"
        selbg = "gray75"
    try: wid.config(selectforeground=selfg)     #Thanasis2024_06_28:Try to change the selection color
    except: pass  #Widget does not have this property
    try: wid.config(selectbackground=selbg)     #Thanasis2024_06_28:Try to change the selection color
    except: pass  #Widget does not have this property

    wid.update_idletasks()


#def oldblackorwhite(wid, bg="background"):
#    "Return black or white depending on the backgound/activebackground color of widget."
#    wid.update_idletasks()
#    try: bgcol = wid.cget(bg)
#    except: return None     #Widget does not have this property
#    #print("blackorwhite(): bgcol = {}     type={}".format(bgcol, type(bgcol)))
#    try: bgcol = p_gcol.thanTk2Rgb(bgcol)
#    except: return None     #Could not decipher background color
#    #print("blackorwhite(): bgcol = {}     type={}".format(bgcol, type(bgcol)))
#    fgcol = "black"
#    if p_gcol.thanRgb2Gray(bgcol) < 127: fgcol = "white"
#    #print("blackorwhite(): fgcol=", fgcol)
#    return fgcol

def blackorwhite(wid, bg="background"):
    "Return black or white depending on the backgound/activebackground color of widget."
    return blueorcyan(wid, blue="black", cyan="white", bg=bg)


def blueorcyan(wid, blue="blue", cyan="cyan", bg="background"):
    "Return blue or cyan depending on the backgound/activebackground color of widget."
    wid.update_idletasks()
    try: bgcol = wid.cget(bg)
    except: return None     #Widget does not have this property
    #print("blueorcyan(): bgcol = {}     type={}".format(bgcol, type(bgcol)))
    try: bgcol = p_gcol.thanTk2Rgb(bgcol)
    except: return None     #Could not decipher background color
    #print("blueorcyan(): bgcol = {}     type={}".format(bgcol, type(bgcol)))
    fgcol = blue
    if p_gcol.thanRgb2Gray(bgcol) < 127: fgcol = cyan
    #print("blueorcyan(): fgcol=", fgcol)
    return fgcol

#===========================================================================

def thanValidateDouble(parentwin, controls, except_=()):
    """Validates the real values of specified (Entry) controls.

    controls is a sequence of the following format:
            Description           control          min value  max value
        ( ("Manning coefficient", self.thanTxtMan, 0.0000001, 0.1),
          ("slope",               self.thanTxtSlo, 0, 1000),
          ("discharge",           self.thanTxtDis, 0, 100000),
          ("Hydraulic depth",     self.thanTxtDep, 0, 1000)
        )
    except_ is a sequence of controls which should be not validated.
    """
    res = []
    for c in controls:
        desc, control, vmin, vmax = c[:4]
        if control in except_: res.append(None); continue
        v = floate(control.get())
        if v is None or v < vmin or v > vmax:
            thanGudModalMessage(parentwin, "Illegal "+desc, "Bad data")
            control.focus_set()
            return
        res.append(v)
    return res 

#===========================================================================

from tkinter import Tk, Frame
def testmenus2():
    "Tests menus with statusbar."
    import p_gtkwid
    def __op(): print("open")
    def __cl(): print("close")
    def __ii(): print("insert image")
    def __ca(): print("load camera")
    def __re(): print("replace")
    def __hi(): print("history")
    def __ex(): root.destroy()
    def cond(): return True

    root = Tk()
    mm = [ ["menu", "&File", "Open file  menu", "magenta"],
           [__op, "&Open", "Open a file", "cyan"],
           [__cl, "&Close", "Closes current file", "cyan"],
           ["menu", "O&rientation", "Orientation submenu", "blue"],
           [__ii, "&Insert Image", "Asks the user to provide image file.", "cyan"],
           [__ca, "&Load Camera file", "Asks the user to provide camera file.", "cyan"],
           ["endmenu"],
           ["-"],
           [__ex, "E&xit", "Terminate program", "red"],
           ["endmenu"],
           ["menu", "&Edit", "Edit menu", "magenta"],
           [__re, "R&eplace", "Search and replace", "cyan"],
           ["endmenu"],
           ["menu", "&Help", "Help menu", "magenta", "help"],
           [__hi, "Histor&y", "History of menus", "cyan"],
           ["endmenu"],
         ]
    fr = Frame(root, height=200)
    fr.grid()
    sb = p_gtkwid.ThanStatusBar(root)
    sb.grid()
    p_gtkwid.thanTkCreateThanMenus2(root, mm, statcommand=sb.sett, condition=cond)
    root.mainloop()

if __name__ == "__main__":
#    root = Tk()
#    t = ThanScrolledText(root)
#    t.grid()
#    t = "Thanasis\nDimitra\nAndreas\n=love\n"*20
#    thanGudHelpWin(root, t, "well...")
#    t = thanGudGetDir(root, "get dir", "/tmp")
#    print t
#    root.mainloop()
    testmenus2()
