# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

This is the professional part of ThanCad which is initially commercial.
"""

from math import sqrt, fabs
import sys, struct
import p_gtkuti, p_ggen
from p_gfil import openFile1, Datlin, closeFiles1
from p_gbmp import ThanBmp

#====================== Metatroph Hatt se Egsa87 ======================

def hattEgsa(com, xh, yh):
      "Convert HATT coordinates to EGSA."
      asMet = com.asMet
      bsMet = com.bsMet
      xe = asMet[0] + asMet[1]*xh + asMet[2]*yh + asMet[3]*xh*yh + \
           asMet[4]*xh**2 + asMet[5]*yh**2
      ye = bsMet[0] + bsMet[1]*xh + bsMet[2]*yh + bsMet[3]*xh*yh + \
           bsMet[4]*xh**2 + bsMet[5]*yh**2
      return xe, ye

#=======================================================================

def readGen(com):
    """Reads the general data from directly from files."""
    DOUBMIN=1.0e-10; DOUBMAX=1.0e10
    f = Datlin(com.frw["gan"], com.prt)
    try:
      f.datCom('ΜΕΤΑΤΡΟΠΗ HATT')
      com.metEgsa = f.datYesno()

      if com.metEgsa:
          readSyntel(com, f)
      elif f.datCom('ΑΡΧΕΙΟ ΣΥΝΤΕΛΕΣΤΩΝ', fail=False):
          com.prt("")
          f.wa("Το αρχείο συντελεστών δεν θα χρησιμοποιηθεί, διότι στην\nεντολή 'ΜΕΤΑΤΡΟΠΗ HATT' γράφεται 'ΟΧΙ'")
      else:
          f.datLinbac()

      f.datCom('ΒΗΜΑ ΚΑΝΑΒΟΥ')
      com.dwkan = f.datFloatR(DOUBMIN, DOUBMAX)
      try: com.dkan = f.datFloatR(DOUBMIN, DOUBMAX)
      except IOError: com.dkan = 100.0
      com.thres = com.dkan/8.0

      if f.datCom('ΑΝΑΛΥΣΗ ΕΙΚΟΝΑΣ', fail=False):
          com.prt("")
          f.wa("Η εντολή 'ΑΝΑΛΥΣΗ ΕΙΚΟΝΑΣ' δεν είναι πια απαραίτητη\n"\
               "και δεν λαμβάνεται υπόψη.")
#          com.dpi = f.datFloatR(DOUBMIN, DOUBMAX)
      else:
          f.datLinbac()

      f.datCom('ΣΥΝΤΕΤΑΓΜΕΝΕΣ ΑΡΧΗΣ')
      rx0 = f.datFloat()
      ry0 = f.datFloat()
      com.cwor = rx0, ry0

      if f.datLin(failoneof=False):
        if f.datComC('ΣΥΝΤΕΤΑΓΜΕΝΕΣ ΚΟΡΥΦΩΝ', fail=False):
          com.corners = []
          rx0 = f.datFloat()
          ry0 = f.datFloat()
          com.corners.append((rx0, ry0))
          for i in xrange(3):
              f.datLin()
              rx0 = f.datFloat()
              ry0 = f.datFloat()
              com.corners.append((rx0, ry0))

#-----Read dx, dy

      f = com.frw["dxy"]
      if f != None:
          dline = f.readline()
          try:
              com.dxMet = float(dline[10:25])
              com.dyMet = float(dline[26:40])
              com.prt("dx%f   dy=%f" % (com.dxMet, com.dyMet))
          except ValueError, why:
	      com.prt("")
              com.prt("Error: Syntax error in file .dxy:")
              com.prt("       %s" % why)
              raise p_ggen.RecordedError
      else:
          com.dxMet = com.dyMet = 0.0

#-----Read bmp header

      try: bmp = ThanBmp(com.frw["bmp"])
      except ValueError, why:
          com.prt(why)
	  raise p_ggen.RecordedError
      com.prt("Bmp resolution = %ddpi x %ddpi" % (bmp.head.hr*0.0254, bmp.head.vr*0.0254))
      com.dpi = bmp.head.hr*0.0254
      if com.dpi < 1.0:
          com.prt("")
          com.prt("Error: Image %s is probably corrupted:" % p_gtkuti.thanAbsrelPath(com.frw["bmp"].name))
	  com.prt("       The resolution seems to be less than 1 dpi!!!")
	  raise p_ggen.RecordedError
      if fabs(com.dpi-72.0) < 1.0:
          com.prt("")
          com.prt("WARNING: IMAGE %s MAY BE CORRUPTED:" % p_gtkuti.thanAbsrelPath(im.filnam))
	  com.prt("         Resolution seems to be 72dpi. This is not wrong but it")
	  com.prt("         usually indicates that the true resolution was not found")
	  com.prt("         and the scanner/graphics program put 72dpi by default.")
    except (IOError, ValueError), why:
      com.prt("\nError: %s" % why)
      raise RecordedError


def readGenTcad(com, proj, v):
      """Reads the general data from directly from ThanCad.

      The sanity checks are assumed to have been done.
      """
      DOUBMIN=1.0e-10; DOUBMAX=1.0e10
      com.metEgsa = v.chkEgsa
      com.asMet = v.entA0, v.entA1, v.entA2, v.entA3, v.entA4, v.entA5
      com.bsMet = v.entB0, v.entB1, v.entB2, v.entB3, v.entB4, v.entB5

      com.dwkan = v.entStepGr             # ΒΗΜΑ ΚΑΝΑΒΟΥ ΣΤΟ ΕΔΑΦΟΣ m
      com.dkan = v.entStepPap             # ΒΗΜΑ ΚΑΝΑΒΟΥ ΔΤΟ ΧΑΡΤΙ mm
      com.thres = com.dkan/8.0

      com.cwor = v.entXori, v.entYori     # Συντεταγμένες αρχής

      if v.chkKor:                        # Συντεταγμένες κορυφών πλαισίου
          com.corners = [(v.entKorX1, v.entKorY1),
                         (v.entKorX2, v.entKorY2),
                         (v.entKorX3, v.entKorY3),
                         (v.entKorX4, v.entKorY4),
                        ]
      com.dxMet = com.dyMet = 0.0         # Δx, Δy

#-----Read bmp header

      lay = proj[1].thanLayerTree.thanFindic("raster")
      if lay == None:
          com.prt("\nError: No layer 'raster' was found.")
          raise p_ggen.RecordedError
      im = None
      from thandr import ThanImage
      for elem in lay.thanQuad:
          if isinstance(elem, ThanImage):
              if im == None:
                  im = elem
              else:
                  com.prt("\nError: Multiple images were found in layer 'raster'.")
                  raise p_ggen.RecordedError
      if im == None:
          com.prt("\nError: No image was found in layer 'raster'.")
          raise p_ggen.RecordedError
      if not im.filnam.lower().endswith(".bmp"):
          com.prt("")
          com.prt("Error: Image %s:" % (p_gtkuti.thanAbsrelPath(im.filnam)))
          com.prt("       Image should be in .bmp format.")
          raise p_ggen.RecordedError

      try:
          bmp = ThanBmp(file(im.filnam, "rb"))
      except ValueError, why:
          com.prt("")
          com.prt("Error: Image %s is probably corrupted:" % p_gtkuti.thanAbsrelPath(im.filnam))
          com.prt("       %s" % why)
          raise p_ggen.RecordedError
#     com.prt("Bmp resolution = %ddpi x %ddpi" % (bmp.head.hr*0.0254, bmp.head.vr*0.0254)
      com.dpi = bmp.head.hr*0.0254
      if com.dpi < 1.0:
          com.prt("")
          com.prt("Error: Image %s is probably corrupted:" % p_gtkuti.thanAbsrelPath(im.filnam))
          com.prt("       The resolution seems to be less than 1 dpi.")
          raise p_ggen.RecordedError
      if fabs(com.dpi-72.0) < 1.0:
          com.prt("")
          com.prt("WARNING: IMAGE %s MAY BE CORRUPTED:" % p_gtkuti.thanAbsrelPath(im.filnam))
          com.prt("         Resolution seems to be 72dpi. This is not wrong but it")
          com.prt("         usually indicates that the true resolution was not found")
          com.prt("         and the scanner/graphics program put 72dpi by default.")
      return im.filnam

#===========================================================================

def readSyntel(com, f):
      "Reads coefficients for the HATT->EGSA transformation."
      f.datCom('ΑΡΧΕΙΟ ΣΥΝΤΕΛΕΣΤΩΝ')
      filnam = f.datStr()
      fn = filnam.rstrip().lower()
      if fn.endswith(".snt"):
          try: fr = open(filnam, "r")
          except IOError:
              com.prt('\nError: Το αρχείο συντελεστών %s δεν μπορεί να προσπελαστεί.' % p_gtkuti.thanAbsrelPath(filnam))
              raise p_ggen.RecordedError
          try:
              com.asMet = [0.0] * 6
              for i in xrange(6):
                  com.asMet[i] = float(fr.next().strip().replace("d", "e"))
              com.bsMet = [0.0] * 6
              for i in xrange(6):
                  com.bsMet[i] = float(fr.next().strip().replace("d", "e"))
          except struct.error:
              com.prt('\nError: Συντακτικό λάθος κατά την ανάγνωση του αρχείου συντελεστών %' % p_gtkuti.thanAbsrelPath(filnam))
              raise p_ggen.RecordedError
          return
      if not fn.endswith(".met"):
          filnam = p_ggen.path(filnam).namebase + ".met"
      try: fr = open(filnam, "rb")
      except IOError:
          com.prt('\nError: Το αρχείο συντελεστών %s δεν μπορεί να προσπελαστεί.' % p_gtkuti.thanAbsrelPath(filnam))
          raise p_ggen.RecordedError

      dl = fr.read()
      try:
          com.asMet = struct.unpack("=dddddd", dl[4:52])
          com.bsMet = struct.unpack("=dddddd", dl[52:100])
          com.prt(("A="+"%13.5e"*6) % com.asMet)
          com.prt(("B="+"%13.5e"*6) % com.bsMet)
      except struct.error:
          com.prt('\nError: Συντακτικό λάθος κατά την ανάγνωση του αρχείου συντελεστών %' % p_gtkuti.thanAbsrelPath(filnam))
          raise p_ggen.RecordedError

#===========================================================================

def writeFile(com):
      "Writes the pixel and EGSA coordinates of all (grid) points."
      fSyp, fNsy = com.frw["syp"], com.frw["nsy"]
      form = "K%-9s%15.3f%15.3f%15.3f%10.1f%10.1f\n"
      for i, (xp, yp, xe, ye) in enumerate(com.cfull):
          if com.metEgsa: xe, ye = hattEgsa(com, xe, ye)
          xe -= com.dxMet
          ye -= com.dyMet
          fSyp.write(form % (i, xe, ye, 0.0, xp, yp))
          fNsy.write(form % (i, xe, ye, 0.0, xp, yp))

def writeGor(com):
    "Creates the .gor file for the orthoimage program."
    form = """\
