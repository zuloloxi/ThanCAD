#from typing import Tuple, TextIO, Iterator, Optional, Callable, List, Sequence, Iterable
#try: from typing import Protocol
#except: from typing_extensions import Protocol
import p_ggen, p_gfil # type: ignore

#class ProtPrt(Protocol):
#    def __call__(self, t: str, tags: Optional[str]=None) -> None: pass


#def reTrg1(fr: TextIO) -> Iterator[Tuple[str, float, float, float, float]]:
def reTrg1(fr):
    """Reads 3d trigonometric points with target height (βάθρο)."

    Αν hsk <  0.0 τότε δεν υπάρχει βάθρο και δεν μπορεί να στηθεί όργανο ούτε στόχος στο τριγωνομετρικό.
    Αν hsk == 0.0 και δεν υπάρχει βάθρο, αλλά μπορεί να στηθεί και όργανο και στόχος στο τριγωνομετρικό.
    Αν hsk >  0.0 τότε υπάρχει βάθρο, αυτό είναι το ύψος σκόπευσης, και μπορεί να στηθεί όργανο στο τριγωνομετρικό."""
    #lindxf: int = 0
    lindxf = 0
    #it: Iterator[str] = iter(fr)
    it = iter(fr)
    for dline in it:    #type: str
        lindxf += 1
        try:
            #aa = dline[:30].rstrip()
            #x1 = float(dline[30:45])
            #y1 = float(dline[45:60])
            #z1 = float(dline[60:75])
            #if dline[75:90].strip() == "": hbaqr = 0.0
            #else:                          hbaqr = float(dline[75:90])
            aa = dline[:10].rstrip()
            x1 = float(dline[10:25])
            y1 = float(dline[25:40])
            z1 = float(dline[40:55])
            if dline[55:70].strip() == "": hbaqr = 0.0
            else:                          hbaqr = float(dline[55:70])
        except (ValueError, IndexError) as e:
            #terr: str = "%s %d of file .trg:\n%s" % ("Error at line", lindxf, e)
            terr = "%s %d of file .trg:\n%s" % ("Error at line", lindxf, e)
            raise ValueError(terr)
        yield aa, x1, y1, z1, hbaqr


#def reYps1(fr: TextIO) -> Iterator[Tuple[str, float]]:
def reYps1(fr):
    "Reads point name and height."
    lindxf = 0
    #it: Iterator[str] = iter(fr)
    it = iter(fr)
    for dline in it:
        lindxf += 1
        try:
            aa = dline[:10].rstrip()
            z1 = float(dline[10:25])
        except (ValueError, IndexError) as e:
            try: fname = fr.name
            except: fname = ".yps"
            terr = "%s %d of file %s:\n%s" % ("Error at line", lindxf, fname, e)
            raise ValueError(terr)
        yield aa, z1


#def reSyn1(fr: TextIO) -> Iterator[Tuple[str, float, float, float]]:
def reSyn1(fr):
    "Reads 3d points from a .syn file."
    lindxf = 0
    #it: Iterator[str] = iter(fr)
    it = iter(fr)
    for dline in it:
        lindxf += 1
        aa, x1, y1, z1, cod, terr = str2syn(dline)
        if aa is None:
            terr = "%s %d of file .syn:\n%s" % ("Error at line", lindxf, terr)
            raise ValueError(terr)
        yield aa, x1, y1, z1


#def str2syn(dline: str) -> Tuple[Optional[str], float, float, float, str, str]:
def str2syn(dline):
    """Transforms a text line to coordinates of a point.

    The format of the point name and point coordinates expected, is:
    {:<10s}{:15.3f}{:15.3f}{:15.3f}{:<2s}"""
    try:
        aa = dline[:10].rstrip()
        x1 = float(dline[10:25])
        y1 = float(dline[25:40])
        z1 = float(dline[40:55])
        cod = dline[55:57].strip()
        return aa, x1, y1, z1, cod, ""
    except (ValueError, IndexError) as why:
        return None, 0.0, 0.0, 0.0, "", str(why)


#def reSyn2(fr: TextIO) -> Iterator[Tuple[str, float, float, float, str]]:
def reSyn2(fr):
    "Reads 3d points from a .syn file, plus code which says if point has unreliable elevation."
    lindxf = 0
    it = iter(fr)
    for dline in it:
        lindxf += 1
        aa, x1, y1, z1, cod, terr = str2syn(dline)
        if aa is None:
            terr = "%s %d of file .syn:\n%s" % ("Error at line", lindxf, terr)
            raise ValueError(terr)
        yield aa, x1, y1, z1, cod


