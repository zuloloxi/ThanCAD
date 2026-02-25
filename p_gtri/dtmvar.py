from math import hypot
from p_ggen import iterby2
from p_gmath import thanLineSeg3, thanNear2

class ThanDTMDEM(object):
    "Base class for DTMs and DEMs."

    def thanLineZendpointstoo(self, cp):
        "Calculate the z coordinates along the line cp."
        cn = []
        for ca, cb in iterby2(cp):
            c = list(ca)
            c[2] = self.thanPointZ(ca, native=True)     # May be None
            cn.append(c)
            for d, c in _uniqint(self.thanIntersegZ(ca, cb, native=True)):
                if d < 0.001: continue     # Avoid points near ca
                if d > 0.999: break        # Avoid points near cb
                cn.append(c)
        c = list(cb)
        c[2] = self.thanPointZ(cb, native=True)   # May be None
        cn.append(c)
        ni = interpolatez(cn)
        return ni, cn


    def thanLineZ(self, cp):
        "Calculate the z coordinates along the line cp."
        if len(cp) < 1: return -1, []     #No points at all
        cb  = cp[0]                       #In case that line has exactly 1 point
        cn = []
        zb = None
        for ca, cb in iterby2(cp):
            can = list(ca)
            can[2] = zb
            cn.append(can)
            za = zb = None
            for d, c in _uniqint(self.thanIntersegZ(ca, cb, native=True)):
                if d < -0.001: continue               # Avoid points outside ca-cb
                if d < 0.001: za = c[2]; continue     # Avoid points near ca
                if d > 1.001: break                   # Avoid points outside ca-cb
                if d > 0.999: zb = c[2]; continue     # Avoid points near cb
                cn.append(c)
            if can[2] is None: can[2] = za
        c = list(cb)
        c[2] = self.thanPointZ(cb, native=True)         # May be None
        cn.append(c)
        cn[0][2] = self.thanPointZ(cn[0], native=True)  # May be None
        ni = interpolatez(cn)
        return ni, cn


    def thanCentroidCompute(self):
        "Compute the centroid of all lines."
        self.thanCena = ((self.xymma[0]+self.xymma[2])*0.5,
                         (self.xymma[1]+self.xymma[3])*0.5,
                         0.0)                               #This is to aid ThanCad

    def thanCen(self):
        "Return the coordinates of the centroid."
        return self.thanCena


    def thanPointZ(self, cp, native=False):
        "Calculate the z coordinate of a point."
        raise AttributeError("Please override this method: thanPointZ")

    def thanIntersegZ(self, ca, cb, native=False):
        "Compute intersections of segment with DEM lines; don't sort intersections from ca to cb."
        raise AttributeError("Please override this method: thanIntersegZ")

    def thanXymm(self, native=False):
        "Return the min and max x and y coordinates."
        raise AttributeError("Please override this method: thanXymm")

    def thanGetWin(self, xymm):
        """Load the frames of the DEM inside xymm.

        Global DEMs should override this function and load their frames which are
        inside or intersect xymm.
        For local DEMs (without frames) this function has no meaning and does nothing.
        """
        pass


    def exportToPython(self, dtmname="dtm1", dir="."):
        "Create a python module which recreates this DEM."
        return 1, "This DEM/DTM ({}) does not support export to Python code".format(self.__class__)


def thanPolygonLine(cpol, pn, n):
    "Finds the intersection between convex polygon segment and line perpendicular to n, whose projection on n axis is pn."
    cts = []
    for i in range(len(cpol)):
        ct = thanLineSeg3(pn, n, cpol[i-1], cpol[i])
        if ct is not None: cts.append(ct)
    if len(cts) == 0: return None, None
    cts.sort()
    j = 1
    while j < len(cts):
        i = j - 1
        if thanNear2(cts[j], cts[i]):
            del cts[j]
        else:
            j += 1
    if len(cts) != 2:
        print("cts=")
        for cp in cts:
            print("%15.3f%15.3f" % (cp[0], cp[1]))
        print("cpol=")
        for cp in cpol:
            print("%15.3f%15.3f" % (cp[0], cp[1]))
        import p_gfil, p_gchart
        ch = p_gchart.ThanChart("xexexe")
        xx = [cp[0] for cp in cpol]
        yy = [cp[1] for cp in cpol]
        ch.curveAdd(xx, yy, color="blue")
        xx = [cp[0] for cp in cts]
        yy = [cp[1] for cp in cts]
        ch.curveAdd(xx, yy, color="red")
        winmain, _, _ = p_gfil.openfileWinget()
        if winmain is None: p_gchart.vis(ch, bg="yellow")
        else:               p_gchart.viswin(winmain, ch, bg="yellow")
        assert len(cts) == 2, "There should be exactly 2 intersections"
    return cts[0], cts[1]


