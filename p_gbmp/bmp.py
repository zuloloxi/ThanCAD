import struct
from p_ggen import Struct

class ThanBmp:
    "Represent a bmp raster."
    def __init__(self, f=None):
        "Reads header and checks for errors; f is a file object."
        self.head, ierr = readHeadBmp(f)
        if ierr != 0: raise ValueError("bmp error %d" % ierr)


    def overwriteHeader(self, fw):
        "Overwrites the header of opened image file fw with current header."
        try:
            bmp = self.head
            head1 = bmp.ift + struct.pack("=lhhl", bmp.fs, bmp.r1, bmp.r2, bmp.off)
            if len(head1) != 14: raise ValueError("Program error: head1 should be exactly 14 bytes.")
            head2 = struct.pack("=lllhhllllll", bmp.hs, bmp.iw, bmp.ih, bmp.np, bmp.bpp, bmp.cm, bmp.sb, bmp.hr,\
                bmp.vr, bmp.ncu, bmp.nsc)
            if len(head2) != 40: raise ValueError("Program error: head2 should be exactly 40 bytes.")
        except:
            raise ValueError("Corrupted ThanBmp header")
        fw.seek(0)
        fw.write(head1)
        fw.write(head2)
        return 0


    def setDpi(self, dpi):
        "Set both horizontal and vertical resolutions to dpi."
#        integer*4 hrBmp              ! Horizontal resolution (pixels per meter)
#        integer*4 vrBmp              ! Vertical resolution (pixels per meter)
        dpi = int(dpi * 100.0/2.53997 + 0.5)
        self.head.hr = dpi
        self.head.vr = dpi


    def getDpi(self):
        "Return the horizontal resolution to the resolution to dpi."
        if self.head.hr != self.head.vr:
            raise ValueError("Bmp image horizontal and vertical resolutions are not the same")
        return self.head.hr * 2.53997/100.0


    def getDpi2(self):
        "Return the horizontal resolution and vertical resolution to the resolution to dpi."
        return self.head.hr * 2.53997/100.0, self.head.vr * 2.53997/100.0 


def readHeadBmp(uBmp):
    "Reads bmp headers."
    bmp = Struct()
    ierr = readHead1Bmp(uBmp, bmp)
    if ierr != 0: return None, ierr
    ierr = readHead2Bmp (uBmp, bmp)
    if ierr != 0: return None, ierr

    #      call checkBmp (ierr)
    #      if (ierr .ne. 0) return

    #      call readPalleteBmp (uBmp, ierr)
    #      if (ierr .ne. 0) return

    #      call supportBmp (ierr)
    #      if (ierr .ne. 0) return
    return bmp, 0




def readHead1Bmp(uBmp, bmp):
    """Reads bmp file's header 1.

    character*2 iftBmp           ! Image File Type, "BM"
    integer*4   fsBmp            ! File Size in bytes
    integer*2   r1Bmp, r2Bmp     ! Reserved1, Reserved2 (always 0)
    integer*4   offBmp           ! Start of image data OFFset (in bytes)
    """

    head = uBmp.read(14)
    if len(head) < 14: return 2           # Incomplete header 1
    bmp.ift = head[:2]
    try: bmp.fs, bmp.r1, bmp.r2, bmp.off = struct.unpack("=lhhl", head[2:14])
    except: return 12                     # Corrupted header 1
    #      print 'Image File Type, "BM"                   :', bmp.ift
    #      print 'File Size in bytes                      :', bmp.fs       
    #      print 'Reserved1, Reserved2 (always 0)         :', bmp.r1, bmp.r2
    #      print 'Start of image data OFFset (in bytes)   :', bmp.off            
    if bmp.ift != b'BM': return 11         # Bad magic number
    if bmp.fs  <  0: return 12            # Corrupted header 1
    if bmp.r1  != 0: return 12            # Corrupted header 1
    if bmp.r2  != 0: return 12            # Corrupted header 1
    if bmp.off < 54: return 12            # Corrupted header 1
    return 0                              # No errors

#==========================================================================


def readHead2Bmp(uBmp, bmp):
    """Reads bmp file's header 2.
      
      integer*4 hsBmp              ! Header Size (40 bytes)
      integer*4 iwBmp, ihBmp       ! ImageWidth, ImageHeight (in pixels)
      integer*2 npBmp              ! Number of image Planes 
      integer*2 bppBmp             ! Bits Per Pixel: 1, 4, 8, or 24 
      integer*4 cmBmp              ! Compression Method: 0, 1, or 2
      integer*4 sbBmp              ! Size of Bitmap (in bytes)
      integer*4 hrBmp              ! Horizontal resolution (pixels per meter)
      integer*4 vrBmp              ! Vertical resolution (pixels per meter)
      integer*4 ncuBmp             ! Number of Colors Used in image
      integer*4 nscBmp             ! Number of Significant Colors in palette
    """
    head = uBmp.read(40)
    if len(head) < 40: return 3                # Incomplete header 2
    bmp.hs, bmp.iw, bmp.ih, bmp.np, bmp.bpp, bmp.cm, bmp.sb, bmp.hr,\
              bmp.vr, bmp.ncu, bmp.nsc = struct.unpack("=lllhhllllll", head)

    #      print 'Header Size (40 bytes)                  :', bmp.hs              
    #      print 'ImageWidth, ImageHeight (in pixels)     :', bmp.iw, bmp.ih
    #      print 'Number of image Planes                  :', bmp.np
    #      print 'Bits Per Pixel: 1, 4, 8, or 24          :', bmp.bpp
    #      print 'Compression Method: 0, 1, or 2          :', bmp.cm
    #      print 'Size of Bitmap (in bytes)               :', bmp.sb
    #      print 'Horizontal resolution (pixels per meter):', bmp.hr
    #      print 'Vertical resolution (pixels per meter)  :', bmp.vr              
    #      print 'Number of Colors Used in image          :', bmp.ncu             
    #      print 'Number of Significant Colors in palette:', bmp.nsc

    if bmp.hs < 40: return 13                  # Corrupted header 1
    if bmp.iw <= 0: return 13                  # Corrupted header 1
    if bmp.ih <= 0: return 13                  # Corrupted header 1
    if bmp.np != 1: return 13                  # Corrupted header 1
    if bmp.bpp not in (1, 4, 8, 24): return 13 # Corrupted header 1
    if bmp.cm < 0 or bmp.cm > 2:     return 13 # Corrupted header 1
    if bmp.sb < 0:  return 13                  # Corrupted header 1
    if bmp.hr < 0:  return 13                  # Corrupted header 1
    if bmp.vr < 0:  return 13                  # Corrupted header 1
    if bmp.ncu < 0: return 13                  # Corrupted header 1
    if bmp.nsc < 0: return 13                  # Corrupted header 1


#---Skip rest of header 2

    n = bmp.hs - 40
    if n > 0:
        head = uBmp.read(n)
        if len(head) < n: return 3             # Incomplete header 2
    return 0                                   # No errors


def test():
    bmp = ThanBmp(open("test.bmp", "rb"))
    print("Bmp resolution = %ddpi x %ddpi" % (bmp.head.hr*0.0254, bmp.head.vr*0.0254))


if __name__ == "__main__": test()
