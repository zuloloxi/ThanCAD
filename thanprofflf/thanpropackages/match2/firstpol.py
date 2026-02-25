# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (www.gnu.org/licenses/gpl.html).
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################

"""\
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

This is the professional part of ThanCad which is initially commercial.

March 8, 2010
1. Check polfirst with the second moments not central.
       result is worse (2010_03_08)
2. Check polfirst with the second moments not central and higher normalized.
       result is worse (2010_03_08)
3. Make more equations using also similarity (centroid is enforced,
   length is enforced, rotation should be somehow enforced).
4. Use one ICP with 2d polynomials (simplest more robust) just after
   the moments.
"""


from math import sqrt, fabs, hypot
from itertools import izip
from p_gnum import (array, matrixmultiply, transpose, solve_linear_equations,
                    LinAlgError, zeros, Float)
from p_gmath import dfridr
from cline import Cline

enhance_with_sim = False   # Enhance first approximation, after computing it with moments, applying a similarity transformation
relative_moments = False   # Compute momenets wigher than 2, relative to the second moment (standard deviation)
test_anal = True           # Check the analytical derivative if it is equal to the numeric derivative
vis_error = True           # Visualize and compute errors
elengths = (True, );      nmoms = xrange(3, 4)  #Number of moments and length equation to apply
#elengths = (False, True); nmoms = xrange(3, 9)  #Number of moments and length equation to apply

test_anal = test_anal and vis_error   #Only works if compute error is on


def epil(proj, gps, rel, disint, tra1):
    "Find the best values with iterations for xg and yg."
    if vis_error:
        global fww
        fn = proj[0].parent / proj[0].namebase + "erioan.txt"
        fww = open(fn, "w")
        chs = []
    for elength in elengths:
        for nmom in nmoms:
            Lbest, ch = epil1(proj, gps, rel, disint, tra1, nmom, elength)
            if vis_error: chs.append(ch)
            if enhance_with_sim: Lbest = trysimilarity(gps, rel, Lbest)
    if vis_error:
        fww.close()
        import thanvar, p_gchart
        p_gchart.viswin(thanvar.thanfiles.ThanCad[2], *chs)
    return Lbest


def epil1(proj, gps, rel, disint, tra1, nmom, elength):
    "Find the best values with iterations for xg and yg."
    gpsx = [xg for (xg, yg, zg, _) in gps]
    gpsy = [yg for (xg, yg, zg, _) in gps]
    L1 = tra1.L[:]
    A, B = mat(gpsx, gpsy, rel, L1, nmom, elength)
    er1 = sqrt(sum(b**2 for b in B)/len(B))
    erbest, Lbest = er1, L1[:]
    L = L1[:]
    erpp = 1.0e30
    erp = er1
    for it in xrange(10):
        dcmin, dcmax = lsm(A, B, L)
        A, B = mat(gpsx, gpsy, rel, L, nmom, elength)
        er = sqrt(sum(b**2 for b in B)/len(B))
        print "initial er=%10.5f iters %02d     er=%10.5f" % (er1, it+1, er)
        if er < erbest: erbest, Lbest = er, L[:]
        if erp <= erpp and er <= erp and erp-er < 0.001: break
        erpp, erp = erp, er
    else:
        print "Warning: max iterations before convergence."
    print "initial er=%10.5f iters %02d bester=%10.5f" % (er1, it+1, erbest)
    makesure(gpsx, rel, Lbest[:3])
    makesure(gpsy, rel, Lbest[3:6])
    makesurelen(gpsx, gpsy, rel, Lbest)

    ch = None
    if vis_error:
        er1 = errorIoannidis(Lbest, gps, rel)
        fww.write("moments:%d :length:%r :error=:%.1f\n" % (nmom, elength, er1))
        ch = vismom("moments=%d length=%r target=red, similarity=white,polynomial=green,error=%.1f" % (nmom, elength, er1), L1, Lbest, gps, rel)
        dxfmom(proj, nmom, elength, L1, L, gps, rel)
    return Lbest, ch


