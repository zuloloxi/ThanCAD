from math import hypot, fabs, cos, sin, atan2
from p_ggen import frangec
from .varcon import PI2
from .lineq import linEq2, lineq
from .ellipse import _ellipsen
from .var import thanNear2, thanNearx

def circle3(c1, c2, c3):
    "Find circle passing through 3 noncollinear points, in 2D."
    x1 = c2[0] - c1[0]
    y1 = c2[1] - c1[1]
    x2 = c3[0] - c1[0]
    y2 = c3[1] - c1[1]
    xc, yc = linEq2(2.0*x1, 2.0*y1, x1**2+y1**2, 2.0*x2, 2.0*y2, x2**2+y2**2)
    if xc is None: return None, None   #Points are collinear
    r = hypot(xc, yc)
    cc = list(c1)
    cc[0] += xc
    cc[1] += yc
    return cc, r


def circle2Line(cx, cy, r, phia=0.0, phib=PI2, dt=0.0):
    """Represent an circular arc between angles phia and phib, with straight line segments; dt refers to length units.

    standard form: ((x-cx)/a)^2 + ((y-cy)/b)^2 = 1
    Note: phib should be bigger than phia or nothing will be returned.
    The anti-clockwise anges are positive. To plot a circular arc from 1.5pi to 0.5pi
    set phia=1.5pi and phib=0.5pi+2pi=2.5pi.
    """
    ab = fabs(r)
    n, dphi = _ellipsen(ab, phia, phib, dt)
    if n is None: return (), ()   #Invalid circle
    cs = []
    phis = []
    for phi in frangec(phia, phib, dphi):
        xt = ab*cos(phi)
        yt = ab*sin(phi)
        cs.append((cx+xt, cy+yt))
        phis.append(phi)
    return cs, phis


def circletttlines(cpa, cpb, cpc):
    """Compute circle tangent to 3 lines.

    aa, bb, cc: the first point of the 3 lines
    ta, tb, tc: unit vectors of the 3 lines
    na, nb, nc: normal unit vectores of the 3 lines
    sin, sic: sign of the normal vectors nb, nc
    da, db, dc: distance of the first point of the line to the tangential point
    r: radius of circle
    ce: center of circle
    The following equations hold:
        aa + ta*da +     na*r = ce
        bb + tb*db + sib*nb*r = ce
        cc + tc*dc + sic*nc*r = ce
    The signs are +1 or -1, thus we have 4 cases, which we compute to see which one
    drives to the solution.
    Subtracting 1st from the 2nd and teh 3d:
        bb-aa + tb*db - ta*da + (sib*nb-na)*r = 0
        cc-aa + tc*dc - ta*da + (sic*nc-na)*r = 0
    =>
        -ta*da + tb*db         + (sib*nb-na)*r = aa-bb
        -ta*da +         tc*dc + (sic*nc-na)*r = aa-cc
    """

    def solve():
        "Compute the circle center and radius for one set of signs sib, sic."
        A = [ [-ta[0], tb[0], 0.0,   sib*nb[0]-na[0]],
              [-ta[1], tb[1], 0.0,   sib*nb[1]-na[1]],
              [-ta[0], 0.0,   tc[0], sic*nc[0]-na[0]],
              [-ta[1], 0.0,   tc[1], sic*nc[1]-na[1]],
            ]
        #print()
        #for q in A: print(q)
        B = [aa[0]-bb[0],
             aa[1]-bb[1],
             aa[0]-cc[0],
             aa[1]-cc[1],
            ]
        #print(B)
        try: lineq(A, B)
        except ZeroDivisionError: return None, None
        da, db, dc, r = B
        ce   = (aa[0] + ta[0]*da +     na[0]*r, aa[1] + ta[1]*da +     na[1]*r)
        temp = (bb[0] + tb[0]*db + sib*nb[0]*r, bb[1] + tb[1]*db + sib*nb[1]*r)
        assert thanNear2(ce, temp)
        temp = (cc[0] + tc[0]*dc + sic*nc[0]*r, cc[1] + tc[1]*dc + sic*nc[1]*r)
        assert thanNear2(ce, temp)
        return ce, r

    circles = []
    aa, ta, na = __vectorpar(cpa)
    if aa is None: return circles    #Failed: ta is the error message
    bb, tb, nb = __vectorpar(cpb)
    if bb is None: return circles    #Failed: tb is the error message
    cc, tc, nc = __vectorpar(cpc)
    if cc is None: return circles    #Failed: tc is the error message

    for sib in (1.0, -1.0):
        for sic in (1.0, -1.0):
            ce, r = solve()
            if ce is None: continue
            circles.append((ce, fabs(r)))
    return circles


