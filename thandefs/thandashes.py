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

This module defines the ThanCad Line type, and some builtin line types.
"""

from math import fabs


class ThanLtype:
    "Line style object."

    def __init__(self, name="continuous", desc="continuous ___________________________________________",
                       dashes=(), align="A"):
        """Initialise line type object.

        In contrast to the Tk specification which does not allow zero length
        dashes, ThanCad accepts a zero dash; it is a special case where the
        dash is plotted as a single pixel dot.
        The dashes list is in the form: dash1, space1, dash2, space2, dash3, space3, ...
        Thus the first element is always a dash. The number of elements must be
        even.
        The unit is either 'mm' or 'u'. The fisrt means that the elements are in
        mm which are independent to the scale of the drawing, and the second
        means user data units, which are affacted by the sclae of the drawing."""
        ok, terr = thanDashesTest(dashes)
        assert ok, terr
        self.thanName = name.strip()
        assert self.thanName != ""
        self.thanDesc = desc
        self.thanDashes = tuple(dashes)
        self.thanAlign = align          #For compatibility with other CADs


    def thanTkSet(self, than, unit="mm", scale=1.0):
        "Convert the dashes to Tk gui pixels."
        self.thanPixelSet(than, unit, scale)
        ds = than.dash
        maxpix = 255
        for i,d1 in enumerate(ds):
            if d1 > maxpix: ds[i] = maxpix


    def thanPilSet(self, than, unit="mm", scale=1.0):
        "Convert the dashes to PIL image pixels."
        self.thanPixelSet(than, unit, scale)


    def thanPixelSet(self, than, unit="mm", scale=1.0):
        "Convert the dashes to device dependent pixels."
        if unit == "mm":
            pixperun = than.pixpermm
        else:
            px, py = than.ct.global2LocalRel(1.0, 1.0)
            pixperun = (fabs(px)+fabs(py))*0.5     #Average of the pixels per unit in x and y direction
#        print "ThanLtype: thanTkset() 1: ds=", self.thanDashes
#        print "ThanLtype: thanTkset() 2: pixperun=", pixperun
        pixperun *= scale
#        print "ThanLtype: thanTkset() 3: pixperun=", pixperun
        ds = [int(d1*pixperun+0.5) for d1 in self.thanDashes]
#        print "ThanLtype: thanTkset() 4: ds=", ds

        i = 0
        while i+1 < len(ds):
            if ds[i] == 0 and ds[i+1] == 0:   #If dash and space are zero, eliminate pair
                del ds[i:i+2]
            elif ds[i+1] == 0:                #If zero space, then add current dash to the next dash..
                if i+3 < len(ds): ds[i+2] += ds[i]
                del ds[i:i+2]                 #..If there is no next dash, then it is continuous line (empty list)
            elif ds[i] == 0:                  #If zero dash, then make it 1 (.e. a dot)
                ds[i] = 1
                i += 2
            else:
                i += 2                        #Normal pair: keep it
#        i = 0
#        while i+1 < len(ds):                  #Split dashes > 255 pixels to smaller pieces
#            if ds[i] > 255:
#                ds1 = min((int(ds[i]/2), 255))
#                ds.insert(i, ds1)             #Smaller dash
#                ds.insert(i+1, 1)             #A small space (1 pixel) is needed
#                ds[i+2] = ds[i+2]-ds[i]
#            i += 2
        than.dash[:] = ds


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
        self.thanImpThc1(fr, ver)
        self.thanName = name
        fr.readEnd(self.thanName)


    def thanExpThc1(self, fw):
        "Saves the linetype definition to a .thcx file."
        fw.writeln(self.thanDesc)
        n = len(self.thanDashes)
        fw.writeln("%d" % (n,))
        fw.writeSnode ("DASH", n, self.thanDashes)


    def thanImpThc1(self, fr, ver):
        "Reads the linetype definition from a .thcx file."
        desc = next(fr).rstrip()
        n = int(next(fr))
        dashes = fr.readSnode("DASH", n)
        ok, terr = thanDashesTest(dashes)
        if not ok: raise ValueError(terr)
        self.thanDesc = desc
        self.thanDashes = tuple(dashes)


    MMSENT = "THANCADMM "
    def thanExpDxf(self, fDxf, unit="mm", scale=1.0):
        "Exports the linetype to dxf file."
        desc = self.desc
        if unit == "mm":
            desc = self.MMSENT + desc
            scale *= 0.1                 #thAtCad equivalent is in cm (ThanCad dash is in mm)
        relems = [d1*scale for d1 in self.thanDashes]
        for i in range(0, len(relems), 2):
            relems[i] = -relems[i]
        fDxf.thanDxfCrLtype (self.thanName, desc, relems)


    def thanFromDxf(self, name, desc, elems):
        "Create the linetype from data found in a dxf formatted linetype."
        dash = list(elems)
        i = 1
        while i < len(dash):
            if dash[i-1] < 0 and dash[i] < 0:     #If two consecutive spaces coalesce them to one
                dash[i-1] += dash[i]
                del dash[i]
            elif dash[i-1] >= 0 and dash[i] >= 0: #If two consecutive dashes coalesce them to one
                dash[i-1] += dash[i]
                del dash[i]
            else:
                i += 1
        if len(dash) > 0:
            if dash[0] < 0:            #If ltype begins with space, add a small dash (dot) in front of it
                dash.insert(0, 0.0)
            if len(dash) % 2 != 0:         #If odd number of dashes..
                if len(dash) >= 3: #thanasis2016_12_11
                    dash.append(dash[1])   #..append a space at the end (the first space defined is appended)
                else:              #thanasis2016_12_11
                    dash.append(-dash[0])  #..append a space equal to the first and only dash: ltype contains only one dash!
        for i,d1 in enumerate(dash):   #Now make spaces positive
            dash[i] = fabs(d1)

        temp = self.MMSENT
        if temp not in desc: temp = temp.lower()
        if temp in desc:
            desc = desc.replace(temp, "")
            unit = "mm"
            dash = [d1*10.0 for d1 in dash]  #In this case thAtCad equivalent is cm and we convert it to mm
        else:
            unit = "u"
        self.thanName = name
        self.thanDesc = desc
        self.thanDashes = tuple(dash)
        return unit


def thanDashesTest(dashes):
    "Test if all dashes are ok."
    for d1 in dashes:
        try:
            d1 = float(d1)
        except ValueError as e:
            return False, "Invalid dash: %s" % (e,)
        if d1 < 0.0: return False, "Negative dash or space found"
    for i in range(1, len(dashes), 2):
        if dashes[i] == 0.0: return False, "Zero space found"
#    if len(dashes) > 12: return False, "Too many dashes"     #Tk does not set a limit (as some other CAD does)
    if len(dashes) % 2 != 0: return False, "The number of dashed must an even number"
    return True, ""


def thanDashes():
    "Define some standard dashes."
    dashes = \
    [   ("continuous",           "_______________________________________", ()),
    ]
    dashes1 = \
    [   ("iso_dashedmedium_q1",  "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _", (1, 1)),
        ("iso_dashedmedium_q2",  "__ __ __ __ __ __ __ __ __ __ __ __ __ ", (2, 1)),
        ("iso_dashedmedium_q3",  "___ ___ ___ ___ ___ ___ ___ ___ ___ ___", (3, 1)),
        ("iso_dashedmedium_q4",  "____ ____ ____ ____ ____ ____ ____ ____", (4, 1)),
        ("iso_chainthin_q1_p3",  "_ _ ___ _ ___ _ _ ___ _ ___ _ _ ___ _ ",  (1, 1, 1, 1, 3, 1, 1, 1, 3, 1)),
        ("iso_chainthin_q2_p3",  "__ __ ______ __ ______ __ __ ______ __ ", (2, 1, 2, 1, 6, 1, 2, 1, 6, 1)),
        ("iso_chainthin_q3_p3",  "___ ___ ________ ___ ________ ___ ___ ",  (3, 1, 3, 1, 9, 1, 3, 1, 9, 1)),
        ("iso_chainthin_q1_p4",  "_ _ ____ _ ____ _ _ ____ _ ____ _ _ ",    (1, 1, 1, 1, 4, 1, 1, 1, 4, 1)),
        ("iso_chainthin_q2_p4",  "__ __ ________ __ ________ __ __ ",       (2, 1, 2, 1, 8, 1, 2, 1, 8, 1)),
        ("iso_chainthin_q3_p4",  "___ ___ ____________ ___ ___________ ",   (3, 1, 3, 1, 12, 1, 3, 1, 12, 1)),
        ("iso_chainthick_q1_p3", "_ ___ _ ___ _ ___ _ ___ _ ___ _ ___ _ ",  (1, 1, 3, 1)),
        ("iso_chainthick_q2_p3", "__ ______ __ ______ __ ______ __ ______", (2, 1, 6, 1)),
        ("iso_chainthick_q3_p3", "___ ________ ___ ________ __ _________ ", (3, 1, 9, 1)),
        ("iso_chainthick_q1_p4", "_ ____ ____ _ ____ _ ____ _ ____ _ ____", (1, 1, 4, 1)),
        ("iso_chainthick_q2_p4", "__ ________ __ ________ __ ________ __ ", (2, 1, 8, 1)),
        ("iso_chainthick_q3_p4", "___ ____________ ___ ___________ ___ ",   (3, 1, 12, 1)),
        ("than_dot",             ". . . . . . . . . . . . . . . . . . . .", (0, 1)),
    ]
    dashes.extend(dashes1)

    ltypes = {}
    for dd in dashes:
        name = dd[0]
        desc = dd[1]
        ds = dd[2]
        align = "A"
        ob = ThanLtype(name, desc, ds, align)
        ltypes[name] = ob
    return ltypes
