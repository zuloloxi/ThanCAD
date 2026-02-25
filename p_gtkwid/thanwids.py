import bisect, time
from tkinter import (Menu, Listbox, Menubutton, Scrollbar, Checkbutton,
    Frame, Radiobutton, Button, Text, Entry, Label,
    IntVar, Toplevel,
    END, SINGLE, EXTENDED, RAISED, GROOVE, SUNKEN, FLAT, HORIZONTAL, VERTICAL,
    BASELINE, SEL, ACTIVE, NORMAL, DISABLED,  W)
from tkinter.messagebox import ERROR
from p_ggen import thanUnicode, thanUnunicode, prg, path, Struct, rdict
import p_gcol
from .thantkutila import (thanGudGetSaveFile, thanGudGetReadFile,
    thanGudGetDir, thanGudOpenSaveFile, thanAbsrelPath, thanGudPosition,
    thanGudModalMessage as mm, correctForeground, blackorwhite)
from .thantkutilb import thanFontRefSave
from .thanwidstrans import T


class ThanMenu(Menu):
    """A menu that shows status when a user interacts with it.

    If function condition is set, this function is checked before
    a menu action. If condition() returns False, no action is taken.
    The keyword "help" provides the status text for each menu entry.
    A character which is prepended by &, is underlined.
    """

    def __init__(self, master, *args, **kw):
        try: self.__condition = master.__condition
        except: self.__condition = None
        if "condition" in kw: self.__condition = kw.pop("condition")

        try: self.__stat = master.__stat
        except: self.__stat = None
        if "statcommand" in kw: self.__stat = kw.pop("statcommand")

        kw["tearoff"] = False

        Menu.__init__(self, master, *args, **kw)

        if self.__stat is not None:
            self.bind("<Motion>", self.__onmotion)
            self.bind("<Leave>", lambda evt, s=self.__stat: s(""))
            self.__ypos = None
        self.__statText = []

    def __onmotion(self, evt):
        if self.__ypos is None:
            yp = [self.yposition(0)]
            if yp[0] == 0: return
            for i in range(1, 100):
                yp1 = self.yposition(i)
                if yp1 == yp[-1]: break
                yp.append(yp1)
            self.__ypos = yp
        i = bisect.bisect_left(self.__ypos, evt.y) - 1
        self.__stat(self.__statText[i])


    def add(self, itemType, cnf=None, **kw):
        if cnf is None: cnf = {}
        i = self.index(END)
        if i is None: i = -1
        assert i == len(self.__statText)-1, "Index missing in ThanMenu!!"
        cnf.update(kw)
        self.__statText.append(cnf.pop("help", ""))
        cnf = self.__entryparse(cnf)
        self.__correctForeground(itemType, cnf)   #Thanasis2021_09_26
        Menu.add(self, itemType, cnf)


    def insert(self, index, itemType, cnf=None, **kw):
        if cnf is None: cnf = {}
        i = index - 1
        assert i < len(self.__statText), "Index missing in ThanMenu!!"
        cnf.update(kw)
        self.__statText.insert(i, cnf.pop("help", ""))
        cnf = self.__entryparse(cnf)              #Thanasis2021_09_26
        self.__correctForeground(itemType, cnf)   #Thanasis2021_09_26
        Menu.insert(self, index, itemType, cnf)   #Thanasis2021_09_26


    def __len__(self):
        "Return the number of entries in the menu (command, separator, submenu etc)."
        n = self.index(END)  #This is the last index; because the first index is zero,
        if n is None: return 0  #This is before tk has had a chance to intialize
        return n+1           #the total number of entries is n+1


    def delete(self, index1, index2=None):
        i1 = index1
        if index2 is None:  i2 = i1 + 1
        elif index2 == END: i2 = len(self.__statText)
        else:               i2 = index2+1     # Tkinter deletes index1:index2 (INCLUDING index2)
        del self.__statText[i1:i2]
        self.__ypos = None
        super().delete(index1, index2)


    def entryconfig(self, index, **kw):
        if "help" in kw: self.__statText[index-1] = kw.pop("help")
        return Menu.entryconfig(self, index, **self.__entryparse(kw))


    def __entryparse(self, kw):
        "Extracts configuration commands that apply to ThanMenu (but not Menu)."
        lab = kw.get("label")
        if lab is not None:
            i = lab.find("&")
            if 0 <= i < len(lab)-1:
                kw["label"] = thanUnicode(lab.replace("&", "", 1))
                kw.setdefault("underline", i)
            else:
                kw["label"] = thanUnicode(lab)
        if self.__condition is not None and "command" in kw:
            kw["command"] = lambda c=kw["command"]: self.__checkCommand(c)
        return kw


    def __checkCommand(self, fun):
        "Makes an action only if __condition() allows it."
        if self.__condition(): fun()


    def destroy(self):
        "Breaks circular references."
        self.__stat = self.__condition = None  #2008_09_12: Python 2.6rc1 calls destroy and..
        self.unbind("<Motion>")                #.. then entryconfig which accesses __condition!!
        self.unbind("<Leave>")
        #self.delete(0, END)   #Thanasis2018_05_09:Probably Menu.destroy() calls delete(), thus if we call it here it crashes
        Menu.destroy(self)

    def __del__(self): print("ThanMenu", self, "is deleted")

    def __correctForeground(self, itemType, kw):  #Thanasis2021_09_26
        "Correct foregound color for menus, according to background color."
        if itemType in ("separator",): return
        for act in "", "active":
            fg = kw.pop(act+"fg", None)
            if fg is None: fg = kw.get(act+"foreground", None)
            fgcol = self.__correct1(fg, act+"background")
            kw[act+"foreground"] = fgcol

    def __correct1(self, fg, bg="background"):
        if fg is None:
            return blackorwhite(self, bg)   #This may be None
        fgcol = blackorwhite(self, bg="background")   #This may be None
        if fgcol is None:
            return fg    #Could not decipher background; return original color
        elif fgcol == "white":
            if fg in ("red",  "darkred"):  return "pink"
            if fg in ("blue", "darkblue"): return "lightblue"
            return fg     #Uknown color; return original color
        else:
            if fg in ("red", "pink"):       return "darkred"
            if fg in ("blue", "lightblue"): return "darkblue"
            return fg     #Uknown color; return original color



def thanTkGuiCreateMenus(self, mlist):
    """Create the menus described in list mlist=thanGetMenus().

    mlist is a list of tuples m with 3 values:
    m[0] = function to call when menu is activated
    m[1] = name of the menu
    m[2] = description of the menu
    m[3] = foreground color
    m[4] = name of Tk object (if == 'help' then it is rendered at far right)
    If m[0] is None and m[1] == '-' then this is a separator
    If m[0] is None and m[1] <> '-' then a new menu with name
                                    m[1] is to be created.
    """
    from string import replace
#---At first do some initialisation
#    self.CreateStatusBar()
    menuBar = Menu(self, activebackground="green")
#---Process mlist
    menu = menuDesc = None
    for m in mlist:
#-------Normal Menu entry
        if len(m) > 3: fg = m[3]
        else         : fg = None
        if m[0] is not None:
            menu.add_command(label=thanUnicode(replace(m[1], "&", "")), foreground=fg,
                             command=m[0])           # Create menu entry
#-------Separator entry
        elif m[1] == "-":
            menu.add_separator()
#-----------New menu: at first add old menu in menubar
        else:
            if menu is not None: menuBar.add_cascade(label=thanUnicode(menuDesc), menu=menu)
            menu = Menu(menuBar, activebackground="green", foreground=fg, tearoff=0)
            menuDesc = replace(m[1], "&", "")

    if menu is not None: menuBar.add_cascade(label=thanUnicode(menuDesc), menu=menu)
    self.config(menu=menuBar)

