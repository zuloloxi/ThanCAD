"Various math functions."
import p_ggen
from math import fabs, pi, log10, sqrt
from .varcon import PI2, thanThresholdx
import bisect


def dpt (gon):                    # Python guarantees that result has
    "Converts an angle (in rads) to normal form (between 0.0 and 2*PI)."
    return gon % PI2              # the same sign as PI2 i.e. positive

#def testGon():       # Test code for dpt function
#    t = [ (500, 140), (900, 180), (-500, 220), (-800, 280) ]
#    for g in t:
#        print dpt(g[0] / 180.0 * pi) / pi * 180, "should be", g[1]


def avgtheta(theta1, theta2, thtol=pi/4.0):  #used to be pi/20
    """Determine if the angles are within thtol, and return average, else none.

    thtol should be (considerably) less than pi/2 for this to have some meaning."""
#    prg("theta1=%.5f deg" % (theta1*180/pi,))
#    prg("theta2=%.5f deg" % (theta2*180/pi,))
    dth = fabs(theta2-theta1)       # WARNING: DO NOT USE FUNCTION dpt() HERE: ELSE ERROR
#    prg("dth=%.5f deg" % (dth*180/pi,))
    if dth < thtol:
        thbest = (theta1+theta2)*0.5
    elif dth > 2*pi-thtol:
        thbest = (theta1+theta2+2*pi)*0.5
    else:
        return None
#    prg("theta1=%.5f deg   theta2=%.5f deg   aver=%.5f deg" % (theta1*180/pi,theta2*180/pi,thbest*180/pi))
    return thbest


def rmse(A, B=None):
    """Compute the root mean squared error of the difference B-A.

    if B is None, the B is considered zero."""
    assert len(A) > 0
    if B is not None:
        assert len(A) == len(B)
        return sqrt(sum((b-a)**2 for a,b in zip(A, B)) / len(A))
    else:
        return sqrt(sum(a**2 for a in A) / len(A))


def linint(x1, y1, x2, y2, x):
    "Linear interpolation with no checking."
    return y1 + (y2-y1)/(x2-x1) * (x-x1)


def polylinint(x, y, xm):
    "Interpolate xm in a polyline; x are sorted in increasing order."
    i = bisect.bisect(x, xm)
    if i <= 0 or i>=len(x): return max(y) #x out of range; return arbitrary y
    #print(x[i-1], x[i], xm)
    return linint(x[i-1], y[i-1], x[i], y[i], xm)


def bilinint(va, ma1, wa1,
                 ma2, wa2,
             vb, mb1, wb1,
                 mb2, wb2,
             v, m):
    """Interpolates for w(w, m) using blinear interpolation.

    For dimensionless axial force v=va it is known:
        dimensionless moment ma1 -> needs wa1 reinforcement
        dimensionless moment ma2 -> needs wa2 reinforcement
    For dimensionless axial force v=vb it is known:
        dimensionless moment mb1 -> needs wb1 reinforcement
        dimensionless moment mb2 -> needs wb2 reinforcement
    With these data compute the reinforcment w for v and m.
    """

    wa = linint(ma1, wa1, ma2, wa2, m)
    wb = linint(mb1, wb1, mb2, wb2, m)
    w = linint(va, wa, vb, wb, v)
    return w


def sign(x, xsign):
    """Returns the number x with the sign of number xsign.

    The function goes into trouble to ensure that the (numeric)
    type of the returned value is the same with x.
    if xsign is zero the sign of x is unchanged."""
    if x >= 0:
        if xsign >= 0: return x
        else:         return -x
    else:
        if xsign > 0: return -x
        else:         return x

def fsign(x, xsign):
    """Returns the float number x with the sign of number xsign."""
    if   xsign > 0.0: return  fabs(x)
    elif xsign < 0.0: return -fabs(x)
    else:             return  float(x)


def roundlog(dh):
    "Round to 1, 2, 5 multiplied by an integer power of 10."
    lo = log10(dh)
#    print "log=", lo
    n = int(lo)
    if dh > 1.0: n += 1
#    print "n=", n
    dh1 = dh/10.0**n
#    print "dh1=", dh1
    dh1 = min((fabs(dh1-1.0), 1.0), (fabs(dh1-0.5), 0.5), (fabs(dh1-0.2), 0.2), (fabs(dh1-0.1), 0.1))[1]
#    print dh1
    dh1 *= 10.0**n
    return dh1


