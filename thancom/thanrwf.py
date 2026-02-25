##############################################################################
# ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2025 Thanasis Stamos, May 20, 2025
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (www.gnu.org/licenses/gpl.html).
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################
"""\
ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers

This module implements read/write mechanism for ThanCad files..
"""

from p_ggen import Pyos

class ThanRfile(object):
    "A wrapper of a read file with unread and count lines capability."

    def __init__(self, fr, proj, name=None):
        "Initialize saved line, line counter."
        self.fr = fr
        self.thanProj = proj
        self.elev = proj[1].thanVar["elevation"]
        self.nelev = len(self.elev)
        self.prev = None
        self.returnPrev = False
        self.nline = 0
        if name is None:
            try: self.filnam = fr.name   #To acommodate BZ2File object
            except: self.filnam = "<Unknown>"
        else:
            self.filnam = name


    def thanDestroy(self):
        "Break circular references."
        del self.fr, self.thanProj, self.elev

    def setElev(self, elev):
        "Set new elevation and dimensionality."
        self.elev = elev
        self.nelev = len(elev)

    def __next__(self):
        "Get next line."
        if self.returnPrev:
            self.returnPrev = False
            #if Pyos.Python3: return self.prev.decode(encoding="iso-8859-7", errors="replace")
            return self.prev
        self.prev = next(self.fr)
        self.nline += 1
        #if Pyos.Python3: return self.prev.decode(encoding="iso-8859-7", errors="replace")
        return self.prev

    def __iter__(self):
        return self

    def unread(self):
        "Next time return the saved previous line."
        self.returnPrev = True

    def prter(self, mes):
        "Print an error message with file info."
        self.thanProj[2].thanPrter(self.er(mes))

    def er(self, mes):
        "Return and error message with location."
        return "Error at line %d of file %s:\n%s" % (self.nline, self.filnam, mes)

    def readBeg(self, s):
        "Read beginning of element and complain if not found."
        header = "<%s>" % s
        #print("header=", header, "   type=", type(header))
        if next(self).strip() != header: raise ValueError("Header %s not found" % header)

    def readEnd(self, s, er=""):
        "Read end of element and complain if not found; er is additional error message."
        footer = "</%s>" % s
        if next(self).strip() != footer: raise ValueError("%sFooter %s not found" % (er, footer))

    def readNode(self):
        "Read a node from thcx format; allow any number of dimensions but at least 2."
        dl = next(self).split()
        if dl[0]  != "<NODE>":  raise ValueError("Header <NODE> not found")   #May raise IndexError
        if dl[-1] != "</NODE>": raise ValueError("Footer </NODE> not found")  #May raise IndexError
        nt = len(dl)-2
        if nt < 2: raise ValueError("At least 2 coordinates were expected")
        if nt >= self.nelev: return [float(x) for x in dl[1:1+self.nelev]]
        return [float(x) for x in dl[1:1+nt]] + self.elev[nt:]

    def readValid(self):
        "Read valid attribute of node from thcx format; allow any number of dimensions but at least 2."
        dl = next(self).split()
        if dl[0]  != "<valid>":  raise ValueError("Header <valid> not found")   #May raise IndexError
        if dl[-1] != "</valid>": raise ValueError("Footer </valid> not found")  #May raise IndexError
        nt = len(dl)-2
        if nt < 2: raise ValueError("At least 2 coordinates were expected")
        if nt >= self.nelev: return [int(x) for x in dl[1:1+self.nelev]]
        return [int(x) for x in dl[1:1+nt]] + self.elev[nt:]

    def readNodes(self):
        "Read many nodes."
        self.readBeg("NODES")
        cp = []
        while True:
            dl = next(self).split()
            if dl[0] == "</NODES>": return cp
            nt = len(dl)
            if nt < 2: raise ValueError("At least 2 coordinates were expected")
            if nt >= self.nelev: cc = [float(x) for x in dl[:nt]]
            else:                cc = [float(x) for x in dl[:nt]] + self.elev[nt:]
            cp.append(cc)

    def iterNodes(self):
        "Read many nodes and return 1 by 1."
        self.readBeg("NODES")
        while True:
            dl = next(self).split()
            if dl[0] == "</NODES>": break
            nt = len(dl)
            if nt < 2: raise ValueError("At least 2 coordinates were expected")
            if nt >= self.nelev: cc = [float(x) for x in dl[:nt]]
            else:                cc = [float(x) for x in dl[:nt]] + self.elev[nt:]
            yield cc

    def readSnode(self, nam, ndim):
        "Read a special node from thcx format; allow only exactly ndim dimensions."
        dl = next(self).split()
        header = "<%s" % nam
        if dl[0]  != header: raise ValueError("Header %s not found" % (header,))  #May raise IndexError
        footer = "/>"
        if dl[-1] != footer: raise ValueError("Footer %s not found" % (footer,))  #May raise IndexError
        nt = len(dl)-2
        if nt != ndim: raise ValueError("Exactly %d coordinates were expected for special node" % ndim)
        return [float(x) for x in dl[1:-1]]

    def readSnodes(self, nam, ndim):
        """Read many special nodes until a no node entry.

        Each node has exactly ndim dimensions which correspond to
        coordinates and other attributes. Typical is a road which has
        a radius and clothoid parameter."""
        self.readBeg(nam)
        footer = "</%s>" % (nam, )
        cp = []
        while True:
            dl = next(self).split()
            if dl[0] == footer: return cp
            nt = len(dl)
            if nt != ndim: raise ValueError("Exactly %d coordinates were expected for special node" % ndim)
            cp.append([float(x) for x in  dl])

    def readAtt(self, name):
        "Read a short element."
        dl = next(self).split()
        header = "<%s" % name
        if dl[0] != header: raise ValueError("Header %s not found" % header)
        footer = "/>"
        if dl[-1] != footer: raise ValueError("Footer %s not found" % footer)
        return dl[1:-1]

    def readAttb(self, name, s2=None):
        """Read an attribute which may contain blanks inside it, and optionally another attribute which does not.

        For example:
        <hatch>
            "solid"
            0
        </hatch>
        """
        self.readBeg(name)
        s = self.readTextln()
        if s2 is not None: s2 = next(self).strip()
        self.readEnd(name)
        if s2 is None: return s
        return s, s2


    def readTextln(self):
        """Reads a line of text.

        It skips characters until first double quote.
        Then it reads the rest of the line. It deletes the newline and then
        it deletes the last char, which should be double quote."""
        dline = next(self).rstrip("\n")
        i = dline.find('"')
        if i < 0 or dline[-1] != '"': raise ValueError("Double quote(s) not found while reading text.")
        return dline[i+1:-1]