def thanTkCreateThanMenus(self, mlist, statcommand=None, condition=None):
    """Create the menus described in list mlist=thanGetMenus().

    mlist is a list of tuples m with 3 values:
    m[0] = function to call when menu is activated
    m[1] = name of the menu
    m[2] = description of the menu
    m[3] = foreground color
    m[4] = Tk name: if name=="help" then it is rendered at far right
    If m[0] is None and m[1] == '-' then this is a separator
    If m[0] is None and m[1] <> '-' then a new menu with name
                                    m[1] is to be created.
    If function condition is set, this function is checked before
    a menu action. If condition() returns False, no action is taken.
    """
    menuBar = ThanMenu(self, activebackground="green", statcommand=statcommand, condition=condition)
    submenus = {}
    menu = menuDesc = menuHelp = None
    for m in mlist:
        if len(m) > 3: fg = m[3]
        else         : fg = None
        if m[0] is not None:   # Normal Menu entry
            menu.add_command(label=m[1], command=m[0], help=m[2], foreground=fg)   # Create menu entry
        elif m[1] == "-":  # Separator entry
            menu.add_separator()
        else:              # New menu: at first add old menu in menubar
            if menu is not None:
                menuBar.add_cascade(label=menuDesc, menu=menu, help=menuHelp, foreground=fg)
            menuDesc = m[1]
            menuHelp = m[2]
            if len(m) > 4: name = m[4]
            else         : name = None
            menu = ThanMenu(menuBar, name=name, activebackground="green", tearoff=0, statcommand=statcommand, condition=condition)
            submenus[menuDesc.replace("&", "")] = menu

    if menu is not None:
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
    menuBar = ThanMenu(self, activebackground="green", statcommand=statcommand, condition=condition)
    submenus = {}
    i = 0
    while i < len(mlist):
        if mlist[i][0] == "menu":
            i = __menu(mlist, menuBar, i, statcommand, condition, submenus)
        else:
            raise ValueError("Element %s of mlist should mark the beginning of a menu" % i)
        i += 1
    self.config(menu=menuBar)
    return menuBar, submenus

def __menu(mlist, menuBar, i, statcommand, condition, submenus):
    "Create a (sub)menu."
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
                raise ValueError("ThanMenu label: %s\nA callable was expected, but type %s was found: %s" % (m[1], type(m[0]), m[0]))
            if len(m) > 3: fg = m[3]    # Create normal menu entry
            else         : fg = None
            menu.add_command(label=m[1], command=m[0], help=m[2], foreground=fg)   # Create normal menu entry
        i += 1
    else:
        i = len(mlist)
    menuBar.add_cascade(label=menuDesc, menu=menu, help=menuHelp, foreground=menuFg)
    submenus[menuDesc.replace("&", "")] = menu
    return i


##############################################################################
##############################################################################

class ThanListbox(Listbox):
    "A standard listbox with thanSet/thanGet."

    def __init__(self, *args, **kw):
        "Save selection mode."
        self.__selectmode = kw.get("selectmode", SINGLE)
        super().__init__(*args, **kw)
        if "fg" not in kw and "foreground" not in kw: correctForeground(self)   #Thanasis2024_06_28

    def thanGetitem(self, *args): return self.get(*args)

    def thanInsert(self, i, items): self.insert(i, items)

    def thanAppend(self, items):
        "Append new values to the end of the listbox."
        self.insert(END, items)

    def thanSetitems(self, items):
        "Empty list and set new values to the listbox."
        self.delete(0, END)
        for item in items:
            self.insert(END, item)


    def thanSet(self, indexm):
        "Set selected indexes."
        self.select_clear(0, END)
        isiterable = False
        try:
            iter(indexm)
            isiterable = True
        except:
            pass
        if isiterable:
            for i in indexm: self.select_set(i)
        else:
            self.select_set(indexm)


    def thanGet(self):
        "Gets the chosen value and returns it."
        indexes = self.curselection()
        if len(indexes) < 1:
            result = [ self.index(ACTIVE) ]   #Tranform index to integer
        else:
            result = [self.index(i) for i in indexes]  #Tranform indexes to integer
        if self.__selectmode == SINGLE: return result[0]
        else:                           return result


##############################################################################
##############################################################################

class ThanChoice(Menubutton):
    "A widget that lets the user choose one of predetermined choices."

    def __init__(self, master, **kw):
        Menubutton.__init__(self, master)
        self.thanMenu = Menu(self, tearoff=0, activebackground="green")
        self["menu"] = self.thanMenu                #Thanasis2009_10_27
        kw.setdefault("labels", ("",))
        kw.setdefault("command", lambda i, lab: None)
        kw.setdefault("width", 10)
        kw.setdefault("relief", RAISED)
        kw.setdefault("anchor", "w")
        if "bg" not in kw and "background" not in kw: kw["bg"] = "lightcyan"
        kw.setdefault("activebackground", "cyan")
        self.thanChoice = 0
        self.config(**kw)
        if "fg" not in kw and "foreground" not in kw: correctForeground(self)

    def config(self, **kw):
        "Adds labels and command support to standard config, and propagates some attributes to menu."
        try: self.thanCommand = kw["command"]
        except KeyError: pass
        else: del kw["command"]

        try: self.thanLabels = tuple(kw["labels"])
        except KeyError: pass
        else:
            del kw["labels"]
            m = Menu(self, tearoff=0, activebackground="green")
            self["menu"] = m
            self.thanMenu.destroy()
            self.thanMenu = m

            for i,key in enumerate(self.thanLabels):
                m.add_command(label=thanUnicode(key), command=lambda i=i: self.__set(i))
            self.thanChoice = 0
            Menubutton.config(self, text=thanUnicode(self.thanLabels[0]))

        if "relief" in kw: kw.setdefault("borderwidth", 1)
        Menubutton.config(self, **kw)
        self.thanMenu.config(**rdict(kw, "font", "class_"))

    def thanSet(self, i):
        i = int(i)
        self.thanChoice = i
        Menubutton.config(self, text=thanUnicode(self.thanLabels[i]))

    def thanSetText(self, t):
        for i,key in enumerate(self.thanLabels):
            if key == t: break
        else: raise IndexError(t)
        self.thanChoice = i
        Menubutton.config(self, text=thanUnicode(key))

    def __set(self, i):
        self.thanChoice = i
        Menubutton.config(self, text=thanUnicode(self.thanLabels[i]))
        self.thanCommand(i, self.thanLabels[i])

    def thanGet(self): return self.thanChoice

    def thanGetText(self): return thanUnunicode(self.thanLabels[self.thanChoice])

    def destroy(self):
#        print "ThanChoice", self, "destroy called"
        self.thanMenu.destroy()
        del self.thanMenu, self.thanCommand, self.thanChoice
        Menubutton.destroy(self)

#    def __del__(self): print "ThanChoice", self, "is deleted"


