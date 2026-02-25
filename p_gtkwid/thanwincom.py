# -*- coding: iso-8859-7 -*-
encoding = "iso-8859-7"
import sys
from Tkinter import *
from p_ggen import thanUnicode, Null
from p_gtkuti import *
from thanwidstrans import T
from thanfiles import ThanFiles
from thanwids import ThanText, ThanMenu, ThanToolButton
import thanicon


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
        if fr == None: return
        if filnam.strip() == "": return
        win = self.factoryWin(self.thanFh, filnam)
        win.thanFileDefined = 1
        if not win.thanMerge(fr): self.thanMnuFileClose(); self.thanFocus(); return
        win.thanFocus()


    def thanOpen(self, filnam):
        try: fr = file(filnam, "r")
        except IOError, why:
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
        if self.thanValidate() == None: return
        try: fw = file(self.thanFilnam, "w")
        except IOError, why: thanGudModalMessage(self, why, T["Error opening file"])
        else:
            if self.thanSave(fw): self.thanFileDefined = 1
        self.thanFocus()


    def thanMnuFileSaveas(self, evt=None):
        if self.thanValidate() == None: return
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
        print "ThanWinComCom", self, "destroy called"
        self.thanDestroy()                      #ThanFontResize class
        del self.thanMenuBar, self.thanMnuRecent, self.thanMnuFile, self.thanMnuWin
#            self.thanStatusbar, self.thanStatustext


    def __del__(self): print "ThanWinComCom", self, "is deleted"


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
        print "ThanWinMainCom", self, "destroy called"
        del self.thanInfo
        ThanWinComCom.destroy(self)
        Tk.destroy(self)

    def __del__(self): print "ThanWinMainCom", self, "is deleted"


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
        print "ThanWinCom", self, "destroy called"
        del self.thanStatustext, self.thanStatusbar
        ThanWinComCom.destroy(self)
        Toplevel.destroy(self)

    def __del__(self): print "ThanWinCom", self, "is deleted"


###############################################################################
###############################################################################

import p_gvers as thanvers

class ThanEditWinMain(ThanWinMainCom):
    def factoryWin(self, *args, **kw): return ThanEditWin(thanvers.name+": ", *args, **kw)
    def thanMnuHelp(self, evt=None)   : thanGudHelpWin(self, thanvers.help, "Help about ThanEdit")
    def thanMnuLicense(self, evt=None): thanGudHelpWin(self, thanvers.license[2],  "ThanEdit License")
    def thanMnuHist(self, evt=None)   : thanGudHelpWin(self, thanvers.history, "ThanEdit history")
    def thanMnuAbout(self, evt=None)  : thanGudHelpWin(self, thanvers.about,"About ThenEdit")
    def __del__(self): print "ThanEditWinMain", self, "is deleted"

class ThanEditWin(ThanWinCom):
    def factoryWin(self, *args, **kw): return ThanEditWin(thanvers.name+": ", *args, **kw)
    def __init__(self, *args, **kw):
        ThanWinCom.__init__(self, *args, **kw)

        menu = ThanMenu(self.thanMenuBar, tearoff=0)
        menu.add_command(label=T["&Produce drawing"], accelerator="F5", command=self.thanRun, help=T["Run the program"])
        self.thanMenuBar.insert_cascade(2, label=T["&Run"], menu=menu)
        self.bind("<F5>", self.thanRun)
        but = ThanToolButton(self.thanToolbar, image=thanicon.get("run"), command=self.thanRun, help=T["Run the program"])
        but.grid(row=0, column=3)

        self.thanText = ThanText(self, width=80, height=25, insertbackground="lightgreen")
        self.thanText.grid(row=1, sticky="wesn")
        fra = self.thanStatusbar
        lab = Label(fra, text="Line")
        lab.grid(row=0, column=1, sticky="e")
        self.thanLabLine = Label(fra, text="1")
        self.thanLabLine.grid(row=0, column=2, sticky="e")
        self.thanResizeBind([self.thanText, lab, self.thanLabLine])
#        lab = Button(fra, text="highlit 124", command=lambda self=self: self.thanHighlit(124))
#        lab.grid(row=0, column=3)

        self.rowconfigure(1, weight=1)
        self.thanValOri = ""
        self._updateLine()

    def thanFocus(self, evt=None):  # Overwrite to focus on a widget in window
        "Set focus to this window."
