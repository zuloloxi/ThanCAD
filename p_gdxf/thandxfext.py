"""Extensions to the dxf format.

These are needed because of the dreadful and unnecessary complexity of the
dxf format.
THANCADSPECIFIC: Extensions specific to ThanCad:
                 Nested layers
                 More layer attributes
THANINTELLICAD:  Extensions which, if present, do not cause
                 intellicad to complain
THANCAD:         ThanCad is able to cope with all extensions
"""

THANCADSPECIFIC = 1
THANINTELLICAD  = 1 << 1
THANCAD         = THANCADSPECIFIC | THANINTELLICAD

thanCadCodes = \
{ "linetype"   :   6,
  "color"      :  62,
  "noplot"     : 290,
  "lineweight" : 370,
  "frozen"     :  71,
  "locked"     :  72,
  "off"        :  73,
}

thanCadAtts = {}
for code,att in thanCadCodes.items(): thanCadAtts[att] = code   #OK for python 2,3
