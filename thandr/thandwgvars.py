##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module defines the variables and objects of a ThanCad drawing.
"""

from thanobject import thanObjClass
from thantrans import T


def thanVarsExpThc(fw, thanVar):
    "Export the variable to thc format."
    sec = "VARIABLES"
    fw.writeBeg(sec)
    fw.pushInd()
    v = thanVar
    f = fw.formFloat
    k = "dimensionality"; fw.writeAtt(k, v[k])              # Number of dimensions a node has
    n = v[k]
    k = "elevation"  ; fw.writeAtt(k, (f*n) % tuple(v[k]))  # Elevation - limited n-dimensional support
    k = "thickness"  ; fw.writeAtt(k, (f*n) % tuple(v[k]))  # Thickness - limited n-dimensional support
    k = "insbase"    ; fw.writeAtt(k, (f*n) % tuple(v[k]))  # Insertion point of the drawing (as block)
    k = "imageframe" ; fw.writeAtt(k, "%d" % v[k])          # If false, the bounding rectangles of images are not displayed
    k = "useroffsetdistance" ; fw.writeAtt(k, f % v[k])     # Default distance for the offset command
    k = "useroffsetthrough"  ; fw.writeAtt(k, "%d" % v[k])  # Default offset mode is "through"
    fw.popInd()
    fw.writeEnd(sec)


def thanVarsImpThc(fr):
    "Read the arc from thc format."
    thanVar = {}
    sec = "VARIABLES"
    fr.readBeg(sec)                                    #May raise ValueError, StopIteration
    k = "dimensionality"; thanVar[k] = int(fr.readAtt(k)[0])   #May raise StopIteration, ValueError
    n = thanVar[k]
    if n < 2: raise ValueError, "%s must be at least 2" % (k, n)
    c = [0.0]*n
    for k in "elevation", "thickness", "insbase":
        thanVar[k] = map(float, fr.readAtt(k))  #May raise StopIteration, ValueError
        nt = len(thanVar[k])
        if nt < 2: raise ValueError, "%s must have at least %d dimensions" % (k, n)
        if nt >= n: thanVar[k] = thanVar[k][:n]
        else:       thanVar[k] += c[nt:]
    fr.setElev(thanVar["elevation"])
    k = "imageframe"; thanVar[k] = bool(fr.readAtt(k)[0])          #May raise StopIteration, ValueError
    k = "useroffsetdistance"; thanVar[k] = float(fr.readAtt(k)[0]) #May raise StopIteration, ValueError
    k = "useroffsetthrough";  thanVar[k] = bool(fr.readAtt(k)[0])  #May raise StopIteration, ValueError
    fr.readEnd(sec) #May raise ValueError, StopIteration
    return thanVar


def thanVarsDef(thanVar=None):
    "Set default values to ThanCad variables or repair old drawing."
    if thanVar == None: thanVar = {}
    n = thanVar.setdefault("dimensionality",  3)    # Number of dimensions a node has
    thanVar.setdefault("elevation",   [0.0]*n)      # Elevation - limited n-dimensional support
    thanVar.setdefault("thickness",   [0.0]*n)      # Thickness - limited n-dimensional support
    thanVar.setdefault("insbase",     [0.0]*n)      # Insertion point of the drawing (as block)
    thanVar.setdefault("imageframe", True)          # If false, the bounding rectangles of images are not displayed
    thanVar.setdefault("useroffsetdistance",  1.0)  # Default distance for the offset command
    thanVar.setdefault("useroffsetthrough",   True) # Default offset mode is "through"
    return thanVar


def thanObjsDef(thanObjects=None):
    "Set default values to ThanCad objects or repair old drawing."
    if thanObjects == None: thanObjects = {}
    for name in thanObjClass:
        thanObjects.setdefault(name, [])
#    thanObjects.setdefault(    "DTMLINES",      None)  #"Set of 3D lines which behaves as a Digital Terrain Model."
#    thanObjects.setdefault("TRIANGULATION", None)  #"A nonconvex triangulation."
#    thanObjects.setdefault("FLOORPLAN",     None)  #"Automated floor plan."
#    thanObjects.setdefault("COSYS",         None)  #"(Non) cartesian coordinate system in 2D."
#    thanObjects.setdefault("PHOTMODEL",     None)  #"Optical photogrammetric model."
#    thanObjects.setdefault("PHOTINTERIOR",  None)  #"Optical photogrammetric interior orientation."
#    thanObjects.setdefault("TRANSFORMATION",None)  #"Transformation between (3D) coordinate systems."
#    thanObjects.setdefault("PROJECTION",    None)  #"Projection of 3D to 2D coordinate system."
#    thanObjects.setdefault("BIOCITYPLAN",   None)  #"Automated east-west oriented city plan."
#    thanObjects.setdefault("LINESIMPLIFICATION", None)  #"Reduce points of lines keeping the error controlled."

    bcps = thanObjects["BIOCITYPLAN"]
    if len(bcps) > 0:
        bcps[0].pc.pol.changed = 0
    return thanObjects


def thanObjsExpThc(fw, thanObjects):
    "Export the objects to thc format."
    sec = "OBJECTS"
    fw.writeBeg(sec)
    fw.pushInd()
    for objs in thanObjects.itervalues():
        for obj in objs:
            print "object=", obj, "name=", obj.thanObjectName
            obj.thanExpThc(fw)
    fw.popInd()
    fw.writeEnd(sec)


def thanObjsImpThc(fr, thanObjects):
    "Read the arc from thc format."
    sec = "OBJECTS"
    fr.readBeg(sec)                                    #May raise ValueError, StopIteration
    tend = "</" + sec + ">"
    while True:
        dline = fr.next().strip()
        if dline == tend: return
        name = dline[1:-1]
        clas = thanObjClass.get(name, None)
        if clas == None:
            fr.prter(T['Uknkown object "%s" is skipped'] % (name, ))
            te = "</" + name + ">"
            while True:
                dline = fr.next().strip()
                if dline == tend: return
                if dline == te: break
            continue
        fr.unread()
        obj = clas()
        ok = True
        try:
            obj.thanImpThc(fr)
        except (ValueError, IndexError), why:
            ok = False
        if not ok:
            fr.prter(T['Error while reading object "%s":\n%s\nObject is skipped'] % (name, why))
            te = "</" + name + ">"
            while True:
                dline = fr.next().strip()
                if dline == tend: return
                if dline == te: break
            continue
        if len(thanObjects[name]) > 0:
            if name not in ("DTMLINES", "DEMUSGS"):
                fr.prter(T['Object "%s" was found again. The last is kept.'] % (name,))
                del thanObjects[name][:]
        thanObjects[name].append(obj)


if __name__ == "__main__":
    print __doc__
