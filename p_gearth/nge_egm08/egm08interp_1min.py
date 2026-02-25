"""
c     INTERP IS A F77 PROGRAM FOR INTERPOLATING FROM A GLOBAL GRID OF
c     REGULARLY SPACED POINT VALUES TO SELECTED SCATTERED COORDINATES.
c     INTERP REQUIRES AN INPUT FILE CONTAINING THE GLOBALLY GRIDDED
c     VALUES, AND AN INPUT FILE CONTAINING THE GEOGRAPHICAL COORDINATES
c     OF THE SCATTERED POINTS FOR WHICH INTERPLATED VALUES ARE REQUIRED.
c
c     THE INPUT FILE OF GLOBALLY GRIDDED POINT VALUES WILL STORE THESE
c     VALUES IN REAL*4 SEQUENTIAL BINARY FORMAT, WITH ONE RECORD FOR
c     EACH PARALLEL BAND. THESE INPUT VALUES ARE EQUALLY SPACED IN
c     LATITUDE AND LONGITUDE, AND ARE SITUATED AT THE CORNERS OF THEIR
c     RESPECTIVE CELLS, SUCH THAT THE TOP-LEFT POINT IN THE GRID HAS A
c     LONGITUDE OF ZERO DEGREES AND A LATITUDE OF NINETY DEGREES. THE
c     FIRST RECORD CONTAINS THE NORTHERN-MOST PARALLEL, AND THE FIRST
c     VALUE IN EACH RECORD IS THE WESTERNMOST VALUE FOR THAT PARALLEL.
c     NOTE THAT GRID VALUES SITUATED ON THE ZERO MERIDIAN APPEAR ONLY
c     ONCE, AS THE FIRST VALUE IN THEIR RESPECTIVE RECORD AT ZERO
c     LONGITUDE. THESE VALUES ARE NOT REPEATED AT THE END OF THEIR
c     RESPECTIVE RECORDS AT LONGITUDE = 360 DEGREEES.
"""
#from past.builtins import xrange
from p_ggen.py23 import xrange
import struct
from math import cos, radians, floor
import p_ggen, p_gnum, p_gfil
from p_gmath import EquidistantSpline
from p_ggeod import egsa87

uGri = None
iwind    = 6
iw       = iwind+1
nrows    = 10801
ncols    = 21600
nriw2    = nrows+2*iw
nciw2    = ncols+2*iw
dlat     = 1.0/60.0
dlon     = 1.0/60.0
path_gd = ('                                        ',
           '/samba/data/gdem/nge_egm08/             ',
           'f:/data/gdem/nge_egm08/                 ',
           '../libs/p_gearth/nge_egm08/             ',
           '/home2/x/libs/p_g/p_gearth/nge_egm08/   ',
           'x:/libs/p_g/p_gearth/nge_egm08/         ',
          )


name_gd  = 'Und_min1x1_egm2008_isw=82_WGS84_TideFree_SE'    #Grid without edges
name_gde = 'thanegm08.bin'                                  #Grid with edges
dostat = False
gridyn = {}     #This array is for dynamic read
notinitialised = True

prt = p_ggen.prg


def openGrid (fn):
    "Opens the file which contains the grid."
    global uGri
    fn = fn.strip()
    for par in path_gd:
        fnu1 = par.strip() + fn
        try:            uGri = open(fnu1, "rb")
        except IOError: pass
        else:           break
    else:
        terr = 'File '+fn+' can not be accessed'
        p_gfil.er1s(terr)
    if dostat:
        prt(' Input file containing globally gridded values : %s' % (fnu1,), "info1")


def egm08ReadGridEdgesDyn(prt1=p_ggen.prg):
    "Reads dynamically the grid which was already the edges."
    global gridyn, prt, notinitialised
    if prt1 is None: prt1 = p_ggen.prgnone
    prt = prt1
    openGrid(name_gde)
    prt('Preparing dynamic reading of EGM08 grid..', "info1")
    gridyn.clear()
    notinitialised = False


def geodDege(alam, phi):
    "Convert angles (degrees) so that they are 0<=alam<360, -90<=phi<90 if possible."
    alam %= 360.0   #Ensure 0 <= alam <= 360
    phi  %= 360.0   #Ensure 0 <= phi  <= 360
    if phi > 180.0: phi -= 360.0
    return alam, phi


def egm08Ndyn (flon, flat):
    "Check (GRS80) geodetic coordinates and compute N."
    if notinitialised: egm08ReadGridEdgesDyn()
    flon, flat = geodDege(flon, flat)
#-----------------------------------------------------------------------
#
#   COORDS OK?
#
#-----------------------------------------------------------------------
    if flat > 90.0 or flat < -90.0 or flon > 360.0 or flon < 0.0: return 999999.0
    dmin =  0.0
    slat = -90.0 - dlat*iw  #  (lat < -90) OK
    wlon =       - dlon*iw  #  (lon <   0) OK
    val = interpdyn(iwind,dmin,gridcell,slat,wlon,dlat,dlon,nriw2,nciw2,nriw2,nciw2,flat,flon)
    return val


