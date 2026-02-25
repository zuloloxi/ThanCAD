from math import pi, cos, sin, tan, sqrt
from p_gmath import dpt
from .ellipsoid import GRS80, Greek1987

class GeodProjection(object):
    "A base class for geodetic projections."

    def __init__(self, name=None, *args, **kw):
        "Initialise; just raise an error."
        if name is None: self.pname = "<unknown>"
        else:            self.pname = name
        self.EOID = None
        raise AttributeError("Please override function __init__()")

    def geodet2en (self, lam, phi):
        "Compute the Easting Northing of the projection given the geodetic coordinates."
        raise AttributeError("Please override function geodet2en()")

    def en2geodet (self, x, y):
        "Compute the geodetic coordinates given Easting Northing of the projection."
        raise AttributeError("Please override function en2geodet()")

    def geodetGRS802en(self, lam, phi):
        "Compute the Easting Northing of the projection given the GRS80 geodetic coordinates."
        xt, yt, zt = GRS80.geodet2cen(lam, phi, 0.0)
        xt, yt, zt = self.EOID.geocenGRS802geocen(xt, yt, zt)
        lam, phi, h = self.EOID.geocen2det(xt, yt, zt)
        return self.geodet2en(lam, phi)

    def en2geodetGRS80(self, x, y):
        "Compute the geodetic coordinates given Easting Northing of the projection."
        lam, phi = self.en2geodet(x, y)
        xt, yt, zt = self.EOID.geodet2cen(lam, phi, 0.0)
        xt, yt, zt = self.EOID.geocen2geocenGRS80(xt, yt, zt)
        lam, phi, h = GRS80.geocen2det(xt, yt, zt)
        return lam, phi

    def geocenGRS802en(self, xt, yt, zt, hgme=0.0):
        """Compute the Easting Northing of the projection given the GRS80 geocentric coordinates."

        hgme=hgeometric-horthometric. Hgeometric= elevation with respect to Greek ellipsoid surface."""
        xt, yt, zt = self.EOID.geocenGRS802geocen(xt, yt, zt)
        lam, phi, h = self.EOID.geocen2det(xt, yt, zt, hgme)
        x, y = self.geodet2en(lam, phi)
        return x, y, h

    def en2geocenGRS80(self, x, y, h, hgme=0.0):
        """Compute the Easting Northing of the projection given the GRS80 geocentric coordinates."

        hgme=hgeometric-horthometric. Hgeometric=elevation with respect to Greek ellipsoid surface."""
        lam, phi = self.en2geodet(x, y)
        xt, yt, zt = self.EOID.geodet2cen(lam, phi, h, hgme)
        xt, yt, zt = self.EOID.geocen2geocenGRS80(xt, yt, zt)
        return xt, yt, zt

    def geocenGRS802det(self, xt, yt, zt, hgme=0.0):
        """Compute the EGSA87 geodetic given the GRS80 geocentric coordinates.

        hgme=hgeometric-horthometric. Hgeometric= elevation with respect to Greek ellipsoid surface."""
        xt, yt, zt = self.EOID.geocenGRS802geocen(xt, yt, zt)
        lam, phi, h = self.EOID.geocen2det(xt, yt, zt, hgme)
        return lam, phi, h

    def geodet2cenGRS80(self, lam, phi, h=0.0, hgme=0.0):
        """Compute geocentric GRS80 coordinates given EGSA87 λ, φ.

        hgme=hgeometric-horthometric. Hgeometric= elevation with respect to Greek ellipsoid surface."""
        xt, yt, zt = self.EOID.geodet2cen(lam, phi, h, hgme)
        xt, yt, zt = self.EOID.geocen2geocenGRS80(xt, yt, zt)
        return xt, yt, zt

    def writeAsc(self, fw):
        "Write the name/definition of the projection to an opened ascii file."
        fw.write("ΓΕΩΔΑΙΤΙΚΗ ΠΡΟΒΟΛΗ: {}\n".format(self.pname))


