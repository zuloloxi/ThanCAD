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

thanCadAtts = \
( (  6, "linetype"  , str),
  ( 62, "color"     , int),
  (290, "noplot"    , int),
  (370, "lineweight", int),
  ( 71, "frozen"    , int),
  ( 72, "locked"    , int),
  ( 73, "off"       , int),
)

thanCadCodes = {}
for code,att,fun in thanCadAtts: thanCadCodes[att] = code
