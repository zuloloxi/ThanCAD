"Ellipse related module."
from math import pi, cos, sin, atan2, sqrt, fabs
from p_gnum import (array, matrixmultiply, transpose, inv, Float, eig, zeros,
                    LinAlgError, solve_linear_equations)
from p_ggen import frangec
from .var import thanNearx, lsmsolve
from .varcon import thanThresholdx, PI2, PI05


def ellipse5Fit(x, y):
    """Fit the points to F(x, y) = ax2 + bxy + cy2 + dx + ey + f  = 0

    If the points define a parabola or hyperbola, make the best fit assuming
    that they define an ellipse.
    Radim Hal, Jan Flusser method.
    """
    xy = list(zip(x,y))
    D1 = array([(x1**2, x1*y1, y1**2) for (x1,y1) in xy]) # quadratic part of the design matrix
    D2 = array([(x1, y1, 1) for (x1,y1) in xy])           # linear part of the design matrix
    S1 = matrixmultiply(transpose(D1), D1)                # quadratic part of the scatter matrix
    S2 = matrixmultiply(transpose(D1), D2)                # combined part of the scatter matrix
    S3 = matrixmultiply(transpose(D2), D2)                # linear part of the scatter matrix
    T = - matrixmultiply(inv(S3), transpose(S2))          # for getting a2 from a1
    M = S1 + matrixmultiply(S2, T)                        # reduced scatter matrix
    #M = [M(3, :) ./ 2; - M(2, :); M(1, :) ./ 2]; % premultiply by inv(C1)
    temp = zeros((3,3), Float)
    temp[0, :] =  M[2, :] / 2.0
    temp[1, :] = -M[1, :]
    temp[2, :] =  M[0, :] / 2.0
    M = temp
    # [evec, eval] = eig(M);         % solve eigensystem
    eval_, evec = eig(M)                                  # solve eigensystem
    # cond = 4 * evec(1, :) .* evec(3, :) - evec(2, :) .^ 2; % evaluate a'Ca
    cond = 4.0*evec[0, :]*evec[2, :] - evec[1, :]**2      # evaluate a'Ca
    # a1 = evec(:, find(cond > 0));  % eigenvector for min. pos. eigenvalue
##    print cond
    temp = [(cond1.real, i) for i,cond1 in enumerate(cond) if cond1.imag == 0 and cond1.real > 0.0]
    if len(temp) == 0:
        print("There should be exactly 1 positive eigenvalue: None was found")
        return None, "Failed to fit ellipse."
    if len(temp) > 1:
        print("There should be exactly 1 positive eigenvalue: more were found")
        return None, "Failed to fit ellipse."
    i = min(temp)[1]
    a1 = evec[:, i]
##    print i, a1
    # a = [a1; T * a1];              % ellipse coefficients
    a = [None]+list(a1)+list(matrixmultiply(T, a1))              # ellipse coefficients
    v = ellipse2Standard5(a)
    if v is None: return None, "Failed to convert to standard form: probably degenerate ellipse."
    return v[1:6], ""


def ellipse4Fit(x, y):
    """Fit the points to F(x, y) = ax2 + bxy + cy2 + dx + ey + f  = 0

    where b=0; the axes of the ellipse are parallel to the x,y axes.
    If the points define a parabola or hyperbola, make the best fit assuming
    that they define an ellipse.
    Stamos method based on Radim Hal, Jan Flusser.
    """
    xy = list(zip(x,y))
    D1 = array([(x1**2, y1**2) for (x1,y1) in xy])        # quadratic part of the design matrix
    D2 = array([(x1, y1, 1) for (x1,y1) in xy])           # linear part of the design matrix
    S1 = matrixmultiply(transpose(D1), D1)                # quadratic part of the scatter matrix
    S2 = matrixmultiply(transpose(D1), D2)                # combined part of the scatter matrix
    S3 = matrixmultiply(transpose(D2), D2)                # linear part of the scatter matrix
    T = - matrixmultiply(inv(S3), transpose(S2))          # for getting a2 from a1
    M = S1 + matrixmultiply(S2, T)                        # reduced scatter matrix