class TMercator(GeodProjection):
    "A transverse mercatoric projection."

    def __init__(self, EOID=GRS80, k0=0.9996, lam0=21.0*pi/180.0, falseeasting=500000.0, falsenorthing=0.0, name=None):
        "Define the parameters of the mercator projection; defaults to UTM zone=34."
        self.EOID = EOID
        self.k0 = k0
        self.lam0 = lam0
        self.falseeasting = falseeasting
        self.falsenorthing = falsenorthing
        self.a = EOID.a
        self.b = EOID.b
        self.e2 = EOID.e2
        if name is None:
            self.pname = "Transverse Mercator, central meridian %.1f deg, ellipsoid %s"
            self.pname %= (self.lam0*180.0/pi, self.EOID.name)
        else:
            self.pname = name

    def geodet2en (self, lam, phi):
        "Compute the Easting Northing of the projection given the geodetic coordinates."
        lam -= self.lam0
        n = (self.a-self.b) / (self.a+self.b)
        v = self.a/sqrt(1.0 - self.e2*sin(phi)**2)
        rho = v**3*(1.0-self.e2)/self.a**2
        beta = v/rho
        c = cos(phi)
        t = tan(phi)
        t2 = t**2
        lc = lam*c
        lc2 = lc**2

        b0 = self.b*(1.0 + n*(1.0 + n*5.0/4.0*(1.0 + n)))
        b2 = -self.b*n*(1.5 + n*(1.5 + n*21.0/16.0))
        b4 = self.b*n**2*15.0/16.0*(1.0 + n)
        b6 = -self.b*35.0/48.0*n**3
        mf = b0*phi + b2*sin(2.0*phi) + b4*sin(4.0*phi) + \
             b6*sin(6.0*phi)

        w3 = beta - t2
#        w5 = 4.0*beta**3*(1.0-6.0*t2) + beta**2*(1.0+8.0*t2) - 2.0*beta*t2 + t2**2
        w5 = t2**2 + beta*(-2.0*t2 + beta*(1.0+8.0*t2 + \
                     beta*4.0*(1.0-6.0*t2)))
        w7 = 61.0 + t2*(-479.0 + t2*(179.0 - t2))
        w4 = -t2 + beta*(1.0 + 4.0*beta)
        w6 = t2**2 + beta*(-2.0*t2 + beta*(1.0-32.0*t2 + \
                     beta*(-28.0*(1.0-6.0*t2) + \
                     beta*8.0*(11.0-24.0*t2))))
        w8 = 1385.0 - t2*(-3111.0 + t2*(543.0 - t2))
        x = self.k0*v*lc*(1.0 + lc2/6.0*(w3 +
            lc2/20.0*(w5+lc2/42.0*w7)))
        y = self.k0*(mf + lc2*v*t/2.0*(1.0 + lc2/12.0*(w4 + \
            lc2/30.0*(w6 + lc2/56.0*w8))))
        x += self.falseeasting
        y += self.falsenorthing
        return x, y


    def en2geodet (self, x, y):
        "Compute the geodetic coordinates given Easting Northing of the projection."
        x -= self.falseeasting
        y -= self.falsenorthing
        n = (self.a-self.b) / (self.a+self.b)

        d2 = n*(1.5 - 27.0/32.0*n**2)
        d4 = n**2*(21.0/16.0 + n**2*55.0/32.0)    #Thanasis2014_11_23
        d6 = 151.0/96.0*n**3
        d8 = 1097.0/512.0*n**4                    #Thanasis2014_11_23
        b0 = self.b*(1.0 + n*(1.0 + n*5.0/4.0*(1.0 + n)))
        mp = pi*b0/2.0
        mu = pi*y/(2.0*mp*self.k0)
        phi1 = mu + d2*sin(2.0*mu) + d4*sin(4.0*mu) + d6*sin(6.0*mu) + d8*sin(8.0*mu) #Thanasis2014_11_23

        v1 = self.a/sqrt(1.0 - self.e2*sin(phi1)**2)
        rho1 = v1**3*(1.0-self.e2)/self.a**2
        beta1 = v1/rho1
        c1 = cos(phi1)
        t1 = tan(phi1)
        t12 = t1**2
        t14 = t12**2

        v3 = beta1 + 2.0*t12
        v5 = -24.0*t14 + beta1*(-72.0*t12 + beta1*(-(9.0-68*t12) + beta1*4.0*(1.0-6.0*t12)))
        v7 = 61.0 + t12*(662.0 + t12*(1320.0 + t12*720.0))  #Thanasis2014_11_23

        u4 = -12.0*t12 + beta1*(-9.0*(1.0-t12) + beta1*4.0)
        u6 = 360.0*t14 + beta1*(180.0*(5.0*t12-3.0*t14) + \
                         beta1*(15.0*(15.0-98.0*t12+15.0*t14) + \
                         beta1*(-12.0*(21.0-71.0*t12) + \
                         beta1*(8.0*(11.0-24.0*t12) ))))
        u8 = -1385.0 + t12*(-3633.0 + t12*(-4095.0 + t12*(-1575.0)))

        kv = self.k0*v1
        xkv2 = x**2/kv**2
        lam = x/c1/kv * (1.0 + xkv2/6.0*(-v3 + xkv2/20.0*(-v5 + xkv2/42.0*(-v7))))
        phi = phi1 + beta1*t1*xkv2/2.0*(-1.0 + xkv2/12.0*(-u4 + \
                              xkv2/30.0*(-u6 + xkv2/56.0*(-u8))))
        lam += self.lam0
        return lam, phi


