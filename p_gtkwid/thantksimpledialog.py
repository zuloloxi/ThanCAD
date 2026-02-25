#
# An Introduction to Tkinter
# tkSimpleDialog.py
#
# Copyright (c) 1997 by Fredrik Lundh
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# Modified by Thanasis Stamos Aug 12, 2004-2013
# 1. Nested grab_set were implemented
# 2. The geometry manager was changed to grid
# 3. More buttonboxes
# 4. Automatic reposition
# 5. Optional menu

# --------------------------------------------------------------------
# dialog base class

'''Dialog boxes
This module handles dialog boxes. It contains the following
public symbols:
Dialog -- a base class for dialogs
askinteger -- get an integer from the user
askfloat -- get a float from the user
askstring -- get a string from the user
'''

import tkinter
from .thantkutilb import thanGrabSet, thanGrabRelease               # Stamos Aug 12, 2004
from .thanwidstrans import T as Twid
from . import thanwids

class ThanDialog(tkinter.Toplevel):
    '''Class to open dialogs.

    This class is intended as a base class for custom dialogs
    '''

#    def __init__(self, parent, title = None):
    def __init__(self, parent, title=None, buttonlabels=2, **kw): # Stamos Jan 7, 2011
        """Initialize a dialog.

        Arguments:
            parent -- a parent window (the application window)
            title -- the dialog title
            buttonlables =
              =2: 2 buttons named: OK, "Cancel"
              =3: 3 buttons named: "OK",  "Apply", "Cancel"
              =("text1", "text2"): 2 buttons named: text1, text2
              =("text1", "text2", "text3"): 3 buttons named: text1, text2, text3
              =None: No button box is displayed
              If 2 buttons: First button calls OK(), Second button calls cancel()
              If 3 buttons: First button calls OK(), Second button calls apply2(),
                            Third button calls cancel()
        """
        tkinter.Toplevel.__init__(self, parent, **kw)
        if parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                      parent.winfo_rooty()+50))
        if title: self.title(title)
        if buttonlabels == 2:
            self._butLabs = Twid["OK"], Twid["Cancel"]
        elif buttonlabels == 3:
            self._butLabs = Twid["OK"], Twid["Apply"], Twid["Cancel"]
        elif buttonlabels is None:
            self._butLabs = None
        else:
            assert len(buttonlabels) in (2, 3), "2 or 3 buttonlabels were expected"
            self._butLabs = tuple(lab+"" for lab in buttonlabels) #Raise TypeError if not strings

        body = tkinter.Frame(self)
        self.initial_focus = self.body(body)
        body.grid(padx=5, pady=5, sticky="wesn") # Stamos Aug 12, 2004
        if not self.initial_focus: self.initial_focus = self
        self.menubar = self.menu()
        if self.menubar:
            self["menu"] = self.menubar
        if self._butLabs:                      # Stamos 2010_11_27
            if len(self._butLabs) == 2: self.buttonbox()  # Stamos 2011_01_07
            else:                       self.buttonbox3() # Stamos 2010_01_07 
        self.columnconfigure(0, weight=1)      # Stamos Aug 12, 2004 
        self.rowconfigure(0, weight=1)         # Stamos Aug 12, 2004

        self.transient(parent)
        thanGrabSet(self)                      # Stamos Aug 12, 2004
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.initial_focus.focus_set()

        self.parent = parent
        self.result = None
        self.wait_window(self)


    def thanRePos(self, master=None):          # Stamos Jul 21, 2005
        "Position this dialog centered over its master."
        siz, xm, ym = master.winfo_toplevel().geometry().split("+")
        wm, hm = siz.split("x")
        self.update_idletasks()
        siz, x, y = self.geometry().split("+")
        w, h = siz.split("x")
        x = int(xm) + int( (int(wm)-int(w))/2 )
        if x < 0: x = 0
        y = int(ym) + int( (int(hm)-int(h))/2 )
        if y < 0: y = 0
        self.geometry("%+d%+d" % (x, y))


    def destroy(self):
        '''Destroy the window'''
        del self._butLabs                       #Stamos2009_10_22
        if self.menubar: self.menubar.destroy() #Stamos2010_11_27
        del self.menubar                        #Stamos2010_11_27
        self.initial_focus = None
        self.parent = None
