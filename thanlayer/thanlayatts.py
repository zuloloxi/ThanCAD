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

This module defines the valid attributes of a layer, their type, and their
default value.
It also defines the actions to do to elements, when an attribute is forced
on them.
"""

import collections
import p_gtkwid, p_ggen
from thanvar import Canc, THANBYPARENT, THANPERSONAL
from thandefs.thanatt import (ThanAttNI, ThanAttTextbNI, ThanAttCol, ThanAttLtype,
    ThanAttScale, ThanAttOnoffInherit, ThanAttTextb, ThanAttOnoff, ThanAttInt,
    ThanAttThick,ThanAttFloat)
from thanopt import thancadconf
from thantrans import T
from thandr import ThanPointNamed
import thantkdia
from .thanlaycon import THANNAME

############################################################################
############################################################################

def thanPlotcolorGet (*args): pass
def thanPointstyleGet(*args): pass
def thanHatchGet     (*args): pass

def thanLockedGet    (*args): pass
def thanNoplotGet    (*args): pass

def thanProtectedGet (*args): pass



def thanOnclick(evt, win, attname, indexes, selLayers):
    "Calls the appropriate function for the attribute and layers chosen by the user."
    fun = thanLayAtts[attname][1]
    if fun is None: return                     # No function; do nothing
    newval,keepsel = fun(win, attname, selLayers)
    if newval == Canc:                         # User cancelled
        if len(indexes) < 2: win.thanSelNone() # Keep the selection (unless only 1 layer)
        return
    typ = thanLayAtts[attname][0]
    if typ != 0: assert newval != THANBYPARENT, attname+": Forced inheritance attributes can not be inherited manually."
    for lay in selLayers:
        lay.thanSetAtts(win.thanLeaflayers, attname, newval)
    win.thanRegen()
    if keepsel and len(indexes) > 1: win.thanSelVar(indexes)  # Keep the selection
    else:                            win.thanSelNone()        # Clear the selection


def thanMoncolorGet(win, att, selLayers):
    "Lets the user select monitor colour."
    c =__commonVal(att, selLayers)
    w = thantkdia.ThanColor(win, c, special=True, title=T["Select ThanCad Colour"])
    r = w.result
    if r is None: r = Canc
    return r, True


def __commonVal(att, selLayers):
    "Selects the common value of att in the layers selLayers, if possible."
    c = selLayers[0].thanAtts[att]
    for lay in selLayers:
        cl = lay.thanAtts[att]
        if cl.thanVal != c.thanVal or cl.thanInher != c.thanInher: return "<varies>"
    if c.thanInher: return THANBYPARENT
    return c


def thanFrozenGet(win, att, selLayers):
    "Lets the user select new frozen value: yes/no/BYPARENT."
    n = 0
    for lay in selLayers:
        if lay.thanAtts[att].thanVal: n += 1
    class_ = thanLayAtts[att][3]
    val = class_(n < len(selLayers))    # Less than half layers are frozen; freeze all
    return val, True


def thanFillGet(win, att, selLayers):
    "Lets the user select new 'fill' value for the selected layers."
    ia = selLayers[0].thanAtts[att]     # A sample attribute value
    tlabs = [str(THANBYPARENT), str(THANPERSONAL), ia.thanOn, ia.thanOff]
    w = p_gtkwid.ThanPoplist(win, tlabs, width=15, title=T["Select ThanCad Fill mode"])
    if w.result is None: return Canc, True
    if w.result == str(THANBYPARENT): return THANBYPARENT, True
    if w.result == str(THANPERSONAL): return THANPERSONAL, True
    class_ = thanLayAtts[att][3]
    r = class_(w.result)
    return r, True


def thanTstyleGet(win, att, selLayers):
    "Lets the user select new textstyle for the selected layers."
    c =__commonVal(att, selLayers)
    proj = win.thanCargo
    tlabs = sorted(proj[1].thanTstyles.keys())    #works for python2,3
    tlabs.insert(0, str(THANBYPARENT))
    tlabs.insert(1, str(THANPERSONAL))
    w = p_gtkwid.ThanPoplist(win, tlabs, width=40, title=T["Select ThanCad Text Style"])
    if w.result is None: return Canc, True
    if w.result == str(THANBYPARENT): return THANBYPARENT, True
    if w.result == str(THANPERSONAL): return THANPERSONAL, True
    class_ = thanLayAtts[att][3]
    r = class_(w.result)
    return r, True


def thanDimstyleGet(win, att, selLayers):
    "Lets the user select new dimstyle for the selected layers."
    return __dstyleltypeGet(win, att, selLayers, idialog=1)

def thanLinetypeGet(win, att, selLayers):
    "Lets the user select new linetype for the selected layers."
    return __dstyleltypeGet(win, att, selLayers, idialog=0)

def __dstyleltypeGet(win, att, selLayers, idialog):
    "Lets the user select new linetype or dimstyle for the selected layers."
    name = collections.Counter()
    unit = collections.Counter()
    scale = collections.Counter()
    inher = collections.Counter()
    for lay in selLayers:
        ia = lay.thanAtts[att]
        print("attltype.thanval", ia)
        lt = ia.thanVal
        print("attltype.thanval", lt)
        print(lt[0])
        print(lt[1])
        print(lt[2])
        name[lt[0]] += 1
        unit[lt[1]] += 1
        scale[lt[2]] += 1
        inher[ia.thanInher] += 1
    s = p_ggen.Struct("Line type settings")
    s.butPattern = name.most_common(1)[0][0]
    s.choUnit  = 0 if unit.most_common(1)[0][0]=="mm" else 1
    s.entScale = scale.most_common(1)[0][0]
    print("s.butPattern = ", s.butPattern)
    print("s.choUnit    = ", s.choUnit)
    print("s.entScale   = ", s.entScale)
    i = inher.most_common(1)[0][0]
    if i: s.butPattern = str(THANBYPARENT)
    win = thantkdia.ThanDialogLtype(master=win, vals=s, cargo=win.thanCargo, translation=None, idialog=idialog)
    s = win.result
    if s is None: return Canc, True
    if s.butPattern == str(THANBYPARENT): return THANBYPARENT, True
    if s.butPattern == str(THANPERSONAL): return THANPERSONAL, True
    class_ = thanLayAtts[att][3]
    r = class_((s.butPattern, ("mm", "u")[s.choUnit], s.entScale))
    return r, True


def thanDraworderGet (win, att, selLayers):
    "Lets the user select new draworder for the selected layers."
    c =__commonVal(att, selLayers)
    w = thantkdia.ThanDro(win, c, title="Select Draw Order")
    r = w.result
    if r is None: return Canc, True
    if r in (THANBYPARENT, THANPERSONAL): return r, True
    class_ = thanLayAtts[att][3]
    r = class_(r)
    return r, True


def thanPenthickGet (win, att, selLayers):
    "Lets the user select new pen  thickness (mm of linear objects) for the selected layers."
    c =__commonVal(att, selLayers)
    w = thantkdia.ThanPen(win, c, "Pen", "mm", title="Select Pen Thickness")
    r = w.result
    if r is None: return Canc, True
    if r in (THANBYPARENT, THANPERSONAL): return r, True
    class_ = thanLayAtts[att][3]
    r = class_(r)
    return r, True


def thanLinethickGet (win, att, selLayers):
    "Lets the user select new thickness (user unints of linear objects) for the selected layers."
    c =__commonVal(att, selLayers)
    w = thantkdia.ThanPen(win, c, "Line", "user units", title="Select Line Thickness")
    r = w.result
    if r is None: return Canc, True
    if r in (THANBYPARENT, THANPERSONAL): return r, True
    class_ = thanLayAtts[att][3]
    r = class_(r)
    return r, True


def thanUpdateElementsold(proj, leaflayers, updatelayers=True):
    """Updates attribute a of the elements of the layers which are already on screen.

    IT IS ASSUMED THAT AFTER THIS ROUTINE IS CALLED, THE CALLER ALSO SETS THE
    STRUCTURE proj[2].than TO REFLECT THE CURRENT'S LAYER ATTRIBUTES i.e.
    TO CALL proj[2].thanLayerTree.thanCur.thanTkSet(proj[2].than, proj[1].thanTstyles)
    """
#    for lay,atts in leaflayers.items(): print(lay.thanGetPathname(), "->", atts   #works for python2,3)
    draworder = False
    dc = proj[2].thanCanvas
    than = proj[2].than
    for lay,atts in leaflayers.items():   #works for python2,3
        colourhasbeenset = False
        if "frozen" in atts:
            nval = atts["frozen"]
            ia = lay.thanAtts["frozen"]
            if ia.thanAct != nval:  # An attribute may be the same, if the user deleted the value, and then gave the same value
                if nval:
                    proj[2].thanGudSetFreezeLayer(lay)       # All items are deleted from canvas; there are no items to update!!!
                else:
                    proj[1].thanTkDraw(proj[2].than, (lay,)) # All items are redrawn; all items are up to date
                    draworder = True                         # All items are redrawn; thus, probably, the draworder is violated

                for a,nval in atts.items(): # Either way, the actual value is the same with new value  #works for python2,3
                    ia = lay.thanAtts[a]
                    if updatelayers: ia.thanAct = nval
                continue

        thawed = not lay.thanAtts["frozen"].thanVal
        for a,nval in atts.items():   #works for python2,3
            ia = lay.thanAtts[a]
            if thawed and ia.thanAct != nval:
                if a == "moncolor":
                    if not colourhasbeenset:
                        lay.thanTkSet(than)  # Note that .thanval is already set with the new value
#                        than.outline = lay.ThanAttCol(nval).thanTk
                        proj[2].thanGudGetSelLayerx(lay.thanTag)
                        proj[2].thanGudSetSelColorx(than.outline, than.fill)
                        colourhasbeenset = True
                elif a == "fill":
                    if not colourhasbeenset:
                        lay.thanTkSet(than)
                        proj[2].thanGudGetSelLayerx(lay.thanTag)
                        proj[2].thanGudSetSelColorx(than.outline, than.fill)
                        colourhasbeenset = True

#                    for elem in lay.thanQuad:
#                        if isinstance(elem, ThanCircle):
#                            dc.delete(elem.thanTags[0])
#                            elem.thanTkDraw(than)
#                        elif isinstance(elem, ThanLine):
#                            if thanNear2(elem.cp[0], elem.cp[-1]):
#                                dc.delete(elem.thanTags[0])
#                                elem.thanTkDraw(than)
                elif a == "draworder":
                    draworder = True
                elif a == "penthick":
                    pass              # Nothing visible changes
                elif a == "linethick":
                    pass              # FIXME: redraw linear elements with new thickness
                elif a == "hidename" or a == "hidepoint":
                    lay.thanTkSet(than)
                    xymm = proj[1].thanAreaIterated
                    for elem in lay.thanQuad:
                        if not isinstance(elem, ThanPointNamed): continue
                        if not elem.thanInarea(xymm): continue   # Display elements only within current area (as all the other elements)
                        dc.delete(elem.thanTags[0])
                        elem.thanTkDraw(than)

            if updatelayers: ia.thanAct = nval
    return draworder


def thanUpdateElements(proj, leaflayers, updatelayers=True):
    """Updates attributes of the elements of the layers which are already on screen.

    It is assumed that leaflayers has been cleaned up by a previous call to thanChangedAtts.
    IT IS ASSUMED THAT AFTER THIS ROUTINE IS CALLED, THE CALLER ALSO SETS THE
    STRUCTURE proj[2].than TO REFLECT THE CURRENT'S LAYER ATTRIBUTES i.e.
    TO CALL proj[2].thanLayerTree.thanCur.thanTkSet(proj[2].than, proj[1].thanTstyles)
    """
#    for lay,atts in leaflayers.items(): print(lay.thanGetPathname(), "->", atts   #works for python2,3)
    draworder = False
    dc = proj[2].thanCanvas
    than = proj[2].than
    for lay,atts in leaflayers.items():    #works for python2,3
        if "frozen" in atts:
            nval = atts["frozen"]
            if nval:
                proj[2].thanGudSetFreezeLayer(lay)       # All items are deleted from canvas; there are no items to update!!!
                proj[2].thanImages -= lay.thanQuad
            else:
                proj[1].thanTkDraw(proj[2].than, (lay,)) # All items are redrawn; all items are up to date
                draworder = True                         # All items are redrawn; thus, probably, the draworder is violated

            for a,nval in atts.items(): # Either way, the actual value is the same with new value   #works for python2,3
                ia = lay.thanAtts[a]
                if updatelayers: ia.thanAct = nval
            continue

        for a,nval in atts.items():   #works for python2,3
            ia = lay.thanAtts[a]
            if a == "moncolor" or a == "fill":
                lay.thanTkSet(than)  # Note that .thanval is already set with the new value
#                than.outline = lay.ThanAttCol(nval).thanTk
                proj[2].thanGudGetSelLayerx(lay.thanTag)
                proj[2].thanGudSetSelColorx(than.outline, than.fill)
            elif a == "draworder":
                draworder = True
            elif a == "penthick":
                pass              # Nothing visible changes
            elif a == "linethick":
                pass              # FIXME: redraw linear elements with new thickness
            elif a == "hidename" or a == "hidepoint":
                lay.thanTkSet(than)
                xymm = proj[1].thanAreaIterated
                for elem in lay.thanQuad:
                    if not isinstance(elem, ThanPointNamed): continue
                    if not elem.thanInarea(xymm): continue   # Display elements only within current area (as all the other elements)
                    dc.delete(elem.thanTags[0])
                    elem.thanTkDraw(than)
            elif a == "linetype":
                lay.thanTkSet(than)  # Note that .thanval is already set with the new value
                proj[2].thanGudGetSelLayerx(lay.thanTag)
                proj[2].thanGudSetSelDashx(dash=than.dash)

            if updatelayers: ia.thanAct = nval
    return draworder

def thanChangedAtts(proj, leaflayers):
    "Finds which attributes of lealayers should be updated."
    cleaf = {}
    for lay,atts in leaflayers.items():   #works for python2,3
        catts = {}
        colourhasbeenset = False
        pnamedhasbeenset = False
        if "frozen" in atts:
            nval = atts["frozen"]
            ia = lay.thanAtts["frozen"]
            if ia.thanAct != nval:  # An attribute may be the same, if the user deleted the value, and then gave the same value
                catts["frozen"] = nval
                cleaf[lay] = catts
                continue

        thawed = not lay.thanAtts["frozen"].thanVal
        for a,nval in atts.items():   #works for python2,3
            ia = lay.thanAtts[a]
            if thawed and ia.thanAct != nval:
                if a == "moncolor" or a == "fill":
                    if not colourhasbeenset:
                        catts[a] = nval
                        colourhasbeenset = True
                elif a == "hidename" or a == "hidepoint":
                    if not pnamedhasbeenset:
                        catts[a] = nval
                        pnamedhasbeenset = True
                else:
                    catts[a] = nval
        cleaf[lay] = catts
    return cleaf


#############################################################################
#############################################################################

#MODULE LEVEL CODE. IT IS EXECUTED ONLY ONCE

thanLayAttsOrder = \
(   ("expand",     (0, None,             "+",    ThanAttNI,
#(   ("expand",     (0, None,             None,   ThanAtt,
                  "'+' if layer's children should be shown.")),
    ("layer",      (0, None,             None,   ThanAttTextbNI, "Layer name.")),
    ("plotcolor",  (0, thanPlotcolorGet, ThanAttCol(thancadconf.thanColRoot), ThanAttCol,        # red
                  "Element color on printer/plotter.")),
    ("moncolor",   (0, thanMoncolorGet,  ThanAttCol(thancadconf.thanColRoot), ThanAttCol,        # red
                  "Element color on screen.")),
    ("linetype",   (0, thanLinetypeGet, ("continuous", "mm", 1.0), ThanAttLtype, "Linetype of linear elements.")),
    ("dimstyle",   (0, thanDimstyleGet, ("standard", "mm", 1.0),   ThanAttLtype, "Dimension style.")),
    ("ltscale",    (0, thanLinetypeGet,  1.0,    ThanAttScale, "Linetype scale. It may be negative "+\
                  "as a percentage to the screen.")),
    ("fill",       (0, thanFillGet,      False,  ThanAttOnoffInherit,
                  "If 1, circles and closed elements are filled with colour/hatch.")),
    ("linethick",  (0, thanLinethickGet, 0.0,    ThanAttFloat,
                  "Line thickness (user units) of linear elements (in Tkinter only lines), "+\
                  "including ThanCadLinearFonts. It may be negative "+\
                  "as a percentage of the screen")),
    ("penthick",   (0, thanPenthickGet, 0.25,    ThanAttThick,
                  "Pen thickness (mm) which the elements are plotted with. Independent to scale.")),
    ("pointstyle", (0, thanPointstyleGet, "dot", ThanAttTextb, "Point style.")),
    ("pointsize",  (0, thanPointstyleGet, -5.0,  ThanAttScale, "Point size. It may be negative "+\
                  "as a percentage of the screen.")),
    ("hidename",   (1, thanFrozenGet, True, ThanAttOnoff, "Hide point name.")),
    ("hideheight", (1, thanFrozenGet, True, ThanAttOnoff, "Hide point height.")),
    ("hatch",      (0, thanHatchGet,     "solid",ThanAttTextb,
                  "Hatch style of hatchable elements.")),
    ("hatchscale", (0, thanHatchGet,  1.0,       ThanAttScale, "Hatch scale. It may be negative "+\
                  "as a percentage to the screen.")),
    ("textstyle",  (0, thanTstyleGet, "standard",ThanAttTextb, "Text style and font of textual elements.")),
    ("textscale",  (0, thanTstyleGet, 1.0,       ThanAttScale, "Text scale. It may be negative "+\
                  "as a percentage to the screen.")),

    ("draworder",  (0, thanDraworderGet, 1000,   ThanAttInt,
                  "Plotting Order. A layer with small draworder is drawn "\
                  "before (and therefore under) a layer with big draworder.")),

    ("frozen",     (1, thanFrozenGet,    False,  ThanAttOnoff,
                  "If 1, elements are not shown, like if they never existed.")),
    ("locked",     (1, thanLockedGet,    False,  ThanAttOnoff,
                  "If 1, elements are shown readonly; they can not be edited.")),
    ("noplot",     (1, thanNoplotGet,    False,  ThanAttOnoff,
                  "If 1, elements are shown but they are not be plotted.")),

    ("protected",  (2, thanProtectedGet, False,  ThanAttOnoff,
                  "Elements are controlled by a program; they are read only."+
                  "This attribute can not be altered by the user."))
)

thanLayAttsType = \
{   0: """Type zero is normal layer inheritance. When this attribute of
          a layer changes, then all their children which have this
          attribute set as BYPARENT change too.
       """,
    1: """Type 1 is global layer inheritance and it is zero (false)
          or nonzero (generalised true). When this attribute
          becomes a<>0 (true), then all its
          children behave as this attribute were also set to a.
          However, when this attribute becomes 0 (false) again, the
          children retain their original attribute value.
       """,
    2: """Type 2 attributes work like type 1, but the user can not modify them.
          These attributes may be modified only by programs embedded in ThanCad.
       """
}

info=\
"""Point size, dashed linetypes, hatch, text size, linethick may be relative to,
actually a percentage of, the screen (as points in autocad).
Another idea is to have them defined relative to the screen, but in cm or inches
assuming that screen has a diagonal of 15, 17, 19 and so on, inches.
"""


thanLayAtts = {}
thanLayAttsNames = []

for (key, val) in thanLayAttsOrder:
    thanLayAtts[key] = val
    thanLayAttsNames.append(key)
thanLayAttsNames = ["expand", THANNAME, "moncolor", "frozen", "textstyle", "linetype",
    "dimstyle", "draworder", "fill", "penthick", "linethick", "hidename", "hideheight"]
thanLayAttsWidths = [1,        30,       20,         3,        20,          40,
    30,         6,           5,      6,          6,           3,          3]


if __name__ == "__main__":
    print(__doc__)

    form = "%-15s%-6s%-15s  %s"
    print(form % ("attribute", "type", "default value", "Doc"))
    print("------------------------------------------------")
    for (name, att) in thanLayAtts.items():   #works for python2,3
        print(form % (name, att[0], att[2], att[3]))

    print()
    for (name, att) in thanLayAttsType.items():   #works for python2,3
        print(name, att)

