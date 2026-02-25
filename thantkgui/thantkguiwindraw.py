##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module defines a Tkinter window to display a ThanCad drawing.
"""

import weakref, Tkinter
import p_ggen, p_gtkuti, p_gtkwid
import thantk, thanvar, thancom, thanvers, thaneng, thanmenus, thanfonts
from thanopt import thancadconf
from thandefs.thanatt import ThanAttCol
from thantrans import T
import thantkguicoor, thantkguihighget, thantkguihighdraw, thantkguilowget
import thantkcmd, thantkstatus

thanfiles = thanvar.thanfiles
Canc = thanvar.Canc


class ThanTkGuiWinDraw(Tkinter.Toplevel,
                       thantkguicoor.ThanTkGuiCoor,
                       thantkguihighget.ThanTkGuiHighGet,
                       thantkguihighdraw.ThanTkGuiHighDraw):
    "A window which contains one drawing."

    def __initold__ (self, fpath, dr):
        "Initialise base classes and mixins and then this class."
        self.thanProj = [fpath, dr, self]
        self.thanTitle = thanvers.thanCadName + " - " + self.thanProj[0].name
        self.thanSelectLayButton = False                 # NOT in selection mode

        thantkguihighget.ThanTkGuiHighGet.__init__(self)
        thantkguihighdraw.ThanTkGuiHighDraw.__init__(self)
        self.thanScheduler = thanvar.ThanScheduler()

        Tkinter.Toplevel.__init__(self, master=thanfiles.ThanCad[2], class_=T["ThanDrawing"])
        self.__position()
        self.__createControls()
        self.thanScriptComs = ()

        self.than = p_ggen.Struct("ThanCad Tk GUI methods and options container")
        self.than.dc = self.thanCanvas
        self.than.thanInfoPush = self.thanStatusBar.thanInfoPush
        self.than.thanInfoPop = self.thanStatusBar.thanInfoPop
        self.than.viewPort = self.thanProj[1].viewPort        # Just a reference
        self.than.thanPoints = thanfonts.thanPoints
        self.than.thanFonts = thanfonts.thanFonts
        self.than.imageFrameOn = dr.thanVar["imageframe"]
        self.than.imageBrightness = 1.0
        self.than.strang = dr.thanUnits.strang
        self.than.strdir = dr.thanUnits.strdir
        self.than.strdis = dr.thanUnits.strdis
        self.than.strcoo = dr.thanUnits.strcoo
        self.than.markselected = set()    #These element will be drawn with the "selall" tag

        S = p_ggen.ThanStub
        B = self.thanGudCommandBegin
        self.protocol("WM_DELETE_WINDOW", S(B, "close")) # In case user closes window with window manager

        thantkguicoor.ThanTkGuiCoor.__init__(self)
        self.than.ct = self.thanCt                            # Just a reference
        self.than.thanImages = self.thanImages = set()        # For image zoom reasons
        self.thanImageCur = None

        self.thanProj[1].thanLayerTree.thanCur.thanTkSet(self.than, self.thanProj[1].thanTstyles)
        self.thanTkSetFocus()


    def __init__(self):
        "Initialise base classes and mixins and then this class."
        thantkguihighget.ThanTkGuiHighGet.__init__(self)
        thantkguihighdraw.ThanTkGuiHighDraw.__init__(self)
        self.thanScheduler = thanvar.ThanScheduler()
        self.thanProj = ["", None, self]

        Tkinter.Toplevel.__init__(self, master=thanfiles.ThanCad[2], class_=T["ThanDrawing"])
        self.__position()
        self.__createControls()

        S = p_ggen.ThanStub
        B = self.thanGudCommandBegin
        self.protocol("WM_DELETE_WINDOW", S(B, "close")) # In case user closes window with window manager


    def setDrawing(self, fn, dr):
        "Associate a ThanCad drawing with this drawing window."
        self.thanProj[:2] = fn, dr
        thantkguicoor.ThanTkGuiCoor.__init__(self)
        self.thanTitle = thanvers.thanCadName + " - " + self.thanProj[0].name
        self.title(self.thanTitle)
        self.thanSelectLayButton = False                 # NOT in selection mode

        self.than = p_ggen.Struct("ThanCad Tk GUI methods and options container")
        self.than.dc = self.thanCanvas
        self.than.thanInfoPush = self.thanStatusBar.thanInfoPush
        self.than.thanInfoPop = self.thanStatusBar.thanInfoPop
        self.than.viewPort = self.thanProj[1].viewPort        # Just a reference
        self.than.thanPoints = thanfonts.thanPoints
        self.than.thanFonts = thanfonts.thanFonts
        self.than.imageFrameOn = dr.thanVar["imageframe"]
        self.than.imageBrightness = 1.0
        self.than.strang = dr.thanUnits.strang
        self.than.strdir = dr.thanUnits.strdir
        self.than.strdis = dr.thanUnits.strdis
        self.than.strcoo = dr.thanUnits.strcoo
        self.than.markselected = set()    #These element will be drawn with the "selall" tag
        self.than.ct = self.thanCt                            # Just a reference
        self.than.thanImages = self.thanImages = set()        # For image zoom reasons
        self.thanImageCur = None
        self.thanScriptComs = ()

        self.thanProj[1].thanLayerTree.thanCur.thanTkSet(self.than, self.thanProj[1].thanTstyles)
        self.thanUpdateLayerButton()
        self.thanStatusBar.setProj(self.thanProj)
        self.thanCom.setProj()    #Notify that new drawing has been set into the project
        self.thanTkSetFocus()
        return self.thanProj

    def __position(self):
        "Position main window at top left; Later, add code to remember the last ThanCad's position, size etc."
        p = thanfiles.ThanCad[2].thanTkPos
        while p[-1][2]() == None: del p[-1]
        for i, (xx, yy, win) in enumerate(p):
            if win() == None:
                p[i] = xx, yy, weakref.ref(self)
                break
        else:
#            xx += 20; yy += 15
            xx += 0; yy += 15
            p.append((xx, yy, weakref.ref(self)))
        self.geometry("%+d%+d" % (xx, yy))
        self.group(thanfiles.ThanCad[2])


    def __createControls (self):
        "Creates various controls and sets attributes."
        self.config(background="#%2xd%2xd%2xd" % (238, 92, 66))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.thanMenu = thanmenus.ThanCadTkMenu(self)

        fra = Tkinter.Frame(self)
        fra.grid(row=0, column=0, sticky="we")
        lab = Tkinter.Label(fra, text=T["Layer:"])
        lab.grid(row=0, column=0, sticky="w")
        self.thanCurLayShow = p_gtkwid.ThanButton(fra, width=20, anchor="e", text="<Current Layer>",
            activebackground="green", command=self.__changeCurLay, takefocus=False)
        self.thanCurLayShow.grid(row=0, column=1, sticky="w")

        but = Tkinter.Button(fra, text=T["Change Layer.."], activebackground="green",
            command=lambda : self.thanGudCommandBegin("chprop"))
        but.grid(row=0, column=2, sticky="e")
        fra.columnconfigure(2, weight=1)

        self.thanStatusBar = thantkstatus.ThanStatusBar(self)
        self.thanStatusBar.grid(row=3, column=0, columnspan=2, sticky="swne")
        self.thanCanvas = thantkguilowget.ThanTkGuiLowGet(self.thanProj,
            width=thancadconf.thanCanvasdim[0], height=thancadconf.thanCanvasdim[1],
            background=thancadconf.thanColBack.thanTk,
            xscrollincrement=1, yscrollincrement=1)
        self.thanCanvas.grid(row=1, column=0, sticky="swne")

        self.thanCom = thantkcmd.ThanTkCmd(self.thanProj, bd=1, relief=Tkinter.SUNKEN, background="lightyellow",
                              height=5, maxlines=1000)
        self.thanCom.grid(row=2, column=0, columnspan=2, sticky="swne")

        import andreas
        fra = andreas.Combut(self.thanProj, self)
        fra.grid(row=0, column=1, rowspan=2, sticky="sn")

        thantk.deficon(self)   # Decorates toplevel window


    def thanTkSet(self, elem=None):
        "Sets the attributes of the layer that contains elem, or the current layer."
	dr = self.thanProj[1]
	if elem == None: lay = dr.thanLayerTree.thanCur
	else:            lay = dr.thanLayerTree.dilay[elem.thanTags[1]]
	lay.thanTkSet(self.than, dr.thanTstyles)


    def thanUpdateLayerButton(self, selected=False):
        "Show the name and colour of current layer, or currently selected elements."
	if selected and len(self.thanSelall) > 0:
	    lays = set(elem.thanTags[1] for elem in self.thanSelall)
	    assert len(lays) > 0, "How come that no layers were found, when there is at least one element????"
	    if len(lays) > 1:
                self.thanCurLayShow.config(fg="red", bg="black", text=T["<varies>"])
		return
	    dilay = self.thanProj[1].thanLayerTree.dilay
	    cl = dilay[lays.pop()]
	else:
	    cl = self.thanProj[1].thanLayerTree.thanCur
        colatt = cl.thanAtts["moncolor"]
        if colatt.than2Gray() < 127: col = "white"
        else:                        col = "black"
        self.thanCurLayShow.config(fg=col, bg=colatt.thanTk)
	self.thanCurLayShow.thanSet(cl.thanGetPathname())


    def __changeCurLay(self, evt=None):
        "Change the current layer, or the layer of selected elements."
        if not self.thanScheduler.thanSchedIdle():
            if self.thanSelectLayButton: self.thanCom.thanEnter("layer")  # ThanCad is in selection mode
            return
        lay = self.thanGudGetLayerleaf(T["Select new current layer"])
        if lay == Canc: return
        proj = self.thanProj
        proj[1].thanLayerTree.thanCur = lay
        lay.thanTkSet(proj[2].than, proj[1].thanTstyles)    # Set Attributes of the current layer
        proj[1].thanTouch()                                 # Drawing IS modified
        self.thanUpdateLayerButton()


    def destroy(self):
        "Deletes circular references."
#       self.thanCanvas.destroy()     # These are automatically called by Toplevel.destroy
#       self.thanCom.destroy()        # These are automatically called by Toplevel.destroy
#       self.thanStatusBar.destroy()  # These are automatically called by Toplevel.destroy
        del self.thanScheduler
        del self.than
        del self.thanProj, self.thanMenu, self.thanCurLayShow, self.thanCanvas
        del self.thanCom, self.thanStatusBar
        Tkinter.Toplevel.destroy(self)


    def __del__(self):
        print "ThanTkGuiWinDraw", self, "dies!"


    def thanTkSetFocus(self):
        "Sets focus to the command window."
        self.lift()
        Tkinter.Toplevel.focus_set(self)
        self.thanCom.focus_sette()

    def focus_set(self):
        "Set focus to command window."
        self.thanTkSetFocus()


if __name__ == "__main__":
    print __doc__
    gui = Tk()
    mainWindow = ThanTkGuiWinMain(gui)
    gui.mainloop()
