# -*- coding: iso-8859-7 -*-

##############################################################################
# ThanCad 0.0.8 "DoSomething": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c)  February 23, 2008  by Thanasis Stamos
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
ThanCad 0.0.8 "DoSomething": 2dimensional CAD with raster support for engineers.

This module computes the intersection of various geometric objects.
"""

from math import sqrt, fabs, hypot
from var import linEq2, thanNearx, fsign
from varcon import thanThresholdx
#from thanvar import thanLogC


def thanSegSeg(ca, cb, c1, c2):
      """
c-----Εύρεση τομής δύο ευθυγράμμων τμημάτων
c                                                ->     ->
c     Ο αλγόριθμος θεωρεί ότι όταν τα διανύσματα AB και 12 είναι
c     συνευθειακά δεν τέμνονται, διότι μπορεί να μην υπάρχει τομή
c     ή να υπάρχει 1 τομή ή άπειρες τομές.
c
c
c
c                                      ->   ->   ->     ->     ->
c                      o B             A2 = AT + T2 = u AB + w 12
c           o 2       /                              ->
c            \       /          Συνεπώς αναλύουμε το A2 σε δύο συνιστώσες.
c             \     /           Για να είναι η τομή εντός του AB πρέπει:
c              \   /                   0.0 <= u <= 1.0
c               \ /             Για να είναι η τομή εντός του 12 πρέπει:
c                o T                   0.0 <= w <= 1.0
c               / \             Οι συντεταγμένες της τομής βρίσκονται:
c              /   \            ->   ->   ->   ->     ->
c             /     \           RT = RA + AT = RA + u AB
c            /       \          οπου RA, RT διανυσματικές ακτίνες
c           o A       \
c                      \        w is essentially the normalised distance between T and 2
c                       \       1-w is the normalised distance between 1 and T
c                        \
c                         o 1
"""


#-----Υπολόγισε διανύσματα

      cab = cb[0] - ca[0], cb[1] - ca[1]
      c12 = c2[0] - c1[0], c2[1] - c1[1]
      ca2 = c2[0] - ca[0], c2[1] - ca[1]

#-----Ανάλυση σε δύο συνιστώσες παράληλλες προς τα 2 ευθ. τμήματα

      u, w = thanAnalVec(ca2, cab, c12)
      if u == None: return None

#-----Ελεγχος αν η τομή βρίσκεται εντος των ευθ. τμημάτων

      if u < 0.0: return None     # Τομή πριν από Α
      if u > 1.0: return None     # Τομή μετά τό Β
      if w < 0.0: return None     # Τομή πριν από 1
      if w > 1.0: return None     # Τομή μετά το 2

#-----Υπολογισμός συντεταγμένων τομής

      return ca[0] + u*cab[0], ca[1] + u*cab[1]


def thanSegSeguw(ca, cb, c1, c2, abisline=False, c12isline=False):
      """
