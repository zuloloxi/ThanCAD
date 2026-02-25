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
various matching algorithms.
"""

from p_ggen import Translation
#from thanopt import thancadconf


#English to greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "utf_8", "gr", "utf_8"),




"&Match 2d"                                       : u"Συνταύτιση 2Δ",
"&Match 3d to 2d"                                 : u"Συνταύτιση 3Δ προς 2Δ",
"&Match 3d"                                       : u"Συνταύτιση 3Δ",
"&Match 3d splines"                               : u"Συνταύτιση κυβικών καμπυλών 3Δ",
"&Match multiple 2d"                              : u"Πολλαπλή Συνταύτιση 2Δ",
"&Mid axis"                                       : u"Μέσος άξονας",
"&Project/transform"                              : u"Εκτέλεση προβολής/μετασχηματισμού",
"Projects/transforms arbitrary ThanCad Elements using a known transform (2D-2D, 3D-2D, 3D-3D":
                                                    u"Προβάλλει/μετασχηματίζει αυθαίρετα στοιχεία του ThanCad "\
                                                    u"χρησιμοποιώντας γνωστό μετασχηματισμό (2Δ-2Δ, 3Δ-2Δ, 3Δ-3Δ)",
"&Compute projection"                             : u"Υπολογισμός προβολής",
"Computes a transformation from control points"   : u"Υπολογίζει μετασχηματισμό από φωτοσταθερά",

"Matches two 2d polylines"                        : u"Συνταύτιση δύο γραμμών 2Δ",
"Matches one 3d polyline to one 2d polylines"     : u"Συνταύτιση μίας γραμμής 3Δ προς μία γραμμή 2Δ",
"Matches two 3d polylines"                        : u"Συνταύτιση δύο γραμμών 3Δ",
"Matches two 3d cubic splines"                    : u"Συνταύτιση δύο κυβικών γραμμών 3Δ",
"Matches two sets of 2d polylines"                : u"Συνταύτιση δύο συνόλων από γραμμές 2Δ",
"&Match multiple 3d to 2d"                        : u"Πολλαπλή Συνταύτιση 3Δ προς 2Δ",
"Matches one set of 3d polylines to one set of 2d polylines"
                                                  : u"Συνταύτιση ενός συνόλου γραμμών 3Δ προς ένα σύνολο γραμμών 2Δ",
"Computes middle axis of road given the road edges":u"Υπολογισμός μέσου άξονα οδού από τις οριογραμμές του",
"Select the 2 edges of a road:\n"                 : u"Επιλογή των 2 οριογραμμών της οδού:\n",
"Computes a projection transformation using control points":
                                                    u"Υπολογισμός μετασχηματισμού προβολής με φωτοσταθερά",
"Global Matching of FFLF networks of different Dimensionality":
                                                    u"Ολική Συνταύτιση δικτύων FFLF διαφορετικής Διάστασης",
"Select the\nsecondary (3D) lines"                : u"Επιλογή δευτερευουσών\n γραμμών (3Δ)",
"Select the\nreference (2D) lines"                : u"Επιλογή γραμμών\nαναφοράς (2Δ)",
"Select the secondary (3D) lines\n"               : u"Επιλογή δευτερευουσών γραμμών (3Δ)\n",
"Select the reference (2D) lines\n"               : u"Επιλογή γραμμών αναφοράς (2Δ)\n",
"Select the reference (3D) line\n"                : u"Επιλογή γραμμής αναφοράς (3Δ)\n",
"2D polynomial approximation"                     : u"Πολυωνυμική προσέγγιση 2Δ",
"Global Matching of 2D Curves"                    : u"Ολική Συνταύτιση Διδιάστατων Γραμμών",
"Global Matching of 3D Curves"                    : u"Ολική Συνταύτιση Τρισδιάστατων Γραμμών",
"Global Matching of 3D cubic Splines"             : u"Ολική Συνταύτιση Τρισδιάστατων Κυβικών Γραμμών",
"Select the\nreference line"                      : u"Επιλογή\nγραμμής αναφοράς",
"Select the line to be moved\ntowards the reference line": u"Επιλογή γραμμής που θα μετακινηθεί\nπρος τη γραμμή αναφοράς",
"Select the reference line:\n"                    : u"Επιλογή γραμμής αναφοράς\n",
"Select the line to be moved towards the reference line:\n": u"Επιλογή γραμμής που θα μετακινηθεί προς τη γραμμή αναφοράς\n",
"Select the\nreference spline"                    : u"Επιλογή κυβικής\nγραμμής αναφοράς\n",
"Select the spline to be moved\ntowards the reference spline": u"Επιλογή κυβικής γραμμής που θα μετακινηθεί\nπρος τη κυβική γραμμή αναφοράς\n",
"SELECT LINES (the lines bust be cubic splines):" : u"ΕΠΙΛΟΓΗ ΓΡΑΜΜΩΝ (οι γραμμές πρέπει να είναι κυβικές)",
"PREALIGNMENT:"                                   : u"ΠΡΟ-ΕΥΘΥΓΡΑΜΜΙΣΗ:",
"Centroid method"                                 : u"Μέθοδος κεντροειδούς",
"Distance method"                                 : u"Μέθοδος απόστασης",
"AZIMOUTH APPROXIMATION:"                         : u"ΠΡΟΣΕΓΓΙΣΗ ΑΖΙΜΟΥΘΙΟΥ:",
"Average of first and last node"                  : u"Μέσος όρος πρώτου και τελευταίου κόμβου",
"Exhaustive search of all azimouths"              : u"Εξονυχιστική έρευνα όλων των αζιμουθίων",
"Average azimouth of whole curve"                 : u"Μέσο αζιμούθιο όλης της γραμμής",
"1 slave line must be selected"                   : u"Πρέπει να γίνει επιλογή 1 δευτερεύουσας γραμμής",

"Multiple Curve Global Matching"                  : u"Ολική Συνταύτιση Πολλαπλών Γραμμών",
"Multiple Curve Matching Algorithms"              : u"Αλγόριθμοι Συνταύτισης Πολλαπλών Γραμμών",
"Dimitra Vassilaki, PhD Candidate"                : u"Δήμητρα Βασιλάκη, Υποψήφια Διδάκτορας",
"Dr. Eng. Dimitra Vassilaki"                      : u"Δρ. Δήμητρα Βασιλάκη",
"Select the\nreference lines"                     : u"Επιλογή\nγραμμών αναφοράς",
"Select the lines to be moved\ntowards the reference lines": u"Επιλογή γραμμών που θα μετακινηθούν\nπρος τις γραμμές αναφοράς",
"Select the reference lines:\n"                     : u"Επιλογή γραμμών αναφοράς:\n",
"Select the lines to be moved towards the reference lines:\n": u"Επιλογή γραμμών που θα μετακινηθούν προς τις γραμμές αναφοράς:\n",
"(%d selected)"                                   : u"(%d επιλεγμένες)",
"CORRESPONDENCE METHOD:"                          : u"ΜΕΘΟΔΟΣ ΑΝΤΙΣΤΟΙΧΙΣΗΣ:",
"Distance of Line Ends"                           : u"Απόσταση άκρων",
"Distance of centroids"                           : u"Απόσταση κεντροειδών",
"Absolute length difference"                      : u"Απόλυτη διαφορά μήκους",
"Average distance with partial ICP application"   : u"Μέση απόσταση με μερική εφαρμογή ICP",
"RMS with full ICP application"                   : u"RMS με πλήρη εφαρμογή ICP",
"Hybrid (ends, centroid, full ICP)"               : u"Υβριδική (άκρα, κεντροειδές, πλήρης ICP)",
"PREALIGNMENT (BEFORE CORRESPONDENCE):"           : u"ΠΡΟ-ΕΥΘΥΓΡΑΜΜΙΣΗ (ΠΡΙΝ ΤΗΝ ΑΝΤΙΣΤΟΙΧΙΣΗ):",
"Centroid method using convex hull"               : u"Μέθοδος κεντροειδούς με χρήση περιγεγραμμένου κυρτού πολυγώνου",
"Centroid method using all curves"                : u"Μέθοδος κεντροειδούς με χρήση όλων των γραμμών",
"None"                                            : u"Καμμία",
"PREALIGNMENT (AFTER CORRESPONDENCE):"            :  u"ΠΡΟ-ΕΥΘΥΓΡΑΜΜΙΣΗ (ΜΕΤΑ ΤΗΝ ΑΝΤΙΣΤΟΙΧΙΣΗ):",
"Individual centroid method for each pair of curves": u"Μέθοδος κεντροειδούς ανεξάρτητη για κάθε ζεύγος γραμμών",
"Individual full ICP method for each pair of curves": u"Μέθοδος πλήρους ICP ανεξάρτητη για κάθε ζεύγος γραμμών",
"Global Matching of Curves of different Dimensionality": u"Ολική Συνταύτιση Γραμμών Διαφορετικών Διαστάσεων",
"Curve Matching Algorithms"                       : u"Αλγόριθμοι Συνταύτισης Γραμμών",
"3D Cubic Splines Matching"                       : u"Συνταύτιση κυβικών γραμμών 3Δ",
"Lab of Photogrammetry, NTUA, "                   : u"Εργαστήριο Φωτογραμμετρίας, ΕΜΠ, ",
"ICP GENERAL PARAMETERS:"                         : u"ΓΕΝΙΚΕΣ ΠΑΡΑΜΕΤΡΟΙ ICP:",
"MATCHING PARAMETERS:"                            : u"ΠΑΡΑΜΕΤΡΟΙ ΣΥΝΤΑΥΤΙΣΗΣ:",
"Interpolation Distance (m)"                      : u"Απόσταση παρεμβολής (m)",
"Distance Range (m)"                              : u"Μέγιστη απόσταση αναζήτησης",
"Convergence threshold (m)"                       : u"Όριο σύγκλισης (m)",
"Max number of steps"                             : u"Μέγιστος αριθμός βημάτων",
"PROJECTION TYPE:"                                : u"ΕΙΔΟΣ ΠΡΟΒΟΛΗΣ:",
"Central Projection (collinearity)"               : u"Κεντρική Προβολή (συγγραμμικότητα)",
"Polynomial Projection of first order"            : u"Πολυωνυμική Προβολή 1ου βαθμού",
"Direct Linear Transform"                         : u"Ευθύς Γραμμικός Μετασχηματισμός",
"Rational Polynomial Projection of first order"   : u"Ρητή Πολυωνυμική Προβολή 1ου βαθμού",
"Polynomial Projection of second order"           : u"Πολυωνυμική Προβολή 2ου βαθμού",
"Rational Polynomial Projection of second order"  : u"Ρητή Πολυωνυμική Προβολή 2ου βαθμού",
"Rational Polynomial Projection of 2/1 order"     : u"Ρητή Πολυωνυμική Προβολή 2ου/1ου βαθμού",
"Projection type"                                 : u"Είδος προβολής",
"SELECT LINES:"                                   : u"ΕΠΙΛΟΓΗ ΓΡΑΜΜΩΝ:",
"Select the\nsecondary (3D) line"                 : u"Επιλογή δευτερεύουσας\n γραμμής (3Δ)",
"Select the\nreference (2D) line"                 : u"Επιλογή\nγραμμής αναφοράς (2Δ)",
"PURE PROJECTION APPROXIMATION:"                  : u"ΠΡΟΣΕΓΓΙΣΗ ΚΑΘΑΡΗΣ ΠΡΟΒΟΛΗΣ:",
"Projection to XY-plane (aerial/satellite images)": u"Προβολή στο επίπεδο XY (αεροφωτογραφίες/δορυφορικές)",
"Projection to known plane (lidar)"               : u"Προβολή προς γνωστό επίπεδο (lidar)",
"Known projection coefficients"                   : u"Γνωστοί συντελεστές προβολής",
"Exhaustive search for projection plane"          : u"Εξονυχιστική διερεύνηση για το επίπεδο προβολής",
"First Approximation of pure projection"          : u"Πρώτη προσέγγιση για την καθαρή προβολή",
"File of projection coefficients"                 : u"Αρχείο συντελεστών προβολής",
"Normal unit vector of projection plane"          : u"Μοναδιαίο κάθετο διάνυσμα του επιπέδου προβολής",
"PURE TRANSFORMATION APPROXIMATION:"              : u"ΠΡΟΣΕΓΓΙΣΗ ΚΑΘΑΡΟΥ ΜΕΤΑΣΧΗΜΑΤΙΣΜΟΥ:",
"None (identity transformation)"                  : u"Καμμία (μοναδιαίος μετασχηματισμός)",
"2D similarity approximation"                     : u"Προσέγγιση ομοιότητας 2Δ",
"Distance algorithm"                              : u"Αλγόριθμος αποστάσεων",
"1 reference line must be selected"               : u"Πρέπει να γίνει επιλογή 1 γραμμής αναφοράς",
"1 projected line must be selected"               : u"Πρέπει να γίνει επιλογή 1 γραμμής προβολής",
"Error in data"                                   : u"Λάθος στα δεδομένα",
"Select the secondary (3D) line\n"                : u"Επιλογή της δευτερεύουσας γραμμής (3Δ)\n",
"Select the reference (2D) line\n"                : u"Επιλογή της γραμμής αναφοράς (2Δ)\n",

"Image Registration with Control Points"          : u"Συσχέτιση Εικόνας με Φωτοσταθερά",
"COMPUTATION TYPE:"                               : u"ΟΡΙΣΜΟΣ ΥΠΟΛΟΓΙΣΜΟΥ:",
"Compute projection/transformation"               : u"Υπολογισμός προβολής/μετασχηματισμού",
"Compute error using checkpoints"                 : u"Υπολογισμός σφάλματος με χρήση σημείων ελέγχου",
"Computation type"                                : u"Ορισμός υπολογισμού",
"Transformation type"                             : u"Είδος μετασχηματισμού",
"3D-2D"                                           : u"3Δ-2Δ",
"2D-2D"                                           : u"2Δ-2Δ",
"Polynomial of first order"                       : u"Πολυώνυμο 1ου βαθμού",
"Rational Polynomial of first order"              : u"Ρητό πολυώνυμο 1ου βαθμού",
"Polynomial of second order"                      : u"Πολυώνυμο 2ου βαθμού",
"TRANSFORMATION DEFINITION:"                      : u"ΟΡΙΣΜΟΣ ΜΕΤΑΣΧΗΜΑΤΙΣΜΟΥ:",
"SELECTION OF CONTROL POINTS:"                    : u"ΕΠΙΛΟΓΗ ΦΩΤΟΣΤΑΘΕΡΩΝ:",
"Drawing/layer of reference points"               : u"Σχέδιο/διαφάνεια σημείων αναφοράς",
"Drawing/layer of image points"                   : u"Σχέδιο/διαφάνεια σημείων εικόνας",
"Control point status"                            : u"Κατάσταση φωτοσταθερών σημείων",
"Check point status"                              : u"Κατάσταση σημείων ελέγχου",
"SELECTION OF CHECK POINTS:"                      : u"ΕΠΙΛΟΓΗ ΣΗΜΕΙΩΝ ΕΛΕΓΧΟΥ:",
"Pixel error"                                     : u"Σφάλμα pixel",
"3D error"                                        : u"Σφάλμα 3Δ",
"Transfomation error (using checkpoints)"         : u"Σφάμα μετασχηματισμού (με χρήση σημείων ελέγχου)",
"Open file with transformation/projection coefficients": u"Άνοιγμα αρχείου συντελεστών μετασχηματισμού/προβολής",
}
Tmatch = Translation(en2gr)
#Tmatch.thanLangSet("en", thancadconf.thanTranslateTo)
del en2gr
