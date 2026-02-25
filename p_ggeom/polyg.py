from itertools import islice
from bisect import bisect
from math import fabs, hypot
from p_gmath import linEq2, linint
from p_ggen import prg, iterby2, tog, frange, frangec
from p_gvec import Vector2
from .area import area


class Polygon:
    "A polygon."
    DCMIN = 0.05
    DYMAX = 10.0

#============================================================================

    def __init__(self, aa, cs, state=0):
        "Initialise polygon."
        dcmin = self.DCMIN
        cs2 = [quant(a, dcmin) for a in cs]    # Make the coordinates quantumised
        self.csori = dict(zip(cs2, cs))        # Save original coordinates    #Ok for python 2, 3
        cs = cs2
        remDup(cs, dcmin)                      # Delete very close points
        if len(cs) <= 2: raise ValueError("Degenerate polygon")

#-------Ensure that first and last point are the same

        if fabs(cs[0][0]-cs[-1][0]) < dcmin and \
            fabs(cs[0][1]-cs[-1][1]) < dcmin:
            cs[-1] = cs[0]
        else:
            cs.append(cs[0])
        assert cs[0] == cs[-1], "First and last point of polygon should coincide."
        if len(cs) <= 3: raise ValueError("Degenerate polygon")

        css = []
        for y, a, b in limitDy(cs, self.DYMAX):
            a = quant(a, dcmin)
            b = quant(b, dcmin)
            if fabs(b[0]-a[0]) < dcmin and fabs(b[1]-a[1]) < dcmin: continue
            css.append((a[1], a, b))
        css.sort()
#        prg("Polygon %s" % aa)
#        for i,(y, a, b) in enumerate(css):
#            assert a[1] <= b[1]
#            prg("%5d%10.3f%10.3f%10.3f%10.3f%10.3f" % (i, y, a[0], a[1], b[0], b[1]))
#        for a, b in iterby2(css):
#            assert b[0] - a[0] <= self.DYMAX


        self.aa = aa
        self.cs = cs
        self.css = css
        self.state = 0
        self._area = None
        if state: self.changeState()

#============================================================================

    def merge(self, other):
        "Assuming that self and other has common edge, merge polygon to a new one, deleting the common edge."
        if self.state != other.state: self.changeState()
        ia, ib = self.__common1(other)
        if ia is None: return None
        for da in 1, -1:
            for db in 1, -1:
                ja = self.__next1(ia, da)
                jb = other.__next1(ib, db)
                if near(self.cs[ja], other.cs[jb]):
                    ja, jb = self.__commonx(other, ia, da, ib, db)
                    ia, ib = self.__commonx(other, ia, -da, ib, -db)
                    return self.__domerge(other, ia, ja, da, ib, jb, db)
#        plotPols((self, other))
        prg("Polygon merge with One common point???")
        return None


    def __common1(self, other):
        "Finds 1 common points between polygons."
        for ia,csa in enumerate(self.cs[:-1]):
            for ib,csb in enumerate(other.cs[:-1]):
                if near(csa, csb): return ia, ib
        return None, None


    def __commonx(self, other, ia, da, ib, db):
        ja1 = ia
        jb1 = ib
        while True:
            ja = self.__next1(ja1, da)
            jb = other.__next1(jb1, db)
            assert (ja, jb) != (ia, ib), "Ταυτίζονται τα πολύγωνα?"
            if not near(self.cs[ja], other.cs[jb]): return ja1, jb1
            ja1, jb1 = ja, jb

    def __next1(self, ia, da):
        ja = ia + da
        if ja >= len(self.cs)-1: ja = 0
        elif ja < 0: ja = len(self.cs)-2
        return ja


    def __next1old(self, other, ia, da, ib, db):
        ja = (ia + da) % len(self.cs)
        jb = (ib + db) % len(other.cs)
        return ja, jb


    def __domerge(self, other, ia, ja, da, ib, jb, db):
        "Do the actual merge."
        all = []
        ii = ja
        while True:
            ii = self.__next1(ii, da)
            if ii == ia: break
            all.append(self.cs[ii])
        ii = ib
        while True:
            all.append(other.cs[ii])
            ii = other.__next1(ii, -db)
            if ii == jb: all.append(other.cs[ii]); break
        polnew = Polygon(self.aa, all)

        polnew.csori = {}
        for cs1 in polnew.cs:
            try:
                polnew.csori[cs1] = self.csori[cs1]
            except KeyError:
                try:
                    polnew.csori[cs1] = other.csori[cs1]
                except KeyError:
                    prg("self:")
                    for x,y in self.csori.iteritems(): print(x, "\t", y)
                    prg("other:")
                    for x,y in other.csori.iteritems(): print(x, "\t", y)
                    polnew.csori[cs1] = other.csori[cs1]

        return polnew