#        self.grab_release()                     # Stamos Nov 28, 2006: commented out
        tkinter.Toplevel.destroy(self)

    #
    # construction hooks

    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        pass


    def menu(self):
        '''create menu system.

        It this function returns the menubar, a menu is added.
        If it returns None, no menu is added.
        It is called by the __init__ method.
        '''
        return None


    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''
        n = max(len(t) for t in self._butLabs)
        n = max((n, 12))
        box = tkinter.Frame(self)
        w = thanwids.ThanButton(box, text=self._butLabs[0], bg="lightgreen", activebackground="green",   # Stamos 2007_03_21
            width=n, command=self.ok, default=tkinter.ACTIVE)   # Stamos Feb 26, 2006
        w.grid(row=0, column=0, padx=5, pady=5, sticky="w")     # Stamos Aug 12, 2004
        w = thanwids.ThanButton(box, text=self._butLabs[1], bg="pink", activebackground="red",            # Stamos 2007_03_21
            width=n, command=self.cancel)                       # Stamos Feb 26, 2006
        w.grid(row=0, column=1, padx=5, pady=5, sticky="e")     # Stamos Aug 12, 2004

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.grid(sticky="wesn")                      # Stamos Aug 12, 2004
        box.columnconfigure(0, weight=1)             # Stamos Aug 12, 2004
        box.columnconfigure(1, weight=1)             # Stamos Aug 12, 2004

    #
    # standard button semantics

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return False
        self.okhousekeep()

    def okhousekeep(self):
        "Do house keeping after ok() or apply2()."
        self.withdraw()
        self.update_idletasks()
        self.apply()
        # put focus back to the parent window
        thanGrabRelease()                      # Stamos Oct 20, 2009
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        # put focus back to the parent window
        thanGrabRelease()                      # Stamos Oct 20, 2009
        if self.parent is not None:
            self.parent.focus_set()
        self.result = None
        self.destroy()

    #
    # command hooks

    def validate(self):
        '''validate the data

        This method is called automatically to validate the data before the
        dialog is destroyed. By default, it always validates OK.
        '''
        return True

    def apply(self):
        '''process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        '''
        pass # override


    def __del__(self):
        print("ThanDialog dies..")


    def buttonbox3(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''
        n = max(len(t) for t in self._butLabs)
        n = max((n, 12))
        box = tkinter.Frame(self)
        w = thanwids.ThanButton(box, text=self._butLabs[0], bg="lightgreen", activebackground="green",  # Stamos 2007_03_21
            width=n, command=self.ok, default=tkinter.ACTIVE)   # Stamos Feb 26, 2006
        w.grid(row=0, column=0, padx=5, pady=5, sticky="w")     # Stamos Aug 12, 2004
        w = thanwids.ThanButton(box, text=self._butLabs[1], bg="gold", activebackground="yellow",       # Stamos 2007_03_21
            width=n, command=self.apply2)                       # Stamos Jan 7, 2011
        w.grid(row=0, column=1, padx=5, pady=5, sticky="w")     # Stamos Jul 15, 2005
        w = thanwids.ThanButton(box, text=self._butLabs[2], bg="pink", activebackground="red",          # Stamos 2007_03_21
            width=n, command=self.cancel)                       # Stamos Feb 26, 2006
        w.grid(row=0, column=2, padx=5, pady=5, sticky="e")     # Stamos Aug 12, 2004

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.grid(sticky="wesn")                      # Stamos Aug 12, 2004
        box.columnconfigure(0, weight=1)             # Stamos Aug 12, 2004
        box.columnconfigure(1, weight=1)             # Stamos Aug 12, 2004


    def apply2(self, *args):
        "The second of 3 buttons was pressed; just validate."
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return False
        return True    #The rest must be called by the overriding method
        self.okhousekeep()

# --------------------------------------------------------------------
# convenience dialogues

class _QueryDialog(ThanDialog):

    def __init__(self, title, prompt,
                 initialvalue=None,
                 minvalue = None, maxvalue = None,
                 parent = None, **kw):
        if not parent:
            parent = tkinter._default_root
        self.prompt   = prompt
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.initialvalue = initialvalue
        self.entrykw = kw
        ThanDialog.__init__(self, parent, title)  #, buttonlabels=3)

    def destroy(self):
        self.entry = None
        ThanDialog.destroy(self)

    def body(self, master):
        w = thanwids.ThanLabel(master, text=self.prompt, justify=tkinter.LEFT, #Thanasis2025_01_20: label->ThanLabel ...
            relief=tkinter.FLAT, width=None)   #... override ThanLabel's default relief/width
        w.grid(row=0, column=0, padx=5, sticky=tkinter.W)
        self.entry = thanwids.ThanEntry(master, name="entry", **self.entrykw)   #thanasis2025_01_20:Entry->ThanEntry
        self.entry.grid(row=1, column=0, padx=5, sticky=tkinter.W+tkinter.E)
        master.columnconfigure(0, weight=1)   #Thanasis2020_05_19
        if self.initialvalue:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, tkinter.END)

        return self.entry

    def validate(self):
        from tkinter import messagebox
        try:
            result = self.getresult()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent = self
            )
            return 0
        if self.minvalue is not None and result < self.minvalue:
            messagebox.showwarning(
                "Too small",
                "The allowed minimum value is %s. "
                "Please try again." % self.minvalue,
                parent = self
            )
            return 0
        if self.maxvalue is not None and result > self.maxvalue:
            messagebox.showwarning(
                "Too large",
                "The allowed maximum value is %s. "
                "Please try again." % self.maxvalue,
                parent = self
            )
            return 0
        self.result = result
        return 1