# ΕΠΕΞΗΓΗΣΕΙΣ
# 1. Η ανάλυση ανηγμένων εικόνων πρέπει να δίνεται 2 ή 3 φορές μεγαλύτερη
#    από την επιθυμητή. Στην συνέχεια η μείωση της ανάλυσης γίνεται με
#    το GIMP ή python με bicubic interpolation, διότι έτσι επιτυγχάνεται
#    καλύτερη ποιότητα.

# 2. Η μέγιστη πλευρά τριγώνου πρέπει να είναι η μέγιστη απόσταση των
#    σημείων που χρησιμοποιούνται στην ορθοαναγωγή (από το πρόγραμμα
#    τριγωνοποίησης). Για παράδειγμα:
#    α. σε ορθοφωτοχάρτη που βασίζεται σε αποτύπωση σημείων (κλ 1:500)
#       η απόσταση είναι 50m.
#    β. σε ορθοφωτοχάρτη που βασίζεται σε υψομετρικές καμπύλες της ΓΥΣ,
#       είναι η απόσταση των ισοϋψών καθώς και η απόσταση των σημείων κάθε
#       ισοϋψούς (τυπικά για χάρτη ΓΥΣ κλ 1:5000 η απόσταση είναι 250m ή
#       5cm στο χάρτη)
#    γ. για την αναγωγή χάρτου ΓΥΣ 1:5000 με κανάβους είναι η μέγιστη
#       απόσταση των κανάβων δηλαδή 500m * τετρ.ρίζα 2 = 708 m