def trysimilarity(gps, rel, L):
    "Try similarity AFTER polynomial."
    import thanvar, p_gchart
    tit = "target=red   pol=green   new=blue"
    ch = p_gchart.ThanChart(tit)
    gps.add2chart(ch, color="red")
    gps1 = []
    for xr, yr, _, _ in rel:
        xg = L[0]*xr + L[1]*yr + L[2]
        yg = L[3]*xr + L[4]*yr + L[5]
        gps1.append((xg, yg, 0.0))
    gps1 = Cline(gps1)
    gps1.add2chart(ch, color="green")
    import firstsim
    tra1, er, erh = firstsim.matchCentroid(gps, gps1, iazim=0, disint=0.2, disrange=150)
    gps2 = []
    for xr, yr, _, _ in gps1:
        xg, yg, _ = tra1.calc2d((xr, yr, 0.0))
        gps2.append((xg, yg, 0.0))
    gps2 = Cline(gps2)
    gps2.add2chart(ch, color="blue")
    p_gchart.viswin(thanvar.thanfiles.ThanCad[2], ch)
    return chain(L, [tra1.a[2], tra1.a[3], tra1.a[0], -tra1.a[3], tra1.a[2], tra1.a[1]])


def chain(L, M):
        """Chain this transformation and another; first current then the other.

        xp = L[0]*x+L[1]*y+L[2]
        yp = L[3]*x+L[4]*y+L[5]
        xn = M[0]*xp+M[1]*yp+M[2] = M[0] * {L[0]*x+L[1]*y+L[2]} + M[1] *  {L[3]*x+L[4]*y+L[5]} + M[2] =
             M[0]*L[0]*x + M[0]*L[1]*y + M[0]*L[2] + M[1]*L[3]*x + M[1]*L[4]*y + M[1]*L[5] + M[2]
             {M[0]*L[0] + M[1]*L[3]}*x + {M[0]*L[1] + M[1]*L[4]}*y + {M[0]*L[2] + M[1]*L[5] + M[2]}
        yn = M[3]*xp+M[4]*yp+M[5]
        """
        LL = [None]*6
        LL[0] = M[0]*L[0] + M[1]*L[3]
        LL[1] = M[0]*L[1] + M[1]*L[4]
        LL[2] = M[0]*L[2] + M[1]*L[5] + M[2]

        LL[3] = M[3]*L[0] + M[4]*L[3]
        LL[4] = M[3]*L[1] + M[4]*L[4]
        LL[5] = M[3]*L[2] + M[4]*L[5] + M[5]
        return LL



def makesure(gpsc, rel, L):
    "Make sure that the moments are OK."
    amg1 = sum(gpsc)/len(gpsc)
    amg2 = rootn(sum((xg-amg1)**2 for xg in gpsc)/len(gpsc), 2)
    amg3 = rootn(sum((xg-amg1)**3 for xg in gpsc)/len(gpsc), 3)
    amg4 = rootn(sum((xg-amg1)**4 for xg in gpsc)/len(gpsc), 4)
    xgt = [L[0]*xr+L[1]*yr+L[2] for xr, yr, _, _ in rel]
    amr1 = sum(xgt)/len(rel)
    amr2 = rootn(sum((xg-amr1)**2 for xg in xgt)/len(rel), 2)
    amr3 = rootn(sum((xg-amr1)**3 for xg in xgt)/len(rel), 3)
    amr4 = rootn(sum((xg-amr1)**4 for xg in xgt)/len(rel), 4)
    print "polfirst:makesure():amg?=%15.3f%15.3f%15.3f%15.3f" % (amg1, amg2, amg3, amg4)
    print "polfirst:makesure():amr?=%15.3f%15.3f%15.3f%15.3f" % (amr1, amr2, amr3, amr4)

def makesurelen(gpsx, gpsy, rel, L):
    "Make sure that the lengths are OK."
    print "polfirst:makesure:lenr=%15.3f" % (plen(rel, L[0], L[1], L[2], L[3], L[4], L[5]), )
    print "polfirst:makesure:leng=%15.3f" % (alen(gpsx, gpsy), )


