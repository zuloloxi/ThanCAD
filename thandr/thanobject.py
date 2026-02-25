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

This module defines the generic ThanCad object. A ThanCad object is an element
without graphical representation, such as DTM, It can be also used as a null
element - this is NOT an asbtract class.
"""

import copy
import Image
import p_ggen, p_gtri, p_gmath, p_grun
from thantrans import T, Tarch, Tmatch
import thanimp, thansupport, thanopt



class ThanObject(object):
    """Base class for thancad's objects.

    This class of elements may ne used whenever a dummy, or Null element
    (see python recipies), is needed. The element accepts usual commands through
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
            raise ValueError, "Unknown thc version of object %s: %s" % (self.thanObjectName, self.thanThcVersion)
        self.thanImpThc1(fr, ver)
        fr.readEnd(self.thanObjectName)


    def thanExpThc1(self, fw):
        "Save the object to a .thc file."
        fw.prter('Object "%s" was not saved (save not implemented)' % (self.thanObjectName,))


    def thanImpThc1(self, fr, ver):
        "Read the object from a .thc file."
        raise ValueError, 'Object "%s" can not be read (read not implemented)' % (self.thanObjectName,)


    def thanClone(self):
        "Makes a copy of itself; the cloned copy must have different thanTags."
        el = copy.deepcopy(self)
        return el



class ThanDTMlines(ThanObject):
    thanObjectName = "DTMLINES"    # Name of the objects's class
    thanObjectInfo = "Set of 3D lines which behaves as a Digital Terrain Model."
    thanVersions = ("1.0",)

    def __init__(self, dxmax=20.0, dext=50.0):
        "Initialize DEM."
        self.dtm = p_gtri.ThanDTMlines(dxmax, dext)


    def thanIsNormal(self):
        "Returns False if the image the DEM was not found."
        return True           #for compatibility with thanDEMusgs

    def thanList(self, than):
        "Shows information about the DTMLines object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        scen = " ".join(map(than.strdis, self.dtm.thanCen()))
        than.write("%s %s\n" % (T["Centroid:"], scen))
        than.write("%s %s\n" % (T["Max X distance of line segments:"], than.strdis(self.dtm.thanDxmax)))
        than.write("%s %s\n" % (T["X extension for intersections  :"], than.strdis(self.dtm.thanDext)))
        than.write("%s %d\n" % (T["Original  line segments: "], self.dtm.thanNori))
        than.write("%s %d\n" % (T["Processed line segments: "], len(self.dtm.thanLines)))

    def thanExpThc1(self, fw):
        "Saves the lines of the DTM to a .thc file."
        self.dtm.thanExpThc1(fw)

    def thanImpThc1(self, fr, ver):
        "Reads the lines of the DTM from a .thc file."
        self.dtm.thanImpThc1(fr, ver)


class ThanDEMusgs(ThanObject):
    thanObjectName = "DEMUSGS"    # Name of the objects's class
    thanObjectInfo = "DEM stores in TIF files (USGS format)."
    thanVersions = ("1.0",)

    def __init__(self):
        "Some initial values to make the object variables clear."
        self.dtm = p_gtri.ThanDEMusgs()


    def thanList(self, than):
        "Shows information about the DEMusgs object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %s\n" % (T["TIF filename:"], self.dtm.filnam))
        if self.dtm.im == "GDEM": return
        if self.thanIsNormal():
            scen = " ".join(map(than.strdis, self.dtm.thanCen()))
            than.write("%s %s\n" % (T["Centroid:"], scen))
            ca = list(than.elevation)
            ca[:2] = self.dtm.X0, self.dtm.Y0
            than.write("%s %s\n" % (T["Upper left corner:"], than.strcoo(ca)))
            than.write("%s %s %s\n" % (T["X and Y distance between DEM points :"], than.strdis(self.dtm.DX), than.strdis(self.dtm.DY)))
        else:
            than.write(T["Invalid tif image or image not found.\n"])

    def thanIsNormal(self):
        "Returns False if the image the DEM was not found."
        return self.dtm.im != None

    def thanExpThc1(self, fw):
        "Saves the name of the tif which contains the USGS DEM."
        fw.writeAtt("TIF", self.dtm.filnam)

    def thanImpThc1(self, fr, ver):
        "Reads the name of the tif which contains the USGS DEM, and loads it."
        self.filnam = fr.readAtt("TIF")[0]
        if self.filnam.startswith("%%%") and self.filnam.endswith("%%%"):
            import p_gearth
            self.dtm = p_gearth.gdem(self.filnam)   #May raise ValueError
            return
        try:
            im = Image.open(self.filnam)
            dxp, dyp = im.size
            if dxp < 2 or dyp < 2: raise ValueError, T["Image is probably corrupted: size is less than 2 pixels"]
            im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised
            self.dtm.thanSet(self.filnam, im)  #This will raise ValueError is something is wrong
        except (IOError, ValueError), why:
            fr.prter("Invalid/missing TIF in while reading %s: %s:\n%s" % (self.thanObjectName, self.filnam, why))
            self.dtm.im = None


