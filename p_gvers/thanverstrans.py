from p_ggen import Translation

#English to Greek translation table
en2gr = \
{ "__TRANSLATION__" : ("en", "iso-8859-1", "gr", "iso-8859-7"),
  "URL"             : u"Σελίδα",
  "e-mail"          : u"ΗΛ-ΤΑ",
  " by "            : u" από ",
  "(Not available)" : u"(Δεν υπάρχει)",
  "Copyright (C)"   : u"Πνευματικά δικαιώματα"
}

T = Translation(en2gr)
del en2gr
#T.thanReport()
