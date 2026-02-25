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

Package which provides constants and ThanCad customisation. It also does some tests
to see if ThanCad can run in the python environmenst of the host OS.
This is the first package that is imported and calls only Python library modules
and external libraries p_g* modules.
"""

from .thaninit import thanInitPregui, thanInitPostgui, thanInitEndgui
from . import thancadconf, thancon, thanmenus2
#from p_gimage import pilpy2exe  #This explicitly import PIL plugins to aid py2exe..
                                #..which makes an executable for windoze..
                                #..Yeha, windoze "just" works!
