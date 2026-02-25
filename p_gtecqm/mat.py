from p_ggen import xfrangec
import matk, matdat


class Macauly:
    "Object to find bending moments and shear forces of a beam."

    def __init__(self, loads=()):
        "Get loads and compute internal coefficients."
        self.loads = list(loads)
        self.computeCoefs()


    def addLoad(self, load):
        "Adds a load to the beam."
        self.loads.append(load)


    def read(self, fr):
        "Reads the loads form an ascii file."
        tit, blen, bstep, loads = matdat.datAll(fr)
        self.loads.extend(loads)


    def computeCoefs(self):
        "Compute the various coefficients needed for the diagrams."
        self.coefs = computeCoefs(self.loads)
        self.coefsQ = genInteg(self.coefs)
        self.coefsM = genInteg(self.coefsQ)


    def evalQ(self, x):
        "Finds the sear force at distance x from the start."
        y = 0.0
        for f1, x1, pow1 in self.coefsQ: 
            if pow1 >= 0 and x > x1: y += f1 * (x-x1)**pow1
        return y


    def evalM(self, x):
        "Finds the bending moments at distance x from the start."
        y = 0.0
        for f1, x1, pow1 in self.coefsM: 
            if pow1 >= 0 and x > x1: y += f1 * (x-x1)**pow1
        return y


    def diags(self, blen=None, bstep=None, axmac=None, tit="Q, M DIAGRAMS", **kw):
        "Shows the Q, M diagrams on the screen."
        Q, M = self.allQM(blen, bstep)
        if axmac == None: N = None
        else:             N = axmac.allN(blen, bstep)
        matk.diag(Q, M, N, tit, **kw)


    def allQM(self, blen=None, bstep=None):
        "Computes Q, M for every bstep until blen."
        if blen == None: blen = max([x1 for f1, x1, pow1 in self.coefsQ])
        if bstep == None: bstep = blen/1000.0 
        Q = genEval(self.coefsQ, 0.0, blen, bstep)
        M = genEval(self.coefsM, 0.0, blen, bstep)
        return Q, M


def genInteg(coefs):
    "Integration of generalised functions."
    coefis = []
    for f1, x1, pow1 in coefs:
        pow1 += 1
        if pow1 > 1: f1 /= pow1
        coefis.append((f1, x1, pow1))
    return coefis


def genEval(coefs, xa, xb, dx):
    "Evaluates generalised functions."
    xy = []
    for x in xfrangec(xa-dx*0.01, xb+dx*0.01, dx):
        y = 0.0
        for f1, x1, pow1 in coefs: 
            if pow1 >= 0 and x > x1: y += f1 * (x-x1)**pow1
        xy.append((x, y))
    return xy


def computeCoefs(loads):
    "Compute the coefficients of generalised functions."
    coefs = []
    for load in loads:
        if load[0] == "FORC":
            f1, x1 = load[1:3]
            coefs.append((f1+0.0, x1+0.0, -1))
        elif load[0] == "UNIF":
            f1, x1, x2 = load[1:4]
            coefs.append(( f1+0.0, x1+0.0, 0))
            coefs.append((-f1+0.0, x2+0.0, 0))
        elif load[0] == "TRAP":
            f1, f2, x1, x2 = load[1:5]
            w = (f2-f1)/float(x2-x1)
            coefs.append(( w,  x1+0.0, 1))
            coefs.append(( f1, x1+0.0, 0))
            coefs.append((-w,  x2+0.0, 1))
            coefs.append((-f2, x2+0.0, 0))
        elif load[0] == "MOME":
            f1, x1 = load[1:3]
            coefs.append((f1+0.0, x1+0.0, -2))
        else:
            assert 0, load[0]+": Unknown load name!"
    return coefs


def test():
    L = 5.0; P=20.0; w=30.0
    RBy = RGy = (w * (1.5*L) + P) / 2

    loads = \
    ( ["UNIFORM", -w,  0.0,   1.5*L],
      ["FORCE",   RBy, 0.25*L],
      ["FORCE",   -P,  0.75*L],
      ["FORCE",   RGy, 1.25*L],
    )
    for load in loads: load[0] = load[0][:4]
    mac = Macauly(loads)
    for x in (0.0, 0.125*L, 0.25*L, 0.75*L, 1.25*L, 1.375*L, 1.5*L):
        print "x=%8.3f : Q=%8.3f  M=%8.3f" % (x, mac.evalQ(x), mac.evalM(x))
    import matax
    axmac=matax.test()
    mac.diags(gcname="pil")
    mac.diags(gcname="dxf")
    mac.diags(1.5*L, axmac=axmac, gcname="tk")


if __name__ == "__main__":
    test()