# 3. Αν δεν οριστούν πινακίδες το πρόγραμμα φτειάχνει μία που να χωράει
#    όλες τις δεδομένες εικόνες

# 4. Στην περίπτωση χρωματισμού εικόνων (βλέπε παρακάτω), αν στην εγχρωμη εικόνα
#    υπάρχει σκια (είναι σκοτεινή ή τουλάχιστον λιγότερη φωτεινή από την
#    υπόλοιπη εικόνα) το αποτέλεσμα μερικές φορές είναι άσχημο. Το πρόγραμμα
#    έχει τη δυνατότητα να αγνοήσει τη σκιά και να μην χρωματίσει αυτό το μέρος
#    της εικόνας. Ως σκιά ορίζεται ένα χρώμα στην έγχρωμη εικόνα του οποίου
#    οι συνιστώσες κόκκινου, πράσινου και μπλέ είναι εντός 2 ορίων (min, max).
#     Ένα χρώμα θεωρείται σκιά αν και οι τρεις συνιστώσες του είναι εντός
#    των ορίων που θέτει ο χρήστης. Στο παρόν αρχείο, ως ΕΜΒΕΛΕΙΑ τοποθετούμε
#    2 ακεραίους από 0 έως 255 που είναι τα όρια (αν min<=χρώμα<=max τότε
#    το χρώμα θεωρείται σκιά).
#    Αν δεν θέλουμε να αγνοηθεί η σκιά, γράφουμε ΟΧΙ στην ερώτηση
#    ΑΓΝΟΗΣΗ ΣΚΙΑΣ ΣΕ ΧΡΩΜΑΤΙΣΜΟ; :
#    Η εμβέλεια των χρωμάτων πρέπει να καθοριστεί ακόμα και αν δεν αγνοείται
#    η σκιά (βάζουμε 0 0 σε κάθε εμβέλεια).

