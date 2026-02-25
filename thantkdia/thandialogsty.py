##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (www.gnu.org/licenses/gpl.html).
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################

"""\
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

This module displays a dialog for the user to create/modify/delete a text style.
"""


from Tkinter import *
import p_ggen, p_gtkuti, p_gtkwid
from thanfonts import thanFonts
from thandefs import ThanTstyle
from thantrans import T

class ThanTkStyle(p_gtkuti.ThanDialog):
    "Dialog for creating and editing linetyles."

    def __init__(self, master, tstyles, val, tstyleinuse, *args, **kw):
        "Extract initial style."
        c = {}
	for k,v in tstyles.iteritems(): c[k] = v.thanCopy()
	self.__val = c.get(str(val), v)     # If val is unknown, choose arbitrarily another one
	self.thanTstyles = c
	self.__tstyleinuse = tstyleinuse
	self.__changed = False
	self.thanVals = None

	p_gtkuti.ThanDialog.__init__(self, master, buttonlabels=3, *args, **kw)

    def body(self, fra):
        "Create dialog widgets."
        self.__stylenameForm(fra, 0, 0)
        self.__fontnameForm(fra, 1, 0)
        self.__effectsForm(fra, 2, 0)
	self.__previewForm(fra, 2, 1)
	self.__updateChosen(self.__val)
	del self.__val
	return self.thanHeight                      # This widget has the focus

    def __stylenameForm(self, fra, ir, ic):
        "Shows common colors."
	f = Frame(fra, bd=2, relief=GROOVE); f.grid(row=ir, column=ic, columnspan=2, sticky="we", ipady=4, pady=4)
	for i in xrange(4): f.columnconfigure(i, weight=1)
	w = Label(f, text=" "+T["Style Name"])
	w.grid(row=0, column=0, columnspan=4, sticky="w")

        self.__tlabs = self.thanTstyles.keys();	self.__tlabs.sort()
        self.thanTname = p_gtkwid.ThanChoice(f, labels=self.__tlabs, width=20, anchor="w", command=self.__styleFill, relief=SUNKEN)
	self.thanTname.grid(row=1, column=0, sticky="w", padx=5)
	w = Button(f, text=T["New"], width=6, command=self.__nameNew)
	w.grid(row=1, column=1, sticky="w", padx=5)
	w = Button(f, text=T["Rename"], width=6, command=self.__nameRen)
	w.grid(row=1, column=2, sticky="w", padx=5)
	w = Button(f, text=T["Delete"], width=6, command=self.__nameDel)
	w.grid(row=1, column=3, sticky="w", padx=5)

    def __fontnameForm(self, fra, ir, ic):
        "Shows common colors."
	f = Frame(fra, bd=2, relief=GROOVE); f.grid(row=ir, column=ic, columnspan=2, sticky="we", ipady=4, pady=4)
	for i in xrange(3): f.columnconfigure(i, weight=1)

	w = Label(f, text=" "+T["Font Name"]); w.grid(row=0, column=0, sticky="w", padx=5)
        self.__flabs = thanFonts.keys(); self.__flabs.sort()
