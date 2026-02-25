from .gen import ing, prg, tog, isString, thanUnunicode, inte
from .jorpath import path


def inpDouble(mes, douDef=None):
    "Inputs a double with default value."
    while True:
        dline = input(tog(mes)).strip()
        if dline == '' and douDef is not None: return douDef     # Default value
        try: return float(dline)
        except: pass
        prg("\nΑναμένεται πραγματικός αριθμός\nΠροσπαθείστε πάλι.\n")


def inpLong(mes, douDef=None):
    "Inputs an integer with default value."
    while True:
        dline = input(tog(mes)).strip()
        if dline == '' and douDef is not None: return douDef     # Default value
        try: return int(dline)
        except: pass
        prg("\nΑναμένεται ακέραιος αριθμός\nΠροσπαθείστε πάλι.\n")


def inpNo(mes, douDef=None):
    "Inputs yes or no."
    while True:
        dline = input(tog(mes)).strip()
        if dline == '' and douDef is not None: return douDef     # Default value
        dl = ing(dline[:2])
#-------Check what We read
        if dl in ('να', 'ΝΑ', 'na', 'NA', 'ye', 'YE', '1'): return True
        if dl in ('οχ', 'ΟΧ', 'ox', 'OX', 'no', 'NO', '0'): return False
        prg('\nΑναμένεται ΝΑΙ (ΝΑ, να, na, ye, YE, 1) ή ΟΧΙ (ΟX, οχ, οx, no, NO, 0)\nΠροσπαθείστε πάλι.\n')


def inpStr(mes, douDef=None):
    "Inputs a string with default value."
    while True:
        dline = ing(input(tog(mes)).strip())
        if dline == '' and douDef is not None: return douDef     # Default value
        return dline


def inpFiles(mes, suf="", nest=False, allownone=False):
    """Gets data files with suffix suf.

    Examples:
    1. fils = inpFiles("Δώστε αρχεία που καταλήγουν σε xx.asc (με ή χωρίς την κατάληξη). Για όλα δώστε * (enter=*) : ", "xx.asc")
       The above gets all the files in current directory (and recursively in the
       subdirectories if nest==True)
       which have xx.asc as a suffix:  axx.asc, thanasisxx.asc, 1xx.asc, ...
    2. The filenames are transformed to lower, to facilitate windows..
    """
    initialdir = path(".")
    while True:
        suf = suf.lower()
        fentries = inpStr(mes, "*")
        fildats = []
        for fentry in fentries.split():
            fentry = path(fentry)
            if "*" in fentry or "?" in fentry:
                cdir = fentry.parent
                if cdir == "": cdir = initialdir
                fentry = fentry.basename()
                if fentry.ext.lower() == "": fentry += suf
                if nest: f = list(cdir.walkfiles(fentry))      # nested subdirectories
                else:    f = list(cdir.files(fentry))          # only current directory
                if len(f) == 0: prg("Warning: no %s files matches '%s'" % (suf, fentry))
                fildats.extend(f)
            else:
                if fentry.ext.lower() == "": fentry += suf
                fildats.append(fentry)
        if len(fildats) > 0 or allownone: return fildats
        prg("Error: No %s files defined or found." % suf)
        prg("Try again.")


def inpSaveFile(ext, mes, mode="w", initialfile=""):
    "Gets a filename that exists, from user."
    while True:
        filnam = inpStrB(mes, initialfile)
        try:
            fw = open(filnam, mode)
        except IOError as why:
            prg("Error opening file %s: %s\nTry again.\n" % (filnam, why), "can1")
        else:
            return filnam, fw


