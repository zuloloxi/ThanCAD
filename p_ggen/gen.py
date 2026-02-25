# -*- coding: iso-8859-7 -*-
import sys, platform

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
        for key,val in self.__dict__.iteritems():
            if key.startswith("_Struct__"): continue     # Avoid private variables
            s.append("%s = %s" % (key, val))
        return "\n".join(s)

    def clone(self):
        "Make an identical copy."
        import copy
        return copy.deepcopy(self)

    def update(self, other):
        "Shallow copy of all attributes from another object except name, private attributes and special attributes."
        if not isinstance(other, self.__class__): raise TypeError, "Not a %s object" % (self.__class__,)
        d = self.__dict__
        for k,v  in other.__dict__.iteritems():
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
        s = raw_input(text)
	s1 = s.strip()
	if s1 in other: return s1
        try: return fun(s)
	except ValueError: pass
	print "Illegal value. Try again"

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

    val1 = it.next()

    for val2 in it:
        yield val1, val2
        val1 = val2

def iterby3(iterable):
    """Returns triples of consecutive elements of iterable (non exclusive).

    For example: by3((1, 3, 7, -5, 'a')) returns:
    (1,3,7) then (3,7,-5) then (7,-5,'a')
    """
    it = iter(iterable)
    val1 = it.next()
    val2 = it.next()
    for val3 in it:
        yield val1, val2, val3
        val1 = val2
        val2 = val3

def any1(iterable):
    "Gets the first iterable (for mappings gets an arbitrary element; raises ValueError if empty."
    for a in iterable:
        return a
    else:
        raise ValueError, "any1() arg is an empty iterable"

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


def configFile(confname, appdir=".thancad"):
    "Returns the path of confname, placing it into appdir."
    from jorpath import path
    appdir = thanUnunicode(appdir)       # If it is unicode it is converted to win greek
    if not appdir.startswith("."): appdir = "." + appdir
    if Pyos.Windows:
        try:
            import win32com.shell
            from win32com.shell import shellcon, shell
            f1 = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
            appdir = appdir[1:]     #For windows do not include the first dot
        except ImportError: # quick semi-nasty fallback for non-windows/win32com case
            f1 = __homerocurrent()
    else:
        f1 = __homerocurrent()
    f1 = thanUnunicode(f1)       # If it is unicode it is converted to win greek
    f = path(f1) / appdir
    try: f.makedirs1()
    except OSError, why: return None, why
    return f / confname, ""


def __homerocurrent():
    "Return home directory or current director if this fails."
    import jorpath
    f1 = "~"
#    f1 = "$windir"
    f = jorpath.path(f1).expand()
    if f == f1:
        f = f.getcwd()   # expand failed; use current directory as homedir
    return f


_iuniqfileprev = 0
def uniqfile(pref, suf="", stat="w", n=3):
    "Opens a unique file by append a unique number to prefix."
    from jorpath import path
    global _iuniqfileprev
    form = "%s%%0%dd%s" % (pref, n, suf)
    nmax = 10**n

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

#===========================================================================

def dictInvert(a):
    "Inverts a dictionary; values become keys and keys become values."
    b = {}
    for key,val in a.iteritems():
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

__textchars = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))
isStringBinary = lambda bytes: bool(bytes.translate(None, __textchars))

#===========================================================================
#GREEK handling routines

gcaw = "ΙΥΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΑΕΗΙΟΥΩΙΥΣ"
gcw  = "ΪΫΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΆΈΉΊΌΎΏΪΫΣ"
gsw  = "ΐΰαβγδεζηθικλμνξοπρστυφχψωάέήίόύώϊϋς"

ecx  = "IYABGDEZHQIKLMNJOPRSTYFXCWAEHIOYWIYS"
esx  = "iuabgdezhqiklmnjoprstufxcwaehiouwius"


from grdos import *
gw2d = dict(zip(gcw, gcd))
gw2d.update(dict(zip(gsw, gsd)))
gd2w = dict(zip(gcd, gcw))
gd2w.update(dict(zip(gsd, gsw)))
gws2c = dict(zip(gsw, gcaw))
gwc2s = dict(zip(gcw, gsw))

grwsh = dict(zip(gcw, ecx))
grwsh.update(dict(zip(gsw, esx)))
grdsh = dict(zip(gcd, ecx))
grdsh.update(dict(zip(gsd, esx)))

