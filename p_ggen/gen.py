# -*- coding: iso-8859-7 -*-
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


#Canc is sentinel object, which is used as a return value from functions.
#It means that the user cancelled the current operation.
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
Pyos.Pi = "armv7" in mach     #Thanasis2018_01_02
del mach
Pyos.Os64 = sys.maxsize > 2**32     #This means that the OS is running at 64bits (on a 64bit processor of course)


############################################################################
############################################################################

#MODULE LEVEL ROUTINES

#============================================================================

def importpackage(MODULE_NAME, MODULE_PATH):
    """Import module from arbitrary pathname as modulename; may be a package.

    The user must type import MODULE_NAME after the call to import package.
    https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path."""
    import sys
    import importlib.util
    #MODULE_PATH = "/path/to/your/module/__init__.py"
    #MODULE_NAME = "mymodule"
    spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module 
    spec.loader.exec_module(module)

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

def frange(start, end, step=1.0, tol=0.0):
    """Implements float range.

    if the last step before end is within tol*step distance from end, it is skipped."""
    assert tol>=0.0, "frange(): tolerance should be a non negative ratio."
    start = float(start); end = float(end); step = float(step); tol = float(tol)
    a = start
    if step > 0.0:
        if start > end: return
        while a < end-tol*step:
            yield a
            a += step
    else:
        if start < end: return
        while a > end-tol*step:   #Note tol>=0 and step < 0
            yield a
            a += step


def frangec(start, end, step=1.0, tol=0.0):
    """Implements float range - which includes start and end; tol is tolerance ratio.

    if the last step before end is within tol*step distance from end, it is skipped."""
    assert tol>=0.0, "frange(): tolerance should be a non negative ratio."
    start = float(start); end = float(end); step = float(step); tol = float(tol)
    a = start
    if step > 0.0:
        if start > end: return
        while a < end-tol*step:
            yield a
            a += step
    else:
        if start < end: return
        while a > end-tol*step:   #Note tol>=0 and step < 0
            yield a
            a += step
    yield end


def iterby2(iterable):
    """Returns pairs of consecutive elements of iterable (non exclusive).

    For example: by2((1, 3, 7, -5)) returns:
    (1,3) then (3,7) then (7,-5)
    """
    it = iter(iterable)
    try: val1 = next(it)         #Thanasis2024:05_02: This raises StopIteration and PEP 479 (2023) will cause a runtime error
    except StopIteration: return #Thanasis2024:05_02: workaround to end generator if iterable contains no elements.
    for val2 in it:
        yield val1, val2
        val1 = val2


def iterby2c(iterable):
    """Returns pairs of consecutive elements of iterable cyclically.

    For example: by2((1, 3, 7, -5)) returns:
    (1,3) then (3,7) then (7,-5) then (-5,1)
    """
    it = iter(iterable)
    try: valfirst = val1 = next(it) #Thanasis2024:05_02: This raises StopIteration and PEP 479 (2023) will cause a runtime error
    except StopIteration: return    #Thanasis2024:05_02: workaround to end generator if iterable contains no elements.
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
    try:          #Thanasis2024:05_02: This raises StopIteration and PEP 479 (2023) will cause a runtime error
        val1 = next(it)
        val2 = next(it)
    except StopIteration:
        return    #Thanasis2024:05_02: workaround to end generator if iterable contains no elements.
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

    for i in range(len(root)-1, -1, -1):
        if root[i].isdigit(): break
    else: return None
    for j in range(i, -1, -1):
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

    for _iuniqfileprev in range(1, nmax):          #Try all
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

    for _iuniqfileprev in range(1, nmax):          #Try all
        fn = path(form % (_iuniqfileprev,))
        if not fn.exists():
            try: fn.mkdir()
            except IOError: pass
            else: return fn
    _iuniqfileprev = 0  #Could not create dir; all numbers are already used
    return None


def fnequal(fna, fnb, fail=False):
    "Tests if 2 (binary) files are identical."
    nb = 1024*1024  # 1MB
    try:
        with open(fna, "rb") as fra, open(fnb, "rb") as frb:
            while True:
                a = fra.read(nb)       #Try to read 1MB
                b = frb.read(nb)       #Try to read 1MB
                if a != b: return False
                if len(a) < nb: break
        return True
    except IOError as why:
        if fail: raise
        prg("Could not access {} or {}:\n{}".format(fna, fnb, why), "can1")
        return False


def fnsize(fn, fail=False):
    "Find the size of (binary) file in bytes."
    nb = 1024*1024  # 1MB
    n = 0
    try:
        with open(fn, "rb") as fr:
            while True:
                b = fr.read(nb)       #Try to read 1MB
                n += len(b)
                if len(b) < nb: break
    except IOError as why:
        prg("Could not access {}:\n{}".format(fn, why), "can1")
        return -1
    return n

#===========================================================================

def getcpu():
    """Get a little more detailed description of the CPU.

    https://stackoverflow.com/questions/4842448/getting-processor-information-in-python"""
    import subprocess, re
    if platform.system() == "Windows":
        family = platform.processor()
        name = subprocess.check_output(["wmic","cpu","get", "name"]).decode()   #thanasis2024_09_12
        name = name.split("\n")[1].strip()    #thanasis2024_09_12
        return ' '.join([name, family])
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command ="sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).decode().strip()    #thanasis2024_09_12
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).decode()
        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub(".*model name.*:", "", line.strip(), 1)
    return platform.processor()   #default


