##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

Package which processes commands entered by the user.
This module processes file related commands.
"""

import cPickle, bz2
from tkMessageBox import ERROR
from p_ggen import path, Struct
import p_gtkuti
import thanvers, thandr, thanimp, thantkgui, thantkdia, thansupport, thanopt
from thantrans import T, Tmatch
from thanvar import Canc, thanfiles, ThanImportError
import thanrwf

mm = p_gtkuti.thanGudModalMessage


def thanFileNew(proj):
    "Creates a new drawing and its drawing window."
    projnew = thanFileNewDo(proj)
    proj[2].thanGudCommandEnd(T["New drawing has been created."], "info")
    projnew[2].thanGudCommandEnd()


def thanFileNewDo(proj, mes=None):
    "Creates a new drawing and its drawing window - does the job."
    fpath = thanfiles.tempname()
    dr = thandr.ThanDrawing()
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
               }
_ser = ".dxf .syk .brk .syn .lin".split()
if thanopt.thancon.thanFrape.civil:
    import thanprocivil
    from thanprocivil.thanproimp import ThanImportMhk
    _importClass[".mhk"] = ("Highway Profile", ThanImportMhk)
    _ser.append(".mhk")
_exts = [(_importClass[suf][0], suf) for suf in _ser]
del _ser
_exts.insert(0, ("ThanCad", ".thc"))
_exts.insert(0, ("ThanCad xml", ".thcx"))
_exts.append(("All Files", "*"))


def thanFileOpen(proj, suf1=None):
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
    if suf1 != None:
        for i,ext1 in enumerate(_exts):
            if suf1 == ext1[1]:
                exts = _exts[:]       #Make a deep local copy
                del exts[i]
                exts.insert(0, ext1)  #Make suf1 the first choice of exts
                break
    fildir = thanfiles.getFiledir()
    while True:
        fns = p_gtkuti.thanGudGetReadFile(proj[2], exts, T["Choose file to open"],
                 initialdir=fildir, multiple=True)
        if fns == None: return proj[2].thanGudCommandCan()     # Open cancelled
        nopened = thanFileOpenPaths(proj, fns)
        if nopened > 0: return proj[2].thanGudCommandEnd()


def thanFileOpenPaths(proj, fns):
    """Opens a files with known paths.

    This is needed to implement opening of recent files (as shown in the menus).
    It is also needed to open files given as command line arguments when
    ThanCad starts."""
    nopened = 0
    for fn in fns:
            fn = path(fn)
            if fn.ext in _importClass:
                dr = impFile(proj, fn, _importClass[fn.ext][1])
                success = "%s: %s" % (fn.name, T["file has been successfully imported."])
            elif fn.ext == ".thcx":
                dr = openThcx(proj, fn)
                success = T["Existing drawing has been opened."]
            else:
                try:
                    dr = None
                    fr = bz2.BZ2File(fn, "r", 0, 1)
                    s = fr.read()         # Uncompress (in case of error it raises IOError)
                    fr.close()
                    dr = cPickle.loads(s) # Unpickle (in case of error it raises PickleError, and maybe ValueError from numpy))
                    success = T["Existing drawing has been opened."]
                except (IOError, cPickle.PickleError, ImportError, AttributeError, ValueError), why:    # ImportError happens if BZ2file can not import its base class
                    try: dr.thanDestroy()
                    except: pass
                    why = str(why) + "\n\n" + T["(This might be an old, no longer supported, drawing file)"]
                    mm(proj[2], why, T["Open failed"], ERROR)   # (Gu)i (d)ependent
            if dr != None:
                dr.thanRepair()       # Try to rectify old .thc files
                nopened += 1
                replace = proj[1]     #in case proj is ThanCad and not another drawing
                replace = replace and (not proj[1].thanIsModified())
                replace = replace and thanfiles.isTempname1(proj[0].basename())
                if replace: __openHouseReplace(proj, fn, dr, success)
                else:       __openHouse(proj, fn, dr, success)
    return nopened


def openThcx(proj, fn):
    "Opens a thancad xml like file."
    dr = thandr.ThanDrawing()
    try:
        try:
            fr = bz2.BZ2File(fn, "r", 0, 1)
            projtemp = (fn, dr, proj[2])      #Make a temporary project for ThanRfile
            frf = thanrwf.ThanRBZfile(fr, projtemp)
            if not frf.isBz2():    #If not a bzip2 file, then it is normal text file
                frf.thanDestroy()
                fr = open(fn)
                frf = thanrwf.ThanRfile(fr, projtemp)
            dr.thanImpThc(frf)
        except StopIteration, why:
            raise IOError, "Incomplete file: end of file encountered"
    except (IOError, ValueError, IndexError, ImportError), e:    # ImportError happens if BZ2file can not import its base class
        dr.thanDestroy()
        try:
            frf
        except:
            pass
        else:
            why = frf.er(e)
            frf.thanDestroy()
        mm(proj[2], why, T["Open failed"], ERROR)   # (Gu)i (d)ependent
        return None
    frf.thanDestroy()
    return dr


def impFile(proj, fn, ImportClass):
    "Imports a drawing saved in .dxf .syk .brk .syn .lin .mhk format."
    fail = "%s: %s" % (fn.name, T["import failed."])
    try:
        finp = fn.open()
    except IOError, e:
        mm(proj[2], e, "%s: %s" % (fn.name, fail), ERROR)   # (Gu)i (d)ependent
        proj[2].thanGudCommandEnd(fail, "can")
        return None
#---create a new drawing
    dr = thandr.ThanDrawing()
#---import
    ts = thanimp.ThanCadDrSave(dr, proj[2].thanPrt)
    imp = ImportClass(finp, ts)
    try:
        imp.thanImport()
    except ThanImportError, e:
        del imp
        finp.close()
        dr.thanDestroy()
        print "impFile: type of exception:", type(e)
        print dir(e)
        print str(e.message)
        mm(proj[2], str(e.message), "%s: %s" % (fn.name, fail), ERROR)            # (Gu)i (d)ependent
        proj[2].thanGudCommandEnd(fail, "can")
        return None
    del imp
    finp.close()
    ts.thanAfterImport()
    dr.thanLayerTree.thanDictRebuild()
    return dr


def __openHouse(proj, fn, dr, mes):
    "House keeping for file open."
    fn = fn.abspath()
    thanfiles.setFiledir(fn.parent)
#---create a new drawing window
    win = thantkgui.ThanTkGuiWinDraw()
    projnew = win.setDrawing(fn, dr)
    projnew = win.thanProj
    try:
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
    projnew[2].thanGudCommandEnd()
    projnew[2].thanTkSetFocus()
    return projnew


def __openHouseReplace(proj, fn, dr, mes):
    "House keeping for file open."
    fn = fn.abspath()
    thanfiles.setFiledir(fn.parent)
#---Replace project with this drawing
    thanfiles.delOpened(proj)
    projold = proj[:]             #Shallow copy
    win = proj[2]
    projnew = win.setDrawing(fn, dr)     #This is exactly the same project as proj
    try:
        projnew[2].thanRegen()
    except:
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

_docSave = """
1. When we open a file we retain its the extension, which means that the
   extension is not converted to .thcx. This means that the extension
   may be
       .dxf .syk .brk .syn .lin .mhk
   as defined in _importClass dictionary.
