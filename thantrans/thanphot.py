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
various photogrammetric algorithms.
"""

from p_ggen import Translation
#from thanopt import thancadconf


#English to greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "utf_8", "gr", "utf_8"),
"&Photogrammetry"                                 : u"Φωτογραμμετρία",
"Image coordinate &system"                        : u"Σύστημα εινονοσυντεταγμένων",
"Rotate Image &90 deg counterclokwise"            : u"Περιστροφή εικόνας 90 μοίρες ανθωρολογιακά",
"Rotate Image &180 deg"                           : u"Περιστροφή εικόνας 180 μοίρες",
"Rotate Image &270 deg counterclokwise"           : u"Περιστροφή εικόνας 270 μοίρες ανθωρολογιακά",
"&Measure image coordinates"                      : u"Μέτρηση εικονοσυντεταγμένων",
"&Brighten Image (Gray+)"                         : u"Αύξηση φωτεινότητας εικόνων (Gray+)",
"&Darken Image (Gray-)"                           : u"Μείωση φωτεινότητας εικόνων (Gray-)",
"&Reset Image brightness"                         : u"Επαναφορά αρχικής φωτεινότητας εικόνων",

"Toggle coordinates on/off (F6)"                  : u"Ενεργοποίηση/απενεργοποίηση προβολής συντεταγμένων (F6)",
"Toggle coordinate system (F7)"                   : u"Εναλλαγή συστήματος προβολής συντεταγμένων (F7)",

"Please insert an image and retry."               : u"Παρακαλώ εισάγετε μία εικόνα και ξαναπροσπαθείστε.",
"First (left) point of x-axis: "                  : u"Πρώτο (αριστερά) σημείο του άξονα x: ",
"Second (right) point of x-axis: "                : u"Δεύτερο (δεξιά) σημείο του άξονα x: ",
"First (down) point of y-axis: "                  : u"Πρώτο (κάτω) σημείο του άξονα y: ",
"Second (up) point of y-axis: "                   : u"Δεύτερο (πάνω) σημείο του άξονα y: ",
"Y-axis does intersect x-axis (without extension). Try again."
                                                  : u"Ο άξονας y δεν τέμνει τον άξονα x1 (χωρίς επέκταση). Προσπαθείστε πάλι.",
"Interior orientation system was defined successfuly." : u"Ο ορισμός του συστήματος εικονοσυντεταγμένων ήταν επιτυχής.",
"Interior orientation system was not defined"     : u"Ο ορισμός του συστήματος εικονοσυντεταγμένων ήταν ανεπιτυχής",
"&INTERIOR ORIENTATION (pixels)"                  : u"ΕΣΩΤΕΡΙΚΟΣ ΠΡΟΣΑΝΑΤΟΛΙΣΜΟΣ (pixels)",
"INTERIOR ORIENTATION (&mm)"                      : u"ΕΣΩΤΕΡΙΚΟΣ ΠΡΟΣΑΝΑΤΟΛΙΣΜΟΣ (mm)",
"Interior orientation submenu"                    : u"Υπομενού εσωτερικού προσανατολισμού",
"Inserts an image in a predefined layer in pixels": u"Εισαγωγή εικόνας σε προκαθορισμένη διαφάνεια σε pixels",
"Load &Camera"                                    : u"Καθορισμός φωτομηχανής",
"Loads the calibrartion parameters of a metric camera": u"Φορτώνει τις παραμέτρους βαθμονόμησης της φωτομηχανής",
"Compu&tation"                                    : u"Υπολογισμός",
"Computes the photogrammetric interior orientation of a metric image":
                                                    u"Υπολογίζει το φωτογραμμετρικό εσωτερικό προσανατολισμό μετρικής εικόνας",
"&Camera management"                              : u"Διαχείριση φωτομηχανών",
"Edit/create photogrammetric camera parameters"   : u"Επεξεργασία/δημιουργία παραμέτρων φωτομηχανών",

"Photogrammetric Camera Parameters"               : u"Φωτογραμμετρικές Παράμετροι Φωτομηχανής",
"CAMERA ID:"                                      : u"ΤΑΥΤΟΤΗΤΑ ΦΩΤΟΜΗΧΑΝΗΣ:",
"Camera Name"                                     : u"Ονομασία φωτομηχανής",
"Focus Length c (mm)"                             : u"Εστιακή απόσταση c (mm)",
"CAMERA FIDUCIALS:"                               : u"ΕΙΚΟΝΟΣΗΜΑΤΑ ΦΩΤΟΜΗΧΑΝΗΣ:",
"Fiducial x (mm)"                                 : u"Εικονόσημα x (mm)",
"Fiducial y (mm)"                                 : u"Εικονόσημα y (mm)",
"Clears all camera parameters"                    : u"Διαγράφει όλες τις παραμέτρους της φωτομηχανής",
"Opens an existing camera file"                   : u"Ανοίγει ένα υφιστάμενο αρχείο φωτομηχανής",
"Saves camera parameters into current file"       : u"Αποθηκεύει παραμέτρους φωτομηχανής στο υφιστάμενο αρχείο",
"Saves camera parameters into another file"       : u"Αποθηκεύει παραμέτρους φωτομηχανής σε διαφορετικό αρχείο",
"Closes camera dialog discarding parameters"      : u"Κλείνει το διάλογο φωτομηχανής διαγράφοντας τις παραμέτρους",
"Closes camera dialog and saves parameters into current file":
                                                    u"Κλείνει το διάλογο φωτομηχανής αποθηκεύοντας τις παραμέτρους στο υφιστάμενο αρχείο",
"The x, y coordinates of a fiducial must be both numbers or blank":
                                                    u"Οι συντεταγμένες x, y ενός εικονοσήματος πρέπει αν είναι και οι δύο είτε αριθμοί είτε κενές",
"Coordinates are not permitted after a blank fiducial.":
                                                    u"Δεν επιτρέπονται συντεταγμένες μετά από ένα κενό εικονόσημα",

"1 or more images are already present.\n\nOK to replace?":
                                                    u"1 ή περισσότερες εικόνες υπάρχουν ήδη.\n\nΕντάξει να αντικατασταθούν;",
"Choose Photogrammetric camera file to open"      : u"Επιλογή αρχείου φωτομηχανής για άνοιγμα",
"Syntax error while reading focus length"         : u"Συντακτικό λάθος κατά την ανάγνωση της εστιακής απόστασης",
"Camera file"                                     : u"Αρχείο φωτομηχανής",
"Camera file was successfuly loaded."             : u"Το αρχείο φωτομηχανής φορτώθηκε επιτυχώς.",
"Photogrammetric Interior Orientation"            : u"Φωτογραμμετρικός Εσωτερικός Προσανατολισμός",
"IMAGE PARAMETERS:"                               : u"ΠΑΡΑΜΕΤΡΟΙ ΕΙΚΟΝΑΣ:",
"FIDUCIALS:"                                      : u"ΕΙΚΟΝΟΣΗΜΑΤΑ:",
"COMPUTATION:"                                    : u"ΥΠΟΛΟΓΙΣΜΟΣ:",
"Compute"                                         : u"Υπολογισμός",
"Overall error"                                   : u"Συνολικό σφάλμα",
"At least 3 fiducials should be given"            : u"Χρειάζονται τουλάχιστον 3 εικονοσήματα",
"Error in computation"                            : u"Λάθος κατά τον υπολογισμό",
"Digitize fiducial"                               : u"Ψηφιοποίηση εικονοσήματος",
"Move to and digitize fiducial"                   : u"Μετακίνηση προς, και ψηφιοποίηση εικονοσήματος",
"Clear pixel coordinates"                         : u"Διαγραφή συντεταγμένων pixel",
"Mark as invalid"                                 : u"Σημείωση ως άκυρο",
"Accept as valid"                                 : u"Αποδοχή ως έγκυρο",
"Please click on the center of fiducial"          : u"Παρακαλώ, κλικάρετε στο κέντρο του εικονοσήματος",
"Camera X (mm)"                                   : u"X φωτομηχανής (mm)",
"Camera Y (mm)"                                   : u"Y φωτομηχανής (mm)",
"Photo x (pixel)"                                 : u"x εικόνας (pixel)",
"Photo y (pixel)"                                 : u"y εικόνας (pixel)",
"Reject"                                          : u"Απόρριψη",
"Computed X (mm)"                                 : u"Υπολογισμένο X (mm)",
"Computed Y (mm)"                                 : u"Υπολογισμένο Y (mm)",
"Error X (mm)"                                    : u"Σφάλμα X (mm)",
"Error Y (mm)"                                    : u"Σφάλμα Y (mm)",
"Computation not performed, OK to close dialog?"  : u"Δέν έχει γίνει ακόμα υπολογισμός, Εντάξει να κλείσει ο διάλογος;",

"ThanCad found that the image was changed. Any previous computations "\
"have probably become invalid and must be redone.\n\nOK to continue?":
                                                    u"Το ThanCad πρόσεξε ότι η εικόνα έχει αλλάξει. "\
                                                    u"Οποιοιδήποτε προηγούμενοι υπολογισμοί πιθανότατα "\
                                                    u"δεν ισχύουν και πρέπει να ξαναγίνουν.\n\nΕντάξει για συνέχεια;",
"A camera file is already loaded. "\
"If a new camera file is loaded, "\
"any previous computations will probably become invalid "\
"and must be redone.\n\nOK to load new camera file?":
                                                    u"Ένα αρχείο φωτομηχανής έχει ήδη φορτωθεί. "\
                                                    u"Αν φορτωθεί νέο αρχείο φωτομηχανής, "\
                                                    u"οποιοιδήποτε προηγούμενοι υπολογισμοί πιθανότατα "\
                                                    u"δεν θα ισχύουν και πρέπει να ξαναγίνουν.\n\n"\
                                                    u"Εντάξει να φορτωθεί νέο αρχείο φωτομηχανής;",
"&Model definition"                               : u"Ορισμός μοντέλων",
"Defines the images which make a photogrammetric model": "Ορισμός εικόνων που απαρτίζουν φωτογραμμετρικό μοντέλο",
"&Stereo toggle"                                  : u"Ενεργοποίηση/απενεργοποίηση στερεοσκοπικής",
"Sets stereo (blue/red) mode on and off"          : u"Ενεργοποίηση και απενεργοποίηση στερεοσκοπικής όρασης (κόκκινο/κυανό)",
"&Stereo average"                                 : u"Μέσος όρος στερεοσκοπικής",
"Zooms the z coordinates so that they are easily visible": u"Εστιάζει τις συντεταγμένες z έτσι ώστε να είναι πιο εύκολα ορατές",
"&Stereo grid"                                    : u"Κάναβος στερεοσκοπικής",
"Sets a grid at the reference elevation on and off to aid stereo viewing":
                                                    u"Ενεργοποίηση/απενεργοποίηση κάναβου στο υψόμετρο αναφοράς για διευκόλυνση στερεσοκπικής όρασης",
"Photogrammetric Model Definition"                : u"Ορισμός Φωτογραμμετρικού Μοντέλου",
"MODEL DEFINITION:"                               : u"ΟΡΙΣΜΟΣ ΜΟΝΤΕΛΟΥ",
"Model Name"                                      : u"Ονομασία μοντέλου",
"Model Description"                               : u"Περιγραφή μοντέλου",
"Left image file"                                 : u"Αρχείο αριστερής εικόνας",
"Right image file"                                : u"Αρχείο δεξιάς εικόνας",

"&Rectify Map"                                    : u"Ορθοαναγωγή χάρτη",
"Rectifies a raster topographic map"              : u"Κάνει ορθοαναγωγή τοπογραφικού χάρτη (raster)",
"G&eoreference Image"                             : u"Γεωαναφορά εικόνας",
"Image georeferencing with control points"        : u"Κάνει γεωαναφορά εικόνας με φωτοσταθερά σημεία",
"&Orthoimage GDEM"                                : u"Ορθοφωτογραφία ΠΨΜΕ",
"Image orthorectification using global DEM"       : u"Ορθοαναγωγή φωτογραφίας με χρήση παγκόσμιου ΨΜΕ",
}
Tphot = Translation(en2gr)
#Tarch.thanLangSet("en", thancadconf.thanTranslateTo)
del en2gr