class ThanChoiceRef(Menubutton):
    """A widget that lets the user choose one of predetermined choices.

    The widget sets and gets references of objects, but shows
    user defined labels instead."""

    def __init__(self, master, **kw):
        Menubutton.__init__(self, master)
        self.thanMenu = Menu(self, tearoff=0)
        self["menu"] = self.thanMenu                #Thanasis2009_10_27
        kw.setdefault("objects", (("",""),))
        kw.setdefault("command", None)
        kw.setdefault("width", 10)
        kw.setdefault("relief", RAISED)
        kw.setdefault("anchor", "w")
        if "bg" not in kw and "background" not in kw: kw["bg"] = "lightcyan"
        kw.setdefault("activebackground", "cyan")
        self.thanChoice = 0      #chosen index
        self.config(**kw)
        if "fg" not in kw and "foreground" not in kw: correctForeground(self)

    def config(self, **kw):
        "Adds objects and command support to standard config, and propagates some attributes to menu."
        if "command" in kw: self.thanCommand = kw.pop("command")
        if "objects" in kw:
            self.thanObjs = kw.pop("objects")
            m = Menu(self, tearoff=0)
            self["menu"] = m
            self.thanMenu.destroy()
            self.thanMenu = m

            for i,(obj, text) in enumerate(self.thanObjs):
                m.add_command(label=thanUnicode(text), command=lambda i=i: self.__set(i))
            self.thanChoice = 0
            Menubutton.config(self, text=thanUnicode(self.thanObjs[0][1]))

        if "relief" in kw: kw.setdefault("borderwidth", 1)
        Menubutton.config(self, **kw)
        self.thanMenu.config(**rdict(kw, "font", "class_"))

    def thanSet(self, obj):
        "Set object."
        for i, (o,t) in enumerate(self.thanObjs):
            if obj == o: break
        else:
            assert 0, "ThanChoiceRef: Object %s not in predetermined choices." % (obj,)
        self.thanChoice = i
        Menubutton.config(self, text=thanUnicode(t))

    def thanSetIndex(self, i):
        "set object by its index."
        o, t = self.thanObjs[i]              #This may raise IndexError
        self.thanChoice = i % len(self.thanObjs)
        Menubutton.config(self, text=thanUnicode(t))

    def __set(self, i):
        "Sets index and call command when user clicks."
        o, t = self.thanObjs[i]
        self.thanChoice = i
        Menubutton.config(self, text=thanUnicode(t))
        if self.thanCommand is not None: self.thanCommand(i, o, t)

    def thanGet(self):
        "Returns the chosen object."
        return self.thanObjs[self.thanChoice][0]

    def thanGetIndex(self):
        "Returns the index of the chosen object."
        return self.thanChoice

    def destroy(self):
        "Break circular references."
        self.thanMenu.destroy()
        del self.thanMenu, self.thanCommand, self.thanChoice, self.thanObjs
        Menubutton.destroy(self)

    def __del__(self):print("ThanChoiceRef", self, "is deleted")

##############################################################################
##############################################################################

class ThanYesno(ThanChoice):
    "Choice of yes or no."

    def __init__(self, master, **kw):
        kw["labels"] = T["Yes"], T["No"]
        kw.setdefault("width", 3)
        ThanChoice.__init__(self, master, **kw)

    def thanSet(self, i):
        "Set the value according to boolean i."
        if i: ThanChoice.thanSet(self, 0)
        else: ThanChoice.thanSet(self, 1)

    def thanGet(self):
        "Get the value as boolean."
        if self.thanChoice == 0: return True
        else: return False


class ThanCheckold(Checkbutton):
    "A Tkinter Checkbutton with ThanSet/ThanGet support and color correction."

    def __init__(self, *args, **kw):
        "Automatically create control variable if one does not exist."
        if "variable" in kw:
            print("You can avoid the hassle of defining a control variable:")
            print("ThanCheck automatically creates private control variable, if not defined!")
            self.thanVar = kw["variable"]
        else:
            self.thanVar = IntVar()
            kw["variable"] = self.thanVar

        self.thanCommand = kw.get("command")   #Get a reference to the user defined command (or None)

        super().__init__(*args, **kw)

        if "fg" not in kw and "foreground" not in kw:
            correctForeground(self)  #This color correction for the text of the button
        if "selectcolor" not in kw:
            bgcol = self.cget("background")  #This is for the correction of the background...
            #print("ThanCheck: bgcol=", bgcol)
            self.config(selectcolor=bgcol)   #...color of the indicator: selectcolor is the ...
                                             #...background for the indicator (at least in SuSE/Linux)
                                             #The foreground of indicator is the foreground of the text
            self.update_idletasks()

    def thanSet(self, val):
        """Set the value as bool.

        Curiously the user defined command is not invoked, so we invoke it here explicitely."""
        self.thanVar.set(bool(val))
        if self.thanCommand: self.thanCommand()     #Invoke command if it exists

    def thanGet(self):
        "Get the value as bool."
        return bool(self.thanVar.get())

    def config(self, **kw):
        if "command" in kw: self.thanCommand = kw["command"]
        super().config(**kw)

    def destroy(self):
        "Make sure that all new class variable are deleted."
        del self.thanVar, self.thanCommand
        super().destroy()


class ThanCheck(Frame):
    "A Tkinter Checkbutton with label as text."

    def __init__(self, *args, **kw):
        "Automatically create control variable."
        if "variable" in kw:
            print("You can avoid the hassle of defining a control variable:")
            print("ThanCheck automatically creates private control variable, if not defined!")
            self.thanVar = kw["variable"]
        else:
            self.thanVar = IntVar()
            kw["variable"] = self.thanVar

        #kw.setdefault("relief", SUNKEN)  #Thanasis2023_06_22: relief is not needed for checkbutton (it is needed for radio buttons)
        #if "relief" in kw: kw.setdefault("borderwidth", 1)
        super().__init__(*args)

        self.thanChk = Checkbutton(self)
        self.thanChk.grid(row=0, column=0, sticky="w")
        self.thanLab = Label(self)
        self.thanLab.grid(row=0, column=1, sticky="w")

        self.config(**kw)
        self.columnconfigure(1, weight=1)

        if "fg" not in kw and "foreground" not in kw:
            correctForeground(self.thanChk)  #This color correction for the checkbutton
            correctForeground(self.thanLab)  #This color correction for the text of the button
        if "selectcolor" not in kw:
            bgcol = self.cget("background")  #This is for the correction of the background...
            #print("ThanCheck: bgcol=", bgcol)
            self.thanChk.config(selectcolor=bgcol)   #...color of the indicator: selectcolor is the ...
                                             #...background for the indicator (at least in SuSE/Linux)
                                             #The foreground of indicator is the foreground of the text
            self.update_idletasks()

        self.thanLab.bind("<Button-1>", self.__onclick)


    def __onclick(self, evt):
        "Label was clicked: -> toggle checkbutton."
        self.toggle()


    def configure(self, *args, **kw):
        "Apply different options to different widgets."
        kwf = {}
        for key in "relief", "borderwidth":
            if key in kw: kwf[key] = kw.pop(key)
        super().config(**kwf)

        kwf = {}
        for key in "text", "font", "justify", "anchor", "wraplength", "underline":
            if key in kw: kwf[key] = kw.pop(key)
        self.thanLab.config(**kwf)

        kwf = {}
        for key in "command", "variable":
            if key in kw: kwf[key] = kw.pop(key)
        self.thanChk.config(**kwf)

        #The remaining options are for both label and checkbutton
        self.thanChk.config(*args, **kw)
        self.thanLab.config(*args, **kw)


    config = configure   #Code from Base class of all widgets
    def cget(self, key):
        """Return the resource value for a KEY given as string."""
        if key in ("relief", "borderwidth"):
            return super().cget(key)
        elif key in ("text", "font", "justify", "anchor", "wraplength", "underline"):
            return self.thanLab.cget(key)
        else:
            return self.thanChk.cget(key)       #thus we get it from the first child

    __getitem__ = cget   #Code from Base class of all widgets
    #def __setitem__(self, key, value):  #Code from Base class of all widgets
    #    self.configure({key: value})


    def toggle(self):
        "Toggle, and call command it it exists."
        self.thanChk.invoke()   #Note that invoke() toggles the checkbutton, and also calls the command


    def thanSet(self, val):
        """Set the value as bool.

        Curiously the user defined command is not invoked, so we invoke it here explicitely."""
        self.thanVar.set(not bool(val))   #Trick: because invoke toggles the checkbutton. It does not call the command.
        self.thanChk.invoke()   #Note that invoke() toggles the checkbutton, and also calls the command


    def thanGet(self):
        "Get the value as bool."
        return bool(self.thanVar.get())


    def destroy(self):
        "Make sure that all new class variable are deleted."
        del self.thanVar, self.thanChk, self.thanLab
        super().destroy()