def mat(gpsx, gpsy, rel, L, nmom, elength):
    "Compute the least square matrices; use nmom moments for LSM."
    neq = 2*nmom
    if elength: neq += 1
    A = zeros((neq, 6), Float)
    B = zeros((neq, ), Float)
    central1 = True
    if not relative_moments:
        mat1(gpsx, rel, L[:3], nmom, A, B, 0, 0)
        mat1(gpsy, rel, L[3:], nmom, A, B, nmom, 3)
        if test_anal:                                #Only for test of the analytical derivatives
            mom = 1
            compareDerMom1(polmom, analDerMom1, mom, rel, L, fww)
            for mom in xrange(2, nmom+1):
                compareDerMom1(polmomroot, analDerMomroot, mom, rel, L, fww)
    else:
        mat3(gpsx, rel, L[:3], nmom, A, B, 0, 0)
        mat3(gpsy, rel, L[3:], nmom, A, B, nmom, 3)
    if elength:
        matCoeflen(A, B, 2*nmom, gpsx, gpsy, rel, L)
        if test_anal: compareDerLen(rel, L, fww)     #Only for test of the analytical derivatives

#    print "polfirst:lenr=%15.3f" % (plen(rel, L[0], L[1], L[2], L[3], L[4], L[5]), )
#    print "polfirst:leng=%15.3f" % (alen(gpsx, gpsy), )
    return A, B


def mat1(gpsc, rel, L, nmom, A, B, id_, jd):
    "Assemble matrices."
    amg1 = sum(gpsc)/len(gpsc)
    matCoef(A, B, id_, jd, polmom, 1, rel, L, amg1)
    for i in xrange(2, nmom+1):
        amg = rootn(sum((xg-amg1)**i for xg in gpsc)/len(gpsc), i)
        matCoef(A, B, id_+i-1, jd, polmomroot, i, rel, L, amg)


def mat3(gpsc, rel, L, nmom, A, B, id_, jd):
    "Assemble matrices; use the relative moments."
    amg1 = sum(gpsc)/len(gpsc)
    matCoef(A, B, id_, jd, polmom, 1, rel, L, amg1)
    i = 2
    amg2 = rootn(sum((xg-amg1)**i for xg in gpsc)/len(gpsc), i)
    matCoef(A, B, id_+i-1, jd, polmomroot, i, rel, L, amg2)
    for i in xrange(3, nmom+1):
        amg = rootn(sum(((xg-amg1)/amg2)**i for xg in gpsc)/len(gpsc), i)
        matCoef(A, B, id_+i-1, jd, polmomrootan, i, rel, L, amg)


def rootn(x, n):
    "Compute the nth root with sign."
    if x == 0.0: return x
    neg = x < 0.0
    x = fabs(x)**(1.0/n)
    if neg: x = -x
    return x


def matCoef(A, B, i, jd, polx, mom, rel, L, amg):
    "Μέτρηση που αντιστοιχεί σε γραμμή i και έχει να κάνει με συντετγαμένες 2 σημείων ja, jb και fun η συνάρτηση της μέτρησης."
    a, b, c = L
    def f(a): return polx(mom, rel, a, b, c)
    da, err = dfridr(f, a, 0.1)
    def f(b): return polx(mom, rel, a, b, c)
    db, err = dfridr(f, b, 0.1)
    def f(c): return polx(mom, rel, a, b, c)
    dc, err = dfridr(f, c, 0.1)
#   A[i,*] = 0.0    for other languages (not needed in Python. see zeros() above)
    A[i,jd+0] = da
    A[i,jd+1] = db
    A[i,jd+2] = dc
#   print "polfirst:matCoef:amg, f(c)=", amg, f(c)
    B[i] = amg - f(c)


def matCoeflen(A, B, i, gpsx, gpsy, rel, L):
    "Ensure that the lengths of the 2 lines are the same."
    ax, bx, cx, ay, by, cy = L
    def f(ax): return plen(rel, ax, bx, cx, ay, by, cy)
    dax, err = dfridr(f, ax, 0.1)
    def f(bx): return plen(rel, ax, bx, cx, ay, by, cy)
    dbx, err = dfridr(f, bx, 0.1)
    def f(cx): return plen(rel, ax, bx, cx, ay, by, cy)
    dcx, err = dfridr(f, cx, 0.1)
    def f(ay): return plen(rel, ax, bx, cx, ay, by, cy)
    day, err = dfridr(f, ay, 0.1)
    def f(by): return plen(rel, ax, bx, cx, ay, by, cy)
    dby, err = dfridr(f, by, 0.1)
    def f(cy): return plen(rel, ax, bx, cx, ay, by, cy)
    dcy, err = dfridr(f, cy, 0.1)

