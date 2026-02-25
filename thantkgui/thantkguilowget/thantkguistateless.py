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

This module defines stateless functionality, i.e. for events (mouse wheel events) which
are (almost) independent to state. It is used as a mixin to ThanCad's canvas.
"""
import tkinter
from p_ggen import Struct
from thanvar import thanLogTk, Canc
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric


class ThanStateLess:
    "A mixin for functionality independent to state."

    def __init__(self):
        "Initialize stateless object."
        self.__wheel = Struct()
        self.__wheel.preempt = False
        self.__wheel.idle = 0
        self.__wheel.task = None
        self.thanEconoRaster = True      # Economise raster regens in zoom (wheel)
        self.thanTempItems = set()       # Temporary tkinter items, which must be deleted in case of error


    def thanUpwheel(self, evt, fact=0.8):
        "Mouse wheel up - zoom out."
        if self.__wheel.preempt:
            thanLogTk.warning("__up_zoomout called preemptively; returning immediately.")
            return
        self.__wheel.preemt = True
        dc = self.thanProj[2].thanCanvas
        if self.__wheel.idle == 0:
            self.__wheel.idle = 1
            self.__wheel.task = dc.after(500, self.__wheelClear)
            self.__wheel.preemt = False
            return
        x = dc.canvasx(evt.x); y = dc.canvasy(evt.y)        # canvas units
        if self.__wheel.idle == 1:
            if dc.thanState == THAN_STATE.ZOOMDYNAMIC: return #The user already zooms (RealTime)
            dc.after_cancel(self.__wheel.task)
            dc.thanCh.thanDisable()                           #Zoom is clearer without croshair
            if self.thanEconoRaster:
                for im in self.thanProj[2].thanImages:
                    for item2 in self.find_withtag(im.thanTags[0]):
                        if self.type(item2) != "image": continue
                        self.delete(item2) #  Delete Images (they can't be zoomed), but not rectangles
                        break
                self.__regenTexts(rectangle=True)

#            self.__prepareZoom(x, y)
            self.__wheel.idle = 2
        dc.after_cancel(self.__wheel.task)
        dc.scale(tkinter.ALL, x, y, fact, fact)
        self.thanOState.thanZoomXyr(x, y, fact)
        self.__notifyScale(x, y, 1.0/fact)
        self.__wheel.task = dc.after(500, self.__notifyWheelEnd)
        self.__wheel.preemt = False


    def __notifyScale(self, xc, yc, fact):
        "Notify drawing that the zoom has changed."
#        self.__calcZoom()
        dc = self.thanProj[2].thanCanvas
        dc._resultCoor(xc, yc)
        w = self.thanProj[2].thanDoZoomRT(dc.thanLastResult[0], fact)
        v = self.thanProj[1].viewPort
        v[:] = w
        if not self.thanEconoRaster:
            self.thanProj[2].thanAutoRegen(regenImages=True)     # Regen images only if zoom realtime is finished
            self.__regenTexts(rectangle=False)


    def __regenTexts(self, rectangle=False):
        "Regenerate texts because tkinter does not scale (zoom) text size."
        dc = self.thanProj[2].thanCanvas
        tagel = self.thanProj[1].thanTagel
        lt = self.thanProj[1].thanLayerTree
        than = self.thanProj[2].than
        dilay = lt.dilay
        #for item in dc.find_all():      #Thanasis2017_01_02
        nexist = 0
        for item in dc.find_withtag("textel"):
            temp = dc.type(item)
            if temp is None:       #Tk bug: Thanasis2020_05_17: item is nonexistent; this item has also no tags..
                dc.delete(item)    #..and the following code fails
                nexist += 1
                continue
            tags = dc.gettags(item)
            #if len(tags) < 2: continue      # We avoid current (rubber line)
            titem = tags[0]
            elem = tagel[titem]
            #if elem.thanElementName != "TEXT": continue
            lay = dilay[elem.thanTags[1]]
            lay.thanTkSet(than)
            selected = "selall" in tags   #If we pan/zoom inside a selection command, check if image is selected
            dc.delete(titem)              # Delete Rectangle and image (if not already deleted)
            elem.thanTkDraw1(than, rectangle)         # Restore this text
            if selected: dc.addtag_withtag("selall", titem)  # reselect text if it was selected
        if nexist>0: print(nexist, "nonexistent canvas items deleted.")
        self.thanProj[2].thanRedraw()     # Text regen probably violated draworder #Not really
        lt.thanCur.thanTkSet(than)        # set current layer's attributes


    def __wheelClear(self):
        "Clear attempt to use the wheel."
        self.__wheel.idle = 0


    def __notifyWheelEnd(self):
        "Notify drawing that the zoom has changed."
        dc = self.thanProj[2].thanCanvas
        dc.thanCh.thanEnable()
        if self.thanEconoRaster:
            self.thanProj[2].thanAutoRegen(regenImages=True)     # Regen images only if zoom realtime is finished
            self.__regenTexts(rectangle=False)
        self.__wheel.idle = 0


    def thanDownwheel(self, evt):
        "Mouse wheel down - zoom in."
        self.thanUpwheel(evt, fact=1.25)


    def thanPanPage(self, evt, ix, iy):
        "Page up,down,left,right."
        dx, dy = self.thanProj[2].thanPanPage(ix, iy)
        if dx != 0.0 and dy != 0.0: return "break"
#       if self.__x1 is not None:
#           self.__x1 += dx
#           self.__y1 += dy
#       if self.__x2 is not None:
#           self.__x2 += dx
#           self.__y2 += dy
        return "break"


    def thanCleanup(self):
        "Do cleanup after error/command-line action."
        dc = self
        self.__wheel.preempt = False
        self.__wheel.idle = 0
        self.__wheel.task = None
        for item in self.thanTempItems:
            dc.delete(item)
        self.thanTempItems.clear()

#        self.thanProj[2].thanStatusxy(self.thanXcu, self.thanYcu)
        dc.config(cursor="")
        self.thanLastResult = Canc, None

        dc.thanOsnap.thanCleanup()
        dc.thanOrtho.disable()

        if self.thanFloatMenu is not None and self.thanFloatMenu.winfo_ismapped():
            self.thanFloatMenu.unpost()

        self.thanState = THAN_STATE.NONE
        self.thanOState = ThanStateGeneric(self.thanProj)