#    M = array([ [M[2,1]*0.5, M[2,2]*0.5],                # premultiply by inv(C1)
#                [M[1,1]*0.5, M[1,2]*0.5],
#                ]
    M = array([ [M[1,0]*0.5, M[1,1]*0.5],                 # premultiply by inv(C1)
                [M[0,0]*0.5, M[0,1]*0.5],
                ])
    # [evec, eval] = eig(M);         % solve eigensystem
    eval_, evec = eig(M)                                  # solve eigensystem
    # cond = 4 * evec(1, :) * evec(2, :)                   # evaluate a'Ca
    cond = 4 * evec[0, :] * evec[1, :]                    # evaluate a'Ca
    # a1 = evec(:, find(cond > 0));  % eigenvector for min. pos. eigenvalue
##    print cond
    temp = [(cond1.real, i) for i,cond1 in enumerate(cond) if cond1.imag == 0 and cond1.real > 0.0]
    if len(temp) == 0:
        print("There should be exactly 1 positive eigenvalue: None was found")
        return None, "Failed to fit ellipse."
    if len(temp) > 1: 
        print("There should be exactly 1 positive eigenvalue: more were found")
        return None, "Failed to fit ellipse."
    i = min(temp)[1]
    a1 = evec[:, i]
##    print i, a1
    # a = [a1; T * a1];              % ellipse coefficients
    a = [None, a1[0], 0.0, a1[1]]+list(matrixmultiply(T, a1))              # ellipse coefficients
    v = ellipse2Standard4(a)
    if v is None: return None, "Failed to convert to standard form: probably degenerate ellipse."
    return v[1:6], ""


def ellipse5Lsm(x, y):
    """Fit the points to F(x, y) = ax2 + bxy + cy2 + dx + ey + f  = 0

    The axes of the ellipse are not parallel to the x,y axes.
    The points may define a parabola or hyperbola. In this case
    it returns None.
    """
    #F(x y) = 1 x2 + bxy + cy2 + dx + ey + f = 0 =>
    #-x2 = bxy + cy2 + dx + ey + f 
    n = len(x)
    nunk = 5
    A = zeros((n, nunk), Float)
    B = zeros((n, ), Float)
    for i in range(n):
        A[i, :] = x[i]*y[i], y[i]**2, x[i], y[i], 1.0
        B[i] = -x[i]**2
    #a = lsmLinDo(A, B)
    a, ter = lsmsolve(A, B)
    if a is None: return None, "LSM failed: probably degenerate ellipse."
    a, b, c, d, e, f = 1.0, a[0], a[1], a[2], a[3], a[4]
    if b**2-4.0*a*c >= 0.0: return None, "The points do not define an ellipse."
    v = ellipse2Standard5((None, a, b, c, d, e, f))
    if v is None: return None, "Failed to convert to standard form: probably degenerate ellipse."
    return v[1:6], ""


def ellipse4Lsm(x, y):
    """Fit the points to F(x, y) = ax2 + bxy + cy2 + dx + ey + f  = 0

    where b=0; the axes of the ellipse are parallel to the x,y axes.
    The points may define a parabola or hyperbola. In this case
    it returns None.
    """
    #F(x y) = 1 x2 + 0.0 xy + cy2 + dx + ey + f = 0 =>
    #-x2 = cy2 + dx + ey + f 
    n = len(x)
    nunk = 4
    A = zeros((n, nunk), Float)
    B = zeros((n, ), Float)
    for i in range(n):
        A[i, :] = y[i]**2, x[i], y[i], 1.0
        B[i] = -x[i]**2
#    a = lsmLinDo(A, B)
    a, ter = lsmsolve(A, B)
    if a is None: return a, "LSM failed: probably degenerate ellipse."
    a, b, c, d, e, f = 1.0, 0.0, a[0], a[1], a[2], a[3]
    if b**2-4.0*a*c >= 0.0: return None, "The points do not define an ellipse."
    v = ellipse2Standard4((None, a, b, c, d, e, f))
    if v is None: return None, "Failed to convert to standard form: probably degenerate ellipse."
    return v[1:6], ""


def ellipse2Standard5(a):
    """Convert the ellipse representation from conic to standard form.

    conic form: F(x, y) = ax2 + bxy + cy2 + dx + ey + f  = 0
    standard form: ((x-cx)/r1)^2 + ((y-cy)/r2)^2 = 1   -> see ellips2line below
    """
    # get ellipse orientation
    try:
        theta = atan2(a[2], a[1]-a[3]) / 2
    except:
        theta = 0.0     #This means that a) the axes lengths are the same, which means 
                        #theta is irrelevant and b) a[2]==zero, which means that theta=0

    # get scaled major/minor axes
    ct = cos(theta)
    st = sin(theta)
    ap = a[1]*ct*ct + a[2]*ct*st + a[3]*st*st
    cp = a[1]*st*st - a[2]*ct*st + a[3]*ct*ct

    # get translations
