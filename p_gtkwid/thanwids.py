#!/usr/bin/python
# -*- coding: iso-8859-7 -*-
import bisect
from Tkinter import (Menu, Listbox, Menubutton, Scrollbar, Checkbutton,
    Frame, Radiobutton, Button, Text, Entry, Label,
    IntVar, Toplevel,
    END, SINGLE, EXTENDED, RAISED, GROOVE, SUNKEN, FLAT, HORIZONTAL, VERTICAL,
    BASELINE, SEL, ACTIVE, NORMAL, DISABLED,  W)
from tkMessageBox import ERROR
from p_ggen import thanUnicode, thanUnunicode, prg, path, Struct, rdict
import p_gcol
from thantkutila import (thanGudGetSaveFile, thanGudGetReadFile,
    thanGudGetDir, thanGudOpenSaveFile, thanAbsrelPath, thanGudPosition,
    thanGudModalMessage as mm)
from thantksimpledialog import ThanDialog
from thantkutilb import thanFontRefSave
from thanwidstrans import T


##############################################################################
##############################################################################

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
            for i in xrange(1, 100):
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
        Menu.add(self, itemType, cnf)


    def insert(self, index, itemType, cnf=None, **kw):
        if cnf is None: cnf = {}
        i = index - 1
        assert i < len(self.__statText), "Index missing in ThanMenu!!"
        cnf.update(kw)
        self.__statText.insert(i, cnf.pop("help", ""))
        Menu.insert(self, index, itemType, self.__entryparse(cnf))


    def delete(self, index1, index2=None):
        i1 = index1
        if index2 is None:  i2 = i1 + 1
        elif index2 == END: i2 = len(self.__statText)
        else:               i2 = index2+1     # Tkinter deletes index1:index2 (INCLUDING index2)
        del self.__statText[i1:i2]
        self.__ypos = None
        Menu.delete(self, index1, index2)


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
        self.delete(0, END)
        Menu.destroy(self)

    def __del__(self): print "ThanMenu", self, "is deleted"


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
            raise ValueError, "Element %s of mlist should mark the beginning of a menu" % i
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


##############################################################################
##############################################################################

class ThanListbox(Listbox):
    "A standard listbox with unicode capabilities."

    def __init__(self, *args, **kw):
        "Save selection mode."
        self.__selectionmode = kw.get("selectmode", SINGLE)
        Listbox.__init__(self, *args, **kw)

    def thanGet(self, *args):
        "Transform to string and then get."
        a = self.get(*args)
        try:    a+"s"
        except: return [thanUnunicode(x) for x in a]
        else:   return thanUnunicode(a)


    def thanInsert(self, i, items):
        "Transform to unicode and then insert."
        try: items+"s"
        except: self.insert(i, [thanUnicode(x) for x in items])
        else:   self.insert(i, thanUnicode(items))


    def thanSet(self, items):
        "Empty list and set new values to the listbox."
        self.delete(0, END)
        for i,item in enumerate(items):
            self.thanInsert(i, item)

    def thanAppend(self, items):
        "Append new values to the end of the listbox."
        self.thanInsert(END, items)

    def thanGetSelection(self):
        "Gets the chosen value and returns it."
        indexes = self.curselection()
        if len(indexes) < 1: result = [self.thanGet(ACTIVE)]
        else: result = [self.thanGet(int(i)) for i in indexes]
        if self.__selectmode == SINGLE: return result[0]
        else:                           return result


##############################################################################
##############################################################################

class ThanChoice(Menubutton):
    "A widget that lets the user choose one of predetermined choices."

    def __init__(self, master, **kw):
        Menubutton.__init__(self, master)
        self.thanMenu = Menu(self, tearoff=0)
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

    def config(self, **kw):
        "Adds labels and command support to standard config, and propagates some attributes to menu."
        try: self.thanCommand = kw["command"]
        except KeyError: pass
        else: del kw["command"]

        try: self.thanLabels = tuple(kw["labels"])
        except KeyError: pass
        else:
            del kw["labels"]
            m = Menu(self, tearoff=0)
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
        else: raise IndexError, t
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

    def __del__(self): print "ThanChoiceRef", self, "is deleted"


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
        ThanDialog.__init__(self, master, *args, **kw)


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
        self.__li = Listbox(fra, selectmode=self.__selectmode, exportselection=0)
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
            self.__li.insert(END, thanUnicode(val))
        self.__li.activate(self.__default)
        del self.__opts, self.__default


    def buttonbox(self):
        "Do not display the default buttons in single mode."
        if self.__selectmode == SINGLE:
            self.bind("<Return>", self.__onListClick)
            self.bind("<Escape>", self.cancel)
        else:
            ThanDialog.buttonbox(self)


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
        ThanDialog.destroy(self)

