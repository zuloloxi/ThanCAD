from math import pi, cos, sin, atan2, log10, fabs
from p_gmath import dpt

MET = pi/180.0


def rnumber(dxf, x,y,h,dn,t,nn):
    "Writes the number so that its last char is at position x, y."
    if nn < 0:
        ipack = "%d" % int(dn+0.5)
    else:
        f = ".%df" % nn
        ipack = f % dn
    tt = t * pi / 180.0
    cc = cos(tt)
    ss = sin(tt)
    n=len(ipack)
    tt=n*h
    dxf.thanDxfPlotSymbol(x-tt*cc,y-tt*ss,h,ipack,t)

#==========================================================================

def cross (dxf, xx, yy, h):
    "Plots a cross."
    hh = h * 0.5
    dxf.thanDxfPlot(xx-hh, yy,    3)
    dxf.thanDxfPlot(xx+hh, yy,    2)
    dxf.thanDxfPlot(xx,    yy-hh, 3)
    dxf.thanDxfPlot(xx,    yy+hh, 2)


def rectangle(dxf, x1, y1, x3, y3):
    "Plots a rectangle as a closed polyline."
    x = [x1, x3, x3, x1, x1]
    y = [y1, y1, y3, y3, y1]
    dxf.thanDxfPlotPolyline(x, y)

#===========================================================================

def elips1 (dxf, x, y, xf, yf, xc, yc, a, b, theta, idr, ic):
    r"""Draw an elipse approximating it with a polyline.
      implicit none
      real*8 x, y, xf, yf, xc, yc, a, b, theta             ! arguments
      integer*4 idr, ic                                    ! arguments     ! could be integer*2
      real*8 dpt                                           ! function
      external dpt
      real*8 pi, met                                       ! constants
      parameter (pi=3.14159265358979323d0, met = pi/180d0)
      integer*4 n, i     ! could be integer*2
      real*8 t, cost, sint, x1, y1, xa, ya, tha, thb, dthab, dth,
     &cosd, sind, cosx, sinx


c      y
c                                         theta = γωνία bay , δηλαδή η γωνία
c      ^                                          μεταξύ του άξονα ab και τον
c      |                                          άξονα xx
c      |                     _     b
c      |                  .      \
c      |               .        / .
c      |             /        /   .
c      |           .        /     .
c      |                  o      .
c      |         .      /
c      |         .    /        /
c      |         .  /       .
c      |          \ . . .
c      |        a
c      +--------------------------------------> x
c
c
c
c      y'
c
c      ^
c      |
c      |
c      |                .   -   .
c      |            /       |       \           c  = σημείο τομής αξόνων
c      |                    |                   ca = a
c      |       a |----------o----------| b      cb = b
c      |                    | c
c      |            \       |       /
c      |                .   _   .
c      |
c      +--------------------------------------> x'
c


c-----Αυτή η sr σχεδιάζει τόξο ελειψης:
c     x, y   : συντεταγμένες αρχικού σημείου του ελειπτικού τόξου
c     xf, yf : συντεταγμένες τελικού σημείου του ελειπτικού τόξου
c     xc, yc : συντεταγμένες της τομής του του κύριου και δευτερεύοντος
c              άξονα της έλειψης
c     a, b   : μήκος κύριου και δευετερεύοντος ημιάξονα
c     theta  : γωνία μεταξύ του κύριου άξονα και του αξονα συστηήματος x-x
c     idr    = 0 : θα σχεδιαστεί το τόξο κατά ανθωρολογιακή φορά
c            = 0 : θα σχεδιαστεί το τόξο κατά ωρολογιακή φορά
c     ic     = 2 : θα σχεδιαστεί γραμμή από το τρέχον σημείο που βρίσκεται
c                  η πένα του plotter μέχρι το πρώτο σημείο του ελειπ. τόξου
c     ic     = 3 : Δεν θα σχεδιαστεί γραμμή από το τρέχον σημείο που βρίσκεται
c                  η πένα του plotter μέχρι το πρώτο σημείο του ελειπ. τόξου
c
c     Ας σημειωθεί ότι η έλειψη που ορίζεται με τά xc,yc και a,b και theta
c     μπορεί να μην περνάει από τα σημεία x,y και xf,yf. Σε αυτήν την
c     περίπτωση τα σημεία x,y και xf,yf χρησιμοποιούνται για τον ορισμό
c     της γωνίας διευθύνσεως του αρχικού και τελικού σημείου αντίστοιχα.
      """

