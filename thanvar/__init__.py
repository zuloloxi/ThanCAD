##############################################################################
# ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2025 Thanasis Stamos, May 20, 2025
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (www.gnu.org/licenses/gpl.html).
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################
"""\
ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers

This package includes various unrelated functions which can not be part of any
other package. It depends only on thanopt (and indirectly to thandefs).
"""
from p_gmath import PI2
from p_gtkwid import ThanScheduler
from p_ggen import Canc, ThanLayerError
from thanopt.thancon import (THANBYPARENT, THANPERSONAL,
    thanMdimj, ThanCadError, ThanDegenerateError)
from .thanutila import (thanCleanLine2, thanCleanLine2t, thanCleanLine3, thanShowFile,
                       thanExtendNodeDims, thanCumulDis, thanNearElev)
from . import thanfiles
from .thanlog import thanLogTk, thanLogC
from .thanroad import calcRoadNode, calcRoadNodeR, tkRoadNode, tkRoadNodeR
from .thanfillet import thanFilletCalc
from .thantxt import DEFMES, DEFCAN
from .thanhw import InfoWin
from .thanpilutil import thanDash2Dash3, thanPilLine, thanPilArc, thanPilCircle
from .thandelay import ThanDelay
