"This module copes with the differences between old Numeric and numpy."


#Thanasis2012_12_10: Note that I added the function eig,mean in the numpy; 
#I added them to Numeric too, but it has not been tested
try:
    from Numeric import (array, transpose, zeros, reshape, fromstring,
        sin, cos, tan, sqrt, absolute, equal, not_equal, compress, where, mean,
        matrixmultiply, histogram)
    from Numeric import (Float, Float16, Float32, Float64, Int, Int8, Int16, Int32,
        UnsignedInt8, UnsignedInt16)
    from LinearAlgebra import (LinAlgError, eig,
        solve_linear_equations as solve, inverse as inv, linear_least_squares as lstsq)
    uint8, uint16 = UnsignedInt8, UnsignedInt16
    def min(a, axis=-1):
        """argmin(a,axis=-1) returns the indices to the minimum value of the
        1-D arrays along the given axis.
        """
        ij = argmin(a, axis)
        return aa[ij]
    def max(a, axis=-1):
        """argmax(a,axis=-1) returns the indices to the maximum value of the
        1-D arrays along the given axis.
        """
        ij = argmax(a, axis)
        return aa[ij]
    def typecode(r):
        return t.typecode()

except ImportError:
    from numpy import (array, transpose, zeros, reshape, fromstring,
        sin, cos, tan, sqrt, absolute, equal, not_equal, compress, where, mean,
        dot as matrixmultiply, histogram)
    from numpy.oldnumeric import (Float, Float16, Float32, Float64, Int, Int8, Int16, Int32,
        UnsignedInt8, UnsignedInt16)
    from numpy.linalg import ( LinAlgError, eig,
                              solve, inv, lstsq)
    from numpy import uint8, uint16
    from numpy import min, max
    def typecode(r):
        import numpy
        d = r.dtype
        if d == numpy.float: return Float
        if d == numpy.float16: return Float16
        if d == numpy.float32: return Float32
        if d == numpy.float64: return Float64
        if d == numpy.int: return Int
        if d == numpy.int32: return Int32
        if d == numpy.uint8: return UnsignedInt8
        if d == numpy.uint16: return UnsignedInt16
        raise ValueError, "numnum.typecode(): don't know how to convert numpy '%r' to old Numeric" % (d,)

solve_linear_equations = solve
