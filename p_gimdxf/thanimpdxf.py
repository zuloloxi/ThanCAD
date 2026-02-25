##############################################################################
# ThanCad 0.0.4: 2dimensional CAD with raster support for engineers.
# 
# Copyright (C)  14, September 2002  by Thanasis Stamos
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
ThanCad 0.0.4: 2dimensional CAD with raster support for engineers.
This module defines an object which reads a .dxf file and it creates
ThanCad's elements to represent it in ThanCad.
"""
import p_ggen
from math import isnan
from thanimpdxfent import ThanEntities
from thanimpdxfhead import ThanHeader
from thanimpdxftab import ThanTables


class ThanImportBase:
    """A producer class to import a drawing saved on syk,mhk,brk,syn,xyz files.

    The class is based on the importation of dxf files; it works like the class
    ThanImportDxf of the p_gimdxf library.
    The class sends drawing commands to the drawing object dr (self.thanDr)
    which is a receiver class instance.
    Here the receiver class is the ThanCadDrSave class.
    """

    def __init__(self, fDxf, dr, defaultLayer="0"):
        "Creates an instance of the class."
        self.thanCancel = 0
        self._fullBuf = 0
        self._prevline = ""
        self._lindxf = 0

        self.thanDr = dr
        self.fDxf = fDxf
        self.defLay = defaultLayer


    def thanImport(self):
        "Begin the import/producing; please override."
        pass


    def thanUngetDxf(self):
        "Unreads a basic dxf entry."
        self._fullBuf = 1


    def thanGetDxf(self):
        "Reads a basic dxf entry: a code followed by a value."
        if self._fullBuf:
            self._fullBuf = 0
        else:
            self._prevline = self.fDxf.readline()
            self._lindxf += 1
        return self._prevline


    def thanWarn(self, s):
        "Prints a warning."
        s1 = "Warning at line %d of file %s: \n%s" % (self._lindxf, self.fDxf.name, s)
        self.thanDr.prt(s1, "can1")


    def thanEr1s(self, s):
        "Raises import error with message."
        s1 = "Error at line %d of file %s: \n%s" % (self._lindxf, self.fDxf.name, s)
        self.thanDr.prt(s1, "can")
        raise p_ggen.ThanImportError, s1


    def thanEr2s(self, s):
        "Raises import error with message (no lines are reported)."
        self.thanDr.prt(s, "can")
        raise p_ggen.ThanImportError, s



class ThanImportDxf(ThanImportBase, ThanHeader, ThanEntities, ThanTables):
    "A producer class to import a dxf file and send drawing commands to the drawing object dr (self.thanDr)."

    def __init__(self, fDxf, dr, defaultLayer="0"):
        "Creates an instance of the class."
        ThanImportBase.__init__(self, fDxf, dr, defaultLayer)
        self._prevline = -1, ""


    def thanGetDxf(self):
        "Reads a basic dxf entry: a code followed by a value."
        if self._fullBuf:
            self._fullBuf = 0
        else:
            s = self.fDxf.readline()
            if s == "": return -1, ""             # End Of File
            try:
                icodp = int(s)
            except ValueError:
                self.thanEr1s("Dxf code not an integer")
            s = self.fDxf.readline()
            if s == "": return -1, ""             # End Of File: incomplete dxf file 
            s = s.rstrip()             #Thanasis2011_12_30: Changed from strip() to rstrip() - Happy new year!!
            self._prevline = icodp, s
            self._lindxf += 2
        return self._prevline

#===========================================================================

    def thanImport(self):
        """Imports [certain] sections of a .dxf file."""
        self.__sections = { "HEADER"  : [self.thanGetHeader,   0],
                            "ENTITIES": [self.thanGetEntities, 0],
                            "TABLES":   [self.thanGetTables,   0]
                          }
        while True:
            icod, text = self.thanGetDxf()
            if icod == -1: break
            if icod != 0: continue         # Unknown code: ignore it
            if text != "SECTION": continue # Unknown text: ignore it
            icod, text = self.thanGetDxf()
            if icod == -1: break
            if icod != 2:
                self.thanWarn("Section name not found: probably corrupted file.")
                continue
            sect = self.__sections.get(text)
            if sect == None: continue      # We don't need this section

            if sect[1] > 1:
                self.thanWarn("Probably corrupted dxf file: "
                "Section "+text+" is multiply declared.\n"
                "This section will be read again.")
            sect[1] = 1
            sect[0]()
        if self.__sections["ENTITIES"][1] < 1:
            self.thanWarn("Warning: 'ENTITIES' section was not found. No elements were imported.")

#===========================================================================

    @staticmethod
    def trAtts(atts, func, *keys):
     """Tries to convert values of keys to the correct type.

     If a key is negative then it doesn't matter if key is not present in dict
     atts. If it is positive, it is an error if key is not in atts.
     Then, the func is applied to the atts[key] and if this is not
     possible an error is returned.
     """
     for key1 in keys:
        key = abs(key1)
        if key not in atts:
            if key1 >= 0: return 1     # Key should be present; return error
        else:
            try: a = func(atts[key])                  # Try to covert to the correct type
            except (ValueError, TypeError): return 1  # Conversion failed; return error
            else:  atts[key] = a                      # Conversion succesful
     return 0


    @staticmethod
    def trAttsFloat(atts, *keys):
        """Tries to convert values of keys to the float type.

        2011_11_24thanasis: this is to ensure that we will not read NAN
        from dxf file.
        If a key is negative then it doesn't matter if key is not present in dict
        atts. If it is positive, it is an error if key is not in atts.
        Then, the float func is applied to the atts[key] and if this is not
        possible an error is returned.
        """
        for key1 in keys:
           key = abs(key1)
           if key not in atts:
               if key1 >= 0: return 1     # Key should be present; return error
           else:
               try:
                   a = float(atts[key])        # Try to covert to the correct type
                   if isnan(a): return 1       # Conversion failed: Not A Number; return error
               except (ValueError, TypeError):
                   return 1                    # Conversion failed; return error
               else:
                   atts[key] = a               # Conversion succesful
        return 0


############################################################################
############################################################################

def thanImportDxf(fDxf, dr, defaultLayer="0"):
    "Creates an instance of the class to do the import."
    ti = ThanImportDxf(fDxf, dr, defaultLayer)
    return ti.thanImport()


############################################################################
############################################################################

#MODULE LEVEL CODE: THIS IS EXECUTED ONLY ONCE

if 0:
    f = file("mhk.dxf", "r")
    t = ThanImportDxf(f, dr)
    t.thanImport()
    f.close()
