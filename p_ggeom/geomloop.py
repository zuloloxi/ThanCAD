"""This module finds closed polygons (loops) which are created by independent polylines
and their intersections.
Then it find the loops that contain a certain point, and form these it chooses
the smaller one (currrently the one with least area."""

from math import floor, ceil
from bisect import bisect_left
import p_gdxf
from p_gmath import thanSegSegGen, thanNear2, thanNearx
from p_ggen import iterby2
import collections

class Seg:
    "A polyline segment with intersection capability."

    def __init__(self, cline, pg):
        "Create a line segment with empty list of intersections."
        assert len(cline) > 1, "It should havee been found"
        self.ia = pg.icod(cline[0])
        self.ib = pg.icod(cline[-1])
        self.cline = cline
        self.cline[0]  = pg.cp[self.ia]    #Ensure that we have exactly the same coordinates with pg.cp
        self.cline[-1] = pg.cp[self.ib]    #Ensure that we have exactly the same coordinates with pg.cp
        self.ct = []    #Intersections between cline[0] and cline[-1]
        self.ct.append((0.0, self.ia))
        self.ct.append((len(self.cline)-1.0, self.ib))


    def inter(self, other, pg):
        "Find intersection of self and sega."
        c = self.cline
        co = other.cline
        for i in range(len(c)-1):
            j = i + 1
            for io in range(len(co)-1):
                jo = io + 1
                res = thanSegSegGen(c[i], c[j], co[io], co[jo], abisline=False, c12isline=False)
                if res is None: continue
                ct, (u, w) = res
                it = pg.icod(ct)
                if it not in (self.ia, self.ib):
                    self.ct.append((i+u, it))
                if it not in (other.ia, other.ib):
                    other.ct.append((io+w, it))


    def interself(self, pg):
        "Find intersections of self with self."
        c = self.cline
        for i in range(len(c)-1):
            j = i + 1
            for io in range(i+2, len(c)-1):
                jo = io + 1
                res = thanSegSegGen(c[i], c[j], c[io], c[jo], abisline=False, c12isline=False)
                if res is None: continue
                ct, (u, w) = res
                it = pg.icod(ct)
                if it not in (self.ia, self.ib):
                    self.ct.append((i+u, it))
                    self.ct.append((io+w, it))


    def iterparts(self):
        "Return parts of the segments between intersections, as polylines (excluding polyline ends)."
        self.ct.sort()
        for (ut1,it1), (ut2,it2) in iterby2(self.ct):
            if thanNearx(ut1, ut2): continue
            i1 = floor(ut1) + 1
            i2 = ceil(ut2) - 1
            yield it1, it2, tuple(self.cline[i1:i2+1])


    def split2(self, pg):
        "Split the segment arbitrarily into 2 segments."
        n = len(self.cline)
        assert n > 2, "We can split only 3 node segments and bigger"
        im = int(n/2)
        seg1 = Seg(self.cline[:im+1], pg)
        seg2 = Seg(self.cline[im+1:], pg)
        return seg1, seg2


