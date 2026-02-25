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

This module displays a dialog for the user to enter the necessary values
for coefficients used in rectification.
"""

import Tkinter
import p_gtkuti, p_gtkwid, p_ggen
from thanvar import thanfiles
from thantrans import T


class ThanNewCoefs(p_gtkwid.ThanComDialog):
    "Dialog to get the transformation coefficients."

    def __init__(self, *args, **kw):
        "Set title."
        kw.setdefault("title", T[u"ΕΙΣΑΓΩΓΗ ΣΥΝΤΕΛΕΣΤΩΝ ΜΕΤΑΤΡΟΠΗΣ"])
        self.__keys = kw.pop("keys")
        p_gtkwid.ThanComDialog.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        assert 0, "Normally this is a slave dialog, and thanValsDef() should never be called!"
        v = p_ggen.Struct()
        v.entFilsnt = "<Undefined>"
        v.entA0 = v.entA1 = v.entA2 = v.entA3 = v.entA4 = v.entA5 = 1.0
        v.entB0 = v.entB1 = v.entB2 = v.entB3 = v.entB4 = v.entB5 = 1.0
        return v


    def body2(self, win):
        self.fraMetEgsa(win)


    def fraMetEgsa(self, fra):
        "Coeeficients' widgets."
        frb = Tkinter.Frame(fra)
        frb.grid(row=2, column=1, columnspan=3, sticky="we")
        for i in xrange(6):
	    tit = u"A"+str(i)
	    key = "ent" + tit
            lab = Tkinter.Label(frb, text=tit)
            lab.grid(row=i, column=0, sticky="w")
	    wid = p_gtkwid.ThanEntry(frb)
	    wid.grid(row=i, column=1, sticky="we")
	    val = p_gtkwid.ThanValFloatFortran()
	    self.thanWids.append((key, tit, wid, val))

	    tit = u"B"+str(i)
	    key = "ent" + tit
            lab = Tkinter.Label(frb, text=tit)
            lab.grid(row=i, column=2, sticky="w")
	    wid = p_gtkwid.ThanEntry(frb)
	    wid.grid(row=i, column=3, sticky="we")
	    val = p_gtkwid.ThanValFloatFortran()
	    self.thanWids.append((key, tit, wid, val))
        frb.columnconfigure(1, weight=1)
        frb.columnconfigure(3, weight=1)


    def validate(self, strict=True, wids=None, values=None):
        "Returns true if the value chosen by the user is valid."
        ret, vs = self.validate2(strict, wids, values)
        if not ret and strict: return ret

        if strict:
            ret1 = self.__saveCoefs(vs)   #Only when strict, save .snt file and ensure that save succeeded
            if not ret1: return None
            vs.entFilsnt = ret1
        else:
            vs.entFilsnt = self.thanValsSaved.entFilsnt

        self.result = vs
        return ret


    def __saveCoefs(self, vs):
        "Saves coefficients to a file."
        fildir = thanfiles.getFiledir()
        while True:
            fn = p_gtkuti.thanGudGetSaveFile(self, ".snt", T["Save transformation coefficients to a file"],
                                             initialdir=fildir)
            if fn == None: return None  # Save cancelled
            fn = p_ggen.path(fn)
            try:
                fw = open(fn, "w")
                for a in self.__keys[1:]:   #Write coefficients with a certain sequence
                    print a, ":", getattr(vs, a), type(getattr(vs, a))
                    fw.write("%s\n" % getattr(vs, a))
                fw.close()
            except (IOError,), why:  # ImportError happens if BZ2file can not import its base class
                p_gtkuti.thanGudModalMessage(self, why, "%s: %s" % (p_gtkuti.thanAbsrelPath(fn), T["Save failed"]))   # (Gu)i (d)ependent
            else:
                break
        return fn