def __vectorpar(cpa):
    "Compute the vector parameters of a line."
    aa = cpa[0]
    at = cpa[1]
    ta = at[0] - aa[0], at[1] - aa[1]
    d = hypot(ta[0], ta[1])
    if thanNearx(d, 0.0): return None, "One or more line segments are degenerate", None
    ta = ta[0]/d, ta[1]/d
    na = -ta[1], ta[0]
    return aa, ta, na


def circletttlinesnear(cpa, cpb, cpc, cnear):
    "Find the circles tangent to lines cpa, cpb, cpc and choose the nearest to points cnear."
    circles = circletttlines(cpa, cpb, cpc)
    return __nearest(circles, cnear)


def __nearest(circles, cnear):
    "Choose the nearest curcle to points cnear."
    if len(circles) == 0: return None, None
    dismin = None
    for ce, r in circles:
        dis = 0.0
        for c in cnear:
            dx, dy = c[1]-ce[1], c[0]-ce[0]
            th = atan2(dy, dx)   #Avoid computing hypotenuse; it may be huge for nearly parallel lines
            t = cos(th), sin(th)
            dx -= r*t[0]  #Find distance from the cirle perimeter
            dy -= r*t[1]  #Find distance from the cirle perimeter
            dis += dx*t[0]+dy*t[1] #Avoid computing hypotenuse; it may be huge for nearly parallel lines
        if dismin is None or dis<dismin:
            dismin = dis
            cemin = ce
            rmin = r
    return cemin, rmin


def circlettrlines(cpb, cpc, r):
    """Compute circle of known radius r, tangent to 2 lines.

    bb, cc: the first point of the 2 lines
    tb, tc: unit vectors of the 2 lines
    nb, nc: normal unit vectores of the 2 lines
    sib, sic: sign of the normal vectors nb, nc
    db, dc: distance of the first point of the line to the tangential point
    r: radius of circle
    ce: center of circle
    The following equations hold:
        bb + tb*db + sib*nb*r = ce
        cc + tc*dc + sic*nc*r = ce
    The signs are +1 or -1, thus we have 4 cases, which we compute to see which one
    drives to the solution.
    Subtracting 1st from the 2nd and teh 3d:
        cc-bb + tc*dc - tb*db + (sic*nc-sib*nb)*r = 0
    =>
        -tb*db + tc*dc = bb-cc + (sib*nb-sic*nc)*r
    """

    def solve():
        "Compute the circle center and radius for one set of signs sib, sic."
        A = [ [-tb[0], tc[0]],
              [-tb[1], tc[1]],
            ]
        #print()
        #for q in A: print(q)
        B = [bb[0]-cc[0] + (sib*nb[0]-sic*nc[0])*r,
             bb[1]-cc[1] + (sib*nb[1]-sic*nc[1])*r,
            ]
        #print(B)
        try: lineq(A, B)
        except ZeroDivisionError: return None, None
        db, dc = B
        ce   = (bb[0] + tb[0]*db + sib*nb[0]*r, bb[1] + tb[1]*db + sib*nb[1]*r)
        temp = (cc[0] + tc[0]*dc + sic*nc[0]*r, cc[1] + tc[1]*dc + sic*nc[1]*r)
        assert thanNear2(ce, temp)
        return ce, r

    circles = []
    bb, tb, nb = __vectorpar(cpb)
    if bb is None: return circles    #Failed: tb is the error message
    cc, tc, nc = __vectorpar(cpc)
    if cc is None: return circles    #Failed: tc is the error message

    for sib in (1.0, -1.0):
        for sic in (1.0, -1.0):
            ce, rr = solve()
            if ce is None: continue
            circles.append((ce, fabs(rr)))
    return circles


def circlettrlinesnear(cpb, cpc, r, cnear):
    "Compute circle of known radius r, tangent to 2 lines and choose the nearest to points cnear."
    circles = circlettrlines(cpb, cpc, r)
    return __nearest(circles, cnear)
