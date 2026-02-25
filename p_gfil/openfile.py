import sys
import p_ggen, p_gtkwid
from . import filmed, ffff, opgui, er
prg = p_ggen.prg
openFilePar = lambda iun, f: None
ppro = 'egn', 'ydr'
proth = ["", ""]

descp = "(None)"
dispLogo = True
files1 = []
fylPro = False
lang = -1



DLERRLIN = 'Error at line'
DLWARLIN = 'Warning at line'
DLOFFIL  = 'Of file'
DLERRSTO = 'Errors logged. Program stops.'
DLMAXNUM = 'Max number of'
DLERRSYN = 'Syntax error.'
DLFILACC = 'File can not be accessed'
DLLIBUNI = 'Library filDat.lib accepts file units between'
DLFILEND = 'Unexpected end of file.'
DLFILREA = 'File can not be read.'
DLDSKFUL = 'The disk is full.'
DLFILWRI = 'The file can not be written to.'
DLTRYAGA = 'Try again.'
DLFILSUF = 'Do not specify suffix in the filename!'

DLMAXPRE = 'Up to 2 prefixes are allowed.'
DLPREFIX = 'PREFIX : '
DLPREFI1 = 'PREFIX 1 : '
DLPREFI2 = 'PREFIX 2 : '
DLMES01 = 'The data files are composed by a prefix and a suffix.'
DLMES02 = 'The suffix is predefined, and the suffix is given by the user.'
DLMES03 = 'For example given the prefix "' + ppro[0] + '"'
DLMES04 = 'the program opens the following FILES:'
DLMES05 = 'For example given the prefix 1 "' + ppro[0] + " and the prefix2 " + ppro[1] + '"'
DLFILDAT = '(data)'
DLFILRES = '(results)'
DLFILOPT = '(optional)'
DLNOSUF = 'Do not append a suffix to the prefix!'
DLNODESC = '(No description available for previous program)'
DLGETPRE = 'Getting prefix from file'
DLERRPRV = 'Error in the execution of the previous program:'
DLRETPRV = '(Delete file "mediate.tmp" and retry)'
DLLOGOST = b'ISTCzcrPx9jK09Ql3NbH0dDXITIpzdXIytfNztPRJsjKxSHR0NnH0srO0NrcIg=='
DLLOGOSS = '  ΑΘΑΝΑΣΙΟΣ ΣΤΑΜΟΣ - ΛΟΓΙΣΜΙΚΟ ΓΙΑ ΜΗΧΑΝΙΚΟΥΣ '


def setPar(fun):
    "Sets the user defined function for reading extended information from mediate.tmp."
    global openFilePar
    openFilePar = fun

def openFile1(un, ext, stat, iPro, desc, encoding=None):
    """Requests a file to be opened.

c-----un = 0  : Θέτει αρχικές τιμές στις διάφορες μεταβλητές.
c               Σε αυτή την περίπτωση, desc είναι το όνομα του προγράμματος.
c               και αν iPro=-1, τότε δεν τυπώνεται το όνομα Αθανάσιος Στάμος.
c     un = 999,998: Τέλος των ορισμών των αρχείων που θα ανοιχθούν. Ανοιξε
c               τα αρχεία. Αν είναι 998 άνοιξε με παράθυρα.
c     un = 888,887: Τέλος των ορισμών των αρχείων που θα ανοιχθούν. Ανοιξε
c               τα αρχεία. Σώσε το πρόθεμα στο αρχείο FILNAMMED.  Αν είναι 887
                άνοιξε με παράθυρα.
c     un > 0  : File unit. Πρέπει uArx<un<uTel. Αν δεν ισχύει και δεν το un
c               είναι διαφορετικό από 0, 888, 999 τότε δημιουργείται λάθος.
c
c     ext : Κατάληξη του αρχείου
c
c     stat = 'old' : Το αρχείο πρέπει αν υπάρχει και θεωρείται ότι περιέχει
c                    δεδομένα.
c     stat = ' '   : Το αρχείο θεωρείται ότι περιέχει αποτελέσματα.
c     stat = 'opt' : Το αρχείο θεωρείται ότι περιέχει δεδομένα. Αν δεν μπορεί
c                    να προσπελαστεί δεν δημιουργείται λάθος (optional).
c                    Αν όλα τα αρχεία που έχουν συγκεκριμένο πρόθεμα είναι
c                    optional, τότε το πρόθεμα αυτό μπορεί να δοθεί και ως
c                    κενό (δηλαδή να μην ανοιχτεί κανένα αρχείο με αυτό
c                    το πρόθεμα).
c     stat = 'opt+': Το αρχείο είναι κατ'επιλογή υποχρεωτικό. Ότι και
c                    το 'opt' αλλά είναι εγγυημένο ότι κάποιο από τα
c                    opt+ πρέπει υποχρεωτικά να υπάρχει. Για χρήση στο
c                    opgui.py
c
c     iPro = 1 ή 2   : Αριθμός προθέματος (μπορούν να δοθούν δύο προθέματα: 1 ή 2)
c     iPro = -1 ή -2 : Αριθμός προθέματος. Το πρόσημο σημαίνει ότι Θα γίνει
c                      έλεγχος αν μπορεί να ανοιχτεί το αρχείο
c                      και στη συνέχεια θα κλείσει. Επίσης δεν θα εμφανιστεί
c                      στο μήνυμα που εκτυπώνεται στην οθόνη.
c                      Είναι για επόμενα προγράμματα που θα τρέξουν αυτόματα
c                      (batch file).
c
c     desc : Εξήγηση του περιεχομένου του αρχείου
    """
