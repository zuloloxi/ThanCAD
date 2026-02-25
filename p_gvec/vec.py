import math
from typing import Optional, Union, Iterable, Tuple, Iterator
from p_gmath import linEq2 # type: ignore

class Vector2:
    "Implements 2d vectors."

    def __init__(self, xx:Union[float, Iterable[float]]=0.0, yy:float=0.0):
        "Initialise a new 2d vector to zero by default."
        if isinstance(xx, Iterable):     #Only one argument: it should be an iterable
            temp = iter(xx)
            self.x = next(temp)
            self.y = next(temp)
        else:                             #Two arguments: they should be the number like
            self.x = float(xx)
            self.y = float(yy)

    def __add__ (self, other):  # type: (Vector2, Vector2) -> Vector2
        "Addition of vectors."
        if isinstance(other, Vector2):
            return Vector2(self.x+other.x, self.y+other.y)
        else:
            raise TypeError("Don't know how to add Vector2 by " + str(type(other)))

    def __sub__ (self, other):  # type: (Vector2, Vector2) -> Vector2
        "Subtraction of vectors."
        if isinstance(other, Vector2):
            return Vector2(self.x-other.x, self.y-other.y)
        else:
            raise TypeError("Don't know how to subtract Vector2 by " + str(type(other)))

    def __neg__ (self):  # type: (Vector2) -> Vector2 
        "Returns the 2d vector with inverse direction."
        return Vector2(-self.x, -self.y)

    def __pos__ (self):  # type: (Vector2) -> Vector2
        "Returns the 3d vector with the same direction."
        return Vector2(self.x, self.y)

    def __or__ (self, other):  # type: (Vector2, Vector2) -> float
        "Returns the scalar product of 2d vectors."
        return self.x * other.x + self.y * other.y

    def __mul__ (self, other):  # type: (Vector2, float) -> Vector2
        "Returns the scalar product of 2d vectors, or the vector multiplied by a number."
        try: other+0.0      #Is it number like
        except: raise TypeError("Don't know how to multiply Vector2 by " + str(type(other)))
        return Vector2(self.x * other, self.y * other)
    def __rmul__ (self, other):  # type: (Vector2, float) -> Vector2
        return self.__mul__(other)

    def __truediv__ (self, other):  # type: (Vector2, float) -> Vector2
        "Returns the vector divided by a number."
        #if isinstance(other, types.FloatType) or isinstance(other, types.IntType):
        try: other+0.0      #Is it number like
        except: raise TypeError("Don't know how to divide Vector2 by " + str(type(other)))
        return Vector2(self.x / other, self.y / other)
    __div__ = __truediv__    #For python2 compatibility

    def __abs__ (self):   # type: (Vector2) -> float
        "Computes the length of the vector."
        return math.hypot(self.x, self.y)

    def unit (self):  # type: (Vector2) -> Optional[Vector2]
        "Computes the unit vector with the same direction."
        a = abs(self)
        if a == 0.0: return None
        return Vector2(self.x / a, self.y / a)

    def normal (self):   # type: (Vector2) -> Optional[Vector2]
        "Compute the unit vector normal to the vector's direction; positive is the left side."
        a = abs(self)
        if a == 0.0: return None
        return Vector2(-self.y / a, self.x / a)

    def dircos(self) -> Tuple[float, float]:
        "Compute direction cosines."
        t = self.unit()
        if t is None: return 0.0, 0.0
        return t.x, t.y

    def cross(self, b):   # type: (Vector2, Vector2) -> float
        """Return the cross product of 2d vectors: self x b; the result is a scalar value.

        The result is a vector whose direction is normal to the xy plane.
        Thus: a. The x,y components of the result are zero; the z component is nonzero.
              b. The result can not be represented as a 2d vector.
        So the z component of the result is returned as a scalar value.
        If you want a 3d vector as a result of the cross product a x b, use:
        c = Vector3(0.0, 0.0, a.cross(b))        or:
        c = a.vector3().cross(b.vector3())
        """
        return self.x*b.y-self.y*b.x

    def rot (self, f):  # type: (Vector2, float) -> Vector2
        "Rotates the vector to f counterclockwise radians."
        cosf = math.cos(f); sinf = math.sin(f)
        return Vector2(self.x*cosf - self.y*sinf, self.x*sinf + self.y*cosf)

    def mirX(self):  # type (Vector2) -> Vector2
        "Returns the vector with the same x and opposite y: mirror with repsect to X axis."
        return Vector2(self.x, -self.y)

    def atan2 (self) -> float:
        "Computes the direction angle; positive=counterclockwise, zero at 3o'clock."
        return math.atan2(self.y, self.x)

    def anal (self, da, db):  # type (Vector2, vector, Vector2) -> Tuple[float, float]
        """Analyses the vector into two non-colinear vectors da and db.

        It solves the vector system:
          ->     ->    ->
        a DA + b DB = SELF
        """
        return linEq2 (da.x, db.x, self.x, da.y, db.y, self.y)

    def vector3(self, z=0.0):
        "Transform self to a 3d vector with given or zero z."
        from . import vec3  # type: ignore
        return vec3.Vector3(self.x, self.y, z)

    def __str__ (self) -> str:
        "Just a string representation of the object."
        return "<%.3f, %.3f>" % (self.x, self.y)

    def __iter__(self) -> Iterator[float]:
        "Return an iterator to the vector."
        yield self.x
        yield self.y
