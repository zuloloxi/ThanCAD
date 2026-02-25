"""We want a structure to hold the type of coordinates that a drawing uses.
Planar coordinates can be:
1. Geocentric coordinates
2. Geodetic coordinates
3. Projection coordinates
For all the cases we need the ellipsoid/datum
In case of geodetic coordinates, they can be expressed in:
0. Rads
1: decimal degrees
2: grads

Elevation coordinates can be:
1. Orthometric
2. Geometric
In case a transformation between the two is needed, it can be:
1. EGM08 geoid of Pavlis
2. Greek geoid, Veis
3. For all geoids, convert between geometric and orthometric using constant undulation

The above info is going to written into a text file, thus we need
some encoding/decoding:
    L[0]: Ellipsoid/Datum
          for λ, φ, projection, geocentric: 0=Unknown
                                            1=GRS80
                                            2=WGS84
                                            101=Greek87, Veis (transformation to GRS80 in 1987)
                                            102=NAD83 (transformation to WGS84 in 1997)
    L[1]: Coordinate type:   0: Unknown
                             1: Easting northing of General Transverse Mercatoric Projection.
                                Parameters:
                                L[0]: ellipsoid
                                L[1]: 1
                                L[11]=undefined
                                L[12]=k0: scale at origin (central meridian)
                                L[13]=lam0: Longitude of central meridian (=21.0*pi/180.0 for EGSA87)
                                L[14]=falseeasting
                                L[15]=falsenorthing
                             2: Easting northing of UTM.
                                Parameters:
                                L[0]: ellipsoid
                                L[1]: 2
                                L[11]: zone (1 to 60 or -1 to -60), positive for north, negative for south
                                L[12]=k0=0.9996: scale at origin (central meridian)
                                L[13]=lam0=(-177.0 + 6*(|zone|-1)) * pi/180.0: Longitude of central meridian
                                L[14]=falseeasting=5000000
                                L[15]=falsenorthing=0         if L[11] > 0 (northern hemisphere)
                                                    10000000  if L[11] < 0 (southern hemisphere)
                            11: Easting northing of Lambert Conformal Conic ProjectionUTM.
                                Parameters:
                                L[0]: ellipsoid
                                L[1]: 11
                                L[11]: undefined
                                L[12]: undefined
                                L[13]=lam0: Longitude of central meridian
                                L[14]=falseeasting
                                L[15]=falsenorthing
                                L[16]=phi0: latitude_of_origin
                                L[17]=phi1: standard_parallel_1
                                L[18]=phi2: standard_parallel_2
                            12: Easting northing of USGS Transantarctic Mountain projection (EPSG:3294 WGS 84)
                                Parameters:
                                L[0]: ellipsoid=WGS84
                                L[1]: 12
                                L[11]: undefined
                                L[12]: undefined
                                L[13]=lam0: Longitude of central meridian=162.0*pi/180.0
                                L[14]=falseeasting=0
                                L[15]=falsenorthing=0
                                L[16]=phi0: latitude_of_origin=-78.0*pi/180.0
                                L[17]=phi1: standard_parallel_1=-76.66666666666667*pi/180.0
                                L[18]=phi2: standard_parallel_2=-79.33333333333333*pi/180.0
                           101: Easting northing of EGSA87.
                                Parameters:
                                L[0]=1
                                L[1]=101
                                L[11]=undefined
                                L[12]=k0=0.9996: scale at origin (central meridian)
                                L[13]=lam0==21.0*pi/180.0: Longitude of central meridian
                                L[14]=falseeasting=5000000
                                L[15]=falsenorthing=0
                           102: Easting northing of HTRS07.
                                Parameters:
                                L[0]=1
                                L[1]=102
                                L[11]=undefined
                                L[12]=k0=0.9996: scale at origin (central meridian)
                                L[13]=lam0==21.0*pi/180.0: Longitude of central meridian
                                L[14]=falseeasting=5000000
                                L[15]=falsenorthing=0
                          1001: Coordinates are geodetic λ, φ coordinates.
                                Parameters:
                                L[0]: ellipsoid
                                L[1]=1001
                                L[11]: 1: decimal radians
                                       2: decimal degrees
                                       3: decimal grads
    L[2]: Elevation 0: Unknown
                    1: Orthometric
                    2: Geometric with respect to ellipsoid in L[0]
    L[3]-L[10]: reserved
    L[11]-L[99]: parameters of the projection (e.g. central meridian, false easting etc)
"""
from math import pi
from . import ellipsoid, mercator, lambert


