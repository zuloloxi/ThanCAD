from .jorpath import path

def getPrefix(fn):
    "Convert fn to path and get the prefix of fn."
    pro = path(fn)
    return pro.parent / pro.namebase


def getSufix(fn):
    "Gets the suffix of a fn, and convert it to path"
    return path(fn).ext


def putOptSufix(fn, suf=".txt"):
    "Transform fn to path and if fn has no suffix put the suffix suf."
    fn = path(fn)
    ext = fn.ext
    if ext =="":
        fn = fn.parent / fn.namebase + suf
    return fn


def putSufix(fn, suf=".txt"):
    "Convert fn to path and put the suffix suf."
    return getPrefix(fn) + suf
