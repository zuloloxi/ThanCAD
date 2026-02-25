from .var import thanNearx

class ThanRectCoorTransf:
    """Class to transform rectangular coordinates.

    A rectangle represents a coordinate system, that is the
    coordinates of lower left corner (point 1) and the coordinates
    of the upper right corner (point 2).
    A "global" and a "local" rectangle are given. It is assumed the
    point 1 of the global rectangle corresponds linearly to point 1
    of local rectangle. The same for point 2.
    This class computes the coefficients of the linear formulas used
    to transform global coordinates to local, and the opposite.
    Note that while in general the global coordinates xg2>xg1 and yg2>yg1,
    the local coordinates usually xl2>xl1 and yl2<yl1.
    """


    def __init__(self, globalr=None, localr=None, samescale=True):
        "Initialise transformation."
        if globalr is None: return
        if localr is None: return
        if samescale:
            globalr = thanRoundCenter(globalr, localr)
        self.set(globalr, localr)


    def set(self, globalr, localr):
        "Computes new coefs for converting formulas."
        xg1, yg1, xg2, yg2 = globalr
        xl1, yl1, xl2, yl2 = localr
        (self.axg2l, self.bxg2l) = self.coef(xg1, xg2, xl1, xl2)
        (self.ayg2l, self.byg2l) = self.coef(yg1, yg2, yl1, yl2)
        (self.axl2g, self.bxl2g) = self.coef(xl1, xl2, xg1, xg2)
        (self.ayl2g, self.byl2g) = self.coef(yl1, yl2, yg1, yg2)


    def coef(self, xg1, xg2, xl1, xl2):
        """Returns the formula coefficients converting global to local.

        xLocal = xl1 + (xl2-xl1)/(xg2-xg1) * (xGlobal-xg1) =
                 xl1 + B*(xGlobal-xg1) = xl1 - B*xg1 + B*xGlobal =
                 A + B*xGlobal
        """
    #    assert xg1 != xg2, "Some window has 1 dimension zero!"
        if xg1 == xg2:
            b = 0.0
        else:
            b = float(xl2-xl1) / float(xg2-xg1)
        a = xl1 - b*xg1
        return a, b


    def global2Local(self, xg, yg):
        "Transform global coordinates to local."
        return self.axg2l + self.bxg2l * xg, self.ayg2l + self.byg2l * yg


    def global2Locali(self, xg, yg):
        "Transform global coordinates to local converting to integers."
        return round(self.axg2l + self.bxg2l * xg), round(self.ayg2l + self.byg2l * yg)


    def local2Global(self, xl, yl):
        "Transform local coordinates to global."
        return self.axl2g + self.bxl2g * xl, self.ayl2g + self.byl2g * yl


    def global2LocalRel(self, xg, yg):
        "Transform global size to local."
        return self.bxg2l * xg, self.byg2l * yg


    def global2LocalReli(self, xg, yg):
        "Transform global size to local converting to integer."
        return round(self.bxg2l * xg), round(self.byg2l * yg)


    def local2GlobalRel(self, xl, yl):
        "Transform local size to global."
        return self.bxl2g * xl, self.byl2g * yl


def thanRoundCenter(w, local, per=6):
    "Rounds an abstract window w, so that it fits exactly to the actual (GuiDependent) window."
    xa, ya, xb, yb = local
    wpi = abs(xb - xa)
    hpi = abs(yb - ya)

    wun = w[2] - w[0]
    hun = w[3] - w[1]

#    per =                                       # margin in pixels
    if wpi < 10*per or hpi < 10*per: per = 0     # no margin for very small windows
    if thanNearx(wun, 0.0):
#        assert not thanNearx(hun, 0.0), "Zero world coordinates window dimensions"
        if thanNearx(hun, 0.0): return tuple(w)  #Zero world coordinates window dimensions
        sx = sy = float(hpi - per) / hun
    elif thanNearx(hun, 0.0):
        sx = float(wpi - per) / wun
    else:
        sx = float(wpi - per) / wun
        sy = float(hpi - per) / hun
        if sy < sx: sx = sy
    dx = (wpi / sx - wun) * 0.5
    dy = (hpi / sx - hun) * 0.5
    return w[0]-dx, w[1]-dy, w[0]+wun+dx, w[1]+hun+dy