#    def __del__(self):
#        print "ThanPoplist ThanDialog", self, "dies.."


##############################################################################
##############################################################################

class ThanPoplistCol(ThanDialog):
    "Displays a popup window with a list of choices; cancel/ok buttons are not required."

    def __init__(self, master, val, width=20, height=10, selectmode=SINGLE, *args, **kw):
        "Extract initial draw order."
        self.__val = val
        self.__opts = dict(width=width, height=height)
        self.__selectmode = selectmode
#        self.result = None
        ThanDialog.__init__(self, master, *args, **kw)


    def body(self, fra):
        "Create dialog widgets."
        self.__listForm(fra, 0, 0)
        self.__filist()
        return self.__li                      # This widget has the focus


    def __listForm(self, fra, ir, ic):
        "Creates and shows list."
        fra.columnconfigure(0, weight=1)
        fra.rowconfigure(0, weight=1)
        self.__li = ThanScrolledText(fra)
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
            self.__li.thanAppend(thanUnicode(name)+"\n", tag)
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
            but = ThanButton(tt, width=20, height=1, anchor="e", text=name, foreground=fg, background=bg,
            activebackground="green", command=lambda name=name: self.__onclick(name))
            tt.window_create(END, window=but, align=BASELINE)
        del self.__opts


    def buttonbox(self):
        "Do not display the default buttons in single mode."
        if self.__selectmode == SINGLE:
            self.bind("<Return>", self.__onListClick)
            self.bind("<Escape>", self.cancel)
        else:
            ThanDialog.buttonbox(self)

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
        print "ThanPopList: ACTIVE=", ACTIVE, "type=", type(ACTIVE)
        if len(indexes) < 1: self.result = [self.__val[self.__li.index(ACTIVE)]]
        else: self.result = [self.__val[int(i)] for i in indexes]
        if self.__selectmode == SINGLE: self.result = self.result[0]
        del self.__val


    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
        del self.__li
        ThanDialog.destroy(self)

#    def __del__(self):
#        print "ThanPoplist ThanDialog", self, "dies.."


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


