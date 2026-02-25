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

This module defines a mixin that copes with tkinter's 2 coordinate systems -
plus the world (user) coordinate system of ThanCad. All the zoom, pan,
autoregeneration, window-dimensions-related functions are here.

2007_03_13: I think that the canvas coordinates and the pixels coordinates
differ only by constant dx, dy. The dx, dy are changed with scrolling.
So, the dimensions of the canvas are the same if it is measured in pixel
coordinates or if it is measured in canvas coordinates.

The functions defined here should not interact with the user, i.e. accept input
or print information to the user.
"""

from math import sqrt, hypot
from tkinter import SCROLL, UNITS, ALL
from p_gmath import thanNearx, thanNear2, ThanRectCoorTransf, thanRoundCenter
from thanvar import Canc, thanLogTk
from thanopt import thancadconf
from thantrans import T
from .thantkguilowget.thantkconst import THAN_STATE


#############################################################################
#############################################################################

class ThanTkGuiCoor:
    """Mixin for viewport and coordinates transformation.

    tkinter maintains 2 coordinates systems. One is the actual pixel based
    system. The other is a logical system which tkinter maps to the pixel
    system. All drawings (lines, circles etc.) are defined in logical
    coordinates.

    On the other hand, ThanCad uses the world (or user) coordinate system.
    No wonder we need a separate mixin for handling the 3 coordinate
    systems.
    """

#============================================================================

    def __init__ (self):
        "Set viewport coordinates and compute coordinate transformation."
        (self.__pixPort, q) = self.__getWinExtent()
        v = self.thanProj[1].viewPort
        v[:] = self.__roundCenter(v)
        self.__worPort = list(v)
        self.thanCt = ThanRectCoorTransf()
        self.thanGudCalcScale()

        self.__zoomwin_preempt = False
        self.__onsizepreempt = False
        self.__autoregen_preempt = False
        self.__regen_preempt = False

        self.thanCanvas.bind("<Configure>", self.__onSize)    # Bind in the end, in order to avoid preemptive calls

    def thanCleanupRegen(self):
        "Cleanup this object's state."
        ret = self.__zoomwin_preempt   or \
              self.__onsizepreempt     or \
              self.__autoregen_preempt or \
              self.__regen_preempt
        self.__zoomwin_preempt = False
        self.__onsizepreempt = False
        self.__autoregen_preempt = False
        self.__regen_preempt = False
        return ret  #If this is true, then the cleanup was necessary


    def __getWinExtent(self):
        """Gets the size of current window.

        Caution: it returns the _CANVAS_ coordinates of the left down-corner
        and the right-up corner, as we see it on the monitor.
        Thus it can be used only by the gui-independent modules.
        The Tkgui-dependent modules should use other functions.
        IT DOES NOT CHANGE THE COORDINATE SYSTEM TRANSFORMATION.
        """
        dc = self.thanCanvas
        dc.update_idletasks()            # _idletasks breaks WinDoze (98?) support. Skotistika
        w = dc.winfo_width()             # Pixels
        h = dc.winfo_height()            # Pixels
        if w < 2 or h < 2: w, h  = self.__robustDim()[-2:]
        return ([0, h-1, w-1, 0],                                                 # Pixels
                [dc.canvasx(0), dc.canvasy(h-1), dc.canvasx(w-1), dc.canvasy(0)]) # Canvas units


    def __resetWinCoor(self):
        "Resets the logical coordinates of Tk canvas so that upper left is again 0,0."
        dc = self.thanCanvas
        dx = int(dc.canvasx(0))
        dy = int(dc.canvasy(0))
        dc.xview(SCROLL, -dx, UNITS)
        dc.yview(SCROLL, -dy, UNITS)
        dx = dc.canvasx(0)
        dy = dc.canvasy(0)
        assert dx==0 and dy==0, "Something wrong with resetWinCoor()??"
        print("__resetWinCoor(): Canvas reset to logical coordinates near 0,0")


    def thanGudGetDt(self, dpix=20):
        """Returns length in units of length equal to dpix pixels.

        This is needed in order to approximate a circle, ellipse, curve etc.
        with small line segments."""
        dx, dy = self.thanCt.global2LocalRel(1.0, 1.0)
        dt = hypot(1.0, 1.0)/hypot(dx, dy)*dpix    #This means that dt is about dpix pixels
        return dt


    def thanGudGetWincm(self):
        "Returns the width and height of the window in cm."
        width, height, widthmm, heightmm, w, h = self.__robustDim()
        return 0.1*widthmm*w/width, 0.1*heightmm*h/height

    def __robustDim(self):
        """Returns the dimensions of the window and screen in pixels and in mm.

        If tkinter answers wrong values, it is assumed that the monitor is
        19 inches, the ratio of height/width is assumed 0.75 and the resolution
        1024 x 768.
        """
        MON = 19.0; RATIO = 0.75; RESOL = (1024, 768)

        dc = self.thanCanvas
        dc.update_idletasks()                  # _idletasks breaks WinDoze (98?) support. Skotistika
        w = dc.winfo_width()                   # Pixels
        h = dc.winfo_height()                  # Pixels
        width  = self.winfo_screenwidth()      # Pixels
        height = self.winfo_screenheight()     # Pixels
        widthmm  = float(self.winfo_screenmmwidth())   # mm
        heightmm = float(self.winfo_screenmmheight())  # mm

        if widthmm < 2.0:
            thanLogTk.warning("TkCoor:robustDim: tkinter reported illegal screen dimensions: %fmmd x %fmm", widthmm, heightmm)
            if heightmm < 2.0:
                widthmm = MON*25.4 / sqrt(1+RATIO**2)
                heightmm = widthmm * RATIO
            else:
                widthmm = heightmm / RATIO
        elif heightmm < 2.0:
            thanLogTk.warning("robustDim: tkinter reported illegal screen dimensions: %fmmd x %fmm", widthmm, heightmm)
            heightmm = widthmm * RATIO

        if width < 2:
            thanLogTk.warning("robustDim: tkinter reported illegal screen dimensions: %dpix x %dpix", width, height)
            if height < 2:
                width, height = RESOL
            else:
                width = int(height / RATIO)
        elif height < 2:
            thanLogTk.warning("robustDim: tkinter reported illegal screen dimensions: %dpix x %dpix", width, height)
            height = int(width * RATIO)

        if w < 2 or h < 2:
            thanLogTk.warning("robustDim: tkinter reported illegal window dimensions: %dpix x %dpix", w, h)
            w, h = width, height
        return width, height, widthmm, heightmm, w, h


    def thanGudGetWinDim(self):
        """Returns the width and height of the window and screen.

        This is just a function to aid the developer and it should be deleted
        when debugging is done.
        """
        dc = self.thanCanvas
        dc.update_idletasks()                          # _idletasks breaks WinDoze (98?) support. Skotistika
        w = dc.winfo_width()                           # Pixels
        h = dc.winfo_height()                          # Pixels
        width  = self.winfo_screenwidth()              # Pixels
        height = self.winfo_screenheight()             # Pixels
        widthmm  = float(self.winfo_screenmmwidth())   # mm
        heightmm = float(self.winfo_screenmmheight())  # mm
        return w, h, width, height, widthmm, heightmm


    def thanGudGetBbox(self):
        """Finds the bounding box of all the entities in a tkinter Canvas; unfortunately it does not work."

        IT DOES NOT CHANGE THE COORDINATE SYSTEM TRANSFORMATION.
        """
        self.thanCanvas.update_idletasks()           # _idletasks breaks WinDoze (98?) support. Skotistika
        w = self.thanCanvas.bbox(ALL)
        if w is None: return w
        xlu, ylu, b, h = w
        return self.thanCt.local2Global(xlu, ylu+h) + self.thanCt.local2Global(xlu+b, ylu)


    def __roundCenter(self, w):
        """Rounds an abstract window w, so that it fits exactly to the actual (GuiDependent) window."

        IT DOES NOT CHANGE THE COORDINATE SYSTEM TRANSFORMATION.
        """
        return thanRoundCenter(w, self.__pixPort, per=6)   #After testinf delete following code
        xa, ya, xb, yb = self.__pixPort
        wpi = abs(xb - xa)
        hpi = abs(yb - ya)

        wun = w[2] - w[0]
        hun = w[3] - w[1]

        per = 6                                      # margin in pixels
        if wpi < 10*per or hpi < 10*per: per = 0     # no margin for very small windows
        if thanNearx(wun, 0.0):
            assert not thanNearx(hun, 0.0), "Zero world coordinates window dimensions"
            sx = sy = float(hpi - per) / hun
        elif thanNearx(hun, 0.0):
            sx = float(wpi - per) / wun
        else:
            sx = float(wpi - per) / wun
            sy = float(hpi - per) / hun
            if sy < sx: sx = sy
        dx = (wpi / sx - wun) * 0.5
        dy = (hpi / sx - hun) * 0.5
        return w[0]-dx, w[1]-dy, w[0]+wun+dx, w[1]+hun+dy

#===========================================================================

    def thanAutoRegen(self, regenImages=False):
        """Checks if a regen is required, usually after a pan or a zoom.

        Pan, as implemented with tkinter, handles images as expected.
        However, zoom, as implemented with tkinter, does not affect the size
        of the images; it affects only the insertion point of the image.
        Thus, when a zoom is performed, or when there is a possibility that
        a zoom was performed, regenImages should be set to True.
        IT DOES NOT CHANGE THE COORDINATE SYSTEM TRANSFORMATION.
        """
        if self.__autoregen_preempt:
            print("thanAutoRegen() called preemptively; returning immediately")
            return
        self.__autoregen_preempt = True

        if self.__isRegenNeeded():
            self.thanRegen()                      # This, of course, regenerates images too
        else:
            d = self.thanImages.copy()            # Shallow copy (i.e fast)
            self.thanImages.clear()
            n = 0
            lt = self.thanProj[1].thanLayerTree
            dilay = lt.dilay
            dc = self.thanCanvas
            for im in d:
                if regenImages or self.__isImageRegenNeeded(im):
                    n += 1
                    lay = dilay[im.thanTags[1]]
                    lay.thanTkSet(self.than)
                    titem = im.thanTags[0]
                    selected = "selall" in dc.gettags(titem)         #If we pan/zoom inside a selection command, check if image is selected
                    dc.delete(titem)              # Delete Rectangle and image (if not already deleted)
                    im.thanTkDraw(self.than)      # Restore this image
                    if selected: dc.addtag_withtag("selall", titem)  # reselect image if it was selected
                else:
                    self.thanImages.add(im)
            if n > 0:
                self.thanRedraw()                          # Image regen probably violated draworder
                lt.thanCur.thanTkSet(self.than)            # set current layer's attributes

        self.__autoregen_preempt = False


    def thanRegen(self):
        "Regenerates the current drawing."
        if self.__regen_preempt:
            print("thanRegen() called preemptively; returning immediately")
            return
        self.__regen_preempt = True
        self.thanCom.thanAppend(T["Regenerating drawing.."])
        self.thanImages.clear()
        self.thanCanvas.thanTkClear()           # Clear window
        self.__resetWinCoor()                   # Reset coordinates so that Canvas logical coordinates are near 0,0
        self.thanGudCalcScale()                 # It is neeeded because logical port was changed
        self.thanCanvas.thanGudCoorChanged()
        import time
        t1 = time.time()
        print("Regenerating elements..",)
        temp = self.than.markselected
        self.than.markselected = self.thanSelall
        self.thanProj[1].thanTkDraw(self.than)  # Repaint all the elements in the window
        self.than.markselected = temp
        t2 = time.time()
        print(t2-t1, "secs")
        self.__regen_preempt = False
        self.thanCom.thanAppend(T["end of regeneration.\n"])   # Inform that regeneration finished


    def thanRedraw(self):
        """Ensures the relative draworder of the layers.

        Redraw is really needed only when the drawing has raster images (and/or
        solid fill in the future). So when there are no raster images, it should
        simply return.
        On the other hand, thanRedraw() is called only when regenerating images
        (or the entire drawing), so the argument is mute. thanRedraw() is also called
        when the user changes the draw order of a layer (which is rare anyway).
        So, no optimisation to the code (Thanasis 2007_03_18).
        """
        leaflayers = sorted((lay.thanAtts["draworder"].thanVal, taglay)
                            for taglay,lay in self.thanProj[1].thanLayerTree.dilay.items()   #works for python2,3
                            if not lay.thanAtts["frozen"].thanVal
                           )
        dc = self.thanCanvas
        for i,tag in leaflayers: dc.lift(tag)
        self.thanUpdateLayerButton()                  # Show current layer again


    def __isRegenNeeded(self):
        """Checks if the visible part of the drawing is already in the tkinter Canvas.

        This routine is needed because if a drawing is big, it is not rendered
        onto the tkinter canvas as a whole, but only the part that is actually
        visible (and maybe a little more, so that we can avoid a regenerate
        when a small pan is done afterwards).
        This routine checks if any of the unrendered part of the drawing has
        become visible after a pan or a zoom.
        IT DOES NOT CHANGE THE COORDINATE SYSTEM TRANSFORMATION.
        """
        v = self.thanProj[1].viewPort
        q = self.thanProj[1].thanAreaIterated
        return q[0] is not None and v[0] < q[0] or\
               q[1] is not None and v[1] < q[1] or\
               q[2] is not None and v[2] > q[2] or\
               q[3] is not None and v[3] > q[3]


    def __isImageRegenNeeded(self, im):
        """Checks if the visible part of the image is already in the tkinter Canvas after a pan.

        Note that, after a zoom, the images must be regenerated anyway,
        since the tkinter scale does not scale images.
        This routine is needed because if an image is big, it is not rendered
        onto the tkinter canvas as a whole, but only the part that is actually
        visible (and maybe a little more, so that we can avoid a regenerate
        when a small pan is done afterwards).
        This routine checks if any of the unrendered part of the image has
        become visible after a pan.
        IT DOES NOT CHANGE THE COORDINATE SYSTEM TRANSFORMATION.
        """
        v = self.thanProj[1].viewPort
        q = im.view
        if im.imagez is None: return True    #The image object will not render the image if it is outside viewport
        return (q[0] is not None and v[0] < q[0] or    #if q[0] is none then it means q[0]=0 (nothing more to render in this direction)
                q[1] is not None and v[1] < q[1] or
                q[2] is not None and v[2] > q[2] or
                q[3] is not None and v[3] > q[3])

#===========================================================================

    def thanGudPan(self, dx, dy):
        """Pans the canvas and adjusts viewport's coordinates."

        IT CHANGES THE COORDINATE SYSTEM TRANSFORMATION.
        """
        ct = self.thanCt
#        dx, dy = ct.global2LocalRel(dx, dy)
#        dx, dy = int(dx), int(dy)
        dx, dy = ct.global2LocalReli(dx, dy)
        dxn, dyn = ct.local2GlobalRel(dx, dy)
        self.__worPort[0] += dxn
        self.__worPort[2] += dxn
        self.__worPort[1] += dyn
        self.__worPort[3] += dyn
        print("thanGudPan(): dx, dy=", dx, dy)
        print("thanGudPan(): new worPort=", self.__worPort)

        if abs(dx) > 1000000 or abs(dy) > 1000000:
            self.thanRegen()     # Canvas can't scroll more than biggest long. CHECK WITH NEWER VERSIONS OF tkinter
        else:
            dc = self.thanCanvas
            dc.xview(SCROLL, dx, UNITS)
            dc.yview(SCROLL, dy, UNITS)

            self.thanGudCalcScale()
            dc.thanGudCoorChanged()
        return tuple(self.__worPort), (dx, dy)


    def thanPanPage(self, ix, iy):
        """Pan integer number of pages to the left, right, up or down.

        One page is the area of the current viewport minus 10% overlap.
        You know, thAtCAD is never going to implement this.
        Fae xoma thAtCAD (Greeklish in text).
        I hate to write trademark notices :)
        """
#-------Calculate length to pan

        dr = self.thanProj[1]
        w = v = dr.viewPort
        dx = (w[2] - w[0])*0.9*ix
        dy = (w[3] - w[1])*0.9*iy
        if dy > 0:
            if w[3]+dy > dr.yMaxAct:
                dy = dr.yMaxAct - w[3]
                if dy <= 0.0: dy = 0.0
        elif dy < 0:
            if w[1]+dy < dr.yMinAct:
                dy = dr.yMinAct - w[1]
                if dy >= 0.0: dy = 0.0
        if dx > 0:
            if w[2]+dx > dr.xMaxAct:
                dx = dr.xMaxAct - w[2]
                if dx <= 0.0: dx = 0.0
        elif dx < 0:
            if w[0]+dx < dr.xMinAct:
                dx = dr.xMinAct - w[0]
                if dx >= 0.0: dx = 0.0

#-------Modify the viewport coordinates and redraw

        if dx != 0.0 or dy != 0.0:
            v[:], (dx, dy) = self.thanGudPan(dx, dy)      # thanGudPan may change dx, dy slightly (to make integer pixel)
            self.thanAutoRegen(regenImages=False)
        return dx, dy       # Logical coordinates (that is, pixel coordinates plus constant x, constant y)


    def thanPan2Points(self, cp, tol=0.1):
        """Pans the drawing so that all points cp are visible; CALLER MUST ALTER proj[1].viewPort. accordingly.

        If points are already visible with tolerance, no pan is done.
        Otherwise we try to pan the drawing to make the points visible with
        tolerance.
        If this is not possible, because the points are too far away from each
        other we also zoom out.
        The tolerance 0=<tol<=0.9 is a percentage to the current window."""
        assert len(cp) > 0, "No points to pan to!"
        assert 0.0 <= tol <= 0.9, "Tolerance out of bounds."
        w = self.__worPort
        dx = w[2]-w[0]
        dy = w[3]-w[1]
        tolxy = max(dx, dy)*tol
        xx = [cp1[0] for cp1 in cp]
        xmin = min(xx)-tolxy
        xmax = max(xx)+tolxy
        yy = [cp1[1] for cp1 in cp]
        ymin = min(yy)-tolxy
        ymax = max(yy)+tolxy
        if xmax-xmin < 0.01*dx and ymax-ymin < 0.01*dy and tol < 0.1:   # We have only 1 point, and tol is zero
            tolxy = max(dx, dy)*0.1
            xmin -= tolxy
            xmax += tolxy
            ymin -= tolxy
            ymax += tolxy
        wn = self.__roundCenter((xmin, ymin, xmax, ymax))
        print("xyminmax", xmin, ymin, xmax, ymax)
        print("wn=", wn)
        print("w=", w)
        inside = w[0] < wn[0] and\
                 w[1] < wn[1] and\
                 w[2] > wn[2] and\
                 w[3] > wn[3]
        print("inside=", inside)
        if inside: return None, None

        dxn = wn[2]-wn[0]
        dyn = wn[3]-wn[1]
        if dxn > dx or dyn > dy:
            print("Zoom to", wn)
            self.thanGudZoomWin(self, wn)           # Zoom is needed to make all points visible
            regenImages = True
        else:
            dx = (wn[2]+wn[0])*0.5 - (w[2]+w[0])*0.5
            dy = (wn[3]+wn[1])*0.5 - (w[3]+w[1])*0.5
            print("pan dx=", dx, "  dy=", dy)
            self.thanGudPan(dx, dy)
            regenImages = False
        return tuple(self.__worPort), regenImages

    def thanGudZoom(self, xc, yc, fact):
        """Zooms dynamically the canvas."

        IT CHANGES THE COORDINATE SYSTEM TRANSFORMATION.
        """
        dc = self.thanCanvas
        if fact != 0.0:          #If fact is zero do not zoom at all
            dx1 = xc - self.__worPort[0]
            dx2 = xc - self.__worPort[2]
            dy1 = yc - self.__worPort[1]
            dy2 = yc - self.__worPort[3]
            self.__worPort[0] = xc - dx1/fact
            self.__worPort[2] = xc - dx2/fact
            self.__worPort[1] = yc - dy1/fact
            self.__worPort[3] = yc - dy2/fact

            (xc, yc) = self.thanCt.global2Local(xc, yc)
            dc.scale(ALL, xc, yc, fact, fact)

#-------Because we scaled the elements the viewport's logical coordinates
#       remain the same. 2006-06-24: Nevermind, compute them again!!

        self.thanGudCalcScale()
        dc.thanGudCoorChanged()


    def thanGudGetPanRT(self, stat):
        """Pans the canvas in real time."

        IT CHANGES THE COORDINATE SYSTEM TRANSFORMATION.
        """
        res, cargo = self.thanWaitFor(stat, THAN_STATE.PANDYNAMIC)
        if res == Canc: return res

#-------The viewport is already panned, so we only change coordinates of viewport

        dx, dy = res[:2]
        self.__worPort[0] += dx
        self.__worPort[2] += dx
        self.__worPort[1] += dy
        self.__worPort[3] += dy

        self.thanGudCalcScale()
        return tuple(self.__worPort)


    def thanGudGetZoomRT(self, stat):
        """Zooms the canvas in real time."

        IT CHANGES THE COORDINATE SYSTEM TRANSFORMATION.
        """
        cc, fact = self.thanWaitFor(stat, THAN_STATE.ZOOMDYNAMIC)   # cc is res and fact is cargo
        if cc == Canc: return cc
        return self.thanDoZoomRT(cc, fact)


    def thanDoZoomRT(self, cc, fact):
        "The viewport is already zoomed, so we only change coordinates of vieport."
        (xc, yc) = cc[:2]
        dx1 = xc - self.__worPort[0]
        dx2 = xc - self.__worPort[2]
        dy1 = yc - self.__worPort[1]
        dy2 = yc - self.__worPort[3]
        self.__worPort[0] = xc - dx1*fact
        self.__worPort[2] = xc - dx2*fact
        self.__worPort[1] = yc - dy1*fact
        self.__worPort[3] = yc - dy2*fact

        self.thanGudCalcScale()
        return tuple(self.__worPort)


    def __onSize(self, event):
        """Well, here is what happens when window changed size.

        When the the window changes size, all drawn elements remain fixed in
        relation to the upper left-corner of the window. Thus the scale of
        the coordinate transfromation does not change.
        If the window shrinks, some elements near the lower-right become
        invisible.
        If the window is elnarged, some elements near the lower-right, which
        were invisible before, become visible.
        Thus the viewport (in world, logical, pixel coordinate) are modified
        to take this into account. Also, the transformation between the coordinate
        systems does not change - but we recalculate it anyway.
        IT CHANGES THE COORDINATE SYSTEM TRANSFORMATION.
        """
        if self.__onsizepreempt:
#            self.thanSchedule(self.__onSize, event)
            print("onSize() called preemptively: call NOT scheduled: returning immediately.")
            return
        self.__onsizepreempt = 1

        (pixPort, logPort) = self.__getWinExtent()
        if pixPort != self.__pixPort:
            w, h = logPort[2] - logPort[0], logPort[3] - logPort[1]
            thancadconf.thanCanvasdim[:] = w+1, -h+1
            w, h = self.thanCt.local2GlobalRel(w, h)
            self.__worPort[2] = self.__worPort[0] + w
            self.__worPort[1] = self.__worPort[3] - h
            self.thanGudCalcScale()

            self.thanProj[1].viewPort[:] = self.__worPort
            self.thanAutoRegen()
            self.thanCanvas.thanGudCoorChanged()
        else:
            print("tkguicoor.onSize() called, but window has not changed dimensions!")

        self.__onsizepreempt = 0


    def thanGudCalcScale(self):
        """Recalculates coordinate transformation.

        IT CHANGES THE COORDINATE SYSTEM TRANSFORMATION.
        """
        (self.__pixPort, logPort) = self.__getWinExtent()
        self.thanCt.set(self.__worPort, logPort)

#===========================================================================

    def thanGudZoomWin(self, worPortn):
        """Do a move and a zoom to show the viewport; CALLER MUST ALTER proj[1].viewPort accordingly.

        IT IMPLICITELY CHANGES THE COORDINATE SYSTEM TRANSFORMATION, via
        thanGudPan, thanGudZoom.
        """
        if self.__zoomwin_preempt:
            print("thanGudZoomWin() called preemptively; returning immediately")
            self.__zoomwin_preempt = 0
            return
        self.__zoomwin_preempt = 1

        print("thanGudZoomWin(): before: worPortn=", worPortn)
        if thanNear2(worPortn[:2], worPortn[2:]):
            self.thanProj[2].thanPrter("Can not zoom/pan to window %s" % (worPortn,))
            self.__zoomwin_preempt = 0
            return tuple(self.__worPort)
        worPortn = self.__roundCenter(worPortn)
        if thanNear2(worPortn[:2], worPortn[2:]):
            self.thanProj[2].thanPrter("Can not zoom/pan to window %s" % (worPortn,))
            self.__zoomwin_preempt = 0
            return tuple(self.__worPort)
        print("thanGudZoomWin(): after:  worPortn=", worPortn)

        if thanNear2(self.__worPort[:2], self.__worPort[2:]):   #Current viewport is invalid
            print("Current viewport is invalid:", self.__worPort)
            self.__worPort[:] = worPortn
            self.thanRegen()
            self.__zoomwin_preempt = 0
            return tuple(self.__worPort)

        xc = self.__worPort[0]*0.5 + self.__worPort[2]*0.5
        yc = self.__worPort[1]*0.5 + self.__worPort[3]*0.5
        xcn = worPortn[0]*0.5 + worPortn[2]*0.5
        ycn = worPortn[1]*0.5 + worPortn[3]*0.5
        print("thanGudZoomWin(): xc,  yc =", xc, yc)
        print("thanGudZoomWin(): xcn, ycn=", xcn, ycn)
        print("thanGudZoomWin(): worPort before pan=", self.__worPort)
        dx, dy = xcn-xc, ycn-yc
        dxp, dyp = self.thanCt.global2LocalReli(dx, dy)
        if dxp != 0 and dyp != 0:
            if thanNear2((xc-dx*0.5, yc-dy*0.5), (xc+dx*0.5, yc+dy*0.5)):  #Because of adding small to big numbers
                self.thanRegen()
                self.__zoomwin_preempt = 0
                return tuple(self.__worPort)
            self.thanGudPan(dx, dy)
        print("thanGudZoomWin(): worPort after  pan=", self.__worPort)

        dxn = worPortn[2] - worPortn[0]
        dyn = worPortn[3] - worPortn[1]
        if abs(dxn) > abs(dyn):    # For numerical stability; otherwise not needed
            fact = (self.__worPort[2] - self.__worPort[0]) / dxn
        else:
            fact = (self.__worPort[3] - self.__worPort[1]) / dyn
        self.thanGudZoom(xcn, ycn, fact)   #If zero factor do not zoom at all
        self.__zoomwin_preempt = 0
        return tuple(self.__worPort)


if __name__ == "__main__":
    print(__doc__)
