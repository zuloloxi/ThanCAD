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

This module defines dragging state, i.e. the generic way that ThanCad responds to
dragging events like realtime zoom and realtime pan.
"""
import tkinter
from thanvar import thanLogTk
from .thantkconst import THAN_STATE
from .thantkguigeneric import ThanStateGeneric

class ThanStateDrag(ThanStateGeneric):
    "An object which interprets dragging events as events as ????."

    def __init__(self, proj):
        "initialize object."
        self.thanProj = proj
        self.thanStateDrag = THAN_STATE.DRAG2BEGIN
        self.__x2 = self.__y2 = self.__xa = self.__ya = self.__zoomorigc = self.__zooma = self.__zoomb = None


    def thanOnMotionDrag(self, event):
        "Well, here is what should be drawn each time mouse moves while it is pressed."
        if self.thanStateDrag == THAN_STATE.DRAG2BEGIN:  # User is not pressing mouse key, do nothing
#           self.__onMotion(event)
            return

#-------Initial values

        dc = self.thanProj[2].thanCanvas
        sb = self.thanProj[2].thanStatusBar
        x = dc.canvasx(event.x); y = dc.canvasy(event.y)                # canvas units
        cc = list(self.thanProj[1].thanVar["elevation"])
        cc[:2] = self.thanProj[2].thanCt.local2Global(x, y)  # User coordinates (transformed from canvas coordinates)
        sb.thanCoorMouse(cc)

#-------The first drag must be at least 3 points (the user accidentally dragged!)

        if self.thanStateDrag == THAN_STATE.DRAGFIRST:
            if abs(x-self.__x2) < 3 and abs(y-self.__y2) < 3: return
            self.__prepareZoom(x, y)

            dc.thanCh.thanDisable()          #  Disable croshair (dragging is clearer)
            if dc.thanState == THAN_STATE.ZOOMDYNAMIC:
                for im in self.thanProj[2].thanImages:
                    for item2 in self.find_withtag(im.thanTags[0]):
                        if self.type(item2) != "image": continue
                        self.delete(item2) #  Delete Images (they can't be zoomed), but not rectangles
                        break
            self.thanStateDrag = THAN_STATE.DRAGGING

#-------The user is dragging now

        if dc.thanState == THAN_STATE.PANDYNAMIC:
            dx = -int(x - dc.thanXcu)                    # pixels
            dy = -int(y - dc.thanYcu)                    # pixels
            dc.xview(tkinter.SCROLL, dx, tkinter.UNITS)
            dc.yview(tkinter.SCROLL, dy, tkinter.UNITS)
            x += dx     # Because the view window changed, local coords of elements (and croshair)
            y += dy     # did not change with these commands. Thus modify croshair coordinates,
                        # so that croshair remains at the same "view" position
        elif dc.thanState == THAN_STATE.ZOOMDYNAMIC:
            dy = int(y - dc.thanYcu)                     # pixels
            fact = 1.03, 1.03
            if dy < 0: fact = 0.97, 0.97
            args = (tkinter.ALL,) + self.__zoomorigc + fact
            dc.scale(*args)

#-------Ending values

        dc.thanXcu = x
        dc.thanYcu = y

#============================================================================

    def __prepareZoom(self, x, y):
        "Makes sentinel elements to prepare for zoom computation."
        dc = self.thanProj[2].thanCanvas
        dc.update_idletasks()               # _idletasks breaks WinDoze (98?) support. Skotistika
        self.__xa = dc.canvasx(0)
        self.__ya = dc.canvasy(0)
        self.__zoomorigc = x, y                                            # canvas units
        self.__zooma = dc.create_line(x-10000, y-10000, x-10001, y-10001)  # sentinel element
        self.__zoomb = dc.create_line(x+10000, y+10000, x+10001, y+10001)  # sentinel element
        dc.thanTempItems.add(self.__zoomorigc)   # Record items so that they can be..
        dc.thanTempItems.add(self.__zooma)       # ..deleted in case of error/command-line action
        dc.thanTempItems.add(self.__zoomb)

#============================================================================

    def thanOnReleaseDrag(self, event):
        "Well, here is what should be done after the end of dragging."
        if self.thanStateDrag == THAN_STATE.NONE: return
        if self.thanStateDrag == THAN_STATE.DRAGFIRST: return
        if self.thanStateDrag != THAN_STATE.DRAGGING:
            thanLogTk.warning("tklowget: onReleaseDrag was triggered before onClick: probably, the click was lost!")

#-------Initial values

        dc = self.thanProj[2].thanCanvas
        x = dc.canvasx(event.x)
        y = dc.canvasy(event.y)

        if dc.thanState == THAN_STATE.PANDYNAMIC:
            dc.update_idletasks()                                     # _idletasks breaks WinDoze (98?) support. Skotistika
            xa = dc.canvasx(0)
            ya = dc.canvasy(0)
            dc._resultCoorRel0(xa-self.__xa, ya-self.__ya)
            dc.thanCh.thanEnable(x, y)                              # Enable, resize and redraw the croshair
            dc.thanState = self.thanStateDrag = THAN_STATE.NONE

        elif dc.thanState == THAN_STATE.ZOOMDYNAMIC:
            if self.__zooma is None:
                thanLogTk.warning("tklowget: Release drag event triggered for no reason!")
                return
            self.__calcZoom()
            dc.thanCh.thanEnable(x, y)                              # Enable, resize and redraw the croshair
            dc.thanState = self.thanStateDrag = THAN_STATE.NONE
        else:
            assert False, "Unknown drag state="+str(dc.thanState)

#-------Ending values

        dc.thanXcu = x
        dc.thanYcu = y


    def __calcZoom(self):
        "Computes the zoom factor using the sentinel elements."
        dc = self.thanProj[2].thanCanvas
        ca = dc.coords(self.__zooma)
        cb = dc.coords(self.__zoomb)
        self.__debugZoom(ca, cb)     # Only for debugging
        dc._resultCoor(*self.__zoomorigc)
        dc.thanLastResult = (dc.thanLastResult[0], 20000.0 / (cb[0] - ca[0]))


    def __debugZoom(self, ca, cb):
        "Check that the center of zoom remained in place; code only for debug; not needed in production."
        cc = (ca[0]+cb[0])*0.5, (ca[1]+cb[1])*0.5
        cor = self.__zoomorigc
        if abs(cc[0]-cor[0])+abs(cc[1]-cor[1]) > 0.5:
            thanLogTk.warning("Zoom center should be: %f %f but is: %f %f \n     ca=%f %f\n     cb=%f %f"\
             % (self.__zoomorigc[0], self.__zoomorigc[1], cc[0], cc[1], ca[0], ca[1], cb[0], cb[1]))


    def thanOnClick(self, event, x, y, cc):
        "Well, here is what should be done when mouse clicks."
#        dc = self.thanProj[2].thanCanvas
#        dc.focus_set()              # This is needed otherwise text controls gets characters?
        if self.thanStateDrag == THAN_STATE.DRAG2BEGIN:
            self.__x2 = x
            self.__y2 = y
            self.thanStateDrag = THAN_STATE.DRAGFIRST


    def thanOnClickr(self, event, x, y, cc):
        "Well, here is what should be done when right mouse clicks."
        win = self.thanProj[2]
        dc = win.thanCanvas
        if dc.thanState == THAN_STATE.ZOOMDYNAMIC:
            win.thanScheduler.thanSchedule(win.thanGudCommandBegin, "panrealtime")
            win.thanCom.thanOnCharEsc(event)     # Finish zoom dynamic
        elif dc.thanState == THAN_STATE.PANDYNAMIC:
            win.thanScheduler.thanSchedule(win.thanGudCommandBegin, "zoomrealtime")
            win.thanCom.thanOnCharEsc(event)     # Finish pan dynamic
        else:
            assert False, "Unknown drag state="+str(dc.thanState)
