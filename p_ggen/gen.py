# -*- coding: iso-8859-7 -*-
from __future__ import print_function
from .py23 import input, xrange
#from builtins import input
#from past.builtins import xrange
import sys, platform, os

class RecordedError(Exception): pass
class ThanLayerError(Exception): pass
class ThanImportError(Exception):  pass

class Struct(object):
    "Each instance of this class is like a C struct."

    def __init__(self, name="<Unnamed>", **kw):
        "Just save the name."
        self.name = name
        self.__dict__.update(kw)

    def __str__(self):
        "Return the name of the structure."
        return self.name

    def anal(self):
        "Return an analytic list of all structure variables and their values as a string."
        s = ["Structure %s at: %s" % (self.name, object.__str__(self))]
        for key,val in self.__dict__.items():  #OK for python 2, 3
            if key.startswith("_Struct__"): continue     # Avoid private variables
            s.append("%s = %s" % (key, val))
        return "\n".join(s)

    def clone(self):
        "Make an identical copy."
        import copy
        return copy.deepcopy(self)

    def update(self, other):
        "Shallow copy of all attributes from another object except name, private attributes and special attributes."
        if not isinstance(other, self.__class__): raise TypeError("Not a %s object" % (self.__class__,))
        d = self.__dict__
        for k,v  in other.__dict__.items(): #OK for python 2, 3
            if k.startswith("__"): continue
            if k == "name": continue
            d[k] = v

    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        if not isinstance(other, self.__class__): return True
        return self.__dict__ != other.__dict__


class ThanStub:
    "This class saves a function and its arguments for a later call."

    def __init__(self, fun, *args, **kw):
        "Save function and arguments."
        self.args = args
        self.kw = kw
#        self.fun = weakref.proxy(fun)
        self.fun = fun

    def __call__(self, *args, **kw):
        "Call the function with possible extra arguments."
        if len(args) > 0: args = self.args+args
        else: args = self.args
        if len(kw) > 0: kw.update(self.kw)
        else: kw = self.kw
        return self.fun(*args, **kw)


class Null:
    "This class does nothing."
    def __init__(self, *args, **kw): pass
    def __getattr__(self, name): return self
    def __call__(self, *args, **kw): return self
    def __nonzero__(self): return 0



Canc = Struct("<Cancel>")
Pyos = Struct("Platform determination")
mach = sys.platform.lower()
Pyos.Windows = mach == "win32" or mach == "win64"       #If we run Windoze
Pyos.Freebsd = "freebsd" in mach                        #If we run Freebsd
Pyos.Openbsd = "openbsd" in mach                        #If we run Openbsd
Pyos.Linux = "linux" in mach                            #If we run Linux
Pyos.Macos = 'darwin' in mach
Pyos.Python3 = sys.version_info.major == 3

mach = platform.machine().lower()
Pyos.Amd64 = ("x86" in mach or "amd" in mach) and "64" in mach  #If machine is x86-64 compatible (OS may still run in 32bits)
del mach
Pyos.Os64 = sys.maxsize > 2**32     #This means that the OS is running at 64bits (on a 64bit processor of course)


############################################################################
############################################################################

#MODULE LEVEL ROUTINES

#============================================================================

def doNothing(*args, **kw):
    "This function does nothing at all."
    pass

def floate(a):
    try: return float(a.replace(",", "."))
    except ValueError: return None

def inte(a):
    try: return int(a)
    except ValueError: return None

def complexe(a):
    try: return complex(a.replace(",", "."))
    except ValueError: return None

#===========================================================================

def _inpGen(text, fun, other=()): 
    "Gets a text and validates it with fun; if text is in other it is valid and it is returned."
    if Pyos.Windows:
        gc = gw2d
        text = "".join([gc.get(c, c) for c in text])
    while 1:
        s = input(text)
        s1 = s.strip()
        if s1 in other: return s1
        try: return fun(s)
        except ValueError: pass
        print("Illegal value. Try again.")