#def reSad1e(fr: TextIO) -> Iterator[Tuple[List[Tuple[str, float, float, float]], str]]:
def reSad1e(fr):
    "Reads the coordinates of the axis of a road; if anything wrong it stops the program."
    try:
        for cc, nam in reSad1(fr):
            yield cc, nam
    except ValueError as e:
        p_gfil.er1s(str(e))


#def reSad1(fr: TextIO) -> Iterator[Tuple[List[Tuple[str, float, float, float]], str]]:
def reSad1(fr):
    "Reads the coordinates of the axis of a road."
    #filnam: str = fr.name if hasattr(fr, "name") else "<Unknown>"
    filnam = fr.name if hasattr(fr, "name") else "<Unknown>"
    lindxf = 0
    #it: Iterator[str] = iter(fr)
    it = iter(fr)
    for nam in it:
        nam = nam.strip()
        lindxf += 1
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            aa1, x1, y1, z1, cod, terr = str2syn(dline)
            if aa1 is None:
                terr = "%s %d of .sad file %s:\n%s" % ("Error at line", lindxf, terr, filnam, e)
                raise ValueError(terr)
            cc.append((aa1, x1, y1, z1))
        yield cc, nam


#def reEry1e(fr: TextIO) -> Iterator[Tuple[List[Tuple[str, float, float, float]], str]]:
def reEry1e(fr):
    "Reads the station, ground line and grade line of a road/pipe; if anything wrong it stops the program."
    try:
        for cc, nam in reEry1(fr):
            yield cc, nam
    except ValueError as e:
        p_gfil.er1s(str(e))


#def reEry1(fr: TextIO) -> Iterator[Tuple[List[Tuple[str, float, float, float]], str]]:
def reEry1(fr):
    "Reads the station, ground line and grade line of a road/pipe."
    #filnam: str = fr.name if hasattr(fr, "name") else "<Unknown>"
    filnam = fr.name if hasattr(fr, "name") else "<Unknown>"
    lindxf = 0
    #it: Iterator[str] = iter(fr)
    it = iter(fr)
    for nam in it:
        nam = nam.strip()
        lindxf += 1
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                aa1 = dline[:8].rstrip()
                xth1 = float(dline[8:18])
                yed1 = float(dline[18:28])
                yer1 = float(dline[28:38])
            except (ValueError, IndexError) as e:
                terr = "%s %d of .ery file %s:\n%s" % ("Error at line", lindxf, filnam, e)
                raise ValueError(terr)
            cc.append((aa1, xth1, yed1, yer1))
        yield cc, nam


#def reSyk1(fr: TextIO, minvert=0, prt: ProtPrt = p_ggen.prg) -> Iterator[List[Tuple[float, float, float]]]:
def reSyk1(fr, minvert=0, prt=p_ggen.prg):
    "Reads the contours of a syk file and converts them to lists of x,y,z lists."
    for cc, nam in reSyk2(fr, minvert, prt):
        yield cc


#def reSyk1e(fr: TextIO, minvert=0, prt: ProtPrt = p_ggen.prg) -> Iterator[List[Tuple[float, float, float]]]:
def reSyk1e(fr, minvert=0, prt=p_ggen.prg):
    "Reads the contours of a syk file and converts them to lists of x,y,z lists and stops the program if error."
    try:
        for cc, nam in reSyk2(fr, minvert, prt):
            yield cc
    except ValueError as e:
        p_gfil.er1s(str(e))


#def reSyk2e(fr, minvert=0, prt: ProtPrt = p_ggen.prg) -> Iterator[Tuple[List[Tuple[float, float, float]], str]]:
def reSyk2e(fr, minvert=0, prt=p_ggen.prg):
    """Reads the contours of a syk file and converts them to lists of x,y,z lists and stops the program if error."

    It also returns the name of the polyline."""
    try:
        for cc, nam in reSyk2(fr, minvert, prt):
            yield cc, nam
    except ValueError as e:
        p_gfil.er1s(e)


