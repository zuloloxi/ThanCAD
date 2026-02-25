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

This module defines the raster image element, based on Python Image Library.
"""

import os
from math import fabs, cos, sin, atan2
import p_gimage, p_gtkwid, p_gbmp, p_gtri
from p_gmath import PI2, thanNearx
from p_ggen import iterby2, path, thanUnicode, thanUnunicode, isString
from p_gfil import Datlin
from thanvar import Canc, thanfiles
from thandefs import imageOpen
from thantrans import T
from . import thanintall
from .thanelem import ThanElement
from .thanutil import thanPntNearest, thanPntNearest2, thanPerpPoints, thanSegNearest
from .thanline import ThanLine
from .thantext import ThanText


class ThanImage(ThanElement):
    """A raster image; read theory.txt"""
    thanTkCompound = 100        # The number of Tkinter objects that make the element:
                                # 2=compound (Image and frame), 100=compound (frame and text)
    thanElementName = "IMAGE"   # Name of the element's class

#===========================================================================

    def thanSet (self, filnam, image, c1, c2, theta, transpose=0, clip=None, loaded=True, embedded=False):
        "Sets the attributes of the image."
        assert c2[0]>=c1[0] and c2[1]>=c1[1], "Image can not have negative dimensions!"
        self.setBoundBox([c1[0], c1[1], c2[0], c2[1]])
        self.c1 = c1               #Possibly clipped point
        self.c2 = c2               #Possibly clipped point
        self.c1ori = list(c1)      #Unclipped point
        self.c2ori = list(c2)      #Unclipped point

        self.image = image
        dxp, dyp = image.size
        if dxp < 2 or dyp < 2:
            self.image = p_gimage.ThanImageMissing()  # Defaults to size 100x100
            dxp, dyp = image.size
        self.size = dxp, dyp                 # Make the following computations easier
        self.imageori = self.image           # Note that this does not waste memory

        self.theta = theta % PI2             # radians assumed
        self.transpose = 0                   # 0, 1, 2, 3: means 0, 90, 180, 270 rotation anti-clockwise
        self.filnam = path(filnam).expand()
        self.imagez = None
        self.view = [1e100, 1e100, -1e100, -1e100]
        self.clipped = False
        self.thanTranspose(transpose)
        self.thanClip(clip)
        self.visited = None                  # Placeholder of a tracker object used in semi-automatic trace
        self.loaded = bool(loaded)           #If it is False, then the raster is not displayed
        self.embedded = bool(embedded)       #If it is True, then the raster is saved into .thcx
#       self.thanTags = ()                   # thanTags is initialised in ThanElement


    def thanClip(self, clip):
        "Try to clip image in the given coordinates."
        if clip is None: return False, "No clip defined"
        c1, c2 = clip
        x1, y1 = c1[:2]
        x2, y2 = c2[:2]
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1
        x1 = max((x1, self.c1[0]))
        y1 = max((y1, self.c1[1]))
        x2 = min((x2, self.c2[0]))
        y2 = min((y2, self.c2[1]))
        assert x2 >= x1 and y2 >= y1, "Impossible error in thanClip()"
        c1 = list(self.c1ori); c1[:2] = x1, y1
        c2 = list(self.c1ori); c2[:2] = x2, y2
        j1, i2 = self.thanGetPixCoor(c1)
        j2, i1 = self.thanGetPixCoor(c2)
        if i2-i1+1 < 2 or j2-j1+1 < 2: return False, "Region too small to clip"
        self.image = self.image.crop((j1, i1, j2, i2))
        self.size = self.image.size
        self.c1 = c1
        self.c2 = c2
        self.clip = (c1, c2)
        self.clipped = True
        self.setBoundBox([self.c1[0], self.c1[1], self.c2[0], self.c2[1]])
        return True, ""


    def thanClipDel(self):
        "Unclip image."
        self.c1 = self.c1ori
        self.c2 = self.c2ori
        self.image = self.imageori
        self.size = self.image.size
        self.clipped = False
        self.setBoundBox([self.c1[0], self.c1[1], self.c2[0], self.c2[1]])


    def thanIsNormal(self):
        "Returns False if the image is degenerate."
        if thanNearx(self.c1ori[0], self.c2ori[0]): return False        # There is no degenerate image
        if thanNearx(self.c1ori[1], self.c2ori[1]): return False        # There is no degenerate image
        return True


    def __getstate__(self):
        odict = self.__dict__.copy() # Note that this is a cheap operation
        del odict["image"]           # Do not save the image in the file
        del odict["imageori"]        # Do not save the image in the file
        del odict["imagez"]
        odict["filnam"] = thanUnicode(self.filnam).split(os.sep)  # If not in unicode it transforms it to unicode..
        return odict                                #..p_ggen should have been notified about the local language encoding


    def __setstate__(self, odict):
        self.__dict__.update(odict)
        if isString(path):
            self.filnam = path(thanUnicode(os.sep).join(self.filnam)).expand() # Filnam is already in unicode
        else:
            self.filnam = path(os.sep.join(map(thanUnunicode, self.filnam))).expand()  #..p_ggen should have been notified about the local language encoding  #works for python2,3

        self.image, _ = imageOpen(self.filnam, self.size)
#        try:
#            self.image = p_gimage.open(self.filnam)
#            dxp, dyp = self.image.size
#            if dxp < 2 or dyp < 2: raise ValueError, T["Image is probably corrupted: size is less than 2 pixels"]
#            im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised
#        except (ValueError, IOError):
#            dxp, dyp = self.size
#            self.image = p_gimage.ThanImageMissing((dxp, dyp))

#       If it is not the same as the saved image, the new image will be fitted in the same area
        self.imageori = self.image
        transpose = self.transpose
        self.transpose = 0
        self.thanTranspose(transpose, c1c2=False)   #This sets self.size
        if self.clipped:
            c1 = self.c1
            c2 = self.c2
            self.c1 = self.c1ori
            self.c2 = self.c2ori
            self.thanClip((c1, c2))
        self.imagez = None


    def thanClone(self):
        """Makes a geometric clone of itself.

        Since PIL.copy() is a lazy operation, the cloned raster DOES NOT
        occupy more memory. But, to be sure, we return a reference to the raster
        so it is sure that no memory is wasted.
        """
        im = self.image
        self.image = None
        el = ThanElement.thanClone(self)
        self.image = el.image = im
        return el


    def thanRotate(self):
        "Rotates the element within XY-plane with predefined angle and rotation angle."
        c1 = self.thanRotateXy(self.c1)
        self.c2[0] += c1[0]-self.c1[0]
        self.c2[1] += c1[1]-self.c1[1]
        self.c1 = c1

        c1 = self.thanRotateXy(self.c1ori)
        self.c2ori[0] += c1[0]-self.c1ori[0]
        self.c2ori[1] += c1[1]-self.c1ori[1]
        self.c1ori = c1

        self.theta += self.rotPhi
        self.theta %= PI2
        self.setBoundBox([self.c1[0], self.c1[1], self.c2[0], self.c2[1]])


    def thanTranspose(self, transpose, c1c2=True):
        "Rotate image pixels 0, 90, 180 or 270 degrees without altering the insertion point."
        assert transpose in (0, 1, 2, 3), "Invalid transpose code: %s" % (transpose,)
        if transpose != 0: assert not self.clipped, "can't transpose clipped image"   #FIXME
        if transpose == 1:   self.image=self.image.transpose(p_gimage.ROTATE_90)    # counterclockwise
        elif transpose == 2: self.image=self.image.transpose(p_gimage.ROTATE_180)   # counterclockwise
        elif transpose == 3: self.image=self.image.transpose(p_gimage.ROTATE_270)   # counterclockwise
        if c1c2 and transpose in (1, 3):    #if 90 or 270, exchange x and y size
            dx = self.c2[0] - self.c1[0]
            dy = self.c2[1] - self.c1[1]
            self.c2[0] += dy-dx
            self.c2[1] += dx-dy
        self.size = self.image.size
        self.transpose = (self.transpose + transpose) % 4
        self.setBoundBox([self.c1[0], self.c1[1], self.c2[0], self.c2[1]])


    def thanMirror(self):
        "Mirrors the element within XY-plane with predefined point and unit vector."
        dbig = self.c2[0] - self.c1[0]
        cbig = list(self.c1)
        cbig[0] += dbig*cos(self.theta)
        cbig[1] += dbig*sin(self.theta)
        cbig = self.thanMirrorXy(cbig)

        c1 = self.thanMirrorXy(self.c1)
        self.c2[0] += c1[0]-self.c1[0]
        self.c2[1] += c1[1]-self.c1[1]
        self.c1 = c1

        c1 = self.thanMirrorXy(self.c1ori)
        self.c2ori[0] += c1[0]-self.c1ori[0]
        self.c2ori[1] += c1[1]-self.c1ori[1]
        self.c1ori = c1

        self.theta = atan2(cbig[1]-self.c1[1], cbig[0]-self.c1[0]) % PI2
        self.setBoundBox([self.c1[0], self.c1[1], self.c2[0], self.c2[1]])


    def thanScale(self, cs, scale):
        "Scales the element in n-space with defined scale and center of scale."
        self.c1 = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.c1, cs)] #works for python2,3
        self.c2 = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.c2, cs)] #works for python2,3
        self.c1ori = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.c1ori, cs)] #works for python2,3
        self.c2ori = [cs1+(cc1-cs1)*scale for (cc1,cs1) in zip(self.c2ori, cs)] #works for python2,3
        self.setBoundBox([self.c1[0], self.c1[1], self.c2[0], self.c2[1]])


    def thanMove(self, dc):
        "Moves the element with defined n-dimensional distance."
        self.c1 = [cc1+dd1 for (cc1,dd1) in zip(self.c1, dc)] #works for python2,3
        self.c2 = [cc1+dd1 for (cc1,dd1) in zip(self.c2, dc)] #works for python2,3
        self.c1ori = [cc1+dd1 for (cc1,dd1) in zip(self.c1ori, dc)] #works for python2,3
        self.c2ori = [cc1+dd1 for (cc1,dd1) in zip(self.c2ori, dc)] #works for python2,3
        self.setBoundBox([self.c1[0], self.c1[1], self.c2[0], self.c2[1]])

    def thanOsnap(self, proj, otypes, ccu, eother, cori):
        "Return a point of type in otypes nearest to ccu."
        if "ena" not in otypes: return None            # Object snap is disabled
        cp = self.__boundaryLine()
        ps = []
        if "end" in otypes:
            for c in cp:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "end", c))
        if "mid" in otypes:
            for ca, cb in iterby2(cp):
                c = [(ca1+cb1)*0.5 for (ca1,cb1) in zip(ca, cb)]  #works for python2,3
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "mid", c))
        if "nea" in otypes:
            c = thanPntNearest(cp, ccu)
            if c is not None:
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "nea", c))
        if cori is not None and "per" in otypes:
            for c in thanPerpPoints(cp, cori):
                ps.append((fabs(c[0]-ccu[0])+fabs(c[1]-ccu[1]), "per", c))
        if eother is not None and "int" in otypes:
            ps.extend(thanintall.thanIntsnap(self, eother, ccu, proj))
        if len(ps) < 1: return None
        return min(ps)


    def __boundaryLine(self):
        "Returns the boundary as a line (a list of points)."
        cp = [self.c1, list(self.c1), self.c2, list(self.c2), self.c1]
        cp[1][0] = self.c2[0]
        cp[3][0] = self.c1[0]
#        cp = [(self.x1, self.y1), (self.x2, self.y1), (self.x2, self.y2), (self.x1, self.y2)]
        return cp


    def thanPntNearest(self, ccu):
        "Finds the nearest point of this line to a point."
        return thanPntNearest2(self.__boundaryLine(), ccu)[0]
    def thanPntNearest2(self, ccu):
        "Finds the nearest point of this line to a point."
        return thanPntNearest2(self.__boundaryLine(), ccu)
    def thanPerpPoints(self, ccu):
        "Finds perpendicular point from ccu to polyline."
        return thanPerpPoints(self.__boundaryLine(), ccu)
    def thanSegNearest(self, ccu):
        "Finds the nearest segment of the surrounding quadrilateral of this image to a point."
        return thanSegNearest(self.__boundaryLine(), ccu)

    def getInspnt(self):
        "Returns the insertion point of the image."
        return list(self.c1)

    def thanChelev(self, z):
        "Set constant elevation of z."
        self.c1[2] = z
        self.c2[2] = z
        self.c1ori[2] = z
        self.c2ori[2] = z

    def thanChelevn(self, celev):
        "Set constant elevation of z and higher dimensions."
        self.c1[2:] = celev
        self.c2[2:] = celev
        self.c1ori[2:] = celev
        self.c2ori[2:] = celev

    def thanLength(self):
        "Returns the length of the (clipped) image."
        alx = self.c2[0]-self.c1[0]    # Note that alx > 0
        aly = self.c2[1]-self.c1[1]    # Note that aly > 0
        if alx > aly: return alx
        return aly

    def thanArea(self):
        "Returns the area of the (clipped) image."
        alx = self.c2[0]-self.c1[0]    # Note that alx > 0
        aly = self.c2[1]-self.c1[1]    # Note that aly > 0
        return alx*aly

    def thanBreak(self, c1=None, c2=None):
        "Just inform that the image can not be broken."
        return False       # Break is NOT implemented

#===========================================================================

    def thanTkGet(self, proj, imori=None, imfilnamori=None, insertmode="u"):
        """Gets the attributes of the image interactively from a window.

        insertmode="u": user data units,
                   "f": photogrammetric pixels (world coordinates 0.0,0.0
                        correspond to the middle of the lower left pixel)
                   "p": pixels (world coordinates 0.0,0.0 correspond to the
                        lower left corner of the lower left pixel
                   "m": milimeters
                   "c": Greek cadastre
                   "g": GeoTiff (currently only certain parts are supported)
        """
        tit = T["Image file open failed"]
        insertmode = insertmode[:1]
        if imori is None:
            fi, im = self.__getImage(proj, insertmode, tit)
            if fi == Canc: return Canc
            dxp, dyp = im.size
        else:
            assert insertmode not in "cg", "Cadastre and geotiff images should have no given imori!!"
            im = imori
            fi = imfilnamori
            dxp, dyp = im.size
            if dxp < 2 or dyp < 2:
                why = T["Image is probably corrupted: size is less than 2 pixels"]
                p_gtkwid.thanGudModalMessage(proj[2], why, tit)   # (Gu)i (d)ependent
                return Canc

        if insertmode not in "rpmcg":
            insertmode = proj[2].thanGudGetPoint(T["Lower-left image point (rectification/pixel/mm/cadastre/<enter>): "], options=("rectification", "pixel","mm","cadastre"))
            if insertmode == Canc: return Canc   # Image cancelled (no destroy required)
        if insertmode == "r":                    # Image is for pixel counting
            c1 = list(proj[1].thanVar["elevation"])
            c1[:2] = -0.5, -0.5  # This is the lower-left corner of the lower-left pixel
            c2 = list(c1)
            c2[0] += dxp         # This is the upper-right corner of the upper-right pixel
            c2[1] += dyp
        elif insertmode == "p":                    # Image is for pixel counting
            proj[2].thanPrt("Warning: use r (rectification) if you intend to digitise image for\n photogrammetry/rectification/mapping", "can1")
            c1 = list(proj[1].thanVar["elevation"])
            c1[:2] = 0.0, 0.0    # This is the lower-left corner of the lower-left pixel
            c2 = list(c1)
            c2[0] += dxp         # This is the upper-right corner of the upper-right pixel
            c2[1] += dyp
        elif insertmode == "m":                  # Image is input in mm
            dpi = self.__dpiGet(proj, im, fi)
            if dpi == Canc: return Canc
            c1 = list(proj[1].thanVar["elevation"])
            c1[:2] = 0.0, 0.0    # This is the lower-left corner of the lower-left pixel
            c2 = list(c1)
            c2[0] += dxp/(dpi/25.3997)           # This is the upper-right corner of the upper-right pixel
            c2[1] += dyp/(dpi/25.3997)
        elif insertmode == "c":                  # Image name conventions according to Greek cadastre maps
            x1, y1, scale = self.__imageKthmxy(fi)
            mes = T["Greek cadastre image scale (1000/5000/<enter>=%d): "] % (scale,)
            scale = proj[2].thanGudGetPosFloat(mes, default=float(scale))
            if scale == Canc: return Canc        # Image cancelled (no destroy required)
            c1 = list(proj[1].thanVar["elevation"])
            c1[:2] = x1, y1   # This is the lower-left corner of the lower-left pixel
            c2 = list(c1)
            c2[0] += 80.0 * scale / 100.0         # Map's standardised width  is 80cm
            c2[1] += 60.0 * scale / 100.0         # Map's standardised height is 60cm
        elif insertmode == "g":                  # GeoTiff
            x1, y2, scalex, scaley, nxcols, nyrows, GDAL_NODATA = p_gtri.prop(im)   #Note that we already have checked the validity
            c1 = list(proj[1].thanVar["elevation"])
            c1[:2] = x1, y2-dyp*scaley   # This is the lower-left corner of the lower-left pixel
            c2 = list(c1)
            c2[:2] = x1+dxp*scalex, y2
        else:
            c1 = insertmode
            c2 = proj[2].thanGudGetRectratio(c1, T["Image width in user data units: "], float(dyp)/dxp)
            if c2 == Canc: return Canc           # Image canceled (no destroy is required)
        self.thanSet(fi, im, c1, c2, theta=0.0, transpose=0, clip=None, loaded=True)
        return True                              # Image OK


    def __getImage(self, proj, insertmode, tit):
        "Prompt the user to define the image file, and check image."
        fildir = thanfiles.getFiledir()
        while True:
            fi = p_gtkwid.thanGudGetReadFile(proj[2], "*", T["Choose image file"],
                     initialdir=fildir)
            if fi is None: return Canc, Canc            # Image canceled
            try:
                fr = open(fi, "rb")
            except IOError as why:
                p_gtkwid.thanGudModalMessage(proj[2], why, tit)     # (Gu)i (d)ependent
                continue
            fr.close()

            im, terr = imageOpen(fi)    #This also checks if dxp>=2 and dyp>=2
            if terr != "":
                p_gtkwid.thanGudModalMessage(proj[2], terr, tit)     # (Gu)i (d)ependent
            elif insertmode == "c":
                x1, y1, scale = self.__imageKthmxy(fi)
                if x1 is not None: break
                p_gtkwid.thanGudModalMessage(proj[2], scale, tit)   #scale has the error message
            elif insertmode == "g":      # Geotiff
                try:                  _ = p_gtri.prop(im)
                except ValueError as e: p_gtkwid.thanGudModalMessage(proj[2], e, tit)   #Not a geotiff/not supported
                else:                   break
            else:
                break
        return fi, im


    def __dpiGet(self, proj, im, fi):
        "Gets dpi from user."
        try:
            dpi = p_gbmp.getDpi(im, fi)
            if dpi < 2:
                dpi = 0
                why = "Resolution too low"
        except ValueError as e:
            dpi = 0
            why = str(e)
        if dpi <= 0:
            proj[2].thanPrter("%s : %s" % (T["Could not determine image resolution (dpi)"], why))
            while True:
                dpi = proj[2].thanGudGetPosFloat(T["Please enter dpi (enter=72) : "], default=72.0)
                if dpi == Canc: return Canc
                if dpi >= 2: break
                proj[2].thanPrter("%s: %s" % (T["Invalid dpi"], dpi))
        return dpi


    def __imageKthmxy(self, fpath):
        """Compute the coordinates of the lower left corner of image of Greek national cadastre map, given the filename.

        Example names of 1:5000 maps: 0480022300.bmp, 0480022330.bmp, 0480022360.bmp, 0484022300.bmp, 0484022330.bmp,
                                      0484022360.bmp, 0488022300.bmp, 0488022330.bmp, 0488022360.bmp,
        Example names of 1:1000 maps: 0482422318.bmp, 0482422324.bmp, 0482422330.bmp, 0482422336.bmp, 0482422366.bmp,
                                      0483222366.bmp, 0487222360.bmp, 0487222366.bmp, 0488022360.bmp, 0488022366.bmp,
                                      0488822318.bmp, 0488822324.bmp, 0488822366.bmp
        """
        name = fpath.namebase.strip()
        n = len(name)
        if n > 10: name = name[n-10:]
        try:
            y = int(name[-5:])
            x = int(name[:-5])       #This is ok if len(name) == 9
        except ValueError:
            return None, None, T["Filename %s does not abide to naming conventions of Greek cadastre map images"] % (name,)
        if x % 10 == 0 and  y % 10 == 0:   #Guess that this is 1:5000
            scale = 5000                   #This may also be scale 1:1000, but maps of 1:5000 are far more common
        else:
            scale = 1000
        return x*100.0, y*100.0, scale


#    def __getxyfromname(self, fpath):
#        "Try to get the lower left point coordinates encoded in the name of the image file."
#        x, y, scale = self.__imageKthmxy(fpath)
#        if x is not None: return x, y, scale
#        name = fpath.namebase
#        for sep in "_- ":
#            a = name.split(sep)
#            if len(a) < 2: continue
#            try:
#                x, y = map(float, a[-2:])   #works for python2,3
#            except ValueError:
#                continue
#            return x, y, 5000
#        return None, None, T["Could not determine x, y in the filename %s\n"\
#           "It does also not abide to naming conventions of Greek cadastre map images."] % (name,)


    def thanTkLocate(self, proj):
        "Specifies the location of the image file (usually when it was not found)."
        tit = T["Image file open failed"]
        fn = self.filnam
        fildir = fn.parent
        while True:
            fi = p_gtkwid.thanGudGetReadFile(proj[2], "*", T["Locate image file"],
                     initialdir=fildir, initialfile=fn.basename())
            if fi is None: return Canc            # location canceled
            fi = path(fi)
            im, terr = imageOpen(fi)
            if terr != "":
                p_gtkwid.thanGudModalMessage(proj[2], terr, tit)   # (Gu)i (d)ependent
                continue
#            try:
#                im = p_gimage.open(fi)
#                if im.size[0] < 2 or im.size[1] < 2: raise ValueError, T["Image is probably corrupted: size is less than 2 pixels"]
#                im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised
#            except (IOError, ValueError), why:
#                p_gtkwid.thanGudModalMessage(proj[2], why, tit)   # (Gu)i (d)ependent
#                continue
            else:
                break
        if self.clipped:
            self.thanSet(fi, im, self.c1ori, self.c2ori, theta=0.0,
                transpose=self.transpose, clip=(self.c1, self.c2), loaded=self.loaded)
        else:
            self.thanSet(fi, im, self.c1, self.c2, theta=0.0, transpose=self.transpose, clip=None, loaded=self.loaded)
        return True                              # Image OK


    def thanLogGet(self, proj, fi):
        """Reads the position of the image from a .log file; raises IOError and ValueError.

PIXEL SIZE:       13803      8756
#CORNER COORDINATES (EGAS87)
LOWER LEFT:       488104.638    4235924.230
LOWER RIGHT:      492487.039    4235924.230
UPPER RIGHT:      492487.039    4238704.227
UPPER LEFT:       488104.638    4238704.227
        """
        fr = open(fi)
        fr = Datlin(fr)
        fr.datCom("PIXEL SIZE")
        fr.datCom("LOWER LEFT");  x1 = fr.datFloat(); y1 = fr.datFloat()
        fr.datCom("LOWER RIGHT")
        fr.datCom("UPPER RIGHT"); x2 = fr.datFloat(); y2 = fr.datFloat()
        fr.datCom("UPPER LEFT")
        c1 = list(proj[1].thanVar["elevation"])
        c2 = list(c1)
        c1[:2] = x1, y1
        c2[:2] = x2, y2

        fi = path(fi)
        fi = fi.parent / fi.namebase + ".bmp"
        if not fi.exists():
            fi = fi.parent / fi.namebase + ".BMP"   #Support windows; yeah, windows "just" works
        im, terr = imageOpen(fi)
        if terr != "": raise ValueError(terr)
        self.thanSet(fi, im, c1, c2, theta=0.0, loaded=True)


    def thanTfwGet(self, proj, fi):
        """Reads the position of the image from a .tfw file; raises IOError and ValueError.

Dimitra 2012_04_03
The relationship between EGSA87 X, Y coordinates and the pixel coordinates
of the othophotos is the affine transformation:
X = ax X + bx Y + cx
Y = ay X + by Y + cy
The coefficents are written in ascii form in the 6 lines of
the *.tfw files:
Line   Coefficient
1      ax
2      ay
3      bx
4      by
5      cx
6      cy

In all cases seen in orthophotos of LIDAR, the coefficents ay and bx are
zero, rendering the equation in simpler form:
X = ax X + cx
Y = by Y + cy

Looking at the coefficients found in *.tfw files, we conclude that the first
pixel is pixel 0 and not pixel 1. That's why they have put +0.50 in
cx and cy coefficients:

1.0000000000
0.0
0.0
-1.0000000000
551884.5000000000
4176435.5000000000

Using the formulas and the number pixel in the x and y direction, we
compute the corber points.
        """
        try:
            fr = open(fi)
            ax = float(next(fr))
            ay = float(next(fr))
            bx = float(next(fr))
            by = float(next(fr))
            cx = float(next(fr))
            cy = float(next(fr))
            fr.close()
        except StopIteration: raise IOError("Incomplete .tfw/.j2w file")

        fi = path(fi)
        def checkifexists(exts):
            for ext in exts:
                fi2 = fi.parent / fi.namebase + ext
                if fi2.exists(): break
                fi2 = fi.parent / fi.namebase + ext.upper()   #Support windows; yeah, windows "just" works
                if fi2.exists(): break
            else:
                raise ValueError("File {} (or .jp2 ) does not exist")
            return fi2
        if fi.ext.lower() == ".j2w": fi = checkifexists((".jp2", ".jpg"))
        else:                        fi = checkifexists((".tif", ))

        im, terr = imageOpen(fi)
        if terr != "": raise ValueError(terr)
        b, h = im.size
        xp1, yp1 = 0, h
        xp2, yp2 = b, 0
        x1 = ax*xp1 + bx*yp1 + cx
        y1 = ay*xp1 + by*yp1 + cy
        x2 = ax*xp2 + bx*yp2 + cx
        y2 = ay*xp2 + by*yp2 + cy
        c1 = list(proj[1].thanVar["elevation"])
        c2 = list(c1)
        c1[:2] = x1, y1
        c2[:2] = x2, y2
        self.thanSet(fi, im, c1, c2, theta=0.0, loaded=True)


    def thanGeotifGet(self, proj, fi):
        "Reads a geotiff image; only certain parts are implemented; may raise ValueError."
        im, terr = imageOpen(fi)
        if terr != "": raise ValueError(terr)
        dxp, dyp = im.size
        x1, y2, scalex, scaley, nxcols, nyrows, GDAL_NODATA = p_gtri.prop(im)   #Note that we already have checked the validity
        c1 = list(proj[1].thanVar["elevation"])
        c1[:2] = x1, y2-dyp*scaley   # This is the lower-left corner of the lower-left pixel
        c2 = list(c1)
        c2[:2] = x1+dxp*scalex, y2
        self.thanSet(fi, im, c1, c2, theta=0.0, loaded=True)


    def thanUnload(self, than):
        "Remove the raster of the image from the canvas."
        if self.embedded: return 1, T["Embedded image %s can not be unloaded."] % (self.filnam,)
        self.loaded = False
        if isinstance(self.image, p_gimage.ThanImageMissing): return 1, T["Image %s already unloaded!"] % (self.filnam,)
        than.dc.delete(self.thanTags[0])
        im = p_gimage.ThanImageMissing(self.size)
        if self.clipped:
            self.thanSet(self.filnam, im, self.c1ori, self.c2ori, theta=0.0, transpose=self.transpose, clip=(self.c1, self.c2), loaded=self.loaded)
        else:
            self.thanSet(self.filnam, im, self.c1, self.c2, theta=0.0, transpose=self.transpose, clip=None, loaded=self.loaded)
        self.thanTkDraw(than)
        return 0, ""


    def thanLoad(self, than):
        "Redraw the raster on the canvas."
        self.loaded = True
        if not isinstance(self.image, p_gimage.ThanImageMissing): return 1, T["Image %s already loaded!"] % (self.filnam,)
        im, terr = imageOpen(self.filnam)
        if terr != "": return 2, "Invalid image or file %s:\n%s" % (self.filnam, terr)
#        try:
#            im = p_gimage.open(self.filnam)
#            if im.size[0] < 2 or im.size[1] < 2: raise ValueError, T["Image is probably corrupted: size is less than 2 pixels"]
#            im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised
#        except (IOError, ValueError), why:
#            return 2, "Invalid image or file %s:\n%s" % (self.filnam, why)
        than.dc.delete(self.thanTags[0])
        if self.clipped:
            self.thanSet(self.filnam, im, self.c1ori, self.c2ori, theta=0.0, transpose=self.transpose, clip=(self.c1, self.c2), loaded=self.loaded)
        else:
            self.thanSet(self.filnam, im, self.c1, self.c2, theta=0.0, transpose=self.transpose, clip=None, loaded=self.loaded)
        self.thanTkDraw(than)
        return 0, ""


    def thanTkDraw1(self, than):
        "Draws the image to a window."
        xymm = than.viewPort
        if self.c2[0] < xymm[0] or self.c1[0] > xymm[2] or self.c2[1] < xymm[1] or self.c1[1] > xymm[3]:
            #assert False, "Image is outside visible screen!"
            self.imagez = None
            than.thanImages.add(self)
            return
        xa, yb = than.ct.global2Locali(self.c1[0], self.c1[1])    # xa, ya is the upper left point of the image
        xb, ya = than.ct.global2Locali(self.c2[0], self.c2[1])    # xb, yb is the lower right point of the image
        if isinstance(self.image, p_gimage.ThanImageMissing):
            w = than.tkThick
            item1 = than.dc.create_rectangle(xa, yb, xb, ya, outline=than.outline, dash=than.dash, tags=self.thanTags, width=w)     # Frame around image
            than.thanImages.add(self)
            t = ThanText()
            h = (self.c2[0]-self.c1[0])/40.0
            n = len(self.filnam)
            ca = list(self.c1)
            ca[0] = (self.c1[0] + self.c2[0])*0.5 - n*h*0.5
            ca[1] = (self.c1[1] + self.c2[1])*0.5 - h*0.5
            t.thanSet(self.filnam, ca, h, self.theta)
            t.thanTags = self.thanTags
            t.thanTkDraw(than)
            return

        than.thanInfoPush(T["Regenerating %s.."] % (self.filnam,))
        wx = xb - xa + 1; wy = yb - ya + 1
        assert wx>=0 and wy>=0, "Something wrong with coordinates systems!!!"
        if wx*wy > 4000000:            # If less than 4Mpixels render the entire image
            self.view[0] = xn1 = max(self.c1[0], xymm[0])
            self.view[1] = yn1 = max(self.c1[1], xymm[1])
            self.view[2] = xn2 = min(self.c2[0], xymm[2])
            self.view[3] = yn2 = min(self.c2[1], xymm[3])
            for i,v in enumerate((self.c1[0], self.c1[1], self.c2[0], self.c2[1])):
                if self.view[i] == v: self.view[i] = None

            xp1, yp2 = self.thanGetPixCoor((xn1, yn1))
            xp2, yp1 = self.thanGetPixCoor((xn2, yn2))
            ca = self.__getWorldLowlef(xp1, yp2)
            cb = self.__getWorldLowlef(xp2, yp1)
            xa, yb = than.ct.global2Locali(ca[0], ca[1])
            xb, ya = than.ct.global2Locali(cb[0], cb[1])
            wx = xb - xa + 1
            wy = yb - ya + 1
            assert wx>=0 and wy>=0, "Something wrong with coordinates systems!!!"
            assert wx*wy <= 4000000, "Reduced (!!!) image too big: %.0f x %.0f" % (wx,wy) #This test may wrong if resolution is higher than 2000x2000
            self.imagez = self.image.crop((xp1, yp1, xp2, yp2))    # This is a lazy operation (i.e. very fast)
            self.imagez = _phresize(self.imagez, wx, wy, than.imageBrightness)
        else:
            if self.theta == 0.0: self.imagez = _phresize(self.image, wx, wy, than.imageBrightness)
            else:                 self.imagez = _phresize(self.image, wx, wy, than.imageBrightness)
            self.view = [None, None, None, None]

#        item2 = than.dc.create_image(xa, yb+1, image=self.imagez, anchor="sw", tags=self.thanTags)  #Thanasis2010_02_27:"sw" has a bug so that we put yb+1
        item2 = than.dc.create_image(xa, ya, image=self.imagez, anchor="nw", tags=self.thanTags)
        if than.imageFrameOn:
            w = than.tkThick
            item1 = than.dc.create_rectangle(xa, yb, xb, ya, outline=than.outline, dash=than.dash, tags=self.thanTags, width=w)     # Frame around image
        than.thanImages.add(self)
        than.thanInfoPop()

#===========================================================================

    def thanExpDxf(self, fDxf, level=12):
        "Exports the image to dxf file."
        if level == 12:
            cp = self.__boundaryLine()
            cp.append(cp[0])
            for c in cp:
                fDxf.thanDxfPlotPolyVertex3(c[0], c[1], c[2], 2)
            fDxf.thanDxfPlotPolyVertex3(0, 0, 0, 999)
            h = (self.c2[0]-self.c1[0])/40.0
            n = len(self.filnam)
            xa = (self.c1[0] + self.c2[0])*0.5
            ya = (self.c1[1] + self.c2[1])*0.5
            fDxf.thanDxfPlotSymbol(xa-n*h*0.5, ya-h*0.5, h, self.filnam, self.theta)
        else:
            wx = fabs(self.c2[0] - self.c1[0])
            wy = fabs(self.c2[1] - self.c2[1])
            dx, dy = self.size
            dx = min(wx/float(dx), wy/float(dy))
            fDxf.thanDxfPlotImage(self.filnam, self.c1[0], self.c1[1], self.size, dx, self.theta)


    def thanExpThc1(self, fw):
        "Save the aligned dimension in thcx format." #FIXME: what about clipped (or nonclipped) images
        f = fw.formFloat
        fw.writeln("%d" % (self.embedded,))
        if self.embedded:
            imbytes = p_gbmp.image2Bytes(self.image, format="jpeg")
            p_gbmp.writeBytesB64(imbytes, fw)
        fw.writeNode(self.c1)
        fw.writeNode(self.c2)
        fw.writeln(f % self.theta)
        fw.writeTextln(self.filnam)
        fw.writeln("%d %d" % self.size)
        fw.writeln("%d" % self.transpose)
        fw.writeNode(self.c1ori)
        fw.writeNode(self.c2ori)
        fw.writeln("%d" % (self.loaded,))


    def thanImpThc1(self, fr, ver, forceunload=False):
        "Read the aligned dimension from thc format."
        if ver < (0,2,1):
            embedded = False
        else:
            embedded = bool(int(next(fr)))  #May raise ValueError, IndexError, StopIteration
            if embedded:
                imbytes = p_gbmp.readBytesB64(fr)
                image = p_gbmp.bytes2Image(imbytes)
        c1 = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        c2 = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        theta = float(next(fr))          #May raise ValueError, StopIteration
        filnam = path(fr.readTextln()).expand() #May raise StopIteration, ValueError
        dxp, dyp = map(int, next(fr).split()) #May raise ValueError, IndexError, StopIteration  #works for python2,3
        transpose = int(next(fr))        #May raise ValueError, StopIteration
        c1ori = fr.readNode()            #May raise ValueError, IndexError, StopIteration
        c2ori  = fr.readNode()           #May raise ValueError, IndexError, StopIteration
        if ver <= (0,1,0):
            loaded = True
        else:
            loaded = bool(int(next(fr))) #May raise ValueError, IndexError, StopIteration

        if embedded:
            loaded = True                  #Embedded images can not be unloaded
        else:
            if forceunload: loaded = False
            if loaded:
                image, terr = imageOpen(filnam, (dxp, dyp))
            else:
                image = p_gimage.ThanImageMissing((dxp, dyp))

        clipped = c1 != c1ori or c2 != c2ori
        if clipped:
            self.thanSet(filnam, image, c1ori, c2ori, theta, transpose, (c1, c2), loaded, embedded)
        else:
            self.thanSet(filnam, image, c1ori, c2ori, theta, transpose, None, loaded, embedded)


    def thanExpSyk(self, than, level=0):
        "Exports the image to syk file."
        if level == 0: return
        cp = self.__boundaryLine()
        cp.append(cp[0])
        than.write("%15.3f  %s\n" % (self.c1[2], than.layname))
        for c in cp:
            than.write("%15.3f%15.3f\n" % (c[0], c[1]))
        than.write("$\n")


    def thanExpPil(self, than):
        "Exports the image to a PIL raster image."
        xymm = than.viewPort
        if self.c2[0] < xymm[0] or self.c1[0] > xymm[2] or self.c2[1] < xymm[1] or self.c1[1] > xymm[3]:
            return #Image is outside visible screen
        if not isinstance(self.image, p_gimage.ThanImageMissing):
            xn1 = max(self.c1[0], xymm[0])
            yn1 = max(self.c1[1], xymm[1])
            xn2 = min(self.c2[0], xymm[2])
            yn2 = min(self.c2[1], xymm[3])

            xa, yb = than.ct.global2Locali(xn1, yn1)    # xa, ya is the upper left point of the image
            xb, ya = than.ct.global2Locali(xn2, yn2)    # xb, yb is the lower  right point of the image
            wx = xb - xa; wy = yb - ya
            assert wx>=0 and wy>=0, "Something wrong with coordinates systems!!!"
            assert wx*wy <= 10000000, "Reduced (!!!) image too big: %.0f x %.0f" % (wx,wy)

            dxp, dyp = self.size
            xp1, yp2 = self.thanGetPixCoor([xn1, yn1])
            xp2, yp1 = self.thanGetPixCoor([xn2, yn2])

            imagez = self.image.crop((xp1, yp1, xp2, yp2))    # This is a lazy operation (i.e. very fast)
            imagez = _resize(imagez, wx, wy, than.imageBrightness)
            than.im.paste(imagez, (xa,ya,xb,yb))
        if than.imageFrameOn or isinstance(self.image, p_gimage.ThanImageMissing):
            cp = self.__boundaryLine()
            cp.append(cp[0])
            elem = ThanLine()
            elem.thanSet(cp)
            elem.thanExpPil(than)


    def thanTransform(self, fun):
        """Transform all the coordinates of the element according to 2D transformation function fun.

        The 2D transformation should also receive Z and return it unchanged.
        If the transformation is 3D, then the resulting Z is treated as an
        attribute, not as geometric property.
        Only the insertion point of the Image is changed."""
        if self.clipped:
            cp = [list(self.c1ori), list(self.c2ori), list(self.c1), list(self.c2)]
            for cc in cp: cc[:3] = fun(cc[:3])
            self.thanSet(self.filnam, self.imageori, cp[0], cp[1], theta=0.0,
                transpose=self.transpose, clip=(cp[2], cp[3]), loaded=self.loaded)
        else:
            cp = [list(self.c1), list(self.c2)]
            for cc in cp: cc[:3] = fun(cc[:3])
            self.thanSet(self.filnam, self.image, cp[0], cp[1], theta=0.0,
                transpose=self.transpose, clip=None, loaded=self.loaded)


    def thanList(self, than):
        "Shows information about the image element."
        than.writecom("%s: %s" % (T["Element"], self.thanElementName))
        than.write("    %s %s\n" % (T["Layer:"], thanUnicode(than.laypath)))
        than.write("%s: %s    %s: %s\n" % (T["Length"], than.strdis(self.thanLength()), T["Area"], than.strdis(self.thanArea())))
        s = ""
        if self.embedded: s = T["    (embedded)"]
        if not self.loaded: s = T["    (unloaded)"]
        t = [T["Image filename: %s%s"] % (self.filnam, s)]
        t.append(T["Image size: %dx%d"] % self.size)
        if self.clipped:
            t.append(T["Rectangular clip: %s"] % than.strcoo(self.c1))
            t.append(  "                  %s"  % than.strcoo(self.c2))
            t.append(T["Original image  : %s"] % than.strcoo(self.c1ori))
            t.append(  "                  %s"  % than.strcoo(self.c2ori))
        else:
            t.append(T["Bounding box: %s"] % than.strcoo(self.c1))
            t.append(  "              %s"  % than.strcoo(self.c2))
        t.append(T["Angle (not used): %s"] % than.strdir(self.theta))
        t.append("%s: %d deg\n" % (T["Integer rotation"], self.transpose*90))
        than.write("\n".join(t))


#===========================================================================

    def thanGetPixCol(self, cw):
        "Finds the color of the pixel of the image that corresponds to the world coordinates xw, yw."
        return self.image.getpixel(self.thanGetPixCoor(cw))


    def __getitem__(self, ji):
        "Returns True if the pixel at ji is black (or less than a threshhold value non-b/w images)."
        return self.image.getpixel(ji) < 127


    def thanGetPixCoor(self, cw):
        """Finds the image pixel coordinates that corresponds to the world coordinates xw, yw.

                        c2   c2 are the world coordinates of the upper right corner of the upper right pixel (B)
        o---o---o---o---o    c1 are the world coordinates of the lower left corner of the lower left pixel (A)
        |   |   |   | B |    The size of the image in world coordinates: dx, dy = c2[0]-c1[0], c2[1]-c1[1]
        o---o---o---o---o    The size of the image in pixels is the size of the raster (here dxp, dyp = 4, 3)
        |   |   |   |   |    If x coordinate of the point cw (cw[0]) coincides with c2[0], or is just to the
        o---o---o---o---o        right of it (for numerical reasons), then we assume that it is inside the
        | A |   |   |   |        rightmost pixel column: j = dxp-1
        o---o---o---o---o    If cw[0] coincides with c1[0], or is just to the left of it, then we assume that
        c1                       it is in the leftmost pixel column.
                             Othwewise we find the pixel coor using ratios (dx corresponds to dxp, 4 pixels
                                 in this example. Then we if we find 0.1 or o.5 or 0.9 this point belongs to the
                                 0th pixel column and thus we take the int() of this real number.
                             Likewise for the y coordinate cw[1].
        """
        terr = "World coordinates do not correspond to image."
        dxp, dyp = self.size
        dx, dy = self.c2[0]-self.c1[0], self.c2[1]-self.c1[1]
        j = (cw[0]-self.c1[0]) / dx * dxp
        if j >= dxp:
            if j > dxp+0.01: raise IndexError(terr)
            j = dxp-1
        elif j < 0.0:
            if j < -0.01:    raise IndexError(terr)
            j = 0
        else:
            j = int(j)
        i = (self.c2[1]-cw[1]) / dy * dyp
        if i >= dyp:
            if i > dyp+0.01: raise IndexError(terr)
            i = dyp-1
        elif i < 0.0:
            if i < -0.01: raise IndexError(terr)
            i = 0
        else:
            i = int(i)
        return j, i


    def thanGetWorldCoor(self, jx, iy, celev=None):
        "Finds the the world coordinates that corresponds to the image pixel coordinates xp, yp."
        dxp, dyp = self.size
        if jx<0 or iy<0 or jx>dxp-1 or iy>dyp-1:
            raise IndexError("Pixel coordinates do not correspond to image")
        dx, dy = self.c2[0]-self.c1[0], self.c2[1]-self.c1[1]
        if celev is None: cw = list(self.c1)
        else:             cw = list(celev)
        cw[0] = self.c1[0] + (jx+0.5)*dx/dxp
        cw[1] = self.c2[1] - (iy+0.5)*dy/dyp
        return cw


    def __getWorldLowlef(self, jx, iy, celev=None):
        "Finds the world coordinates of the lower left corner of the pixel which corrresponds to image pixel coordinates xp, yp."
        dxp, dyp = self.size
        if jx<0 or iy<0 or jx>dxp-1 or iy>dyp-1:
            raise IndexError("Pixel coordinates do not correspond to image")
        dx, dy = self.c2[0]-self.c1[0], self.c2[1]-self.c1[1]
        if celev is None: cw = list(self.c1)
        else:             cw = list(celev)
        cw[0] = self.c1[0] + (jx+0.0)*dx/dxp
#        cw[1] = self.c2[1] - (iy+1.0)*dy/dyp
        cw[1] = self.c2[1] - (iy+0.0)*dy/dyp
        return cw


    def thanGetPixCoorori(self, cw):
        "Finds the image pixel coordinates that corresponds to the world coordinates xw, yw."
        terr = "World coordinates do not correspond to image."
        dxp, dyp = self.imageori.size
        dx, dy = self.c2ori[0]-self.c1ori[0], self.c2ori[1]-self.c1ori[1]
        j = (cw[0]-self.c1ori[0]) / dx * dxp
        if j >= dxp:
            if j > dxp+0.01: raise IndexError(terr)
            j = dxp-1
        elif j < 0.0:
            if j < -0.01:    raise IndexError(terr)
            j = 0
        else:
            j = int(j)
        i = (self.c2ori[1]-cw[1]) / dy * dyp
        if i >= dyp:
            if i > dyp+0.01: raise IndexError(terr)
            i = dyp-1
        elif i < 0.0:
            if i < -0.01: raise IndexError(terr)
            i = 0
        else:
            i = int(i)
        return j, i


    def thanGetWorldCoorori(self, jx, iy, celev=None):
        "Finds the the world coordinates that corresponds to the image pixel coordinates xp, yp."
        dxp, dyp = self.imageori.size
        if jx<0 or iy<0 or jx>dxp-1 or iy>dyp-1:
            raise IndexError("Pixel coordinates do not correspond to image")
        dx, dy = self.c2ori[0]-self.c1ori[0], self.c2ori[1]-self.c1ori[1]
        if celev is None: cw = list(self.c1ori)
        else:             cw = list(celev)
        cw[0] = self.c1ori[0] + (jx+0.5)*dx/dxp
        cw[1] = self.c2ori[1] - (iy+0.5)*dy/dyp
        return cw


def _phresize(im, wx, wy, brfact):
    "Resizes image using the appropriate filter, brightens/darkens and converts to Tkinter image."
    b, h = im.size
    if wx < b: im1 = im.resize((wx, wy), _filterDown)
    else:      im1 = im.resize((wx, wy), _filterUp)
    if fabs(brfact-1.0) > 0.01:
        gen = p_gimage.Brightness(im1)
        im1 = gen.enhance(brfact)
        del gen
    return p_gimage.PhotoImage(im1)


def _resize(im, wx, wy, brfact):
    "Resizes image using the appropriate filter and then brightens/darkens."
    b, h = im.size
    if wx < b: im1 = im.resize((wx, wy), _filterDown)
    else:      im1 = im.resize((wx, wy), _filterUp)
    if fabs(brfact-1.0) > 0.01:
        gen = p_gimage.Brightness(im1)
        im1 = gen.enhance(brfact)
        del gen
    return im1


def thanSetRendering(mode):
    "Set rendering mode of images: 0=quick or 1=best."
    global _filterDown, _filterUp
    if mode == 0:
        _filterDown = p_gimage.NEAREST
        _filterUp   = p_gimage.NEAREST
    else:
        _filterDown = p_gimage.ANTIALIAS
        _filterUp   = p_gimage.BICUBIC


def thanGetRendering():
    "Return current mode of rendering of images."
    if _filterDown == p_gimage.NEAREST: return 0
    return 1


thanSetRendering(0)     # Quick rendering of images
