import re
from p_ggen import prg, tog, isString, Tgui


class Datlin(object):
    "Class to assist reading text data."
    def __init__(self, fr, prt=None, comment="#"):
        self.fr = fr
        try: self.name = self.fr.name
        except: self.name = "<unknown>"
        if prt is None: self.prt = prg
        else:           self.prt = prt
        self.lin = 0
        self.itok = 0
        self.dlPrev = []
        self.dlUnread = False
        self._comment = comment
        self.ncom = len(comment)
        if comment == "*": comment = r"\*"
#        self._splitter = re.compile(r"""'.+'|".+"|%s.*|\S+""" % comment)
        self._splitter = re.compile(r"""'[^']+'|"[^"]+"|%s.*|\S+""" % comment)

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict["_splitter"]          # Do not save the regulat expression in the file
        return odict

    def __setstate__(self, odict):
        self.__dict__.update(odict)
        comment = self._comment
        if comment == "*": comment = r"\*"
        self._splitter = re.compile(r"""'[^']+'|"[^"]+"|%s.*|\S+""" % comment)   # Restore regular expression

    def __iter__(self):
        "Return an iterator which produces raw lines."
        return self

    def __next__(self):
        if self.datLin(failoneof=False): return self.dlPrev
        raise StopIteration


    def datLinold(self, failoneof=False):
        "Reads a new line, unless the previous line was unread."
        if not self.dlUnread:
            while 1:
                dl = self.fr.readline()
                if dl == "":
                    if not failoneof: return False
                    raise IOError("Unexpected end of file %s after line %d." % (self.name, self.lin))
                self.dlPrev = dl.strip("\n")
                self.lin += 1
                dl = dl.strip()
                if dl != "" and dl[0:self.ncom] != self._comment: break
#        self.dl = self.dlPrev.strip().split()
        self.dl = self._splitter.findall(self.dlPrev)
        if len(self.dl) > 0:
            if self.dl[-1][0:self.ncom] == self._comment: del self.dl[-1]       # Delete trailing comment
        for i,dl1 in enumerate(self.dl):
            if dl1[0] == "'" == dl1[-1] or dl1[0] == '"' == dl1[-1]:
                self.dl[i] = self.dl[i][1:-1]           # Delete apostrophis in strings
        self.dlUnread = False
        self.itok = 0
        return True


    def datLin(self, failoneof=False):
        "Reads a new line, unless the previous line was unread."
        if not self.dlUnread:
            for dl in self.fr:
                self.dlPrev = dl.strip("\n")
                self.lin += 1
                dl = dl.strip()
                if dl != "" and dl[0:self.ncom] != self._comment: break
            else:
                if not failoneof: return False
                raise IOError("Unexpected end of file %s after line %d." % (self.name, self.lin))
