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
This module processes file related commands.
"""

import bz2, copy, tkinter
try: import xlwt          #Hopefully py2exe and cxFreeze get the hint to include xlwt
except ImportError: pass

from p_ggen import path, doNothing, ThanImportError, thanGetEncoding
import p_gtkwid, p_ggeod
import thandwg, thanimp, thanexp, thantkdia, thanvers, thandr
import thanopt, thanlayer
from thantrans import T
from thanvar import Canc, thanfiles
from . import thancomview, thanrwf, thancomsel, thanundo
from .thancommod import thanModCanc, thanModEnd

mm = p_gtkwid.thanGudModalMessage


def thanFileNew(proj):
    "Creates a new drawing and its drawing window."
    projnew = thanFileNewDo(proj)
    proj[2].thanGudCommandEnd(T["New drawing has been created."], "info")
    projnew[2].thanGudCommandEnd()


def thanFileNewDo(proj, mes=None):
    "Creates a new drawing and its drawing window - does the job."
    import thantkgui
    fpath = thanfiles.tempname()
    dr = thandwg.ThanDrawing()
    win = thantkgui.ThanTkGuiWinDraw()
    projnew = win.setDrawing(fpath, dr)
    thanfiles.fillMenu(projnew)
    thanfiles.addOpened(projnew)
    projnew[2].thanTkSetFocus()
    return projnew

#=============================================================================

_importClass = { ".dxf": ("Drawing Interchange",     thanimp.ThanImportDxf),
                 ".syk": ("2D Lines with Elevation", thanimp.ThanImportSyk),
                 ".brk": ("3D Lines",                thanimp.ThanImportBrk),
                 ".syn": ("Topographic Points",      thanimp.ThanImportSyn),
                 ".lin": ("Linicad Drawing",         thanimp.ThanImportLin),
                 ".lcad":("Linicad Drawing",         thanimp.ThanImportLcad),
                 ".xyz": ("3D Lines, Intermap xyz format", thanimp.ThanImportXyzIntermap),
                 ".kml": ("Google KML 3D points (placemarks)", thanimp.ThanImportKml),
                 ".kmz": ("Compressed Google KML 3D points (placemarks)", thanimp.ThanImportKmz),
               }
_ser = ".dxf .syk .brk .syn .kml .kmz .xyz .lcad .lin".split()
if thanopt.thancon.thanFrape.civil:
    import thanprocivil
    from thanprocivil.thanproimp import ThanImportMhk
    _importClass[".mhk"] = ("Highway Profile", ThanImportMhk)
    _ser.append(".mhk")
_exts = [(_importClass[suf][0], suf) for suf in _ser]
del _ser
_exts.insert(0, ("ThanCad xml", ".thcx"))
_exts.append(("All Files", "*"))


def thanFileOpenSpreadPoints(proj):
    "Opens one or more spreadsheet files, which contain points."
    _spreadClass = { #".ods": ("LibreOffice points",thanimp.ThanImportOdsPoints),
                     ".xls": ("Excel points",      thanimp.ThanImportXlsPoints),
                     ".xlsx":("Excel points",      thanimp.ThanImportXlsPoints),
                   }
    _ser = ".xls .xlsx".split()
    exts = [(_spreadClass[suf][0], suf) for suf in _ser]
    del _ser

    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkwid.thanGudGetReadFile(proj[2], exts, T["Choose files to open"],
                 initialdir=fildir, multiple=True)
        if fns is None: return proj[2].thanGudCommandCan()     # Open cancelled
        nopened = thanFileOpenPaths(proj, fns, _spreadClass)
        if nopened > 0: return proj[2].thanGudCommandEnd()


def thanFileOpenSpreadLines(proj):
    "Opens one or more spreadsheet files, which contain lines."
    _spreadClass = { #".ods": ("LibreOffice points",thanimp.ThanImportOdsPoints),
                     ".xls": ("Excel lines",      thanimp.ThanImportXlsLines),
                     ".xlsx":("Excel lines",      thanimp.ThanImportXlsLines),
                   }
    _ser = ".xls .xlsx".split()
    exts = [(_spreadClass[suf][0], suf) for suf in _ser]
    del _ser

    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkwid.thanGudGetReadFile(proj[2], exts, T["Choose files to open"],
                 initialdir=fildir, multiple=True)
        if fns is None: return proj[2].thanGudCommandCan()     # Open cancelled
        nopened = thanFileOpenPaths(proj, fns, _spreadClass)
        if nopened > 0: return proj[2].thanGudCommandEnd()


def thanFileOpenSpreadTexts(proj):
    "Opens one or more spreadsheet files, which contain lines."
    _spreadClass = { #".ods": ("LibreOffice points",thanimp.ThanImportOdsPoints),
                     ".xls": ("Excel texts",      thanimp.ThanImportXlsTexts),
                     ".xlsx":("Excel texts",      thanimp.ThanImportXlsTexts),
                   }
    _ser = ".xls .xlsx".split()
    exts = [(_spreadClass[suf][0], suf) for suf in _ser]
    del _ser

    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkwid.thanGudGetReadFile(proj[2], exts, T["Choose files to open"],
                 initialdir=fildir, multiple=True)
        if fns is None: return proj[2].thanGudCommandCan()     # Open cancelled
        nopened = thanFileOpenPaths(proj, fns, _spreadClass)
        if nopened > 0: return proj[2].thanGudCommandEnd()


def thanFileOpenSpreadSurface(proj):
    "Opens one or more spreadsheet files, which contain a surface."
    _spreadClass = { #".ods": ("LibreOffice points",thanimp.ThanImportOdsPoints),
                     ".xls": ("Excel surface",      thanimp.ThanImportXlsSurface),
                     ".xlsx":("Excel surface",      thanimp.ThanImportXlsSurface),
                   }
    _ser = ".xls .xlsx".split()
    exts = [(_spreadClass[suf][0], suf) for suf in _ser]
    del _ser

    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkwid.thanGudGetReadFile(proj[2], exts, T["Choose files to open"],
                 initialdir=fildir, multiple=True)
        if fns is None: return proj[2].thanGudCommandCan()     # Open cancelled
        nopened = thanFileOpenPaths(proj, fns, _spreadClass)
        if nopened > 0: return proj[2].thanGudCommandEnd()


def thanFileOpen(proj, suf1=None, forceunload=False):
    """Opens a file which contains thancad drawing.

    The following are not saved, but they are automatically rebuilt when
    the drawing is restored, via the __setstate__, __getstate__ functions:
        self.thanLayerTree.dilay        : because it contains weak references
        elem.image (elem is a ThanImage): because it is too big

    The following are not saved, but they are rebuilt via the dw.thanRegen()
    where dw is the window which shows the drawing:
        elem.imagez (elem is a ThanImage): because it is Tk object
