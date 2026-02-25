from tkinter import (Tk, Toplevel, Frame, Text, Label, GROOVE, END,
    StringVar)
from .thanfontresize import ThanFontResize
from .thantkutila import (thanGudOpenReadFile, thanGudModalMessage, thanGudAskOkCancel,
    thanGudOpenSaveFile)
from .thanwidstrans import T
from .thanfiles import ThanFiles
from .thanwids import ThanMenu, ThanToolButton
from . import thanicon


class ThanWinComCom(ThanFontResize):
    "Mechanism for an application window."

    def thanOpenedRefresh(self, opened):
        "Shows new list of opened files."
        mr = self.thanMnuWin
        mr.delete(0, END)
        win,filnam = opened[0]
        mr.add_command(label=filnam, command=lambda w=win: w.thanFocus1())
        mr.add_separator()
        for win,filnam in opened[1:]:
#            mr.add_command(label=filnam, accelerator="ctrl+"+str(i), command=win.thanFocus1)
            mr.add_command(label=filnam, command=lambda w=win: w.thanFocus1())


    def thanRecentRefresh(self, recent):
        "Shows new list of recent files."
        mr = self.thanMnuRecent
        mr.delete(0, END)
        for filnam in recent:
            mr.add_command(label=filnam, command=lambda f=filnam:self.thanOpen(f))


    def thanFocus(self, evt=None):  # Overwrite to focus on a widget in window
        "Set focus to this window."
#       self.lift()                 # It seems that this slows down focus    
        self.focus_set()


    def thanFocus1(self, evt=None):  # Overwrite to focus on a widget in window
        """Set focus to this window and uncovers it if it covered by other windows.

        This function should only be called from the windows menu, since it seems that
        self.lift() slows down the focus procedure."""
        self.deiconify()        # In case it is minimised/iconified
        self.lift()
        self.focus_set()


    def thanMenusComAll(self):
        "Common menus an application needs."
        menuBar = ThanMenu(self, condition=None, statcommand=self.thanStatustext.set)
        menu = ThanMenu(menuBar, tearoff=0)
        menu.add_command(label=T["&New"],  accelerator="ctrl+N", command=self.thanMnuFileNew, help=T["Create a new file"])
        menu.add_command(label=T["&Open"], accelerator="ctrl+O", command=self.thanMnuFileOpen, help=T["Open an existing file"])
        self.thanMnuRecent = ThanMenu(menu, tearoff=0)
        menu.add_cascade(label=T["Recent"], underline=0, menu=self.thanMnuRecent, help=T["Reopen recently opened files"])
        menu.add_separator()
        menu.add_command(label=T["&Save"],    accelerator="ctrl+S", command=self.thanMnuFileSave, help=T["Save current file"])
        menu.add_command(label=T["S&ave as"], command=self.thanMnuFileSaveas, help=T["Save current file with new name"])
        menu.add_command(label=T["&Close"],   accelerator="ctrl+W", command=self.thanMnuFileClose, help=T["Close current file"])
        menu.add_separator()
        menu.add_command(label=T["E&xit"], accelerator="ctrl+X", command=self.thanMnuFileExit, help=T["Terminate and exit program"])
        menuBar.add_cascade(label=T["&File"], menu=menu)
        self.thanMnuFile = menu

        self.thanMnuWin = ThanMenu(menuBar, tearoff=0)
        menuBar.add_cascade(label=T["&Windows"], underline=0, menu=self.thanMnuWin)

        menu = ThanMenu(menuBar, tearoff=0)
        menu.add_command(label=T["&Help"], accelerator="F1", command=self.thanMnuHelp)
        menu.add_command(label=T["&License"], command=self.thanMnuLicense, help=T["Show lisense of the program"])
        menu.add_command(label=T["&History"], command=self.thanMnuHist, help=T["Show evolution of the program"])
        menu.add_command(label=T["&About"], command=self.thanMnuAbout, help=T["Summarised info about the program"])
        menuBar.add_cascade(label=T["&Help"], underline=0, menu=menu)
        self.config(menu=menuBar)
        self.thanMenuBar = menuBar

        self.bind("<F1>", self.thanMnuHelp)
        self.bind("<Control-n>", self.thanMnuFileNew)
        self.bind("<Control-N>", self.thanMnuFileNew)
        self.bind("<Control-o>", self.thanMnuFileOpen)
        self.bind("<Control-O>", self.thanMnuFileOpen)
        self.bind("<Control-s>", self.thanMnuFileSave)
        self.bind("<Control-S>", self.thanMnuFileSave)
        self.bind("<Control-w>", self.thanMnuFileClose)
        self.bind("<Control-W>", self.thanMnuFileClose)
