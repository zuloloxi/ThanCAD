from math import fabs
from . import polyg

def polygCentroid(v, holes=()):
    """Compute centroid of closed centroid taking into account surfaces - really the center of gravity.

    https://en.wikipedia.org/wiki/Centroid.
    EGSA87 coordinates (and any UTM coordinates) are not good, because they are very large
    and thus the formula has large numerical error.
    Thus we take relative coordinates with respect an arbitrary point
    of the polygon."""
    crel = v[0][0], v[0][1]
    cen, signedArea = __polygon(v, crel)
    for v in holes:
        cen1, signedArea1 = __polygon(v, crel)
        if signedArea*signedArea1 > 0.0: #Holes must be subtracted: the holes may have different spin than the polygon
            signedArea -= signedArea1
            cen[0] -= cen1[0]
            cen[1] -= cen1[1]
        else:
            signedArea += signedArea1
            cen[0] += cen1[0]
            cen[1] += cen1[1]

    signedArea *= 0.5
    cen[0] = (cen[0]) / (6 * signedArea) + crel[0]
    cen[1] = (cen[1]) / (6 * signedArea) + crel[1]
    return cen


def __polygonold(v, crel):
    "Compute the contribution of a polygon or a polygonal hole."
    n = len(v)
    if v[0] == v[-1]: n -= 1
    #For all vertices
    cen = [ 0.0, 0.0 ]
    signedArea = 0.0
    for i in range(n):
        x0 = v[i][0] - crel[0]
        y0 = v[i][1] - crel[1]
        x1 = v[(i + 1) % n][0] - crel[0]
        y1 = v[(i + 1) % n][1] - crel[1]
        # Calculate value of A
        # using shoelace formula
        A = (x0 * y1) - (x1 * y0)
        signedArea += A
        # Calculating coordinates of
        # centroid of polygon
        cen[0] += (x0 + x1) * A
        cen[1] += (y0 + y1) * A
    return cen, signedArea


def __polygon(v, crel):
    "Compute the contribution of a polygon or a polygonal hole."
    n = len(v)
    if v[0] == v[-1]: n -= 1    #Ignore last point if same as first: it is taken into account below
    cen = [ 0.0, 0.0 ]
    signedArea = 0.0

    x1 = v[n-1][0] - crel[0]   #last point
    y1 = v[n-1][1] - crel[1]   #last point
    for i in range(n):
        x0 = x1
        y0 = y1
        x1 = v[i][0] - crel[0]
        y1 = v[i][1] - crel[1]
        A = (x0 * y1) - (x1 * y0)   # Calculate value of A using shoelace formula
        cen[0] += (x0 + x1) * A     # Calculate coordinates of..
        cen[1] += (y0 + y1) * A     # ..centroid of polygon
        signedArea += A
    return cen, signedArea


def polygCentroidin(v, holes=()):
    "Find centroid which is inside the (non)convex polygon."
    ca = polygCentroid(v, holes)  #This is the geometric centroid: may not be inside the polygon
    p = polyg.Polygon("main", v)
    pholes = [polyg.Polygon("hole", temp) for temp in holes]

#-----Αποφυγή της ισότητας   yPol(i) == yGram:
#     Αν yGram-yPol(i) < 10% του dot, τότε άλλαξε τη συντεταγμένη yPol
#     έτσι ώστε να υπάρχει αυτή η διαφορά.

    xx, yy = polyg.quant(ca, p.DCMIN)
    xx += p.DCMIN*0.25
    yy += p.DCMIN*0.25

    xs = p.compYinter(yy)
    for temp in pholes:
        xs1 = temp.compYinter(yy)
        xs.extend(xs1)
    xs.sort()

    if len(xs) == 0: raise ValueError("Geometric centroid is outside of enclosing polygon rectangle")
    assert len(xs)%2 == 0, "there should be even number of intersections"
    xen = (xs[0]+xs[1]) * 0.5     #center of horizontal line which is inside the polygon.
    for i in range(0, len(xs), 2):
        xen1 = (xs[i]+xs[i+1])*0.5  #center of horizontal line which is inside the polygon.
        if fabs(xen1-xx) < fabs(xen-xx):  #If this is closer to the geometric centroid, accept it
            xen = xen1
    return xen, yy