def inpFloat(text,  other=()): return  _inpGen(text, lambda t: float(t.replace(",",".")), other)
def inpComplex(text,other=()): return  _inpGen(text, lambda t: complex(t.replace(",",".")), other)
def inpInt(text,    other=()): return  _inpGen(text, int, other)
def inpText(text,   other=()): return  _inpGen(text, ing, other)

#===========================================================================

def xfrangec(start, end, step=1):
    "Implements float xrange - which includes start and end."
    start = float(start); end = float(end); step = float(step)
    a = start
    if step > 0:
        if start > end: return
        while a < end:
            yield a
            a += step
    else:
        if start < end: return
        while a > end:
            yield a
            a += step
    yield end

def frangec(start, end, step=1):
    "Implements float range - which includes start and end."
    return list(xfrangec(start, end, step))

def xfrange(start, end, step=1):
    "Implements float xrange."
    start = float(start); end = float(end); step = float(step)
    a = start
    if step > 0:
        if start > end: return
        while a < end:
            yield a
            a += step
    else:
        if start < end: return
        while a > end:
            yield a
            a += step

def frange(start, end, step=1):
    "Implements float range - which includes start and end."
    return list(xfrange(start, end, step))

def iterby2(iterable):
    """Returns pairs of consecutive elements of iterable (non exclusive).

    For example: by2((1, 3, 7, -5)) returns:
    (1,3) then (3,7) then (7,-5)
    """
    it = iter(iterable)
    val1 = next(it)
    for val2 in it:
        yield val1, val2
        val1 = val2


def iterby2c(iterable):
    """Returns pairs of consecutive elements of iterable cyclically.

    For example: by2((1, 3, 7, -5)) returns:
    (1,3) then (3,7) then (7,-5) then (-5,1)
    """
    it = iter(iterable)
    valfirst = val1 = next(it)
    for val2 in it:
        yield val1, val2
        val1 = val2
    yield val2, valfirst

def iterby3(iterable):
    """Returns triples of consecutive elements of iterable (non exclusive).

    For example: by3((1, 3, 7, -5, 'a')) returns:
    (1,3,7) then (3,7,-5) then (7,-5,'a')
    """
    it = iter(iterable)
    val1 = next(it)
    val2 = next(it)
    for val3 in it:
        yield val1, val2, val3
        val1 = val2
        val2 = val3

def any1(iterable):
    "Gets the first iterable (for mappings gets an arbitrary element; raises ValueError if empty."
    for a in iterable:
        return a
    else:
        raise ValueError("any1() arg is an empty iterable")

def groupitems(seq, key):
    "Group all elements of seq with the same key together; key is a function; return key, keyseq pairs."
    import collections
    groupbykey = collections.defaultdict(list)
    for e in seq:
        ekey = key(e)
        groupbykey[ekey].append(e)
    return groupbykey.items()
#def group(seq, key):    #Only python 3
#    "Group all elements of seq with the same key together; key is a function; return only the grouped elements."
#    for ekey, keyseq in groupitems:
#        yield from keyseq

#===========================================================================

def fnum(root):
    """Returns the last integer number in a string, or zero.

    For example all of the following strings return the integer 123:
    "123",  "a123", "123b", "a123b", "55a123b", "c55da123b", "5_123"
    If no digits are found the function returns None.
    This function is very slow. Thus don't use fit for many
    computations."""

    for i in xrange(len(root)-1, -1, -1):
        if root[i].isdigit(): break
    else: return None
    for j in xrange(i, -1, -1):
        if not root[j].isdigit(): return int(root[j+1:i+1])
    return int(root[:i+1])


