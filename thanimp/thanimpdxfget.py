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

This module defines an object which reads a .dxf file and it creates
ThanCad's elements to represent it in ThanCad.
"""

import Image
import sys, time
from types import *
from math import pi
from p_gimdxf import ThanImportDxf, ThanDrWarn
from thandefs import ThanImageMissing
from thandefs.thanatt import ThanAttCol
from thanlayer import THANNAME
from thanvar import ThanLayerError
from thandr import *

COLSENT = ThanAttCol("0 222 255", inherit=False)  # This color does not exist in dxf and it is used as sentinel
                                                  # If one of already defined layers has this color, it will
                                                  # probably lose it

############################################################################
############################################################################

class ThanCadDrSave(ThanDrWarn):
    "A class which stores the elements read by ThanImportDxf into a ThanCad drawing."

    def __init__(self, dr, prt):
        "Creates an instance of the class."
        ThanDrWarn.__init__(self, laykno=("*",), prt=prt)
        self._dr = dr
        self._elev = dr.thanVar["elevation"]
        self.ielems = self.ieldeg = 0
        self.t1 = self.t2 = time.time()
        self.addElem = dr.thanElementAdd     # Oprimisation: it is freqently needed
#-------Use already defined layers
	self.dxfLayers = {}
#	for lay in self.thanDr.thanLayerTree.thanRoot.thanChildren:
#	    nam = str(lay.thanAtts[THANNAME])
#	    col = "%03d" % lay.thanAtts["moncolor"].thanDxf()
#	    self.dxfLayers[nam, col] = self.dxfLayers[nam, None] =\
#	        self.dxfLayers[nam] = lay


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
        try:
            lt.thanRoot.tempCol    # This means that setLay has been called at least once
            self._delTempCol(self._dr.thanLayerTree.thanRoot)
        except:
            pass                   # This means that setLay has NEVER been called (no elements at all)
        self._count(force=True)
#-------Add here code to put default color to layers with COLSENT


    def dxfVport(self, name, x1, y1, x2, y2):
        "Saves a View Port."
        self._dr.viewPort[:] = (x1, y1, x2, x2)
        self._count()


    def dxfXymm(self, x1, y1, x2, y2):
        "Saves xmin,ymin,xmax,ymax of the dxf drawing."
        dr = self._dr
        dr.xMinAct = x1
        dr.yMinAct = y1
        dr.xMaxAct = x2
        dr.yMaxAct = y2
        self._count()


    def dxfLayer(self, name, atts):
        "Saves a layer."
        lay = self._createHierarchyLayer(name, self._dr.thanLayerTree)
	a = lay.thanAtts
	try: v = str(atts["color"])
	except KeyError: a["moncolor"] = a["plotcolor"] = COLSENT
	else:
	    a["moncolor"]  = ThanAttCol(v, inherit=False)
	    a["plotcolor"] = ThanAttCol(v, inherit=False)
	try: v = atts["frozen"]
	except KeyError: pass
	else: class_ = a["frozen"].__class__; a["frozen"] = class_(v, False)
	self._count()


#    def dxfLtype(self, name, desc, elems):    # Let ThanWarn base class inform the user
#        "Saves a line type."
#        self._count()


    def dxfPolyline(self, xx, yy, zz, lay, handle, col):
        "Saves a polyline."
        n = len(xx)
        elev = self._elev
        nd = len(elev)
        more = [n*[elev[i]] for i in xrange(3, nd)]
        e = ThanLine()
        e.thanSet(zip(xx, yy, zz, *more))
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
            self._count()
        else:
            self._count(degenerate=True)


    dxfLine = dxfPolyline                               # "Saves a line."


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
        if name == None:
            e = ThanPoint()
            e.thanSet(cc)
        else:
            if validc == None: validc = [True, True, True]
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
	cc1 = list(self._elev)
	cc1[0] = xx
	cc1[1] = yy
	cc1[2] = zz
	cc2 = list(self._elev)
	cc2[0] = xx+width*scale
	cc2[1] = yy+height*scale
	cc2[2] = zz
        try:
	    im = Image.open(filnam)
        except IOError, why:
	    self.prt("Error loading image from file %s\n    %s" % (filnam, why))
	    im = ThanImageMissing(size=size)
        width, height = im.size

        e = ThanImage()
        e.thanSet(filnam, im, cc1, cc2, theta*pi/190)
        if e.thanIsNormal():
            self.thanSetLay(lay, col)
            self.addElem(e)
	    self._count()
	else:
	    self._count(degenerate=True)


#    def dxfBlockAtt(self, xx, yy, zz, lay, handle, col, blname, blatts):    # Let ThanWarn base class inform the user
#        "Block instance."
#	self.iblocks += 1
#	if self.iblocks == 1:
#	    self.prt("Block mechanism not yet implemented: blocks are ignored.")
#	self._count()


#    def dxf3dface  (self, xx, yy, zz, lay, handle, col):    # Let ThanWarn base class inform the user
#        "3d face."
#	self.prt("3dface can not be handled by 2d ThanCad. It is Ignored.")


    def thanSetLay(self, named, col):
        """Sets as current layer the top layer whose name is named.

	If color is not the same as the color of the layer, create a child layer
	which will have this color."""

#-------Layer, color pair in cache

        assert type(col) in (NoneType, IntType)
        if col <= 0: col = None
        lt = self._dr.thanLayerTree
        try:
            lt.thanRoot.tempCol                       # This means we just entered SECTION ENTITIES..
        except:                                       # .. and thus we add temCol to all defined layers
            self._addTempCol(lt.thanRoot)
            lay0 = lt.thanRoot.thanChildren[0]
            if len(lt.thanRoot.thanChildren) == 1 and len(lay0.thanChildren) == 0:
                self._setCol(lay0, None)    #This is probably a new empty drawing, so that we chan change the color of layer 0
	if (named, col) in self.dxfLayers:             # LAYER AND COLOR IS ALREADY THERE
	    lt.thanCur = self.dxfLayers[named, col]
            assert lt.thanCur != None
	    return lt.thanCur
	assert named.strip() != "__root", "__root layer should not be accessed here :("  # Shortcircuit to childlayer "0"

	lay = self._createHierarchyLayer(named, lt)    # Create layer if it doesn't exist (child of root)
        if col == None: col = lay.tempCol
	if lay.tempCol == None: self._setCol(lay, col)
        if col == lay.tempCol and len(lay.thanChildren) == 0: # If colours match return the created layer
	    lt.thanCur = self.dxfLayers[named, col] = self.dxfLayers[named, None] = lay
            assert lt.thanCur != None
	    return lay
#       todo: what happens if layer has grandchildren? elements can not be written to child!?
        self._move2ChildLayer(lay)                     # Move elements to child layer
        laych = self._createChildLayer(lay, col)
	self._setCol(laych, col)
	lt.thanCur = self.dxfLayers[named, col] = self.dxfLayers[named, None] = laych
        assert lt.thanCur != None
	return laych


    def _createHierarchyLayer(self, named, lt):
        "Create base layer if it doesn't exist (child of root)."
	if named.strip() == "__root": return lt.thanRoot
	names = named.split("__")
	laypar = lt.thanRoot
	for named in names:
            name = named.strip().replace(" ", "_")     # Erase blanks
            if name[:1] == ".": name = "*"+name[1:]    # Erase initial dot
	    for lay in laypar.thanChildren:
	        if name == str(lay.thanAtts[THANNAME]): break # name is an existing layer
	    else:
                lay = self._createChildUnknown(laypar, name, named)
	    laypar = lay
	return laypar


    def _createChildUnknown(self, laypar, name, named):
        "Create a new child layer with name name, or with name unknown."
        try:
            lay = laypar.thanChildNew(name)            # Create new layer if possible
	    self._setCol(lay, None)
	    return lay
	except ThanLayerError, why:
	    pass
	name = "unknown"                               # Layer is invalid; create default
	self.prt("Dxf layer '%s' can not be created and it is ignored:" % named)
	self.prt("    %s" % why)
	self.prt("    Layer '%s' is used instead." % name)
	for lay in laypar.thanChildren:
	    if name == str(lay.thanAtts[THANNAME]): return lay # Return existing default layer
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
	    if str(lay.thanAtts[THANNAME]) == name: return lay
        lay = laypar.thanChildNew(name)                # No error expected here
        self._setCol(lay, col)
	return lay


    def _setCol(self, lay, col):
        "Set the colour of the layer to col."
        if col == None: tc = COLSENT
        else:           tc = ThanAttCol(str(col), inherit=False)
	lay.thanAtts["moncolor"]  = lay.thanAtts["plotcolor"] = tc
	lay.tempCol = col


    def _count(self, degenerate=False, force=False):
        "Prints reading progress."
        self.ielems += 1
        if degenerate: self.ieldeg += 1
        if self.ielems % 1000 == 0 or force:
            self.t2 = time.time()
            self.prt("%d elements, %d degenerate, %.1f sec" % (self.ielems, self.ieldeg, self.t2-self.t1))
            self.t1 = self.t2


    def __delete__(self):
        "So that object is dead for debuggin reasons."
	from p_ggen import prg
	prg("ThanCadDrSave %s is deleted." % self)



############################################################################
############################################################################

#MODULE LEVEL CODE: THIS IS EXECUTED ONLY ONCE

if 0:
    print __doc__
    from thandr import ThanDrawing
    dr = ThanDrawing()
    f = file("mhk.dxf", "r")

    ts = ThanCadDrSave(dr)
    t = ThanImportDxf(f, ts)
    t.thanImport()
    f.close()
