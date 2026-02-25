from math import pi, cos, sin
from p_gmath import thanLineSeg2


def gfill(dxf, x, y, phi, d, icol):
    "Fill an area with lines."
#---Για να θεωρηθεί κλειστή γραμμή πρέπει: x(1)=x(n) και y(1)=y(n)
    n = len(x)
    if n < 3: return
    closed = x[0] == x[-1] and y[0] == y[-1]
#---compute tangent and normal vector------------------------
    dd = phi * pi / 180.0
    t  = cos(dd), sin(dd)
    an = -t[1], t[0]
#---find lowest and highest coordinates (with respect to n)
    pmin =  an[0] * x[0] + an[1] * y[0]
    pmax =  pmin
    ipmin = 0
    ipmax = ipmin
    for i in range(1, n):
        dd = an[0] * x[i] + an[1] * y[i]
        if dd < pmin:
            pmin = dd
            ipmin = i
        if dd > pmax:
            pmax = dd
            ipmax = i

    if closed:
        ileft  = ipmax
        iright = ipmax
    else:
        ileft  = 1
        iright = n
#---begin iteration-----------------------------------------------
    dxf.thanDxfSetColor(icol)
    dd = d
    while dd <= pmax-pmin:
        c = x[ipmin] + dd * an[0], y[ipmin] + dd * an[1]
        tom1 = intSide(ipmin, ileft,  -1, c, t, x, y)       # left
        if tom1 is not None:
            tom2 = intSide(ipmin, iright,  1, c, t, x, y)
            if tom2 is not None:                                # right
                dxf.thanDxfPlot(tom1[0], tom1[1], 3)        # plot line
                dxf.thanDxfPlot(tom2[0], tom2[1], 2)
        dd = dd + d


def intSide(i1, i2, idir, c, t, x, y):
    i = i1
    n = len(x)
    while True:
        if i == i2: return None
        ip = i
        i = (i + idir) % n           # this implies that i==n -> 0  and i==-1 -> n-1
        a = x[ip], y[ip]
        b = x[i], y[i]
        tom = thanLineSeg2(c, t, a, b)
        if tom is not None: return tom