class ThanTri(p_gtri.ThanTri, ThanObject):
    thanObjectName = "TRIANGULATION"    # Name of the objects's class
    thanObjectInfo = "A nonconvex triangulation."
    thanVersions = ("1.0",)

    def thanList(self, than):
        "Shows information about the Triangulation object."
        n = 0
        for _ in self.itertriangles(): n += 1
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %d\n" % (T["Processed points: "], len(self.ls)))
        than.write("%s %d\n" % (T["Triangles       : "], n))


class ThanFplan(ThanObject):
    thanObjectName = "FLOORPLAN"    # Name of the objects's class
    thanObjectInfo = "Automated floor plan."
    thanVersions = ("1.0",)

    def __init__(self):
        "Set initial values to the floorplan origin."
        self.xor = self.yor = 0.0

    def run(self, proj, v):
        "Run the automatic floor plan design algorithm."
        import thanpackages.fplan
        thanpackages.fplan.simroom.thancadMain(proj, v, self.xor, self.yor)
        self.xor += v.entWidth*1.20
        if self.xor > 3.01*1.20*v.entWidth:
            self.xor = 0.0
            self.yor -= v.entHeight*1.2

    def thanList(self, than):
        "Shows information about the FloorPlan object."
        c = list(than.elevation)
        c[:2] = self.xor, self.yor
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %s\n" % (Tarch["Next floor plan position:"], than.strcoo(c)))

    def thanExpThc1(self, fw):
        "Saves the origin of the next floor plan to a .thc file."
        fw.writeBeg("origin")
        fw.pushInd()
        fw.writeNode((self.xor, self.yor))
        fw.popInd()
        fw.writeEnd("origin")

    def thanImpThc1(self, fr, ver):
        "Reads the origin of the next floor plan from a .thc file."
        fr.readBeg("origin")
        cp = fr.readNode()
        self.xor, self.yor = cp[:2]
        fr.readEnd("origin")


class NonCartesian(p_gmath.NonCartesian, ThanObject):
    thanObjectName = "COSYS"    # Name of the objects's class
    thanObjectInfo = "(Non) cartesian coordinate system in 2D."
    thanVersions = ("1.0",)

    def thanList(self, than):
        "Shows information about the coordinate-system object."
        cor = list(than.elevation)
        cor[:2] = self.L[:2]
        cx = list(cor)
        cx[:2] = self.L[2:4]
        cy = list(cor)
        cy[:2] = self.L[4:]
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %s\n" % (T["Origin of X,Y axes: "], than.strcoo(cor)))
        than.write("%s %s\n" % (T["X-axis unit vector: "], than.strcoo(cx)))
        than.write("%s %s\n" % (T["Y-axis unit vector: "], than.strcoo(cy)))

    def thanExpThc1(self, fw):
        "Saves the coordinate system to a .thc file."
        for i,att in enumerate("origin unitx unity".split()):
            fw.writeBeg(att)
            fw.pushInd()
            fw.writeNode(self.L[i*2:i*2+2])
            fw.popInd()
            fw.writeEnd(att)

    def thanImpThc1(self, fr, ver):
        "Reads the coordinate system from a .thc file."
        for i,att in enumerate("origin unitx unity".split()):
            fr.readBeg(att)
            cp = fr.readNode()
            self.L[i*2:i*2+2] = cp[:2]
            fr.readEnd(att)


