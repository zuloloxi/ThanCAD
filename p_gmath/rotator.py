from math import sin, cos

class Rotator2d:
    "Class to rotate coordinates in 2d; preserves z and higher dimensions; no numpy."

    def __init__(self, cc, phi):
        "Set center and rotation angle in radians."
        self.rotPhi = phi
        self.cosf = cos(self.rotPhi)
        self.sinf = sin(self.rotPhi)
        self.cc = cc


    def rotateXy(self, ca):
        "Rotate a point."
        xa = ca[0] - self.cc[0]
        ya = ca[1] - self.cc[1]
        ct = list(ca)
        ct[0] = self.cc[0] + xa*self.cosf - ya*self.sinf
        ct[1] = self.cc[1] + xa*self.sinf + ya*self.cosf
        return ct


    def rotateXyn(self, cc):
        "Rotate many points in place."
        xc = self.cc[0]
        yc = self.cc[1]
        cosf = self.cosf
        sinf = self.sinf
        for ct in cc:
            xa = ct[0] - xc
            ya = ct[1] - yc
            xt = xa*cosf - ya*sinf
            yt = xa*sinf + ya*cosf
            ct[0] = xt + xc
            ct[1] = yt + yc
