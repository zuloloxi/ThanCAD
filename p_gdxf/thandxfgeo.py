class ThanDxfGeo:
    "Mixin to geometry of .dxf file."

#===========================================================================

    def __init__(self):
        "No initialisation needed."
        pass

#===========================================================================

    def thanDxfTop (self, xx, yy):
        "Transforms a 2d point to local coordinates."
        return (self.thanPXar + (xx-self.thanXar) * self.thanXfac,
                self.thanPYar + (yy-self.thanYar) * self.thanYfac)

#===========================================================================

    def thanDxfTop3 (self, xx, yy, zz):
        "Transforms a 3d point to local coordinates."
        return (self.thanPXar + (xx-self.thanXar) * self.thanXfac,
                self.thanPYar + (yy-self.thanYar) * self.thanYfac,
                self.thanPZar + (zz-self.thanZar) * self.thanZfac)

#===========================================================================

    def thanDxfSetFactor(self, ff):
        "Assigns an overall absolute scale to the output of dxf."
        ff1 = ff / self.thanFact
        self.thanXfac *= ff1
        self.thanYfac *= ff1
        self.thanZfac *= ff1

        self.thanFact = ff

#===========================================================================

    def thanDxfLocref(self, xx, yy, fx, fy):
        "Assigns relative scales to x, y output of dxf."
        self.thanXar = xx
        self.thanYar = yy
        self.thanPXar = self.thanPXnow
        self.thanPYar = self.thanPYnow
        if fx > 0: self.thanXfac = fx * self.thanFact
        if fy > 0: self.thanYfac = fy * self.thanFact

#===========================================================================

    def thanDxfLocref3(self, xx, yy, zz, fx, fy, fz):
        "Assigns relative scales to x, y, z output of dxf."
        self.thanXar = xx
        self.thanYar = yy
        self.thanYar = zz
        self.thanPXar = self.thanPXnow
        self.thanPYar = self.thanPYnow
        self.thanPZar = self.thanPZnow
        if fx > 0: self.thanXfac = fx * self.thanFact
        if fy > 0: self.thanYfac = fy * self.thanFact
        if fz > 0: self.thanZfac = fz * self.thanFact

#===========================================================================

    def thanDxfWhere(self):
        "Returns the current position of the 'pen'."
        return ((self.thanPXnow - self.thanPXar) / self.thanXfac + self.thanXar,
                (self.thanPYnow - self.thanPYar) / self.thanYfac + self.thanYar)

#===========================================================================

    def thanWhere3(self):
        "Returns the current position of the 'pen'."
        return ((self.thanPXnow - self.thanPXar) / self.thanXfac + self.thanXar,
                (self.thanPYnow - self.thanPYar) / self.thanYfac + self.thanYar,
                (self.thanPZnow - self.thanPZar) / self.thanZfac + self.thanZar )


    def thanDxfGetNow(self):
        "Returns the current position of the 'pen' in plot units (for example cm)."
        return self.thanPXnow, self.thanPYnow


    def thanDxfGetNow3(self):
        "Returns the current position of the 'pen' in plot units (for example cm)."
        return self.thanPXnow, self.thanPYnow, self.thanPZnow


    def thanDxfSetNow(self, px, py):
        "Sets the current position of the 'pen' in plot units (for example cm)."
        self.thanPXnow = px
        self.thanPYnow = py


    def thanDxfSetNow3(self, px, py, pz):
        "Sets the current position of the 'pen' in plot units (for example cm)."
        self.thanPXnow = px
        self.thanPYnow = py
        self.thanPZnow = pz


if __name__ == "__main__":
    dxf = ThanDxfGeo()