2. When we open a file, the drawing is marked as NOT modified regardless of
   the extension, so that the user can close it, without ThanCad asking if it
   should save it.
3. When the user presses save:
   a. If the file extension is .thcx, a backup copy is created as .thcx.bak
      and the file is saved in .thcx format. If the backup copy can not be made
      or the drawinng can not be saved in .thcx file, the user is notified
      and ThanCad asks the user for a new file name with .thcx extension.
   b. If the file extension is .thcx but the prefix is a temporary file,
      it means that the drawing was created as new, and ThanCad prompts the
      user for a filename with the .thcx extrension. No backup file is created.
   c. If the file exdtension is not .thcx the user is prompted to save
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
    if fn.ext != ".thcx": return thanFileSaveas(proj)   #The drawing was NOT read form a .thcx file; ask for confirmation
    if thanfiles.isTempname(fn.basename()): return thanFileSaveas(proj)   #temp file;ask for new name
    print "thanfilesave: fn=", fn
    if not fn.exists(): return thanFileSaveas(proj)  #The drawing was read from .thcx file: something funny happens, so ask for confirmation
    fnbak = fn.parent / fn.namebase + ".bak"
    try:
        if fnbak.exists(): fnbak.remove()
        fn.rename(fnbak)
    except Exception, why:
        mm(proj[2], why, T["Failed to create backup file %s"] % (fnbak.basename(),), ERROR)   # (Gu)i (d)ependent
        return thanFileSaveas(proj)
    nopened = thanFileSavePath(proj, fn)
    if nopened == 0: return thanFileSaveas(proj)  #Could not save file; let the use try with another name


