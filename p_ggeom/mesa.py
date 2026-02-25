from math import fabs
from p_ggen import iterby2
from polyg import area


class MesaHull:
    "An object which represents a convex polygon to perform fast inclusion test."

    def __init__(self, cc):
        "First point should coincide with last."
        self.cc = tuple(tuple(c) for c in cc)
        self.emp = area(self.cc)

    def mesa(self, c1):
      "Tests if point x,y is inside the polygon."
      e = sum(area((c1, c2, c3)) for c2, c3 in iterby2(self.cc))
      return e-self.emp < 0.001  #If x,y is outside convex polygon then e > emp; (the 0.001 tolerance is for arithmetic errors)


#==========================================================================

class MesaQuad:
    "An object which represents a 4-node convex polygon to perform fast inclusion test."

    def __init__(self,XP1,YP1,XP2,YP2,XP3,YP3,XP4,YP4):
      "Initialise object."
      self.XM1=XP1
      self.XM2=XP2-XP1
      self.XM3=XP3-XP1
      self.XM4=XP4-XP1
      self.YM1=YP1
      self.YM2=YP2
      self.YM3=YP3
      self.YM4=YP4
      self.EMP=fabs(self.XM2*(self.YM1-self.YM3)+self.XM3*(self.YM2-self.YM4)+self.XM4*(self.YM3-self.YM1))

#===========================================================================

    def mesa(self,X,Y):
      "Tests if point x,y is inside the polygon."
      XM=X-self.XM1
      YM=Y
      E= fabs(self.XM2*(self.YM1-YM)      +XM      *(self.YM2-self.YM1))
      E+=fabs(XM      *(self.YM3-self.YM2)+self.XM2*(YM      -self.YM3) + self.XM3*(self.YM2-YM))
      E+=fabs(XM      *(self.YM3-self.YM4)+self.XM4*(YM      -self.YM3) + self.XM3*(self.YM4-YM))
      E+=fabs(self.XM4*(self.YM1-YM)      +XM      *(self.YM4-self.YM1))
      if E-self.EMP > 0.001: return False
      return True

#==========================================================================

class MesaTri:
    "An object which represents a triangle to perform fast inclusion test."

    def __init__(self,xp1,yp1,xp2,yp2,xp3,yp3):
      "Initialise object."
      self.ymin = min(yp1, yp2, yp3)
      self.ym1 = yp1 - self.ymin
      self.ym2 = yp2 - self.ymin
      self.ym3 = yp3 - self.ymin
      self.xm1 = xp1
      self.xm2 = xp2
      self.xm3 = xp3
      self.emp = fabs( (self.xm2-self.xm1)*(self.ym2+self.ym1) + \
                       (self.xm3-self.xm2)*(self.ym3+self.ym2) + \
                       (self.xm1-self.xm3)*(self.ym1+self.ym3)   \
                     )
#      print self.xm1, self.ym1
#      print self.xm2, self.ym2
#      print self.xm3, self.ym3
#      print self.emp
#      print "----------------"


#===========================================================================

    def mesa(self, x, y):
      "Tests if point x,y is inside the polygon."
      y -= self.ymin
      if y < 0.0: return False
      e =  fabs( (self.xm2-x       )*(self.ym2+y       ) + \
                 (self.xm3-self.xm2)*(self.ym3+self.ym2) + \
                 (x       -self.xm3)*(y       +self.ym3)   \
               )

      e += fabs( (x       -self.xm1)*(y       +self.ym1) + \
                 (self.xm3-x       )*(self.ym3+y       ) + \
                 (self.xm1-self.xm3)*(self.ym1+self.ym3)   \
               )

      e += fabs( (self.xm2-self.xm1)*(self.ym2+self.ym1) + \
                 (x       -self.xm2)*(y       +self.ym2) + \
                 (self.xm1-x       )*(self.ym1+y       )   \
               )
      if e-self.emp > 0.001: return False
      return True
