"This module copes with the differences between old Numeric and numpy."

try:
    from Numeric import (array, Float, Float32, Float64, Int, Int8, Int16, Int32, UnsignedInt8,
        matrixmultiply, transpose, zeros, reshape, fromstring,
        sin, cos, tan, sqrt, absolute, equal, not_equal, compress, where)
    from LinearAlgebra import solve_linear_equations, LinAlgError, inverse, linear_least_squares
    def typecode(r):
        return t.typecode()
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

except ImportError:
    from numpy import (array, transpose, zeros, reshape, fromstring,
        sin, cos, tan, sqrt, absolute, max, min, equal, not_equal, compress, where,
        dot as matrixmultiply)
    from numpy.oldnumeric import Float, Float32, Float64, Int, Int8, Int16, Int32, UnsignedInt8
    from numpy.linalg import (solve as solve_linear_equations, LinAlgError,
                              inv as inverse, lstsq as linear_least_squares
                             )

    def typecode(r):
        import numpy
        d = r.dtype
        if d == numpy.float: return Float
        if d == numpy.float32: return Float32
        if d == numpy.float64: return Float64
        if d == numpy.int: return Int
        if d == numpy.int32: return Int32
        if d == numpy.uint8: return UnsignedInt8
        raise ValueError, "numnum.typecode(): don't know how to convert numpy '%r' to old Numeric" % (d,)
