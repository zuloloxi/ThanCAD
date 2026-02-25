import os, sys
from tkinter import *
from tkinter.font import Font
from p_gtkwid import *
import help
encoding="utf-8"


###############################################################################
###############################################################################

class ThanMhkWinMain(ThanWinMainCom):
    def factoryWin(self, *args, **kw): return ThanMhkWin("FMHK: ", *args, **kw)
    def thanMnuHelp(self): thanGudHelpWin(self, help.help, "Help about FMHK", font=_tfont)
    def thanMnuLicense(self): thanGudHelpWin(self, help.lic, "FMHK License", font=_tfont)
    def thanMnuAbout(self): thanGudHelpWin(self, help.about, "About FMHK", height=12, font=_tfont)


class ThanMhkWin(ThanWinCom):
    def factoryWin(self, *args, **kw): return ThanMhkWin("FMHK: ", *args, **kw)
    def __init__(self, *args, **kw):
        ThanWinCom.__init__(self, *args, **kw)
        menu = ThanMenu(self.thanMenuBar, tearoff=0)
        menu.add_command(label=T["&Produce drawing"], accelerator="F5", command=self.thanRun)
        self.thanMenuBar.insert_cascade(2, label=T["&Run"], underline=0, menu=menu)

        self.thanText = ThanText(self, width=80, height=25, insertbackground="lightgreen", font=_tfont)
        self.thanText.grid(sticky="wesn")

        fra = Frame(self)
        fra.grid(sticky="we")
        lab = Label(fra, text="Line")
        lab.grid(row=0, column=0, sticky="e")
        self.thanLabLine = Label(fra, text="1")
        self.thanLabLine.grid(row=0, column=1, sticky="e")
        fra.columnconfigure(0, weight=1)

        self.rowconfigure(1, weight=1)
        self.thanValOri = ""
        self._updateLine()

    def thanFocus1(self, evt=None):  # Overwrite to focus on a widget in window
        self.lift()
        self.thanText.focus_set()
    def thanFocus(self, evt=None):  # Overwrite to focus on a widget in window
        self.thanText.focus_set()
    def thanMerge(self, fr):
        self.thanValOri = fr.read()
        if sys.platform == "win32":
            self.thanText.thanSet(unicode(self.thanValOri, encoding))
        else:
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
    def thanRun(self):
        if not self.thanFileDefined or self.thanIsModified():
            thanGudModalMessage(self, T["Please save the data before you run the program."],
                                T["Data is not saved"])
            return
        f = os.path.abspath(self.thanFilnam)
        dlines = runmhk(f)
        tit = u"ΕΠΙΤΥΧΗΣ ΕΚΤΕΛΕΣΗ ΠΡΟΓΡΑΜΜΑΤΟΣ"
        if dlines[-1].strip() == tit:
            f = os.path.splitext(f)[0] + ".dxf"
            thanGudModalMessage(self, T["Drawing is saved in file "]+f, tit)
            return
        tit = u"ΑΝΕΠΙΤΥΧΗΣ ΕΚΤΕΛΕΣΗ ΠΡΟΓΡΑΜΜΑΤΟΣ"
        if dlines[-1].strip() == tit:
            if u"ΓΡΑΜΜΗ" in dlines[0]:
                lin = int(dlines[0].split()[-1][:-1])
                self.thanHighlit(lin)
                thanGudModalMessage(self, "\n".join(dlines[:-2]), tit)
                self.after(10000, self._clearRed)
            else:
                thanGudModalMessage(self, "\n".join(dlines[:-2]), tit)
        elif "Bad command" in dlines[-1] or "not found" in dlines[-1]:
            dlines.append("Program mhkex not found.")
            thanGudModalMessage(self, "\n".join(dlines), tit)
        else:
            thanGudModalMessage(self, "\n".join(dlines), tit)


    def thanMnuHelp(self): thanGudHelpWin(self, help.help, "Help about FMHK", font=_tfont)
    def thanMnuLicense(self): thanGudHelpWin(self, help.lic, "FMHK License", font=_tfont)
    def thanMnuAbout(self): thanGudHelpWin(self, help.about, "About FMHK", height=12, font=_tfont)


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
            dlines[i] = unicode(dline.strip(), encoding)
        else:
            dlines[i] = dline.strip()

    return dlines


###############################################################################
###############################################################################

if __name__ == "__main__":
    root = ThanMhkWinMain(title="FMHK 12.1.1", suffix=("MHK files", ".mhk"))
    if sys.platform == "win32":_tfont = Font(family="Courier New", size=10, weight=NORMAL)
    else: _tfont = Font(family="LiberationMono", size=10, weight=NORMAL)
    root.mainloop()
