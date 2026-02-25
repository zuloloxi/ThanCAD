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

This module defines functionality necessary for user lowlevel interaction in
a drawing window.
"""

import p_ggen
import tkinter
from thanvar import thanLogTk
from thantrans import T
from .thantkguicroshair import CrosHair, ThanCrosHairs
from .thantkconst import THAN_STATE, thanCursor
from .thantkguiosnap import ThanOsnap, ThanOrtho

from .thantkguistateless import ThanStateLess
from .thantkguigeneric   import ThanStateGeneric
from .thantkguidrag      import ThanStateDrag
from .thantkguimove      import ThanStateMove
from .thantkguiline      import ThanStateLine, ThanStateLine2, ThanStatePolar, ThanStateAzimuth
from .thantkguicircle    import ThanStateCircle, ThanStateCircle2, ThanStateCircle3, ThanStateArc
from .thantkguirect      import ThanStateRectangle, ThanStateRectratio
from .thantkguiroad      import ThanStateRoadp, ThanStateRoadr
from .thantkguispline    import ThanStateSplinep
from .thantkguiellipse   import ThanStateEllipseb
from .thantkguivar       import ThanStatePoint, ThanStateSelem


class ThanTkGuiLowGet(tkinter.Canvas, ThanStateLess):
    "Lowlevel input from a Tk canvas."

#============================================================================

    def __init__(self, proj, *args, **kw):
        "Initialise base class and then this class."
        ThanStateLess.__init__(self)
        tkinter.Canvas.__init__(self, proj[2], *args, **kw)
        self.__sb = proj[2].thanStatusBar

#-------Do some local initialisation

        dc = self
        dc.bind("<Key>",             self.__onChar)     # This should be deleted, or at least redirected to thanCom
        dc.bind("<Shift-Button-3>",  self.__onDclick)
        dc.bind("<Button-1>",        self.__onClick)
        dc.bind("<Button-3>",        self.__onClickr)
        dc.bind("<Motion>",          self.__onMotion)
        dc.bind("<B1-Motion>",       self.__onMotionDrag)
        dc.bind("<ButtonRelease-1>", self.__onReleaseDrag)
        if p_ggen.Pyos.Windows:
            dc.bind("<MouseWheel>",      self._mouseWheel)
            proj[2].bind("<MouseWheel>", self._mouseWheelp)   # Hack for Windows: Yeha, Windows "just works", no need for hacks
            dc.bind("<Shift-MouseWheel>",      self._shiftmouseWheel)
            proj[2].bind("<Shift-MouseWheel>", self._shiftmouseWheelp)   # Hack for Windows: Yeh, Windows "just works", no need for hacks
        else:
            dc.bind("<Button-4>",        self.__downwheel)
            dc.bind("<Button-5>",        self.__upwheel)
            dc.bind("<Shift-Button-4>",  self.__shiftdownwheel)
            dc.bind("<Shift-Button-5>",  self.__shiftupwheel)

        if not p_ggen.Pyos.Windows:
            self.bind("<Page_Up>",        self.thanPanpageup)
            self.bind("<Shift-Page_Up>",  p_ggen.doNothing)
            self.bind("<Page_Down>",      self.thanPanpagedown)
            self.bind("<Shift-Page_Down>",p_ggen.doNothing)
        self.bind("<Control-Up>",    self.thanPanpageup)
        self.bind("<Control-Down>",  self.thanPanpagedown)
        self.bind("<Control-Left>",  self.thanPanpageleft)
        self.bind("<Control-Right>", self.thanPanpageright)
        self.bind("<F7>", self.__onF7)

        self.thanState = THAN_STATE.NONE
        self.thanOState = ThanStateGeneric(proj)

        dc.update_idletasks()                 # _idletasks breaks WinDoze (98?) support. Skotistika
        mx = dc.winfo_width() - 1
        my = dc.winfo_height() - 1
        self.thanXcu = dc.canvasx(mx // 2)
        self.thanYcu = dc.canvasy(my // 2)

        self.thanChs = ThanCrosHairs(proj)
        self.thanCh = CrosHair(dc)
        self.after(250, self.thanCh.resize)   # Give the Canvas a fourth of a second, to stabilise

        self.thanOsnap = ThanOsnap(proj)
        self.thanOrtho = ThanOrtho()
        self.thanStereoGridOn = True          # Support for red/blue stereo vision
        self.thanStereoOn = False             # Support for red/blue stereo vision
        self.thanFloatMenu = None
        self.thanProj = proj

#============================================================================

    def _mouseWheel(self, evt):
        "Mouse wheel up or down; for windows only."
        if evt.delta < 0: self.__upwheel(evt)
        else:             self.__downwheel(evt)
    def _mouseWheelp(self, evt):
        "Mouse wheel up or down when triggered on the parent; for windows only."
        self.update_idletasks()                   # so that .winfo_xxx() works
        evt.x = evt.x_root - self.winfo_rootx()
        evt.y = evt.y_root - self.winfo_rooty()
        if evt.delta < 0: self.__upwheel(evt)
        else:             self.__downwheel(evt)
    def _shiftmouseWheel(self, evt):
        "Mouse wheel up or down; for windows only."
        if evt.delta < 0: self.__shiftupwheel(evt)
        else:             self.__shiftdownwheel(evt)
    def _shiftmouseWheelp(self, evt):
        "Mouse wheel up or down when triggered on the parent; for windows only."
        self.update_idletasks()                   # so that .winfo_xxx() works
        evt.x = evt.x_root - self.winfo_rootx()
        evt.y = evt.y_root - self.winfo_rooty()
        if evt.delta < 0: self.__shiftupwheel(evt)
        else:             self.__shiftdownwheel(evt)

#============================================================================

    def __upwheel(self, evt): self.thanUpwheel(evt)
    def __downwheel(self, evt): self.thanDownwheel(evt)
    def __shiftupwheel(self, evt): self.thanCh.thanUpwheel(evt)
    def __shiftdownwheel(self, evt): self.thanCh.thanDownwheel(evt)

    def __onMotionDrag(self, evt): self.thanOState.thanOnMotionDrag(evt)
    def __onReleaseDrag(self, evt): self.thanOState.thanOnReleaseDrag(evt)
    def __onClick(self, evt): self.thanOnClick(evt)
    def __onClickr(self, evt): self.thanOnClickr(evt)

    def thanPanpagedown (self, evt): return self.thanPanPage(evt,  0, -1)
    def thanPanpageleft (self, evt): return self.thanPanPage(evt, -1,  0)
    def thanPanpageright(self, evt): return self.thanPanPage(evt,  1,  0)
    def thanPanpageup   (self, evt): return self.thanPanPage(evt,  0,  1)

    def __onF7(self, event): self.thanProj[2].thanCom.thanOnF7(event)

#============================================================================

    def _resultCoorRel0(self, dxp, dyp):
        "Convert relative pixel coordinates to user data units."
        self.thanLastResult = ([0.0]*self.thanProj[1].thanVar["dimensionality"], None)
        self.thanLastResult[0][:2] = self.thanProj[2].thanCt.local2GlobalRel(dxp, dyp)

    def _resultCoor(self, xp, yp):
        "Convert relative pixel coordinates to user data units."
        self.thanLastResult = (list(self.thanProj[1].thanVar["elevation"]), None)
        self.thanLastResult[0][:2] = self.thanProj[2].thanCt.local2Global(xp, yp)

#============================================================================

    def __onMotion(self, event):
        "Well, here is what should be drawn each time mouse moves."
        self.thanOsnap.active = "ena" in self.thanOsnap.types
        dc = self
        x = dc.canvasx(event.x)
        y = dc.canvasy(event.y)

        self.thanCh.draw(x, y)
        cc = list(self.thanProj[1].thanVar["elevation"])
        cc[:2] = self.thanProj[2].thanCt.local2Global(x, y)  # User coordinates (transformed from canvas coordinates)
        self.__sb.thanCoorMouse(cc)

        self.thanOState.thanOnMotion(event, x, y)

        self.thanXcu = x
        self.thanYcu = y
        if self.thanState != THAN_STATE.NONE and self.thanOsnap.active:
            self.after(10, self.thanOsnap.thanFind)


#============================================================================


    def thanOnClick(self, event):
        "Well, here is what should be done when mouse clicks."
        dc = self
#        dc.focus_set()              # This is needed otherwise text control gets characters?
        x = dc.canvasx(event.x)
        y = dc.canvasy(event.y)      # Click canvas coordinates

        if self.thanOsnap.active and self.thanOsnap.items != (): # If object snap, change click coordinates
            x = self.thanOsnap.x           # Canvas coordinates
            y = self.thanOsnap.y           # Canvas coordinates
            cc = self.thanOsnap.cc         # User coordinates (from object snap)
        else:
            cc = list(self.thanProj[1].thanVar["elevation"])
            x, y = self.thanOrtho.orthoxy(x, y)          # In case ortho is active
            cc[:2] = self.thanProj[2].thanCt.local2Global(x, y)  # User coordinates (transformed from canvas coordinates)

        self.__sb.thanCoorClick(cc)                      # Draw status text

        self.thanOState.thanOnClick(event, x, y, cc)

        self.thanXcu = x
        self.thanYcu = y

#============================================================================

    def thanOnClickr(self, event):
        "Well, here is what should be done when right mouse clicks."
        dc = self
#        dc.focus_set()              # This is needed otherwise text controls gets characters
        x = dc.canvasx(event.x)
        y = dc.canvasy(event.y)

        if self.thanOsnap.active and self.thanOsnap.items != (): # If object snap, change click coordinates
            x = self.thanOsnap.x           # Canvas coordinates
            y = self.thanOsnap.y           # Canvas coordinates
            cc = self.thanOsnap.cc         # User coordinates (from object snap)
        else:
            cc = list(self.thanProj[1].thanVar["elevation"])
            cc[:2] = self.thanProj[2].thanCt.local2Global(x, y)  # User coordinates (transformed from canvas coordinates)

        self.__sb.thanCoorClick(cc)                      # Draw status text

        self.thanOState.thanOnClickr(event, x, y, cc)

        if self.thanState == THAN_STATE.NONE:
            if self.thanFloatMenu is not None and self.thanFloatMenu.winfo_ismapped():
                self.thanFloatMenu.unpost()
            self.thanFloatMenu = self.__createFloatMenu()
            self.thanFloatMenu.post(event.x_root, event.y_root)


    def __createFloatMenu(self):
        m = tkinter.Menu(self, tearoff=False)
        fbeg = self.thanProj[2].thanGudCommandBegin
        m.add_command(label=T["P&aste to Original Coordinates"], command=lambda fbeg=fbeg: fbeg("pasteorig"))
        m.add_command(label="Repeat last command", command=lambda fbeg=fbeg: fbeg(""))
        m.add_command(label="Real time zoom",      command=lambda fbeg=fbeg: fbeg("zoomrealtime"))
        m.add_command(label="Real time pan",       command=lambda fbeg=fbeg: fbeg("panrealtime"))

#       m1 = Menu(m, tearoff=False)
#       m1.add_checkbutton(label="zoom  when window changes", variable=self.zoomWhenConf)
#       m1.add_checkbutton(label="regen when window changes", variable=self.regenWhenConf)
#       m1.add_separator()
#       m1.add_checkbutton(label="regen when zoom", variable=self.regenWhenZoom)
#       m1.add_checkbutton(label="regen when zoom all", variable=self.regenWhenZoomall)
#       m1.add_checkbutton(label="center when zoom", variable=self.centerWhenZoom)
#       m1.add_separator()
#       m1.add_checkbutton(label="show menu bar", variable=self.showMenubar)
#       m1.add_checkbutton(label="show tool bar", variable=self.showToolbar)

#       m.add_cascade(label="options", menu=m1)
        return m

#============================================================================

    def __onDclick(self, event):
        "On double click change to the next available croshair."
        self.thanChs.thanRotate(self.canvasx(event.x), self.canvasy(event.y))

#============================================================================

    def __onChar(self, event):
        "Well, here is what should be done when user presses a key."
        thanLogTk.error("onChar(): Unexpected Canvas <key> event redirected to ThanCom.")
        win = self.thanProj[2]
        win.thanTkSetFocus()
        win.thanCom.thanOnChar(event)

#============================================================================

    def thanPrepare(self, state, cc1=None, cc2=None, cc3=None, r1=None, t1=None, t2=None):
        "Sets the appropriate state and lets gui take on."
        ct = self.thanProj[2].thanCt
        x1, y1 = None, None
        if cc1 is not None: x1, y1 = ct.global2Local(cc1[0], cc1[1])    # Transform to local coordinates
        x2, y2 = None, None
        if cc2 is not None: x2, y2 = ct.global2Local(cc2[0], cc2[1])    # Transform to local coordinates
        x3, y3 = None, None
        if cc3 is not None: x3, y3 = ct.global2Local(cc3[0], cc3[1])    # Transform to local coordinates
        r1, t1 = r1, t1
        if r1 is not None: r1, r  = ct.global2LocalRel(r1, r1)  # Transform to local coordinates
        self.thanOsnap.cc1 = cc1

        dc = self
        dc.config(cursor=thanCursor.get(state, ""))
        if state == THAN_STATE.POINT1: state = THAN_STATE.POINT

        if state.value > THAN_STATE.DRAGFOLLOWS.value:
            self.thanOState = ThanStateDrag(self.thanProj)
        elif state == THAN_STATE.MOVE:
            self.thanOState = ThanStateMove(self.thanProj, x1, y1, t1)
        elif state == THAN_STATE.LINE:
            self.thanOState = ThanStateLine(self.thanProj, x1, y1)
        elif state == THAN_STATE.LINE2:
            self.thanOState = ThanStateLine2(self.thanProj, x1, y1, x2, y2)
        elif state == THAN_STATE.POLAR:
            self.thanOState = ThanStatePolar(self.thanProj, x1, y1, r1)
        elif state == THAN_STATE.AZIMUTH:
            self.thanOState = ThanStateAzimuth(self.thanProj, x1, y1, t1)
        elif state == THAN_STATE.CIRCLE:
            self.thanOState = ThanStateCircle(self.thanProj, x1, y1, coef=t1)
        elif state == THAN_STATE.CIRCLE2:
            self.thanOState = ThanStateCircle2(self.thanProj, x1, y1, coef=t1)
        elif state == THAN_STATE.CIRCLE3:
            self.thanOState = ThanStateCircle3(self.thanProj, x1, y1, x2, y2)
        elif state == THAN_STATE.ARC:
            self.thanOState = ThanStateArc(self.thanProj, x1, y1, r1, t1, clockwise=t2)
        elif state == THAN_STATE.POINT:
            self.thanOState = ThanStatePoint(self.thanProj)
        elif state == THAN_STATE.RECTANGLE:
            self.thanOState = ThanStateRectangle(self.thanProj, x1, y1, t1, t2)
        elif state == THAN_STATE.RECTRATIO:
            self.thanOState = ThanStateRectratio(self.thanProj, x1, y1, t1, cc1)
        elif state == THAN_STATE.ROADP:
            self.thanOState = ThanStateRoadp(self.thanProj, x1, y1, x2, y2,
                                             x3, y3, r1)
        elif state == THAN_STATE.ROADR:
            self.thanOState = ThanStateRoadr(self.thanProj, x1, y1, x2, y2,
                                             x3, y3, r1)
        elif state == THAN_STATE.SPLINEP:
            self.thanOState = ThanStateSplinep(self.thanProj, x1, y1, x2, y2)
        elif state == THAN_STATE.ELLIPSEB:
            self.thanOState = ThanStateEllipseb(self.thanProj, x1, y1, r1, t1)
        elif state == THAN_STATE.SNAPELEM:
            self.thanOState = ThanStateSelem(self.thanProj)

        self.thanState = state


#============================================================================

    def thanGudIdle(self):
        "Returns true if not in the middle of a command."
        return self.thanState == THAN_STATE.NONE


    def thanTkClear(self):
        "Clears a window."
        dc = self
        dc.delete(tkinter.ALL)                          # Clear window
        self.thanCh.resize()


    def thanGudCoorChanged(self):
        "System of canvas changed; redraw croshair."
        self.thanCh.resize()


    def destroy(self):
        "Deletes circular references."
        del self.__sb, self.thanProj, self.thanChs, self.thanCh,\
            self.thanOState, self.thanOsnap
        tkinter.Canvas.destroy(self)


    def __delete__(self):
        "Show that self is really deleted."
        print("thantklowget:", self, "has been freed.")


#############################################################################
#############################################################################

#MODULE LEVEL CODE. IT IS EXECUTED ONLY ONCE

if __name__ == "__main__":
    print(__doc__)
