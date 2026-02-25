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

This module defines base class for ThanCad fonts made by straight lines.
"""

from math import pi, cos, sin
import copy
#from p_ggen import Pyos, thanGetEncoding

class ThanFont:
    "Base class for all ThanCad fonts - well perhaps not all."
    thanImiss = 63

    def __init__(self, name):
        "Initialisation: just sets the name."
        self.thanName = name

    def thanGetCodes(self):
        "Return the implemented codes in this font."
        raise AttributeError("getCodes() should be overriden")


class ThanFontLine(ThanFont):
    "Font class made by straight lines with no width, no fill."
    thanHnorm = 1000.0

#=============================================================================

    def __init__(self, name, A, B, C, proportional, dilines):
        """Initialisation.
        o--------o B     All capital characters and most small ones fit into
        |        |       the AB rectangle. Some small characters as p,q,j
      h |        |       use the AC rectangle.
        |        |       The insertion point of the character is point A.
        |   b    |       The local coordinates of points A, B, C must be defined.
      A o--------o       It is assumed that xA == xC.
        |        |       If proportional is True, then the last line of each character,
        |        | h1    (which is not really a line), defines one and only one point,
      C o--------o       which will be the origin of the next character.
                         Note that proportional fonts (which define the above last point)
                         can be also used as fixed-size, since lines with one point are
                         ignored.

        """
        ThanFont.__init__(self, name)
        self.thanABC = tuple(A), tuple(B), tuple(C)       # Dimensions of a rectangle
        self.thanProp = proportional
        self.thanDilines = dilines
        self.thanVert = False
        self.thanMakepairs()
#       self.thanObliqueMake(30)
#       self.thanVerticalMake()

    def thanCopy(self):
        "Make a distinct copy of self."
        return copy.deepcopy(self)

    def thanCopypartial(self, keep):
        "Make a distinct copy of self, copying only certain characters."
        sty = copy.copy(self)
        dil = self.thanDilines; dilnew = {}; cop = copy.deepcopy
        for c in keep+chr(self.thanImiss):
            i = ord(c)
            try: dilnew[i] = cop(dil[i])
            except KeyError: pass
        sty.thanDilines = dilnew
        return sty

    def thanExportTxt(self, fw):
        "Export the font coordinates to a text file."
        fw.write("%s\n" % self.thanName)
        fw.write("%s\n" % (("fixed", "proportional")[self.thanProp],))
        tfont = self.thanDilines
        linesdef = tfont[self.thanImiss]
        for i in range(256):                          # Loop of all the characters
            fw.write("%d\n" % i)
            lines = tfont.get(i, linesdef)
            for pl in lines:                           # Loop of all polylines of a char
                for (xx, yy) in pl: fw.write("%15.3f%15.3f\n" % (xx, yy))
                fw.write("$\n")
            fw.write("$\n")


#=============================================================================

    def thanTkPaint(self, tk, xz, yz, h, a, theta, tags):
        "Draws text using ThanCad's line fonts."
        assert h >= 1, "Text height must be > 1 pixel"
        c = cos(theta); s = sin(theta)
        scale = h / self.thanHnorm; bx  = scale * c; by = scale * s
        if self.thanVert:
            hx2 = 1.2*(0*bx - (-self.thanHnorm*by)); hy2 = 1.2*(-0*by - (-self.thanHnorm*bx))
        else:
            hx2 = self.thanBnorm*bx - 0*by; hy2 = -self.thanBnorm*by - 0*bx

#-------Transform the coordinates

        dc = tk.dc
        w = tk.tkThick
        col = tk.outline
        for c in a:                                    # Loop over all the characters in text
            for pl in self.lines1(c):                  # Loop over all polylines of a char
                plr = [ (xz+xx*bx-yy*by, yz-(xx*by+yy*bx)) for (xx, yy) in pl ]
                if len(plr) > 1: dc.create_line(plr, fill=col, width=w, tags=tags)
            if self.thanProp: xz, yz = plr[0]          # Next character position is defined within current char
            else:             xz += hx2; yz += hy2     # Advance to next fixed character position


    def lines1(self, c1):
        "Find the ascii value of 1 character and return the lines that correspond to it."
        k = ord(c1)
        lines = self.thanDilines.get(k)
        if lines is None: lines = self.thanDilines[self.thanImiss]
        return lines


    def than2linesold(self, xz, yz, h, a, theta, mirrory=False):
        "Returns the text as a list of lines (again lists)."
        c = cos(theta); s = sin(theta)
        scale = h / self.thanHnorm; bx  = scale * c; by = scale * s
        if self.thanVert:
            hx2 = 1.2*(0*bx - (-self.thanHnorm*by)); hy2 = 1.2*(-0*by - (-self.thanHnorm*bx))
        else:
            hx2 = self.thanBnorm*bx - 0*by; hy2 = -self.thanBnorm*by - 0*bx

#-------Transform the coordinates

        tfont = self.thanDilines
        linesdef = tfont[self.thanImiss]
        rlines = []
        #print "than2lines: a=", a
        for c in a:                                    # Loop of all the characters in text
            #print "than2lines: c=", c
            try: lines = tfont[ord(c)]
            except KeyError: lines = linesdef
            for pl in lines:                           # Loop over all polylines of a char
                #print "than2lines: pl=", pl
                if mirrory:
                    plr = [ (xz+xx*bx-yy*by, yz+(xx*by+yy*bx)) for (xx, yy) in pl ]
                else:
                    plr = [ (xz+xx*bx-yy*by, yz-(xx*by+yy*bx)) for (xx, yy) in pl ]
                rlines.append(plr)
            if self.thanProp: xz, yz = plr[0]          # Next character position is defined within current char
            else:             xz += hx2; yz += hy2     # Advance to next fixed character position
        return rlines


    def than2lines(self, xz, yz, h, a, theta, mirrory=False):
        "Iterates through the lines that represent the text."
        c = cos(theta); s = sin(theta)
        scale = h / self.thanHnorm; bx  = scale * c; by = scale * s
        if self.thanVert:
            hx2 = 1.2*(0*bx - (-self.thanHnorm*by)); hy2 = 1.2*(-0*by - (-self.thanHnorm*bx))
        else:
            hx2 = self.thanBnorm*bx - 0*by
            hy2 = -self.thanBnorm*by - 0*bx
            if mirrory: hy2 = -hy2

#-------Transform the coordinates

        for c in a:                                    # Loop of all the characters in text
            for pl in self.lines1(c):                  # Loop over all polylines of a char
                if mirrory:
                    plr = [ (xz+xx*bx-yy*by, yz+(xx*by+yy*bx)) for (xx, yy) in pl ]
                else:
                    plr = [ (xz+xx*bx-yy*by, yz-(xx*by+yy*bx)) for (xx, yy) in pl ]
                yield plr
            if self.thanProp: xz, yz = plr[0]          # Next character position is defined within current char
            else:             xz += hx2; yz += hy2     # Advance to next fixed character position


    def thanCalcSizexy(self, tk, h):
        "Returns the dimensions of the rectangle that the text occupies."
        scale = h / self.thanHnorm
        if self.thanVert: return self.thanBnorm*scale, len(tk)*1.2*h  # In case of vertical plotting, it is fixed sized
        if not self.thanProp: return len(tk)*self.thanBnorm*scale, h  # Fixed size
        xz = 0.0
        for c in tk:                          # Loop of all the characters in text
            lines = self.lines1(c)
            pl = lines[-1]
            xz += pl[0][0]*scale              # Next character position is defined within current char
        return xz, h


    def thanPilPaint(self, tk, xz, yz, h, a, theta):
        "Draws text using ThanCad's line fonts."
        assert h >= 1, "Text height must be > 1 pixel"
        c = cos(theta); s = sin(theta)
        scale = h / self.thanHnorm; bx  = scale * c; by = scale * s
        if self.thanVert:
            hx2 = 1.2*(0*bx - (-self.thanHnorm*by)); hy2 = 1.2*(-0*by - (-self.thanHnorm*bx))
        else:
            hx2 = self.thanBnorm*bx - 0*by; hy2 = -self.thanBnorm*by - 0*bx

#-------Transform the coordinates

        dc = tk.dc
        col = tk.outline
        wid = tk.widthline
        #print "thanPilPaint: a=", a
        for c in a:                                    # Loop of all the characters in text
            for pl in self.lines1(c):                  # Loop of all polylines of a char
                plr = [        (xz+xx*bx-yy*by, yz-(xx*by+yy*bx)) for (xx, yy) in pl ]
                if len(plr) > 1: dc.line(plr, fill=col, width=wid)
            if self.thanProp: xz, yz = plr[0]          # Next character position is defined within current char
            else:             xz += hx2; yz += hy2     # Advance to next fixed character position


    def thanGetCodes(self):
        "Return the implemented codes in this font."
        return self.thanDilines.keys()

#=============================================================================

    def thanMakepairs(self):
        "Makes the list of coordinates as list of tuples and normalises coordinates."
        xor, yor = self.thanABC[0]
        scale = self.thanHnorm / (self.thanABC[1][1] - yor)
        self.thanBnorm = (self.thanABC[1][0] - xor) * scale
        for lines in self.thanDilines.values():   #works for python2,3
            if type(lines) == int: continue
            for li in lines:
                if len(li) < 1: continue
                c = li[0]
                try:    c[0]; c[1]
                except: li[:] = [((li[i]-xor)*scale, (li[i+1]-yor)*scale) for i in range(0, len(li), 2)]
                else:   li[:] = [((x-xor)*scale, (y-yor)*scale) for x,y in li]

        self.thanDilines.setdefault(self.thanImiss, [(self.thanBnorm*0.5, 0.0)] )

        for i in range(10): # De-index font
            again = False
            for key,lines in self.thanDilines.items():  #works for python2,3
                if type(lines) != int: continue
                self.thanDilines[key] = self.thanDilines[lines]   # Note that this does NOT waste memory
                again = True
            if not again: return
        raise ValueError("font %s: key indexing too nested or circular!!" % self.thanName)

    def thanWidthScale(self, scale):
        "Scale only x coordinates by f."
        assert scale > 0.0
        for lines in self.thanDilines.values():   #works for python2,3
            lines[:] = [ [(x*scale, y) for x,y in li] for li in lines]
        self.thanBnorm *= scale

    def thanObliqueMake(self, phi):
        "Make the font oblique; rotate only y coordinate; affects only x coordinate."
        assert -90.0 < phi < 90.0
        phi = phi * pi / 180; c = cos(phi); s = sin(phi)
        for lines in self.thanDilines.values():  #works for python2,3
            lines[:] = [ [(x + y*s, y) for x,y in li] for li in lines]

    def thanUpsidedownMake(self):
        "Makes the font upside down; essentially the letters are mirrored."
        h = self.thanHnorm
        for lines in self.thanDilines.values():   #works for python2,3
            lines[:-1] = [ [(x, h-y) for x,y in li] for li in lines[:-1]]

    def thanBackwardsMake(self):
        "Makes the font look backwards; essentially the letters are mirrored."
        for lines in self.thanDilines.values():   #works for python2,3
            if self.thanProp: b = lines[-1][0][0]
            else:             b = self.thanBnorm
            lines[:-1] = [ [(b-x, y) for x,y in li] for li in lines[:-1]]

    def thanVerticalMake(self):
        "Makes the font look backwards; essentially the letters are mirrored."
        for lines in self.thanDilines.values():   #works for python2,3
            if self.thanProp: b = lines[-1][0][0]*0.5
            else:             b = self.thanBnorm*0.5
            h = self.thanHnorm
            lines[:-1] = [ [(x-b, y-h) for x,y in li] for li in lines[:-1]]
        self.thanProp = False            # Next character position defined within current char, is invalid
        self.thanVert = True

thanFonts = {}
