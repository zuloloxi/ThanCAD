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

This package includes dialogs (forms to get user input) implemented with Tkinter.
"""
from .thandialogcol   import ThanColor
from .thandialogdro   import ThanDro
from .thandialogpen   import ThanPen
from .thandialogltype import ThanDialogLtype

from .thandialogdimstyle import ThanDimstyleManager, ThanDialogDimstyle

from .thandialoglay   import ThanDialogLay
from .thandialogosn   import ThanTkOsnap
from .thandialogsty   import ThanTkStyle
from .thandiaexppil   import ThanTkExppil
from .thandialogtext  import ThanElemtext
from .thandialogscan  import ThanScan
from .thandialogprint import ThanDiaPlot
#from thantkwinerror  import ThanTkWinError
from .thandialogunits import ThanDialogUnits
from .thandialogsimpl import ThanSimplificationSettings
from .thandialogenc   import thanSelectEncoding
from .thandialogpodis import ThanPodisSettings

from .thanarch.thandiaarch import ThanArchCom
from .thanarch.thandiafplan import ThanFplan
#from thanarch.thandiabcplan import ThanBcplan
from . import transf

from .thandiaisoclinal import ThanDialogIsoclinal
