from math import fabs

class TriLocal:
    "A triangle transformation from local<->global coordinates."
    def __init__(self, x1, y1, x2, y2, x3, y3):
        """Transforms global to local coordinate sin a triangle.

  c-----Numerical considerations:
  c     Usually the sides of a triangle will be much smaller than  the
  c     dimensions of the orthophoto or the aerial photos. This means  that
  c     the length of a side will be of the order of hundreds of pixels.
  c     Therefore x1x3, y1y3 have typical values: 100, 200, 300
  c     I think that a product of two such values is adequately represented
  c     by a real number of 4 bytes, which has 6-7 decimal digits mantissa.
  c     The difference of two such products is scaled so that we don't lose
  c     accuracy.
        """

        self.x3Dat = x3
        self.y3Dat = y3
        self.x1x3 = x1 - x3
        self.y1y3 = y1 - y3
        self.x2x3 = x2 - x3
        self.y2y3 = y2 - y3
        d1 = max(fabs(self.x1x3), fabs(self.y1y3), fabs(self.x2x3), fabs(self.y2y3))
        self.dDat = self.x1x3 * self.y2y3 / d1 - self.y1y3 * self.x2x3 / d1
        self.dDat *= d1


    def glob2loc(self, x, y):
        "Transforms global to local coordinates."
        xx3 = x - self.x3Dat
        yy3 = y - self.y3Dat
        l1 = xx3  * self.y2y3 / self.dDat - yy3  * self.x2x3 / self.dDat
        l2 = self.x1x3 * yy3  / self.dDat - self.y1y3 * xx3  / self.dDat
        l3 = 1.0 - l1 - l2
        return l1, l2, l3


    def loc2glob(self, l1, l2, l3):
        """Transforms local to global coordinates.

        xx1 = l1 x1 + l2 x2 + l3 x3 = l1 x1 + l2 x2 + (1-l1-l2) x3 =
        l1 (x1-x3) + l2 (x2-x3) + l3 (x3-x3) + [l1 x3 + l2 x3 + (1-l1-l2) x3] =
        l1 (x1-x3) + l2 (x2-x3) + l3 (x3-x3) + [l1 x3 + l2 x3 + x3 - l1 x3 -l2 x3] =
        l1 (x1-x3) + l2 (x2-x3) + x3
        """
        x1 = l1*self.x1x3 + l2*self.x2x3 # + l3*self.x3x3 = + l3*0 = +0
        y1 = l1*self.y1y3 + l2*self.y2y3 # + l3*self.x3x3 = + l3*0 = +0
        return self.x3Dat+x1, self.y3Dat+y1


    def interg(self, a1, a2, a3, x1, y1):
        "Interpolates scalar values known at the corners of the triangle to a point inside defined by global coordinates."
        l1, l2, l3 = self.glob2loc(x1, y1)
        return l1*a1 + l2*a2 + l3*a3


    def interp(self, a1, a2, a3, l1, l2, l3):
        "Interpolates scalar values known at the corners of the triangle to a point inside defined by local coordinates."
#        call glob2loc(float(j), float(i), l1, l2, l3)
        return l1*a1 + l2*a2 + l3*a3
