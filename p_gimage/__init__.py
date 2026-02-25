try:
    from PIL import Image
    from PIL.Image import (open, new,
        ROTATE_90, ROTATE_180, ROTATE_270,
        NEAREST, BICUBIC)

    try: #See  https://stackoverflow.com/questions/76616042/attributeerror-module-pil-image-has-no-attribute-antialias
         # ANTIALIAS is deprecated and will be removed in Pillow 10 (2023-07-01). Use LANCZOS or Resampling.LANCZOS instead.
        from PIL.Image import ANTIALIAS
    except ImportError:
        from PIL.Image import LANCZOS as ANTIALIAS

    try:
        from PIL.Image import DecompressionBombError
    except ImportError:
        class DecompressionBombError(Exception): pass    #Support for older versions of PILLOW 
    from PIL.ImageTk import PhotoImage
    from PIL.ImageEnhance import Brightness
    from PIL.ImageDraw import Draw
    from PIL.ImageFont import load_path, truetype
    from PIL.ImageFilter import SMOOTH
except ImportError:
    raise
    from . import Imagefake as Image
    from .Imagefake import (open, new,
        ROTATE_90, ROTATE_180, ROTATE_270,
        NEAREST, ANTIALIAS, BICUBIC,
        DecompressionBombError)
    from .ImageTkfake import PhotoImage
    from .ImageEnhancefake import Brightness
    from .ImageDrawfake import Draw
    from ImageFontfake import load_path, truetype
    from .ImageFilterfake import SMOOTH       #Note: ImageFilterfake is the real ImageFilter (it is not fake)

try:
    import sane
except ImportError:
    from . import sanefake as sane
try:
    import _sane
except ImportError:
    from . import _sanefake as _sane

from .getscandpi import getScanDpi, getScanDpiFake
from .Imagefake import ThanImageMissing


def imageSetmaxpixels(n=None):   #Thanasis2018_04_05
    """Change the default max pixel size (int(1024 * 1024 * 1024 // 4 // 3))."

    The Limit is around a quarter gigabyte for a 24-bit (3 bpp) image"""
    if n is None: 
        Image.MAX_IMAGE_PIXELS = int(1024 * 1024 * 1024 // 4 // 3)  #default
    else:
        n = int(n)
        if n >= 1024: Image.MAX_IMAGE_PIXELS = n
