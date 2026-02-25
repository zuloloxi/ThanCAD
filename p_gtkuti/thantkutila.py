import os
from string import replace
from Tkinter import *
from Tkinter import TclError
import tkMessageBox, tkFileDialog, tkFont
from tkMessageBox import ERROR, INFO, QUESTION, WARNING

from p_ggen import floate, isString, thanUnunicode, thanUnicode, path, Pyos
import thantksimpledialog, thanfontresize




def thanTkGuiCreateMenus(self, mlist):
    """Create the menus described in list mlist=thanGetMenus().

    mlist is a list of tuples m with 3 values:
    m[0] = function to call when menu is activated
    m[1] = name of the menu
    m[2] = description of the menu
    m[3] = foreground color
    m[4] = name of Tk object (if == 'help' then it is render at far right)
    If m[0] == None and m[1] == '-' then this is a separator
    If m[0] == None and m[1] <> '-' then a new menu with name
                                    m[1] is to be created.
    """

#---At first do some initialisation

#    self.CreateStatusBar()
    menuBar = Menu(self, activebackground="green")

#---Process mlist

    menu = None
    for m in mlist:

#-------Normal Menu entry
        if len(m) > 3: fg = m[3]
	else         : fg = None

        if m[0] != None:
            menu.add_command(label=thanUnicode(replace(m[1], "&", "")), foreground=fg, 
                             command=m[0])           # Create menu entry

#-------Separator entry

        elif m[1] == "-":
            menu.add_separator()

#-----------New menu: at first add old menu in menubar

        else:
            if menu != None: menuBar.add_cascade(label=thanUnicode(menuDesc), menu=menu)
            menu = Menu(menuBar, activebackground="green", foreground=fg, tearoff=0)
            menuDesc = replace(m[1], "&", "")

    if menu != None: menuBar.add_cascade(label=thanUnicode(menuDesc), menu=menu)
    self.config(menu=menuBar)

def thanTkCreateThanMenus(self, mlist, statcommand=None, condition=None):
    """Create the menus described in list mlist=thanGetMenus().

    mlist is a list of tuples m with 3 values:
    m[0] = function to call when menu is activated
    m[1] = name of the menu
    m[2] = description of the menu
    m[3] = foreground color
    m[4] = Tk name: if name=="help" then it is rendered at far right
    If m[0] == None and m[1] == '-' then this is a separator
    If m[0] == None and m[1] <> '-' then a new menu with name
                                    m[1] is to be created.
    If function condition is set, this function is checked before
    a menu action. If condition() returns False, no action is taken.
    """
    from p_gtkwid import ThanMenu
    menuBar = ThanMenu(self, activebackground="green", statcommand=statcommand, condition=condition)
    submenus = {}
    menu = None
    for m in mlist:
        if len(m) > 3: fg = m[3]
        else         : fg = None
        if m[0] != None:   # Normal Menu entry
            menu.add_command(label=m[1], command=m[0], help=m[2], foreground=fg)   # Create menu entry
        elif m[1] == "-":  # Separator entry
            menu.add_separator()
        else:              # New menu: at first add old menu in menubar
            if menu != None: 
                menuBar.add_cascade(label=menuDesc, menu=menu, help=menuHelp, foreground=fg)
            menuDesc = m[1]
            menuHelp = m[2]
            if len(m) > 4: name = m[4]
            else         : name = None
            menu = ThanMenu(menuBar, name=name, activebackground="green", tearoff=0, statcommand=statcommand, condition=condition)
            submenus[menuDesc.replace("&", "")] = menu

    if menu != None: 
        menuBar.add_cascade(label=menuDesc, menu=menu, help=menuHelp)
    self.config(menu=menuBar)
    return menuBar, submenus


