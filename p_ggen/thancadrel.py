from jorpath import path

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
        for subdir1 in dirs(dir1, excluded):
            yield subdir1
