"Utilities for projection transformations."
from .proj import (DLTProjection, Rational1Projection, Rational2Projection,
                  Rational15Projection, Polynomial1Projection, Polynomial2Projection,
                  Polynomial1_2DProjection, DLT2Projection, Rational1_2DProjection,
                  Polynomial2_2DProjection, NonCartesian,
                 )
from .projcom import read1


def Projection(icod):
    "Select projection class according to integer indes."
    if   icod == 0: return Polynomial1Projection
    elif icod == 1: return DLTProjection
    elif icod == 2: return Rational1Projection
    elif icod == 3: return Polynomial2Projection
    elif icod == 4: return Rational2Projection
    elif icod == 5: return Rational15Projection

    elif icod == 6: return Polynomial1_2DProjection         # alias to help ThanCad
    elif icod == 7: return DLT2Projection                   # alias to help ThanCad
    elif icod == 8: return Rational1_2DProjection           # alias to help ThanCad
    elif icod == 9: return Polynomial2_2DProjection         # alias to help ThanCad
    elif icod == 10: return Polynomial1_2DProjection
    elif icod == 11: return DLT2Projection
    elif icod == 12: return Rational1_2DProjection
    elif icod == 13: return Polynomial2_2DProjection

    elif icod == 21: return NonCartesian
    raise ValueError("No projection with integer index %d" % (icod,))


def readProj(fr):
    "Reads a projection form file and return Projection object."
    dl1 = read1(fr)
    ic = int(dl1)
    p = Projection(ic)()
    p.read(fr, skipicod=True)
    return p


if __name__ == "__main__":
    print(__doc__)
