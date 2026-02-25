from p_gfil import Datlin

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
