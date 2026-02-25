try:
    from PIL.Image import (open, new,
        ROTATE_90, ROTATE_180, ROTATE_270,
        NEAREST, ANTIALIAS, BICUBIC)
    from PIL.ImageTk import PhotoImage
    from PIL.ImageEnhance import Brightness
    from PIL.ImageDraw import Draw
    from PIL.ImageFont import load_path
    from PIL.ImageFilter import SMOOTH
except ImportError:
    from .Imagefake import (open, new,
        ROTATE_90, ROTATE_180, ROTATE_270,
        NEAREST, ANTIALIAS, BICUBIC)
    from .ImageTkfake import PhotoImage
    from .ImageEnhancefake import Brightness
    from .ImageDrawfake import Draw
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
