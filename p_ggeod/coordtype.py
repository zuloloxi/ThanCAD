"""We want a structure to hold the type of coordinates that a drawing uses.
Planar coordinates can be:
1. Geocentric coordinates
2. Geodetic coordinates
3. Projection coordinates
For all the cases we need the ellipsoid/datum
In case of geodetic coordinates, they can be expressed in:
0. Rads
1: degrees
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
          for ë, ö, projection, geocentric: 0=Unknown
                                            1=GRS80
                                            2=WGS84
                                            101=Greek, Veis (transformation to GRS80 in 1987)
                                            102=NAD83 (transformation to WGS84 in 1997)
    L[1]: Coordinate type:   0: Unknown
                             1: Easting northing of General Transverse Mercatoric Projection.
                                Parameters:
                                L[11]=undefined
                                L[12]=k0: scale at origin (central meridian)
                                L[13]=lam0: Longitude of central meridian (=21.0*pi/180.0 for EGSA87)
                                L[14]=falseeasting
                                L[15]=falsenorthing
                             2: Easting northing of UTM.
                                Parameters:
                                L[0]: ellipsoid
                                L[11]: zone (1 to 60 or -1 to -60), positive for north, negative for south
                                L[12]=k0=0.9996: scale at origin (central meridian)
                                L[13]=lam0=(-177.0 + 6*(|zone|-1)) * pi/180.0: Longitude of central meridian
                                L[14]=falseeasting=5000000
                                L[15]=falsenorthing=0         if L[11] > 0 (northern hemisphere)
                                                    10000000  if L[11] < 0 (southern hemisphere)
                           101: Easting northing of EGSA87.
                                Parameters:
                                L[0]=101
                                L[11]=undefined
                                L[12]=k0=0.9996: scale at origin (central meridian)
                                L[13]=lam0==21.0*pi/180.0: Longitude of central meridian
                                L[14]=falseeasting=5000000
                                L[15]=falsenorthing=0
                           102: Easting northing of HTRS07.
                                Parameters:
                                L[0]=1
                                L[0]=1
                                L[11]=undefined
                                L[12]=k0=0.9996: scale at origin (central meridian)
                                L[13]=lam0==21.0*pi/180.0: Longitude of central meridian
                                L[14]=falseeasting=5000000
                                L[15]=falsenorthing=0
                                L[11]=undefined
                          1001: Coordinates are geodetic ë, ö coordinates.
                                Parameters:
                                L[0]: ellipsoid
                                L[11]: 1: decimal radians
                                       2: decimal degrees
                                       3: decimal grads
    L[2]: Elevation 0: Unknown
                    1: Orthometric
                    2: Geometric with respect to ellipsoid in L[0]
    L[3]-L[10]: reserved
    L[11]-L[99]: parameters of the projection (e.g. central meridian, false easting etc)
"""

import ellipsoid, mercator

def geodCosys(L):
    "Return a geodetic coordinates system according to coefficients L."
    if L[1] == 0: return None         #Unknown
    if L[1] == 1:                     #Transverse Mercator
        if L[0] == 0: return None       #Unknown
    """   class TMercator(GeodProjection):
    "A transverse mercatoric projection."

    def __init__(self, EOID=GRS80, k0=0.9996, lam0=21.0*pi/180.0, falseeasting=500000.0, falsenorthing=0.0):
    """    
    if L[1] == 2:                     #Universal Transverse Mercator
        if L[0] == 0: L[0] = 1          #Unknown -> GRS80
        if L[0] == 1:
            EOID = ellipsoid.GRS80
        elif L[0] == 2:
            EOID = ellipsoid.WGS84
        elif L[0] == 102:
            EOID = ellipsoid.NAD83_1997
        else:
            raise ValueError, "Only GRS80/WGS84 ellipsoids form UTM." % (L[0],)
        izone = int(abs(L[11]))
        north = L[11] > 0
        if izone < 1 or izone > 60: raise ValueError, "Invalid UTM zone %s" % (L[11],)
        return mercator.UTMercator(EOID, izone, north)
