import random
from math import cos, sin, hypot, ceil, pi
from p_ggen import iterby2, frange
from p_gmath import thanNear2, thanLineSeg2, thanNearzero, thanNearx
import p_gtri

class HatchPolygon:
    "A non convex polygon which is going to be filled with inclide lines or triangle solids."

    def __init__(self, cpol):
        "Initialize polygon."
        self.cpol = list((c[0], c[1]) for c in cpol)
        if len(self.cpol) == 0: self.cpol.append((0.0, 0.0)) #If empty, add arbitrary point
        if not thanNear2(self.cpol[0], self.cpol[-1]):
            self.cpol.append(tuple(self.pol[0])) #Make the polygon closed
        self.dmean = sum(hypot(b[0]-a[0], b[1]-a[1]) for a,b in iterby2(cpol)) / (len(cpol)-1)
        self.tri = None    #Placeholder for triangulation


    def isNormal(self):
        "Check that the poygoin has at least 4 points."
        return len(self.cpol) >= 4


    def linpolint(self, clin, tlin,):
        "Find all intersections between line and polygon."
        ct = []
        for cpa, cpb in iterby2(self.cpol):
            c = thanLineSeg2(clin, tlin, cpa, cpb)
            if c is None: continue
            xt = c[0]*tlin[0] + c[1]*tlin[1]
            ct.append((xt, c))
        assert len(ct) % 2 == 0
        ct.sort()
        ct = [c for xt,c in ct]
        return ct


    def linpolyminmax(self, nlin):
        "Find y'min and y'max of the projections of polygon points to line."
        yt = [(c[0]*nlin[0] + c[1]*nlin[1], c) for c in self.cpol]
        ytmin, cpolmin = min(yt)
        ytmax, cpolmax = max(yt)
        return cpolmin, ytmin, ytmax


    def checklinpol(self, clin, nlin):
        """Check if any polygon point is exactly on the line.

        nlin is the normal unit vector of the line
        dmean is the average length of the polygon sides."""
        for c in self.cpol:
            v = c[0]-clin[0], c[1]-clin[1]  #Vector from the line point to the polygon point
            d = v[0]*nlin[0] + v[1]*nlin[1] #Perpendicular distance of polygon point to the line
            if thanNearzero(d, self.dmean): return False   #If perp. distance too small, then polygon point is on the line.
        return True


    def onpol(self, c):
        "Check if c is on the perimeter of the polygon."
        for clin, cb in iterby2(self.cpol):
            if thanNear2(clin, cb): #Degenerate side
                if thanNear2(cb, c): return True
                continue
            tlin = cb[0]-clin[0], cb[1]-clin[1]
            t = hypot(tlin[0], tlin[1])
            tlin = tlin[0]/t, tlin[1]/t
            nlin = tlin[1], -tlin[0]
            v = c[0]-clin[0], c[1]-clin[1]  #Vector from the line point to the polygon point
            d = v[0]*nlin[0] + v[1]*nlin[1] #Perpendicular distance of polygon point to the line
            if thanNearzero(d, self.dmean): return True   #If perp. distance too small, then polygon point is on the line.
        return False


    def hatchlines(self, de, thetae):
        "Create hatch lines in polygon."
        if not self.isNormal(): return  #Degenerate polygon: do nothing
        tlin = cos(thetae), sin(thetae)
        nlin = tlin[1], -tlin[0]
        cpolmin, ytmin, ytmax = self.linpolyminmax(nlin)
        ytmin = ceil(ytmin/de)*de
        dee = de/100.0
        for yt in frange(ytmin, ytmax, de):
            for ytt in frange(yt, yt+10.0*dee, dee):
                clin = ytt*nlin[0], ytt*nlin[1]
                if self.checklinpol(clin, nlin): break
            else:
                continue
            ct = self.linpolint(clin, tlin)
            assert len(ct) > 0, "At least 2 intersections should have been found"
            for i in range(0, len(ct), 2):
                yield ct[i], ct[i+1]


    def inpol(self, cp):
        "Check if point cp is inside non-convex polygon cpol."
        if self.onpol(cp): return False  #The point is exactly on the perimeter
        ntries = 1000
        for itry in range(ntries):
            thetae = random.uniform(0, 2.0*pi)
            tlin = cos(thetae), sin(thetae)
            nlin = tlin[1], -tlin[0]
            if self.checklinpol(cp, nlin): break
        else:
            raise ValueError("Too many tries in inpol")

        xtp = cp[0]*tlin[0] + cp[1]*tlin[1]
        ninters = 0   #Number of intersections to the right of cp
        for cpa, cpb in iterby2(self.cpol):
            c = thanLineSeg2(cp, tlin, cpa, cpb)
            if c is None: continue
            xt = c[0]*tlin[0] + c[1]*tlin[1]
            if thanNearx(xtp, xt): return True   #cp is on a side if the polygon
            if xt > xtp: ninters += 1 
        return ninters % 2 == 1    #If odd number of intersections then the point is inside


    def triangulate(self):
        "Create a constrained triangulation of the poygon."
        ps = [(None, x1, y1, -123.456) for x1,y1 in self.cpol]
        print("Creating triangulation..")
        tri = p_gtri.ThanTri()
        tri.make(axy=ps[:-1], convex=False, infinite=False)
        print("Applying sides as breaklines..")
        for ps1,ps2 in iterby2(ps):
            tri.brkapply(ps1, ps2)
        self.tri = tri


    def hatchsolids(self):
        "Create hatch triangles to be filled with solid color."
        if not self.isNormal(): return  #Degenerate polygon: do nothing
        if self.tri is None: self.triangulate()
        for a, b, c in self.tri.itertriangles():    #loop over all triangles
            cp = (a[0]+b[0]+c[0])/3.0, (a[1]+b[1]+c[1])/3.0   #Center of triangle
            if self.inpol(cp): #Triangle is inside the polygon
                yield a, b, c


def plothatchlines(plotline, x, y, dise, thetae):
    """Plot hatch using inclined lines (thetae in deg) whose distance is dise.

    x, y coordinates must form a polygon. If the polygon is not closed, we
    close it."""
    cpol = list(zip(x, y))
    hp = HatchPolygon(cpol)
    thetae *= pi/180.0
    for a, b in hp.hatchlines(dise, thetae):
        plotline(a[0], a[1], b[0], b[1])


def plothatchsolids(plotsolid3, x, y):
    """Plot hatch using inclined lines (thetae in deg) whose distance is dise.

    x, y coordinates must form a polygon. If the polygon is not closed, we
    close it."""
    cpol = list(zip(x, y))
    hp = HatchPolygon(cpol)
    for a, b, c in hp.hatchsolids():
        plotsolid3(a[0], a[1], b[0], b[1], c[0], c[1])