#     hhhh()
    global descp, dispLogo, files1, fylPro, lang
    lang = -1
    if un == 0:
        descp = desc
        dispLogo = iPro != -1
        files1 = []
        #if lang == 0: optFile1(0, -1)  # If language is not set, then set language to Greek
    elif un == 888:
        fylPro = True
        return openFiles1()
    elif un == 999:
        fylPro = False
        return openFiles1()
    elif un == 887:
        fylPro = True
        gui = "--commandline" not in sys.argv
        return openFiles1(gui)
    elif un == 998:
        fylPro = False
        gui = "--commandline" not in sys.argv
        return openFiles1(gui)
#        except Exception, why:
#            prg("%s" % (why,))
#            print "yyyyyyyyyyyyyyyyyyyyyyyyy"
#            stopErr1()
    else:
        if not (1 <= abs(iPro) <= 2):
            prg(' Sr openFile1: %d %s' % (iPro, DLMAXPRE), "can")
            stopErr1()
        file1 = p_ggen.Struct()
        file1.ext = ext; file1.stat = stat[:4].strip().lower(); file1.desc = desc; file1.iPro = iPro
        file1.encoding = encoding
        if encoding is None: file1.encoding = p_ggen.thanGetFileEncoding()
        file1.fun = None
        file1.linesf = 0             # It signals that the file unit is used
        files1.append(file1)


def reopenUniqFile1(frw, exts):
    """Reopen an opened file with the same prefix and suffix, and a unique integer in between.

    Do the same for many files; the unique integer will be the same for all files."""
    files1n = {}
    for ext in exts:
        for file1 in files1:
            if ext == file1.ext:
                files1n[ext] = file1
                break
        else:
            raise KeyError("File extension %s has not been opened" % (ext,))
    ext = exts[0]
    file1 = files1n[ext]
    file1.fun.close()
    pref = proth[file1.iPro-1]
    print("pref=", pref, "ipro=", file1.iPro, "proth=", proth)
    file1.fun = p_ggen.uniqfile(pref, "."+ext, "r" if file1.stat=="old" else "w")
    frw[ext] = frw[ext, file1.iPro] = file1.fun
    pref = p_ggen.getPrefix(file1.fun.name)
    for ext in exts[1:]:
        file1 = files1n[ext]
        file1.fun.close()
        pref = p_ggen.putSufix(pref, "."+ext)
        file1.fun = open(pref, "r" if file1.stat=="old" else "w")
        frw[ext] = frw[ext, file1.iPro] = file1.fun


def opFile1e(un, ext, stat, pro, desc, iPro=1, encoding=None):
    "Opens the file and fails if it can not open it."
#---It is assumed that stat1 is at least 3 characters long
    di, why = opFile1(un, ext, stat, pro, desc, iPro, encoding)
    if di is not None: return di
    er.er1s("Error while opening file %s:\n%s" % (pro+"."+ext, why))