def roundStep(hmin, hmax, n=20):
    """Compute rounded step so that between hmin and hmax there are about n steps.

    hmin and hmax are probably not integer pollaplasia of the step."""
    dh = (hmax-hmin) / float(n)
    dh = roundlog(dh)
    return dh


def linintc(x1, y1, x2, y2, x):
    """Stable linear interpolation.

      x1, y1: known point 1
      x2, y2: known point 2
      x     : x coordinate where the function is to be computed
      If x1=x2=x then the rsult is the mean of y1, y2
    """
    if x2 < x1: x1, y1, x2, y2 = x2, y2, x1, y1
    xmax = max((fabs(x1), fabs(x2)))
    if xmax > thanThresholdx:
        dx = x2 - x1
        if dx/xmax > thanThresholdx:
            return y1 + (y2-y1)/(x2-x1) * (x-x1)   #Linear interpolation is safe
#-----Case of x1=x2
    if x < x1-thanThresholdx or x > x2+thanThresholdx: return None
    return y1*0.5 + y2*0.5          # Case of x1=x2=x


def thanErNear2(a, b):
    "Returns the error (difference) between two 2dimensional points taking numerical error into account."
    xa, ya = a[:2]
    xb, yb = b[:2]
    d = fabs(xb-xa) + fabs(yb-ya)
    v = (fabs(xa)+fabs(xb)+fabs(ya)+fabs(yb))*0.5
    if v < thanThresholdx: return d*0.5   #Absolute error
    return d/v                            #Relative error


def thanNear2(a, b):
    "Checks if two 2dimensional points coincide taking numerical error into account."
    xa, ya = a[:2]
    xb, yb = b[:2]
    d = fabs(xb-xa) + fabs(yb-ya)
    v = (fabs(xa)+fabs(xb)+fabs(ya)+fabs(yb))*0.5
    if v < thanThresholdx: return d < thanThresholdx
    return d < v*thanThresholdx


def thanNear3(a, b):
    "Checks if two 3dimensional points coincide taking numerical error into account."
    xa, ya, za = a[:3]
    xb, yb, zb = b[:3]
    d = fabs(xb-xa) + fabs(yb-ya) + fabs(zb-za)
    v = (fabs(xa)+fabs(xb)+fabs(ya)+fabs(yb)+fabs(za)+fabs(zb)) * 0.5
    if v < thanThresholdx: return d < thanThresholdx
    return d < v*thanThresholdx


def thanNearx(xa, xb):
    "Checks if two coordinates (x or y) coincide taking numerical error into account."
    d = fabs(xb-xa)
    v = (fabs(xa)+fabs(xb))*0.5
    if v < thanThresholdx: return d < thanThresholdx
    return d < v*thanThresholdx


def thanNearzero(small, big):
    "Checks if one coordinate (small) is zero with respect to the other (big), taking numerical error into account."
    d = fabs(small)
    v = fabs(big)
    if v < thanThresholdx: return d < thanThresholdx
    return d < v*thanThresholdx


def isZero(x, xmax=1000.0, fact=1.0e-6):
    "Test if x is zero compared to xmax; xmax is non-negative."
    if xmax < fact:
        return fabs(x) < fact
    return fabs(x) < fact*xmax


def pollap(hh, dhx, dhm):
    """Η Fn pollap επιστρέφει true αν το hh είναι ακέραιο πολλαπλάσιο του dhx.

    Η ακρίβεια dhm, σημαίνει ότι το hh είναι ακέραιο πολλαπλάσιο του dhx
    συν ή πλην dhm. Η dhm είναι για παράδειγμα dhx/10."""
    h1 = round(hh/dhx)
    pollap1 = fabs(hh-h1*dhx) < dhm
    return pollap1


def ICPconverged(er, erp, erpp, threshold, icp, prter):
    "Test if the ICP method converged and print warnings."
    if fabs(erp-er) < threshold and fabs(erpp-erp) < threshold:
        return True  #Perhaps er > erp and/or erp>erpp but both of them are too small -> convergence
    elif erp < erpp and fabs(erp-er) < threshold:
        return True  #Perhaps er > erp but it is too small -> convergence
    elif er > erp and erp > erpp:
        prter("WARNING: ICP STOPPED DUE TO INSTABILITY AFTER %d STEPS!" % icp)
        return True
    return False


