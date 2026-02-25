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

This module defines an object which reads a .mhk file and it creates
ThanCad's elements to represent it in ThanCad.
"""

from p_ggen import path, ThanImportError
from p_gmhk import thanMainTcad, thanGetGround
from p_gimdxf import ThanImportBase
import thandr, thansupport


class ThanImportMhkold(ThanImportBase):
    "A class to import a mhk file."

    def thanImport(self):
        "Imports a mhk file."
        dxf = thansupport.ThanDxfEmu()
        dxf.thanDxfPlots1(self.thanDr)
        try:
            import weakref
            thanMainTcad(path(self.fDxf.name).abspath(), weakref.proxy(dxf), self.thanWarn)
        except Exception, why:
            self.thanEr1s(why)
        aa, xth, hed = thanGetGround()
        if aa == None:
            print "ThanImportMhk: thanImport(): A profile created successfuly but can't get ground coordinates!!!!!"
        else:
            dr = self.thanDr._dr
            pfs = dr.thanObjects["PROFILE"]
            cori = list(dr.thanVar["elevation"])
            cori[:2] = 0.0, 0.0
            pf = thandr.thanobject.ThanProfile(aa, xth, hed, cori)
            pfs[:] = [pf]

    def __del__(self):
        print "ThanImportMhk object dies.."


class ThanImportMhk(thansupport.ThanDxfEmu):
    "A class to import a mhk file."

    def thanImport(self):
        "Imports a mhk file."
        self.thanDxfPlots1()
        try:
            thanMainTcad(path(self.fDxf.name).abspath(), self, self.thanWarn)
        except Exception, why:
            self.thanEr1s(why)
        aa, xth, hed = thanGetGround()
        if aa == None:
            self.thanWarn("A profile imported successfuly but can't get ground coordinates to create profile object!!!!!")
        else:
            dr = self.thanDr._dr
            pfs = dr.thanObjects["PROFILE"]
            cori = list(dr.thanVar["elevation"])
            cori[:2] = 0.0, 0.0
            pf = thandr.thanobject.ThanProfile(aa, xth, hed, cori)
            pfs[:] = [pf]

    def __del__(self):
        print "ThanImportMhk object dies.."