def fromFile(fr):
    "Read the parameters of the geodetic projection from an opened file; may raise StopIteration, ValueError."
    n = int(next(fr))
    if n < 11: raise ValueError("At least 11 parameters must be present")
    L = []
    L.append(float(next(fr)))
    icod = int(L[0])
    if icod not in (0, 1, 2, 101, 102): raise ValueError("Unknown code of ellipsoid: %d (valid codes  are 0, 1, 2, 101, 102)" % (icod,))
    L.append(float(next(fr)))
    icod = int(L[1])
    if icod not in (0, 1, 2, 11, 12, 101, 102, 1001): raise ValueError("Unknown code of geodetic projection: %d (valid codes  are 0, 1, 2, 11, 12, 101, 102, 1001)" % (icod,))
    for i in range(2, n):
        L.append(float(next(fr)))
    return L


def toFile(L, fw):
    "Write the parameters to an opened file; may raise ValueError."
    n = len(L)
    if n < 11: raise ValueError("At least 11 parameters must be present")
    fw.write("%5d\n" % n)
    icod = int(L[0])
    fw.write("%5d\n" % icod)
    icod = int(L[1])
    fw.write("%5d\n" % icod)
    for i in range(2, n):
        par = float(L[i])
        fw.write("%25.15e\n" % par)


def toProj(L):
    "Return the geodetic projection objects which is defined by the parameters L; may raise ValueError, IndexError."
    icod = int(L[0])
    if   icod == 0:   EOID = ellipsoid.GRS80   #Unknown: default=GRS80
    elif icod == 1:   EOID = ellipsoid.GRS80
    elif L[0] == 2:   EOID = ellipsoid.WGS84
    elif L[0] == 101: EOID = ellipsoid.Greek1987
    elif L[0] == 102: EOID = ellipsoid.NAD83_1997
    else: raise ValueError("Unknown code of ellipsoid: %d (valid codes  are 0, 1, 2, 101, 102)" % (icod,))
    icod = int(L[1])
    if icod == 0:
        return mercator.egsa87       #Unknown: default EGSA87
    elif icod == 1:
        return mercator.TMercator(EOID=EOID, k0=L[12], lam0=L[13], falseeasting=L[14], falsenorthing=L[15])
    elif icod == 2:
        izone = int(L[11])
        if not 0 < abs(izone) < 61: raise ValueError("Invalid Universal Transverse Mercator zone: %d (should be between 1 and 60)" % (izone,))
        return mercator.UTMercator(EOID=EOID, zone=abs(izone), north=izone>0)
    elif icod == 11:
        return lambert.LambertConfConical(eoid=EOID, lam0=L[13], phi0=L[16],
            phi1=L[17], phi2=L[18], falseeasting=L[14], falsenorthing=L[15], name=None)
    elif icod == 12:
        return lambert.Epsg3294()
    elif icod == 101:
        return mercator.egsa87
    elif icod == 102:
        return mercator.Htrs07()
    elif icod == 1001:
        return mercator.GeodetGRS80(EOID=EOID, angleunit=int(L[11]))
    else:
        raise ValueError("Unknown code of geodetic projection: %d (valid codes  are 0, 1, 2, 11, 12, 101, 102, 1001)" % (icod,))


