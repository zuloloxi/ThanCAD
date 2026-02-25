import sys
from p_gfil import Datlin

def openFiles():
    "Opens the files for reading and writing."
    print
    print
    print " BDIAG 1.0 (April, 14, 2004) - ..."
    print "------------------------------------------------------------------------"
    print "ASPAITE - Department of Construction Engineering"
    print "Diploma Thesis: Mega Maria"
    print "                Xenakis Mathaios"
    print "Professor A.A. Stamos"
    print
    print
    print 'The program reads a data file with suffix ".dat" and writes the results'
    print 'into a file with suffix ".dxf". The prefix is given by the user.'
    print 'For example if the user gives prefix "road" the program opens the'
    print 'following files:'
    print
    print 'road.dat    : Input file'
    print 'road.dxf    : Output file'
    print
    while 1:
        print
        pr = raw_input("Enter prefix : ")
	pr = pr.strip()
	if pr == "": sys.exit()

        try:                 fr = file(pr+".dat")
	except IOError, why: print pr+".dat:", why; continue
        return fr
    
def datAll(fr):
    "Reads the loads."
    fr = Datlin(fr)
    tit = fr.datRawline()
    fr.datCom("BEAM LENGTH")
    blen = fr.datFloatR(0.0, 1000.0)
    fr.datCom("BEAM STEP")
    bstep = fr.datFloatR(0.0, 1000.0)

    loads = []
    while fr.datLin(failoneof=False):
        if fr.datComC("FORCE", fail=False):
            fr.datComC("F1", fail=False)
            f1 = fr.datFloat()
            if fr.datComC("X1", fail=False): x1 = fr.datFloatR(0.0, blen)
            else:                            x1 = 0.0
            x2 = None
            loads.append(("FORC", f1, x1))
        elif fr.datComC("UNIFORM", fail=False):
            fr.datComC("F1", fail=False)
            f1 = fr.datFloat()
            if fr.datComC("X1", fail=False): x1 = fr.datFloatR(0.0, blen)
            else:                            x1 = 0.0
            if fr.datComC("X2", fail=False): x2 = fr.datFloatR(0.0, blen)
            else:                            x2 = blen
            loads.append(("UNIF", f1, x1, x2))
        elif fr.datComC("TRIANGULAR", fail=False):
            if fr.datComC("F2", fail=False):
                f2 = fr.datFloat()
                f1 = 0.0
            else:
                fr.datComC("F1", fail=False)
                f1 = fr.datFloat()
                f2 = 0.0
            if fr.datComC("X1", fail=False): x1 = fr.datFloatR(0.0, blen)
            else:                           x1 = 0.0
            if fr.datComC("X2", fail=False): x2 = fr.datFloatR(0.0, blen)
            else:                           x2 = blen
            loads.append(("TRAP", f1, f2, x1, x2))
        elif fr.datComC("TRAPEZOIDAL", fail=False):
            fr.datComC("F1")
            f1 = fr.datFloat()
            fr.datComC("F2")
            f2 = fr.datFloat()
            if fr.datComC("X1", fail=False): x1 = fr.datFloatR(0.0, blen)
            else:                            x1 = 0.0
            if fr.datComC("X2", fail=False): x2 = fr.datFloatR(0.0, blen)
            else:                            x2 = blen
            loads.append(("TRAP", f1, f2, x1, x2))
        elif fr.datComC("MOMENT", fail=False):
            f1 = fr.datFloat()
            if fr.datComC("X1", fail=False): x1 = fr.datFloatR(0.0, blen)
            else:                            x1 = 0.0
            x2 = None
            loads.append(("MOME", f1, x1))
        else:
            fr.er("FORCE, UNIFORM, TRIANGULAR or TRAPEZOIDAL was expected.")

        t = fr.datStr(failoneol=False)
        if t != None: fr.er("'"+t+"' was found when nothing was expected.")

        if x1<0.0 or x1>blen: fr.er(str(x1)+": X1 should be 0.0 < X1 <"+str(blen))
        if x2 != None:
            if x2<0.0 or x1>blen: fr.er(str(x1)+": X2 should be 0.0 < X2 <"+str(blen))
            if x2<=x1: fr.er(str(x2)+": X2 should be X2 > X1.")
    return tit, blen, bstep, loads
