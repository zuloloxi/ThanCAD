from math import fabs

class Lagrange(object):
    "Polynomial (Lagrange) interpolation using Neville's algorithm."

    def __init__(self, xa, ya):
        "Save the nodes withn known x and y."
        self.xa = list(xa)
        self.xa.insert(0, None)
        self.ya = list(ya)
        self.ya.insert(0, None)


    def polint(self, x):
      "Interpolate between the known nodes, or extrapolate."
      xa = self.xa
      ya = self.ya
      n = len(self.xa)-1
      c = [None]
      d = [None]
      ns=1
      dif=fabs(x-xa[1])
      #do 11 i=1,n
      for i in range(1, n+1):
          dift=fabs(x-xa[i])
          if dift < dif:
              ns=i
              dif=dift
          #endif
          c.append(ya[i])
          d.append(ya[i])
#11    continue
      y=ya[ns]
      ns=ns-1
      #do 13 m=1,n-1
      for m in range(1, n):
          #do 12 i=1,n-m
          for i in range(1, n-m+1):
              ho=xa[i]-x
              hp=xa[i+m]-x
              w=c[i+1]-d[i]
              den=ho-hp
              assert den != 0.0, 'Sr polint: failure: Two same xa(i)?'
              den=w/den
              d[i]=hp*den
              c[i]=ho*den
#12        continue
          if 2*ns < n-m:
              dy=c[ns+1]
          else:
              dy=d[ns]
              ns=ns-1
          #endif
          y=y+dy
#13    continue
      return y, dy