class ThanRadio(Frame):
    "A Tkinter Radiobutton with ThanSet/ThanGet support."

    def __init__(self, *args, **kw):
        "Automatically create control variable."
        self.thanVar = IntVar()
        self.ival = 0
        self.thanChildren = []
        kw.setdefault("relief", SUNKEN)
        if "relief" in kw: kw.setdefault("borderwidth", 1)
        Frame.__init__(self, *args, **kw)

    def add_button(self, *args, **kw):
        assert "variable" not in kw, "ThanRadio automatically creates private control variable!"
        kw["variable"] = self.thanVar
        kw["value"] = self.ival
        self.ival += 1
        rad = Radiobutton(self, *args, **kw)
        self.thanChildren.append(rad)

        if "fg" not in kw and "foreground" not in kw:
            correctForeground(rad)  #This color correction for the text of the button
        if "selectcolor" not in kw:
            bgcol = self.cget("background")  #This is for the correction of the background...
            #print("ThanCheck: bgcol=", bgcol)
            self.config(selectcolor=bgcol)   #...color of the indicator: selectcolor is the ...
                                             #...background for the indicator (at least in SuSE/Linux)
                                             #The foreground of indicator is the foreground of the text
            self.update_idletasks()

        return rad

    def configure(self, *args, **kw):
        "Keep something for Frame and propagate the rest to children."
        kwf = {}
        for key in "relief", "borderwidth":
            if key in kw: kwf[key] = kw.pop(key)
        Frame.config(self, **kwf)
        for rad in self.thanChildren:
            rad.config(*args, **kw)

    config = configure   #Code from Base class of all widgets
    def cget(self, key):
        """Return the resource value for a KEY given as string."""
        if key in ("relief", "borderwidth"):
            return super().cget(key)
        if len(self.thanChildren) > 0:
            rad = self.thanChildren[0] #All children have the same attribute values,
            return rad.cget(key)       #thus we get it from the first child
        else:
            return None   #No children yet -> no attribute value

    __getitem__ = cget   #Code from Base class of all widgets
    #def __setitem__(self, key, value):  #Code from Base class of all widgets
    #    self.configure({key: value})


    def thanSet(self, val):
        "Set the value as integer."
        self.thanVar.set(int(val))

    def thanGet(self):
        "Get the value as integer."
        return int(self.thanVar.get())

    def destroy(self):
        "Make sure that all new class variables are deleted."
        del self.thanChildren, self.thanVar
        Frame.destroy(self)


##############################################################################
##############################################################################

class ThanCombo(Frame):
    "A widget that lets the user choose one of predetermined choices or write a text."

    def __init__(self, master, buttontext="...", **kw):
        Frame.__init__(self, master)
        readonly = kw.pop("readonly", False)
        if readonly: self.thanText = ThanLabel(self)
        else:        self.thanText = ThanEntry(self)
        self.thanText.grid(row=0, column=0, sticky="ew")
        self.thanMenubutton = Menubutton(self, text=buttontext, relief=FLAT, padx=0, pady=0,
            bg="lightcyan", activebackground="cyan")
        self.thanMenubutton.grid(row=0, column=1, sticky="w")
        self.thanMenu = Menu(self.thanMenubutton, tearoff=0)
        kw.setdefault("labels", ("",))
        kw.setdefault("command", lambda i, lab: None)
        kw.setdefault("width", 10)
        self.config(**kw)
        self.columnconfigure(0, weight=1)

    def config(self, **kw):
        "Adds labels and command support to standard config, and propagates some attributes to menu."

        try: self.thanCommand = kw["command"]
        except KeyError: pass
        else: del kw["command"]

        try: self.thanLabels = tuple(kw["labels"])
        except KeyError: pass
        else:
            del kw["labels"]
            m = Menu(self.thanMenubutton, tearoff=0)
            self.thanMenubutton["menu"] = m
            self.thanMenu.destroy()
            self.thanMenu = m
            for i,key in enumerate(self.thanLabels):
                m.add_command(label=thanUnicode(key), command=lambda i=i: self.__comboSet(i))
            self.__comboSet(0)

        if "relief" in kw: kw.setdefault("borderwidth", 1)
        Frame.config(self, **rdict(kw, "relief", "borderwidth", "class_"))
        self.thanText.config(      **rdict(kw, "state", "font", "width", "class_"))
        self.thanMenubutton.config(**rdict(kw, "state", "font", "class_", "bg", "background"))
        self.thanMenu.config(      **rdict(kw, "font", "class_"))

    def __comboSet(self, i):
        "Set predefined entry; call callback with index and text."
        self.thanChoice = i
        self.thanText.thanSet(self.thanLabels[i])
        self.thanCommand(i, self.thanLabels[i])

    def thanSet(self, t):
        "Sets a, possibly not predfined text; call callback without index."
        self.thanText.thanSet(thanUnicode(t))
        self.thanCommand(None, self.thanGet())   #Previous thanset may transform something

    def thanGet(self):
        "Return the text of the combo box."
        return thanUnunicode(self.thanText.thanGet())

    def destroy(self):
        "Break circular references."
#        print "ThanCombo", self, "destroy called"
        del self.thanMenu, self.thanMenubutton, self.thanText
        Frame.destroy(self)

    def __del__(self):
        "For debugging."
        print("ThanCombo", self, "is deleted")


##############################################################################
##############################################################################

class ThanFile(Frame):
    """A widget which lets the user choose a file.

    The initialdir is given only at widget creation time. If it
    is blank then the current directory is assumed (note that path("").abspath()
    will give the current directory.
    The filename will be shown in the widget as relative to this initialdir,
    or as absolute path if it is not within initialdir (and its subdirs).
    The filename returned by thanGet() is always the absolute path of the file.
    An exception of the above rules is that if a filename is blank, it remains blank.
    """

    def __init__(self, master, initialdir="", readonly=False, buttontext="...", **kw):
        kw.setdefault("text", ".")               # Current directory
        kw.setdefault("extension", ".txt")
        kw.setdefault("mode", "r")
        kw.setdefault("title", "")
        kw.setdefault("command", None)
        kw.setdefault("beforeopen", None)
        kw.setdefault("width", 10)
        self.initialdir = path(initialdir).abspath()