def fromMercator(icodEOID=1, k0=0.9996, lam0=21.0*pi/180.0, falseeasting=500000.0, falsenorthing=0.0):
    "Build the parameters L which represent a general Transverse Mercator Projection."
    L = [0.0]*16
    L[0]  = float(icodEOID)
    L[1]  = float(1)
    L[12] = float(k0)     #scale at origin (central meridian)
    L[13] = float(lam0)   #Longitude of central meridian (=21.0*pi/180.0 for EGSA87)
    L[14] = float(falseeasting)
    L[15] = float(falsenorthing)
    return L


def fromUTM(icodEOID=1, zone=34, north=True):
    "Build the parameters L which represent a Univaresal Transverse Mercator Projection."
    L = [0.0]*12
    L[0]  = float(icodEOID)
    L[1]  = float(2)
    L[11] = float(abs(zone))
    if not north: L[11] = -L[11]
    return L


def fromEgsa87():
    "Build the parameters L which represent EGSA87."
    L = [0.0]*11
    L[0]  = float(1)
    L[1]  = float(101)
    return L


def fromHtrs07():
    "Build the parameters L which represent a HTRS07."
    L = [0.0]*11
    L[0]  = float(1)
    L[1]  = float(102)
    return L


def fromGeodetic(icodEOID=1, angleunit=1):
    "Build the parameters L which represent geodetic coordinates."
    if angleunit not in (0, 1, 2):
        raise ValueError("angleunit may be 0 (radians), 1 (decimal degrees), or 2 (gradians)")
    L = [0.0]*12
    L[0]  = float(icodEOID)
    L[1]  = float(1001)
    L[11] = float(angleunit)
    return L


def fromLambertConfConic(icodEOID=2, lam0=162.0*pi/180.0, phi0=-78.0*pi/180.0,
                 phi1=-76.66666666666667*pi/180.0, phi2=-79.33333333333333*pi/180.0,
                 falseeasting=0.0, falsenorthing=0.0):
    "Build the parameters L which represent a Lambert Conformal Conic Projection."
    L = [0.0]*19
    L[0]  = float(icodEOID)
    L[1]  = float(11)
    L[13] = float(lam0)   #Longitude of central meridian
    L[14] = float(falseeasting)
    L[15] = float(falsenorthing)
    L[16] = phi0
    L[17] = phi1
    L[18] = phi2
    return L


def fromEpsg3294():
    "Build the parameters L which represent USGS Transantarctic Mountain projection (EPSG:3294 WGS 84)."
    L = [0.0]*11
    L[0]  = float(2)
    L[1]  = float(12)
    return L


def reGeodp(fr):
    "Read the geodetic projection from an opened file (p_gfil.Datlin object)."
    geod = [None, None, None, None]
    fr.datCom("ΓΕΩΔΑΙΤΙΚΗ ΠΡΟΒΟΛΗ")
    geod[0] = fr.datMchoice("ΕΓΣΑ87 HTRS07 UTM EPSG3294", 8)
    if geod[0] == "UTM":
        geod[1] = fr.datIntR(1, 60)
        geod[2] = fr.datMchoice("NORTH SOUTH", 5)
        geod[3] = fr.datMchoice("GRS80 WGS84 NAD83", 5)
    if geod[0] == "ΕΓΣΑ87":
        geodp = mercator.egsa87
    elif geod[0] == "HTRS07":
        geodp = mercator.Htrs07()
    elif geod[0] == "UTM":
        zone = geod[1]
        north = geod[2] == "NORTH"
        if geod[3] == "GRS80":
            eoid = ellipsoid.GRS80
        elif geod[3] == "WGS84":
            eoid = ellipsoid.WGS84
        elif geod[3] == "NAD83":
            eoid = ellipsoid.NAD83_1997
        else:
            assert 0, "Uknown ellipsoid '{}' (it should have been found)".format(geod[3])
        geodp = mercator.UTMercator(eoid, zone, north)
    elif geod[0] == "EPSG3294":
        geodp = lambert.Epsg3294()
    else:
        assert 0, "Uknown projection '{}' (it should have been found)".format(geod[0])
    return geodp