def opFile1(un, ext, stat1, pro, desc, iPro=1, encoding=None):
    "Opens file immediately."
    global files1
    stat = stat1[:4].strip().lower()
    if ext == "": fn = pro
    else:         fn = pro+"."+ext
    fr, why = _opFile1(fn, stat, encoding)   # Try to open file
    if fr is None:
        if stat[:3].lower() == 'opt': return {ext:None, (ext, iPro):None}, None   # Optional data
        return None, why
    file1 = p_ggen.Struct()
    file1.ext = ext; file1.stat = stat; file1.desc = desc; file1.iPro = iPro
    file1.linesf = 0             # It signals that the file unit is used
    file1.fun = fr
    files1.append(file1)
    return {ext:fr, (ext, iPro):fr}, None


def inpFile1(mhn, kat, stat, encoding=None):
    """This sr opens a file with the a prefix supplied by user and suffix kat.

      If a wrong file is given, it is asked again.
      If kat == ' ', then the user may supply and the suffix. Else he can't."""

#-----Form message

    kat = kat.rstrip()
    if kat == "": mhn1 = 'FILE %s: ' % (mhn,)
    else:         mhn1 = 'FILE %s (.%s): ' % (mhn, kat)

#-----Get and open file

    while True:
        filnam = p_ggen.path(p_ggen.inpStrB(mhn1, "").rstrip())
        kat1 = filnam.ext.rstrip()
        if filnam == "":
            prg(DLTRYAGA, "can1")                        # Try again
        elif kat != "" and kat1 != '':
            prg(DLFILSUF, "can1")                        # No suffix allowed
            prg(DLTRYAGA, "can1")
        else:
            if kat != "": filnam = filnam.parent / filnam.namebase
            if kat[:1] == ".": kat = kat[1:]                 #Delete dot
            frw, terr = opFile1(1, kat, stat, filnam, "", encoding=encoding)
            if frw is not None: return frw
            prg("\n%s: %s" % (filnam+kat, DLFILACC), "can")  # Can't access file
            prg(DLTRYAGA, "can")


def xinpFile1(win, mhn, kat, stat, encoding=None):
    """This sr opens a file with the a prefix supplied by user and suffix kat.

    If a wrong file is given, it is asked again.
    If kat == ' ', then the user may supply and the suffix. Else he can't."""

#---Form message

    kat = kat.rstrip()
    if kat == "": mhn1 = 'FILE %s: ' % (mhn,)
    else:         mhn1 = 'FILE %s (.%s): ' % (mhn, kat)
    if stat.strip() == "": stat1 = "w"
    else:                  stat1 = "r"

#-----Get and open file

    while True:
        fn , f = opgui.thanTxtopen(win, mhn1, kat, stat1, initialfile=None, initialdir=None)
        if f == p_ggen.Canc: return None     # File open cancelled
#        kat = fn.ext
#        fn = fn.parent / fn.namebase
#        if kat[:1] == ".": kat = kat[1:]
        f.close()
        frw, terr = opFile1(1, kat, stat, fn, "", encoding=encoding)
        if frw is not None: return frw
        p_gtkwid.thanGudModalMessage(win, "%s: %s" % (fn+kat, DLFILACC), "Error opening file", p_gtkwid.ERROR)


def medFile1(iun, mes, kat, stat, encoding=None):
    """This sr opens a file with the a prefix supplied by opend file unit iun and suffix kat.

    If kat == ' ', then the user may supply and the suffix. Else he can't
    This routine is used to read values from file "mediate.tmp". See
    library fildat."""
    try:                  filnam = next(iun).rstrip()
    except StopIteration: er.er1s('Απροσδόκητο τέλος αρχείου %s' % (filmed.FILNAMMED,))
    if filnam == "": er.er1s('Σφάλμα κατά την ανάγνωση αρχείου %s:\n%s κενό αρχείο' % (filmed.FILNAMMED, mes))

    if kat != "": filnam = filnam.parent / filnam.namebase     #Delete dot
    if kat[:1] == ".": kat = kat[1:]
    frw, terr = opFile1(1, kat, stat, filnam, "", encoding=encoding)
    if frw is not None:
        prg('FILE %s= %s' % (mes, filnam))
        return frw
    er.er1s('Σφάλμα κατά την ανάγνωση αρχείου %s:\n%s\n%s: %s' % (filmed.FILNAMMED, mes, filnam, DLFILACC))

#===========================================================================