#   A[i,*] = 0.0    for other languages (not needed in Python. see zeros() above)
    A[i,0] = dax
    A[i,1] = dbx
    A[i,2] = dcx
    A[i,3] = day
    A[i,4] = dby
    A[i,5] = dcy
#   print "polfirst:matCoef:amg, f(c)=", amg, f(c)
    B[i] = alen(gpsx, gpsy) - f(cy)


def compareDerLen(rel, L, fwc):
    "Ensure that the length derivatives are the same: analytical and numerical."
    ax, bx, cx, ay, by, cy = L
    def f(ax): return plen(rel, ax, bx, cx, ay, by, cy)
    dax, err = dfridr(f, ax, 0.1)
    def f(bx): return plen(rel, ax, bx, cx, ay, by, cy)
    dbx, err = dfridr(f, bx, 0.1)
    def f(cx): return plen(rel, ax, bx, cx, ay, by, cy)
    dcx, err = dfridr(f, cx, 0.1)
    def f(ay): return plen(rel, ax, bx, cx, ay, by, cy)
    day, err = dfridr(f, ay, 0.1)
    def f(by): return plen(rel, ax, bx, cx, ay, by, cy)
    dby, err = dfridr(f, by, 0.1)
    def f(cy): return plen(rel, ax, bx, cx, ay, by, cy)
    dcy, err = dfridr(f, cy, 0.1)
    anum = dax, dbx, dcx, day, dby, dcy
    anal = analDerLen(rel, L)
    fwc.write("Length anal: %15.3f%15.3f%15.3f%15.3f%15.3f%15.3f\n" % anal)
    fwc.write("        num: %15.3f%15.3f%15.3f%15.3f%15.3f%15.3f\n" % anum)


def compareDerMom1(polx, derpolx, mom, rel, L, fwc):
    "Ensure that the derivatives of 1st moment are the same: analytical and numerical."
    ax, bx, cx, ay, by, cy = L

    a, b, c = L[:3]
    def f(a): return polx(mom, rel, a, b, c)
    da, err = dfridr(f, a, 0.1)
    def f(b): return polx(mom, rel, a, b, c)
    db, err = dfridr(f, b, 0.1)
    def f(c): return polx(mom, rel, a, b, c)
    dc, err = dfridr(f, c, 0.1)
    dax, dbx, dcx = da, db, dc

    a, b, c = L[3:]
    def f(a): return polx(mom, rel, a, b, c)
    da, err = dfridr(f, a, 0.1)
    def f(b): return polx(mom, rel, a, b, c)
    db, err = dfridr(f, b, 0.1)
    def f(c): return polx(mom, rel, a, b, c)
    dc, err = dfridr(f, c, 0.1)
    day, dby, dcy = da, db, dc

    anum = dax, dbx, dcx, day, dby, dcy
    anal = derpolx(mom, rel, L)
    fwc.write(" mom%2d anal: %15.3f%15.3f%15.3f%15.3f%15.3f%15.3f\n" % ((mom,)+anal))
    fwc.write("        num: %15.3f%15.3f%15.3f%15.3f%15.3f%15.3f\n" % anum)


def analDerLen(rel, L):
    "Compute the analytical derivatives of length with respect to the unknowns."
    a, b, c, d, e, f = L
    xr1, yr1, _, _ = rel[0]
    da = db = dc = dd = de = df = 0.0
    for i in xrange(1, len(rel)):
        xr2, yr2, _, _ = rel[i]
        dx = xr2 - xr1
        dy = yr2 - yr1
        L2 = hypot(a*dx+b*dy, d*dx+e*dy)
        da += (a*dx+b*dy)*dx/L2
        db += (a*dx+b*dy)*dy/L2
        dd += (d*dx+e*dy)*dx/L2
        de += (d*dx+e*dy)*dy/L2
        xr1, yr1 = xr2, yr2
    return da, db, dc, dd, de, df


