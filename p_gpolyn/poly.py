from __future__ import print_function
#from past.builtins import xrange
from p_ggen.py23 import xrange
from math import fabs, hypot
import types
from p_gmath import thanThresholdx  # Threshold for coordinate difference; if less the coordinates are the same


class Polynomial(list):
    "Implements a polynomial."
    __slots__ = ()

    def __init__(self, iterable=(0.0,)):
        try:    iter(iterable)
        except: raise TypeError("Can not create Polynomial with %s" % type(iterable))
        list.__init__(self)
        for f in iterable:
            try:    self.append(f+0.0) # Ensure that if coeeficients are sumFactors, they are unique sumFactors
            except: raise TypeError("Can not create Polynomial with %s" % type(f))
        if len(self) == 0:
            self[:] = [0.0]     # Ensure that the polynomial is at least zeroth order

    def __add__ (self, other):
        "Addition of polynomials or polynomial+number."
        if isinstance(other, Polynomial):
            if len(self) > len(other): a, b = self,  other
            else:                      a, b = other, self
            c = Polynomial(a)
            for i,f in enumerate(b):
                c[i] += b[i]
            return c
        try:
            other+0.0        # Check if it is number like
        except:
            raise TypeError("Don't know how to add Polynomial with %s" % type(other))
        c = Polynomial(self)
        c[0] += other
        return c


    def __radd__ (self, other):
        "Just an alias of addition."
        return self.__add__(other)


    def __sub_mistaken__ (self, other):
        "Subtraction of polynomials or polynomial-number."
        if isinstance(other, Polynomial):
            if len(self) > len(other): pra, a, prb, b =  1.0, self, -1.0, other
            else:                      pra, a, prb, b = -1.0, other, 1.0, self
            c = Polynomial(a)
            for i,f in enumerate(b):
                c[i] = pra*c[i] + prb*b[i]
            return c
        try:
            other+0.0        # Check if it is number like
        except:
            raise TypeError("Don't know how to subtract %s from Polynomial" % type(other))
        c = Polynomial(self)
        c[0] -= other
        return c


    def __sub__ (self, other):
        "Subtraction of polynomials or polynomial-number."
        other = -other
        return self+other


    def __rsub__ (self, other):
        "Subtraction number-polynomial."
        try:
            other+0.0        # Check if it is number like
        except:
            raise TypeError("Don't know how to subtract Polynomial from %s" % type(other))
        c = Polynomial(self)
        c[0] -= other
        for i,f in enumerate(c):
            c[i] = -f
        return c


    def __neg__ (self):
        "Returns the negative of polynomial."
        c = Polynomial(self)
        for i,f in enumerate(c):
            c[i] = -f
        return c


    def __pos__ (self):
        "Returns the positive of polynomial - that is the same:)."
        return Polynomial(self)


    def __mul__ (self, other):
        "Returns the product of polynomials or polynomial*number."
        if isinstance(other, Polynomial):
            n = len(self)+len(other)-1
            c = Polynomial([0.0]*n)
            for ia,fa in enumerate(self):
                for ib,fb in enumerate(other):
                    c[ia+ib] += fa*fb
            return c
        try:
            other+0.0        # Check if it is number like
        except:
            raise TypeError("Don't know how to multiply Polynomial with %s" % type(other))
        c = Polynomial(self)
        for i,f in enumerate(c):
            c[i] *= other
        return c


    def __rmul__ (self, other):
        "Just an alias of multiplication."
        return self.__mul__(other)


    def __truediv__ (self, other):
        "Returns division of polynomial / number."
        try:
            other+0.0        # Check if it is number like
        except:
            raise TypeError("Don't know how to divide Polynomial by %s" % type(other))
        c = Polynomial(self)
        for i,f in enumerate(c):
            c[i] /= other
        return c
    __div__ = __truediv__    # for compatibility with python 2

    def __call__(self, x):
        "Evaluates the polynomial at x; if x is a polynomial then it returns synthesis of polynomials self(x())."
        try:
            x+0.0        # Check if it is number like
        except:
            raise TypeError("Don't know how to evaluate Polynomial with %s" % type(x))
        s = self[-1]
#        print("():", s)
        for i in xrange(len(self)-2, -1, -1):
            s = x*s + self[i]
#            print("():", s)
        return s


    def __abs__(self, a=-1.0, b=1.0, steps=100):
        "Computes the length of the polynomial."
        dx = (b-a)/steps
        xp = a
#        print(xp)
        vp = self(xp)
        d = 0.0
        for i in xrange(steps):
            x = xp + dx