def interpolatez(cp):
    "Interpolate the z coordinate to the points which have none; return number of interpolations."
    n = len(cp)
    for j in range(n):
        if cp[j][2] is not None: break
    else:
        return -1            # No z at all!
    zj = cp[j][2]
    for i in range(j):      # Points from 0 to j-1 do not have valid z
        cp[i][2] = zj
    ni = j                   # Number of interpolated points

    while True:
        for i in range(j+1, n):
            if cp[i][2] is None: break
        else:
            return ni        # All points, from j to end, have valid z
        for j in range(i+1, n):
            if cp[j][2] is not None: break
        else:
            break            # No point, from j to end, has valid z
        __interp2(cp[i-1:j+1])
        ni += j-i-1

    zj = cp[i-1][2]
    for j in range(i, n):
        cp[j][2] = zj
        ni += 1
    return ni


def __interp2(cp):
        "Interpolate the z coordinate to the points which have none."
        d = [0.0]
        j = len(cp) - 1
        for k in range(1, j+1):
            d.append(d[-1] + hypot(cp[k][1]-cp[k-1][1], cp[k][0]-cp[k-1][0]))
        zj = cp[j][2]        # We access list in order, so we are fast
        zi = cp[0][2]
        fact = (zj - zi)/d[j]
        for k in range(1, j):
            cp[k][2] = zi + fact*d[k]


def thanPointZ(dtms, cp):
    "Calculate the z coordinate of a point when multiple DTMs/DEMs are available."
    z = None    #In case that dtms is empty
    for dtm in dtms:
        z = dtm.thanPointZ(cp)
        if z is not None: break
    return z


def thanLineZ(dtms, cp):
        "Calculate the z coordinates along the line cp."
        dtms = tuple(dtms)
        cn = []
        zb = None
        for ca, cb in iterby2(cp):
            can = list(ca)
            can[2] = zb
            cn.append(can)
            za = zb = None
            for d, c in _uniqint(thanIntersegZ(dtms, ca, cb)):
                if d < -0.001: continue               # Avoid points outside ca-cb
                if d < 0.001: za = c[2]; continue     # Avoid points near ca
                if d > 1.001: break                   # Avoid points outside ca-cb
                if d > 0.999: zb = c[2]; continue     # Avoid points near cb
                cn.append(c)
            if can[2] is None: can[2] = za
        c = list(cb)
        c[2] = thanPointZ(dtms, cb)         # May be None
        cn.append(c)
        cn[0][2] = thanPointZ(dtms, cn[0])  # May be None
        ni = interpolatez(cn)
        return ni, cn


def thanLineZendpointstoo(dtms, cp):
        "Calculate the z coordinates along the line cp."
        dtms = tuple(dtms)
        cn = []
        for ca, cb in iterby2(cp):
            c = list(ca)
            c[2] = thanPointZ(dtms, ca)     # May be None
            cn.append(c)
            for d, c in _uniqint(thanIntersegZ(dtms, ca, cb)):
                if d < 0.001: continue     # Avoid points near ca
                if d > 0.999: break        # Avoid points near cb
                cn.append(c)
        c = list(cb)
        c[2] = thanPointZ(dtms, cb)   # May be None
        cn.append(c)
        ni = interpolatez(cn)
        return ni, cn


def thanIntersegZ(dtms, ca, cb):
    "Compute intersections of segment with DEM lines; sort intersection from ca to cb."
    cint = []
    for dtm in dtms:
        cints1 = dtm.thanIntersegZ(ca, cb)
        cint.extend(cints1)
    return cint


def _uniqint(cint, tol=0.001):
    "Sort intersections and delete double entries (with 0.1 percent tolerance)."
    cint.sort()
    i = 0
    j = 1
    while j < len(cint):
#        if cint[j][0]-cint[i][0] < 0.001: # Delete double entries (with 0.1 percent tolerance)
        if thanNear2(cint[i][1], cint[j][1]):
            del cint[j]
        else:
            i = j
            j += 1
    return cint
