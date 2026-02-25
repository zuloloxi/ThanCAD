"This module copes with the differences between old Numeric and numpy."


def histogram1(a, bins=10, ra=None):
        """Compute the histogram of a set of data.
        Parameters :
        a : array_like
           Input data. The histogram is computed over the flattened array.
        bins : int or sequence of scalars, optional
        If bins is an int, it defines the number of equal-width bins in the given 
            range (10, by default). If bins is a sequence, it defines the bin edges, 
            including the rightmost edge, allowing for non-uniform bin widths.
        range : (float, float), optional
            The lower and upper range of the bins. If not provided, range is simply
            (a.min(), a.max()). Values outside the range are ignored.
        """
        try:
            1.0/bins
        except:
            v = array(bins, Float)
        else:
            if ra is None: ra = min(a), max(a)
            dd = float(ra[1]-float(ra[0]))/bins
            v = arange(ra[0]+0.0, ra[1]+dd*0.5, dd)
        dd = (v[-1] - v[-2])*0.000001
        v[-1] += dd                       #numpy.histogram INCLUDES the last value, and thus this hack
        n = searchsorted(sort(a), v)
        return n[1:] - n[:-1], v


#Thanasis2012_12_10: Note that I added the function eig,mean in the numpy; 
#I added them to Numeric too, but it has not been tested
#Thanasis2018_06_11: Note that I added the function diag in the numpy; 
#I added them to Numeric too, but it has not been tested
try:
    from Numeric import (array, transpose, zeros, reshape, fromstring,
        sin, cos, tan, sqrt, absolute, equal, not_equal, greater_equal, less_equal,
        greater, less, logical_and, compress, where, mean, diag,
        matrixmultiply, histogram, argmin, argmax, arange, sort, searchsorted,
        eye, polyfit, polyval, interp)
    from Numeric import (Float, Float16, Float32, Float64, Int, Int8, Int16, Int32,
        UnsignedInt8, UnsignedInt16, Complex64)
    from LinearAlgebra import (LinAlgError, eig,
        solve_linear_equations as solve, inverse as inv, linear_least_squares as lstsq,
        determinant as det)
    uint8, uint16 = UnsignedInt8, UnsignedInt16

    def min(a, axis=-1):
        """argmin(a,axis=-1) returns the indices to the minimum value of the
        1-D arrays along the given axis.
        """
        ij = argmin(a, axis)
        return a[ij]

    def max(a, axis=-1):
        """argmax(a,axis=-1) returns the indices to the maximum value of the
        1-D arrays along the given axis.
        """
        ij = argmax(a, axis)
        return a[ij]

    histogram = histogram1

    def typecode(r):
        return r.typecode()


except ImportError:
    from numpy import (array, transpose, zeros, reshape, fromstring,
        sin, cos, tan, sqrt, absolute, equal, not_equal, greater_equal, less_equal,
        greater, less, logical_and, compress, where, mean, diag,
        dot as matrixmultiply, histogram, argmin, argmax, arange, sort, searchsorted,
        eye, polyfit, polyval, interp)
    from numpy.linalg import (LinAlgError, eig,
                              solve, inv, lstsq,
                              det)
    from numpy import uint8, uint16
    from numpy import min, max, histogram

#   Thanasis2014_09_17: numpy 1.9 and later does not have the oldnumeric package.
#    from numpy.oldnumeric import (Float, Float16, Float32, Float64, Int, Int8, Int16, Int32,
#        UnsignedInt8, UnsignedInt16, Complex64)
    import numpy
    Float   = numpy.float64  #thanasis2023_05_08: numpy.float was an alias for python float: python float coincides with numpy.float64
    Float16 = numpy.float16
    Float32 = numpy.float32
    Float64 = numpy.float64
    Int     = numpy.int32    #thanasis2023_05_08: numpy.int was an alias for python int: python int coincides with numpy.int32
    Int8    = numpy.int8
    Int16   = numpy.int16
    Int32   = numpy.int32
    UnsignedInt8  = numpy.uint8
    UnsignedInt16 = numpy.uint8
    Complex64     = numpy.complex64
    del numpy

    def typecode(r):
        import numpy
        d = r.dtype
        if d == numpy.float: return Float
        if d == numpy.float16: return Float16
        if d == numpy.float32: return Float32
        if d == numpy.float64: return Float64
        if d == numpy.int: return Int
        if d == numpy.int16: return Int16
        if d == numpy.int32: return Int32
        if d == numpy.uint8: return UnsignedInt8
        if d == numpy.uint16: return UnsignedInt16
        if d == numpy.complex64: return Complex64
        raise ValueError("numnum.typecode(): don't know how to convert numpy '%r' to old Numeric" % (d,))

solve_linear_equations = solve