# 5. Παρόμοιο αποτέλεσμα έχει ο χρωματισμός όταν η ένταση (φωτεινότητα) ενός
#    έγχρωμου pixel είναι πολύ χαμηλή, οπότε στην ουσία είναι μαύρο. Αν αυτό
#    το pixel χρωματίσει pixel της γκρίζας εικόνας που τυχαίνει να είναι
#    φωτεινό, τότε το γκρίζο pixel θα μετασχηματιστεί σε κόκκινο ή πράσινο ή
#    μπλε που θα φαίνεται ως έγχρωμος θόρυβος (έγχρωμα pixels τυχαία
#    τοποθετημένα) στην ανηγμένη εικόνα.
#    Το πρόγραμμα έχει δυνατοτητα να αγνοήσει έγχρωμα pixel κάτω από μία
#    ελάχιστη φωτεινότητα. Μία λογική τιμή ελάχιστης φωτενότητας είναι 5.
#    Αν δεν θέλουμε να αγνοηθεί τα σκούρα έγχρωμα γράφουμε ΟΧΙ στην ερώτηση
#    ΑΓΝΟΗΣΗ ΣΚΟΥΡΩΝ PIXEL ΧΡΩΜΑTΙΣΜΟΥ:
#    Η ελάχιστη φωτεινότητα πρέπει να καθοριστεί ακόμα και αν δεν αγνοούνται
#    τα σκούρα pixel (βάζουμε 0).

# 6. Τρίγωνα μεγάλης κλίσης είναι συνήθως όψεις κτιρίων που φαίνονται στην
#    εικόνα λόγω πλάγιας λήψης. Τα τρίγωνα αυτά κανονικά έπρεπε να έχουν
#    άπειρη κλίση, αλλά λόγω μικροσφαλμάτων η κλίση είναι απλώς μεγάλη.
#    Στην ορθοαναγωγή τα τρίγωνα αυτά δίνουν μερικές φορές άσχημο αποτέλεσμα.
#    Το πρόγραμμα έχει τη δυνατότητα να τα αγνοήσει, αν η κλίσης τους ξεπερνά
#    μία μέγιστη κλίση. Η κλίση δίνεται επί %% ύψος/πλάτος και μία λογική τιμή
#    είναι 1000%%.
#    Αν δεν θέλουμε να αγνοηθούν τα τρίγωνα μεγάλης κλίσης γράφουμε ΟΧΙ στην
#    ερώτηση
#    ΑΓΝΟΗΣΗ ΤΡΙΓΩΝΩΝ ΜΕΓΑΛΗΣ ΚΛΙΣΗΣ :
#    Η μέγιστη κλίση πρέπει να δοθεί καθοριστεί ακόμα και αν δεν αγνοούνται
#    τα τρίγωνα μεγάλης κλίσης (βάζουμε 0).
#    Ας σημειωθεί ότι η αγνόηση τριγώνων μεγάλης κλίσης γίνεται μόνο σε
#    ορθοαναγωγή και όχι σε χρωματισμό εικόνων (είτε είναι χρωματισμός
#    ανηγμένης εικόνας είτε χρωματισμός ανεπεξέργαστης εικόνας, είτε
#    χρωματισμός εικόνας με αλλαγή γεωμετρίας.

