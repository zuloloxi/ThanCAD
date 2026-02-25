import sys
from math import sqrt, cos, sin, pi, exp, sqrt, fabs
from varcon import PI05, PIR


def fresnel(x):
    "Compute the Fresnel integrals."
    EPS=6.e-8
    MAXIT=100
    FPMIN=1.e-30
    XMIN=1.5

    ax=abs(x)
    if ax < sqrt(FPMIN):
        s=0.
        c=ax
        if x < 0.: c=-c; s=-s
        return s, c
    elif ax <= XMIN:
        sum=0.
        sums=0.
        sumc=ax
        sign=1.
        fact=PI05*ax*ax
        odd = True
        term=ax
        n=3
        for k in range(1, MAXIT+1):
            term=term*fact/k
            sum=sum+sign*term/n
            test=abs(sum)*EPS
            if odd:
                sign=-sign
                sums=sum
                sum=sumc
            else:
                sumc=sum
                sum=sums
            if term < test:
                s=sums
                c=sumc
                if x < 0.: c=-c; s=-s
                return s, c

            odd = not odd
            n += 2

        print 'series failed in fresnel'
        return None
    else:
        pix2=pi*ax*ax
        b=complex(1.,-pix2)
        cc=1./FPMIN
        d=1./b
        h=d
        n=-1
        for k in range(2,MAXIT+1):
            n += 2 
            a=-n*(n+1)
            b=b+4.
            d=1./(a*d+b)
            cc=b+a/cc
            del1=cc*d
            h=h*del1
#            if absc(del1-1.) < EPS:
            if abs(del1.real-1.) + abs(del1.imag) < EPS:
                h=h*complex(ax,-ax)
                cs=complex(.5,.5)*(1.-complex(cos(.5*pix2),sin(.5*pix2))*h)
                c=cs.real
                s=cs.imag
                if x < 0.: c=-c; s=-s
                return s, c
        print 'cf failed in fresnel'
        return None


def klotXy(A, L, pr=1):
    "Calculates xy coordinates of klotoidis of parameter A at distance L from start."
    s, c = fresnel(L / A / PIR)
    apir = A * PIR
    return (apir*c, apir*s*pr)


def dokKlot():
    from p_gchart import ThanChart, vis
    ch = ThanChart()
    al = 40.83
    r = 30.0
    a = sqrt(al*r)
    xth = 0.0; xx = []; yy = []
    for i in range(250):
        xth = xth + 1.0
        v = klotXy(a, xth, 1.0)
#        print  "%15.3f%15.3f%15.3f" % (xth, v[0], v[1])
        xx.append(v[0]); yy.append(v[1])

    ch.curveAdd(xx, yy, style="christar", color="magenta", fill="yellow", size=10)
    ch.curveAdd(xx, yy, style="continuous", color="blue", size=5)
    vis(ch)

#============================================================================

# from: http://www.cs.princeton.edu/introcs/21function/ErrorFunction.java.html
# Implements the Gauss error function.
#   erf(z) = 2 / sqrt(pi) * integral(exp(-t*t), t = 0..z)
#
# fractional error in math formula less than 1.2 * 10 ^ -7.
# although subject to catastrophic cancellation when z in very close to 0
# from Chebyshev fitting formula for erf(z) from Numerical Recipes, 6.2
def erf(z):
        t = 1.0 / (1.0 + 0.5 * fabs(z))
        # use Horner's method
        ans = 1 - t * exp( -z*z -  1.26551223 +
                                                t * ( 1.00002368 +
                                                t * ( 0.37409196 + 
                                                t * ( 0.09678418 + 
                                                t * (-0.18628806 + 
                                                t * ( 0.27886807 + 
                                                t * (-1.13520398 + 
                                                t * ( 1.48851587 + 
                                                t * (-0.82215223 + 
                                                t * ( 0.17087277))))))))))
        if z >= 0.0:
                return ans
        else:
                return -ans


def phiNormalUnit(x):
    "Cumulative unit normal distribution probability."
    return 0.5*(1.0+erf(x/sqrt(2.0)))


def phiNormal(x, mu, sigma):
    "Cumulative nonunit normal distribution probability = phi1((x-mu)/sigma))."
    return 0.5*(1.0+erf((x-mu)/(sigma*sqrt(2.0))))


def testErf():
    """\
  0.0000  0.5000  0.5000
  0.1000  0.5398  0.5793
  0.2000  0.5793  0.6554
  0.3000  0.6179  0.7257
  0.4000  0.6554  0.7881
  0.5000  0.6915  0.8413
  0.6000  0.7257  0.8849
  0.7000  0.7580  0.9192
  0.8000  0.7881  0.9452
  0.9000  0.8159  0.9641
  1.0000  0.8413  0.9772
  1.1000  0.8643  0.9861
  1.2000  0.8849  0.9918
  1.3000  0.9032  0.9953
  1.4000  0.9192  0.9974
  1.5000  0.9332  0.9987
  1.6000  0.9452  0.9993
  1.7000  0.9554  0.9997
  1.8000  0.9641  0.9998
  1.9000  0.9713  0.9999"""
    from p_ggen import xfrange
    for x in xfrange(0.0, 2.0, 0.1):
        print "%8.4f%8.4f%8.4f" % (x, phiNormalUnit(x), phiNormal(x, 0.0, 0.5))


if __name__ == "__main__":
    dokKlot()
    testErf()
