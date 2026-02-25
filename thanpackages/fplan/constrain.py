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
import copy


class Constrain(object):

    def clone(self, **kw):
        "Make a deep copy of self."
        new = copy.deepcopy(self)
        new.config(**kw)
        return new


    def config(self, **kw):
        "Set new penalties constrains etc."
        for key, val in kw.ieritems():
            getattr(self, key)      # Raise error if key is not known attribute
            setattr(self, key, val)


class RoomConstrain:
    "All constrains and penalties for one room."

    def __init__(self, bmin1=3.0, bmin=3.0, bmax=4.0, bmax1=9.0,
                       hmin1=3.0, hmin=3.0, hmax=5.0, hmax1=9.0,
                       penalt1=10.0, penalt=1.0):
        "Assume that bmin <= hmin."
        self.bcon = RoomConstrain1(bmin1, bmin, bmax, bmax1, penalt1, penalt)
        self.hcon = RoomConstrain1(hmin1, hmin, hmax, hmax1, penalt1, penalt)

    def penalty(self, b, h):
        "Computes the penalty due to both dimensions."
        if b > h: b, h = h, b
        return self.bcon.penalty(b)+self.hcon.penalty(h)


class RoomConstrain1(Constrain):
    "All constrains and penalties for one room."

    def __init__(self, bmin1=2.5, bmin=3.0, bmax=4.0, bmax1=5.0,
                       penalt1=10.0, penalt=1.0):
        self.bmin1   = bmin1
        self.bmin    = bmin
        self.bmax    = bmax
        self.bmax1   = bmax1
        self.penalt1 = penalt1
        self.penalt  = penalt


    def penalty(self, b):
        "Computes the penalty due to small or big width."
        assert b > 0.0, "b<=0"
        if b < self.bmin1:
            e = (self.bmin-self.bmin1)*self.penalt + (self.bmin1-b)*self.penalt1
        elif b < self.bmin:
            e = (self.bmin-b)*self.penalt
        elif b <= self.bmax:
            e = 0.0
        elif b < self.bmax1:
            e = (self.bmax1-b)*self.penalt
        else:
            e = (self.bmax1-self.bmax)*self.penalt + (b-self.bmax1)*self.penalt1
        return e


class RoomConfigurationConstrain(Constrain):
    "All constrains and penalties for a floor plan."

    def __init__(self, minrooms=5, maxrooms=6, penaltmore=20.0):
        self.minrooms    = minrooms
        self.maxrooms    = maxrooms
        self.penaltmore = penaltmore


    def penalty(self, n):
        "Computes the penalt due to many rooms."
        if n < self.minrooms:
            return (self.minrooms-n)*self.penaltmore*n
        elif n > self.maxrooms:
            return (n-self.maxrooms)*self.penaltmore*n
        else:
            return 0.0