#        self.dl = self.dlPrev.strip().split()
        self.dl = self._splitter.findall(self.dlPrev)
        if len(self.dl) > 0:
            if self.dl[-1][0:self.ncom] == self._comment: del self.dl[-1]       # Delete trailing comment
        for i,dl1 in enumerate(self.dl):
            if dl1[0] == "'" == dl1[-1] or dl1[0] == '"' == dl1[-1]:
                self.dl[i] = self.dl[i][1:-1]           # Delete apostrophis in strings
        self.dlUnread = False
        self.itok = 0
        return True


    def datCurline(self):
        "Returns current whole raw dataline."
        return self.dlPrev

    def datRawline(self, failoneof=True):
        "Reads and returns a raw dataline."
        if not self.datLin(failoneof): return None
        return self.dlPrev

    def datLinSet(self, dl):
        "Sets the current line as if it were read from file."
        self.dlPrev  = dl.strip("\n")
        self.dlUnread = True
        self.datLin()

    def datLinbac(self):
        "Unread current line."
        self.dlUnread = True

    def datBac(self, n=1):
        "Unreads n tokens of current line."
        self.itok -= n
        if self.itok < 0: self.itok = 0

    def eol(self):
        "Return true if end of line."
        return self.itok >= len(self.dl)

    def datCom(self, coms, fail=True):
        "Reads a line and checks if the commands found in coms are present."
        self.datLin(failoneof=True)
        return self.datComC(coms, fail)

    def datComC(self, coms, fail=True):
        "Checks if the commands found in coms are present on current line."
        coms = coms.strip().split()
        i = self.itok

        for com in coms:
            if i >= len(self.dl):
                if not fail: return False
                raise IOError("Error at line %d of file %s: End of line encountered where '%s' was expected." % (self.lin, self.name, com))
            if not self.dl[i].startswith(com[:4]):
                if not fail: return False
                raise ValueError("Error at line %d of file %s: '%s' was found where '%s' was expected." % (self.lin, self.name, self.dl[i], tog(com)))
            i += 1
        for j in range(i, len(self.dl)):
            if self.dl[j][-1] == ":": i = j + 1; break    # Skip to colon
        self.itok = i
        return True

    def datFloat(self):
        "Tries to read a real number."
        i = self.itok
        if i >= len(self.dl):
            raise IOError("Error at line %d of file %s: End of line encountered where a real number was expected." % (self.lin, self.name))
        self.itok += 1
        try: return float(self.dl[i])
        except ValueError:
            raise ValueError("Error at line %d of file %s: '%s' was found where a real number was expected." % (self.lin, self.name, self.dl[i]))

    def datInt(self):
        "Tries to read an integer number."
        i = self.itok
        if self.itok >= len(self.dl):
            raise IOError("Error at line %d of file %s: End of line encountered where an integer number was expected." % (self.lin, self.name))
        self.itok += 1
        try: return int(self.dl[i])
        except ValueError:
            raise ValueError("Error at line %d of file %s: '%s' was found where an integer number was expected." % (self.lin, self.name, self.dl[i]))

    def datStr(self, failoneol=True):
        "Tries to read a string."
        i = self.itok
        if self.itok >= len(self.dl):
            if not failoneol: return None
            raise IOError("Error at line %d of file %s: End of line encountered where a string was expected." % (self.lin, self.name))
        self.itok += 1
        return self.dl[i]

    def datYesno(self):
        "Tries to read an yes/no string."
        t = self.datStr()[:2].strip()
        if t[:2] in ("ΝΑ", "να", "NA", "na", "YE", "ye", "1"): return True
        if t[:2] in ("ΟΧ", "οχ", "OX", "ox", "NO", "no", "0"): return False
        raise ValueError("Error at line %d of file %s: '%s' was found where NAI/YES/OXI/NO was expected." % (self.lin, self.name, t))

    def datMchoice(self, coms, nc=4):
        "Gets a string that has to be one of the given commands."
        if isString(coms): coms = coms.split()
        t = self.datStr()
        n = min(len(t), nc)
        for com1 in coms:
            if t[:n] == com1[:n]: return com1
        raise ValueError("Error at line %d of file %s: '%s' was found where one of the following was expected:\n%s" %
                          (self.lin, self.name, t, ", ".join(coms)))

    def datFloatR(self, amin, amax):
        "Reads a float number and checks if it is in range."
        a = self.datFloat()
        if amin <= a <= amax: return a
        raise ValueError("Error at line %d of file %s: '%f'\nThe real number was expected in range %f and %f" % (self.lin, self.name, a, amin, amax))

    def datIntR(self, amin, amax):
        "Reads an integer number and checks if it is in range."
        a = self.datInt()
        if amin <= a <= amax: return a
        raise ValueError("Error at line %d of file %s: '%d'\nThe integer number was expected in range %d and %d" % (self.lin, self.name, a, amin, amax))

    def er(self, mes):
        "Prints error message and exits."
        t = "Error at line %d of file %s:\n%s" % (self.lin, str(self.name), tog(mes))
        raise ValueError(t)

#    def er(self, mes):
#        "Prints error message and continues."
#        t = "Error at line %d of file %s:\n%s" % (self.lin, str(self.fr.name), tog(mes))
#        self.prt(t)

    def syntaxEr(self):
        "Prints error message and exits."
        self.er("Syntax error.")

    def wa(self, mes):
        "Prints a warning message."
        self.prt("Warning: At line %d of file %s:\n%s" % (self.lin, str(self.fr.name), mes), "can1")


def test():
    "Tests Datlin."
    class flike(object):
        def __init__(self, dlines):
            self.dlines = dlines
            self.i = 0
        def __iter__(self):
            return self
        def __next__(self):
            if self.i < len(self.dlines):
                self.i += 1
                return self.dlines[self.i-1]
            else:
                raise StopIteration
        def readline(self):
            if self.i < len(self.dlines):
                self.i += 1
                return self.dlines[self.i-1]
            else:
                return ""

    fr = flike(['Thanasis Stamos "andreas stella"  189.99 #comments 1+1+1',
                "  'Thanasis Stamos'  ''  'andreas' # stella  189.99 #comments 1+1+1 "])
    d = Datlin(fr)
    d.datLin()
    for i in range(4):
        print(d.datStr())
    d.datLin()
    for i in range(6):
        print(d.datStr())

if __name__ == "__main__": test()
