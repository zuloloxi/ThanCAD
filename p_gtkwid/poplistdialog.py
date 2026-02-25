from tkinter import Listbox, Scrollbar, SINGLE, VERTICAL, END, ACTIVE
import p_ggen, p_gcol
from .thantksimpledialog import ThanDialog
from . import thanwids


class Listboxc(Listbox):  #Thanasis2024_06_28
    "A listbox with different background color for the active entry, when in single mode."

    def __init__(self, master, selectmode=SINGLE, **kw):
        super().__init__(master, selectmode=selectmode, **kw)
        if selectmode == SINGLE:
            self.bind("<Motion>", self.__onmotion)
            self.bind("<Key>", self.__format2)


    def __onmotion(self, evt):
        "As the user moves the mouse inside the list widget, the active entry is automatically updated."
        #print(evt.x, evt.y)
        #activate(f'@{evt.x},{evt.y}')
        i = self.nearest(evt.y)
        self.activate(i)
        self.itemconfigure(i, background="green")
        bg = self.cget("background")
        for j in range(self.size()):
            if j != i: self.itemconfigure(j, background=bg)


    def __format2(self, evt):
        "When the user cliks up or down arrow, the active entry is  is automatically updated."
        #self.update()
        #print(evt.keysym)
        if evt.keysym == "Up":
            i = self.index(ACTIVE)
            if i > 0: i -= 1
            #print(i)
        elif evt.keysym == "Down":
            i = self.index(ACTIVE)
            if i < self.size()-1: i += 1
            #print(i)
        else:
            return
        self.select_clear(0, END)  #This is needed as up and down arrows somehow select the entry
        self.activate(i)
        self.itemconfigure(i, background="green")
        bg = self.cget("background")
        for j in range(self.size()):
            if j == i: continue
            #print("j=", j)
            self.itemconfigure(j, background=bg)
        return "break"  #entry i is already actrivated: return break (or else it will move twice)


def test():
    "Test the Listboxc widget."
    from tkinter import Tk
    root = Tk()
    lb = Listboxc(root)
    lb.grid()
    lb.insert(END, "Thanasis")
    lb.insert(END, "Dimitra")
    lb.insert(END, "Andreas")
    lb.insert(END, "Stella")
    lb.focus_set()
    lb.activate(0)

    root.mainloop()



##############################################################################
##############################################################################

class ThanPoplist(ThanDialog):
    "Displays a popup window with a list of choices; cancel/ok buttons are not required."

    def __init__(self, master, val, width=20, height=10, selectmode=SINGLE, default=0, font=None, *args, **kw):
        "Extract initial draw order."
        self.__val = val
        self.__opts = dict(width=width, height=height)
        self.__selectmode = selectmode
        self.__default = default
        self.__font = font
#        self.result = None
        super().__init__(master, *args, **kw)


    def body(self, fra):
        "Create dialog widgets."
        if self.__font is not None: self.option_add("*%s*font" % (self.winfo_name(),), self.__font)
        self.__listForm(fra, 0, 0)
        self.__filist()
        return self.__li                      # This widget has the focus


    def __listForm(self, fra, ir, ic):
        "Creates and shows list."
        fra.columnconfigure(0, weight=1)
        fra.rowconfigure(0, weight=1)
        self.__li = Listboxc(fra, selectmode=self.__selectmode, exportselection=0)  #Thanasis2024_06_28
        self.__li.grid(row=ir, column=ic, sticky="wesn")
        sc = Scrollbar(fra, orient=VERTICAL, command=self.__li.yview)
#           Change the color of inactive indicator to the color of active indicator
#           because it was confusing to change color when you pressed the button
        sc.config(background=sc["activebackground"])
        sc.grid(row=ir, column=ic+1, sticky="sn")
        self.__li.config(yscrollcommand=sc.set)
        self.__li.bind("<Button-1>", lambda evt: self.__li.after(100, self.__onListClick))


    def __filist(self):
        "Fills the list with the user supplied values."
        self.__opts["height"] = min(self.__opts["height"], len(self.__val))
        self.__li.config(**self.__opts)
        for val in self.__val:
            self.__li.insert(END, p_ggen.thanUnicode(val))
        self.__li.activate(self.__default)
        del self.__opts, self.__default


    def buttonbox(self):
        "Do not display the default buttons in single mode."
        if self.__selectmode == SINGLE:
            self.bind("<Return>", self.__onListClick)
            self.bind("<Escape>", self.cancel)
        else:
            super().buttonbox()


    def __onListClick(self, evt=None):
        "Gets the chosen valure and returns it."
        if self.__selectmode == SINGLE: self.ok()


    def apply(self):
        "Gets the chosen value and returns it."
        indexes = self.__li.curselection()
        if len(indexes) < 1:
            i = self.__li.index(ACTIVE)
            self.result1 = [i]
            self.result = [self.__val[i]]
        else:
            self.result1 = [int(i) for i in indexes]
            self.result = [self.__val[i] for i in self.result1]
        if self.__selectmode == SINGLE:
            self.result = self.result[0]
            self.result1 = self.result1[0]
        del self.__val


    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
        del self.__li
        super().destroy()