#        print "ThanFile:initialdir=", self.initialdir
        try: self.initialdir.chdir()     #Try to change to this directory
        except OSError as e: print(str(e))
        super().__init__(master)
        if readonly: self.thanText = ThanLabel(self, justify="right")
        else:        self.thanText = ThanEntry(self, justify="right")
        self.thanText.grid(row=0, column=0, sticky="ew")
        #self.thanMenubutton = Button(self, text=buttontext, relief=FLAT, padx=0, pady=0,
        #    bg="lightcyan", activebackground="cyan", command=self.thanOpen)
        self.thanMenubutton = ThanButton(self, text=buttontext, relief=FLAT, padx=0, pady=0, command=self.thanOpen)
        self.thanMenubutton.grid(row=0, column=1, sticky="w")
        self.config(**kw)
        self.columnconfigure(0, weight=1)


    def configure(self, **kw):
        "Adds labels and command support to standard config, and propagates some attributes to menu."
        if "extension"  in kw: self.thanExt = kw.pop("extension")
        if "mode"       in kw: self.thanMode = kw.pop("mode")
        if "title"      in kw: self.thanTitle = kw.pop("title")
        if "command"    in kw: self.thanCommand = kw.pop("command")
        if "beforeopen" in kw: self.thanBeforeopen = kw.pop("beforeopen")
        if "relief"     in kw: kw.setdefault("borderwidth", 1)
        super().config(      **rdict(kw, "relief", "borderwidth", "class_"))
        self.thanText.config(**rdict(kw, "text", "state", "font", "width", "bg", "background", "foreground", "fg", "class_"))
        if "textvariable" in kw and isinstance(self.thanText, ThanEntry): self.thanText.config(textvariable=kw["textvariable"])
        self.thanMenubutton.config(**rdict(kw, "state", "font", "class_"))
        if "text"       in kw: self.thanSet(kw.pop("text"))


    config = configure   #Code from Base class of all widgets
    def cget(self, key):
        """Return the resource value for a KEY given as string."""
        if key == "extension":  return self.thanExt
        if key == "mode":       return self.thanMode
        if key == "title":      return self.thanTitle
        if key == "command":    return self.thanCommand
        if key == "beforeopen": return self.thanBeforeopen
        if key in ("relief", "borderwidth", "class_"):
            return super().cget(key)
        elif key in ("text", "state", "font", "width", "bg", "background", "foreground", "fg", "class_"):
            return self.thanText.cget(key)
        else:
            return None   #No children yet -> no attribute value

    __getitem__ = cget   #Code from Base class of all widgets
    #def __setitem__(self, key, value):  #Code from Base class of all widgets
    #    self.configure({key: value})



    def thanOpen(self):
        "Prompt the user to search for the filename; it may be overwritten."
        print("thanwids: ThanFile: thanOpen(): extension=", self.thanExt)
        filnam = self.thanGet()              #This is absolute path or ""
        par = path("")
        if filnam != "": par = filnam.parent
        if self.thanBeforeopen is not None and not self.thanBeforeopen(filnam): return
        if self.thanMode == "r":
            filnam = thanGudGetReadFile(self, self.thanExt, self.thanTitle,
                initialdir=par, initialfile=filnam.basename())
        elif self.thanMode == "w":
            filnam = thanGudGetSaveFile(self, self.thanExt, self.thanTitle,
                initialdir=par, initialfile=filnam.basename())
        else:
            filnam = thanGudGetDir(self, self.thanTitle, initialdir=par)
        if filnam is None: return
        filnam = path(filnam).abspath()
        if self.thanCommand is None or self.thanCommand(filnam):        # Let user do something
            self.thanSet(filnam)

    def showend(self):
        '''Shows the rightmost prortion of the text, if it does not fit on the available space.

        2009_01_02: The Tkinter.py of python 2.6, class Entry must change from:
    def xview(self, index):
        """Query and change horizontal position of the view."""
        self.tk.call(self._w, 'xview', index)

        to:
    def xview(self, index=None):
        """Query and change horizontal position of the view."""
        if index is None:
            return self.tk.call(self._w, 'xview')
        self.tk.call(self._w, 'xview', index)
        '''
        try:    a, b = map(float, self.thanText.xview().split())
        except: return
        vis = b - a                      # Percentage that is visible
        a = 1.0-vis                      # Percentage of the leftmost position, so that end is visible
        a = min((a+0.1, 0.99))           # Correct bug in Tk xview
        self.thanText.xview_moveto(a)

    def thanSet(self, t):
        "This is a filename provided by the programmer."
        t = t.strip()
        if t != "":
            t = path(t)
            t = t.abspath()
            t = thanAbsrelPath(t, self.initialdir)       #Tranform to relative to initialdir or absolute pathname
#            t = t.parent / t.namebase + self.thanExt
            t = t.parent / t.basename()
        self.thanText.thanSet(t)
        if isinstance(self.thanText, ThanEntry): self.showend()

    def thanGet(self):
        "Return the absolute path to the file."
        t = self.thanText.thanGet()
        #if t.strip() == "": return self.initialdir / ""  #Thanasis2022_11_29: Commented out
        if t.strip() == "": return path("")   #Thanasis2022_11_29: Nothing was chosen
        t = path(t).expand()
        if t != t.abspath(): t = self.initialdir/t  #If not absolute path, then it is relative to initialdir
        return t.abspath()

    def thanIsEmpty(self):
        "Return true if user has input only blanks; mote that thanGet() returns initialdir if empty."
        return self.thanText.thanGet().strip() == ""

    def invoke(self): self.thanMenubutton.invoke()

    def focus_set(self): return self.thanText.focus_set()

    def destroy(self):
        "break circular references."
        del self.thanMenubutton, self.thanText, self.thanCommand, self.thanBeforeopen
        super().destroy()

    def __del__(self):
        "Print message when deleted, to aid debugging."
        print("ThanFile", self, "is deleted")


##############################################################################
##############################################################################

class ThanText(Text):
    "A standard text which copes with greek text and windows/linux iconsistencies."
    #_SENTINEL = 2_000_000_000
    _SENTINEL = 2000000000
    _keysallowed = frozenset(("Up","Down","Left","Right","Prior","Next","Home","End"))

    def __init__(self, master, **kw):
        "Handle resize capability."
        self.__maxLines = self._SENTINEL
        self.__timep = time.time()
        self.__dtimep = 5.0
        Text.__init__(self, master)
        self.config(**kw)
        if "fg" not in kw and "foreground" not in kw: correctForeground(self)
        self.bind("<Control-C>", self.__prop)  #Thanasis2024_04_28:Workaround to allow copy to clipboard work in readonly mode
        self.bind("<Control-c>", self.__prop)  #Thanasis2024_04_28:Workaround to allow copy to clipboard work in readonly mode

    def __prop(self, evt):                     #Thanasis2024_04_28
        "Workaround to allow copy to clipboard work in readonly mode."
        pass #return None, so that the event is propagated

    def __format(self, evt):
        "Allow only scrolling."
        if evt.keysym not in self._keysallowed: return "break"

    def __return(self, evt):
        "Do not propagate <Return> event."
        self.thanAppend("\n")
        return "break"

    def keysallowed(self, keys=()):
        "Set the allowed keys if readonly==True."
        if not keys: return self._keysallowed
        self._keysallowed = frozenset(keys)

    def config(self, **kw):
        "Just get maxlines attribute."
        n = kw.pop("maxlines", None)
        if kw.pop("capturereturn", False): self.bind("<Return>", self.__return)
        if kw.pop("readonly", False): self.bind("<Key>", self.__format)

        Text.config(self, **kw)
        if n is None: return
        if n <= 0: n = self._SENTINEL   # Resize is going to be cancelled
        self.__maxLines = n
        self.__resize()                 # Force resize now


    def thanIndex(self, index1):
        "Return the line.column index corresponding to the given index as two integers."
        return self.index2ints(self.index(index1))


    def index2ints(self, index1):
        "Return the line.column index corresponding to the given index as two integers."
        t = str(index1).split(".")
        return int(t[0]), int(t[1])


    def set_insert(self, index):
        "Sets the insertion cursor at index simulating mouse click."
#       The following code makes the position of index visible
        self.update()
        b = self.bbox(index)
        if b is None:
            self.see(index)
            self.update()
            b = self.bbox(index)
            if b is None:
                print("ThanText.set_insert() failed. No position has been set.")
                return
#       The following code makes the position of index the position of the next character from keyboardvisible
        self.event_generate("<Button-1>", x=b[0], y=b[1])        #Thanasis2011_07_10:this line was commented out
        self.event_generate("<ButtonRelease-1>", x=b[0], y=b[1]) #Thanasis2011_07_10:this line was commented out


    def set_insert_end(self):
        "Sets the insertion cursor at then end of the text simulating mouse click."
        self.set_insert(END+"-1c")
        self.tag_remove(SEL, 1.0, END)  # This is because, often, this method causes unwanted selection of the last line


    def thanSet(self, t, tags=()):
        self.delete(1.0, END)
        t = thanUnicode(t)
        self.insert(1.0, t, tags)
        self.__resize()


    def thanInsert(self, ipos, t, tags=()):
        "Inserts text at position."
        t = thanUnicode(t)
        Text.insert(self, ipos, t, tags)
        self.__resize()


    def thanAppend(self, t, tags=()):
        "Appends text to the widget and makes sure that the appened text is visible."
        t = thanUnicode(t)
        self.insert(END, t, tags)
        self.set_insert(END+"-1c")
        self.tag_remove(SEL, 1.0, END)  # This is because, often, this method causes unwanted selection of the last line
        self.__resize()


    def thanAppendf(self, t, tags=()):
        "Appends text to the widget but it does not make sure that the text is visible."
        t = thanUnicode(t)
        self.insert(END, t, tags)
        self.__resize()


    def thanGet(self):
        "Get all content of widget."
        t = self.get(1.0, END)[:-1]
        return thanUnunicode(t)


    def thanGetPart(self, ipos1, ipos2):
        "Get partial content of widget."
        t = self.get(ipos1, ipos2)
        #print "ThanText or ThanScrolledText: type(t)=", type(t), "t=", t
        #tt = thanUnunicode(t)
        #print "         after thanUnunicode: type(t)=", type(tt), "t=", tt
        return thanUnunicode(t)


    def thanGetFtext(self, ind1="1.0", ind2=END):
        "Gets the text and its format (as tags) between the index positions, as an object."
        fo = Struct("text format object")
        ind1 = self.index(ind1)
        if ind2 == END: t = self.get(ind1, END)[:-1]
        else:           t = self.get(ind1, ind2)