#---ΒΡΕΣ ΑΡΧΙΚΗ ΓΩΝΙΑ

    t = (theta - 180.0) * MET
    cost = cos(t)
    sint = sin(t)

    x1 = x - xc
    y1 = y - yc
    xa = cost * x1 + sint * y1
    ya = cost * y1 - sint * x1
    tha = atan2(ya/b, xa/a)

#---ΒΡΕΣ ΤΕΛΙΚΗ ΓΩΝΙΑ

    x1 = xf - xc
    y1 = yf - yc
    xa = cost * x1 + sint * y1
    ya = cost * y1 - sint * x1
    thb = atan2(ya/b, xa/a)

#---ΒΡΕΣ ΒΗΜΑ ΓΩΝΙΑΣ: default 20 ΜΟΙΡες, ΑΛΛΑ ΤΟΥΛΑΧΙΣΤΟΝ 4 ΒΗΜΑΤΑ

    dthab = thb - tha
    if idr != 0: dthab = 2.0 * pi - dthab
    dthab = dpt(dthab)

    dth = 20.0 * MET
    n = int(dthab/dth)
    if n < 4: n = 4
    n = n + 1                # Το πρώτο είναι για θ=tha

    dth = dthab / n
    if idr != 0: dth = -dth
    cosd = cos(dth)
    sind = sin(dth)

#---ΑΛΛΑΓΗ ΣΤΟ ΠΡΟΣΗΜΟ ΓΩΝΙΑΣ t

    sint = -sint

#---ΠΗΓΑΙΝΕ ΣΤΗΝ ΠΡΩΤΗ ΘΕΣΗ ΜΕ ic

    cosx = cos(tha)
    sinx = sin(tha)

    x1 = a * cosx
    y1 = b * sinx
    xa = xc + cost * x1 + sint * y1
    ya = yc + cost * y1 - sint * x1
    dxf.thanDxfPlot (xa, ya, ic)
    dxf.thanDxfPlotPolyVertex (xa, ya, 2)

#---ΕΠΟΜΕΝΑ ΒΗΜΑΤΑ

    for i in range(n):
        x1 = cosx * cosd - sinx * sind
        y1 = sinx * cosd + cosx * sind
        cosx = x1
        sinx = y1

        x1 = a * cosx
        y1 = b * sinx
        xa = xc + cost * x1 + sint * y1
        ya = yc + cost * y1 - sint * x1
        dxf.thanDxfPlotPolyVertex (xa, ya, 2)
    dxf.thanDxfPlotPolyVertex (0.0, 0.0, 999)

#====================================================================

def logax (dxf, xa,ya,pw,th,emin,emax,legend,escale):
    """Plots a logarithmic axis.

c      pw: paper width in cm. if negative, legend goes to the left
c     dpw: minimum distance in cm between two numbers on the axis
c      dx: the "distance" between logs of emin and emax, in log[user units]
c     ddx: minimum distance in log[user units] between two numbers on the axis
c
    """
    HS=0.20; HSL=0.30; DPW=1.0

    dx  = log10(emax/emin)
    ddx = DPW * dx/fabs(pw)
    escale = fabs(pw)/dx

    t = th * pi/180.0
    cost = cos(t)
    sint = sin(t)

    thn = th - 90.0
    t = thn * pi/180.0
    costn = cos(t)
    sintn = sin(t)

#---initial values

    al = log10(emax)
    k = int(al + 0.9999)
    if al < 0.0: k=k-1
    fct = 10.0 ** k

    xx = 10.0 ** (1.001 * ddx)
    anump = emin / xx
    n = 0
    an = [emax * xx]

#---first number (anump) for new fct

    endn = False
    while True:
        anum = anump/fct
        anum = int(anum) * fct
        while True:
            anum = anum + fct
            ddxn = log10(anum/anump)
            if (ddxn < ddx): continue   # go to 20

#-----------if too big gap between anump-anum try smaller fct.

            if ddxn >= 2.0*ddx:
                n=n+1
                if n >= len(an): an.append(anum)
                else:            an[n] = anum
                fct = fct * 0.1
                k = k - 1
                break       #go to 10

#-----------if numbers for current fct finished, get new fct or end.

            while log10(an[n]/anum) < ddx:
                if n <= 0: endn = True; break # go to 21
                anum = an[n]
                n = n - 1
                fct = fct * 10.0
                k = k + 1
                ddxn = log10(anum/anump)