_exportClass = { ".dxf": ("Drawing Interchange 12 ascii", "thanExpDxf"),
                 ".syk": ("2D Lines with Elevation",      "thanExpSyk"),
                 ".brk": ("3D Lines",                     "thanExpBrk"),
                 ".syn": ("Topographic Points",           "thanExpSyn"),
               }
_sexts = [(_exportClass[suf][0], suf) for suf in ".dxf .syk .brk .syn".split()]
_sexts.insert(0, ("ThanCad", ".thc"))
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
    if suf1 != None:
        for i,ext1 in enumerate(_exts):
            if suf1 == ext1[1]:
                exts = _sexts[:]       #Make a deep local copy
                del exts[i]
                exts.insert(0, ext1)   #Make suf1 the first choice of exts
                break
    fildir = thanfiles.getFiledir()
    while True:
        fn = p_gtkuti.thanGudGetSaveFile(proj[2], exts, T["Save/export drawing to a file"],
            initialfile=proj[0].namebase, initialdir=fildir)
        if fn == None: return proj[2].thanGudCommandCan()     # Open cancelled
        print "thanFileSaveas: fn=", fn
        nopened = thanFileSavePath(proj, fn)
        if nopened > 0: return                             # OK


def thanFileSavePath(proj, fn):
    """Opens a files with known paths.

    This is needed to implement saving by direct command such as dxfout.
    """
    fn = path(fn)
    if fn.ext in _exportClass:
        try:
            fout = fn.open("w")
        except IOError, why:
            p_gtkuti.thanGudModalMessage(proj[2], T["Open failed"], why)   # (Gu)i (d)ependent
            return 0
#-------export
        method = getattr(proj[1], _exportClass[fn.ext][1])
        icod = method(fout)
        fout.close()                          #Ok to close closed files.
        if icod == -1:
            fail = "%s: %s" % (fn.name, T["export failed."])
            mm(proj[2], text, fail, ERROR)    # (Gu)i (d)ependent
            proj[2].thanGudCommandEnd(fail)
            return 0
        success = "%s: %s" % (fn.name, T["file has been successfully exported."])
    elif fn.ext == ".thcx":
        try:
            fw = bz2.BZ2File(fn, "w", 0, 1)
            fwf = thanrwf.ThanWfile(fw, proj)
            proj[1].thanExpThc(fwf)
            fwf.thanDestroy()
            fw.close()
            success = T["Drawing saved in %s."] % fn
        except (IOError, cPickle.PickleError, ImportError, ValueError), why:  # ImportError happens if BZ2file can not import its base class
            mm(proj[2], why, T["Save failed"], ERROR)   # (Gu)i (d)ependent
            return 0
    else:
        try:
            fw = bz2.BZ2File(fn, "w", 0, 1)
            s = cPickle.dumps(proj[1])
            fw.write(s)
            fw.close()
            success = T["Drawing saved in %s."] % fn
        except (IOError, cPickle.PickleError, ImportError, ValueError), why:  # ImportError happens if BZ2file can not import its base class
            mm(proj[2], why, T["Save failed"], ERROR)   # (Gu)i (d)ependent
            return 0
    __saveHouse(proj, fn)
    proj[2].thanGudCommandEnd(success, "info")
    return 1


def __saveHouse(proj, fn):
    "House keeping for file open."
#---Save drawing in active drawings
    fnold = proj[0]
    thanfiles.delOpened(proj)    #It should be already there
    proj[0] = fn
    proj[2].thanTitle = thanvers.thanCadName + " - " + proj[0].name
    proj[2].title(proj[2].thanTitle)
    if fn.ext == ".thcx": proj[1].thanResetModified()
    fn = fn.abspath()
    thanfiles.setFiledir(fn.parent)
    thanfiles.addOpened(proj)
    if not thanfiles.isTempname(fnold.name): thanfiles.addRecent(fnold)
    proj[2].thanGudCommandEnd(T["Drawing has been saved."], "info")

#=============================================================================

def thanFileClose(proj):
    "Closes a drawing and prints cancelled id appropriate."
    if thanFileCloseDo(proj) == Canc:
        proj[2].thanGudCommandCan()    # Close cancelled