def inpDir(mes, mustexist=False, mustnotexist=False, default=None):
    "Inputs a non-blank directory name with default value."
    if default is not None:
        try:
            default = thanUnunicode(default)
        except:
            default = ""
    while True:
        f = ing(input(tog(mes)).strip())
        if f == '' and default is not None: f = default       # Default value
        if f.strip() == '':
            prg('\nΑναμένεται όνομα φακέλλου (μη κενό)\nΠροσπαθείστε πάλι.\n', "can1")
            continue
        f = path(f).expand().abspath()
        if mustexist:
            if f.exists():
                if not f.isdir():
                    prg("Ο φάκελλος %s δεν είναι φάκελλος (είναι αρχείο). Προσπαθείστε πάλι." % f)
                    continue
            else:
                prg("Ο φάκελλος %s δεν υπάρχει. Προσπαθείστε πάλι." % f)
                continue
        if mustnotexist:
            if f.exists():
                prg("Ο φάκελλος %s ήδη υπάρχει. Προσπαθείστε πάλι." % f)
                continue
        if f.exists() and not f.isdir():   #In case that both mustexist=False and mustnotexist=False
            prg("Ο φάκελλος %s δεν είναι φάκελλος (είναι αρχείο). Προσπαθείστε πάλι." % f)
            continue
        return f


def inpStrB(mes, douDef=None):
    "Inputs a non-blank string with default value."
    while True:
        dline = ing(input(tog(mes)).strip())
        if dline == '' and douDef is not None: dline = douDef         # Default value
        if dline.strip() != '': return dline
        prg('\nΑναμένεται κείμενο (μη κενό)\nΠροσπαθείστε πάλι.\n')


def inpDoubleR (mes, douMin, douMax, douDef):
    "Inputs a double with default value and range check."
    while True:
        dou = inpDouble(mes, douDef)
        if douMin <= dou <= douMax: return dou
        prg('\nΑναμένεται πραγματικός αριθμός εντός των ορίων:')
        prg('%.3f και %.3f' % (douMin, douMax))
        prg('\nΠροσπαθείστε πάλι.\n')


def inpLongR (mes, douMin, douMax, douDef):
    "Inputs an integer with default value and range check."
    while True:
        dou = inpLong(mes, douDef)
        if douMin <= dou <= douMax: return dou
        prg('\nΑναμένεται ακέραιος αριθμός εντός των ορίων:')
        prg('%d και %d' % (douMin, douMax))
        prg('\nΠροσπαθείστε πάλι.\n')


def inpMchoice(mes, coms, douDef=1):
    "Inputs a choice of the user as an integer starting at 1."
    if isString(coms): coms = coms.split()
    for com1 in coms:
        prg(com1)
    prg("")
    return inpLongR(mes, 1, len(coms), douDef)


#===========================================================================

def medDouble(un, mes, douDef):
    """
    This routine tries to read a double number dou from unit iun.

    If it does -> OK. If dou can not be read
    dou takes the default value, and warning message mes is printed.
    This routine is used to read values from file "mediate.tmp". See
    library fildat
    """
    dline = un.readline()
    if dline != "":                  # not end of file
        try:
            dou = float(dline.strip())
            return dou
        except:
            pass
    prg("%s %.3f" % (mes, douDef))  # Use the default value and print message
    return douDef


def medNo(un, mes, douDef):
    "Reads yes or no from un."
    dline = un.readline()
    if dline != "":                  # not end of file
        dl = dline[:2]
#-------Check what We read
        if dl in ('να', 'ΝΑ', 'na', 'NA', 'ye', 'YE', '1'): return True
        if dl in ('οχ', 'ΟΧ', 'ox', 'OX', 'no', 'NO', '0'): return False
    return douDef      # Default value


def medDoubleR (un, mes, douMin, douMax, douDef):
    """
    This routine tries to read a double number dou from unit iun.

    If it does and dou is between douMin and douMax -> OK.
    If dou can not be read or is outside douMin-douMax,
    dou takes the default value, and warning message mes is printed.
    This routine is used to read values from file "mediate.tmp". See
    library fildat
    """
    dline = un.readline()
    if dline != "":                  # not end of file
        try:
            dou = float(dline.strip())
            if douMin <= dou <= douMax: return dou
        except:
            pass
    prg("%s %.3f" % (mes, douDef))  # Use the default value and print message
    return douDef


