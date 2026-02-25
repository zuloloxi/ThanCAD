#!/usr/bin/python
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
import p_ggen
from p_ganneal import SimulatedAnnealing
from .room import RoomConfiguration
from .constrain import RoomConstrain, RoomConfigurationConstrain


def pyMain():
    "Main routine of standalone program."
    v = p_ggen.Struct()
    v.entWidth = 9.0
    v.entHeight = 7.0
    v.entMinRooms = 5
    v.entMaxRooms = 6

    v.entMintolWidth = 2.5
    v.entMinWidth = 3.0
    v.entMaxWidth = 6.0
    v.entMaxtolWidth = 7.0
    v.entMintolHeight = 3.0
    v.entMinHeight = 3.0
    v.entMaxHeight = 7.0
    v.entMaxtolHeight = 8.0

    v.entPenaltmore = 1.0
    v.entPenalt1 = 10.0
    v.entPenalty = 1.0

    rcon = RoomConstrain(v.entMintolWidth , v.entMinWidth, v.entMaxWidth, v.entMaxtolWidth,
                         v.entMintolHeight, v.entMinHeight, v.entMaxHeight, v.entMaxtolHeight,
                         v.entPenalt1, v.entPenalty)
    ccon = RoomConfigurationConstrain(v.entMinRooms, v.entMaxRooms, v.entPenaltmore)
    rc = RoomConfiguration(0.0, 0.0, v.entWidth, v.entHeight, ccon, rcon)
    sa = SimulatedAnnealing()
    sa.anneal(rc)
    print("final energy=", rc.energyState())
    rc.plot("Final Diaryqmish")


def thancadMain(proj, v, xor, yor):
    "Main routine of embedded program to ThanCad."
    rcon = RoomConstrain(v.entMintolWidth,  v.entMinWidth,  v.entMaxWidth,  v.entMaxtolWidth,
                         v.entMintolHeight, v.entMinHeight, v.entMaxHeight, v.entMaxtolHeight,
                         v.entPenalt1, v.entPenalty)
    ccon = RoomConfigurationConstrain(v.entMinRooms, v.entMaxRooms, v.entPenaltmore)
    rc = RoomConfiguration(xor, yor, v.entWidth, v.entHeight, ccon, rcon, proj[2].thanPrt)
    pref = proj[0].parent / proj[0].namebase + "_anim"
    sa = SimulatedAnnealing(prt=proj[2].thanPrt, animon=False, animpref=pref)
    sa.anneal(rc)
    proj[2].thanPrtbo("final energy=%s" % (rc.energyState(),))
#   rc.plot("Final Diaryqmish")
    rc.plot2(proj)


if __name__ == "__main__": pyMain()
