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

This module defines various croshairs for ThanCad's canvas.
"""

from thanopt import thancadconf

class ThanCrosHairs:
    "An object which deals with croshairs."

    def __init__(self, proj):
        "Define which croshairs are going to be used."
        self.thanProj = proj
        self.thanSizeDynamic = 5*thancadconf.thanBSEL
        self.thanCrosHairs = [ (CrosHair,),
                               (CrosHairCros, self.thanSizeDynamic),
                               (CrosHairChi, self.thanSizeDynamic),
                               (CrosHairCircle, self.thanSizeDynamic),
                               (CrosHairRectangle, self.thanSizeDynamic),
                               (CrosHairRect, thancadconf.thanBSEL),
                               (CrosHairDummy,),
                             ]
        self.thanIcrosHair = [0]              # Set big croshair


    def thanRotate(self, x1=None, y1=None):
        "Changes the croshair."
        self.thanIcrosHair[-1] = (self.thanIcrosHair[-1] + 1) % len(self.thanCrosHairs)
        self.thanSet(self.thanIcrosHair[-1], x1, y1)


    def thanPush(self, i, x1=None, y1=None):
        "Change the cursor temporarily."
        i %= len(self.thanCrosHairs)
        self.thanIcrosHair.append(i)
        self.thanSet(self.thanIcrosHair[-1], x1, y1)


    def thanPop(self, x1=None, y1=None):
        "Change to the previous cursor."
        if len(self.thanIcrosHair) < 1: return
        del self.thanIcrosHair[-1]
        self.thanSet(self.thanIcrosHair[-1], x1, y1)


    def thanSet(self, i, x1=None, y1=None):
        "Set the croshair."
        dc = self.thanProj[2].thanCanvas
        i %= len(self.thanCrosHairs)
        if x1 is None:
            x1 = dc.thanCh.thanX1p
            y1 = dc.thanCh.thanY1p
        clas = self.thanCrosHairs[i][0]
        args = self.thanCrosHairs[i][1:]
        if isinstance(dc.thanCh, CrosHairResizeable): self.thanSizeDynamic = dc.thanCh.thanGetSize()
        dc.thanCh.thanDisable()
        dc.thanCh = clas(dc, *args)
        if isinstance(dc.thanCh, CrosHairResizeable): dc.thanCh.thanSetSize(self.thanSizeDynamic)
        dc.thanCh.resize(x1, y1)


#############################################################################
#############################################################################

class CrosHair(object):
    "Draws, moves, deletes and maintains a croshair in a canvas."

    def __init__(self, dc):
        "Initialise the croshair."
        self.thanDc = dc
        self.thanExists = 0
        self.thanX1p = -999999
        self.thanY1p = -999999
        self.thanOn = True
        self.thanChx = []
        self.resize()


    def destroy(self):
        "Break circular references."
        del self.thanDc


    def resize(self, x1=None, y1=None):
        "Recomputes the size of the croshair."
        dc = self.thanDc
        dc.update_idletasks()        # _idletasks breaks WinDoze (98?) support. Skotistika

        maxx = dc.winfo_width() - 1
        maxy = dc.winfo_height() - 1
        minx = 0
        miny = 0

        self.thanMinx = dc.canvasx(minx)
        self.thanMiny = dc.canvasy(miny)
        self.thanMaxx = dc.canvasx(maxx)
        self.thanMaxy = dc.canvasy(maxy)

        if self.thanExists:
#            self.thanX1p = dc.coords(self.thanCh1)[0]
#            self.thanY1p = dc.coords(self.thanCh2)[1]
            for it in self.thanChx:
                dc.delete(it)
            self.thanExists = 0

        if x1 is None: x1 = self.thanX1p; y1 = self.thanY1p
        if x1 < self.thanMinx or x1 > self.thanMaxx or \
           y1 < self.thanMiny or y1 > self.thanMaxy:
            x1 = self.thanMinx + (self.thanMaxx - self.thanMinx) // 2
            y1 = self.thanMiny + (self.thanMaxy - self.thanMiny) // 2
        self.draw(x1, y1)
#        self.thanX1p = x1; self.thanY1p = y1   !These are also set in .draw()


    def draw(self, x1, y1):
        "Draws a croshair and deletes previous croshair."
        if self.thanOn:
            dc = self.thanDc
            if self.thanExists:
#                dc.move(self.thanCh1, x1-self.thanX1p, 0)
#                dc.move(self.thanCh2, 0, y1-self.thanY1p)
                dc.coords(self.thanChx[0], x1, self.thanMiny, x1, self.thanMaxy,)
                dc.coords(self.thanChx[1], self.thanMinx, y1, self.thanMaxx, y1)
                for it in self.thanChx:
                    dc.lift(it)
            else:
                it1 = dc.create_line(x1, self.thanMiny, x1, self.thanMaxy, fill="red")
                it2 = dc.create_line(self.thanMinx, y1, self.thanMaxx, y1, fill="green")
                self.thanChx[:] = it1, it2
                self.thanExists = 1
        self.thanX1p = x1
        self.thanY1p = y1


    def delete(self):
        "Deletes the croshair from the canvas - if it exists."
        if self.thanExists:
            dc = self.thanDc
            for it in self.thanChx:
                dc.delete(it)
            self.thanExists = 0


    def thanEnable(self, x1=None, y1=None):
        "Enable the croshair."
        self.thanOn = True
        self.resize(x1, y1)


    def thanDisable(self):
        "Disable the croshair."
        self.thanOn = False
        self.delete()

    def thanUpwheel(self, evt): pass
    def thanDownwheel(self, evt): pass


class CrosHairRect(CrosHair):
    "Draws, moves, deletes and maintains a limited croshair in a canvas."

    def __init__(self, dc, size):
        "Take size as an argument."
        self.dx = self.dy = size//2
        CrosHair.__init__(self, dc)


    def draw(self, x1, y1):
        "Draws a croshair and deletes previous croshair."
        if self.thanOn:
            dc = self.thanDc
            if self.thanExists:
                dc.coords(self.thanChx[0], x1-self.dx, y1-self.dy, x1+self.dx, y1+self.dy)
                dc.lift(self.thanChx[0])
            else:
                it1 = dc.create_rectangle(x1-self.dx, y1-self.dy, x1+self.dx, y1+self.dy,
                    outline=thancadconf.thanColSel.thanTk)
                self.thanChx[:] = (it1,)
                self.thanExists = 1
        self.thanX1p = x1
        self.thanY1p = y1


#############################################################################
#############################################################################

class CrosHairResizeable(CrosHair):
    "A croshair whose size may be changes dynamically."

    def __init__(self, dc, size):
        "Take size as an argument."
        self.thanSizeor = self.thanSize = size
        CrosHair.__init__(self, dc)


    def thanGetSize(self):
        "Return current size."
        return self.thanSize


    def thanSetSize(self, size):
        "Set new size."
        self.thanSize = size
        self.resize()


    def thanResetSize(self):
        "Go back to the original size."
        self.thanSize = self.thanSizeor
        self.resize()


    def thanUpwheel(self, evt):
        "Make the size bigger."
        self.thanSize *= 0.9
        self.resize()


    def thanDownwheel(self, evt):
        "Make the size smaller."
        self.thanSize *= 1.1
        self.resize()


class CrosHairRectangle(CrosHairResizeable):
    "Draws, moves, deletes and maintains a limited croshair in a canvas."

    def draw(self, x1, y1):
        "Draws a croshair and deletes previous croshair."
        if self.thanOn:
            dx = dy = self.thanSize*0.5
            dc = self.thanDc
            if self.thanExists:
                dc.coords(self.thanChx[0], x1-dx, y1-dy, x1+dx, y1+dy)
                dc.lift(self.thanChx[0])
            else:
                it1 = dc.create_rectangle(x1-dx, y1-dy, x1+dx, y1+dy,
                    outline=thancadconf.thanColSel.thanTk)
                self.thanChx[:] = (it1,)
                self.thanExists = 1
        self.thanX1p = x1
        self.thanY1p = y1


class CrosHairCircle(CrosHairResizeable):
    "Draws, moves, deletes and croshair as a circle in a canvas."

    def draw(self, x1, y1):
        "Draws a croshair and deletes previous croshair."
        if self.thanOn:
            dx = dy = self.thanSize*0.5
            dc = self.thanDc
            if self.thanExists:
                dc.coords(self.thanChx[0], x1-dx, y1-dy, x1+dx, y1+dy)
                dc.lift(self.thanChx[0])
            else:
                it1 = dc.create_oval(x1-dx, y1-dy, x1+dx, y1+dy,
                   outline=thancadconf.thanColSel.thanTk)
                self.thanChx[:] = (it1,)
                self.thanExists = 1

        self.thanX1p = x1
        self.thanY1p = y1


class CrosHairChi(CrosHairResizeable):
    "Draws, moves, deletes and croshair as a circle in a canvas."

    def draw(self, x1, y1):
        "Draws a croshair and deletes previous croshair."
        if self.thanOn:
            dx = dy = self.thanSize*0.5
            dc = self.thanDc
            if self.thanExists:
                dc.coords(self.thanChx[0], x1-dx, y1-dy, x1+dx, y1+dy)
                dc.coords(self.thanChx[1], x1-dx, y1+dy, x1+dx, y1-dy)
                for it in self.thanChx:
                    dc.lift(it)
            else:
                it1 = dc.create_line(x1-dx, y1-dy, x1+dx, y1+dy,
                   fill=thancadconf.thanColSel.thanTk)
                it2 = dc.create_line(x1-dx, y1+dy, x1+dx, y1-dy,
                   fill=thancadconf.thanColSel.thanTk)
                self.thanChx[:] = (it1, it2)
                self.thanExists = 1
        self.thanX1p = x1
        self.thanY1p = y1


class CrosHairCros(CrosHairResizeable):
    "Draws, moves, deletes and maintains a limited croshair in a canvas."

    def draw(self, x1, y1):
        "Draws a croshair and deletes previous croshair."
        if self.thanOn:
            dx = dy = self.thanSize*0.5
            dc = self.thanDc
            if self.thanExists:
                dc.coords(self.thanChx[0], x1, y1-dy, x1, y1+dy)
                dc.coords(self.thanChx[1], x1-dx, y1, x1+dx, y1)
                for it in self.thanChx:
                    dc.lift(it)
            else:
                it1 = dc.create_line(x1, y1-dy, x1, y1+dy, fill="red")
                it2 = dc.create_line(x1-dx, y1, x1+dx, y1, fill="green")
                self.thanChx[:] = (it1, it2)
                self.thanExists = 1
        self.thanX1p = x1
        self.thanY1p = y1

#############################################################################
#############################################################################


class CrosHairDummy(CrosHair):
    "A croshair that does nothing."

    def draw(self, x1, y1):
        "Draws a croshair and deletes previous croshair."
        if self.thanOn:
            if self.thanExists:
                pass
            else:
                self.thanChx[:] = ()
                self.thanExists = 1
        self.thanX1p = x1
        self.thanY1p = y1