class LineSimplification(ThanObject):
    thanObjectName = "LINESIMPLIFICATION"    # Name of the objects's class
    thanObjectInfo = "Simplification of line."
    thanVersions = ("1.0",)
    atts  = "entXYmean entXY entZ choKeep".split()

    def __init__(self):
        "Set default attributes of simplification."
        self.entXYmean = 0.15
        self.entXY     = 0.20
        self.entZ      = 0.10
        self.choKeep   = True

    def toDialog(self):
        "Return the data in a form needed by ThanSimplificationSettings dialog."
        v = p_ggen.Struct("Line simplification settings")
        for att in self.atts:
            setattr(v, att, getattr(self, att))
        return v

    def fromDialog(self, v):
        "Get the data from ThanSimplificationSettings dialog."
        for att in self.atts:
            setattr(self, att, getattr(v, att))

    def thanList(self, than):
        "Shows line simplification settings."
        yn = "No", "Yes"
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s: %s\n" % (T["Tolerance of mean xy error"], than.strdis(self.entXYmean)))
        than.write("%s: %s\n" % (T["Tolerance of individual xy error"], than.strdis(self.entXY)))
        than.write("%s: %s\n" % (T["Tolerance of individual z error"], than.strdis(self.entZ)))
        than.write("%s: %s\n" % (T["Keep original lines after simplification"], T[yn[self.choKeep]]))

    def thanExpThc1(self, fw):
        "Saves the simplification settings to a .thc file."
        f = fw.formFloat
        fw.writeAtt("entXYmean", f    % (self.entXYmean,))
        fw.writeAtt("entXY",     f    % (self.entXY,))
        fw.writeAtt("entZ",      f    % (self.entZ,))
        fw.writeAtt("choKeep",   "%d" % (self.choKeep,))

    def thanImpThc1(self, fr, ver):
        "Reads the simplification settings from a .thc file."
        self.entXYmean = float(fr.readAtt("entXYmean")[0])
        self.entXY     = float(fr.readAtt("entXY")[0])
        self.entZ      = float(fr.readAtt("entZ")[0])
        self.choKeep   = bool(int(fr.readAtt("choKeep")[0]))


class ThanPhot(ThanObject):
    "An object which stores photogrannetric data."
    thanObjectName = "PHOTMODEL"    # Name of the objects's class
    thanObjectInfo = "Optical photogrammetric model."
    thanVersions = ("1.0",)

    def __init__(self, model=None):
        "Create an initialised or empty model."
        from thanopt.thancadconf import thanUndefPrefix     #"<undefined>"
        if model == None:
            self.model = None
        else:
            m = self.model = p_ggen.Struct("Photogrammetric model")
            m.nam      = thanUndefPrefix
            m.desc     = ""
            m.filLeft  = thanUndefPrefix
            m.filRight = thanUndefPrefix

    def model2dialog(self):
        "Create a structure with model attributes expected by ThanCad's dialog."
        v = p_ggen.Struct()
        m = self.model
        v.entName  = m.nam
        v.entDesc  = m.desc
        v.filLeft  = m.filLeft
        v.filRight = m.filRight

    def thanList(self, than):
        "Shows information about the photogrammetric model object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        m = self.model
        than.write("%s %s\n" % (T["Model name       : "], m.nam))
        than.write("%s %s\n" % (T["Model description: "], m.desc))
        than.write("%s %s\n" % (T["Left  image: "], m.filLeft))
        than.write("%s %s\n" % (T["Right image: "], m.filRight))


