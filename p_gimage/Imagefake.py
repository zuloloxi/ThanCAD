"A fake Image module in case Image is not available."
ROTATE_90 = 2   #These values were taken from PIL January 9, 2014
ROTATE_180 = 3
ROTATE_270 = 4
# resampling filters
NONE = 0
NEAREST = 0
ANTIALIAS = 1 # 3-lobed lanczos
LINEAR = BILINEAR = 2
CUBIC = BICUBIC = 3

# Limit to around a quarter gigabyte for a 24 bit (3 bpp) image
MAX_IMAGE_PIXELS = int(1024 * 1024 * 1024 // 4 // 3)

class DecompressionBombError(Exception):
    pass


class ThanImageMissing(object):
    "This class represents a fake image object of the fake Image module."

    def __init__(self, size=(100,100), mode="L"): 
        self.size = size
        self.mode = mode

    def copy(self):
        return ThanImageMissing(self.size)

    def __error(self):
        raise ValueError("Image was not found/not supported/corrupted.")
    def resize  (self, *args, **kw): self.__error()

    def getpixel(self, xy):
        return 0

    def paste(self, image, box, mask=None):
        pass

    def save(self, outfile, format=None, **options):
        pass

    def crop(self, clip):
        j1, i1, j2, i2 = clip
        return ThanImageMissing(size=(j2-j1+1, i2-i1+1))

    def transpose(self, rot):
        if rot == ROTATE_180: dxp, dyp = self.size
        else:                 dyp, dxp = self.size
        return ThanImageMissing(size=(dxp, dyp))

    def convert(self, mode, matrix=None):
        return ThanImageMissing(self.size, mode)

    def load(self, *args, **kw):
        pass


def open(fi):
    "Open the image stored in filename fi; return ThanImageMissing."
    return ThanImageMissing()


def new(mode, size, color="black"):
    "Return a new image; return ThanImageMissing."
    return ThanImageMissing(size, mode)
