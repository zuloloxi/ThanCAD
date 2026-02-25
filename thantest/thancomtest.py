##############################################################################
# ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2013 Thanasis Stamos, March 25, 2013
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
ThanCad 0.2.3 "Hannover": 2dimensional CAD with raster support for engineers

This package contains tests that should eventually test every aspect of ThanCad
and report errors.
"""
from thanvar import Canc
from thancom import thancomfile, thancomvar


def thanTestLine1(proj):
    "Test line creation."
    proj[1].thanTouch()                    #Prevent auto close of this drawing
    projt = thancomfile.thanFileNewDo(proj)
    coms = "line", "50,60", "100.9,110.8", "75.1,85.0", "c"
    try:
        thancomvar.thanVarScriptDo(projt, coms)
    except Exception, e:
        proj[2].thanPrter("Test failed: %s" % (e,))
        projt[2].thanPrter("Test failed: %s" % (e,))
        return projt[2].thanGudCommandEnd()
    projt[1].thanResetModified()           #Set as unmodified in order to close the temporary drawing
    r = thancomfile.thanFileCloseDo(projt)
    assert r != Canc, "file is unmodified, why did it fail to close?"
    return proj[2].thanGudCommandEnd()