def configFile(confname, appdir="thancad"):
    "Returns the path of confname, placing it into appdir."
    #Please see appdata.odt in directory developer
    from .jorpath import path
    appdir = thanUnunicode(appdir)       # If it is unicode it is converted to win greek
    if Pyos.Windows:
        try:
            import win32com.shell
            from win32com.shell import shellcon, shell
            f1 = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        except ImportError: # quick semi-nasty fallback for non-windows/win32com case
            f1 = __homeorcurrent()
    else:
        f1 = os.environ.get("XDG_CONFIG_HOME")  # this should return: /home/a12/.config
        if f1 is None:
            f1 = __homeorcurrent()   #if XDG_CONFIG_HOME is not set, use '.config' in home directory
            f1 = path(f1) / ".config"
    f1 = thanUnunicode(f1)       # If it is unicode it is converted to win greek
    f = path(f1) / appdir
    try: f.makedirs1()
    except OSError as why: return None, why
    return f / confname, ""


def __homeorcurrent():
    "Return home directory or current directory if this fails."
    from . import jorpath
    f1 = "~"
#    f1 = "$windir"
    f = jorpath.path(f1).expand()
    if f == f1:
        f = f.getcwd()   # expand failed; use current directory as homedir
    return f


_iuniqfileprev = 0
def uniqfile(pref, suf="", stat="w", n=3, inum=-1):
    "Opens a unique file by appending a unique number to prefix."
    from .jorpath import path
    global _iuniqfileprev
    form = "%s%%0%dd%s" % (pref, n, suf)
    nmax = 10**n

    if inum >= 0: _iuniqfileprev = inum
    _iuniqfileprev += 1
    i = _iuniqfileprev % nmax    #Try 1 after previous
    fn = path(form % (i,))
    if not fn.exists():
        try: fw = open(fn, stat)
        except IOError: pass
        else: return fw

    for _iuniqfileprev in xrange(1, nmax):          #Try all
        fn = path(form % (_iuniqfileprev,))
        if not fn.exists():
            try: fw = open(fn, stat)
            except IOError: pass
            else: return fw
    _iuniqfileprev = 0  #Could not open file; all numbers are already used
    return None

def uniqdir(pref, suf="", stat="w", n=3, inum=-1):
    "Created a unique directory by appending a unique number to prefix."
    from .jorpath import path
    global _iuniqfileprev
    form = "%s%%0%dd%s" % (pref, n, suf)
    nmax = 10**n

    if inum >= 0: _iuniqfileprev = inum
    _iuniqfileprev += 1
    i = _iuniqfileprev % nmax    #Try 1 after previous
    fn = path(form % (i,))
    if not fn.exists():
        try: fn.mkdir()
        except IOError: pass
        else: return fn

    for _iuniqfileprev in xrange(1, nmax):          #Try all
        fn = path(form % (_iuniqfileprev,))
        if not fn.exists():
            try: fn.mkdir()
            except IOError: pass
            else: return fn
    _iuniqfileprev = 0  #Could not create dir; all numbers are already used
    return None

#===========================================================================

def dictInvert(a):
    "Inverts a dictionary; values become keys and keys become values."
    b = {}
    for key,val in a.items():  #OK for python 2, 3
        b[val] = key
    return b

def rdict(kw, *allowed):
    "Returns an reduced dictionary which contains only the keys *allowed."
    kw1 = {}
    for key in allowed:
        try: kw1[key] = kw[key]
        except KeyError: pass
    return kw1

def isString(t):
        "Check if argument is string-like object."
        try: t+""
        except: return False
        else:   return True

if Pyos.Python3:
    __textchars = bytes([7,8,9,10,12,13,27] + list(range(0x20, 0x100)))
    __textcharsgr = bytes([7,8,9,10,12,13,27] + list(range(0x20, 0x100))+
        list("ΪΫΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΆΈΉΊΌΎΏΪΫΣΐΰαβγδεζηθικλμνξοπρστυφχψωάέήίόύώϊϋς".encode("iso-8859-7")))
