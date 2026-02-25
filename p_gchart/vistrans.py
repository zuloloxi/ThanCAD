# -*- coding: iso-8859-7 -*-

from p_ggen import Translation

##############################################################################
##############################################################################

#English to greek translation table
en2gr = \
{ "__TRANSLATION__"     : ("en", "iso-8859-1", "gr", "iso-8859-7"),
  "Error in data"       :"Λάθος στα δεδομένα",
  "Values have changed.\nAbandon changes?":"Οι τιμές μεταβλήθηκαν\nΝα ακυρωθούν οι μεταβολές;",
  "WARNING"             :"ΠΡΟΕΙΔΟΠΟΙΗΣΗ",
  "Apply"               :"Εφαρμογή",
  "Cancel"              :"Ακύρωση",
  "OK"                  :"Εντάξει",
  "Yes"                 :"Ναι",
  "No"                  :"Οχι",
  "Insert"              :"Εισαγωγή",
  "Delete"              :"Διαγραφή",
  "&New"                :"&Νέο"
}
T = Translation(en2gr)
T.thanLangSet("en", "gr")
del en2gr
#T.thanReport()