#    def __del__(self):
#        print "ThanPoplist ThanDialog", self, "dies.."


##############################################################################
##############################################################################

class ThanPoplistCol(ThanDialog):
    "Displays a popup window with a list of choices in color; cancel/ok buttons are not required."

    def __init__(self, master, val, width=20, height=10, selectmode=SINGLE, *args, **kw):
        "Extract initial draw order."
        self.__val = val
        self.__opts = dict(width=width, height=height)
        self.__selectmode = selectmode
#        self.result = None
        super().__init__(master, *args, **kw)


    def body(self, fra):
        "Create dialog widgets."
        self.__listForm(fra, 0, 0)
        self.__filist()
        return self.__li                      # This widget has the focus


    def __listForm(self, fra, ir, ic):
        "Creates and shows list."
        fra.columnconfigure(0, weight=1)
        fra.rowconfigure(0, weight=1)
        self.__li = thanwids.ThanScrolledText(fra)
        self.__li.grid(row=ir, column=ic, sticky="wesn")


    def __filist(self):
        "Fills the list with the user supplied values."
        self.__opts["height"] = min(self.__opts["height"], len(self.__val))
        self.__opts.setdefault("cursor", "arrow")
        self.__li.config(**self.__opts)
        for name, col in self.__val:
            tag = "t%03d%03d%03d" % col
            if p_gcol.thanRgb2Gray(col) < 127: fg = "white"
            else:                              fg = "black"
            bg = p_gcol.thanFormTkcol % col
            self.__li.tag_config(tag, foreground=fg, background=bg)
            self.__li.tag_bind(tag, "<1>", lambda evt, name=name: self.__onclick(evt, name))
            self.__li.thanAppend(p_ggen.thanUnicode(name)+"\n", tag)
        del self.__opts


    def __filist2(self):
        "Fills the list with the user supplied values."
        self.__opts["height"] = min(self.__opts["height"], 2*len(self.__val))
        self.__opts.setdefault("cursor", "arrow")
        self.__li.config(**self.__opts)
        tt = self.__li.thanText
        for name, col in self.__val:
            if p_gcol.thanRgb2Gray(col) < 127: fg = "white"
            else:                              fg = "black"
            bg = p_gcol.thanFormTkcol % col
            but = thanwids.ThanButton(tt, width=20, height=1, anchor="e", text=name, foreground=fg, background=bg,
            activebackground="green", command=lambda name=name: self.__onclick(name))
            tt.window_create(END, window=but, align=BASELINE)
        del self.__opts


    def buttonbox(self):
        "Do not display the default buttons in single mode."
        if self.__selectmode == SINGLE:
            self.bind("<Return>", self.__onListClick)
            self.bind("<Escape>", self.cancel)
        else:
            super().buttonbox()

#    def __onListClickOld(self, evt=None):
#        "Gets the chosen valure and returns it."
#        indexes = self.__li.curselection()
#        if len(indexes) < 1: i = ACTIVE
#        else:                i = int(indexes[0])
#        self.result = self.__li.get(i)
#        self.ok()


    def __onclick(self, evt, name):
        "The user chose something."
        prg("ThanPoplistCol: user clicked: %s" % name)


    def __onListClick(self, evt=None):
        "Gets the chosen value and returns it."
        if self.__selectmode == SINGLE: self.ok()


    def apply(self):
        "Gets the chosen value and returns it."
        indexes = self.__li.curselection()
        print("ThanPopList: ACTIVE=", ACTIVE, "type=", type(ACTIVE))
        if len(indexes) < 1: self.result = [self.__val[self.__li.index(ACTIVE)]]
        else: self.result = [self.__val[int(i)] for i in indexes]
        if self.__selectmode == SINGLE: self.result = self.result[0]
        del self.__val


    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
        del self.__li
        super().destroy()

#    def __del__(self):
#        print "ThanPoplist ThanDialog", self, "dies.."


if __name__ == "__main__": test()
