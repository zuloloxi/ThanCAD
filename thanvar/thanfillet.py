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

This module computes intersection of 2 lines segments (extending them if
necessary and joins them with circular arc.
"""
from math import pi
from p_gvec import Vector2
from p_gmath import thanNearx
from .thanroad import calcRoadNode


def thanFilletCalc(a, b, rr, anear=None, bnear=None):
    r"""
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

    assert rr >= 0.0, "negative radius?!"
    assert len(a.cp) == 2 and len(b.cp) == 2, "This routine can fillet only single line segments"

#-----Υπολόγισε διανύσματα

    ca, cb, c1, c2 = map(Vector2, a.cp+b.cp)   #works for python2,3
    cab = cb - ca
    c12 = c2 - c1
    ca2 = c2 - ca

#-----Ανάλυση σε δύο συνιστώσες παράληλλες προς τα 2 ευθ. τμήματα

    u, w = ca2.anal(cab, c12)
    if u is None: return 1, None     #No intersection
    w = 1.0-w

    K2 = ca+u*cab
    K1, ia = __keep(ca, cb, u, anear)
    K3, ib = __keep(c1, c2, w, bnear)

    if rr == 0.0:
        a.cp[ia][:2] = K2.x, K2.y
        b.cp[ib][:2] = K2.x, K2.y
        return 0, None
    c = calcRoadNode(K1.x, K1.y, K2.x, K2.y, K3.x, K3.y, rr)

    if c.T1 >= abs(K2-K1): return 2, None        # Circular arc is outside the first line
    if c.T2 >= abs(K2-K3): return 2, None        # Circular arc is outside the second line
    a.cp[ia][:2] = c.pa.x, c.pa.y
    b.cp[ib][:2] = c.pt.x, c.pt.y
    cc = list(a.cp[ia])
    cc[0:2] = c.pc.x, c.pc.y
    return 0, (cc, rr, c.theta1*pi/180, c.theta2*pi/180)


def __keep(ca, cb, u, anear):
    "Decide which line end point to keep."
    if anear is not None:
        cab = cb - ca
        un = (Vector2(anear)-ca) | cab / abs(cab)**2
        print("u=", u, "un=", un)
    if   u <= 0 or thanNearx(u, 0.0): K1 = cb; ia = 0     #Intersection beyond ca, keep cb
    elif u >= 1 or thanNearx(u, 1.0): K1 = ca; ia = 1     #Intersection beyond cb, keep ca
    elif anear is not None and un <= u:   K1 = ca; ia = 1     #Intersection between ca and cb, user chooses to keep ca
    elif anear is not None and un >  u:   K1 = cb; ia = 0     #Intersection between ca and cb, user chooses to keep cb
    else:                             K1 = ca; ia = 1     #Intersection between ca and cb, no user choice, keep ca (original orientation)
    return K1, ia
