from math import sin, cos, atan, atan2, sqrt, hypot, pi
import p_gmath


class Ellipsoid(object):
    """A reference ellipsoid plus origin."

    This object is also a Datum, that is a reference ellipsoid plus its
    origin which usually is the center of the earth.
    GRS80, WGS84 have their center on the center of the earth, while NAD83
    which is based on GRS80, does not.
    Each datum must have a function which converts the datum coordinates (which
    are geocentric) to GRS80 geocentric coordinates."""

    def __init__(self, a, b, name="<unknown>"):
        "Create the ellispoid's characteristics"
        self.a = a    #semi-major axis a
        self.b = b    #semi-minor axis b
        self.name = name
        self.e2 = (a**2-b**2) / a**2             #eccentricity
        self.et2 = (a**2-b**2) / b**2
        self.tra2cur = self.tra2GRS80 = None     #No transformation


    def geodet2cen (self, lam, phi, h, hgme=0.0):
        "Return the geocentric coordinates of an ellipsoid given the geodetic coords and height."
        N = self.a / sqrt(1.0 - self.e2*sin(phi)**2)
        xt = (N+h+hgme) * cos(phi) * cos(lam)
        yt = (N+h+hgme) * cos(phi) * sin(lam)
        zt = ((1.0-self.e2) * N + h + hgme) * sin(phi)
        return xt, yt, zt


    def geocen2det (self, xt, yt, zt, hgme=0.0):
        "Return the geodetic coordinates and height of an ellipsoid given the geocentric."
        par = hypot(xt, yt)
        phi = atan(zt*(1.0+self.et2) / par)
        for i in range(4):
            N = self.a / sqrt(1.0 - self.e2*sin(phi)**2)
            phi = atan((zt+self.e2*N*sin(phi))/par)
        N = self.a / sqrt(1.0 - self.e2*sin(phi)**2)
        lam = atan2(yt, xt)         #Thanasis2013_04_23
        h = xt/(cos(phi)*cos(lam)) - N - hgme
        return lam, phi, h

    tee = "Don't know how to convert from %s ellipsoid to %s ellipsoid"
    def geocen2geocenGRS80(self, X, Y, Z):
        "Convert datum geocentric coordinates to GRS80 geocentric coordinates."
        if self.tra2cur is None: raise ValueError(self.tee % (self.name, GRS80.name))
        return self.tra2GRS80.calc((X, Y, Z))

    def geocenGRS802geocen(self, X, Y, Z):
        "Convert datum geocentric coordinates to GRS80 geocentric coordinates."
        if self.tra2cur is None: raise ValueError(self.tee % (GRS80.name, self.EOID.name))
        return self.tra2cur.calc((X, Y, Z))

    def setBursaWolf(self, tx, ty, tz, ex, ey, ez, sk):
        "Set the coefficients of Bursa-Wolf transformation; the coefficients transform from GRS80 to current ellipsoid."
        self.tra2cur = p_gmath.SimilarTransformation(cu=(tx, ty, tz), gon=(ex, ey, ez), am=sk)
        self.tra2GRS80 = self.tra2cur.invert()

    def setTranslation(self, tx, ty, tz):
        "Set the coefficients of translation transformation; the coefficients are added and transform from GRS80 to current ellipsoid."
        self.tra2cur = p_gmath.TranslationTransformation(cu=(tx, ty, tz))
        self.tra2GRS80 = self.tra2cur.invert()

    def setIdentity(self):
        "Set the coefficients of identity transformation; the coefficients transform from GRS80 to current ellipsoid."
        self.tra2cur = p_gmath.Transformation()
        self.tra2GRS80 = self.tra2cur.invert()


#From http://earth-info.nga.mil/GandG/wgs84/gravitymod/egm2008/index.html (Pavlis Nikolaos)
#a=6378137.00 m (semi-major axis of WGS 84 ellipsoid)
#f=1/298.257223563 (flattening of WGS 84 ellipsoid)
#GM=3.986004418 x 1014 m3s-2 (Product of the Earth's mass and the Gravitational Constant)
#ω=7292115 x 10-11 radians/sec (Earth's angular velocity)

WGS84 = Ellipsoid(a=6378137.0, b=6356752.314245, name="WGS84")
WGS84.setIdentity()
GRS80 = Ellipsoid(a=6378137.0, b=6356752.314140, name="GRS80")
GRS80.setIdentity()