#============================================================================

    def inPolPol(self, other):
        "Check (not rigorously, if other is contained in self."
        for cs1 in other.cs:
            if self.inPol(cs1) != 1: return False
        return True

#============================================================================

    def intPolEdge(self, other):
        """Finds 1 of the intersections points of self with another polygon."""
        cints = self.__intPolEdge(other)      # Try self first
        if len(cints) > 0: return cints
        return other.__intPolEdge(self)       # No luck: try other


    def __intPolEdge(self, other):
        """Finds 1 of the intersections points of self with another polygon."""
        cints = []
        for i1 in range(len(self.cs)-1):
            in1 = other.inPol(self.cs[i1])
            if in1 != 2: break
        else:
            return cints                      # No intersections (they probably coincide)
        for i2 in range(i1+1, len(self.cs)):
            in2 = other.inPol(self.cs[i2])
            if in2 == 2: continue
            if in2 == in1:
                in1 = in2
                i1 = i2
                continue
            if i2-i1 > 1:                     # There was a point exactly on edge (which is now an intersection)
                cints.append(self.cs[i1+1])
                return cints
            for j in range(1, len(other.cs)):
                fs, fo = intLinseg(self.cs[i1], self.cs[i2], other.cs[j-1], other.cs[j])
                if fs is not None and 0 <= fs <= 1 and 0 <= fo <= 1:
                    a, b = self.cs[i1], self.cs[i2]
                    ct1 = a[0] + (b[0]-a[0])*fs, a[1] + (b[1]-a[1])*fs
                    cints.append(ct1)
                    return cints
            else:
                prg("i1=%d  i2=%d" % (i1, i2))
                prg("in1=%d in2=%d" % (in1, in2))
                assert 0, "There should be at least 1 intersection!"
#       If the program gets here, it means that the for loop was never executed
#       So there is one point inside or outside
        return cints        # So, Probably one polygon is inside the other

#============================================================================

    def iterIntPolygon(self, other):
        "Finds all the intersections of self with another polygon."

#-------The following code makes it impossible for the 2 polygons
#       to have nodes with the same coordinates.
#       self.inPol() uses DCMIN*0.10 in order to avoid problems with this.

        self._area = None                                 # Invalidate area
        if self.state == other.state:
            if len(self.cs) < len(other.cs): self.changeState()
            else:                            other.changeState()


#-------Find all intersections between line segments of polygons

        intss = [ ]
        intso = [ ]
        cints = [ ]
        for i in range(1, len(self.cs)):
            for j in range(1, len(other.cs)):
                fs, fo = intLinseg(self.cs[i-1], self.cs[i], other.cs[j-1], other.cs[j])
#                print "fs,fo=", fs, fo
#                if fs is not None and -1 <= fs <= 2 and -1 <= fo <= 2:
#                print "fs,fo=", fs, fo
                if fs is not None and 0 <= fs <= 1 and 0 <= fo <= 1:
                    a, b = self.cs[i-1:i+1]
                    ct1 = a[0] + (b[0]-a[0])*fs, a[1] + (b[1]-a[1])*fs
                    cints.append(ct1)
                    intss.append((i, fs, ct1))
                    intso.append((j, fo, ct1))

#-------Put intersection points as polygon points

        intss.sort(); intss.reverse()
        for i, fs1, ct1 in intss: self.cs.insert(i, ct1)
        intso.sort(); intso.reverse()
        for i, fs1, ct1 in intso: other.cs.insert(i, ct1)

        f = file("qp0.syk", "w")
        wrsyk(f, self.cs)
        wrsyk(f, other.cs)
        f.close()
        f = file("qpt.syk", "w")

