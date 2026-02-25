"""\
This module contains a script which updates the title, version, author and other
information of all the source files of a python program. The information is
written as comments in the beginning of every source file.
"""
descMod = __doc__

import sys
#from typing import Dict, TextIO, Iterable, Union, Callable, Optional
#try: from typing import Protocol
#except: from typing_extensions import Protocol

import p_ggen, p_gtkwid
from . import thanvers

#class ProtPrt(Protocol):
    #def __call__(self, t: str, tags: Optional[str]=None) -> None: pass


#frw:Dict[str, TextIO] = {}
frw = {}
winmain = None
#prg:ProtPrt = p_ggen.prg
prg = p_ggen.prg
sourceDir = ""


#def thanVersUpdate(thanCadAbout:str, title:str) -> None:
def thanVersUpdate(thanCadAbout, title, suf="*.py"):
    "Main routine."
    import p_gfil
    openFiles()
    try:
        doversion(thanCadAbout, title, suf)
    except BaseException as e:
        raise
        p_gfil.er1s("\n%s:\n%s" % (p_ggen.Tgui["Error while executing program"], e), "can")
    p_gfil.closeFiles1()                        #Not reentrant


#def doversion(thanCadAbout:str, title:str) -> None:
def doversion(thanCadAbout, title, suf):
    "Main function."
    global sourceDir
    prg("source path: %s" % (sourceDir,), "info")
    prg("excluded directories: %s" % (",".join(p_ggen.thancadrel.excluded),), "info")
    p_ggen.thancadrel.excludedmatch.add("thanprofflf")
    prg("excluded matched directories: %s" % (",".join(p_ggen.thancadrel.excludedmatch),), "info")
    prg("excluded matched directories with numbers: %s" % (",".join(p_ggen.thancadrel.excludedmatchnumber),), "info")
    prg("-----------------------------------------------------------------------------")
    if winmain is None: a = p_ggen.inpNo("Proceed with update (enter=yes)?", True)
    else:               a = p_gtkwid.xinpNo(winmain, "Proceed with update (enter=yes)?", True)
    if not a: return
    thanUpdateSources(sourceDir, thanCadAbout, title, suf)
    prg("-----------------------------------------------------------------------------")
    prg("Sources have been updated as .new files.", "info")
    lineCount(sourceDir, suf)
    if winmain is None:
        a = p_ggen.inpNo("Proceed with replace (enter=no)?", False)
    else:
        winmain.showEnd()
        a = p_gtkwid.xinpNo(winmain, "Proceed with replace (enter=no)?", False)
    if a:
        rotateSources(sourceDir, suf)
        prg("done", "info")
        prg("-----------------------------------------------------------------------------")
        lineCount(sourceDir, suf)

#==========================================================================

#def thanUpdateSources(sourceDir:str, thanCadAbout:str, title:str) -> None:
def thanUpdateSources(sourceDir, thanCadAbout, title, suf):
    "Updates the version number, description and license in the sources."
    for fp in p_ggen.thancadrel.iterfpy(sourceDir, suf):
        prg(fp)
        fInp = open(fp, "r", errors="surrogateescape")
        iterInp = iter(fInp)
        fOut = open(fp+".new", "w", errors="surrogateescape")
        __skipOldDoc(iterInp, fOut, suf)
        __writeNewDoc(fOut, thanCadAbout, title, suf)
        __writeRest(iterInp, fOut)
        fInp.close()
        fOut.close()

#==========================================================================

#def rotateSources(sourceDir: str) -> None:
def rotateSources(sourceDir, suf):
    "Renames the previously created *.py.new files to *.py files."
    for f in p_ggen.thancadrel.iterfpy(sourceDir, suf):
        filbak = __getBackupName(f)
        f.rename(filbak)
        fnew = f + ".new"
        fnew.rename(f)

#==========================================================================

#def lineCount(sourceDir:str) -> None:
def lineCount(sourceDir, suf):
    "Counts all the lines in .py files recursively."
    n = 0
    for f in p_ggen.thancadrel.iterfpy(sourceDir, suf):
        with open(f, errors="surrogateescape") as fr:
            for dl in fr:
                n += 1
    prg("Total line count=%s" % (n,), "info")

#==========================================================================