c-----Εύρεση τομής δύο ευθυγράμμων τμημάτων
c                                                ->     ->
c     Ο αλγόριθμος θεωρεί ότι όταν τα διανύσματα AB και 12 είναι
c     συνευθειακά δεν τέμνονται, διότι μπορεί να μην υπάρχει τομή
c     ή να υπάρχει 1 τομή ή άπειρες τομές.
c
c
c
c                                      ->   ->   ->     ->     ->
c                      o B             A2 = AT + T2 = u AB + w 12
c           o 2       /                              ->
c            \       /          Συνεπώς αναλύουμε το A2 σε δύο συνιστώσες.
c             \     /           Για να είναι η τομή εντός του AB πρέπει:
c              \   /                   0.0 <= u <= 1.0
c               \ /             Για να είναι η τομή εντός του 12 πρέπει:
c                o T                   0.0 <= w <= 1.0
c               / \             Οι συντεταγμένες της τομής βρίσκονται:
c              /   \            ->   ->   ->   ->     ->
c             /     \           RT = RA + AT = RA + u AB
c            /       \          οπου RA, RT διανυσματικές ακτίνες
c           o A       \
c                      \        w is essentially the normalised distance between T and 2
c                       \       1-w is the normalised distance between 1 and T
c                        \      If absisline==True, the a-b is considered infinite line
c                         o 1   If c12isline==True, the 1-2 is considered infinite line
"""


#-----Υπολόγισε διανύσματα

      cab = cb[0] - ca[0], cb[1] - ca[1]
      c12 = c2[0] - c1[0], c2[1] - c1[1]
      ca2 = c2[0] - ca[0], c2[1] - ca[1]

#-----Ανάλυση σε δύο συνιστώσες παράληλλες προς τα 2 ευθ. τμήματα

      u, w = thanAnalVec(ca2, cab, c12)
      if u == None: return None

#-----Ελεγχος αν η τομή βρίσκεται εντος των ευθ. τμημάτων

      if not abisline:
          if u < 0.0: return None     # Τομή πριν από Α
          if u > 1.0: return None     # Τομή μετά τό Β
      if not c12isline:
          if w < 0.0: return None     # Τομή πριν από 1
          if w > 1.0: return None     # Τομή μετά το 2
      return u, 1-w


def thanLineSeg(ca, cb, c1, c2):
      """
c-----Εύρεση τομής ευθείας ca-cb με ευθ. τμήμα c1-c2
c                                                ->     ->
c     Ο αλγόριθμος θεωρεί ότι όταν τα διανύσματα AB και 12 είναι
c     συνευθειακά δεν τέμνονται, διότι μπορεί να μην υπάρχει τομή
c     ή να υπάρχει 1 τομή ή άπειρες τομές.
c
c
c
c                                      ->   ->   ->     ->     ->
c                      o B             A2 = AT + T2 = u AB + w 12
c           o 2       /                              ->
c            \       /          Συνεπώς αναλύουμε το A2 σε δύο συνιστώσες.
c             \     /           Για να είναι η τομή εντός του AB πρέπει:
c              \   /                   0.0 <= u <= 1.0
c               \ /             Για να είναι η τομή εντός του 12 πρέπει:
c                o T                   0.0 <= w <= 1.0
c               / \             Οι συντεταγμένες της τομής βρίσκονται:
c              /   \            ->   ->   ->   ->     ->
c             /     \           RT = RA + AT = RA + u AB
c            /       \          οπου RA, RT διανυσματικές ακτίνες
c           o A       \
c                      \        w is essentially the normalised distance between T and 2
c                       \       1-w is the normalised distance between 1 and T
c                        \
c                         o 1
c Για την ευθεία AB εχουμε τις εξής περιπτώσεις:
c u < 0.0          Η τομή είναι πριν από το A
c 0.0 <= u <= 1.0  Η τομή είναι εντόε του ευθ. τμήματος AB
c u > 1.0          Η τομή είναι μετά το Β
"""


#-----Υπολόγισε διανύσματα

      cab = cb[0] - ca[0], cb[1] - ca[1]
      c12 = c2[0] - c1[0], c2[1] - c1[1]
      ca2 = c2[0] - ca[0], c2[1] - ca[1]

#-----Ανάλυση σε δύο συνιστώσες παράληλλες προς τα 2 ευθ. τμήματα

      u, w = thanAnalVec(ca2, cab, c12)
      if u == None: return None

#-----Ελεγχος αν η τομή βρίσκεται εντος των ευθ. τμημάτων

#      if u < 0.0: return None     # Τομή πριν από Α
#      if u > 1.0: return None     # Τομή μετά τό Β
      if w < 0.0: return None     # Τομή πριν από 1
      if w > 1.0: return None     # Τομή μετά το 2

#-----Υπολογισμός συντεταγμένων τομής

      return (ca[0] + u*cab[0], ca[1] + u*cab[1]), u


def thanLineSeg2(C, t, A, B):
      """