class ThanCheck(Checkbutton):
    "A Tkinter Checkbutton with ThanSet/ThanGet support."

    def __init__(self, *args, **kw):
        "Automatically create control variable."
        self.thanVar = IntVar()
        assert "variable" not in kw, "ThanCheck automatically creates private control variable!"
        kw["variable"] = self.thanVar
        if "command" in kw: self.thanCommand = kw["command"]    #Create a reference to the command
        else: self.thanCommand = None
        Checkbutton.__init__(self, *args, **kw)

    def thanSet(self, val):
        "Set the value as bool."
        self.thanVar.set(bool(val))
        if self.thanCommand: self.thanCommand()     #Invoke command if it exists

    def thanGet(self):
        "Get the value as bool."
        return bool(self.thanVar.get())

    def config(self, **kw):
        if "command" in kw: self.thanCommand = kw["command"]
        Checkbutton.config(self, **kw)

    def destroy(self):
        "Make sure that all new class variable are deleted."
        del self.thanVar, self.thanCommand
        Checkbutton.destroy(self)


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
        return rad

    def config(self, *args, **kw):
        "Keep something for Frame and propagte the rest to children."
        kwf = {}
        for key in "relief", "borderwidth":
            if key in kw: kwf[key] = kw.pop(key)
        Frame.config(self, **kwf)
        for rad in self.thanChildren:
            rad.config(*args, **kw)

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
        print "ThanCombo", self, "is deleted"


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
        except OSError, e: print str(e)
        Frame.__init__(self, master)
        if readonly: self.thanText = ThanLabel(self, justify="right")
        else:        self.thanText = ThanEntry(self, justify="right")
        self.thanText.grid(row=0, column=0, sticky="ew")
        self.thanMenubutton = Button(self, text=buttontext, relief=FLAT, padx=0, pady=0,
            bg="lightcyan", activebackground="cyan", command=self.thanOpen)
        self.thanMenubutton.grid(row=0, column=1, sticky="w")
        self.config(**kw)
        self.columnconfigure(0, weight=1)

    def config(self, **kw):
        "Adds labels and command support to standard config, and propagates some attributes to menu."
        if "extension"  in kw: self.thanExt = kw.pop("extension")
        if "mode"       in kw: self.thanMode = kw.pop("mode")
        if "title"      in kw: self.thanTitle = kw.pop("title")
        if "command"    in kw: self.thanCommand = kw.pop("command")
        if "beforeopen" in kw: self.thanBeforeopen = kw.pop("beforeopen")
        if "relief"     in kw: kw.setdefault("borderwidth", 1)
        Frame.config(self,         **rdict(kw, "relief", "borderwidth", "class_"))
        self.thanText.config(      **rdict(kw, "text", "state", "font", "width", "bg", "background", "foreground", "fg", "class_"))
        if "textvariable" in kw and isinstance(self.thanText, ThanEntry): self.thanText.config(textvariable=kw["textvariable"])
        self.thanMenubutton.config(**rdict(kw, "state", "font", "class_"))
        if "text"       in kw: self.thanSet(kw.pop("text"))


    def thanOpen(self):
        "Prompt the user to search for the filename; it may be overwritten."
        print "thanwids: ThanFile: thanOpen(): extension=", self.thanExt
        filnam = self.thanGet()              #This absolute path
        if self.thanBeforeopen is not None and not self.thanBeforeopen(filnam): return
        if self.thanMode == "r":
            filnam = thanGudGetReadFile(self, self.thanExt, self.thanTitle,
                initialdir=filnam.parent, initialfile=filnam.basename())
        elif self.thanMode == "w":
            filnam = thanGudGetSaveFile(self, self.thanExt, self.thanTitle,
                initialdir=filnam.parent, initialfile=filnam.basename())
        else:
            filnam = thanGudGetDir(self, self.thanTitle, initialdir=filnam.parent)
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
        if t.strip() == "": return self.initialdir / ""
        t = path(t).expand()
        if t != t.abspath(): t = self.initialdir/t  #If not absolute path, then it is relative to ibitialdir
        return t.abspath()

    def thanIsEmpty(self):
        "Return true if user has input only blanks; mote that thanGet() returns initialdir if empty."
        return self.thanText.thanGet().strip() == ""

    def invoke(self): self.thanMenubutton.invoke()

    def focus_set(self): return self.thanText.focus_set()

    def destroy(self):
        "break circular references."
        del self.thanMenubutton, self.thanText, self.thanCommand, self.thanBeforeopen
        Frame.destroy(self)

    def __del__(self):
        "Print message when deleted, to aid debugging."
        print "ThanFile", self, "is deleted"


##############################################################################
##############################################################################

class ThanText(Text):
    "A standard text which copes with greek text and windows/linux iconsistencies."
    _SENTINEL = 2000000000
    _keysallowed = frozenset(("Up","Down","Left","Right","Prior","Next","Home","End"))

    def __init__(self, master, **kw):
        "Handle resize capability."
        self.__idResize = None
        self.__maxLines = self._SENTINEL
        Text.__init__(self, master)
        self.config(**kw)

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
        t = str(self.index(index1)).split(".")
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
                print "ThanText.set_insert() failed. No position has been set."
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


    def thanInsert(self, ipos, t, tags=()):
        "Inserts text at position."
        t = thanUnicode(t)
        Text.insert(self, ipos, t, tags)


    def thanAppend(self, t, tags=()):
        "Appends text to the widget and makes sure that the appened text is visible."
        t = thanUnicode(t)
        self.insert(END, t, tags)
        self.set_insert(END+"-1c")
        self.tag_remove(SEL, 1.0, END)  # This is because, often, this method causes unwanted selection of the last line


    def thanAppendf(self, t, tags=()):
        "Appends text to the widget but it does not make sure that the text is visible."
        t = thanUnicode(t)
        self.insert(END, t, tags)


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
        "Returns index whose relative position with respct to newinda is the same as the relative position of indb with respctto inda."
        alin, aich = self.thanIndex(inda)  ##map(int, self.index(inda).split("."))
        blin, bich = self.thanIndex(indb)
        clin, cich = self.thanIndex(indc)
        if alin == blin:
            dlin = clin
            dich = cich+ bich-aich
        else:
            dlin = clin + blin-alin
            dich = cich
        return "%d.%d" % (dlin, dich)


    def thanInsertFtext(self, fo, ind1="1.0"):
        "Insert text and its format (as tags) at the index position."