#        w = self.thanFname = p_gtkwid.ThanChoice(f, labels=self.__flabs, width=20,  relief=SUNKEN)
        w = self.thanFname = Button(f, text=self.__flabs[0], width=20, anchor="w", relief=SUNKEN, command=self.__fontShow)
	w.grid(row=1, column=0, sticky="w", padx=5)

	w = Label(f, text=" "+T["Font Style"]); w.grid(row=0, column=1, sticky="w", padx=5)
	w = Label(f, text="          ", width=10, relief=GROOVE); w.grid(row=1, column=1, sticky="w", padx=5)

	w = Label(f, text=" "+T["Height"]); w.grid(row=0, column=2, sticky="w", padx=5)
	self.thanHeight = Entry(f, width=8); self.thanHeight.grid(row=1, column=2, sticky="w", padx=5)

    def __fontShow(self, *args):
        "Show all the fonts for the user to choose from."
	win = p_gtkwid.ThanPoplist(self, self.__flabs, width=40, title="Select ThanCad Font")
	if win.result == None: return
	self.thanFname.config(text=win.result)
	self.__changed = True

    def __effectsForm(self, fra, ir, ic):
        "Shows common colors."
	f = Frame(fra, bd=2, relief=GROOVE); f.grid(row=ir, column=ic, sticky="wesn", ipady=4, pady=4)
	for i in xrange(1, 2): f.columnconfigure(i, weight=1)
	for i in xrange(1, 4): f.rowconfigure(i, weight=1)

	w = Label(f, text=" "+T["Effects"]); w.grid(row=0, column=0, sticky="w", padx=5)
	self.__efUp = IntVar(); self.__efUp.set(False)
	self.__efBack = IntVar(); self.__efBack.set(False)
	self.__efVert = IntVar(); self.__efVert.set(False)
        w = Checkbutton(f, text=T["Upside Down"], variable=self.__efUp)
        w.grid(row=1, column=0, sticky="w")
        w = Checkbutton(f, text=T["Backwards"], variable=self.__efBack)
        w.grid(row=2, column=0, sticky="w")
        w = Checkbutton(f, text=T["Vertical"], variable=self.__efVert)
        w.grid(row=3, column=0, sticky="w")

        w = Frame(f); w.grid(row=1, column=1, sticky="we")

	w = Label(f, text=T["Width Factor:"]); w.grid(row=1, column=2, sticky="e", padx=5)
	self.thanWidthf = Entry(f, width=8); self.thanWidthf.grid(row=1, column=3, sticky="e", padx=5)
	w = Label(f, text=T["Oblique Angle:\n(deg clockwise)"]); w.grid(row=2, column=2, sticky="e", padx=5)
	self.thanObliq = Entry(f, width=8); self.thanObliq.grid(row=2, column=3, sticky="e", padx=5)

    def __previewForm(self, fra, ir, ic):
        "Shows common colors."
	f = Frame(fra, bd=2, relief=GROOVE); f.grid(row=ir, column=ic, sticky="wesn", ipady=4, pady=4)
	for i in xrange(1): f.columnconfigure(i, weight=1)
	for i in xrange(1,2): f.rowconfigure(i, weight=1)

	w = Label(f, text=""+T["Preview"], anchor="w", width=15); w.grid(row=0, column=0, sticky="w", padx=5)
        w = self.__prevBig = Canvas(f, width=20, height=60, bd=2, relief=RIDGE)
        w.grid(row=1, column=0, columnspan=2, sticky="wesn", padx=5)
        w = self.__prevSmall = Canvas(f, width=20, height=15, bd=2, relief=RIDGE)
        w.grid(row=2, column=0, sticky="wesn", padx=5)
	w = Button(f, text=T["Preview"], command=self.__doPreview)
	w.grid(row=2, column=1, sticky="w", padx=5)

    def __doPreview(self, *args):
        "Preview the chosen style/font."
