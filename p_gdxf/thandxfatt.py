class ThanDxfAtt:
    "Mixin for setting and writing attributes."

    def __init__(self):
        "Initialisation is not needed, but for compatibility."
        pass

    def thanDxfWrEntry(self, icod, whatever):
        "Writes a basic entry to dxf file."
        self.thanFdxf.write(str(icod) + "\n" + str(whatever) + "\n")

    def thanDxfWrLayer(self):
        "Writes layer name of a entity."
        self.thanFdxf.write("8\n" + self.thanLayer + "\n")

    def thaDxfWrLtype(self):
        "Writes linetype of a linear entity."
        if self.thanLtype != "BYLAYER":
            self.thanFdxf.write("6\n" + self.thanLtype + "\n")

    def thanDxfWrColor(self):
        "Writes color of an entity."
        if self.thanColor > 0:
            self.thanFdxf.write("62\n" + str(self.thanColor) + "\n")

    def thanDxfWrTstyle(self):
        "Writes text style of text entity."
        if self.thanTstyle != "DEFAULT":
            self.thanFdxf.write("7\n" + self.thanTstyle + "\n")


    def thanDxfWrPlineWidth(self):
        "Writes the (variable) line width for polylines."
        if self.thanPlineWidth[0] != 0.0 or self.thanPlineWidth[1] != 0.0:
            thanDxfWrEntry(40, self.thanPlineWidth[0])
            thanDxfWrEntry(41, self.thanPlineWidth[1])


    def thanDxfWrLinatts(self):
        "Writes all the attributes of a linear entity together."
        self.thanFdxf.write("8\n" + self.thanLayer + "\n")
        if self.thanLtype != "BYLAYER":
            self.thanFdxf.write("6\n" + self.thanLtype + "\n")
        if self.thanColor > 0:
            self.thanFdxf.write("62\n" + str(self.thanColor) + "\n")

    def thanDxfWrXy(self, x, y):
        "Writes xy coordinates."
        self.thanFdxf.write("10\n" + str(x) + "\n20\n" + str(y) + "\n")

    def thanDxfWrXyz(self, x, y, z):
        "Writes xyz coordinates."
        self.thanFdxf.write("10\n" + str(x) + "\n20\n" + str(y) + "\n30\n" + str(z) + "\n")

    def thanDxfWrXy1(self, x, y):
        "Writes xyz coordinates."
        self.thanFdxf.write("11\n" + str(x) + "\n21\n" + str(y) + "\n")

    def thanDxfWrXyz1(self, x, y, z):
        "Writes xyz coordinates."
        self.thanFdxf.write("11\n" + str(x) + "\n21\n" + str(y) + "\n31\n" + str(z) + "\n")

    def thanDxfWrXyc(self, c, x, y):
        "Writes xy coordinates."
        self.thanFdxf.write("%d\n%f\n%d\n%f\n" % (10+c, x, 20+c, y))

    def thanDxfWrXyzc(self, c, x, y, z):
        "Writes xyz coordinates."
        self.thanFdxf.write("%d\n%f\n%d\n%f\n%d\n%f\n" % (10+c, x, 20+c, y, 30+c, z))

    def thanDxfSetLayer(self, la):
        "Sets the linetype for subsequent entities."
        self.thanLayer = la

    def thanDxfSetLtype(self, lt):
        "Sets the linetype for subsequent linear entities."
        self.thanLtype = lt

    def thanDxfSetColor(self, co):
        "Sets the color for subsequent entities."
        self.thanColor = co

    def thanDxfSetPlineWidth(self, w1, w2):
        "Sets the text style for subsequent text entities."
        self.thanPlineWidth = (w1, w2)

    def thanDxfSetTstyle(self, lt):
        "Sets the text style for subsequent text entities."
        self.thanTstyle = lt


if __name__ == "__main__":
    dxf = ThanDxfAtt()
