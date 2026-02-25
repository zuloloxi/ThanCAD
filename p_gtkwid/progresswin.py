import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from .thantkutila import thanGudPosition


class ProgressWin:
    "A window which shows one or more progress bars which can be interrupted."

    def __init__(self, master, vmax, tit, width=400, height=None):
        "Create the window."
        self.win = tk.Toplevel(master)
        thanGudPosition(self.win, master)
        self.win.title(tit)
        try: vmax[0]
        except: vmax = [vmax]
        if height is None: height = len(vmax)*70
        self.win.geometry('{}x{}'.format(width, height))
        self.vmax = vmax
        self.stopComputation = False
        self.makeWidgets()
        self.win.protocol("WM_DELETE_WINDOW", self.cancel)

    def setMaximum(self, vmax, i=0):
        "Set the maximum of progressbar u."
        self.pro[i].config(maximum=vmax)

    def start(self, fun, *args):
        "Start the computation."
        self.win.update()
        self.win.grab_set()
        try:
            r=fun(*args)
        finally:
            self.win.grab_release()
        return r


    def update(self, ival, i=0):
        "Set a value to the progress bar."
        self.pro[i].config(value=ival)
        self.win.update()


    def cancel(self):
        "Confirm and cancel."
        if not self.ok2quit(): return
        self.stopComputation = True


    def ok2quit(self):
        "The user wants to cancel; ask for confirmation."
        ok = mb.askokcancel(title="Computation in progress", message="OK to stop computation?",
            default="cancel", parent=self.win)
        if ok: return True
        else: return False


    def destroy(self):
        "Break circular references."
        del self.pro
        self.win.grab_release()
        self.win.destroy()
        del self.win


    def makeWidgets(self):
        "Create the widgets of the window."
        #s = ttk.Style()
        #s.theme_use("default")
        #s.configure("TProgressbar", thickness=50)
        self.pro = []
        ir = -1
        for i in range(len(self.vmax)):
            if i > 0:
                ir += 1
                lab = tk.Label(self.win, text="", font="Arial4")
                lab.grid(row=ir, column=0)
            ir += 1
            pro1 = ttk.Progressbar(self.win, maximum=self.vmax[i], orient=tk.HORIZONTAL, length=200, mode='determinate')
            pro1.grid(row=ir, column=0, sticky="wesn")
            self.pro.append(pro1)
        ir += 1
        but = ttk.Button(self.win, text="Cancel", command=self.cancel)
        but.grid(row=ir, column=0)
        self.win.columnconfigure(0, weight=1)
        for i in range(0, ir, 2):
            self.win.rowconfigure(i, weight=1)
