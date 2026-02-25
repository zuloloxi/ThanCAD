# -*- coding: iso-8859-7 -*-

##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module defines various information for the translation from English to Greek
and other languages. This module is specific to the modules which implement the
various architectural algorithms.
"""

from p_ggen import Translation
#from thanopt import thancadconf


#English to greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "iso-8859-1", "gr", "iso-8859-7"),

"INTERSCIENTIFIC PROGRAM"                         : u"ΔΙΕΠΙΣΤΗΜΟΝΙΚΟ ΠΡΟΓΡΑΜΜΑ",
"OF GRADUATE STUDIES (DPMS) OF NTUA"              : u"ΜΕΤΑΠΤΥΧΙΑΚΩΝ ΣΠΟΥΔΩΝ (ΔΠΜΣ) ΤΟΥ ΕΜΠ",
"ENVIRONMENT AND DEVELOPMENT"                     : u"ΠΕΡΙΒΑΛΛΟΝ ΚΑΙ ΑΝΑΠΤΥΞΗ",
"Applications of environmental design on the built space":
                                                    u"Εφαρμογές περιβαλλοντικού σχεδιασμού στον δομημένο χώρο",
"A.A. Stamos"                                     : u"Θ. Στάμος",

"&Floor plan"                                     : u"Διαρρύθμιση κάτοψης",
"Automated Floor Plan Design Algorithms"          : u"Αλγόριθμοι Αυτόματης Διαρρύθμισης Κάτοψης",
"Automated Floor Plan Design"                     : u"Αυτόματη Διαρρύθμιση Κάτοψης",
"Thanasis Stamos, Research/Teaching Personnel"    : u"Θανάσης Στάμος, Ερευνητικό/Διδακτικό Προσωπικό",
"School of Civil Engineering, NTUA, "             : u"Σχολή Πολιτικών Μηχανικών, Ε.Μ.Π., ",
"Floor plan width (m)"                            : u"Πλάτος κάτοψης",
"Floor plan height (m)"                           : u"Ύψος κάτοψης",
"FLOOR PLAN CONSTRAINTS:"                         : u"ΠΕΡΙΟΡΙΣΜΟΙ ΔΙΑΡΥΘΜΙΣΗΣ:",
"Min number of rooms"                             : u"Ελάχιστος αριθμός δωματίων",
"Max number of rooms"                             : u"Μέγιστος αριθμός δωματίων",
"ROOM CONSTRAINTS:"                               : u"ΠΕΡΙΟΡΙΣΜΟΙ ΔΩΜΑΤΙΩΝ:",
"Min room length - hard (m)"                      : u"Min μήκος δωματίων - αναγκαίο (m)",
"Min room length - soft (m)"                      : u"Min μήκος δωματίων - ελαστικό (m)",
"Max room length - soft (m)"                      : u"Max μήκος δωματίων - ελαστικό (m)",
"Max room length - hard (m)"                      : u"Max μήκος δωματίων - αναγκαίο (m)",
"Min room width - hard (m)"                       : u"Min πλάτος δωματίων - αναγκαίο (m)",
"Min room width - soft (m)"                       : u"Min πλάτος δωματίων - ελαστικό (m)",
"Max room width - soft (m)"                       : u"Max πλάτος δωματίων - ελαστικό (m)",
"Max room width - hard (m)"                       : u"Max πλάτος δωματίων - αναγκαίο (m)",
"PENALTY (ADVANCED):"                             : u"ΠΟΙΝΕΣ (ΓΙΑ ΠΡΟΧΩΡΗΜΕΝΟΥΣ):",
"Number of rooms less(more) than min(max) (penalty/room)": u"Για περισσότερα(λιγότερα) δωμάτια από min(max) (ποινή/δωμάτιο)",
"(absolute)"                                      : u"(απόλυτη)",
"Room dimension less(more) than hard min(max) (penalty/m)": u"Για διάσταση δωματίου μεγαλύτερη(μικρότερη) από αναγκαίο min(max) (ποινή/m)",
"(normalised)"                                    : u"(κανονικοποιημένη)",
"Room dimension between soft and hard min(max) (penalty/m)": u"Για διάσταση δωματίου μεταξύ αναγκαίου και ελαστικού min(max) (ποινή/m)",

"Select polygon enclosing city plan\n"            : u"Επιλογή πολυγώνου που περικλείει το ρυμοτομικό\n",
"&Bio city plan"                                  : u"Βιοκλιματικό Ρυμοτομικό",
"Bioclimatic City Plan Design"                    : u"Βιοκλιματικός Σχεδιασμός Ρυμοτομικού Σχεδίου Πόλης",
"Preprocess"                                      : u"Προεπεξεργασία",
"Bioclimatic City Plan Design Algorithms"         : u"Αλγόριθμοι Βιοκλιματικού Σχεδιασμού\nΡυμοτομικού Σχεδίου Πόλης",
"CITY PLAN DEFINITION:"                           : u"ΚΑΘΟΡΙΣΜΟΣ ΡΥΜΟΤΟΜΙΚΟΥ ΣΧΕΔΙΟΥ",
"Polygon enclosing\ncity plan defined?"           : u"Έχει καθοριστεί το πολύγωνο\nπου περικλείει το ρυμοτομικό;",
"Define..."                                       : u"Καθορισμός...",
"Preprocessing done?"                             : u"Έχει γίνει προεπεξεργασία;",
"DTM defined?"                                    : u"Έχει γίνει ΨΜΕ;",
"CITY BLOCK PARAMETERS:"                          : u"ΠΑΡΑΜΕΤΡΟΙ ΟΙΚΟΔΟΜΙΚΩΝ ΤΕΤΡΑΓΩΝΩΝ",
"City block width (east-west):"                   : u"Πλάτος Ο.Τ. (ανατολή-δύση):",
"Min width (m)"                                   : u"Ελάχιστο πλάτος (m)",
"Max width (m)"                                   : u"Μέγιστο πλάτος (m)",
"City block height (north-south) < width:"        : u"Ύψος Ο.Τ. (βοράς-νότος) < πλάτος:",
"Min height (m)"                                  : u"Ελάχιστο ύψος (m)",
"Max height (m)"                                  : u"Μέγιστο ύψος (m)",
"Road width:"                                     : u"Πλάτος οδών:",
"Apply bioclimatic constraints?"                  : u"Εφαρμογή βιοκλιματικών κριτηρίων;",
"1 polygon enclosing the city plan must be selected": u"Πρέπει να επιλεγεί 1 πολύγωνο που περικλείει το ρυμοτομικό σχέδιο",
"Multiple executions of the algorithm"            : u"Πολλαπλές εκτελέσεις του αλγόριθμου",
"Import from file..."                             : u"Εισαγωγή απο αρχείο...",

"Bio a&zimuth"                                    : "Βιοκλιματικός προσανατολισμός",
"This command computes statistics of the azimuth of roads (lines) for bioclimatic evaluation of city plans.":
                                                    "Η εντολή αυτή υπολογίζει στατιστικά στοιχεία για τη γωνία διεύθυνσης οδών (lines) για βιοκλιματική αποτίμηση ρυμοτομικού.",
"Number of azimuth categories (enter=4): "        : "Πλήθος κλάσεων που θα χωριστούν οι γωνίες διεύθυνσης (enter=4): ",
"Select roads to process:"                        : "Επιλογή οδών προς επεξεργασία:",
}
Tarch = Translation(en2gr)
#Tarch.thanLangSet("en", thancadconf.thanTranslateTo)
del en2gr