#        fo.text = thanUnunicode(t)
        fo.text = t
        fo.taginfo = self.dump(ind1, ind2, tag=True)
        fo.ind1 = ind1
        return fo


    def _rel(self, inda, indb, indc):
        "Returns index whose relative position with respect to indc, is the same as the relative position of indb with respect to inda."
        alin, aich = self.index2ints(inda)  ##map(int, self.index(inda).split("."))
        blin, bich = self.index2ints(indb)
        clin, cich = self.thanIndex(indc)
        if alin == blin:
            dlin = clin
            dich = cich + bich-aich
        else:
            dlin = clin + blin-alin
            dich = cich
        return "%d.%d" % (dlin, dich)


    def thanInsertFtext(self, fo, ind1="1.0"):
        "Insert text and its format (as tags) at the index position."
#        self.insert(ind1, thanUnicode(fo.text))
        ind1 = self.index(ind1)    #In case ind1 is "end" (this would create prooblems later on)
        print("previous fo.ind1=", fo.ind1, " -> new ind1=", ind1)
        self.insert(ind1, fo.text)
        tagon = {}
        for key,val,indb in fo.taginfo:
            print("thanInsertFtext:", key, val, indb)
            if key == "tagon":
                tagon[val] = indb
            elif key == "tagoff":
                inda = tagon.pop(val, None)
                if inda is None:
                    print("thanInsertFtext: tagoff '%s' without previous tagon." % (val,))
                    continue
                posa = self._rel(fo.ind1, inda, ind1)
                posb = self._rel(fo.ind1, indb, ind1)
                print("tag_add:", val, ":", inda, indb, " ->", posa, posb)
                self.tag_add(val, posa, posb)
        for val, inda in tagon.items():   #OK for python 2, 3
            print("thanInsertFtext: tagon '%s' without later tagoff." % (val,))
#            ind = len(fo.text)  ???!!!
#            self.tag_add(val, self._rel(fo.ind1, ind1, inda), self._rel(fo.ind1, ind1, ind))
        self.__resize()


    def __resize(self):
        "Keep total number of lines less than __maxLines."
        timen = time.time()
        if timen-self.__timep < self.__dtimep: return
        self.__timep = timen
        temp = self.count("1.0", END, "lines")
        n = temp[0]
        #print("count:", temp, n)
        n = n - self.__maxLines + 1
        if n > 0: self.delete("1.0", "%d.0" % n)
        #print("new count:", self.count("1.0", END, "lines"))


#    def __del__(self): print "ThanText", self, "is deleted"


##############################################################################
##############################################################################

class ThanScrolledText(Frame):
    """Modified standard ScrolledText provided py python distribution.

    A horizontal scrollbar is implemented.
    Keywords vbar,hbar control the placement of vertical and horizontal bars.
        Default vbar=1, hbar=0.
    It uses the grid geometry manager.
    It changes the colour of the vertical scroll bar.
    Function apply was converted to a more readable form.
    """
    def set_insert (self, *args, **kw): return self.thanText.set_insert (*args, **kw)
    def set_insert_end(self, *args, **kw): return self.thanText.set_insert_end(*args, **kw)
    def thanSet    (self, *args, **kw): return self.thanText.thanSet    (*args, **kw)
    def thanInsert (self, *args, **kw): return self.thanText.thanInsert (*args, **kw)
    def thanAppend (self, *args, **kw): return self.thanText.thanAppend (*args, **kw)
    def thanAppendf(self, *args, **kw): return self.thanText.thanAppendf(*args, **kw)
    def thanGet    (self, *args, **kw): return self.thanText.thanGet    (*args, **kw)
    def thanGetPart(self, *args, **kw): return self.thanText.thanGetPart(*args, **kw)
    def tag_config (self, *args, **kw): return self.thanText.tag_config (*args, **kw)
    def tag_bind   (self, *args, **kw): return self.thanText.tag_bind   (*args, **kw)
    def index      (self, *args, **kw): return self.thanText.index      (*args, **kw)
    def tag_add    (self, *args, **kw): return self.thanText.tag_add    (*args, **kw)
    def tag_delete (self, *args, **kw): return self.thanText.tag_delete (*args, **kw)
    def dump       (self, *args, **kw): return self.thanText.dump       (*args, **kw)
    def thanIndex  (self, *args, **kw): return self.thanText.thanIndex  (*args, **kw)
    def focus_sette(self, *args, **kw): return self.thanText.focus_set  (*args, **kw)
    def keysallowed(self, *args, **kw): return self.thanText.keysallowed(*args, **kw)
    def thanGetFtext   (self, *args, **kw): return self.thanText.thanGetFtext   (*args, **kw)
    def thanInsertFtext(self, *args, **kw): return self.thanText.thanInsertFtext(*args, **kw)

    def bindte (self, *args, **kw):
        "This needs more code than delegation (just for Windows - yeah windows 'just works')."
        self.thanText.bind(*args, **kw)
        self.bind(*args, **kw)             #Special code for windows, yeah windows "just works"


    def __init__(self, master=None, **kw):
        Frame.__init__(self, master)
        drawHbar = kw.pop("hbar", 0)
        drawVbar = kw.pop("vbar", 1)

        self.vbar = self.hbar = None
        if drawVbar:
            self.vbar = Scrollbar(self, name='vbar')
#           Change the color of inactive indicator to the color of active indicator
#           because it was confusing to change color when you pressed the button
            self.vbar.config(background=self.vbar["activebackground"])
            self.vbar.grid(row=0, column=1, sticky="sn")
        if drawHbar:
            self.hbar = Scrollbar(self, name='hbar', orient=HORIZONTAL)
            self.hbar.config(background=self.hbar["activebackground"])
            self.hbar.grid(row=1, column=0, sticky="we")

        self.thanText = ThanText(self)
        self.thanText.grid(row=0, column=0, sticky="wesn")
        if drawVbar:
            self.thanText['yscrollcommand'] = self.vbar.set
            self.vbar['command'] = self.thanText.yview
        if drawHbar:
            self.thanText['xscrollcommand'] = self.hbar.set
            self.hbar['command'] = self.thanText.xview

        self.config(**kw)
        if "fg" not in kw and "foreground" not in kw: correctForeground(self.thanText)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
#        if drawVbar: self.columnconfigure(0, weight=1)
#        if drawHbar: self.rowconfigure(1, weight=1)


    def config(self, **kw):
        "Propagates attributes to the correct widgwet."
        if "relief" in kw: kw.setdefault("borderwidth", 1)
        kwf = {}
        for a in "relief bd borderwidth".split():
            if a in kw: kwf[a] = kw.pop(a)
        for a in "class_ ".split():
            if a in kw: kwf[a] = kw[a]
        Frame.config(self, **kwf)
        self.thanText.config(**kw)


    def destroy(self):
        "Delete/destroy any variables we created and saved a reference."
        del self.vbar, self.hbar, self.thanText
        Frame.destroy(self)       # This will call thanText.destroy()


#    def __del__(self):
#        print "ThanScrolledText", self, "dies.."


##############################################################################
##############################################################################

