##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module defines the ThanCad TextStyle, and an object used if an image is
not found or if Python Image Library is not installed.
"""
import copy

class ThanTstyle:
    def __init__(self, name, font, height=0.0, widthfactor=1.0, obliqueangle=0.0,
                 upsidedown=False, backwards=False, vertical=False):
        "Initialise textstyle object."
	self.thanName = name
	self.thanFont       = font.thanCopy()
	self.thanHeight     = height
	self.thanWidthfactor= widthfactor
	self.thanOblique    = obliqueangle
        self.thanUpsidedown = upsidedown
	self.thanBackwards  = backwards
	self.thanVertical   = vertical
#	self.thanRecreate()

    def thanCopy(self):
        "Make a distinct copy of self."
	c = copy.copy(self)
	c.thanFont = self.thanFont.thanCopy()
	return c


class ThanImageMissing:
    def __init__(self, size=(100,100)): self.size = size
    def copy    (self): return ThanImageMissing(self.size)
    def __error (self):	raise ValueError, "Image was not found/not supported/corrupted."
    def getpixel(self, *args, **kw): self.__error()
    def resize  (self, *args, **kw): self.__error()
    def paste   (self, *args, **kw): self.__error()
    def crop    (self, clip):
        j1, i1, j2, i2 = clip
        return ThanImageMissing(size=(j2-j1+1, i2-i1+1))
    def transpose(self, rot):
        try: from Image import ROTATE_180
        except: ROTATE_180 = 3   #This value was taken from PIL October 15, 2010
        if rot == ROTATE_180: dxp, dyp = self.size
        else:                 dyp, dxp = self.size
        return ThanImageMissing(size=(dxp, dyp))


class ThanCoor(list):
    "A list with attribute aliases."
    def __getx(self): return self[0]
    def __gety(self): return self[1]
    def __getz(self): return self[2]
    def __gett(self): return self[3]
    def __setx(self, val): self[0] = val
    def __sety(self, val): self[1] = val
    def __setz(self, val): self[2] = val
    def __sett(self, val): self[3] = val
    x = property(__getx, __setx)
    y = property(__gety, __sety)
    z = property(__getz, __setz)
    t = property(__gett, __sett)


def testThanCoorMemory():
    "Tests the memory consumed by this class."
    import time
    from p_ggen import prg
    a = []
    c = [1.0,2.0,3.0]
    n = 1100000
    cl = ThanCoor
    t1 = time.time()
    for i in xrange(n):
        a.append(cl(c))
    t2 = time.time()
    prg("Time for ThanCoor: %s" % (t2-t1,))
    x=raw_input()


def testThanCoor():
    "Tests the list class."
    from p_ggen import prg
    c = ThanCoor((1.0,2.0,3.0,4.0))
    prg("%s" % c)
    prg("x=%s=%s" % (c[0], c.x))
    prg("y=%s=%s" % (c[0], c.y))
    prg("z=%s=%s" % (c[0], c.z))
    prg("t=%s=%s" % (c[0], c.t))
    c.x = 10
    c.y = 20
    c.z = 30
    c.t = 40
    prg("%s" % c)
    prg("x=%s=%s" % (c[0], c.x))
    prg("y=%s=%s" % (c[0], c.y))
    prg("z=%s=%s" % (c[0], c.z))
    prg("t=%s=%s" % (c[0], c.t))
    c = ThanCoor((1.0,2.0,3.0))
    prg("%s" % c)
    prg("x=%s=%s" % (c[0], c.x))
    prg("y=%s=%s" % (c[0], c.y))
    prg("z=%s=%s" % (c[0], c.z))
    prg("t=%s=%s" % (c[0], c.t))


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


class ThanId:
    """Class to return unique ids (e.g. for wxWindows windows).

    Ids 0-99 are reserved. It seems that when ids are plain integers
    or plain integers converted to strings with str(), Tkinter will
    neither work, nor complain about it. A prefix with a letter is
    a workaround."""

    def __init__(self, id=20000, prefix="t"):
        "Initialise seed."
        self.id = id
        self.prefix = prefix

    def new(self, nids=1):
        "Return an id so that id, id+1, id+2, ..., id+nids-1 are unique."
        i = self.id
        self.id += nids
        return self.prefix + str(i)

    def new2(self, nids=1):
        "Return an id so that id, id+1, id+2, ..., id+nids-1 are unique, as both integer and text."
        i = self.id
        self.id += nids
        return i, self.prefix + str(i)

    def addprefix(self, id1):
        "Add the prefix to an existing integer handle and adjust max id."
        if id1 >= self.id: self.id = id1+1
        return self.prefix + str(id1)

    def delprefix(self, tid1):
        "Remove the prefix from an existing id."
        np = len(self.prefix)
        if tid1[:np] != self.prefix:
            raise ValueError, "Not valid id: %s: It should begin with: %s" % (tid1, self.prefix)
        try:
            id1 = int(tid1[np:])
        except ValueError:
            raise ValueError, "Not valid id: %s: It should begin with: %s" % (tid1, self.prefix)
        if id1 >= self.id:
            raise ValueError, "Not valid id: %s: Greater than current free value: %d" % (tid1, self.id)
        return id1


if __name__ == "__main__":
    print __doc__
    testThanCoorMemory()