def thanTkCreateThanMenus2(self, mlist, statcommand=None, condition=None):
    """Create the menus described in list mlist=thanGetMenus().

    mlist is a list of tuples m with 3 values:
    m[0] = function to call when menu is activated
    m[1] = name of the menu
    m[2] = description of the menu
    m[3] = foreground color
    m[4] = Tk name: if name=="help" then it is rendered at far right
    If m[0] == "-" then this is a separator
    If m[0] == "menu" then a new menu or submenu with name m[1] is created.
    if m[0] == "endmenu" then the current parent menu is terminated. Each menu
                         or submenu must stop with an "endmenu" entry.
    If function condition is set, this function is checked before
    a menu action. If condition() returns False, no action is taken.
    statcommand is a command which displaye the menu description.
    """
    from p_gtkwid import ThanMenu
    menuBar = ThanMenu(self, activebackground="green", statcommand=statcommand, condition=condition)
    submenus = {}
    i = 0
    while i < len(mlist):
        if mlist[i][0] == "menu":
            i = __menu(mlist, menuBar, i, statcommand, condition, submenus)
        else:
            raise ValueError, "Element %s of mlist should mark the beginning of a menu" % i
        i += 1
    self.config(menu=menuBar)
    return menuBar, submenus

def __menu(mlist, menuBar, i, statcommand, condition, submenus):
    "Create a (sub)menu."
    from p_gtkwid import ThanMenu
    m = mlist[i]
    menuDesc = m[1]
    menuHelp = m[2]
    if len(m) > 3: menuFg = m[3]
    else         : menuFg = None
    if len(m) > 4: name = m[4]
    else         : name = None
    menu = ThanMenu(menuBar, name=name, activebackground="green", tearoff=0, statcommand=statcommand, condition=condition)
    i += 1
    while i<len(mlist):
        m = mlist[i]
        if m[0] == "endmenu":
            break                       # End of menu (or submenu)
        elif m[0] == "-":
            menu.add_separator()        # Create Separator entry
        elif m[0] == "menu":
            i = __menu(mlist, menu, i, statcommand, condition, submenus)  # Create submenu entry
        else:
            if not callable(m[0]):
                raise ValueError, "ThanMenu label: %s\nA callable was expected, but type %s was found: %s" % (m[1], type(m[0]), m[0])
            if len(m) > 3: fg = m[3]    # Create normal menu entry
            else         : fg = None
            menu.add_command(label=m[1], command=m[0], help=m[2], foreground=fg)   # Create normal menu entry
        i += 1
    else:
        i = len(mlist)
    menuBar.add_cascade(label=menuDesc, menu=menu, help=menuHelp, foreground=menuFg)
    submenus[menuDesc.replace("&", "")] = menu
    return i

#============================================================================

def thanGudGetReadFile(self, ext, tit, initialfile="", initialdir="", multiple=False):
    "Gets a filename that exists, from user."
    ext = thanExtExpand(ext)
    while True:
        opendialog = tkFileDialog.Open(parent=self, initialfile=initialfile,
#          initialdir=initialdir, defaultextension=ext[0][1][1:],    # For Windows?
          initialdir=initialdir, defaultextension=ext[0][1], multiple=multiple,
          title=thanUnicode(tit), filetypes=ext)  #Here defaultextension works ok: When the users types somethings
                                     #It gets the extension specfied as the first element of ext
        try:
            filnam = opendialog.show()
        except TclError, why:
            w = str(why)
            if "invalid" in w and "filename" in w: #If the initialfile is invalid then..
                initialfile = ""                   #..work around tcl/tk bug
                continue
            raise                                  #Something else happened; raise error
        break
    if multiple:
#        print "thangudgetreadfile: multiple=", multiple, ":", filnam
#        print "thangudgetreadfile: type(filnam)=", type(filnam)
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
    fs = []
    for i,f1 in enumerate(dl):
        if f1[0] == "{" and f1[-1] ==  "}": f1 = f1[1:-1]
        dl[i] = thanAbsrelPath(f1)
    return dl

#============================================================================

def thanAbsrelPath(f, cdir=None):
    "Returns the absolute path of f, or, if f is in current dir, the relative path to f."
    if not f: return None
    f = thanUnunicode(f)
    if cdir == None: cdir = os.getcwd()
    cdir = os.path.abspath(cdir)
    f = thanUnunicode(os.path.abspath(f))
    if os.path.commonprefix((cdir, f)) == cdir: f = f[len(cdir)+1:]
    return path(f)

