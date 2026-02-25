from math import fabs
import math, random
#from typing import Union, Iterable, Optional, Tuple, Iterator
import p_gmath, p_gnum  #type: ignore


class Vector3:
    "Implements 3d vectors."

    #def __init__ (self, xx:Union[float, Iterable[float]]=0.0, yy:float=0.0, zz:float=0.0):
    def __init__ (self, xx=0.0, yy=0.0, zz=0.0):
        "Initialise a new 3d vector to zero by default."
        #if isinstance(xx, Iterable): #Only one argument: it should be an iterable
        try: temp=iter(xx)
        except: temp = None
        if temp is not None: #Only one argument: it should be an iterable
            temp = iter(xx)
            self.x = next(temp)
            self.y = next(temp)
            self.z = next(temp)
        else:                               #Two arguments or three: they should be the number like
            self.x = float(xx)
            self.y = float(yy)
            self.z = float(zz)


    def __add__(self, other):  # type: (Vector3, Vector3) -> Vector3
        "Addition of vectors."
        if isinstance(other, Vector3):
            return Vector3(self.x+other.x, self.y+other.y, self.z+other.z)
        else:
            raise TypeError("Don't know how to add Vector3 by " + str(type(other)))

    def __sub__ (self, other):  # type: (Vector3, Vector3) -> Vector3
        "Subtraction of vectors."
        if isinstance(other, Vector3):
            return Vector3(self.x-other.x, self.y-other.y, self.z-other.z)
        else:
            raise TypeError("Don't know how to subtract Vector3 by " + str(type(other)))

    def __neg__ (self):  # type: (Vector3) -> Vector3
        "Returns the 3d vector with inverse direction."
        return Vector3(-self.x, -self.y, -self.z)

    def __pos__ (self):  # type: (Vector3) -> Vector3
        "Returns the 3d vector with the same direction."
        return Vector3(self.x, self.y, self.z)


    def __mul__ (self, other):  # type: (Vector3, float) -> Vector3
        "Returns the the vector multiplied by a number."
        try: other+0.0      #Is it number like
        except: raise TypeError("Don't know how to multiply Vector3 by " + str(type(other)))
        return Vector3(self.x * other, self.y * other, self.z * other)
    def __rmul__(self, other):  # type: (Vector3, float) -> Vector3
        return self.__mul__(other)


    def __or__(self, other):  # type: (Vector3, Vector3) -> float
        "Returns the scalar product of 3d vectors."
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __truediv__ (self, other):  # type: (Vector3, float) -> Vector3
        "Returns the vector divided by a number."
        try: other+0.0      #Is it number like
        except: raise TypeError("Don't know how to divide Vector3 by " + str(type(other)))
        return Vector3(self.x/other, self.y/other, self.z/other)
    __div__ = __truediv__   #For python 2 compatibility


    #def __abs__ (self) -> float:
    def __abs__ (self):
        "Computes the length of the vector."
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def unit(self):  # type: (Vector3) -> Optional[Vector3]
        "Computes the unit vector with the same direction."
        a = abs(self)
        if a == 0.0: return None
        return Vector3(self.x / a, self.y/a, self.z/a)


    def normal (self):  # type: (Vector3) -> Optional[Vector3]
        "Compute a random unit vector normal to the vector's direction."
        t = self.unit()
        if t is None:
            return None
        else:
            b = Vector3(1,0,0)
            bb = (b - (b|t)*t).unit()
            if bb is not None: return bb
            b = Vector3(0,1,0)
            bb = (b - (b|t)*t).unit()
            assert bb != None
            return bb


    def normal2(self):  # type: (Vector3) -> Tuple[Vector3, Vector3]
        "Find 2 random unit vectors so that they and t are mutually normal."
        t = self.unit()
        if t is None:
            return Vector3(1, 0, 0), Vector3(0, 1, 0)     #self is zero vector: return 2 arbitrary normal vectors
        #r:random.Random = random.Random()
        r = random.Random()
        while True:
            a = Vector3(r.uniform(0, 1), r.uniform(0, 1), r.uniform(0, 1))  # Note that it is not a unit vector..
            na = a - (t|a)*t                                                # but I don't want to ensure that it is <>0
            nn = abs(na)
            if nn > 0.1: break
        na /= nn
        while True:
            b = Vector3(r.uniform(0, 1), r.uniform(0, 1), r.uniform(0, 1))
            nb = b-(t|b)*t
            if abs(nb) > 0.1:
                nb = nb - (na|nb)*na
                nn = abs(nb)
                if nn > 0.1: break
        nb /= nn
        assert fabs(na|nb) < p_gmath.thanThresholdx
        assert fabs(t|na) < p_gmath.thanThresholdx
        assert fabs(t|nb) < p_gmath.thanThresholdx
        return na, nb

    #def dircos(self) -> Tuple[float, float, float]:
    def dircos(self):
        "Compute direction cosines."
        t = self.unit()
        if t is None: return 0.0, 0.0, 0.0
        return t.x, t.y, t.z

    def cross(self, b):  # type: (Vector3, Vector3) -> Vector3
        "Return the cross product of vectors self x b."
        return Vector3(self.y*b.z-self.z*b.y, self.z*b.x-self.x*b.z, self.x*b.y-self.y*b.x)