def openFiles1(gui=False):
    "Tries to open the requested files."
    global prg
    nPro = prothem1(); proth[:] = ["", ""]
    if gui:
        root, prg, _ = opgui.openfileWinmain(descp)
        filmed.prg = prg
        nProm = None  #Windows opens mediate.tmp in program directory; thus we can not use it in GUI mode
    else:
        nProm = filmed.openFileMed(proth, nPro)
    if nProm is None:
        if gui:
            openfileMhn(nPro)
            if nPro == 1:
                proth[0] = opgui.openfilepro(DLPREFIX, 0, files1, descp)
                if proth[0] is None: sys.exit(1)
            elif nPro == 2:
                proth[0] = opgui.openfilepro(DLPREFI1, 0, files1, descp)
                if proth[0] is None: sys.exit()
                proth[1] = opgui.openfilepro(DLPREFI2, 1, files1, descp)
                if proth[1] is None: sys.exit(1)
        else:
            openfileMhn(nPro)
            if nPro == 1:
                proth[0] = openfilepro(DLPREFIX, 0)
            elif nPro == 2:
                proth[0] = openfilepro(DLPREFI1, 0)
                proth[1] = openfilepro(DLPREFI2, prothem1Opt(1))
        filmed.openFileWrmed(nPro, proth)  # Gets ready for errors
        openFileOpen()
        if gui: openFilePar(3, root)       # Διαβάζει άλλες παραμέτρους του προγράμματος από GUI
        else  : openFilePar(0, 0)          # Διαβάζει άλλες παραμέτρους του προγράμματος από πληκτρολόγιο
        filmed.openFileWrmed(nPro, proth)  # Include παραμέτρους
    else:
        filmed.openFileWrmed(nProm, proth) # Gets ready for errors
        openFileOpen()
        filmed.openFileWrmed(nProm, proth) # Include παραμέτρους
    return openedFiles()


def openedFiles():
    "Return a dictionary of opened files."
    d = {}
    for file1 in files1:
        ip = abs(file1.iPro)
        if ip == 1:                                        #Thanasis2024_02_18
            d[file1.ext] = d[file1.ext, ip] = file1.fun    #Thanasis2024_02_18
        else:
            d[file1.ext, ip] = file1.fun                   #Thanasis2024_02_18
    return d

#===========================================================================

def openfileMhn(nPro):
    "Prints message for the user."
    pay = "=" * (len(ffff.gggg(DLLOGOST))+1)
    if dispLogo: prg("%s\n%s" % (ffff.gggg(DLLOGOST), pay), "thancad") # Ονομασία γραφείου
    np = max(len(x.strip()) for x in descp.split("\n"))
    prg("\n\n %s\n%s" % (descp, "-"*(np+2)), "mes")            # Μήνυμα στην οθόνη
    openFilePar(lang, lambda t, tags="info1": prg(t, tags))    # Τυχόν οδηγίες του προγράμματος στην οθόνη
    prg("")
    if nPro == 0: return

    prg("\n".join((DLMES01, DLMES02)))                   # Files composed by prefix, suffix
    if nPro == 1: prg("\n".join((DLMES03, DLMES04, ""))) # Example for 1 prefix
    else:         prg("\n".join((DLMES05, DLMES04, ""))) # Example for 2 prefixes

#-----Εμφάνισε τα ονόματα των αρχείων στην οθόνη

    n = max([len(file1.desc) for file1 in files1])          # Βρες μεγαλύτερη περιγραφή αρχείου
    form = "%s.%s: FILE %-" + str(n) + "s %s"
    for file1 in files1:
        ded = DLFILDAT                                    # data
        if file1.stat != 'old': ded = DLFILRES            # results
        if file1.stat[:3] == 'opt': ded = DLFILOPT        # optional
        i = abs(file1.iPro)
        if file1.iPro > 0:
            prg(form % (ppro[i-1], file1.ext, file1.desc, ded))
    prg("\n")

#===========================================================================

def openfilepro(mes, icod):
    """Διαβάζει το πρόθεμα που δίνει ο χρήστης.
    Αν icod=0 δεν επιτρέπεται ο χρήστης να δώσει κενό πρόθεμα.
    Αν icod=1  επιτρέπεται.
    """
    from p_ggen.py23 import input
    while True:
        pro = p_ggen.path(input(mes).strip())
        if pro == '' and icod == 0: continue
        if pro == '': return pro
        if pro.ext in ("", "."): return pro.parent / pro.namebase
        prg(DLNOSUF)          # Do not append a suffix to the prefix!

#===========================================================================

def openFileOpen():
    "Open all the requested files."

#---Ανοιξε αρχεία

    for file1 in files1:
        i = abs(file1.iPro)
        if len(proth[i-1]) > 0:                         # Check if prefix is optional
            filnam = proth[i-1] + "." + file1.ext
            file1.fun = _opFile1e(filnam, file1.stat, file1.encoding)
        else:
            file1.fun = None

