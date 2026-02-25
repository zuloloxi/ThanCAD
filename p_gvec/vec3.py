from math import fabs
import math
import types
from p_gmath import thanThresholdx

#===========================================================================

class Vector3:
    "Implements 3d vectors."

    def __initolds__ (self, xx=0.0, yy=0.0, zz=0.0):
        "Initialise a new 3d vector to zero by default."
        self.x = float(xx)
        self.y = float(yy)
        self.z = float(zz)

    def __init__ (self, xx=None, yy=None, zz=0.0):
        "Initialise a new 3d vector to zero by default."
        if xx == None:                    #No arguments: Default vector is zero
            self.x = self.y = self.z = 0.0
        elif yy == None:                  #Only one argument: it should be an iterable
            yy = iter(xx)
            self.x = yy.next()
            self.y = yy.next()
            self.z = yy.next()
        else:                             #Two arguments or three: they should be the number like
            self.x = xx
            self.y = yy
            self.z = zz

    def __add__ (self, other):
        "Addition of vectors."
        if isinstance(other, Vector3):
            return Vector3(self.x+other.x, self.y+other.y, self.z+other.z)
        else:
            raise TypeError, "Don't know how to add Vector3 by " + `type(other)`

    def __sub__ (self, other):
        "Substraction of vectors."
        if isinstance(other, Vector3):
            return Vector3(self.x-other.x, self.y-other.y, self.z-other.z)
        else:
            raise TypeError, "Don't know how to subtract Vector3 by " + `type(other)`

    def __neg__ (self):
        "Returns the 3d vector with inverse direction."
        return Vector3(-self.x, -self.y, -self.z)

    def __pos__ (self):
        "Returns the 3d vector with the same direction."
        return Vector3(self.x, self.y, self.z)

    def __mul__ (self, other):
        "Returns the scalar product of 3d vectors, or the vector multiplied by a number."
        if isinstance(other, Vector3):
            return self.x * other.x + self.y * other.y + self.z * other.z
        elif isinstance(other, types.FloatType) or \
        isinstance(other, types.IntType):
            return Vector3(self.x * other, self.y * other, self.z * other)
        else:
            raise TypeError, "Don't know how to multiply Vector3 by " + `type(other)`

    def __div__ (self, other):
        "Returns the vector divided by a number."
        if isinstance(other, types.FloatType) or \
        isinstance(other, types.IntType):
            return Vector3(self.x/other, self.y/other, self.z/other)
        else:
            raise TypeError, "Don't know how to divide Vector3 by " + `type(other)`

    def __rmul__ (self, other):
        "Just an alias of multiplication."
        return self.__mul__ (other)

    def __abs__ (self):
        "Computes the length of the vector."
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def unit(self):
        "Computes the unit vector with the same direction."
        a = abs(self)
        if a == 0.0: return None
        return Vector3(self.x / a, self.y/a, self.z/a)

    def normal (self):
        "Compute a random unit vector normal to the vector's direction."
        t = self.unit()
        if t == None: return None
	b = Vector3(1,0,0)
	b = (b - (b*t)*t).unit()
	if b != None: return b
	b = Vector3(0,1,0)
	b = (b - (b*t)*t).unit()
	assert b != None
	return b

    def normal2(self):
         "Find 2 random unit vectors so that they and t are mutually normal."
         import random
         t = self.unit()
         r = random.Random()
         while True:
            a = Vector3(r.uniform(0, 1), r.uniform(0, 1), r.uniform(0, 1))  # Note that it is not a unit vector..
            na = a - (t*a)*t                                                # but I don't want to ensure that it is <>0
            nn = abs(na)
            if nn > 0.1: break
         na /= nn
         while True:
            b = Vector3(r.uniform(0, 1), r.uniform(0, 1), r.uniform(0, 1))
            nb = b-(t*b)*t
            if abs(nb) > 0.1:
                nb = nb - (na*nb)*na
                nn = abs(nb)
                if nn > 0.1: break
         nb /= nn
         assert fabs(na*nb) < thanThresholdx
         assert fabs(t*na) < thanThresholdx
         assert fabs(t*nb) < thanThresholdx
         return na, nb

    def dircos(self):
         "Compute direction cosines."
	 t = self.unit()
	 if t == None: return 0.0, 0.0, 0.0
	 return t.x, t.y, t.z

    def cross(a, b):
        "Return the cross product of vectors self x b."
	return Vector3(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)

