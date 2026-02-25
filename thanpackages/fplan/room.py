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

Package which creates a floor plan design automatically.
"""
import random, copy
from functools import partial
from p_ggen import prg
from p_ganneal import SAAnnealable
import p_gimage

class Room:
    "A class which represents a room, posible divided."

    def __init__(self, xymm, rcon):
        "The xymm are the coordinates of lower left followed by the coordinates of upper right."
        self.xymm = list(xymm)
        self.rcon = rcon
        self.isplit = None         # Room is not (yet) split
        self.csplit = None
        self.roomll = self.roomur = None # Children

    def split(self, isplit, csplit):
        "Split the room to 2 children."
        assert self.isleaf(), "room is already split!"
        assert self.xymm[isplit] < csplit < self.xymm[isplit+2], "Split line outside of the room"
        self.isplit = isplit
        self.csplit = csplit
        xymm = list(self.xymm)
        xymm[isplit+2] = csplit
        self.roomll = Room(xymm, self.rcon)
        xymm = list(self.xymm)
        xymm[isplit] = csplit
        self.roomur = Room(xymm, self.rcon)


    def merge(self):
        "Merges all the children/grandchildren of the room."
        self.isplit = self.csplit = self.roomll = self.roomur = None

    def isleaf(self):
        "Checks if the room is a leaf node (it has not been split)."
        return self.isplit is None

    def list(self, all, mall, sall, chall):
        "Returns a list of self and children."
        all.append(self)
        if self.isleaf():
            sall.append(self)                #Splitable
        else:
            if self.roomll.isplit is None and \
                self.roomur.isplit is None: chall.append(self) #Changable: parent, but not a grandparent
            mall.append(self)                #Mergeable
            self.roomll.list(all, mall, sall, chall)
            self.roomur.list(all, mall, sall, chall)

    def energyold(self, e):
        "Computed the energy of the ...."
        e += self.penalty(self.xymm[2]-self.xymm[0])
        e += self.penalty(self.xymm[3]-self.xymm[1])
        if self.isleaf(): return e
        e = self.roomll.energy(e)
        e = self.roomur.energy(e)
        return e

    def energy(self):
        "Compute the energy of the room"
        e  = self.rcon.penalty(self.xymm[2]-self.xymm[0], self.xymm[3]-self.xymm[1])
        return e


    col = "red yellow green blue cyan magenta white".split()
    def plot(self, ch, icol):
        "Plots the room into a ThanChart."
        xa, ya = self.xymm[:2]
        xb, yb = self.xymm[2:]
        xx = (xa, xb, xb, xa, xa)
        yy = (ya, ya, yb, yb, ya)
        ch.curveAdd(xx, yy, color=self.col[icol%len(self.col)])
        if not self.isleaf(): self.plotSplit(ch, icol+1)


    def plotSplit(self, ch, icol):
        "Plots the split line of the room."
        if self.isplit == 0:
            xx = (self.csplit,  self.csplit)
            yy = (self.xymm[1], self.xymm[3])
        else:
            xx = (self.xymm[0], self.xymm[2])
            yy = (self.csplit,  self.csplit)
        ch.curveAdd(xx, yy, color=self.col[icol%len(self.col)])
        if not self.roomll.isleaf(): self.roomll.plotSplit(ch, icol+1); icol += 1
        if not self.roomur.isleaf(): self.roomur.plotSplit(ch, icol+1)

    def plot3(self, imd, ct, icol):
        "Plots the room into a ThanChart."
        if icol == -1:
            if not self.isleaf(): self.plotSplit3(imd, ct, icol)
        else:
            g2li = ct.global2Locali
            xa, ya = g2li(*self.xymm[:2])
            xb, yb = g2li(*self.xymm[2:])
            xx = (xa, xb, xb, xa, xa)
            yy = (ya, ya, yb, yb, ya)
            imd.line(list(zip(xx, yy)), width=4, fill=self.col[icol%len(self.col)])  #works for python2,3
            if not self.isleaf(): self.plotSplit3(imd, ct, icol+1)


    def plotSplit3(self, imd, ct, icol):
        "Plots the split line of the room."
        g2li = ct.global2Locali
        if self.isplit == 0:
            ca = g2li(self.csplit, self.xymm[1])
            cb = g2li(self.csplit, self.xymm[3])
        else:
            ca = g2li(self.xymm[0], self.csplit)
            cb = g2li(self.xymm[2], self.csplit)
        if icol == -1:
            imd.line([ca, cb], fill="lightgreen")
            if not self.roomll.isleaf(): self.roomll.plotSplit3(imd, ct, icol)
            if not self.roomur.isleaf(): self.roomur.plotSplit3(imd, ct, icol)
        else:
            imd.line([ca, cb], width=4, fill=self.col[icol%len(self.col)])
            if not self.roomll.isleaf(): self.roomll.plotSplit3(imd, ct, icol+1); icol += 1
            if not self.roomur.isleaf(): self.roomur.plotSplit3(imd, ct, icol+1)


    def plot2(self, proj, icol):
        "Plots the room into an active ThanCad drawing."
        from thansupport import thanToplayerCurrent
        from thandr import ThanLine
        col1 = self.col[icol%len(self.col)]
        thanToplayerCurrent(proj, "floorplan/%d%s"%(icol, col1), moncolor=col1)
        cn = partial(cnp, prototype=proj[1].thanVar["elevation"])
        xa, ya = self.xymm[0], self.xymm[1]
        xb, yb = self.xymm[2], self.xymm[3]
        cc = [cn(xa, ya), cn(xb, ya), cn(xb, yb), cn(xa, yb), cn(xa, ya)]
        e = ThanLine()
        e.thanSet(cc)
        proj[1].thanElementAdd(e)
        e.thanTkDraw(proj[2].than)
        if not self.isleaf(): self.plotSplit2(proj, icol+1)


    def plotSplit2(self, proj, icol):
        "Plots the split line of the room into an active ThanCad drawing."
        from thansupport import thanToplayerCurrent
        from thandr import ThanLine
        col1 = self.col[icol%len(self.col)]
        thanToplayerCurrent(proj, "floorplan/%d%s"%(icol, col1), moncolor=col1)
        cn = partial(cnp, prototype=proj[1].thanVar["elevation"])
        if self.isplit == 0:
            cc = [cn(self.csplit, self.xymm[1]), cn(self.csplit, self.xymm[3])]
        else:
            cc = [cn(self.xymm[0], self.csplit),  cn(self.xymm[2], self.csplit)]
        e = ThanLine()
        e.thanSet(cc)
        proj[1].thanElementAdd(e)
        e.thanTkDraw(proj[2].than)
        if not self.roomll.isleaf(): self.roomll.plotSplit2(proj, icol+1); icol += 1
        if not self.roomur.isleaf(): self.roomur.plotSplit2(proj, icol+1)


class RoomConfiguration(SAAnnealable):
    "A room hierarchy amenable to simulated annealling."

    def __init__(self, xor, yor, b, h, ccon, rcon, prt=prg):
        "Initial configuration is a single room."
        SAAnnealable.__init__(self)
        self.prt = prt
        self.ccon = ccon
        self.rcon = rcon
        self.root = Room((xor,yor,xor+b,yor+h), self.rcon)
        self.per = 0.2                      # Do not split nearer to 20% from sides
        self.typeNodes()


    def energyState(self):
        "Computes the energy of the configuration."
        e = 0.0
        for room in self.sable:
            e += room.energy()
        e += self.ccon.penalty(len(self.sable))
        return e / len(self.sable)


    def changeState(self, fill=False):
        "Changes the configuration a little."
        p = self.r.random()
        if p < 0.4 and self.chable:     # In case that only the root room exists
#            print "change"
            room = self.r.choice(self.chable)
            i = room.isplit
            dc = (room.xymm[i+2] - room.xymm[i])*self.per
            room.csplit = self.r.uniform(room.xymm[i]+dc, room.xymm[i+2]-dc)
            room.roomll.xymm[i+2] = room.csplit
            room.roomur.xymm[i]   = room.csplit
        elif self.splitable(p, fill): #Note that in normal mode this may lead to more than maxrooms
#            print "split"
            room = self.r.choice(self.sable)
            dx = room.xymm[2]-room.xymm[0]
            dy = room.xymm[3]-room.xymm[1]
            px = 1.0/(1.0+dy/dx)
            if self.r.random() < px: i = 0
            else:                    i = 1
            dc = (room.xymm[i+2] - room.xymm[i])*self.per
            c = self.r.uniform(room.xymm[i]+dc, room.xymm[i+2]-dc)
            room.split(i, c)
            self.typeNodes()
        else:                      # Note that here this may result to less than minrooms
#            print "merge"
            room = self.r.choice(self.chable)
            room.merge()
            self.typeNodes()


    def splitable(self, p, fill):
        """Decide if the change can be a split.

        In fill mode we fluctuate between minrooms and maxrooms.
        Otherwise, in normal mode, the rooms may become more than maxrooms,
        since this makes the changes more agile.
        """
        if not self.chable: return True    # Only 1 room exists: split is the only option
        if fill:            #Fill mode
            n = len(self.sable)
            if n <  self.ccon.maxrooms: return True  # Add until we reach minrooms
            if n >= self.ccon.maxrooms: return False # We have already reached maxrooms: do not add
            return p < 0.7                           # Between min and max: decide randomly
        return p < 0.7      # Normal mode: decide randomly: may lead to more than max rooms


    def saveCurState(self):
        "Save current configuration for future restorePrevState()."
        self.rootOld = copy.deepcopy(self.root)

    def restorePrevState(self):
        "Restores previously saved state."
        self.root = self.rootOld
        self.typeNodes()

    def saveMinState(self):
        "Save current configuration as the best so far."
        self.rootMin = copy.deepcopy(self.root)

    def restoreMinState(self):
        "Restores previously saved best configuration."
        self.root = self.rootMin
        self.typeNodes()

    def getDimensions(self):
        "Return the dimensionality of current configuration of the annealing object."
        return len(self.all)       # Dimensionality of the configuration

    def initState_old(self, spSch):
      "Initialize random changes and calibrate energy."
      self.efact = 1.0
      ndim = self.ccon.minrooms             # Assume (minrooms) rooms in house
      tries = ndim*10
      for i in range(tries):        # Randomise a bit
          j = self.changeState(fill=True)    # (almost) ensure that number of rooms is about minrooms
      e1 = self.energyState()
      n1 = len(self.sable)
      de = 0.0
      ndim = len(self.all)
      tries = ndim*10
      for i in range(tries):
          j = self.changeState()
          e2 = self.energyState()
          de += abs(e2-e1)
          e1 = e2
      de /= tries
      self.efact = 100.0 / de             # Normalise delta energy to 100: efact*de = 100
      self.prt('Αρχική ενέργεια=%.3f' % e1)
      self.prt("Αρχική μέση Δε =%.3f" % de)
      print("Initial    number of rooms:", n1)
      print("Randomized number of rooms:", len(self.sable))
      print("efact=", self.efact, "Initial temperature=", 100.0/self.efact)
#      self.plot("First approximation")
      return len(self.all)

    def typeNodes(self):
        "Finds lists of mergeable, splittable, splittable, changeable rooms and a list of all."
        self.all = []             #All :)
        self.mable = []           #Mergeable
        self.sable = []           #Splittable
        self.chable = []          #Changeble
        self.root.list(self.all, self.mable, self.sable, self.chable)


    def imageForegroundState(self, im, ct, colot, T, e):
        "Superimpose image foreground to the given the background image."
        imd = p_gimage.Draw(im)
        if colot == "green":
            self.root.plot3(imd, ct, -1)
        else:
            self.root.plot3(imd, ct, 0)
            if T is not None: imd.text((5,1), text="t=%.2f  e=%.1f" % (T, e), fill="yellow")

    def imageBackgroundState(self, imsize):
        "Create and return background image and object for coordinate transformation."
        from p_gmath import ThanRectCoorTransf
        width, height = imsize
        ct = ThanRectCoorTransf(self.root.xymm, (5, height-5, width-5, 5))
        im = p_gimage.new("RGB", imsize, (0, 0, 0))
        return im, ct


    def plot(self, tit):
        from p_gchart import ThanChart, vis
        ch = ThanChart(title=tit)
        self.root.plot(ch, 0)
        vis(ch)

    def plot2(self, proj):
        self.root.plot2(proj, 0)


def cnp(xa, ya, prototype):
    "Return the coordinates as list like prototype."
    ca = list(prototype)
    ca[:2] = xa, ya
    return ca


def test():
    "Test-builds a random room hierarchy."
    from p_gchart import ThanChart, vis
    r = random.Random()
    root = Room((0,0,20,10), None)
    global col
    col = "red yellow green blue cyan magenta white".split()
    per = 0.2
    for itry in range(5):
        all = []; mall = []; sall = []; chall = []
        root.list(all, mall, sall, chall)
        room = r.choice(sall)
        dx = room.xymm[2]-room.xymm[0]
        dy = room.xymm[3]-room.xymm[1]
        px = 1.0/(1.0+dy/dx)
        if r.random() < px: i = 0
        else:               i = 1
#        i = r.randint(0, 1)
        dc = (room.xymm[i+2] - room.xymm[i])*per
        c = r.uniform(room.xymm[i]+dc, room.xymm[i+2]-dc)
        room.split(i, c)
    print("energy=", root.energy())
    ch = ThanChart()
    root.plot(ch, 0)
    vis(ch)

if __name__ == "__main__": test()