#    def rot (self, f):
#        "Rotates the vector to f counterclockwise radians."
#        cosf = math.cos(f); sinf = math.sin(f)
#        return Vector2(self.x*cosf - self.y*sinf, self.x*sinf + self.y*cosf)

    def mirXY(self):  # type: (Vector3) -> Vector3
        "Returns the vector with the same x,y and opposite z: mirror with repsect to XY plane."
        return Vector3(self.x, self.y, -self.z)

#    def atan2 (self):
#        "Computes the direction angle; positive=counterclockwise, zero at 3o'clock."
#        return math.atan2(self.y, self.x)

    def anal (self, da, db, dc):  # type: (Vector3, Vector3, Vector3, Vector3) -> Tuple[float, float, float]
        """Analyzes self into 3 non-coplanar vectors da, db and dc.

        It solves the vector system:
          ->     ->     ->    ->
        a DA + b DB + c DC = SELF
        """
        A = p_gnum.array(((da.x, db.x, dc.x),
                          (da.y, db.y, dc.y),
                          (da.z, db.z, dc.z),
                        ))
        B = p_gnum.array((self.x, self.y, self.z))
        return p_gnum.solve_linear_equations(A, B)

    def vector2(self):  # type: ignore
        "Return a 2d vector, discarding z."
        from . import vec
        return vec.Vector2(self.x, self.y)

    #def __str__ (self) -> str:
    def __str__ (self):
        "Just a string representation of the object."
        return "<%.3f, %.3f, %.3f>" % (self.x, self.y, self.z)


    #def __iter__(self) -> Iterator[float]:
    def __iter__(self):
        "Return an iterator to the vector."
        yield self.x
        yield self.y
        yield self.z


#def planeaxes2(a:Vector3, b:Vector3, z:Vector3) -> Tuple[Optional[Vector3], Optional[Vector3]]: 
def planeaxes2(a, b, z):
    """Find coordinate system of a plane so that the second axis is paralel to z.

    Given two vectors a and b which define a plane (a x b <> 0), find two
    perpendicular unit vectors u and v (u x v <> 0) which define a coordinate
    system in the plane, so that v is parallel to arbitrary vector z and has the
    same direction as z.
    If z is perpendicular to the plane, or z is zero, or a and b do not define
    a plane (they are colinear ore one of them is zero) return None.
    """
    zz = z.unit()
    if zz is None: return None, None
    z = zz
    ab = a + b
    tv = ab | z
    v = fabs(tv) * z     #v vector has the same direction as z
    u = ab - v
    if u|v < 0.0: u = -u #Make the system convex
    uu = u.unit()
    vv = v.unit()
    if uu is None or vv is None: return None, None
    return uu, vv
