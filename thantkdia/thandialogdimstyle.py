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

This dialog asks for the dimension style parameters.
"""

#The following commented out import is in order for the test1() function
#to work as standalone.
#import sys
#sys.path.append("/home/a12/h/b/cad/thancad/work/tcadtree.52foithtes")
#import thanopt             # This runs a test for the needed modules automatically
#thanopt.thanInitPregui()


import tkinter
import p_gtkwid, p_ggen
from thandefs import ThanDimstyle
from thantrans import T


class ThanDialogDimstyle(p_gtkwid.ThanComDialog):
    "Dialog for the dimension style parameters."

    def __init__(self, *args, **kw):
        "Just set the title."
        proj = kw["cargo"]
        self.dimstyles = kw.pop("dimstyles", ())
        self.changename = kw.pop("changename", False)
        kw.setdefault("title", "%s - %s" % (proj[0].name, T["Dimension Style"]))
        super().__init__(*args, **kw)


    #    s.entName = self.thanName
    #    s.entDesc = self.thanDesc
    #    s.choNdigits  = self.thanDigits    #decimal digits: "2"
    #    s.entTextsize = self.thanTextsize
    #    s.choTicktype = self.thanTicktypes.index(self.thanTicktype)
    #    s.entTicksize = self.thanTicksize

    def thanValsDef(self):
        "Build default values."
        temp = ThanDimstyle()    #Dimstyle with default values
        s = temp.thanTodialog(self.thanProj)
        return s

    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraDesc(     win, 0, 0)
        self.fraText(     win, 1, 0)
        self.fraArrowhead(win, 2, 0)


    def fraDesc(self, win, irfra, icfra):
        "Widgets for text settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=irfra, column=icfra, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)

        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["DIMENSION STYLE DESCRIPTION:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        key = "entName"
        tit = "Style name"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        if self.changename:
            val = p_gtkwid.ThanValUniqname(others=self.dimstyles)
        else:
            wid.config(state=tkinter.DISABLED)
            val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))

        ir += 1
        key = "entDesc"
        tit = "Style description"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))


    def fraText(self, win, irfra, icfra):
        "Widgets for text settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=irfra, column=icfra, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)

        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["DIMENSION TEXT SETTINGS:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        labs = tuple("0123456789")
        key = "choNdigits"
        tit = "Number of decimal digits"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanChoice(fra, labels=labs, width=5)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))

        ir += 1
        key = "entTextsize"
        tit = "Dimension text size"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, T[tit], wid, val))


    def fraArrowhead(self, win, irfra, icfra):
        "Widgets for arowhead settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=irfra, column=icfra, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)

        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["ARROWHEAD SETTINGS:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        key = "choTicktype"
        tit = "Type of arrowheads"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanChoice(fra, labels=ThanDimstyle.thanTicktypes, width=20)
        wid.grid(row=ir, column=2, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))

        ir += 1
        key = "entTicksize"
        tit = "Tick size"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=ir, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0e-6, 1.0e6)
        self.thanWids.append((key, T[tit], wid, val))


    def fraLin(self, win, ir):
        "Widgets for simplification settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir-1, column=0, pady=5, sticky="wesn")
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["SIMPLIFIED LINES:"])
        lab.grid(row=0, column=1, columnspan=2, sticky="w")

        key = "choKeep"
        tit = "Keep original lines after simplification"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=1, column=1, sticky="e")
        wid = p_gtkwid.ThanYesno(fra,width=5)
        wid.grid(row=1, column=2, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))

        tit = "If the original lines are kept, the simplified lines should be put\n"\
              "into another layer (by changing the current layer)."
        lab = tkinter.Label(fra, text=T[tit], anchor="w", justify=tkinter.LEFT)
        lab.grid(row=2, column=1, columnspan=2, sticky="w", pady=5)
        fra.columnconfigure(2, weight=1)



class ThanDimstyleManager(p_gtkwid.ThanComDialog):
    "Dialog for the dimension style parameters."

    def __init__(self, *args, **kw):
        "Just set the title."
        proj = kw["cargo"]
        self.dimstyles = dict((key, dst.thanClone()) for key,dst in proj[1].thanDimstyles.items())
        kw.setdefault("title", "%s - %s" % (proj[0].name, T["Dimension Style Manager"]))
        p_gtkwid.ThanComDialog.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        s = p_ggen.Struct("Dimension style parameters")
        s.lstStyles  = 0    #First style
        #s.entTextsize = 0.20
        #s.choTicktype = 0  #"Architectural tick"
        #s.entTicksize = 0.20  #0.15
        #s.entScale   = 1.0
        return s


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraText(     win, 0, 0)
        #self.fraArrowhead(win, 0, 1)
        #self.fraOverall(  win, 1, 0)
        #self.columnconfigure(1, weight=1)


    def fraText(self, win, irfra, icfra):
        "Widgets for text settings."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=irfra, column=icfra, pady=5, sticky="wesn")
        fra.columnconfigure(2, weight=1)

        ir = 0
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["DIMENSION TEXT SETTINGS:"])
        lab.grid(row=ir, column=1, columnspan=2, sticky="w")

        ir += 1
        key = "lstStyles"
        tit = "Styles:"
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="w")
        ir += 1
        wid = p_gtkwid.ThanListbox(fra, width=30)
        wid.grid(row=ir, column=1, rowspan=4, sticky="we")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, T[tit], wid, val))
        self.__listrefill(wid)

        ir = 1
        ir += 1
        but = p_gtkwid.ThanButton(fra, text=T["New"], command=self.__butnew)
        but.grid(row=ir, column=2, padx=5, sticky="we")
        ir += 1
        but = p_gtkwid.ThanButton(fra, text=T["Copy"], command=self.__butcopy)
        but.grid(row=ir, column=2, padx=5, sticky="we")
        ir += 1
        but = p_gtkwid.ThanButton(fra, text=T["Modify"], command=self.__butmodify)
        but.grid(row=ir, column=2, padx=5, sticky="we")
        ir += 1
        but = p_gtkwid.ThanButton(fra, text=T["Delete"], command=self.__butdelete)
        but.grid(row=ir, column=2, padx=5, sticky="we")


    def __listrefill(self, wid=None, sel=""):
        "Recreate the listbox."
        labs = sorted(self.dimstyles.keys())
        if sel == "_current":
            lay = self.thanProj[1].thanLayerTree.thanCur
            sel = lay.thanAtts["dimstyle"].thanVal[0]
        try: isel = labs.index(sel)
        except ValueError: isel = 0
        if wid is None: wid = self.lstStyles
        wid.thanSetitems(labs)
        wid.select_set(isel)
        wid.see(isel)


    def __butnew(self):
        "Create a new dimstyle."
        for i in range(1, 100):
            nam1 = 'newdimstyle{}'.format(i)
            if nam1 not in self.dimstyles: break
        self.__makenew(nam1)


    def __makenew(self, nam1):
        "Create a new dimstyle."
        dst = ThanDimstyle()
        dst.thanSet(nam1)
        vals = dst.thanTodialog(self.thanProj)
        dia = ThanDialogDimstyle(self, vals=vals, cargo=self.thanProj,
            dimstyles=self.dimstyles, changename=True)
        r = dia.result
        if r is None: return
        dst.thanFromdialog(self.thanProj, r)
        self.dimstyles[dst.thanName] = dst
        self.__listrefill(sel=dst.thanName)


    def __butcopy(self):
        "Create a new dimstyle copying existing."
        i = self.lstStyles.thanGet()
        nam = self.lstStyles.thanGetitem(i)
        for i in range(1, 100):
            nam1 = '{}_copy{}'.format(nam, i)
            if nam1 not in self.dimstyles: break
        self.__makenew(nam1)


    def __butmodify(self):
        "Edit and modify an existing dimstyle."
        i = self.lstStyles.thanGet()
        nam = self.lstStyles.thanGetitem(i)
        dst = self.dimstyles[nam]
        vals = dst.thanTodialog(self.thanProj)
        dia = ThanDialogDimstyle(self, vals=vals, cargo=self.thanProj,
            dimstyles=self.dimstyles, changename=False)
        r = dia.result
        if r is None: return
        dst.thanFromdialog(self.thanProj, r)


    def __butdelete(self):
        "Edit and modify an existing dimstyle, if not used."
        i = self.lstStyles.thanGet()
        nam = self.lstStyles.thanGetitem(i)
        if nam == "standard":
            p_gtkwid.thanGudModalMessage(self,
                T["Special style {} can not be deleted"].format(nam),
                T["Special dimension style"], p_gtkwid.ERROR)
            return

        lay = self.thanProj[1].thanLayerTree.thanFindAtt1("dimstyle", nam)
        if lay is not None:
            p_gtkwid.thanGudModalMessage(self,
                T["Can not delete {}: style is used by layer {}"].format(nam, lay.thanGetPathname()),
                T["Dimension style in use"], p_gtkwid.ERROR)
            return
        del self.dimstyles[nam]
        self.__listrefill(sel="")


def test1():
    "Test the dialogs."
    root = tkinter.Tk()
    proj = [ p_ggen.path("xxxx"), p_ggen.Struct(), root]
    proj[1].thanDimstyles = dict(standard=ThanDimstyle(), a=ThanDimstyle(),
        b=ThanDimstyle())
    dia = ThanDimstyleManager(root, cargo=proj)
    #dia = ThanDialogDimstyle(root, cargo=proj, dimstyles=proj[1].thanDimstyles, changename=False)
    r = dia.result
    if r is None: print(r)
    else: print(r.anal())
#    root.mainloop()

if __name__ == "__main__":
    test1()