del gcaw, gcw, gsw, gcd, gsd, ecx, esx

def gr2upper(fr):
    "Convert to windows greek capital."
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
    if blank == None: return t
    return t.replace(" ", blank)

def greeklishpath(fn, blank="_", slash="_", dot=None, gtlt="", quote=""):
    "Convert name to greeklish, lower, strip, replace slash, replace blank, replace dots and return path object."
    from jorpath import path
    t = fn.strip()
    if slash != None: t = t.replace("/", slash).replace("\\", slash)
    if dot != None: t = t.replace(".", dot)
    if gtlt != None: t = t.replace("<", gtlt).replace(">", gtlt)
    if quote != None: t = t.replace("'", quote).replace('"', quote).replace("`", quote)
    return path(greeklish(t, blank).lower())

def prgnone(fr, tags=()): pass    #Prints nothing

def prg(fr, tags=()):
    "Print converting to DOS greek only if we run windows (tags is for compatibility)."
    if Pyos.Windows:
        gc = gw2d
        print "".join([gc.get(c, c) for c in fr])
    else:
        print fr
def prints(fr):
    "Print without newline converting to DOS greek only if we run windows."
    if Pyos.Windows:
        gc = gw2d
        sys.stdout.write("".join([gc.get(c, c) for c in fr]))
    else:
        sys.stdout.write(fr)
def tog(fr):
    "Convert to DOS greek only if we run windows."
    if Pyos.Windows:
        gc = gw2d
        return "".join([gc.get(c, c) for c in fr])
    else:
        return fr
def togi(fr):
    "Convert DOS greek only to WINDOWS greek, onlyif we run windows."
    if Pyos.Windows:
        gc = gd2w
        return "".join([gc.get(c, c) for c in fr])
    else:
        return fr
def ing(fr):
    "Convert to linux greek only if we read from DOS (we run windows)."
    if Pyos.Windows:
        gc = gd2w
        return "".join([gc.get(c, c) for c in fr])
    else:
        return fr

#===========================================================================
#Unicode handling routines

import codecs

def thanUnunicode(t):
    "Convert unicode to string."
    if not isinstance(t, unicode): return str(t)
    return thanUnunicode1(t, "replace")[0]

def thanUnicode(t):
    "Convert to unicode."
    if isinstance(t, unicode): return t
    return thanUnicode1(str(t), "replace")[0]

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


thanSetEncoding("iso-8859-7")

############################################################################
############################################################################

#MODULE LEVEL ROUTINES - TEST CODE

#===========================================================================

#def testFrangec():
#    print "frangec"
#    print "10  , 0        :", frangec(10, 0)
#    print " 0  ,10   , 2  :", frangec(0, 10, 2)
#    print " 0  ,10   , 3  :", frangec(0, 10, 3)
#    print " 0.1,10.99, 2.7:", frangec(0.1, 10.99, 2.7)
#
#    print " 0   ,10  ,-1  :", frangec(0, 10, -1)
#    print "10   , 0  ,-2  :", frangec(10, 0, -2)
#    print "10   , 0  ,-3  :", frangec(10, 0, -3)
#    print "10.99, 0.1,-2.7:", frangec(10.99, 0.1, -2.7)
#    print "frange"
#    print "10  , 0        :", frange(10, 0)
#    print " 0  ,10   , 2  :", frange(0, 10, 2)
#    print " 0  ,10   , 3  :", frange(0, 10, 3)
#    print " 0.1,10.99, 2.7:", frange(0.1, 10.99, 2.7)
#
#    print " 0   ,10  ,-1  :", frange(0, 10, -1)
#    print "10   , 0  ,-2  :", frange(10, 0, -2)
#    print "10   , 0  ,-3  :", frange(10, 0, -3)
#    print "10.99, 0.1,-2.7:", frange(10.99, 0.1, -2.7)

#===========================================================================

#def testFnum():
#    ex = ("123",  "a123", "123b", "a123b", "55a123b", "c55da123b", "5_123", "aaa")
#    for t in ex: print t, fnum(t)
                                

############################################################################
############################################################################

#MODULE LEVEL CODE

#---Module initialisation (This code is executed only once)---------


#===========================================================================

#if __name__ == "__main__":
#    testGon()
#    testFrangec()
#    testFnum()
#    print complexe("10")
#    print complexe("ff34")
#    print complexe("10j")
#    print complexe("5+10j")
#    print complexe(20)
#    print complexe(50.220)
