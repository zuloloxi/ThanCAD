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

This module defines a hierarchical layer structure (class).
Each layer has a set of attributes. It is very easy to extend this set.
Each attribute has a type which defines the way the attribute is
inherited by a layer's children. Actually the layer does not care
what the attributes mean (i.e. color of elements, line type and
so on).
When an attribute is changed the layer class calls method thanUpdateElements
to do what is needed (e.g. change the color of the elements).
thanUpdateElements is inherited by ThanLayAtts.
"""
import weakref, copy
import p_ggen, p_gcol
from thanvar import ThanLayerError, THANBYPARENT, THANPERSONAL
from thandefs import ThanId
from thanopt import thancadconf

from .thanlaycon import THANNAME
from .thanlayername import checkLayerName, repairLayerUniq, isLayerUniq
from thanopt.thancon import THANLC
from . import thanlayatts


THANMRECURS = 20          # Maximum layer tree depth

############################################################################
############################################################################


def col2tuple(bg, mode):
    "Convert colour attribute to RGB, gray or black and white colour; output is an RGB tuple."
    if mode == "RGB":
        bg = bg.thanVal
    elif mode == "L":
        bg = bg.than2Gray()
        bg = bg, bg, bg
    elif mode == "1":
        bg = bg.than2Gray()
        if bg < 255: bg = 0                     # Everything is black except pure white
        bg = bg, bg, bg
    else:
        assert 0, "unknown mode '%s'" % (mode,)
    return bg


class ThanLayer(object):
    "Class that holds the information of a layer object."

    def __init__(self):
        "Creates a layer node object."
        pass


    def thanGetColour(self, bg=None, mode="RGB", format="tk"):
        "Return the colour of the layer, taking into account the background colour."
        ats = self.thanAtts
        if bg is None: bg = thancadconf.thanColBack
        bg = col2tuple(bg, mode)
        col = col2tuple(ats["moncolor"], mode)
        if bg == (0,0,0):   #If background is black and layer's color is also black, turn color to white
            if col == (0,0,0): col = 255,255,255
        elif bg == (255,255,255): #If background is white and layer's color is also white, turn color to black
            if col == (255,255,255): col = 0,0,0
        if format == "tk":
            fill = outline = p_gcol.thanFormTkcol % col
        elif format == "pil":
            if mode == "RGB": fill = outline = col
            else:             fill = outline = col[0]    #If gray or b/w PIL needs one integer
        else:
            fill = outline = col
        if not ats["fill"].thanVal: fill = None
        return outline, fill


    def thanTkSet(self, than):
        "Sets the drawing attributes according to layer."
        ats = self.thanAtts
        than.outline, than.fill = self.thanGetColour()   #default format is tk, mode is RGB, bg is canvas background
#        col = ats["moncolor"].thanTk
#        bg = str(thancadconf.thanColBack)
#        if bg == "black":   #If background is black and layer's color is also black, turn color to white
#            if str(ats["moncolor"]) == "black": col = "white"
#        elif bg == "white": #If background is white and layer's color is also white, turn color to black
#            if str(ats["moncolor"]) == "white": col = "black"
#        than.fill = than.outline = col
#        if not ats["fill"].thanVal: than.fill = ""

        t = ats["textstyle"].thanVal
        than.font = than.thanTstyles[t].thanFont
        namlt, unit, scale = ats["linetype"].thanVal
        if namlt not in than.thanLtypes: namlt = "continuous"   #If line type is not found use continuous as default
        than.thanLtypes[namlt].thanTkSet(than, unit, scale)
        namlt, unit, scale = ats["dimstyle"].thanVal
        if namlt not in than.thanDimstyles: namlt = "standard"  #If dimension style is not found use standard as default
        than.thanDimstyles[namlt].thanTkSet(than, unit, scale)

        than.pointPlotname   = not ats["hidename"].thanVal
        than.pointPlotheight = not ats["hideheight"].thanVal

        # Note that penthickness in mm is irrelevent unless we know the dimensions of the screen
        temp = ats["penthick"].thanVal * than.pixpermm   #Thanasis2018_07_01: pixelpermm is calculated when a new drawing is created
                                                         #Perhaps it should be update in every regen
        than.tkThick, _ = than.ct.global2LocalRel(ats["linethick"].thanVal, 0.0)
        than.tkThick = max(than.tkThick, temp)

        for a in thanlayatts.thanLayAttsNames[2:]:
            ia = ats[a]
            ia.thanAct = ia.thanVal


    def thanDxfSet(self, than):
        "Sets the drawing attributes for a dxf file according to layer."
        ats = self.thanAtts
        than.layname = self.thanGetPathname(THANLC)  #Active layername is needed by namedpoint
        than.fill = ats["fill"].thanVal   #Needed by ThanLineFilled element
        t = ats["textstyle"].thanVal
        than.font = than.thanTstyles[t].thanFont
        namlt, unit, scale = ats["dimstyle"].thanVal
        if namlt not in than.thanDimstyles: namlt = "standard"  #If dimension style is not found use standard as default
        than.thanDimstyles[namlt].thanDxfSet(than, unit, scale)


    def thanPilSet(self, than, dpi):
        "Sets the drawing attributes for a PIL image according to layer."
        than.outline, than.fill = self.thanGetColour(than.bcol, than.mode, "pil")
        ats = self.thanAtts
#        c = ats["moncolor"].thanVal
#        if than.mode == "1" or than.mode == "L":
#            c = int(c[0]*0.299+c[1]*0.587+c[2]*0.114+0.49)   # Convert to gray
#            if than.mode == "1":
#                if c < 255: c = 0                            # Everything is black except pure white
#            black = 0
#            white = 255
#        else:
#            black = 0,0,0
#            white = 255,255,255
#
#        if than.bcol == black:   #If background is black and layer's color is also black, turn color to white
#            if c == black: c = white
#        elif than.bcol == white: #If background is white and layer's color is also white, turn color to black
#            if c == white: c = black
#
#        than.fill = than.outline = c
#        if not self.thanAtts["fill"].thanVal: than.fill = None

        t = ats["textstyle"].thanVal
        than.font = than.thanTstyles[t].thanFont
        namlt, unit, scale = ats["linetype"].thanVal
        if namlt not in than.thanLtypes: namlt = "continuous"   #If line type is not found use continuous as default
        than.thanLtypes[namlt].thanTkSet(than, unit, scale)
        namlt, unit, scale = ats["dimstyle"].thanVal
        if namlt not in than.thanDimstyles: namlt = "standard"  #If dimension style is not found use standard as default
        than.thanDimstyles[namlt].thanTkSet(than, unit, scale)

        than.pointPlotname   = not ats["hidename"].thanVal
        than.pointPlotheight = not ats["hideheight"].thanVal

        w1, _ = than.ct.global2LocalRel(ats["linethick"].thanVal, 0.0)
        w2 = ats["penthick"].thanVal*dpi/25.4
        than.rwidth = max(w1, w2)


    def thanPdfSet(self, than):
        "Sets the drawing attributes for a PIL image according to layer."
        t = self.thanAtts["textstyle"].thanVal
        than.font = than.thanTstyles[t].thanFont
        return
        c = self.thanAtts["moncolor"].thanVal
        if   c == (255,255,255): c = 0,0,0            # Invert white and ..
        elif c == (  0,  0,  0): c = 255,255,255      # ..black
        if than.mode == "1":
            c = int(c[0]*0.299+c[1]*0.587+c[2]*0.114+0.49)   # Convert to gray
            if c < 255: c = 0                                # Everything is black except pure white
        elif than.mode == "L":
            c = int(c[0]*0.299+c[1]*0.587+c[2]*0.114+0.49)   # Convert to gray
        than.fill = than.outline = c
        if not self.thanAtts["fill"].thanVal: than.fill = ""


    def thanRename(self, name):
        "Renames a layer."
        root = self
        while root.thanParent is not None: root = root.thanParent   #find root
        delnot = set((root, root.thanChildren[0]))   # Layers which must not be deleted/renamed
        if self in delnot:
            nameold = self.thanAtts[THANNAME].thanVal.strip()
            raise ThanLayerError("Can not rename layer '{}'".format(nameold))

        name = name.strip()
        terr = checkLayerName(name)          # Check name
        if terr != "": raise ThanLayerError("Illegal layer name '{}': {}".format(name, terr))
        if self.thanParent is not None:               # Root layer has no parent and no siblings
            for lay in self.thanParent.thanChildren:
                if str(lay.thanAtts[THANNAME]) == name:        # Check unique name
                    raise ThanLayerError("Duplicate layer name '{}'".format(name))
        self.thanAtts[THANNAME].thanVal = name
        self.thanAtts[THANNAME].thanPers = name


    def thanRenametest(self, name):
        "Rename a layer, and return string error message if unsuccessful."
        try:
            self.thanRename(name)
        except ThanLayerError as e:
            return str(e)
        return self


    def thanUnlink(self):
        """Unlinks the hierarchy beginning with self from the children of self's parent."

        This is dangerous because the elements of the self will become
        orphans. This may lead the program to crash. So it must be used
        only if we know that there are no elements in the hierarchy.
        Or, the hierarchy must be inserted somewhere else.
        Note that the hierarchy is only unlinked; it is not deleted.
        """
        par = self.thanParent
        assert par is not None, "Well we can't delete root layer. How on earth was root accessed?!"
        i = par.thanChildren.index(self)
        del par.thanChildren[i]
        return self

    def thanDestroy(self):
        """Destroys the circular references, so that layer can be recycled.

        This is dangerous because the elements of self and of all children
        of self, will become orphans. This may lead to program crash.
        So it must be used only if we know that there are no elements in
        the hierarchy. Or, the hierarchy must be inserted somewhere else.
        Or that we have an exact copy so that the elements will have
        the copy as a parent."""
        for chlay in self.thanChildren: chlay.thanDestroy()
        del self.thanChildren
        del self.lt, self.thanParent

    def thanChildAdd(self, lays):
        """Adds some lays as children of self.

        lays are complete layer hierarchies and they are assumed to be ok,
        except from their parent.
        If a name of lays duplicates one of self's current children, we try
        to rename it. If all renames are succesful, we add the children."""

        if len(lays) <= 0: return
        names = [str(lay.thanAtts[THANNAME]) for lay in self.thanChildren]
        namen = {}
        for lay in lays:
            name = str(lay.thanAtts[THANNAME]).strip()
            terr = checkLayerName(name)          # Check name
            if terr != "": raise ThanLayerError("Illegal layer name '{}': {}".format(name, terr))
            name1, terr = repairLayerUniq(name, names)
            if name1 is None: raise ThanLayerError(terr+"; Try to rename some layers.")
            namen[lay] = name1
            names.append(name1)

        self.thanMove2child()     # If childless, move all elements to a new child
        for lay in lays:
            lay.thanAtts[THANNAME].thanVal = namen[lay]
            lay.thanAtts[THANNAME].thanPers = namen[lay]
            self.thanChildren.append(lay)
            lay.thanParent = self


#===========================================================================

    def thanChildNew(self, name=None, atts=None):
        "Creates a new child layer; if something is wrong, an exception is raised and no changes are made."
        if self.__getDepth() > THANMRECURS: raise ThanLayerError("Layer nested too deep.")
        chlay = self.__newEmptyLeaf(name, atts)  # Create child here to check for error early
        self.thanMove2child()                    # If self is leaf, create new child which inherits the elements
        self.thanChildren.append(chlay)          # Now, add an empty child
        return chlay


    def __newEmptyLeaf(self, name, atts=None):
        """Creates a new empty leaf layer, intended to be child of self.

        The newly created has self as parent, but it does not belong
        to self's children yet.
        The attributes of the newly created layer are an exact copy of the
        attributes of self through inheritance.
        If atts is defined, the attributes will be taken from there, as
        well as the inherit switch.
        """

#-------Check name or try to find a unique name

        if name is not None:
            names = [str(lay.thanAtts[THANNAME]) for lay in self.thanChildren]
            name = name.strip()
            terr = checkLayerName(name)          # Check name
            if terr != "": raise ThanLayerError("Illegal layer name '{}': {}".format(name, terr))
            if not isLayerUniq(name, names): raise ThanLayerError("Duplicate layer name '{}'".format(name))
        else:
            name = self.thanChildUniqName()

#-------Create new layer

        lay = ThanLayer()
        lay.lt = self.lt
        lay.thanParent = self
        lay.thanChildren = []
        lay.thanTag = self.lt.thanIdLay.new()  # In order to exploit TK mechanism
        lay.thanQuad = set()                   # This holds the elements of the layer

        copyinher = atts is not None
        if atts is None: atts = self.thanAtts
        lay.thanAtts = {}
        for a, val in thanlayatts.thanLayAtts.items():   #works for python2,3
            defval = atts[a].thanPers
            class_ = val[3]
            lay.thanAtts[a] = class_(defval)
            lay.thanAtts[a].thanValSet(atts[a].thanVal)
            if copyinher: lay.thanAtts[a].thanInher = atts[a].thanInher
        lay.thanAtts[THANNAME].__init__(name, False)         #Make sure that name is not inherited
        return lay


    def thanChildUniqName(self):    #needed by p_gtkwid.thantkcli.py
        "Return a unique child name (not equal to other children)."
        names = [str(lay.thanAtts[THANNAME]) for lay in self.thanChildren]
        name, terr = repairLayerUniq("newlayer", names, forcedigit=True)
        if name is None: raise ThanLayerError(terr+"; Try to rename some layers.")
        return name


    def thanMove2child(self, name=None, force=False):
        """Move elements to a child.

        If self is childless, a child is created which inherits the tag of
        self and, thus, its elements. Self gets no tag and, thus, it has
        no elements.
        If layer has no elements then no child is created.
        """
        if len(self.thanChildren) > 0: return
        if not force and len(self.thanQuad) == 0: return
        if self.__getDepth() > THANMRECURS: raise ThanLayerError("Layer nested too deep.")
        if name is None: name = str(self.thanAtts[THANNAME])+"child"
        lay = self.__newEmptyLeaf(name)  # No errors expected

        lay.thanQuad = self.thanQuad               # inherit self's elements
        lay.thanTag = self.thanTag                 # inherit self's elements
        self.thanQuad = self.thanTag = None        # parents do not have elements
        self.thanChildren = [lay]
        return lay

    def __getDepth(self):
        "Finds the nested level of layer."
#       Note that when ThanCad displays the layer control widget, the parent of layer "0"
#       is not self.lt.thanRoot, but another root layer, created temporarily for the widget.
#       So we check for root layer with the condition:    lay.thanParent == None
        par = self
        for i in range(THANMRECURS):
            if par.thanParent  is None: return i
            par = par.thanParent
        return THANMRECURS + 1

    def thanClone(self, parent=None):
        """Creates a new layer hierarchy copying self's children.

        This routine copies only the hierarchy including tags. It does not
        copy elements, it copies only a reference to the structure that holds
        the elements.
        In effect the new layer is created with the same name, parent, tag,
        attributes, with the same (cloned) children and references to the
        same elements.
        """
        lay = ThanLayer()
        lay.lt = self.lt
        if parent is None: lay.thanParent = self.thanParent
        else             : lay.thanParent = parent

        lay.thanTag = self.thanTag                 # In order to exploit TK mechanism
        lay.thanQuad = self.thanQuad               # This holds the elements of the layer

        lay.thanAtts = copy.deepcopy(self.thanAtts)
        lay.thanChildren = [chlay.thanClone(lay) for chlay in self.thanChildren]
        return lay


    def __del__(self):
        print("Memory of layer", str(self.thanAtts[THANNAME]), " is recycled")

    def thanSetAtts(self, leaflayers, attname, newval):
        "Sets the attributes of the layer self, propagates the attributes and returns the leaflayers affected."
        for a,val in (attname, newval),:
            assert a in thanlayatts.thanLayAtts, "Unknown layer attribute: " + a
            ia = self.thanAtts[a]
            if val == THANBYPARENT:
                if self.thanParent is None: continue       # Root element can't inherit
                ia.thanInher = True
                val = self.thanParent.thanAtts[a].thanVal  # The parent's attribute (which ISN'T THANBYPARENT)
            elif val == THANPERSONAL:
                ia.thanInher = False
                val = ia.thanPers
            else:
                val = val.thanVal
                ia.thanInher = False
                ia.thanPers = val

            if val == ia.thanVal: continue                 # Happens to have the correct value
            ia.thanValSet(val)
            if len(self.thanChildren) == 0:                # No children - leaf ThanLayer.
                leaflayers.setdefault(self, {})[a] = val
            else:                                          # Only leaf ThanLayer has elements
                if thanlayatts.thanLayAtts[a][0] == 0:                 # Propagate this value to the children..
                    self.thanPropAttByParent(leaflayers, a, val) # Propagate only if by parent
                else:
                    self.thanPropAttForce(leaflayers, a, val)    # Propagate unconditionally


    def thanPropAttByParent(self, leaflayers, a, val):
        "Propagates an attribute of type 0 to the layer's children, if by parent."
        lay2see = self.thanChildren[:]   # These layers (and their children) must be inspected
        while len(lay2see) > 0:
            lay = lay2see.pop()
            ia = lay.thanAtts[a]
            if not ia.thanInher: continue                # Child Layer does not inherit
            if lay.thanAtts[a].thanVal == val: continue  # Child Layer happens to have the correct value
            ia.thanValSet(val)
            if len(lay.thanChildren) == 0:
                leaflayers.setdefault(lay, {})[a] = val  # only leaf ThanLayer has elements
            else:
                lay2see.extend(lay.thanChildren)


    def thanPropAttForce(self, leaflayers, a, val):
        "Propagates an attribute of type 1,2 to the layer's children, while not resetting the values."
        lay2see = self.thanChildren[:]   # These layers (and their children) must be inspected
        while len(lay2see) > 0:
            lay = lay2see.pop(0)
            if val: val1 = val           # If val==False
            else:   val1 = lay.thanAtts[a].thanPers        # Attribute can not be inherited
            if lay.thanAtts[a].thanVal == val1: continue   # Layer already with this value
            lay.thanAtts[a].thanValSet(val1)
            if len(lay.thanChildren) == 0:
                leaflayers.setdefault(lay, {})[a] = val1   # only leaf ThanLayer has elements
            else:
                lay2see.extend(lay.thanChildren)


    def thanPropAttAll(self, leaflayers, a, val):
        """Sets attribute a (of type 0) to self and all children.

        The attribute of a is set as personal. The attributes of the children
        are set as inherited."""
        assert thanlayatts.thanLayAtts[a][0] == 0, "thanPropAttAll() works for type 0 attributes."
        ia = self.thanAtts[a]
        ia.thanValSet(val)
        ia.thanPers = ia.thanVal
        ia.thanInher = False
        lay2see = self.thanChildren[:]   # These layers (and their children) must be inspected
        while len(lay2see) > 0:
            lay = lay2see.pop(0)
            ia = lay.thanAtts[a]
            ia.thanValSet(val)
            ia.thanInher = True
            if len(lay.thanChildren) == 0:
                leaflayers.setdefault(lay, {})[a] = val   # only leaf ThanLayer has elements
            else:
                lay2see.extend(lay.thanChildren)


#===========================================================================

#    def thanPropAttRestore(self, a, val):
#        "Propagates and restores attribute of the layer's children."
#
#        layers = [ ]
#        lay2see = self.thanChildren[:]
#        while len(lay2see) > 0:
#            lay = lay2see.pop()
#            if len(lay.thanChildren) == 0:
#                if lay.thanAtts[a] != val: layers.append(lay)      # only leaf ThanLayer has elements
##           else:
#                lay2see.extend(lay.thanChildren)
#
##-------Group layers with the same value
#
#        while len(layers) > 0:
##           lay = layers.pop()
#            val = lay.thanAtts[a]
#            layersSameVal = [lay]
#            layersOtherVal = [ ]
#            while len(layers) > 0:
#                lay = layers.pop()
#                if lay.thanAtts[a] == val:
#                    layersSameVal.append(lay)
#                else:
#                    layersOtherVal.append(lay)
#
#            self.thanUpdateElements(layersSameVal, a, val)       # Update all the layers with the same value
#            layers = layersOtherVal
#


    def thanExpDxf(self, fDxf, pref):
        "Exports this layer and its children to dxf."
        e = fDxf.thanDxfCrLayer
        a = None                       #In case there are no children and thus the for is not executed (and the delete)
        for lay in self.thanChildren:
            if len(lay.thanChildren) > 0: continue   #Parent do not have elements
            a = lay.thanAtts
            e(name=pref+str(a[THANNAME]), color=a["moncolor"].thanDxf(), frozen=a["frozen"].thanVal)
        del e, a                       #Save memory before recursive call
        for lay in self.thanChildren:
            if len(lay.thanChildren) == 0: continue  #No children; avoid unneeded recursive call
            lay.thanExpDxf(fDxf, pref+str(lay.thanAtts[THANNAME])+THANLC)


    def thanExpThc(self, fw):
        "Save the layer in thc format."
        fw.writeBeg("LAYER")
        fw.pushInd()
        fw.writeAttb("path", self.thanGetPathname())
        for nam, a in self.thanAtts.items():   #works for python2,3
            a.thanExpThc(fw, nam)
        fw.popInd()
        fw.writeEnd("LAYER")
        for lay in self.thanChildren:
            lay.thanExpThc(fw)


    def thanImpThc(self, fr, ver, than):
        "Read the layer attributes from .thcx file."
        fr.readBeg("LAYER")
        if ver < (0,2,0): pname = fr.readAtt("path")[0]
        else:             pname = fr.readAttb("path")
        while True:
            dl = next(fr).strip().split()
            fr.unread()
            if dl[0] == "</LAYER>": break
            namatt = dl[0].strip("<>")
            if namatt not in self.thanAtts: raise ValueError("Unknown layer attribute: %s" % (namatt,))
            if namatt == "linetype" and ver < (0,2,0):
                next(fr)    #Ignore linetype attribute; use default value ("continuous", mm, 1.0)
                continue
            self.thanAtts[namatt].thanImpThc(fr, ver, namatt)

            if namatt == "textstyle" and self.thanAtts[namatt].thanVal not in than.thanTstyles:
                tdef = "standard"
                than.prt("Substituting '{}' for text style '{}'".format(tdef, self.thanAtts[namatt].thanVal), "can1")
                self.thanAtts[namatt].__init__(tdef, self.thanAtts[namatt].thanInher)

        fr.readEnd("LAYER")
        return pname


    def thanGetPathname(self, sep="/"):
        "Compute the full pathname of the layer - without the root name."
        if self.thanParent is None:        #This is the root layer
            return str(self.thanAtts[THANNAME])
        par = self
        i = 0
        m = THANMRECURS
        name = []
        while par.thanParent is not None:
            name.append(str(par.thanAtts[THANNAME]))
            par = par.thanParent
            i += 1
            if i > m: break      # Recursive limit found; return incomplete name
        name.reverse()
        return sep.join(name)


    def thanFind(self, names):
        "Finds a layer whose name, parent, grandparent .. are in names."
        for lay in self.thanChildren:
            if str(lay.thanAtts[THANNAME]) == names[0]:
                if len(names) == 1: return lay
                return lay.thanFind(names[1:])
        return None

    def thanFindic(self, names):
        "Finds a layer whose name, parent, grandparent .. are in names; ignore case."
        name0 = names[0].lower()
        for lay in self.thanChildren:
            if str(lay.thanAtts[THANNAME]).lower() == name0:
                if len(names) == 1: return lay
                return lay.thanFindic(names[1:])
        return None

    def thanIsEmpty(self):
        "Returns true if layer has no elements nor children, or no children with elements."
        if self.thanParent is None: return False     # Root layer is considered non-empty
        if len(self.thanChildren) == 0:
            return len(self.thanQuad) == 0
        for chlay in self.thanChildren:
            if not chlay.thanIsEmpty(): return False
        return True


    def thanMergeHier(self, cl, rootother):
        """Merges rootother hierarchy to self hierarchy.

        May raise ThanLayerError, in which case self may have part of the new layers."""
        than = p_ggen.Struct()
        than.other2lay = {}
        than.cl = cl
        try:
            for layother in rootother.thanChildren:
                self.thanMergeLay1(layother, than)
        except ThanLayerError as e:
            return None, None, e
        return than.other2lay, than.cl, ""


    def thanMergeLay1(self, layother, than):
        "Add child layer layother to self, if not already there."
        nameother = layother.thanAtts[THANNAME].thanVal
        nameother1 = nameother.lower()
        for lay in self.thanChildren:
            name = lay.thanAtts[THANNAME].thanVal.lower()
            if name != nameother1: continue
            than.other2lay[layother] = lay
            break
        else:
            if len(self.thanChildren) > 0:
                chlay1 = self.thanMove2child()
                chlay2 = self.thanChildNew(name=nameother, atts=layother.thanAtts)
                if than.cl is self: than.cl = chlay1 if chlay1 is not None else chlay2
            else:
                chlay2 = self.thanChildNew(name=nameother, atts=layother.thanAtts)
            than.other2lay[layother] = chlay2

        for chlayother in layother.thanChildren:
            than.other2lay[layother].thanMergeLay1(chlayother, than)

#===========================================================================

    def pr(self, a=None, b=""):
        if a is None:
            print(b, str(self.thanAtts[THANNAME]))
        else:
            ia = self.thanAtts[a]
            print(b, str(self.thanAtts[THANNAME]), ia.thanVal, "=", ia.thanAct, ia.thanPers, ia.thanInher)

        for lay in self.thanChildren:
            lay.pr(a, b+"    ")


############################################################################
############################################################################


class ThanLayerTree:
    "Class that holds a tree of layers."

    def __init__(self):
        "Creates the root of tree of layers."
        self.thanIdLay = ThanId(prefix="L")
        self.thanRoot = ThanLayer()
        self.thanMakeRoot(self.thanRoot)
        self.thanDictRebuild()


    def thanDestroy(self):
        "Break circular references."
        self.thanRoot.thanDestroy()
        del self.thanRoot, self.dilay


    def __getstate__(self):
        "Delete 'dilay' whioch is not pickle-able, so that the class is pickle-abe."
        odict = self.__dict__.copy()
        del odict["dilay"]         # Do not save weak dictionary (it is redundant after all)
        return odict


    def __setstate__(self, odict):
        "After unpickling recreate 'dilay'."
        self.__dict__.update(odict)
        self.thanDictRebuild()     # Recreate weak dictionary


    def thanDictRebuild(self, lay=None):
        "Rebuilds dictionary of tags to layers."
        if lay is None:
            self.dilay = weakref.WeakValueDictionary()
            lay = self.thanRoot
        if len(lay.thanChildren) == 0:   # Only leaf layers have elements (and tags)
            self.dilay[lay.thanTag] = lay
        else:
            for chlay in lay.thanChildren: self.thanDictRebuild(chlay)


    def thanMakeRoot(self, root, name="Root"):
        "Makes root the root of new layer tree."
#        root.lt = weakref.proxy(self)
        root.lt = self
        root.thanParent = None
        root.thanChildren = []
        root.thanTag = root.lt.thanIdLay.new()     # In order to exploit TK mechanism
        root.thanQuad = set()                      # This holds the elements of the layer

        root.thanAtts = {}
        for a,val in thanlayatts.thanLayAtts.items():   #works for python2,3
            defval = val[2]
            class_ = val[3]
            root.thanAtts[a] = class_(defval, False)
        root.thanAtts[THANNAME].__init__(name, False)   #Make sure the name is not inherited
        root.thanAtts["expand"].__init__("-", False)    #So that the first level layers are visible in layer control
        self.thanCur = root.thanChildNew("0")


    def thanFindAtt1old(self, att1, name1):
        "Find a layer of which the linetype name (or dimstyle name) is name1."
        assert att in ("linetype", "dimstyle"), "thanFindAtt1() only supports linetype and dimstyle attributes."
        def _findatt(laypar):
            if laypar.thanAtts[att1].thanVal[0] == name1: return laypar
            for lay in laypar.thanChildren:
                if _findatt(lay) is not None: return lay
            return None

        return findatt(self.thanRoot)


    def thanFindAtt1(self, att1, name1):
        "Find a layer of which the linetype name (or dimstyle name) is name1."
        assert att1 in ("linetype", "dimstyle"), "thanFindAtt1() only supports linetype and dimstyle attributes."
        stack = [self.thanRoot]
        while len(stack) > 0:
            lay = stack.pop()
            if lay.thanAtts[att1].thanVal[0] == name1: return lay
            stack.extend(lay.thanChildren)
        return None


    def thanFind(self, pathname):
        "Find the layer object from its pathname."
        names = pathname.split("/")
        return self.thanRoot.thanFind(names)


    def thanFindic(self, pathname):
        "Find the layer object from its pathname; ignore case."
        names = pathname.split("/")
        return self.thanRoot.thanFindic(names)


    def thanExpDxf(self, fDxf):
        "Exports this layer and its children to dxf."
#        e = fDxf.thanDxfCrLayer
#        a = self.thanRoot.thanAtts
#        e(name=THANLC+"root", color=a["moncolor"].thanDxf(), frozen=a["frozen"].thanVal)
#        del e, a
        self.thanRoot.thanExpDxf(fDxf, "")


    def thanExpThc(self, fw):
        "Save the layer tree in thc format."
        fw.writeBeg("LAYERTREE")
        fw.pushInd()
        fw.writeAttb("current", self.thanCur.thanGetPathname())
        self.thanRoot.thanExpThc(fw)
        fw.popInd()
        fw.writeEnd("LAYERTREE")


    def thanImpThc(self, fr, ver, than):
        "Read the layer from .thcx file."
        fr.readBeg("LAYERTREE")
        if ver < (0,2,0): pcur = fr.readAtt("current")[0]
        else:             pcur = fr.readAttb("current")

        lay = self.thanRoot
        pname = lay.thanImpThc(fr, ver, than)
        if pname != "Root": raise ValueError("Invalid root layer pathname: '%s'" % (pname,))
        if lay.thanAtts[THANNAME].thanVal != pname: raise ValueError("Layer pathname '%s' and name '%s' differ" % (pname, lay.thanAtts[THANNAME].thanVal))
        lay.thanAtts[THANNAME].__init__(pname, False)   #Make sure the name is not inherited
        lay.thanAtts["expand"].__init__("-", False)     #So that the first level layers are visible in layer control

        lay = self.thanRoot.thanChildren[0]
        pname = lay.thanImpThc(fr, ver, than)
        if pname != "0": raise ValueError("Invalid first layer pathname: '%s'. It should be '0'." % (pname,))
        if lay.thanAtts[THANNAME].thanVal != pname: raise ValueError("Layer pathname '%s' and name '%s' differ" % (pname, lay.thanAtts[THANNAME].thanVal))
        lay.thanAtts[THANNAME].__init__(pname, False)   #Make sure the name is not inherited

        while True:
            dl = next(fr).strip()
            fr.unread()
            if dl == "<LAYER>":
                lay = self.thanRoot.thanChildNew()   #make an empty layer, calling childnew() on root..
                del self.thanRoot.thanChildren[-1]   #..which is immediatly removed from root
                pname = lay.thanImpThc(fr, ver, than)
                names = pname.split("/")
                if lay.thanAtts[THANNAME].thanVal != names[-1]: raise ValueError("Layer pathname '%s' and name '%s' differ" % (pname, lay.thanAtts[THANNAME].thanVal))
                ppar = "/".join(names[:-1]).strip()
                if ppar == "":
                    laypar = self.thanRoot
                else:
                    laypar = self.thanFindic(ppar)
                    if laypar is None: raise ValueError("Parent of layer %s was not found" % (pname,))
                laypar.thanChildAdd([lay])  #May rename the layer name if duplicate, may raise ThanLayerError
                names[-1] = lay.thanAtts[THANNAME].thanVal   #In case thanChildAdd renamed the layer
                lay.thanAtts[THANNAME].__init__(names[-1], False)    #MAke sure that the name is not inherited
                for nam, a in lay.thanAtts.items():   #works for python2,3
                    if a.thanInher:
                        a.thanValSet(laypar.thanAtts[nam].thanVal)
            elif dl == "</LAYERTREE>":
                break
            else:
                raise ValueError("<LAYER> or </LAYERTREE> was expected, but found: %s" % (dl,))
        fr.readEnd("LAYERTREE")
        self.thanDictRebuild()
        self.thanCur = self.thanFindic(pcur)
        if self.thanCur is None: raise ValueError("Current layer %s was not found" % (pcur,))


    def __del__(self):
        print("Memory of layertree is recycled")


#############################################################################
#############################################################################

#MODULE LEVEL FUNCTIONS

def test():
    "Tests creation and alteration of layers."

    print(__doc__)
    print("Module thanlayer test")

    laytree = testcreate()
    laytree.thanDictRebuild()
    for key in laytree.dilay:
        print(key, ':', str(laytree.dilay[key].thanAtts[THANNAME]))
#    testalter(laytree)
#    testgui(laytree)

    print("Tests memory leaks.")
    laytree.thanRoot.thanDestroy()
    laytree.thanRoot = 1
    print("---------------------------------------------------")

#===========================================================================

def testgui(lay):
    "Tests Tkinter layer gui."
    import p_gtkwid

#    atts = ("expand", "name", "color", "visibility", "plotcolor", "textstyle")
#    widths = (1, 40, 15, 2, 15, 15)
    from tkinter import Tk
    win = Tk()
    win.title("Test ThanLayers")
    li = p_gtkwid.ThantkClist5(win, objs=[lay], atts=thanlayatts.thanLayAttsNames,
        widths=thanlayatts.thanLayAttsWidths, height=15,
        vscroll=1, hscroll=1, onclick=lambda evt=None: None)
#    li = p_gtkwid.ThantkClist1(win, atts=atts, widths=widths, height=15,
#        vscroll=1, hscroll=1, onclick=onclick)
    li.grid()
    win.mainloop()
#    print(li.getResult())

#===========================================================================

def testcreate():
    "Creates a layer hierarchy."

    laytree = ThanLayerTree()
    ch = laytree.thanRoot.thanChildNew("cxxx")
    ch_2 = laytree.thanRoot.thanChildNew("cxxx1")

    ch1 = ch.thanChildNew("jjjlls")
    ch2 = ch.thanChildNew("jjjlls2")
    ch3 = ch1.thanChildNew("j1")
    ch4 = ch1.thanChildNew("j2")
    laytree.thanRoot.pr()
    print("-------------------------------")
    return laytree

#===========================================================================

def testalter(laytree):
    "Tests alteration of layers."

    att = "frozen"
    val1 = "1"
    val2 = "0"

    att = "moncolor"
    val1 = "2"
    val2 = "0"

    ch = laytree.thanRoot.thanChildren[2]
    ch1 = ch.thanChildren[1]
    ch4 = ch1.thanChildren[2]
    ch4.thanSetAtts(**{att : 777})

    print("------------------------------------", att, "=", val1)
    ch.thanSetAtts(**{att : val1})
    laytree.thanRoot.pr(att)

    print("------------------------------------", att, "=", val2)
    ch.thanSetAtts(**{att : val2})
    laytree.thanRoot.pr(att)
