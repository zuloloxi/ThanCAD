# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2015 Thanasis Stamos, January 18, 2015
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers

Package which creates a bioclimatic city plan.
"""
from __future__ import print_function
#from past.builtins import xrange
from p_ggen.py23 import xrange
import random, copy
import p_gimage
from math import pi
import p_ggen, p_ganneal
from . import hippo, roadut


class HippoAnneal(p_ganneal.SAAnnealable):
    "A grid of roads in region amenable to simulated annealling."

    def __init__(self, hull=None):
        "Initial configuration is a single room."
        p_ganneal.SAAnnealable.__init__(self)
        self.pol = hippo.HippoUrban(hull)
        self.state = p_ggen.Struct()
        self.setPar(50.0, 100.0, 8.0+15.0+8.0, 12.0+25.0+12.0, 2.0+10.0+2.0, 2.5+12.0+2.5, True)
        self.setPar(60.0, 140.0, 25.0+25.0, 30.0+30.0, 2.5+7.0+2.5, 2.5+9.0+2.5, True)
        self.ndim = 1+1


    def setPar(self, boik1, boik2, hoik1, hoik2, bod1, bod2, biochange):
        "Sets the parameters of city blocks."
        self.boik1 = boik1        # Parallel to ideal direction (east-west)
        self.boik2 = boik2        # Parallel to ideal direction (east-west)
        self.hoik1 = hoik1        # Perpendicular to ideal direction (tolerance+house_width1+tolerance+house_with2+tolerance))
        self.hoik2 = hoik2        # Perpendicular to ideal direction (north-south)
        self.bod1 = bod1          # Road width (pavement+width+pavement)
        self.bod2 = bod2
        self.state.e = -1.0             # Invalid value for energy
        self.state.boik = [self.boik1]
        self.state.hoik = [self.hoik1]
        self.state.bod = [self.bod1]
        self.biochange = biochange      # If true, bioclimatic constraints are forced
        if self.biochange: self.state.theta = 90.0   #Theta is angle of ideal direction + 90deg (shows to the north)
        else:              self.state.theta = 0.0    #Theta is angle of ideal direction + 90deg *shows to the north)


    def repairState(self):
        "Initalizes state after cache has been created or read."
        if self.biochange: self.state.theta = 90.0
        else:              self.state.theta = 0.0
        pxmin, pxmax, pymin, pymax = roadut.pminmax(self.pol.hull, self.state.theta)
        nb = int( (pymax-pymin) / (self.bod1+self.boik1) + 0.5)
        nh = int( (pxmax-pxmin) / (self.bod1+self.hoik1) + 0.5)
        print("nb=", nb, "nh=", nh)
        self.state.boik = [self.boik1]*nb
        self.state.hoik = [self.hoik1]*nh
        self.state.bod = [self.bod1]*max(nb, nh)
        for i in xrange(len(self.state.bod)):                          #Thanasis2010_05_21
            self.state.bod[i] = self.r.uniform(self.bod1, self.bod2)   #Thanasis2010_05_21
        self.ndim = 2*(nb + nh)


    def test(self):
        "Tests energy for various angles."
        for theta in p_ggen.xfrange(-90, 90, 10):
            self.state.theta = theta*pi/180.0
            self.pol.create_geometry(self.state)
            print("theta=%8.1f   energy=%15.6f" % (theta, self.pol.energy(self.state)))


    def energyState(self):
        "Computes the energy of the configuration."
        return self.pol.energy(self.state)


    def changeState(self):
        "Changes the configuration a little."
        p = self.r.random()
        if p < 0.20:      # Change theta
            theta = self.state.theta
            if self.biochange:
                if theta < 0.0: theta = self.state.theta = theta+180.0
            while True:
                dth = 5.0
                theta = self.pol.roundt(self.state.theta + self.r.uniform(-dth, dth))
#                print("theta=", theta, "biochange=", self.biochange)
                if self.biochange:
                    if 90.0-22.5 <= theta < 90.0+22.5: break
                else:
                    if -90.0 <= theta < 90.0: break
            if self.biochange:
                if theta > 89.0: theta = theta-180.0
            self.state.theta = theta
        elif p < 0.6:    # Change width of OT
            i = self.r.randint(0, len(self.state.boik)-1)
            self.state.boik[i] = self.pol.roundy(self.r.uniform(self.boik1, self.boik2))
        else:             # Change height of OT
            i = self.r.randint(0, len(self.state.hoik)-1)
            self.state.hoik[i] = self.pol.roundx(self.r.uniform(self.hoik1, self.hoik2))


    def getDimensions(self):
        "Return the dimensionality of current configuration of the annealing object."
        return self.ndim  # Dimensionality of the configuration

    def getState(self):
        "Return an object which fully reflects the state of the annealing object."
        return copy.deepcopy(self.state)

    def setState(self, state):
        "Replace current state of the anneling object with the one in variable state."
        self.state = state


    def initState_old(self):
      "Initialize random changes and calibrate energy."
      self.efact = 1.0
      ndim = self.ndim
      tries = ndim*10
      for i in xrange(tries):        # Randomise a bit
          j = self.changeState()
      e1 = self.energyState()
      de = 0.0
      ndim = self.ndim
      tries = ndim*10
      for i in xrange(tries):
          j = self.changeState()
          e2 = self.energyState()
          de += abs(e2-e1)
          e1 = e2
      de /= tries
      self.efact = 100.0 / de             # Normalise delta energy to 100: efact*de = 100
      p_ggen.prg('Αρχική ενέργεια=%.3f -> %3.f' % (e1, e1*self.efact))
      p_ggen.prg("Αρχική μέση Δε =%.3f -> %3.f" % (de, de*self.efact))
      print("efact=", self.efact)
#      self.plot("First approximation")
      return self.ndim


    def wrstate(self, fw):
        "Save the current state to a file."
        s = self.state
#        e, d8, d10 = self.pol.cache.energy3(s)
        fw.write("# Energy e, length with slope > 8%, length with slope > 10%:\n")
        fw.write("%f  %f  %f\n" % (s.e, s.d8, s.d10))
        fw.write("\n# theta:\n")
        fw.write("%f\n" % s.theta)
        for nam, b in ("boik", s.boik), ("hoik", s.hoik), ("bod", s.bod):
            fw.write("\n# %s:\n" % nam)
            for a in b: fw.write("%f\n" % a)
            fw.write("$\n")


    def rdstate(self, fr):
        "Reads the current state from a file."
        s = self.state
        it = roadut.itercom(fr)
        s.e, s.d8, s.d10 = map(float, next(it).split())
        s.theta = float(next(it))
        for nam, b in ("boik", s.boik), ("hoik", s.hoik), ("bod", s.bod):
            del b[:]
            while True:
                dline = next(it)
                if dline == "$": break
                b.append(float(dline))


    def imageForegroundState(self, im, ct, colot, T, e):
        "Superimpose image foreground to the given the background image."
        ot = list(self.pol.iterOT(self.state))
        imd = p_gimage.Draw(im)
        self.pol.topil(imd, ct, ot=ot, colot=colot)
        if T is not None: imd.text((5,1), text="t=%.2f  e=%.1f" % (T, e), fill=colot)


    def imageBackgroundState(self, imsize):
        "Superimpose background to the given (blank)image and return object for coordinate transformation."
        ot = list(self.pol.iterOT(self.state))
        return self.pol.pilout("", imsize[0], imsize[1], iso=self.pol.contours, roads=())
