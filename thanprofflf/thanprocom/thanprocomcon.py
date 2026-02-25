##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

Package which processes commands entered by the user.
This module defines various constants.
"""

from thanprofflf.thanprocom import thanprocomedu, thanprocomtransf

coms = \
[ ("eduaxis",        thanprocomedu.thanEduAxis),
  ("edumatch2",      thanprocomedu.thanEduMatch2),
  ("edumatch23",     thanprocomedu.thanEduMatch23),
  ("edumatch3",      thanprocomedu.thanEduMatch3),
  ("edumatchmult2",  thanprocomedu.thanEduMatchMult2),
  ("edumatchmult23", thanprocomedu.thanEduMatchMult23),
  ("eduproject",     thanprocomedu.thanEduPointProject),
  ("edutransf",      thanprocomtransf.thanEngTransf),
]
