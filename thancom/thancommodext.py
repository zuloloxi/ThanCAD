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
This module provides for line extension (modification) commands.
"""

import p_ggen
from thanvar import Canc, thanFilletCalc
from thantrans import T
from .selutil import thanSel2linsegs
from .thancommod import thanModCanc, thanModEnd, thanModCancSel, thanFilterCut
from . import thanundo, thancomsel


__filletrad = 0.0
def thanModFillet(proj):
    "Extends and joins 2 line segments with circular arc."
    global __filletrad
    strd = proj[1].thanUnits.strdis
    rr = __filletrad
    dilay = proj[1].thanLayerTree.dilay
    while True:
        proj[2].thanPrt("Current radius=%s" % (strd(rr),))
        res = thanSel2linsegs(proj, T["Select first single segment line to fillet (R=Radius): "],
                                    T["Select second single segment line to fillet: "], options=("radius",))
        if res == Canc: return thanModCanc(proj)               # Fillet was cancelled
        if res[0] != "r": break
        mes = T["Radius of circular arc (enter=%s): "] % (strd(rr),)
        res = proj[2].thanGudGetFloat2(mes, default=rr, limits=(0.0, None), strict=True)
        if res == Canc: proj[2].thanPrtCan()      #New radius was cancelled; continue with the fillet command
        else:           rr = res
    aa, bb, anear, bnear = res
    __filletrad = rr
    selold = proj[2].thanSelold
    a, b = aa.thanClone(), bb.thanClone()
    ierr, obj = thanFilletCalc(a, b, rr, anear, bnear)
    if ierr == 1: return thanModCanc(proj, T["End lines are parallel and do not intersect"])
    if ierr == 2: return thanModCanc(proj, T["Circular arc lies beyond the line segments"])
    assert ierr == 0
#    a.thanTags = aa.thanTags
#    a.handle = aa.handle
#    b.thanTags = bb.thanTags
#    b.handle = bb.handle
    delelems = set((aa, bb))
    newelems = set((a, b))
    if obj is not None:
        from thandr import ThanArc
        arc = ThanArc()
        arc.thanSet(*obj)
        lay = dilay[aa.thanTags[1]]
        proj[1].thanElementAdd(arc, lay)
        newelems.add(arc)
    thanundo.thanReplaceRedo(proj, delelems, newelems, newelems),
    proj[1].thanDoundo.thanAdd("fillet", thanundo.thanReplaceRedo, (delelems, newelems, newelems),
                                         thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)           # 'Reset color' is needed here


thanExtendMethod = 0
def thanModExtend(proj):
    "Extends elements using other elements as boundary edges, if possible."
    global thanExtendMethod
    mt = ("The extended element replaces the original element",
          "The extended element replaces the original element but retains the original end node (lines only)",
          "The extended element contains only the net extension and the original element is retained",
         )
    while True:
        proj[2].thanPrt(T["Select elements to be used as boundary edges, or press enter to select all elements on display:"])
        proj[2].thanPrt("%s: %s" % (T["Extension method"], T[mt[thanExtendMethod]]), "info")
        res = thancomsel.thanSelectOr(proj, standalone=False, filter=thanFilterCut,
            optionname="method", optiontext="m=extension method", enter=1)
        if res == Canc: return thanModCanc(proj)
        if res == "m":
            thanModCancSel(proj)   #The user did not select anything so cancel current (empty) selection
            for i, t in enumerate(mt): proj[2].thanPrt("%d. %s" % (i+1, T[t]), "")
            res = proj[2].thanGudGetInt2(T["Select extension method (1/2/3) <1>: "], default=1, limits=(1, 3))
            if res == Canc: proj[2].thanPrtCan()
            else:           thanExtendMethod = res - 1
            continue
        break
    __extend2Boundaries(proj, thanExtendMethod)


def __extend2Boundaries(proj, thanExtendMethod):
    """Extends elements using other elements as boundary edges, if possible.

    Note that the selection this command does, is the selection of the boundary
    edges. This selection is cancelled if the command is cancelled. And this
    is the "previous" selection of next command to be given to ThanCad.
    The selections of 1 extensible element are not recorded.
    """
    from thandr import thanintall
#    proj[2].thanPrt(T["Select elements to be used as boundary edges:"])
##    res = thancomsel.thanSelectGen(proj, standalone=False, filter=thanFilterCut)
#    res = thancomsel.thanSelectOr(proj, standalone=False, filter=thanFilterCut,
#        optionname="settings", optiontext="s=settings")
#    if res == Canc: return thanModCanc(proj)               # Extend was cancelled
    elcut = proj[2].thanSelall
    selold = proj[2].thanSelold
    proj[2].thanUpdateLayerButton()                   # Show current layer again
    iel = 0
    dodo = []             # Undo/Redo list
    mes1 = T["Select an element to extend"]
    dilay = proj[1].thanLayerTree.dilay
    while True:
        opts = []
        if iel > 0: opts.append("undo")
        if len(dodo) > iel: opts.append("redo")
        if len(opts) > 0: mes = "%s (%s): " % (mes1, "/".join(opts))
        else: mes = "%s: " % mes1
        opts.append("")
        res = thancomsel.thanSelect1Gen(proj, mes, filter=__filterExt, options=opts)
        if res == Canc: break                         # Trim was cancelled/ended
        if res == "": break                           # Trim was cancelled/ended
        if res == "u":
            iel -= 1
            delelems, newelems = dodo[iel]
            proj[1].thanElementDelete(newelems, proj)
            proj[1].thanElementRestore(delelems, proj)
            continue
        if res == "r":
            delelems, newelems = dodo[iel]
            proj[1].thanElementDelete(delelems, proj)
            proj[1].thanElementRestore(newelems, proj)
            iel += 1
            continue
        c1 = proj[2].thanSel1coor
        assert c1 is not None, "thancomsel.thanSelect1Gen does not work well!"
        for elem in proj[2].thanSelall: break    # Get the element
        ps = []
        for elcut1 in elcut:
            iend, ps1 = thanintall.thanExt(elem, elcut1, c1, proj)
            ps.extend(ps1)
        if len(ps) < 1:
            proj[2].thanPrt(T["Element extension does not intersect boundary edges"], "can")
            proj[2].thanUpdateLayerButton()           # Show current layer again
            continue
        _, cp = min(ps)
        newelems = elem.thanExtend(cp, iend, thanExtendMethod)
#        newelems = [e for e in elem.thanExtendTrim(ps, c1) if e is not None]
        assert newelems, "thanintall.thanExt() should have already found that no extensions are possible :("
        lay = dilay[elem.thanTags[1]]
        for e in newelems: proj[1].thanElementTag(e, lay)
        if thanExtendMethod != 2: proj[1].thanElementDelete((elem,), proj)  #Delete original element
        proj[1].thanElementRestore(newelems, proj)

        proj[2].thanUpdateLayerButton()               # Show current layer again
        del dodo[iel:]
        if thanExtendMethod != 2: dodo.append(((elem,), newelems))          #Delete original element
        else:                     dodo.append(((), newelems))               #Do not delete original element
        iel += 1

    proj[2].thanGudSetSelElem(elcut)          # The current selection (cutting edges)
    proj[2].thanGudSetSeloldElem(selold)      # The selection before the command trim started
    if iel == 0: return thanModCanc(proj)     # Trim was cancelled: unselect cutting edges
#    delelems = []
#    newelems = []
#    for i in range(iel):
#        delelems.extend(dodo[i][0])
#        newelems.extend(dodo[i][1])
    delelems = []
    newelems = []
    for i in range(iel):
        #print i, "/", iel
        delelemsi, newelemsi = dodo[i]
        for e in delelemsi:
            if e in newelems:      #If (e) was a previously new element, then (e) was an intermediate element
                #print e, "is intermediate"
                newelems.remove(e) #which is already deleted, and there is no need to recreate it and redelete it
            else:
                #print e, "is to be deleted"
                delelems.append(e)
        #print newelemsi, "are to be added"
        newelems.extend(newelemsi)
    #print "delelems=", delelems
    #print "newelems=", newelems
    proj[1].thanDoundo.thanAdd("extend", thanundo.thanReplaceRedo, (delelems, newelems, elcut),
                                         thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)


def __filterExt(e):
    "Filters elements that can be extended."
    from thandr import ThanLine, ThanArc
    for cls in ThanLine, ThanArc:
        if isinstance(e, cls): return True
    return False


__dis = p_ggen.Struct()
__dis.delta = 10.0
__dis.per = 100.0
__dis.total = 10.0
def thanModLengthen(proj):
    "Extends elements with various methods."
    strd = proj[1].thanUnits.strdis
    selold = proj[2].thanSelold
    selnew = selold    #No new selection: we dont have boundaries as in the extend command

    #mes = T["Lengthen: DElta/Percent/Total/DYnamic (enter=DE): "]
    mes = T["Lengthen: DElta/Percent/Total (enter=DE): "]
    res = proj[2].thanGudGetOpts(mes, default="DE", options=("delta", "percent", "total", "dynamic"))
    if res == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
    if res == "d" or res == "delta":
        res = proj[2].thanGudGetFloat(T["Delta length (enter=%s): "] % (strd(__dis.delta),), default=__dis.delta)
        if res == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
        __dis.delta = res
        return __process(proj, selnew, selold, 0)
    elif res == "p":
        res = proj[2].thanGudGetPosFloat(T["Percentage length (enter=%s): "] % (strd(__dis.per),), default=__dis.per)
        if res == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
        __dis.per = res
        return __process(proj, selnew, selold, 1)
    elif res == "t":
        res = proj[2].thanGudGetPosFloat(T["Total length (enter=%s): "] % (strd(__dis.total),), default=__dis.total)
        if res == Canc: return proj[2].thanGudCommandCan()     # DEM operation was cancelled
        __dis.total = res
        return __process(proj, selnew, selold, 2)
    elif res == "dynamic":
        return proj[2].thanGudCommandCan("Not yet implemented :(")


def __process(proj, selnew, selold, icod):
    from thandr import ThanLine
    def filt2(e): return isinstance(e, ThanLine)
    comname = "lengthen"
    dilay = proj[1].thanLayerTree.dilay

    newelems = []
    delelems = []
    while True:
        res = thancomsel.thanSelect1Gen(proj, T["Select element to lengthen: "], filter=filt2, options=("",))
        if res == Canc: break                         # Trim was cancelled/ended
        if res == "": break                           # Trim was cancelled/ended
        c1 = proj[2].thanSel1coor
        assert c1 is not None, "thancomsel.thanSelect1Gen does not work well!"
        for elem in proj[2].thanSelall: break    # Get the element
        if icod == 0: delta = __dis.delta
        elif icod == 1: delta = elem.thanLength() * (__dis.per-100.0)/100.0
        elif icod == 2: delta = __dis.total - elem.thanLength()
        newelem = elem.thanLengthen(delta, c1)
        if newelem is None:
            proj[2].thanPrter1("Element can not be lengthened: it would have zero or almost zero length.")
            proj[2].thanUpdateLayerButton()           # Show current layer again
            continue
        lay = dilay[elem.thanTags[1]]
        proj[1].thanElementDelete((elem,), proj)     #Delete original element
        proj[1].thanElementRestore((newelem,), proj)
        proj[2].thanUpdateLayerButton()               # Show current layer again

        newelems.append(newelem)
        if elem in newelems:      #If (e) was a previously new element, then (e) was an intermediate element
            newelems.remove(elem) #which is already deleted, and there is no need to recreate it and redelete it
        else:
            delelems.append(elem)

    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo, (delelems, newelems, selnew),
                                        thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)













