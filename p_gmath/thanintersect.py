"This module computes the intersection of various geometric objects."
from math import sqrt, fabs, hypot
from .lineq import linEq2
from .var import thanNearx, fsign, linint, thanNearzero
from .varcon import thanThresholdx


def thanSegSeg(ca, cb, c1, c2, abisline=False, c12isline=False):
    "Εύρεση συντεταγμένων τομής δύο ευθυγράμμων τμημάτων ή ευθειών."
    res = thanSegSegGen(ca, cb, c1, c2, abisline, c12isline)
    if res is None: return res
    return res[0]


def thanSegSeguw(ca, cb, c1, c2, abisline=False, c12isline=False):
    "Εύρεση τοπικών συντεταγμένων τομής δύο ευθυγράμμων τμημάτων ή ευθειών."
    res = thanSegSegGen(ca, cb, c1, c2, abisline, c12isline)
    if res is None: return res
    return res[1]


def thanLineSeguw(ca, cb, c1, c2, abisline=True, c12isline=False):
    "Εύρεση τοπικών συντεταγμένων τομής ευθείας ca-cb με ευθ. τμήμα c1-c2 "
    res = thanSegSegGen(ca, cb, c1, c2, abisline, c12isline)
    if res is None: return res
    return res[1]


def thanSegSegGen(ca, cb, c1, c2, abisline=False, c12isline=False):
      r"""
c-----Εύρεση συντεταγμένων και τοπικών συντεταγμένων τομής δύο ευθυγράμμων τμημάτων ή ευθειών
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
      if u is None: return None

#-----Ελεγχος αν η τομή βρίσκεται εντος των ευθ. τμημάτων

      if not abisline:
          if u < 0.0 and not thanNearx(u+1.0, 1.0): return None     # Τομή πριν από Α
          if u > 1.0 and not thanNearx(u,     1.0): return None     # Τομή μετά τό Β
      if not c12isline:
          if w < 0.0 and not thanNearx(w+1.0, 1.0): return None     # Τομή πριν από 1
          if w > 1.0 and not thanNearx(w,     1.0): return None     # Τομή μετά το 2

#-----Υπολογισμός συντεταγμένων τομής

      return (ca[0]+u*cab[0], ca[1]+u*cab[1]), (u, 1-w)


def thanLineSeg2(C, t, A, B):
      r"""
c-----Βρίσκει συντεταγμένες τομής ευθείας (C+λ*t) και ευθ. τμήματος  (AB)

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
      if not inters: return None

      cb = B[0] - A[0], B[1] - A[1]      # διάνυσμα ab
      Kcb = cb[0] * n[0] + cb[1] * n[1]
      if thanNearzero(Kcb, hypot(cb[0], cb[1])):
          #Thanasis2021_10_28: AB is parallel and exactly on line Ct
          return A[0] + cb[0] * 0.5, A[1] + cb[1] * 0.5   #Infinite intersection points: arbitrarily return middle point
      Kcb = fabs(Kca / Kcb)              # αναλογία ac/ab
      return A[0] + cb[0] * Kcb, A[1] + cb[1] * Kcb


def thanLineSeg3old(pn, n, A, B):
    """Finds the coordinates of the intersection between line perpendicular to n and line segment AB.

    The line's projection on n axis is pn.

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
    pna = n[0]*A[0] + n[1]*A[1]
    pnb = n[0]*B[0] + n[1]*B[1]
    if fsign(1.0, pna-pn)*fsign(1.0, pnb-pn) > 0.0: return None
    ct = [linint(pna, a, pnb, b, pn) for a,b in zip(A, B)]
    return ct


def thanLineSeg3(Ot, n, A, B):
    """Finds the coordinates of the intersection between line perpendicular to n and line segment AB.

    The line's projection on n axis is Ot.

