from math import fabs, sin, cos, log

def axis(dxf, x,y,s,theta,xmin,dx,ibcd,n):
      """      implicit none
      integer*4 n                                        ! arguments in
      real*8 x, y, s, theta, xmin, dx                    ! arguments in
      character*(*) ibcd                               ! arguments in
c
c     function
c     to draw an annotated axis line
c     scale marks and values of the variable are drawn
c     at sub-divisions along the axis
c     a label is added in a central position,
c     and parallel to the axis
c     copyright   computer instrumentation limited   november 1978
c
c     parameter descriptions
c     x,y      coordinates of axis origin (user units)
c     s        length of axis (centimetres)
c     theta    axis orientation (degrees to positive x direction)
c     xmin     value of variable to be printed at the origin
c     dx       scale factor of axis (units/centimetre)
c     ibcd     array with axis label
c     n        number of characters in label
c              +ve   annotation on clockwise side of axis
c              -ve   annotation on anticlockwise side of axis
c
c     update history for this issue
c     17/10/80   ncd   redundant label removed
cc      dimension idrgex(10)
cc      common/cildrg/ scalex,scaley,fact,fstep,fstepx,fstepy,
cc     c      sizeh,sizew,slant,sized1,sizesp,sized2,
cc     c      origlx,origly,stepx,stepy,lintyp,incory,ipenx,ipeny,
cc     c      ips,ipc,idrgex
c     text for decimal exponent
      """
      sizen,sizel,tick = 0.2, 0.4, 0.2

      scalex = 1.0
      scaley = 1.0

#     angular constants
      thetr=theta*0.0174533
      sth=sin(thetr)
      cth=cos(thetr)

#     set position of annotation
      if n < 0:
          clock=1.0
          nchar=-n
      else:
          clock=-1.0
          nchar=n

#     ensure integral value of s is .ge. 1.0
      ixs=int(fabs(s)+0.5)
      if ixs-1 < 0: ixs=1

#     determine decimal exponent of scale factor
      adx=fabs(dx)
      ak=log(adx)*0.434294
      if ak < 0.0: ak = 0.0
      ak = 0.0               #################################
      k=int(ak)
      adx=10.0**(-k)
      xscale=1.0/scalex
      yscale=1.0/scaley

#     tick length
      dxt=-tick*clock*sth*xscale
      dyt=tick*clock*cth*yscale

#     offsets for annotation
      dxn=-sizen-sizen
      dyn=(tick+sizen)*clock-0.5*sizen
      ddx1=(dxn*cth-dyn*sth)*xscale
      ddy1=(dyn*cth+dxn*sth)*yscale

#     increments for each mark
      rcth=cth*xscale
      rsth=sth*yscale
      radx=adx*dx

#     set up first tick
      xn=x
      yn=y
      x0=xmin*adx

#     draw tick marks and annotation
      ntic=ixs+1
      #do 20 i=1,ntic
      for i in range(1, ntic+1):
            dxf.thanDxfPlot(xn,yn,3)
            dxf.thanDxfPlot(xn+dxt,yn+dyt,2)
            if i-(i//2)*2 != 0: dxf.thanDxfPlotNumber(xn+ddx1,yn+ddy1,sizen,x0,theta,2)
            #if i-(i//2)*2 != 0: dxf.thanDxfPlotNumber(xn+ddx1,yn+ddy1,sizen,x0,theta,-1)      ########
            xn=xn+rcth
            yn=yn+rsth
            x0=x0+radx
      radx=float(ixs)
      dxf.thanDxfPlot(x+radx*rcth,y+radx*rsth,3)

#     write axis description and draw axis line
      z=float(nchar)*sizel
      if k != 0: z=z+2.0*sizel+4.0*sizen
#     jump out if no multiplier and no label
      if z > 0.0:
#     draw to midpoint first
            xn=x+float(ixs/2)*rcth
            yn=y+float(ixs/2)*rsth
            dxf.thanDxfPlot(xn,yn,2)
#     work out start position of annotation
            dxn=(radx-z)/2.0
            dyn=(tick+sizen+sizel)*clock-0.5*sizel
            xt=x+(dxn*cth-dyn*sth)*xscale
            yt=y+(dyn*cth+dxn*sth)*yscale
#     write axis label
            if nchar>0:
                  dxf.thanDxfPlotSymbol(xt,yt,sizel,ibcd,theta)
                  xt, yt = dxf.thanDxfWhere()
#     write multiplier
#     do it character by character then we dont have to worry
#     about machine characteristics
            if k != 0:
                  xt=xt+2.0*sizel*rcth
                  yt=yt+2.0*sizel*rsth
                  dxf.thanDxfPlotSymbol(xt,yt,sizen,"*10",theta)
                  xt, yt = dxf.thanDxfWhere()
                  xt=xt-0.5*sth*sizen*xscale
                  yt=yt+0.5*cth*sizen*yscale
                  dxf.thanDxfPlotNumber(xt,yt,sizen/2.0,float(-k),theta,0)
#     move back to midpoint
            dxf.thanDxfPlot(xn+rcth,yn+rsth,3)
      dxf.thanDxfPlot(x,y,2)


def test():
    import p_gdxf
    dxf = p_gdxf.ThanDxfPlot()
    dxf.thanDxfPlots()
    axis(dxf, 10.0, 200.0, 20.0,  0.0, -100.0, 10.0, "My x axis",  1)
    axis(dxf, 10.0, 200.0, 20.0, 90.0, -100.0, 10.0, "My y axis", -1)
    dxf.thanDxfPlot(0.0,0.0,999)


if __name__ == "__main__": test()
