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
This module processes photogrammetry related commands.
"""

from math import hypot, atan2
from tkinter.messagebox import ERROR
from p_gmath import thanSegSeg, thanNear2
import p_ggen, p_gtkwid
from thantrans import Tphot, T
from thanvar import Canc
import thandr, thanobj
from thanprophoto import thanprotkdia
from thansupport import thanToplayerCurrent
from thanopt import thancadconf
from thandefs import ThanImageMissing


mm = p_gtkwid.thanGudModalMessage

def thanPhotF6(proj): proj[2].thanCom.thanOnF6(None)
def thanPhotF7(proj): proj[2].thanCom.thanOnF7(None)


def thanPhotImage(proj, insertmode="p"):
    "Draws an element with the help of a GUI and stores it to database."
    from thancom import thanundo
    dimitra(proj, "interior")
    im, terr, nim = thanFindImage(proj)
    if nim > 0:
        ret1 = p_gtkwid.thanGudAskOkCancel(proj[2],
        Tphot["1 or more images are already present.\n\nOK to replace?"], T["Warning"])
        if not ret1: return proj[2].thanGudCommandCan()

    elem = thandr.ThanImage()
    ret = elem.thanTkGet(proj, insertmode=insertmode)      # insert image with units in mm or pixels
    if ret == Canc: return proj[2].thanGudCommandCan()     # insert was cancelled

    oldcl, oldroot = thanundo.thanLtClone(proj)   # This is not needed if no layers are created, but for simplicity...
    lay, terr = __crlayer(proj, "photogrammetry/raster", moncolor="red", draworder=500)
    if lay is None: return proj[2].thanGudCommandCan(terr)

    delelems = []
    if nim > 0:
        delelems = [e for e in lay.thanQuad if isinstance(e, thandr.ThanImage)]
        proj[1].thanElementDelete(delelems, proj)

    proj[1].thanElementAdd(elem, lay)                   # thanTouch is implicitely called
    lay.thanTkSet(proj[2].than)
    elem.thanTkDraw(proj[2].than)
    lt = proj[1].thanLayerTree
    lt.thanCur.thanTkSet(proj[2].than)

    v = proj[1].viewPort
    oldport = list(v)
    v[:] = proj[2].thanGudZoomWin(elem.getBoundBox())   # Zoom to show the entire image
    proj[2].thanAutoRegen(regenImages=True)

    newelems = (elem,)
    proj[1].thanDoundo.thanAdd("photimage", __photImageRedo, (lt.thanCur, lt.thanRoot, delelems, newelems, list(v), (), ()),
                                            __photImageUndo, (oldcl,       oldroot,    delelems, newelems, oldport, (), ()))
    proj[2].thanGudCommandEnd()


def __photImageRedo(proj, newcl, newroot, delelems, newelems, newport, newobjs, oldobjs):
    "Redoes new layers, new elements and zooms (with this order)."
    from thancom import thanundo
    thanundo.thanLtRestore(proj, newcl, newroot)
    thanundo.thanReplaceRedo(proj, delelems, newelems)
    thanundo.thanObjsRestore(proj, oldobjs, newobjs)
    proj[1].viewPort[:] = proj[2].thanGudZoomWin(newport)
    proj[2].thanAutoRegen(regenImages=True)


def __photImageUndo(proj, oldcl, oldroot, delelems, newelems, oldport, newobjs, oldobjs):
    "Undoes new elements and new layers and unzooms (with this order)."
    from thancom import thanundo
    thanundo.thanReplaceUndo(proj, delelems, newelems)
    thanundo.thanLtRestore(proj, oldcl, oldroot)
    thanundo.thanObjsRestore(proj, newobjs, oldobjs)
    proj[1].viewPort[:] = proj[2].thanGudZoomWin(oldport)
    proj[2].thanAutoRegen(regenImages=True)


def thanPhotCosys(proj):
    "Defines an internal orientation coordinate system."
    from thancom import thanundo
    def __can():
        proj[2].thanCanvas.delete("e0")
        proj[2].thanGudCommandCan()

    dimitra(proj, "interior")
    c1 = proj[2].thanGudGetPoint(Tphot["First (left) point of x-axis: "])
    if c1 == Canc: return __can()         # cosys cancelled
    while True:
        c2 = proj[2].thanGudGetLine(c1, Tphot["Second (right) point of x-axis: "])
        if c2 == Canc: return __can()     # cosys cancelled
        if not thanNear2(c1, c2): break
        proj[2].thanPrter(Tphot["Points of x-axis are identical. Try again."])
    elemx = __crarrow(c1, c2)
    elemx.thanTkDraw(proj[2].than)

    while True:
        c3 = proj[2].thanGudGetPoint(Tphot["First (down) point of y-axis: "])
        if c3 == Canc: return __can()     # cosys cancelled
        while True:
            c4 = proj[2].thanGudGetLine(c3, Tphot["Second (up) point of y-axis: "])
            if c4 == Canc: return __can() # cosys cancelled
            if not thanNear2(c3, c4): break
            proj[2].thanPrter(Tphot["Points of y-axis are identical. Try again."])
        if thanSegSeg(c1, c2, c3, c4) is not None: break
        proj[2].thanPrter(Tphot["Y-axis does intersect x-axis (without extension). Try again."])
    elemy = __crarrow(c3, c4)
    proj[2].thanCanvas.delete("e0")

    cosys = thanobj.NonCartesian()
    ok, terr = cosys.from4(c1, c2, c3, c4)
    if not ok:
        s = "%s:\n" % (Tphot["Interior orientation system was not defined"], terr)
        return thanGudCommandCan(s)

    oldcl, oldroot = thanundo.thanLtClone(proj)   # This is not needed if no layers are created, but for simplicity...
    lay, terr = __crlayer(proj, "photogrammetry/axes", moncolor="red")
    if lay is None: return proj[2].thanGudCommandCan(terr)
    oldcosyses = proj[1].thanObjects["COSYS"][:]
    proj[1].thanObjects["COSYS"][:] = [cosys]
    proj[2].thanStatusBar.thanConfig(typ="image", every="move")

    proj[1].thanElementAdd(elemx, lay)                   # thanTouch is implicitely called
    lay.thanTkSet(proj[2].than)
    elemx.thanTkDraw(proj[2].than)
    proj[1].thanElementAdd(elemy, lay)                   # thanTouch is implicitely called
    elemy.thanTkDraw(proj[2].than)
    lt = proj[1].thanLayerTree
    lt.thanCur.thanTkSet(proj[2].than)

    newelems = (elemx, elemy)
    proj[1].thanDoundo.thanAdd("photimage", __photCosysRedo, (lt.thanCur, lt.thanRoot, newelems, [cosys]),
                                            __photCosysUndo, (oldcl,       oldroot,    newelems, oldcosyses))
    proj[2].thanGudCommandEnd(Tphot["Interior orientation system was defined successfuly."])


def __photCosysRedo(proj, newcl, newroot, newelems, newcosyses):
    "Redoes new layers, new elements and zooms (with this order)."
    from thancom import thanundo
    thanundo.thanLtRestore(proj, newcl, newroot)
    thanundo.thanReplaceRedo(proj, (), newelems)
    proj[1].thanObjects["COSYS"][:] = newcosyses
    proj[2].thanStatusBar.thanConfig(typ="image", every="move")


def __photCosysUndo(proj, oldcl, oldroot, newelems, oldcosyses):
    "Undoes new elements and new layers and unzooms (with this order)."
    from thancom import thanundo
    thanundo.thanReplaceUndo(proj, (), newelems)
    thanundo.thanLtRestore(proj, oldcl, oldroot)
    proj[1].thanObjects["COSYS"][:] = oldcosyses


def __crarrow(ca, cb, size=10.0):
    "Create a line with an arrow."
    d = hypot(cb[0]-ca[0], cb[1]-ca[1])
    phi = atan2(cb[1]-ca[1], cb[0]-ca[0])
    cc = []
    for dx, dy in [(0.0, 0.0),
                   (d,   0.0),
                   (d-size, size/4.0),
                   (d-size, -size/4.0),
                   (d, 0.0),]:
        ct = list(ca)
        ct[0] += dx
        ct[1] += dy
        cc.append(ct)
    elem = thandr.ThanLine()
    elem.thanSet(cc)
    elem.thanRotateSet(ca, phi)
    elem.thanRotate()
    elem.thanTags = ("e0",)
    return elem


def __crlayer(proj, layname, moncolor, draworder=None):
    "Create, make current and set color of layer if it does not exist; else make current."
    from thancom import thanundo
    oldcl, oldroot = thanundo.thanLtClone(proj)
    lt = proj[1].thanLayerTree
    atts = {"moncolor":moncolor}
    if draworder is not None: atts["draworder"] = draworder
    try:
        lay = lt.thanFindic(layname)
        if lay is None:
            lay = thanToplayerCurrent(proj, layname, current=False, **atts)
        else:
            lay = thanToplayerCurrent(proj, layname, current=False)
        return lay, ""
    except Exception as why:
        terr = ["%s %s/%s:" % (Tphot["Could not create/access layer"], "photogrammetry", layname),
                str(why),
                Tphot["Please create a new drawing and try again."],
               ]
        return None, "\n".join(terr)


def thanPhotTranspose(proj, comname, transpose):
    "Rotates the image counterclockwise 0, 90, 180, 270 degrees."
    dimitra(proj, "interior")
    e, terr, _ = thanFindImage(proj)
    if e is None: return proj[2].thanGudCommandCan(terr)
    if transpose == 0: return proj[2].thanGudCommandEnd()   #Nothing to do
    tran_rev = transpose                                    #Reverse transpose
    if transpose != 2: tran_rev = (transpose+2) % 4         #Reverse transpose
    proj[2].thanCom.thanAppend("Rotating image..")
    __transposeDo(proj, e, transpose)
    proj[1].thanDoundo.thanAdd(comname, __transposeDo, (e, transpose),
                                        __transposeDo, (e, tran_rev))
    proj[1].thanTouch()
    proj[2].thanGudCommandEnd("")


def __transposeDo(proj, e, tran):
    "Transpose the image; do the job."
    e.thanTranspose(tran)
    proj[2].thanAutoRegen(regenImages=True)


__dim = set()
def dimitra(proj, icom):
    if icom in __dim: return
    __dim.add(icom)
    pr = proj[2].thanPrtbo
    if icom == "interior":
        pr("Photogrammetry, Dimitra Vassilaki, PhD Candidate", "info")
        pr("Lab of Photogrammetry, NTUA, 2010-2015", "info")


def thanPhotCamera(proj):
    "Display the camera management dialog."
    w = thanprotkdia.ThanCamera(proj[2], vals=None, cargo=proj)
    if w.result is None: return proj[2].thanGudCommandCan()
    proj[2].thanGudCommandEnd()


def thanPhotIntcamera(proj):
    "Open, read and check a photogrammetric camera file."
    from thancom import thanundo
    from thancom.thancomfile import thanTxtopen
    im, terr = __getimage(proj)
    if im is None: return proj[2].thanGudCommandCan(terr)
    iors = proj[1].thanObjects["PHOTINTERIOR"]
    if len(iors) > 0:
        cam = iors[0].getCamera()
        if cam is not None:
            ret2 = p_gtkwid.thanGudAskOkCancel(proj[2],
            Tphot["A camera file is already loaded. "\
            "If a new camera file is loaded, "\
            "any previous computations will probably become invalid "\
            "and must be redone.\n\nOK to load new camera file?"], T["Warning"])
            if not ret2: return proj[2].thanGudCommandCan()

    idir = thancadconf.thanCameradir
    while True:
        filnam, fr = thanTxtopen(proj, Tphot["Choose Photogrammetric camera file to open"],
            suf=".cam", initialdir=idir)
        if fr == Canc: return proj[2].thanGudCommandCan()
        v, terr = __checkCam(fr)
        fr.close()
        idir = filnam.parent
        if v is not None: break
        mm(proj[2], "%s:\n\n%s" % (fr.name, terr),
            "%s - %s" % (proj[0], Tphot["Camera file"]), ERROR)
    thancadconf.thanCameradir = idir

    if len(iors) == 0: ior = thanobj.ThanPhotInterior()
    else:              ior = iors[0].thanClone()
    ior.setImage(im)
    ior.setCamera(v)
    newobjs = [("PHOTINTERIOR", ior)]
    oldobjs = []
    if len(iors) > 0: oldobjs = [("PHOTINTERIOR", iors[0])]
    thanundo.thanObjsRestore(proj, oldobjs, newobjs)
    proj[1].thanDoundo.thanAdd("photintimage", thanundo.thanObjsRestore, (oldobjs, newobjs),
                                               thanundo.thanObjsRestore, (newobjs, oldobjs))
    proj[2].thanGudCommandEnd(Tphot["Camera file was successfuly loaded."])


def __getimage(proj):
    "Try to load the image and report errors."
    im, terr, _ = thanFindImage(proj)
    if im is None: return None, terr
    iors = proj[1].thanObjects["PHOTINTERIOR"]
    if len(iors) > 0:
        imi = iors[0].getImage()
        if imi is not None and im != imi:
            ret1 = p_gtkwid.thanGudAskOkCancel(proj[2],
            Tphot["ThanCad found that the image was changed. "\
            "Any previous computations have probably become invalid and must be redone.\n\n"
            "OK to continue?"], T["Warning"])
            if not ret1: return None, None
    return im, ""


def __checkCam(fr):
    """Read and check that camera file is OK.

    Structure of camera: v = Struct():
    v.name: camera name as string
    v.x[], v.y[]: coordinates of fiducials as floats.
    """
    v = p_ggen.Struct()
    try:
        v.name = next(fr).strip()
        if v.name.strip() == "": return None, Tphot["Blank camera name"]
        try: v.focus = float(next(fr))
        except ValueError: return None, Tphot["Syntax error while reading focus length"]
        if v.focus < 0.001 or v.focus > 1000.0: return None, Tphot["Invalid focus length"]
    except StopIteration:
        return None, Tphot["Incomplete camera file"]
        mm(proj[2], "%s:\n\n%s" % (fr.name, why), why, ERROR)   # (Gu)i (d)ependent
    v.x = []
    v.y = []
    for dline in fr:
        try: x1, y1 = map(float, dline.split())   #works for python2,3
        except (ValueError, IndexError): return None, Tphot["Syntax error while reading fiducial coordinates"]
        v.x.append(x1)
        v.y.append(y1)
    if len(v.x) < 3: return None, Tphot["At least 3 fiducials should be given"]
    return v, ""


def thanPhotInterior(proj):
    "Display the dialog for computing photogrammetric interior orientation."
    from thancom import thanundo
    im, terr = __getimage(proj)
    if im is None: return proj[2].thanGudCommandCan(terr)
    iors = proj[1].thanObjects["PHOTINTERIOR"]
    if len(iors) == 0 or iors[0].getCamera() is None:
        return proj[2].thanGudCommandCan(Tphot["Please load a photogrammetric camera file and retry."])
    assert iors[0] is not None

    v = proj[1].viewPort
    oldport = list(v)
    oldcl, oldroot = thanundo.thanLtClone(proj)   # This is not needed if no layers are created, but for simplicity...
    lay, terr = __crlayer(proj, "photogrammetry/fiducials", moncolor="red")
    if lay is None: return proj[2].thanGudCommandCan(terr)   #Laters could not be created
    lt = proj[1].thanLayerTree
    lay.thanTkSet(proj[2].than)

    ior = iors[0].thanClone()
    ior.setImage(im)
    delelems, newelems = ior.replacePoints(proj, lay)
    vals, other = ior.toDialog()
    other.lay = lay
    other.newelems = newelems
    w = thanprotkdia.ThanInterior(proj[2], vals, proj, Tphot, other)
    if w.result is None:                         #Interior cancelled
        thanundo.thanReplaceUndo(proj, delelems, list(newelems.values()))    #works for python2,3
        thanundo.thanLtRestore(proj, oldcl, oldroot)   #It also calls thanTkSet for current layer
        proj[1].viewPort[:] = proj[2].thanGudZoomWin(oldport)
        proj[2].thanAutoRegen(regenImages=True)
        return proj[2].thanGudCommandCan()
    ior.fromDialog(w.result, w.other)
    proj[1].thanObjects["PHOTINTERIOR"][:] = [ior]
    lt.thanCur.thanTkSet(proj[2].than)

    newelems = list(w.other.newelems.values())   #works for python2,3
    oldobjs = [("PHOTINTERIOR", iors[0])]
    newobjs = [("PHOTINTERIOR", ior)]
    proj[1].thanDoundo.thanAdd("photinterior", __photImageRedo, (lt.thanCur, lt.thanRoot, delelems, newelems, list(v), oldobjs, newobjs),
                                               __photImageUndo, (oldcl,      oldroot,     delelems, newelems, oldport, oldobjs, newobjs))
    proj[2].thanGudCommandEnd()


def thanFindImage(proj):
    "Try to find an image in layer 'photogrammetry/raster'."
    terr = Tphot["Please insert an image and retry."]
    lay = proj[1].thanLayerTree.thanFindic("photogrammetry/raster")
    if lay is None: return None, terr, 0
    ims = []
    for e in lay.thanQuad:
        if isinstance(e, thandr.ThanImage): ims.append(e)
    if len(ims) == 0: return None, terr, 0
    if len(ims) > 1: return None, Tphot["Multiple (%d) images were found. Please delete all but one."] % len(ims), len(ims)
    e = ims[0]
    if isinstance(e.image, ThanImageMissing):
        return None, Tphot["The raster file of the image is missing.\nPlease "\
                     "use 'imagelocate' or imagedirectory' to locate it."], 1
    return e, "", 1


def thanPhotModel(proj):
    "Display the dialog which defines the photogrammetric model."
    from thancom import thanundo
    phs = proj[1].thanObjects["PHOTMODEL"]
    vals = None
    if len(phs) > 0 and phs[0].model is not None: vals = phs[0].model2dialog()
    w = thanprotkdia.ThanModel(proj[2], vals=vals, cargo=proj)
    v = w.result
    if v is None: return proj[2].thanGudCommandCan()
    phot = thanobj.ThanPhotModel(model=v)
    newobjs = [("PHOTMODEL", phot)]
    oldobjs = [("PHOTMODEL", phs[0])]
    thanundo.thanObjsRestore(proj, oldobjs, newobjs)
    proj[1].thanDoundo.thanAdd("purge", thanundo.thanObjsRestore, (oldobjs, newobjs),
                                        thanundo.thanObjsRestore, (newobjs, oldobjs))
    proj[2].thanGudCommandEnd(Tphot["Photogrammetric model was defined successfuly."])
