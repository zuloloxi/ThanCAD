from jorpath import path


def thancadirs(root):
    excluded = "var"
    excluded = set(root/dir1 for dir1 in excluded.split())
    for dir1 in dirs(root, excluded):
        yield dir1


def dirs(parent, excluded=()):
    yield parent
    for dir1 in parent.dirs():
        if dir1 in excluded: continue
        nam = dir1.namebase.lower()
        if nam == "cop": continue
        if nam == "copy": continue
        if nam[:2] == "ok":
            try: int(nam[2:])
            except ValueError: pass
            else: continue
        for subdir1 in dirs(dir1, excluded):
            yield subdir1