#def reSyk2(fr: TextIO, minvert=0, prt: ProtPrt = p_ggen.prg) -> Iterator[Tuple[List[Tuple[float, float, float]], str]]:
def reSyk2(fr, minvert=0, prt=p_ggen.prg):
    """Reads the contours of a syk file and converts them to lists of x,y,z lists.

    It also returns the name of the polyline."""
    #filnam: str = fr.name if hasattr(fr, "name") else "<Unknown>"
    filnam = fr.name if hasattr(fr, "name") else "<Unknown>"
    lindxf = 0
    it = iter(fr)
    for dline in it:
        lindxf += 1
        try:
            z1 = float(dline[:15])
            nam = dline[17:].rstrip()
        except (ValueError, IndexError) as why:
            terr = "%s %d of syk file %s:\n%s" % ("Error at line", lindxf, why, filnam)
            raise ValueError(terr)
        #cc: List[Tuple[float, float, float]] = []
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                x1 = float(dline[:15])
                y1 = float(dline[15:30])
            except (ValueError, IndexError) as why:
                terr = "Error at line %d of syk file %s:\n%s" % (lindxf, filnam, why)
                raise ValueError(terr)
            else:
                cc.append((x1, y1, z1))   #Thanasis2018_06_12: program syk2gps() expects cc a list of tuples, not a list of lists

        if len(cc) < 2: prt("Polyline with less than %d vertices." % (2,))   #Just a warning
        if len(cc) >= minvert: yield (cc, nam) #-----------return the polyline


#def reBrk1(fr: TextIO, minvert=0, prt: ProtPrt = p_ggen.prg) -> Iterator[List[Tuple[float, float, float]]]:
def reBrk1(fr, minvert=0, prt=p_ggen.prg):
    "Reads a 3d polyline from a .brk file."
    lindxf = 0
    it = iter(fr)
    while True:
        #cc: List[Tuple[float, float, float]] = []
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                x1 = float(dline[10:25])
                y1 = float(dline[25:40])
                z1 = float(dline[40:55])
            except (ValueError, IndexError) as why:
                nam = fr.name if hasattr(fr, "name") else "<Unknown>"
                terr = "%s %d of brk file %s:\n%s" % ("Error at line", lindxf, nam, why)
                raise ValueError(terr)
            else: cc.append((x1, y1, z1))
        else:
            if len(cc) == 0: return
            raise ValueError("Unexpected end of file")
        if len(cc) < 2: prt("Polyline with less than %d vertices." % (2,))
        if len(cc) >= minvert: yield (cc) #-----------return the polyline


#def reBrk2(fr:TextIO, minvert=0, prt:ProtPrt=p_ggen.prg) -> Iterator[List[Tuple[str, float, float, float]]]:
def reBrk2(fr, minvert=0, prt=p_ggen.prg):
    "Reads a 3d polyline from a .brk fil and returns the names of the break line points as well."
    lindxf = 0
    it = iter(fr)
    while True:
        #cc:List[Tuple[str, float, float, float]] = []
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                a1 = dline[:10].rstrip()
                x1 = float(dline[10:25])
                y1 = float(dline[25:40])
                z1 = float(dline[40:55])
            except (ValueError, IndexError) as why:
                nam = fr.name if hasattr(fr, "name") else "<Unknown>"
                terr = "%s %d of brk file %s:\n%s" % ("Error at line", lindxf, nam, why)
                raise ValueError(terr)
            else: cc.append((a1, x1, y1, z1))
        else:
            if len(cc) == 0: return
            raise ValueError("Unexpected end of file")
        if len(cc) < 2: prt("Polyline with less than %d vertices." % (2,))
        if len(cc) >= minvert: yield (cc) #-----------return the polyline


#def wrTrg1(fw:TextIO, aa:str, x:float, y:float, h:float, hbaqr:float=0.0) -> None:
def wrTrg1(fw, aa, x, y, h, hbaqr=0.0):
    "Write 1 trigonometric point with predefined format."
    fw.write("{:<10s}{:15.3f}{:15.3f}{:15.3f}{:15.3f}\n".format(aa, x, y, h, hbaqr))


#def wrSyn1(fw:TextIO, aa:str, x:float, y:float, h:float, cod="") -> None:
def wrSyn1(fw, aa, x, y, h, cod=""):
    "Write 1 point with predefined format."
    fw.write("{:<10s}{:15.3f}{:15.3f}{:15.3f}{:<2s}\n".format(aa, x, y, h, cod))


#def wrYps1(fw:TextIO, aa:str, h:float) -> None:
def wrYps1(fw, aa, h):
    "Write 1 point name and height with predefined format."
    fw.write("{:<10s}{:15.3f}\n".format(aa, h))


#def wrSyk1(fw: TextIO, cc:Iterable[Sequence[float]], h:float, lay="") -> None:
def wrSyk1(fw, cc, h, lay=""):
    "Write 1 contour line in predefined format."
    fw.write("{:15.3f}  {}\n".format(h, lay))
    for cca in cc:
        fw.write("{:15.3f}{:15.3f}\n".format(cca[0], cca[1]))
    fw.write("$\n")