#-------Find disjoint common areas of the first polygon with second

        while len(cints) > 0:
            ct1 = cints[0]
            cts = [ct1]
            pol = self
            polother = other
            i = pol.cs.index(ct1)
            j = i + 1
            if j >= len(pol.cs): j = 1
            ptest = (pol.cs[i][0] + pol.cs[j][0])*0.5, (pol.cs[i][1] + pol.cs[j][1])*0.5
            if polother.inPol(ptest): jnext = 1
            else:                     jnext = -1
            j = i
            while 1:
                j += jnext
                if   j >= len(pol.cs): j = 1
                elif j < 0:            j = len(pol.cs) - 2

                assert j != i, "Another intersection should be present."
                ct1 = pol.cs[j]
                cts.append(ct1)
                if ct1 == cts[0]: break
                if ct1 in cints:
                    pol, polother = polother, pol
                    i = pol.cs.index(ct1)
                    j = i + 1
                    if j >= len(pol.cs): j = 1
                    ptest = (pol.cs[i][0] + pol.cs[j][0])*0.5, (pol.cs[i][1] + pol.cs[j][1])*0.5
                    if polother.inPol(ptest): jnext = 1
                    else:                     jnext = -1
                    j = i
                else:
                    if len(cts)>5000:
                        wrsyk(f, cts)
                        f.close()
                        f = file("qp1.syk", "w")
                        wrsyk(f, self.cs)
                        wrsyk(f, other.cs)
                        assert 0, "5000 τομές!"

#-----------Clear the intersection points found on the common area

            for ct1 in cts:
                try: i = cints.index(ct1)
                except ValueError: continue
                del cints[i]
                i = self.cs.index(ct1)
                del self.cs[i]
                i = other.cs.index(ct1)
                del other.cs[i]
            wrsyk(f, cts)
            yield cts

#============================================================================

    def changeState(self):
        "Changes the quantum state of a polygon."
#-------If state = 1 (odd), add DCMIN*0.5 to the coordinates.
#       Thus, the coordinates of odd polygons are never the same with
#       the coordinates of even polygons.
#       self.inPol() uses DCMIN*0.10 in order to avoid problems with this.
        prg("changeState: self=%s" % self)
        if self.state: dcmin = -0.5*self.DCMIN
        else:          dcmin =  0.5*self.DCMIN
        cs = self.cs
        css = self.css
        for i,a in enumerate(cs): cs[i] = a[0]+dcmin, a[1]+dcmin
        for i,(y,a,b) in enumerate(css):
            css[i] = y+dcmin, (a[0]+dcmin, a[1]+dcmin), (b[0]+dcmin, b[1]+dcmin)
        self.state = (self.state+1) % 2

#============================================================================

    def onEdge(self, cp):
        "Checks if point p is on an edge of a polygon."
        vp = Vector2(*cp[:2])
        dy = 0.5*self.DYMAX
        i1 = bisect(self.css, (cp[1]-self.DYMAX-dy, cp, cp))
        jj = i1 - 1
        for y, a, b in islice(self.css, i1, None):
            if y - cp[1] > dy: break
            jj += 1
#            prg("onEdge %d: %f %f" % (i1, cp[0], cp[1]))
            va = Vector2(*a)
            vb = Vector2(*b)
            vab = vb - va
            assert abs(vab) > 0.0
            tab = vab.unit()
            dab = vab|tab
            vap = vp - va
            dap = vap|tab
            if dap <    -2*self.DCMIN: continue
            if dap > dab+2*self.DCMIN: continue
            dn = vap|tab.normal()
            if fabs(dn) <= 2*self.DCMIN:
                if   dap <     2*self.DCMIN: node = a
                elif dap > dab-2*self.DCMIN: node = b
                else:                        node = None
                return 2, jj, node
        return 0, None, None


    def inPol(self, ca): return self.inPol2(ca)[0]


    def inPol2(self, ca):
        "Checks if point a is in polygon."

#-----Αποφυγή της ισότητας   yPol(i) == yGram:
#     Αν yGram-yPol(i) < 10% του dot, τότε άλλαξε τη συντεταγμένη yPol
#     έτσι ώστε να υπάρχει αυτή η διαφορά.

        res = self.onEdge(ca)
        if res[0] == 2: return res
        xx, yy = quant(ca, self.DCMIN)
        xx += self.DCMIN*0.25
        yy += self.DCMIN*0.25

        xs = self.compYinter(yy)
        if len(xs) == 0 or xx < xs[0]: return 0, None, None
        for i in range(len(xs)):
