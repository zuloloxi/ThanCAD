"""
This programs computes the elevation difference (hgme) between the geoid and the
EGSA87 ellipsoid (which is the the GRS80 translated by some constant values).
hgme = geoid surface - ellipsoid surface
In Greece near Athens the geoid surface is above the ellipsoid surface and thus
an elevation with respect to the geoid surface is smaller than an elevation
with respect to the ellipsoid surface, and thus hgme > 0.0. In general it holds:
    horthometric = h(with respect to geoid surface) = hgeometric - hgme =
                                                    = h(with respect to ellipsoid) - hgm
or
    hgme = hgeometric - horthometric

hgme is computed using the contour map from the book (page 25)
Ανώτερη Γεωδαισία, Βέης, Μπιλίρης, Παπαζήση,
ΕΜΠ 1992.

The same with the elevation difference between geoid and the GRS80
ellipsoid itself (from the same book page 26).

The program returns None if the geodetic coordinates are not within
Greece.

2011_05_08
It seems that the diagram on page 25 (Greek local GRS80) was computed using
the diagram on page 26 (international GRS80), transforming λ, φ, h from
GRS80 to Greek local. It seems that these computations were done with
ΔΧ, ΔΥ, ΔΖ which ARE NOT the final ΔΧ, ΔΥ, ΔΖ defined in EGSA87.
The difference between the hgme of local ellipsoid and international GRS80
are about 0.60-0.70m.
On the other hand the difference between the hgme of diagram on page 26 (GRS80)
and the hgme computed by NASA EGM2008 (Pavlis Nikolaos:
http://earth-info.nga.mil/GandG/wgs84/gravitymod/egm2008/egm08_wgs84.html)
are about zero.
"""

from math import pi
import p_gtri
from p_ggeod import egsa87, GRS80

useGRS80 = True    #If this is set to False the results will be about 0.60-0.70m wrong. See above.


if useGRS80:
    from . import hgme_grs80brk as hgmebrk, hgme_grs80syk as hgmesyk
else:
    from . import hgme_egsa87brk as hgmebrk, hgme_egsa87syk as hgmesyk

_hgme = p_gtri.ThanDTMlines()
hgmebrk.addlines(_hgme)
hgmesyk.addlines(_hgme)
_hgme.thanRecreate()


def getN(l, f):
    "Compute the difference of elevation between geoid and the (chosen) ellipsoid; l, f in decimal degrees."
    return _hgme.thanPointZ((l, f))


def getNegs(cpegs):
    "Calculate DH geoid-ellipsoid for point with egsa87 coordinates."
    assert not useGRS80, "useGRS80 should be False"
    l, f = egsa87.en2geodet(cpegs[0], cpegs[1])                 #Geodetic EGSA87
    l *= 180.0/pi
    f *= 180.0/pi
    h1 = getN(l, f)              #hgme between geoid and EGSA87 ellipsoid
    if h1 is None:
        print(cpegs, l, f)
        assert 0, "%r, %r, %r" % (cpegs, l, f)
    return h1


def getNlf80(l, f):
    "Calculate DH geoid-ellipsoid for point with λ, φ in GRS80 international."
    assert useGRS80, "useGRS80 should be True"
    l *= 180.0/pi
    f *= 180.0/pi
    h1 = getN(l, f)              #hgme between geoid and EGSA87 ellipsoid
    if h1 is None:
        raise ValueError("Point is outside Greece: GRS80 (deg) λ=%.5f φ=%.5f" % (l, f))
    return h1


def getDhEgsa87(xgyse, ygyse):
    "Get the elevation difference: Greek local GRS80 surface minus the international GRS80 surface, given x,y EGSA87 coordinates."
    assert useGRS80, "useGRS80 should be True"
    xt, yt, zt = egsa87.en2geocenGRS80(xgyse, ygyse, h=0.0, hgme=0.0)
    l8, f8, h8 = GRS80.geocen2det(xt, yt, zt, hgme=0.0)
    return h8


def getHgmeEgsa87(xgyse, ygyse):
    "Get the elevation difference geoid surface minus the Greek local GRS80 ellipsoid surface, given x,y EGSA87 coordinates."
    assert useGRS80, "useGRS80 should be True"
    xt, yt, zt = egsa87.en2geocenGRS80(xgyse, ygyse, h=0.0, hgme=0.0)
    l8, f8, h8 = GRS80.geocen2det(xt, yt, zt, hgme=0.0)
    l8 *= 180.0/pi
    f8 *= 180.0/pi
#    print "λ, φ GRS80:", l8, f8
    h1 = getN(l8, f8)                                #hgme between geoid and EGSA87 ellipsoid
    if h1 is None:
        raise ValueError("Point is outside Greece: x=%.3f y=%.3f: GRS80 (deg) λ=%.5f φ=%.5f" % (xgyse, ygyse, l8, f8))
#    print "h1=", h1
    return h1-h8
