"Splines and equidistant splines."
from math import pi, atan2, sqrt, floor
import p_ggen
from .var import dpt

class ThanSpline:
    "A cubic Spline."

    def __init__(self, ic, xs, ys, zs=None):
        """Creates a spline through some xy points.
        include 'indspl.inc'
        integer*4 ns, ic     ! could be integer*2
        real*8 xs(*), ys(*), tmax1
        integer*4 i     ! could be integer*2
        real*8 a(nmax), b(nmax), c(nmax), d(nmax), pr, e
        character cret

  c-----ic = 0 : κανονική ανοικτή καμπύλη με καμπυλότητα 0 στα δύο άκρα
  c        = 1 : κανονική κλειστή καμπύλη με ίδια καμπυλότητα στα δύο "άκρα"
  c        = 2 : κλειστή καμπύλη με αντίθετη καμπυλότητα στα δύο "άκρα":
  c              μορφή σταγόνας
        """
        def calc(x):
            a = [0]; b = [0]; c = [0]; d = [0]
            for i in range(1, len(x)-1):
                a.append(t[i+1])
                b.append(2.0 * (t[i]+t[i+1]))
                c.append(t[i])
                d.append(3.0 * (t[i]**2 * (x[i+1]-x[i]) + t[i+1]**2 * (x[i]-x[i-1])) / (t[i]*t[i+1]))
            if ic == 0:
                b[0] = 1.0
                c[0] = 0.5
                d[0] = 1.5 * (x[1]-x[0]) / t[1]
                a.append(2.0)
                b.append(4.0)
                d.append(6.0 * (x[-1]-x[-2]) / t[-1])
                xt = lse(a, b, c, d, 0.0)
            else:
                b[0] = 2.0 + 2.0 * t[-1] / t[1]
                c[0] = t[-1] / t[1]
                d[0] = 3.0 * (x[1]-x[0]) * t[-1] / t[1]**2 - pr * 3.0 * (x[-2]-x[-1])/t[-1]
                e = pr
                xt = lse(a, b, c, d, e)
                xt.append(pr * xt[0])
            return xt
        pr = 1.0
        if ic == 2: pr = -1.0
        x = tuple(xs); y = tuple(ys)
        if zs is None: z = None
        else:          z = tuple(zs)
        t = [0.0]
        for i in range(1, len(x)):
            d = (x[i]-x[i-1])**2 + (y[i]-y[i-1])**2
            if z is not None: d += (z[i]-z[i-1])**2
            t.append(sqrt(d))
        self.t = t; self.tmax = sum(t)
        self.x = x; self.xt = calc(x)
        self.y = y; self.yt = calc(y)
        self.z = z
        if z is not None: self.zt = calc(z)


    def splfun(self, ts):
        "Evaluates the spline at the parameter ts."
        def calc(x, xt):
            a = 3.0 * (x[k]-x[i]) / t[k]**2 - (2.0*xt[i]+xt[k]) / t[k]
            b = 2.0 * (x[i]-x[k]) / t[k]**3 + (xt[i]+xt[k]) / t[k]**2
            xs = x[i] + tt * (xt[i] + tt*(a + tt*b))
            xts = xt[i] + tt * (2.0*a + tt*3.0*b)
            return xs, xts

        t = self.t
        tt = ts
        if tt <= 0.0: tt = 0.0
        elif (tt > self.tmax): tt = self.tmax
        tor = 0.0
        for i in range(1, len(t)):
            tor = tor + t[i]
            if (tt <= tor):
                tt = tt + t[i] - tor
                break
        else: assert 0, 'impossible error in ThanSpline.splfun(), lib p_gmath'

        k = i
        i = i-1
        xs, xts = calc(self.x, self.xt)
        ys, yts = calc(self.y, self.yt)
        if self.z is None: return xs, ys
        zs, zts = calc(self.z, self.zt)
        return xs, ys, zs


    def splder(self, ts):
        "Evaluates the derivatives with respect to parameter t of the spline at the parameter ts."
        def calc(x, xt):
            a = 3.0 * (x[k]-x[i]) / t[k]**2 - (2.0*xt[i]+xt[k]) / t[k]
            b = 2.0 * (x[i]-x[k]) / t[k]**3 + (xt[i]+xt[k]) / t[k]**2
            xs = x[i] + tt * (xt[i] + tt*(a + tt*b))
            xts = xt[i] + tt * (2.0*a + tt*3.0*b)
            return xs, xts

        t = self.t
        tt = ts
        if tt <= 0.0: tt = 0.0
        elif (tt > self.tmax): tt = self.tmax
        tor = 0.0
        for i in range(1, len(t)):
            tor = tor + t[i]
            if (tt <= tor):
                tt = tt + t[i] - tor
                break
        else: assert 0, 'impossible error in ThanSpline.splfun(), lib p_gmath'

        k = i
        i = i-1
        xs, xts = calc(self.x, self.xt)
        ys, yts = calc(self.y, self.yt)
        theta = dpt(0.5*pi - atan2(xts,yts)) * 180.0 / pi
        if self.z is None: return xts, yts, theta
        zs, zts = calc(self.z, self.zt)
        return xts, yts, zts, theta


    def than2Line(self, dt=0.0, ta=None, tb=None):
        "Represent the spline with straight line segments."
        if ta is None:
            ta = 0.0
            tb = self.tmax
        if dt <= 0.0:
            dt = self.tmax/len(self.x)   #Average distance between original line segments
            dt /= 4.0                    #4 points should be enough to show the curvature
        cs = []
        ts = []
        for t in p_ggen.frangec(ta, tb, dt):
            c = self.splfun(t)
            cs.append(c)
            ts.append(t)
        return cs, ts


