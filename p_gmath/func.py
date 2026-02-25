"Special functions module."
from math import sqrt, cos, sin, pi, exp, fabs, log
from .varcon import PI05, PIR
from .var import fsign


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
        raise ValueError('Series failed in fresnel()')
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
        raise ValueError('cf failed in fresnel')


def klotXy(A, L, pr=1):
    "Calculates xy coordinates of clothoid of parameter A at distance L from start."
    apir = A * PIR
    s, c = fresnel(L / apir)
    return (apir*c, apir*s*pr)

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
    "Cumulative unit normal distribution probability (integral from -infinity to x)."
    return 0.5*(1.0+erf(x/sqrt(2.0)))


def phiNormal(x, mu, sigma):
    "Cumulative nonunit normal distribution probability = phi1((x-mu)/sigma));  (integral from -infinity to x)."
    return 0.5*(1.0+erf((x-mu)/(sigma*sqrt(2.0))))


def phiNormalUnitInv(y):
    "Inverse cumulative unit normal distribution probability."
    return sqrt(2.0) * erfinvapprox(2.0*y-1.0)


def erfinvapprox(x):
    "A very good approximation of the inverse error function."
#    a = 8.0*(pi-3.0) / (3.0*pi*(4.0-pi)) #This value of a gives slightly worse approximation 
    a = 0.147                             #This value of a gives slightly better approximation (see developer/erf.pdf)
    t2 = log(1.0-x**2)
    t1 = 2.0/(pi*a) + t2/2.0
    return fsign(sqrt(sqrt(t1**2-t2/a) - t1), x)


if __name__ == "__main__":
    print(__doc__)