class GeodetGRS80(GeodProjection):
    """A "projection" whose easting, northing are the GRS80 geodetic coordinates (λ, φ)."""

    def __init__(self, EOID=GRS80, angleunit=0, name=None):
        """Define the ellipsoid and name of the geodetic coordinates "projection"."""
        if angleunit == 0   :  #radians
            self.frad2en = 1.0
            t = "radians"
        elif angleunit == 1:   #decimal degrees
            self.frad2en = 180.0/pi
            t = "decimal degrees"
        elif angleunit == 2:   #gradians
            self.frad2en = 200.0/pi
            t = "gradians"
        else:
            raise ValueError("angleunit may be 0 (radians), 1 (decimal degrees), or 2 (gradians)")
        self.EOID = EOID
        self.angleunit = angleunit
        if name is None:
            self.pname = "Geodetic coordinates of %s in %s" % (self.EOID.name, t)
        else:
            self.pname = name

    def geodet2en (self, lam, phi):
        "Compute the Easting Northing of the projection given the geodetic coordinates."
        return lam*self.frad2en, phi*self.frad2en #Convert rad to EN

    def en2geodet (self, x, y):
        "Compute the geodetic coordinates given Easting Northing of the projection."
        return x/self.frad2en, y/self.frad2en     #Convert EN to rad


def computeUTMzone(alam, phi):
    """Find the Universal transverse Mercatoric projection zone from geodetic coordinates in radians.

    alam is positive when it is to the east of greenwhich.
    phi is positive when it is to the north of the equator"""
    assert phi -pi*0.5 <= phi <= pi*0.5, "Error: phi should be between -pi/2 and pi/2"
    alam = dpt(alam)*180.0/pi
    if alam > 180: alam -= 360     #Thanasis2019_11_07
    zone = (177.0 + alam) / 6.0 + 1.0
    zone = int(round(zone))
    north = phi >= 0.0
    return zone, north


class UTMercator(TMercator):
    "Universal transverse Mercatoric projection."

    def __init__(self, EOID=GRS80, zone=34, north=True, name=None):
        "Automatically define the parameters of the transverse mercatoric projection."
        assert zone == int(zone) and 1 <= zone <= 60, "Error: illegal zone=%s" % zone
        lam0 = (-177.0 + 6*(zone-1) ) * pi/180.0
        if north: falsenorthing = 0.0
        else:     falsenorthing = 10000000.0
        self.zone = int(zone)
        if not north: self.zone = -self.zone
        if name is None:
            name = "Universal Transverse Mercator, zone=%d %s, ellipsoid=%s"
            name %= (abs(self.zone), "North" if north else "South", EOID.name)
        TMercator.__init__(self, EOID=EOID, k0=0.9996, lam0=lam0,
            falseeasting=500000.0, falsenorthing=falsenorthing, name=name)

    def writeAsc(self, fw):
        "Write the name/definition of the projection to an opened ascii file."
        ns = "NORTH" if self.falsenorthing == 0.0 else "SOUTH"
        fw.write("ΓΕΩΔΑΙΤΙΚΗ ΠΡΟΒΟΛΗ: UTM {} {} {}\n".format(self.zone, ns, self.EOID.name))


