"Projection transformation functions module."
from math import hypot
from p_gnum import array, matrixmultiply, transpose, solve_linear_equations, LinAlgError
from .var import thanNear2
from .lineq import linEq2
from .thanintersect import thanSegSeg
from .projcom import _Projection


###############################################################################
###############################################################################

class DLTProjection(_Projection):
    "This class provides the machinery for the DLT projection."
    icodp = 1
    name = "Direct Linear Transform Projection"
    NL = 17

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [None,
                      1.0, 0.0, 0.0, 0.0,       # Coefs for xr
                      0.0, 1.0, 0.0, 0.0,       # Coefs for yr
                      0.0, 0.0, 0.0,            # Coefs for denominator
                      0.0, 0.0, 0.0,            # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0             # xpmin, ypmin, am
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the %s" % (self.NL, self.name)
            self.L = L[:]
            self.L.insert(0, None)


    def project(self, c3d):
        "Projects 3d point with 3D DLT projection."
        X, Y, Z = c3d[:3]
        L = self.L
        X -= L[12]; Y -= L[13]; Z -= L[14]
        par = L[9]*X +  L[10]*Y + L[11]*Z + 1
        xp = (L[1]*X +  L[2]*Y + L[3]*Z + L[4]) / par
        yp = (L[5]*X +  L[6]*Y + L[7]*Z + L[8]) / par
        return xp/L[17]+L[15], yp/L[17]+L[16], c3d[2]      # The last coordinate (z) is not used


    def lsm23(self, fots):
        "Find 3D DLT coefficients using least square."
        fotsr, con, dcp = self.relative(fots)
        A, B = [], []
        for (X,Y,Z,x,y,zr,xyok,zok) in fotsr:
    #FIXME       ??????????WEIGHTS??????????????
            A.append((-X, -Y, -Z, -1, 0, 0, 0, 0, x*X, x*Y, x*Z))
            B.append(-x)
            A.append((0, 0, 0, 0, -X, -Y, -Z, -1, y*X, y*Y, y*Z))
            B.append(-y)
        A = array(A)
        B = array(B)

        AT = transpose(A)
        A = matrixmultiply(AT, A)
        B = matrixmultiply(AT, B)
        try: a = solve_linear_equations(A, B)
        except LinAlgError as why:
    #       print "Match2 DLT solution failed: ", why
            return None, None, None
        self.L = list(a)
        self.L.insert(0, None)
        self.L.extend(con)
        self.L.extend(dcp)
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
            self.L.insert(0, None)
        else:                                   # Read coefficients from polynomial1 projection
            L = self.readCoefs(fr, 8)
            self.L = [None,
                      L[0], L[1], L[2], L[3],   # Coefs for xr
                      L[4], L[5], L[6], L[7],   # Coefs for yr
                      0.0, 0.0, 0.0,            # Coefs for denominator
                      0.0, 0.0, 0.0,            # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0             # xpmin, ypmin, am
                     ]


    def write(self, fw):
        "Write the projection parameters to an ascii file."
        fw.write("""\
#DLT projection
#
#       L1 X' + L2 Y' + L3 Z' + L4
# x' = -----------------------------
#       L9 X' + L10 Y' + L11 Z' + 1
#
#       L5 X' + L6 Y' + L7 Z' + L8
# y' = -----------------------------
#       L9 X' + L10 Y' + L11 Z' + 1
#
# x = x'/mu + xmin
# y = y'/mu + ymin

# X' = X - Xmin
# Y' = Y - Ymin
# Z' = Z - Zmin
#
""")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(1, 5):  fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(5, 9):  fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(9, 12): fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        fw.write("%27.20e    # Xmin\n" % self.L[12])
        fw.write("%27.20e    # Ymin\n" % self.L[13])
        fw.write("%27.20e    # Zmin\n" % self.L[14])
        fw.write("\n")
        fw.write("%27.20e    # xmin\n" % self.L[15])
        fw.write("%27.20e    # xmin\n" % self.L[16])
        fw.write("%27.20e    # mu\n"   % self.L[17])


###############################################################################
###############################################################################

class DLT2Projection(_Projection):
    "This class provides the machinery for the DLT projection in 2 dimensions."
    icodp = 11
    name = "Direct Linear Transform 2D"
    NL = 15

    def __init__(self, L=None):
        "Initialize the object with known coefficients."
        if (L == None):
            self.L = [None,
                      1.0, 0.0, 0.0,       # Coefs for xr
                      0.0, 1.0, 0.0,       # Coefs for yr
                      0.0, 0.0,            # Coefs for denominator
                      0.0, 0.0, 0.0, 1.0,  # Xmin, Ymin, Zmin, amg
                      0.0, 0.0, 1.0        # xpmin, ypmin, am
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the %s" % (self.NL, self.name)
            self.L = L[:]
            self.L.insert(0, None)


    def project(self, c3d):
        "Projects 3d point with 2D DLT projection."
        X, Y, Z = c3d[:3]
        L = self.L
        X = (X - L[9]) *L[12]
        Y = (Y - L[10])*L[12]
#        Z = (Z - L[11])*L[12]      # correct formula, but it is not needed
        par = L[7]*X +  L[8]*Y + 1
        xp = (L[1]*X +  L[2]*Y + L[3]) / par
        yp = (L[4]*X +  L[5]*Y + L[6]) / par
        return xp/L[15]+L[13], yp/L[15]+L[14], c3d[2]      # The last coordinate (z) is not used


    def lsm23(self, fots):
        "Find 2D DLT coefficients using least square."
        fotsr, con, dcp = self.relative(fots)
        A, B = [], []
        for (X,Y,Z,x,y,zr,xyok,zok) in fotsr:
    #FIXME       ??????????WEIGHTS??????????????
            A.append((-X, -Y, -1, 0, 0, 0, x*X, x*Y))
            B.append(-x)
            A.append((0, 0, 0, -X, -Y, -1, y*X, y*Y))
            B.append(-y)
        A = array(A)
        B = array(B)

        AT = transpose(A)
        A = matrixmultiply(AT, A)
        B = matrixmultiply(AT, B)
        try: a = solve_linear_equations(A, B)
        except LinAlgError as why:
    #       print "Match2 DLT solution failed: ", why
            return None, None, None
        self.L = list(a)
        self.L.insert(0, None)
        self.L.extend(con)
        self.L.append(1.0)                  # amg
        self.L.extend(dcp)
        return self.er(fots)


    def invert(self):
        """Returns the inverse of current transformation which is also a DLT in 2 dimensions."

       (L5 - L6 L8)          (L3 L8 - L2)         (L6 L2 - L3 L5)
      ----------------- x + ---------------- y + -----------------
       (L1 L5 - L4 L2)       (L1 L5 - L4 L2)      (L1 L5 - L4 L2)
X = ------------------------------------------------------------------
           (L4 L8 - L7 L5)       (L7 L2 - L1 L8)
          ----------------- x + ---------------- y + 1
           (L1 L5 - L4 L2)       (L1 L5 - L4 L2)


       (L7 L6 - L4)          (L1 -L7 L3)          L4 L3 - L1 L6
      ----------------- x + ---------------- y + -----------------
       (L1 L5 - L4 L2)       (L1 L5 - L4 L2)      (L1 L5 - L4 L2)
Y = ------------------------------------------------------------------
           (L4 L8 - L7 L5)       (L7 L2 - L1 L8)
          ----------------- x + ---------------- y + 1
           (L1 L5 - L4 L2)       (L1 L5 - L4 L2)

        """
        L = self.L
        par = (L[1]*L[5] - L[4]*L[2])
        M = [ None,
          (L[5]      - L[6]*L[8]) / par,
          (L[3]*L[8] - L[2])      / par,
          (L[6]*L[2] - L[3]*L[5]) / par,
          (L[7]*L[6] - L[4])      / par,
          (L[1]      - L[7]*L[3]) / par,
          (L[4]*L[3] - L[1]*L[6]) / par,
          (L[4]*L[8] - L[7]*L[5]) / par,
          (L[7]*L[2] - L[1]*L[8]) / par,
          L[13], L[14], 0.0, L[15],          # Xmin, Ymin, Zmin, amg
          L[9], L[10], L[12],                # xpmin, ypmin, am
        ]
        return self.__class__(M)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
            self.L.insert(0, None)
        else:                                   # Read coefficients from polynomial1 2D projection
            L = self.readCoefs(fr, 6)
            self.L = [None,
                      L[0], L[1], L[2],         # Coefs for xr
                      L[3], L[4], L[5],         # Coefs for yr
                      0.0, 0.0,                 # Coefs for denominator
                      0.0, 0.0, 0.0, 1.0,       # Xmin, Ymin, Zmin, amg
                      0.0, 0.0, 1.0             # xpmin, ypmin, am
                     ]


    def write(self, fw):
        "Write the projection parameters to an ascii file."
        fw.write("""\
#DLT projection in 2 dimensions
#
#       L1 X' + L2 Y' + L3
# x' = --------------------
#       L7 X' + L8 Y' + 1
#
#       L4 X' + L5 Y' + L6
# y' = --------------------
#       L7 X' + L8 Y' + 1
#
# x = x'/mu + xmin
# y = y'/mu + ymin

# X' = (X - Xmin)*mug
# Y' = (Y - Ymin)*mug
#
""")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(1, 4): fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(4, 7): fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(7, 9): fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        fw.write("%27.20e    # Xmin\n" % self.L[9])
        fw.write("%27.20e    # Ymin\n" % self.L[10])
        fw.write("%27.20e    # Zmin\n" % self.L[11])
        fw.write("%27.20e    # mug\n"  % self.L[12])
        fw.write("\n")
        fw.write("%27.20e    # xmin\n" % self.L[13])
        fw.write("%27.20e    # xmin\n" % self.L[14])
        fw.write("%27.20e    # mu\n"   % self.L[15])


###############################################################################
###############################################################################

class Rational1Projection(_Projection):
    "This class provides the machinery for the 1st order rational polynomial projection."
    icodp = 2
    name = "1st order rational projection"
    NL = 20

    def __init__(self, L=None):
        "Initialize the object with known coefficients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0, 0.0,       # Coefs for xr
                      0.0, 0.0, 0.0,            # Coefs for denominator xr
                      0.0, 1.0, 0.0, 0.0,       # Coefs for yr
                      0.0, 0.0, 0.0,            # Coefs for denominator yr
                      0.0, 0.0, 0.0,            # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0             # xpmin, ypmin, am
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the %s" % (self.NL, self.name)
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with 1st order rational projection."
        X, Y, Z = c3d[:3]
        L = self.L
        X -= L[14]; Y -= L[15]; Z -= L[16]
        par = L[4]*X +  L[5]*Y + L[6]*Z + 1
        xp = (L[0]*X +  L[1]*Y + L[2]*Z + L[3]) / par
        par = L[11]*X +  L[12]*Y + L[13]*Z + 1
        yp = (L[7]*X +  L[8]*Y + L[9]*Z + L[10]) / par
        return xp/L[19]+L[17], yp/L[19]+L[18], c3d[2]      # The last coordinate (z) is not used


    def lsm23(self, fots):
        "Find 1st order rational projection coefficients using least square."
        fotsr, con, dcp = self.relative(fots)
        self.L = []
        for i in 0, 1:
            A, B = [], []
            for (X,Y,Z,x,y,zr,xyok,zok) in fotsr:
                #FIXME       ??????????WEIGHTS??????????????
                if i == 0: cx = x
                else:      cx = y
                A.append((-X, -Y, -Z, -1, cx*X, cx*Y, cx*Z))
                B.append(-cx)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#               print "Match2 Rational 1 solution failed: ", why
                return None, None, None
            self.L.extend(list(a))

        self.L.extend(con)
        self.L.extend(dcp)
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
        else:                                   # Read coefficients from polynomial1 projection
            L = self.readCoefs(fr, 8)
            self.L = [L[0], L[1], L[2], L[3],   # Coefs for xr
                      0.0, 0.0, 0.0,            # Coefs for denominator xr
                      L[4], L[5], L[6], L[7],   # Coefs for yr
                      0.0, 0.0, 0.0,            # Coefs for denominator yr
                      0.0, 0.0, 0.0,            # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0             # xpmin, ypmin, am
                     ]


    def write(self, fw):
        "Write the projection parameters to an ascii file."
        fw.write("""\
#Rational projection of first order
#
#       L1 X' + L2 Y' + L3 Z' + L4
# x' = ----------------------------
#       L5 X' + L6 Y' + L7 Z' + 1
#
#       L8 X' + L9 Y' + L10 Z' + L11
# y' = ------------------------------
#       L12 X' + L13 Y' + L14 Z' + 1
#
# x = x/mu + xmin
# y = y/mu + ymin

# X' = X - Xmin
# Y' = Y - Ymin
# Z' = Z - Zmin
#
""")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(0, 4):   fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(4, 7):   fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(7, 11):  fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(11, 14): fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        fw.write("%27.20e    #Xmin\n" % self.L[14])
        fw.write("%27.20e    #Ymin\n" % self.L[15])
        fw.write("%27.20e    #Zmin\n" % self.L[16])
        fw.write("\n")
        fw.write("%27.20e    #xmin\n" % self.L[17])
        fw.write("%27.20e    #xmin\n" % self.L[18])
        fw.write("%27.20e    #mu\n"   % self.L[19])


###############################################################################
###############################################################################

class Rational1_2DProjection(_Projection):
    "This class provides the machinery for the 1st order rational polynomial projection in 2 dimensions."
    icodp = 12
    name = "1st order rational in 2D"
    NL = 16

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0,       # Coefs for xr
                      0.0, 0.0,            # Coefs for denominator xr
                      0.0, 1.0, 0.0,       # Coefs for yr
                      0.0, 0.0,            # Coefs for denominator yr
                      0.0, 0.0, 0.0,       # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0        # xpmin, ypmin, am
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the Rational1 Projection in 2D" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with 1st order rational polynomial projection."
        X, Y, Z = c3d[:3]
        L = self.L
        X -= L[10]; Y -= L[11]; Z -= L[12]
        par = L[3]*X +  L[4]*Y + 1
        xp = (L[0]*X +  L[1]*Y + L[2]) / par
        par = L[8]*X +  L[9]*Y + 1
        yp = (L[5]*X +  L[6]*Y + L[7]) / par
        return xp/L[15]+L[13], yp/L[15]+L[14], c3d[2]      # The last coordinate (z) is not used


    def lsm23(self, fots):
        "Find 1st order rational projection coefficients using least square."
        fotsr, con, dcp = self.relative(fots)
        self.L = []
        for i in 0, 1:
            A, B = [], []
            for (X,Y,Z,x,y,zr,xyok,zok) in fotsr:
                #FIXME       ??????????WEIGHTS??????????????
                if i == 0: cx = x
                else:      cx = y
                A.append((-X, -Y, -1, cx*X, cx*Y))
                B.append(-cx)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#               print "Match2 Rational 1 solution failed: ", why
                return None, None, None
            self.L.extend(list(a))

        self.L.extend(con)
        self.L.extend(dcp)
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
        else:                                   # Read coefficients from polynomial1 projection
            L = self.readCoefs(fr, 6)
            self.L = [L[0], L[1], L[2],   # Coefs for xr
                      0.0, 0.0,           # Coefs for denominator xr
                      L[3], L[4], L[5],   # Coefs for yr
                      0.0, 0.0,           # Coefs for denominator yr
                      0.0, 0.0, 0.0,      # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0       # xpmin, ypmin, am
                     ]


    def write(self, fw):
        "Write the projection parameters to an ascii file."
        fw.write("""\
#Rational projection of first order in 2 dimensions
#
#       L1 X' + L2 Y' + L3
# x' = --------------------
#       L4 X' + L5 Y' + 1
#
#       L6 X' + L7 Y' + L8
# y' = --------------------
#       L9 X' + L10 Y' + 1
#
# x = x/mu + xmin
# y = y/mu + ymin

# X' = X - Xmin
# Y' = Y - Ymin
# Z' = Z - Zmin
#
""")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(0, 3):   fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(3, 5):   fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(5, 8):  fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(8, 10): fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        fw.write("%27.20e    #Xmin\n" % self.L[10])
        fw.write("%27.20e    #Ymin\n" % self.L[11])
        fw.write("%27.20e    #Zmin\n" % self.L[12])
        fw.write("\n")
        fw.write("%27.20e    #xmin\n" % self.L[13])
        fw.write("%27.20e    #xmin\n" % self.L[14])
        fw.write("%27.20e    #mu\n"   % self.L[15])


###############################################################################
###############################################################################

class Rational2Projection(_Projection):
    "This class provides the machinery for the 2nd order rational polynomial projection."
    icodp = 4
    name = "2nd order rational"
    NL = 36

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,      # Coefs for xr
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,           # Coefs for denominator xr
                      0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,      # Coefs for yr
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,           # Coefs for denominator yr
                      0.0, 0.0, 0.0,            # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0             # xpmin, ypmin, am
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the Rational2 Projection" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with 2nd order rational projection."
        X, Y, Z = c3d[:3]
        L = self.L
        X -= L[30]; Y -= L[31]; Z -= L[32]
        par =  L[8]*X +  L[9]*Y +  L[10]*Z + 1 +     L[11]*X**2 + L[12]*Y**2 + L[13]*Z**2 + L[14]*X*Y
        xp = ( L[0]*X +  L[1]*Y +   L[2]*Z + L[3] +   L[4]*X**2 +  L[5]*Y**2 +  L[6]*Z**2 +  L[7]*X*Y) / par
        par = L[23]*X +  L[24]*Y + L[25]*Z + 1 +     L[26]*X**2 + L[27]*Y**2 + L[28]*Z**2 + L[29]*X*Y
        yp = (L[15]*X +  L[16]*Y + L[17]*Z + L[18] + L[19]*X**2 + L[20]*Y**2 + L[21]*Z**2 + L[22]*X*Y) / par
        return xp/L[35]+L[33], yp/L[35]+L[34], c3d[2]      # The last coordinate (z) is not used


    def lsm23(self, fots):
        "Find 2nd order rational projection coefficients using least square."
        fotsr, con, dcp = self.relative(fots)
        self.L = []
        for i in 0, 1:
            A, B = [], []
            for (X,Y,Z,x,y,zr,xyok,zok) in fotsr:
                #FIXME       ??????????WEIGHTS??????????????
                if i == 0: cx = x
                else:      cx = y
                A.append((-X, -Y, -Z, -1, -X**2, -Y**2, -Z**2, -X*Y, cx*X, cx*Y, cx*Z, cx*X**2, cx*Y**2, cx*Z**2, cx*X*Y))
                B.append(-cx)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#               print "Match2 Rational 1 solution failed: ", why
                return None, None, None
            self.L.extend(list(a))

        self.L.extend(con)
        self.L.extend(dcp)
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
        else:                                   # Read coefficients from polynomial1 projection
            L = self.readCoefs(fr, 8)
            self.L = [L[0], L[1], L[2], L[3],  0.0, 0.0, 0.0, 0.0,  # Coefs for xr
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,            # Coefs for denominator xr
                      L[4], L[5], L[6], L[7],  0.0, 0.0, 0.0, 0.0,  # Coefs for yr
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,            # Coefs for denominator yr
                      0.0, 0.0, 0.0,                                # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0                                 # xpmin, ypmin, am
                     ]


    def write(self, fw):
        "Write the projection parameters to an ascii file."
        fw.write("""\
#Rational projection of second order
#
#       L0 X' + L1 Y' + L2 Z' + L3 +  L4 X^2 +  L5 Y^2 +  L6 Z^2 +  L7 X Y
# x' = --------------------------------------------------------------------
#       L8 X' + L9 Y' + L10 Z' + 1 + L11 X^2 + L12 Y^2 + L13 Z^2 + L14 X Y
#
#       L15 X' + L16 Y' + L17 Z' + L18 + L19 X^2 + L20 Y^2 + L21 Z^2 + L22 X Y
# y' = ----------------------------------------------------------------------------
#       L23 X' + L24 Y' + L25 Z' + 1   + L26 X^2 + L27 Y^2 + L28 Z^2 + L29 X Y
#
# x = x/mu + xmin
# y = y/mu + ymin

# X' = X - Xmin
# Y' = Y - Ymin
# Z' = Z - Zmin
#
""")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(0, 8):   fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(8, 15):  fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(15, 23): fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(23, 30): fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        fw.write("%27.20e    #Xmin\n" % self.L[30])
        fw.write("%27.20e    #Ymin\n" % self.L[31])
        fw.write("%27.20e    #Zmin\n" % self.L[32])
        fw.write("\n")
        fw.write("%27.20e    #xmin\n" % self.L[33])
        fw.write("%27.20e    #xmin\n" % self.L[34])
        fw.write("%27.20e    #mu\n"   % self.L[35])


###############################################################################
###############################################################################

class Rational15Projection(_Projection):
    "This class provides the machinery for the 2nd order nominator, first order denominator polynomial projection."
    icodp = 5
    name = "2nd and 1st order rational"
    NL = 28

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,      # Coefs for xr
                      0.0, 0.0, 0.0,                               # Coefs for denominator xr
                      0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,      # Coefs for yr
                      0.0, 0.0, 0.0,                               # Coefs for denominator yr
                      0.0, 0.0, 0.0,            # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0             # xpmin, ypmin, am
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the Rational 1.5 Projection" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with rational (2nd and 1st) projection."
        X, Y, Z = c3d[:3]
        L = self.L
        X -= L[22]; Y -= L[23]; Z -= L[24]
        par =  L[8]*X +  L[9]*Y +  L[10]*Z + 1
        xp = ( L[0]*X +  L[1]*Y +   L[2]*Z + L[3] +   L[4]*X**2 +  L[5]*Y**2 +  L[6]*Z**2 +  L[7]*X*Y) / par
        par = L[19]*X +  L[20]*Y + L[21]*Z + 1
        yp = (L[11]*X +  L[12]*Y + L[13]*Z + L[14] + L[15]*X**2 + L[16]*Y**2 + L[17]*Z**2 + L[18]*X*Y) / par
        return xp/L[27]+L[25], yp/L[27]+L[26], c3d[2]      # The last coordinate (z) is not used


    def lsm23(self, fots):
        "Find rational (2nd and 1st) projection coefficients using least square."
        fotsr, con, dcp = self.relative(fots)
        self.L = []
        for i in 0, 1:
            A, B = [], []
            for (X,Y,Z,x,y,zr,xyok,zok) in fotsr:
                #FIXME       ??????????WEIGHTS??????????????
                if i == 0: cx = x
                else:      cx = y
                A.append((-X, -Y, -Z, -1, -X**2, -Y**2, -Z**2, -X*Y, cx*X, cx*Y, cx*Z))
                B.append(-cx)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#               print "Match2 Rational 1 solution failed: ", why
                return None, None, None
            self.L.extend(list(a))

        self.L.extend(con)
        self.L.extend(dcp)
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the reponsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
        else:                                   # Read coefficients from polynomial1 projection
            L = self.readCoefs(fr, 8)
            self.L = [L[0], L[1], L[2], L[3],  0.0, 0.0, 0.0, 0.0,  # Coefs for xr
                      0.0, 0.0, 0.0,                                # Coefs for denominator xr
                      L[4], L[5], L[6], L[7],  0.0, 0.0, 0.0, 0.0,  # Coefs for yr
                      0.0, 0.0, 0.0,                                # Coefs for denominator yr
                      0.0, 0.0, 0.0,                                # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0                                 # xpmin, ypmin, am
                     ]


    def write(self, fw):
        "Write the projection parameters to an ascii file."
        fw.write("""\
#Rational projection of second order
#
#       L0 X' + L1 Y' + L2 Z' + L3 +  L4 X^2 +  L5 Y^2 +  L6 Z^2 +  L7 X Y
# x' = --------------------------------------------------------------------
#       L8 X' + L9 Y' + L10 Z' + 1
#
#       L11 X' + L12 Y' + L13 Z' + L14 + L15 X^2 + L16 Y^2 + L17 Z^2 + L18 X Y
# y' = ----------------------------------------------------------------------------
#       L19 X' + L20 Y' + L21 Z' + 1
#
# x = x/mu + xmin
# y = y/mu + ymin

# X' = X - Xmin
# Y' = Y - Ymin
# Z' = Z - Zmin
#
""")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(0, 8):   fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(8, 11):  fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(11, 19): fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        for i in range(19, 22): fw.write("%27.20e    #L%d\n" % (self.L[i], i+1))
        fw.write("\n")
        fw.write("%27.20e    #Xmin\n" % self.L[22])
        fw.write("%27.20e    #Ymin\n" % self.L[23])
        fw.write("%27.20e    #Zmin\n" % self.L[24])
        fw.write("\n")
        fw.write("%27.20e    #xmin\n" % self.L[25])
        fw.write("%27.20e    #xmin\n" % self.L[26])
        fw.write("%27.20e    #mu\n"   % self.L[27])


###############################################################################
###############################################################################

class Polynomial1Projection(_Projection):
    "This class provides the machinery for the polynomial projection of 1st degree."
    icodp = 0
    name = "1st order polynomial"
    NL = 8

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0, 0.0,       # Coefs for xr
                      0.0, 1.0, 0.0, 0.0,       # Coefs for yr
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the Polynomial Projection of 1st order" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with polynomial projection."
        x, y, z = c3d[:3]
        L = self.L
        xp = L[0]*x+L[1]*y+L[2]*z+L[3]
        yp = L[4]*x+L[5]*y+L[6]*z+L[7]
        return xp, yp, z      # The last coordinate (z) is not used


    def invproject(self, xp, yp, z):
        "Compute object coordinates given pixel coordinates x,y and object coordinate z."
#        xp = L[0]*x+L[1]*y+L[2]*z+L[3]     =>
#        yp = L[4]*x+L[5]*y+L[6]*z+L[7]
#        xp-L[2]*z-L[3] = L[0]*x+L[1]*y
#        yp-L[6]*z-L[7] = L[4]*x+L[5]*y
        L = self.L
        x, y = linEq2(L[0], L[1], xp-L[2]*z-L[3],
                      L[4], L[5], yp-L[6]*z-L[7])
        if x is None: raise ValueError("%s projection can not be inverted" % (self.name,))
        return x, y, z


    def lsm23(self, fots):
        "Find polynomial coefficients using least square."
        L = []
        for i in 0, 1:
            A, B = [], []
            for xg,yg,zg,xr,yr,zr,xyok,zok in fots:
                A.append([xg*xyok, yg*xyok, zg*xyok, xyok])
                if i == 0: B.append(xr*xyok)
                else     : B.append(yr*xyok)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#                print "Match2 polynomial solution failed: ", why
                return None, None, None
            L.extend(list(a))
        self.L = L
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        assert ic == self.icodp, "Well it IS a polynomial1 projection!"
        self.L = self.readCoefs(fr, self.NL)


    def write(self, fw):
        "Write the projection coefficients to a text file."
        fw.write("#First order polynomial projection\n")
        fw.write("# x = L0 X + L1 Y + L2 Z + L3\n")
        fw.write("# y = L4 X + L5 Y + L6 Z + L7\n")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(4): fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(4, 8): fw.write("%27.20e    # L%d\n" % (self.L[i], i))


###############################################################################
###############################################################################

class Polynomial1_2DProjection(_Projection):
    "This class provides the machinery for the polynomial projection of 1st degree."
    icodp = 10
    name = "1st order polynomial"
    NL = 6

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0,       # Coefs for xr
                      0.0, 1.0, 0.0,       # Coefs for yr
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the %s projection" % (self.NL, self.name)
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with polynomial projection."
        x, y, z = c3d[:3]
        L = self.L
        xp = L[0]*x+L[1]*y+L[2]
        yp = L[3]*x+L[4]*y+L[5]
        return xp, yp, z      # The last coordinate (z) is not used


    def invertold(self):   #Old method: Does not control numerical error
        """Returns the inverse of current transformation which is also a DLT in 2 dimensions."

       L5                    -L2                  (L6 L2 - L3 L5)
X =   ----------------- x + ---------------- y + -----------------
       (L1 L5 - L4 L2)       (L1 L5 - L4 L2)      (L1 L5 - L4 L2)

       -L4                   L1                   L4 L3 - L1 L6
Y =   ----------------- x + ---------------- y + -----------------
       (L1 L5 - L4 L2)       (L1 L5 - L4 L2)      (L1 L5 - L4 L2)

        """
        L = list(self.L)
        L.insert(0, None)
        par = (L[1]*L[5] - L[4]*L[2])
        M = [ L[5] / par,
             -L[2]      / par,
             (L[6]*L[2] - L[3]*L[5]) / par,
             -L[4]      / par,
              L[1] / par,
             (L[4]*L[3] - L[1]*L[6]) / par,
        ]
        return self.__class__(M)


    def invert(self):
        """Returns the inverse of current transformation which is also a DLT in 2 dimensions."

       L5                    -L2                  (L6 L2 - L3 L5)
X =   ----------------- x + ---------------- y + -----------------
       (L1 L5 - L4 L2)       (L1 L5 - L4 L2)      (L1 L5 - L4 L2)

       -L4                   L1                   L4 L3 - L1 L6
Y =   ----------------- x + ---------------- y + -----------------
       (L1 L5 - L4 L2)       (L1 L5 - L4 L2)      (L1 L5 - L4 L2)

        If the constant terms L[2] and L[5] are large, then numerical error creeps in.
        Thus we set L[2]=L[5]=0, which means that x=0,y=0 corresponds to xp=0,yp=0
        instead of xp=L[2],yp=L[5].
        We compute the invserse, and then we crorrect the inverse so that xp=L[2],yp=L[5]
        corresponds to x=0,y=0.
        """
        L = list(self.L)
        L[2] = L[5] = 0.0   #Avoid numerical error
        L.insert(0, None)
        par = L[1]*L[5] - L[4]*L[2]
        M = [ L[5]/par, -L[2]/par,  0.0,
             -L[4]/par,  L[1]/par,  0.0,
        ]

        xp = self.L[2]
        yp = self.L[5]
        x = M[0]*xp+M[1]*yp+M[2]
        y = M[3]*xp+M[4]*yp+M[5]
        #print("invert: x,y=", x, y, "M[2],M[5]=", M[2], M[5])
        M[2] -= x   #Avoid numerical error
        M[5] -= y   #Avoid numerical error
        return self.__class__(M)


    def chain(self, other):
        """Chain this transformation and another; first current then the other.

        xp = L[0]*x+L[1]*y+L[2]
        yp = L[3]*x+L[4]*y+L[5]
        xn = M[0]*xp+M[1]*yp+M[2] = M[0] * {L[0]*x+L[1]*y+L[2]} + M[1] *  {L[3]*x+L[4]*y+L[5]} + M[2] = 
             M[0]*L[0]*x + M[0]*L[1]*y + M[0]*L[2] + M[1]*L[3]*x + M[1]*L[4]*y + M[1]*L[5] + M[2]
             {M[0]*L[0] + M[1]*L[3]}*x + {M[0]*L[1] + M[1]*L[4]}*y + {M[0]*L[2] + M[1]*L[5] + M[2]}
        yn = M[3]*xp+M[4]*yp+M[5]
        """
        LL = [None]*6
        L = self.L
        M = other.L
        LL[0] = M[0]*L[0] + M[1]*L[3]
        LL[1] = M[0]*L[1] + M[1]*L[4]
        LL[2] = M[0]*L[2] + M[1]*L[5] + M[2]

        LL[3] = M[3]*L[0] + M[4]*L[3]
        LL[4] = M[3]*L[1] + M[4]*L[4]
        LL[5] = M[3]*L[2] + M[4]*L[5] + M[5]
        self.L[:] = LL


    def lsm23(self, fots):
        "Find polynomial coefficients using least square."
        L = []
        for i in 0, 1:
            A, B = [], []
            for xg,yg,zg,xr,yr,zr,xyok,zok in fots:
                A.append([xg*xyok, yg*xyok, xyok])
                if i == 0: B.append(xr*xyok)
                else     : B.append(yr*xyok)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#                print "Match2 polynomial solution failed: ", why
                return None, None, None
            L.extend(list(a))
        self.L = L
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        assert ic == self.icodp, "Well it IS a polynomial1 2D projection!"
        self.L = self.readCoefs(fr, self.NL)


    def readtfw(self, fr):
        """Reads the coefficients of the affine (2d polynomial) projection from a .tfw/.j2w files.

Does not raise exceptions; it retuenrs error message as text.

Affine transformation for tfw/j2w files; taken from ThanCad::ThanImage::thanTfwGet()."
Dimitra 2012_04_03
The relationship between EGSA87 X, Y coordinates and the pixel coordinates
of the othophotos is the affine transformation:
X = ax X + bx Y + cx
Y = ay X + by Y + cy
The coefficents are written in ascii form in the 6 lines of
the *.tfw files:
Line   Coefficient
1      ax
2      ay
3      bx
4      by
5      cx
6      cy

In all cases seen in orthophotos of LIDAR, the coefficents ay and bx are
zero, rendering the equation in simpler form:
X = ax X + cx
Y = by Y + cy

Looking at the coefficients found in *.tfw files, we conclude that the first
pixel is pixel 0 and not pixel 1. That's why they have put +0.50 in
cx and cy coefficients:

1.0000000000
0.0
0.0
-1.0000000000
551884.5000000000
4176435.5000000000

Using the formulas and the number pixel in the x and y direction, we
compute the corner points.
        """
        try: fn = fr.name
        except: fn = "<Unknown>"
        try:
            ax = float(next(fr))
            ay = float(next(fr))
            bx = float(next(fr))
            by = float(next(fr))
            cx = float(next(fr))
            cy = float(next(fr))
        except StopIteration:
            return IOError("Incomplete .tfw/.j2w file '{}'".format(fn))
        except IOError as e:
            return "Can not access .tfw/.j2w file '{}': {}".format(fn, e)
        except ValueError as e:
            return "Invalid .tfw/.j2w file '{}': {}".format(fn, e)
        self.L[:] = ax, bx, cx, ay, by, cy
        return ""

    def write(self, fw):
        "Write the projection coefficients to a text file."
        fw.write("#First order polynomial projection\n")
        fw.write("# x = L0 X + L1 Y + L2\n")
        fw.write("# y = L3 X + L4 Y + L5\n")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(3):    fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(3, 6): fw.write("%27.20e    # L%d\n" % (self.L[i], i))


class Polynomial1_2D_normalisedProjection(_Projection):
    """This class provides the machinery for the polynomial projection of 1st degree.

    The data are normalised (distance and size) before the application of the LSM.
    This should produce identical results with Polynomial1_2DProjection.
    This class is used for testing and debugging.
    """
    icodp = 10
    name = "1st order polynomial"
    NL = 12

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0,       # Coefs for xr
                      0.0, 1.0, 0.0,       # Coefs for yr
                      0.0, 0.0, 0.0,            # Xmin, Ymin, Zmin
                      0.0, 0.0, 1.0             # xpmin, ypmin, am
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the Polynomial 2D Projection of 1st order" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with polynomial projection."
        x, y, z = c3d[:3]
        L = self.L
        x -= L[6]; y -= L[7]; z -= L[8]
        xp = L[0]*x+L[1]*y+L[2]
        yp = L[3]*x+L[4]*y+L[5]
        return xp/L[11]+L[9], yp/L[11]+L[10], c3d[2]      # The last coordinate (z) is not used


    def invert(self):
        """Returns the inverse of current transformation which is also a DLT in 2 dimensions."

       L5                    -L2                  (L6 L2 - L3 L5)
X =   ----------------- x + ---------------- y + -----------------
       (L1 L5 - L4 L2)       (L1 L5 - L4 L2)      (L1 L5 - L4 L2)

       -L4                   L1                   L4 L3 - L1 L6
Y =   ----------------- x + ---------------- y + -----------------
       (L1 L5 - L4 L2)       (L1 L5 - L4 L2)      (L1 L5 - L4 L2)

        """
        L = list(self.L)
        L.insert(0, None)
        par = (L[1]*L[5] - L[4]*L[2])
        M = [ L[5] / par,
             -L[2]      / par,
             (L[6]*L[2] - L[3]*L[5]) / par,
             -L[4]      / par,
              L[1] / par,
             (L[4]*L[3] - L[1]*L[6]) / par,
        ]
        return self.__class__(M)


    def chain(self, other):
        """Chain this transformation and another; first current then the other.

        xp = L[0]*x+L[1]*y+L[2]
        yp = L[3]*x+L[4]*y+L[5]
        xn = M[0]*xp+M[1]*yp+M[2] = M[0] * {L[0]*x+L[1]*y+L[2]} + M[1] *  {L[3]*x+L[4]*y+L[5]} + M[2] = 
             M[0]*L[0]*x + M[0]*L[1]*y + M[0]*L[2] + M[1]*L[3]*x + M[1]*L[4]*y + M[1]*L[5] + M[2]
             {M[0]*L[0] + M[1]*L[3]}*x + {M[0]*L[1] + M[1]*L[4]}*y + {M[0]*L[2] + M[1]*L[5] + M[2]}
        yn = M[3]*xp+M[4]*yp+M[5]
        """
        LL = [None]*6
        L = self.L
        M = other.L
        LL[0] = M[0]*L[0] + M[1]*L[3]
        LL[1] = M[0]*L[1] + M[1]*L[4]
        LL[2] = M[0]*L[2] + M[1]*L[5] + M[2]

        LL[3] = M[3]*L[0] + M[4]*L[3]
        LL[4] = M[3]*L[1] + M[4]*L[4]
        LL[5] = M[3]*L[2] + M[4]*L[5] + M[5]
        self.L[:] = LL


    def lsm23(self, fots):
        "Find polynomial coefficients using least square."
        fotsr, con, dcp = self.relative(fots)
        L = []
        for i in 0, 1:
            A, B = [], []
            for xg,yg,zg,xr,yr,zr,xyok,zok in fotsr:
                A.append([xg*xyok, yg*xyok, xyok])
                if i == 0: B.append(xr*xyok)
                else     : B.append(yr*xyok)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#                print "Match2 polynomial solution failed: ", why
                return None, None, None
            L.extend(list(a))
        self.L = L
        self.L.extend(con)
        self.L.extend(dcp)
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        assert ic == self.icodp, "Well it IS a polynomial1 2D projection!"
        self.L = self.readCoefs(fr, self.NL)


    def write(self, fw):
        "Write the projection coefficients to a text file."
        fw.write("#First order polynomial projection\n")
        fw.write("# x = L0 X + L1 Y + L2\n")
        fw.write("# y = L3 X + L4 Y + L5\n")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(3):    fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(3, 6): fw.write("%27.20e    # L%d\n" % (self.L[i], i))


###############################################################################
###############################################################################

class Polynomial2Projection(_Projection):
    "This class provides the machinery for the polynomial projection of 2nd degree."
    icodp = 3
    name = "2nd order polynomial"
    NL = 16

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,     # Coefs for xr
                      0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0      # Coefs for yr
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the Polynomial Projection of 2nd order" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with 2nd order polynomial projection."
        x, y, z = c3d[:3]
        L = self.L
        xp = L[0]*x+L[1]*y+L[2] *z+L[3] +L[4] *x**2+L[5] *y**2+L[6] *z**2+L[7] *x*y
        yp = L[8]*x+L[9]*y+L[10]*z+L[11]+L[12]*x**2+L[13]*y**2+L[14]*z**2+L[15]*x*y
        return xp, yp, z      # The last coordinate (z) is not used


    def lsm23(self, fots):
        "Find 2nd order polynomial projection coefficients using least square."
        L = []
        for i in 0, 1:
            A, B = [], []
            for xg,yg,zg,xr,yr,zr,xyok,zok in fots:
                A.append([xg, yg, zg, 1.0, xg**2, yg**2, zg**2, xg*yg])
                if i == 0: B.append(xr)
                else     : B.append(yr)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#                print "Match2 polynomial solution failed: ", why
                return None, None, None
            L.extend(list(a))
        self.L = L
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
        else:                                   # Read coefficients from polynomial1 projection
            L = self.readCoefs(fr, 8)
            self.L = [L[0], L[1], L[2], L[3], 0.0, 0.0, 0.0, 0.0,     # Coefs for xr
                      L[4], L[5], L[6], L[7], 0.0, 0.0, 0.0, 0.0      # Coefs for yr
                     ]


    def write(self, fw):
        "Write the projection coefficients to a text file."
        fw.write("#Second order polynomial projection\n")
        fw.write("# x = L0 X + L1 Y + L2  Z + L3  + L4  X^2 + L5  Y^2 + L6  Z^2 + L7  X Y\n")
        fw.write("# y = L8 X + L9 Y + L10 Z + L11 + L12 X^2 + L13 Y^2 + L14 Z^2 + L15 X Y\n")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(8): fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(8, 16): fw.write("%27.20e    # L%d\n" % (self.L[i], i))


###############################################################################
###############################################################################

class Polynomial2_2DProjection(_Projection):
    "This class provides the machinery for the polynomial projection of 2nd degree in 2 dimensions."
    icodp = 13
    name = "2nd order polynomial in 2 dimensions"
    NL = 12

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0,     # Coefs for xr
                      0.0, 1.0, 0.0, 0.0, 0.0, 0.0,     # Coefs for yr
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the Polynomial Projection of 2nd order" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Projects 3d point with 2nd order polynomial projection."
        x, y, z = c3d[:3]
        L = self.L
        xp = L[0]*x+L[1]*y+L[2]+L[3]*x**2+L[4] *y**2+L[5] *x*y
        yp = L[6]*x+L[7]*y+L[8]+L[9]*x**2+L[10]*y**2+L[11]*x*y
        return xp, yp, z      # The last coordinate (z) is not used


    def lsm23(self, fots):
        "Find 2nd order polynomial projection coefficients using least square."
        L = []
        for i in 0, 1:
            A, B = [], []
            for xg,yg,zg,xr,yr,zr,xyok,zok in fots:
                A.append([xg, yg, 1.0, xg**2, yg**2, xg*yg])
                if i == 0: B.append(xr)
                else     : B.append(yr)
            A = array(A)
            B = array(B)

            AT = transpose(A)
            A = matrixmultiply(AT, A)
            B = matrixmultiply(AT, B)
            try: a = solve_linear_equations(A, B)
            except LinAlgError as why:
#                print "Match2 polynomial solution failed: ", why
                return None, None, None
            L.extend(list(a))
        self.L = L
        return self.er(fots)


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the responsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
        else:                                   # Read coefficients from polynomial1 projection
            L = self.readCoefs(fr, 6)
            self.L = [L[0], L[1], L[2], 0.0, 0.0, 0.0,     # Coefs for xr
                      L[3], L[4], L[5], 0.0, 0.0, 0.0      # Coefs for yr
                     ]


    def write(self, fw):
        "Write the projection coefficients to a text file."
        fw.write("#Second order polynomial projection\n")
        fw.write("# x = L0 X + L1 Y + L2 + L3 X^2 + L4  Y^2 + L5  X Y\n")
        fw.write("# y = L6 X + L7 Y + L8 + L9 X^2 + L10 Y^2 + L11 X Y\n")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(6): fw.write("%27.20e    # L%d\n" % (self.L[i], i))
        fw.write("\n")
        for i in range(6, 12): fw.write("%27.20e    # L%d\n" % (self.L[i], i))


###############################################################################
###############################################################################


class NonCartesian(_Projection):
    """This class provides the machinery for a 2d-2d transformation, useful
    for the internal orientation in photogrammetry.
    It transforms x, y of the world coordinate system to a new non-cartesian
    coordinate system. The new system is defined by its origin in the world
    coordinate system, and 2 unit vectors, which show the direction of the
    2 axes (not necessarily orthogonal). The scale between the world coordinate
    system and this system is 1.
    """
    icodp = 21
    name = "Transformation to non-cartesian system in 2 dimensions"
    NL = 6

    def __init__(self, L=None):
        "Initialize the object with known coeffcients."
        if (L == None):
            self.L = [0.0, 0.0,     # Origin
                      1.0, 0.0,     # Unit vector for "x" axis
                      0.0, 1.0,     # Unit vector for "Y" axis
                     ]
        else:
            assert len(L) == self.NL, "There should be exactly %d coefficients for the non-cartesian transfornmatin in 2 dimensions" % self.NL
            self.L = L[:]


    def project(self, c3d):
        "Transforms 3d point to non-cartesian system."
        x, y, z = c3d[:3]
        L = self.L
        x -= L[0]
        y -= L[1]
#        linEq2 (da.x, db.x, self.x, da.y, db.y, self.y)
        xp, yp = linEq2 (L[2], L[4], x, L[3], L[5], y)     #We do not expect error here, since intersection was successful
        return xp, yp, z      # The last coordinate (z) is not used


    def from4(self, ca, cb, cc, cd, align=False):
        """Compute the coefficients using 4 points.

        The first 2 points define the x-axis and the last 2 points define
        the y-axis. The origin is the intersection of the points.
        Returns False and error message if unsuccesful and True and blank text
        if it is successful."""
        if thanNear2(ca, cb): return False, "The 2 x-axis definition points are identical"
        if thanNear2(cc, cd): return False, "The 2 y-axis definition points are identical"
        cor = thanSegSeg(ca, cb, cc, cd)
        if cor is None: return False, "The 2 axes do not intersect (without extension)"
        tab = cb[0]-ca[0], cb[1]-ca[1]
        t = hypot(tab[0], tab[1])
        tab = tab[0]/t, tab[1]/t
        tcd = cd[0]-cc[0], cd[1]-cc[1]
        t = hypot(tcd[0], tcd[1])
        tcd = tcd[0]/t, tcd[1]/t
        if align:
            if tab[0]*1+tab[1]*0 < 0.0: tab = -tab[0], -tab[1]  #Make x-axis to the about the same direction as the world x-axis
            tabn = -tab[1], tab[0]    #Normal to tab
            if tcd[0]*tabn[0]+tcd[1]*tabn[1] < 0.0: tcd = -tcd[0], -tcd[1] #Make the system positive (standard)
        self.L = [cor[0], cor[1], tab[0], tab[1], tcd[0], tcd[1]]
        return True, ""


    def from4old(self, ca, cb, cc, cd, align=False):
        """Compute the coefficients using 4 points.

        The first 2 points define the x-axis and the last 2 points define
        the y-axis. The origin is the intersection of the points.
        Returns False and error message if unsuccesful and True and blank text
        if it is successful."""
        #from p_gvec import Vector2
        import p_ggen
        Vector2 = p_ggen.Null
        if thanNear2(ca, cb): return False, "The 2 x-axis definition points are identical"
        if thanNear2(cc, cd): return False, "The 2 y-axis definition points are identical"
        cor = thanSegSeg(ca, cb, cc, cd)
        if cor is None: return False, "The 2 axes do not intersect (without extension)"
        tab = (Vector2(cb[0], cb[1])-Vector2(ca[0], ca[1])).unit()
        tcd = (Vector2(cd[0], cd[1])-Vector2(cc[0], cc[1])).unit()
        if align:
            if tab*Vector2(1, 0) < 0.0: tab = -tab    #Make x-axis to the about the same direction as the world x-axis
            if tcd*tab.normal() < 0.0: tcd = -tcd     #Make the system positive (standard)
        self.L = [cor[0], cor[1], tab.x, tab.y, tcd.x, tcd.y]
        return True, ""


    def read(self, fr, skipicod=False):
        """Reads the coefficients from an opened text file.

        It is the reponsibility of the caller to catch any exceptions."""
        if skipicod: ic = self.icodp
        else:        ic = self.readIcod(fr)
        if ic == self.icodp:
            self.L = self.readCoefs(fr, self.NL)
        else:                                   # Read coefficients from polynomial1 projection
            raise ValueError("Projection code in file is wrong")   # Accept polynomial as a first approximation


    def write(self, fw):
        "Write the projection coefficients to a text file."
        fw.write("#%s\n" % self.name)
        fw.write("# x' = X - L0\n")
        fw.write("# y' = Y - L1\n")
        fw.write("# x = L2 x' + L3 y'\n")
        fw.write("# y = L4 x' + L5 y'\n")
        fw.write("\n%2d                             # ThanCad Projection code\n\n" % self.icodp)
        for i in range(6): fw.write("%27.20e    # L%d\n" % (self.L[i], i))


if __name__ == "__main__":
    print(__doc__)
