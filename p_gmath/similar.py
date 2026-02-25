"Similar transformation in 2D and 3D."
from p_gnum import (array, matrixmultiply, transpose, zeros, Float)
from math import cos, sin, fabs, atan2
from .var import dpt

class Transformation(object):
    "An identity transformation; transforms coordinates to the same coordinates."

    def __init__(self, cu=(0.0,0.0,0.0), gon=(0.0,0.0,0.0), am=1.0):
        "Create the object; first rotation around (0,0,0), then scale around (0,0,0), then translation."
        pass

    def invert(self):
        """Returns a new transformation which is the inversion of self."""
        return Transformation()

    def calc(self, cp):
        "Transform the coordinates of a 3d point."
        return array(cp)


class TranslationTransformation(Transformation):
    "An object which adds constant displacements to X, Y, Z."

    def __init__(self, cu=(0.0,0.0,0.0), gon=(0.0,0.0,0.0), am=1.0):
        "Create the object; only translation."
        self.cu = array(cu)

    def invert(self):
        """Returns a new transformation which is the inversion of self."""
        return TranslationTransformation(cu=-self.cu)

    def calc(self, cp):
        "Transform the coordinates of a 3d point."
        return self.cu + array(cp)


class SimilarTransformation(Transformation):
    """Keeps the rotation, translation and scale.

    It is generally 3dimensional, but it also works for the 2dimensional case
    if cu[2]=0 and gon[0]=gon[1]=0.
    p_gsar library adds more functionality to this (base) class.
    """

    def __init__(self, cu=(0.0,0.0,0.0), gon=(0.0,0.0,0.0), am=1.0):
        "Create the object; first rotation around (0,0,0), then scale around (0,0,0), then translation."
        self.cu = array(cu)
        self.gon = array(gon)
        self.am = am
        self.rxyz = matwfk(gon)
        self.a = cu[0], cu[1], am*cos(gon[2]), am*sin(gon[2])


    def invert(self):
        """Returns a new transformation which is the inversion of self.

        [A'] = [CU] + m [R] [A] => m [R] [A] = [A'] - [CU] =>
        [A] = (1/m) [RI] ([A'] - [CU]) =>
        [A] = -(1/m) [RI] [CU] + (1/m) [RI] [A']
        [A] = [CU'] + m' [R'] [A']

        [RI] is the inverse of [R], which is also the transpose.
        The angles are found by the rotation matrix
        """
        tra = SimilarTransformation(am=1.0/self.am)
        tra.rxyz = transpose(self.rxyz)
#        om  = atan2(tra.rxyz[1,2], tra.rxyz[2,2])
#        kap = atan2(tra.rxyz[0,1], tra.rxyz[0,0])
#        s = sin(om)
#        c = cos(om)
#        if fabs(s) > fabs(c): phi = atan2(-tra.rxyz[0,2], tra.rxyz[1,2]/s)   # Avoid zero division
#        else:                 phi = atan2(-tra.rxyz[0,2], tra.rxyz[2,2]/c)   # Avoid zero division
#        tra.gon = array((om, phi, kap))
        tra.gon = array(calcwfk(tra.rxyz))
        tra.cu = -tra.am * matrixmultiply(tra.rxyz, self.cu)
        tra.a = tra.cu[0], tra.cu[1], tra.am*cos(tra.gon[2]), tra.am*sin(tra.gon[2])
        return tra


    def calcwfk(self):
        "Just call calwfk with self.rxyz."
        return calcwfk(self.rxyz)


    def calc(self, cp):
        "Transform the coordinates of a 3d point."
        return self.cu + self.am * matrixmultiply(self.rxyz, array(cp))


    def calc2d(self, cp):
        "Transform the coordinates of a 2d point."
        xr, yr, zr = cp; a = self.a
        xx = a[0] + a[2]*xr + a[3]*yr
        yy = a[1] + a[2]*yr - a[3]*xr
        zz = self.cu[2] + self.am*zr
        return xx, yy, zz


def mhtstr (cosf, sinf, i, j, k):
    "Rotation matrix for an angle (ω, φ, κ)."
    ry = zeros((3, 3), Float)
    ry[i,i] =  cosf
    ry[i,j] =  sinf
    ry[j,i] = -sinf
    ry[j,j] =  cosf

    ry[k,k] = 1.0

    dry = zeros((3, 3), Float)
    dry[i,i] = -sinf
    dry[i,j] =  cosf
    dry[j,i] = -cosf
    dry[j,j] = -sinf
    return ry, dry


def matwfk(gon):
    """Computes the rotation matrix of w,f,k.

    Βιβλίο Πατιά: "Εισαγωγή στη Φωτογραμμετρία, σελ. 104
    Στο βιβλίο δίνεται ο πολλαπλασιασμός κ*φ*ω ενώ εδώ χρησιμοποιούμε
    ω*φ*κ:
    cosφ cosκ                      cosφ sinκ                     -sinφ
    sinω sinφ cosκ - cosω sinκ     sinω sinφ sinκ + cosω cosκ     sinω cosφ
    cosω sinφ cosκ + sinω sinκ     cosω sinφ sinκ - sinω cosκ     cosω cosφ
    """
    cosw = cos(gon[0])
    sinw = sin(gon[0])
    cosf = cos(gon[1])
    sinf = sin(gon[1])
    cosk = cos(gon[2])
    sink = sin(gon[2])
    rxyz, t1 = mhtstr(cosw,  sinw, 1, 2, 0)      # = rx
    te,   t1 = mhtstr(cosf, -sinf, 0, 2, 1)      # = ry
    tt = matrixmultiply(rxyz, te)        # = rxy
    te,   t1 = mhtstr(cosk,  sink, 0, 1, 2)      # = rz
    return matrixmultiply(tt, te)        # = rxyz


def calcwfk(rxyz):
    "Compute the omega,phi,kapa from the rotation matrix."
    om  = atan2(rxyz[1,2], rxyz[2,2])
    kap = atan2(rxyz[0,1], rxyz[0,0])
    s = sin(om)
    c = cos(om)
    if fabs(s) > fabs(c): phi = atan2(-rxyz[0,2], rxyz[1,2]/s)   # Avoid zero division
    else:                 phi = atan2(-rxyz[0,2], rxyz[2,2]/c)   # Avoid zero division
    return dpt(om), dpt(phi), dpt(kap)


if __name__ == "__main__":
    print(__doc__)