c-----Βρίσκει τομή ευθείας (C+λ*t) και ευθ. τμήματος  (AB)

c                                  o B
c                                 / \
c                               /     \               t
c                         TOM /         \  C         -->
c   ------------------------o-------------o------------------
c                         /            .
c                       /          .
c                     /        .
c                   /      .
c                 /    .
c               /  .
c           A o


c-----A, B : δύο σημεία που ορίζουν το ευθ. τμήμα
c     t    : Μοναδιαίο διάνυσμα στη διεύθυνση της ευθείας
c     C    : Ενα σημείο της ευθείας
c     TOM  : τομή ευθ. τμήματος και ευθείας
      """
      n = -t[1], t[0]                   # μοναδιαίο κάθετο διάνυσμα στην ευθεία
      ca = A[0] - C[0], A[1] - C[1]
      Kca = ca[0] * n[0] + ca[1] * n[1]
      cb = B[0] - C[0], B[1] - C[1]
      Kcb = cb[0] * n[0] + cb[1] * n[1]

#-----find intersection if it exists

      inters = fsign(1.0, Kca) * fsign(1.0, Kcb) <= 0.0
      if inters:
          cb = B[0] - A[0], B[1] - A[1]      # διάνυσμα ab
          Kcb = cb[0] * n[0] + cb[1] * n[1]
          Kcb = fabs(Kca / Kcb)              # αναλογία ac/ab
          return A[0] + cb[0] * Kcb, A[1] + cb[1] * Kcb
      return None


def thanLineSeg3(pn, n, A, B):
    """Finds the intersection between line segment and line perpendicular to n, whose projection on n axis is pn."
c    |
c    | ^
c    | |n
c    | |
c  b o    .    .    .    .    .    o B
c    |                            /
c    |                          /
c    |                    TOM /
c  t-o----------------------o--------------------------------
c    |                    /
c    |                  /
c    |                /
c    |              /
c    |            /
c    |          /
c  a o   .    o  A
c    |
c    |
c    |
c    |
c    O


