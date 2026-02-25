# -*- coding: iso-8859-7 -*-
"Solution of system o linear equations module."
from math import fabs


def lineq(A, B):
    "ΕΠΙΛΥΣΗ ΓΡΑΜΜΙΚΟΥ ΣΥΣΤΗΜΑΤΟΣ ΜΕ ΤΗ ΜΕΘΟΔΟ GAUSS ΜΕ MEPIKH ΟΔΗΓΗΣΗ"
#---1η ΦΑΣΗ: ΤΡΙΓΩΝΟΠΟΙΗΣΗ ΜΗΤΡΩΟΥ----------------------------------------
    n = len(A)
    for j in xrange(n):
        vmax = 0.0
        for i in xrange(j, n): #ΒΡΕΣ ΕΞΙΣΩΣΗ ΜΕ ΜΕΓΙΣΤΟ A(I,J) ΓΙΑ I = J..N
            if fabs( A[i][j] ) > vmax:
                vmax = fabs( A[i][j] )
                imax = i
        if vmax == 0:
            raise ZeroDivisionError, 'Linear system of equations is not soluble'
#-----H ΕΞΙΣΩΣΗ ΒΡΕΘΗΚΕ. ΑΝΤΙΚΑΤΕΣΤΗΣΕ ΤΗΝ ΕΞΙΣΩΣΗ ΙΜΑΧ ΜΕ ΤΗΝ ΕΞΙΣΩΣΗ J
        if imax != j:           # ΧΡΕΙΑΖΕΤΑΙ ΑΝΤΙΚΑΤΑΣΤΑΣΗ;
            for k in xrange(j, n):
                A[imax][k], A[j][k] = A[j][k], A[imax][k]
            B[j], B[imax] = B[imax], B[j]
#-----ΠΡΟΧΩΡΗΣΕ ΣΤΗΝ ΑΠΑΛΟΙΦΗ GAUSS
        for i in xrange(j+1, n):      # ΒΡΟΧΟΣ ΟΛΩΝ ΤΩΝ ΕΠΟΜΕΝΩΝ ΕΞΙΣΩΣΕΩΝ
            if A[i][j] != 0:          # ΑΝ ΕΙΝΑΙ ΗΔΗ 0 ΔΕΝ ΧΡΕΙΑΖΕΤΑΙ ΑΠΑΛΟΙΦΗ
                cc = A[i][j] / A[j][j]
                for k in xrange(j, n):
                    A[i][k] -= cc * A[j][k]
                B[i] -= cc * B[j]

#---2η ΦΑΣΗ: ΛΥΣΗ ΤΡΙΓΩΝΟΠΟΙΗΜΕΝΟΥ ΣΥΣΤΗΜΑΤΟΣ------------------------------
    for i in xrange(n-1, -1, -1):
        for j in xrange(i+1, n):
            B[i] -= A[i][j] * B[j]
        B[i] /= A[i][i]


if __name__ == "__main__":
    print __doc__
