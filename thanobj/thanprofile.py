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

This module defines an object which creates and stores a highway profile.
"""
import p_ggen, p_grun
from thantrans import T, Tarch
try:                import p_gmhk
except ImportError: pass
from .thanobject import ThanObject


class ThanProfile(ThanObject):
    thanObjectName = "PROFILE"    # Name of the objects's class
    thanOjectInfo = "Profile of a roads, conduits etc.."
    thanVersions = ((1,0),)

    def __init__(self, aa=None, xth=None, hed=None, cori=None, xthmin=None, hmin=None, dscale=10.0):
        "Set initial values to the profile plan and paraphernalia (if they are defined)."
        if aa is None: return
        self.thanSet(aa, xth, hed, cori, xthmin, hmin, dscale)


    def thanSet(self, aa, xth, hed, cori=None, xthmin=None, hmin=None, dscale=10.0):
        "Set initial values to the profile plan and paraphernalia."
        assert len(aa) > 1
        self.aa = tuple(aa)
        self.xth = tuple(xth)
        self.hed = tuple(hed)
        if cori is not None: self.cori = tuple(cori)
        else:                self.cori = (0.0, 0.0, 0.0)
        if xthmin is not None: self.xthmin = xthmin
        else:                self.xthmin = self.xth[0]
        if hmin is not None: self.hmin = hmin
        else:            self.hmin = min(self.hed)
        self.dscale = dscale                        #Differential scale: scale for h is 10 times bigger than scale for xth


    def thanXy(self, xth1, h1):
        "Find the position of station xth1 with height h1 on the drawing."
        cp = list(self.cori)
        cp[0] += (xth1-self.xthmin)/self.dscale
        cp[1] += (h1-self.hmin)
        return cp


    def execute(self, proj):
        "Write the .ger and .mhk files which are needed for the program mhker."
        try:
            fw = p_ggen.uniqfile(proj[0].parent/proj[0].namebase, suf=".ger", stat="w", n=3)
            if fw is None: raise IOError("Can not create unique name with prefix %s" % (proj[0],))
            fn = p_ggen.path(fw.name)
            fns = [fn.parent / fn.namebase + suf for suf in ".ger .mhk .nmh".split()]
            fns.append(fn.parent / "mediate.tmp")

            nSpa = 15
            aklisOr =  ( 0.400,          0.500,          4.000,          5.000)
            aklisTim = (10.000,         10.000,        -10.000,         10.000)
            rErola = 1000.000
            fw.write("%10d\n" % (nSpa,))
            fw.write("%15.3f%15.3f%15.3f%15.3f\n" % aklisOr)
            fw.write("%15.3f%15.3f%15.3f%15.3f\n" % aklisTim)
            fw.write("%15.3f\n" % (rErola,))
            fw.close()
            fn.remove()

            fw = open(fns[1], "w")
            p_gmhk.wrMhk1ti(fw, ngram=2)
            p_gmhk.wrMhk1oned(fw, "PROFILE 1", list(zip(self.aa, self.xth, self.hed)))  #works for python2,3
            fw.close()

            fw = open(fns[-1], "w")
            fw.write("1\n%s\n" % (fn.namebase,))
            fw.close()
        except IOError as e:
            for fn in fns:
                try: fn.remove()
                except IOError: pass
            return False, str(e)

        ok = p_grun.runExecWin("c_mhker", pdir=proj[0].parent, pexpectline=True, master=proj[2],
             title=u"ThanCad - %s: Grade line computation" % (fn.namebase),)
        if not ok: return False, "Errors recorded in output window."
        if fns[3].exists():
            try: fns[3].remove()
            except IOError: pass
            return False, "Errors recorded in output window."
        for fn in fns[:2]:
            try: fn.remove()
            except IOError: pass
        try: fns[2].rename(fns[1])
        except IOError as e: return False, str(e)
        import thancom
        thancom.thancomfile.thanFileOpenPaths(proj, [fns[1]])
        return True, ""


    def thanList(self, than):
        "Shows information about the profile object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s: %s\n" % (Tarch["Number of stations"], len(self.xth)))
        than.write("%s: %s\n" % (T["Length"], than.strdis(self.xth[-1]-self.xth[0])))


if __name__ == "__main__":
    print(__doc__)
