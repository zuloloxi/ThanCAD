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

This module defines the classes for layer attributes.
"""

import p_ggen, p_gcol

############################################################################
############################################################################

class ThanAtt:
    """The base for a standard attribute of a ThanLayer, such as monitor color.

    This base class may be used for an attribute that takes string values.

    An attribute class has the following properties:

    thanVal  : The value of the attribute, either personal or inherited py its parent.
    thanAct  : The value of the attribute as it is already drawn on the screen (Tkinter canvas).
               Almost always it is equal to thanVal.
    thanInher: True if the attribute's value is inherited by its parent.
    thanPers : The value that the user set to this attribute. When thanInher is False
               thanVal is equal to thanPers.

    EXPLANATION
    From now on the "moncolor" is used as an example of an attribute.
    When a layer is created the thanInher is set to true, and thanVal, thanPers
    attributes are set to the "moncolor" of the parent, and thanAct is set
    to None (since nothing is drawn on the screen with this attribute yet).

        If the user changes the "moncolor" to "red", thanInher is set to False,
    thanVal and thanPers is set to the color chosen by the user, and thanAct
    is not altered. (a) When the user presses OK, ThanCad looks at the children
    of current current layer and if thanInher of "moncolor" is True, it sets
    the corresponding thanVal to "red". Then it does the same for the children's
    children and so on.
        Then it checks all the (leaf) layers to see if the thanAct of "moncolor"
    is different to thanVal. If it is different, it changes the "moncolor"
    of all the elements that belong to this layer (and which are already drawn
    on the screen; if no elements of the layer are drawn on the screen, or if
    the layer is "off" nothing happens).

        If the user changes the "moncolor" to the "<BYPARENT>" value, thanInher
    is set to True, thanVal is set to thanVal of the parent layer's thanVal,
    and thanPers and thanAct are not altered. Then as (a) above.

        If the user changes the "moncolor" to the "<PERSONAL>" value, thanInher
    is set to False, thanVal is set to thanPers, and thanPers and thanAct are
    not altered. Then as (a) above.

        When the elements of a layer are drawn on the screen (Tkinter Canvas)
    thanAct is set to thanVal.
    """

    def __init__(self, val, inherit=True):
        "Initialise attribute."
        self.thanValSet(val)
        self.thanAct = None        # If it is not explicitly set later, there will be a failure
        self.thanPers = self.thanVal
        self.thanInher = bool(inherit)

    def thanValSet(self, val):
        "It is useful only for override; here we assume that val is a string."
        self.thanVal = val

    def __str__(self):
        "Transform value to string."
        return p_ggen.thanUnunicode(self.thanVal)

    def thanExpThc (self, fw, name):
        "Save the personal value and the inherit switch in .thc format."
        t = ("%s" % self.thanPers).strip()
        if t == "": t = "+"       #Avoid empty strings as they can not be read by impthc
        fw.writeAtt(name, "%s %d" % (p_ggen.thanUnunicode(t), self.thanInher))

    def thanImpThc(self, fr, ver, name):
        "Read the personal value and the inherit switch from thc format."
        dl = fr.readAtt(name)                 #May raise ValueError, StopIteration
        val, inher = dl[0], bool(int(dl[1]))  #May raise ValueError, IndexError
        self.__init__(val, inher)


class ThanAttLtype(ThanAtt):
    "Linetype attribute; a tuple of: the name of the linetype pattern (dashes), the unit, and the scale."

    def thanValSet(self, val):
        "Save the value as a tuple of a string, units and non negative double."
        namlt, unit, scale = val    #May raise IndexError
        namlt = namlt.strip()
        if namlt == "": raise ValueError("Blank line type name")
        if unit not in ("mm", "u"): raise ValueError("Invalid line type unit: %s" % (unit,))
        scale = float(scale)       #May raise ValueError
        if scale < 0.0: raise ValueError("Invalid line type scale: %s" % (scale,))
        self.thanVal = namlt, unit, scale

    def __str__(self):
        "Transform value to string."
        return "%s,%s,%.3f" % (self.thanVal[0], self.thanVal[1], self.thanVal[2])

    def thanExpThc(self, fw, name):
        "Save the personal value and the inherit switch in .thc format."
        f = "%s  " + fw.formFloat + "  %d"
        namlt, unit, scale = self.thanPers
        fw.writeAttb(name, p_ggen.thanUnunicode(namlt), f % (unit, scale, self.thanInher))

    def thanImpThc(self, fr, ver, name):
        "Read the personal value and the inherit switch from thc format."
        namlt, dl = fr.readAttb(name, s2=True)
        unit, scale, inher = dl.split()                 #May raise IndexError
        inher = bool(int(inher))                        #May raise ValueError
        self.__init__((namlt, unit, scale), inher)


class ThanAttNI(ThanAtt):                     #Inherit is by default False
    def __init__(self, val, inherit=False):
        ThanAtt.__init__(self, val, inherit)


class ThanAttTextb(ThanAtt):
    "A class where the value is text which main contain spaces inside."

    def thanExpThc (self, fw, name):
        "Save the personal value and the inherit switch in .thc format."
        t = ("%s" % self.thanPers).strip()
        fw.writeAttb(name, p_ggen.thanUnunicode(t), "%d" % (self.thanInher,))


    def thanImpThc(self, fr, ver, name):
        "Read the personal value and the inherit switch from thc format."
        if ver < (0,2,0):
            ThanAtt.thanImpThc(self, fr, ver, name)
            return
        val, dl = fr.readAttb(name, s2=True)
        inher = bool(int(dl))
        self.__init__(val, inher)


class ThanAttTextbNI(ThanAttTextb):                     #Inherit is by default False
    def __init__(self, val, inherit=False):
        ThanAttTextb.__init__(self, val, inherit)


class ThanAttOnoffInherit(ThanAtt):
    "An attribute that takes False or True values and it can inherit."

    def __init__(self, val, inherit=True, on="ON", off="off"):
        self.thanOn = on; self.thanOff = off
#        ThanAtt.__init__(self, self.tobool(val), inherit)
        ThanAtt.__init__(self, val, inherit)


    def thanValSet(self, val):
        "Save the value as boolean."
        self.thanVal = self.tobool(val)


    def tobool(self, val):
        "Makes the value boolean."
        try: val = val.strip()+ ""      # If it is a string, strip white chars
        except: string = False
        else:   string = True
        if string:
            if val == self.thanOn.strip(): val = True
            else:                          val = False
        else:
            if val: val = True
            else:   val = False
        return val


    def __str__(self):
        "Transform value to string."
        if self.thanVal: return self.thanOn
        else:            return self.thanOff


    def thanExpThc (self, fw, name):
        "Save the personal values and the inherit switch in thc format."
        fw.writeAtt(name, "%d %d" % (self.thanPers, self.thanInher))


    def thanImpThc(self, fr, ver, name):
        "Read the arc from thc format."
        dl = fr.readAtt(name)             #May raise ValueError, StopIteration
        val, inher = int(dl[0]), int(dl[1]) #May raise ValueError, IndexError
        self.__init__(val, inher)


class ThanAttOnoff(ThanAttOnoffInherit):
    "An attribute that takes False or True values but can't inherit."

    def __init__(self, val, inherit=False, on=" x ", off=" _ "):
        assert not inherit, "Forced inheritance attributes can not be inherited manually."
        ThanAttOnoffInherit.__init__(self, val, inherit, on, off)


############################################################################
############################################################################


class ThanAttInt(ThanAtt):
    "An attribute that takes integer values within limits."
    valmin = None
    valmax = None
    nonzero = False
    tera = "Integer attribute out of range: %s"
    intorfloat = int


    def thanValSet(self, val):
        "Save the value as boolean."
        self.thanVal = self.tonum(val)


    def tonum(self, val):
        "Makes the value boolean."
        if isinstance(val, ThanAtt): val = val.thanVal
        val = self.intorfloat(val)    #If it is a string or a different number,  it is converted to correct number
        if self.valmin is not None and val < self.valmin: raise ValueError(self.tera % (val,))
        if self.valmax is not None and val > self.valmax: raise ValueError(self.tera % (val,))
        if self.nonzero        and val == 0:          raise ValueError(self.tera % (val,))
        return val


class ThanAttFloat(ThanAttInt):
    "An attribute that takes floating point values within limits."
    tera = "Floating point attribute out of range: %s"
    intorfloat = float


class ThanAttScale(ThanAttFloat):
    "An attribute which may not take zero value."
    nonzero = True


class ThanAttThick(ThanAttFloat):
    "An attribute which may not take negative value."
    valmin = 0.0


############################################################################
############################################################################

class ThanAttCol(ThanAtt):
    """ThanCad color class.

    A ThanCad colour is a type of 3 integer (r, g, b) eahc of which
    has values 0 <= r,g,b <= 255
    r=red, g=green, b=blue
    """

#    def __init__(self, col, inherit=True):
#      self.thanValSet(col)
#      ThanAtt.__init__(self, self.thanVal, inherit)     # Initialise Base class

    def thanValSet(self, val):
        """Transforms val to ThanCol object; raises ValueError for invalid colors.

        val  may be one of the following:
        1. ThanCol instance
        2. A string which contains the name of the color (e.g. "yellow")
        3. A string which contains 1 integer which is the index of the color in the
           partial list (e.g. "2")
        4. A string which contains 3 integers, separated by spaces, which represent
           the rgb value of the color (e.g. "10 50 200")
        5. A list/tuple/sequence of 3 texts or 3 integers, which represent the rgb
           value of the color (e.g. ["10","50","200"])
        """
        col = val
        terr = "Invalid ThanCad color: %s" % (col,)
        if isinstance(col, ThanAttCol): self.__dict__.update(col.__dict__); return
        try: col + ""      # Is it string?
        except: string = False
        else: string = True
        if string:
            cs = col.split()
        else:
            try: cs = col[0], col[1], col[2]; n = len(cs)
            except: raise ValueError(terr)
            if n != 3: raise ValueError(terr)

        if len(cs) == 1:
            col = cs[0]
            try: rgb = p_gcol.thanDxfColName2Rgb.get(col, None) or p_gcol.thanDxfColCode2Rgb.get(int(col), None)
            except ValueError: raise ValueError(terr)
            if not rgb: raise ValueError(terr)
        elif len(cs) != 3:
            raise ValueError(terr)
        else:
            try: rgb = tuple(map(int, cs))    #works for python2,3
            except ValueError: raise ValueError(terr)
            for i in rgb:
                if i < 0 or i > 255: raise ValueError(terr)
        self.thanVal = rgb
        self.thanPartial = p_gcol.thanRgb2DxfColCode.get(rgb, None)
        self.thanName = p_gcol.thanRgb2DxfColName.get(rgb, None)
        self.thanTk = p_gcol.thanFormTkcol % rgb
        self.thanNorm = str(self.thanName or self.thanPartial or ("%d %d %d" % rgb))

    def __str__(self): return self.thanNorm

    def rgbShow(self):
        "Shows rgb if normal is partial or name."
        if self.thanName or self.thanPartial: return "RGB: %d %d %d" % self.thanVal
        else: return ""


    def thanDxf(self):
        "Returns a dxf color that resembles self's color."
        return p_gcol.thanRgb2DxfColCodeApprox(self.thanVal)


    def than2Gray(self):
        "Transform the colour to gray scale according to ITU-R 601-2 transform; return an integer."
        return p_gcol.thanRgb2Gray(self.thanVal)


    def thanExpThc (self, fw, name):
        "Save the personal values and the inherit switch in thc format."
        fw.writeAtt(name, "%d %d %d %d" % (self.thanPers[0], self.thanPers[1],
                                           self.thanPers[2], self.thanInher))

    def thanImpThc(self, fr, ver, name):
        "Read the arc from thc format."
        dl = fr.readAtt(name)                 #May raise ValueError, StopIteration
        r, g, b, inher = map(int, dl)         #May raise ValueError, IndexError   #works for python2,3
        for c in r, g, b:
            if c < 0 or c > 255: raise ValueError("Invalid rgb colour")
        self.__init__((r, g, b), inher)


def thanAttCol(col):
    "Factory function for ThanCol class which does not stop in case of mistake."
    try: return ThanAttCol(col)
    except ValueError: return None


def thanAttCol2Tuple(bg, mode):
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
