# -*- coding: iso-8859-7 -*-
from math import pi, sqrt
from .ellipsoid import Ellipsoid
from .mercator import GeodProjection


class Lambert(GeodProjection):
    "Lambert azimuthal equal-area projection."

    def __init__(self, phi0, lam0, eoid=None, name=None):
        "The center of the projection is phi0, lam0."
        self.phi0 = phi0
        self.lam0 = lam0
        if eoid is None:
            r = 6370997.0
            self.eoid = Ellipsoid(a=r, b=r, name="Lambert_default")
        else:
            self.eoid = eoid
        self.dlam = 0.0 - lam0
        self.dphi = -pi*0.5 - phi0
        if name is None:
            self.pname = "Lambert azimuthal equal-area, center λ=%.1f φ=%.1f, ellipsoid=%s"
            self.pname %= (self.lam0*180.0/pi, self.phi0*180.0/pi, self.EOID.name)
        else:
            self.pname = name


    def geodet2en(self, lam, phi):
        "Convert geodetic coordinates to easting, northing."
        lam += self.dlam
        phi += self.dphi
        xt, yt, zt = self.eoid.geodet2cen(lam, phi)
        r = self.eoid.a
        c = sqrt(2.0*r/(r-zt))
        return c*xt, c*yt


    def en2geodet(self, x, y):
        "Convert easting, northing to geodetic coordinates."
        c = x**2 + y**2
        r = self.eoid.a
        sc = r - c / (4.0*r**2)
        xt = sc*x
        yt = sc*y
        zt = -r + c / (2.0*r)
        lam, phi = self.eoid.geodet2cen(xt, yt, zt)
        return lam-self.dlam, phi-self.dphi
