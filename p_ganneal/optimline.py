from math import atan2, cos, sin, sqrt, pi, atan, hypot, degrees

def fitline_endpoints(cc, p, vt):
    "Compute 2 end points on the line whic encompass all points cc."
    #xloc = (cc-p)@vt
    xloc = [(c[0]-p[0])*vt[0] + (c[1]-p[1])*vt[1] for c in cc]
    xlocmin = min(xloc)
    xlocmax = max(xloc)
    #c1 = p + xlocmin*vt
    #c2 = p + xlocmax*vt
    c1 = p[0] + xlocmin*vt[0], p[1] + xlocmin*vt[1]
    c2 = p[0] + xlocmax*vt[0], p[1] + xlocmax*vt[1]
    return c1, c2


def oldapproxtheta(cc):
    "Approximate the angle theta of best line which fit given points."
    pa = sum(c[0] for c in cc)/len(cc), sum(c[1] for c in cc)/len(cc)
    print("pa=", pa)
    vt = [0.0, 0.0]
    for c in cc:
        v = c[0]-pa[0], c[1]-pa[1]
        d = hypot(*v)
        if d > 0.0:
            if v[0]*vt[0]+v[1]*vt[1] < 0:  #Note that for the first point c, this expression is zero, and thus the condition is False
                v = -v[0], -v[1]   #Ensure that all linear segments point to the same direction
            vt[0] += v[0]/d
            vt[1] += v[1]/d
            second = False
    if vt[0] < 0.0: vt = -vt[0], -vt[1]  #Ensure angle is between -90 ~ 90 degrees
    th = atan2(vt[1], vt[0])
    return pa, th


def approxtheta(cca):
    "Approximate the angle theta of best line which fit given points."
    paa = sum(c[0] for c in cca)/len(cca), sum(c[1] for c in cca)/len(cca)   #centroid, world coordinates
    print("paa=", paa)
    cc = tuple((c[0]-paa[0], c[1]-paa[1]) for c in cca)  #relative coordiantes
    pa = (0.0, 0.0)     #centroid, relative coordinates

    vt = [0.0, 0.0]
    for c in cc:
        v = c[0]-pa[0], c[1]-pa[1]
        d = hypot(*v)
        if d > 0.0:
            if v[0]*vt[0]+v[1]*vt[1] < 0:  #Note that for the first point c, this expression is zero, and thus the condition is False
                v = -v[0], -v[1]   #Ensure that all linear segments point to the same direction
            vt[0] += v[0]/d
            vt[1] += v[1]/d
            second = False
    if vt[0] < 0.0: vt = -vt[0], -vt[1]  #Ensure angle is between -90 ~ 90 degrees
    th = atan2(vt[1], vt[0])
    return paa, cc, pa, th


def fitline_perp(cca):
    "Fit line to 2d points cc; minimize perp distance to points; return a point on the line and unit vector of the line."
    from scipy.optimize import least_squares
    import numpy
    from numpy.linalg import norm
    paa, cc, pa, th = approxtheta(cca)
    cc = numpy.array(cc)
    #pa, th = approxtheta(cc)
    vt = numpy.array([cos(th), sin(th)])
    vn = numpy.array([-vt[1], vt[0]])

    yloc = numpy.mean( (cc-pa)@vn )
    coef0 = [th, yloc]
    print('Initial approx: theta=%.3f deg    yloc=%.10e m' % (degrees(coef0[0]), coef0[1]))

    dyloc = numpy.zeros((numpy.size(cc, 0),))

    ftemp = lambda coef: f(coef, cc, pa)
    r = least_squares(ftemp, coef0, method='lm')
    coef = r.x
    print("success=", r.success, "status=", r.status, "message=", r.message)
    print('Final coeffs  : theta=%.3f deg    yloc=%.10e m' % (degrees(coef[0]), coef[1]));

    th = coef[0]
    yloc = coef[1]
    vt = numpy.array([cos(th), sin(th)])
    vn = numpy.array([-vt[1], vt[0]])
    p = pa + yloc*vn;              #relative coordinates
    rmsey = rmse(dyloc, (cc-pa)@vn - yloc)
    p = p[0]+paa[0], p[1]+paa[1]   #world coodinates
    print("p=", p)
    return p, vt, rmsey


def f(coef, cc, pa):
    import numpy
    th = coef[0]
    yloc = coef[1]
    m = numpy.size(cc, 0)
    dyloc = (cc-pa) @ numpy.array([-sin(th), cos(th)]) - yloc
    return dyloc

def rmse(ydata, ymodel):
    return sqrt( sum((ydata-ymodel)**2)/(len(ydata)-1) )


def fitline_simple(cca, optwhat="auto"):
    "Fit line to 2d points cc; minimize dy or dx distance to points; return a point on the line and unit vector of the line."
    paa, cc, pa, th = approxtheta(cca)
    print('Initial approx: theta=%.3f deg' % (degrees(th), ))

    sx = sum(c[0] for c in cc)
    sy = sum(c[1] for c in cc)
    sxy = sum(c[0]*c[1] for c in cc)
    n = len(cc)
    if optwhat == "auto":
        th1 = th % (2.0*pi)
        optdy = th1 < pi/4.0 or th1 > 2.0*pi-pi/4.0   #if True line is closer to horizontal the vertical, if False line is closer to verical
        if optdy: print("optimizing auto -> dy")
        else:     print("optimizing auto -> dx")
    elif optwhat == "dy":
        optdy = True
    else:
        optdy = False
    if optdy:                           #line is closer to horizontal the vertical
        #y = ax + b
        sx2 = sum(c[0]**2 for c in cc)
        a = (n*sxy - sx*sy) / (n*sx2 - sx**2)
        b = (sy - a*sx) / n
        p = pa[0], a*pa[0] + b
        th = atan(a)
    else:                               #line is closer to vertical than horizontal
        #x = ay + b
        sy2 = sum(c[1]**2 for c in cc)
        a = (n*sxy - sx*sy) / (n*sy2 - sy**2)
        b = (sx - a*sy) / n
        p = a*pa[1]+b, pa[1]            #Relative coordinates
        th = atan2(1.0, a*1.0)   #dy,dx

    vt = cos(th), sin(th)
    vn = -vt[1], vt[0]
    yloc = (p[0]-pa[0])*vn[0] + (p[1]-pa[1])*vn[1]
    print('Final coeffs  : theta=%.3f deg    yloc=%.10e m' % (degrees(th), yloc))

    temp = [(c[0]-p[0])*vn[0] + (c[1]-p[1])*vn[1] for c in cc]
    q = [0]*n
    rmsey = rmse1(q, temp)
    p = p[0]+paa[0], p[1]+paa[1]   #world coodinates
    print("p=", p)
    return p, vt, rmsey

def rmse1(ydata, ymodel):
    return sqrt( sum((ydata1-ymodel1)**2 for ydata1,ymodel1 in zip(ydata,ymodel))/(len(ydata)-1) )