class Htrs07(TMercator):
    "The HTRS07 used by Greek cadastre agency is like EGSA87 but without translating the ellipsoid."

    def __init__(self):
        "Automatically define parameters."
        TMercator.__init__(self, EOID=GRS80, k0=0.9996, lam0=24.0*pi/180.0,
                           falseeasting=500000.0, falsenorthing=-2000000.0, name="Greek HTRS07")

    def writeAsc(self, fw):
        "Write the name/definition of the projection to an opened ascii file."
        fw.write("ΓΕΩΔΑΙΤΙΚΗ ΠΡΟΒΟΛΗ: {}\n".format("HTRS07"))


class Egsa87(TMercator):
    """The EGSA87 mercatoric projection.

    The undulation hgme which appears in many of the methods is the undulation
    of the Greek ellipsoid:
    hgme=hgeometric-horthometric. Hgeometric= elevation with respect to Greek ellipsoid surface."""

    def __init__(self):
        "Automatically define parameters."
        TMercator.__init__(self, EOID=Greek1987, k0=0.9996, lam0=24.0*pi/180.0,
                           falseeasting=500000.0, falsenorthing=0.0, name="Greek EGSA87")

    def writeAsc(self, fw):
        "Write the name/definition of the projection to an opened ascii file."
        fw.write("ΓΕΩΔΑΙΤΙΚΗ ΠΡΟΒΟΛΗ: {}\n".format("ΕΓΣΑ87"))

    def geodetGRS802h7m80(self, lamgrs80, phigrs80):
        """Compute the elevation difference between EGSA87 ellipsoidal surface and GRS80 ellipsoidal surface.

        hgeometric Egsa87 = h(with respect to Greek Egsa87 ellipsoidal surface) =
            hgeometric GRS80 - h7m80 = h(with respect to GRS80 ellipsoidal surface) - h7m80
        or:
        h7m80 = hgeometric GRS80 - hgeometric EGSA87

        The geodetic coordinates given are with respect the GRS80 ellipsoid."""
        xt, yt, zt = self.EOID.geodet2cen(lamgrs80, phigrs80, 0.0, 0.0)   #Coordinates on the surface of the GRS80 ellipsoid
        lam, phi, h = self.geocenGRS802det(xt, yt, zt)  #h=geometric elevation of the surface of the GRS80 ellipsoid..
                                                        #..with respect to the EGSA87 ellipsoidal surface (negative near Athens)
        return -h


    def geodet2h7m80(self, lam, phi):
        """Compute the elevation difference between EGSA87 ellipsoidal surface and GRS80 ellipsoidal surface.

        hgeometric Egsa87 = h(with respect to Greek Egsa87 ellipsoidal surface) =
            hgeometric GRS80 - h7m80 = h(with respect to GRS80 ellipsoidal surface) - h7m80
        or:
        h7m80 = hgeometric GRS80 - hgeometric EGSA87

        The geodetic coordinates given are with respect the GRS80 ellipsoid."""
        xt, yt, zt = self.geodet2cenGRS80(lam, phi, h=0.0, hgme=0.0)  #Coordinates on the surface of the EGSA87 ellipsoid
        lam, phi, h = self.EOID.geocen2det(xt, yt, zt)  #h=geometric elevation of the surface of the EGSA87 ellipsoid..
                                                        #..with respect to the GRS80 ellipsoidal surface (positive near Athens)
        return h


    def en2h7m80(self, x, y):
        """Compute the elevation difference between EGSA87 ellipsoidal surface and GRS80 ellipsoidal surface.

        hgeometric Egsa87 = h(with respect to Greek Egsa87 ellipsoidal surface) =
            hgeometric GRS80 - h7m80 = h(with respect to GRS80 ellipsoidal surface) - h7m80
        or:
        h7m80 = hgeometric GRS80 - hgeometric EGSA87

        The geodetic coordinates given are with respect the GRS80 ellipsoid."""
        xt, yt, zt = self.en2geocenGRS80(x, y, 0.0, hgme=0.0)  #Coordinates on the surface of the EGSA87 ellipsoid
        lam, phi, h = self.EOID.geocen2det(xt, yt, zt)  #h=geometric elevation of the surface of the EGSA87 ellipsoid..
                                                        #..with respect to the GRS80 ellipsoidal surface (positive near Athens)
        return h


egsa87 = Egsa87()      #Make an instance of the object, since it is heavily used (in Greece :))
