# -*- coding: iso-8859-7 -*-
import Tkinter
import p_ggen
import thantkutila, thantksimpledialog


def xinpStr(win, mes, douDef=None, width=80):
    "Inputs a string with default value."
    win.update()     # Experience showed that there should be no pending Tk jobs when we show a modal window
    tit = tit1 = "Please enter text"
    mes = p_ggen.thanUnicode(mes)
    while True:
          dline = thantksimpledialog.askstring(tit, mes, initialvalue=p_ggen.thanUnicode(douDef), parent=win, width=width)
          if dline == None: return dline
          if dline == '' and douDef != None: return douDef     # Default value
          return p_ggen.thanUnunicode(dline)


def xinpStrB(win, mes, douDef=None):
    "Inputs a non-blank string with default value."
    win.update()     # Experience showed that there should be no pending Tk jobs when we show a modal window
    tit = tit1 = "Please enter non-blank text"
    mes = p_ggen.thanUnicode(mes)
    while True:
          dline = thantksimpledialog.askstring(tit, mes, initialvalue=p_ggen.thanUnicode(douDef), parent=win)
          if dline == None: return dline
          if dline == '' and douDef != None: dline = douDef         # Default value
          if dline.strip() != '': return p_ggen.thanUnunicode(dline)
          tit = "Try again: " + tit1


def xinpDouble (win, mes, douDef):
    "Inputs a double with default value."
    win.update()     # Experience showed that there should be no pending Tk jobs when we show a modal window
    tit = "Please enter a real number"
    mes = p_ggen.thanUnicode(mes)
    if douDef == 0.0: douDef = "0.0"      #Work around bug: when initialvalue is zero, it does not show on the widget
    dou = thantksimpledialog.askfloat(tit, mes, initialvalue=douDef, parent=win)
    if dou == None: return dou
    return dou


def xinpLong (win, mes, douDef):
    "Inputs an integer with default value."
    win.update()     # Experience showed that there should be no pending Tk jobs when we show a modal window
    tit = "Please enter an integer number"
    mes = p_ggen.thanUnicode(mes)
    if douDef == 0: douDef = "0"      #Work around bug: when initialvalue is zero, it does not show on the widget
    dou = thantksimpledialog.askinteger(tit, mes, initialvalue=douDef, parent=win)
    if dou == None: return dou
    return dou


def xinpDoubleR (win, mes, douMin, douMax, douDef):
    "Inputs a double with default value and range check."
    win.update()     # Experience showed that there should be no pending Tk jobs when we show a modal window
    tit = "Please enter a real number"
    mes = p_ggen.thanUnicode(mes)
    if douDef == 0.0: douDef = "0.0"      #Work around bug: when initialvalue is zero, it does not show on the widget
    dou = thantksimpledialog.askfloat(tit, mes, initialvalue=douDef, minvalue=douMin, maxvalue=douMax, parent=win)
    if dou == None: return dou
    return dou


def xinpLongR (win, mes, douMin, douMax, douDef):
    "Inputs an integer with default value and range check."
    win.update()     # Experience showed that there should be no pending Tk jobs when we show a modal window
    tit = "Please enter an integer number"
    mes = p_ggen.thanUnicode(mes)
    if douDef == 0: douDef = "0"      #Work around bug: when initialvalue is zero, it does not show on the widget
    dou = thantksimpledialog.askinteger(tit, mes, initialvalue=douDef, minvalue=douMin, maxvalue=douMax, parent=win)
    if dou == None: return dou
    return dou


class XinpFiles(thantksimpledialog.ThanDialog):

    def __init__(self, parent, mes, suf="", nest=False, initialdir=".", title=None, buttonlabels=None, **kw):
        self.thanCargo = mes, suf, nest, initialdir
        print "suf=", self.thanCargo[1]
        thantksimpledialog.ThanDialog.__init__(self, parent, title, buttonlabels, **kw)

    def body(self, win):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        import p_gtkwid, p_gtkuti
        lab = Tkinter.Label(win, text=self.thanCargo[0])
        lab.grid(row=0, column=0, sticky="w")
        #If text= is not defined, then it default to the current directory, which we do not want
        self.thanFil = p_gtkwid.ThanFile(win, text="", initialdir=self.thanCargo[3], extension=self.thanCargo[1], width=40)
        self.thanFil.grid(row=1, column=0, sticky="we")
        win.columnconfigure(0, weight=1)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        return self.thanFil

    def apply(self):
        '''process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        '''
        self.result = self.thanFil.thanGet()

    def destroy(self):
        "Break circular references."
        del self.thanFil
        thantksimpledialog.ThanDialog.destroy(self)