#============================================================================

def thanExtExpand(ext):
    """Extension ext can be one of the following:

    string with no blanks: the string contains one extension and it is transformed to:
        [ (<NULL explanation>, string),
          ("All files", "*"),
        ]
    string with blanks: the string contains mulrtiple extensions separated by
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
#    Linux openfile dialog:
#    1. Linux always shows the first entry either blanmk or nonblank tuple.
#    2. All the blank tuples are shown as one entry.
    if ext == None:
        exts = [("All files", "*")]
    elif isString(ext):
        if ext.strip() == "":
            exts = [("All files", "*")]
        elif " " in ext.strip():
            exts = []
            for exta in ext.split():
                if exta[0] not in ".*": exta = "*" + exta
                exts.append(("", exta))
            if Pyos.Windows: exts.insert(0, ("All files", "*"))
            else:            exts.append(("All files", "*"))
        else:
            desc, exta = "", ext
            if exta[0] not in "*.": exta = "*" + exta
            exts = [(desc, exta), ("All files", "*")]
    elif isString(ext[0]):
        desc, exta = ext
        if exta.strip() == "":
            exts = [(desc, "*")]
        else:
            if exta[0] not in ".*": exta = "*" + exta
            exts = [(desc, exta), ("All files", "*")]
    else:
        exts = []
        for desc, exta in ext:
            if exta[0] not in ".*": exta = "*" + exta
            exts.append((desc, exta))
    return exts
#    return [(thanUnicode(desc), thanUnicode(exta)) for desc, exta in exts]


def thanGudGetSaveFile(self, ext, tit, initialfile="", initialdir=""):
    "Gets a filename that may exists, from user."
    ext = thanExtExpand(ext)
    kw = {}
    if Pyos.Windows: kw["defaultextension"]=ext[0][1]
    while True:
        opendialog = tkFileDialog.SaveAs(parent=self, initialfile=initialfile,
          initialdir=initialdir, title=thanUnicode(tit), filetypes=ext,
          **kw)       #Thanasis2011_08_28:Here defaultextension does not work ok in Linux: When the user types something
                      #It gets the extension ext[0], even if the user has selected another one with the widget
        try:
            filnam = opendialog.show()
        except TclError, why:
            w = str(why)
            if "invalid" in w:
                if "filename" in w:
                    initialfile = ""
                    continue
            raise
        break
    return thanAbsrelPath(filnam)


def thanGudOpenReadFile(self, ext, tit, mode="r", initialfile="", initialdir=""):
    "Gets a filename that exists, from user."
    while 1:
        filnam = thanGudGetReadFile(self, ext, tit, initialfile, initialdir)
        if not filnam: return filnam, filnam
        try: fw = file(filnam, mode)
        except IOError, why: thanGudModalMessage(self, why, "Error opening file")
        else: return filnam, fw


def thanGudOpenSaveFile(self, ext, tit, mode="w", initialfile="", initialdir=""):
    "Gets a filename that exists, from user."
    while True:
        filnam = thanGudGetSaveFile(self, ext, tit, initialfile, initialdir)
        if not filnam: return filnam, filnam
        try: fw = file(filnam, mode)
        except IOError, why: thanGudModalMessage(self, why, "Error opening file")
        else: return filnam, fw


def thanGudGetDir(self, tit, initialdir="", mustexist=False):
    "Gets a filename that exists, from user."
    opendialog = tkFileDialog.Directory(parent=self,
                 title=thanUnicode(tit), initialdir=initialdir, mustexist=mustexist)
    filnam = opendialog.show()
    return thanAbsrelPath(filnam)

#============================================================================

def thanGudAskOkCancel(self, message, title, default="cancel"):
        "Shows message and returns true if user pressed OK; there is no default answer."
        return tkMessageBox.askokcancel(thanUnicode(title), thanUnicode(message),
            default=default, parent=self)

def thanGudAskYesNo(self, message, title, default="yes"):
        "Shows message and returns true if user pressed OK; there is no default answer; returns boolean True or False."
        return tkMessageBox.askyesno(thanUnicode(title), thanUnicode(message),
            default=default, parent=self)


#icons
#ERROR = "error"
#INFO = "info"
#QUESTION = "question"
#WARNING = "warning"
def thanGudModalMessage(self, message, title, icon=None, **kw):
        "Show a message and wait until user discards it."
        tkMessageBox.showinfo(thanUnicode(title), thanUnicode(message), parent=self, icon=icon, **kw)

#===========================================================================

class ThanToplevel(Toplevel, thanfontresize.ThanFontResize):
    def destroy(self):
        self.thanDestroy()
        Toplevel.destroy(self)


def thanGudHelpWin(parentwin, mes, title, hbar=0, vbar=1, width=80, height=25,
    font=None, background="lightyellow", foreground="black"):
        "Implements an Information window."
        import p_gtkwid
        help = ThanToplevel(parentwin)
        help.thanResizeFont(font)
        help.title(title)

        thanGudPosition(help, parentwin) #Position help window over parent

        txtHelp = p_gtkwid.ThanScrolledText(help, readonly=True, hbar=hbar, vbar=vbar,
            background=background, foreground=foreground, width=width, height=height)
        help.thanResizeBind([txtHelp])
        if not isinstance(mes, unicode): mes = thanUnicode(mes)
        txtHelp.thanSet(mes)
        txtHelp.grid(sticky="wesn")

        help.rowconfigure(0, weight=1)
        help.columnconfigure(0, weight=1)
        txtHelp.focus_set()
        help.focus_set()
        return help


def thanGudPosition(self, master="parent", dx=20, dy=15):
    "Position self with respect to parent window (master='parent'), to another window/widget (master=widget) or top left of the screen (master=None)."
    if master == "parent":             #Try to find parent window
        try:    master = self.master
        except: master = None

    if master == None:                 #With repsect to top left of the screen
        x = y = 0
    else:                              #With respect to parent window
        master.update()
        x = master.winfo_rootx()
        y = master.winfo_rooty()
    self.geometry("%+d%+d" % (x+dx, y+dy))


def thanGudGetText(self, mes, textDefault):
        "Accepts a nonblank text via a modal window."
        self.update()     # Experience showed that there should be no pending
                         # Tk jobs when we show a modal window
        while 1:
            ans = thantksimpledialog.askstring("Please enter text", mes,
                initialvalue=textDefault, parent=self)
            if ans == None: return ans
            if ans != "": return ans
            self.bell()

def thanGudGetFloat(self, mes, textDefault):
        "Accepts a real number via a modal window."
        self.update()     # Experience showed that there should be no pending
                          # Tk jobs when we show a modal window

        ans = thantksimpledialog.askfloat("Please enter a number", mes,
            initialvalue=textDefault, parent=self)
        return ans


def thanGudGetPosFloat(self, mes, textDefault):
    "Accepts a positive real number via a modal window."
    ans = thantksimpledialog.askfloat("Please enter a positive number", mes,
        initialvalue=textDefault, minvalue=0.00000001, parent=self)
    return ans


def thanGudGetFloat2(self, mes, textDefault):
        "Accepts 2 real number via a modal window."
        self.update()     # Experience showed that there should be no pending
                          # Tk jobs when we show a modal window
        while 1:
            ans = thantksimpledialog.askstring("Please enter 2 numbers separated by a space", mes,
                initialvalue=textDefault, parent=self)
            if ans == None: return None, None
            if ans != "":
                try:
                    f1, f2 = map(float, ans.replace(",", ".").split())
                    return f1, f2
                except ValueError, IndexError:
                    pass
            self.bell()

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
        if v == None or v < vmin or v > vmax:
            thanGudModalMessage(parentwin, "Illegal "+desc, "Bad data")
            control.focus_set()
            return
        res.append(v)
    return res 



def testmenus2():
    "Tests menus with statusbar."
    import p_gtkwid
    def __op(): print "open"
    def __cl(): print "close"
    def __ii(): print "insert image"
    def __ca(): print "load camera"
    def __re(): print "replace"
    def __hi(): print "history"
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
    thanTkCreateThanMenus2(root, mm, statcommand=sb.sett, condition=cond)
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
