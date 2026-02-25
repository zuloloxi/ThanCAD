"""\
This module defines various information for the translation from English to Greek
and other languages. This module is specific to the modules which implement the
GUI of p_gfil.
"""

from .thantrans import Translation


#English to greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "iso-8859-1", "gr", "iso-8859-7"),
"&File"                                           : "Αρχείο",
"&Save program output"                            : "Αποθήκευση εξόδου προγράμματος",
"E&xit"                                           : "Έξοδος",
"Save the text of the program output"             : "Αποθήκευση του κειμένου που τύπωσε το πρόγραμμα στο παράθυρο",
"Close GUI"                                       : "Κλείσιμο της γραφικής διεπαφής (GUI)",



"Warning at line %d of file %s:\n%s"              : "Προειδοποίηση στη γραμμή %d του αρχείου %s:\n%s",
"Error at line %d of file %s:\n%s"                : "Λάθος στη γραμμή %d του αρχείου %s:\n%s",
"Syntax error at line %d of file %s:\n%s"         : "Συντακτικό λάθος στη γραμμή %d του αρχείου %s:\n%s",
"Unexpected end of file"                          : "απροσδόκητο τέλος αρχείου",
"Error while executing program"                   : "Λάθος κατά την εκτέλεση του προγράμματος",
"Error while executing external program"          : "Λάθος κατά την εκτέλεση εξωτερικού προγράμματος",
"Details were recorded on output window"          : "Περισσότερες λεπτομέρειες στο παράθυρο εξόδου",
"ERROR executing"                                 : "ΛΑΘΟΣ κατα την εκτέλεση",
"Close this window to finish.."                   : "Κλείστε αυτό το παράθυρο για τερματισμό..",
}

Tgui = Translation(en2gr)
Tgui.thanLangSet("en", "gr")
del en2gr
#Tgui.thanReport()