#        self.bind("<Alt-h>", self.cb_help)


    def thanMenusComMain(self):
        "Menus that occur in the main application window."
        self.thanMenusComAll()
        self.thanMnuFile.delete(4, 7)
        self.unbind("<Control-s>")
        self.unbind("<Control-S>")
        self.bind("<Control-w>", self.thanMnuFileExit)
        self.bind("<Control-W>", self.thanMnuFileExit)


    def thanMenusCom(self):
        "Menus that occur in the document application window."
        self.thanMenusComAll()
        self.thanMnuFile.delete(7, 9)


    def thanToolbarComAll(self, iicons):
        "Common toolbar an application needs."
        self.thanToolbar = t = Frame(self, relief=GROOVE, bd=2)
        buttons = \
        ( ("new",  self.thanMnuFileNew, "Creates a new file"),
          ("open", self.thanMnuFileOpen, "Opens an existing fil"),
          ("save", self.thanMnuFileSave, "Saves current file")
        )
        c = 0
        for i in iicons:
            icon, callback, h = buttons[i]
            but = ThanToolButton(t, image=thanicon.get(icon), command=callback, help=h)
            but.grid(row=0, column=c)
            c += 1
        t.grid(row=0, sticky="wn")


    def thanToolbarCom(self):     self.thanToolbarComAll((0,1,2))
    def thanToolbarComMain(self): self.thanToolbarComAll((0,1))


    def thanStatusbarComAll(self):
        "Common statusbar an application needs."
        self.thanStatustext = StringVar()
        self.thanStatusbar = sb = Frame(self)
        sb.grid(row=2, sticky="we")
        lab = Label(sb, anchor="w", textvariable=self.thanStatustext, bg="lightyellow")
        lab.grid(row=0, column=0, sticky="we")
        sb.columnconfigure(0, weight=1)
        return lab


    def thanMnuFileNew(self, evt=None):
        "Creates a new file and corresponding window."
        filnam = self.thanFh.thanTemp()
        win = self.factoryWin(self.thanFh, filnam)
        win.thanFocus()


    def thanMnuFileOpen(self, evt=None):
        "Opens an existing file and corresponding window."
        filnam, fr = thanGudOpenReadFile(self, self.thanFh.thanSuf, "Open Existing File")
        if fr is None: return
        if filnam.strip() == "": return
        win = self.factoryWin(self.thanFh, filnam)
        win.thanFileDefined = 1
        if not win.thanMerge(fr): self.thanMnuFileClose(); self.thanFocus(); return
        win.thanFocus()


    def thanOpen(self, filnam):
        try: fr = open(filnam, "r")
        except IOError as why:
            thanGudModalMessage(self, why, T["Error opening file"])
            return
        win = self.factoryWin(self.thanFh, filnam)
        win.thanFileDefined = 1
        if not win.thanMerge(fr): self.thanMnuFileClose(); self.thanfocus(); return
        win.thanFocus()


    def thanMnuFileClose(self, evt=None):
        if self.thanIsModified():
            a = thanGudAskOkCancel(self, T["File modified. Ok to quit?"], T["FILE MODIFIED"])
            if not a: self.thanFocus(); return "break"
        self.thanFh.thanOpenedDel(self)
        if self.thanFileDefined: self.thanFh.thanRecentAdd(self.thanFilnam)
        self.destroy()
        self.thanFh.thanOpenedGet()[-1][0].thanFocus()    # Focus on last window opened


    def thanMnuFileSave(self, evt=None):
        if not self.thanFileDefined: return self.thanMnuFileSaveas()
        if self.thanValidate() is None: return
        try: fw = open(self.thanFilnam, "w")
        except IOError as why: thanGudModalMessage(self, why, T["Error opening file"])
        else:
            if self.thanSave(fw): self.thanFileDefined = 1
        self.thanFocus()


    def thanMnuFileSaveas(self, evt=None):
        if self.thanValidate() is None: return
        filnam, fw = thanGudOpenSaveFile(self, self.thanFh.thanSuf, "Saves to a File") 
        self.thanFocus()
        if filnam.strip() == "": return
        if not self.thanSave(fw): return
        if self.thanFileDefined: self.thanFh.thanRecentAdd(self.thanFilnam)
        self.thanFh.thanOpenedDel(self)
        self.thanFilnam = filnam
        self.thanFh.thanOpenedAdd(self, self.thanFilnam)
        self.title(self.thanTitlePrefix+self.thanFilnam)
        self.thanFileDefined = 1


    def thanMnuFileExit(self, evt=None):
        opened = self.thanFh.thanOpenedGet()
        for win,filnam in opened:
            if str(win) == str(self): continue
            if win.thanMnuFileClose() == "break": return "break"
        self.thanFh.thanConfigSave()
        self.destroy()


    def thanMnuHelp(self, evt=None): pass
    def thanMnuLicense(self, evt=None): pass
    def thanMnuHist(self, evt=None): pass
    def thanMnuAbout(self, evt=None): pass


    def destroy(self):
        print("ThanWinComCom", self, "destroy called")
        self.thanDestroy()                      #ThanFontResize class
        del self.thanMenuBar, self.thanMnuRecent, self.thanMnuFile, self.thanMnuWin