# 7. Στο τέλος του παρόντος αρχείου δίνονται τα στοιχεία της κάθε
#    δεδομένης εικόνας:
#    filename: το αρχείο που περιέχει την εικόνα (χωρίς την κατάληξη .bmp). Το
#              αρχείο δεν πρέπει να είναι pathname (δηλαδή όχι κάτι σαν
#              c:\image\map.bmp).
#    Περ-Πάνω: Πλατος ζώνης σε pixel στην πάνω πλευρά της εικόνας.
#              Αυτή η ζώνη δεν θα ληφθεί υπόψη στην ορθοαναγωγή
#    Περ-Αριστ, Περ-Κάτω, Περ-Δεξιά: ανάλογα
#    Χρωματισμός: κενό (τίποτα), ή η λέξη COLORISER, ή η λέξη RECEIVER
#                 ή η λέξη PASSIVE_RECEIVER
#        Αν έχει τη λέξη COLORISER τότε αυτή η εικόνα χρησιμοποιείται για
#        χρωματίσει την ορθοφωτογραφία. Αν κάποιο μέρος της ορθοφωτογραφίας
#        είναι κενό, δηλαδή δεν έχει ληφθεί από άλλη εικόνα, τότε το μέρος
#        αυτό ΔΕΝ χρωματίζεται (παραμένει κενό).
#        Αν έχει τη λέξη RECEIVER ή PASSIVE_RECEIVER τότε αυτή η εικόνα
#        που κανονικά πρέπει
#        να είναι gray-scale χρωματίζεται ως έχει χωρίς να γίνεται
#        ορθοφωτογραφία. Πρέπει να υπάρχουν υποχρεωτικά και εικόνες με
#        COLORISER. Όλες οι άλλες εικόνες αγνοούνται. Επιπλέον οι εικόνες
#        με RECEIVER (ή PASSIVE_RECEIVER) και COLORISER πρέπει απαραίτητα
#        να έχουν το ίδιο
#        τριγωνισμό (αρχείο .trp) με εξαίρεση τις εικονοσυντεταγμένες.
#        Όταν μία εικόνα είναι RECEIVER παίρνει την απόχρωση της εικόνας
#        COLORISER αλλά διατηρεί τη σκουρότητά της. Αντίθετα, α είναι
#        PASSIVE_RECEIVER παίρνει και την απόχρωση και τη σκουρότητα
#        από την εικόνα COLORISER.
#        Μπορούν να χρωματιστούν παραπάνω από μία εικόνα σε κάθε τρέξιμο
#        του προγράμματος.
#
#    Για κάθε εικόνα με filename για παράδειγμα egn πρέπει να υπάρχουν τα
#    αρχεία:
#        egn.bmp: το αρχείο της εικόνας
#        egn.trp: Τριγωνισμός με σημεία δοσμένα σε συντεταγμένες ΕΓΣΑ87
#                 (ή άλλη προβολή όπου z=υψόμετρο) και σε συντεταγμένες
#                 pixel της εικόνας.
#
#
ΑΝΑΛΥΣΗ ΑΝΗΓΜΕΝΩΝ ΕΙΚΟΝΩΝ (dpi) : %.1f
ΚΛΙΜΑΚΑ ΑΝΗΓΜΕΝΩΝ ΕΙΚΟΝΩΝ       : %.1f
ΜΕΓΙΣΤΗ ΠΛΕΥΡΑ ΤΡΙΓΩΝΟΥ (m)     : %.1f
ΟΡΙΖΟΝΤΑΙ ΠΙΝΑΚΙΔΕΣ;            : ΟΧΙ

ΑΓΝΟΗΣΗ ΣΚΙΑΣ ΣΕ ΧΡΩΜΑΤΙΣΜΟ;    : ΟΧΙ
    ΕΜΒΕΛΕΙΑ ΚΟΚΚΙΝΟΥ ΣΚΙΑΣ     : 90 130
    ΕΜΒΕΛΕΙΑ ΠΡΑΣΙΝΟΥ ΣΚΙΑΣ     : 66 95
    ΕΜΒΕΛΕΙΑ ΜΠΛΕ ΣΚΙΑΣ         : 89 110

ΑΓΝΟΗΣΗ ΣΚΟΥΡΩΝ PIXEL ΧΡΩΜΑTΙΣΜΟΥ: ΟΧΙ
    ΕΛΑΧΙΣΤΗ ΦΩΤΕΙΝΟΤΗΤΑ         : 5

