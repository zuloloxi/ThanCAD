# -*- coding: iso-8859-7 -*-
"""This is the equivalent of Macauley method for axial forces.

Two types of axial loading are supported:
1. Concentrated axial load Fi at some distance a from the first (left) joint
2. Uniform distribnuted axial load v, which applies to the whole legth of the member.
The loads are considered positive according to the local coordinate
system of the member. This means that positive is the dircetion which
goes form left to right (or form the first joint of the member towards the
second -the last- joint.
The axial force at distance x from the first (left) joint of the member is:

    N(x) = -Σ Fi -v*x 

Where only the concentrated loads that are before x are summed.
"""

import matdat, matk, matdxf
from mat import genEval, xrangec


class Axialmac:
    "Object to find bending moments and shear forces of a beam."

    def __init__(self, loads=()):
        "Get loads and compute internal coeficients."
        self.loads = list(loads)
        self.computeCoefs()


    def addLoad(self, load):
        "Adds a load to the beam."
        self.loads.append(load)


#    def read(self, fr):
#        "Reads the loads form an ascii file."
#        tit, blen, bstep, loads = matdat.datAll(fr)
#        self.loads.extend(loads)


    def computeCoefs(self):
        "Compute the various coefficients needed for the diagrams."
        self.coefs = computeCoefs(self.loads)


    def evalN(self, x):
        "Finds the sear force at distance x from the start."
        y = 0.0
        for f1, x1, pow1 in self.coefs: 
            if pow1 >= 0 and x > x1: y += f1 * (x-x1)**pow1
        return y


    def diags(self, blen=None, bstep=None, tit="Q, M DIAGRAMS", **kw):
        "Shows the Q, M diagrams on the screen."
        N = self.allN(blen, bstep)
#        matdxf.diag(Q, M, tit)
#        matk.diag(Q, M, tit, **kw)


    def allN(self, blen=None, bstep=None):
        "Computes N for every bstep until blen."
        if blen == None: blen = max([x1 for f1, x1, pow1 in self.coefs])
        if bstep == None: bstep = blen/1000.0 
        N = genEval(self.coefs, 0.0, blen, bstep)
        return N


def computeCoefs(loads):
    "Compute the coefficients of generalised functions."
    coefs = []
    for load in loads:
        if load[0] == "FORC":
            f1, x1 = load[1:3]
            coefs.append((-f1+0.0, x1+0.0, 0))
        elif load[0] == "UNIF":
            f1, x1, x2 = load[1:4]
            coefs.append((-f1+0.0, x1+0.0, 1))
            coefs.append(( f1+0.0, x2+0.0, 1))
        else:
            assert 0, load[0]+": Unknown load name!"
    return coefs


def test(L=5.0, Fx=50.0, v=2.0):
    loads = \
    ( ["UNIFORM", -v,  0.25*L ,  1.25*L],
      ["FORCE",   Fx+v*L*0.5,    0.25*L],
      ["FORCE",  -Fx+v*L*0.5,    1.25*L],
    )
    for load in loads: load[0] = load[0][:4]
    mac = Axialmac(loads)
    for x in [-0.01, 0.01]+list(xrangec(0.5, 1.5*L, 0.5))+[1.5*L+0.01]:
        print "x=%8.3f : N=%8.3f" % (x, mac.evalN(x))
    return mac


if __name__ == "__main__": test()