def egm08PixelCoor(flon, flat):
    "Return the column and row of the nearest undulation to flon, flat."
    if notinitialised: egm08ReadGridEdgesDyn()
    flon, flat = geodDege(flon, flat)
    if flat > 90.0 or flat < -90.0 or flon > 360.0 or flon < 0.0: return -1, -1
    slat = -90.0 - dlat*iw  #  (lat < -90) OK
    wlon =       - dlon*iw  #  (lon <   0) OK
    ri=(flat-slat)/dlat
    rj=(flon-wlon)/dlon
    return int(rj), int(ri)


def egm08joinDem(xymm):
    "Return a single DEM that contains the region xymm."
    jxa, iya = egm08PixelCoor(xymm[0], xymm[3])    #Up, left point of the window
    jxb, iyb = egm08PixelCoor(xymm[2], xymm[1])    #Down, right point of the window
    a = p_gnum.zeros((iya-iyb+1, jxb-jxa+1), p_gnum.Float32)
    i = 0
    for iy in xrange(iya, iyb-1, -1):
        _ = gridcell(iy, 0)      #Force dynamic load of row iy
        a[i, :] = gridyn[iy][jxa:jxb+1]
#        print i
#        print a[i, :]
        i += 1
    return p_gnum.num2im(a)


def egm08NEgsa87dyn (flon, flat):
    "Compute the undulation N with respect to the modified GRS80 (Egsa87)."
    valint = egm08Ndyn (flon, flat)
    if valint == 999999.0: return valint
    h7m80 = egsa87.geodetGRS802h7m80(radians(flon), radians(flat))
    return valint - h7m80


def gridcell(i, j):
    "Return the i, j element of grid; read the data if not there."
    row = gridyn.get(i)
    if row is None:
        uGri.seek((i-1)*nciw2*4)
        dl = uGri.read(nciw2*4)
        fmt = "%df" % (nciw2,)
        row = gridyn[i] = p_gnum.array(struct.unpack(fmt, dl), p_gnum.Float32)
    return row[j-1]


def interpdyn(iwo,dmin,h,phis,dlaw,ddfi,ddla,nphi,ndla,ipdim,ildim,phi,dla):
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
#                                                                      C
#     SUBROUTINE FOR INTERPOLATION OF VALUES FROM A STANDARD DTM-GRID  C
#     TO INDIVIDUAL STATION LOCATIONS.                                 C
#                                                                      C
#                                                                      C
#     INPUT PARAMETERS...                                              C
#     ===================                                              C
#     iwO...    A SPLINE WINDOW OF SIZE 'iwO' X 'iwO' WILL BE C
#                  USED AROUND EACH STATION. IF 'iwO' IS 0 OR 1,    C
#                  BILINEAR INTERPOLATION WILL BE USED.                C
#     DMIN...      MINIMUM ACCEPTABLE DISTANCE FROM THE GRID EDGE IN   C
#                  KM (USEFUL FOR FFT GRIDS).                          C
#     H...         2D DATA ARRAY (ELEMENT (1,1) IN SW CORNER).         C
#     PHIS,DLAW... LATITUDE AND LONGITUDE OF SW GRID POINT.            C
#     DDFI,DDLA... GRID SPACING IN LATITUDE AND LONGITUDE DIRECTION.   C
#     NPHI,NDLA... NUMBER OF GRID POINTS IN LATITUDE AND LONGITUDE     C
#                  DIRECTION.                                          C
#     IPDIM,ILDIM..DIMENSIONS OF 2D DATA ARRAY 'H' AS DECLARED IN THE  C
#                  CALLING PROGRAM.                                    C
#     PHI,DLA...   LATITUDE AND LONGITUDE OF INTERPOLATION POINT.      C
#                                                                      C
#                                                                      C
#     OUTPUT PARAMETERS...                                             C
#     ====================                                             C
#     VALINT...    INTERPOLATED VALUE.                                 C
#                                                                      C
#                                                                      C
#     EXECUTION TIME ON CDC 990 IS...                                  C
#     ===============================                                  C
#     +------------------+-------------------+-------------------+     C
#     I  INTERPOLATION   I  OPT=LOW          I  OPT=HIGH         I     C
#     I------------------I-------------------I-------------------I     C
#     I  BILINEAR        I  1.44 MSEC/STAT.  I  1.44 MSEC/STAT.  I     C
#     I  3 X 3 SPLINE    I  1.53 MSEC/STAT.  I  1.51 MSEC/STAT.  I     C
#     I  5 X 5 SPLINE    I  1.70 MSEC/STAT.  I  1.67 MSEC/STAT.  I     C
#     I  7 X 7 SPLINE    I  2.02 MSEC/STAT.  I  1.74 MSEC/STAT.  I     C
#     I  9 X 9 SPLINE    I  2.31 MSEC/STAT.  I  2.00 MSEC/STAT.  I     C
#     +------------------+-------------------+-------------------+     C
#                                                                      C
#                                                                      C
#     PROGRAM CREATION BY...   H. DENKER          MAY 30, 1987         C
#                              H. DENKER          MARCH 13, 1989       C
#                                                                      C
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    ipa1=20
    idim1=ipa1
    twopi=6.28318530717959
    rho=360.0/twopi
    rearth=6371000.0
    if iwo < 2: iwo=2
    if iwo > idim1: iwo=idim1
    ilim=int(dmin*1000.0*rho/(rearth*ddfi))
    jlim=int(dmin*1000.0*rho/(rearth*ddla*cos((phis+ddfi*nphi/2.0)/rho)))
    lodd=int(iwo/2)*2 != iwo
    ri=(phi-phis)/ddfi
    rj=(dla-dlaw)/ddla
    if lodd:
        i0=int(ri-0.5)
        j0=int(rj-0.5)
    else:
        i0=int(ri)
        j0=int(rj)
    i0=i0-int(iwo/2)+1
    j0=j0-int(iwo/2)+1
    ii=i0+iwo-1
    jj=j0+iwo-1
    if i0 < 0 or ii >= nphi or j0 < 0 or jj >= ndla:
        prt('%12.6f%12.6f STATION TOO NEAR GRID BOUNDARY  - NO INT. POSSIBLE|' % (phi,dla), "can")
        valint=999999.0
        return valint
    elif i0 < ilim or ii > nphi-ilim or j0 < jlim or jj > ndla-jlim:
        prt('%12.6f%12.6f STATION OUTSIDE ACCEPTABLE AREA - NO INT. PERFORMED|' % (phi,dla), "can")
        valint=999999.0
        return valint
    if iwo > 2:
        hc = []
        for i in xrange(1, iwo+1):
            a = []
            for j in xrange(1, iwo+1):
                a.append(h(i0+i,j0+j))
