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

This module defines a ThanCad drawing, which contains elements, has layers,
viewports, etc."
"""

from __future__ import print_function
import p_ggen, p_gdxf, p_gimgeo, p_gimage, p_ggeod
from p_gmath   import ThanRectCoorTransf, thanRoundCenter
import thanfonts, thandefs
from thanlayer import ThanLayerTree, col2tuple
from thandefs  import ThanId
from thandr    import ThanElement, ThanImage, thanElemClass, thanImageClasses

from .thandwgvars import thanVarsDef, thanVarsExpThc, thanVarsImpThc, thanObjsDef, thanObjsExpThc, thanObjsImpThc


class ThanDoundo:
    "Implements the undo/redo scheme."

    def __init__(self):
        "Make an empty do/undo list."
        self.clear()

    def thanAdd(self, text, redoFun, redoArgs, undoFun, undoArgs):
        "A new command (or task) to undo/redo."
        del self.__doundo[self.__i:]    #Clear future do list
        self.__doundo.append((text, redoFun, redoArgs, undoFun, undoArgs))
        self.__i = len(self.__doundo)

    def thanRedo(self, proj):
        "Redoes previously 'undone' command/task."
        assert self.__i < len(self.__doundo), "Nothing left to redo"
        redoFun, redoArgs = self.__doundo[self.__i][1:3]
        redoFun(proj, *redoArgs)
        self.__i += 1

    def thanUndo(self, proj):
        "Undoes previous command/task."
        assert self.__i > 0, "Nothing left to undo"
        undoFun, undoArgs = self.__doundo[self.__i-1][3:5]
        undoFun(proj, *undoArgs)
        self.__i -= 1

    def thanRedotry(self):
        "Finds out if redo is possible; returns command's text if possible."
        if self.__i >= len(self.__doundo): return None  # Nothing left to redo
        return self.__doundo[self.__i][0]

    def thanUndotry(self):
        "Finds out if undo is possible; returns command's text if possible."
        if self.__i <= 0: return None                   # Nothing left to undo
        return self.__doundo[self.__i-1][0]

    def clear(self):
        "Clears the do/undo list."
        self.__doundo = []
        self.__i = 0


class ThanTagel(dict):
    "A dictionary with predefined/readonly items."

    rdlist = frozenset(("e0", "edrag", "enull"))
#    __slots__ = ("prefix",)       #So that we don't need __getstate__ and __setstate__ (anyway we use few ThanTegl objects)

    def __init__(self, *args, **kw):
        "Set predefined items, if not already in args/kw."
        self.prefix = kw.pop("prefix", "")
        dict.__init__(self, *args, **kw)
        temp = ThanElement()    # Null element: This is to ensure that temporary elements..
                                # ..do not lead to KeyError, and do all operations passively
        for key in self.rdlist:
            self.setdefault(key, temp)

    def __delitem__(self, key):
        "Do not delete readonly items."
        if key in self.rdlist: return
        dict.__delitem__(self, key)

    def __setitem__(self, key, val):
        "Do not delete readonly items."
        if key in self.rdlist: raise KeyError("Readonly item: key: %s" % key)
        dict.__setitem__(self, key, val)

    def get(self, key, defv=None):
        "Check also if it is handle instead of a tag, by adding prefix."
        v = dict.get(self, key)
        if v is not None: return v
        return dict.get(self, self.prefix+str(key), defv)

    def __getitem__(self, key):
        "Check also if it is handle instead of a tag, by adding prefix."
        v = dict.get(self, key)
        if v is not None: return v
        v = dict.get(self, self.prefix+str(key))
        if v is not None: return v
        raise ValueError("Tag/handle %s not found in this drawing" % (key,))   # Raise ValueError to accommodate ThanRfile/ThanWfile


class ThanDrawing:
    "Represents a whole drawing."
    thanThcVersions = ((0,1,0), (0,1,1), (0,2,0), (0,2,1), (0,3,0))   #All supported versions of .thcx files

    def __init__ (self):
        """Creates a new drawing instance.

        xyminmaxact: Smallest rectangle which contains all active elements (for zoom extents)
             active elements are all the elements of the drawing that are not in a
             frozen layer.
        thanAreaIterated: a rectangle >= viewport. All active elements inside (or partly inside)
            this rectangle are drawn in the Canvas.
        thanLayerTree: the layer hierarchy and related dictionaries
        __idTag: id (or handle) generator for elements
        thanTagel: maps id (handle) to element
        thanDoundo: the do/undo history
        __modified: True if the drawing has been modified since last save
        thanEdus: elements which are hilighted when the mouse gets near them
        thanThcVersion: the version of .thcx file
        viewPort: The part of the drawing that matches exactly the canvas
        thanTstyles: text styles dictionary of the drawing
        thanLtypes: line types dictionary of the drawing
        thanUnits: the units of the drawing
        thanVar: a dictionary of variables/values
        thanPlotDef: the previous plot parameters (window, plotter etc)
        thanObjects: a dictionary of names/objects of the drawing. Objects are elements
                     with no graphic representation
        """
        self.thanAreaIterated = (None, None, None, None)  # No element -> no limit in regen
        self.xMinAct = self.yMinAct = self.xMaxAct = self.yMaxAct = None  #Smallest rectangle which contains all active elements
        self.thanLayerTree = ThanLayerTree()
        self.__idTag = ThanId(prefix="E")
        self.thanTagel = ThanTagel(prefix="E")
        self.thanDoundo = ThanDoundo()
        self.__modified = False
#        self.thanEdus = weakref.WeakKeyDictionary()
        self.thanEdus = set()   #We use set (instead of weakdictionary) because the do/undo mechanism
                                #kept a reference to the elements (also stored in thanEdus), and thus
                                #elements in thanEdus were never deleted. It does not matter if edus
                                #has deleted elements, unless thanEdus occupies huge memory (unlikely)
                                #In the future, thanEdus will be synchronised at file save time.
        self.thanThcVersion = self.thanThcVersions[-1]
        self.viewPort = [-10.0, -10.0, 100.0, 100.0]
        t = thandefs.ThanTstyle("standard", thanfonts.thanFonts["thanprime1"])
        self.thanTstyles = {t.thanName: t}
        self.thanLtypes = thandefs.thanDashes()
        self.thanUnits = thandefs.ThanUnits()
        self.thanVar = thanVarsDef()
        self.thanPlotDef = thandefs.thanplotcups.ThanPlot()  # Previous plot settings
        self.thanObjects = thanObjsDef()
        self.thanElements2Repair = []    #Elements with wrong handle which must be repaired
        self.repairhandle = False        #If True, then elements with wrong handle will be repaired
        self.Lgeodp = p_ggeod.params.fromEgsa87()  #Default geodetic projection is EGSA87
        self.geodp = p_ggeod.params.toProj(self.Lgeodp) #Geodetic projections are BUILTIN in ThanCad


    def thanExpThc(self, fw):
        "Save all attributes of the drawing except the elements in thc format."
        f = fw.formFloat
        fw.writeBeg("THANCAD_DRAWING")

        fw.writeBeg("ATTRIBUTES")
        fw.pushInd()
        fw.writeAtt("version",  "%d.%d.%d" % self.thanThcVersion)
        fw.writeAtt("viewport", (f*4) % tuple(self.viewPort))
        fw.popInd()
        fw.writeEnd("ATTRIBUTES")
        fw.writeBeg("TEXTSTYLES")
        fw.pushInd()
        for t in self.thanTstyles.values():  #works for python2,3
            pass
        fw.popInd()
        fw.writeEnd("TEXTSTYLES")
        fw.writeBeg("LINETYPES")
        fw.pushInd()
        for t in self.thanLtypes.values():  #works for python2,3
            t.thanExpThc(fw)
        fw.popInd()
        fw.writeEnd("LINETYPES")

        fw.writeBeg("GEODETICPROJECTION")
        fw.pushInd()
        p_ggeod.params.toFile(self.Lgeodp, fw)
        fw.popInd()
        fw.writeEnd("GEODETICPROJECTION")

        self.thanUnits.thanExpThc(fw)
        thanVarsExpThc(fw, self.thanVar, self.thanThcVersion)
        self.thanPlotDef.thanExpThc(fw)
        self.thanLayerTree.thanExpThc(fw)
#        thanEdus  #Here I must synchronise thanEdus: delete entries which correspond to deleted elements
        self.thanExpThcElements(fw)
        thanObjsExpThc(fw, self.thanObjects)
        fw.writeEnd("THANCAD_DRAWING")


    def thanImpThc(self, fr, forceunload=False, prt=p_ggen.doNothing):
        "Read all attributes of the drawing except the elements from a thc format file."
        fr.readBeg("THANCAD_DRAWING")

        fr.readBeg("ATTRIBUTES")
        t = fr.readAtt("version")[0]
        self.thanThcVersion = tuple(map(int, t.split(".")))  #works for python2,3
        if self.thanThcVersion not in self.thanThcVersions: raise ValueError("Unknown thc version: %r" % (self.thanThcVersion,))
        self.viewPort = list(map(float, fr.readAtt("viewport")))    #works for python2,3
        if len(self.viewPort) != 4: raise ValueError("Invalid viewport")
        fr.readEnd("ATTRIBUTES")
        fr.readBeg("TEXTSTYLES")
        fr.readEnd("TEXTSTYLES")
        fr.readBeg("LINETYPES")
        for name in fr:
            name = name.strip()[1:-1]
            fr.unread()
            if name == "/LINETYPES": break
            lt = thandefs.ThanLtype()
            lt.thanImpThc(fr, self.thanThcVersion)
            if lt.thanName != "continuous":
                self.thanLtypes[lt.thanName] = lt
        fr.readEnd("LINETYPES")

        if (self.thanThcVersion >= (0,3,0)):   #Otherwise keep default geodetic projection
            fr.readBeg("GEODETICPROJECTION")
            self.Lgeodp = p_ggeod.params.fromFile(fr)
            self.geodp = p_ggeod.params.toProj(self.Lgeodp)
            fr.readEnd("GEODETICPROJECTION")

        self.thanUnits.thanImpThc(fr)
        d = thanVarsImpThc(fr, self.thanThcVersion)
        self.thanVar.update(d)
        self.thanPlotDef.thanImpThc(fr)
        self.thanLayerTree.thanImpThc(fr, self.thanThcVersion)
#        thanEdus
        self.thanImpThcElements(fr, forceunload, prt)
        thanObjsImpThc(fr, self.thanObjects)
        fr.readEnd("THANCAD_DRAWING")
        self.thanThcVersion = self.thanThcVersions[-1]


    def thanExpThcElements(self, fw):
        "Save all the elements of the drawing in thc format."
        fw.writeBeg("ELEMENTS")
        fw.pushInd()
        for lay in self.thanLayerTree.dilay.values():   #works for python2,3
            layname = lay.thanGetPathname()
            for e in lay.thanQuad:
                e.thanExpThc(fw, layname)
        fw.popInd()
        fw.writeEnd("ELEMENTS")


    def thanImpThcElements(self, fr, forceunload=False, prt=p_ggen.doNothing):
        "Read all the elements from a thc format file."
        self.repairhandle = True        #If True, then elements with wrong handle will be repaired
        fr.readBeg("ELEMENTS")
        lt = self.thanLayerTree
        layori = lt.thanCur
        laynamecur = layori.thanGetPathname()
        for name in fr:
            name = name.strip()[1:-1]
            fr.unread()
            if name == "/ELEMENTS": break
            class_ = thanElemClass.get(name)
            if class_ is None: raise ValueError("Unknown element type: %s" % name)
            e1 = class_()
            if forceunload and name in thanImageClasses:
                layname = e1.thanImpThc(fr, self.thanThcVersion, forceunload)
            else:
                layname = e1.thanImpThc(fr, self.thanThcVersion)
            if layname != laynamecur:
                lt.thanCur = lt.thanFindic(layname)
                if lt.thanCur is None: raise ValueError("Layer %s was not found in layer hierarchy" % (layname,))
                laynamecur = layname
            self.thanElementAdd(e1)
        fr.readEnd("ELEMENTS")
        self.repairhandle = False        #If True, then elements with wrong handle will be repaired
        if len(self.thanElements2Repair) > 0:
            self.thanRepairHandles()
            prt("The handles of %d elements were repaired." % (len(self.thanElements2Repair),), "can")
        lt.thanCur = layori


    def thanDestroy(self):
        "Destroy circular references."
        self.thanLayerTree.thanDestroy()
        del self.thanDoundo


    def thanElementTag(self, elem, cl=None):
        "Adds tags to an elements and gets it ready for 'restore'."
        if cl is None: cl = self.thanLayerTree.thanCur
        if elem.handle <= 0: elem.handle, tag = self.__idTag.new2()
        else:                tag = self.__idTag.addprefix(elem.handle)
        if elem.thanTkCompound > 1:
            elem.thanTags = tag, cl.thanTag
        else:
            elem.thanTags = tag, cl.thanTag, "nocomp"     # Not a compound element

    def thanGetLayer(self, e):
        "Gets the layer object which the element belongs to."
        taglay = self.thanLayerTree.dilay
        return taglay[e.thanTags[1]]


    def thanElementAdd(self, elem, cl=None):
        "Adds an element to the drawing."
        if cl is None: cl = self.thanLayerTree.thanCur
        if elem.handle <= 0:
            #class Than:
            #    def strdis(self, s): import sys; sys.stdout.write(str(s))
            #    def strcoo(self, s): import sys; sys.stdout.write(str(s))
            #    def read(self, s): from thanvar import Canc; return Canc
            #    laypath = "***"
            #    def write(self, s): import sys; sys.stdout.write(s)
            #    def writecom(self, s): import sys; sys.stdout.write(s)
            #elem.thanList(Than())
            #raise ValueError, "Element read without handle:"+elem.thanElementName
            if self.repairhandle:
                elem.handle, tag = -1, "-1"
                self.thanElements2Repair.append(elem)    #Elements with wrong handle which must be repaired
                print("New element added has illegal handle: %s" % (elem.handle,))
            else:
                elem.handle, tag = self.__idTag.new2()
        else:
            elem1 = self.thanTagel.get(elem.handle)
            if elem1 is not None:
                if not self.repairhandle: raise IndexError("New element added has the same tag/handle with existing element: %s" % (elem.handle,))
                elem.handle, tag = -1, "-1"
                self.thanElements2Repair.append(elem)    #Elements with wrong handle which must be repaired
                print("New element added has the same tag/handle with existing element: %s" % (elem.handle,))
            else:
                tag = self.__idTag.addprefix(elem.handle)
        if elem.thanTkCompound > 1:
            elem.thanTags = tag, cl.thanTag
        else:
            elem.thanTags = tag, cl.thanTag, "nocomp"     # Not a compound element
        self.__elementAddHouse(elem, cl)


    def __elementAddHouse(self, elem, cl):
        """Do housekeeping for the new element.

        Since the new element is drawn (if not frozen) thanAreaIterated is unchanged.
        """
        self.thanTagel[elem.thanTags[0]] = elem
        cl.thanQuad.add(elem)
        if not cl.thanAtts["frozen"].thanVal:
            if self.xMinAct is None:
                self.xMinAct = elem.thanXymm[0]
                self.yMinAct = elem.thanXymm[1]
                self.xMaxAct = elem.thanXymm[2]
                self.yMaxAct = elem.thanXymm[3]
            else:
                if elem.thanXymm[0] < self.xMinAct: self.xMinAct = elem.thanXymm[0]
                if elem.thanXymm[1] < self.yMinAct: self.yMinAct = elem.thanXymm[1]
                if elem.thanXymm[2] > self.xMaxAct: self.xMaxAct = elem.thanXymm[2]
                if elem.thanXymm[3] > self.yMaxAct: self.yMaxAct = elem.thanXymm[3]
        self.__modified = True


    def thanRepairHandles(self):
        "Repair handles of elements with wrong handles."
        del self.thanTagel["-1"]   #At least one element was added with tag "-1"  #Thanasis2015_09_29
        for elem in self.thanElements2Repair:
            elem.handle, tag = self.__idTag.new2()
            elem.thanTags = (tag,) + elem.thanTags[1:]
            self.thanTagel[elem.thanTags[0]] = elem                               #Thanasis2015_09_29

#===========================================================================

    def thanTkDraw(self, than, lays="all"):
        """Draws the active elements (inside the viewport) into a gui window.

        Active are the elements which do not belong to a layer which is 'off'.
        This function checks each element of ThanDrawing and if it, or part of it,
        is inside the viewport (which is just a rectangle), draws it into 'win'.
        Thus, in general, 'win' has less elements than ThanDrawing.
        'win' has all the elements that are, at least partially, inside viewport.

            If we assume that all elements of ThanDrawing are partially inside
        viewport, then 'win' has actually all ThanDrawing's elements, even
        though viewport is smaller than the viewport that fully covers all
        the elements.
            It is also possible that 'win' does not have all ThanDrawing's elements,
        but all elements that are covered by a bigger rectangle than viewport.
        This bigger rectangle is called 'thanAreaIterated'. 'thanAreaIterated' is
        the rectangle which is smaller (i.e. it does not cover) any part of the
        elements not drawn.
            'thanAreaIterated' is quite useful because if the user pans or zooms
        the drawing, the new viewport may be inside  'thanAreaIterated'. It is
        thus not necessary to redraw (actually regenerate) the elements, since
        these elements are already in 'win'. All that is needed is that 'win'
        pans or zooms its elements, which is usually much faster.
            This feature is so useful that when thanDraw is called, it draws the
        elements of a rectangle 5 (or 25) times bigger than the viewport, so
        that pan and zoom can be done faster.

            Another concept, completely unrelated to the above, is the smallest
        rectangle 'xyMinMaxAct', which covers all the active elements of
       ThanDrawing. This is needed when the user wants to zoom all.
            xyMinMaxAct are the x and y min and max of the active elements
        (elements of the visible layers). When a drawing is read, 'xyMinMaxAct'
        is computed. When an element is added, 'xyMinMaxAct' is updated.
        When a layer is turned on, all its elements are checked, to see if
        they are inside the viewport, and xyMinMaxAct is updated.
            However, when an element is deleted, and its rectangle share at
        least one edge with xyMinMaxAct, then xyMinMaxAct may no longer be valid.
        It will always cover all the active elements, but it may not be the
        smaller rectangle which covers all the elements.
            Since thanDraw iterates through all visible elements, xyMinMaxAct
        is also computed.
            When a user zooms all, and xyMinMaxAct is within thanAreaIterated,
        thanDraw() is not called. However, it should be possible to ask the gui
        window for its version of xyMinMaxAct, and pass it here.
        """

        self.thanAreaIterated = (1, 1, -1, -1)                            # Set as invalid in case user aborts
        self.xMinAct = self.yMinAct = self.xMaxAct = self.yMaxAct = None  # Set as invalid in case user aborts
        xymm = self.thanExtViewPort()

#------Initialise min,max with first element

        if lays == "all": lays = list(self.thanLayerTree.dilay.values())   #works for python2,3
        #lays = [(lay.thanAtts["draworder"].thanVal, lay) for lay in lays]
        #lays.sort()
        #lays = [lay for i,lay in lays]
        lays.sort(key=lambda lay: lay.thanAtts["draworder"].thanVal)
        for lay in lays:
            if lay.thanAtts["frozen"].thanVal: continue
            for e in lay.thanQuad:
                self.xMinAct = e.thanXymm[0]
                self.yMinAct = e.thanXymm[1]
                self.xMaxAct = e.thanXymm[2]
                self.yMaxAct = e.thanXymm[3]
                break
            else: continue
            break
        else:
            print("no elements found in active layers")
            self.thanAreaIterated = (None, None, None, None)    # No limit in all directions
            self.xMinAct = self.yMinAct = self.xMaxAct = self.yMaxAct = None
            return    # Drawing has no elements in active layers

#-------Now iterate through all elements of active layers

        for lay in lays:
            if lay.thanAtts["frozen"].thanVal: continue
            lay.thanTkSet(than)
            for e in lay.thanQuad:
                if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
                if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
                if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
                if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
                if e.thanInbox(xymm):
                    if e in than.markselected:   #Add the "selall" tag
                        temp = e.thanTags
                        e.thanTags = temp + ("selall",)
                        e.thanTkDraw(than)
                        e.thanTags = temp
                    else:
                        e.thanTkDraw(than)

#-------Compute limits of thanAreaIterated

        if xymm[0] <= self.xMinAct: xymm[0] = None
        if xymm[1] <= self.yMinAct: xymm[1] = None
        if xymm[2] >= self.xMaxAct: xymm[2] = None
        if xymm[3] >= self.yMaxAct: xymm[3] = None
        self.thanAreaIterated = tuple(xymm)
        self.thanLayerTree.thanCur.thanTkSet(than)


    def thanExtViewPort(self):
        "Extend the viewport twice and return it as a rectangle."
        xymm = self.viewPort
        dx = xymm[2] - xymm[0]
        dy = xymm[3] - xymm[1]
        return [xymm[0]-2*dx, xymm[1]-2*dy, xymm[2]+2*dx, xymm[3]+2*dy]   # xymm is a new list now: not viewPort.thanXymm


    def thanTkHiwin(self, than):
        "Lengthens (a little) very small elements so that they become visible."
        seen = set()
        tagel = self.thanTagel
        dc = than.dc
        for item in dc.find_all():
            tags = dc.gettags(item)
            if not tags: continue             # Sentinel elements
            titem = tags[0]
            if titem[0] != "E": continue      # not a ThanCad Element
            if titem in seen: continue
            seen.add(titem)
            el = tagel[titem]
            el.thanTkHiwin(than)


#===========================================================================

    def thanMoveSel(self, elems, dc):
        "Moves the selected elements."
        if all(dc1==0.0 for dc1 in dc): return
        for e in elems:
            e.thanMove(dc)
            if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
            if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
            if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
            if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
        self.thanTouch()

    def thanCopySel(self, elems, dc):
        "Copies the selected elements with offset."
        lt = self.thanLayerTree
        thanCur1 = lt.thanCur
        dilay = lt.dilay
        copelems = []
        for e in elems:
            lt.thanCur = dilay[e.thanTags[1]]
            e1 = e.thanClone()
            e1.thanUntag()                 #Make invalid thanTags and handle
            e1.thanMove(dc)
            self.thanElementAdd(e1)
            copelems.append(e1)
        lt.thanCur = thanCur1
        self.thanTouch()
        return copelems

    def thanRotateSel(self, elems, cc, phi):
        "Rotates the selected elements."
        if phi == 0.0: return
        if cc == "i":
            for e in elems:
                cc = e.getInspnt()
                ThanElement.thanRotateSet(cc, phi)
                e.thanRotate()
                if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
                if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
                if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
                if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
        else:
            ThanElement.thanRotateSet(cc, phi)
            for e in elems:
                e.thanRotate()
                if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
                if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
                if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
                if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
        self.thanTouch()


    def thanMirrorSel(self, elems, c1, t):
        "Mirrors the selected elements."
        ThanElement.thanMirrorSet(c1, t)
        for e in elems:
            e.thanMirror()
            if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
            if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
            if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
            if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
        self.thanTouch()


    def thanPointMirSel(self, elems, c1):
        "Mirrors the selected elements with respect to a point."
        ThanElement.thanPointMirSet(c1)
        for e in elems:
            e.thanPointMir()
            if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
            if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
            if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
            if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
        self.thanTouch()


    def thanScaleSel(self, elems, cc, fact):
        "Scales the selected elements."
        if fact == 1.0: return
        if cc == "i":
            for e in elems:
                cc = e.getInspnt()
                e.thanScale(cc, fact)
                if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
                if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
                if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
                if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
        else:
            for e in elems:
                e.thanScale(cc, fact)
                if e.thanXymm[0] < self.xMinAct: self.xMinAct = e.thanXymm[0]
                if e.thanXymm[1] < self.yMinAct: self.yMinAct = e.thanXymm[1]
                if e.thanXymm[2] > self.xMaxAct: self.xMaxAct = e.thanXymm[2]
                if e.thanXymm[3] > self.yMaxAct: self.yMaxAct = e.thanXymm[3]
        self.thanTouch()

#===========================================================================

    def thanDelSel(self, elems):
        "Deletes elements from the drawing as simply as possible."
        if len(elems) == 0: return
        taglay = self.thanLayerTree.dilay
        for e in elems:
            lay = taglay[e.thanTags[1]]
            lay.thanQuad.remove(e)
            del self.thanTagel[e.thanTags[0]]
        self.thanTouch()


    def thanDelSelMany(self, elems):
        """Deletes a large number of elements efficiently from the drawing.

        This should be faster if the number of elements to delete are,
        say, over 10000. Again, this is not certain without actual test.
        """
        taglay = self.thanLayerTree.dilay
        elay = {}
        for e in elems:
            elay.setdefault(e.thanTags[1], set()).add(e)
            del self.thanTagel[e.thanTags[0]]
        for tlay,eset in elay.items():   #works for python2,3
            lay = taglay[tlay]
            lay.thanQuad -= eset
        self.thanTouch()


    def thanElementRestore(self, elems, proj):
        """Restores previously deleted elements as simply as possible.

        It is assumed that the elements' structure is already in legal state, and that
        the layer they belong to is also in legal state.
        FIXME: maybe it will be faster to sort by layer first, and call lay.thanTkSet
        less times.
        """
        if len(elems) == 0: return
        taglay = self.thanLayerTree.dilay
        than = proj[2].than
        for e in elems:
            lay = taglay[e.thanTags[1]]
            lay.thanTkSet(than)
            self.__elementAddHouse(e, lay)
            if not lay.thanAtts["frozen"].thanVal:
                e.thanTkDraw(than)
                if isinstance(e, ThanImage): than.thanImages.add(e)
        self.thanTouch()
        self.thanLayerTree.thanCur.thanTkSet(than)


    def thanElementDelete(self, elems, proj):
        "Deletes elements from the drawing and canvas as simply as possible, leaving structures intact."
        taglay = self.thanLayerTree.dilay
        dc = proj[2].thanCanvas
        for e in elems:
            lay = taglay[e.thanTags[1]]
            lay.thanQuad.remove(e)
            dc.delete(e.thanTags[0])
            if isinstance(e, ThanImage): proj[2].thanImages.remove(e)
        self.thanTouch()

#===========================================================================

    def thanIsModified(self):
        "Returns true if drawing has been modified since last save."
        return self.__modified
    def thanResetModified(self):
        "Informs that drawing has just been saved or read and so it is unmodified."
        self.__modified = 0
    def thanTouch(self):
        "Make the drawing as it it were modified."
        self.__modified = True

#===========================================================================

    def thanExpDxf(self, fout):
        "Exports all the elements of the drawing to dxf file."
        dxf = p_gdxf.ThanDxfPlot()
        dxf.thanDxfPlots1(fout, vars=self.__calcVars())
        dxf.thanDxfTableDef (' ', 0)

        dxf.thanDxfTableDef('LAYER', 1)
        self.thanLayerTree.thanExpDxf(dxf)        # export layers

        dxf.thanDxfTableDef('ENTITIES', 1)
        dxf.than = than = p_ggen.Struct()
        than.pointsize = 0.14       #cm
        than.scale = 500.0 / 100.0  #scale 1:500
        for lay in self.thanLayerTree.dilay.values():   #works for python2,3
            layname = lay.thanGetPathname("__")
            dxf.thanDxfSetLayer(layname)
            than.layname = layname  #Active layername is needed by namedpoint
            than.fill = lay.thanAtts["fill"].thanVal   #Needed by ThanLineFilled element
            for e in lay.thanQuad:
                e.thanExpDxf(dxf)
        dxf.thanDxfPlot(0.0, 0.0, 999)
        return True, ""


    def __calcVars(self):
        "Determine the values of dxf variables."
        lays = [self.thanLayerTree.thanRoot]
        leaflayers = []
        while len(lays) > 0:
            lay = lays.pop(0)
            if len(lay.thanChildren) > 0: lays.extend(lay.thanChildren)
            else:                         leaflayers.append(lay)
        vars = []
        nfillon = 0
        for lay in leaflayers:
            ia = lay.thanAtts["fill"]
            if ia.thanVal: nfillon += 1
        if nfillon == len(leaflayers): vars.append(("$FILLMODE", 70, 1))
        else:                          vars.append(("$FILLMODE", 70, 0))
        return vars


    def thanExpSyk(self, fSyk):
        "Exports all the linear elements of the drawing to syk file."
        than = p_ggen.Struct("ThanCad .syk file and options container")
        than.write = fSyk.write
        for lay in self.thanLayerTree.dilay.values():   #works for python2,3
            than.layname = lay.thanGetPathname("__")
            for e in lay.thanQuad:
                e.thanExpSyk(than)
        return True, ""


    def thanExpBrk(self, fSyk):
        "Exports all the linear elements of the drawing to brk file."
        than = p_ggen.Struct("ThanCad .brk file and options container")
        than.write = fSyk.write
        than.ibr = 0
        than.form = "THC%07d%15.3f%15.3f%15.3f\n"
        for lay in self.thanLayerTree.dilay.values():   #works for python2,3
            than.layname = lay.thanGetPathname("__")
            for e in lay.thanQuad:
                e.thanExpBrk(than)
        return True, ""


    def thanExpSyn(self, fSyk):
        "Exports all the point of the drawing to syn file."
        than = p_ggen.Struct("ThanCad .syn file and options container")
        than.write = fSyk.write
        than.ibr = 0
        than.form = "THC%07d%15.3f%15.3f%15.3f\n"     #normal point
        than.formnam = "%-10s%15.3f%15.3f%15.3f\n"    #named point
        for lay in self.thanLayerTree.dilay.values():    #works for python2,3
            than.layname = lay.thanGetPathname("__")
            for e in lay.thanQuad:
                e.thanExpSyn(than)
        return True, ""


    def thanExpKml(self, fSyk):
        "Exports all the point of the drawing to a Google kml file."
        than = p_ggen.Struct("ThanCad .syn file and options container")
        than.kml = fSyk
        than.ibr = 0
        than.form = "THC%07d"     #normal point
#        p_gimgeo.writeKmlInit(than.kml)
        than.kml = p_gimgeo.ThanKmlWriter(fSyk)
        for lay in self.thanLayerTree.dilay.values():  #works for python2,3
            than.layname = lay.thanGetPathname("__")
            for e in lay.thanQuad:
                e.thanExpKml(than)
        than.kml.close()
        return True, ""


    def thanPlotPdf(self, scale):
        "Plots all elements of the drawing to pdf file."
        import pyx
        than = p_ggen.Struct("ThanCad .pdf file and options container")
        than.dc = pyx.canvas.canvas()
        than.ct = ThanRectCoorTransf()
        x1 = y1 = 0.0
        x2 = y2 = 1.0
        than.ct.set((x1, y1, x2, y2), (0, 0, (x2-x1)*scale, (y2-y1)*scale))
        for lay in self.thanLayerTree.dilay.values():   #works for python2,3
            lay.thanPdfSet(than)
            for e in lay.thanQuad:
                e.thanPlotPdf(than)
        return than


    def thanExpPil(self, filpath, mode, width, height, drwin, bcol):
        "Exports the circle to a PIL raster image."
        than = p_ggen.Struct("ThanCad PIL image and options container")
        page = 19.5, 29.5
#        dpi = 300.0 #120.0
#        imsize = [int(p*dpi/2.54+0.5) for p in page]
#        than.mode = "RGB"

        than.mode = mode
        imsize = width, height
        dpi = imsize[1]/(page[1]/2.54)
        than.pixpermm = dpi/25.4
        than.dash = []
#        bcol = bcol.thanVal
#        if than.mode == "1":
#            bcol = thanRgb2Gray(bcol)
#            if bcol < 128: bcol = 0
#            else:          bcol = 255
#        elif than.mode == "L":
#            bcol = thanRgb2Gray(bcol)
        than.bcol = bcol
        bcolpil = col2tuple(than.bcol, than.mode)
        if than.mode != "RGB": bcolpil = bcolpil[0]    #If gray or b/w PIL needs one integer
        than.im = p_gimage.new(than.mode, imsize, bcolpil)
        if isinstance(than.im, p_gimage.ThanImageMissing): raise ValueError("Python module Image/Pillow was not found")
        ib, ih = than.im.size
        than.viewPort = x1, y1, x2, y2 = self.__roundCenter(self.viewPort, (0, ih, ib, 0))
        than.dc = p_gimage.Draw(than.im)
        than.ct = ThanRectCoorTransf()
        than.ct.set((x1, y1, x2, y2), (0, ih, ib, 0))
        than.imageFrameOn = self.thanVar["imageframe"]
        than.imageBrightness = 1.0     #FIXME: it should be equal to proj[2].than.imageBrightness
        than.thanTstyles = self.thanTstyles                # Just a reference
        than.thanLtypes  = self.thanLtypes                 # Just a reference
#        than.fill = ThanAttCol("red").thanVal
#        than.outline = ThanAttCol("yellow").thanVal
#        than.width = int((9+1)/2)    # for the bugged version of ThanLine.thanExpPil()
#        than.width = 0
#        f = p_gimage.load_path("/home/a12/work/tcadtree.23/grhelv-b-10.pil")
#        than.font = f

        lays = list(self.thanLayerTree.dilay.values())   #works for python2,3
        #lays = [(lay.thanAtts["draworder"].thanVal, lay) for lay in lays]
        #lays.sort()
        #lays = [lay for i,lay in lays]
        lays.sort(key=lambda lay: lay.thanAtts["draworder"].thanVal)
        for lay in lays:
            if lay.thanAtts["frozen"].thanVal: continue
            lay.thanPilSet(than, dpi)
            print("PIL: outline=", than.outline)
            than.width  = int(than.rwidth + 0.5)
            than.widthline = int((than.width+1)/2)               # Get around PIL bug for line width
            i2 = int(than.width/2)
            i1 = -i2
            if i2-i1+1 > than.width: i1 += 1
            than.widtharc = i1, i2+1                             # Simulate widths in ars, circles
            assert than.width == than.widtharc[1]-than.widtharc[0]
            for e in lay.thanQuad:
                e.thanExpPil(than)

        del than.dc
        x1, y1, x2, y2 = self.viewPort
        ix1, iy1 = than.ct.global2Locali(x1, y2)  # PIL need left,upper and ..
        ix2, iy2 = than.ct.global2Locali(x2, y1)  # ..right,lower
        box = ix1, iy1, ix2, iy2
        im1 = than.im.crop(box)                   # Crop lines etc. outside the user defined window.
#        im1 = im1.filter(p_gimage.SMOOTH)
        than.im = p_gimage.new(than.mode, imsize, bcolpil)
        than.im.paste(im1, box)
        than.im.save(filpath)


    def __roundCenter(self, w, pixPort):
        "Rounds an abstract window w, so that it fits exactly to the actual (GuiDependent) window."
        return thanRoundCenter(w, pixPort, per=0)   #After testinf delete following code
        xa, ya, xb, yb = pixPort
        wpi = abs(xb - xa)
        hpi = abs(yb - ya)
        wun = w[2] - w[0]
        hun = w[3] - w[1]

        per = 6
        if wpi < 10*per or hpi < 10*per: per = 0
        per = 0
        sx = float(wpi - per) / wun
        sy = float(hpi - per) / hun
        if sy < sx: sx = sy

        dx = (wpi / sx - wun) * 0.5
        dy = (hpi / sx - hun) * 0.5
        return w[0]-dx, w[1]-dy, w[0]+wun+dx, w[1]+hun+dy


    def thanRepair(self):
        "Try to create some new objects that were not present in older versions of .thc."
        pass


if __name__ == "__main__":
    print(__doc__)
