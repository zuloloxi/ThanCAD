from math import fabs, hypot, atan2, pi
import bisect
from p_ggen import iterby2, frangec
from p_gmath import thanSegCir, thanNearx, dpt
from p_gdxf import ThanDxfPlot

class Isoclinal:
    "Class to compute isoclinal line."

    def __init__(self, syks1, eps1):
        "Create the object."
        self.syks = {}
        self.hsorted = []
        self.corigin = None
        self.ctarget = None
        self.slope = None
        self.eps = eps1

        self.idir = None
        self.diads = []
        self.disave = 0.0
        self.ndisave = 0
        self.prepareSyks(syks1)


    def findGrade(self, corigin1, ctarget1, sa, sb, ds):
        "Find the grade (slope) that yields the list distance to target."
        dmin = 1e100
        diad1min = ()
        slopemin = 1e100
        for slope1 in frangec(sa, sb, ds):
            d, diad1 = self.isoclinalMin(corigin1, ctarget1, slope1)
            if d>1000.0: print("grade={:.2f}  d={}".format(slope1, d))
            else:        print("grade={:.2f}  d={:.2f}".format(slope1, d))
            if d < dmin:
                dmin = d
                diad1min = diad1
                slopemin = slope1
        return diad1min, slopemin, dmin


    def isoclinalMin(self, corigin1, ctarget1, slope1):
        "Return the isoclinal with least distance to the target."
        diads, disave = self.isoclinals(corigin1, ctarget1, slope1)
        dmin = 1e100
        diad1min = ()
        for diad1 in diads:
            d = self.mindis(diad1)
            if d < dmin:
                dmin = d
                diad1min = diad1
        return dmin, diad1min


    def isoclinals(self, corigin1, ctarget1, slope1):
        "Compute all the possible isoclinals with grade slope1 from origin to target."
        if ctarget1[2] > corigin1[2]:
            self.idir = 1
        elif ctarget1[2] < corigin1[2]:
            self.idir = -1
        else:
            print("isoclinals(): Warning: Origin and target point have the same elevation")
            self.idir = 1
        self.corigin = tuple(corigin1)
        self.ctarget = tuple(ctarget1)
        self.slope = slope1/100.0
        self.diads.clear()

        self.disave = 0.0
        self.ndisave = 0

        temp = (self.corigin,)
        self.forward(temp)

        if self.ndisave > 0: self.disave /= self.ndisave
        return self.diads, self.disave


    def mindis(self, diad1):
        "Compute distance from last point of line to target."
        cb = diad1[-1]
        return hypot(self.ctarget[1]-cb[1], self.ctarget[0]-cb[0])
    def maxh(self, diad1):
        "Compute elevation of last point of line multiplied by idir (1 or -1)."
        cb = diad1[-1]
        return cb[2]*self.idir


    def plotDiad(self, diadsDismin, diadsHmin):
        "Plot the solutions."
        dxf = ThanDxfPlot()
        dxf.thanDxfPlots()

        dxf.thanDxfSetLayer("syk")
        for syks1 in self.syks.values():
            for syk1 in syks1:
                xx = [c[0] for c in syk1]
                yy = [c[1] for c in syk1]
                zz = [c[2] for c in syk1]
                dxf.thanDxfPlotPolyline3(xx, yy, zz)

        dxf.thanDxfSetLayer("origin")
        dxf.thanDxfPlotPoint3(*self.corigin)
        dxf.thanDxfSetLayer("target")
        dxf.thanDxfPlotPoint3(*self.ctarget)

        dxf.thanDxfSetLayer("isoklineis_dismin")
        for syk1 in diadsDismin:
            xx = [c[0] for c in syk1]
            yy = [c[1] for c in syk1]
            zz = [c[2] for c in syk1]
            dxf.thanDxfPlotPolyline(xx, yy)

        dxf.thanDxfSetLayer("isoklineis_hmin")
        for syk1 in diadsHmin:
            xx = [c[0] for c in syk1]
            yy = [c[1] for c in syk1]
            zz = [c[2] for c in syk1]
            dxf.thanDxfPlotPolyline(xx, yy)
        dxf.thanDxfPlot(0,0,999)


    def prepareSyks(self, syks1):
        "Find all elevations and keep them in a dictionary."
        self.syks.clear()
        syks = self.syks
        for syk1 in syks1:
            if len(syk1) < 2: continue
            h = syk1[0][2]
            syks.setdefault(h, []).append(syk1)
        self.hsorted[:] = sorted(syks)


    def hnext(self, ha):
        "Find the next avalaible elevation > or < than h accoding to idir."
        if self.idir == 1:
            if ha >= self.hsorted[-1]: return None        #No higher elevations
            i = bisect.bisect(self.hsorted, ha)
            if thanNearx(ha, self.hsorted[i]):
                i += 1
                if i >= len(self.hsorted): return None    #No higher elevations
        else:
            if ha <= self.hsorted[0]: return None   #no lower elevations
            i = bisect.bisect(self.hsorted, ha)-1
            assert i>=0
            if thanNearx(ha, self.hsorted[i]):
                i -= 1
                if i < 0: return None          #No lower elevations
        return self.hsorted[i]


    def forward(self, isoklinhs):
        "Forward a step toward the next contour line."
        ca = isoklinhs[-1]
        ha = ca[2]
        hb = ha
        for itry in range(1): #Try 3 next contour line elevations
            hb = self.hnext(hb)
            if hb is None or hb*self.idir > self.ctarget[2]*self.idir: #No more contour lines or exceeded elevation of target
            #if hb is None: #No more contour lines
                if len(isoklinhs) > 1: self.addIsokl(isoklinhs)
                return
            self.forwardtryelev(isoklinhs, hb)


    def forwardtryelev(self, isoklinhs, hb):
        "Try to find intersection with contourlines of next elevation."
        ca = isoklinhs[-1]
        ha = ca[2]

        dis = fabs(hb-ha)/self.slope
        self.disave += dis
        self.ndisave += 1

        found = False
        for syk1 in self.syks[hb]:
            for c1, c2 in iterby2(syk1):
                toms = thanSegCir(c1, c2, ca, dis, abisline=False)
                for cb in toms:
                    found = True
                    cb = cb[0], cb[1], hb
                    assert fabs(hypot(cb[1]-ca[1], cb[0]-ca[0]) - dis) < 0.0001
                    temp = isoklinhs + (cb,)
                    if not self.checkAngle(temp): continue
                    if hypot(cb[1]-self.ctarget[1], cb[0]-self.ctarget[0]) < self.eps: #target point is reached
                        self.addIsokl(temp)
                        return
                    self.forward(temp)
        if not found and len(isoklinhs) > 1: self.addIsokl(isoklinhs)


    @staticmethod
    def checkAngle(isokl):
        "Check that we have less than 90 degrees turns in the isoclinal."
        anglemax = pi*0.5
        if len(isokl) < 3: return True
        ca = isokl[-3]
        cb = isokl[-2]
        cc = isokl[-1]
        aab = atan2(cb[1]-ca[1], cb[0]-ca[0])
        abc = atan2(cc[1]-cb[1], cc[0]-cb[0])
        da = dpt(abc-aab)
        if da > pi: da = pi+pi-da
        ok = da < anglemax
        return ok


    def addIsokl(self, isokl):
        "Add another isoclinal."
        self.diads.append(isokl)


    def cluster(self):
        "Cluster solutions."
        step = 5.0*self.disave
        grid = {}
        for diad in self.diads:
            cb = diad[-1]
            jx = round(cb[0]/step)
            iy = round(cb[1]/step)
            grid.setdefault((iy,jx), []).append(diad)
        diadsDismin = []
        diadsHmin = []
        for diads1 in grid.values():
            diad1 = min(diads1, key=self.mindis)
            diadsDismin.append(diad1)
            diad1 = max(diads1, key=self.maxh)
            diadsHmin.append(diad1)
            diad1 = min(diads1, key=self.maxh)
            diadsHmin.append(diad1)
        return diadsDismin, diadsHmin
