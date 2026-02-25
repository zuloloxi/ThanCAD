##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

This module contains tests that should eventually test every aspect of ThanCad
and report errors.
"""
from thanvar import Canc
import thancomfile, thancomvar


def thanTestLine1(proj):
    "Test line creation."
    proj[1].thanTouch()                    #Prevent auto close of this drawing
    projt = thancomfile.thanFileNewDo(proj)
    coms = ("line", "5,6", "50.9,60.8", "6.1,35.0", "c",
            "circle", "31, 30.5, 5.8", "20.3",
            "arc", "31, 30.5, 6.4", "10.3", "45.0", "91.1",
           )
    try:
        thancomvar.thanVarScriptDo(projt, coms)
    except Exception, e:
        proj[2].thanPrter("Test failed: %s" % (e,))
        projt[2].thanPrter("Test failed: %s" % (e,))
        return projt[2].thanGudCommandEnd()

    lay = projt[1].thanLayerTree.thanFindic("0")
    lin = projt[1].thanTagel["E20000"]
    cir = projt[1].thanTagel["E20001"]
    projt[2].thanPrt("line: area=%s length=%s" % (lin.thanArea(), lin.thanLength()))
    projt[2].thanPrt("circle: area=%s length=%s" % (cir.thanArea(), cir.thanLength()))
#    projt[1].thanResetModified()           #Set as unmodified in order to close the temporary drawing
#    r = thancomfile.thanFileCloseDo(projt)
#    assert r != Canc, "file is unmodified, why did it fail to close?"


    return proj[2].thanGudCommandEnd("Test suceeded!")