def thanFileCloseDo(proj):
    "Closes a drawing (deletes dr, win and alters modified, recent list) but warns if it is modified."
    if proj[1].thanIsModified():
        a = p_gtkuti.thanGudAskOkCancel(proj[2], T["Drawing modified, OK to close?"], proj[0], default="cancel")
        if not a: return Canc    # Close cancelled
    thanfiles.delOpened(proj)
    proj[1].thanDestroy()
    proj[2].destroy()
    if not thanfiles.isTempname(proj[0].name): thanfiles.addRecent(proj[0])
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
    if initialdir == None: initialdir = thanfiles.getFiledir()
    if initialfile == None: initialfile = proj[0].namebase
    if "w" in mode:
        fildxf, frw = p_gtkuti.thanGudOpenSaveFile(proj[2], suf, mes, mode,
            initialfile, initialdir)
    else:
        fildxf, frw = p_gtkuti.thanGudOpenReadFile(proj[2], suf, mes, mode,
            initialfile, initialdir)
    if frw == None: return Canc, Canc     # File open cancelled
    return path(fildxf), frw


def thanTxtsave(proj, mes, suf=".txt"):
    "Opens a text file for saving something."
    fildir = thanfiles.getFiledir()
    while True:
        fildxf = p_gtkuti.thanGudGetSaveFile(proj[2], suf, mes,
            proj[0].namebase, initialdir=fildir)
        if fildxf == None: proj[2].thanGudCommandCan(); return Canc      # Export cancelled
        fildxf = path(fildxf)
        try:                 fout = fildxf.open("w")
        except IOError, why: mm(proj[2], why, T["Open failed"], ERROR)   # (Gu)i (d)ependent
        else:                break
    return fout


#=============================================================================

def thanPlotPdf(proj):
    "Plots drawing to pdf file."
    try:
        import pyx
    except ImportError, e:
        t = "Python library module pyx is probably not installed:\n%s" % (e,)
        return proj[2].thanGudCommandCan(t)
    fildir = thanfiles.getFiledir()
    than = None
    while True:
        fildxf = p_gtkuti.thanGudGetSaveFile(proj[2], ".pdf", T["Plot to pdf file"],
            initialfile=proj[0].namebase, initialdir=fildir)
        if fildxf == None: del than; proj[2].thanGudCommandCan(); return   # Export cancelled
	fildxf = path(fildxf)
	try:
	    fout = fildxf.open("w")
	    fout.close()
        except IOError, why:
	    mm(proj[2], why, T["Open failed"], ERROR)        # (Gu)i (d)ependent
	    continue
	if than == None: than = proj[1].thanPlotPdf(1.0)
	try:
	    than.dc.writePDFfile(fildxf)
	except IOError, why:
	    mm(proj[2], why, T["Write failed"], ERROR)       # (Gu)i (d)ependent
	    continue
	break
    del than
    proj[2].thanGudCommandEnd(T["Pdf file has been created."], "info")


def thanPlotPilold(proj):
    "Exports to PIL image."
    fpath = proj[0].parent / proj[0].namebase + ".bmp"
    win = thantkdia.ThanTkExppil(proj[2], fpath, title=T["Export to Image: specifications"])
    if win.result == None: proj[2].thanGudCommandCan(); return                      # Export cancelled
    fpath, mode, width, height, drwin = win.result
    try:
        proj[1].thanExpPil(fpath, mode, width, height, drwin)
    except IOError, why:
        return proj[2].thanGudCommandCan("%s:\n%s" % (T["Image could not be exported"], why))
    proj[2].thanGudCommandEnd(T["Image has been exported."], "info")


def thanPlotPil(proj):
    "Exports to PIL image."
    win = thantkdia.ThanTkExppil(proj[2], vals=None, cargo=proj, title=T["Export to Image: specifications"])
    v = win.result
    if v == None: return proj[2].thanGudCommandCan()  # Export cancelled
    try:
#        proj[1].thanExpPil(fpath, mode, width, height, drwin)
        proj[1].thanExpPil(v.filIm, v.choMode, v.entWidth, v.entHeight, v.choPlotCode)
    except IOError, why:
        return proj[2].thanGudCommandCan("%s:\n%s" % (T["Image could not be exported"], why))
    proj[2].thanGudCommandEnd(T["Image has been exported."], "info")
