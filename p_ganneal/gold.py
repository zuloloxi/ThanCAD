from math import fabs
import p_ggen


def goldSect(func, cka=0.0, ckb=1.0, eps=None, prt2=p_ggen.doNothing):
    "Golden section minimisation."
    assert ckb > cka
    t = 0.6180339887  # t= (sqrt(5.)-1.)/2. : αριΘΜΟΣ ΧΡΥΣΗΣ ΤΟΜΗΣ
    if eps is None: eps = (ckb-cka)/100.0
    sfa = func(cka)
    sf = func(ckb)
    ckx1 = cka + (ckb-cka) / 4.0; sx1 = func(ckx1)
    ckx2 = ckb - (ckb-cka) / 3.0; sx2 = func(ckx2)
    telx1 = False
    prt2(cka,  sfa)
    prt2(ckx1, sx1)
    prt2(ckx2, sx2)
    prt2(ckb,  sf)

#-----ΜΕΘΟΔΟΣ ΧΡΥΣΗΣ ΤΟΜΗΣ

    while fabs(ckx2-ckx1) > eps:
        if sx2 < sx1:
            cka = ckx1
            ckx1 = ckx2
            ckx2 = t*ckx1 + (1.0-t)*ckb
            sx1  = sx2
            sx2 = func(ckx2)
            prt2(ckx2, sx2)
            telx1 = False
        else:
            ckb  = ckx2
            ckx2 = ckx1
            ckx1 = t*ckx2 + (1.0-t)*cka
            sx2  = sx1
            sx1 = func(ckx1)
            prt2(ckx1, sx1)
            telx1 = True

#-----βρέΘΗΚΕ ΤΟ ΕΛΑΧΙΣΤΟ

    if sx1 < sx2:
        if not telx1: sx1 = func(ckx1)
        ck = ckx1
        sf = sx1
    else:
        if telx1:     sx2 = func(ckx2)
        ck = ckx2
        sf = sx2
    prt2(ck, sf)
    return ck


def test():
    "Find the minimum of f(x)."
    from math import fabs, sin, pi
    def prt2(x, v): print("%8.4f  %8.4f" % (x, v))
    def f(x): return (x-1)**3
    goldSect(f, cka=0.0, ckb=2*pi, prt2=prt2)

if __name__ == "__main__": test()