class ThanPhotInterior(ThanObject):
    "An object which stores photogrannetric interior orentation data."
    thanObjectName = "PHOTINTERIOR"    # Name of the objects's class
    thanObjectInfo = "Optical photogrammetric interior orientation."
    thanVersions = ("1.0",)

    def __init__(self, camera=None):
        "Create an initialised or empty model."
        self.image = None
        self.camera = None
        self.fids = ()
        self.tra = p_gmath.Polynomial1_2DProjection()  #First order Poynomial: affine transform: Identity: x = X, y = Y


    def replacePoints(self, proj, lay):
        """Delete and return old points in layer lay and create and return new points at the fiducials.

        It is assumed that the caller has already called thanTkSet."""
        import thandr
        cam = self.camera
        assert cam != None
        n = len(cam.x)
        delelems = lay.thanQuad.copy()
        proj[1].thanElementDelete(delelems, proj)
        elev = proj[1].thanVar["elevation"]
        newelems = {}
        for ifid in xrange(len(cam.x)):
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
        self.fids = [["", "", False] for i in xrange(n)]


    def getImage(self): return self.image
    def setImage(self, image): self.image = image


    def toDialog(self):
        "Return the data in a form needed by ThanInterior dialog."
        cam = self.camera
        assert cam != None
        v = p_ggen.Struct()
        n = len(cam.x)
        for ifid in xrange(1, n+1):
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
        for ifid in xrange(1, n+1):
            xp = getattr(v, "labXpix%d" % ifid)
            yp = getattr(v, "labYpix%d" % ifid)
            rej = getattr(v, "thanChkReject%d" % ifid)
            self.fids[ifid-1][:] = xp, yp, rej
        self.tra = other.tra


    def thanList(self, than):
        "Shows information about the photogrammetric model object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        if self.camera != None:
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
        if self.tra != None:
            than.write("Affine transformation x: %15.6f%15.6f%15.6f\n" % tuple(self.tra.L[:3]))
            than.write("                      y: %15.6f%15.6f%15.6f\n" % tuple(self.tra.L[3:6]))


#    v.name: camera name as string
#    v.x[], v.y[]: coordinates of fiducials as floats.
    def thanExpThc1(self, fw):
        "Saves the photogrammetric interior orientation attributes to a .thc file."
        f = fw.formFloat
        if self.image == None:  fw.writeAtt("image", "_NONE_")
        else:                   fw.writeAtt("image", "%d" % self.image.handle)

        fw.writeBeg("camera")
        fw.pushInd()
        if self.camera == None:
            fw.writeAtt("name", "_NONE_")
        else:
            fw.writeAtt("name", self.camera.name)
            fw.writeNodes(zip(self.camera.x, self.camera.y))
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


    def thanImpThc1(self, fr, ver):
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


class ThanTransformation(ThanObject):
    thanObjectName = "TRANSFORMATION"    # Name of the objects's class
    thanObjectInfo = "Transformation between (3D) coordinate systems."
    thanVersions = ("1.0",)

    def __init__(self, transformation=None):
        "Obtain the transformartion object."
        if transformation == None: self.transformation = p_gmath.Polynomial1Projection()  # Identity: x = X, y = Y
        else:                      self.transformation = transformation
        self.inverted = None

    def transform(self, cor):
        "Transform the coordinates of a point."
        return None

    def transformn(self, corn):
        "Transform the coordinates of many points."
        return None

    def invert(self):
        "Compute the inverted transformation, save it and return it."
        return None #Return None if transformation can not be inverted, or inversion not implemented

    def invtransform(self, cta):
        "Invert the coordinates of a transformed point to get the original."
        return None

    def invtransformn(self, ctan):
        "Invert the coordinates of many transformed points to get the original."
        return None


if thanopt.thancon.thanFrape.fflf:
    from p_gsar import readProj
else:
    from p_gmath import readProj