#def __getBackupName(fp:p_ggen.path) -> p_ggen.path:
def __getBackupName(fp):
    "Finds a backup name for the file fp, which does not already exist."
    filnam = fp+".bak"
    if not filnam.exists(): return filnam
    for i in range(10):
        filnam = p_ggen.path("%s.bk%d" % (fp, i))
        if not filnam.exists(): return filnam
    raise IOError(fp+": Can not create backup file.")

#==========================================================================

#def __skipOldDoc (iterInp:Iterable[str], fOut:TextIO) -> None:
def __skipOldDoc (iterInp, fOut, suf):
    "Skips the doc string which must be long format string and at the first line."
    import p_gfil
    for dl in iterInp:
        if dl.rstrip() == thanvers.SENTCOM: break
        fOut.write(dl.rstrip()+'\n')
    else:
        p_gfil.er1s("    Sentinel comment not found at the beginning of file!")

    for dl in iterInp:
        if dl.rstrip() == thanvers.SENTCOM: break
    else:
        p_gfil.er1s("    Sentinel comment not found before end of file!")

    if suf != "*.py": return   #Only Python scripts have a documentation string
    for dl in iterInp:
        if dl.rstrip() == '"""\\': break
    else:
        p_gfil.er1s("    Doc string not found before end of file!")

    for dl in iterInp:
        break
    else:
        p_gfil.er1s("    Doc string does not exist!")

#==========================================================================

#def __writeNewDoc (fOut:TextIO, thanCadAbout:Iterable[str], title:str) -> None:
def __writeNewDoc (fOut, thanCadAbout, title, suf):
    "Writes description of the project and the new doc string."
    for dl in thanCadAbout: fOut.write(dl)
    fOut.write('\n')
    if suf != "*.py": return   #Only Python scripts have a documentation string
    fOut.write('"""\\\n')
    fOut.write(title+"\n")

#==========================================================================

#def __writeRest (iterInp:Iterable[str], fOut:TextIO) -> None:
def __writeRest (iterInp, fOut):
    "Copies the rest of the source file."
    for dl in iterInp:
        fOut.write(dl.rstrip()+'\n')

#==========================================================================

#def openFiles() -> None:
def openFiles():
    "Opens files for the program."
    import p_gfil
    global frw, winmain, prg
    p_gfil.setPar(openfileParx)
    p_gfil.openFile1(0, ' ', ' ', 0, 'Πρόγραμμα αντικατάστασης έκδοσης σε αρχεία κώδικα (python, octave etc)')
    frw = p_gfil.openFile1(998, ' ', ' ', 0, ' ')
    winmain, prg1, _ = p_gfil.openfileWinget()
    if winmain is not None: prg = prg1


#def openfileParx (icod1: int, un:Union[TextIO, ProtPrt, object]) -> None:
def openfileParx (icod1, un):
    global sourceDir
    if p_ggen.Pyos.Windows: sourceDir1 = p_ggen.path(".\\")  # type: ignore
    else:                   sourceDir1 = p_ggen.path(".").expand()
#---Read parameters from keyboard
    if icod1 == 0:
        prg(' ')
        sourceDir = p_ggen.inpStrB("Φάκελλος αρχείων κώδικα (enter=%s): " % sourceDir1, sourceDir1)
        sourceDir = p_ggen.path(sourceDir).expand().abspath()
#---Read parameters from unit un (file="mediate.tmp")
    elif icod1 == 1:
        assert isinstance(un, TextIO)
        sourceDir = p_ggen.medStr(un, "Φάκελλος αρχείων κώδικα=", sourceDir1)
        sourceDir = p_ggen.path(sourceDir).expand().abspath()
#---Read parameters from xwin
    elif icod1 == 3:
        assert isinstance(un, object)
        sourceDir = p_gtkwid.thanGudGetDir(un, "Φάκελλος αρχείων κώδικα", initialdir=sourceDir1)
        if sourceDir is None: sys.exit()
        sourceDir = p_ggen.path(sourceDir).expand().abspath()
    elif icod1 == 2:
        #assert isinstance(un, TextIO)
        un.write("%s\n" % (sourceDir,))
#---messages
    elif icod1 < 0:
        prt = un
        prt(descMod)  # type: ignore
    else:
        assert False, 'Sr openFilePar: Fildat library error: unknown code!'
