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
This module provides for a modification commands.
"""

from math import pi, hypot, fabs, atan2, cos, sin
from p_gmath import thanNear2, thanNear3, sign
import p_ggen
from thanvar import Canc, ThanLayerError
from thantrans import T
from . import thancomsel, thanjoin, thanundo
from .selutil import thanSel1line, thanSelMultlines, thanSelectCrosClear


def thanModContline(proj):
    "Continues a line selected by the user."
    import thandr
    def getprevline():
        "Return the most recent created line, if it still exists."
        t = proj[2].thanLineRecentTag    #Most recent created line (so that we may continue it in the future)
        if t is None: return None
        linori = proj[1].thanTagel.get(t)
        if linori is None: return None
        if isinstance(linori, thandr.ThanLine): return linori
        print("Program Error: thanModContline(): Most recent created line is not a line!!!")
        return None

    linori = getprevline()
    if linori is not None:
        res = thanSel1line(proj, T["Select a line to continue (p=continue previous line): "], options=("previous",))
        if res == Canc: return thanModCanc(proj)               # Line continue was cancelled
        if res != "p": linori = res
    else:
        res = thanSel1line(proj, T["Select a line to continue:"])
        if res == Canc: return thanModCanc(proj)               # Line continue was cancelled
        linori = res

    crelold = proj[1].thanGetLastPoint()
    selold = proj[2].thanSelold
    lin = linori.thanClone()
#    lin.thanTags = linori.thanTags
#    lin.handle = linori.handle

    proj[2].thanTkSet(lin)          # Set the attributes of lin's layer
    res = lin.thanTkContinue(proj)
    proj[2].thanTkSet()             # Set the attribute of current layer
    if res == Canc:
        crelold = proj[1].thanSetLastPoint(crelold)
        return thanModCanc(proj, crelold)
    if lin.cp == linori.cp: return thanModCanc(proj)  #No change; cancel

    proj[2].thanLineRecentTag = lin.thanTags[0]   #Most recent created line (so that we may continue it in the future)

    delelems = [linori]
    newelems = set((lin,))
    crel = proj[1].thanGetLastPoint()
    thanundo.thanReplaceRedo2(proj, delelems, newelems, newelems, crel) #Room for optimisation here.
    proj[1].thanDoundo.thanAdd("continueline", thanundo.thanReplaceRedo2, (delelems, newelems, newelems, crel),
                                               thanundo.thanReplaceUndo2, (delelems, newelems, selold, crelold))
    thanModEnd(proj)                # 'Reset color' is not needed, but it is called for only 1..
                                    # ..element, so it is fast

#=============================================================================

def thanModChelevContour(proj):
    "Change the elevation of contour lines massively."
    from thandr import ThanLine, ThanText
    from thandr.thanintall import thanInt
    fil = lambda e: isinstance(e, ThanLine)
    def sel1(proj, stat):
        "Select a line and find its nearest point."
        while True:
            elem1 = thancomsel.thanSelect1(proj, stat, filter=fil)
            thanModCancSel(proj)
            if elem1 == Canc: return Canc, Canc       #elevation cancelled
            #print("chelevcontour: type(sel1coor)=", type(proj[2].thanSel1coor))
            c1 = elem1.thanPntNearest(proj[2].thanSel1coor)
            #print("chelevcontour: type(c1)=", type(c1))
            if c1 is not None: return elem1, c1
            proj[2].thanPrter(T["Point not near line. Try again."])

    elem1, c1 = sel1(proj, T["Select first contour line to elevate.."])
    if elem1 == Canc: return proj[2].thanGudCommandCan()
    while True:
        elem2, c2 = sel1(proj, T["Select last contour line to elevate.."])
        if elem2 == Canc: return proj[2].thanGudCommandCan()
        if not thanNear2(c1, c2): break
        proj[2].thanPrter(T["Selected points are identical. Try again."])

    stat = "%s%s): " % (T["Elevation of first contour line (enter="], c1[2])
    z1 = proj[2].thanGudGetFloat(stat, c1[2])
    if z1 == Canc: return thanModCanc(proj)

    stat = "%s%s): " % (T["Elevation of last contour line (enter="], c2[2])
    z2 = proj[2].thanGudGetFloat(stat, c2[2])
    if z2 == Canc: return thanModCanc(proj)

    #lin1 = ThanLine()
    #lin1.thanSet([c1, c2])
    lines = thanSelectCrosClear(proj, c1, c2, fil)
    lines -= set((elem1, elem2))
    seq = []
    for lin2 in lines:
        #ct = thanInt(lin1, lin2, proj)
        ct = lin2.thanIntseg(c1, c2)
        if len(ct) == 0: continue
        if len(ct) > 1:
            return proj[2].thanGudCommandCan("%s\n%s" % (
                T["Error: An interim contour line is met more than once:"],
                T["The elevation must increase/decrease monotonically between first and last line."]))
        ct = ct[0]
        seq.append((hypot(ct[0]-c1[0], ct[1]-c1[1]), len(seq), ct, lin2))   #len(seq) is counter: in case 2 intersection are identical
    n = len(seq)
    if n == 0:
        return proj[2].thanGudCommandCan(T["No lines were met between first and last line."])
    dz = (z2-z1)/float(n+1)
    idz = fabs(dz)
    idz = sign(int(idz+0.5), dz)
    if fabs(dz-idz) > 0.001:
        statonce = __chechDupContour(seq)
        statonce += T["Warning: delta z is not a integer: %s\n"] % dz
        stat1 = T["Continue (yes/no) (enter=yes): "]
        ans = proj[2].thanGudGetYesno(stat1, default=True, statonce=statonce)
        if ans == Canc: return proj[2].thanGudCommandCan()
        if not ans: return proj[2].thanGudCommandCan()
    else:
        dz = idz
    seq.sort()
    seq.insert(0, (0.0, 0, c1, elem1))
    seq.append((hypot(c2[0]-c1[0], c2[1]-c1[1]), len(seq), c2, elem2))
    sizes = [seq[i+1][0]-seq[i][0] for i in range(len(seq)-1)]
    siz = min(sizes)*0.5
    theta = atan2(c2[1]-c1[1], c2[0]-c1[0])   #Note that c1 != c2
    cost = cos(theta)                         #This is the user line direction
    sint = sin(theta)
    theta -= pi*0.5                           #This is the text (the plotted number z) direction
    strd = proj[1].thanUnits.strdis

    delelems = set()
    newelems = set()
    selelems = set()
    z = z1
    for _, _, ct, lin1 in seq:
        lin2 = lin1.thanClone()
        lin2.thanChelev(z)
#        lin2.thanTags = lin1.thanTags
#        lin2.handle = lin1.handle
        delelems.add(lin1)
        newelems.add(lin2)
        selelems.add(lin2)
        e = ThanText()
        ct[0] -= siz*0.5*cost
        ct[1] -= siz*0.5*sint
        e.thanSet(strd(z), ct, siz, theta)
        proj[1].thanElementTag(e)
        newelems.add(e)
        z += dz
    selold = proj[2].thanSelall
    thanundo.thanReplaceRedo(proj, delelems, newelems, selelems)
    proj[1].thanDoundo.thanAdd("chelevcontour", thanundo.thanReplaceRedo, (delelems, newelems, selelems),
                                                thanundo.thanReplaceUndo, (delelems, newelems, selold))
    proj[2].thanGudCommandEnd()


def __chechDupContour(seq):
    "Checks if the distance between contour lines is < 0.001; if yes there is probably a duplicate contour line."
    for a, b in p_ggen.iterby2(seq):
        if fabs(b[0]-a[0]) < 0.001: break
    else:
        return ""
    statonce = ""
    return T["Warning: there is probably an interim  duplicate contour line.\n"]


def thanModBreak(proj):
    "Breaks an element to 2 pieces if possible."
    elem = thancomsel.thanSelect1(proj, T["Select a (breakable) element to break.."],
        filter=lambda e: e.thanBreak()) # .break() with no arguments returns True if element is breakable
    if elem == Canc: return thanModCanc(proj)        # Break was cancelled
    c1 = proj[2].thanSel1coor
    if c1 is None or elem.thanPntNearest(c1) is None:
        c1 = __getNearPnt(proj, elem, T["First point of element to break: "])
        if c1 == Canc: return thanModCanc(proj)      # Break was cancelled
        c2 = __getNearPnt(proj, elem, T["Second point of element to break (enter=same as first point): "], options=("",))
        if c2 == Canc: return thanModCanc(proj)      # Break was cancelled
        if c2 == "": c2 = c1
    else:
        c2 = __getNearPnt(proj, elem, T["Second point of element to break (enter=same as first/F=choose other first point): "], options=("", "first"))
        if c2 == Canc: return thanModCanc(proj)      # Break was cancelled
        if c2 == "":
            c2 = c1
        elif c2 == "f":
            c1 = __getNearPnt(proj, elem, T["First point of element to break: "])
            if c1 == Canc: return thanModCanc(proj)  # Break was cancelled
            c2 = __getNearPnt(proj, elem, T["Second point of element to break (enter=same as first point): "], options=("",))
            if c2 == Canc: return thanModCanc(proj)  # Break was cancelled
            if c2 == "": c2 = c1
    newelems = set(e for e in elem.thanBreak(c1, c2) if e is not None)
    if not newelems: return thanModCanc(proj, T["Element can not be deleted; use 'ERASE'."])

    lay = proj[1].thanGetLayer(elem)
    for e in newelems: proj[1].thanElementTag(e, lay)
    delelems = [elem]
    selold = proj[2].thanSelold
    thanundo.thanReplaceRedo(proj, delelems, newelems, newelems) #Room for optimisation here.
    proj[1].thanDoundo.thanAdd("break", thanundo.thanReplaceRedo, (delelems, newelems, newelems),
                                        thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)            # 'Reset color' is completely unnecessary here, and it will slow..
                                # ..the command down. Room for optimisation here.

def __getNearPnt(proj, elem, stat1, options=()):
    "Get a point and check if it is near the element."
    statonce = ""
    while True:
        res = proj[2].thanGudGetPoint(stat1, statonce, options=options)
        if res == Canc: return Canc      # Break was cancelled
        for opt in options:
            if res == opt[:1]: return res
        if elem.thanPntNearest(res) is not None: return res
        statonce = T["Point is not near element. Try again.\n"]


def thanModStraighten(proj):
    "Straightens a line between 2 user selected points."
    from thandr import ThanLine
    elem = thancomsel.thanSelect1(proj, T["Select a line element to straighten.."],
        filter=lambda e: isinstance(e, ThanLine)) # .break() with no arguments returns True if element is breakable
    if elem == Canc: return thanModCanc(proj)         # Straighten was cancelled
    c1 = proj[2].thanSel1coor
    if c1 is None or elem.thanPntNearest(c1) is None:
        c1 = __getNearPnt(proj, elem, T["First point of element to straighten: "])
        if c1 == Canc: return thanModCanc(proj)      # Straighten was cancelled
        c2 = __getNearPnt(proj, elem, T["Second point of element to straighten: "])
        if c2 == Canc: return thanModCanc(proj)      # Straighten was cancelled
    else:
        c2 = __getNearPnt(proj, elem, T["Second point of element to straighten (F for first point): "], options=("first",))
        if c2 == Canc: return thanModCanc(proj)      # Straighten was cancelled
        if c2 == "f":
            c1 = __getNearPnt(proj, elem, T["First point of element to straighten: "])
            if c1 == Canc: return thanModCanc(proj)  # Straighten was cancelled
            c2 = __getNearPnt(proj, elem, T["Second point of element to straighten: "])
            if c2 == Canc: return thanModCanc(proj)      # Straighten was cancelled
    if thanNear2(c1, c2): return thanModCanc(proj, T["Selected points are identical."])
    e = elem.thanStraighten(c1, c2)
    e.thanTags = elem.thanTags
    delelems = [elem]
    newelems = [e]
    selold = proj[2].thanSelold
    thanundo.thanReplaceRedo(proj, delelems, newelems, newelems) #Room for optimisation here.
    proj[1].thanDoundo.thanAdd("straighten", thanundo.thanReplaceRedo, (delelems, newelems, newelems),
                                             thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)            # 'Reset color' is completely unnecessary here, and it will slow..
                                # ..the command down. Room for optimisation here.

#=============================================================================

def thanFilterCut(e):
    "Filters elements that can be used as cutting edges."
    from thandr import ThanLine, ThanCircle, ThanArc, ThanImage
    for cls in ThanLine, ThanCircle, ThanArc, ThanImage:
        if isinstance(e, cls): return True
    return False


def thanModTrim(proj):
    """Trims elements using other elements as cutting edges, if possible.

    Note that the selection this command does, is the selection of the cutting
    edges. This selection is cancelled if the command is cancelled. And this
    is the "previous" selection of next command to be given to ThanCad.
    The selections of 1 breakable element are not recorded.
    """
    from thandr import thanintall
    proj[2].thanPrt(T["Select elements to be used as cutting edges:"])
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=thanFilterCut)
    if res == Canc: return thanModCanc(proj)               # Rotation cancelled
    elcut = proj[2].thanSelall
    selold = proj[2].thanSelold
    proj[2].thanUpdateLayerButton()                   # Show current layer again
    iel = 0
    dodo = []             # Undo/Redo list
    mes1 = T["Select an element to trim"]
    dilay = proj[1].thanLayerTree.dilay
    while True:
        opts = []
        if iel > 0: opts.append("undo")
        if len(dodo) > iel: opts.append("redo")
        if len(opts) > 0: mes = "%s (%s): " % (mes1, "/".join(opts))
        else: mes = "%s: " % mes1
        opts.append("")
        res = thancomsel.thanSelect1Gen(proj, mes, filter=lambda e: e.thanBreak(), options=opts)
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
            ps.extend(thanintall.thanInt(elem, elcut1, proj))
        if len(ps) < 1:
            proj[2].thanCom.thanAppend(T["Element does not intersect cutting edges\n"], "can")
            proj[2].thanUpdateLayerButton()           # Show current layer again
            continue
        newelems = [e for e in elem.thanTrim(ps, c1) if e is not None]
        if not newelems:
            proj[2].thanCom.thanAppend(T["Element can not be deleted; use 'ERASE' instead.\n"], "can")
            proj[2].thanUpdateLayerButton()           # Show current layer again
            continue
        lay = dilay[elem.thanTags[1]]
        for e in newelems: proj[1].thanElementTag(e, lay)
        proj[1].thanElementDelete((elem,), proj)
        proj[1].thanElementRestore(newelems, proj)

        proj[2].thanUpdateLayerButton()               # Show current layer again
        del dodo[iel:]
        dodo.append(((elem,), newelems))
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
        #print(i, "/", iel)
        delelemsi, newelemsi = dodo[i]
        for e in delelemsi:
            if e in newelems:      #If (e) was a previously new element, then (e) was an intermediate element
                #print(e, "is intermediate")
                newelems.remove(e) #which is already deleted, and there is no need to recreate it and redelete it
            else:
                #print(e, "is to be deleted")
                delelems.append(e)
        print(newelemsi, "are to be added")
        newelems.extend(newelemsi)
    #print("delelems=", delelems)
    #print("newelems=", newelems)

    proj[1].thanDoundo.thanAdd("trim", thanundo.thanReplaceRedo, (delelems, newelems, elcut),
                                       thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)

#=============================================================================

def thanModEnd(proj, mes=None, mestype="can"):
    "House keeping for normal end."
    proj[2].thanGudResetSelColor()                   # Unmarks the selection
    proj[2].thanUpdateLayerButton()                  # Show current layer again
    proj[2].thanGudCommandEnd(mes, mestype)


def thanModCanc(proj, mes=None, mestype="can"):
    "House keeping for user cancel."
    proj[2].thanGudResetSelColor()                   # Unmarks the selection
    proj[2].thanGudSetSelRestore()                   # Restores previous selection
    proj[2].thanUpdateLayerButton()                  # Show current layer again
    proj[2].thanGudCommandCan(mes, mestype)          # Show prompt

def thanModCancSel(proj):
    "Cancels the most recent selection."
    proj[2].thanGudResetSelColor()                   # Unmarks the selection
    proj[2].thanGudSetSelRestore()                   # Restores previous selection
    proj[2].thanUpdateLayerButton()                  # Show current layer again

#=============================================================================

def thanModRotate(proj):
    "Rotates selected elements."
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # Rotation cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    c1 = proj[2].thanGudGetPoint(T["Origin of rotation (Insertion point): "], options=("Insertion", ))
    if c1 == Canc: return thanModCanc(proj)                # Rotation cancelled

    un = proj[1].thanUnits
    st = "%s(%s): " % (T["Rotation angle"], un.anglunit)
    phi = un.rad2unit(0.5*pi)
    phi = proj[2].thanGudGetFloat(st, phi)
    if phi == Canc: return thanModCanc(proj)               # Rotation cancelled
    phi = un.unit2rad(phi)

    __modRotateDo(proj, c1, phi)
    proj[1].thanDoundo.thanAdd("rotate", thanundo.thanActionRedo, (elems,         __modRotateDo, c1, phi),
                                         thanundo.thanActionUndo, (elems, selold, __modRotateDo, c1, -phi))
    thanModEnd(proj)                                       # 'Reset color' is necessary here; OK!


def __modRotateDo(proj, cc, phi):
    "Rotates selected elements; it actualy does the job."
    import time
    t1 = time.time()
    if cc == "i": proj[2].thanGudSetSelRotateins(phi)
    else:         proj[2].thanGudSetSelRotate(cc[0], cc[1], phi)
    t2 = time.time(); proj[1].thanRotateSel(proj[2].thanSelall, cc, phi) # ThanTouch is implicitly called
    t3 = time.time()
    #print("Rotate time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t2-t1, t3-t2, t3-t1))

#=============================================================================

def thanModMirror(proj):
    "Mirrors the selected elements."
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # Mirror cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    c1 = proj[2].thanGudGetPoint(T["First point of mirror line: "])
    if c1 == Canc: return thanModCanc(proj)                # Mirror cancelled
    while True:
        c2 = proj[2].thanGudGetLine(c1, T["Second point of mirror line: "])
        if c2 == Canc: return thanModCanc(proj)            # Mirror cancelled
        if not thanNear2(c1, c2): break
        proj[2].thanCom.thanAppend("Second point coincides with first. Try again.\n", "can")
    keeporig = proj[2].thanGudGetYesno(T["Keep original elements (<yes>/no): "], default="yes")
    if keeporig == Canc: return thanModCanc(proj)          # Mirror cancelled
    t = [c2[0]-c1[0], c2[1]-c1[1]]
    tt = hypot(t[0], t[1])
    t[0] /= tt
    t[1] /= tt
    if keeporig:
        dc = [0.0]*len(c1)
        newelems = __modMirrorCopyDo(proj, elems, c1, t)
        proj[1].thanDoundo.thanAdd("mirror", thanundo.thanReplaceRedo, ((), newelems, elems),
                                             thanundo.thanReplaceUndo, ((), newelems, selold))
    else:
        __modMirrorDo(proj, c1, t)
        proj[1].thanDoundo.thanAdd("mirror", thanundo.thanActionRedo, (elems,         __modMirrorDo, c1, t),
                                             thanundo.thanActionUndo, (elems, selold, __modMirrorDo, c1, t))
    thanModEnd(proj)       # 'Reset color' is necessary here; OK!


def __modMirrorCopyDo(proj, elems, c1, t):
    "Copies selected elements; it actualy does the job."
    import time
    t1 = time.time();
    dc = [0.0]*len(c1)
    copelems = proj[1].thanCopySel(elems, dc)   # thanTouch is implicitly called
    proj[1].thanMirrorSel(copelems, c1, t)
    t2 = time.time(); proj[2].thanGudDrawElemsMany(copelems)
    t3 = time.time()
    #print("Mirror time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t3-t2, t2-t1, t3-t1))
    return copelems


def __modMirrorDo(proj, c1, t):
    "Mirrors selected elements; it actually does the job."
    import time
    t1 = time.time(); proj[2].thanGudSetSelMirror(c1[0], c1[1], t)
    t2 = time.time(); proj[1].thanMirrorSel(proj[2].thanSelall, c1, t) # ThanTouch is implicitly called
    t3 = time.time()
    #print("Mirror time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t2-t1, t3-t2, t3-t1))

#=============================================================================

def thanModPointMir(proj):
    "Mirrors the selected elements with respect to a point."
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # Mirror cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    c1 = proj[2].thanGudGetPoint(T["Mirror point: "])
    if c1 == Canc: return thanModCanc(proj)                # Mirror cancelled
    keeporig = proj[2].thanGudGetYesno(T["Keep original elements (<yes>/no): "], default="yes")
    if keeporig == Canc: return thanModCanc(proj)          # Mirror cancelled
    assert keeporig, "Point mirror not implemented with keeporoig==False"
    if keeporig:
        dc = [0.0]*len(c1)
        newelems = __modPointMirCopyDo(proj, elems, c1)
        proj[1].thanDoundo.thanAdd("mirror", thanundo.thanReplaceRedo, ((), newelems, elems),
                                             thanundo.thanReplaceUndo, ((), newelems, selold))
    else:
        __modPointMirDo(proj, c1)
        proj[1].thanDoundo.thanAdd("mirror", thanundo.thanActionRedo, (elems,         __modPointMirDo, c1),
                                             thanundo.thanActionUndo, (elems, selold, __modPointMirDo, c1))
    thanModEnd(proj)       # 'Reset color' is necessary here; OK!


def __modPointMirCopyDo(proj, elems, c1):
    "Copies selected elements; it actualy does the job."
    import time
    t1 = time.time();
    dc = [0.0]*len(c1)
    copelems = proj[1].thanCopySel(elems, dc)   # thanTouch is implicitly called
    proj[1].thanPointMirSel(copelems, c1)
    t2 = time.time(); proj[2].thanGudDrawElemsMany(copelems)
    t3 = time.time()
    #print("Mirror time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t3-t2, t2-t1, t3-t1))
    return copelems


def __modPointMirDo(proj, c1):
    "Mirrors selected elements with respect to point; it actually does the job."
    import time
    t1 = time.time(); proj[2].thanGudSetSelPointMir(c1[0], c1[1])
    t2 = time.time(); proj[1].thanPointMirSel(proj[2].thanSelall, c1) # ThanTouch is implicitly called
    t3 = time.time()
    #print("Mirror time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t2-t1, t3-t2, t3-t1))

#=============================================================================

def thanModReverse(proj):
    "Reverses the orientation of the direction of lines."
    from thandr import ThanLine, ThanCircle, ThanArc
    reversibles = (ThanLine, ThanCircle, ThanArc)
    filt = lambda elem: isinstance(elem, reversibles)
    proj[2].thanPrt(T["Select lines, circles, arcs to reverse orientation:"])
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=filt)
    if res == Canc: return thanModCanc(proj)               # Reverse cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold
    __modReverseDo(proj)
    proj[1].thanDoundo.thanAdd("reverse", thanundo.thanActionRedo, (elems,         __modReverseDo),
                                          thanundo.thanActionUndo, (elems, selold, __modReverseDo))
    thanModEnd(proj)                                       # 'Reset color' is necessary here; OK!


def __modReverseDo(proj):
    "Rotates selected elements; it actually does the job."
    import time
    t1 = time.time()                                       # nothing to do on the canvas
    t2 = time.time()
    for e in proj[2].thanSelall:
        e.thanReverse()
    t3 = time.time()
    #print("Reverse time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t2-t1, t3-t2, t3-t1))
    proj[1].thanTouch()

#=============================================================================

def thanModExplode(proj):
    "Explodes elements to (1 level) smaller elements."
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=lambda e: e.thanExplode())
    if res == Canc: return thanModCanc(proj)     # Explode was cancelled
    delelems = proj[2].thanSelall
    selold = proj[2].thanSelold

    newelems = set()
    for e in delelems:
        lay = proj[1].thanGetLayer(e)
        lay.thanTkSet(proj[2].than)
        for e1 in e.thanExplode(proj[2].than):
            proj[1].thanElementTag(e1, lay)
            newelems.add(e1)
    thanundo.thanReplaceRedo(proj, delelems, newelems, newelems) #Room for optimisation here.
    proj[1].thanDoundo.thanAdd("explode", thanundo.thanReplaceRedo, (delelems, newelems, newelems),
                                          thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)    # 'Reset color' is not needed since the exploded fragments are redrawn. So..
                        # ..if a large number of elements are exploded, this will slow down..
                        # ..the command. Here, there is room for optimisation!

#=============================================================================

def thanModJoin(proj, ndim):
    "Joins elements (lines) to bigger ones, ignoring z and higher dimensions."
    if ndim == 3:
        nearx = thanNear3
        comname = "join"
    else:
        nearx = thanNear2
        comname = "join2d"
        proj[2].thanPrt(T["This command will join lines even if they have different z or higher dimensions"], "info1")
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # Join cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    delelems, newelems, samelems, othelems = thanjoin.thanJoinSel(proj, elems, nearx)
    selelems = othelems | samelems | newelems
    thanundo.thanReplaceRedo(proj, delelems, newelems, selelems)
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo, (delelems, newelems, selelems),
                                        thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj, "%d joined lines were produced (%d left unchanged)." % (len(newelems), len(samelems)))
                        # 'Reset color' is not needed for the joined lines..
                        # since the joined elements are redrawn. So if a large number of elements..
                        # (unlikely)  are joined, this will slow down the command.
                        # However, unjoined lines remain with the "selection" color.
                        # there is room for optimisation!


def thanModJoinGap(proj, ndim=2):
    """Joins n>=2 lines to form a larger line, filling the smallest gaps between them.

    There are 3 slightly different commands:
    joingap2: Joins lines regardless of the z or higher dimensions. It finds the
        smallest gap between two lines using 2d distance.
    joingap3: Joins lines taking into account the z (but not higher dimensions).
        It finds the smallest gap between two lines using 3d distance.
    joingap: Joins contour lines, that is lines with the same z at all
        points. It finds the smallest gap between two lines using 2d distance
        (in this case 2d distance and 3d distance is identical). Further more,
        if one line was different z than the other line, the command refuses to
        join them.
    For two lines which both have zero (or any constant value) z at all points
    the three commands are identical.
    """
    if ndim == 3:
        disx = lambda a, b: hypot(hypot(b[0]-a[0], b[1]-a[1]), b[2]-a[2])
        comname = "joingap3d"
    elif ndim == 2:
        disx = lambda a, b: hypot(b[0]-a[0], b[1]-a[1])
        comname = "joingap2d"
        proj[2].thanPrt(T["This command will join nearest lines ignoring z or higher dimension distance"], "info1")
    elif ndim == -1:  #This is the code for contour lines
        disx = lambda a, b: hypot(b[0]-a[0], b[1]-a[1])
        comname = "joingap"
        proj[2].thanPrt(T["This command will join nearest lines assuming lines have constant z (contour lines)"], "info1")
    else:
        assert 0, "Invalid code ndim={}".format(ndim)

    delelems = thanSelMultlines(proj, 1, T["Select at least 2 lines to join or 1 line to close:\n"], strict=False)
    if delelems == Canc: return thanModCanc(proj)               # Join cancelled
    selold = proj[2].thanSelold
    if ndim == -1:
        ok, terr = __testz2(delelems)
        if not ok: return thanModCanc(proj, terr)               # Join contour failed
    if len(delelems) == 1:
        for e in delelems: break
        if thanNear2(e.cp[0], e.cp[-1]): thanModCanc(proj, T["Line already closed"])      # Join failed
        en = e.thanClone()
        en.cp.append(list(en.cp[0]))
#        en.thanTags = e.thanTags
#        en.handle = e.handle
        newelems = [en]
    else:
        newelems = thanjoin.thanJoinGapn(proj, delelems, disx)
    selelems = set(newelems)
    thanundo.thanReplaceRedo(proj, delelems, newelems, selelems)
    proj[1].thanDoundo.thanAdd(comname, thanundo.thanReplaceRedo, (delelems, newelems, selelems),
                                        thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)    # 'Reset color' is not needed for the joined lines..
                        # since the joined elements are redrawn. So if a large number of elements..
                        # (unlikely) are joined, this will slow down the command.
                        # there is room for optimisation!

def __testz2(elems):
    "Tests if each polyline has the same z every where and that all polylines have the same z."
    zall = None
    for e in elems:
        zpol = e.cp[0][2]
        for ct in e.cp:
            if ct[2] != zpol:
                return False, T["One of the lines has no constant z"]
        if zall is None: zall = zpol
        if zpol != zall:
            return False, T["One of the lines has not the same z as the others"]
    return True, ""

#=============================================================================

def thanModChlayer(proj):
    "Changes the layer of selected elements."
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # Rotation cancelled
    dilay = proj[1].thanLayerTree.dilay
    elemslays = [(elem, dilay[elem.thanTags[1]]) for elem in proj[2].thanSelall]
    selold = proj[2].thanSelold
    elems = proj[2].thanSelall

    res = proj[2].thanGudGetLayerleaf(T["Select new layer for the elements"])
    if res == Canc: return thanModCanc(proj)               # Rotation cancelled
    laynew = res

    __modChlayerDo(proj, elemslays, laynew)
    proj[1].thanDoundo.thanAdd("chlayer", thanundo.thanActionRedo, (elems, __modChlayerDo,           elemslays, laynew),
                                          thanundo.thanActionUndo, (elems, selold, __modChlayerUndo, elemslays, laynew))
    thanModEnd(proj)         # 'Reset color' has already been called and it is completely redundant and time consuming here (room for optimisation here)


def __modChlayerDo(proj, elemslays, laynew):
    "Changes the layer of selected elements; it actually does the job; implicitly assumes that elements were visible."
    import thanlayer
    proj[1].thanTouch()
    lays = {}
    for elem,lay in elemslays:
        tags = list(elem.thanTags)
        lay.thanQuad.remove(elem)
        laynew.thanQuad.add(elem)
        tags[1] = laynew.thanTag
        elem.thanTags = tuple(tags)
        lays.setdefault(lay, []).append(elem)
    if laynew.thanAtts["frozen"].thanVal:
        proj[2].thanGudSetSelDel()      # Deletes the canvas items, because the new layer is frozen
        proj[2].thanGudSetSelClear()    # Can't change frozen elements (if select previous is used)
        return
    assert len(lays) > 0, "How come that no layers were found, when there is at least one element????"
    draworder = False
    than = proj[2].than
    laynew.thanTkSet(than)         #Settings of the new layer for all the selected elements
    for lay, elems in lays.items(): #works for python2,3       # Find only the attributes which differ (and thus they must be changed)
        for a in thanlayer.thanlayatts.thanLayAttsNames[2:]: # We know that lay is NOT frozen (otherwise the elements could not be selected:) )
            nval = laynew.thanAtts[a].thanVal
            val = lay.thanAtts[a].thanAct
            if nval == val: continue
            if a == "moncolor":
                pass  # Optimisation: Since thanGudResetSelColor will be called, no need to change colour now
            elif a == "draworder":
                draworder = True
            elif a == "penthick":
                pass              # Nothing visible changes
            elif a == "linetype":
                proj[2].thanGudGetSelElemx(elems)    #Note: the settings of the new layer are already set
                proj[2].thanGudSetSelDashx(dash=than.dash)

    proj[2].thanGudSetSelLayertag(laynew.thanTag)
    proj[2].thanGudResetSelColor()
    proj[1].thanLayerTree.thanCur.thanTkSet(than)    #Restore settings of current layer
    if draworder: proj[2].thanRedraw()


def __modChlayerUndo(proj, elemslays, laynew):
    "UnChanges the layer of selected elements; implicitly assumes that elements were visible."
    import thanlayer
    proj[1].thanTouch()
    lays = {}
    for elem,lay in elemslays:
        tags = list(elem.thanTags)
        laynew.thanQuad.remove(elem)
        lay.thanQuad.add(elem)
        tags[1] = lay.thanTag
        elem.thanTags = tuple(tags)
        lays.setdefault(lay, []).append(elem)
    if laynew.thanAtts["frozen"].thanVal:    #Layer was frozen; so redraw elements
        proj[2].thanGudDrawElemsMany([elem for (elem,lay) in elemslays])
        return
    assert len(lays) > 0, "How come that no layers were found, when there is at least one element????"
    draworder = False
    than = proj[2].than
    for lay, elems in lays.items():#works for python2,3  # Find only the attributes which differ (and thus they must be changed)
        for a in thanlayer.thanlayatts.thanLayAttsNames[2:]:   # We know that lay is NOT frozen (otherwise the elements could not be selected:) )
            nval = laynew.thanAtts[a].thanVal
            val = lay.thanAtts[a].thanAct
            if nval == val: continue
            if a == "moncolor":
                pass  # Optimisation: thanGudResetSelColor will probably do the work faster
            elif a == "draworder":
                draworder = True
            elif a == "penthick":
                pass           # Nothing visible changes
            elif a == "linetype":
                lay.thanTkSet(than)    #Settings of the original layer that the element belonged to
                proj[2].thanGudGetSelElemx(elems)
                proj[2].thanGudSetSelDashx(dash=than.dash)

    dc = proj[2].thanCanvas
    for elem,lay in elemslays:
        titem = elem.thanTags[0]
        tags = list(dc.gettags(titem))
        tags[1] = lay.thanTag
        dc.itemconfig(titem, tags=tuple(tags))
    proj[2].thanGudResetSelColor()
    proj[1].thanLayerTree.thanCur.thanTkSet(than)    #Restore settings of current layer
    if draworder: proj[2].thanRedraw()

#=============================================================================

def thanModScale(proj):
    """Scales selected elements.

    FIXME: The limits (area iterated) of the visible drawing are probably changed
    as well. It must be checked.
    """
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # Scale was cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    c1 = proj[2].thanGudGetPoint(T["Origin of scale (Insertion point): "], options=("Insertion", ))
    if c1 == Canc: return thanModCanc(proj)                # Scale was cancelled
    #print("c1=", c1, type(c1))
    fact = 1.0
    fact = proj[2].thanGudGetPosFloat(T["Scale factor: "], fact)
    if fact == Canc: return thanModCanc(proj)              # Scale was cancelled

    __modScaleDo(proj, c1, fact)
    proj[1].thanDoundo.thanAdd("scale", thanundo.thanActionRedo, (elems,         __modScaleDo, c1, fact),
                                        thanundo.thanActionUndo, (elems, selold, __modScaleDo, c1, 1.0/fact))
    thanModEnd(proj)                                       # 'Reset color' is necessary here


def __modScaleDo(proj, cc, fact):
    "Scales selected elements; it actually does the job."
    import time       # thanScaleSel is called first, because thanGudSetSelScale calls thanautoregen to re-render the images
    t1 = time.time()
    t1 = time.time(); proj[1].thanScaleSel(proj[2].thanSelall, cc, fact) # ThanTouch is implicitly called
    t2 = time.time()
    if cc == "i": proj[2].thanGudSetSelScaleIns(fact)
    else:         proj[2].thanGudSetSelScale(cc[0], cc[1], fact)
    t3 = time.time()
    #print("Scale time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t3-t2, t2-t1, t3-t1))

#=============================================================================

def thanModMove(proj):
    "Moves selected elements."
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # Move was cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    stat1 = T["Destination or <enter>: "]
#    n = proj[1].thanVar["dimensionality"]
#    dc = [0.0] * n
    res = proj[2].thanGudGetPoint(T["Origin or Delta coordinates: "])
    if res == Canc: return thanModCanc(proj)               # Move was cancelled
    dc = res
    res = proj[2].thanGudGetMovend(dc, stat1, options=("",))
    if res == Canc: return thanModCanc(proj)               # Move was cancelled
    if res != "":
        for i in range(len(dc)): dc[i] = res[i] - dc[i]

    __modMoveDo(proj, dc)
    dcm = [-c for c in dc]
    proj[1].thanDoundo.thanAdd("move", thanundo.thanActionRedo, (elems,         __modMoveDo, dc),
                                       thanundo.thanActionUndo, (elems, selold, __modMoveDo, dcm))
    thanModEnd(proj)                                       # 'Reset color' is necessary here


def __modMoveDo(proj, dc):
    "Moves selected elements; it actually does the job."
    import time
    t1 = time.time(); proj[2].thanGudSetSelMove(dc[0], dc[1])
    t2 = time.time(); proj[1].thanMoveSel(proj[2].thanSelall, dc)   # thanTouch is implicitly called
    t3 = time.time()
    #print("Move time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t2-t1, t3-t2, t3-t1))


#=============================================================================

def thanModCopy(proj):
    "Copies selected elements."
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)                # Copy was cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold
    stat1 = T["Destination or <enter>: "]
    c1 = proj[2].thanGudGetPoint(T["Origin or Delta coordinates: "])
    if c1 == Canc: return thanModCanc(proj)                 # Copy was cancelled
    res = proj[2].thanGudGetMovend(c1, stat1, options=("",))
    if res == Canc: return thanModCanc(proj)                # Copy was cancelled
    if res == "":
        copelems = __modCopyDo(proj, elems, c1)
    else:
        dc = [b-a for a,b in zip(c1, res)]   #works for python2,3
        copelems = __modCopyDo(proj, elems, dc)
        while True:                                         # Copy multiple mode
            res = proj[2].thanGudGetMovend(c1, stat1, options=("",))
            if res == Canc or res == "": break              # Copy is ended
            dc = [b-a for a,b in zip(c1, res)]  #works for python2,3
            e1 = __modCopyDo(proj, elems, dc)
            copelems.extend(e1)

    proj[1].thanDoundo.thanAdd("copy", thanundo.thanReplaceRedo, ((), copelems, elems),
                                       thanundo.thanReplaceUndo, ((), copelems, selold))
    thanModEnd(proj)                       # 'Reset color' is necessary here


def __modCopyDo(proj, elems, dc):
    "Copies selected elements; it actually does the job."
    import time
    t1 = time.time(); copelems = proj[1].thanCopySel(elems, dc)   # thanTouch is implicitly called
    t2 = time.time(); proj[2].thanGudDrawElemsMany(copelems)
    t3 = time.time()
    #print("Move time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t3-t2, t2-t1, t3-t1))
    return copelems

#=============================================================================

def thanModOffset(proj):
    "Offsets elements (1 by 1 to be compatible with thAtCad - WARNING CODE NOT FINISHED."
    elems = set()
    selold = proj[2].thanSelall
    newelems = set()
    dis = disori = proj[1].thanVar["useroffsetdistance"]
    through = throughori = proj[1].thanVar["useroffsetthrough"]
    strd = proj[1].thanUnits.strdis
    elemun = True
    while True:
        if through:
            mes = T["Select element to offset or (offset Distance): "]
            elem = thancomsel.thanSelect1(proj, mes, options=("distance", ), filter=lambda e: e.thanOffset())
            if elem == Canc: return thanModCanc(proj)  # Offset cancelled
            if elem != "d": elemun=False; break
            through = False
            proj[2].thanGudSetSelRestore()             # Restores previous selection
        else:
            mes = "%s <%s>: " % (T["Specify offset distance or (Through point)"], strd(dis))
            dis = proj[2].thanGudGetPosFloat(mes, default=dis, options=("through",))
            if dis == Canc: return proj[2].thanGudCommandCan() # Offset cancelled (no thanModCanc here because no selection has been made)
            if dis != "t": break
            through = True
    while True:
        if elemun:
            elem = thancomsel.thanSelect1(proj, T["Select element to offset or <exit>: "],
                   options=("",), filter=lambda e: e.thanOffset())
            if elem == Canc or elem == "": break     # Offset cancelled or ended
        elemun = True
        if through:
            ct = proj[2].thanGudGetPoint(T["Specify through point: "])
            if ct == Canc: proj[2].thanPrtCan(); continue        # Offset of _this_ element was cancelled
            e = elem.thanOffset(through, None, ct)
        else:
            ct = proj[2].thanGudGetPoint(T["Specify point on side to offset: "])
            if ct == Canc: proj[2].thanPrtCan(); continue        # Offset of _this_ element was cancelled
            e = elem.thanOffset(through, dis, ct)
        if e is None:
            proj[2].thanCom.thanAppend(T["Invalid point or element can not be offset. Try again.\n"], "can")
            continue
        proj[1].thanElementAdd(e, proj[1].thanGetLayer(elem))
        proj[2].thanTkSet(elem)
        e.thanTkDraw(proj[2].than)
        elems.add(elem)
        newelems.add(e)

    proj[2].thanGudSetSelElem(elems)          # The original elements which were offset
    proj[2].thanGudSetSeloldElem(selold)      # The selection before the command offset started
    if len(newelems) == 0: return thanModCanc(proj)     # Offset cancelled
    proj[2].thanTkSet()       #Set current layer's settings
    newvars = {"useroffsetthrough":through}
    oldvars = {"useroffsetthrough":throughori}
    if not through:
        newvars["useroffsetdistance"] = dis
        oldvars["useroffsetdistance"] = disori
    proj[1].thanVar.update(newvars)   # Set new default only if user did not cancel
    proj[1].thanDoundo.thanAdd("offset", thanundo.thanReplaceRedo, ((), newelems, elems, newvars),
                                         thanundo.thanReplaceUndo, ((), newelems, selold, oldvars))
    thanModEnd(proj)       # 'Reset color' is not necessary here; room for optimization here

#=============================================================================

def thanModDDedit(proj):
    "Prompts the user to alter the text of a ThanText object."
    from thandr import ThanText, ThanPointNamed, ThanDimali, ThanBimColumn
    filt2 = lambda e: isinstance(e, (ThanText, ThanPointNamed, ThanDimali, ThanBimColumn))
    first = True
    while True:
        elem = thancomsel.thanSelect1(proj, T["Select text to edit: "], filter=filt2, options=("",))
        if elem == Canc or elem == "":
            if first: return thanModCanc(proj)            # DDedit cancelled
            else: break                                   # DDedit ended
        if isinstance(elem, ThanText):
            textold = elem.text
        elif isinstance(elem, (ThanPointNamed, ThanBimColumn)):
            textold = elem.name
        else:    #ThanDimali
            textold = elem.distext
        textnew = proj[2].thanGudGetText1(T["Edit text"], textDefault=textold)
        if textnew == Canc:
            proj[2].thanGudSetSelRestore()
            proj[2].thanPrtCan()
            continue                      # DDedit of this text was cancelled; ask for other
        elems = set((elem,))
        selold = proj[2].thanSelold

        __modDDeditDo(proj, elems, textnew)
        proj[1].thanDoundo.thanAdd("ddedit", thanundo.thanActionRedo, (elems,         __modDDeditDo, elems, textnew),
                                             thanundo.thanActionUndo, (elems, selold, __modDDeditDo, elems, textold))
        first = False
    proj[2].thanGudSetSelRestore()   #Reselect the most recent modified element
    if elem == Canc: thanModEnd(proj, "")    # If cancelled then goto the next line of the command window
    else:            thanModEnd(proj)        # If the user pressed enter, we are already on the next line


def __modDDeditDo(proj, elems, text):
    "Changes the text of the (single) selected element."
    from thandr import ThanText, ThanPointNamed, ThanDimali, ThanBimColumn
    for elem in elems: break
    if isinstance(elem, ThanText):
        #elem.thanSet(elem.cc, text, elem.validc)
        elem.thanRename(text)
    elif isinstance(elem, (ThanPointNamed, ThanBimColumn)):
        #elem.thanSet(elem.cc, text, elem.validc)
        elem.name = text
    else:    #ThanDimali
        elem.setText(text)
    proj[2].thanGudSetSelDel()                         # Delete the text from the canvas
    proj[2].thanTkSet(elem)                            # Set attributes of elem's layer
    elem.thanTkDraw(proj[2].than)                      # Draw the new text
    proj[2].thanTkSet()                                # Set attributes of current layer
    proj[2].thanGudSetSelElem1(elems)                  # Reselect the element (we deleted it)
    proj[1].thanTouch()

#=============================================================================

def thanModPoint(proj):
    "Prompts the user to alter the text/usability/Z of a named point."
    from thandr import ThanPointNamed
    first = True
    while True:
        elem = thancomsel.thanSelect1(proj, T["Select named point to edit: "], filter=lambda e: isinstance(e, ThanPointNamed), options=("",))
        if elem == Canc or elem == "":
            if first: return thanModCanc(proj)            # Point edit cancelled
            else: break                                   # Point edit ended
        attsnew = __pointgetnewatts(proj, elem)
        if attsnew[0] == Canc:
            proj[2].thanGudSetSelRestore()
            proj[2].thanPrtCan()
            continue                   # Edit of this point was cancelled; ask for other
        attsold = elem.cc[2], elem.name, list(elem.validc)
        elems = set((elem,))
        selold = proj[2].thanSelold
        __modPointDo(proj, elems, attsnew)
        proj[1].thanDoundo.thanAdd("poedit", thanundo.thanActionRedo, (elems,         __modPointDo, elems, attsnew),
                                             thanundo.thanActionUndo, (elems, selold, __modPointDo, elems, attsold))
        first = False
    proj[2].thanGudSetSelRestore()   #Reselect the most recent modified element
    if elem == Canc: thanModEnd(proj, "")    # If cancelled then goto the next line of the command window
    else:            thanModEnd(proj)        # If the use pressed enter, we are already on the next line


def __pointgetnewatts(proj, elem):
    "Prompt the use to edit Z, name or usability of the named point."
    cvis = T["Coordinate usability (for DTM, etc)"]
    strd = proj[1].thanUnits.strdis
    z, name, validc = elem.cc[2], elem.name, list(elem.validc)
    while True:
        statonce = "Name=%s   %s: X=%r Y=%r Z=%r\n" % (name, cvis, validc[0], validc[1], validc[2])
        res = proj[2].thanGudGetFloat(T["New Z or (change Name/toggle X/toggle Y/toggle Z) <enter=%s>: " % strd(z)],
            default=z, statonce=statonce, options=("Name", "X", "Y", "Z"))
        if res == Canc:
            return Canc, Canc, Canc                    # Point cancelled
        if res == "n":
            res = proj[2].thanGudGetText0(T["New point name (enter=%s): "]%name, default=name)
            if res != Canc: name = res
        elif res in ("x", "y", "z"):
            i = "xyz".index(res)
            validc[i] = not validc[i]
        else:
            z = res
            return z, name, validc


def __modPointDo(proj, elems, atts):
    "Changes attributes of points; it actually does the job."
    for elem in elems: break
    elem.cc[2] = atts[0]
    elem.thanSet(elem.cc, atts[1], atts[2])
    proj[2].thanGudSetSelDel()                         # Delete the text from the canvas
    proj[2].thanTkSet(elem)                            # Set attributes of elem's layer
    elem.thanTkDraw(proj[2].than)                      # Draw the new text
    proj[2].thanTkSet()                                # Set attributes of current layer
    proj[2].thanGudSetSelElem1(elems)                  # Reselect the element (we deleted it)
    proj[1].thanTouch()

#=============================================================================

def thanModErase(proj):
    "Erases selected elements."
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)               # Erase was cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold
    __modEraseDo(proj)
    proj[1].thanDoundo.thanAdd("erase", thanundo.thanReplaceRedo, (elems, set(), set()),
                                        thanundo.thanReplaceUndo, (elems, set(), selold))
    thanModEnd(proj)            # 'Reset color' is completely unnecessary here, and it will slow..
                                # ..the command down. Room for optimisation here.


def thanModErasenew(proj):  #THIS FUNCTIONALITY MUST BE ADDED AT thanSelectGen() and thanSelectOr()
    "Erases selected elements, 2017_10_13: adds the 'all' option."
    while True:
        res = thancomsel.thanSelectOr(proj, standalone=False, optionname="all", optiontext="a=All")
        if res == Canc: return thanModCanc(proj)               # Erase was cancelled
        if res == "a":
            #1. Select all the elements in selall all the elemnts of the drawing
            #2. change color of all elementes currently drawn and assign selxxx to them
            #3.   ....
            pass
        else:
            break
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold
    __modEraseDo(proj)
    proj[1].thanDoundo.thanAdd("erase", thanundo.thanReplaceRedo, (elems, set(), set()),
                                        thanundo.thanReplaceUndo, (elems, set(), selold))
    thanModEnd(proj)            # 'Reset color' is completely unnecessary here, and it will slow..
                                # ..the command down. Room for optimisation here.

def __modEraseDo(proj):
    "Erases selected elements; it actually does the job."
    import time
    t1 = time.time()
    proj[2].thanGudSetSelDel()
    proj[2].thanImages.difference_update(proj[2].thanSelall) #Delete deleted images from thanImages
    t2 = time.time(); proj[1].thanDelSel(proj[2].thanSelall) #thanTouch is implicitly called
    t3 = time.time()
    #print("Erase time: canvas=%.2f   elements=%.2f   sum=%.2f (secs)" % (t2-t1, t3-t2, t3-t1))
    proj[2].thanGudSetSelClear()

#=============================================================================

def thanModPurge(proj):
    "Purges unused declarations; for the moment unused layer and objects."
    ans = proj[2].thanGudGetOpts(T["Purge [Layers/Objects/Do-undo history] <L>: "], default="Layers",
        options="Layers/Objects/Doundo".split("/"))
    if ans == Canc: return proj[2].thanGudCommandCan()  # user cancelled purge
    elif ans == "l": return thanModPurgelay(proj)
    elif ans == "d": return __purgeDoundo(proj)
    else:            return __purgeobjects(proj)


def __purgeobjects(proj):
    "Purges (unused) objects."
    mes = { False: T["Delete %s (enter=no): "],
            True : T["Delete %s (enter=yes): "]
          }
    ansdef = False
    delyes = []
    purgeable = False
    for name, objs in proj[1].thanObjects.items():   #works for python2,3
        for i,obj in enumerate(objs):
            purgeable = True
            more = ""
            if i > 0: more = " (%d)" % (i+1,)
            ans = proj[2].thanGudGetYesno(mes[ansdef] % (obj.thanObjectInfo+more,), default=ansdef)
            if ans == Canc: return proj[2].thanGudCommandCan()  # user cancelled purge
            if ans: delyes.append((name, obj))
            ansdef = ans
    if len(delyes) == 0:
        proj[1].thanDoundo.thanAdd("purge", p_ggen.doNothing, (),
                                            p_ggen.doNothing, ())
        if not purgeable: mes = T["No defined/unused objects."]
        else:             mes = T["No objects were purged."]
        return proj[2].thanGudCommandEnd(mes)
    addobjs = []
    thanundo.thanObjsRestore(proj, delyes, addobjs)
    proj[1].thanDoundo.thanAdd("purge", thanundo.thanObjsRestore, (delyes, addobjs),
                                        thanundo.thanObjsRestore, (addobjs, delyes))
    proj[1].thanTouch()         # Drawing was changed
    proj[2].thanGudCommandEnd() # thanModEnd() does not carry a benefit here; no elements were selected.


def thanModPurgelay(proj):
    "Purges unused declarations; for the moment unused layer declarations (but not the current and its parents)."
    lt = proj[1].thanLayerTree
    cl, newRoot = thanundo.thanLtClone(proj)

    cl.thanQuad.add(None)         # Make current layer non Empty
    delnot = set((newRoot, newRoot.thanChildren[0]))   # Layers which must not be deleted
    delyes = set()                # Layers that are going to deleted
    try:                   purgeable = __purgeLay(proj, newRoot, delnot, delyes)
    except ThanLayerError:
        cl.thanQuad.remove(None)            #New cl gets a reference to thanQuad, so this is NECESSARY
        return proj[2].thanGudCommandCan()  #user cancelled purge
    if len(delyes) == 0:
        proj[1].thanDoundo.thanAdd("purge", p_ggen.doNothing, (),
                                            p_ggen.doNothing, ())
        if not purgeable: mes = T["No unused layers (current layer can not be purged)."]
        else:             mes = T["No layers were purged."]
        cl.thanQuad.remove(None)            #New cl gets a reference to thanQuad, so this is NECESSARY
        return proj[2].thanGudCommandEnd(mes)
    for chlay in delyes:
        lay = chlay.thanParent
        chlay.thanUnlink()        # remove chlay and hierarchy from parent's children
        chlay.thanDestroy()       # Delete chlay and hierarchy
        if len(lay.thanChildren) == 0:  # This is leaf layer now; it can hold elements
            lay.thanQuad = set()
            lay.thanTag = lay.lt.thanIdLay.new()  # In order to exploit TK mechanism
    cl.thanQuad.remove(None)
    oldCl = lt.thanCur
    oldRoot = lt.thanRoot
    thanundo.thanLtRestore(proj, cl, newRoot)
    proj[1].thanDoundo.thanAdd("purge", thanundo.thanLtRestore, (cl, newRoot),
                                        thanundo.thanLtRestore, (oldCl, oldRoot))
    proj[2].thanGudCommandEnd()   # thanModEnd() does not carry a benefit here; no elements were selected..


def __purgeLay(proj, lay, delnot, delyes):
    "Ask recursively the empty layers to be deleted."
    emptyFound = False
    ansdef = False
    mes = { False: T["Delete empty layer %s (enter=no): "],
            True : T["Delete empty layer %s (enter=yes): "]
          }
    for chlay in lay.thanChildren:
        if chlay in delnot: continue           # These layers can not be deleted
        if not chlay.thanIsEmpty(): continue   # Layer not empty
        emptyFound = True
        ans = proj[2].thanGudGetYesno(mes[ansdef] % chlay.thanGetPathname(), default=ansdef)
        if ans == Canc: raise ThanLayerError("User cancelled purge")
        if ans: delyes.add(chlay)
        ansdef = ans
    for chlay in lay.thanChildren:
        if chlay in delyes: continue           # Already marked for deletion
        emptyFound1 = __purgeLay(proj, chlay, delnot, delyes)
        emptyFound = emptyFound or emptyFound1
    return emptyFound


def __purgeDoundo(proj):
    "Purge do/undo history."
    if thanundo.thanRetainUndo(proj): return proj[2].thanGudCommandCan() # User cancelled purge
    proj[2].thanGudCommandEnd(T["Do/undo history has been purged."], "info")

#=============================================================================

def thanModChelev(proj):
    "Change the elevation of z dimension of elements."
    nd = proj[1].thanVar["dimensionality"]
    assert nd > 2, "Well, this should be ThanCad with limited n-dimensional support!"
    if nd > 3:
        proj[2].thanPrt(T["This drawing has %d dimensions. The elevation"] % nd)
        proj[2].thanPrt(T["of dimensions higher than 3 are set with the CHELEVN command."])
    c = proj[1].thanVar["elevation"]          # Reference to the elevation list
    sd = proj[1].thanUnits.strdis
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)  # chelev was cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    stat = "%s%s): " % (T["New elevation (enter="], sd(c[2]))
    z = proj[2].thanGudGetFloat(stat, c[2])
    if z == Canc: return thanModCanc(proj)

    newelems = set()
    for e in elems:
        en = e.thanClone()
        en.thanChelev(z)
        newelems.add(en)
    thanundo.thanReplaceRedo(proj, elems, newelems, newelems)
    proj[1].thanDoundo.thanAdd("chelev", thanundo.thanReplaceRedo, (elems, newelems, newelems),
                                         thanundo.thanReplaceUndo, (elems, newelems, selold))
    thanModEnd(proj)            # 'Reset color' is completely unnecessary here, and it will slow..
                                # ..the command down. Room for optimisation here.

def thanModChelevn(proj):
    "Change the elevation of z and higher dimensions of elements."
    nd = proj[1].thanVar["dimensionality"]
    assert nd > 2, "Well, this should be ThanCad with limited n-dimensional support!"
    if nd < 4:
        proj[2].thanPrt(T["This drawing has only %d dimensions. The elevation"] % nd)
        proj[2].thanPrt(T["of dimension z can also be set with the CHELEV command."])
    c = proj[1].thanVar["elevation"]          # Reference to the elevation list
    sd = proj[1].thanUnits.strdis
    res = thancomsel.thanSelectGen(proj, standalone=False)
    if res == Canc: return thanModCanc(proj)   # chelevn cancelled
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold
    t = ",".join(sd(c[j]) for j in range(2, nd))
    stat = "%s%s): " % (T["New elevations of z and higher dimensions (enter="], t)
    cz = proj[2].thanGetElevations(nd, stat, c[2:])
    if cz == Canc: return thanModCanc(proj)

    newelems = set()
    for e in elems:
        en = e.thanClone()
        en.thanChelevn(cz)
        newelems.add(en)
    thanundo.thanReplaceRedo(proj, elems, newelems, newelems) #Room for optimisation here.
    proj[1].thanDoundo.thanAdd("chelevn", thanundo.thanReplaceRedo, (elems, newelems, newelems),
                                          thanundo.thanReplaceUndo, (elems, newelems, selold))
    thanModEnd(proj)