c    |
c    | ^
c    | |n
c    | |
c  b o    .    .    .    .    .    o B
c    |                            /
c    |                          /
c    |                    TOM /
c  t-o----------------------o-------------------------------- line
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
c     Ot   : Προβολή όλων των σημείων της ευθείας (και συνεπώς και της τομής)
c            σε άξονα παράλληλο προς n που περνάει από την αρχή των αξόνων (άξονας n)
c     Oa   : Προβολή του OA στον άξονα n
c     Ob   : Προβολή του OB στον άξονα n
"""
    Oa = n[0]*A[0] + n[1]*A[1]
    Ob = n[0]*B[0] + n[1]*B[1]
    if fsign(1.0, Oa-Ot)*fsign(1.0, Ob-Ot) > 0.0: return None
    ct = [linint(Oa, a, Ob, b, Ot) for a,b in zip(A, B)]
    return ct


def thanSegCir(ca, cb, cc, rc, abisline=False):
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
    if thanNearx(d, 0.0): return []                 # Line segment is a dot
    tab = dc[0]/d, dc[1]/d
    nab = -tab[1], tab[0]
    vac = cc[0]-ca[0], cc[1]-ca[1]
    dn = vac[0]*nab[0] + vac[1]*nab[1]
    if fabs(dn) > rc:
        if not thanNearx(fabs(dn), rc): return []   # Thanasis2021_11_24: added thanNearx: No intersections
    cm = cc[0]-dn*nab[0], cc[1]-dn*nab[1]
    tm = (cm[0]-ca[0])*tab[0] + (cm[1]-ca[1])*tab[1]
    if thanNearx(fabs(dn), rc):
        if abisline: return [cm]           # One intersection in or out of the segment
        elif 0.0 <= tm <= d: return [cm]   # One intersection in the segment
        elif thanNearx(0.0+rc, tm+rc) or thanNearx(d, tm): return [cm]  # Thanasis2021__11_24: One intersection near one end of the segment
        else:                return []     # One Intersection out of segment
    dt = sqrt(rc**2-dn**2)
    ps = []
    if abisline:            ps.append((cm[0]-dt*tab[0], cm[1]-dt*tab[1])) # Intersection 1 is in or out of the segment
    elif 0.0 <= tm-dt <= d: ps.append((cm[0]-dt*tab[0], cm[1]-dt*tab[1])) # intersection 1 is in segment
    if abisline:            ps.append((cm[0]+dt*tab[0], cm[1]+dt*tab[1])) # Intersection 2 is in or out of the segment
    elif 0.0 <= tm+dt <= d: ps.append((cm[0]+dt*tab[0], cm[1]+dt*tab[1])) # intersection 2 is in segment
    return ps


def thanSegCirGen(ca, cb, cc, rc, abisline=False):
    """Finds the coordinates and local coordinates of the intersection of linear segment ca-cb and circle.


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
    if thanNearx(d, 0.0): return []                 # Line segment is a dot
    tab = dc[0]/d, dc[1]/d
    nab = -tab[1], tab[0]
    vac = cc[0]-ca[0], cc[1]-ca[1]
    dn = vac[0]*nab[0] + vac[1]*nab[1]
    if fabs(dn) > rc: return []          # No intersections
    cm = cc[0]-dn*nab[0], cc[1]-dn*nab[1]
    tm = (cm[0]-ca[0])*tab[0] + (cm[1]-ca[1])*tab[1]
    if thanNearx(fabs(dn), rc):
        if abisline: return [cm]           # One intersection in or out of the segment
        elif 0.0 <= tm <= d: return [(cm, tm/d)]   # One intersection in the segment
        else:                return []     # One Intersection out of segment
    dt = sqrt(rc**2-dn**2)
    ps = []
    if abisline:            ps.append(( (cm[0]-dt*tab[0], cm[1]-dt*tab[1]), (tm-dt)/d)) # Intersection 1 is in or out of the segment
    elif 0.0 <= tm-dt <= d: ps.append(( (cm[0]-dt*tab[0], cm[1]-dt*tab[1]), (tm-dt)/d)) # intersection 1 is in segment
    if abisline:            ps.append(( (cm[0]+dt*tab[0], cm[1]+dt*tab[1]), (tm+dt)/d)) # Intersection 2 is in or out of the segment
    elif 0.0 <= tm+dt <= d: ps.append(( (cm[0]+dt*tab[0], cm[1]+dt*tab[1]), (tm+dt)/d)) # intersection 2 is in segment
    return ps


def thanCirCir(ca, ra, cb, rb):
    r"""Finds intersection of 2 circles.

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
        print("Warning: Radius of circles must be positive >%s" % thanThresholdx)
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
        print("Algorithm failure in circles' intersection")
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


def pdis(a, b, c):
    "Find (normal) distace of point c to line a-b."
    t = b[0]-a[0], b[1]-a[1]           # Vector ab
    dd = hypot(t[0], t[1])             # Length of ab
    t = t[0]/dd, t[1]/dd               # unit vector of ab
    n = -t[1], t[0]                    # normal unit vector to ab
    ac = c[0]-a[0], c[1]-a[1]          # vector ac
    return fabs(ac[0]*n[0]+ac[1]*n[1]) # Projection of ac to n (the minimum distance)


if __name__ == "__main__":
    print(__doc__)
