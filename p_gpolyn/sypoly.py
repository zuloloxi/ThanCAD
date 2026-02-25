from __future__ import print_function

class SyFactor:
    """Implements a symbolic factor.

    A symbolic factor is the product of a number and zero, one, or more symbols:
        -8.5
        -8.5 a
        -8.5 a y
    """

    def __init__(self, fnum=0.0, *var):
        "Initialize the factor."
        if isinstance(fnum, SyFactor):
            other = fnum
            self.fnum = other.fnum
            if self.fnum == 0.0:
                self.var = []
            else:
                self.var = sorted(other.var)
        else:
            try: fnum+0.0
            except: raise TypeError( "Dont't know how to create SyFactor from %s" % (type(fnum),))
            self.fnum = fnum
            if fnum == 0.0:
                self.var = []
            else:
                self.var = sorted(var)
                for v in self.var:
                    try: v+"a"
                    except: raise TypeError("Symbols bust be string like; instead %s was found" % (type(v),))

    def __mul__(self, other):
        if isinstance(other, SyFactor):
            return SyFactor(self.fnum*other.fnum, *(self.var+other.var))
        try:
            other+0.0        # Check if it is number like
        except:
            raise TypeError("Don't know how to multiply SyFactor with %s" % type(other))
        return SyFactor(self.fnum*other, *self.var)


    def __rmul__ (self, other):
        "Just an alias of multiplication."
        return self.__mul__(other)


    def __pos__(self):
        "Return positive self."
        return SyFactor(self)


    def __neg__(self):
        "Return negative self."
        return SyFactor(-self.fnum, *self.var)


    def __str__(self):
        "Return self as string."
        if len(self.var) == 0:
            return "%s" % (self.fnum,)
        elif self.fnum == 1.0:
            return " ".join(self.var)
        else:
            return "%s %s" % (self.fnum, " ".join(self.var))


class SumFactor:
    "Implements a sum of symbolic factors."

    def __init__(self, v=0.0, *args):
        "Make a new SumFactor."
        if isinstance(v, SumFactor):
            self.facts = [SyFactor(f) for f in v.facts]
        else:
            v = SyFactor(v, *args)
            self.facts = [v]
        self.compact()

    def compact(self):
        "Compact SyFactors with the same symbols."
        self.facts.sort(key=lambda f: f.var)
        i = 1
        while i < len(self.facts):
            if self.facts[i-1].var == self.facts[i].var:
                self.facts[i-1].fnum += self.facts[i].fnum
                del self.facts[i]
            else:
                i += 1
        i = 0
        while i < len(self.facts):             #Delete zero SyFactors
#            print("compact: fnum=", self.facts[i].fnum,)
            if abs(self.facts[i].fnum) < 1.0e-10:
#                print(": deleted")
                del self.facts[i]
            else:
#                print(": not deleted")
                i += 1
        if len(self.facts) == 0:
            self.facts.append(SyFactor())      #Must have at least one SyFactor (=zero)


    def __add__(self, other):
        "Add 2 sumfactors."
        if not isinstance(other, SumFactor): other = SumFactor(other)  #This also accepts common numbers
        return self.list2SumFactor(self.facts+other.facts)

    @staticmethod
    def list2SumFactor(facts):
        "Create a SumFactor from a list of SyFactors or numbers."
        s = SumFactor()
        s.facts[:] = [SyFactor(f) for f in facts]    #Deepcopies SyFactors or converts to SyFactors
        s.compact()
        return s

    def __radd__ (self, other):
        "Just an alias of addition."
        return self.__add__(other)

    def __iadd__(self, other):
        "Inplace add 2 sumfactors."
        if not isinstance(other, SumFactor): other = SumFactor(other)  #This also accepts common numbers
        self.facts.extend(SyFactor(f) for f in other.facts)   #Deepcopies SyFactors
        self.compact()
        return self

    def __neg__(self):
        "Return negative self."
        s = SumFactor(self)
        for i, f in enumerate(s.facts):
            s.facts[i] = -f
        return s

    def __sub__(self, other):
        "Subtract 2 sumfactors."
        if not isinstance(other, SumFactor): other = SumFactor(other)  #This also accepts common numbers
        facts = [-f for f in other.facts]
        return self.list2SumFactor(self.facts+facts)

    def __rsub__ (self, other):
        "Subtraction other-polynomial."
        raise ValueError("Not implemented")
        return (-self)+other

    def __isub__(self, other):
        "Inplace subtract 2 sumfactors."
        if not isinstance(other, SumFactor): other = SumFactor(other)  #This also accepts common numbers
        facts = [-f for f in other.facts]
        self.facts.extend(facts)      #facts have already been deepcopied
        self.compact()
        return self


    def __mul__(self, other):
        "Multiply 2 sumfactors."
        if not isinstance(other, SumFactor): other = SumFactor(other)  #This also accepts common numbers
        facts = []
        for f1 in self.facts:
            for f2 in other.facts:
                facts.append(f1*f2)
        return self.list2SumFactor(facts)

    def __rmul__ (self, other):
        "Just an alias of multiplication."
        return self.__mul__(other)

    def __imul__(self, other):
        "Inplace multiply sumfactors."
        if not isinstance(other, SumFactor): other = SumFactor(other)  #This also accepts common numbers
        facts = []
        for f1 in self.facts:
            for f2 in other.facts:
                facts.append(f1*f2)
        self.facts[:] = facts
        self.compact()
        return self


    def __str__(self):
        "Return self as string."
        ss = [str(self.facts[0])]
        for f in self.facts[1:]:
            if f.fnum < 0.0:
                ss.append("-")
                ss.append(str(-f))
            else:
                ss.append("+")
                ss.append(str(f))
        return " ".join(ss)



#===========================================================================

def test1():
    from poly import Polynomial
    a = SyFactor()
    print("a=", a)
    b = SyFactor(5.0, "a", "b")
    print("b=", b)
    print("a*b=", a*b)
    a = SyFactor(500.0, "a", "c", "d")
    print("a=", a)
    print("a*b=", a*b)
    print()
    a = SumFactor(a)
    b = SumFactor(b)
    print("a+b+a*b=", a+b+a*b)
    print("a-b=", a-b)
    print()
    pa = Polynomial((a, b))
    print("pa=", pa)

#---Real example

    s = Polynomial((SumFactor(1.0, "a0"), SumFactor(1.0, "a1"), SumFactor(1.0, "a2"), SumFactor(1.0, "a3")))
    print("s=", s)
    v = s.derivative()
    print("v=", v)
    P = Polynomial((SumFactor(1.0, "Xp"),))
    print("P=", P)
    print("s-P=", s-P)
    print("P=", P)
    print("s=", s)
    print("P-s=", P-s)
    fivex = v * (P-s)
    print("fivex=", fivex)

    s = Polynomial((SumFactor(1.0, "b0"), SumFactor(1.0, "b1"), SumFactor(1.0, "b2"), SumFactor(1.0, "b3")))
    v = s.derivative()
    P = Polynomial((SumFactor(1.0, "Yp"),))
    fivey = v * (P-s)
    print("fivey=", fivey)

    s = Polynomial((SumFactor(1.0, "c0"), SumFactor(1.0, "c1"), SumFactor(1.0, "c2"), SumFactor(1.0, "c3")))
    v = s.derivative()
    P = Polynomial((SumFactor(1.0, "Zp"),))
    fivez = v * (P-s)
    print("fivez=", fivez)

    five = fivex + fivey + fivez
    print()
    print("five=", five)
#    print("five[0]=", five[0])
#    mu = five[0].facts[0]
#    print("mu=five[0].facts[0]=", mu)
#    print("mu.fnum=", mu.fnum, "  mu.var=", mu.var)
#    five[0].compact()
#    print("after compact five[0]=", five[0])


if __name__ == "__main__":
    test1()