class ThanWfile(object):
    "A wrapper of a write file with format capability."
    formFloat = "%24.15e"

    def __init__(self, fw, proj, name=None):
        "Initialize saved line, line counter."
        self.fw = fw
        self.ind = ""
        self.thanProj = proj
        if name is None:
            try: self.filnam = fw.name   #To acommodate BZ2File object
            except: self.filnam = "<Unknown>"
        else:
            self.filnam = name

    def thanDestroy(self):
        "Break circular references."
        del self.fw, self.thanProj

    def prter(self, mes):
        "Print an error message with file info."
        self.thanProj[2].thanPrter(mes)

    def pushInd(self, n=4):
        "Make the indent bigger."
        self.ind += " "*n

    def popInd(self, n=4):
        "Make the indent smaller."
        n = len(self.ind) - n
        if n <= 0: self.ind = ""
        else: self.ind = self.ind[:n]

    def write(self, s):
        "Delegate write."
        self.writeb(s)

    def writeln(self, s):
        "Delegate write with newline."
        self.writeb("%s%s\n" % (self.ind, s))

    def writeBeg(self, s):
        "Write beginning of element."
        self.writeb("%s<%s>\n" % (self.ind, s))

    def writeb(self, s):
        "Convert string to bytes and write."
        #if Pyos.Python3:
            #b = s.encode(encoding="iso-8859-7", errors="replace")
            #self.fw.write(b)
        #else:
        #    self.fw.write(s)
        self.fw.write(s)

    def writeEnd(self, s):
        "Write end of element."
        self.writeb("%s</%s>\n" % (self.ind, s))

    def writeNode (self, cc):
        "Convert node in a string of thcx format."
        f = self.formFloat
        self.writeb("%s<NODE> %s </NODE>\n" % (self.ind, "".join(f%c for c in cc)))

    def writeNodes (self, cs):    #may accept an iterator of nodes
        "Convert node in a string of thcx format."
        f = self.formFloat
        self.writeBeg("NODES")
        self.pushInd()
        for cc in cs:
            self.writeb("%s %s\n" % (self.ind, "".join(f%c for c in cc)))
        self.popInd()
        self.writeEnd("NODES")

    def writeSnode (self, nam, ndim, cc):
        "Convert a special node in a string of thcx format."
        if len(cc) != ndim: raise ValueError("Exactly %d coordinates were expected for special node" % ndim)
        f = self.formFloat
        self.writeb("%s<%s %s />\n" % (self.ind, nam, "".join(f%c for c in cc)))

    def writeSnodes (self, nam, ndim, cs):
        "Convert node in a string of thcx format."
        f = self.formFloat
        self.writeBeg(nam)
        self.pushInd()
        for cc in cs:
            if len(cc) != ndim: raise ValueError("Exactly %d coordinates were expected for special node" % ndim)
            self.writeb("%s %s\n" % (self.ind, "".join(f%c for c in cc)))
        self.popInd()
        self.writeEnd(nam)

    def writeValid (self, validc):
        "Convert valid attribute of node in a string of thcx format."
        f = " %d"
        self.writeb("%s<valid> %s </valid>\n" % (self.ind, "".join(f%c for c in validc)))

    def writeAtt(self, name, s):
        "Write an attribute."
        self.writeb("%s<%s %s />\n" % (self.ind, name, s))

    def writeAttb(self, name, s, s2=None):
        "Write an attribute which may contain blanks inside it and an attribute which does not."
        self.writeBeg(name)
        self.pushInd()
        self.writeTextln(s)
        if s2 is not None: self.writeln(s2)
        self.popInd()
        self.writeEnd(name)

    def writeTextln(self, s):
        "Writes a line of text with quotes and indent."
        self.writeb('%s"%s"\n' % (self.ind, s))


class ThanRBZfile(ThanRfile):
    "A wrapper of a read file compressed with bz2, with unread and count lines capability."

    def __nextdisabled__(self):   #Thanasis2015_04_05
        "Get next line."
        if self.returnPrev:
            self.returnPrev = False
            return self.prev
        try:
            self.prev = self.fr.readline()
        except EOFError as why:                  #This happens if the bzipped file was not closed properly when it was created
            raise StopIteration
        if self.prev == "": raise StopIteration
        self.nline += 1
        return self.prev


    def isBz2(self):
        "Checks if the file opened is real a bzip2 file."
        try:
            next(self)
        except OSError as why:     #In python 3.3 IOError was merged to OSError
            why = str(why).lower()            #If not transformed to string the in operator does not work
            if "invalid" in why and "data" in why: return False
            raise       #If other IOError propagate
        except EOFError as why:     #EOFError is not a subclass of OSError (or IOError)
            #EOFError: Compressed file ended before the end-of-stream marker was reached
            return False  #This realy means invalid data (or completely empty file)
        else:
            self.unread()
            return True


class ThanWBZfile(ThanWfile):
    "A wrapper of a read file compressed with bz2, with unread and count lines capability."
    pass
