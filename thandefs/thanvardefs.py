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

This module defines the ThanCad TextStyle, and others.
"""
import random, copy
import p_gimage


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
#        self.thanRecreate()


    def thanCopy(self):
        "Make a distinct copy of self."
        c = copy.copy(self)
        c.thanFont = self.thanFont.thanCopy()
        return c


def imageOpen(fi, size=None, load=True):
    "Get an image from a file and report errors."
    try:
        im = p_gimage.open(fi)
        if im.size[0] < 2 or im.size[1] < 2: raise ValueError(T["Image is probably corrupted: size is less than 2 pixels"])
        if im.mode == "I;16S": im.mode = "I"
        if load:
            im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised
        if isinstance(im, p_gimage.ThanImageMissing): return im, "Python module PILLOW was not found"
        return im, ""
    except (IOError, ValueError, RuntimeError, p_gimage.DecompressionBombError) as e:
        if size is not None: im = p_gimage.ThanImageMissing(size)
        else:                im = p_gimage.ThanImageMissing()        #Default size
        return im, str(e)


class ThanId:
    """Class to return unique ids (e.g. for Tkinter windows).

    The tag of an element is its id prefixed by a prefix. The id of an element
    is its handle (id and handle refer to the same thing).
    If an element has not a valid handle (for example when it has just been created)
    the new2() method creates a handle and a tag for the element. The tag is the
    handle prefixed by self.prefix.
    If an element already has a handle (for example it was read from a dxf file),
    then its tag is computed as its handle prefixed by self.prefix. The next
    available handle is adjusted to be the element's handle plus one.
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

    def new2random(self, nids=1):
        "Return an id so that id, id+1, id+2, ..., id+nids-1 are unique, as both integer and text."
        i = random.randint(10*self.id, 1000*self.id)
        return i, self.prefix + str(i)

    def addprefix(self, id1):
        "Add the prefix to an existing integer handle and adjust max id."
        if id1 >= self.id: self.id = id1+1
        return self.prefix + str(id1)

    def delprefix(self, tid1):
        "Remove the prefix from an existing id."
        np = len(self.prefix)
        if tid1[:np] != self.prefix:
            raise ValueError("Not valid id: %s: It should begin with: %s" % (tid1, self.prefix))
        try:
            id1 = int(tid1[np:])
        except ValueError:
            raise ValueError("Not valid id: %s: It should begin with: %s" % (tid1, self.prefix))
        if id1 >= self.id:
            raise ValueError("Not valid id: %s: Greater than current free value: %d" % (tid1, self.id))
        return id1


if __name__ == "__main__":
    print(__doc__)