class ThanEntry(Entry):
    "A standard entry which changes color if it is disabled."

    def __init__(self, master, **kw):
        """Initialise and determine normal and disabled colours.

        For some unknown reason, all the instances of ThanEntry share the same
        text variable and have exactly the same content. So the caller must set
        a textvariable explicitelly."""
        super().__init__(master, **kw)
        if "fg" not in kw and "foreground" not in kw: correctForeground(self)
        self.__normalforeground = self["foreground"]
        self.__disabledforeground = _disfg(master)


    def config(self, **kw):
        "Changes colour when disabled."
        if "state" in kw:
            if kw["state"] == NORMAL:
                kw.setdefault("foreground", self.__normalforeground)
                self.__normalforeground = kw["foreground"]   #in case the user defined a new disabled colour
            else:
                kw.setdefault("foreground", self.__disabledforeground)
                self.__disabledforeground = kw["foreground"] #in case the user defined a new normal colour
        Entry.config(self, **kw)


    def thanSet(self, t):
        """Deletes current text and sets the new one to unicode.

        If it is not a string, it converts it to string."""
        try:    t+"x"
        except: t = str(t)
        self.delete(0, END)
        self.insert(0, thanUnicode(t))


    def thanGet(self):
        "Returns current text in plain string."
        return thanUnunicode(self.get())


##############################################################################
##############################################################################

class ThanLabel(Label):
    "A standard label with thanSet, thanGet and foreground color correction capabilities."

    def __init__(self, master, **kw):
        "Some default values."
        kw.setdefault("relief", GROOVE)
        kw.setdefault("bd", 3)
        kw.setdefault("anchor", W)
        kw.setdefault("width", 10)
        Label.__init__(self, master, **kw)
        if "fg" not in kw and "foreground" not in kw: correctForeground(self)


    def thanSet(self, t):
        "Set the text of the widget."
        self.config(text=t)
        self.update_idletasks()


    def thanGet(self):
        "Return the text of the widget."
        return self.cget("text")


#    def __del__(self): print "ThanLabel", self, "is deleted"


class ThanLabyesno(Label):
    "A label which takes only boolean values."

    def __init__(self, master, **kw):
        "Some default values."
        kw.setdefault("relief", GROOVE)
        kw.setdefault("bd", 3)
        kw.setdefault("anchor", W)
        kw.setdefault("width", 10)
        kw.setdefault("text", True)
        self.__yes = T["Yes"]
        self.__no = T["No"]
        self.__bgyes = "green"
        self.__bgno = "red"
        self.__replacetext(kw)
        Label.__init__(self, master, **kw)

    def thanSet(self, t):
        "Set the text of the widget."
        if t: Label.config(self, text=self.__yes, bg=self.__bgyes)
        else: Label.config(self, text=self.__no, bg=self.__bgno)
        self.update_idletasks()

    def thanGet(self):
        "Return the text of the widget."
        t = self.cget("text")
        if t == self.__yes: return True
        elif t == self.__no: return False
        raise ValueError("Unexpected value: %s. Please use thanSet() to put values to the widget." % (t, ))

    def __replacetext(self, kw):
        "Get the text value and convert to boolean."
        t = kw.pop("text", None)
        if t is None: return
        try:
            t+"x"
        except:                      #Not a string
            t = bool(t)
        else:                        #String
            if t[:2] in ('να', 'ΝΑ', 'na', 'NA', 'ye', 'YE', '1'): t = True
            elif t[:2] in ('οχ', 'ΟΧ', 'ox', 'OX', 'no', 'NO', '0'): t = False
            else: raise ValueError("Invalid bool value: %s" % (t,))
        if t:
            kw["text"] = self.__yes
            kw.setdefault("bg", self.__bgyes)
        else:
            kw["text"] = self.__no
            kw.setdefault("bg", self.__bgno)


    def config(self, *args, **kw):
        "Get the text value and convert to boolean."
        self.__replacetext(kw)
        Label.config(self, *args, **kw)

##############################################################################
##############################################################################

class ThanButton(Button):
    "A standard button with thanSet, thanGet and fotreground color corecction capabilities."

    def __init__(self, *args, **kw):
        "Make unicode text."
        if "bg" not in kw and "background" not in kw: kw["bg"] = "lightcyan"
        kw.setdefault("activebackground", "cyan")
        super().__init__(*args, **kw)
        if "fg" not in kw and "foreground" not in kw: correctForeground(self)


    def thanSet(self, t):
        "Set the text of the button and convert to unicode."
        self.config(text=t)
        self.update_idletasks()


    def thanGet(self):
        "Get the text of the button and convert to string."
        return self.cget("text")


#    def __del__(self): print "ThanButton", self, "is deleted"


class ThanButtonIm(Button):
    """A standard button with PIL image (instead of text), and thanSet, thanGet and imageview capabilities."

    This is also an Imageview widget.
    This widget stores a PIL image and shows it as an icon of small dimensions
    (which default to 128 pixels).
    If the users clicks the widget, then the full image is shown in another window.
    The 'command' may be overridden.
    """

    def __init__(self, *args, **kw):
        "Image is PIL image instead of a Tkinter image."
        if "bg" not in kw and "background" not in kw: kw["bg"] = "lightcyan"
        kw.setdefault("activebackground", "cyan")
#        kw.setdefault("command", self.thanShow)
        im = kw.pop("image", None)
        self._iconsize = kw.pop("iconsize", (128, 128))
        self.thanDefaultIm = kw.pop("default", None)
        self.thanTitle = kw.pop("title", None)
        self.thanUrl = kw.pop("url", None)
        Button.__init__(self, *args, **kw)
        self.thanSet(im)
        if self._pilimage is None and self.thanDefaultIm is not None:
            self.thanSet(self.thanDefaultIm)

        self.thanFloatMenu = None
        self.bind("<Button-3>", self.__photoclickr)
        self.bind("<Escape>", self.thanUnpost)


    def thanSetold(self, im):
        "Set the image of the button to the icon created by the pin image."
        #from PIL import Image, ImageTk   #24/11/2023
        import p_gimage                   #24/11/2023
        self._pilimage = im
        if im is None:
            self._tkimage = None
        else:
            b, h = im.size
            bhm = max(im.size)
            if bhm > self._iconsize:
                s = float(self._iconsize) / bhm
                b = int(b*s+0.5)
                h = int(h*s+0.5)
                im = im.resize((b, h), p_gimage.ANTIALIAS)   #24/11/2023
            self._tkimage = p_gimage.PhotoImage(im)          #24/11/2023
        self.config(image=self._tkimage)
        self.update_idletasks()


    def thanSet(self, im):
        "Set the image of the button to the icon created by the pin image."
        #from PIL import Image, ImageTk   #24/11/2023
        import p_gimage                   #24/11/2023
        self._pilimage = im
        if im is None:
            self._tkimage = None
        else:
            b, h = im.size
            bm, hm = self._iconsize
            if b > bm or h > hm:
                sb = float(bm) / b
                sh = float(hm) / h
                s = min(sb, sh)
                b = int(b*s+0.5)
                h = int(h*s+0.5)
                im = im.resize((b, h), p_gimage.ANTIALIAS)   #24/11/2023
            self._tkimage = p_gimage.PhotoImage(im)          #24/11/2023
        self.config(image=self._tkimage)
        self.update_idletasks()


    def thanGet(self):
        "Get the (big) pil image."
        return self._pilimage


    def thanShow(self):
        "Withdraw then build widgets then update and then deiconify helps to paint the window _immediately_ to its correct position."
        #from PIL import ImageTk          #24/11/2023
        import p_gimage                   #24/11/2023
        self.thanUnpost()
        if self._pilimage is None: return None
        win = Toplevel(self)
        win.withdraw()
        thanGudPosition(win, master=self)
        _tkimage2 = p_gimage.PhotoImage(self.thanGet())  #24/11/2023
        thanFontRefSave(win, _tkimage2)
        lab = Label(win, image=_tkimage2)
        lab.grid()
        if self.thanTitle is not None: win.title(self.thanTitle)
        win.update()
        win.deiconify()
        return win


    def __photoclickr(self, event):
        "Well, here is what should be done when right mouse clicks on the photo."
        if self.thanUnpost() == "break": return
        if event is None:
            w = self
            x, y = w.winfo_rootx(), w.winfo_rooty()
        else:
            x, y = event.x_root, event.y_root
        self.thanFloatMenu = self.__createFloatMenu()
        self.thanFloatMenu.post(x, y)


    def thanUnpost(self):
        "Unpost floating menu."
        if self.thanFloatMenu is not None and self.thanFloatMenu.winfo_ismapped():
            self.thanFloatMenu.unpost()
            self.thanFloatMenu = None
            return "break"
        self.thanFloatMenu = None
        return None


    def __createFloatMenu(self):
        "A menu with action for deleteing the image."
        m = Menu(self, tearoff=False)
        if self.thanUrl is not None:
            try: import webbrowser
            except: pass
            else: m.add_command(label=self.thanUrl, command=lambda: webbrowser.open(self.thanUrl, new=2))
        m.add_command(label=T["Show bigger photo"], command=self.thanShow)
        m.add_command(label=T["Clear photo"],       command=self.__photoclear)
        m.add_command(label=T["Save photo"],        command=self.__photosave)
        return m


    def __photoclear(self):
        "Clear the photo and replace with default."
        if self.thanDefaultIm is not None:
            self.thanSet(self.thanDefaultIm)
        else:
            self.thanSet(None)


    def __photosave(self):
        "Save the image to user defined file."
        im = self.thanGet()
        if im is None: return
        filnam, frw = thanGudOpenSaveFile(self, ".jpg", T["Choose file to save image"])
        if frw is None: return            #save image was cancelled
        frw.close()
        try:
            im.save(filnam)
        except Exception as why:
            mm(self, "%s\n%s" % (T["Photo was not saved:"], why),  "%s - %s" % (filnam, T["Save failed"]), ERROR)   # (Gu)i (d)ependent


    def destroy(self):
        "Break circular references."
        self.thanUnpost()
        del self._tkimage, self._pilimage, self.thanFloatMenu, self.thanTitle
        Button.destroy(self)


    def __del__(self): print("ThanButtonIm", self, "is deleted")


