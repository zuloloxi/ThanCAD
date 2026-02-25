#!/usr/bin/python
from tkinter import Tk, Toplevel, Frame, Button, Label, Entry, SUNKEN, RAISED

from .thantkutila import thanGudModalMessage, thanGudAskOkCancel
from .thanval import ThanValidator, ThanValFloat, ThanValInt
from .thanwids import ThanEntry, ThanCheck, ThanChoice
from .thanwidstrans import T


##############################################################################
##############################################################################

class ThanData:
    "An abstract frame which accepts data."

    def __init__(self, vals, fraWid, cargo=None):
        self.thanCargo = cargo
        self.thanWidgetsCreate(fraWid)
        self.thanSet(vals)
        self.thanValsOri = self.thanGet()

    def thanSet(self, vs):
        for (tit,wid,vld),v in zip(self.thanWids,vs): wid.thanSet(v)

    def thanValidate(self):
        vs = []
        for tit,wid,vld in self.thanWids:
            vs.append(vld.thanValidate(wid.thanGet()))
            if vs[-1] is None:
                tit = '"%s":\n%s' % (tit, vld.thanGetErr())
                thanGudModalMessage(self, tit, T["Error in data"])
                wid.focus_set()
                return None
        return vs

    def thanGet(self):
        return [vld.thanGet(wid.thanGet()) for (tit,wid,vld) in self.thanWids]

    def thanWidgetsCreate(self, fra):
        "Creates data widgets."
        pass


##############################################################################
##############################################################################

class ThanDataFrame(Frame, ThanData):
    "A tkinter frame which accepts data."

    def __init__(self, vals, master, cargo=None, **kw):
        Frame.__init__(self, master, **kw)
        ThanData.__init__(self, vals, self, cargo)


##############################################################################
##############################################################################

class ThanDataForm(Toplevel, ThanData):
    "A tkinter form which accepts data."

    def __init__(self, vals, callerapply, master, cargo=None, **kw):
        self.thanCallerApply = callerapply

        Toplevel.__init__(self, master, **kw)
        self.protocol("WM_DELETE_WINDOW", self.thanCancel)
        fraWid = Frame(self, relief=SUNKEN, borderwidth=1)
        fraWid.grid(row=0, sticky="wesn")
        ThanData.__init__(self, vals, fraWid, cargo)
        fraBut = Frame(self)
        fraBut.grid(row=1, sticky="we")
        self.thanButtonsCreate(fraBut)
        for i in 0,: self.columnconfigure(i, weight=1)
        for i in 0,: self.rowconfigure(i, weight=1)

    def thanButtonsCreate(self, fra):
        "Creates OK, APPLY, CANCEL buttons."

        but = Button(fra, text=T["OK"], bg="lightgreen", activebackground="green", width=8, relief=RAISED, command=self.thanOk)
        but.grid(row=0, column=0)
        but = Button(fra, text=T["Apply"], bg="lightyellow", activebackground="yellow", width=8, relief=RAISED, command=self.thanApply)
        but.grid(row=0, column=1)
        but = Button(fra, text=T["Cancel"], bg="pink", activebackground="red", width=8, relief=RAISED, command=self.thanCancel)
        but.grid(row=0, column=2)
        for i in 0,1,2: fra.columnconfigure(i, weight=1)

    def thanOk(self, evt=None):
        if self.thanApply() == "break": return
        self.destroy()

    def thanApply(self, evt=None):
        v = self.thanValidate()
        if v is None: return "break"
        self.thanCallerApply(tuple(v))
        self.thanValsOri = v

    def thanCancel(self, evt=None):
        if self.thanGet() != self.thanValsOri:
            if not thanGudAskOkCancel(self,
               T["Values have changed.\nAbandon changes?"], T["WARNING"]):
                return "break"
        self.destroy()


##############################################################################
##############################################################################


class ThanDataGen(ThanDataForm):
    "A form which accepts data."

    def thanWidgetsCreate(self, fra):
        "Creates data widgets."
        self.title(T["MHK genetal data"])
        fs = T["HIGHWAY"], T["SEWAGE"], T["IRRIGATION"]
        wids = \
        ( (T["POSITION SCALE 1/"],    ThanEntry(fra), ThanValFloat(1e-6, 1e6)),
          (T["HEIGHT SCALE 1/"],      ThanEntry(fra), ThanValFloat(1e-6, 1e6)),
          (T["DRAW GRADE LINES"],     ThanCheck(fra), ThanValidator()),
          (T["HORIZONTAL CURVES"],    ThanCheck(fra), ThanValidator()),
          (T["MAIN FUNCTION"],        ThanChoice(fra, labels=fs, relief=RAISED), ThanValidator()),
          (T["DRAW VERTICAL SLOPES"], ThanCheck(fra), ThanValidator()),
          (T["TITLE IN EACH DRAWING"],ThanCheck(fra), ThanValidator()),
          (T["DRAW DRIVER LINES"],    ThanCheck(fra), ThanValidator()),
          (T["PAPER WIDTH (cm)"],     ThanEntry(fra), ThanValFloat(15, 1000)),
          (T["HORIZON MARGIN (cm)"],  ThanEntry(fra), ThanValFloat(0, 1000)),
          (T["MAIN GROUND LINE"],     ThanEntry(fra), ThanValInt(1, 50)),
          (T["MAIN GRADE LINE"],      ThanEntry(fra), ThanValInt(1, 50)),
          (T["NUMBER OF LINES"],      ThanEntry(fra), ThanValInt(1, 50))
        )

        i = -1
        for text,wid,v in wids:
            i += 1
            lab = Label(fra, text=text)
            lab.grid(row=i, column=0, sticky="e")
            s = "we"
            if isinstance(wid, ThanCheck) or isinstance(wid, ThanChoice): s = "w"
            wid.grid(row=i, column=1, sticky=s)

        self.thanWids = wids
        for i in 1,: fra.columnconfigure(i, weight=1)


##############################################################################
##############################################################################

if __name__ == "__main__" and 1:
    import sys
    def f(v): print(v)
    root = Tk()
    from tkinter import tkFont
    if sys.platform == "win32":
        fo = tkFont.Font(family="Arial", size=12)
        root.option_add("*font", fo)
    else:
        fo = tkFont.Font(family="Thorndale AMT", size=12)
#        fo = tkFont.Font(family="Vera", size=12)
        fo = tkFont.Font(family="4x6", size=12)
        print(fo)
        root.option_add("*font", fo)
    v = (1000.0, 100.0, 1, 1, 0, 1, 0, 0, 30.0, 1.5, 1, 2, 2)
    d = ThanDataGen(v, f, root, class_="ThanHigh")
    t = Entry()
    t.grid()
    root.mainloop()
    T.thanReport()