else:
    __textchars = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100))+
        list("ΪΫΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΆΈΉΊΌΎΏΪΫΣΐΰαβγδεζηθικλμνξοπρστυφχψωάέήίόύώϊϋς"))
isStringBinary = lambda bytes1: bool(bytes1.translate(None, __textchars))
isGreekStringBinary = lambda bytes1: bool(bytes1.translate(None, __textcharsgr))

#===========================================================================
#GREEK handling routines

gcaw = "ΙΥΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΑΕΗΙΟΥΩΙΥΣ"
gcw  = "ΪΫΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΆΈΉΊΌΎΏΪΫΣ"
gsw  = "ΐΰαβγδεζηθικλμνξοπρστυφχψωάέήίόύώϊϋς"

ecx  = "IYABGDEZHQIKLMNJOPRSTYFXCWAEHIOYWIYS"
esx  = "iuabgdezhqiklmnjoprstufxcwaehiouwius"


from .grdos import *
gw2d = dict(zip(gcw, gcd))
gw2d.update(dict(zip(gsw, gsd)))
gd2w = dict(zip(gcd, gcw))
gd2w.update(dict(zip(gsd, gsw)))

gws2c = dict(zip(gsw, gcaw))
gws2c.update(dict(zip(gcw, gcaw)))   #Thanasis2013_10_13
gwc2s = dict(zip(gcw, gsw))

grwsh = dict(zip(gcw, ecx))
grwsh.update(dict(zip(gsw, esx)))
grdsh = dict(zip(gcd, ecx))
grdsh.update(dict(zip(gsd, esx)))

del gcaw, gcw, gsw, gcd, gsd, ecx, esx

def gr2upper(fr):
    "Convert to windows greek capital (no carets allowed)."
    gc = gws2c
    return "".join([gc.get(c, c) for c in fr])
def gr2lower(fr):
    "Convert to windows greek capital."
    gc = gwc2s
    return "".join([gc.get(c, c) for c in fr])
def grwin2dos(fr):
    "Convert to DOS greek."
    gc = gw2d
    return "".join([gc.get(c, c) for c in fr])
def grdos2win(fr):
    "Convert to Windows greek."
    gc = gd2w
    return "".join([gc.get(c, c) for c in fr])


if Pyos.Python3:
    def greeklish(t, blank=None):
        "Convert greek (unicode) text to equivalent with latin characters."
        t = "".join([grwsh.get(c, c) for c in t])
        if blank is None: return t
        return t.replace(" ", blank)
    def guessGreekEncoding(data):
        "Given bytes data, try to guess the greek encoding."
        encs = "iso-8859-7", "utf8", "cp737"     #cp737 are old DOS greek
        nmax = -1
        encmax = ""
        for i,enc in enumerate(encs):
            text = data.decode(enc, errors="replace")
            #print()
            #print(enc)
            #print("----------------------------------------------")
            #b = text.encode("iso-8859-7", errors="backslashreplace")
            #s = b.decode("iso-8859-7")
            #print(s)
            #print("----------------------------------------------")
            #greekbytes.clear()
            #greekbytes.update(gcw.encode(enc))
            #greekbytes.update(gsw.encode(enc))
            n = 0
            for c in text:
                if c in grwsh: n += 1
            #print(enc, n)
            if n > nmax:
                nmax = n
                encmax = enc
        return encmax
else:
    def greeklish(t, blank=None):
        "Convert greek text to equivalent with latin characters."
        t = thanUnunicode(t)       # If it is unicode it is converted to win greek
        nd = len([1 for c in t if c in grdsh])
        nw = len([1 for c in t if c in grwsh])
        if nw >= nd:
            t = "".join([grwsh.get(c, c) for c in t])
            if nd > 0: t = "".join([grdsh.get(c, c) for c in t])   #Change remaining greek chars (not chars already transformed to latin)
        else:
            t = "".join([grdsh.get(c, c) for c in t])
            if nw > 0: t = "".join([grwsh.get(c, c) for c in t])   #Change remaining greek chars (not chars already transformed to latin)
        if blank is None: return t
        return t.replace(" ", blank)