def analDerMom1(mom, rel, L):
    "Compute the analytical derivatives of first moment with respect to the unknowns."
    xm = ym = 0.0
    for xr, yr, _, _ in rel:
        xm += xr
        ym += yr
    xm /= len(rel)
    ym /= len(rel)
    da = dd = xm
    db = de = ym
    dc = df = 1.0
    return da, db, dc, dd, de, df


def analDerMomroot(mom, rel, L):
    "Compute the analytical derivatives of normalized central moment of higher order, with respect to the unknowns."
    a, b, c, d, e, f = L
    mom1x = polmom(1, rel, a, b, c)
    mom1y = polmom(1, rel, d, e, f)
    momrootx = polmomroot(mom, rel, a, b, c)
    momrooty = polmomroot(mom, rel, d, e, f)
    xm, ym, _, _, _, _ = analDerMom1(1, rel, L)
    da = db = dc = dd = de = df = 0.0
    for xr, yr, _, _ in rel:
        da += (a*xr+b*yr+c-mom1x)**(mom-1)*(xr-xm)
        db += (a*xr+b*yr+c-mom1x)**(mom-1)*(yr-ym)
        dd += (d*xr+e*yr+f-mom1y)**(mom-1)*(xr-xm)
        de += (d*xr+e*yr+f-mom1y)**(mom-1)*(yr-ym)
    da *= momrootx**(1-mom)/len(rel)
    db *= momrootx**(1-mom)/len(rel)
    dd *= momrooty**(1-mom)/len(rel)
    de *= momrooty**(1-mom)/len(rel)
    return da, db, dc, dd, de, df


def plen(rel, ax, bx, cx, ay, by, cy):
    "Find the length for first order polynomial in 2D."
    xr, yr, _, _ = rel[0]
    xg1 = ax*xr + bx*yr + cx
    yg1 = ay*xr + by*yr + cy
    s = 0.0
    for i in xrange(1, len(rel)):
        xr, yr, _, _ = rel[i]
        xg = ax*xr + bx*yr + cx
        yg = ay*xr + by*yr + cy
        s += hypot(xg-xg1, yg-yg1)
        xg1, yg1 = xg, yg
    return s


def alen(gpsx, gpsy):
    "Find the real length of the curve."
    xg1 = gpsx[0]
    yg1 = gpsy[0]
    s = 0.0
    for i in xrange(1, len(gpsx)):
        xg = gpsx[i]
        yg = gpsy[i]
        s += hypot(xg-xg1, yg-yg1)
        xg1, yg1 = xg, yg
    return s


def polmom(mom, rel, a, b, c):
    "Find the moment of rank mom for first order polynomial in 2D."
    s = 0.0
    for xr, yr, _, _ in rel:
        s += (a*xr + b*yr + c)**mom
    s /= len(rel)
    return s


def polmomroot(mom, rel, a, b, c):
    "Find the moment normalized to meters of rank mom for first order polynomial in 2D."
    am1 = polmom(1, rel, a, b, c)
    s = 0.0
    for xr, yr, _, _ in rel:
        s += (a*xr + b*yr + c - am1)**mom
    s /= len(rel)
    return rootn(s, mom)


def polmomrootan(mom, rel, a, b, c):
    "Find the moment normalized to meters of rank mom for first order polynomial in 2D; relative."
    am1 = polmom(1, rel, a, b, c)
    am2 = polmomroot(2, rel, a, b, c)
    s = 0.0
    for xr, yr, _, _ in rel:
        s += ((a*xr + b*yr + c - am1)/am2)**mom
    s /= len(rel)
    return rootn(s, mom)


def lsm(A, B, L):
    "Least square method."
    AT = transpose(A)
    A = matrixmultiply(AT, A)
    B = matrixmultiply(AT, B)
    try: a = solve_linear_equations(A, B)
    except LinAlgError, why:
         return None
    dcmax = -1e30
    dcmin = 1e30
    i = 0
    for i in xrange(len(B)):
        if a[i] > dcmax: dcmax = a[i]
        if a[i] < dcmin: dcmin = a[i]
        L[i] += a[i]
    return dcmin, dcmax