#            print 'i=', i, 'a=', a
            spl = EquidistantSpline(a)
#            print "spline argument=", rj-j0+1.0
            hc.append(spl.spline(rj-j0+1.0))
#            print "result=", hc[-1]
        spl = EquidistantSpline(hc)
        valint=spl.spline(ri-i0+1.0)
    else:
        valint=bilindyn(ri+1.0,rj+1.0,h,nphi,ndla,ipdim,ildim)
    return valint


def bilindyn(ri,rj,a,imax,jmax,iadim,jadim):
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
#                                                                      C
#                           B I L I N                                  C
#                                                                      C
#  INTERPOLATES VALUES IN AN ARRAY A USING BILINEAR                    C
#  (PARABOLIC HYPERBOLOID) INTERPOLATION.                              C
#                                                                      C
#----------------------------------------------------------------------C
#                                                                      C
#  PARAMETERS:                                                         C
#                                                                      C
#  BILIN...       INTERPOLATED VALUE                                   C
#                                                                      C
#  RI, RJ...      INTERPOLATION ARGUMENT, (1,1) IN LOWER LEFT CORNER,  C
#                 (IMAX, JMAX) IN UPPER RIGHT.                         C
#                                                                      C
#  A...           INTEGER*2 ARRAY WITH ARGUMENTS                       C
#                                                                      C
#  IMAX, JMAX...  NUMBER OF POINTS IN GRID                             C
#                                                                      C
#  IADIM, JADIM...DECLARED DIMENSIONS OF 'A'                           C
#                                                                      C
#  OUTSIDE AREA COVERED BY 'A' THE FUNCTION RETURNS THE VALUE OF       C
#  THE NEAREST BOUNDARY POINT.                                         C
#                                                                      C
#----------------------------------------------------------------------C
#                                                                      C
#  PROGRAMMER:                                                         C
#  RENE FORSBERG, JULY 1983                                            C
#                                                                      C
#  MODIFICATIONS BY:                                                   C
#  HEINER DENKER, 07/01/1987                                           C
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    in_ = int(floor(ri))
    ie = int(floor(rj))
    rn = ri - in_
    re = rj - ie
    if in_ < 1:
        in_ = 1
        rn = 0.0
    elif in_ >= imax:
        in_ = imax-1
        rn = 1.0
    if ie < 1:
        ie = 1
        re = 0.0
    elif ie >= jmax:
        ie = jmax-1
        re = 1.0
    rnm1=1.0-rn
    rem1=1.0-re
    return rnm1*rem1*a(in_,ie) + rn*rem1*a(in_+1,ie) + rnm1*re*a(in_,ie+1) + rn*re*a(in_+1,ie+1)


def test():
    "Test the module."
    egm08ReadGridEdgesDyn()
    prt(egm08Ndyn(flat=38.0, flon=21.0))
    prt(egm08Ndyn(flat=38.0, flon=22.0))


if __name__ == "__main__":
    test()
