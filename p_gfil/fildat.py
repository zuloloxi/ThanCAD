import p_ggen
from . import openfile, opgui
Tgui = p_ggen.Tgui


class File1(object):
    "A file that counts lines."

    def __init__(self, fr):
        "Hold the opened file and do housekeeping."
        self.fr        = fr
        self.linesf    = 0
        self.isSavedf  = False
        self.isEOFf    = False
        self.dlineSavf = ""                 # In case someone calls unerfile1 before reading anything
        self.icodf     = 0
#        if self.lang ==  0: self.optFile1(0, -1) #-----If language is not set, then set language to Greek
#        self.opened.append(weakref.ref(self))


    def __iter__(self):
        "The iterator is the object itself."
        return self


    def __next__(self):
        "Return the next line and advance line count."
        if self.isEOFf: raise StopIteration
#-------Unreading is enabled here
        if not self.isSavedf:
            self.linesf += 1
            try:
                self.dlineSavf = next(self.fr)
            except StopIteration:
                self.isEOFf = True
                raise
        buf = self.dlineSavf.rstrip()
        self.isSavedf = False
        return buf


    def re1(self):
        "Return the next line and advance line count; return ierr!=0 end error message if error."
        try:
            return next(self), 0
        except StopIteration:
            return "End of file", -1
        except Exception as e:
            return "%s" % (e,), 1


    def re1e(self):
        "Return the next line and advance line count; return ierr=-1 if end of fil; fail with error message otherwise."
        try:
            return next(self), 0
        except StopIteration:
            return "End of file", -1
        except Exception as e:
            self.er1s("%s" % (e,))


    def re1ee(self):
        "Return the next line and advance line count; fail with error message otherwise."
        try:
            return next(self)
        except StopIteration:
            self.er1s(Tgui["Unexpected end of file"])
        except Exception as e:
            self.er1s("%s" % (e,))


    def unre1(self):
        "Unread the previous line."
        self.isSavedf = True


    def wr1(self, dline):
        "Write data line to file append a newline, exceptions are not handled."
        self.fr.write("{}\n".format(dline))
        self.linesf += 1


    def wr1ee(self, dline):
        "Write data line to file append a newline, stop with message if error."
        try:
            self.fr.write("{}\n".format(dline))
        except Exception as e:
            self.er1s("%s" % (e,))
        self.linesf += 1


    def wa1(self, mes, tags="can1"):
        "Print a warning message."
        winmain, prt, _ = opgui.openfileWinget()
        if winmain is None: prt = p_ggen.prg
        prt(Tgui["Warning at line %d of file %s:\n%s"] % (self.linesf, self.fr.name, mes), tags)


    def er1s(self, mes, tags="can"):
        "Prints an error message and stops."
        winmain, prt, _ = opgui.openfileWinget()
        if winmain is None: prt = p_ggen.prg
        prt(Tgui["Error at line %d of file %s:\n%s"] % (self.linesf, self.fr.name, mes), tags)
        openfile.stopErr1()


    def erSyntax1s(self, mes, tags="can"):
        "Prints a syntax error message and stops."
        winmain, prt, _ = opgui.openfileWinget()
        if winmain is None: prt = p_ggen.prg
        prt(Tgui["Syntax error at line %d of file %s:\n%s"] % (self.linesf, self.fr.name, mes), tags)
        openfile.stopErr1()

    def close(self):
        "Close the opened file."
        self.fr.close()
