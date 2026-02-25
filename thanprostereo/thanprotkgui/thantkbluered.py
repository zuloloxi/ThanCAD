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

This is the professional part of ThanCad which is initially commercial.
The package supports 3dviewing with red/blue glasses.
The subpackage contains the enhanced Tk canvas to support 3d viewing.
This module contains the enhanced Tk canvas to support 3d viewing.
"""

import p_gstereo
from thanopt import thancadconf
from thantkgui.thantkguilowget import ThanTkGuiLowGet, CrosHair

#ThanTkGuiLowGet.__bases__ += (Bluered3d,)

class ThanTkBlueRed(ThanTkGuiLowGet):
    "Blue red 3D visualisation mixin for ThanTkGuiLowGet."

    def __init__(self, proj, *args, **kw):
        "Set if the the zero surface will be drawn."
        ThanTkGuiLowGet.__init__(self, proj, *args, **kw)
        self.thanChs.thanCrosHairs.insert(-2, (CrosHairRect3d, thancadconf.thanBSEL))


    def thanStereoToggle(self):
        "Toggle red/blue stereo vison on and off."
        self.thanStereoOn = not self.thanStereoOn
        if self.thanStereoOn:
            self.thanChs.thanPush(-3)
            self.thanRestereo()
        else:
            self.thanChs.thanPop()
            than = self.thanProj[2].than
            than.stereo = None
            self.thanProj[2].thanRegen()
#            self.delete("enull0")        #No need to erase: thanRegen() has already deleted it


    def thanRestereo(self):
        "Recalculate the stereo transformation."
        if self.thanStereoOn:
            var = self.thanProj[1].thanVar
            than = self.thanProj[2].than
            than.stereo = p_gstereo.Zparallax(var["elevation"][2], var["elevationstep"][2])
            self.thanProj[2].thanRegen()
            if self.thanStereoGridOn: self.br3dZeroSurface()


    def thanStereoGridToggle(self):
        "Toggle red/blue stereo vison on and off."
        self.thanStereoGridOn = not self.thanStereoGridOn
        if self.thanStereoOn and self.thanStereoGridOn:
            self.br3dZeroSurface()
        else:
            self.delete("enull0")


    def thanGudCoorChanged(self):
        "System of canvas changed; redraw croshair, blue red grid."
        self.thanCh.resize()
        if self.thanStereoOn and self.thanStereoGridOn:
            self.br3dZeroSurface()


    def pointpair(self, x1, y1, size, paral, tags=()):
        "Draw 1 red and 1 cyan square centered at jx, iy with size and parallax paral."
        dx = dy = max(size//2, 1)
        ip2 = int(paral//2)
        jxb = x1-dx-ip2
        jxr = x1-dx+paral-ip2
        iy = y1-dy
        return self.redbluepair(jxb, jxr, iy, s=2*dx+1, tags=tags)


    thanFormTkcol = "#%02x%02x%02x"
    blue = thanFormTkcol % (0, 255, 255)     #r,g,b to tk
    red  = thanFormTkcol % (255, 0, 0)       #r,g,b to tk
    blred = thanFormTkcol % (255, 255, 255)  #r,g,b to tk
    del thanFormTkcol

    def redbluepair(self, jxb, jxr, iy, s, tags=()):
        "Plot a red blue point pair."
        if jxb == jxr:
            it1 = self.create_rectangle(jxb, iy, jxb+s, (iy+s), outline=self.blred, tags=tags)
            return (it1,)
        j1, c1 = jxb, self.blue
        j2, c2 = jxr, self.red
        if jxb > jxr: j1, c1, j2, c2 = j2, c2, j1, c1
        if j1+s < j2:
            it1 = self.create_rectangle(j1, iy, j1+s, (iy+s), outline=c1, tags=tags)
            it2 = self.create_rectangle(j2, iy, j2+s, (iy+s), outline=c2, tags=tags)
            return (it1, it2)
        else:
            it1 = self.create_rectangle(j1, iy, j1+s, (iy+s), outline=c1, tags=tags)
            it2 = self.create_rectangle(j2, iy, j2+s, (iy+s), outline=c2, tags=tags)
            if j1+s == j2:   #Only the vertical line is common
                it3 = self.create_line(j2, iy, j2, (iy+s), fill=self.blred, tags=tags)
                return (it1, it2, it3)
            else:            #2 horizontal lines are common
                it3 = self.create_line(j2, iy, j1+s, iy, fill=self.blred, tags=tags)
                it4 = self.create_line(j2, (iy+s), j1+s, (iy+s), fill=self.blred, tags=tags)
                return (it1, it2, it3, it4)


    def br3dZeroSurface(self):
        "Test red blue 3d possibilities making a zero height surface."
        dc = self
        maxx = dc.winfo_width() - 1
        maxy = dc.winfo_height() - 1
        minx = 0
        miny = 0
        jdx = idy = max((maxx/16, 10))     #Avoid zero and infinite loops
        thanMinx = int(dc.canvasx(minx))
        thanMiny = int(dc.canvasy(miny))
        thanMaxx = int(dc.canvasx(maxx))
        thanMaxy = int(dc.canvasy(maxy))
        print("br3dZeroSurface():", thanMinx, thanMiny, thanMaxx, thanMaxy, jdx, idy)

        br = self.blred
        tags = "enull", "enull0"
        dc.delete("enull0")
        for jx in range(thanMinx, thanMaxx, jdx):
            dc.create_line(jx, thanMiny, jx, thanMaxy, fill=br, tags=tags)
        for iy in range(thanMiny, thanMaxy, idy):
            dc.create_line(thanMinx, iy, thanMaxx, iy, fill=br, tags=tags)


class CrosHairRect3d(CrosHair):
    "Draws, moves, deletes and maintains a limited croshair in a canvas."

    def __init__(self, dc, size):
        "Take size as an argument."
        self.dx = self.dy = max(size//2, 1)
        self.incp = -1                       #Previous increase moved left subcursor
        self.paral = 0
        CrosHair.__init__(self, dc)


    def draw(self, x1, y1):
        "Draws a croshair and deletes previous croshair."
        if self.thanOn:
            dc = self.thanDc
            if self.thanExists:
                xa, ya = dc.coords(self.thanChx[0])[:2]
                xp1 = xa + self.dxa
                yp1 = ya + self.dya
                for it in self.thanChx:
                    dc.move(it, x1-xp1, y1-yp1)
                    dc.lift(it)
            else:
#                ip2 = int(self.paral/2)
#                jxb = x1-self.dx-ip2
#                jxr = x1-self.dx+self.paral-ip2
#                iy = y1-self.dy
#                self.thanChx[:] = dc.pointpair(jxb, jxr, iy, s=2*self.dx+1)
                self.thanChx[:] = dc.pointpair(x1, y1, self.dx*2, self.paral)
                xa, ya = dc.coords(self.thanChx[0])[:2]
                self.dxa, self.dya = x1-xa, y1-ya   #The position of the mouse relative to first cursor point
                self.thanExists = 1
        self.thanX1p = x1
        self.thanY1p = y1


    def thanUpwheel(self, evt):
        self.paral += 1
        self.resize()


    def thanDownwheel(self, evt):
        self.paral -= 1
        self.resize()


    def thanEnable(self, x1=None, y1=None):
        "Enable the croshair."
        self.thanDc.config(cursor="none") #disable tk cursor
        CrosHair.thanEnable(self, x1, y1)

    def thanDisable(self):
        "Disable the croshair."
        self.thanDc.config(cursor="")     #enable default tk cursor
        CrosHair.thanDisable(self)

    def resize(self, x1=None, y1=None):
        "Redraw the cursor."
        self.thanDc.config(cursor="none") #disable tk cursor
        CrosHair.resize(self, x1, y1)
