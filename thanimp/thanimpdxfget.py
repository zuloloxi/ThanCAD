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

This module defines an object which reads a .dxf file and it creates
ThanCad's elements to represent it in ThanCad.
"""
import time
import p_gcol
from math import pi
from p_gimdxf import ThanImportDxf, ThanDrWarn
from p_gmath import thanNear2
from thandefs import imageOpen, ThanLtype
from thandefs.thanatt import ThanAttCol
from thanlayer import THANNAME
from thanlayer.thanlayername import splitDash2, repairLayerName
from thanvar import ThanLayerError
from thandr import (ThanLine, ThanCircle, ThanArc, ThanText, ThanPoint, ThanPointNamed,
    ThanEllipse, ThanImage, ThanFace3d, ThanLineFilled, ThanHatch)
from thantrans import T

from thanopt.thancon import THANLC
rootname = THANLC+"root"    #This must be all lower letters (not capital)


COLSENT = ThanAttCol("0 222 255", inherit=False)    # This color does not exist in dxf and it is used as sentinel
                                                    # If one of already defined layers has this color, it will
                                                    # probably lose it

class ThanCadDrSave(ThanDrWarn):
    "A receiver class which stores the elements read by p_gimdxf.ThanImportDxf into a ThanCad drawing."

    def __init__(self, dr, prt):
        "Creates an instance of the class."
        ThanDrWarn.__init__(self, laykno=("*",), prt=prt)
        self._dr = dr
        self._elev = dr.thanVar["elevation"]
        self.ielems = self.ieldeg = 0
        self.t1 = self.t2 = time.time()
        self.newelems = []                   #Records elements which are added to the drawing
        self.viewportDefined = False         #True if the viewport was defined by the caller (dxfVport())
#-------Use already defined layers
        self.dxfLayers = {}   #This is just a cache; no need to fill it with existing layers (if not a new drawing)
#       for lay in self._dr.thanLayerTree.thanRoot.thanChildren:
#           nam = str(lay.thanAtts[THANNAME])
#           col = "%03d" % lay.thanAtts["moncolor"].thanDxf()
#           self.dxfLayers[nam, col] = self.dxfLayers[nam, None] = lay
        self.ltunit = {}     #This dict saves the unit of the linetype as read from the dxf file
        self.var = {}         #Global variables


    def addElem(self, e, handle=None):
        "Add the element to ThanCad's database."
        if handle is not None and handle > 0:
            e1 = self._dr.thanTagel(handle)
            if e1 is None: e.handle = handle   #It is safe to keep the handle of the dxf
        self._dr.thanElementAdd(e)
        self.newelems.append(e)


    def _addTempCol(self, laypar):
        "Adds temporary attribute to layer hierarchy."
        laypar.tempCol = laypar.thanAtts["moncolor"].thanDxf()
        for lay in laypar.thanChildren:
            self._addTempCol(lay)


    def _delTempCol(self, laypar):
        "Deletes temporary attribute to layer hierarchy."
        del laypar.tempCol
        for lay in laypar.thanChildren:
            self._delTempCol(lay)


    def thanAfterImport(self):
        "Post initialisation."
        lt = self._dr.thanLayerTree
        try:    lt.thanRoot.tempCol    # This means that setLay has been called at least once
        except: pass
        else:   self._delTempCol(lt.thanRoot)
        self._count(force=True)
#-------Add here code to put default color to layers with COLSENT


    def dxfVars(self, v):
        "Global variables of dxf file."
        self.var.update(v)
        k = "fillmode"
        kv = self.var.get(k.upper())  #kv is guaranteed to be integer (if k exists)
        if kv is not None: self._dr.thanVar[k] = bool(kv)


    def dxfVport(self, name, x1, y1, x2, y2):
        "Saves a View Port."
        self._dr.viewPort[:] = (x1, y1, x2, x2)
        self.viewportDefined = True    #Viewport  has been defined
        self._count()


    def dxfLayer(self, name, atts):
        "Saves a layer."
        name = name.strip()
        lay = self._createHierarchyLayer(name, self._dr.thanLayerTree)
        a = lay.thanAtts
        try:
            v = str(atts["color"])
        except KeyError:
            a["moncolor"] = a["plotcolor"] = COLSENT     #COLSENT is a ThanAttCol instance
        else:
            a["moncolor"]  = ThanAttCol(v, inherit=False)
            a["plotcolor"] = ThanAttCol(v, inherit=False)

        #try:
        #    v = atts["frozen"]
        #except KeyError:
        #    pass
        #else:
        #    class_ = a["frozen"].__class__
        #    a["frozen"] = class_(v, False)
        v = atts.get("frozen", False)   #Thanasis2022_12_17
        v2 = atts.get("off", False)
        v = v or v2      #If either "frozen" or "off" is true, the layer will be frozen in ThanCad
        class_ = a["frozen"].__class__
        a["frozen"] = class_(v, False)

        try:
            v = str(atts["linetype"]).strip().lower()
        except KeyError:
            pass                  #default linetype is continuous
        else:
            class_ = a["linetype"].__class__
            scale = self.var.get("LTSCALE", 1.0)
            a["linetype"] = class_((v, self.ltunit.get(v, "mm"), scale))    #Unit "mm" is the default
            if v not in self._dr.thanLtypes: #If not found then complain (thanlayer.thanTkSet replaces it with continuous)
                self.prt(T["Unknown linetype '%s' is replaced with 'continuous'"] % (v,), "can1")
        self._count()


    def dxfLtype(self, name, desc, elems):    # Let ThanWarn base class inform the user
        "Saves a line type; name is in lower letters and free of preceding and trailing blanks."
        ltypes1 = {"continuous", "bylayer", "byblock"}  #bylayer, byblock are not real linetypes, just sentinels..
                                                        #..and continuous is automatically inside ThanCad
        name = name.strip().lower()
        if name in ltypes1: return
        lt = ThanLtype()
        unit = lt.thanFromDxf(name, desc, elems)
        self._dr.thanLtypes[lt.thanName] = lt      #Thanasis2016_12_31: name->lt.thanName
        self.ltunit[lt.thanName] = unit
        self._count()
        print("thanimpdxfget.dxfLtype(): thanLtypes=")
        for xxx in self._dr.thanLtypes.keys(): print(xxx)


    def dxfPolyline(self, xx, yy, zz, lay, handle, col, linw=None):
        "Saves a polyline."
        n = len(xx)
        elev = self._elev
        nd = len(elev)
        more = [n*[elev[i]] for i in range(3, nd)]
        e = ThanLine()
        e.thanSet(list(zip(xx, yy, zz, *more)))   #works for python2,3
        if e.thanIsNormal():
            self.thanSetLay(lay, col, linw)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)

    dxfLine = dxfPolyline                               # "Saves a line."


    def dxfHatch(self, xx, yy, zz, lay, handle, col):
        "Saves a hatch."
        print("dxfHatch:", len(xx))
        n = len(xx)
        elev = self._elev
        nd = len(elev)
        more = [n*[elev[i]] for i in range(3, nd)]
        cp = list(zip(xx, yy, zz, *more))   #works for python2,3
        e = ThanHatch()
        itype = 0   #Solid for the moment
        e.thanSet (cp, itype, 0.0, 0.0)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    def dxf3dface(self, xx, yy, zz, lay, handle, col):
        "Saves 3dface as a closed polyline."
        n = len(xx)
        elev = self._elev
        nd = len(elev)
        more = [n*[elev[i]] for i in range(3, nd)]
        cp = list(zip(xx, yy, zz, *more))   #works for python2,3

        if thanNear2(cp[-1], cp[-2]): del cp[-1]     #This is a 3 point 3dface
        cp.append(list(cp[0]))                       #Make the polyline closed

        e = ThanFace3d()
        e.thanSet(cp)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    def dxfSolid(self, xx, yy, zz, lay, handle, col):
        """Saves solid as a filled line.

        Note that the coordinates are given in clockwise or anti-clockwise order:
        The caller has already swapped 3rd and 4th point.
        See documetation line of method __getSolid(self, name) of class ThanEntities
        in file .../h/libs/source_python/p_gimdxf/thanimpdxfent.py
        """
        n = len(xx)
        elev = self._elev
        nd = len(elev)
        more = [n*[elev[i]] for i in range(3, nd)]
        cp = list(zip(xx, yy, zz, *more))   #works for python2,3

        if thanNear2(cp[-1], cp[-2]): del cp[-1]     #This is a 3 point solid
        cp.append(list(cp[0]))                       #Make the polyline closed

        e = ThanLineFilled()
        e.thanSet(cp, persistentfilled=True)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    def dxfCircle(self, xx, yy, zz, lay, handle, col, r):
        "Saves a View Port."
        cc = list(self._elev)
        cc[0] = xx
        cc[1] = yy
        cc[2] = zz
        e = ThanCircle()
        e.thanSet(cc, r)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    def dxfPoint(self, xx, yy, zz, lay, handle, col, name=None, validc=None):
        "Saves a point or a ThanCad named point."
        cc = list(self._elev)
        cc[0] = xx
        cc[1] = yy
        cc[2] = zz
        if name is None:
            e = ThanPoint()
            e.thanSet(cc)
        else:
            if validc is None: validc = [True, True, True]
            e = ThanPointNamed()
            e.thanSet(cc, name, validc)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    def dxfArc(self, xx, yy, zz, lay, handle, col, r, theta1, theta2):
        "Saves an arc."
        cc = list(self._elev)
        cc[0] = xx
        cc[1] = yy
        cc[2] = zz
        e = ThanArc()
        e.thanSet(cc, r, theta1*pi/180, theta2*pi/180)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    def dxfEllipse(self, xx, yy, zz, lay, handle, col, a, b, phia, phib, theta, full):
        "Saves an elliptic arc."
        cc = list(self._elev)
        cc[0] = xx
        cc[1] = yy
        cc[2] = zz
        e = ThanEllipse()
        dr = pi/180.0
        print("thanCad.imp.dxfEllipse:", xx, yy, a, b, phia, phib, theta, full)
        e.thanSet(cc, a, b, phia*dr, phib*dr, theta*dr, full)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    def dxfText(self, xx, yy, zz, lay, handle, col, text, h, theta):
        "Saves a text."
        cc = list(self._elev)
        cc[0] = xx
        cc[1] = yy
        cc[2] = zz
        e = ThanText()
        e.thanSet(text, cc, h, theta*pi/180)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    def dxfThanImage(self, xx, yy, zz, lay, handle, col, filnam, size, scale, theta):
        "Saves an ThanImage."
        im, terr = imageOpen(filnam)
        if terr != "":
            self.prt(T["Error loading image from file %s\n    %s"] % (filnam, terr))
            im.size=size
        width, height = im.size
        cc1 = list(self._elev)
        cc1[0] = xx
        cc1[1] = yy
        cc1[2] = zz
        cc2 = list(self._elev)
        cc2[0] = xx+width*scale
        cc2[1] = yy+height*scale
        cc2[2] = zz

        e = ThanImage()
        e.thanSet(filnam, im, cc1, cc2, theta*pi/180.0)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


#    def dxfBlockAtt(self, xx, yy, zz, lay, handle, col, blname, blatts)    # Let ThanWarn base class inform the user



    def thanSetLay(self, named, col, linw=None):
        """Sets as current layer the top layer whose name is named.

        If color is not the same as the color of the layer, create a child layer
        which will have this color."""

#-------Layer, color pair in cache

        #Thanasis2021_10_31: According to dxf 12 manual, col==0 means byblock and
        #col==256 means bylayer. Thus in these cases we put col=None (blocks not
        #yet supported).
        assert col is None or type(col) == int and 0<=col<=256, "col should be None or int between 0 and 256"
        named = named.strip()
        if col == 0 or col == 256:
            col = None
        elif col not in p_gcol.thanDxfColCode2Rgb:
            col = None      #color code is not recognised  #Thanasis2019_11_02
        lt = self._dr.thanLayerTree
        try:
            lt.thanRoot.tempCol                       # This means we just entered SECTION ENTITIES..
        except:                                       # .. and thus we add tempCol to all defined layers
            self._addTempCol(lt.thanRoot)
            lay0 = lt.thanRoot.thanChildren[0]
            if len(lt.thanRoot.thanChildren) == 1 and len(lay0.thanChildren) == 0:
                self._setCol(lay0, None)    #This is probably a new empty drawing, so that we can change the color of layer 0
        if (named, col) in self.dxfLayers:             # LAYER AND COLOR IS ALREADY THERE
            lt.thanCur = self.dxfLayers[named, col]
            assert lt.thanCur is not None
            return lt.thanCur
        #assert named.strip() != "__root", "__root layer should not be accessed here :("  # Shortcircuit to childlayer "0"
        assert named.lower() != rootname, "{} layer should not be accessed here :(".format(rootname)  # Shortcircuit to childlayer "0"


        if col is None:   #Thanasis2022_02_15
            print("Thanasis2022_02_14: col=", col, "named=", named)
            lay = self._getHierarchyLayer(named, lt) #get layer if it exists
            print("Thanasis2022_02_14: lay=", lay)
            if lay is not None: print("Thanasis2022_02_14: lay=", lay.thanAtts["layer"])
            if lay is not None: col = lay.tempCol  #If element color is not defined, then it gets the name of the original layer

        lay = self._createHierarchyLayer(named, lt)    # Create layer if it doesn't exist (child of root)
        if col is None: col = lay.tempCol
        if lay.tempCol is None: self._setCol(lay, col)
        if col == lay.tempCol and len(lay.thanChildren) == 0: # If colours match return the created layer
            lt.thanCur = self.dxfLayers[named, col] = self.dxfLayers[named, None] = lay
            assert lt.thanCur is not None
            return lay
        #todo: what happens if layer has grandchildren? elements can not be written to child!?
        self._move2ChildLayer(lay)                     # Move elements to child layer
        laych = self._createChildLayer(lay, col)
        self._setCol(laych, col)
        #lt.thanCur = self.dxfLayers[named, col] = self.dxfLayers[named, None] = laych #Thanasis2022_02_15:commented out
        lt.thanCur = self.dxfLayers[named, col] = laych #Thanasis2022_02_15:replacement of the abaove
        assert lt.thanCur is not None
        return laych


    def _createHierarchyLayer(self, named, lt):
        "Create base layer if it doesn't exist (child of root)."
        #We assume here that named has been striped: named=named.strip()
        if named.lower() == rootname: return lt.thanRoot  #Thanasis2022_12_17: .lower() added, rootname is already in lower
        names = splitDash2(named)
        laypar = lt.thanRoot
        for named in names:
            name = repairLayerName(named)
            if name[:1] == ".": name = "*"+name[1:]    # Erase initial dot
            for lay in laypar.thanChildren:
                if name.lower() == str(lay.thanAtts[THANNAME]).lower(): break # name is an existing layer
            else:
                lay = self._createChildUnknown(laypar, name, named)
            laypar = lay
        return laypar


    def _getHierarchyLayer(self, named, lt):          #Thanasis2022_02_15
        "Get a layer if it exists (child of root)."
        #We assume here that named has been striped: named=named.strip()
        if named.lower() == rootname: return lt.thanRoot  #Thanasis2022_12_17: .lower() added, rootname is already in lower
        names = splitDash2(named)
        laypar = lt.thanRoot
        for named in names:
            name = repairLayerName(named)
            if name[:1] == ".": name = "*"+name[1:]    # Erase initial dot
            for lay in laypar.thanChildren:
                if name.lower() == str(lay.thanAtts[THANNAME]).lower(): break # name is an existing layer
            else:
                return None   #layer not found
            laypar = lay
        return laypar


    def _createChildUnknown(self, laypar, name, named):
        "Create a new child layer with name name, or with name unknown."
        try:
            lay = laypar.thanChildNew(name)            # Create new layer if possible
            self._setCol(lay, None)
            return lay
        except ThanLayerError as why:
            why1 = why                                 #Work around curious Python3 bug
        name = "unknown"                               # Layer is invalid; create default
        self.prt(T["Dxf layer '%s' can not be created and it is ignored:"] % named)
        self.prt("    %s" % why1)
        self.prt(T["    Layer '%s' is used instead."] % name)
        for lay in laypar.thanChildren:
            if name.lower() == str(lay.thanAtts[THANNAME]).lower(): return lay # Return existing default layer
        lay = laypar.thanChildNew(name)                # No error is expected here
        self._setCol(lay, None)
        return lay


    def _move2ChildLayer(self, laypar):
        "Move current colour to child layer if not already there."
        if len(laypar.thanChildren) > 0: return
        if len(laypar.thanQuad) == 0: return
        colpar = laypar.tempCol
        lay = laypar.thanMove2child("col%03d"%colpar, force=True) # No error is expected here
        self._setCol(lay, colpar)
        self.dxfLayers.clear()                         # Invalidate cache


    def _createChildLayer(self, laypar, col):
        "Create child layer if it doesn't exist (child of root)."
        name = "col%03d" % col
        for lay in laypar.thanChildren:
            if str(lay.thanAtts[THANNAME]).lower() == name.lower(): return lay
        lay = laypar.thanChildNew(name)                # No error expected here
        self._setCol(lay, col)
        return lay


    def _setCol(self, lay, col):
        "Set the colour of the layer to col."
        if col is None: tc = COLSENT
        else:           tc = ThanAttCol(str(col), inherit=False)
        lay.thanAtts["moncolor"]  = lay.thanAtts["plotcolor"] = tc
        lay.tempCol = col


    def _count(self, degenerate=False, force=False):
        "Prints reading progress."
        if not force:    #When we force to print the number of elements, do not increment number of elements
            self.ielems += 1
            if degenerate: self.ieldeg += 1
        if self.ielems % 1000 == 0 or force:
            self.t2 = time.time()
            self.prt(T["%d elements, %d degenerate, %.1f sec"] % (self.ielems, self.ieldeg, self.t2-self.t1))
            self.t1 = self.t2


    def __del__(self):
        "So that object is dead for debugging reasons."
        from p_ggen import prg
        prg("ThanCadDrSave %s is deleted." % self)


def test():
    print(__doc__)
    from thandwg import ThanDrawing
    dr = ThanDrawing()
    f = open("mhk.dxf", "r")

    ts = ThanCadDrSave(dr)
    t = ThanImportDxf(f, ts)
    t.thanImport()
    f.close()
