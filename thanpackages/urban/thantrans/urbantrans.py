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

The package provides tools and automation for urban analysis/design.
The subpackage contains translations for urban related procedures.
This module defines the translations to Greek.
"""
import p_ggen

#English to Greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "iso-8859-1", "gr", "iso-8859-7"),
"Road width (m)"                                  : u"Πλάτος οδού (m)",
"Left Pavement width (m)"                         : u"Πλάτος αριστερού πεζοδρομίου (m)",
"Right Pavement width (m)"                        : u"Πλάτος δεξιού πεζοδρομίου (m)",
"Median strip width (m)"                          : u"Πλάτος νησίδας (m)",

"&Locate roads of slope"                          : u"Εύρεση οδών με κλίση",
"Locates roads (lines) whose slope is less than arbitrary threshold":
                                                    u"Βρίσκει οδούς (γραμμές) των οποίων η κλίση είναι μικρότερη από ένα αυθαίρετο όριο",
"Please enter grade threshold (enter=%.1f%%): "   : u"Δώστε όριο κλίσης (enter=%.1f%%): ",
"Please select lines to search:"                  : u"Επιλογή γραμμών προς εύρεση:",
"%d roads have elevation zero and were ignored."  : u"%d οδοί έχουν υψόμετρο μηδέν και αγνοήθηκαν.",
"No suitable roads were found!"                   : u"Δεν βρέθηκαν κατάλληλες οδοί!",
"%d suitable roads were copied to current layer." : u"%d κατάλληλες οδοί αντιγράφησαν στην τρέχουσα διαφάνεια.",
}

Turban = p_ggen.Translation(en2gr)
Turban.thanLangSet("en", "gr")
del en2gr
