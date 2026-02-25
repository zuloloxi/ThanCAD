# -*- coding: iso-8859-7 -*-
import sys
from math import atan2, sqrt, pi
from p_gmath import dpt


class ThanSpline:
    def __init__(self):
      self.tmax = -1.0
      self.n = -1
      self.t = []
      self.x = []
      self.y = []
      self.xt = []
      self.yt = []

#===========================================================================

    def splfun(self, ts):
      "Find coordinates of spline at distance ts."
      x = self.x
      y = self.y
      t = self.t
      xt = self.xt
      yt = self.yt
      tt = ts
      if (tt <= 0.0):
          tt = 0.0
          i = 2
      elif (tt > self.tmax):
          tt = self.tmax
          i = self.n
      else:
          tor = 0.0
          for i in xrange(2, self.n+1):    #do i=2, n
              tor = tor + self.t[i]
              if (tt <= tor):
                  tt = tt + t[i] - tor
                  break
          else:
              print 'impossible error in sr splfun, lib indplt'
              sys.exit(1)
      k = i
      i = i-1
      a = 3.0 * (x[k]-x[i]) / t[k]**2 - (2.0*xt[i]+xt[k]) / t[k]
      b = 2.0 * (x[i]-x[k]) / t[k]**3 + (xt[i]+xt[k]) / t[k]**2
      xs = x[i] + tt * (xt[i] + tt*(a + tt*b))
      xts = xt[i] + tt * (2.0*a + tt*3.0*b)

      a = 3.0 * (y[k]-y[i]) / t[k]**2 - (2.0*yt[i]+yt[k]) / t[k]
      b = 2.0 * (y[i]-y[k]) / t[k]**3 + (yt[i]+yt[k]) / t[k]**2
      ys = y[i] + tt * (yt[i] + tt * (a+tt*b))
      yts = yt[i] + tt * (2.0*a + tt*3.0*b)

      theta = dpt(0.5*pi - atan2(xts,yts)) * 180.0 / pi
      return xs, ys, theta

