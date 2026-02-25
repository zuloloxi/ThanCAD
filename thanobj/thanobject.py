##############################################################################
# ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2016 Thanasis Stamos, June 19, 2016
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
ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers

This module defines the generic ThanCad object. A ThanCad object is an element
without graphical representation, such as DTM, It can be also used as a null
element - this is NOT an abstract class.
"""
import copy


class ThanObject(object):
    """Base class for thancad's objects.

    This class of elements may be used whenever a dummy, or Null element
    (see python recipes), is needed. The element accepts usual commands through
    the routine but does nothing.
    """
    thanObjectName = "GENERICOBJECT"    # Name of the objects's class
    thanObjectInfo = ""
    thanVersions = ("0.0",)

#---Dummy operations

    def thanList(self, than):
        "Shows information about the object."
        pass

#---Reasonable default behavior of objects

    def thanExpThc(self, fw):
        "Saves the object name and its version to a .thc file."
        fw.writeBeg(self.thanObjectName)
        fw.pushInd()
        fw.writeAtt("version", self.thanVersions[-1])
        self.thanExpThc1(fw)
        fw.popInd()
        fw.writeEnd(self.thanObjectName)


    def thanImpThc(self, fr):
        "Reads the object name and returns its version from a .thc file."
        fr.readBeg(self.thanObjectName)
        ver = fr.readAtt("version")[0]
        if ver not in self.thanVersions:
            raise ValueError("Unknown thc version of object %s: %s" % (self.thanObjectName, self.thanThcVersion))
        self.thanImpThc1(fr, ver)
        fr.readEnd(self.thanObjectName)


    def thanExpThc1(self, fw):
        "Save the object to a .thc file."
        fw.prter('Object "%s" was not saved (save not implemented)' % (self.thanObjectName,))


    def thanImpThc1(self, fr, ver):
        "Read the object from a .thc file."
        raise ValueError('Object "%s" can not be read (read not implemented)' % (self.thanObjectName,))


    def thanClone(self):
        "Makes a copy of itself; the cloned copy must have different thanTags."
        el = copy.deepcopy(self)
        return el