#            print(x)
            v = self(x)
            d += hypot(x-xp, v-vp)
            xp = x
            vp = v
        return d


    def __strnumbers__ (self):
        "Just a string representation of the object."
        if type(self[0]) == types.ComplexType:
            s = ["%s" % self[0]]
            for f in self[1:2]:
                s.append(" + %sx" % f)
            i = 2
            for f in self[2:]:
                s.append(" + %sx^%d" % (f, i))
                i += 1
            return "".join(s)

        s = ["%.3f" % self[0]]
        for f in self[1:2]:
            if f >= 0.0: s.append(" + %.3fx" % fabs(f))
            else:        s.append(" - %.3fx" % fabs(f))
        i = 2
        for f in self[2:]:
            if f >= 0.0: s.append(" + %.3fx^%d" % (fabs(f), i))
            else:        s.append(" - %.3fx^%d" % (fabs(f), i))
            i += 1
        return "".join(s)


    def __str__ (self):
        "Just a string representation of the object."
        s = ["[%s]" % self[0]]
        for f in self[1:2]:
            s.append(" + [%s]x" % f)
        i = 2
        for f in self[2:]:
            s.append(" + [%s]x^%d" % (f, i))
            i += 1
        return "".join(s)


    def factorout(self, root):
        "Divide self by (x-root)."
        n = len(self)
        q = Polynomial((0.0,)*(n-1))
        rem = Polynomial(self)
        #div = Polynomial((-root, 1.0))
        for i in xrange(n-1, 0, -1):
            q[i-1] = rem[i]
            rem[i] = 0.0
            rem[i-1] += root*q[i-1]
#            assert abs(rem[i]) < thanThresholdx
            del rem[i]
        assert len(rem) == 1, "factorout(): polynomial remainder: rem=%s" % (rem,)
        if abs(rem[0]) > thanThresholdx: raise ValueError("factorout(): Non-zero remainder: rem[0]=%s" % (rem[0],))   #abs() also converts complex number to real
        return q


    def compact(self, tol=thanThresholdx):
        "Compacts zero coefficients of higher orders if they are practically zero."
        for i in xrange(len(self)-1, -1, -1):
            if abs(self[i]) > tol: break
        del self[i+1:]                    # Note that at least 1 coefficient remains (zeroth order)


    def integral(self):
        "Computes the integral of the polynomial, which is also a polynomial."
        n = len(self)
        c = Polynomial([0.0]*(n+1))
        for i,f in enumerate(self):
            c[i+1] = f/float(i+1)
        return c


    def derivative(self):
        "Computes the derivative of the polynomial, which is also a polynomial."
        n = len(self)
        if n < 1: return Polynomial((0.0,))      # Derivative of constant is zero
        c = Polynomial([0.0]*(n-1))
        for i in xrange(n-1):
            c[i] = self[i+1]*(i+1)
        return c


    def root(self, x0, eps=thanThresholdx):
        "Find a root of the polynomial with x0 as a first approximation."
        der = self.derivative()
        for itry in xrange(100):
            x1 = x0 - self(x0)/der(x0)
            if abs(x1-x0) < eps: return x1
            x0 = x1
        return None                             # No convergence


    def scale(self, fact=1.0):
        "Changes variable; original var x, new var w: x=fact*w; it returns new polynomial."
        c = Polynomial(self)
        f = 1.0
        for i in xrange(len(c)):
            c[i] *= f
            f *= fact
        return c

#===========================================================================

def test1():
    a = Polynomial((1,1,1))
    b = Polynomial((5,-10,-14,2))
    print("a=", a)
    print("b=", b)
    print("|a|=", abs(a))
    print("|b|=", abs(b))
    print("a+b=", a+b)
    print("|a+b|=", abs(a+b))
    print("a+13.45=", a+13.45)
    print("b+1=", b+1)
    print("1+b=", 1+b)
    print("b-a=", b-a)
    print("a-b=", a-b)
    print("b-1=", b-1)
    print("1-b=", 1-b)
    print("=======================================================================")
    print("a=", a)
    print("b=", b)
    print("a*b=", a*b)
    print("a*13.45=", a*13.45)
    print("b*2=", b*2)
    print("2*b=", 2*b)
    print("b/2=", b/2)
    print("+a=", +a)
    print("-a=", -a)
#    print("2/b=", 2/b      # Raises exception)
    print("=======================================================================")
    b = Polynomial((-5,1))
    print("a=", a)
    print("b=", b)
    print("a(1)=", a(1))
    print("a(2)=", a(2))
    print("a(b)=", a(b))     # b is number like
    print("integral   a=", a.integral())
    print("derivative a=", a.derivative())
    print("integral   b=", b.integral())
    print("derivative b=", b.derivative())
    print("=======================================================================")
    b = Polynomial((5,-10,-14,2,3,4))
    print("b=", b)
    q = Polynomial(b)
    for i in xrange(5):
        r1 = q.root(0.0)
        if r1 is None: break
        r1 = b.root(r1)
        print("root%d= %10.5f    remainder=%e" % (i+1, r1, b(r1)))
        q = q.factorout(r1)
    print("=======================================================================")
    b = Polynomial((5+0j,-10+0j,-14+0j,2+0j,3+0j,4+0j))
    print("b=", b)
    q = Polynomial(b)
    for i in xrange(5):
        r1 = q.root(1+1j)
        if r1 is None: break
        r1 = b.root(r1)
        print("root%d= %s    remainder=%s" % (i+1, r1, b(r1)))
        q = q.factorout(r1)


if __name__ == "__main__":
    test1()