#==========================================================================

def lse(a,b,c,d,e):
    "Solve tridiagonal system of linear equations."
    n = len(a)
    i = n - 1
    p = [0]*n
    while True:
        i -= 1
        b[i]=b[i]-c[i]*a[i+1] / b[i+1]
        d[i]=d[i]-c[i]*d[i+1] / b[i+1]
        d[1]=d[1]-e*d[i+1] / b[i+1]
        e=-e*a[i+1]/b[i+1]

        if (b[i] == 0.0):
            p[i-1]=d[i]/a[i]
            i=i-1
            d[i]=d[i]-b[i]*p[i]
            if i <= 0:
                p[1]=(d[0]-b[0]*p[0])/(b[0]+e)
                i=0
                break
            i-=1
            d[i]=d[i]-c[i]*p[i+1]
            d[1]=d[1]-e*d[i+1]/c[i+1]
            e=-e*a[i+1]/c[i+1]
        if i <= 0:
            p[0]=d[0]/(b[0]+e)
            i=0
            break

    while True:
        i += 1
        if i < n-1:
            if b[i+1] == 0.0:
                p[i+1]=(d[i]-a[i]*p[i-1])/c[i]
                i+=2
        p[i]=(d[i]-a[i]*p[i-1])/b[i]
        if i >= n-1: break
    return p


#==========================================================================

class EquidistantSpline:
    def __init__(self, Y):
        """
  CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
  C                                                                      C
  C                      I N I T S P                                     C
  C                                                                      C
  C  INITIALIZATION PROCEDURE FOR FAST 1-DIMENSIONAL EQUIDISTANT         C
  C  SPLINE INTERPOLATION, WITH FREE BOUNDARY END CONDITIONS             C
  C  REFERENCE: JOSEF STOER: EINFUHRUNG IN DIE NUMERISCHE MATHEMATIK     C
  C  I, SPRINGER 1972, PAGE 82 AND 86.                                   C
  C                                                                      C
  C----------------------------------------------------------------------C
  C                                                                      C
  C  PARAMETERS (REAL):                                                  C
  C                                                                      C
  C  Y...   GIVEN VALUES, Y(1), ..., Y(N)                                C
  C                                                                      C
  C  R...   SPLINE MOMENTS (1 ... N), TO BE USED BY FUNCTION 'SPLINE'    C
  C                                                                      C
  C  Q...   WORK-ARRAY, DECLARED AT LEAST 1:N                            C
  C                                                                      C
  C----------------------------------------------------------------------C
  C                                                                      C
  C  RENE FORSBERG, JULY 1983                                            C
  C                                                                      C
  CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
        """
        N = len(Y)
        self.Y = Y = list(Y)
        Y.insert(0, None)            #emulate Fortran indexes which start from 1
        Q = [None] * (N+1)
        self.R = R = [None] * (N+1)
        Q[1] = 0.0
        R[1] = 0.0
        for K in range(2, N):
            P = Q[K-1]/2+2
            Q[K] = -0.5/P
            R[K] = (3*(Y[K+1]-2*Y[K]+Y[K-1]) - R[K-1]/2)/P
        R[N] = 0.0
        for K in range(N-1, 1, -1):
            R[K] = Q[K]*R[K+1]+R[K]

#-----------------------------------------------------------------------

    def spline(self, X):
        """
  CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
  C                                                                      C
  C                          S P L I N E                                 C
  C                                                                      C
  C  FAST ONE-DIMENSIONAL EQUIDISTANT SPLINE INTERPOLATION FUNCTION.     C
  C  REFERENCE: JOSEF STOER: EINFUHRUNG IN DIE NUMERISCHE MATHEMATIK     C
  C  I, SPRINGER 1972, PAGE 81.                                          C
  C                                                                      C
  C----------------------------------------------------------------------C
  C                                                                      C
  C  PARAMETERS:                                                         C
  C                                                                      C
  C  X...  INTERPOLATION ARGUMENT (REAL), X = 1 FIRST DATA-POINT,        C
  C        X = N LAST DATA-POINT. OUTSIDE THE RANGE LINEAR EXTRA-        C
  C        POLATION IS USED.                                             C
  C                                                                      C
  C  Y...  REAL*8 ARRAY, 1 .. N : DATA VALUES                            C
  C                                                                      C
  C  R...  DO: SPLINE MOMENTS CALCULATED BY SUBROUTINE 'INITSP'          C
  C                                                                      C
  C----------------------------------------------------------------------C
  C                                                                      C
  C  PROGRAMMER:                                                         C
  C  RENE FORSBERG, JUNE 1983                                            C
  C                                                                      C
  CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
        """
        #X += 1.0
        Y = self.Y
        R = self.R
        N = len(Y) - 1
        if (X < 1):
            SPLINE = Y[1] + (X-1)*(Y[2]-Y[1]-R[2]/6)
        elif (X > N):
            SPLINE = Y[N] + (X-N)*(Y[N]-Y[N-1]+R[N-1]/6)
        else:
            J = int(floor(X))
            XX = X - J
            SPLINE = Y[J] + \
                     XX * ((Y[J+1]-Y[J]-R[J]/3-R[J+1]/6) + \
                     XX * (R[J]/2 + \
                     XX * (R[J+1]-R[J])/6))
        return SPLINE


if __name__ == "__main__":
    print(__doc__)
