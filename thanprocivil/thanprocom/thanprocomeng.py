# -*- coding: iso-8859-7 -*-

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

Package which processes commands entered by the user.
This module processes commands related to engineering.
"""

from math import hypot
import p_gmhk, p_ggen
import thantkdia, thandr, thanprocivil
from thanvar import Canc
from thantrans import T, Tcivil


def thanEngLineprofile(proj):
    "Creates a (3D) line profile into a new drawing."
    from thancom import thancomsel, thancomfile
    from thancom.thancommod import thanModCanc, thanModEnd
    proj[2].thanPrt(Tcivil["Select 3d lines to make profiles:"], "info1")
    res = thancomsel.thanSelectGen(proj, standalone=False, filter=lambda e: isinstance(e, thandr.ThanLine))
    if res == Canc: return thanModCanc(proj)           # Profile was cancelled

    fn, fw = thancomfile.thanTxtopen(proj, Tcivil["Save profile to file"], suf=".mhk", mode="w", initialfile=proj[0].namebase)
    if fn == Canc: return thanModCanc(proj)           # Profile was cancelled

    p_gmhk.wrMhk1ti(fw)
    for i, e in enumerate(proj[2].thanSelall):
        cb = e.cp[0]
        d = 0.0
        j = 1
        ground = [("S"+str(j), d, cb[2])]
        for ca, cb in p_ggen.iterby2(e.cp):
            d += hypot(cb[1]-ca[1], cb[0]-ca[0])
            j += 1
            ground.append(("S"+str(j), d, cb[2]))
        p_gmhk.wrMhk1oned(fw, "ΜΗΚΟΤΟΜΗ %d" % (i+1,), ground)
    fw.close()
    proj[2].thanPrt(T["%s was created successfully."] % (fn,), "info")
    thancomfile.thanFileOpenPaths(proj, [fn])
#    return thanModEnd(proj, T["%d profiles were created."]%len(proj[2].thanSelall), "info")
    return thanModEnd(proj)


def thanEngGradeline(proj):
    "Compute the gradeline of a profile."
    pfs = proj[1].thanObjects["PROFILE"]
    if len(pfs) == 0: return proj[2].thanGudCommandCan(Tcivil["Can't compute grade line: No profile has been defined!"])
    ok, ter = pfs[0].execute(proj)
    if ok: return proj[2].thanGudCommandEnd()
    return proj[2].thanGudCommandCan(ter)