def greeklishpath(fn, blank="_", slash="_", dot=None, gtlt="", quote="", qmark=""):
    "Convert name to greeklish, lower, strip, replace slash, replace blank, replace dots and return path object."
    from .jorpath import path
    t = fn.strip()
    if slash is not None: t = t.replace("/", slash).replace("\\", slash)
    if dot is not None: t = t.replace(".", dot)
    if gtlt is not None: t = t.replace("<", gtlt).replace(">", gtlt)
    if quote is not None: t = t.replace("'", quote).replace('"', quote).replace("`", quote)
    if qmark is not None: t = t.replace("?", qmark)
    return path(greeklish(t, blank).lower())

def prgnone(fr, tags=()): pass    #Prints nothing


#Thanasis2016_06_22: The followiung are for compatibility with programs running python2

def prg(fr, tags=()):
    "Print converting to DOS greek only if we run windows (tags is for compatibility)."
    print(fr)
def prints(fr):
    "Print without newline converting to DOS greek only if we run windows."
    sys.stdout.write(fr)
def tog(fr):
    "Convert to DOS greek only if we run windows."
    return fr
def togi(fr):
    "Convert DOS greek only to WINDOWS greek, onlyif we run windows."
    return fr
def ing(fr):
    "Convert to linux greek only if we read from DOS (we run windows)."
    return fr

#===========================================================================
#Unicode handling routines

import codecs

def thanUnunicode(t):
    "Convert unicode to string."
    if Pyos.Python3: return str(t)
    if not isinstance(t, unicode): return str(t)
    return thanUnunicode1(t, "replace")[0]

def thanUnicode(t):
    "Convert to unicode."
    if Pyos.Python3:
        if isinstance(t, str): return t
        if isinstance(t, bytes): return t.decode(encoding=thanGetEncoding())
        if isinstance(t, bytearray): return t.decode(encoding=thanGetEncoding())
        return str(t)
    if isinstance(t, unicode): return t
    return thanUnicode1(str(t), "replace")[0]

def thanGetDefaultEncoding():
    "Get the system default encoding; try various methods."
    #Try locale default encoding
    import locale
    temp = locale.getdefaultlocale()
    try:
        enc = temp[1]
    except:
        pass
    else:
        if isString(enc) and enc.strip() != "": return enc.lower()
    #Try file system encoding
    enc = sys.getfilesystemencoding()
    if isString(enc) and enc.strip() != "":
        enc = enc.lower()
        if Pyos.Windows and enc == "mbcs":   #Multi Byte Character Set: does not say anything useful
            enc = "utf8"                     #..Thus we set utf8 (the most probable)
        return enc.lower()
    #All failed; guess according to OS
    if Pyos.Windows:
        enc="utf8"
    else:
        enc="utf8"
    return enc


def thanSetEncoding(enc):
    "Set new encoding."
    ununi = codecs.getencoder(enc)   # This will potentialy cause an exception without..
    uni   = codecs.getdecoder(enc)   # .. changing current encoding
    global thanEncoding, thanUnunicode1, thanUnicode1
    thanEncoding   = enc
    thanUnunicode1 = ununi
    thanUnicode1   = uni

def thanGetEncoding():
    "Return current encoding."
    return thanEncoding

def griso2utf(fr):
    "Convert iso8859-7 Greek to utf8."
    enc = thanEncoding
    if enc != "iso-8859-7": thanSetEncoding("iso-8859-7")
    t = thanUnicode(fr)
    thanSetEncoding("utf8")
    t = thanUnunicode(t)
    if enc != "utf8": thanSetEncoding(enc)
    return t