#    T = [[a[1] a[2]/2]' [a[2]/2 a[3]]'];
    T = array([ [a[1],   a[2]/2],
                [a[2]/2, a[3]  ],
              ])
    t = matrixmultiply(-inv(2*T), array([a[4], a[5]]))
    cx = t[0]
    cy = t[1]

    # get scale factor
    #val = t'*T*t;
    val = matrixmultiply(matrixmultiply(transpose(t), T), t)
    scale = 1 / (val- a[6]);

    # get major/minor axis radii
    try:
        r1 = 1/sqrt(scale*ap);
        r2 = 1/sqrt(scale*cp);
    except:
        v = None
    else:
        v = [None, r1, r2, cx, cy, theta]
    return v


def ellipse2Standard4(a):
    """Convert the ellipse representation from conic to standard form.

    conic form: F(x, y) = ax2 + bxy + cy2 + dx + ey + f  = 0
    standard form: ((x-cx)/r1)^2 + ((y-cy)/r2)^2 = 1
    Here we know that theta == 0.0
    """
    v = ellipse2Standard5(a)
    if v is None: return v
#    print v
    theta = v[-1] % PI2
#    print "theta=", theta
    if thanNearx(theta, 0.0) or thanNearx(theta, PI2):
        pass
    elif thanNearx(theta, PI05):
        v[1], v[2] = v[2], v[1]
    else:
        assert 0, "Theta should be zero!!!"
    v[-1] = 0.0
    return v



def ellipseLength(a, b):
    """Compute the length of an ellipse given the semiaxes.

    See ellipse/bib_properties/ellipse.odt."""
    a2 = a*a
    a4 = a2*a2
    b2 = b*b
    b4 = b2*b2
    q = b4 + 60.0*a*b2*b + 134*a2*b2 + 60.0*a2*a*b + a4
    r = (432.0*(a2-b2)**2*(a-b)**6.0*b*a)/q**3
    v1 = b*a*(15.0*b4 + 68.0*a*b2*b + 90.0*a2*b2 + 68.0*a2*a*b + 15.0*a4)
    v2 = -a4*a2 - b4*b2 + 126.0*a*b4*b + 1041.0*a2*b4 + 1764.0*a2*a*b2*b + 1041.0*a4*b2 + 126.0*a4*a*b
    arp = v1
    oros = arp
    c = oros
    for n in range(1, 10):
        ar = arp + v2
        oros *= 5.0/144.0*ar/arp*r/n**2
        c += oros
        if n>3 and fabs(oros/c) < thanThresholdx: break   #At least 3 steps
        arp = ar
#        print c * 8*pi/q**(5.0/4.0)
    c *= 8*pi/q**(5.0/4.0)
#    print c
#    print ellipseLengthApprox(a, b), "approx"
    return c


def ellipseLengthApprox(a, b):
    """Compute approximate length of an ellipse given the semiaxes.

    See ellipse/bib_properties/ellipse.odt."""
    ab2 = ((a-b)/(a+b))**2
    c1 = pi*(a+b)*(1 + (3*ab2)/(10+sqrt(4-3*ab2)) )  #A very good approximation
    return c1


def ellipseArea(a, b):
    "Compute the length of an ellipse given the semiaxes."
    return pi*a*b


def ellipse2Lineold(cx, cy, a, b, theta, dt=0.0):
    """Represent an ellipse with straight line segments.

    standard form: ((x-cx)/a)^2 + ((y-cy)/b)^2 = 1
    """
    a = fabs(a)
    b = fabs(b)
    ab = max(a, b)
    if thanNearx(ab, 0.0): return ()     #Invalid ellipse
    dphi = dt/ab    #Approximate dphi like a circle with radius the biggest of the semi-axes
    if dt <= 0.0 or thanNearx(dphi, 0.0):
        n = 16                           #Something wrong with dt; use a logical value of points
    else:
        n = int(PI2/dphi+0.5)
        if n < 8: n = 8                  #At least 8 points for a full ellipse
    dphi = PI2 / n

    cosf = cos(theta)
    sinf = sin(theta)
    cs = []
    for phi in frangec(0.0, PI2, dphi):
        x = a*cos(phi)
        y = b*sin(phi)
        xt = x*cosf - y*sinf
        yt = x*sinf + y*cosf
        cs.append((cx+xt, cy+yt))
    return cs