def errorIoannidis(L, gps, rel):
    "The error between the first approximation and the GPS line."
    from icp2 import icp2, erricp
    gps2 = []
    for xr, yr, _, _ in rel:
        xg = L[0]*xr + L[1]*yr + L[2]
        yg = L[3]*xr + L[4]*yr + L[5]
        gps2.append((xg, yg, 0.0))
    gps2 = Cline(gps2)
    gr = icp2(gps, gps2, disint=0.2, disrange=150.0)
    if gr == None:
        prg("ICP failed whlie computin first approximation error in polfirst.py")
        return -1.0
    er1, erh = erricp(gr)
    return er1


def dxfmom(proj, nmom, elength, L1, L, gps, rel, all=False):
    "Write monents to dxf file."
    from p_gdxf import ThanDxfPlot
    fn = proj[0].parent / proj[0].namebase + "_mom%d_%s.dxf" % (nmom, ("none", "leng")[elength])
    fw = open(fn, "w")
    dxf = ThanDxfPlot()
    dxf.thanDxfPlots1(fw)
    defDxf(dxf)
    gps.add2dxf(dxf, layer="target")
    if all:
        rel.add2dxf(dxf, layer="0")
    gps1 = []
    for xr, yr, _, _ in rel:
        xg = L1[0]*xr + L1[1]*yr + L1[2]
        yg = L1[3]*xr + L1[4]*yr + L1[5]
        gps1.append((xg, yg, 0.0))
    gps1 = Cline(gps1)
    gps1.add2dxf(dxf, layer="similarity")
    gps2 = []
    for xr, yr, _, _ in rel:
        xg = L[0]*xr + L[1]*yr + L[2]
        yg = L[3]*xr + L[4]*yr + L[5]
        gps2.append((xg, yg, 0.0))
    gps2 = Cline(gps2)
    gps2.add2dxf(dxf, layer="polynomial")
    dxf.thanDxfPlot(0,0,99)


def defDxf(dxf):
    "Example of initial definition."

    dxf.thanDxfTableDef (' ', 0)

#---Line types

    dxf.thanDxfTableDef('LTYPE', 3)
    dxf.thanDxfCrLtype('CONTINUOUS', 'Solid Line',        ( ))
    dxf.thanDxfCrLtype('DOTR',       '.................', (0, -0.06))
    dxf.thanDxfCrLtype('DASHED2',    '- - - - - - - - -', (0.25, -0.125))

#---Text styles

    dxf.thanDxfTableDef ('STYLE', 1)
    dxf.thanDxfCrTstyle ('GRSTYLE', 'GRSIMPW')

#---Layers

    dxf.thanDxfTableDef('LAYER', 3)
    dxf.thanDxfCrLayer('target',     1, 'CONTINUOUS')
    dxf.thanDxfCrLayer('similarity', 7, 'CONTINUOUS')
    dxf.thanDxfCrLayer('polynomial', 4, 'CONTINUOUS')

    dxf.thanDxfTableDef ('ENTITIES', 1)


def vismom(tit, L1, L, gps, rel, all=False):
    "Visualize the results."
    import p_gchart
    ch = p_gchart.ThanChart(tit)
    gps.add2chart(ch, color="red")
    if all:
        rel.add2chart(ch, color="yellow")
    gps1 = []
    for xr, yr, _, _ in rel:
        xg = L1[0]*xr + L1[1]*yr + L1[2]
        yg = L1[3]*xr + L1[4]*yr + L1[5]
        gps1.append((xg, yg, 0.0))
    gps1 = Cline(gps1)
    gps1.add2chart(ch, color="white")
    gps2 = []
    for xr, yr, _, _ in rel:
        xg = L[0]*xr + L[1]*yr + L[2]
        yg = L[3]*xr + L[4]*yr + L[5]
        gps2.append((xg, yg, 0.0))
    gps2 = Cline(gps2)
    gps2.add2chart(ch, color="green")
    return ch