def grutf2iso(fr):
    "Convert utf8 to iso8859-7 Greek."
    enc = thanEncoding
    if enc != "utf8": thanSetEncoding("utf8")
    t = thanUnicode(fr)
    thanSetEncoding("iso-8859-7")
    t = thanUnunicode(t)
    if enc != "iso-8859-7": thanSetEncoding(enc)
    return t


def fsurrogateReplace(exc):
    """Error handler which calls surrogateescape error handler and if this fails then the replace error handler.

    Here is the deal:
    a. We use cp737 codec (DOS Greek) to convert from DOS Greek to unicode.
    b. Non Greek characters (or more precisely characters not representable
       by the Greek character set are mapped to a private space in the
       unicode space by surrogatereplace errors handler.
    c. When these characters are converted from unicode to iso-8859-7
       they take their original byte value by the surrogatereplace errors
       handler.
    d. However, a character, which is not a Greek alphabetic character but
       another character (for example the dos Greek equivalent of '\u256c')
       which happens to be in the DOS Greek character set is converted to
       unicode character set.
    e. When this character is converted to iso-8859-7, it has no equivalent
       and an exception is raised by the surrogatereplace errors handler.
    f. A solution is to call the replace errors handler after that.
       Thus the surrogatereplace handler which is implemented by this
       function.
    """
    import codecs
    fsurrogateescape = codecs.lookup_error("surrogateescape")
    freplace = codecs.lookup_error("replace")
    try:
        return fsurrogateescape(exc)
    except Exception as e:
        return freplace(e)
def makeSurrogatereplace():
    "Create the surrogatereplace errors handler (codecs), if not found."
    import codecs
    try:
        codecs.lookup_error("surrogatereplace")
        return
    except LookupError:
        pass
    codecs.register_error("surrogatereplace", fsurrogateReplace)


#thanSetEncoding("iso-8859-7")
thanSetEncoding(thanGetDefaultEncoding())


############################################################################
############################################################################

#MODULE LEVEL ROUTINES - TEST CODE

#===========================================================================

#def testFrangec():
#    print("frangec"
#    print("10  , 0        :", frangec(10, 0))
#    print(" 0  ,10   , 2  :", frangec(0, 10, 2))
#    print(" 0  ,10   , 3  :", frangec(0, 10, 3))
#    print(" 0.1,10.99, 2.7:", frangec(0.1, 10.99, 2.7))
#
#    print(" 0   ,10  ,-1  :", frangec(0, 10, -1))
#    print("10   , 0  ,-2  :", frangec(10, 0, -2))
#    print("10   , 0  ,-3  :", frangec(10, 0, -3))
#    print("10.99, 0.1,-2.7:", frangec(10.99, 0.1, -2.7))
#    print("frange"
#    print("10  , 0        :", frange(10, 0))
#    print(" 0  ,10   , 2  :", frange(0, 10, 2))
#    print(" 0  ,10   , 3  :", frange(0, 10, 3))
#    print(" 0.1,10.99, 2.7:", frange(0.1, 10.99, 2.7))
#
#    print(" 0   ,10  ,-1  :", frange(0, 10, -1))
#    print("10   , 0  ,-2  :", frange(10, 0, -2))
#    print("10   , 0  ,-3  :", frange(10, 0, -3))
#    print("10.99, 0.1,-2.7:", frange(10.99, 0.1, -2.7))

#===========================================================================

#def testFnum():
#    ex = ("123",  "a123", "123b", "a123b", "55a123b", "c55da123b", "5_123", "aaa")
#    for t in ex: print(t, fnum(t))


############################################################################
############################################################################

#MODULE LEVEL CODE

#---Module initialisation (This code is executed only once)---------


#===========================================================================

#if __name__ == "__main__":
#    testGon()
#    testFrangec()
#    testFnum()
#    print(complexe("10"))
#    print(complexe("ff34"))
#    print(complexe("10j"))
#    print(complexe("5+10j"))
#    print(complexe(20))
#    print(complexe(50.220))