dc = -199.723, 74.030, 246.018    #From program ew.f and we.f, (Paper Συγγρού και Γιαννίου)
#dc = -199.652, 74.759, 246.057    #FROM NTUA:SCHOOL OF SURVEYING:2007: http://ecourses.dbnet.ntua.gr/geodaisia1
#                                  #  ALSO FROM BOOK: ΑΝΩΤΕΡΗ ΓΕΩΔΑΙΣΙΑ ΤΟΥ ΜΠΕΗ (1989)
#dc = -199.870, 74.790, 246.620    #http://trac.osgeo.org/proj/wiki/GenParms, http://proj.maptools.org/gen_parms.html
Greek1987 = Ellipsoid(a=6378137.0, b=6356752.314140, name="Greek1987")
Greek1987.setTranslation(-dc[0], -dc[1], -dc[2])

#The WGS84 datum remains fixed at the center of the earth. NAD83 moves every year
#with the tectonic plates of north America. Thus the coordinates of maps in
#north America are unchanged through time.
#However the translation from
#WGS84 (or GRS80) to NAD83 changes through time. Thus if some measurements are
#done with WGS84 in, for example, 1997, then the translation from 1997 WGS84
#to NAD84 are needed. That is what the following NAD83_1997 Datum does.
#For later WGS84 measurements the, translations are increased with rate:
# x=0.0007 m/year  y=-0.0007/year   z=0.0005 m/year
#The rotations with rate:
# εx=0.067 mas/year εy=-0.757 mas/year εz=-0.051 mas/year  (mas=mili-arc-second)
#The scale rate:
# s=-0.18E-9 /year
#The translations rate are too small to make a practical difference:
#in 20 years (2017) the differences are:
# dx=0.0007*20=0.014m   dy=-0.0007*20=-0.014m   dz=0.0005*20=0.01m
NAD83_1997 = Ellipsoid(a=6378137.0, b=6356752.314245, name="NAD83")
NAD83_1997.setBursaWolf(0.9956, -1.9013, -0.5215,
    25.915/3600000.0*pi/180.0, 9.426/3600000.0*pi/180.0, 11.599/3600000.0*pi/180.0,
    1.0+0.62e-9)

_ellipsoid = {0: ('Clarke 1866', 6378206.4000000004, 6356583.7999999998),
              1: ('Clarke 1880', 6378249.1449999996, 6356514.8695499999),
              2: ('Bessel', 6377397.1550000003, 6356078.9628400002),
              3: ('International 1967', 6378157.5, 6356772.2000000002),
              4: ('International 1909', 6378388.0, 6356911.9461300001),
              5: ('WGS 72', 6378135.0, 6356750.5199149996),
              6: ('Everest', 6377276.3452000003, 6356075.4133000001),
              7: ('WGS 66', 6378145.0, 6356759.7693560002),
              8: ('GRS 1980/WGS 84', 6378137.0, 6356752.3141400004),
              9: ('Airy', 6377563.3959999997, 6356256.9100000001),
              10: ('Modified Everest', 6377304.0630000001, 6356103.0389999999),
              11: ('Modified Airy', 6377340.1890000002, 6356034.4479999999),
              12: ('Walbeck', 6378137.0, 6356752.3142449996),
              13: ('Southeast Asia', 6378155.0, 6356773.3205000004),
              14: ('Australian National', 6378160.0, 6356774.7189999996),
              15: ('Krassovsky', 6378245.0, 6356863.0187999997),
              16: ('Hough', 6378270.0, 6356794.343479),
              17: ('Mercury 1960', 6378166.0, 6356784.2836659998),
              18: ('Modified Mercury 1968', 6378150.0, 6356768.3373029996),
              19: ('Sphere', 6370997.0, 6370997.0),
             }

"""From http://trac.osgeo.org/proj/wiki/GenParms
The following predeclared prime meridian names are supported. These can be listed using the cs2cs argument -lm.
   greenwich 0dE
      lisbon 9d07'54.862"W
       paris 2d20'14.025"E
      bogota 74d04'51.3"E
      madrid 3d41'16.48"W
        rome 12d27'8.4"E
        bern 7d26'22.5"E
     jakarta 106d48'27.79"E
       ferro 17d40'W
    brussels 4d22'4.71"E
   stockholm 18d3'29.8"E
      athens 23d42'58.815"E
        oslo 10d43'22.5"E
"""
