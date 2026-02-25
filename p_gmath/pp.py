"See p_gmath/developer/paraboloid for documentation - this is untested code."
from __future__ import print_function
from math import sqrt
from .var import lsmsolve
import p_gnum
from .projcom import _Projection


class ParaboloidProjection(_Projection):
    """This class provides the machinery for the paraboloid fit.

    z=ax^2+bx^2+cx+dy+e  ."""
    icodp = 101
    name = "Paraboloid - not really a projection"
    NL = 5

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 1.0,            # Coefs a, b
                      0.0, 0.0, 0.0,       # Coefs c, d, e
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the Paraboloid fit" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with polynomial projection."
        x, y, z = c3d[:3]
        L = self.L
        zp = L[0]*x**2+L[1]*y**2+L[2]*x+L[3]*y+L[4]
        return x, y, zp


    def lsm23(self, fots):
        "Find polynomial coefficients using least square."
        A, B = [], []
        for fot in fots:
            xg, yg, zg = fot[:3]
            A.append([xg**2, yg**2, xg, yg, 1.0])
            B.append(zg)
        a, terr = lsmsolve(p_gnum.array(A), p_gnum.array(B))
        if a is None: return None, None, None
        self.L[:] =  a
        return 0.0, self.erz(fots), 1.0


    def erz(self, fots):
        "Computes the normalised z error of the fit."
        s = 0.0
        for fot in fots:
            ca = fot[:3]
            cb = self.project(ca)
            s += (cb[2] - ca[2])**2
        return sqrt(s/len(fots))


    def getType(self):
        "Return the type of paraboloid."
        if self.L[0] > 0.0:
            if self.L[1] > 0.0:
                return 0             #Elliptic paraboloid with minimum
            elif self.L[1] < 0.0:
                return 2             #Hyperbolic paraboloid
            else:
                return 4             #Parabolic surface
        elif self.L[0] < 0.0:
            if self.L[1] < 0.0:
                return 1             #Elliptic paraboloid with maximum
            elif self.L[1] > 0.0:
                return 3             #Hyperbolic paraboloid
            else:
                return 5             #Parabolic surface
        else:
            if self.L[1] != 0.0:
                return 6             #Parabolic surface
            else:
                return 7             #Plane


    def getExtremum(self):
        "Returns minmum or maximum, if paraboloid."
        if self.L[0] == 0.0 or self.L[1] == 0.0: return [None, None, None]
        c1 = -0.5*self.L[2]/self.L[0]
        d1 = -0.5*self.L[3]/self.L[1]
        e1 = self.L[4] - self.L[0]*c1**2 - self.L[1]*d1**2
        return [c1, d1, e1]


if __name__ == "__main__":
    print(__doc__)