#            assert xx != xs[i], "inpol: xx="+str(xx)+" should not be equal to polygon point."
            if xs[i] > xx: return (i % 2 == 1), None, None
        return 0, None, None


    def compYinter(self, yy):
        "Compute intersection of the polygon with a horizontal line at y; assume yy is already quantumised."
        dy = 0.5*self.DYMAX
        #i1 = bisect(self.css, (yy-self.DYMAX-dy, ca, ca))
        i1 = bisect(self.css, (yy-self.DYMAX-dy, (0.0,0.0), (0.0,0.0)))
        xs = []
        for y, va, vb in islice(self.css, i1, None):
            if y - yy > dy: break
            if (vb[1]-yy) * (va[1]-yy) < 0:
                xs.append(linint(va[1], va[0], vb[1], vb[0], yy))
        if len(xs) % 2 != 0:
            import p_gdxf
            dxf = p_gdxf.ThanDxfPlot()
            dxf.thanDxfPlots()
            dxf.thanDxfSetLayer(self.aa)
            dxf.thanDxfPlotPoint(xx, yy)
            for y,a,b, in self.css:
                dxf.thanDxfPlot(a[0], a[1], 3)
                dxf.thanDxfPlot(b[0], b[1], 2)
            dxf.thanDxfPlot(0.0, 0.0, 999)
            assert len(xs) % 2 == 0, 'in: %f %f: odd number of intersections!' % (xx, yy)
        xs.sort()
        return xs


    def interpYpoints(self, yy, dx):
        "Compute interpolation points inside the polygon with distance dx, at a horizontal line at yy; assume yy is already quantumised."
        xs = self.compYinter(yy)
        for i in range(0, len(xs), 2):
            for xx in frangec(xs[i], xs[i+1], dx):
                yield xx, yy


    def interpPoints(self, dx, dy):
        "Compute interpolation points inside the polygon with distance every dx and dy."
        ymin, ccmin = min((cc[1],cc) for cc in self.cs)
        ymax, ccmax = max((cc[1],cc) for cc in self.cs)
        yield ccmin[:2]
        for y in frange(ymin+dy, ymax-dy*0.1, dy):
            _, yy = quant((0.0, y), self.DCMIN)
            yy += self.DCMIN*0.25
            for cp in self.interpYpoints(yy, dx):
                yield cp
        yield ccmax[:2]


    def interpPerim(self, dd):
        "Compute interpolation points on the perimeter with distance every dd."
        for (xa, ya), (xb, yb) in iterby2(self.cs):   #Create points in the edges of the polygon
            yield xa, ya
            dol = hypot(yb-ya, xb-xa)
            for d in frange(dd, dol-dd/10.0, dd):
                xp = linint(0.0, xa, dol, xb, d)
                yp = linint(0.0, ya, dol, yb, d)
                yield xp, yp
        #Note that self.cs[0] == self.cs[-1]


    def area(self, force=False):
        "Computes the area of the polygon; note that this is lazy operation."
        if self._area is None or force:
            self._area = area(self.cs)
        return self._area

#============================================================================

def limitDy(cs, dymax):
        "Limit the y difference of 2 consecutive points."
        css = []
        for a, b in iterby2(cs):
            dab = b[1]-a[1]
            if dab < 0:
                a, b = b, a
                dab = -dab
            if dab <= dymax:
                css.append((a[1], a, b))
            else:
                n = int(dab / dymax) + 1
                dd = dab / n
                d = 0.0
                u = a
                for i in range(n-1):
                    d += dd
                    v = a[0] + (b[0]-a[0]) * d / dab, a[1] + d
                    css.append((u[1], u, v))
                    u = v
                css.append((u[1], u, b))    # Avoid round off error; with stroggylopoihsh ebgaine error oloklhro DCMIN!!!!
        css.sort()
        return css


def quant(a, dcmin):
        "Make the coordinates quantumised."
        kx = int(a[0])
        ky = int(a[1])
        dx = int( (a[0]-kx) / dcmin)
        dy = int( (a[1]-ky) / dcmin)
        xn = kx+dx*dcmin
        dx = fabs(xn-a[0])
        if dx < 0.1*dcmin or fabs(dx-dcmin) < 0.1*dcmin: xn = a[0]       # Already quantimised
        yn = ky+dy*dcmin
        dy = fabs(yn-a[1])
        if dy < 0.1*dcmin or fabs(dy-dcmin) < 0.1*dcmin: yn = a[1]       # Already quantimised
        return xn, yn


def remDup(cs, DCMIN):
    "Remove duplicate points from list."
    i = 1
    while i < len(cs):
        if fabs(cs[i][0]-cs[i-1][0]) < DCMIN and \
           fabs(cs[i][1]-cs[i-1][1]) < DCMIN:
            del cs[i]
        else:
            i += 1

DCMIN = 2*Polygon.DCMIN
def near(a, b):
#   print "DCMIN=", DCMIN
    if fabs(a[0]-b[0]) < DCMIN and \
       fabs(a[1]-b[1]) < DCMIN: return True
    return False


