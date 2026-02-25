from jorpath import path
from gen import Pyos, prg

excluded = "var other"
excludedmatch = "cop copy fortran f95 ok[number] ex developer"


def iterfpy(root):
    "Iterate through all the python sources of a program."
    for di in thancadirs(root):
        for fp in di.files("*.py"):
            yield fp


def thancadirs(root):
    excluded1 = set(root/dir1 for dir1 in excluded.split())
#    yield from dirs(root, excluded1)
    for dir1 in dirs(root, excluded1):
        yield dir1


def dirs(parent, excluded=()):
    yield parent
    for dir1 in parent.dirs():
        if dir1 in excluded: continue
        nam = dir1.namebase.lower()
        if nam == "cop": continue
        if nam == "copy": continue
        if nam == "fortran": continue
        if nam == "f95": continue
        if nam == "ex": continue
        if nam == "developer": continue
        if nam[:2] == "ok":
            try: int(nam[2:])
            except ValueError: pass
            else: continue
        for subdir1 in dirs(dir1):
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
    except Exception, e:
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
