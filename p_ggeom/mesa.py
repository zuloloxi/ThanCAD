from math import fabs
from p_ggen import iterby2
import p_gmath, p_gvarcom
from .area import area


class MesaHull:
    "An object which represents a convex polygon to perform fast inclusion test."

    def __init__(self, cc):
        "First point should coincide with last."
        ca = [tuple(c) for c in cc]
        if not p_gmath.thanNear2(ca[0], ca[-1]): ca.append(ca[0])
        self.cc = tuple(ca)
        self.emp = area(self.cc)
        self.eps = 0.001

    def mesa(self, c1):
        "Tests if point x,y is inside the polygon."
        e = sum(area((c1, c2, c3)) for c2, c3 in iterby2(self.cc))
        return e-self.emp < self.eps  #If x,y is outside convex polygon then e > emp; (the 0.001 tolerance is for arithmetic errors)


class MesaQuad:
    "An object which represents a 4-node convex polygon to perform fast inclusion test."

    def __init__(self, p1, p2, p3, p4):
        "Initialise object."
        XP1,YP1 = p1[:2]
        XP2,YP2 = p2[:2]
        XP3,YP3 = p3[:2]
        XP4,YP4 = p4[:2]
        self.XM1=XP1
        self.XM2=XP2-XP1
        self.XM3=XP3-XP1
        self.XM4=XP4-XP1
        self.YM1=YP1
        self.YM2=YP2
        self.YM3=YP3
        self.YM4=YP4
        self.EMP=fabs(self.XM2*(self.YM1-self.YM3)+self.XM3*(self.YM2-self.YM4)+self.XM4*(self.YM3-self.YM1))
        self.eps = 0.001


    def mesa(self,p):
        "Tests if point x,y is inside the polygon."
        X,Y = p[:2]
        XM=X-self.XM1
        YM=Y
        E= fabs(self.XM2*(self.YM1-YM)      +XM      *(self.YM2-self.YM1))
        E+=fabs(XM      *(self.YM3-self.YM2)+self.XM2*(YM      -self.YM3) + self.XM3*(self.YM2-YM))
        E+=fabs(XM      *(self.YM3-self.YM4)+self.XM4*(YM      -self.YM3) + self.XM3*(self.YM4-YM))
        E+=fabs(self.XM4*(self.YM1-YM)      +XM      *(self.YM4-self.YM1))
        if E-self.EMP > self.eps: return False
        return True


class MesaTri:
    "An object which represents a triangle to perform fast inclusion test using area."

    def __init__(self, p1, p2, p3):
        "Initialise object."
        xp1,yp1 = p1[:2]
        xp2,yp2 = p2[:2]
        xp3,yp3 = p3[:2]
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
        self.eps = 0.001


    def mesa(self, p):
        "Tests if point p is inside the polygon."
        x, y = p[:2]
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
        if e-self.emp > self.eps: return False
        return True


class MesaTriLocal:
    "An object which represents a triangle to perform fast inclusion test using triangular local coordinates."

    def __init__(self, pa, pb, pc, tol=0.00001):
        "Initialise object; tolerance tol is relative to the size of the triangle."
        self.triloc = p_ggeom.TriLocal(pa[0], pa[1], pb[0], pb[1], pc[0], pc[1])
        self.lmin = 0.0-tol
        self.lmax = 1.0+tol


    def mesaLocal(self, cp):
        "Tests if point p is inside the triangle and return the local coordinates of the point."
        l1, l2, l3 = self.triloc.glob2loc(cp[0], cp[1])
        if l1 < self.lmin or l1 > self.lmax or l2 < self.lmin or l2 > self.lmax or \
           l3 < self.lmin or l3 > self.lmax: return False, l1, l2, l3
        if lmin < 0.0: print("Point FOUND on EDGES: %d %d %d" % (l1, l2, l3))
        return True, l1, l2, l3


    def mesa(self, cp):
        "Tests if point p is inside the triangle."
        return self.mesaLocal(cp)[0]


    def interp(self, a1, a2, a3, l1, l2, l3):
        "Interpolates scalar values known at the corners of the triangle to a point inside defined by local coordinates."
        return self.triloc.interp(a1, a2, a3, l1, l2, l3)


class MesaXymm(p_gvarcom.Xymm):
    "A rectangular region; decorate Xymm class with mesa function."
    __slots__ = ()
    def mesa(self, p):
        "Tests if point p is inside the rectangular region."
        return p in self
