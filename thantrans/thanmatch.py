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
various matching algorithms.
"""

from p_ggen import Translation
#from thanopt import thancadconf


#English to greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "iso-8859-1", "gr", "iso-8859-7"),
"&Match 2d"                                       : u"Συνταύτιση 2Δ",
"&Match 3d to 2d"                                 : u"Συνταύτιση 3Δ σε 2Δ",
"&Match 3d"                                       : u"Συνταύτιση 3Δ",
"&Match multiple 2d"                              : u"Πολλαπλή Συνταύτιση 2Δ",
"&Mid axis"                                       : u"Μέσος άξονας",
"&Project 3d to 2d"                               : u"Προβολή 3Δ σε 2Δ",
"&Compute transformation"                         : u"Υπολογισμός μετασχηματισμού",
"Computes a transformation from control points"   : u"Υπολογίζει μετασχηματισμό από φωτοσταθερά",

"Global Matching of 2D Curves"                    : u"Ολική Συνταύτιση Διδιάστατων Γραμμών",
"Global Matching of 3D Curves"                    : u"Ολική Συνταύτιση Τρισδιάστατων Γραμμών",
"Select the\nreference line"                      : u"Επιλογή\nγραμμής αναφοράς",
"Select the line to be moved\ntowards the reference line": u"Επιλογή γραμμής που θα μετακινηθεί\nπρος τη γραμμή αναφοράς",
"Select the reference line:\n"                    : u"Επιλογή γραμμής αναφοράς\n",
"Select the line to be moved towards the reference line:\n": u"Επιλογή γραμμής που θα μετακινηθεί προς τη γραμμή αναφοράς\n",
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
"Lab of Photogrammetry, NTUA, "                   : u"Εργαστήριο Φωτογραμμετρίας, ΕΜΠ, ",
"ICP GENERAL PARAMETERS:"                         : u"ΓΕΝΙΚΕΣ ΠΑΡΑΜΕΤΡΟΙ ICP:",
"Interpolation Distance (m)"                      : u"Απόσταση παρεμβολής (m)",
"Distance Range (m)"                              : u"Μέγιστη απόσταση αναζήτησης",
"Convergence threshold (m)"                       : u"Όριο σύγκλισης (m)",
"Max number of steps"                             : u"Μέγιστος αριθμός βημάτων",
"PROJECTION TYPE:"                                : u"ΕΙΔΟΣ ΠΡΟΒΟΛΗΣ:",
"Polynomial Projection of first order"            : u"Πολυωνυμική Προβολή 1ου βαθμού",
"Direct Linear Transform"                         : u"Ευθύς Γραμμικός Μετασχηματισμός",
"Rational Polynomial Projection of first order"   : u"Κλασματική Πολυωνυμική Προβολή 1ου βαθμού",
"Polynomial Projection of second order"           : u"Πολυωνυμική Προβολή 2ου βαθμού",
"Rational Polynomial Projection of second order"  : u"Κλασματική Πολυωνυμική Προβολή 2ου βαθμού",
"Rational Polynomial Projection of 2/1 order"     : u"Κλασματική Πολυωνυμική Προβολή 2ου/1ου βαθμού",
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
"Select the reference (3D) line\n"                : u"Επιλογή της γραμμής αναφοράς (3Δ)\n",
"Select the projected (2D) line\n"                : u"Επιλογή της γραμμής προβολής (2Δ)\n",

"Image Registration with Control Points"          : u"Συσχέτιση Εικόνας με Φωτοσταθερά",
"COMPUTATION TYPE:"                               : u"ΟΡΙΣΜΟΣ ΥΠΟΛΟΓΙΣΜΟΥ:",
"Compute projection/transformation"               : u"Υπολογισμός προβολής/μετασχηματισμού",
"Compute error using checkpoints"                 : u"Υπολογισμός σφάλματος με χρήση σημείων ελέγχου",
"Computation type"                                : u"Ορισμός υπολογισμού",
"TRANSFORMATION TYPE:"                            : u"ΕΙΔΟΣ ΜΕΤΑΣΧΗΜΑΤΙΣΜΟΥ:",
"Projections"                                     : u"Προβολές",
"2D Transformations"                              : u"Μετασxηματισμοί 2Δ",
"Polynomial of first order"                       : u"Πολυώνυμο 1ου βαθμού",
"Rational Polynomial of first order"              : u"Κλασματικό πολυώνυμο 1ου βαθμού",
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
