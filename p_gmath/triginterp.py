from math import cos, sin, sqrt, pi
from p_gnum import zeros, Float
import p_gmath

class TrigonometricInterpolation(object):
    "This class provides the machinery for the 1st order rational polynomial projection in 2 dimensions."
    icodp = 121
    name = "Trigonometric interpolation in multiple dimensions"
    NL = -1

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            nterms = 1
            ndim = 3
            Tper = 1.0
            n = 3+ndim+1 + ndim*(2*nterms+1)
            self.L = zeros((n, ), Float)
            self.L[:] = [nterms, ndim, Tper,
                         0.0, 0.0, 0.0,       # Minimum coordnates (cmin)
                         1.0,                 # Scale factor (am)
                         0.0, 0.0, 0.0,       # Coefs for dimension 0
                         0.0, 0.0, 0.0,       # Coefs for dimesnion 1
                         0.0, 0.0, 0.0,       # Coefs for dimensjon 2
                        ]
        else:
            nterms = int(L[0])
            ndim = int(L[1])
            Tper = L[2]
            if nterms <= 0: raise(ValueError, "L[0] = Number of trigonometric terms should be > 0")
            if ndim   <= 0: raise(ValueError, "L[1] = Number of dimensions should be > 0")
            if Tper <= 0.0: raise(ValueError, "L[2] = period should be positive.")
            n = 3+ndim+1 + ndim*(2*nterms+1)
            if len(L) != n: raise(ValuError, "The number of coefs should be $d: 3 + number of dimensions + 1 + (number of dimensions) * [2*(number of terms) + 1]" % (n,))
            self.L = zeros((n, ), Float)
            self.L[:] = L


    def project(self, t):
        "Interpolates and return the coordinates of a point at time t."
        L = self.L
        nterms = int(L[0])
        ndim = int(L[1])
        Tper = L[2]
        j = 3+ndim
        cmin = L[3:j]
        am = L[j]
        j += 1

        cpoint = zeros((ndim,), Float)
        for idim in range(ndim):
            c = 0.5*L[j]
            j += 1
            for n in range(1, nterms+1):
                phi = 2.0*pi*n*t / Tper
                c += L[j]*cos(phi) + L[j+1]*sin(phi)
                j += 2
            cpoint[idim] = c
        cpoint = cpoint/am + cmin
        return cpoint


    def lsm(self, fots, nterms=None, period=None):
        "Find 1st order rational projection coefficients using least square."
        npoints = len(fots)                 #Number of known points
        if npoints < 3: return None, "At least 3 known points should be defined"
        mterms   = int((npoints-1)/2)       #Nax number of trigonometric terms (they may be less)
        if nterms is None:
            nterms = mterms
        else:
            if nterms <= 0: return None, "Number of trigonometric terms should be > 0"
        if nterms > mterms: return None, "Number of trigonometric terms should be not greater than %d for %d known points" % (mterms, npoints)
        ndim = len(fots[0][1])              #Number of dimensions
        tmax = max(t for t,_ in fots)       #Maximum time
        if period is None:
            Tper = (nterms+1) * (tmax/1)       #Period for nonperiodical function (cery big period)
            #Tper = (nterms+1) * (tmax/nterms)  #Period for periodical function with period slightly bigger than max time of data
        else:
            Tper = period
            if Tper <= 0.0: return None, "The period should be positive."
        self.L = zeros((3+ndim+1 + ndim*(2*nterms+1)),)
        self.L[0] = nterms
        self.L[1] = ndim
        self.L[2] = Tper
        nl1 = 3
        fotsr, cmin, am = self.relative(fots, ndim)
        nl2 = nl1 + ndim
        self.L[nl1:nl2] = cmin
        nl1 = nl2
        self.L[nl1] = am
        nl1 += 1

        A = zeros((npoints, 2*nterms+1), Float)
        B = zeros((npoints,), Float)
        for idim in range(ndim):
            for i, (t, cpoint) in enumerate(fotsr):
                #FIXME       ??????????WEIGHTS??????????????
                j = 0
                A[i, j] = 0.5
                for n in range(1, nterms+1):
                    phi = 2.0*pi*n*t / Tper
                    j += 1
                    A[i, j] = cos(phi)
                    j += 1
                    A[i, j] = sin(phi)
                B[i] = cpoint[idim]
            x, terr = p_gmath.lsmsolve(A, B)
            if x is None: None, terr
            nl2 = nl1 + 2*nterms+1
            self.L[nl1:nl2] = x
            nl1 = nl2
        return self.er(fots), ""


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            nterms, ndim, Tper = self.readCoefs(fr, 3)
            nterms = int(nterms)
            ndim = int(ndim)
            if nterms <= 0: raise ValueError("L[0] = Number of trigonometric terms should be > 0")
            if ndim   <= 0: raise ValueError("L[1] = Number of dimensions should be > 0")
            if Tper <= 0.0: raise ValueError("L[2] = period should be positive.")

            n = 3+ndim+1 + ndim*(2*nterms+1)
            self.L = zeros((n, ), Float)
            self.L[:3] = [nterms, ndim, Tper]
            self.L[3:] = self.readCoefs(fr, n-3)
        else:                                   # Read coefficients from polynomial1 projection
            raise ValueError("The code %d of the trigonometric interpolation was expected (found %d)" % (self.icodp, ic))


    def write(self, fw):
        "Write the projection parameters to an ascii file."
        fw.write("""\
#Trigonometric interpolation in multiple dimensions Nd
#
#       a0     M            2πn           2πn
# x =  ---- +  Σ  [ an cos(-----t) + sin(-----t) ]
#       2     n=1            T             T
#
# y, z, ..  accordingly
#
# M  = number of trigonometric terms
# Nd = number of dimensions
# T  = period
#
""")
        nterms = int(self.L[0])
        ndim = int(self.L[1])
        fw.write("\n%2d                             # ThanCad Interpolation code\n\n" % self.icodp)
        fw.write("%27.20e    #Number of trigonometric terms\n" % (self.L[0], ))
        fw.write("%27.20e    #Number of dimensions\n"          % (self.L[1], ))
        fw.write("%27.20e    #Period\n"                        % (self.L[2], ))
        j = 3

        for idim in range(ndim):
            fw.write("%27.20e    #cmin%d\n" % (self.L[j], idim))
            j += 1
        fw.write("%27.20e    #am%d\n" % (self.L[j], idim))
        j += 1

        for idim in range(ndim):
            fw.write("%27.20e    #a0\n" % (self.L[j], ))
            for i in range(1, nterms+1):
                j += 1
                fw.write("%27.20e    #a%d\n" % (self.L[j], i))
                j += 1
                fw.write("%27.20e    #b%d\n" % (self.L[j], i))


    def er(self, fots):
        "Compute the error of the interpolation."
        er = 0.0
        ndim = int(self.L[1])
        for t, cpoint in fots:
            dc = [(cb-ca)**2 for ca, cb in zip(cpoint, self.project(t))]
            er += sum(dc)
        return sqrt(er/len(fots))


    def relative(self, fots, ndim):
        "Find mean and subtract constant term; normalize world coordinates to 100."
        assert len(fots) > 1, "Only 1 point??!!"
        csum = zeros((ndim,), Float)
        cmin = zeros((ndim,), Float)
        #print "cmin=", cmin
        #print "fots[0]=", fots[0][:ndim]
        cmin[:] = fots[0][1][:ndim]
        for t, c in fots:
            for i in range(ndim):
                csum[i] += c[i]
                if c[i] < cmin[i]: cmin[i] = c[i]
        n = len(fots)
        csum /= n

        am = 1.0
        D = sqrt( sum((csum-cmin)**2) )
        if D > 0.0: am = 100.0/D
        fotsr = [(t, (c-cmin)*am) for t, c in fots]
        return fotsr, cmin, am
