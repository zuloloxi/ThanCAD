# -*- coding: iso-8859-7 -*-

##############################################################################
# ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2013 Thanasis Stamos, March 25, 2013
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
ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers

Package which processes commands entered by the user.
This module processes various commands.
"""

import sys
from math import pi, atan2
import tkFont
import p_ggen, p_gtkuti, p_ggeom
from p_gmath import dpt, thanNear2
import thandr, thancomsel, thantkdia, thanlayer
from thanvers import tcver
from thanvar import Canc
from thantrans import T, thanLangSet
import thanundo
from thancomfile import thanTxtopen
from thancommod import thanModCanc, thanModCancSel, thanModEnd
from thanopt import thancadconf


def thanVarLang(proj):
    "Change the physical language of ThanCad's interface."
    res = proj[2].thanGudGetOpts("Enter language (en=english/gr=greek) <en>:",
        default="en", fullopt=True, options=("en", "gr"))
    if res == Canc: return proj[2].thanGudCommandCan()
    print "new lang=", res
    thanLangSet(res)
    proj[2].thanGudCommandEnd("Please restart ThanCad to complete the translation.", "info")


def thanVarElev(proj):
    "Displays and sets the elevation of z dimension."
    nd = proj[1].thanVar["dimensionality"]
    assert nd > 2, "Well, this should be ThanCad with limited n-dimensional support!"
    if nd > 3:
        proj[2].thanPrt(T["This drawing has %d dimensions. The elevation and thickness"] % nd)
        proj[2].thanPrt(T["of dimensions higher than 3 are set with the ELEVN command."])
    c = proj[1].thanVar["elevation"]          # Reference to the elevation list
    sd = proj[1].thanUnits.strdis
    t = sd(c[2])
    proj[2].thanPrt("%s %s" % (T["Current elevation:"], t), "")
    stat = "%s%s): " % (T["New elevation (enter="], t)
    z = proj[2].thanGudGetFloat(stat, c[2])
    if z == Canc: return proj[2].thanGudCommandCan()
    c[2] = z                                  # Update elevation list
    proj[1].thanTouch()                       # Drawing has been modified
    proj[2].thanGudCommandEnd()


def thanVarElevn(proj):
    "Displays and sets the elevation of z and higher dimensions."
    nd = proj[1].thanVar["dimensionality"]
    assert nd > 2, "Well, this should be ThanCad with limited n-dimensional support!"
    if nd < 4:
        proj[2].thanPrt(T["This drawing has only %d dimensions. The elevation and thickness"] % nd)
        proj[2].thanPrt(T["of dimension z can also be set with the ELEV command."])
    c = proj[1].thanVar["elevation"]          # Reference to the elevation list
    sd = proj[1].thanUnits.strdis
    t = ",".join(sd(c[j]) for j in xrange(2, nd))
    proj[2].thanPrt("%s %s" % (T["Current elevations of z and higher dimensions:"], t), "")
    stat = "%s%s): " % (T["Enter new elevations separated by coma (enter="], t)
    cz = proj[2].thanGetElevations(nd, stat, c[2:])
    if cz == Canc: return proj[2].thanGudCommandCan()
    c[2:] = cz                                # Update elevation list
    proj[1].thanTouch()                       # Drawing has been modified
    proj[2].thanGudCommandEnd()


def thanVarSudup(proj):
    "Funny!."
    proj[2].thanGudCommandEnd(T["Sudup, brother!"])


def thanVarFill(proj):
    "Explain what happened with the fill command."
    proj[2].thanPrt("ThanCad hint: The 'fill' attribute of layers is superior to the 'fill' command.")
    res = proj[2].thanGudGetOpts(T["Enter fill mode for all layers [ON/OFF] <ON>:"],
        default="ON", fullopt=True, options=("ON", "OFF"))
    if res == Canc: return proj[2].thanGudCommandCan()
    res = res == "on"
    from thanlayer.thanlayatts import thanUpdateElements
    leaflayers = {}
    proj[1].thanLayerTree.thanRoot.thanPropAttAll(leaflayers, "fill", res)
    thanUpdateElements(proj, leaflayers)
    proj[1].thanTouch()
    proj[2].thanGudCommandEnd()


def thanVarScript(proj):
    "Run a series of commands."
    _, fr = thanTxtopen(proj, T["Open script file (with ThanCad's commands)"], suf=".scr")
    if fr == Canc: return Canc      # thanGudCommandCan has been already called
    thanVarScriptDo(proj, fr)
    fr.close()


def thanVarScriptDo(proj, fr):
    "Run a series of commands from an opened file."
    win = proj[2]
    coms = win.thanScriptComs = __itercom(fr)
    cmd = win.thanCom
    dc = win.thanCanvas
    win.thanGudCommandEnd()                   # Finish the sript command and reprompt
    while True:
        while not cmd.thanWaitingInput:
            dc.update()
        try: com1 = coms.next()
        except StopIteration: break
        win.thanScheduler.thanSchedClear()    # The previous command is cleared; breaks some tk gui commands
        cmd.thanEnter(com1)
    win.thanScriptComs = ()


def __itercom(fr):
    "Iterator which excudes the comments."
    for dline in fr:
        dline = dline.strip()
        if dline[:1] == "#": continue
        yield dline


def thanFormLay(proj):
    "Shows interactive window with layer tree in order to manipulates layers."
    from thanlayer.thanlayatts import thanChangedAtts
    newcl, newroot = thanundo.thanLtClone(proj)
    print "newroot"
    pre(newroot)
    w = thantkdia.ThanDialogLay(proj[2],
        objs=[newroot], current=newcl,
        atts=thanlayer.thanlayatts.thanLayAttsNames, cargo=proj,
        widths=thanlayer.thanlayatts.thanLayAttsWidths,
        height=15, vscroll=1, hscroll=1,
        onclick=thanlayer.thanlayatts.thanOnclick,
        title=proj[2].thanTitle+": "+T["Layer Control"])
    if w.result != None:
        lt = proj[1].thanLayerTree
        oldroot = lt.thanRoot  #Please note that oldroot contains just a reference to the set of elements
        oldcl = lt.thanCur     #..and thus we waste no memory here
        newleaflayers, newcl = w.result
        newleaflayers = thanChangedAtts(proj, newleaflayers)
        thanundo.thanLtRestore(proj, newcl, newroot, newleaflayers)
        proj[1].thanDoundo.thanAdd("ddlmodes", thanundo.thanLtRestore, (newcl, newroot, newleaflayers),
                                               __formLayUndo, (oldcl, oldroot))
        proj[2].thanGudCommandEnd()
    else:
        proj[2].thanGudCommandCan()

def pre(lay):
    print "%s '%s' '%s'" % (lay.thanAtts[thanlayer.THANNAME].thanVal, lay.thanAtts["expand"].thanVal, lay.thanAtts["expand"].thanPers)
    for lay in lay.thanChildren: pre(lay)

def __formLayUndo(proj, oldcl, oldroot):
    "Undoes the changes layer hierarchy."
#The following commented code is broken, since a whole subhierarchy of layers
#may have been moved to another parent
#    oldleaflayers = {}
#    for lay,atts in newleaflayers.iteritems():
#        names = lay.thanGetPathname().split("/")
#        lay = oldroot.thanFind(names)
#        natts = dict((a, lay.thanAtts[a].thanAct) for a in atts)
#        oldleaflayers[lay] = natts
#   thanundo.thanLtRestore, (oldcl, oldroot, oldleaflayers))

    thanundo.thanLtRestore(proj, oldcl, oldroot, "regen") #This is the easiest and most costly way to undo
                                                    #Since we don't know what attributes were before

def thanModDxfUndo(proj, newelems, oldcl, oldroot, oldvars={}):
    "Undeletes the previously deleted elements, and deletes the previously created new elements."
    thanundo.thanReplaceUndo(proj, (), newelems, selold=None, oldvars=oldvars)
    thanundo.thanLtRestore(proj, oldcl, oldroot)
    proj[2].thanRegen()


def thanModDxfRedo(proj, newelems, newcl, newroot, newvars={}):
    "Redeletes the deleted elements, and recreates the new elements."
    thanundo.thanLtRestore(proj, newcl, newroot)
    thanundo.thanReplaceRedo(proj, (), newelems, selelems=None, newvars=newvars)
    proj[2].thanRegen()


def thanFormTstyle(proj):
    "Manipulates text styles."
    win = thantkdia.ThanTkStyle(proj[2], proj[1].thanTstyles, "standard", lambda x: False, title=T["Edit ThanCad Text styles"])
    if win.result == None: return proj[2].thanGudCommandCan()
    proj[1].thanTstyles.clear()
    proj[1].thanTstyles.update(win.result)
    proj[1].thanTouch()
    proj[2].thanGudCommandEnd(T["Changes will be visible after the next regeneration."], "can")


def thanUnits(proj):
    "Shows interactive window to choose units and units printing."
    vs = proj[1].thanUnits
    vold = p_ggen.Struct()
    vold.radDistunit = vs._dis2num[vs.distunit]    # Unit of distance measurements
    vold.entDistdigs = vs.distdigs                 # Number of digits to display for distance values
    vold.radAnglunit = vs._ang2num[vs.anglunit]    # Unit of angular measurements
    vold.entAngldigs = vs.angldigs                 # Number of digits to display for angular values
    vold.radAngldire = vs._dir2num[vs.angldire]    # Anti-clockswise angles are positive
    a = (3.0 - vs.anglzero*6.0/pi) % 12.0          # Tranform radians to 3, 12, 9 or 6 o'clock
    if int(a+0.1) == 0: a = 12.0
    vold.radAnglzero = vs._ori2num[int(a+0.1)]     # Zero is at 0.0 radians angle from the x-axis in the anticlockwise direction

    w = thantkdia.ThanDialogUnits(proj[2], vals=vold, cargo=proj,
        title="%s - %s: %s" % ("ThanCad", proj[0].namebase, T["Unit management"]))
    vnew = w.result
    if vnew == None: return proj[2].thanGudCommandCan()

    __unitsrestore(proj, vnew)                     #thanTouch is implicitely called
    proj[1].thanDoundo.thanAdd("units", __unitsrestore, (vnew,),
                                        __unitsrestore, (vold,))
    proj[2].thanGudCommandEnd()


def __unitsrestore(proj, v):
    "Does or undoes new units definition."
    vs = proj[1].thanUnits
    vs.thanConfig(
        distunit = vs._dis2text[v.radDistunit],   # Unit of distance measurements
        distdigs = v.entDistdigs,                 # Number of digits to display for distance values
        anglunit = vs._ang2text[v.radAnglunit],   # Unit of angular measurements
        angldigs = v.entAngldigs,                 # Number of digits to display for angular values
        angldire = vs._dir2text[v.radAngldire],   # Anti-clockswise angles are positive
        anglzero = vs._ori2text[v.radAnglzero])   # Zero is at 0.0 radians angle from the x-axis in the anticlockwise direction
    proj[1].thanTouch()


def thanList(proj):
    "Lists the properties of elements."
    res = thancomsel.thanSelectOr(proj, standalone=False, optionname="objects", optiontext="o=objects")
    if res == Canc: return thanModCanc(proj)
    than = p_ggen.Struct()
    than.write = proj[2].thanCom.thanAppend
    than.read = proj[2].thanGudGetText
    than.writecom = lambda t, proj=proj: proj[2].thanCom.thanAppend(t, "com")
    than.strang = proj[1].thanUnits.strang
    than.strdir = proj[1].thanUnits.strdir
    than.strdis = proj[1].thanUnits.strdis
    than.strcoo = proj[1].thanUnits.strcoo
    than.elevation = proj[1].thanVar["elevation"]
    dilay = proj[1].thanLayerTree.dilay

    if res == "o":                      #List objects
        thanModCancSel(proj)            #The user did not select anything so cancel current (empty) selection
        for name, objs in proj[1].thanObjects.iteritems():
            for obj in objs:
                obj.thanList(than)
    else:                               #List elements
        for elem in proj[2].thanSelall:
            lay = dilay[elem.thanTags[1]]
            than.laypath = lay.thanGetPathname()
            elem.thanList(than)
        del than, dilay
    thanModEnd(proj)


def thanHelpAbout(proj):
    "Shows brief information about the program."
    font1 = tkFont.Font(family=thancadconf.thanFontfamily, size=thancadconf.thanFontsize)
    p_gtkuti.thanGudHelpWin(proj[2], tcver.about, "%s %s" % (T["About"], tcver.name),
                            font=font1)   # (Gu)i (d)ependent
    proj[2].thanGudCommandEnd()


def thanHelpHelp(proj):
    font1 = tkFont.Font(family=thancadconf.thanFontfamily, size=thancadconf.thanFontsize)
    p_gtkuti.thanGudHelpWin(proj[2], tcver.help, tcver.name+" "+T["Help"],   # (Gu)i (d)ependent
                            font=font1)   # (Gu)i (d)ependent
    proj[2].thanGudCommandEnd()

def thanHelpGpl (proj):
    font1 = tkFont.Font(family=thancadconf.thanFontfamily, size=thancadconf.thanFontsize)
    p_gtkuti.thanGudHelpWin(proj[2], tcver.license[2], tcver.name+" "+T["GPL"],   # (Gu)i (d)ependent
                            font=font1)   # (Gu)i (d)ependent
    proj[2].thanGudCommandEnd()

def thanHelpVer(proj):
    "Prints ThanCad's version."
    proj[2].thanCom.thanCadVer()
    proj[2].thanGudCommandEnd()


def thanDevFont(proj):
    "Show font for debugging reasons."
    c = list(proj[1].thanVar["elevation"])
    c[0] = 0; c[1] = 30; h = 50
    __AddElem(proj, thandr.ThanText, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", c, h, 0.0)
    c[1] -= h*1.2
    __AddElem(proj, thandr.ThanText, "abcdefghijklmnopqrstuvwxyz", c, h, 0.0)

    for i in xrange(0, 256, 8):
        c[1] -= h*3
        c[0] = 0
        for j in xrange(i, i+8):
            t = "%3d:%s" % (j, chr(j))
            __AddElem(proj, thandr.ThanText, t, c, h, 0.0)
            c[0] += h*8
    proj[2].thanGudCommandEnd()


def thanDevCm(proj):
    "Gets dimension of window and screen."
    w, h, width, height, widthmm, heightmm = proj[2].thanGudGetWinDim()
    s = ("screen width x height (mm)     : %7.1f x %7.1f" % (widthmm, heightmm),
         "screen width x height (pixels) : %7d x %7d"     % (width,  height),
         "window width x height (pixels) : %7d x %7d"     % (w, h),
        )
    proj[2].thanGudCommandEnd("\n".join(s), "info")


def thanDevCmdsave(proj):
    "Saves the content of the command window to a txt file."
    import thancomfile
    _, fout = thancomfile.thanTxtopen(proj, T["Save command window text"], mode="w")
    if fout == Canc: return proj[2].thanGudCommandCan()
    fout.write(proj[2].thanCom.thanGet())
    fout.close()
    proj[2].thanGudCommandEnd(T["Save command window text was completed."], "info")


def __AddElem(proj, elemClass, *args, **kw):
    "Creates an element with attributes *args on the current layer."
    elem = elemClass()
    elem.thanSet(*args, **kw)
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)


def thanDevTrans(proj):
    "Save the translation report to a file."
    import thancomfile, thantrans
    _, fout = thancomfile.thanTxtopen(proj, T["Save translation report"], mode="w")
    if fout == Canc: return proj[2].thanGudCommandCan()
    for t, Ti in thantrans.thanTransAll.iteritems():
        fout.write("%s:\n" % t)
        Ti.thanReport(fout)
        fout.write("\n\n\n")
    fout.close()
    proj[2].thanGudCommandEnd(T["Translation report was completed"], "info")


def thanDevHandle(proj):
    "Show the handles of some elements."
    import itertools
    n = 100
    prt = proj[2].thanPrt
    prt("%7s %-7s %-7s %r" % ("Handle", "Tag", "ElemTag", "Element"), "info")
    for h,e in itertools.islice(proj[1].thanTagel.iteritems(), n):
        prt("%7d %-7s %-7s %r" % (e.handle, h, e.thanTags[0], e))
    proj[2].thanGudCommandEnd()


def thanFractal(proj):
    "Create a colored fractal."
    from thanpackages import fractal
    cor = proj[2].thanGudGetPoint(T["Fractal origin: "])
    if cor == Canc: return proj[2].thanGudCommandCan()
    width = proj[2].thanGudGetPosFloat(T["Fractal width (enter=256): "], 256.0)
    if width == Canc: return proj[2].thanGudCommandCan()
    dwav = proj[2].thanGudGetFloat(T["Color difference (enter=+20): "], 20.0)
    if dwav == Canc: return proj[2].thanGudCommandCan()
    proj[2].thanPrt(T["Please wait.."])
    print width, dwav, cor
    fractal(proj,  width, dwav, cor)
#    fractal(proj,  512,  20.0, cor)   #"cred.jpg"
#    fractal(proj,  512, -20.0, cor)   #"cblue.jpg"
    proj[2].thanGudCommandEnd()


def thanBackroundColor(proj):
    "Change the background colour of the canvas."
    from thandefs.thanatt import ThanAttCol
    colold = thancadconf.thanColBack
    proj[2].thanPrt("%s: %s" % (T["Current background colour is"], colold))
    r = proj[2].thanGudGetOpts(T["Select background colour [Black/White/Other] <Black>:"],
        default="Black", options=("Black", "White", "Other"))
    if r == Canc: return proj[2].thanGudCommandCan()
    if r == "w":
        colnew = ThanAttCol("white")
    elif r == "b":
        colnew = ThanAttCol("black")
    else:
        w = thantkdia.ThanColor(proj[2], colold, special=False, title=T["Select background colour"])
        colnew = w.result
        if colnew == None: return proj[2].thanGudCommandCan()
    __backgrestore(proj, colnew)
    proj[1].thanDoundo.thanAdd("background", __backgrestore, (colnew,),
                                             __backgrestore, (colold,))
    proj[2].thanGudCommandEnd()


def __backgrestore(proj, col):
    "Restores canvas background colour."
    #If the new background is black or white:
            #If the layer's colour is the same as the background, we change its colour. However if layer's colour
            #is black and the background was previously black, then the layer was drawn as white previously
            #and so the layer must be drawn again when the new background is white, even if in theory
            #it has not the same colour as the new background
    #If the new background is not black nor white:
            #If the layer's colour
            #is black and the background was previously black, then the layer was drawn as white previously.
            #With the new background (nonblank and nonwhite) it must be redrawn to restrore it original colour
    #Thus all the layers with black or white colour must be drawn again
    thancadconf.thanColBack = col
    proj[2].thanCanvas.config(background=col.thanTk)
    for tlay,lay in proj[1].thanLayerTree.dilay.iteritems():
        if lay.thanAtts["frozen"].thanVal: continue   #There are no elements of frozen layers on the canvas
        sc = str(lay.thanAtts["moncolor"])
        if sc != "black" and sc != "white": continue
        scoli, fill = lay.thanGetColour()
        proj[2].thanGudGetSelLayerx(tlay)                     #Select all layer's active elements on the canavas and..
        proj[2].thanGudSetSelColorx(col=scoli, fillcol=fill)  #..Change their colour
