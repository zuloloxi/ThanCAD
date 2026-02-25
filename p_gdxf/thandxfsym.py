from math import pi, cos, sin


class ThanDxfSym:
    "Mixin to draw text to .dxf file."

#===========================================================================

    def __init__(self):
        "No initialisation needed."
        pass

#===========================================================================

    def thanDxfPlotNumber (self, x, y, h, dn, theta, nn):
        "Plots a number to .dxf file."
        if nn < 0:
            #s = str(int(dn+0.5))    #This does not round negative numbers!!!!!!
            s = str(int(round(dn)))  #Thanasis2014_06_07(bug after 10 years)
        else:
            s = ("%." + str(nn) + "f") % (dn, )

        self.thanDxfPlotSymbol(x, y, h, s, theta)

#===========================================================================

    def thanDxfPlotSymbol3(self, xx, yy, zz, hh, text, th):
        "Plots a 3d string to a .dxf file."

        (px, py, pz) = self.thanDxfTop3(xx, yy, zz)

        self.thanDxfWrEntry(0, 'TEXT')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        self.thanDxfWrXyz(px, py, pz)
        self.thanDxfWrEntry(40, hh)

        self.thanDxfWrEntry(1, text)
        self.thanDxfWrEntry(50, th)
        self.thanDxfWrTstyle()

#-------find current pen position--------------------------------------

        pt = th * pi / 180.0
        al = hh * self.thanXfac * len(text)
        self.thanPXnow = px + al * cos(pt)
        self.thanPYnow = py + al * sin(pt)
        self.thanPZnow = pz

#===========================================================================

    def thanDxfPlotSymbol(self, xx, yy, hh, text, th):
        "Plots a string to a .dxf file."

        (px, py) = self.thanDxfTop(xx, yy)

        self.thanDxfWrEntry(0, 'TEXT')
        self.thanDxfWrLayer()
        self.thanDxfWrColor()

        self.thanDxfWrXy(px, py)
        self.thanDxfWrEntry(40, hh)

        self.thanDxfWrEntry(1, text)
        self.thanDxfWrEntry(50, th)
        self.thanDxfWrTstyle()

#-------find current pen position--------------------------------------

        pt = th * pi / 180.0
        al = hh * self.thanXfac * len(text)
        self.thanPXnow = px + al * cos(pt)
        self.thanPYnow = py + al * sin(pt)

#===========================================================================

    def thanDxfPlotVsymbol (self, x, y, h, let, th):
        """Plots a string vertically."

c-----When a letter has height h, its actual width is h*(2/3).
c     The remaining h*(1/3) is left for horizontal distance
c     between letters of the same word.
c     However the actual height of the letter is h. Thus when
c     the word is to be written vertically, a vertical distance
c     of h*(1/3) should be left between the letters of the same
c     word. Factor fvdl (Factor of Vertical Distance between
c     Letters) enlarges h for this reason.
c     Factor fvdw (Factor of Vertical Distance between Words)
c     is for the same reason, but bigger distance is needed between
c     words."""


        FVDL=1.0+1.0/3.0
#        FVDW=1.0+1.0/2.0)

        t = (th - 90.0) * pi / 180.0
        sh = FVDL * h * sin(t)
        ch = FVDL * h * cos(t)
        xx = x
        yy = y

        for let1 in let:
            self.thanDxfPlotSymbol(xx, yy, h, let1, th)
            xx = xx + ch
            yy = yy + sh


if __name__ == "__main__":
    dxf = ThanDxfSym()
