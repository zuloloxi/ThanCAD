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

This module defines various information for the translation from English to Greek
and other languages. This module is specific to the modules which implement the
various civil engineering algorithms.
"""

from p_ggen import Translation
#from thanopt import thancadconf


#English to greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "utf_8", "gr", "utf_8"),

"&Grade line"                                     : u"Ερυθρά γραμμή",
"Can't compute grade line: No profile has been defined!":
                                                    u"Δεν μπορεί να υπολογιστεί η ερυθρά γραμμή: δεν έχει οριστεί μηκοτομή!",
"Computes automatically the grade line of a road profile":
                                                    u"Αυτόματος υπολογισμός ερυθράς γραμμής μηκοτομής οδού",
}

Tcivil = Translation(en2gr)
#Tcivil.thanLangSet("en", thancadconf.thanTranslateTo)
del en2gr