ΑΓΝΟΗΣΗ ΤΡΙΓΩΝΩΝ ΜΕΓΑΛΗΣ ΚΛΙΣΗΣ : ΟΧΙ
    ΜΕΓΙΣΤΗ ΚΛΙΣΗ ΤΡΙΓΩΝΩΝ %%    : 1000.0

#
#ΣΤΟΙΧΕΙΑ ΔΕΔΟΜΕΝΩΝ ΕΙΚΟΝΩΝ
#Filename  Περ-Αριστ  Περ-Κάτω Περ-Δεξιά  Περ-Πάνω  Χρωματισμός
%-10s         0         0         0         0
"""
    scale = com.dwkan / (com.dkan*0.001)
    diag = 1.5*com.dwkan                     # diagonal = 1.414*dwkan; we want it a little bigger
    if com.mapCase == "GYS5K-4":
        x1, y1 = com.corners[0]
        x3, y3 = com.corners[2]
        diag = 1.1*sqrt((x3-x1)**2+(y3-y1)**2)
    filnam = p_ggen.path(com.frw["gor"].name).namebase  # nane of the map without suffix
    com.frw["gor"].write(form % (com.dpi, scale, 3*diag, str(filnam)))
#    com.frw["gor"].write("%f\n%f\n%f\n%s\n" % (com.dpi, scale, 3*diag, str(filnam)))

#===========================================================================

def openFiles(com):
      "Opens the needed files."
      try: p_ggen.path('mediate.bat').remove()
      except OSError: pass

      openFile1(0, ' ',   ' ',   1, 'ΠΡΟΓΡΑΜΜΑ ΑΝΑΓΩΓΗΣ ΧΑΡΤΩΝ ΜΕ ΚΑΝΑΒΟ')
      openFile1(1, 'bmp', 'old', 1, 'εικόνας που περιέχει το χάρτη')
      openFile1(1, 'gan', 'old', 1, 'γενικών δεδομένων κανάβων')
      openFile1(1, 'dxp', 'old', 1, 'Συντεταγμένων pixel κανάβων')
      openFile1(1, 'dxy', 'opt', 1, 'συντεταγμένων που αφαιρούνται')
      openFile1(1, 'gor', ' ',   1, 'γενικών δεδομένων αναγωγής')

      openFile1(1, 'nb1', ' ',  -1, 'break lines')

      openFile1(1, 'syp', ' ',   1, 'αποτελεσμάτων')
      openFile1(1, 'nsy', ' ',   1, 'αντιγρ. αποτελεσμάτων')

      com.frw = openFile1(888, ' ', ' ', 1, ' ')
      filnam = com.frw["bmp"].name
      com.frw["bmp"].close()
      com.frw["bmp"] = file(filnam, "rb")

#-----Write the batch file to execute the remaining programs

      pro = p_ggen.path(com.frw["gan"].name).namebase

      linux = not p_ggen.Pyos.Windows

      if linux:
          fw=open('mediate.sh', 'w')
          fw.write('brk2pol\n')
          fw.write('echo   \\* ΠΡΟΓΡΑΜΜΑ ΤΡΙΓΩΝΟΠΟΙΗΣΗΣ\n')
          fw.write('tria -p /tmp/%s >/dev/null\n' % pro)
          fw.write('#\n')
          fw.write('pol2tri\n')
          fw.write('trp\n')
          fw.write('orthoim\n')
          fw.write('#\n')
          fw.write('rm %s.nsy\n' % pro)
          fw.write('rm %s.nb1\n' % pro)
          fw.write('rm %s.tri\n' % pro)
          fw.write('rm %s.syp\n' % pro)
      else:
          fw=open('mediate.bat', 'w')
          fw.write('brk2pol\n')
          fw.write('echo  * ΠΡΟΓΡΑΜΜΑ ΤΡΙΓΩΝΟΠΟΙΗΣΗΣ\n')
          fw.write('trw -p c:\\temp\\%s >NUL\n' % pro)
          fw.write('\n')
          fw.write('pol2tri\n')
          fw.write('trp\n')
          fw.write('orthoim\n')
          fw.write('\n')
          fw.write('del %s.nsy\n' % pro)
          fw.write('del %s.nb1\n' % pro)
          fw.write('del %s.tri\n' % pro)
          fw.write('del %s.syp\n' % pro)
      fw.close()

closeFiles = closeFiles1
