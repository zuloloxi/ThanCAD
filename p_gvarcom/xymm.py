import sys
#from typing import Sequence, Iterable, Optional, List, TextIO, Tuple

class Xymm:
    "A rectangular region: [xmin,ymin,xmax,ymax]."
    __slots__ = ("regname", "xymm")


    #def __init__(self, seq:Optional[Iterable[float]] = None) -> None:
    def __init__(self, seq=None):
        "Initialize object to empty rectangle, if not explicitly initialised."
        #self.xymm: List[float] = []
        self.xymm = []
        #self.regname: str = "untitled"
        self.regname = "untitled"
        self.clear()
        if seq is None: return
        for i,x in enumerate(seq):  # type: int, float #Thiw will raise TypeError if seq is not iterable
            self[i] = x
            if i >= 3: break
        if i != 3: raise TypeError("Iterable with 4 floats was expected")


    #def __getitem__(self, i:int) -> float:
    def __getitem__(self, i):
        return self.xymm[i]
    #def __setitem__(self, i:int, val: float) -> None:
    def __setitem__(self, i, val):
        self.xymm[i] = val

    #def clear(self) -> None:
    def clear(self):
        "Make a null object which contains nothing; suitable for includeXymm, includePoint."
        #big: float = sys.float_info.max
        big = sys.float_info.max
        self.xymm[:] = big, big, -big, -big

    #def isNull(self) -> bool:
    def isNull(self):
        "Check if it is a null object which is not able to contain anything."
        return self.xymm[0]>self.xymm[2] or self.xymm[1]>self.xymm[3]

    @staticmethod
    def infinite(): # type: () -> Xymm
        "Make a region which contains all points."
        #big: float = sys.float_info.max
        big = sys.float_info.max
        return Xymm((-big, -big, big, big))


    #def includeXymm(self, other: Sequence[float]) -> None:
    def includeXymm(self, other):
        "Extend region to contain other region."
        if other[0] < self[0]: self[0] = other[0]
        if other[1] < self[1]: self[1] = other[1]
        if other[2] > self[2]: self[2] = other[2]
        if other[3] > self[3]: self[3] = other[3]


    #def includePoint(self, c: Sequence[float]) -> None:
    def includePoint(self, c):
        "Extend the region to contain point c."
        if c[0] < self[0]: self[0] = c[0]
        if c[1] < self[1]: self[1] = c[1]
        if c[0] > self[2]: self[2] = c[0]
        if c[1] > self[3]: self[3] = c[1]


    #def __contains__(self, c: Sequence[float]) -> bool:
    def __contains__(self, c):
        "Return True if point c in inside the rectangular region."
        if c[0] < self[0]: return False
        if c[1] < self[1]: return False
        if c[0] > self[2]: return False
        if c[1] > self[3]: return False
        return True


    #def containsXymm(self, other: Sequence[float]) -> bool:
    def containsXymm(self, other):
        "Return True if rectangular region other is inside the rectangular region."
        if other[0] < self[0]: return False
        if other[1] < self[1]: return False
        if other[2] > self[2]: return False
        if other[3] > self[3]: return False
        return True


    #def intersectsXymm(self, other: Sequence[float]) -> bool:
    def intersectsXymm(self, other):
        "Return True if rectangular region other intersects the rectangular region."
        if other[0] > self[2]: return False
        if other[1] > self[3]: return False
        if other[2] < self[0]: return False
        if other[3] < self[1]: return False
        return True


    def intersection(self, other): # type: (Xymm, Sequence[float]) -> Xymm
        "Compute and return the intesection of the rectangular regions."
        n = Xymm()  # type: Xymm
        n[0] = max(self[0], other[0])
        n[1] = max(self[1], other[1])
        n[2] = min(self[2], other[2])
        n[3] = min(self[3], other[3])
        return n


    #def enlargeAreaPer(self, per: float) -> None:
    def enlargeAreaPer(self, per):
        "Enlarge area by percentage."
        #dc: float = max(self[2]-self[0], self[3]-self[1])*per
        dc = max(self[2]-self[0], self[3]-self[1])*per
        self[0] -= dc
        self[1] -= dc
        self[2] += dc
        self[3] += dc
