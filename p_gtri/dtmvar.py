from math import hypot
from p_ggen import iterby2
from p_gmath import thanNear2

class ThanDTMDEM:
    "Base class for DTMs and DEMs."

    def thanLineZendpointstoo(self, cp):
        "Calculate the z coordinates along the line cp."
        cn = []
        for ca, cb in iterby2(cp):
            c = list(ca)
            c[2] = self.thanPointZ(ca)     # May be None
            cn.append(c)
            for d, c in self.thanIntersegZ(ca, cb):
                if d < 0.001: continue     # Avoid points near ca
                if d > 0.999: break        # Avoid points near cb
                cn.append(c)
        c = list(cb)
        c[2] = self.thanPointZ(cb)         # May be None
        cn.append(c)
        ni = interpolatez(cn)
        return ni, cn


    def thanLineZ(self, cp):
        "Calculate the z coordinates along the line cp."
        cn = []
        zb = None
        for ca, cb in iterby2(cp):
            can = list(ca)
            can[2] = zb
            cn.append(can)
            za = zb = None
            for d, c in _uniqint(self.thanIntersegZ(ca, cb)):
                if d < -0.001: continue               # Avoid points outside ca-cb
                if d < 0.001: za = c[2]; continue     # Avoid points near ca
                if d > 1.001: break                   # Avoid points outside ca-cb
                if d > 0.999: zb = c[2]; continue     # Avoid points near cb
                cn.append(c)
            if can[2] == None: can[2] = za
        c = list(cb)
        c[2] = self.thanPointZ(cb)         # May be None
        cn.append(c)
        cn[0][2] = self.thanPointZ(cn[0])  # May be None
        ni = interpolatez(cn)
        return ni, cn


def interpolatez(cp):
    "Interpolate the z coordinate to the points which have none; return number of interpolations."
    n = len(cp)
    for j in xrange(n):
        if cp[j][2] != None: break
    else:
        return -1            # No z at all!
    zj = cp[j][2]
    for i in xrange(j):      # Points from 0 to j-1 do not have valid z
        cp[i][2] = zj
    ni = j                   # Number of interpolated points

    while True:
        for i in xrange(j+1, n):
            if cp[i][2] == None: break
        else:
            return ni        # All points, from j to end, have valid z
        for j in xrange(i+1, n):
            if cp[j][2] != None: break
        else:
            break            # No point, from j to end, has valid z
        __interp2(cp[i-1:j+1])
        ni += j-i-1

    zj = cp[i-1][2]
    for j in xrange(i, n):
        cp[j][2] = zj
        ni += 1
    return ni


def __interp2(cp):
        "Interpolate the z coordinate to the points which have none."
        d = [0.0]
        j = len(cp) - 1
        for k in xrange(1, j+1):
            d.append(d[-1] + hypot(cp[k][1]-cp[k-1][1], cp[k][0]-cp[k-1][0]))
        dij = d[-1]
        zj = cp[j][2]        # We access list in order, so we are fast
        zi = cp[0][2]
        fact = (zj - zi)/d[j]
        for k in xrange(1, j):
            cp[k][2] = zi + fact*d[k]


def thanPointZ(dtms, cp):
    "Calculate the z coordinate of a point when multimple DTMs/DEMs are available."
    z = None    #In case that dtms is empty
    for dtm in dtms:
        z = dtm.thanPointZ(cp)
        if z != None: break
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
            if can[2] == None: can[2] = za
        c = list(cb)
        c[2] = thanPointZ(dtms, cb)         # May be None
        cn.append(c)
        cn[0][2] = thanPointZ(dtms, cn[0])  # May be None
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