#       self.lift()                 # It seems that this slows down focus
        self.thanText.focus_set()

    def thanFocus1(self, evt=None):  # Overwrite to focus on a widget in window
        """Set focus to this window and uncovers it if it covered by other windows.

        This function should only be called from the windows menu, since it seems that
        self.lift() slows down the focus procedure."""
        self.deiconify()        # In case it is minimised/iconified
        self.lift()
        self.thanText.focus_set()

    def thanMerge(self, fr):
        self.thanValOri = fr.read()
        self.thanText.thanSet(self.thanValOri)
        self.thanText.set_insert("1.0")
        return 1

    def thanIsModified(self):
        return self.thanValOri != self.thanText.thanGet()

    def thanSave(self, fw):
        t = self.thanText.thanGet()
        fw.write(t)
        self.thanValOri = t
        return 1

    def _updateLine(self):
        ind = self.thanText.index(INSERT)
        self.thanLabLine["text"] = ind.split(".")[0]
        self.after(200, self._updateLine)

    def thanHighlit(self, lin):
        i = "%d.0"%lin
        self.thanText.set_insert(i)
        self.thanText.tag_add("red", i, "%d.end"%lin)
        self.thanText.tag_config("red", foreground="red")
#        self.after(5000, self._clearRed)

    def _clearRed(self):
        self.thanText.tag_delete("red")

    def thanRun(self, evt=None):
        if not self.thanFileDefined or self.thanIsModified():
	    thanGudModalMessage(self, T["Please save the data before you run the program."],
	                        T["Data is not saved"])
	    return
	f = os.path.abspath(self.thanFilnam)
	dlines = runmhk(f)
	if sys.platform == "win32": 
	    tit = u"ΕΠΙΤΥΧΗΣ ΕΚΤΕΛΕΣΗ ΠΡΟΓΡΑΜΜΑΤΟΣ", u"ΑΝΕΠΙΤΥΧΗΣ ΕΚΤΕΛΕΣΗ ΠΡΟΓΡΑΜΜΑΤΟΣ", u"ΓΡΑΜΜΗ"
	else:
	    tit = "ΕΠΙΤΥΧΗΣ ΕΚΤΕΛΕΣΗ ΠΡΟΓΡΑΜΜΑΤΟΣ", "ΑΝΕΠΙΤΥΧΗΣ ΕΚΤΕΛΕΣΗ ΠΡΟΓΡΑΜΜΑΤΟΣ", "ΓΡΑΜΜΗ"
        if dlines[-1].strip() == tit[0]:
	    f = os.path.splitext(f)[0] + ".dxf"
	    thanGudModalMessage(self, T["Drawing is saved in file "]+f, tit[0])
	    return
        if dlines[-1].strip() == tit[1]:
	    if tit[2] in dlines[0]:
	        lin = int(dlines[0].split()[-1][:-1])
		self.thanHighlit(lin)
	        thanGudModalMessage(self, "\n".join(dlines[:-2]), tit[1])
	        self.after(10000, self._clearRed)
	    else:
	        thanGudModalMessage(self, "\n".join(dlines[:-2]), tit[1])
	elif "Bad command" in dlines[-1] or "not found" in dlines[-1]:
	    dlines.append("Program mhkex not found.")
            thanGudModalMessage(self, "\n".join(dlines), tit[1])
	else:
            thanGudModalMessage(self, "\n".join(dlines), tit[1])

    def thanMnuHelp(self, evt=None)   : thanGudHelpWin(self, thanvers.help, "Help about ThanEdit")
    def thanMnuLicense(self, evt=None): thanGudHelpWin(self, thanvers.license,  "ThanEdit License")
    def thanMnuHist(self, evt=None)   : thanGudHelpWin(self, thanvers.history, "ThanEdit history")
    def thanMnuAbout(self, evt=None)  : thanGudHelpWin(self, thanvers.about,"About ThenEdit")
    def destroy(self):
        print "ThanEditWin", self, "destroy called"
        del self.thanText, self.thanLabLine
        ThanWinCom.destroy(self)
    def __del__(self): print "ThanEditWin", self, "is deleted"


###############################################################################
###############################################################################

def runmhk(pref):
    "Runs mhkex, provides mhkex with prefix, and returns the output of mhkex."

#---In Linux 2.4, python 2.3, if popen4 does not find the program,
#   it returns a shell error message that it didn't find the program:
#       /bin/sh: mhkex: command not found.
#   But, sometimes-not always, it reports IOError when the tomhk pipe
#   is closed. Thus the hack below.

    program = "mhkex"
    try:
        tomhk, fromhk = os.popen4(program)
        tomhk.write(pref+"\n")
        tomhk.close()
        dlines = fromhk.readlines()
        fromhk.close()
    except IOError:
        dlines = ["IOError: "+program+": not found"]
    for i,dline in enumerate(dlines):
        if sys.platform == "win32":
            dlines[i] = thanUnicode(dline.strip())
        else:
            dlines[i] = dline.strip()

    return dlines


###############################################################################
###############################################################################

if __name__ == "__main__":
    from edhelp import ver as thanvers
    root = ThanEditWinMain(title=thanvers.title, suffix=("Text files", ".txt"),
                           config=thanvers.name)
    root.mainloop()
    del root