def xinpFiles(win, mes, suf="", nest=False, initialdir=None):
    """Gets data files with suffix suf.

    Examples:
    1. fils = xinpFiles("Δώστε αρχεία που καταλήγουν σε xx.asc (με ή χωρίς την κατάληξη). Για όλα δώστε * (enter=*) : ", "xx.asc")
       The above gets all the files in current directory (and recursively in the 
       subdirectories if nest==True)
       which have .asc as a suffix:  a.asc, thanasis.asc, 1.asc, ...
    2. The filenames are transformed to lower, to facilitate windows..
    """
    import p_gfil
    win.update()     # Experience showed that there should be no pending Tk jobs when we show a modal window
    tit = tit1 = "Please enter filename prefixes and/or *"
    mes = p_ggen.thanUnicode(mes)
    suf = suf.lower()
    print "suf=", suf
    if initialdir == None: _, _, initialdir = p_gfil.openfileWinget()
    initialdir = p_ggen.path(initialdir)
    print "initialdir=", initialdir
    while True:
        x = XinpFiles(win, mes, suf, nest, initialdir, title=tit)
        fentries = x.result
        print "fentries=", fentries
        del x
        if fentries == None: return None
        fentries = fentries.strip()
        if fentries == "" or p_ggen.path(fentries)/"q1" == initialdir/"q1": fentries = initialdir / "*"+suf   #Work around missing last "/"
        print "fentries=", fentries
        fildats = []
        for fentry in fentries.split():
            fentry = p_ggen.path(fentry)
            if "*" in fentry or "?" in fentry:
                cdir = fentry.parent
                if cdir == "": cdir = initialdir
                fentry = fentry.basename()
                if not fentry.lower().endswith(suf): fentry += suf
                if nest: f = list(cdir.walkfiles(fentry))      # nested subdirectories
                else:    f = list(cdir.files(fentry))          # only current directory
#                if len(f) == 0: prg("Warning: no %s files matches '%s'" % (suf, fentry))
                fildats.extend(f)
            else:
                if not fentry.lower().endswith(suf): fentry += suf
                fildats.append(fentry)
        if len(fildats) > 0: return fildats
        ter = "Error: No %s files defined or found.\nTry again." % (suf,)
        thantkutila.thanGudModalMessage(win, ter, "No files found", icon=thantkutila.ERROR)


def xinpDir(win, mes, mustexist=False, mustnotexist=False, default=None):
    "Inputs a non-blank directory name with default value."
    from p_gfil import Tgui
    if default != None:
        try:
            default = thanUnunicode(default)
        except:
            default = ""
    while True:
        f = thantkutila.thanGudGetDir(win, mes, initialdir=default, mustexist=mustexist)
        if f == None: return f
        f = p_ggen.path(f).expand().abspath()
        if mustnotexist:
            if f.exists():
                ter = "Ο φάκελλος %s ήδη υπάρχει. Προσπαθείστε πάλι." % f
                thantkutila.thanGudModalMessage(win, ter, "Directory already exists", icon=thantkutila.ERROR)
                continue
        if f.exists() and not f.isdir():   #In case that both mustexist=False and mustnotexist=False
            ter="Ο φάκελλος %s δεν είναι φάκελλος (είναι αρχείο). Προσπαθείστε πάλι." % f
            thantkutila.thanGudModalMessage(win, ter, "Not a directory", icon=thantkutila.ERROR)
            continue
        return f


def xinpMchoice(win, mes, coms, douDef=1):
    "Inputs a choice of the user as an integer starting at 1."
    import p_gtkwid
    win.update()     # Experience showed that there should be no pending Tk jobs when we show a modal window
    if p_ggen.isString(coms): coms = coms.split()
    w = max(len(com1) for com1 in coms)
    w = max(w, 10+len(mes))
    win = p_gtkwid.ThanPoplist(win, coms, width=w, height=len(coms), title=p_ggen.thanUnicode(mes), default=douDef-1)
    dou = win.result
    if dou == None: return dou
    return coms.index(dou) + 1


def xinpNo(win, mes, douDef=True):
      "Inputs yes or no."
      coms = "Yes", "No"
      if douDef: douDef = 1
      else:      douDef = 2
      ans = xinpMchoice(win, mes, coms, douDef)
      if ans == None: return ans
      return ans == 1


def testxinpFiles():
    "Test the xinpFiles() function."
    root = Tkinter.Tk()
    x = xinpFiles(root, mes="Δώστε αρχεία που καταλήγουν σε xx.asc (με ή χωρίς την κατάληξη).\nΓια να επιλεγούν όλα δώστε *", suf="xx.asc", nest=False)
    print "files found=", x


def testxinpMchoice():
    "Test the xinpFiles() function."
    root = Tkinter.Tk()
    x = xinpMchoice(root, "Διάλεξε γλυκό:", "Δήμητρα Ανδρέας Στέλλα", 3)
    print "answer=", x


def testxinpDir():
    "Test the xinpDir() function."
    root = Tkinter.Tk()
    x = xinpDir(root, "Διάλεξε φάκελλο:", mustexist=False, mustnotexist=False, default=".")
    print "answer=", x


if __name__ == "__main__":
    testxinpDir()
