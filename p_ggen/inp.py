# -*- coding: iso-8859-7 -*-

from gen import ing, prg, tog, isString, thanUnunicode
from jorpath import path


def inpDouble(mes, douDef=None):
      "Inputs a double with default value."
      while True:
          dline = raw_input(tog(mes)).strip()
          if dline == '' and douDef != None: return douDef     # Default value
          try: return float(dline)
          except: pass
          prg("\nΑναμένεται πραγματικός αριθμός\nΠροσπαθείστε πάλι.\n")


def inpLong(mes, douDef=None):
      "Inputs an integer with default value."
      while True:
          dline = raw_input(tog(mes)).strip()
          if dline == '' and douDef != None: return douDef     # Default value
          try: return int(dline)
          except: pass
          prg("\nΑναμένεται ακέραιος αριθμός\nΠροσπαθείστε πάλι.\n")


def inpNo(mes, douDef=None):
      "Inputs yes or no."
      while True:
          dline = raw_input(tog(mes)).strip()
          if dline == '' and douDef != None: return douDef     # Default value
          dl = ing(dline[:2])
#---------Check what We read
          if dl in ('να', 'ΝΑ', 'na', 'NA', 'ye', 'YE', '1'): return True
          if dl in ('οχ', 'ΟΧ', 'ox', 'OX', 'no', 'NO', '0'): return False
          prg('\nΑναμένεται ΝΑΙ (ΝΑ, να, na, ye, YE, 1) ή ΟΧΙ (ΟX, οχ, οx, no, NO, 0)\nΠροσπαθείστε πάλι.\n')


def inpStr(mes, douDef=None):
      "Inputs a string with default value."
      while True:
          dline = ing(raw_input(tog(mes)).strip())
          if dline == '' and douDef != None: return douDef     # Default value
          return dline


def inpFiles(mes, suf="", nest=False):
    """Gets data files with suffix suf.

    Examples:
    1. fils = inpFiles("Δώστε αρχεία που καταλήγουν σε xx.asc (με ή χωρίς την κατάληξη). Για όλα δώστε * (enter=*) : ", "xx.asc")
       The above gets all the files in current directory (and recursively in the 
       subdirectories if nest==True)
       which have .asc as a suffix:  a.asc, thanasis.asc, 1.asc, ...
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
                if not fentry.lower().endswith(suf): fentry += suf
                if nest: f = list(cdir.walkfiles(fentry))      # nested subdirectories
                else:    f = list(cdir.files(fentry))          # only current directory
                if len(f) == 0: prg("Warning: no %s files matches '%s'" % (suf, fentry))
                fildats.extend(f)
            else:
                if not fentry.lower().endswith(suf): fentry += suf
                fildats.append(fentry)
        if len(fildats) > 0: return fildats
        prg("Error: No %s files defined or found." % suf)
        prg("Try again.")


def inpImage(mes, initialfile=""):
    "Open an image with PIL."
    import p_gbmp
    while True:
        fn = p_ggen.inpStrB(mes, initialfile)
        im, ter = p_gbmp.imageOpen(fn)
        if im != None: return fn, im
        ter = "Error while accessing %s:\n%s\nTry again." % (fn, ter)
        prg(ter, "can1")


def inpSaveFile(ext, mes, mode="w", initialfile=""):
    "Gets a filename that exists, from user."
    while True:
        filnam = inpStrB(mes, initialfile)
        try:
            fw = file(filnam, mode)
        except IOError, why:
            prg("Error opening file %s: %s\nTry again.\n" % (filnam, why), "can1")
        else:
            return filnam, fw


def inpDir(mes, mustexist=False, mustnotexist=False, default=None):
    "Inputs a non-blank directory name with default value."
    if default != None:
        try:
            default = thanUnunicode(default)
        except:
            default = ""
    while True:
        f = ing(raw_input(tog(mes)).strip())
        if f == '' and default != None: f = default       # Default value
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
          dline = ing(raw_input(tog(mes)).strip())
          if dline == '' and douDef != None: dline = douDef         # Default value
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
c-----This routine tries to read a double number dou from unit iun.

c     If it does -> OK. If dou can not be read
c     dou takes the default value, and warning message mes is printed.
c     This routine is used to read values from file "mediate.tmp". See
c     library fildat
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


def medDoubleR (un, mes, douMin, douMax, douDef):
      """
c-----This routine tries to read a double number dou from unit iun.

c     If it does and dou is between douMin and douMax -> OK.
c     If dou can not be read or is outside douMin-douMax,
c     dou takes the default value, and warning message mes is printed.
c     This routine is used to read values from file "mediate.tmp". See
c     library fildat
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
c-----This routine tries to read a long number dou from unit iun.

c     If it does and dou is between douMin and douMax -> OK.
c     If dou can not be read or is outside douMin-douMax,
c     dou takes the default value, and warning message mes is printed.
c     This routine is used to read values from file "mediate.tmp". See
c     library fildat
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
c-----This routine tries to read a string dou from unit iun.

c     If it does and dou is not blank -> OK.
c     If dou can not be read or is blank,
c     dou takes the default value, and warning message mes is printed.
c     This routine is used to read values from file "mediate.tmp". See
c     library fildat
      """
      dline = un.readline()
      if dline != "":                  # not end of file
          dline = dline.strip()
          if dline != "": return dline
      prg("%s %s" % (mes, douDef))  # Use the default value and print message
      return douDef


def medDir(un, mes, mustexist=False, mustnotexist=False, default=None):
    "Inputs a non-blank directory name with default value."
    if default != None:
        try:
            default = thanUnunicode(default)
        except:
            default = ""
    f = un.readline()             #If end of file, f=""
    f = f.strip()
    while True:
        if f == '':
            if default != None: f = default       # Default value
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
    prg("%s %s" % (mes, douDef))          # Use the default value and print message
    return f


def medMchoice(un, mes, coms, douDef=1):
    "Inputs a choice of the user as an integer starting at 1."
    if isString(coms): coms = coms.split()
    return medLongR(un, mes, 1, len(coms), douDef)


def test():
    "Tests the functions."
    akl = inpDoubleR('ΚΛΙΜΑΚΑ ΤΕΛΙΚΟΥ ΣΧΕΔΙΟΥ (return=500) : ', 1.0e-10, 1.0e10, 500.0)
    print "akl=", akl

def testd():
    "Tests the functions."
#    d = inpDir('Φάκελλος: ', mustexist=True, mustnotexist=False, default=".")
#    d = inpDir('Φάκελλος: ', mustexist=False, mustnotexist=True, default=".")
#    print "directory=", d
    d = inpDir('Φάκελλος: ', mustexist=False, mustnotexist=False, default=".")
    print "directory=", d


if __name__ == "__main__": testd()