#    def rot (self, f):
#        "Rotates the vector to f counterclockwise radians."
#        cosf = math.cos(f); sinf = math.sin(f)
#        return Vector2(self.x*cosf - self.y*sinf, self.x*sinf + self.y*cosf)

    def mirXY(self):
        "Returns the vector with the same x,y and opposite z: mirror with repsect to XY plane."
        return Vector3(self.x, self.y, -self.z)

#    def atan2 (self):
#        "Computes the direction angle; positive=counterclockwise, zero at 3o'clock."
#        return math.atan2(self.y, self.x)

    def anal (self, da, db, dc):
        """Analyzes self into 3 non-coplanar vectors da, db and dc.

        It solves the vector system:
          ->     ->     ->    ->
        a DA + b DB + c DC = SELF
        """
        from Numeric import array, Float
	from LinearAlgebra import solve_linear_equations
	A = array(((da.x, db.x, dc.x),
	           (da.y, db.y, dc.y),
	           (da.z, db.z, dc.z),
		 ))
        B = array((self.x, self.y, self.z))
        return solve_linear_equations(A, B)

    def vector2(self):
        "Return a 2d vector, discarding z."
	import vec
	return vec.Vector2(self.x, self.y)

    def __str__ (self):
        "Just a string representation of the object."
        return "<%.3f, %.3f, %.3f>" % (self.x, self.y, self.z)


    def __iter__(self):
        "Return an iterator to the vector."
        yield self.x
        yield self.y
        yield self.z

#===========================================================================

def testV():
    a = Vector3(10,20,30); print "a      = ", a
    b = Vector3(5, 6, 7);  print "b      = ", b
    z = Vector3(0, 0, 0);  print "z      = ", z
    c = a + b;             print "a+b    = ", c
    c = a - b;             print "a-b    = ", c
    c = a * b;             print "a*b    = ", c
    c = -a;                print "-a     = ", c
    c = +a;                print "+a     = ", c
    print
    c = a * 10.0;          print "a*10.0 = ", c
    c = 10.0 * a;          print "10.0*a = ", c
    c = a / 10.0;          print "a/10.0 = ", c
#    c = a / b;             print "a/b    = ", c    # Error!
#    c = 10.0 / a;          print "10.0/a = ", c    # Error!
    print
    c = 10.0 * a * b;      print "10.0*a*b = ", c
    c = a * 10.0 * b;      print "a*10.0*b = ", c
    c = a *  b * 10.0;     print "a*b*10.0 = ", c
    print
    c = 10.0*a + 20.0*b;   print "c=10.0*a+20.0*b = ", c
    print
    c = a.cross(b);        print "a x b=", c
    print "c*a=", c*a
    print "c*b=", c*b
    print
    c = abs(a);            print "abs(a) = ", c
    c = abs(b);            print "abs(b) = ", c
    print
    c = a.unit();          print "a.unit = ", c
    c = z.unit();          print "z.unit = ", c           # Error
    c = a.normal();        print "a.normal = ", c

    i = Vector3(1,0,0)
    j = Vector3(0,1,0)
    k = Vector3(0,0,1)
    print
    a = 10*i + 25*j + 30*k;  print "a =", a
    t=Vector3(1,1,1).unit(); print "t =", t
    at = (a * t) * t;        print "at =", at
    an = a - at;             print "an =", an

    print
    print "testing iterator:"
    v = Vector3(999.0, 1999.0, 2999.0)
    for i,c in enumerate(v): print "v[", i, "] =", c
    print

#    k = 1
#    while (k < 3000):
#        a = 10*i + 25*j
#        t = a.normal()
#        k = k + 1

#    print "-----"
#    for k in range(3000):
#        a = 10*i + 25*j
#        t = a.normal()


def testAnal():
    "Test anal function."
    print 
    i = Vector3(2, 1, 1);    print "i =", i
    j = Vector3(4, 18, 2);   print "j =", j
    k = Vector3(4, 18, -2);  print "k =", k
    a = Vector3(10, 25, 99); print "a =", a
    s = a.anal(i, j, k);     print "a.anal =", s
    print "a = ", s[0], "* i +", s[1], "* j +", s[2], "* k =", s[0]*i + s[1]*j + s[2]*k


if __name__ == "__main__":
    testV();
    testAnal()
