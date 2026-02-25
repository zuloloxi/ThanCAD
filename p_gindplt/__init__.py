from .inddra import rnumber, cross, rectangle, trectangle, elips1, north
from .plotdashdot import plotdashdot, plotdashdotarc1
from .linehatch import HatchPolygon, plothatchlines, plothatchsolids
from .regularpolygon import regularPolygon, plotregularpolygon
from .axis import axis, logax
from .indfil import gfill
from .bintree import plotbintree
from .stairs import staircaseU, staircaseS


class ThanSpline:
    def __init__(self, *args, **kw):
        raise AttributeError("ThanSpline class moved to the p_gmath library")