"""
    exts = _exts                      #Make a shallow copy
    if suf1 is not None:
        for i,ext1 in enumerate(_exts):
            if suf1 == ext1[1]:
                exts = _exts[:]       #Make a deep local copy
                del exts[i]
                exts.insert(0, ext1)  #Make suf1 the first choice of exts
                break
    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkwid.thanGudGetReadFile(proj[2], exts, T["Choose files to open"],
                 initialdir=fildir, multiple=True)
        if fns is None: return proj[2].thanGudCommandCan()     # Open cancelled
        nopened = thanFileOpenPaths(proj, fns, _importClass, forceunload)
        if nopened > 0: return proj[2].thanGudCommandEnd()


def thanFileOpenPaths(proj, fns, impClass=_importClass, forceunload=False):
    """Opens files with known paths.

    This is needed to implement opening of recent files (as shown in the menus).
    It is also needed to open files given as command line arguments when
    ThanCad starts."""
    nopened = 0
    for fn in fns:
            index1 = proj[2].thanCom.index(tkinter.END+"-1c")  #TkGui dependent: get end position of command window
            fn = path(fn)
            if fn.ext in impClass:
                dr, zoomext = impFile(proj, fn, impClass[fn.ext][1])
                success = "%s: %s" % (fn.name, T["file has been successfully imported."])
            else:
                dr = openThcx(proj, fn, forceunload)
                success = T["Existing drawing has been opened."]
                zoomext = False
            if dr is not None:
                dr.thanRepair()       # Try to rectify older versions of .thcx files
                nopened += 1
                replace = proj[1]     #in case proj is ThanCad and not another drawing. If proj is ThanCad then proj[1] is None
                replace = replace and (not proj[1].thanIsModified())
                replace = replace and thanfiles.isTempname1(proj[0].basename())
                if replace: __openHouseReplace(proj, fn, dr, success, zoomext)
                else:       __openHouse(proj, fn, dr, success, zoomext, index1)
    return nopened



def __openBZ2(proj, fn, dr, encoding):
    "Open thcx file stored as either BZ2 compessed or text, with encoding."
    fr = bz2.open(fn, "rt", compresslevel=1, encoding=encoding, errors="surrogateescape")
    projtemp = (fn, dr, proj[2])      #Make a temporary project for ThanRfile
    frf = thanrwf.ThanRBZfile(fr, projtemp, fn)
    if not frf.isBz2():    #If not a bzip2 file, then it is normal text file
        frf.thanDestroy()
        #import io, p_ggen
        #fr = io.open(fn, encoding=p_ggen.thanGetDefaultEncoding())
        fr = open(fn, encoding=encoding, errors="surrogateescape")
        frf = thanrwf.ThanRfile(fr, projtemp, fn)
    return frf


def openThcx(proj, fn, forceunload):
    "Opens a thancad xml like file."
    dr = thandwg.ThanDrawing()
    try:
        try:
            frf = __openBZ2(proj, fn, dr, "utf_8")      #Open temporarily to read version
            version = dr.thanReadVersion(frf)   #May raise ValueError if invalid version
            frf.thanDestroy()
            if version < (0,4,0): frf = __openBZ2(proj, fn, dr, "iso8859_7") #reopen with old encoding
            else:                 frf = __openBZ2(proj, fn, dr, "utf_8")     #reopen with UTF8
            dr.thanImpThc(frf, forceunload, prt=proj[2].thanPrt) #may raise ValueError and other exceptions
        except StopIteration as why:
            raise IOError("Incomplete file: end of file encountered")
    except (IOError, ValueError, IndexError, ImportError, OSError) as e:  # ImportError happens if BZ2file can not import its base class
            #JSONDecodeError is a subclass of ValueError and thus is handled by this except command
        dr.thanDestroy()
        try:
            frf
        except:
            why = e
        else:
            why = frf.er(e)
            frf.thanDestroy()
        mm(proj[2], why, T["Open failed"], p_gtkwid.ERROR)   # (Gu)i (d)ependent
        return None
    frf.thanDestroy()
    return dr


def impFile(proj, fn, ImportClass, defaultLayer="0", defaultLgeodp=None):
    "Imports a drawing saved in .dxf .syk .brk .syn .lin .mhk .xyz .lcad .lin format."
    fail = "%s: %s" % (fn.name, T["import failed."])
    try:
        if fn.ext in (".kml", ".kmz", ".lin", ".lcad", ".ods", ".xls", ".xlsx"):
            #p_gimgeo library used to open kml,kmz: a) accepts filenames and not file objects
            #b) sets the encoding defined in the kml/kmz file. Thus here we open the files
            #just to make sure that we can.
            #Linicad .lin and .lcad file must be opened as binary as they are
            #based on pickle.
            #Spreadsheet files must be opened in binary
            finp = open(fn, "rb")   #Thanasis2016_12_24 (merry Christmas!)
        else:  #.dxf .syk .brk .syn .xyz .mhk
            finp = open(fn, "r", encoding=thanGetEncoding(), errors="replace") #Thanasis2016_12_24 (merry Christmas!)
    except IOError as e:
        mm(proj[2], e, "%s: %s" % (fn.name, fail), p_gtkwid.ERROR)   # (Gu)i (d)ependent
        proj[2].thanGudCommandEnd(fail, "can")
        return None, None
#---create a new drawing
    dr = thandwg.ThanDrawing()
    if defaultLgeodp is not None:
        dr.Lgeodp = defaultLgeodp.copy()
        dr.geodp = p_ggeod.params.toProj(proj[1].Lgeodp)
#---import
    ts = thanimp.ThanCadDrSave(dr, proj[2].thanPrt)
    imp = ImportClass(finp, ts, defaultLayer)
    try:
        imp.thanImport()
    except ThanImportError as e:
        del imp
        finp.close()
        dr.thanDestroy()
        print("impFile: type of exception:", type(e))
        mm(proj[2], str(e), "%s: %s" % (fn.name, fail), p_gtkwid.ERROR)            # (Gu)i (d)ependent
        proj[2].thanGudCommandEnd(fail, "can")
        return None, None
    finp.close()
    ts.thanAfterImport()
#    del imp.thanDr._dr, imp.thanDr.prt
#    del imp.thanDr
#    del imp
    dr.thanLayerTree.thanDictRebuild()
    zoomext = not ts.viewportDefined
    return dr, zoomext


def __openHouse(proj, fn, dr, mes, zoomext, index1):
    "House keeping for file open."
    import thantkgui
    fn = fn.abspath()
    thanfiles.setFiledir(fn.parent)
#---create a new drawing window
    win = thantkgui.ThanTkGuiWinDraw()
    projnew = win.setDrawing(fn, dr)
    #projnew = win.thanProj
    projnew[2].thanCom.thanInsertFtext(proj[2].thanCom.thanGetFtext(index1), tkinter.END+"-1c")
    try:
        if zoomext: thancomview.thanZoomExt1(projnew)
        projnew[2].thanRegen()
    except:
        projnew[2].destroy()
        del win, projnew
        raise
#---Save drawing in active drawings
    thanfiles.fillMenu(projnew)
    thanfiles.addOpened(projnew)
    v = projnew[1].viewPort
    v[:] = projnew[2].thanGudZoomWin(v) # In case that the file defined other viewport
    projnew[1].thanResetModified()      # In case the file was saved with the modified variable set to true
    proj[2].thanPrt(mes, "info")
    projnew[2].thanGudCommandEnd(mes, "info")
    projnew[2].thanTkSetFocus()
    return projnew


def __openHouseReplace(proj, fn, dr, mes, zoomext):
    "House keeping for file open."
    fn = fn.abspath()
    thanfiles.setFiledir(fn.parent)
#---Replace project with this drawing
    thanfiles.delOpened(proj)
    projold = proj[:]             #Shallow copy
    win = proj[2]
    projnew = win.setDrawing(fn, dr)     #This is exactly the same project as proj
    try:
        if zoomext: thancomview.thanZoomExt1(projnew)
        projnew[2].thanRegen()
    except:
        raise
        projnew[2].destroy()
        projnew[1].thanDestroy()
        del projnew
        proj[:] = projold[:]
        thanfiles.addOpened(projold)
        raise
#---Save drawing in active drawings

    thanfiles.addOpened(projnew)
    v = projnew[1].viewPort
    v[:] = projnew[2].thanGudZoomWin(v) # In case that the file defined other viewport
    projnew[1].thanResetModified()      # In case the file was saved with the modified variable set to true
    proj[2].thanPrt(mes, "info")
#    projnew[2].thanGudCommandEnd()
    projnew[2].thanTkSetFocus()
    return projnew

#=============================================================================

def thanFileMerge(proj, copyelems=False, forceunload=False):
    """Opens files which contains thancad drawing for mergeing with current project."""
    exts = _exts                      #Make a shallow copy
    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkwid.thanGudGetReadFile(proj[2], exts, T["Choose files to insert"],
                 initialdir=fildir, multiple=True)
        if fns is None: return proj[2].thanGudCommandCan()     # Open cancelled
        projothers = thanFileMergePaths(proj, fns, _importClass, forceunload)
        if len(projothers) > 0: break

    projothers, newcl, newroot = thanMergeHier(proj, projothers, copyelems)
    if len(projothers) < 1: return proj[2].thanGudCommandCan(T["No files were inserted"])
    oldcl, oldroot, newelemsdrawn, newelemsnot = thanMergeDo(proj, projothers, newcl, newroot, copyelems)
    newcl.thanTkSet(proj[2].than)
    proj[2].thanUpdateLayerButton()
    proj[1].thanTouch()                                        # Drawing IS modified
#    thanundo.thanLtRestore(proj, newcl, newroot)
    proj[2].thanGudCommandEnd(T["%d file(s) were inserted"] % (len(projothers),), "info")


def thanFileMergePaths(proj, fns, impClass, forceunload=False):
    """Opens files with known paths for merging with current proj.

    This closely resembles thanFileOpenPaths on purpose. Any change must be
    done to both functions."""
    projothers = []
    cl = proj[1].thanLayerTree.thanCur
    clname = cl.thanAtts[thanlayer.THANNAME].thanVal
    for fn in fns:
            fn = path(fn)
            if fn.ext in impClass:
                print("thanFileMergePaths(): Lgeodp=", proj[1].Lgeodp)
                dr, _ = impFile(proj, fn, impClass[fn.ext][1], defaultLayer=clname,
                    defaultLgeodp=proj[1].Lgeodp)
            else:
                dr = openThcx(proj, fn, forceunload)
            if dr is not None:
                projothers.append([fn, dr, None])
    return projothers


def thanMergeHier(proj, projothers, copyelems=False):
    "Copy all the elements (references or distinct) of other projects to current."
    from . import thanundo
    lt = proj[1].thanLayerTree
    newcl, newroot = thanundo.thanLtClone2(lt.thanCur, lt.thanRoot)
    projoks = []
    for fn, dr, _ in projothers:
        bakcl, bakroot = thanundo.thanLtClone2(newcl, newroot)
        ltother = dr.thanLayerTree
        other2lay, newcl, terr = newroot.thanMergeHier(newcl, ltother.thanRoot)
        if other2lay is None:
            terr = "Error while importing %s: %s" % (fn, terr)
            proj[2].thanPrt(terr, "can1")
            newcl, newroot = bakcl, bakroot
        else:
            projoks.append((fn, dr, _, other2lay))
    return projoks, newcl, newroot


def thanMergeDo(proj, projothers, newcl, newroot, copyelems=False):
    "Copy all the elements (references or distinct) of other projects to current."
    lt = proj[1].thanLayerTree                   #Please note that oldroot contains just a reference to the set of elements
    oldcl, oldroot = lt.thanCur, lt.thanRoot     #..and thus we waste no memory here
    lt.thanCur, lt.thanRoot = newcl, newroot
    lt.thanDictRebuild()

    self = proj[1]
    xymm = self.thanExtViewPort()           #Return twice the viewport window
    than = proj[2].than
    newelemsdrawn = []
    newelemsnot = []

    for _, dr, _, other2lay in projothers:
        ltother = dr.thanLayerTree
        for layother in ltother.dilay.values():  #works for python2,3
            lay = other2lay[layother]
            frozen = lay.thanAtts["frozen"].thanVal
            if not frozen: lay.thanTkSet(than)
            for e in layother.thanQuad:
                if copyelems: e = e.thanClone()
                if e.handle is not None and e.handle > 0:
                    e1 = self.thanTagel.get(e.handle)
                    if e1 is not None: e.thanUntag()   #It is not safe to keep the old handle
                self.thanElementAdd(e, lay)
                if frozen:
                    newelemsnot.append(e)
                    continue
                if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
                if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
                if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
                if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
                if e.thanInbox(xymm):
                    newelemsdrawn.append(e)
                    e.thanTkDraw(than)
                else:
                    newelemsnot.append(e)
    return oldcl, oldroot, newelemsdrawn, newelemsnot


#=============================================================================

_docSave = """
1. When we open a file we retain its the extension, which means that the
   extension is not converted to .thcx. This means that the extension
   may be
       .dxf .syk .brk .syn .lin .mhk .xyz
   as defined in _importClass dictionary.
