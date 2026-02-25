# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.2.4 "Valencia": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2014 Thanasis Stamos, November 15, 2014
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.2.4 "Valencia": n-dimensional CAD with raster support for engineers

Curve Matching Algorithms, Dimitra Vassilaki, PhD Candidate
Lab of Photogrammetry, NTUA, 2011-2013
This module contains a mixin for the various 3d-2d and 2d-2d transformations
available to ThanCad.
"""

import Tkinter
import p_gtkwid
from thantrans import Tmatch


class TransfMixin:
    projectcode = \
        (("Central Projection (collinearity)",             31),
         ("Direct Linear Transform",                       1),
         ("Rational Polynomial Projection of first order", 2),
         ("Polynomial Projection of first order",          0),
         ("Polynomial Projection of second order",         3),
         ("Rational Polynomial Projection of second order",4),
         ("Rational Polynomial Projection of 2/1 order",   5),
         ("Direct Linear Transform",                      11),
         ("Rational Polynomial Projection of first order",12),
         ("Polynomial Projection of first order",         10),
         ("Polynomial Projection of second order",        13),
        )

    def thanProjectFromlib(self, icodp):
        "Find the projection code for the radProject widget given the library projection code."
        for ia,(_,icodpa) in enumerate(self.projectcode):
            if icodp == icodpa: return ia
        return -1

    def thanProjectTolib(self, v=None):
        "Get the projection code from the radProject widget or the values v and transform it to library projection code."
        if v == None: i = self.radProject.thanGet()
        else:         i = v.radProject
        return self.projectcode[i][1]

    def bodyProject(self, win, ir, wids):
        "Select projection type."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tmatch["PROJECTION TYPE:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        key = "radProject"
        tit = "Projection type"           #Tmatch["Projection type"]
        rad = p_gtkwid.ThanRadio(fra)
        rad.grid(row=1, column=1, sticky="wesn")

        lab = Tkinter.Label(rad, text=Tmatch["3D-2D"], fg=self.colfra)
        lab.grid(row=0, column=0, sticky="w")
        pc = self.projectcode
        for i in xrange(3):
            wid = rad.add_button(text=Tmatch[pc[0+i][0]])
            wid.grid(row=i+1, column=0, sticky="w")
        for i in xrange(4):
            wid = rad.add_button(text=Tmatch[pc[3+i][0]])
            wid.grid(row=i+1, column=2, sticky="w")

        lab = Tkinter.Label(rad, text=Tmatch["2D-2D"], fg=self.colfra)
        lab.grid(row=5, column=0, sticky="w")
        for i in xrange(4, 6):
            wid = rad.add_button(text=Tmatch[pc[3+i][0]])
            wid.grid(row=i+2, column=0, sticky="w")
        for i in xrange(4, 6):
            wid = rad.add_button(text=Tmatch[pc[5+i][0]])
            wid.grid(row=i+2, column=2, sticky="w")
        wid = Tkinter.Frame(rad)
        wid.grid(row=0, column=1, sticky="we", padx=30)

        val = p_gtkwid.ThanValidator()
        wids.append((key, Tmatch[tit], rad, val))

        fra.columnconfigure(1, weight=1)
        fra.columnconfigure(2, weight=1)
        return fra
