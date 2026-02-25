from math import pi, atan2, cos, sin, hypot
from p_ggen import iterby2, frange

def regularPolygon(n, icase, ca, cb):
    """Compute the coordinates of regular polygon of n corners.

    case 0: ca is center and cb is the first point: |cb-ca| is the radius of circumscribed circle
    case 1: ca is center and cb is the middle of the first edge: |cb-ca| is the radius of inscribed circle
    case 2: ca, cb are the corners of the first edge: |cb-ca| is the length of the edges
    """
    dphi = pi / n
    theta = atan2(cb[1]-ca[1], cb[0]-ca[0])
    if icase == 0:
        cc = ca
        r = hypot(cb[1]-ca[1], cb[0]-ca[0])
    elif icase == 1:
        cc = ca
        a = hypot(cb[1]-ca[1], cb[0]-ca[0])
        r = a / cos(dphi)
        theta += -dphi   # -2*dphi*0.5
    elif icase == 2:
        s = hypot(cb[1]-ca[1], cb[0]-ca[0])
        r = s / (2.0 * sin(dphi))
        theta += -pi*0.5 - dphi  # -2*dphi*0.5
        cc = list(ca)
        cc[0] -= r * cos(theta)
        cc[1] -= r * sin(theta)
    else:
        raise ValueError('Unknown case number: {}'.format(icase))
    cp = []
    for i in range(n):
        ce = list(cc)
        ce[0] += r*cos(theta)
        ce[1] += r*sin(theta)
        theta += 2.0*dphi
        cp.append(ce)
    cp.append(list(cp[0]))
    return cp


def plotregularpolygon(plotline, n, icase, xa, ya, xb, yb):
    "Plot a regular polygon of n corners."
    cp = regularPolygon(n, icase, (xa, ya), (xb, yb))
    for ca, cb in iterby2(cp):
        plotline(ca[0], ca[1], cb[0], cb[1])
