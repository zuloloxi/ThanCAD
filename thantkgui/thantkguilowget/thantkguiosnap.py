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

This module defines the object snap functionality.
"""

from thanvar import thanLogTk
from thanopt import thancadconf
from thandefs.thanatt import ThanAttCol

_AVOIDTAG = frozenset(("e0", "edrag", "enull"))


class ThanOsnap:
    "Object snap functionality class."

    def __init__(self, proj):
        "Initialize the object."
        self.thanProj = proj
        self.BSEL = thancadconf.thanBSEL
        self.size = thancadconf.thanBOSN      # size of osnap signs
        self.types = thancadconf.thanOsnapModes

        self.active = "ena" in self.types
        self.preempt = False
        self.items = ()
        self.tcol = ThanAttCol(thancadconf.thanColOsn).thanTk
        self.selems = proj[2].thanSelems # Elements which may be snapped to.
        self.selem = None                # Snapable element which is near cursor.
        self.cc1 = None   #This is the first point of a line, when we prompt the user to enter the other point (and dragging the line)


    def thanClear(self):
        "Clear icons, if any."
        dc = self.thanProj[2].thanCanvas
        for item in self.items:
            dc.delete(item)
        self.items = ()


    def thanFind(self):
        "Finds end, mid, center etc near the mouse cursor."
        if self.preempt:
            thanLogTk.error("tklowget: osnapFind: preemptive call. It shouldn't happen.")
            return
        self.preempt = True
        dc = self.thanProj[2].thanCanvas
        tagel = self.thanProj[1].thanTagel
        ct = self.thanProj[2].thanCt
        bpix, hpix = self.BSEL//2, self.BSEL//2
        x1, y1 = dc.thanXcu-bpix, dc.thanYcu-hpix
        x2, y2 = dc.thanXcu+bpix, dc.thanYcu+hpix
        items = dc.find_overlapping(x1, y1, x2, y2)
        otypes = self.types

        ccu = list(self.thanProj[1].thanVar["elevation"])
        ccu[:2] = ct.local2Global(dc.thanXcu, dc.thanYcu)
        if "ele" in otypes:
            selems = self.selems
            for item in items:
                tags = dc.gettags(item)
                                                # Tkinter may automatically add the tag 'current' in any element
                                                # so the next test (which should succeed) does not succeed.
                                                # Thus we have to check for "e0", "edrag" and "enull"
                if len(tags) < 2: continue      # We avoid current (rubber line)
                if tags[0] in _AVOIDTAG: continue    # We avoid current compound element (we shouldn't really)
                e = tagel[tags[0]]
                if e in selems:
                    dc.delete("e0")
                    self.selem = e
                    e1 = e.thanClone()
                    e1.thanUntag()             #Make thanTags and handle invalid
                    e1.thanTags = ("e0",)
                    than = self.thanProj[2].than
                    col1 = than.outline
                    than.outline = self.tcol
                    e1.thanTkDraw(than)
                    dc.itemconfig("e0", width=5)
                    than.outline = col1
                    self.preempt = False
                    return
            self.selem = None
            dc.delete("e0")
            self.preempt = False
            return
        elif "int" in otypes:
            ps = self.__int(dc, tagel, otypes, items, ccu, self.cc1)
        else:
            ps = []
            for item in items:
#               tags = dc.itemcget(item, "tags").split()
                if dc.type(item) == "image": continue # Ignore Tk images; only the bounding rectangle counts
                tags = dc.gettags(item)
                if len(tags) < 2: continue      # We avoid current (rubber line)
                if tags[0] in _AVOIDTAG: continue    # We avoid current compound element (we shouldn't really)
                e = tagel[tags[0]]
                p = e.thanOsnap(self.thanProj, otypes, ccu, None, self.cc1)
                if p is not None:
                    ps.append(p)
                    if len(ps) > 2: break
        for item1 in self.items: dc.delete(item1)
        if len(ps) < 1:
            self.items = ()
            self.preempt = False
            return
        try:
            p = min(ps)
        except:
            print("ps=\n", ps)
            raise
        b, h = ct.global2LocalRel(p[0], p[0])
        if b > 10*self.BSEL:
            self.items = ()
            self.preempt = False
            return
        t = self.type = p[1]
        cc = self.cc = p[2]
        x, y = ct.global2Local(cc[0], cc[1])
        self.x = x
        self.y = y
        b = h = self.size//2
        tcol = self.tcol
        if t == "end":
            self.items = \
            ( dc.create_rectangle(x-b, y-h, x+b, y+h, width=3, outline=tcol, fill=""),
            )
        elif t == "mid":
            self.items = \
            ( dc.create_polygon(x-b, y-b, x+b, y-b, x, y+b, width=3, outline=tcol, fill=""),
            )
        elif t == "cen":
            self.items = \
            ( dc.create_oval(x-b, y-b, x+b, y+b, width=3, outline=tcol, fill=""),
            )
        elif t == "nod":
            self.items = \
            ( dc.create_oval(x-b, y-b, x+b, y+b, width=3, outline=tcol, fill=""),
              dc.create_line(x-b, y-b, x+b, y+b, width=2, fill=tcol),
              dc.create_line(x-b, y+b, x+b, y-b, width=2, fill=tcol),
            )
        elif t == "qua":
            self.items = \
            ( dc.create_polygon(x-b,y, x,y+b, x+b,y, x,y-b, width=2, outline=tcol, fill=""),
            )
        elif t == "int":
            self.items = \
            ( dc.create_line(x-b, y-b, x+b, y+b, width=2, fill=tcol),
              dc.create_line(x-b, y+b, x+b, y-b, width=2, fill=tcol),
            )
        elif t == "tan":
            bb = 0.8*b
            self.items = \
            ( dc.create_oval(x-bb, y-bb, x+bb, y+bb, width=3, outline=tcol, fill=""),
              dc.create_line(x-b, y-b, x+b, y-b, width=2, fill=tcol),
            )
        elif t == "nea":
            self.items = \
            ( dc.create_polygon(x-b, y-b, x+b, y+b, x-b, y+b, x+b, y-b, width=2, outline=tcol, fill=""),
            )
        elif t == "per":
            self.items = \
            ( dc.create_line(x-b, y-b, x-b, y+b, x+b, y+b, width=3, fill=tcol),
              dc.create_line(x-b, y, x, y, x, y+b, width=2, fill=tcol),
            )
        self.preempt = False


    def __int(self, dc, tagel, otypes, items, ccu, cc1):
        "Finds int near the mouse cursor."
        dc = self.thanProj[2].thanCanvas
        ps = []
        it = iter(items)
        for item in it:                     # Search for first element of intersection
            if dc.type(item) == "image": continue # Ignore Tk images; only the bounding rectangle counts
            tags = dc.gettags(item)
            if len(tags) < 2:   continue    # We avoid current (rubber line)
            if tags[0] in _AVOIDTAG: continue    # We avoid current compound element (we shouldn't really)
            e = tagel[tags[0]]
            p = e.thanOsnap(self.thanProj, otypes, ccu, None, self.cc1)
            if p is not None: ps.append(p)
            break
        else: return ps
        etried = False
        for item in it:                     # Search for second element of intersection
            if dc.type(item) == "image": continue # Ignore Tk images; only the bounding rectangle counts
            tags = dc.gettags(item)
            if len(tags) < 2:   continue    # We avoid current (rubber line)
            if tags[0] in _AVOIDTAG: continue    # We avoid current compound element (we shouldn't really)
            etried = True
            e2 = tagel[tags[0]]
            p = e.thanOsnap(self.thanProj, otypes, ccu, e2, cc1)
            if p is not None: ps.append(p); break
            e = e2
        if etried: return ps
        p = e.thanOsnap(self.thanProj, otypes, ccu, None, cc1)

        if p is not None: ps.append(p)
        return ps


    def thanCleanup(self):
        "Do cleanup after error/command-line action."
        dc = self.thanProj[2].thanCanvas
        for item1 in self.items:
            dc.delete(item1)
        self.items = ()


class ThanOrtho:
    "Ortho mode functionality class."

    def __init__(self):
        "Initialize the object."
        self.thanIdirs = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
        self.on = False      # If this is false then ortho is off
        self.active = False  # This is false if ortho has no meaning for current action
        self.xa = None       # The reference point for ortho mode..
        self.ya = None       # ..in canvas coordinates


    def enable(self, xa, ya):
        "Enable ortho mode, if it is on."
        self.xa = xa
        self.ya = ya
        self.active = True


    def disable(self):
        "Disable ortho mode; ortho has no meaning for current action."
        self.active = False
        self.xa = self.ya = None


    def toggle(self):
        "Toggle on/off and return the current state."
        self.on = not self.on
        return self.on


    def orthoxy(self, xb, yb):
        "Force the coordinates of the mouse parallel to a direction; usually ortho mode."
        if not self.active or not self.on: return xb, yb
        dx = xb - self.xa
        dy = yb - self.ya
        dismax = 0.0
        for idir1 in self.thanIdirs:
            disproj = dx*idir1[0] - dy*idir1[1]   # The negative sign in y is due to local coordinate systems
            if disproj > dismax:
                dismax = disproj
                idirmax = idir1
        return self.xa + dismax*idirmax[0], self.ya - dismax*idirmax[1]
