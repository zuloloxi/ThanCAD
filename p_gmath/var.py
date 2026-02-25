# -*- coding: iso-8859-7 -*-
from math import fabs, pi
from varcon import PI2, thanThresholdx

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


def linint(x1, y1, x2, y2, x):
    "Linear interpolation with no checking."
    return y1 + (y2-y1)/(x2-x1) * (x-x1)


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

def linEq2 (a, b, c, d, e, f):
      """Solve a system of 2 linear equations.

                                 | c   b |                | a   c |
                                 | f   e |                | d   f |
      ax + by = c    =>     x = -----------   ,      y = -----------
      dx + ey = f                | a   b |                | a   b |
                                 | d   e |                | d   e |
      """
      delta = a*e - d*b
      if delta == 0.0: return None, None
      x = (c*e - f*b) / delta
      y = (a*f - d*c) / delta
      return (x, y)


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


def isZero(x, xmax=1000.0, fact=1.0e-6):
    "Test if x is zero compared to xmax; xmax is non-negative."
    if xmax < fact:
        return fabs(x) < fact
    return fabs(x) < fact*xmax


def ICPconverged(er, erp, erpp, threshold, icp, prter):
    "Test if the ICP method converged and print warnings."
    if fabs(erp-er) < threshold and fabs(erpp-erp) < threshold:
        return True  #Perhaps er > erp and/or erp>erpp but both of them are too small -> convergence
    elif erp < erpp and fabs(erp-er) < threshold:
        return True  #Perhaps er > erp but it is too small -> convergence
    elif er > erp and erp > erpp:
        prter(Tmatch["WARNING: ICP STOPPED DUE TO INSTABILITY AFTER %d STEPS!"] % icp)
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


from p_gnum import zeros, Float

def dfridr(func,x,h):
      "Numerical computation of derivative of function."
      CON=1.4; CON2=CON*CON; BIG=1.0e100; NTAB=10; SAFE=2.0
      a = zeros((NTAB+1, NTAB+1), Float)
      assert h > 0.0, 'h must be nonzero in dfridr'
      hh=h
      a[1,1] = (func(x+hh)-func(x-hh))/(2.0*hh)
      err=BIG
      for i in xrange(1, NTAB+1):
          hh=hh/CON
          a[1,i]=(func(x+hh)-func(x-hh))/(2.0*hh)
          fac=CON2
          for j in xrange(2, i+1):
              a[j,i]=(a[j-1,i]*fac-a[j-1,i-1])/(fac-1.0)
              fac=CON2*fac
              errt=max((fabs(a[j,i]-a[j-1,i]), fabs(a[j,i]-a[j-1,i-1])))
              if errt <= err:
                  err=errt
                  dfridr1=a[j,i]
          if fabs(a[i,i]-a[i-1,i-1]) >= SAFE*err: return dfridr1, err

      return dfridr1, err


def partialder(f, j, *param):
    "Compute the partial derivative of function b with respct to variable j of the function."
    par = list(param)
    def ff(a):
        par[j] = a
        return f(*par)
    return dfridr(ff, param[j], 0.1)


def testder():
      from math import exp
      while True:
          x = float(raw_input("x: "))
          df = exp(x)
          dfn, er = dfridr(exp, x, 0.2*fabs(x))
          print df, dfn, er


def testpartialder():
      from math import exp, cos, sin
      def g(x, y): return exp(x)*sin(x+y)
      while True:
          x, y = map(float, raw_input("x, y: ").split())
          dx, err = partialder(g, 0, x, y)
          dy, err = partialder(g, 1, x, y)
          print "x, y=", x, y
          print "dg/dx analytic:", exp(x)*sin(x+y)+exp(x)*cos(x+y), "numerical:", dx
          print "dg/dy analytic:", exp(x)*cos(x+y), "numerical:", dy


from p_gnum import transpose, matrixmultiply, solve_linear_equations, LinAlgError

def lsmsolve(A, B):
    "Solev the Least square method problem defined by matrixes A and B."
    AT = transpose(A)
    AA = matrixmultiply(AT, A)
    BB = matrixmultiply(AT, B)
    try: BB = solve_linear_equations(AA, BB)
    except LinAlgError, why: return None, why
    return BB, ""

if __name__ == "__main__": testpartialder()
