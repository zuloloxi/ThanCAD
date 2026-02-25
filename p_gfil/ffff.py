# -*- coding: iso-8859-7 -*-
import base64
k = []


def pre():
    from math import pi
    a = pi - int(pi)
    for i in xrange(8):
        a *= 10.0
        k.append(int(a))
        a = a - int(a)


def fff():
    f = 'ISTCzcrPx9jK09Ql3NbH0dDXITIpzdXIytfNztPRJsjKxSHR0NnH0srO0NrcIg=='
    return gggg(f)


def ffff (dl):
      dl1 = []
      for i,c in enumerate(dl):
          j = ord(c)
          j = j + k[i % 8]
          dl1.append(chr(j))
      dl1 = "".join(dl1)
      return base64.encodestring(dl1)[:-1]


def gggg(dl):
      dl = base64.decodestring(dl)[:-1]
      dl1 = []
      for i,c in enumerate(dl):
          j = ord(c)
          j = j - k[i % 8]
          dl1.append(chr(j))
      return "".join(dl1)

#c============================================================================
#
#      subroutine hhhh
#      include 'fildat.inc'
#      integer*4 ierr
#      character*10 dline
#      character*35 f
#
#c-----try to open file
#
#c      f = '\\51thanasis\d\tif\var\sat.tif'
#      f = ']`46|csgb`szwrxthw]yrhb{bv]xjv4yjj!' ! \\31samba\runprogs\tif\var\sat.tif
#      call gggg (f)
#      open (uArx, file=f, iostat=ierr)
#      if (ierr .ne. 0) then
#          f = ']`itvgxasyou{qmx]xjkexgw]wby7vok!$!' ! \\homer\runprogs\tif\var\sat.tif
#          call gggg (f)
#          open (uArx, file=f, iostat=ierr)
#          if (ierr .ne. 0) go to 200
#      end if
#
#c-----Try to validate
#
#      read (uArx, 20, iostat=ierr) dline
#20    format (a)
#      if (ierr .ne. 0) go to 100
#      call gggg (dline)
#      if (dline .ne. 'XYZZYXYZZY') go to 100    ! Magic word
#      close (uArx)
#      return
#
#c-----Validation failed
#
#100   continue
#      close (uArx)
#200   continue
#      f = 'B2!X]CSTT$Mnktgwz$ot}"ltvre%)"&%!$!' ! A. STAMOS Library not found
#      call gggg (f)
#      print 10, f
#10    format (1x, a)
#      stop
#      end

pre()
if __name__ == "__main__":
    than()
