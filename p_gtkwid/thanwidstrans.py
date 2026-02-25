from p_ggen import Translation

#English to Greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "iso-8859-1", "gr", "iso-8859-7"),
  "Error in data"       :u"Λάθος στα δεδομένα",
  "Data modified, OK to abandon modifications?":u"Τα δεδομένα έχουν μεταβληθεί, είναι εντάξει να χαθούν οι μεταβολές;",
  "WARNING"             :u"ΠΡΟΕΙΔΟΠΟΙΗΣΗ",
  "Apply"               :u"Εφαρμογή",
  "Cancel"              :u"Ακύρωση",
  "OK"                  :u"Εντάξει",
  "Yes"                 :u"Ναι",
  "No"                  :u"Όχι",
  "Insert"              :u"Εισαγωγή",
  "Delete"              :u"Διαγραφή",
  "&New"                :u"&Νέο",
"Show bigger photo"     :u"Προβολή μεγαλύτερης φωτογραφίας",
"Clear photo"           :u"Διαγραφή φωτογραφίας",
"Save photo"            :u"Αποθήκευση φωτογραφίας",
"Choose file to save image" : u"Επιλογή αρχείου για αποθήκευση φωτογραφίας",
"Photo was not saved:"  :u"Η φωτογραφία δεν αποθηκεύτηκε:",
"Save failed"           :u"Ανεπιτυχής αποθήκευση",

#For use in the thantkcli*.py modules:

"Previous set"                                    : u"Προηγούμενες ιδιότητες",
"Next set"                                        : u"Επόμενες ιδιότητες",
"Select All"                                      : u"Επιλογή όλων",
"Deselect All"                                    : u"Αποεπιλογή όλων",
"Invert selection"                                : u"Αντιστροφή επιλογής",
"New Top Layer"                                   : u"Νέα διαφάνεια πρώτου επιπέδου",
"New Child Layer"                                 : u"Νέα θυγατρική διαφάνεια",
"Rename Layer"                                    : u"Μετονονομασία διαφάνειας",
"Copy"                                            : u"Αντιγραφή",
"Paste"                                           : u"Επικόλληση",
"Cut"                                             : u"Αποκοπή",
"Set Current"                                     : u"Ορισμός τρέχουσας",
"Create New Top Level Layer"                      : u"Δημιουργία νέας διαφάνειας πρώτου επιπέδου",
"Create New '%s' Child Layer"                     : u"Δημιουργία νέας θυγατρικής διαφάνειας της '%s'",
}

T = Translation(en2gr)
T.thanLangSet("en", "gr")
del en2gr
#T.thanReport()