#	self.thanVals = (self.thanTname.thanGetText(),
#	                 thanFonts[self.thanFname.thanGetText()],
#			 height, fact, obl, self.__efUp.get(), self.__efBack.get(), self.__efVert.get()
#			)
        self.thanValidate(strict=False)
        text = "AaBb"
        f = self.thanVals[1].thanCopypartial(text)
        obl = self.thanVals[4]
        if obl != 0: f.thanObliqueMake(obl)
        fact = self.thanVals[3]
        if fact != 1: f.thanWidthScale(fact)
        if self.thanVals[5]: f.thanUpsidedownMake()
        if self.thanVals[6]: f.thanBackwardsMake()
        if self.thanVals[7]: f.thanVerticalMake()

	tk = p_ggen.Struct(); tk.fill = tk.outline = None
	import Tkinter
	for dc in self.__prevBig, self.__prevSmall:
	    b = dc.winfo_width(); h = dc.winfo_height()
	    if f.thanVert: hchar = h*0.18; h2 = h*0.95
	    else:          hchar = h*0.5; h2 = (h-hchar)*0.6
	    dc.delete(Tkinter.ALL)
	    tk.dc = dc
            f.thanTkPaint(tk, 0.1*b, h-h2, hchar, text, 0.0, ())

    def __nameNew(self, *args):
        "Creates a new text style."
	name1 ="NewTextStyle"
	while True:
	    name1 = p_gtkuti.thanGudGetText(self, "Create new text style ", name1)
	    if name1 == None: return
	    name1 = name1.strip()
	    name2 = name1.lower()
	    for nam in self.thanTstyles:
	        if name2 == nam.lower(): break
	    else: break
	    p_gtkuti.thanGudModalMessage(self, "A font with this name already exists", "Create Failed")
	sty = ThanTstyle(name1, thanFonts["thanprime1"])
	self.thanTstyles[name1] = sty
	labs = self.thanTstyles.keys()
	labs.sort()
	self.thanTname.config(labels=labs)
	self.__updateChosen(sty)
	self.__changed = True

    def __nameRen(self, *args):
        "Renames current text style."
	name = name1 = self.thanTname.thanGetText()
	if name1.lower() == "standard":
	    p_gtkuti.thanGudModalMessage(self, "Text style 'standard' can not be renamed", "Rename Failed")
	    return
	while True:
	    name1 = p_gtkuti.thanGudGetText(self, "Rename text style "+name, name1)
	    if name1 == None: return
	    name1 = name1.strip()
	    name2 = name1.lower()
	    for nam in self.thanTstyles:
	        if name2 == nam.lower(): break
	    else: break
	    p_gtkuti.thanGudModalMessage(self, "A font with this name already exists", "Rename Failed")
	sty = self.thanTstyles.pop(name)
	sty.thanName = name1
	self.thanTstyles[name1] = sty
	labs = self.thanTstyles.keys()
	labs.sort()
	self.thanTname.config(labels=labs)
	self.thanTname.thanSetText(name1)
	self.__changed = True

    def __nameDel(self, *args):
        "Deletes current text style."
	name1 = self.thanTname.thanGetText()
	if name1.lower() == "standard":
	    p_gtkuti.thanGudModalMessage(self, "Text style 'standard' can not be deleted", "Delete Failed")
	    return
	if self.__tstyleinuse(self.thanTstyles[name1]):
	    p_gtkuti.thanGudModalMessage(self, "Text style %s is in use"%name1, "Delete Failed")
	    return
	i = self.thanTname.thanGet()
	del self.thanTstyles[name1]
	labs = self.thanTstyles.keys()
	labs.sort()
	self.thanTname.config(labels=labs)
	if i <= len(labs): i -= 1     # last tstyle was deleted
	self.thanTname.thanSet(i)
	self.__changed = True

    def __styleFill(self, *args):
        "Fill the dialog with the attributes of the chosen text style."
	print "styleFill:", args
	print "efUp:", self.__efUp.get()
	self.__updateChosen()


    def __updateChosen(self, tstyle=None):
        "Updates the text with the chosen value."
	if tstyle == None: tstyle = self.thanTstyles[self.thanTname.thanGetText()]
        self.thanTname.thanSetText(tstyle.thanName)
        self.thanFname.config(text=tstyle.thanFont.thanName)
	self.thanHeight.delete(0, END); self.thanHeight.insert(0, "%.4f"%tstyle.thanHeight)
	self.__efUp.set(tstyle.thanUpsidedown)
	self.__efBack.set(tstyle.thanBackwards)
	self.__efVert.set(tstyle.thanVertical)
	self.thanWidthf.delete(0, END); self.thanWidthf.insert(0, "%.4f"%tstyle.thanWidthfactor)
	self.thanObliq.delete(0, END); self.thanObliq.insert(0, "%.4f"%tstyle.thanOblique)
	return tstyle

    def apply2(self):
        "The user pressed the apply button."
        self.__changed = True
        return p_gtkuti.ThanDialog.apply(self)

    def validate(self):
        "If everything is ok, it stores the changes and writes the result."
        if self.thanValidate(strict=True):
            sty = ThanTstyle(*self.thanVals)
            self.thanTstyles[sty.thanName] = sty
	    self.__updateChosen()
	    self.result = self.thanTstyles
	    return True
	else:
	    return False

    def thanValidate(self, strict=True):
        "Returns true if the value chosen by the user is valid."
        ok = True
        try:
	    height = float(self.thanHeight.get())
	    if height < 0: raise ValueError
	except:
	    if strict:
	        p_gtkuti.thanGudModalMessage(self, "Invalid height", "Error Message")
	        self.thanHeight.focus_set()
	        return False
	    height = 0.0; ok = False
	try:
	    fact = float(self.thanWidthf.get())
	    if fact <= 0: raise ValueError
	except:
	    if strict:
	        p_gtkuti.thanGudModalMessage(self, "Invalid width factor", "Error Message")
	        self.thanWidthf.focus_set()
	        return False
	    fact = 1.0; ok = False
	try:
            obl = float(self.thanObliq.get())
            if obl <= -90.0 or obl >= 90.0: raise ValueError
        except:
            if strict:
	        p_gtkuti.thanGudModalMessage(self, "Invalid oblique angle", "Error Message")
	        self.thanObliq.focus_set()
	        return False
	    obl = 0.0; ok = False
	self.thanVals = (self.thanTname.thanGetText(),
	                 thanFonts[self.thanFname["text"]],
			 height, fact, obl, self.__efUp.get(), self.__efBack.get(), self.__efVert.get()
			)
	return ok

    def ok(self, *args):
        "The user pressed ok."
	if not self.validate(): return
        self.__changed = False
        p_gtkuti.ThanDialog.ok(self, *args)

    def cancel(self, *args):
        "The user pressed cancel."
	if self.__changed:
	    t = T["The changes you made (even if you pressed apply)\n"\
	        "are going to be lost.\n"\
		"OK to Abandon changes?"]
	    a = p_gtkuti.thanGudAskOkCancel(self, t, T["CHANGES DETECTED"])
	    if not a: return
	p_gtkuti.ThanDialog.cancel(self, *args)

    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
	del self.thanHeight, self.__efUp, self.__efBack, self.__efVert
	del self.thanWidthf, self.thanObliq, self.thanTname, self.thanFname, self.thanVals
	del self.__prevBig, self.__prevSmall
	del self.__tstyleinuse
	p_gtkuti.ThanDialog.destroy(self)

    def __del__(self):
        print "ThanTstyle ThanDialog", self, "dies.."


def test():
    global root, fs
    try: root
    except:
        from thandefs import ThanTstyle
	t = ThanTstyle("standard", thanFonts["thanprime1"])
	t1 = ThanTstyle("thanasis1", thanFonts["thanlcd1"])
	fs = {t.thanName:t, t1.thanName:t1}
        root = Tk()
    win = ThanDialogSty(root, fs, "standard", lambda x: False, title="Edit ThanCad Text styles")
    print win.result
