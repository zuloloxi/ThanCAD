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

from math import isnan
from thanimpdxfent import ThanEntities
from thanimpdxfhead import ThanHeader
from thanimpdxftab import ThanTables


class ThanImportError(Exception):  pass


class ThanImportDxf(ThanHeader, ThanEntities, ThanTables):
    "A class to import a dxf file."

#===========================================================================

    def __init__(self, fDxf, dr, defaultLayer="0"):
        "Creates an instance of the class."
        self.thanCancel = 0
        self.__fullBuf  = 0
        self.__lindxf   = 0
        self.thanDr = dr
	self.fDxf   = fDxf
	self.defLay = defaultLayer

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

    def thanUngetDxf(self):
        "Unreads a basic dxf entry."
        self.__fullBuf = 1


    def thanGetDxf(self):
        "Reads a basic dxf entry: a code followed by a value."
        if self.__fullBuf:
            self.__fullBuf = 0
        else:
            s = self.fDxf.readline()
            if s == "": return -1, ""             # End Of File
	    try: 
	        self.__icodp = int(s)
            except ValueError:
	        s1 = "Warning at line %d:\nDxf code not an integer" % self.__lindxf
	        raise ThanImportError, s1
	    s = self.fDxf.readline()
            if s == "": return -1, ""             # End Of File: incomplete..
            self.__scomp = s.rstrip()             # ..dxf file    #Thanasis2011_12_30: Changed from strip() to rstrip() - Happy new year!!
            self.__lindxf += 2
        return self.__icodp, self.__scomp

#===========================================================================

    def thanWarn(self, s):
        "Prints a warning."
        s1 = "Warning at line %d:\n%s" % (self.__lindxf, s)
        self.thanDr.prt(s1)

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

        2011_11_24thanasis: this is to snusre that we will not read NAN
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