#-----------plot the number

            if anum <= emax:  # go to 31
                dis = log10(anum/emin) * fabs(pw)/dx
#                disn = dsign(1.5 * HS, pw)
                disn = 1.5 * HS
                if pw < 0: disn = -disn

                xx = xa + (dis-0.5*HS)*cost + disn*costn
                yy = ya + (dis-0.5*HS)*sint + disn*sintn
                k1=-k
                if k == 0: k1=-1
                if pw > 0.0:
                    dxf.thanDxfPlotNumber(xx, yy, HS, anum, thn, k1)
                else:
                    rnumber(dxf, xx, yy, HS, anum, thn, k1)

#---------------plot line

                disn=HS
                if pw < 0: disn = -HS
                xx = xa + dis*cost
                yy = ya + dis*sint
                dxf.thanDxfPlot (xx, yy, 3)
                dxf.thanDxfPlot (xx+disn*costn, yy+disn*sintn, 2)
            anump = anum
        if endn: break    #go to 21

#---plot line - legend

    dxf.thanDxfPlot(xa, ya, 3)
    dxf.thanDxfPlot(xa+fabs(pw)*cost, ya+fabs(pw)*sint, 2)

    k = len(legend)
    dis = (fabs(pw) - k*HSL) * 0.5
    disn = 6.0*HS + 2.0*HSL
    if pw < 0.0: disn=-(disn-HSL)
    xx = xa + dis*cost + disn*costn
    yy = ya + dis*sint + disn*sintn
    dxf.thanDxfPlotSymbol(xx, yy, HSL, legend, th)
    return escale


def north(dxf, xc, yc, ssize, theta):
    "Plot the north symbol."

    def plota(a):
        "Plot a line."
        ipen = 3
        for i in range(0, len(a), 2):
            dx = a[i]  *aklp
            dy = a[i+1]*aklp
            xx1 = xc + (dx*cs - dy*ss)
            yy1 = yc + (dx*ss + dy*cs)
            dxf.thanDxfPlot(xx1, yy1, ipen)
            ipen = 2

    a = [           1.023020244608095e-01,   1.576180803996224e+00,
                    1.301631017509486e-02,   1.486895089710509e+00,
                   -2.548408326820490e-01,   1.486895089710509e+00,
                   -2.548408326820490e-01,   2.111895089710512e+00,
                    1.301631017509486e-02,   2.111895089710512e+00,
                    1.023020244608095e-01,   2.022609375424797e+00,
                    1.023020244608095e-01,   1.933323661139082e+00,
                    1.301631017509486e-02,   1.844037946853368e+00,
                   -2.548408326820490e-01,   1.844037946853368e+00,
                    1.301631017509486e-02,   1.844037946853368e+00,
                    1.023020244608095e-01,   1.754752232567653e+00,
                    1.023020244608095e-01,   1.576180803996224e+00,];
    b = [           1.767766952970221e-01,   1.767766952962581e-01,
                    7.071067811869242e-01,  -7.071067811869242e-01,
                   -1.767766952962581e-01,  -1.767766952970130e-01,
                   -7.071067811861786e-01,   7.071067811861786e-01,
                    1.767766952970221e-01,   1.767766952962581e-01,];
    c = [           3.774000000000000e-13,  -3.125000000003832e-01,
                    1.250000000000379e+00,  -3.820000000000000e-13,
                    3.729000000000000e-13,   3.124999999996191e-01,
                   -1.249999999999622e+00,  -3.820000000000000e-13,
                    3.774000000000000e-13,  -3.125000000003832e-01,];
    d = [          -1.767766952962535e-01,   1.767766952962672e-01,
                    7.071067811869290e-01,   7.071067811861697e-01,
                    1.767766952970175e-01,  -1.767766952970130e-01,
                   -7.071067811861739e-01,  -7.071067811869333e-01,
                   -1.767766952962535e-01,   1.767766952962672e-01,];
    e = [           3.125000000003739e-01,  -3.820000000000000e-13,
                    3.729000000000000e-13,   1.249999999999622e+00,
                   -3.124999999996282e-01,  -3.820000000000000e-13,
                    3.729000000000000e-13,  -1.250000000000377e+00,
                    3.125000000003739e-01,  -3.820000000000000e-13,];
    aklp = ssize/2.5;
    theta *= pi/180.0
    cs = cos(theta)
    ss = sin(theta)

    plota(a)
    plota(b)
    plota(c)
    plota(d)
    plota(e)
