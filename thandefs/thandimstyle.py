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

This module defines the ThanCad dimension style.
"""

import p_ggen

class ThanDimstyle:
    "Dimension style object."
    thanTicktypes = "arrow", "architectural_tick"

    def __init__(self):
        "Initialise dimension style object."
        self.thanSet()


    def thanSet(self, name="standard", desc="default dimension style",
            ndigits=2, textsize=2.0, ticktype="architectural_tick", ticksize=2.0):
        "Initialise dimension style object."
        ok, terr = self.thanTest(name, desc, ndigits, textsize, ticktype, ticksize)
        if not ok: raise ValueError(terr)

        self.thanName     = name.strip()
        self.thanDesc     = desc
        self.thanTicktype = ticktype
        self.thanTicksize = ticksize
        self.thanTextsize = textsize
        self.thanNdigits  = int(ndigits)


    @staticmethod
    def thanTest(name, desc, ndigits, textsize, ticktype, ticksize):
        name1 = name.strip()
        ndigits1 = int(ndigits)
        if name1 == "" or " " in name1 or "\n" in name1 or "\t" in name1:
            return False, "Invalid dimension style name: {}".format(name)
        if ndigits1 < 0 or ndigits1 > 15:
            return False, "Invalid dimension style number of desimal digits: {}".format(ndigits)
        if textsize <= 0.0:
            return False, "Invalid dimension style text size: {}".format(textsize)
        if ticktype not in ThanDimstyle.thanTicktypes:
            return False, "Invalid dimension style tick type: {}".format(ticktype)
        if ticksize <= 0.0:
            return False, "Invalid dimension style tick size: {}".format(ticksize)
        return True, ""


    def thanClone(self):
        "Make a distinct copy of self."
        c = ThanDimstyle()
        c.thanSet(self.thanName, self.thanDesc,
            self.thanNdigits, self.thanTextsize, self.thanTicktype, self.thanTicksize)
        return c

    def thanTkSet(self, than, unit="mm", scale=1.0):
        "Convert the dimstyle to Tk gui pixels."
        than.dimstyle = self.thanClone()
        if unit == "mm":
            #than.pixpermm      #How many pixels correspond to 1 mm to the screen
            dt = than.thanGudGetDt(dpix=than.pixpermm) #How many user units correspond to pixpermm pixels..
                                                       #..that is how many units to a single mm
            than.dimstyle.thanScale(dt*scale)
        else:
            than.dimstyle.thanScale(scale)
        print("thanTkSet(): dimstyle.thanTextsize=", than.dimstyle.thanTextsize)


    def thanDxfSet(self, than, unit="mm", scale=1.0):
        "Convert the dimstyle to Tk gui pixels."
        than.dimstyle = self.thanClone()
        if unit == "mm":
            than.dimstyle.thanScale((scale*0.1)*than.scale)  #Convert mm to cm, and the multiply by klimaka
        else: #Unit is in user units
            than.dimstyle.thanScale(scale)

    def thanPixelSet(self, than, unit="mm", scale=1.0):
        "Convert the dashes to device dependent pixels."
        if unit == "mm":
            pixperun = than.pixpermm
        else:
            #px, py = than.ct.global2LocalRel(1.0, 1.0)
            #pixperun = (fabs(px)+fabs(py))*0.5     #Average of the pixels per unit in x and y direction
            dt = thanGudGetDt(self, dpix=1)
            pixperun = 1.0/dt
        pixperun *= scale
        return pixperun


    def thanScale(self, fact):
        "Multiply all lengths by fact."
        self.thanTicksize *= fact
        self.thanTextsize *= fact


    def thanExpThc(self, fw):
        "Saves the object name to a .thcx file."
        fw.writeBeg(self.thanName)
        fw.pushInd()
        self.thanExpThc1(fw)
        fw.popInd()
        fw.writeEnd(self.thanName)


    def thanImpThc(self, fr, ver):
        "Reads the object name and returns its version from a .thcx file."
        name = next(fr).strip()[1:-1]
        fr.unread()
        fr.readBeg(name)
        self.thanImpThc1(fr, ver, name)
        fr.readEnd(self.thanName)


    def thanExpThc1(self, fw):
        "Saves the dimension style definition to a .thcx file."
        f = fw.formFloat
        fw.writeAttb("DESCRIPTION", self.thanDesc)
        fw.writeAtt("TICK", ("%s "+f) % (self.thanTicktype, self.thanTicksize))
        fw.writeAtt("TEXT", ("%d "+f) % (self.thanNdigits, self.thanTextsize))


    def thanImpThc1(self, fr, ver, name):
        "Reads the linetype definition from a .thcx file."
        desc = fr.readAttb("DESCRIPTION")
        temp = fr.readAtt("TICK")
        ticktype = temp[0]
        ticksize = float(temp[1])
        temp = fr.readAtt("TEXT")
        ndigits = int(temp[0])
        textsize = float(temp[1])
        self.thanSet(name, desc, ndigits, textsize, ticktype, ticksize) #This may raise ValueError


    def thanTodialog(self, proj):
        "Return the data in a form needed by dim style dialog."
        s = p_ggen.Struct("Dimension style parameters")
        s.entName = self.thanName
        s.entDesc = self.thanDesc
        s.choNdigits  = self.thanNdigits    #decimal digits: "2"
        s.entTextsize = self.thanTextsize
        s.choTicktype = self.thanTicktypes.index(self.thanTicktype)
        s.entTicksize = self.thanTicksize
        return s


    def thanFromdialog(self, proj, s):
        "Get parameters from dim style dialog."
        self.thanSet(name=s.entName, desc=s.entDesc,
            ndigits=s.choNdigits, textsize=s.entTextsize,
            ticktype=self.thanTicktypes[s.choTicktype], ticksize=s.entTicksize)
