from math import hypot, fabs, cos, sin
from p_ggen import frangec
from .varcon import PI2
from .lineq import linEq2
from .ellipse import _ellipsen

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