def converged3(er, erp, erpp, threshold=thanThresholdx):
    "Test if an iterative procedure has converged checking 3 errors."
    if fabs(erp-er) < threshold and fabs(erpp-erp) < threshold:
        return 1  #Perhaps er > erp and/or erp>erpp but both of them are too small -> convergence
    elif erp < erpp and fabs(erp-er) < threshold:
        return 1  #Perhaps er > erp but it is too small -> convergence
    elif er > erp and erp > erpp:
        return -1          #Stopped due to instability
    return 0


def rootBisection(fun, a,b,TOL):
    "Find the root of fun() using bisection method."
    c = (a+b)/2.0
    fa = fun(a)
    if fa == 0.0: return a
    fb = fun(b)
    if fb == 0.0: return b
    assert fa*fb < 0.0, "f(a)*f(b) should be <= 0.0"
    while (b-a)/2.0 > TOL:
        c = (a+b)/2.0
        #print(c)
        fc = fun(c)
        if fc==0.0:
            return c
        elif fa*fc <= 0.0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc
    return (a+b)/2.0


def rootBracket(fun, a,b, step):
    "Bracket a solution of function fun searching from a to b by step."
    xa = a
    ya = fun(a)
    for xb in p_ggen.frangec(a+step, b, step, tol=0.1):
        yb = fun(xb)
        if fsign(1, ya)*fsign(1, yb) <= 0.0: return xa, xb
        xa = xb
        ya = yb
    return None, None


def rootBracketnotgoodidea(fun, a,b, step):
    "Bracket a solution of function fun searching from a to b by step."
    x = [a]
    y = [fun(a)]
    for xb in p_ggen.frangec(a+step, b, step, tol=0.1):
        x.append(xb)
        y.append(fun(xb))
        if fsign(y[-2])*fsign(y[-1]) <= 0.0: return x[-1], x[-2]
    istep = 2
    imax = len(x)
    while istep < imax//2:
        for i in range(istep, imax, istep):
            ip = i - istep
            if fsign(y[ip])*fsign(y[i]) <= 0.0: return x[ip], x[i]
        istep *= 2
    return None, None


from p_gnum import zeros, Float

def dfridr(func,x,h):
    "Numerical computation of derivative of function."
    CON=1.4; CON2=CON*CON; BIG=1.0e100; NTAB=10; SAFE=2.0
    a = zeros((NTAB+1, NTAB+1), Float)
    assert h > 0.0, 'h must be nonzero in dfridr'
    hh=h
    a[1,1] = (func(x+hh)-func(x-hh))/(2.0*hh)
    err=BIG
    for i in range(1, NTAB+1):
        hh=hh/CON
        a[1,i]=(func(x+hh)-func(x-hh))/(2.0*hh)
        fac=CON2
        for j in range(2, i+1):
            a[j,i]=(a[j-1,i]*fac-a[j-1,i-1])/(fac-1.0)
            fac=CON2*fac
            errt=max((fabs(a[j,i]-a[j-1,i]), fabs(a[j,i]-a[j-1,i-1])))
            if errt <= err:
                err=errt
                dfridr1=a[j,i]
        if fabs(a[i,i]-a[i-1,i-1]) >= SAFE*err: return dfridr1, err

    return dfridr1, err


def partialder(f, j, param):
    "Compute the partial derivative of function b with respect to variable j of the function."
    par = list(param)
    def ff(a):
        par[j] = a
        return f(par)
    return dfridr(ff, param[j], 0.1)


from p_gnum import transpose, matrixmultiply, solve_linear_equations, LinAlgError, lstsq

def lsmsolve(A, B):
    "Solve the Least square method problem defined by matrixes A and B."
    try:
        x, residual, rank, s = lstsq(A, B, rcond=-1.0)
    except LinAlgError as why:
        print(why)
        return None, why
    try: return x[:, 0], ""  #2016_01_12thanasis:This converts shape from (333, 1) to (333,)
                             #Otherwise x[1] is an array, not a scalar
    except: return x, ""  #Thanasis2016_04_16: Changed again to normal???
    #The following code is the equivalent of the above code, without using lstsq()
    #It is not used any more.
    AT = transpose(A)
    AA = matrixmultiply(AT, A)
    BB = matrixmultiply(AT, B)
    try:
        BB = solve_linear_equations(AA, BB)
    except LinAlgError as why:
        import p_gnum
        print("det(AA)=", p_gnum.det(AA))
        print("AA=", AA)
        print("BB=", BB)
        return None, why
    return BB, ""


if __name__ == "__main__":
    print(__doc__)
