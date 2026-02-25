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

This module defines the photogrammetric interior orientation of a metric image.
"""
import p_ggen, p_gmath
from thantrans import T
import thandr
from .thanobject import ThanObject


class ThanPhotInterior(ThanObject):
    "An object which stores photogrannetric interior orientation data."
    thanObjectName = "PHOTINTERIOR"    # Name of the objects's class
    thanObjectInfo = "Optical photogrammetric interior orientation."
    thanVersions = ((1,0),)

    def __init__(self, camera=None):
        "Create an initialised or empty model."
        self.image = None
        self.camera = None
        self.fids = ()
        self.tra = p_gmath.Polynomial1_2DProjection()  #First order Poynomial: affine transform: Identity: x = X, y = Y


    def replacePoints(self, proj, lay):
        """Delete and return old points in layer lay and create and return new points at the fiducials.

        It is assumed that the caller has already called thanTkSet."""
        cam = self.camera
        assert cam is not None
        delelems = lay.thanQuad.copy()
        proj[1].thanElementDelete(delelems, proj)
        elev = proj[1].thanVar["elevation"]
        newelems = {}
        for ifid in range(len(cam.x)):
            xp, yp, rej = self.fids[ifid-1]
            if xp == "" or yp == "" or rej: continue
            cp = list(elev)
            cp[:2] = xp, yp
            elem = thandr.ThanPoint()
            elem.thanSet(cp)
            proj[1].thanElementAdd(elem, lay)
            elem.thanTkDraw(proj[2].than)
            newelems[ifid] = elem
        return delelems, newelems


    def getCamera(self): return self.camera

    def setCamera(self, cam):
        "Set camera and make empty pixel values."
        self.camera = cam
        n = len(cam.x)
        self.fids = [["", "", False] for i in range(n)]


    def getImage(self): return self.image
    def setImage(self, image): self.image = image


    def toDialog(self):
        "Return the data in a form needed by ThanInterior dialog."
        cam = self.camera
        assert cam is not None
        v = p_ggen.Struct()
        n = len(cam.x)
        for ifid in range(1, n+1):
            xp, yp, rej = self.fids[ifid-1]
            if xp == "" or yp == "":
                setattr(v, "labXpix%d" % ifid, "")
                setattr(v, "labYpix%d" % ifid, "")
            else:
                setattr(v, "labXpix%d" % ifid, xp)
                setattr(v, "labYpix%d" % ifid, yp)
            setattr(v, "thanChkReject%d" % ifid, rej)
        other = p_ggen.Struct()
        other.image = self.image
        other.camera = cam
        other.tra = self.tra
        return v, other


    def fromDialog(self, v, other):
        "Get the data from ThanInterior dialog."
        n = len(self.camera.x)
        for ifid in range(1, n+1):
            xp = getattr(v, "labXpix%d" % ifid)
            yp = getattr(v, "labYpix%d" % ifid)
            rej = getattr(v, "thanChkReject%d" % ifid)
            self.fids[ifid-1][:] = xp, yp, rej
        self.tra = other.tra


    def thanList(self, than):
        "Shows information about the photogrammetric model object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        if self.camera is not None:
            than.write("%s: %s\n" % (T["Camera"], p_ggen.thanUnicode(self.camera.name)))
        than.write("Fiducials:\n")
        ifid = 0
        for xp, yp, rej in self.fids:
            ifid += 1
            if xp != "": xp = "%8.1f" % xp
            else:        xp = "blank"
            if yp != "": yp = "%8.1f" % yp
            else:        yp = "blank"
            if rej: rej = "rejected"
            else:   rej = "accepted"
            than.write("%d %8s%8s  %s\n" % (ifid, xp, yp, rej))
        if self.tra is not None:
            than.write("Affine transformation x: %15.6f%15.6f%15.6f\n" % tuple(self.tra.L[:3]))
            than.write("                      y: %15.6f%15.6f%15.6f\n" % tuple(self.tra.L[3:6]))


#    v.name: camera name as string
#    v.x[], v.y[]: coordinates of fiducials as floats.
    def thanExpThc1(self, fw):
        "Saves the photogrammetric interior orientation attributes to a .thc file."
        if self.image is None:  fw.writeAtt("image", "_NONE_")
        else:                   fw.writeAtt("image", "%d" % self.image.handle)

        fw.writeBeg("camera")
        fw.pushInd()
        if self.camera is None:
            fw.writeAtt("name", "_NONE_")
        else:
            fw.writeAtt("name", self.camera.name)
            fw.writeNodes(zip(self.camera.x, self.camera.y))  #works for python2,3  (writeNodes acceprts iterator of nodes)
        fw.popInd()
        fw.writeEnd("camera")

        cs = []
        for x,y,r in self.fids:
            if x == "" or y == "": x = y = -999999.0
            cs.append((x, y, float(r)))
        fw.writeNodes(cs)

        fw.writeBeg("affine")
        self.tra.write(fw)
        fw.writeEnd("affine")


    def thanImpThc1(self, fr, ver, than):
        "Reads the simplification settings from a .thc file."
        im = fr.readAtt("image")[0]
        if im == "_NONE_":
            self.image = None
        else:
            handle = int(im)
            self.image = fr.thanProj[1].thanTagel[handle] # This will raise ValueError if handle is not found

        fr.readBeg("camera")
        cam = fr.readAtt("name")[0]
        if cam == "_NONE_":
            self.camera = None
        else:
            self.camera = p_ggen.Struct()
            self.camera.name = cam
            cs = fr.readNodes()
            self.camera.x = [c[0] for c in cs]
            self.camera.y = [c[1] for c in cs]
        fr.readEnd("camera")

        cs = fr.readNodes()
        self.fids = []
        for x,y,r in cs:
            if x == -999999.0 or y == -999999.0: x = y = ""
            self.fids.append((x, y, bool(int(r+0.1))))

        fr.readBeg("affine")
        self.tra.read(fr)
        fr.readEnd("affine")
