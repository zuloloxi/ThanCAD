import math, types
from p_gmath import linEq2

class Vector2:
    "Implements 2d vectors."

    def __initolds__ (self, xx=0.0, yy=0.0):
        "Initialise a new 2d vector to zero by default."
        self.x = float(xx)
        self.y = float(yy)

    def __init__ (self, xx=None, yy=None):
        "Initialise a new 2d vector to zero by default."
        if xx == None:                    #No arguments: Default vector is zero
            self.x = self.y = 0.0
        elif yy == None:                  #Only one argument: it should be an iterable
            yy = iter(xx)
            self.x = yy.next()
            self.y = yy.next()
        else:                             #Two arguments: they should be the number like
            self.x = xx
            self.y = yy

    def __add__ (self, other):
        "Addition of vectors."
        if isinstance(other, Vector2):
            return Vector2(self.x+other.x, self.y+other.y)
        else:
            raise TypeError, "Don't know how to add Vector2 by " + `type(other)`

    def __sub__ (self, other):
        "Substraction of vectors."
        if isinstance(other, Vector2):
            return Vector2(self.x-other.x, self.y-other.y)
        else:
            raise TypeError, "Don't know how to subtract Vector2 by " + `type(other)`

    def __neg__ (self):
        "Returns the 2d vector with inverse direction."
        return Vector2(-self.x, -self.y)

    def __pos__ (self):
        "Returns the 3d vector with the same direction."
        return Vector2(self.x, self.y)

    def __mul__ (self, other):
        "Returns the scalar product of 2d vectors, or the vector multiplied by a number."
        if isinstance(other, Vector2):
            return self.x * other.x + self.y * other.y
        elif isinstance(other, types.FloatType) or \
        isinstance(other, types.IntType):
            return Vector2(self.x * other, self.y * other)
        else:
            raise TypeError, "Don't know how to multiply Vector2 by " + `type(other)`

    def __div__ (self, other):
        "Returns the vector divided by a number."
        if isinstance(other, types.FloatType) or \
        isinstance(other, types.IntType):
            return Vector2(self.x / other, self.y / other)
        else:
            raise TypeError, "Don't know how to devide Vector2 by " + `type(other)`

    def __rmul__ (self, other):
        "Just an alias of multiplication."
        return self.__mul__ (other)

    def __abs__ (self):
        "Computes the length of the vector."
        return math.sqrt(self.x**2 + self.y**2)

    def unit (self):
        "Computes the unit vector with the same direction."
        a = abs(self)
        if a == 0.0: return None
        return Vector2(self.x / a, self.y / a)

    def normal (self):
        "Compute the unit vector normal to the vector's direction; positive is the left side."
        a = abs(self)
        if a == 0.0: return None
        return Vector2(-self.y / a, self.x / a)

    def dircos(self):
         "Compute direction cosines."
	 t = self.unit()
	 if t == None: return 0.0, 0.0
	 return t.x, t.y

    def cross(a, b):
        """Return the cross product of 2d vectors: self x b; the result is a scalar value.
	
	The result is a vector whose direction is normal to the xy plane.
	Thus: a. The x,y components of the result are zero; the z component is nonzero.
	      b. The result can not be represented as a 2d vector.
	So the z component of the result is returned as a scalar value.      
	"""
	return a.x*b.y-a.y*b.x

    def rot (self, f):
        "Rotates the vector to f counterclockwise radians."
        cosf = math.cos(f); sinf = math.sin(f)
        return Vector2(self.x*cosf - self.y*sinf, self.x*sinf + self.y*cosf)

    def mirX(self):
        "Returns the vector with the same x and opposite y: mirror with repsect to X axis."
        return Vector2(self.x, -self.y)

    def atan2 (self):
        "Computes the direction angle; positive=counterclockwise, zero at 3o'clock."
        return math.atan2(self.y, self.x)

    def anal (self, da, db):
        """Analyses the vector into two non-colinear vectors da and db.

        It solves the vector system:
          ->     ->    ->
        a DA + b DB = SELF
        """
        return linEq2 (da.x, db.x, self.x, da.y, db.y, self.y)

    def vector3(self, z=0.0):
        "Transform self to a 3d vector with given or zero z."
	import vec3
	return vec3.Vector3(self.x, self.y, z)

    def __str__ (self):
        "Just a string representation of the object."
        return "<%.3f, %.3f>" % (self.x, self.y)

    def __iter__(self):
        "Return an iterator to the vector."
        yield self.x
        yield self.y

#===========================================================================

def testV():
    a = Vector2(10.0, 20.0); print "a      = ", a
    b = Vector2(5.0, 6.0);   print "b      = ", b
    z = Vector2(0.0, 0.0);   print "z      = ", b
    c = a + b;               print "a+b    = ", c
    c = a - b;               print "a-b    = ", c
    c = a * b;               print "a*b    = ", c
    c = -a;                  print "-a     = ", c
    c = +a;                  print "+a     = ", c
    print
    c = a * 10.0;            print "a*10.0 = ", c
    c = 10.0 * a;            print "10.0*a = ", c
    c = a / 10.0;            print "a/10.0 = ", c
    #c = a / b;               print "a/b    = ", c    # Error!
    #c = 10.0 / a;            print "10.0/a = ", c    # Error!
    print
    c = 10.0 * a * b;        print "10.0*a*b = ", c
    c = a * 10.0 * b;        print "a*10.0*b = ", c
    c = a *  b * 10.0;       print "a*b*10.0 = ", c
    print
    c = 10.0 * a + 20.0 * b; print "10.0*a+20.0*b = ", c
    print
    c = abs(a);              print "abs(a) = ", c
    c = abs(b);              print "abs(b) = ", c
    print
    c = a.unit();            print "a.unit = ", c
    c = z.unit();            print "z.unit = ", c           # Error
    c = a.normal();          print "a.normal = ", c


    i = Vector2(1, 0)
    j = Vector2(0, 1)
    print
    a = 10*i + 25*j;        print "a =", a
    t=Vector2(1, 1).unit(); print "t =", t
    at = (a * t) * t;       print "at =", at
    an = a - at;            print "an =", an

    print
    print "testing iterator:"
    v = Vector2(999.0, 1999.0)
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
    i = Vector2(2, 9);      print "i =", i
    j = Vector2(4, -18);    print "j =", j
    a = Vector2(10, 25);    print "a =", a
    s = a.anal(i, j);       print "a.anal =", s
    print "a = ", s[0], "* i +", s[1], "* j =", s[0]*i + s[1]*j

if __name__ == "__main__":
    testV();
    testAnal()