#        prg("Enlarged area: %s %s %s %s" % tuple(self))


    #def enlargeArea(self, dc: Sequence[float]) -> None:
    def enlargeArea(self, dc):
        "Enlarge area by vector dc."
        self[0] -= dc[0]
        self[1] -= dc[1]
        self[2] += dc[0]
        self[3] += dc[1]
#        prg("Enlarged area: %s %s %s %s" % tuple(self))


    #def round(self, dx: float, dy: float) -> None:
    def round(self, dx, dy):
        "Round the coordinates so that the inside area is integer multiplier of dx, dy."
        #dcor: Tuple[float, float] = (self[2]-self[0], self[3]-self[1])
        dcor = (self[2]-self[0], self[3]-self[1])
        #dc: Tuple[float, float] = (round(dcor[0]/dx)*dx, round(dcor[1]/dy)*dy)
        dc = (round(dcor[0]/dx)*dx, round(dcor[1]/dy)*dy)
        dx, dy = (dc[0]-dcor[0])*0.5, (dc[1]-dcor[1])*0.5
        self[0] -= dx
        self[1] -= dy
        self[2] += dx
        self[3] += dy


    #def writeSyk(self, fw: TextIO) -> None:
    def writeSyk(self, fw):
        "Write the xymm area to a syk file."
        fw.write("%15.3f  %s\n" % (0.0, self.regname))
        for ix,iy in (0, 1), (2, 1), (2, 3), (0, 3), (0, 1):  #type: int, int
            fw.write("%15.3f%15.3f\n" % (self[ix], self[iy]))
        fw.write("$\n")


    def dxfplot(self, dxf):
        "Plot the region into current layer of an opened dxf file."
        for ix,iy in (0, 1), (2, 1), (2, 3), (0, 3), (0, 1):  #type: int, int
            dxf.thanDxfPlotPolyVertex(self[ix], self[iy], 2)
        dxf.thanDxfPlotPolyVertex(0, 0, 999)


    #def readPin(self, fr: TextIO) -> str:
    def readPin(self, fr):
        """Read the rectangular region from a pin file.

        The file contains one line give x,y of lower left corner, dx,dy of the
        region and the angle between x-axis and the 'horizontal' side of the
        region in degrees. If the angle is not exactly zero an error is returned.
        This function return an epty string if successful, and a non-empty string
        which contains the error message if unsuccessful.
        """
        for dline in fr:  # type: str
            break
        else:
            return "End of file (empty file?)"
        try:
            #name1: str = dline[:10].rstrip()
            #x1: float = float(dline[15:25])
            #y1: float = float(dline[25:40])
            #dx: float = float(dline[40:55])
            #dy: float = float(dline[55:70])
            #th: float = float(dline[70:85])
            name1 = dline[:10].rstrip()
            x1 = float(dline[15:25])
            y1 = float(dline[25:40])
            dx = float(dline[40:55])
            dy = float(dline[55:70])
            th = float(dline[70:85])
            if th != 0.0: raise ValueError("Angle should be zero but is {}".format(th))
        except (ValueError, IndexError) as e:
            return str(e)
        self.clear()
        self.includePoint((x1, y1))
        self.includePoint((x1+dx, y1+dy))
        self.regname = name1
        return ""


    #def writePin(self, fw: TextIO) -> None:
    def writePin(self, fw):
        "Write the xymm area to a pin file."
        #dx: float = self[2] - self[0]
        dx = self[2] - self[0]
        #dy: float = self[3] - self[1]
        dy = self[3] - self[1]
        fw.write("%-10s%15.3f%15.3f%15.3f%15.3f%15.5f\n" % (self.regname, self[0], self[1], dx, dy, 0.0))
