# -*- coding: iso-8859-7 -*-
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
The subpackage contains the commands which handle 3d viewing.
This module defines various constants.
"""

import copy
import p_ggen
from p_gmath import thanNearx
import thandr
from thantrans import T


def thanStereoToggle(proj):
    "Toggles red/blue stereo viewing on and off."
    __stereoToggle(proj)
    proj[1].thanDoundo.thanAdd("stereotoggle", __stereoToggle, (),     #redo
                                               __stereoToggle, ())     #undo
    proj[2].thanGudCommandEnd()

def __stereoToggle(proj):
    "Toggles red/blue stereo viewing on and off - does the job."
    proj[2].thanCanvas.thanStereoToggle()
    if proj[2].thanCanvas.thanStereoOn:
        proj[2].thanPrt(T["<Stereo on>"])
    else:
        proj[2].thanPrt(T["<Stereo off>"])


def thanStereoGridToggle(proj):
    "Toggles a reference elevation grid on and off."
    __stereoGridToggle(proj)
    proj[1].thanDoundo.thanAdd("stereogridtoggle", __stereoGridToggle, (),   #redo
                                                   __stereoGridToggle, ())   #undo
    proj[2].thanGudCommandEnd()

def __stereoGridToggle(proj):
    "Toggles a reference elevation grid on and off - does the job."
    proj[2].thanCanvas.thanStereoGridToggle()
    if proj[2].thanCanvas.thanStereoGridOn:
        proj[2].thanPrt(T["<Stereo grid on>"])
    else:
        proj[2].thanPrt(T["<Stereo grid off>"])


def thanStereoAverage(proj):
    """Zooms the 3d stereo coordinates so that they can be easily seen.

    The current elevation is the average elevation of all elements.
    The elevation step is set to a value so that all elements are  between
    +-5 clicks of current elevation."""
    ThanPoint = thandr.ThanPoint
    proj[2].thanGudSetSelExternalFilter(lambda e: isinstance(e, ThanPoint))
    elems = proj[2].thanGudGetDisplayed()    #Get cuurenty displayed elements
    proj[2].thanGudSetSelExternalFilter(None)
    if not elems: return proj[2].thanGudCommandCan(T["No points found."])
    oldvars = p_ggen.rdict(proj[1].thanVar, "elevation", "elevationstep")   #Shallowcopy only these variables
    oldvars = copy.deepcopy(oldvars)
    newvars = copy.deepcopy(oldvars)

    zmin = min(e.cc[2] for e in elems)
    zmax = max(e.cc[2] for e in elems)
    zave = sum(e.cc[2] for e in elems)/len(elems)
    dz = (zmax-zmin)/10
    if thanNearx(dz, 0.0): dz = 1.0
    newvars["elevation"][2] = zave
    newvars["elevationstep"][2] = dz

    thanStereoViewRedoundo(proj, newvars)
    proj[1].thanVar.update(newvars)   # Set new default only if user did not cancel
    proj[1].thanDoundo.thanAdd("stereoaverage", thanStereoViewRedoundo, (newvars,),    #redo
                                                thanStereoViewRedoundo, (oldvars,))    #undo
    proj[2].thanGudCommandEnd()


def thanStereoViewRedoundo(proj, oldvars):
    "Unloads and loads images and sets selectiom."
    proj[1].thanVar.update(oldvars)
    proj[2].thanCanvas.thanRestereo()