class ThanProjection(ThanTransformation):
    thanObjectName = "PROJECTION"    # Name of the objects's class
    thanObjectInfo = "Projection of 3D to 2D coordinate system."
    thanVersions = ("1.0",)

    def transform(self, cor):
        "Transform the coordinates of a point."
        tra = self.transformation
        return tra.project(cor)

    def transformn(self, corn):
        "Transform the coordinates of many points."
        tra = self.transformation
        pr = tra.project
        return [pr(cor) for cor in corn]

    def thanList(self, than):
        "Shows information about the transformation object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s: %s\n" % (Tmatch["Transformation type"], self.transformation.name,))

    def thanExpThc1(self, fw):
        "Saves the projection coefficients to a .thc file."
        f = fw.formFloat
        self.transformation.write(fw)

    def thanImpThc1(self, fr, ver):
        "Reads the projection coefficients from a .thc file."
        self.transformation = readProj(fr)


class ThanBiocityplan(ThanObject):
    thanObjectName = "BIOCITYPLAN"    # Name of the objects's class
    thanOjectInfo = "Automated east-west oriented city plan."
    thanVersions = ("1.0",)

    def __init__(self):
        "Set initial values to the city plan and paraphernalia."
        import thanpackages.biocityplan
        self.xor = self.yor = 0.0
        self.dxor = self.dyor = None
        self.pc = thanpackages.biocityplan.HippoAnneal()

    def toDialog(self, proj):
        "Return the data in a form needed by ThanBcplan dialog."
        pc = self.pc
        v = p_ggen.Struct()
        if pc.pol.hull == None: v.refPolygon = []
        else:                   v.refPolygon = pc.pol.hull
        v.refPrepro = pc.pol.shallowClone()   #Shallow copy
        v.labDTM = len(proj[1].thanObjects["DTMLINES"]) > 0
        v.doPrepro = False
        v.entMinWidth = pc.boik1
        v.entMaxWidth = pc.boik2
        v.entMinHeight = pc.hoik1
        v.entMaxHeight = pc.hoik2
        v.entMinRoad = pc.bod1
        v.entMaxRoad = pc.bod2
        v.choBio = pc.biochange
        v.entMult = 1
        return v

    def fromDialog(self, proj, v):
        "Get parameters from ThanBcplan dialog."
        pc = self.pc
        pc.pol = v.refPrepro
        pc.pol.hull = v.refPolygon
        pc.setPar(v.entMinWidth, v.entMaxWidth, v.entMinHeight, v.entMaxHeight, v.entMinRoad, v.entMaxRoad, v.choBio)

    def tkDraw(self, proj, state):
        "Draws a city plan as produced by simulated annealing."
        pc = self.pc
        first = self.dxor == None
        if first:
            self.dxor = self.pc.pol.uxmax - self.pc.pol.uxmin
            self.dyor = self.pc.pol.uymax - self.pc.pol.uymin
            self.yor -= 2.0*self.dyor*1.2     #leave space for original DTM (it may be visible :))
        ot = list(pc.pol.iterOT(state))