class _QueryInteger(_QueryDialog):
    errormessage = "Not an integer."
    def getresult(self):
        return int(self.entry.get())


def askinteger(title, prompt, **kw):
    '''get an integer from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is an integer
    '''
    d = _QueryInteger(title, prompt, **kw)
    return d.result

class _QueryFloat(_QueryDialog):
    errormessage = "Not a floating point value."
    def getresult(self):
        #return float(self.entry.get())
        return float(self.entry.get().replace(",", ".")) #Thanasis2013_10_27

def askfloat(title, prompt, **kw):
    '''get a float from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is a float
    '''
    d = _QueryFloat(title, prompt, **kw)
    return d.result


class _QueryString(_QueryDialog):
    def __init__(self, *args, **kw):
        if "show" in kw:
            self.__show = kw["show"]
            del kw["show"]
        else:
            self.__show = None
        _QueryDialog.__init__(self, *args, **kw)

    def body(self, master):
        entry = _QueryDialog.body(self, master)
        if self.__show is not None:
            entry.configure(show=self.__show)
        return entry

    def getresult(self):
        return self.entry.get()


def askstring(title, prompt, **kw):
    '''get a string from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is a string
    '''
    d = _QueryString(title, prompt, **kw)
    return d.result


def test1():
    "Tests menus."
    root = tkinter.Tk()
    w = ThanDialog(root)


if __name__ == "__main__":
    if 0: 
        test1()
    else:
        root = tkinter.Tk()
        root.update()
        print(askinteger("Spam", "Egg count", initialvalue=12*12))
        print(askfloat("Spam", "Egg weight\n(in tons)", minvalue=1, maxvalue=100))
        print(askstring("Spam", "Egg label"))
