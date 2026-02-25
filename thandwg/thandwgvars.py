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

This module defines the variables and objects of a ThanCad drawing.
"""

from thanobj import thanObjClass
from thantrans import T


def thanVarsExpThc(fw, thanVar, ver):
    "Export the variable to thc format."
    sec = "VARIABLES"
    fw.writeBeg(sec)
    fw.pushInd()
    v = thanVar
    f = fw.formFloat
    k = "dimensionality"; fw.writeAtt(k, v[k])              # Number of dimensions a node has
    n = v[k]
    k = "elevation"  ;   fw.writeAtt(k, (f*n) % tuple(v[k]))  # Elevation - limited n-dimensional support
    k = "elevationstep"; fw.writeAtt(k, (f*n) % tuple(v[k]))  # Elevation - limited n-dimensional support
    k = "thickness"  ;   fw.writeAtt(k, (f*n) % tuple(v[k]))  # Thickness - limited n-dimensional support
    k = "insbase"    ;   fw.writeAtt(k, (f*n) % tuple(v[k]))  # Insertion point of the drawing (as block)
    k = "imageframe" ;   fw.writeAtt(k, "%d" % v[k])          # If false, the bounding rectangles of images are not displayed
    k = "useroffsetdistance" ; fw.writeAtt(k, f % v[k])       # Default distance for the offset command
    k = "useroffsetthrough"  ; fw.writeAtt(k, "%d" % v[k])    # Default offset mode is "through"
    k = "fillmode"  ;    fw.writeAtt(k, "%d" % v[k])          # Default fillmode is True
    fw.popInd()
    fw.writeEnd(sec)


def thanVarsImpThc(fr, ver):
    "Read the arc from thc format."
    thanVar = {}
    sec = "VARIABLES"
    fr.readBeg(sec)                                    #May raise ValueError, StopIteration
    k = "dimensionality"; thanVar[k] = int(fr.readAtt(k)[0])   #May raise StopIteration, ValueError
    n = thanVar[k]
    if n < 2: raise ValueError("%s must be at least 2" % (k, n))
    c = [0.0]*n
    for k in "elevation", "elevationstep", "thickness", "insbase":
        if k == "elevationstep" and ver <= (0,1,0):
            thanVar[k] = [1.0]*n
            continue
        thanVar[k] = list(map(float, fr.readAtt(k)))  #May raise StopIteration, ValueError  #works for python2,3
        nt = len(thanVar[k])
        if nt < 2: raise ValueError("%s must have at least %d dimensions" % (k, n))
        if nt >= n: thanVar[k] = thanVar[k][:n]
        else:       thanVar[k] += c[nt:]
    fr.setElev(thanVar["elevation"])
    k = "imageframe"; thanVar[k] = bool(fr.readAtt(k)[0])          #May raise StopIteration, ValueError
    k = "useroffsetdistance"; thanVar[k] = float(fr.readAtt(k)[0]) #May raise StopIteration, ValueError
    k = "useroffsetthrough";  thanVar[k] = bool(fr.readAtt(k)[0])  #May raise StopIteration, ValueError

    k = "fillmode"
    if (ver >= (0,5,0)): thanVar[k] = bool(int(fr.readAtt(k)[0]))  #May raise StopIteration, ValueError
    else:                thanVar[k] = True  #set default fillmode for older versions of thcx files
    fr.readEnd(sec) #May raise ValueError, StopIteration
    return thanVar


def thanVarsDef(thanVar=None):
    "Set default values to ThanCad variables or repair old drawing."
    if thanVar is None: thanVar = {}
    n = thanVar.setdefault("dimensionality",  3)    # Number of dimensions a node has
    thanVar.setdefault("elevation",    [0.0]*n)     # Elevation - limited n-dimensional support
    thanVar.setdefault("elevationstep",[1.0]*n)     # Elevation step - limited n-dimensional support
    thanVar.setdefault("thickness",    [0.0]*n)     # Thickness - limited n-dimensional support
    thanVar.setdefault("insbase",      [0.0]*n)     # Insertion point of the drawing (as block)
    thanVar.setdefault("imageframe",   True)        # If false, the bounding rectangles of images are not displayed
    thanVar.setdefault("useroffsetdistance",  1.0)  # Default distance for the offset command
    thanVar.setdefault("useroffsetthrough",   True) # Default offset mode is "through"
    thanVar.setdefault("fillmode",     True)        # Specifies whether hatches and fills, 2D solids, and wide polylines are filled in.Default fillmode is to fill solids
    return thanVar


def thanObjsDef(thanObjects=None):
    "Set default values to ThanCad objects or repair old drawing."
    if thanObjects is None: thanObjects = {}
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
    for objs in thanObjects.values():   #works for python2,3
        for obj in objs:
            #print "object=", obj, "name=", obj.thanObjectName
            obj.thanExpThc(fw)
    fw.popInd()
    fw.writeEnd(sec)


def thanObjsImpThc(fr, thanObjects, than):
    "Read the arc from thc format."
    sec = "OBJECTS"
    fr.readBeg(sec)                                    #May raise ValueError, StopIteration
    tend = "</" + sec + ">"
    while True:
        dline = next(fr).strip()
        if dline == tend: return
        name = dline[1:-1]
        clas = thanObjClass.get(name, None)
        if clas is None:
            fr.prter(T['Uknkown object "%s" is skipped'] % (name, ))
            te = "</" + name + ">"
            while True:
                dline = next(fr).strip()
                if dline == tend: return
                if dline == te: break
            continue
        fr.unread()
        obj = clas()
        terr = None
        try:
            obj.thanImpThc(fr, than)
        except (ValueError, IndexError) as why:
            terr = str(why)
        if terr is not None:
            fr.prter(T['Error while reading object "%s":\n%s\nObject is skipped'] % (name, terr))
            te = "</" + name + ">"
            while True:
                dline = next(fr).strip()
                if dline == tend: return
                if dline == te: break
            continue
        if len(thanObjects[name]) > 0:
            if name not in ("DTMLINES", "DEMUSGS"):
                fr.prter(T['Object "%s" was found again. The last is kept.'] % (name,))
                del thanObjects[name][:]
        thanObjects[name].append(obj)


if __name__ == "__main__":
    print(__doc__)
