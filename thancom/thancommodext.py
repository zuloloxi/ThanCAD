# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

Package which processes commands entered by the user.
This module provides for line extension (modification) commands.
"""


from thanvar import Canc, thanFiletCalc
from thantrans import T
from selutil import thanSel1line, thanSel2linsegs, thanSelMultlines, thanSelectCrosClear
from thancommod import thanModCanc, thanModEnd, thanModCancSel, thanFilterCut
import thanundo, thancomsel


__filetrad = 0.0
def thanModFilet(proj):
    "Extends and joins 2 line segments with circular arc."
    global __filetrad
    strd = proj[1].thanUnits.strdis
    rr = __filetrad
    dilay = proj[1].thanLayerTree.dilay
    while True:
        proj[2].thanPrt("Current radius=%s" % (strd(rr),))
        res = thanSel2linsegs(proj, T["Select first two sinle segment line to filet (R=Radius): "],
                                    T["Select second two sinle segment line to filet: "], options=("radius",))
        if res == Canc: return thanModCanc(proj)               # Filet was cancelled
        if res[0] != "r": break
        mes = T["Radius of circular arc (enter=%s): "] % (strd(rr),)
        res = proj[2].thanGudGetFloat2(mes, default=rr, limits=(0.0, None), strict=True)
        if res == Canc: proj[2].thanPrtCan()      #New radius was cancelled; continue with the filet command
        else:           rr = res
    aa, bb, anear, bnear = res
    __filetrad = rr
    selold = proj[2].thanSelold
    a, b = aa.thanClone(), bb.thanClone()
    ierr, obj = thanFiletCalc(a, b, rr, anear, bnear)
    if ierr == 1: return thanModCanc(proj, T["End lines are parallel and do not intersect"])
    if ierr == 2: return thanModCanc(proj, T["Circular arc lies beyond the line segments"])
    assert ierr == 0
#    a.thanTags = aa.thanTags
#    a.handle = aa.handle
#    b.thanTags = bb.thanTags
#    b.handle = bb.handle
    delelems = set((aa, bb))
    newelems = set((a, b))
    if obj != None:
        from thandr import ThanArc
        arc = ThanArc()
        arc.thanSet(*obj)
        lay = dilay[elem.thanTags[1]]
        proj[1].thanElementAdd(arc, lay)
        newelems.add(arc)
    thanundo.thanReplaceRedo(proj, delelems, newelems, newelems),
    proj[1].thanDoundo.thanAdd("filet", thanundo.thanReplaceRedo, (delelems, newelems, newelems),
                                        thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)           # 'Reset color' is needed here


def thanModExtend(proj):
    "Extends elements using other elements as boundary edges, if possible."
    mt = ("The extended element replaces the original element",
          "The extended element replaces the original element but retains the original end node (lines only)",
          "The extended element contains only the net extension and the original element is retained",
         )
    thanExtendMethod = 1
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
        assert c1 != None, "thancomsel.thanSelect1Gen does not work well!"
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
#        newelems = [e for e in elem.thanExtendTrim(ps, c1) if e != None]
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
#    for i in xrange(iel):
#        delelems.extend(dodo[i][0])
#        newelems.extend(dodo[i][1])
    delelems = []
    newelems = []
    for i in xrange(iel):
        print i, "/", iel
        delelemsi, newelemsi = dodo[i]
        for e in delelemsi:
            if e in newelems:      #If (e) was a previously new element, then (e) was an intermediate element
                print e, "is intemediate"
                newelems.remove(e) #which is already deleted, and there is no need to recreate it and redelete it
            else:
                print e, "is to be deleted"
                delelems.append(e)
        print newelemsi, "are to be added"
        newelems.extend(newelemsi)
    print "delelems=", delelems
    print "newelems=", newelems
    proj[1].thanDoundo.thanAdd("extend", thanundo.thanReplaceRedo, (delelems, newelems, elcut),
                                         thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)


def __filterExt(e):
    "Filters alaments that can be extended."
    from thandr import ThanLine, ThanArc
    for cls in ThanLine, ThanArc:
        if isinstance(e, cls): return True
    return False
