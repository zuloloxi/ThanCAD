##############################################################################
# ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2025 Thanasis Stamos, May 20, 2025
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
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
ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers

This module displays a dialog fro the user to enter a color.
It also has the routine to get the user defined colors from the config files.
"""

from tkinter import Frame, Label, Button, Entry, BitmapImage, END, GROOVE
from tkinter.colorchooser import askcolor
from p_ggen import ThanStub as S, Pyos
import p_gtkwid, p_gcol
import thanvar
from thandefs import thanatt
from thanopt import thancadconf


class ThanColor(p_gtkwid.ThanDialog):
    "Dialog for the visibility of a layer."
    thanAttsTk = None

    def __init__(self, master, val, special=True, *args, **kw):
        "Extract initialcolor."
        self.__val = str(val)
        self.__special = special
        p_gtkwid.ThanDialog.__init__(self, master, *args, **kw)

    def body(self, fra):
        "Create dialog widgets."
        self.__getAttrs()
        if Pyos.Windows: buwi = 2
        else:            buwi = 0

        ir = 0
        self.__commonColors(fra, ir, 0, buwi)

        ir += 1
        fra1 = Frame(fra)
        fra1.grid(row=ir, sticky="we", pady=4)
        fra1.columnconfigure(1, weight=1)
        self.__grayShades(   fra1, 0, 0, buwi)
        if self.__special: self.__specialVals(fra1, 0, 1)

        ir += 1
        self.__partialFullColor(fra, ir, 0)
        ir += 1
        self.__userColors(fra, ir, 0, buwi)
        ir += 1
        self.__chosenValue(fra, ir, 0, buwi)
        self.thanCol.select_range(0, END)
        return self.thanCol                      # This widget has the focus


    def __commonColors(self, fra, ir, ic, buwi):
        "Shows common colors."
        f = Frame(fra, bd=2, relief=GROOVE)
        f.grid(row=ir, column=ic, sticky="we", ipady=4, pady=4)
        f.columnconfigure(11, weight=1)
        w = Frame(f, width=5)
        w.grid(row=0, column=0)
        w = Label(f, text=" Common Colors")
        w.grid(row=0, column=1, columnspan=9, sticky="w")
        w = Frame(f)
        w.grid(row=0, column=11)

        ic1 = 1
        for jcol in range(0, 10):
            thc = thanatt.thanAttCol(p_gcol.thanDxfColCode2Rgb.get(jcol, (255,255,255)))
            but = Button(f, width=buwi, bd=1, bg=thc.thanTk, activebackground=thc.thanTk, command=S(self.__updateChosen, str(thc)))
            but.grid(row=1, column=ic1, padx=buwi)
            ic1 += 1


    def __grayShades(self, fra, ir, ic, buwi):
        "Shows shades of gray."
        grays = [rgb for rgb in p_gcol.thanDxfColCode2Rgb.values()  if rgb[0] == rgb[1] == rgb[2]]   #works for python2,3
        grays.sort()
        n = len(grays)

        f = Frame(fra, bd=2, relief=GROOVE)
        f.grid(row=ir, column=ic, sticky="wsn", ipady=4)
        w = Frame(f, width=5)
        w.grid(row=0, column=0)
        w = Label(f, text=" Gray Shades")
        w.grid(row=0, column=1, columnspan=6, sticky="w")
        w = Frame(f, width=5)
        w.grid(row=0, column=n+1)

        ic1 = 1
        for rgb in grays:
            thc = thanatt.thanAttCol(rgb)
            but = Button(f, width=buwi, bd=1, bg=thc.thanTk, activebackground=thc.thanTk,
                command=S(self.__updateChosen, str(thc)))
            but.grid(row=1, column=ic1, padx=buwi)
            ic1 += 1


    def __specialVals(self, fra, ir, ic):
        "Shows special values."
        f = Frame(fra, bd=2, relief=GROOVE); f.grid(row=ir, column=ic, sticky="esn", ipady=4)
        f.columnconfigure(0, weight=1); f.columnconfigure(1, weight=1)
        w = Frame(f, width=5); w.grid(row=0, column=0)
        w = Label(f, text=" Special Colors")
        w.grid(row=0, column=1, columnspan=2, sticky="w")
        w = Frame(f, width=5); w.grid(row=0, column=3)

        but = Button(f, text=str(thanvar.THANBYPARENT), bg="gold", activebackground="yellow",
            command=S(self.__updateChosen, str(thanvar.THANBYPARENT)))
        but.grid(row=1, column=1, sticky="we", padx=5)
        p_gtkwid.correctForeground(but)    #Thanasis2024_06_29
        but = Button(f, text=str(thanvar.THANPERSONAL), bg="darkcyan", activebackground="cyan",
            command=S(self.__updateChosen, str(thanvar.THANPERSONAL)))
        but.grid(row=1, column=2, sticky="we", padx=5)
        p_gtkwid.correctForeground(but)    #Thanasis2024_06_29


    def __userColors(self, fra, ir, ic, buwi):
        "Shows common colors."
        f = Frame(fra, bd=2, relief=GROOVE); f.grid(row=ir, column=ic, sticky="we", ipady=4, pady=4)
        f.columnconfigure(len(thancadconf.thanColUser)+1, weight=1)
        w = Frame(f, width=5); w.grid(row=0, column=0)
        w = Label(f, text=" User Defined Colors")
        w.grid(row=0, column=1, columnspan=max((len(thancadconf.thanColUser),1)), sticky="w")
        w = Frame(f, width=5); w.grid(row=0, column=len(thancadconf.thanColUser)+1)

        ic1 = 1
        self.rbut = [None]*len(thancadconf.thanColUser)
        for i,col in enumerate(thancadconf.thanColUser):
            if col is None:
                self.rbut[i] = Button(f, width=buwi, bd=1, command=None)
            else:
                thc = thanatt.thanAttCol(col)
                self.rbut[i] = Button(f, width=buwi, bd=1, bg=thc.thanTk, activebackground=thc.thanTk,
                                      command=S(self.__updateChosen, str(thc)))
            self.rbut[i].grid(row=1, column=ic1, pady=4, padx=buwi)
            ic1 += 1

        f1 = Frame(f)
        f1.grid(row=2, column=1, columnspan=max((len(thancadconf.thanColUser), 1)), sticky="e")
        but = Button(f1, text="Nearest palette color", command=S(self.__nearest))
        but.grid(row=0, column=0, sticky="e")
        p_gtkwid.correctForeground(but)    #Thanasis2024_06_29
        but = Button(f1, text="Define new...", command=S(self.__choosecol))
        but.grid(row=0, column=1, sticky="e")
        p_gtkwid.correctForeground(but)    #Thanasis2024_06_29


    def __nearest(self):
        "Find nearest 'full color palette' color to the one chosen."
        thc = self.__updateChosen()
        if thc in (None, thanvar.THANBYPARENT, thanvar.THANPERSONAL): return
        col = thc.thanDxf()
        self.__updateChosen(str(col))


    def __partialFullColor(self, fra, ir, ic):
        """Shows partial "Full" Color Palette."""
        f = Frame(fra, bd=2, relief=GROOVE)
        f.grid(row=ir, column=ic, sticky="we", ipadx=5, ipady=4, pady=4)
        ir1 = 0
        w = Label(f, text=" Full Color Palette")
        w.grid(row=ir1, column=0, columnspan=25, sticky="w")

        ir1 += 1; blankim1 = self.thanAttsTk[2]
        for i in list(range(18, 9, -2))+list(range(11, 20, 2)):
            ic1 = 0
            for jcol in range(i, 230+i+1, 10):
                thc = thanatt.thanAttCol(p_gcol.thanDxfColCode2Rgb.get(jcol, (255,255,255)))
#                but = Button(f, image=blankim1, width=10, height=8, # Blank image instead of blank text, so that button is arbitrarily small
                but = Button(f, image=blankim1, width=14, height=8, # Blank image instead of blank text, so that button is arbitrarily small
                bd=1, bg=thc.thanTk, activebackground=thc.thanTk, command=S(self.__updateChosen, str(thc)))
                but.grid(row=ir1, column=ic1)
                ic1 += 1
            ir1 += 1
            if i == 10: ir2 = ir1; ir1 += 1   # Leave a row for some blank space

        but = Frame(f, height=5)
        but.grid(row=ir2, column=1, columnspan=25)


    def __chosenValue(self, fra, ir, ic, buwi):
        "Shows the chosen value and the capability to compose a new rgb one."
        f = Frame(fra, bd=0, relief=GROOVE); f.grid(row=ir, column=ic, sticky="we", ipady=4, pady=4)
        f.columnconfigure(10, weight=1)

        w = Label(f, text="Chosen Color:")
        w.grid(row=0, column=1, sticky="w")
        self.thanCol = Entry(f, width=12)
        self.thanCol.grid(row=0, column=2, sticky="w")
        p_gtkwid.correctForeground(self.thanCol)    #Thanasis2024_06_29
        self.cbut = Button(f, width=buwi, bd=1, command=self.__updateChosen)
        self.cbut.grid(row=0, column=3, sticky="w", padx=buwi)
        self.thanColRGB = Label(f, text="")
        self.thanColRGB.grid(row=0, column=4, sticky="w")

        self.__updateChosen(self.__val)
        del self.__val


    def __updateChosen(self, txtcol=None):
        "Updates the button with the chosen value."
        if txtcol is None: txtcol = self.thanCol.get()
        txtcol = txtcol.strip()
        thc = thanatt.thanAttCol(txtcol)
        if thc is not None:
            txtcol = str(thc)
            tkcol = thc.thanTk
            rgb = thc.rgbShow()
        elif txtcol == str(thanvar.THANBYPARENT):
            thc = thanvar.THANBYPARENT
            tkcol = self.thanAttsTk[1]
            rgb = ""
        elif txtcol == str(thanvar.THANPERSONAL):
            thc = thanvar.THANPERSONAL
            tkcol = self.thanAttsTk[1]
            rgb = ""
        else:
            tkcol = self.thanAttsTk[1]
            rgb = ""
        self.cbut.config(bg=tkcol, activebackground=tkcol)
        self.thanColRGB.config(text=rgb)
        self.thanColRGB.update_idletasks()                           # _idletasks breaks WinDoze (98?) support. Skotistika
        self.thanCol.delete(0, END)
        self.thanCol.insert(0, txtcol)
        return thc


    def __getAttrs(self):
        "Returns suitable fonts, colors and images."
        if self.thanAttsTk is None:
            but = Button(self)
            butfont1 = p_gtkwid.thanFontGet(but)
            butcol1 = but["bg"]
            but.destroy()
            butfont1.config(size=6)

            #self.__class__.thanAttsTk = butfont1, butcol1, \
            #                           BitmapImage(data=b'\0'*2) # A blank b/w image of size 2x2 pixels
            #im2x2 = b'''#define 2x2_width 2
            #            #define 2x2_height 2
            #            static unsigned char 2x2_bits[] = {
            #                0x03, 0x03 };'''
            #Thanasis2024_06_29:the above creates a black dot in the image but it was a workaround for
            #previous version of tkinter/tk: if the bitmap was completely empty (black), and you used it
            #as the image of a button with background color, no color was shown.
            #Today the bug (?) was fixed in tkinter/tk, and thus workaround is no longer necessary,
            #and thus the code below
            im2x2 = b'''#define 2x2_width 2
                        #define 2x2_height 2
                        static unsigned char 2x2_bits[] = {
                            0x00, 0x00 };'''
            self.__class__.thanAttsTk = butfont1, butcol1, \
                                       BitmapImage(data=im2x2) # A blank b/w image of size 2x2 pixels


    def __choosecol(self, *args):
        "Lets the user define a new TGB color."
        thc = self.__updateChosen()
        if thc in (None, thanvar.THANBYPARENT, thanvar.THANPERSONAL): tkcol = "white"
        else: tkcol = thc.thanTk
        col, tkcol = askcolor(tkcol, master=self, parent=self)
        if col is None: return
        tkcol = str(tkcol)
        thc = thanatt.thanAttCol((int(tkcol[1:3], 16), int(tkcol[3:5], 16), int(tkcol[5:7], 16)))
        thc = self.__updateChosen(str(thc))    # Note that this returns a valid color

        if str(thc) in thancadconf.thanColUser: return
        del thancadconf.thanColUser[-1]; thancadconf.thanColUser.insert(0, str(thc))
        for i,col in enumerate(thancadconf.thanColUser):
            if col is None: continue
            thc = thanatt.thanAttCol(col)
            self.rbut[i].config(bg=thc.thanTk, activebackground=thc.thanTk, command=S(self.__updateChosen, str(thc)))

    def validate(self):
        "Returns true if the value chosen by the user is valid."
        thc = self.__updateChosen()
        if thc is None:
            p_gtkwid.thanGudModalMessage(self, "Invalid ThanCad color", "Error Message")
            return False
        if thc in (thanvar.THANBYPARENT, thanvar.THANPERSONAL):
            self.result = thc
        else:
            self.result = thc
        return True


    def destroy(self):
        "Deletes references to widgets, so that it breaks circular references."
        del self.rbut, self.thanCol, self.cbut, self.thanColRGB
        p_gtkwid.ThanDialog.destroy(self)


    def __del__(self):
        print("ThanColor ThanDialog", self, "dies..")
