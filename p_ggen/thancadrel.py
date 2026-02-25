from .jorpath import path
from .gen import Pyos, prg

excluded = set("other".split())
excludedmatch = set("cop copy fortran f95 ex developer".split())
excludedmatchnumber = "ok".split()   #This means ok[number]


def iterfpy(root, suf="*.py"):
    "Iterate through all the python sources of a program."
    for di in thancadirs(root):
        for fp in di.files(suf):
            yield fp


def thancadirs(root):
    excluded1 = set((root/dir1).abspath() for dir1 in excluded)
#    yield from dirs(root, excluded1)
    for dir1 in dirs(root, excluded1):
        yield dir1


def dirs(parent, excluded=()):
    yield parent
    for dir1 in parent.dirs():
        if dir1.abspath() in excluded: continue
        nam = dir1.namebase.lower()
        if nam in excludedmatch: continue
        matched = False
        for nam1 in excludedmatchnumber:
            n1 = len(nam1)
            if nam[:n1] != nam1: continue
            try:
                #int(nam[n1:])     #thanasis2022_06_13: commented out: it does not exclude ok09oldtoexe
                int(nam[n1:n1+1])  #thanasis2022_06_13: If it is fllowed by a digit..
            except ValueError:     #..it is excluded, for example ok09oldtoexe
                pass
            else:
                matched = True
                break
        if matched: continue
        for subdir1 in dirs(dir1, excluded):
            yield subdir1


def copyPylib(name, todir=".", fromdir=None, prt=prg):
    "Copy the *.py files of a Thanasis' python library (for example p_ggen) to the todir directory."
    if fromdir == None:
        if Pyos.Windows: fromdir = path("h:/libs/source_python")
        else:            fromdir = path("~/h/libs/source_python").expand().abspath()
    fromdir = path(fromdir)
    todir = path(todir)

    fromlibdir = fromdir/name
    if not (fromlibdir.exists() and fromlibdir.isdir()):
        prt("Library %s can not be found/accessed in %s" % (name, fromdir), "can1")
        return
    tolibdir = todir/name
    try:
        tolibdir.makedirs1()
    except Exception as e:
        prt("Library %s can not be created/accessed in %s:\n%s" % (name, todir, e), "can1")
        return

    for dir1 in thancadirs(fromlibdir):
        fns = dir1.files("*.py")
        if len(fns) < 1: continue
        dir1rel = fromlibdir.relpathto(dir1)
        todir1 = tolibdir/dir1rel
        todir1.makedirs1()
        for fn in fns:
            prt("copying %s" % (fn,))
            fnt = fn.basename()
            if fnt == "cpy.py" or fnt == "tobin.py": continue
            fnt = todir1/fnt
            fn.copyfile(fnt)


if __name__ == "__main__":
    copyPylib("p_gearth", "/home/a12/temp")