#        self.insert(ind1, thanUnicode(fo.text))
        self.insert(ind1, fo.text)
        tagon = {}
        for key,val,ind in fo.taginfo:
            if key == "tagon":
                tagon[val] = ind
            elif key == "tagoff":
                inda = tagon.pop(val, None)
                if inda is None:
                    print "thanInsertFtext: tagoff '%s' without previous tagon." % (val,)
                    inda = ind1
                pos1 = self._rel(fo.ind1, ind1, inda)
                pos2 = self._rel(fo.ind1, ind1, ind)
                self.tag_add(val, pos1, pos2)
        for val, inda in tagon.iteritems():
            print "thanInsertFtext: tagon '%s' without later tagoff." % (val,)
#            ind = len(fo.text)  ???!!!
#            self.tag_add(val, self._rel(fo.ind1, ind1, inda), self._rel(fo.ind1, ind1, ind))


    def __resize(self):
        "Keep total number of lines less than __maxLines."
        if self.__maxLines >= self._SENTINEL: return                      # Avoid race conditions
        if self.__idResize is not None: self.after_cancel(self.__idResize)    # In case thanResize was explicitely called
        n = self.get("1.0", END).count("\n")
        n = n - self.__maxLines + 1
        if n > 0: self.delete("1.0", "%d.0" % n)
        self.__idResize = self.after(60000, self.__resize)


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
        text variable and have exactly content. So the caller must set
        a textvariable explicitelly."""
        Entry.__init__(self, master, **kw)
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
    "A standard label with thanSet, thanGet and unicode capabilities."

    def __init__(self, master, **kw):
        "Some default values."
        kw.setdefault("relief", GROOVE)
        kw.setdefault("bd", 3)
        kw.setdefault("anchor", W)
        kw.setdefault("width", 10)
        Label.__init__(self, master, **kw)


    def thanSet(self, t):
        "Set the text of the widget."
        self.config(text=thanUnicode(t))
        self.update_idletasks()


    def thanGet(self):
        "Return the text of the widget."
        return thanUnunicode(self.cget("text"))


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
        raise ValueError, "Unexpected value: %s. Please use thanSet() to put values to the widget." % (t, )

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
            else: raise ValueError, "Invalid bool value: %s" % (t,)
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
    "A standard button with thanSet, thanGet and unicode capabilities."

    def __init__(self, *args, **kw):
        "Make unicode text."
        if "bg" not in kw and "background" not in kw: kw["bg"] = "lightcyan"
        kw.setdefault("activebackground", "cyan")
        text = kw.pop("text", None)
        Button.__init__(self, *args, **kw)
        if text is not None: self.thanSet(text)


    def thanSet(self, t):
        "Set the text of the button and convert to unicode."
        self.config(text=thanUnicode(t))
        self.update_idletasks()


    def thanGet(self):
        "Get the text of the button and convert to string."
        return thanUnunicode(self.cget("text"))


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
        from PIL import Image, ImageTk
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
                im = im.resize((b, h), Image.ANTIALIAS)
            self._tkimage = ImageTk.PhotoImage(im)
        self.config(image=self._tkimage)
        self.update_idletasks()


    def thanSet(self, im):
        "Set the image of the button to the icon created by the pin image."
        from PIL import Image, ImageTk
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
                im = im.resize((b, h), Image.ANTIALIAS)
            self._tkimage = ImageTk.PhotoImage(im)
        self.config(image=self._tkimage)
        self.update_idletasks()


    def thanGet(self):
        "Get the (big) pil image."
        return self._pilimage


    def thanShow(self):
        "Withdraw then build widgets then update and then deiconify helps to paint the window _immediately_ to its correct position."
        from PIL import ImageTk
        self.thanUnpost()
        if self._pilimage is None: return None
        win = Toplevel(self)
        win.withdraw()
        thanGudPosition(win, master=self)
        _tkimage2 = ImageTk.PhotoImage(self.thanGet())
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
        except Exception, why:
            mm(self, "%s\n%s" % (T["Photo was not saved:"], why),  "%s - %s" % (filnam, T["Save failed"]), ERROR)   # (Gu)i (d)ependent


    def destroy(self):
        "Break circular references."
        self.thanUnpost()
        del self._tkimage, self._pilimage, self.thanFloatMenu, self.thanTitle
        Button.destroy(self)


    def __del__(self): print "ThanButtonIm", self, "is deleted"


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
        print "ThanReference", self, "is deleted"


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
        print "ThanStatusBar", self, "dies.."

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


##############################################################################
##############################################################################

import sys
from Tkinter import Tk

def dddd():
    global mb1
    mb1.destroy()
    del mb1


def testPoplist():
    root = Tk()
    win = ThanPoplist(root, (20*"thanasis dimitra andreas stella").split(), width=30, height=50, title="Choose someone")
    print win.result

def testPoplistextented():
    root = Tk()
    win = ThanPoplist(root, (20*"thanasis dimitra andreas stella").split(), width=30, height=50, selectmode=EXTENDED, title="Choose someone")
    print win.result



if __name__ == "__main__":
    def testpop(evt=None):
#        win = ThanPoplist(mb31, (20*"Θανάσης dimitra andreas stella").split(), width=30, height=50, title="Choose someone")
        win = ThanPoplistCol(mb31, 2*(("Θανάσης", (255,0,0)),
                                       ("dimitra", (0,255,0)),
                                       ("andreas", (0,0,255)),
                                       ("stella",  (255,255,0)),
                                      ), width=30, height=50, title="Choose someone")
        print "ThanPoplist result =", win.result

    def testpopext(evt=None):
        win = ThanPoplist(mb31, (20*"thanasis dimitra ανδρέας stella").split(), width=30, height=50, selectmode=EXTENDED, title="Choose someone")
        print "ThanPoplist result =", win.result

    def pr(a): print a

    root = Tk()
    if sys.platform == "win32":
        root.option_add("*font", "Arial 10")
    else:
        import tkFont
        f=tkFont.Font(family="Thorndale AMT", size=12)
#        f=tkFont.Font(family="monospace", size=12)
        root.option_add("*font", f)

    mb1 = ThanMenu(root)
    m = ThanMenu(mb1, tearoff=False, statcommand=pr)
    m.add_command(label="a", help="Well.. a")
    m.add_command(label="b", help="Well.. b")
    mb1.add_cascade(label="ab", menu=m)
    root["menu"] = mb1
    del m

    labs = ("Thanasis", "Δήμητρα", "Andreas")*10
    print labs
    mb2 = ThanChoice(root, labels=labs, relief=RAISED)
    mb2.grid()
    mb3 = ThanYesno(root, relief=RAISED)
    mb3.grid()
#    mb31 = Button(root, text="Try ThanPoplist", command=testpop)
    mb31 = Button(root, text="Try ThanPoplist", command=testPoplist)
    mb31.grid()
    mb32 = Button(root, text="Try ThanPoplist Extended", command=testpopext)
    mb32.grid()
    mb4 = ThanCombo(root, labels=("Thanasis", "Dimitra", "Andreas"), relief=RAISED)
    mb4.grid()
    mb5 = ThanFile(root, text="no file", extension=".gan", mode="r", title="Define gan file", relief=RAISED)
    mb5.grid()
    mb6 = ThanFile(root, text="no dir",  extension="",     mode="d", title="Define dir file", relief=RAISED)
    mb6.grid()
    mb7 = ThanText(root, width=20, height=8, maxlines=4)
    mb7.grid()
    mb8 = ThanEntry(root)
    mb8.grid()
    mb8.thanSet("This should be disabled")
    mb8.config(state=DISABLED)
    mb9 = ThanToolButton(root, text="Press", help="Show the working of ThanToolButton", command=dddd)
    mb9.grid()
    mb10 = ThanRadio(root)
    mb10.grid()
    rad = mb10.add_button(text="AA")
    rad.grid(row=0, column=0)
    rad = mb10.add_button(text="BB")
    rad.grid(row=0, column=1)
    rad = mb10.add_button(text="CC")
    rad.grid(row=1, column=0)
    rad = mb10.add_button(text="DD")
    rad.grid(row=1, column=1)

    root.mainloop()
