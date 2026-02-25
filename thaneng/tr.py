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

This module implements semiautomatic tracing of curves of a raster image.
Specifically, it is intended to help the digitising of contour lines
of topographic maps.
"""

from math import hypot
import p_gimage

FORKMAX=5; FORKSTEPS=20; STEPS=10000; MAXWIDTH=100



class _RasterTracker:
    def __init__(self):
        pass
    def __getitem__(self, ji):
        raise AttributeError(__name__+" must be overwritten.")
    def __setitem__(self, ji, val):
        raise AttributeError(__name__+" must be overwritten.")


    def traceAll(self):
        "Find and digitize all the possible lines."
        self.visited.clear()
        for ia in range(self.height):
#        for ia in range(100):
            print(ia, "/", self.height)
            ja = 0
            while ja < self.width:
                for iloop in (0,):
                    if not self[ja, ia]: j2 = ja + 1; break
                    j1, j2 = self.thickx(ia, ja)
                    if self.visited.in_((ia, int((j1+j2)/2))): break
                    if j2-j1+1 > MAXWIDTH:
                        self.visited.add((ia, int((j1+j2)/2)))
                        print("Max width encounter:", j2-j1+1, ". Point is ignored.")
                        break
                    curve = self.trace(ia, ja)
                    curves.append(curve)
                ja = j2 + 1


    def trace(self, i, j, fork=0, curve=None):
        "Trace a curve semiautomatically beginning in i, j."
        assert self[j, i], "trace() must begin at point which is not empty."
        if curve is None: curve = []
        j1, j2 = self.thickx(i, j)
        jc = int((j1+j2)/2)
        print("New trace: fork=%d: begin at i=%d, j=%d" % (fork, i, j))
        if j != jc:
            j = jc
            print("    Warning: does not begin at center of gravity of current raster line segment.")
            print("             New begin at i=%d, j=%d" % (i, j))

        while len(curve) < STEPS:
            if fork > 0 and len(curve) > FORKSTEPS: return curve
            j1, j2 = self.thickx(i, j)
            jc = int((j1+j2)/2)
            print(i, j)
            assert j == jc, "Point not at center of gravity of current raster line segment!!!"

            curve.append((i, j))
            self.visited.add((i, j))
            if fork == 0: self.im.putpixel((j, i), 100)
#            print "trace i,j", i, j, "-->>", i, int((j1+j2)/2)
            todo = self.candidatej(i+1, j1, j2)
            todo.extend(self.candidatej(i-1, j1, j2))
            print(i, j, "step=", len(curve), "fork=", fork, "# of todos=", len(todo))
            todo.sort(key=lambda ij: hypot(ij[0]-i, ij[1]-j))
#            todo = [((i1-i)**2+(j1-j)**2, i1, j1) for (i1,j1) in todo]
#            todo.sort()
#            todo = [a[1:] for a in todo]
#            print len(todo)

            if len(todo) == 0:
                if fork > 0: return curve
                else:        return curve, []
            elif len(todo) == 1:
                i, j = todo[0]
            elif fork == 0:
#               if len(curve) <= 1:
#                   i, j = todo[0]
#               else:
                    print("tr(2) todo->", len(todo))
                    fcs = self.tryAllForks(todo, fork)
                    if fcs[1][0] > 10: return curve, fcs # At least 2 curves with 10 pixels;let user decide
                    assert fcs[0][0] > 0, "since len(todo) > 1, how can this happen?"
                    i, j = fcs[0][1][0]    # Next curve is the longest
                    print("Only one long fork: next i,j=", i, j)  # Only 1 curve with len() >= 10, or all curves with len() < 10
            else:    # If fork >= 1, then we need the longest path from fork 0, so that the user can choose at fork 0
                self.chooseLongest(curve, todo, fork)
                return curve

        else:
#            self.plotcurve(curve)
#            self[j, i] = "E"
#            self.save(open("res.asc", "w"))
            print("\nMax number of steps encountered: %d" % STEPS)
            if fork == 0: return curve, []
            return curve


    def tryAllForks(self, todo, fork):
        "Get all the possible curves that fork at this point."
        print("tryallforks tracepoint(1)")
        fork += 1
        self.visited.pushLevel()
        cs = []
        for i1, j1 in todo:
            print("tryallforks: i1, j1=", i1, j1)
            j11, j12 = self.thickx(i1, j1)
            c2 = []
            if not self.visited.in_((i1, int((j11+j12)/2) )):  # Maybe c1 includes candidate i1,j1
                c2 = self.trace(i1, j1, fork)
            cs.append((len(c2), c2))
        cs.sort(); cs.reverse()
        self.visited.popLevel()
        return cs


    def chooseLongest(self, curve, todo, fork):
        """Choose the longest line.

        If FORKMAX==1 then it chooses the longest line that does
        not have a fork.
        """
        fork += 1
        if fork > FORKMAX: return
        n = len(curve)
        i1, j1 = todo[0]
        c1 = self.trace(i1, j1, fork)
        self.visited.pushLevel()
        for i1, j1 in todo[1:]:
            j11, j12 = self.thickx(i1, j1)
            if self.visited.in_((i1, int((j11+j12)/2) )): continue  # Maybe c1 includes candidate i1,j1
            c2 = self.trace(i1, j1, fork)
            if len(c2) > len(c1): c1, c2 = c2, c1
        self.visited.popLevel()
        curve.extend(c1)


    def candidatej(self, i, j1, j2, all=1):
        "Checks for direction candidates."
        todo = []
        if i < 0 or i >= self.height: return todo
        jj1, jj2 = max(j1-1, 0), min(j2+2, self.width)
        while jj1 > 0 and self[jj1,i]: jj1 -= 1    #Find blank until start of current raster line
        while True:
            for jj in range(jj1, jj2):            #Find nonblank character beginning from from previous blank
                if self[jj, i]: break
            else:
                return todo                        #No more nonblanks in current raster line;finish
            jj1 = jj                               #Found nonblank; it is the beginning of non-blank segment
            for jj in range(jj1, self.width):     #Find thickness of nonblank segment
                if not self[jj, i]: jj -= 1; break
            jc = int((jj1+jj)/2)                   #Center of gravity of segment; if not visited...
            if not self.visited.in_((i,jc)): todo.append((i,jc))    #...append it to the todo list
            jj1 = jj + 1                           #Pixel (i,jj1) is blank; go to find next non-blank segment in current raster line


    def thickx(self, i, j):
        "Finds the thickness of a line at point i,j in the x direction."
        for j1 in range(j, -1, -1):
            if not self[j1, i]: j1 += 1; break
        for j2 in range(j, self.width):
            if not self[j2, i]: j2 -= 1; break
        return j1, j2


    GAPTOLMAX = 0      #=2
    GAPTOLMIN = 0      #=1
    def thickx_complex(self, i, j):
        """Finds the thickness of a line at point i,j in the x direction.

        If it finds a gap of more than MGAPMAX pixels long it stops. Else it
        continues. If the gap is <= MGAPMIN it is filled. Else it is checked
        that the whole thickness is > 2*gap. If it is not
        """
        gaptolmax1 = self.GAPTOLMAX
        while gaptolmax1 >= self.GAPTOLMIN:
            gapmax = 0
            jg1 = j                          # First blank pixel
            for j1 in range(j, -1, -1):
                if self[j1, i]:
                    jg1 = j1
                else:
                    gap = abs(jg1-j1)
                    if gap > gaptolmax1: j1 = jg1; break
                    if gap > gapmax: gapmax = gap

            jg2 = j
            for j2 in range(j, self.width):
                if self[j2, i]:
                    jg2 = j2
                else:
                    gap = abs(jg2-j2)
                    if gap > gaptolmax1: j2 = jg2; break
                    if gap > gapmax: gapmax = gap

            if abs(jg2-jg1) > 3*gapmax: break
            if abs(jg2-jg1) == 0: break
            gaptolmax1 /= 2
        print("thickx: j1,j2=", j1, j2)
        return j1, j2


    def thick(self, i, j):
        "Finds the thickness of a line at point i,j in the x and y directions."
        for i1 in range(i, -1, -1):
            if not self[j, i1]: i1 += 1; break
        for i2 in range(i, self.height):
            if not self[j, i2]: i2 -= 1; break
        for j1 in range(j, -1, -1):
            if not self[j1, i]: j1 += 1; break
        for j2 in range(j, self.width):
            if not self[j2, i]: j2 -= 1; break
        return i1, i2, j1, j2

    def thickness(self, curve):
        "Finds the average thickness of a line."
        t = 0.0
        for i, j in curve:
            i1, i2, j1, j2 = self.thick(i, j)
            t1 = min(i2-i1+1, j2-j1+1)
            print(t1)
            t += t1
        return t / float(len(curve))

    def plotcurve(self, curve):
        "Plot the curve to the image."
        k = 0
        for i, j in curve:
            self[j, i] = str(k)
            k = (k+1) % 10

    def plotcurvea(self, curve):
        "Plot the curve to the image."
        k = ord("A")
        for i, j in curve:
            self[j, i] = chr(k)
            k += 1
            if k > ord("Z"): k = ord("A")


class ThanAscRasterTracker(_RasterTracker):
    def __init__(self, fr):
        "Reads an ascii raster."
        _RasterTracker.__init__(self)
        self.dlines = list(fr)
        self.height = len(self.dlines)
        self.width = max([len(dl) for dl in self.dlines])
        self.width = max(self.width, self.height)
        self.visited = ThanMultiSet()
        for i,dl in enumerate(self.dlines):
            dl = dl.rstrip("\n")
            self.dlines[i] = list(dl + " " * (self.width-len(dl)))
    def __getitem__(self, ji):
        j, i = ji
        return not self.dlines[i][j] == " "
    def __setitem__(self, ji, val):
        j, i = ji
        self.dlines[i][j] = val[0]

    def save(self, fw):
        "Saves the image to an ascii file."
        for dl in self.dlines: fw.write("".join(dl) + "\n")


class ThanPilRasterTracker(_RasterTracker):
    def __init__(self, im, visited):
        "Reads an image."
        _RasterTracker.__init__(self)
        assert im.mode == "1" or im.mode == "L", "Image should be black and white!"
        self.im = im
        self.width, self.height = im.size
        self.visited = visited

    def __getitem__(self, ji):
        return self.im.getpixel(ji) < 127

    def __setitem__(self, ji, val):
        if val == " ": self.im.putpixel(ji, 255)
        else:          self.im.set(ji, 0)

    def save(self, fw):
        "Saves the image to a new file."
        self.im.save(fw)

    def makeAsc(self, fw):
        "Saves the image as an ascii file."
        for i in range(self.height):
            for j in range(self.width):
                if self[j, i]: fw.write("o")
                else:          fw.write(" ")
            fw.write("\n")

    def destroy(self):
        "Breaks circular dependencies."
        pass


class ThanMultiSet:
    "Multilevel set."

    def __init__(self):
        "Create level 0 set."
        self.__sets = [set()]
        self.thanLevel = 0

    def add(self, val):
        "Add point to the highest level set."
        self.__sets[-1].add(val)

    def in_(self, val):
        "Check if val is in one of the sets."
        for set1 in self.__sets:
            if val in set1: return True
        return False


    def pushLevel(self):
        "Create a new level of sets."
        self.thanLevel += 1
        self.__sets.append(set())


    def popLevel(self):
        "Delete the highest level of sets."
        assert len(self.__sets) > 0, "There is no level to delete!"
        self.__sets.pop()

    def clear(self):
        "Empties the multiset."
        del self.__sets[1:]
        self.__sets[0].clear()


def test():
    "Various standalone tests."
    global curves
    curves = []
    fot1 = ThanPilRasterTracker(p_gimage.open("seg1.bmp"))
#    fot1 = ThanAscRasterTracker(open("seg1.asc"))
#    print "thickness=", fot1.thickness(curve)
#    curves.append(curve)

    fot1.traceAll()
#    fot1.plotcurve(curve)
#    fot1.save(open("res.asc", "w"))

    fw = open("res.syn", "w")
    i = 0
    for curve in curves:
        for y,x in curve:
            i += 1
            fw.write("%-10d%15.3f%15.3f\n" % (i, float(x), float(fot1.height-y)))
        fw.write("T\n")

#    fot1 = ThanPilRasterTracker(p_gimage.open("3573_8.bmp"))
#    print "m,n=", fot1.m, fot1.n
#    curvefork = fot1.forks(curve, visited)
#    fot1.plotcurvea(curvefork)

if __name__ == "__main__": test()
