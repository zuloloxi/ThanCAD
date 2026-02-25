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

Package which processes commands entered by the user.
This module processes various commands.
"""
from math import pi, fabs
import tkinter
import p_ggen, p_gtkwid
import thandr, thantkdia, thanlayer
from thanvers import tcver
from thanvar import Canc, InfoWin, thanNearElev
from thantrans import T, thanLangSetall
from thanopt import thancadconf
from . import thancomsel, thanundo
from .thancomfile import thanTxtopen
from .thancommod import thanModCanc, thanModCancSel, thanModEnd


def thanVarLang(proj):
    "Change the physical language of ThanCad's interface."
    res = proj[2].thanGudGetOpts("Enter language (en=english/gr=greek) <en>:",
        default="en", fullopt=True, options=("en", "gr"))
    if res == Canc: return proj[2].thanGudCommandCan()
    #print "new lang=", res
    thanLangSetall(res)
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
    t = ",".join(sd(c[j]) for j in range(2, nd))
    proj[2].thanPrt("%s %s" % (T["Current elevations of z and higher dimensions:"], t), "")
    stat = "%s%s): " % (T["Enter new elevations separated by coma (enter="], t)
    cz = proj[2].thanGetElevations(nd, stat, c[2:])
    if cz == Canc: return proj[2].thanGudCommandCan()
    c[2:] = cz                                # Update elevation list
    proj[1].thanTouch()                       # Drawing has been modified
    proj[2].thanGudCommandEnd()


def thanTkImageFrame(proj):
    "Set imageframe on or off."
    prev = bool(proj[1].thanVar["imageframe"])
    defa = ("OFF", "ON")[prev]
    proj[2].thanPrt(T["Imageframe is %s."] % (defa, ))
    mes = T["Enter image frame setting [ON/OFF] <%s>: "] % (defa, )
    imfr = proj[2].thanGudGetOnoff(mes, default=defa)
    if imfr == Canc: return proj[2].thanGudCommandCan()
    __regenimages(proj, imfr)
    proj[1].thanDoundo.thanAdd("imageframe", __regenimages, (imfr,),
                                             __regenimages, (prev,))
    proj[2].thanGudCommandEnd()

def __regenimages(proj, imfr):
    "Regenerate images, set variables and print result."
    imfr = bool(imfr)
    proj[1].thanVar["imageframe"] = imfr
    proj[2].than.imageFrameOn = imfr
    proj[2].thanAutoRegen(regenImages=True)
    proj[2].thanPrtbo(T["Imageframe is now %s."] % ( ("OFF", "ON")[imfr], ))


def thanVarFill(proj):
    "Set fill on or off."
    proj[2].thanPrt("This command controls the fill of hatches and solids.")
    prev = bool(proj[1].thanVar["fillmode"])
    defa = ("OFF", "ON")[prev]
    mes = T["Enter mode [ON/OFF] <%s>: "] % (defa, )
    fimo = proj[2].thanGudGetOnoff(mes, default=defa)
    if fimo == Canc: return proj[2].thanGudCommandCan()
    __regensolidshatches(proj, fimo)
    proj[1].thanDoundo.thanAdd("fillmode", __regensolidshatches, (fimo,),
                                           __regensolidshatches, (prev,))
    proj[2].thanGudCommandEnd()


def __regensolidshatches(proj, fimo):
    "Regenerate solids and hatches, set variables and print result."
    fimo = bool(fimo)
    proj[1].thanVar["fillmode"] = fimo
    than = proj[2].than
    than.fillModeOn = fimo

    filt = lambda e: isinstance(e, thandr.ThanHatch)
    proj[2].thanGudSetSelExternalFilter(filt)
    elems = proj[2].thanGudGetDisplayed()

    proj[2].thanGudSetSelExternalFilter(None)   #Reset filter
    proj[2].thanGudGetSelElemx(elems)           #Mark elements with 'selx'
    proj[2].thanGudSetSelDelx()                 #Removes the drawn elements from the canvas

    for e in elems: e.thanTkDraw(than)  #Redraws the elements on the canvas
    #proj[2].thanPrtbo(T["Fill mode is now %s."] % ( ("OFF", "ON")[fimo], ))
    proj[1].thanTouch()


def thanVarOrtho(proj):
    "Set ortho mode on or off."
    prev = proj[2].thanCanvas.thanOrtho.toggle()   #Toggle
    prev = proj[2].thanCanvas.thanOrtho.toggle()   #Toggle again to get current ortho mode
    defa = ("OFF", "ON")[prev]
    mes = T["Enter mode [ON/OFF] <%s>: "] % (defa, )
    fimo = proj[2].thanGudGetOnoff(mes, default=defa)
    if fimo == Canc: return proj[2].thanGudCommandCan()
    __setortho(proj, fimo)
    proj[1].thanDoundo.thanAdd("orthomode", __setortho, (fimo,),
                                            __setortho, (prev,))
    proj[2].thanGudCommandEnd()


def __setortho(proj, fimo):
    "Regenerate solids and hatches, set variables and print result."
    fimo = bool(fimo)
    cur = proj[2].thanCanvas.thanOrtho.toggle()   #Toggle and get current value
    if fimo:
        if not cur: cur = proj[2].thanCanvas.thanOrtho.toggle()   #Toggle again to make it True
    else:
        if cur: cur = proj[2].thanCanvas.thanOrtho.toggle()   #Toggle again to make it False


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
    win.thanGudCommandEnd()                   # Finish the script command and reprompt
    while True:
        while not cmd.thanWaitingInput:
            dc.update()
        try: com1 = next(coms)
        except StopIteration: break
        win.thanScheduler.thanSchedClear()    # The previous command is cleared; breaks some tk gui commands
        cmd.thanEnter(com1)
    win.thanScriptComs = ()


def __itercom(fr):
    "Iterator which excludes the comments."
    for dline in fr:
        dline = dline.strip()
        if dline[:1] == "#": continue
        yield dline


def thanFormLay(proj):
    "Shows interactive window with layer tree in order to manipulates layers."
    from thanlayer.thanlayatts import thanChangedAtts
    newcl, newroot = thanundo.thanLtClone(proj)
    #print "newroot"
    pre(newroot)
    w = thantkdia.ThanDialogLay(proj[2],
        objs=[newroot], current=newcl,
        atts=thanlayer.thanlayatts.thanLayAttsNames, cargo=proj,
        widths=thanlayer.thanlayatts.thanLayAttsWidths,
        height=15, vscroll=1, hscroll=1,
        onclick=thanlayer.thanlayatts.thanOnclick,
        title=proj[2].thanTitle+": "+T["Layer Control"])
    if w.result is not None:
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
    print("%s '%s' '%s'" % (lay.thanAtts[thanlayer.THANNAME].thanVal, lay.thanAtts["expand"].thanVal, lay.thanAtts["expand"].thanPers))
    for lay in lay.thanChildren: pre(lay)

def __formLayUndo(proj, oldcl, oldroot):
    "Undoes the changes layer hierarchy."
#The following commented code is broken, since a whole subhierarchy of layers
#may have been moved to another parent
#    oldleaflayers = {}
#    for lay,atts in newleaflayers.items():   #works for python2,3
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
    if win.result is None: return proj[2].thanGudCommandCan()
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
    vold.radAngldire = vs._dir2num[vs.angldire]    # Anti-clockwise angles are positive
    a = (3.0 - vs.anglzero*6.0/pi) % 12.0          # Transform radians to 3, 12, 9 or 6 o'clock
    if int(a+0.1) == 0: a = 12.0
    vold.radAnglzero = vs._ori2num[int(a+0.1)]     # Zero is at 0.0 radians angle from the x-axis in the anticlockwise direction

    w = thantkdia.ThanDialogUnits(proj[2], vals=vold, cargo=proj,
        title="%s - %s: %s" % ("ThanCad", proj[0].namebase, T["Unit management"]))
    vnew = w.result
    if vnew is None: return proj[2].thanGudCommandCan()

    __unitsrestore(proj, vnew)                     #thanTouch is implicitly called
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
        angldire = vs._dir2text[v.radAngldire],   # Anti-clockwise angles are positive
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
        for name, objs in proj[1].thanObjects.items():  #works for python2,3
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
    font1 = tkinter.font.Font(family=thancadconf.thanFontfamily, size=thancadconf.thanFontsize)
    p_gtkwid.thanGudHelpWin(proj[2], tcver.about, "%s %s" % (T["About"], tcver.name),
                            font=font1)   # (Gu)i (d)ependent
    proj[2].thanGudCommandEnd()


def thanHelpHelp(proj):
    font1 = tkinter.font.Font(family=thancadconf.thanFontfamily, size=thancadconf.thanFontsize)
    p_gtkwid.thanGudHelpWin(proj[2], tcver.help, tcver.name+" "+T["Help"],   # (Gu)i (d)ependent
                            font=font1)   # (Gu)i (d)ependent
    proj[2].thanGudCommandEnd()

def thanHelpGpl (proj):
    font1 = tkinter.font.Font(family=thancadconf.thanFontfamily, size=thancadconf.thanFontsize)
    p_gtkwid.thanGudHelpWin(proj[2], tcver.license[2], tcver.name+" "+T["GPL"],   # (Gu)i (d)ependent
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

    codes = sorted(proj[2].than.font.thanGetCodes())
    for i in range(0, len(codes), 8):
        c[1] -= h*3
        c[0] = 0
        for j in range(i, min(i+8, len(codes))):
            t = "%3d:%s" % (codes[j], chr(codes[j]))
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
    from . import thancomfile
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
    import thantrans
    from . import thancomfile
    _, fout = thancomfile.thanTxtopen(proj, T["Save translation report"], mode="w")
    if fout == Canc: return proj[2].thanGudCommandCan()
    for t, Ti in thantrans.thanTransAll.items():   #works for python2,3
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
    for h,e in itertools.islice(proj[1].thanTagel.items(), n):   #works for python2,3
        prt("%7d %-7s %-7s %r" % (e.handle, h, e.thanTags[0], e))
    proj[2].thanGudCommandEnd()




def thanHighlightZero(proj):
    "Show briefely all (currently visible) lines and point with elevation 0."
    elev2show = 0.0

    ThanLine = thandr.ThanLine
    ThanPoint = thandr.ThanPoint
    filt = lambda e: isinstance(e, ThanLine) or isinstance(e, ThanPoint)
    proj[2].thanGudSetSelExternalFilter(filt)

    elzer = []
    for e in proj[2].thanGudGetDisplayed():    #Select all lines and points currently visible
        if isinstance(e, ThanPoint):
            c1 = e.getInspnt()
            if thanNearElev(c1[2], elev2show): elzer.append(e)
        else:
            for c1 in e.cp:
                if not thanNearElev(c1[2], elev2show): break
            else:
                elzer.append(e)
    if len(elzer) == 0: return proj[2].thanGudCommandCan(T["No elements with zero elevation found."])

    proj[2].thanGudSetSelExternalFilter(None)
    proj[2].thanGudGetSelElemx(elzer)
    proj[2].thanGudSetSelColorx()
    text = "z=" + proj[2].than.strdis(elev2show)
    dc = proj[2].thanCanvas
    ct = proj[2].thanCt
    n = len(elzer)
    nmax = 20
    if n > nmax:
        proj[2].thanPrter1("Too many lines/points with zero elevations: only {} elevations are shown".format(nmax))
        proj[2].thanPrter1("(zoom in, in oder to limit the search area)")
        n = nmax
    for i in range(n):
        e = elzer[i]
        c1 = e.getInspnt()
        px, py = ct.global2Locali(c1[0], c1[1])
        px += -dc.canvasx(0) + dc.winfo_rootx()
        py += -dc.canvasy(0) + dc.winfo_rooty()
        t = InfoWin(help=text, position=(px, py))
    dc.after(3000, __recolor, proj, elzer)
    proj[2].thanGudCommandEnd()


def __recolor(proj, elzer):
    "Paint the elements with their original color."
    dilay = proj[1].thanLayerTree.dilay
    for e in elzer:
        tlay = e.thanTags[1]
        lay = dilay[tlay]
        outline = lay.thanAtts["moncolor"].thanTk
        if lay.thanAtts["fill"].thanVal: fill = outline
        else:                            fill = ""
        proj[2].thanGudGetSelElemx([e])
        proj[2].thanGudSetSelColorx(outline, fill)



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
    #print width, dwav, cor
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
        if colnew is None: return proj[2].thanGudCommandCan()
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
            #With the new background (nonblank and nonwhite) it must be redrawn to restore it original colour
    #Thus all the layers with black or white colour must be drawn again
    thancadconf.thanColBack = col
    proj[2].thanCanvas.config(background=col.thanTk)
    for tlay,lay in proj[1].thanLayerTree.dilay.items():  #works for python2,3
        if lay.thanAtts["frozen"].thanVal: continue   #There are no elements of frozen layers on the canvas
        sc = str(lay.thanAtts["moncolor"])
        if sc != "black" and sc != "white": continue
        scoli, fill = lay.thanGetColour()
        proj[2].thanGudGetSelLayerx(tlay)                     #Select all layer's active elements on the canvas and..
        proj[2].thanGudSetSelColorx(col=scoli, fillcol=fill)  #..Change their colour


def thanEditEncoding(proj):
    "Sets the encoding for import/export to text data format and other uses."
    encold = p_ggen.thanGetEncoding()
    proj[2].thanPrt(T["Current encoding is: "]+encold, "info1")
    encnew = thantkdia.thanSelectEncoding(proj, encold)
    if encnew is None: return proj[2].thanGudCommandCan()   #User cancelled
    p_ggen.thanSetEncoding(encnew)
    proj[1].thanDoundo.thanAdd("encoding", __encrestore, (encnew,),
                                           __encrestore, (encold,))
    proj[2].thanGudCommandEnd(T["Encoding set to: "]+encnew, "info")


def __encrestore(proj, enc):
    "Restores encoding for imprort/export of text files."
    p_ggen.thanSetEncoding(enc)


def thanDrawOrder(proj):
    "Inform the user about the draworder attribute of layers."
    comname = "draworder"
    proj[2].thanPrt(T["Instead of the draworder command, please use ThanCad's draworder layer attribute"], "can1")
    proj[2].thanPrt(T["which is much more versatile."], "can1")
    proj[2].thanGudCommandCan()


import p_gimgeo
import thantk, thansupport
class EduDfr(tkinter.Toplevel):
    """Opens dfr file produced by the demtra.py program (demtra finds the systematic bias in a DEM file).

    See: /home/a12/h/a/topog/demresearch/demtra/developer/ex/sanfransisco_tanxdem_srtm_cgiar
    This class reads the file content (coordinates) and shows them in a window.
    Doubleclicking on a line of the opened window, the class reads the coordinates
    of the point there, makes a circle in the current drawing, writes the coordinates
    to a kml file with the prefix of the current drawing, and writes the coordinates
    to .syn.tel file with the prefix of the current drawing."""


    def __init__(self, proj, fn, fr, *args, **kw):
        tkinter.Toplevel.__init__(self, proj[2], *args, **kw)
        self.thanProj = proj
        self.title(proj[0].basename()+" - "+fn.basename())
        #self.txt = p_gtkwid.ThanText(self)
        self.txt = p_gtkwid.ThanScrolledText(self)
        self.txt.grid(sticky="wesn")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.txt.thanAppend(fr.read())
        #self.txt.bind("<Double-Button-1>", self.dfrOnDClick)
        self.txt.bindte("<Double-Button-1>", self.dfrOnDClick)
        thantk.createTags((self.txt,))
        self.cps = []        #Points that we made circles at
        fn = self.thanProj[0].parent / self.thanProj[0].namebase + ".kml"
        self.kmlw = p_gimgeo.ThanKmlWriter(fn)
        #self.protocol("WM_DELETE_WINDOW", self.destroy) # THIS IS NOT NEEDED (IT IS ACTUALLY WRONG)..
                                                         # ..destroy()) is automatically called when window is deleted

    def dfrOnDClick(self, evt):
        """Selects a point from read .dxf point, draws ity and saves it.

        Doubleclicking on a line of the opened window, the class reads the coordinates
        of the point there, makes a circle in the current drawing, writes the coordinates
        to a kml file with the prefix of the current drawing, and writes the coordinates
        to .syn.tel file with the prefix of the current drawing."""
        pos = "@%d,%d" % (evt.x, evt.y)
        t = self.txt.thanGetPart(pos+"linestart", pos+"lineend")
        #print t
        try:
            dl = t.split()
            xp, yp = float(dl[0]), float(dl[1])
        except (ValueError, IndexError):
            return
        #print xp, yp
        cp = list(self.thanProj[1].thanVar["elevation"])
        cp[:2] = xp, yp

        laydfr = thansupport.thanToplayerCurrent(self.thanProj, "dfr", current=True, moncolor="red")
        elem = thandr.ThanCircle()
        elem.thanSet(cp, 1000.0)
        self.thanProj[1].thanElementAdd(elem)             # thanTouch is implicitly called
        elem.thanTkDraw(self.thanProj[2].than)
        self.cps.append(cp)
        fn = self.thanProj[0].parent / self.thanProj[0].namebase + ".kml"
        kmlw = p_gimgeo.ThanKmlWriter(fn)
        kmlw.thanSetProjection(self.thanProj[1].geodp)
        fw = open(fn.parent / fn.namebase + ".syn.sel", "w")
        for i,cp in enumerate(self.cps):
            kmlw.writePlacemark("THC"+str(i+1), cp)
            fw.write("%-10s%15.3f%15.3f\n" % ("THC"+str(i+1), cp[0], cp[1]))
        kmlw.close()
        fw.close()

        xymm = list(elem.getBoundBox())
        dx, dy = xymm[2]-xymm[0], xymm[3]-xymm[1]
        xymm[0] -= 5*dx; xymm[2] += 5*dx
        xymm[1] -= 5*dy; xymm[3] += 5*dy
        self.thanProj[1].viewPort[:] = self.thanProj[2].thanGudZoomWin(xymm)
        self.thanProj[2].thanAutoRegen(regenImages=True)

    def destroy(self):
        "Break circular references."
        #print "destroy called"
        del self.txt, self.thanProj
        tkinter.Toplevel.destroy(self)


def thanEduDfr(proj):
    "Open a dfr file which contains coordinates."
    fn, fr = thanTxtopen(proj, "Please select .dfr file", suf=".dfr", mode="r", initialfile=None, initialdir=None)
    if fn == Canc: return proj[2].thanGudCommandCan()
    top = EduDfr(proj, fn, fr)
    fr.close()
    proj[1].thanDoundo.thanAdd("edudfr", p_ggen.doNothing, (),
                                         p_ggen.doNothing, ())
    proj[2].thanGudCommandEnd()
