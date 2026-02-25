from math import pi, sqrt, hypot, cos, sin, tan, atan, log
from p_gmath import fsign
from .ellipsoid import WGS84
from .mercator import GeodProjection


class LambertAzimEqualArea(GeodProjection):
    "Lambert azimuthal equal-area projection."

    def __init__(self, EOID=None, lam0=0, phi0=0, name=None):
        "The center of the projection is lam0, phi0."
        self.phi0 = phi0
        self.lam0 = lam0
        if EOID is None:
            r = 6370997.0
            self.EOID = Ellipsoid(a=r, b=r, name="Lambert_default")
        else:
            self.EOID = EOID
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
        xt, yt, zt = self.EOID.geodet2cen(lam, phi)
        r = self.EOID.a
        c = sqrt(2.0*r/(r-zt))
        return c*xt, c*yt


    def en2geodet(self, x, y):
        "Convert easting, northing to geodetic coordinates."
        c = x**2 + y**2
        r = self.EOID.a
        sc = r - c / (4.0*r**2)
        xt = sc*x
        yt = sc*y
        zt = -r + c / (2.0*r)
        lam, phi = self.EOID.geodet2cen(xt, yt, zt)
        return lam-self.dlam, phi-self.dphi


class LambertConfConic(GeodProjection):
    """Lambert conformal conic projection.

    The formulas are taken from  "Map projections - A working manual", USGS 1987, page 106.
    From the same book:
    * Conic.
    * Conformal.
    * Parallels aer euneually spaced arcs of concentric circles, moreclosely spaced
      near the center of the map
    * Meridials are equally spaced radii of the same circles, thereby cutting parallels
      at right angles.
    * Scale is true along two standard parallels normally. Or along just one.
    * Pole in the same hemishpere as standard parallels is a point; other pole in at infinity.
    * Use for maps of countries anf regions with predominant east-west expanse.
    * Presented by lambert in 1772.
    """

    def __init__(self, EOID=WGS84, lam0=162.0*pi/180.0, phi0=-78.0*pi/180.0,
                 phi1=-76.66666666666667*pi/180.0, phi2=-79.33333333333333*pi/180.0,
                 falseeasting=0.0, falsenorthing=0.0, name=None):
        """Define the parameters of the lambert conformal conic projection; defaults to Transantarctic Mountain projection EPSG:3294 WGS 84.

        lam0: central_meridian
        phi0: latitude_of_origin
        phi1: standard_parallel_1
        phi2: standard_parallel_2
        """
        self.EOID = EOID
        self.lam0 = lam0
        self.phi0 = phi0
        self.phi1 = phi1
        self.phi2 = phi2
        self.falseeasting = falseeasting
        self.falsenorthing = falsenorthing

        if name is None:
            self.pname = "Lambert conformal conic, center λ=%.1f φ=%.1f, φ1=%.1f φ2=%.1f, ellipsoid=%s"
            self.pname %= (self.lam0*180.0/pi, self.phi0*180.0/pi, self.phi1*180.0/pi,
                           self.phi2*180.0/pi, self.EOID.name)
        else:
            self.pname = name
        self.preliminary()


    def preliminary(self):
        "Make preliminary computations for geodet2en() and en2geodet()."
        self.e = sqrt(self.EOID.e2)
        t0 = self.ti(self.phi0)
        t1 = self.ti(self.phi1)
        t2 = self.ti(self.phi2)
        m1 = self.mi(self.phi1)
        m2 = self.mi(self.phi2)
        #print("t1,2=", t1, t2)
        #print("m1,2=", m1, m2)
        self.n = (log(m1)-log(m2)) / (log(t1)-log(t2))
        #print("lambert: n=", self.n)
        self.F = m1/(self.n * t1**self.n)
        self.rho0 = self.rho(t0)


    def ti(self, phi1):
        """Compute ti formula; page 107 "Map projections - A working manual"."""
        e = self.e
        sinf = sin(phi1)
        return tan(pi/4-phi1/2) / ( (1-e*sinf)/(1+e*sinf) )**(e/2)


    def mi(self, phi1):
        """Compute mi formula; page 107 "Map projections - A working manual"."""
        return cos(phi1) / sqrt(1-self.EOID.e2*sin(phi1)**2)


    def rho(self, t0):
        """Compute rhoi formula; page 107 "Map projections - A working manual"."""
        return self.EOID.a * self.F * t0**self.n


    def geodet2en(self, lam, phi):
        "Convert geodetic coordinates to easting, northing."
        rho = self.rho(self.ti(phi))
        theta = self.n*(lam - self.lam0)
        x = rho * sin(theta)
        y = self.rho0 - rho*cos(theta)
        x += self.falseeasting
        y += self.falsenorthing
        return x, y


    def en2geodet(self, x, y):
        "Convert easting, northing to geodetic coordinates."
        x -= self.falseeasting
        y -= self.falsenorthing
        rho0 = self.rho0
        #if self.n < 0:
        #    x = -x
        #    y = -y
        #    rho0 = -rho0
        theta = atan(x/(rho0-y))
        lam = theta/self.n + self.lam0
        rho = fsign(hypot(x, self.rho0-y), self.n)
        t = (rho / (self.EOID.a * self.F))**(1/self.n)

        phi = pi/2 - 2*atan(t)
        e = self.e
#        print("------------------")
        for i in range(5):
            phip = phi
            sinf = sin(phi)
            phi = pi/2 - 2*atan( t * ((1-e*sinf)/(1+e*sinf))**(e/2) )
#            print(phi)
#        print("------------------")
        return lam, phi


class Epsg3294(LambertConfConic):
    """USGS Transantarctic Mountain projection (EPSG:3294 WGS 84 / USGS Transantarctic Mountains).

    PROJCS["WGS 84 / USGS Transantarctic Mountains",
        GEOGCS["WGS 84",
            DATUM["WGS_1984",
                SPHEROID["WGS 84",6378137,298.257223563,
                    AUTHORITY["EPSG","7030"]],
                AUTHORITY["EPSG","6326"]],
            PRIMEM["Greenwich",0,
                AUTHORITY["EPSG","8901"]],
            UNIT["degree",0.0174532925199433,
                AUTHORITY["EPSG","9122"]],
            AUTHORITY["EPSG","4326"]],
        PROJECTION["Lambert_Conformal_Conic_2SP"],
        PARAMETER["standard_parallel_1",-76.66666666666667],
        PARAMETER["standard_parallel_2",-79.33333333333333],
        PARAMETER["latitude_of_origin",-78],
        PARAMETER["central_meridian",162],
        PARAMETER["false_easting",0],
        PARAMETER["false_northing",0],
        UNIT["metre",1,
            AUTHORITY["EPSG","9001"]],
        AXIS["Easting",EAST],
        AXIS["Northing",NORTH],
        AUTHORITY["EPSG","3294"]]"""

    def __init__(self):
        "Initialise parameters of the lambert conformal conic projection."
        super().__init__(EOID=WGS84, lam0=162.0*pi/180.0, phi0=-78.0*pi/180.0,
            phi1=-76.66666666666667*pi/180.0, phi2=-79.33333333333333*pi/180.0,
            falseeasting=0.0, falsenorthing=0.0, name="USGS Transantarctic Mountain projection (EPSG:3294 WGS 84)")

    def writeAsc(self, fw):
        "Write the name/definition of the projection to an opened ascii file."
        fw.write("ΓΕΩΔΑΙΤΙΚΗ ΠΡΟΒΟΛΗ: {}\n".format("EPSG3294"))