#============================================================================

def plotPols(pols):
    import p_gdxf
    dxf = p_gdxf.ThanDxfPlot()
    dxf.thanDxfPlots()
    for i,pol1 in enumerate(pols):
        dxf.thanDxfSetLayer("p"+str(i+1))
        dxf.thanDxfSetColor(i+1)
        xx = [c1[0] for c1 in pol1.cs]
        yy = [c1[1] for c1 in pol1.cs]
        dxf.thanDxfPlotPolyline(xx, yy)
    dxf.thanDxfPlot(0,0,999)


#============================================================================

def wrsyk (f, cs):
    "Writes a polyline into an opened syk file."
    f.write("%15.3f\n" % (0.0,))
    for c in cs: f.write("%15.3f%15.3f\n" % c)
    f.write("$\n")

def wrsykf (filnam, cs):
    "Writes a polyline into a syk file."
    f = file(filnam, "w")
    wrsyk(f, cs)
    f.close()

#############################################################################
#############################################################################


def intLinseg(a, b, c, d):
    """Intersection of 2 line segments.

                  C
                  o
                 /
                /
               /
  A o---------o-------------o B
             /
            /
           /
          /
         o
         D

               ->     ->    ->     ->
    Condition: rA + f AB == rC + g CD  =>

    ->      ->   ->     ->      ->   ->
    rA + f (rB - rA) == rC + g (rD - rC)  =>

    xA + f (xB - xA) == xC + g (xD - xC)
    yA + f (yB - yA) == yC + g (yD - yC)  =>

    f (xB - xA) + g [-(xD - xC)] == xC - xA
    f (yB - yA) + g [-(yD - yC)] == yC - yA
    """

#    return lineq2(xb-xa, xc-xd, xc-xa, yb-ya, yc-yd, yc-xa)
    return linEq2(b[0]-a[0], c[0]-d[0], c[0]-a[0],
                  b[1]-a[1], c[1]-d[1], c[1]-a[1])



def samplePolygons():
    "Some polygons used for tests."
    c1 = [ (0, 0), (10, 0), (10, 10), (0, 0) ]
    c2 = [ (7, 5), (15, 5), (7, -5), (7, 5) ]
    c3 = [ (7, 5), (15, 5), (7.7, -0.85), (7, 5) ]

    c4 = [(-10.727,         13.547),
          (-10.537,         11.116),
           (-6.055,           7.887),
           (-6.397,          13.472),
          (-10.727,          13.547)
         ]
    c5 = [ (-9.246,          9.483),
           (-7.270,         10.432),
           (-7.384,          8.267),
           (-8.828,          8.191),
          (-11.183,          8.267),
          (-10.044,          8.609),
          ( -9.170,          8.495),
          ( -9.930,          8.913),
          ( -8.296,          8.837),
          (-11.221,          9.369),
          (-11.449,         12.940),
          (-10.347,         13.016),
          (-11.069,         12.294),
          (-10.234,         11.990),
          (-10.955,         11.420),
          ( -9.208,         11.800),
          ( -8.144,         13.016),
          ( -6.169,         13.092),
          ( -7.536,         11.800),
          ( -5.181,         11.762),
          ( -7.726,         10.926),
          (-10.082,         10.926),
          (-10.158,         10.128),
          ( -9.094,         10.053),
           (-9.246,          9.483)
         ]
    return c1, c2, c3, c4, c5


def testKthm():
    "Tests Polygons from Greek Cadastre."
    cdas1 = [ ]
    f = file("das1.syk", "r")
    it = iter(f)
    next(it)
    for dline in it:
        cols = dline[:-1].split()
        if cols[0] == "$": break
        cdas1.append((float(cols[0]), float(cols[1])))
    f.close()

    ckt1 = [ ]
    f = file("kthm1.syk", "r")
    it = iter(f)
    next(it)
    for dline in it:
        cols = dline[:-1].split()
        if cols[0] == "$": break
        ckt1.append((float(cols[0]), float(cols[1])))
    f.close()

    pdas1 = Polygon("das1", cdas1)
    pkt1 = Polygon("kthm1", ckt1)
    f = file("q1.syk", "w")
    for pt in pkt1.iterIntPolygon(pdas1):
        f.write("%15.3f\n" % (0.0,))
        for p in pt: f.write("%15.3f%15.3f\n" % p)
        f.write("$\n")
    f.close()


if __name__ == "__main__":
    testPoints()