def ellipse2Line(cx, cy, a, b, phia=0.0, phib=PI2, theta=0.0, dt=0.0):
    """Represent an elliptic arc between angles phia and phib, with straight line segments; dt refers to length units.

    standard form: ((x-cx)/a)^2 + ((y-cy)/b)^2 = 1
    Note: phib should be bigger than phia or nothing will be returned.
    The anti-clockwise anges are positive. To plot an elliptic arc from 1.5pi to 0.5pi
    set phia=1.5pi and phib=0.5pi+2pi=2.5pi.
    """
    a = fabs(a)
    b = fabs(b)
    ab = max(a, b)
    if thanNearx(ab, 0.0): return (), () #Invalid ellipse
    phiab = phib - phia                  #angle span of elliptic arc
    if phiab < 0.0: return (), ()               #Zero lengthed elliptic arc
    if thanNearx(phiab*ab, 0.0): return (), ()  #Zero lengthed elliptic arc
    n16 = phiab/PI2 * 16.0               #a logical value of points: 16 points for full ellipse
    dphi = dt/ab    #Approximate dphi based on a circle with radius the biggest of the semi-axes
    if dt <= 0.0 or thanNearx(dphi, 0.0):
        n = n16     #Something wrong with dt; use a logical value of points: 16 points for full ellipse
    else:
        n = max(phiab/dphi, n16/2.0)  #At least 8 points for a full ellipse
    if n < 3.0: n = 3.0               #At least 3 points for any elliptic arc
    dphi = phiab / n
    print("****ellipse2Line: dphi=", dphi)

    cosf = cos(theta)
    sinf = sin(theta)
    cs = []
    phis = []
    for phi in frangec(phia, phib, dphi):
        x = a*cos(phi)
        y = b*sin(phi)
        xt = x*cosf - y*sinf
        yt = x*sinf + y*cosf
        cs.append((cx+xt, cy+yt))
        phis.append(phi)
    return cs, phis



def _ellipsen(ab, phia, phib, dt):
    """Determine dphi and number of linear segments for line approximation of an allipse."

    ab is the bigger of the semi axes."""
    if thanNearx(ab, 0.0): return None, None        #Invalid ellipse
    phiab = phib - phia                             #angle span of elliptic arc
    if phiab < 0.0: return None, None               #Zero lengthed elliptic arc
    if thanNearx(phiab*ab, 0.0): return None, None  #Zero lengthed elliptic arc
    n16 = phiab/PI2 * 16.0               #a logical value of points: 16 points for full ellipse
    dphi = dt/ab    #Approximate dphi based on a circle with radius the biggest of the semi-axes
    if dt <= 0.0 or thanNearx(dphi, 0.0):
        n = n16     #Something wrong with dt; use a logical value of points: 16 points for full ellipse
    else:
        n = max(phiab/dphi, n16/2.0)  #At least 8 points for a full ellipse
    if n < 3.0: n = 3.0               #At least 3 points for any elliptic arc
    dphi = phiab / n
    print("****ellipse2Line: dphi=", dphi)
    return n, dphi


def circle3Lsm(x, y):
    """Fit the points to F(x, y) = x2 + y2 -2ax -2by +a2 +b2 -r2 = 0

    The points may not define a circle. In this case
    it returns None.
    """
    #F(x y) = x2 + y2 -2ax -2by +a2 +b2 -r2 = 0 =>
    #x2 + y2 = 2ax + 2by - a2 -b2 +r2  = 2ax +2by + c 
    n = len(x)
    nunk = 3
    A = zeros((n, nunk), Float)
    B = zeros((n, ), Float)
    for i in range(n):
        A[i, :] = 2*x[i], 2*y[i], 1.0
        B[i] = x[i]**2+y[i]**2
    sol, ter = lsmsolve(A, B)
    if sol is None: return None, ter
    a, b, c = sol
    r2 = c + a**2 + b**2
    if r2 < 0.0: return None, "Not a circle"
    return a, b, sqrt(r2)


if __name__ == "__main__":
    print(__doc__)