#            self.thanStatusbar, self.thanStatustext


    def __del__(self): print("ThanWinComCom", self, "is deleted")


class ThanWinMainCom(Tk, ThanWinComCom):
    "Application main window."

    def factoryWin(self, *args, **kw):
        "Return a document window of this application."
        return ThanWinCom(*args, **kw)

    def __init__(self, title="Application", suffix=".txt", config="text", **kw):
        Tk.__init__(self, **kw)
        self.thanResizeFont()
        self.thanPlatform()
        self.thanFh = ThanFiles(suffix=suffix, config=config)
        self.title(title)
        self.thanToolbarComMain()
        lab = self.thanStatusbarComAll()
        self.thanMenusComMain()
        self.thanFh.thanOpenedAdd(self, title)
        self.thanRecentRefresh(self.thanFh.thanRecentGet())
        self.protocol("WM_DELETE_WINDOW", self.thanMnuFileExit)
        self.thanInfo = Text(self, width=30, height=5)
        self.thanInfo.grid(row=1, sticky="wesn")
        self.thanResizeBind([lab, self.thanInfo])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def thanPlatform(self):
        "Platform specific code?."
        self.option_add("*Text.background", "black")
        self.option_add("*Text.foreground", "lightgreen")
        self.option_add("*Text.insertbackground", "lightgreen")

    def destroy(self):
        print("ThanWinMainCom", self, "destroy called")
        del self.thanInfo
        ThanWinComCom.destroy(self)
        Tk.destroy(self)

    def __del__(self): print("ThanWinMainCom", self, "is deleted")


class ThanWinCom(Toplevel, ThanWinComCom):
    "Application's document window."

    def factoryWin(self, *args, **kw):
        "Return a document window of this application."
        return ThanWinCom(*args, **kw)

    def __init__(self, title, filehandler, filnam, **kw):
        Toplevel.__init__(self, **kw)
        self.thanResizeFont()
        self.thanPlatform()
        self.thanTitlePrefix = title
        self.thanFh = filehandler
        self.title(self.thanTitlePrefix+filnam)
        self.thanToolbarCom()
        lab = self.thanStatusbarComAll()
        self.thanResizeBind([lab])
        self.thanMenusCom()
        self.thanFh.thanOpenedAdd(self, filnam)
        self.thanRecentRefresh(self.thanFh.thanRecentGet())
        self.thanFilnam = filnam
        self.thanFileDefined = 0
        self.protocol("WM_DELETE_WINDOW", self.thanMnuFileClose)
        self.columnconfigure(0, weight=1)

    def thanPlatform(self): pass
    def thanMerge(self, fr): return 1
    def thanIsModified(self): return 0
    def thanSave(self, fw): return 1
    def thanValidate(self): return True

    def destroy(self):
        print("ThanWinCom", self, "destroy called")
        del self.thanStatustext, self.thanStatusbar
        ThanWinComCom.destroy(self)
        Toplevel.destroy(self)

    def __del__(self): print("ThanWinCom", self, "is deleted")

