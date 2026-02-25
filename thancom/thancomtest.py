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

This module contains tests that should eventually test every aspect of ThanCad
and report errors.
"""
from math import fabs
from thanvar import Canc
import thandr
from . import thancomfile, thancomvar


def thanTestLine1oldold(proj):
    "Test line creation."
    proj[1].thanTouch()                    #Prevent auto close of this drawing
    projt = thancomfile.thanFileNewDo(proj)
    coms = ("line", "5,6", "50.9,60.8", "6.1,35.0", "c",
            "circle", "31, 30.5, 5.8", "20.3",
            "arc", "31, 30.5, 6.4", "10.3", "45.0", "91.1",
           )
    try:
        thancomvar.thanVarScriptDo(projt, coms)
    except Exception as e:
        proj[2].thanPrter("Test failed: %s" % (e,))
        projt[2].thanPrter("Test failed: %s" % (e,))
        return projt[2].thanGudCommandEnd()

    lay = projt[1].thanLayerTree.thanFindic("0")
    lin = projt[1].thanTagel["E20000"]
    cir = projt[1].thanTagel["E20001"]
    projt[2].thanPrt("line: area=%s length=%s" % (lin.thanArea(), lin.thanLength()))
    projt[2].thanPrt("circle: area=%s length=%s" % (cir.thanArea(), cir.thanLength()))
    projt[2].thanGudCommandEnd()
#    projt[1].thanResetModified()           #Set as unmodified in order to close the temporary drawing
#    r = thancomfile.thanFileCloseDo(projt)
#    assert r != Canc, "file is unmodified, why did it fail to close?"


    return proj[2].thanGudCommandEnd("Test suceeded!")



def thanTestLine1old(proj):
    "Test line creation."
    proj[1].thanTouch()                    #Prevent auto close of this drawing
    projt = thancomfile.thanFileNewDo(proj)
    coms = ("line", "5,6", "50.9,60.8", "6.1,35.0", "c",
            "circle", "31, 30.5, 5.8", "20.3",
            "arc", "31, 30.5, 6.4", "10.3", "45.0", "91.1",
           )
    try:
        thancomvar.thanVarScriptDo(projt, coms)
        lay = projt[1].thanLayerTree.thanFindic("0")
        lin = projt[1].thanTagel["E20000"]
        cir = projt[1].thanTagel["E20001"]
        arc = projt[1].thanTagel["E20002"]
        projt[2].thanPrt("line: area=%s length=%s" % (lin.thanArea(), lin.thanLength()))
        projt[2].thanPrt("circle: area=%s length=%s" % (cir.thanArea(), cir.thanLength()))
        projt[2].thanGudCommandEnd()
    except Exception as e:
        projt[2].thanGudCommandEnd("Test failed: %s" % (e,))
        return proj[2].thanGudCommandEnd("Test failed: %s" % (e,))
#    projt[1].thanResetModified()           #Set as unmodified in order to close the temporary drawing
#    r = thancomfile.thanFileCloseDo(projt)
#    assert r != Canc, "file is unmodified, why did it fail to close?"


    return proj[2].thanGudCommandEnd("Test suceeded!")


def thanTestLine1(proj):
    "Test line creation."
    proj[1].thanTouch()                    #Prevent auto close of this drawing
    projt = thancomfile.thanFileNewDo(proj)
    coms = ("line", "5,6", "50.9,60.8", "6.1,35.0", "c",
            "line", "6,7", "50.0,0.0", "60.1,30.2", "u", "0,0", ""
           )
    try:
        thancomvar.thanVarScriptDo(projt, coms)
        lay = projt[1].thanLayerTree.thanFindic("0")
        lins = []
        lins.append((projt[1].thanTagel["E20000"], 635.41, 152.202038))
        lins.append((projt[1].thanTagel["E20001"], 175.0,   94.553339))
        eps = 1.0e-6
#        projt[2].thanPrt("line 1: area=%f length=%f" % (lin1.thanArea(), lin1.thanLength()))
#        projt[2].thanPrt("line 2: area=%f length=%f" % (lin2.thanArea(), lin2.thanLength()))
        for lin, area, alen in lins:
            if fabs(area - lin.thanArea()) > eps:
                raise ValueError("Line area should be %f but is %f" % (area, lin.thanArea()))
            if fabs(alen - lin.thanLength()) > eps:
                raise ValueError("Line length should be %f but is %f" % (alen, lin.thanLength()))
        projt[2].thanGudCommandEnd()
    except Exception as e:
        projt[2].thanGudCommandEnd("Test failed: %s" % (e,))
        return proj[2].thanGudCommandEnd("Test failed: %s" % (e,))

    projt[1].thanResetModified()           #Set as unmodified in order to close the temporary drawing
    r = thancomfile.thanFileCloseDo(projt)
    assert r != Canc, "file is unmodified, why did it fail to close?"
    return proj[2].thanGudCommandEnd("Test succeeded!")


def thanCircle01(proj):
    "Test the creation and mnipulation of a circle."
    c = thandr.ThanCircle()
    cc = list(proj[1].thanVar["elevation"])
    cc[:3] = 100.0, 200.0, 10.0
    c.thanSet(cc, 0.0)
    assert not c.thanIsNormal()
    c.thanSet(cc, 50.0, spin=1)
    assert c.thanIsNormal()
    assert c.cc == cc
    assert c.r == 50.0
    assert c.spin == 1
    c.thanReverse()
    assert c.spin == -1
    c.thanMove([1.0, 1.0, 1.0])
    assert c.cc[0] == 101.0
    assert c.cc[1] == 51.0
    assert c.cc[1] == 11.0
    c.thanMove([-1.0, -1.0, -1.0])
    assert c.cc == cc