2. When we open a file, the drawing is marked as NOT modified regardless of
   the extension, so that the user can close it, without ThanCad asking if it
   should save it.
3. When the user presses save:
   a. If the file extension is .thcx, a backup copy is created as .thcx.bak
      and the file is saved in .thcx format. If the backup copy can not be made
      or the drawing can not be saved in .thcx file, the user is notified
      and ThanCad asks the user for a new file name with .thcx extension.
   b. If the file extension is .thcx but the prefix is a temporary file,
      it means that the drawing was created as new, and ThanCad prompts the
      user for a filename with the .thcx extension. No backup file is created.
   c. If the file extension is not .thcx the user is prompted to save
      the drawing with the .thcx extension. No backup is created
4. When the users presses saveas:
   a. If the file extension is .thcx, ThanCad asks the user for a new file
      name with .thcx extension.
   b. If the file extension is not .thcx, ThanCad asks the user for a new file
      name with .thcx extension.
   When the user modifies the drawing, ThanCad should warn the user that the
   file must be written to a .thcx file, in order to
5. ThanCad shows the name of the files on the title as prefix.suffix (without the parent)
6. When the user saves to a filename other than .thcx (command save can't, only
   command saveas can), then ThanCad does not reset the modified flag. This means
   that if the drawing before the save was considered modified, it is considered
   modified and after the save.
