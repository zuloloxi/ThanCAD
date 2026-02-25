import sys, time
try: from configparser import SafeConfigParser     #python3.9
except: from configparser import ConfigParser as SafeConfigParser  #python3.12
import tkinter
import p_ggen, p_gtkwid
Tgui = p_ggen.Tgui

root = None
geom = None     #"200x200+1046+35"
prevdir = p_ggen.path(".")
prevpref = p_ggen.path("")
iconxbm = None      #Icon to be shown near the title of the window
tkclass = None


class Root(tkinter.Tk, p_gtkwid.ThanFontResize):
    "A gui window for opening files and showing program status."

    def __init__(self, descp, *args, **kw):
        "Create widgets."
        if "className" not in kw: kw["className"] = "thanapps"
        tkinter.Tk.__init__(self, *args, **kw)
        self.title(p_ggen.thanUnicode(descp))
        self.thanResizeFont()
        p_gtkwid.thanDeficon(self, iconxbm)
        #thanFormTkcol = "#%02x%02x%02x"
        #col = thanFormTkcol % (254, 214, 254)
        #col = "orange"
        import p_gcol
        col = p_gcol.thanDxfColName2Rgb["apricot"]   #251, 206, 177)
        col = p_gcol.thanFormTkcol % col
        self.tinfo = p_gtkwid.ThanScrolledText(root, font=self.thanFonts[0], readonly=True, width=100, bg=col)
        self.tinfo.grid(sticky="wesn")
        self.tinfo.tag_config("mes", foreground="blue")
        self.thanResizeBind([self.tinfo])
        self.thanCreateTags([self.tinfo])
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.__crmenus()
#        self.protocol("WM_DELETE_WINDOW", destroy) # In case user via window manager
        try: self.geometry(geom)
        except: print("bad geometry:", geom); pass
        self.timep = time.time()
        self.dtimep = 5.0

    def __crmenus(self):
        "Creates a description of the desired menus in a list."
        seq = ["File"]
        menus = {}
        menus["File"] = \
        [ ("menu", Tgui["&File"], ""),            # Menu Title
          (self.__devcmd, Tgui["&Save program output"],  Tgui["Save the text of the program output"]),
          (self.destroy,  Tgui["E&xit"], Tgui["Close GUI"], "darkred"),
          ("endmenu",),
        ]
        ms = []
        for m in seq: ms.extend(menus[m])
        menubar, submenus = p_gtkwid.thanTkCreateThanMenus2(self, ms)
        self["menu"] = menubar

    def __devcmd(self):
        "Saves the content of the command window to a txt file."
        _, fout = thanTxtopen(self, Tgui["Save the text of the program output"], mode="w")
        if fout == p_ggen.Canc: return
        fout.write(self.tinfo.thanGet())
        fout.close()

    def thanPrt(self, t, tags=()):
        "Print text to the embedded info window."
        self.tinfo.thanAppendf("%s\n" % (t,), tags)
        t1 = time.time()
        if t1-self.timep > self.dtimep:
            self.showEnd()
            self.timep = t1
        self.tinfo.update()

    def thanPrts(self, t, tags=()):
        "Print text to the embedded info window."
        self.tinfo.thanAppendf("%s" % (t,), tags)
        t1 = time.time()
        if t1-self.timep > self.dtimep:
            self.showEnd()
            self.timep = t1
        self.tinfo.update()

    def showEnd(self):
        "Go to the end of the text shown in the window."
        self.tinfo.set_insert_end()

    def destroy(self):
        "Break circular references."
        del self.tinfo
        self.thanDestroy()
        tkinter.Tk.destroy(self)


def thanTxtopen(win, mes, suf=".txt", mode="r", initialfile=None, initialdir=None):
    "Opens a text file for reading or writting something."
    if initialdir is None: initialdir = prevdir
    if initialfile is None: initialfile = prevpref.namebase
    if "w" in mode:
        fildxf, frw = p_gtkwid.thanGudOpenSaveFile(win, suf, mes, mode,
            initialfile, initialdir, errors="replace")
    else:
        fildxf, frw = p_gtkwid.thanGudOpenReadFile(win, suf, mes, mode,
            initialfile, initialdir, errors="replace")
    if frw is None: return p_ggen.Canc, p_ggen.Canc     # File open cancelled
    return p_ggen.path(fildxf), frw


def openfileWinmain(descp):
    "Make main window of the program."
    global root
    thanOptsGet()
    root = Root(descp)
    return root, root.thanPrt, prevdir


def openfileWinget():
    "Return root and print function."
    if root is None and prevdir == ".": thanOptsGet()        #In case we need prevdir without the gui mechanism
    if root is None: return root, None,         prevdir
    else:            return root, root.thanPrt, prevdir


