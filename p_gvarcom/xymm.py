import sys
class Xymm(list):
    "A rectangular region."
    __slots__ = ()

    def __init__(self, *args, **kw):
        "Initialize object to empty rectangle, if not explicitly initialised."
        super(Xymm, self).__init__(self, *args, **kw)
        if len(self) == 0: self.clear()


    def clear(self):
        "Make a null object which contains nothing; suitable for includeXymm, includePoint."
        big = sys.float_info.max
        self[:] = big, big, -big, -big


    def includeXymm(self, other):
        "Extend region to contain other region."
        if other[0] < self[0]: self[0] = other[0]
        if other[1] < self[1]: self[1] = other[1]
        if other[2] > self[2]: self[2] = other[2]
        if other[3] > self[3]: self[3] = other[3]


    def includePoint(self, c):
        "Extend the region to contain point c."
        if c[0] < self[0]: self[0] = c[0]
        if c[1] < self[1]: self[1] = c[1]
        if c[0] > self[2]: self[2] = c[0]
        if c[1] > self[3]: self[3] = c[1]


    def __contains__(self, c):
        "Return True if point c in inside the rectangular region."
        if c[0] < self[0]: return False
        if c[1] < self[1]: return False
        if c[0] > self[2]: return False
        if c[1] > self[3]: return False
        return True


    def containsXymm(self, other):
        "Return True if rectangular region other is inside the rectangular region."
        if other[0] < self[0]: return False
        if other[1] < self[1]: return False
        if other[2] > self[2]: return False
        if other[3] > self[3]: return False
        return True


    def intersectsXymm(self, other):
        "Return True if rectangular region other intersects the rectangular region."
        if other[0] > self[2]: return False
        if other[1] > self[3]: return False
        if other[2] < self[0]: return False
        if other[3] < self[1]: return False
        return True


    def enlargeAreaPer(self, per):
        "Enlarge area by percentage."
        dc = max(self[2]-self[0], self[3]-self[1])*per
        self[0] -= dc
        self[1] -= dc
        self[2] += dc
        self[3] += dc
#        prg("Enlarged area: %s %s %s %s" % tuple(self))


    def enlargeArea(self, dc):
        "Enlarge area by vector dc."
        self[0] -= dc[0]
        self[1] -= dc[1]
        self[2] += dc[0]
        self[3] += dc[1]
#        prg("Enlarged area: %s %s %s %s" % tuple(self))


    def round(self, dx, dy):
        "Round the coordinates so that the inside area is integer multiplier of dx, dy."
        dcor = self[2]-self[0], self[3]-self[1]
        dc = round(dcor[0]/dx)*dx, round(dcor[1]/dy)*dy
        dx, dy = (dc[0]-dxor[0])*0.5, (dc[1]-dxor[1])*0.5
        self[0] -= dx
        self[1] -= dy
        self[2] += dx
        self[3] += dy


    def writeSyk(self, fw):
        "Write the xymm area to a syk file."
        fw.write("%15.3f  %s\n" % (0.0, "area"))
        for ix,iy in (0, 1), (2, 1), (2, 3), (0, 3), (0, 1):
            fw.write("%15.3f%15.3f\n" % (self[ix], self[iy]))
        fw.write("$\n")