"""

def thanFileSave(proj):
    "Saves a drawing into .thcx file."
    fn = proj[0]
    if fn.ext != ".thcx": return thanFileSaveas(proj)   #The drawing was NOT read from a .thcx file; ask for confirmation
    if thanfiles.isTempname(fn.basename()): return thanFileSaveas(proj)   #temp file;ask for new name
    #print "thanfilesave: fn=", fn
    if not fn.exists(): return thanFileSaveas(proj)  #The drawing was read from .thcx file: something funny happens, so ask for confirmation
    fnbak = fn.parent / fn.namebase + ".bak"
    try:
        if fnbak.exists(): fnbak.remove()
        fn.rename(fnbak)
    except Exception as why:
        mm(proj[2], why, T["Failed to create backup file %s"] % (fnbak.basename(),), p_gtkwid.ERROR)   # (Gu)i (d)ependent
        return thanFileSaveas(proj)
    nopened = thanFileSavePath(proj, fn)
    if nopened == 0: return thanFileSaveas(proj)  #Could not save file; let the use try with another name


_exportClass = { ".dxf": ("Drawing Interchange 12 ascii", "thanExpDxf"),
                 ".syk": ("2D Lines with Elevation",      "thanExpSyk"),
                 ".brk": ("3D Lines",                     "thanExpBrk"),
                 ".syn": ("Topographic Points",           "thanExpSyn"),
                 ".kml": ("Google Placemarks",            "thanExpKml"),
               }
_sexts = [(_exportClass[suf][0], suf) for suf in ".dxf .syk .brk .syn .kml".split()]
_sexts.insert(0, ("ThanCad xml", ".thcx"))
_sexts.append(("All Files", "*"))

def thanFileSaveas(proj, suf1=None):
    """Opens a file which contains thancad drawing.

    The following are not saved, but they are automatically rebuilt when
    the drawing is restored, via the __setstate__, __getstate__ functions:
        self.thanLayerTree.dilay        : because it contains weak references
        elem.image (elem is a ThanImage): because it is too big

    The following are not saved, but they are rebuilt via the dw.thanRegen()
    where dw is the window which shows the drawing:
        elem.imagez (elem is a ThanImage): because it is Tk object
