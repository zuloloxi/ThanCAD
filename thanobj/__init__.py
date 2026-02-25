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

This package defines ThanCad's objects. Objects are entities which have no direct
graphic representation in the drawing AND have a state which must be saved (and
read) with the drawing.
"""
from .thandtmlines     import ThanDTMlines
from .thandemusgs      import ThanDEMusgs
from .thantri          import ThanTri
from .thanfplan        import ThanFplan
from .thannoncartesian import NonCartesian
from .thanlinesimp     import LineSimplification
from .thanphotmodel    import ThanPhotModel
from .thanphotinterior import ThanPhotInterior
from .thantransform    import ThanTransformation, ThanProjection
from .thanbiocityplan  import ThanBiocityplan
from .thanprofile      import ThanProfile
from .thanisoclinal    import ThanIsoclinal

thanObjClasses = (ThanDTMlines, ThanDEMusgs, ThanTri, ThanFplan, NonCartesian,
                  LineSimplification, ThanPhotModel, ThanPhotInterior,
                  ThanTransformation, ThanProjection, ThanBiocityplan,
                  ThanProfile, ThanIsoclinal)
thanObjClass = dict((c.thanObjectName, c) for c in thanObjClasses)
del thanObjClasses
