from .inddra import rnumber, cross, rectangle, elips1, logax, north
from .plotdashdot import plotdashdot, plotdashdotarc1
from .linehatch import HatchPolygon, plothatchlines, plothatchsolids
from .regularpolygon import regularPolygon, plotregularpolygon
from .axis import axis
from .indfil import gfill
from .bintree import plotbintree

class ThanSpline:
    def __init__(self, *args, **kw):
        raise AttributeError("ThanSpline class moved to the p_gmath library")