"""
    exts = _sexts                      #Make a shallow copy
    if suf1 is not None:
        for i,ext1 in enumerate(_exts):
            if suf1 == ext1[1]:
                exts = _sexts[:]       #Make a deep local copy
                del exts[i]
                exts.insert(0, ext1)   #Make suf1 the first choice of exts
                break
    fildir = thanfiles.getFiledir()
    while True:
        fn = p_gtkwid.thanGudGetSaveFile(proj[2], exts, T["Save/export drawing to a file"],
            initialfile=proj[0].namebase, initialdir=fildir)
        if fn is None: return proj[2].thanGudCommandCan()     # Open cancelled
        #print "thanFileSaveas: fn=", fn
        nopened = thanFileSavePath(proj, fn)
        if nopened > 0: return                             # OK


def thanFileExportSpreadx(proj, eltype):
    "Export user selected points or lines to an .xlsx/.xls file."
    try:
        import xlwt
    except ImportError:
        return proj[2].thanGudCommandCan(T["Can not export xls/xlsx spreadsheets: The xlwt library/package was not found.\n"\
            "Please install xlwt in your system and retry."])

    if eltype == "points":
        filterfun = lambda e: isinstance(e, thandr.ThanPoint)
        expmethod = proj[1].thanExpXlspoints
    elif eltype == "lines":
        filterfun = lambda e: isinstance(e, thandr.ThanLine)
        expmethod = proj[1].thanExpXlslines
    else:
        assert 0, "eltype='{}': it should be 'points' or 'lines'".format(eltype)
    while True:
        proj[2].thanPrt(T["Select {} to export:".format(eltype)], "info1")
        res = thancomsel.thanSelectOr(proj, standalone=False, filter=filterfun,
            optionname="all", optiontext="a=all")
        if res == Canc: return thanModCanc(proj)           # Profile was cancelled
        if res == "a":
            #The user did not select anything, but keep current (empty) selection
            break
        break
    if res == "a":
        elements = None  #This means selection of all elements in the drawing
    else:
        elements = proj[2].thanSelall

    book = xlwt.Workbook()
    sh = book.add_sheet(eltype, cell_overwrite_ok=False)
    xf = xlwt.Style.easyxf(num_format_str="0.000")
    ok, ter = expmethod(proj, sh, xf, elements)
    if not ok:
        fail = T["export failed."]
        mm(proj[2], ter, fail, p_gtkwid.ERROR)    # (Gu)i (d)ependent
        proj[2].thanGudCommandEnd(fail)
        return 0

    exts = ("excel", ".xlsx"), ("excel old", ".xls")
    fildir = thanfiles.getFiledir()
    while True:
        fn = p_gtkwid.thanGudGetSaveFile(proj[2], exts, T["Export {} to spreadsheet".format(eltype)],
            initialfile=proj[0].namebase, initialdir=fildir)
        if fn is None: return proj[2].thanGudCommandCan()     # Open cancelled
        try:
            book.save(fn)
        except Exception as e:
            fail = "%s: %s" % (fn.name, T["export failed."])
            mm(proj[2], str(e), fail, p_gtkwid.ERROR)    # (Gu)i (d)ependent
        else:
            break
    return proj[2].thanGudCommandEnd()


def thanFileExportImages(proj):
    "Export user selected images to an autocad script (.scr) file."
    comname = "exportimages"
    filterfun = lambda e: isinstance(e, thandr.ThanImage)
    while True:
        proj[2].thanPrt(T["Select images to export to an autocad script file:"], "info1")
        res = thancomsel.thanSelectOr(proj, standalone=False, filter=filterfun,
            optionname="all", optiontext="a=all")
        if res == Canc: return thanModCanc(proj)           # Profile was cancelled
        if res == "a":
            #The user did not select anything, but keep current (empty) selection
            break
        break
    if res == "a":
        elements = None  #This means selection of all elements in the drawing
    else:
        elements = proj[2].thanSelall
    elems = proj[2].thanSelall
    selold = proj[2].thanSelold

    exts = ("Autocad script", ".scr"),
    fildir = thanfiles.getFiledir()
    fn, fw = p_gtkwid.thanGudOpenSaveFile(proj[2], exts, T["Export images to autocad script"],
        initialfile=proj[0].namebase, initialdir=fildir)
    if fn is None: return thanModCanc(proj)     # Open cancelled

    ok, ter = proj[1].thanExpImages(proj, fw, elements)
    fw.close()
    if not ok:
        fail = T["export failed."]
        mm(proj[2], ter, fail, p_gtkwid.ERROR)    # (Gu)i (d)ependent
        return thanModCanc()

    proj[1].thanDoundo.thanAdd(comname, thanundo.thanActionRedo, (elems,         doNothing),  #file .scr is not rewritten
                                        thanundo.thanActionUndo, (elems, selold, doNothing))  #file .scr is not unwritten
    thanModEnd(proj)                              # 'Reset color' may be necessary here


def thanFileSavePath(proj, fn):
    """Opens a file with known path.

    This is needed to implement saving by direct command such as dxfout.
    """
    fn = path(fn)
    if fn.ext in _exportClass:
        try:
            if fn.ext in (".kml"):
                #p_gimgeo library used to write kml: a) accepts file objects opened as text
                #b) the encoding must be utf_8
                fout = open(fn, "w", encoding="utf_8", errors="replace")   #Thanasis2016_12_25 (merry Christmas!)
            else:  #.dxf .syk .brk .syn .xyz .mhk
                fout = open(fn, "w", encoding=thanGetEncoding(), errors="replace") #Thanasis2016_12_25 (merry Christmas!)
        except IOError as why:
            mm(proj[2], why, T["Open failed"])   # (Gu)i (d)ependent
            return 0
#-------export
        method = getattr(proj[1], _exportClass[fn.ext][1])
        ok, ter = method(fout)
        fout.close()                          #Ok to close closed files.
        if not ok:
            fail = "%s: %s" % (fn.name, T["export failed."])
            mm(proj[2], ter, fail, p_gtkwid.ERROR)    # (Gu)i (d)ependent
            proj[2].thanGudCommandEnd(fail)
            return 0
        success = "%s: %s" % (fn.name, T["file has been successfully exported."])
    else:
        try:
            #fw = bz2.BZ2File(fn, "w", 0, 1)
            fw = bz2.open(fn, "wt", compresslevel=1, encoding="utf_8", errors="surrogateescape")
            fwf = thanrwf.ThanWfile(fw, proj, fn)
            proj[1].thanExpThc(fwf)
            fwf.thanDestroy()
            fw.close()
            success = T["Drawing saved in %s."] % fn
        except (IOError, ImportError, ValueError) as why:  # ImportError happens if BZ2file can not import its base class
            mm(proj[2], why, T["Save failed"], p_gtkwid.ERROR)   # (Gu)i (d)ependent
            return 0
    __saveHouse(proj, fn)
    proj[2].thanGudCommandEnd(success, "info")
    return 1


def __saveHouse(proj, fn):
    "House keeping for file save."
#---Save drawing in active drawings
    thanRenameHouse(proj, fn)
    proj[2].thanGudCommandEnd(T["Drawing has been saved."], "info")


def thanRenameHouse(proj, fn):
    "House keeping for file rename."
#---Save drawing in active drawings
    fnold = proj[0]
    thanfiles.delOpened(proj)    #It should be already there
    proj[0] = fn
    proj[2].thanTitle = thanvers.tcver.name + " - " + proj[0].name
    proj[2].title(proj[2].thanTitle)
    if fn.ext == ".thcx": proj[1].thanResetModified()
    fn = fn.abspath()
    thanfiles.setFiledir(fn.parent)
    thanfiles.addOpened(proj)
    if (not thanfiles.isTempname(fnold.name) and   #Temporary files are not put in recent list
            fnold.ext.lower() not in (".ods", ".xls", ".xlsx")): #Spreadsheet open is ambiguous: not put in recent list
        thanfiles.addRecent(fnold)

#=============================================================================

def thanFileClose(proj):
    "Closes a drawing and prints cancelled id appropriate."
    if thanFileCloseDo(proj) == Canc:
        proj[2].thanGudCommandCan()    # Close cancelled


def thanFileCloseDo(proj):
    "Closes a drawing (deletes dr, win and alters modified, recent list) but warns if it is modified."
    if proj[1].thanIsModified():
        a = p_gtkwid.thanGudAskOkCancel(proj[2], T["Drawing modified, OK to close?"], proj[0], default="cancel")
        if not a: return Canc    # Close cancelled
    thanfiles.delOpened(proj)
    proj[1].thanDestroy()
    proj[2].destroy()
    if (not thanfiles.isTempname(proj[0].name) and   #Temporary files are not put in recent list
            proj[0].ext.lower() not in (".ods", ".xls", ".xlsx")): #Spreadsheet open is ambiguous: do not put in recent list
        thanfiles.addRecent(proj[0])
    return True


def thanFileExit(proj):
    "Terminates the program."
    for proj in thanfiles.getOpened():   # Close each open window
        if proj == thanfiles.ThanCad: continue
        if thanFileCloseDo(proj) == Canc:         # abort if an open window is not closed
            proj[2].thanTkSetFocus()
            proj[2].thanGudCommandCan(T["Quit cancelled"])
            return
    thanfiles.ThanCad[2].destroy()


#=============================================================================

def thanTxtopen(proj, mes, suf=".txt", mode="r", initialfile=None, initialdir=None):
    "Opens a text file for reading or writting something."
    if initialdir is None: initialdir = thanfiles.getFiledir()
    if initialfile is None: initialfile = proj[0].namebase
    if "w" in mode:
        fildxf, frw = p_gtkwid.thanGudOpenSaveFile(proj[2], suf, mes, mode,
            initialfile, initialdir)
    else:
        fildxf, frw = p_gtkwid.thanGudOpenReadFile(proj[2], suf, mes, mode,
            initialfile, initialdir)
    if frw is None: return Canc, Canc     # File open cancelled
    return path(fildxf), frw


def thanTxtsave(proj, mes, suf=".txt"):
    "Opens a text file for saving something."
    fildir = thanfiles.getFiledir()
    while True:
        fildxf = p_gtkwid.thanGudGetSaveFile(proj[2], suf, mes,
            proj[0].namebase, initialdir=fildir)
        if fildxf is None: proj[2].thanGudCommandCan(); return Canc      # Export cancelled
        fildxf = path(fildxf)
        try:                 fout = fildxf.open("w")
        except IOError as why: mm(proj[2], why, T["Open failed"], p_gtkwid.ERROR)   # (Gu)i (d)ependent
        else:                break
    return fout


#=============================================================================

def thanPlotPdf(proj):
    "Plots drawing to pdf file."
    try:
        import pyx
    except ImportError as e:
        t = "Python library module pyx is probably not installed:\n%s" % (e,)
        return proj[2].thanGudCommandCan(t)
    fildir = thanfiles.getFiledir()
    than = None
    while True:
        fildxf = p_gtkwid.thanGudGetSaveFile(proj[2], ".pdf", T["Plot to pdf file"],
            initialfile=proj[0].namebase, initialdir=fildir)
        if fildxf is None: del than; proj[2].thanGudCommandCan(); return   # Export cancelled
        fildxf = path(fildxf)
        try:
            fout = fildxf.open("w")
            fout.close()
        except IOError as why:
            mm(proj[2], why, T["Open failed"], p_gtkwid.ERROR)        # (Gu)i (d)ependent
            continue
        if than is None: than = proj[1].thanPlotPdf(1.0)
        try:
            than.dc.writePDFfile(fildxf)
        except IOError as why:
            mm(proj[2], why, T["Write failed"], p_gtkwid.ERROR)       # (Gu)i (d)ependent
            continue
        break
    del than
    proj[2].thanGudCommandEnd(T["Pdf file has been created."], "info")


def thanPlotPilold(proj):
    "Exports to PIL image."
    fpath = proj[0].parent / proj[0].namebase + ".bmp"
    win = thantkdia.ThanTkExppil(proj[2], fpath, title=T["Export to Image: specifications"])
    if win.result is None: proj[2].thanGudCommandCan(); return                      # Export cancelled
    fpath, mode, width, height, drwin = win.result
    try:
        proj[1].thanExpPil(fpath, mode, width, height, drwin)
    except IOError as why:
        return proj[2].thanGudCommandCan("%s:\n%s" % (T["Image could not be exported"], why))
    proj[2].thanGudCommandEnd(T["Image has been exported."], "info")


def thanPlotPil(proj):
    "Exports to PIL image."
    win = thantkdia.ThanTkExppil(proj[2], vals=None, cargo=proj, title=T["Export to Image: specifications"])
    v = win.result
    if v is None: return proj[2].thanGudCommandCan()  # Export cancelled
    try:
#        proj[1].thanExpPil(fpath, mode, width, height, drwin)
        proj[1].thanExpPil(v.filIm, v.choMode, v.entWidth, v.entHeight, v.choPlotCode, v.choBackGr, v.butPlotWin)
    except IOError as why:
        return proj[2].thanGudCommandCan("%s:\n%s" % (T["Image could not be exported"], why))
    proj[2].thanGudCommandEnd(T["Image has been exported."], "info")


def thanImpLin(proj):
    "Import the linetypes definitions from a .lin file to current drawing."
    fn, fr = thanTxtopen(proj, T["Choose .lin file to import"], suf=".lin")
    if fr == Canc: return proj[2].thanGudCommandCan()    #Import cancelled
    ltypes = thanimp.thanImpLin(fr, prt=proj[2].thanPrter1)
    fr.close()
    if len(ltypes) == 0: return proj[2].thanGudCommandCan(T["No line types were imported."])
    ltypesold = copy.deepcopy(proj[1].thanLtypes)        #This is fast, because ThanLtype consists of only immutable attributes
    n = sum(1 for namlt in ltypes if namlt in ltypesold)
    proj[1].thanLtypes.update(ltypes)
    ltypesnew = copy.deepcopy(proj[1].thanLtypes)        #This is fast, because ThanLtype consists of only immutable attributes
    proj[1].thanDoundo.thanAdd("linin", thanLtRestore, (ltypesnew,),       #redo
                                        thanLtRestore, (ltypesold,))       #undo
    proj[1].thanTouch()
    proj[2].thanGudCommandEnd("%d linetypes were added (%d were updated)." % (len(ltypes)-n, n), "info")

def thanLtRestore(proj, ltypes):
    "Restore previously save line types."
    proj[1].thanLtypes.clear()
    proj[1].thanLtypes.update(ltypes)
    proj[1].thanTouch()


def thanExpLin(proj):
    "Export the linetypes defintitions to a .lin file from current drawing."
    fn, fw = thanTxtopen(proj, T["Choose .lin file to export"], suf=".lin", mode="w")
    if fw == Canc: return proj[2].thanGudCommandCan()    #Export cancelled
    thanexp.thanExpLin(fw, proj[1].thanLtypes, proj[2].thanPrter1)
    proj[1].thanDoundo.thanAdd("linout", doNothing, (),
                                         doNothing, ())
    proj[2].thanGudCommandEnd("%d linetypes were exported." % (len(proj[1].thanLtypes),), "info")