#        roads = pc.pol.roadcoor(state)
        roads = ()
        tit = "Energy=%.1f,  d>8%%=%.1f,  d>10%%=%.1f" % (state.e, state.d8, state.d10)
        ts = thanimp.ThanCadDrSave(proj[1], proj[2].thanPrt)
        dxf = thansupport.ThanDxfEmu()
        dxf.thanDxfPlots(ts)
        pc.pol.todxf(dxf, title=tit, hulls=(pc.pol.hull,), iso=pc.pol.contours, ot=ot, roads=roads, xor=self.xor, yor=self.yor)
        dxf.thanDxfPlot(0,0,999)
        ts.thanAfterImport()
        proj[1].thanLayerTree.thanDictRebuild()
        proj[2].thanRegen()
        if first:
            from thancom.thancomview import thanZoomExt
            thanZoomExt(proj)
        self.xor += self.dxor*1.10
        if self.xor > 3.01*1.10*self.dxor:
            self.xor = 0.0
            self.yor -= self.dyor*1.2

    def run(self, proj):
        "Run the bioclimatic city plan algorithm."
        import thanpackages.biocityplan
        thanpackages.biocityplan.simpol.runOnce(self.pc, prt=proj[2].thanPrt)


    def wrState(self, proj):
        "Save the state of the solution."
        import thanpackages.biocityplan
        pref = proj[0].parent / proj[0].namebase
        thanpackages.biocityplan.simpol.wrState(self.pc, pref, prter=proj[2].thanPrter)

    def thanList(self, than):
        "Shows information about the FloorPlan object."
        c = list(than.elevation)
        c[:2] = self.xor, self.yor
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s %s\n" % (Tarch["Next city plan position:"], than.strcoo(c)))


    def thanExpThc1(self, fw):
        "Saves the bioclimatic city plan to a .thc file."
        f2 = fw.formFloat + "  " + fw.formFloat
        pc = self.pc

        fw.writeBeg("location")
        fw.pushInd()
        fw.writeAtt("current", f2 % (self.xor, self.yor))
        if self.dxor == None: fw.writeAtt("delta", "_NONE_  _NONE_")
        else:                 fw.writeAtt("delta", f2 % (self.dxor, self.dyor))
        fw.popInd()
        fw.writeEnd("location")

        fw.writeBeg("parameters")
        fw.pushInd()
        fw.writeAtt("city_block_width", f2 % (pc.boik1, pc.boik2))
        fw.writeAtt("city_block_height", f2 % (pc.hoik1, pc.hoik2))
        fw.writeAtt("road_width", f2 % (pc.bod1, pc.bod2))
        fw.writeAtt("bioclimatic", "%d" % (pc.biochange,))
        fw.popInd()
        fw.writeEnd("parameters")

        fw.writeBeg("road_grid")
        fw.pushInd()
        if pc.pol.roadenx != None:
            fw.writeAtt("computed", "%d" % (True,))
            pc.pol.writeGrid(fw)
        else:
            fw.writeAtt("computed", "%d" % (False,))
        fw.popInd()
        fw.writeEnd("road_grid")


    def thanImpThc1(self, fr, ver):
        "Reads the bioclimatic city plan from a .thc file."
        pc = self.pc

        fr.readBeg("location")
        self.xor, self.yor =  map(float, fr.readAtt("current"))
        self.dxor, self.dyor =  fr.readAtt("delta")
        if self.dxor == "_NONE_": self.dxor = self.dyor = None
        else:                     self.dxor, self.dyor = float(self.dxor), float(self.dyor)
        fr.readEnd("location")

        fr.readBeg("parameters")
        boik1, boik2 = map(float, fr.readAtt("city_block_width"))
        hoik1, hoik2 = map(float, fr.readAtt("city_block_height"))
        bod1, bod2 = map(float, fr.readAtt("road_width"))
        biochange = bool(int(fr.readAtt("bioclimatic")[0]))
        fr.readEnd("parameters")
        pc.setPar(boik1, boik2, hoik1, hoik2, bod1, bod2, biochange)

        fr.readBeg("road_grid")
        computed = bool(int(fr.readAtt("computed")[0]))
        if computed:
            pc.pol.readGrid(fr)
        else:
            pc.pol.roadenx = pc.pol.roadeny = None
        fr.readEnd("road_grid")


