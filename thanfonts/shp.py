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

This module imports shape files (.shp).
"""

from math import pi, sqrt, atan2, cos, sin, fabs
import codecs, unicodedata
from p_gmath import dpt
from p_ggen import Struct
from .thanfont import ThanFontLine, thanFonts


_xyr = \
{ 0: ( 1.0,  0.0),
  1: ( 1.0,  0.5),
  2: ( 1.0,  1.0),
  3: ( 0.5,  1.0),
  4: ( 0.0,  1.0),
  5: (-0.5,  1.0),
  6: (-1.0,  1.0),
  7: (-1.0,  0.5),
  8: (-1.0,  0.0),
  9: (-1.0, -0.5),
 10: (-1.0, -1.0),
 11: (-0.5, -1.0),
 12: ( 0.0, -1.0),
 13: ( 0.5, -1.0),
 14: ( 1.0, -1.0),
 15: ( 1.0, -0.5),
}

class ShpIter:
    "Iterator for a file which contains a shape."

    def __init__(self, fr):
        "Initialises shape file reader."
        self.__fr = fr
        self.__savedLine = ""
        self.__bufferEmpty = True
        self.__ilin = 0

    def __next__(self):
        "Send the next entry."
        if self.__bufferEmpty:
            while True:
                dline = next(self.__fr)
                self.__ilin += 1
                i = dline.find(";")
                if i >= 0: dline = dline[:i]
                dline = dline.strip()
                if len(dline) != 0: break
            self.__savedLine = dline.replace("(", "").replace(")", "")
        self.__bufferEmpty = True
        dl = [dl1.strip() for dl1 in self.__savedLine.split(",")]
        dl = [dl1 for dl1 in dl if dl1 != ""]
        return dl

    def unread(self):
        "Unreads the current line."
        self.__bufferEmpty = False

    def setnext(self, dl):
        "Sets a line that will be 'read' when next() is called."
        self.__bufferEmpty = False
        self.__savedLine = ",".join(dl)

    def __iter__(self): return self

    def prer(self, t):
        "Prints error message to suitable output."
        t1 = "Error at line %d:\n    %s\n    %s\n" % (self.__ilin, self.__savedLine, t)
        print(t1)

    def prwa(self, t):
        "Prints warning message to suitable output."
        t1 = "Warning at line %d:\n    %s\n    %s\n" % (self.__ilin, self.__savedLine, t)
        print(t1)

class Inslist(list):
    def __init__(self, *args, **kw):
        list.__init__(self, *args, **kw)
        self.thani = -1
    def __next__(self):
        self.thani += 1
        if self.thani >= len(self): raise StopIteration()
        return self[self.thani]
    def replaceSubshape(self, other):
        i1 = self.thani - 1
        self[i1:i1+2] = other[:-1]
        self.thani = i1-1
    def __iter__(self): return self

class ThanCadShapefile:
    "An object to read and convert a .shp file."

    def __init__(self):
        self.__shape = {}
        self.fontname = None

    def thanRead(self, fr):
        "Reads the shape from an opened file."
        it = ShpIter(fr)
        imax = 258
        for dl in it:
            if dl[0][:1] != "*": it.prer("Asterisk not found!"); continue
            try:
                ishape, nbytes = dl[0][1:].lower(), int(dl[1])
                if len(dl) < 3: tshape = ""
                else:           tshape = dl[2]
                if   ishape == "degree_sign":        ishape = 256
                elif ishape == "plus_or_minus_sign": ishape = 257
                elif ishape == "diameter_symbol":    ishape = 258
                elif ishape == "unifont":            ishape = 0; imax = 65535
                elif ishape[:1] == "0":              ishape = int(ishape, 16)
                else:                                ishape = int(ishape)
            except:
                it.prer("Syntax error")
                print(dl)
                import sys
                sys.exit()
                continue
#           sameline = False   # When more entries in the first line the number of bytes is 1 more than those defined!!!!!!!!!!!!!!!
#           if len(dl) > 3 and ishape != 0: it.setnext(dl[3:]); sameline = True
            if ishape < 0 or ishape > imax: it.prer("Illegal shape number: %d" % ishape); continue
            if nbytes < 0: it.prer("Illegal number of bytes: %d" % nbytes); continue
            bytes = self.__getBytes(it, nbytes)
            if bytes is None: continue
            if ishape in self.__shape: it.prer("Shape code %d is multiply declared." % ishape); continue
            if ishape == 0:
                self.__shape[ishape] = None
                if len(bytes) < 3:  it.prer("Not all font attributes defined."); return None
                self.above, self.below, self.modes = bytes[:3]
                self.fontname = tshape
            else:
                shp = Struct(); shp.ord = ishape; shp.name = tshape; shp.bytes = bytes
                if not self.thanConvert1(it, shp): return False
                self.__shape[ishape] = shp
        if 0 not in self.__shape: it.prer("Font name/attrinutes not defined."); return False
        del self.__shape[0]
        return self.__resolveSubshapes(it)

    def __getBytes(self, it, nbytes):
        "Reads the byte that define the geometry of the shape."
        bytes = []
        for dl in it:
            if dl[0][:1] == "*": it.unread(); break
            for n in dl:
                try:
                    if   n[:1] == "-": pr = -1; n = n[1:]
                    elif n[:1] == "+": pr =  1; n = n[1:]
                    else:              pr =  1
                    if n[:1] == "0": n = pr*int(n, 16)
                    else:            n = pr*int(n)
                except: it.prer("Not an integer: %s" % n); return None
                bytes.append(n)
        if len(bytes) != nbytes:
#            if not sameline or len(bytes) != nbytes-1:          # very very very unprofessional!!!!!!!!!!!!!
            it.prwa("Less or more than %d bytes are defined!" % nbytes)
        if len(bytes) < 1:
            it.prwa("No bytes defined for shape.")
            bytes.append(0)
        elif bytes[-1] != 0:
            it.prwa("Last byte is not zero!")
            bytes.append(0)
        return bytes

    def thanConvert1(self, it, shp, xnow=0.0, ynow=0.0, fact=1.0, xystack=None):
        "Convert 1 character to coordinates; subshapes are not resolved."
        itb = Inslist(shp.bytes)
        lis = []; li = []; decipher = []
        if xystack is None: xystack = []
        pendown = True; shp.resolved = True
        for byte in itb:
            if byte > 255: it.prer("%d: byte is longer than 8 bits."%byte); return None
            byte9 = byte
#           d = int(byte/16)
            d = (byte >> 4) & 15
#           byte %= 16
            byte &= 15
            try:
                if d > 0:
                    if pendown and len(li) == 0: li.append((xnow, ynow))
                    x, y = _xyr[byte]
                    decipher.append("%3d: pen_relative %3d %3d\n" % (byte9, x, y))
                    xnow += x*d*fact; ynow += y*d*fact
                    if pendown: li.append((xnow,ynow))
                elif byte == 0:                              # End of shape
                    decipher.append("%3d: end\n" % (byte9,))
                    break
                elif byte == 1:                              # Move pen down
                    if not pendown: assert len(li) == 0
                    pendown = True
                    decipher.append("%3d: pendown\n" % (byte9,))
                elif byte == 2:                              # Nove pen up
                    if pendown:
                        if len(li) > 0: assert len(li) > 1; lis.append(li)
                        li = []
                    pendown = False
                    decipher.append("%3d: penup\n" % (byte9,))
                elif byte == 3:                              # Divide lengths by next byte
                    byte8 = next(itb)
                    fact /= byte8
                    decipher.append("%3d: factor / %3d\n" % (byte9, byte8))
                elif byte == 4:                              # Multiply lengths by next byte
                    byte8 = next(itb)
                    fact *= byte8
                    decipher.append("%3d: factor * %3d\n" % (byte9, byte8))
                elif byte == 5:                              # Push current position to stack
                    xystack.append((xnow, ynow))
                    decipher.append("%3d: push to stack\n" % (byte9,))
                elif byte == 6:                              # Pop position from stack
                    if len(xystack) < 1: it.prer("6: Pop from empty stack."); return None
                    if pendown:
                        if len(li) > 0: assert len(li) > 1; lis.append(li)
                        li = []
                    xnow, ynow = xystack.pop(-1)
                    decipher.append("%3d: pop from stack\n" % (byte9,))
                elif byte == 7:                              # Draw subshape at this position
                    i1 = next(itb)
                    if i1 in self.__shape and self.__shape[i1].resolved:
                        itb.replaceSubshape(self.__shape[i1].bytes)
                    else:
                        shp.resolved = False
                        decipher.append("%3d: draw subshape %d (not resolved)\n" % (byte9, i1))
                elif byte == 8:                              # Explicit x,y of 1 point follow
                    if pendown and len(li) == 0: li.append((xnow, ynow))
                    x = next(itb); y = next(itb)
                    decipher.append("%3d: pen_relative %d %d\n" % (byte9, x, y))
                    xnow += x*fact; ynow += y*fact
                    if pendown: li.append((xnow,ynow))
                elif byte == 9:                              # Explicit x,y of many points follow
                    decipher.append("%3d: multiple pen_absolute:\n" % (byte9,))
                    while True:
                        x = next(itb); y = next(itb)
                        decipher.append("     %d %d\n" % (x, y))
                        if x == 0 and y == 0:
                            decipher.append("     %d %d: stop\n" % (x, y))
                            break                            # No more x,y points
                        decipher.append("     %d %d\n" % (x, y))
                        if pendown and len(li) == 0: li.append((xnow, ynow))
                        xnow += x*fact; ynow += y*fact
                        if pendown: li.append((xnow,ynow))
                elif byte == 10:                             # Draw octant arc
                    r = next(itb)*fact
                    if r == 0: it.prer("Error: arc radius is zero"); return None
                    byte = next(itb)
                    if byte < 0: idd = -1; byte = -byte
                    else:        idd =  1
#                    dth = byte%16
                    dth = byte & 7
                    if dth == 0: dth = 8
                    byte = (byte >> 4) & 7
                    decipher.append("%3d: arc radius %d begin_octant %d octants %d\n" % (byte9, r, byte, idd*dth))
                    th = byte*2*pi/8
                    xc = xnow-r*cos(th); yc = ynow-r*sin(th)
                    xnow, ynow = self.__arc(li, xnow, ynow, pendown, xc, yc, r, th, idd*dth*2*pi/8)
                elif byte == 11:                             # Draw (more) general arc
                    dth1 = (pi/180) * next(itb)*45/256
                    dth2 = (pi/180) * next(itb)*45/256
                    r = next(itb) * 256; r = (r+next(itb)) * fact
                    if r == 0: it.prer("Error: arc radius is zero"); return None
                    byte = next(itb)
                    if byte < 0: idd = -1; byte = -byte
                    else:        idd =  1
                    dth = byte & 7
                    if dth == 0: dth = 8
                    byte = (byte >> 4) & 7
                    decipher.append("%3d: arc radius %d begin_octant %d octants %d dth1=%10.2f dth2=%10.2f\n" % (byte9, r, byte, dth*idd, dth1, dth2))
                    th = byte*2*pi/8 + dth1
                    dth = idd * (dth * 2*pi/8 + dth2-dth1)
                    xc = xnow-r*cos(th); yc = ynow-r*sin(th)
                    xnow, ynow = self.__arc(li, xnow, ynow, pendown, xc, yc, r, th, dth)
                elif byte == 12:                             # Draw 1 buldge
                    x = next(itb); y = next(itb); byte8 = next(itb)
                    decipher.append("%3d: buldge_relative %d %d curvature %d\n" % (byte9, x, y, byte8))
                    xnow, ynow = self.__buldge(li, xnow, ynow, fact, pendown, x, y, byte8)
                elif byte == 13:                             # Draw many buldges
                    decipher.append("%3d: multiple_buldge_relative:\n" % (byte9,))
                    while True:
                        x = next(itb); y = next(itb)
                        if x == 0 and y == 0:
                            decipher.append("     %d %d: stop\n" % (x, y))
                            break
                        byte8 = next(itb)
                        decipher.append("     %d %d curvature %d\n" % (x, y, byte8))
                        xnow, ynow = self.__buldge(li, xnow, ynow, fact, pendown, x, y, byte8)
                elif byte == 14:
                    decipher.append("%3d: skip next:\n" % (byte9,))
                    self.__skipNext(it, itb)
                else:
                    it.prer("%d: illegal special command."%byte); return None

            except StopIteration: it.prer("Incomplete definition bytes."); return None
        shp.bytes = itb[:]
        if len(xystack) > 0: it.prwa("Stack is not empty after shape definition.")
        if fact != 1.0: it.prwa("Factor is not reset to 1 after shape definition.")
        if len(li) > 0: assert len(li) > 1; lis.append(li)
        lis.append([xnow, ynow])
        shp.lines = lis
        shp.decipher = decipher
        return True

    def __arc(self, li, xnow, ynow, pendown, xc, yc, r, th, dth):
        "Creates an arc."
        nseg = 3
#       n = int(dth*nseg/(0.25*pi))+1
        n = fabs(dth)/(0.25*pi)
        n = int(n*nseg)+1
        dth /= n
        for i in range(n):
            th += dth
            if pendown and len(li) == 0: li.append((xnow, ynow))
            xnow = xc+r*cos(th); ynow = yc+r*sin(th)
            if pendown: li.append((xnow, ynow))
        return xnow, ynow

    def __buldge(self, li, xnow, ynow, fact, pendown, dx, dy, b):
        "Process a buldge entry."
        dx *= fact; dy *= fact
        if b == 0:
            if pendown and len(li) == 0: li.append((xnow, ynow))
            xnow += dx; ynow += dy
            if pendown: li.append((xnow,ynow))
        else:
            d = sqrt(dx**2+dy**2)
            if d == 0.0: return xnow, ynow
            th = atan2(dy, dx)
            idd = b/abs(b)
            h = abs(b)*d/2/127
            r = ((d/2)**2+h**2)/2/h
            th += idd*pi*0.5
            xc = xnow+dx*0.5+(r-h)*cos(th)
            yc = ynow+dy*0.5+(r-h)*sin(th)
            th = atan2(ynow-yc, xnow-xc)
            dth = dpt(atan2(ynow+dy-yc, xnow+dx-xc) - th)
            if idd > 0:
                assert dth >= 0.0 and dth <= pi
            else:
                dth -= 2*pi
                assert dth <= 0.0 and dth >= -pi
            xnow, ynow = self.__arc(li, xnow, ynow, pendown, xc, yc, r, th, dth)
        return xnow, ynow

    def __skipNext(self, it, itb):
        "Skips next (compound) command."
        byte = next(itb)
        d = (byte >> 4) & 15
        byte &= 15
        if d > 0: return
        if byte in (0,1,2,5,6,14): return
        if byte in (3,4,7,10): next(itb); return
        if byte == 8: next(itb); next(itb); return
        if byte == 99:
            while True:
                x = next(itb); y = next(itb)
                if x == 0 and y == 0: return
        elif byte == 11:
            for i in range(5): next(itb)
        elif byte == 12:
            for i in range(3): next(itb)
        elif byte == 13:
            while True:
                x = next(itb); y = next(itb)
                if x == 0 and y == 0: break
                next(itb)
        else:
            it.prer("%d: illegal special command." % byte); return None

    def __resolveSubshapes(self, it):
        "A all subshape definitions."
        for tries in range(10):
            allresolved = True
            for shp in self.__shape.values():   #works for python2,3
                if shp.resolved: continue
                if not self.thanConvert1(it, shp): return False
                if not shp.resolved: allresolved = False
            if allresolved: return True
        it.prer("Subshapes nested too deeply.")
        return False

    def toThanCad(self):
        "Transforms the shape collection to a ThanCad line font."
        lines = {}
#       imiss = 63
#       if imiss not in self.__shape:
#           self.__shape[imiss] = shp = Struct()
#           shp.ord = imiss; shp.name = "?"; shp.bytes = []
#           shp.lines = [[2,0]]; shp.resolved = True
#        for i1 in range(256):
#           if i1 not in self.__shape: lines[i1] = imiss; continue
#           lines[i1] = self.__shape[i1].lines
        for i1,shp in self.__shape.items():    #works for python2,3
            lines[i1] = self.__shape[i1].lines
        thanFonts[self.fontname] = ThanFontLine(self.fontname, (0,0), (6,self.above), (0,-self.below),
                                   True, lines)

    def info(self):
        "Prints info of the shape file."
        print("Font:", self.fontname)
        for a in "above below modes".split():
            print("          ", a, ":", getattr(self, a))
#       unu = codecs.getencoder("iso-8859-1")
        iss = sorted(self.__shape.keys())   #works for python2,3
        for i in iss:
            shp = self.__shape[i]
#           t = unu(unichr(i))
            t = unicodedata.name(unichr(i), "<none>")
            print("ord=%d   shape_name=%s  unicode_name=%s" % (i, shp.name, t))
            print("     Bytes (with subshapes resolved):")
            for i in range(0, len(shp.bytes), 18):
                b1 = shp.bytes[i:i+18]
                print("    ", (len(b1)*"%3d,") % tuple(b1))
            print("     Deciphered bytes (with subshapes resolved):")
            for b1 in shp.decipher: print("    ", b1,)
            print("     Generated lines:")
            for li in shp.lines:
                print("    ", li)

def test():
    "Tests the module with txt.shp."
    fs = "Xgothicen"
    fs = "txt gdt greeks arfor arford leroy mleroy complex dim grekcomp "\
         "monotxt simplex times timesout italic italian russell"
    fs = fs.split()[-1]
    for fn in fs.split():
        shp = ThanCadShapefile()
        if shp.thanRead(open("./thanfonts/developer/shp/"+fn+".shp")):
            shp.toThanCad()
#            shp.info()
        else:
            break

if __name__ == "__main__": test()