c-----A, B : δύο σημεία που ορίζουν το ευθ. τμήμα
c     n    : Μοναδιαίο διάνυσμα κάθετο στη διεύθυνση της ευθείας
c     Ο    : Αρχή του συστήματος συντεταγμένων (οι άξονες έχουν αυθαίρετη κλίση
c            και δεν φαίνονται στο σχήμα)
c     TOM  : τομή ευθ. τμήματος και ευθείας
c     pt   : Προβολή όλων των σημείων της ευθείας (και συνεπώς και της τομής)
c            σε άξονα παράλληλο προς n που περνάει από την αρχή των αξόνων (άξονας n)
c     pa   : Προβολή του OA στον άξονα n
c     pb   : Προβολή του OB στον άξονα n
"""
    from var import linint
    pna = n[0]*A[0] + n[1]*A[1]
    pnb = n[0]*B[0] + n[1]*B[1]
    if fsign(1.0, pna-pn)*fsign(1.0, pnb-pn) > 0.0: return None
    ct = [linint(pna, a, pnb, b, pn) for a,b in zip(A, B)]
    return ct


def thanSegCir(ca, cb, cc, rc):
    """Finds intersection of linear segment ca-cb and circle.


                   --
               o        o
   a---------1------m-----2------------b               d   = distance from a to b
            o       |      o                           tab = tangential unit vector from a to b
            |       C      |                           nab = normal unit vector to line ab
            o              o                           vac = vector from a to c
             o            o                            dn  = normal distance of circle center to line ab (from C to m)
               o        o                              tm  = signed distance from a to m (m may not be inside ab)
                   --                                  dt  = distance from intersection 1 or intersection 2 to point m



    """
    dc = cb[0]-ca[0], cb[1]-ca[1]
    d = hypot(*dc)
    if d == 0: return []                 # Line segment is a dot
    tab = dc[0]/d, dc[1]/d
    nab = -tab[1], tab[0]
    vac = cc[0]-ca[0], cc[1]-ca[1]
    dn = vac[0]*nab[0] + vac[1]*nab[1]
    if fabs(dn) > rc: return []          # No intersections
    cm = cc[0]-dn*nab[0], cc[1]-dn*nab[1]
    tm = (cm[0]-ca[0])*tab[0] + (cm[1]-ca[1])*tab[1]
    if fabs(dn) == rc:
	if 0.0 <= tm <= d: return [cm]   # 1 intersection
	else:              return []     # Intersection out of segment
    dt = sqrt(rc**2-dn**2)
    ps = []
    if 0.0 <= tm-dt <= d:                # intersection in segment
        ps.append((cm[0]-dt*tab[0], cm[1]-dt*tab[1]))
    if 0.0 <= tm+dt <= d:                # intersection in segment
        ps.append((cm[0]+dt*tab[0], cm[1]+dt*tab[1]))
    return ps

def thanCirCir(ca, ra, cb, rb):
    """Finds intersection of 2 circles.

                   o o                x x
              o           o       x         x
          o                  .1.                x
        o                  /x | o\                x
       o                 / x  |  o \               x        d   = distance from Ca to Cb
                       /      |      \                      tab = tangential unit vector from Ca to Cb
      o             Ca----x---f---o----Cb           x       nab = normal unit vector to line Ca-Cb
      o                   x   |   o                 x       dt  = distance from Ca to f (it may be negative)
                              |                             dn = distance from f to 1
       o                   x  |  o                 x        cf  = coordinates of point f
        o                   x | o                 x         c1, c2 = coordinates of the 2 intersection points
          o                   2                 x
	      o           o       x         x
	           o o                x x


    """
    if ra < thanThresholdx or rb < thanThresholdx:
        print "Warning: Radius of circles must be positive >%s" % thanThresholdx
        return []
    dc = cb[0]-ca[0], cb[1]-ca[1]
    d = hypot(*dc)
    if d < thanThresholdx: return []     # Concentric circles; no intersection or identical
    srab = ra+rb
    if d > srab: return []               # No intersections
    if ra > rb: rmax=ra; rmin=rb
    else:       rmin=ra; rmax=rb
    if rmax-d > rmin: return []          # No intersections
    tab = dc[0]/d, dc[1]/d
    if thanNearx(srab, d) or thanNearx(rmax-d, rmin):
        return [(ca[0]+tab[0]*ra, ca[1]+tab[1]*ra)]  # 1 intersection
    nab = -tab[1], tab[0]
#   dt = (ra**2 - rb**2 + d**2) / (2*d) = ((ra+rb)*(ra-rb) + d**2) / (2*d) =>
    dt = (srab*(ra-rb)/d + d) * 0.5
#   dn = sqrt(ra**2-dt**2) =>
    dn = sqrt((ra+dt)*(ra-dt))
    for dt in (-dt, dt):                 # Try both solutions (+-dt)
        cf = ca[0] + tab[0]*dt, ca[1] + tab[1]*dt
        c1 = cf[0] + nab[0]*dn, cf[1] + nab[1]*dn
	rb1 = hypot(c1[0]-cb[0], c1[1]-cb[1])
	if thanNearx(rb1, rb): break
    else:
        print "Algorithm failure in circles' intersection"
	return []

    c2 = cf[0] - nab[0]*dn, cf[1] - nab[1]*dn
    return [c1, c2]

def thanAnalVec(self, da, db):
      """
#---It analyzes self into two non-colinear vectors da and db.
#   It solves the vector system:
#
#      ->     ->    ->
#    a DA + b DB = SELF
#
"""
      return linEq2 (da[0], db[0], self[0], da[1], db[1], self[1])