def ncores():
    "Find the number of physical and logical cores."
    #https://askubuntu.com/questions/1292702/how-to-get-number-of-phy-logical-cores
    import subprocess
    try:
        t = subprocess.check_output(["lscpu"])
    except:
        #raise
        return None, None

    ithreads = icores = isockets = None
    for dline in t.decode().splitlines():
        try:
            if dline.startswith("Thread"):
                dl = dline.split()
                ithreads = int(dl[-1])
            elif dline.startswith("Core"):
                dl = dline.split()
                icores = int(dl[-1])
            elif dline.startswith("Socket"):
                dl = dline.split()
                isockets = int(dl[-1])
        except ValueError:
            #raise
            return None, None

    #print(ithreads, icores, isockets)
    if ithreads is None or icores is None or isockets is None or ithreads<=0 or icores<=0 or isockets<=0:
        return None, None
    nphysical = isockets * icores
    nlogical = nphysical * ithreads
    return nphysical, nlogical

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


from .grdos import gcd, gsd
from .grutf8 import gca8, gc8, gs8


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

gr8sh = dict(zip(gc8, ecx))
gr8sh.update(dict(zip(gs8, esx)))

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
        #Thanasis2022_02_16: The unicode character with dedimal code 769 ("Μ") is the
        #Combining Acute Accent, which mean that if it follows for example letter "a"
        #the letter "a" is acuted.
        #Thus we completely ignore this character
        t = t.replace(chr(769), "")
        t = "".join([gr8sh.get(c, c) for c in t])
        if blank is None: return t
        return t.replace(" ", blank)
    def guessGreekEncoding(data):
        "Given bytes data, try to guess the greek encoding."
        encs = "utf8", "iso-8859-7", "cp737"     #cp737 are old DOS greek
        nmin = None
        encmin = ""
        for i,enc in enumerate(encs):
            text = data.decode(enc, errors="surrogateescape")
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
                ic = ord(c)
                if 0xDC80 <= ic <= 0xDCFF: n += 1  #Thanasis2017_01_15 (surrogate characters)
            print(enc, n)
            if nmin is None or n < nmin:
                nmin = n
                encmin = enc
        return encmin
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

def greeklishpath(fn, blank="_", slash="_", dot=None, gtlt="", quote="", qmark="", colon="_", backslash="", comma="_"):
    "Convert name to greeklish, lower, strip, replace slash, replace blank, replace dots and return path object."
    from .jorpath import path
    t = fn.strip()
    if slash is not None: t = t.replace("/", slash)
    if backslash is not None: t = t.replace("\\", backslash)
    if dot is not None: t = t.replace(".", dot)
    if gtlt is not None: t = t.replace("<", gtlt).replace(">", gtlt)
    if quote is not None: t = t.replace("'", quote).replace('"', quote).replace("`", quote)
    if qmark is not None: t = t.replace("?", qmark)
    if colon is not None: t = t.replace(":", colon)
    if comma is not None: t = t.replace(",", comma)
    t = greeklish(t, blank)

    temp = []
    for t1 in t:
        if ord(t1) >= 128: t1 = "x"
        temp.append(t1)
    t = "".join(temp)
    return path(t.lower())

def prgnone(fr, tags=()): pass    #Prints nothing

def cls():
    """Clear screen.

    https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console"""
    print("\033c", end='')

def beep():
    """Make e beep sound.

    https://stackoverflow.com/questions/6537481/python-making-a-beep-noise"""
    print('\a', end="")


#Thanasis2016_06_22: The following are for compatibility with programs running python2

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
        if isinstance(t, bytes): return t.decode(encoding=thanGetEncoding(), errors="surrogateescape")
        if isinstance(t, bytearray): return t.decode(encoding=thanGetEncoding(), errors="surrogateescape")
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


def thanSetFileEncoding(enc):
    "Set new encoding."
    global thanFileEncoding
    thanFileEncoding = enc

def thanGetFileEncoding():
    "Return current encoding."
    return thanFileEncoding

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
       unicode space by surrogateescape errors handler.
    c. When these characters are converted from unicode to iso-8859-7
       they take their original byte value by the surrogateescape errors
       handler.
    d. However, a character, which is not a Greek alphabetic character, but
       another character (for example the dos Greek equivalent of '\u256c')
       which happens to be in the DOS Greek character set, is converted to
       unicode character set.
    e. When this character is converted to iso-8859-7, it has no equivalent
       and an exception is raised by the surrogateescape errors handler.
    f. A solution is to call the replace errors handler after the 
       surogateescape handler.
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


copyrightyear = 2025
def thanCopyright(iyear1):
      "Return Thanasis copyright."
      iyear2=copyrightyear
      return 'Copyright (c) {}-{} Dr. Thanasis Stamos, EMail: cyberthanasis@gmx.net'.format(iyear1, iyear2)
def dimCopyright(iyear1):
      "Return Dimitra copyright."
      iyear2=copyrightyear
      return 'Copyright (c) {}-{} Dr. Dimitra Vassilaki, EMail: dimitra.vassilaki@gmail.com'.format(iyear1, iyear2)


#thanSetEncoding("iso-8859-7")
thanSetEncoding(thanGetDefaultEncoding())
thanSetFileEncoding("utf8")
makeSurrogatereplace()


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