class PointGraph:
    "A graph of linked points."

    def __init__(self, clines):
        "Initialize and clean line segments."
        self.cp = []
        self.npointsori = 0   #Original points (without intersection points)
        self.ls   = collections.defaultdict(list)     #Links
        self.edge = {}   #edges which link the points
        self.segs = self.cleanLines(clines)
        #The following are needed for transversing the graph
        self.visited = set()
        self.seq = []
        self.seen = {}


    def link(self, ia, ib, e):
        "Link proint ia and point ib."
        self.ls[ia].append((ib, e))
        self.ls[ib].append((ia, tuple(reversed(e))))

    def icod(self, ca):
        "Find point number."
        for i, cc in enumerate(self.cp):
            if thanNear2(ca, cc): return i
        i = len(self.cp)   #new point number
        self.cp.append(tuple(ca))  #Store new point
        return i


    def cleanLinesold(self, clines):
        "Discard duplicate points in lines, and lines with one point."
        segs = {}
        for cline in clines:
            if len(cline) < 2: continue
            clineb = []
            for ca in cline:
                if len(clineb) > 0 and thanNear2(ca, clineb[-1]): continue
                clineb.append(tuple(ca))
            if len(clineb) > 1:
                seg1 = Seg(clineb, self)
                k = seg1.ia, seg1.ib
                seg2 = segs.get(k)   #Existing segment from ia to ib (if not None)
                if seg2 is None:
                    segs[k] = seg1   #Add unique segment from ia to ib
                elif len(seg1.cline) == 2 and len(seg2.cline) == 2:
                    pass   #seg1 is identical to seg2 and it is ignored
                    assert 0, 'identical segments found'
                else:
                    assert 0, '2 paths for the same ia-ib'
                    if len(seg1.cline) == 2:
                        segs[k] = seg1    #Replace existing segment (seg2) with seg1
                        seg1 = seg2       #Set seg2 to split
                    seg1, seg2 = seg1.split2(self)
                    k = seg1.ia, seg1.ib
                    segs[k] = seg1
                    k = seg2.ia, seg2.ib
                    segs[k] = seg2

        self.npointsori = len(self.cp)
        return list(segs.values())


    def cleanLines(self, clines):
        "Discard duplicate points in lines, and lines with one point."
        segs = []
        for cline in clines:
            if len(cline) < 2: continue
            clineb = []
            for ca in cline:
                if len(clineb) > 0 and thanNear2(ca, clineb[-1]): continue
                clineb.append(tuple(ca))
            if len(clineb) > 1:
                seg1 = Seg(clineb, self)
                segs.append(seg1)

        self.npointsori = len(self.cp)
        return segs


    def inter(self, delay=None):
        "Find intersections of lines and create graph."
        #compute proper intesections (proper: other than end points)
        segs = self.segs
        n = len(segs)
        for i in range(n):   #The upper bound is n (not n-1) because we want to call interself()
            sega = segs[i]
            if delay is not None and delay.quit(): raise TimeoutError("User quit")
            sega.interself(self)
            for j in range(i+1, n):
                sega.inter(segs[j], self)

        #Create the links of the graph
        for seg1 in segs:
            for it1, it2, e in seg1.iterparts():
                self.link(it1, it2, e)

        self.segs.clear()   #Release memory which is not needed any more


    def plotGraph(self, dxf, hs=0.2):
        "Plot the graph to a dxf file."
        #print("cp=", self.cp)

        dxf.thanDxfSetLayer("ORIGINALPOINTS")
        for i in range(self.npointsori):
            c = self.cp[i]
            dxf.thanDxfPlotCircle(c[0], c[1], hs)

        dxf.thanDxfSetLayer("INTERSECTIONPOINTS")
        for i in range(self.npointsori, len(self.cp)):
            c = self.cp[i]
            dxf.thanDxfPlotCircle(c[0], c[1], hs)

        dxf.thanDxfSetLayer("INDEXES")
        for i in range(len(self.cp)):
            c = self.cp[i]
            dxf.thanDxfPlotSymbol(c[0], c[1], hs, str(i), 0.0)

        dxf.thanDxfSetLayer("EDGES")
        seen = set()
        #print("ls=", self.ls)

        for ia in self.ls:
            for ib, e in self.ls[ia]:
                k = ia, ib, e
                if k in seen: continue
                c = self.cp[ia]
                x = [c[0]]
                y = [c[1]]
                for c in e:
                    x.append(c[0])
                    y.append(c[1])
                c = self.cp[ib]
                x.append(c[0])
                y.append(c[1])
                dxf.thanDxfPlotPolyline(x, y)
                k = ib, ia, tuple(reversed(e))
                seen.add(k)


    def iterloops(self):
        "Traverse the graph and find loops."
        self.visited.clear()
        for ia in range(len(self.cp)):
            if ia in self.visited: continue
            self.seq.clear()
            self.seen.clear()
            print("iterloops(): beginning:", ia)
            yield from self.visit(ia, iparent=-1, edge=())


    def visit(self, ia, iparent, edge):
        "Visit self and all children."
        j = self.seen.get(ia)
        if j is not None: #loop found
            loop1 = self.seq[j:]
            loop1[0] = loop1[0][0], ()   #First point has no edge leading to it
            loop1.append((ia, edge))
            yield loop1
            return

        self.seq.append((ia, edge))
        self.seen[ia] = len(self.seq)-1   #The index of the last element added
        edger = tuple(reversed(edge))
        for ib,e in self.ls[ia]:
            if ib == iparent and e == edger: continue   #Do not go back to parent
            yield from self.visit(ib, iparent=ia, edge=e)
        itemp = self.seq.pop()
        #assert itemp == ia
        del self.seen[ia]
        self.visited.add(ia)


    def index2coor(self, loop1):
        "Convert point indexes to coordinate."
        cpol = []
        for ia, edge in loop1:
            cpol.extend(edge)
            cpol.append(self.cp[ia])
        return cpol
