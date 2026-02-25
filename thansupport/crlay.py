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

This module defines utility functions to create/edit layers from within
an embedded program.
"""
from thanvar import THANBYPARENT, THANPERSONAL, ThanLayerError
from thanlayer import THANNAME
from thanlayer.thanlayatts import thanLayAtts, thanUpdateElements


def thanLayerCurrent(proj, pname, current=True, **atts):
    "Create a layer pathname relative to current layer."
    lt = proj[1].thanLayerTree
    pname = "%s/%s" % (lt.thanCur.thanGetPathname(), pname)
    return thanToplayerCurrent(proj, pname, current, **atts)


def thanToplayerCurrent(proj, pname, current=True, **atts):
    """Create a toplevel or child layer, set its colour, and set it as current.

    If the toplevel layer exists:
    a. It is not created.
    b. Its colour is set to col, or if col==None, it is unaffected.
    c. If current==True, it is set as current layer.
    d. If current==False, but it happens that the layer is the current layer
       the attributes of the current layer are set again to the .than object.
    If the toplevel layer does not exist:
    a. It is created.
    b. Its colour is set to col, or if col==None, the colour is inherited.
    c. If current==True, it is set as current layer.
    This routine may raise ThanLayerError if the layer can not be created,
    or if any attributes is not recognised.
    This routine may raise ValueError if the value of the attribute is illegal.
    This routine is safe: if something is invalid, it will perform no changes
    at all, and it will raise the appropriate exception.

    """
    lt = proj[1].thanLayerTree
    pname = pname.strip()
    lay = lt.thanRoot
    newlayer = False
    for name in pname.split("/"):
        parent = lay
        name0 = name.strip().lower()
        for lay in parent.thanChildren:
            if str(lay.thanAtts[THANNAME]).lower() == name0: break
        else:
            try:     lay = parent.thanChildNew(name) # This may raise ThanLayerError
            finally: lt.thanDictRebuild()
            newlayer = True
    if newlayer:                                 # Layer did not exist
        for att, rawval in atts.items():  #works for python2,3
            if att not in thanLayAtts: raise ThanLayerError("Attribute %s is not recognised" % att)
            if rawval == THANPERSONAL: raise ValueError("New layer does not have PERSONAL attributes yet")
            class_ = thanLayAtts[att][3]        # Get class of attribute 'moncolor'
            if rawval == THANBYPARENT:
                val = class_(parent.thanAtts[att].thanVal, inherit=True)
            else:
                val = class_(rawval, inherit=False) # This will raise ValueError if rawval is invalid
            lay.thanAtts[att] = val             # No propagation is necessary
        if current:
            lt.thanCur = lay
            lay.thanTkSet(proj[2].than)
            proj[2].thanUpdateLayerButton()
        proj[1].thanTouch()                     # Drawing IS modified
    else:
        if current and len(lay.thanChildren) > 0: raise ThanLayerError("Only a leaflayer may be current layer")
        __atts(proj, parent, lay, atts, check=True) # At first checks the attributes and raise exceptions if invalid
        __atts(proj, parent, lay, atts, check=False)

        if current or lay == lt.thanCur:
            lt.thanCur = lay
            lay.thanTkSet(proj[2].than)
            proj[2].thanUpdateLayerButton()
            proj[1].thanTouch()                 # Drawing IS modified
    return lay


def __atts(proj, parent, lay, atts, check):
        "Check or set the attributes."
        if len(atts) == 0: return
        leaflayers = {}
        for att, rawval in atts.items():  #works for python2,3
            if att not in thanLayAtts: raise ThanLayerError("Attribute %s is not recognised" % att)
            class_ = thanLayAtts[att][3]        # Get class of attribute 'moncolor'
            if rawval == THANBYPARENT:
#                val = class_(parent.thanAtts[att].thanVal, inherit=True)
                val = rawval
            elif rawval == THANPERSONAL:
#                val = class_(lay.thanAtts[att].thanVal.personal, inherit=False)
                val = rawval
            else:
                val = class_(thanLayAtts[att][2], inherit=False)
                val.thanValSet(rawval)          # This will raise ValueError if rawval is invalid
            if not check:
                lay.thanSetAtts(leaflayers, att, val)

        if check: return
        draworder = thanUpdateElements(proj, leaflayers)
        if draworder: proj[2].thanRedraw()      # Set relative draworder
        proj[1].thanTouch()                     # Drawing IS modified