def openfileSetprev(prevdir1=None, prevpref1=None):
    "Set previous directory and previous prefix."
    global prevdir, prevpref
    if root is None and prevdir == ".": thanOptsGet()        #In case we need prevdir without the gui mechanism
    if prevdir1  is not None: prevdir  = p_ggen.path(prevdir1).abspath()
    if prevpref1 is not None: prevpref = p_ggen.path(prevpref1).abspath()


def xinpFiles(win, mes, suf="", nest=False, initialdir=None):
    """Gets data files with suffix suf.

    Examples:
    1. fils = xinpFiles("Δώστε αρχεία που καταλήγουν σε xx.asc (με ή χωρίς την κατάληξη). Για όλα δώστε * (enter=*) : ", "xx.asc")
       The above gets all the files in current directory (and recursively in the
       subdirectories if nest==True)
       which have .asc as a suffix:  a.asc, thanasis.asc, 1.asc, ...
    2. The filenames are transformed to lower, to facilitate windows..
    """
    if initialdir is None: _, _, initialdir = openfileWinget()
    return p_gtkwid.xinpFiles(win, mes, suf, nest, initialdir)


def openfileWindestroy():
    "Destroy gui."
    global root, geom
    if root is None: return
    geom = root.geometry()
    thanOptsSave()
    root.thanPrt("\n%s\n" % (Tgui["Close this window to finish.."],), "mes")
    root.showEnd()
#    root.tinfo.set_insert_end()           # Go to the end of the text shown in the window
    root.mainloop()
#    root.destroy() #The only way to close the window is via the window manager: If so, Tkinter automatically call destroy on root
    root = None


def openfilepro(mes, iPro, files1, descp):
    """Opens all the needed files from a single prefix.

    ext is a string of extensions separated by a space including the dot.
    For example:
        ".xyd .ery"
    """
    global prevdir, prevpref
    ext = []
    iopen = False
    for file1 in files1:
#        print "opgui.openfilepro():", file1.ext, "stat=", file1.stat
        i = abs(file1.iPro)
        if i-1 != iPro: continue
        if file1.stat == 'old' or file1.stat == "opt+": iopen = True
        if iopen or file1.stat != 'opt': ext.append("." + file1.ext)   #Avoid to overwrite optional files, if all other files are open for writting (opt+ is different)
    ext = " ".join(ext)
    mes1 = "Enter %s (%s)" % (mes, descp)
    if iopen:
        fnam, fXyd = p_gtkwid.thanGudOpenReadFile(root, ext, p_ggen.thanUnicode(mes1), initialfile="", initialdir=prevdir)
    else:
        fnam, fXyd = p_gtkwid.thanGudOpenSaveFile(root, ext, p_ggen.thanUnicode(mes1), initialfile="", initialdir=prevdir)
    if not fnam: return None
    fnam = p_ggen.path(fnam).abspath()
    prevdir = fnam.parent
    fpref = prevdir / fnam.namebase
    if iPro == 0: prevpref = fpref  #Save only the first prefix; when user saves the text of the graphics window, they get the first prefix as default
    fXyd.close()
    return fpref

#=============================================================================

def thanOptGeometryGet(c):
    "Read dimensions in pixels of various objects."
    global geom
    try:
        geom1 = c.get("geometry", "canvas geometry")
    except:
        return
    geom = geom1


def thanOptFilesGet(c):
    "Read directories and files."
    global prevdir
    #thanasis2017_06_05: directory in command line arguments supersedes prevdir
    t = None
    if len(sys.argv) > 1:
        t = sys.argv[1]
        if t == "--commandline":
            if len(sys.argv) > 2: t = sys.argv[2]
            else:                 t = None
    if t is not None:
        prevdir = t
        return

    try:
        prevdir1 = c.get("files", "previous directory")
    except:
        return
    prevdir = p_ggen.path(prevdir1)


def thanOptGeometrySave(c):
    "Write dimensions of various objects."
    if not c.has_section("geometry"): c.add_section("geometry")
    c.set("geometry", "canvas geometry", str(geom))


def thanOptFilesSave(c):
    "Write directories and files."
    if not c.has_section("files"): c.add_section("files")
    c.set("files", "previous directory", prevdir)


def thanOptsGet():
    "Reads the attributes from config files and store them as global variables."
    fc, terr = p_ggen.configFile("common.conf", "thanapps")
    if terr != "":
        print("thanOptsGet():", terr)
        return
    c = SafeConfigParser()
    c.read(fc)
    thanOptGeometryGet(c)
    thanOptFilesGet(c)


def thanOptsSave():
    "Writes the attributes to config files."
    fc, terr = p_ggen.configFile("common.conf", "thanapps")
    if terr != "":
        print("thanOptsSave():", terr)
        return
    c = SafeConfigParser()
    c.read(fc)
    thanOptGeometrySave(c)
    thanOptFilesSave(c)
    try:
        f = open(fc, "w")
        c.write(f)
    except IOError as why:
        print("Could not save config file:", str(why))