class ThanRef(Frame):
    "A widget which refers to another object but shows text representation of the object."

    def __init__(self, master, text="", reference="", readonly=True, buttontext="...", **kw):
        Frame.__init__(self, master)
        if readonly: self.thanText = ThanLabel(self)
        else:        self.thanText = ThanEntry(self)
        self.thanText.grid(row=0, column=0, sticky="we")
        self.thanMenubutton = Button(self, text=buttontext, relief=FLAT, padx=0, pady=0,
            bg="lightcyan", activebackground="cyan", command=self.__onclick)
        self.thanMenubutton.grid(row=0, column=1, sticky="w")

        kw.setdefault("command", None)
        kw.setdefault("textcommand", None)
        kw.setdefault("width", 10)
        self.config(**kw)
        self.columnconfigure(0, weight=1)
        self.thanSetText(text)
        self.thanReference = reference  #Bypass normal thanSet


    def __onclick(self):
        """Call the user supplied command.

        This user supplied routine (command should return a 'reference' and
        a value. The reference is reference to an object, or a code that uniqly
        specifies the object. The value is representation text to be shown
        on the widget. If value is None, then it is assumed that the click
        is cancelled. The reference may be None if the programmer wants."""
        if self.thanCommand is not None:
            reference, text = self.thanCommand(self.thanGet())
            if text is None: return   #Cancelled
            self.thanSetText(text)
            self.thanReference = reference   #Bypass normal thanSet


    def config(self, **kw):
        "Adds labels and command support to standard config, and propagates some attributes to menu."
        if "command"     in kw: self.thanCommand = kw.pop("command")
        if "textcommand" in kw: self.thanTextCommand = kw.pop("textcommand")
        if "relief"      in kw: kw.setdefault("borderwidth", 1)
        Frame.config(self, **rdict(kw, "relief", "borderwidth", "class_"))
        self.thanText.config(      **rdict(kw, "state", "font", "width", "bg", "background", "foreground", "fg", "class_"))
        self.thanMenubutton.config(**rdict(kw, "state", "font", "class_"))


    def thanSet(self, reference):
        """Saves the reference, and calls textcommand to find representation text.

        If textcommand is None, the user is reponsible to set the
        representation text via .thanTextSet().
        If textcommand exists, then .thanTextSet() is not needed.
        """
        self.thanReference = reference
        if self.thanTextCommand is not None:
            text = self.thanTextCommand(reference)
            self.thanSetText(text)


    def thanSetText(self, text): self.thanText.thanSet(text)
    def thanGet(self):     return self.thanReference
    def thanGetText(self): return self.thanText.thanGet()
    def invoke(self):    self.thanMenubutton.invoke()
    def focus_set(self): return self.thanText.focus_set()


    def destroy(self):
        "Break circular references."
        del (self.thanText, self.thanMenubutton, self.thanCommand,
             self.thanTextCommand, self.thanReference)
        Frame.destroy(self)


    def __del__(self):
        "Print message when deleted, to aid debugging."
        print("ThanReference", self, "is deleted")


class ThanStatusBar(Frame):
    "Implements a status bar."

    def __init__(self, master):
        "Initialise base classes and create status bar (as a label)."
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W, width=60)
        self.label.grid(sticky="swne")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def set(self, format, *args):
        "Prints formatted text to statusbar."
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def sett(self, text1):
        "Prints text to statusbar."
        self.label.config(text=text1)
        self.label.update_idletasks()

    def clear(self):
        "Clears the status bar."
        self.label.config(text="")
        self.label.update_idletasks()

    def destroy(self):
        "Deletes circular references."
        del self.label
        Frame.destroy(self)

    def __del__(self):
        "Report that object dies for debugging purposes."
        print("ThanStatusBar", self, "dies..")

##############################################################################
##############################################################################

class ThanToolButton(Button):
    "Button to be used in toolbar and show help on button."
    def __init__(self, *args, **kw):
        if "help" not in kw: return Button.__init__(self, *args, **kw)
        self.__help = kw.pop("help")
        Button.__init__(self, *args, **kw)
        self.__cron = None

        self.__helpWin = w = Toplevel(self)
        w.overrideredirect(True)
        lab = Label(w, text=self.__help, bg="lightyellow")
        lab.grid()
        self.bind("<Enter>", self.__cronHelpWin)
        self.bind("<Leave>", self.__unCronHelpWin)
        w.bind("<ButtonPress>", self.__unCronHelpWin) # In case of bug we should be able to delete it
        w.withdraw()

    def __cronHelpWin(self, *args):
        if self.__cron is None:
            self.__cron = self.after(1000, self.__helpWinShow)

    def __unCronHelpWin(self, *args):
        if self.__cron is not None:
            self.after_cancel(self.__cron)
            self.__cron = None
        self.__helpWin.withdraw()

    def __helpWinShow(self):
        self.__cron = None
        w = self.__helpWin
        self.update()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 1
        w.geometry("%+d%+d" % (x, y))
        w.deiconify()

    def destroy(self):
#        print "ThanToolButton", self, "destroy called"
        self.__unCronHelpWin()
        del self.__helpWin
        Button.destroy(self)
#    def __del__(self): print "ThanToolButton", self, "is deleted"


##############################################################################
##############################################################################

thanDisabledforeground = None
def _disfg(master):
    "Get the default 'disabled foreground' of Tkinter from a Button."
    global thanDisabledforeground
    if thanDisabledforeground is None:
        dummy = Button(master)
        thanDisabledforeground = dummy["disabledforeground"]
        dummy.destroy()
    return thanDisabledforeground