#---Κλείσε τα files για χρήση άλλων προγραμμάτων
#   στο ίδιο batch file.

    for file1 in files1:
        if  file1.iPro < 0 and file1.fun is not None: file1.fun.close(); file1.fun = None

#===========================================================================

def prothem1():
    "Βρίσκει πόσα προθέματα πρέπει να οριστούν"
    nPro = 0
    for file1 in files1:
        i1 = abs(file1.iPro)
        if i1 > nPro: nPro = i1
    return nPro

#===========================================================================

def prothem1Opt(iPro):
    "Βρίσκει αν το πρόθεμα είναι optional."
    for file1 in files1:
        if abs(file1.iPro)-1 == iPro:
            if file1.stat != 'opt': return 0    # not optional (here opt+ is different and it means that iPro is not optional)
    return 1                                    # optional

def closeFiles1():
    doCloseFiles1()
    filmed.okMedFile1()
    opgui.openfileWindestroy()


def closeFiles2():
    "Close files but do not close window system."
    doCloseFiles1()
    filmed.okMedFile1()


def doCloseFiles1():
    "JUst close the files and nothing more."
    for file1 in files1:
        if file1.fun is not None:
            file1.fun.close()
            file1.fun = None


def clFile1(ext):
    "Close the opened file with suffix ext."
    for i,file1 in enumerate(files1):
        if ext == file1.ext: break
    else:
        return              #File was not found/not open
    if file1.fun is not None:
        file1.fun.close()   #File opened; close it
    del files1[i]


def stopErr1():
    doCloseFiles1()
    filmed.errMedFile1()
    opgui.openfileWindestroy()
    sys.exit(1)     #This stops the program after the user has closed the GUI window (if present)


def _opFile1(filnam1, stat1, encoding):
    stat = stat1.lower().strip()
    if stat == '':          stat = 'w'    # unknown -> write
    elif stat[:3] == 'old': stat = 'r'    # read
    elif stat[:3] == 'app': stat = 'a'    # append
    elif stat[:3] == 'opt': stat = 'r'    # Optional data
    try: return open(filnam1, stat, encoding=encoding), None # Try to open file
    except IOError as why: return None, why

def _opFile1e(filnam1, stat1, encoding):
    "Opens a file with status stat1; fail if error."
    f, why = _opFile1(filnam1, stat1, encoding)
    if f is not None: return f
    stat1 = stat1.lower().strip()
    if stat1[:3] == 'opt': return f       # Optional data
    prg("%s: %s" % (filnam1, DLFILACC))
    stopErr1()


import subprocess
import p_grun
T = p_gtkwid.Twid


def runMediate(app, pexpectline=True, popen=False):
    """Runs an executable (communicating with mediate.tmp) and redirect the output to print command.

    It is the responsibility of the caller to ensure that mediate.tmp exists in pdir
    and that it is valid."""
    print("inside runMediate")
    p_ggen.thanSetEncoding("utf8")   #Thanasis2017_01_29
    out, _, _ = opgui.openfileWinget()
    assert out != None, "runMediate() should be called in GUI mode!"
    try:
        fn = p_ggen.path(proth[0]).abspath()
        pdir = fn.parent
        closeFiles2()
        #p_gtkwid.thanGudModalMessage(out, str(pdir), "wait")    #for debugging
        try:
            p_grun.runExec(app, pdir, out, pexpectline, popen)
        except BaseException as e:
            raise
            dl = "%s '%s'" % (p_ggen.Tgui["Error while executing external program"], app)
            out.thanPrt("\n%s:\n%s" % (dl, e), "can")
            p_gtkwid.thanGudModalMessage(out, "%s.\n%s." % (dl, p_ggen.Tgui["Details were recorded on output window"]),
                                          "%s %s" % (p_ggen.Tgui["ERROR executing"], app))
#          out.thanTkSetFocus()
    except BaseException as e:
        raise
        out.thanPrt("Exception: %s" % (e,))


def runExec2(openFiles, executable):
    "Run a (fortran, C) executable in commandline or in a window."
    if "--commandline" in sys.argv:
        subprocess.call(executable)
    else:
        openFiles()
        try:
            runMediate(executable)
        except BaseException as e:
            er.er1s("\n%s:\n%s" % (p_ggen.Tgui["Error while executing program"], e), "can")
        closeFiles1()
