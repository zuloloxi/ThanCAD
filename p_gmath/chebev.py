from math import cos, pi

class Chebyshev(object):
    "Chebyshev approximation of a function."

    def __init__(self,a,b,n,func):
          "Compute the Chebyshev coefficients."
          bma=0.5*(b-a)
          bpa=0.5*(b+a)
          f = [None]
    #      do 11 k=1,n
          for k in range(1, n+1):
            y=cos(pi*(k-0.5)/n)
            f.append(func(y*bma+bpa))
    #11    continue
          fac=2.0/n
          c = [None]
    #      do 13 j=1,n
          for j in range(1, n+1):
            sum=0.0
    #        do 12 k=1,n
            for k in range(1, n+1):
              sum=sum+f[k]*cos((pi*(j-1))*((k-0.5)/n))
    #12      continue
            c.append(fac*sum)
    #13    continue
          self.a = a
          self.b = b
          self.c = c
          self.n = n


    def chebev(self,m, x):
          "Interpolate the function using m<=n Chebyshev polynomials."
          c = self.c
          assert (x-self.a)*(x-self.b) <= 0.0, 'x not in range in chebev'
          assert m <= self.n, "m is greater than previously defined"
          d=0.0
          dd=0.0
          y=(2.0*x-self.a-self.b)/(self.b-self.a)
          y2=2.0*y
    #      do 11 j=m,2,-1
          for j in range(m, 2-1, -1):
            sv=d
            d=y2*d-dd+c[j]
            dd=sv
    #11    continue
          return y*d-dd+0.5*c[1]