class ThanProfile(ThanObject):
    thanObjectName = "PROFILE"    # Name of the objects's class
    thanOjectInfo = "Profile of a roads, conduits etc.."
    thanVersions = ("1.0",)

    def __init__(self, aa=None, xth=None, hed=None, cori=None, xthmin=None, hmin=None, dscale=10.0):
        "Set initial values to the profile plan and paraphernalia (if they are defined)."
        if aa == None: return
        self.thanSet(aa, xth, hed, cori=None, xthmin=None, hmin=None, dscale=10.0)


    def thanSet(self, aa, xth, hed, cori=None, xthmin=None, hmin=None, dscale=10.0):
        "Set initial values to the profile plan and paraphernalia."
        assert len(aa) > 1
        self.aa = tuple(aa)
        self.xth = tuple(xth)
        self.hed = tuple(hed)
        if cori != None: self.cori = tuple(cori)
        else:            self.cori = (0.0, 0.0, 0.0)
        if xthmin != None: self.xthmin = xthmin
        else:              self.xthmin = self.xth[0]
        if hmin != None: self.hmin = hmin
        else:            self.hmin = min(self.hed)
        self.dscale = dscale                        #Differential scale: scale for h is 10 times bigger than scale for xth


    def thanXy(self, xth1, h1):
        "Find the position of station xth1 with height h1 on the drawing."
        cp = list(self.cori)
        cp[0] += (xth1-xthmin)/scale
        cp[1] += (h1-hmin)
        return cp


    def execute(self, proj):
        "Write the .ger and .mhk files which are needed for the program mhker."
        import p_gmhk
        try:
            fw = p_ggen.uniqfile(proj[0].parent/proj[0].namebase, suf=".ger", stat="w", n=3)
            if fw == None: raise IOError, "Can not create unique name with prefix %s" % (proj[0],)
            fn = p_ggen.path(fw.name)
            fns = [fn.parent / fn.namebase + suf for suf in ".ger .mhk .nmh".split()]
            fns.append(fn.parent / "mediate.tmp")

            nSpa = 15
            aklisOr =  ( 0.400,          0.500,          4.000,          5.000)
            aklisTim = (10.000,         10.000,        -10.000,         10.000)
            rErola = 1000.000
            fw.write("%10d\n" % (nSpa,))
            fw.write("%15.3f%15.3f%15.3f%15.3f\n" % aklisOr)
            fw.write("%15.3f%15.3f%15.3f%15.3f\n" % aklisTim)
            fw.write("%15.3f\n" % (rErola,))
            fw.close()
            fn.remove()

            fw = open(fns[1], "w")
            p_gmhk.wrMhk1ti(fw, ngram=2)
            p_gmhk.wrMhk1oned(fw, "PROFILE 1", zip(self.aa, self.xth, self.hed))
            fw.close()

            fw = open(fns[-1], "w")
            fw.write("1\n%s\n" % (fn.namebase,))
            fw.close()
        except IOError, e:
            for fn in fns:
                try: fn.remove()
                except IOError: pass
            return False, e.message

        ok = p_grun.runExecWin("c_mhker", pdir=proj[0].parent, pexpectline=True, master=proj[2],
             title=u"ThanCad - %s: Grade line computation" % (fn.namebase),)
        if not ok: return False, "Errors recorded in output window."
        if fns[3].exists():
            try: fns[3].remove()
            except IOError: pass
            return False, "Errors recorded in output window."
        for fn in fns[:2]:
            try: fn.remove()
            except IOError: pass
        try: fns[2].rename(fns[1])
        except IOError, e: return False, e.message
        import thancom
        thancom.thancomfile.thanFileOpenPaths(proj, [fns[1]])
        return True, ""


    def thanList(self, than):
        "Shows information about the profile object."
        than.writecom("%s: %s\n" % (T["Object"], self.thanObjectName))
        than.write("%s: %s\n" % (Tarch["Number of stations"], len(self.xth)))
        than.write("%s: %s\n" % (T["Length"], than.strdis(self.xth[-1]-self.xth[0])))


thanObjClasses = (ThanDTMlines, ThanDEMusgs, ThanTri, ThanFplan, NonCartesian,
                  LineSimplification, ThanPhot, ThanPhotInterior,
                  ThanTransformation, ThanProjection, ThanBiocityplan,
                  ThanProfile)
thanObjClass = dict((c.thanObjectName, c) for c in thanObjClasses)
del thanObjClasses


if __name__ == "__main__":
    print __doc__