#===========================================================================

    def splin(self, xs, ys, ns, ic):
      """Προετοιμασία για υπολογισμό κυβικών πολυνύμων. 

      ic = 0 : κανονική ανοικτή καμπύλη με καμπυλότητα 0 στα δύο άκρα
         = 1 : κανονική κλειστή καμπύλη με ίδια καμπυλότητα στα δύο "άκρα"
         = 2 : κλειστή καμπύλη με αντίθετη καμπυλότητα στα δύο "άκρα":
               μορφή σταγόνας
      """
      n = self.n = ns
      pr = 1.0
      if (ic==2): pr = -1.0
      ns1 = ns + 1
      x = self.x = [0.0]*ns1
      y = self.y = [0.0]*ns1
      xt = self.xt = [0.0]*ns1
      yt = self.yt = [0.0]*ns1
      t = self.t = [0.0]*ns1
      a = [0.0]*ns1
      b = [0.0]*ns1
      c = [0.0]*ns1
      d = [0.0]*ns1

      x[1] = xs[1]
      y[1] = ys[1]

      t[1] = 0.0
      self.tmax = 0.0
      for i in xrange(2, n+1):     #do i=2, n
          x[i] = xs[i]
          y[i] = ys[i]
          t[i] = sqrt((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2)
          self.tmax = self.tmax + t[i]

      for i in xrange(2, n):       #do i=2, n-1
          a[i] = t[i+1]
          b[i] = 2.0 * (t[i]+t[i+1])
          c[i] = t[i]
          d[i] = 3.0 * (t[i]**2 * (x[i+1]-x[i]) + t[i+1]**2 *\
                 (x[i]-x[i-1])) / (t[i]*t[i+1])

      if (ic == 0):
          b[1] = 1.0
          c[1] = 0.5
          d[1] = 1.5 * (x[2]-x[1]) / t[2]
          a[n] = 2.0
          b[n] = 4.0
          d[n] = 6.0 * (x[n]-x[n-1]) / t[n]
          ierr = lse(a, b, c, d, 0.0, xt, n)
          if ierr != 0: return None, ierr
      else:
          b[1] = 2.0 + 2.0 * t[n] / t[2]
          c[1] = t[n] / t[2]
          d[1] = 3.0 * (x[2]-x[1]) * t[n] / t[2]**2 -\
                 pr * 3.0 * (x[n-1]-x[n])/t[n]
          e = pr
          ierr = lse(a, b, c, d, e, xt, n-1)
          if ierr != 0: return None, ierr
          xt[n] = pr * xt[1]

      for i in xrange(2, n):       #do i=2, n-1
          a[i] = t[i+1]
          b[i] = 2.*(t[i]+t[i+1])
          c[i] = t[i]
          d[i] = 3.0 * (t[i]**2 * (y[i+1]-y[i]) + t[i+1]**2 *\
                 (y[i]-y[i-1])) / (t[i]*t[i+1])

      if (ic == 0):
          b[1] = 1.0
          c[1] = 0.5
          d[1] = 1.5 * (y[2]-y[1]) / t[2]
          a[n] = 2.0
          b[n] = 4.0
          d[n] = 6.0 * (y[n]-y[n-1]) / t[n]
          ierr = lse(a, b, c, d, 0.0, yt, n)
          if ierr != 0: return None, ierr
      else:
          b[1] = 2.0 + 2. * t[n] / t[2]
          c[1] = t[n] / t[2]
          d[1]=3.0 * (y[2]-y[1]) * t[n] / t[2]**2 -\
               pr*3.*(y[n-1]-y[n])/t[n]
          e = pr
          ierr = lse(a, b , c , d , e , yt, n-1)
          yt[n] = pr * yt[1]
          if ierr != 0: return None, ierr
      return self.tmax, 0

#==========================================================================

    def linfun(self, ts):
      "Find coordinates of straight line segment  at distance ts."
      tt = ts
      if (tt <= 0.0):
          tt = 0.0
          i = 2
      elif (tt > tmax):
          tt = tmax
          i = n
      else:
          tor = 0.0
          for i in xrange(2, self.n+1):      #do i=2, n
              tor = tor + t[i]
              if (tt <= tor):
                  tt = tt + t[i] - tor
                  break
          else:
              print 'impossible error in sr splfun, lib indplt'
              sys.exit(1)

      tt = tt / t[i]
      k = i
      i = i-1

      dx = x[k] - x[i]
      dy = y[k] - y[i]
      xs = x[i] + dx * tt
      ys = y[i] + dy * tt

      theta = dpt(0.5*pi - atan2(dx,dy)) * 180.0 / pi
      return xs, ys, theta

#===========================================================================

    def contlin (self, xs, ys, ns, ic):
      "Προετοιμασία για υπολογισμό παρεμβολής με ευθείες."
      n = ns
      ns1 = ns + 1
      x = self.x = [0.0]*ns1
      y = self.y = [0.0]*ns1

      x[1] = xs[1]
      y[1] = ys[1]

      t[1] = 0.0
      self.tmax = 0.0
      for i in xrange(2, self.n+1):     #do i=2, n
          x[i] = xs[i]
          y[i] = ys[i]
          t[i] = sqrt((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2)
          self.tmax = self.tmax + t[i]

      return self.tmax


def lse(a,b,c,d,e1,p,n):
    "Επίλυση συστήματος εξισώσεων ζώνης."
    try:
      e = e1
      i = n
      while True:
          i = i - 1
          b[i]=b[i]-c[i]*a[i+1]/b[i+1]
          d[i]=d[i]-c[i]*d[i+1]/b[i+1]
          d[1]=d[1]-e*d[i+1]/b[i+1]
          e=-e*a[i+1]/b[i+1]

          if (b[i] == 0.0):
              p[i-1]=d[i]/a[i]
              i=i-1
              d[i]=d[i]-b[i]*p[i]
              if (i==1):
                  p[2]=(d[1]-b[1]*p[1])/(b[1]+e)
                  i=2
                  break
              i=i-1
              d[i]=d[i]-c[i]*p[i+1]
              d[1]=d[1]-e*d[i+1]/c[i+1]
              e=-e*a[i+1]/c[i+1]
          if (i<=1):
              p[1]=d[1]/(b[1]+e)
              i=1
              break

      while True:
          i=i+1
          if (i<n and b[i+1] == 0.0):
              p[i+1]=(d[i]-a[i]*p[i-1])/c[i]
              i=i+2
          p[i]=(d[i]-a[i]*p[i-1])/b[i]
          if (i>=n): break
      return 0
    except ZeroDivisionError:
      return 1