def medLongR (un, mes, douMin, douMax, douDef):
    """
    This routine tries to read a long number dou from unit iun.

    If it does and dou is between douMin and douMax -> OK.
    If dou can not be read or is outside douMin-douMax,
    dou takes the default value, and warning message mes is printed.
    This routine is used to read values from file "mediate.tmp". See
    library fildat
    """
    dline = un.readline()
    if dline != "":                  # not end of file
        try:
            dou = int(dline.strip())
            if douMin <= dou <= douMax: return dou
        except:
            pass
    prg("%s %d" % (mes, douDef))  # Use the default value and print message
    return douDef


def medStr(un, mes, douDef):
    """
    This routine tries to read a string dou from unit iun.

    If it does and dou is not blank -> OK.
    If dou can not be read or is blank,
    dou takes the default value, and warning message mes is printed.
    This routine is used to read values from file "mediate.tmp". See
    library fildat
    """
    dline = un.readline()
    if dline != "":                  # not end of file
        dline = dline.strip()
        if dline != "": return dline
    prg("%s %s" % (mes, douDef))  # Use the default value and print message
    return douDef


def medFiles(un, mes, suf, nest=False, allownone=False):
    """
    This routine tries to read filenames from unit iun.

    If it does and dou is not blank -> OK.
    If dou can not be read or is blank,
    dou takes the default value, and warning message mes is printed.
    This routine is used to read values from file "mediate.tmp". See
    library fildat
    """
    dline = un.readline()
    if dline == "": return []   #end of file; no files
    n = inte(dline)
    if n is None or n <= 0: return []   #error or zero number: no files
    fils = []
    for i in range(n):
        dline = un.readline()
        if dline == "": break    #End of file
        fils.append(path(dline))
    return fils


def medDir(un, mes, mustexist=False, mustnotexist=False, default=None):
    "Inputs a non-blank directory name with default value."
    if default is not None:
        try:
            default = thanUnunicode(default)
        except:
            default = ""
    f = un.readline()             #If end of file, f=""
    f = f.strip()
    while True:
        if f == '':
            if default is not None: f = default       # Default value
            break
        if mustexist:
            if f.exists():
                if not f.isdir(): break   #Ο φάκελλος %s δεν είναι φάκελλος (είναι αρχείο)
            else:
                break                     #Ο φάκελλος %s δεν υπάρχει
        if mustnotexist:
            if f.exists(): break          #Ο φάκελλος %s ήδη υπάρχει. Προσπαθείστε πάλι
        if f.exists() and not f.isdir():      #In case that both mustexist=False and mustnotexist=False
            break                         #Ο φάκελλος %s δεν είναι φάκελλος (είναι αρχείο).
        return f
    prg("%s %s" % (mes, default))          # Use the default value and print message
    return f


def medMchoice(un, mes, coms, douDef=1):
    "Inputs a choice of the user as an integer starting at 1."
    if isString(coms): coms = coms.split()
    return medLongR(un, mes, 1, len(coms), douDef)


def test():
    "Tests the functions."
    akl = inpDoubleR('ΚΛΙΜΑΚΑ ΤΕΛΙΚΟΥ ΣΧΕΔΙΟΥ (return=500) : ', 1.0e-10, 1.0e10, 500.0)
    print("akl=", akl)

def testd():
    "Tests the functions."
#    d = inpDir('Φάκελλος: ', mustexist=True, mustnotexist=False, default=".")
#    d = inpDir('Φάκελλος: ', mustexist=False, mustnotexist=True, default=".")
#    print("directory=", d)
    d = inpDir('Φάκελλος: ', mustexist=False, mustnotexist=False, default=".")
    print("directory=", d)


if __name__ == "__main__": testd(); test()
