import p_ggen, p_gfil


def reSyn1(fr):
    "Reads 3d points from a .syn file."
    lindxf = 0
    it = iter(fr)
    for dline in it:
        lindxf += 1
        try:
            aa = dline[:10].rstrip()
            x1 = float(dline[10:25])
            y1 = float(dline[25:40])
            z1 = float(dline[40:55])
        except (ValueError, IndexError) as why:
            why = "%s %d of file .syn:\n%s" % ("Error at line", lindxf, why)
            raise ValueError(why)
        yield aa, x1, y1, z1


def reSyn2(fr):
    "Reads 3d points from a .syn file, plus code which says if point has unreliable elevation."
    lindxf = 0
    it = iter(fr)
    for dline in it:
        lindxf += 1
        try:
            aa = dline[:10].rstrip()
            x1 = float(dline[10:25])
            y1 = float(dline[25:40])
            z1 = float(dline[40:55])
            cod = dline[55:57].strip()
        except (ValueError, IndexError) as why:
            why = "%s %d of file .syn:\n%s" % ("Error at line", lindxf, why)
            raise ValueError(why)
        yield aa, x1, y1, z1, cod


def reSyk1(fr, minvert=0, prt=p_ggen.prg):
    "Reads the contours of a syk file and converts them to lists of x,y,z lists."
    for cc, nam in reSyk2(fr, minvert, prt):
        yield cc


def reSyk1e(fr, minvert=0, prt=p_ggen.prg):
    "Reads the contours of a syk file and converts them to lists of x,y,z lists and stops the program if error."
    try:
        for cc, nam in reSyk2(fr, minvert, prt):
            yield cc
    except ValueError as e:
        p_gfil.er1s(e)


def reSyk2e(fr, minvert=0, prt=p_ggen.prg):
    """Reads the contours of a syk file and converts them to lists of x,y,z lists and stops the program if error."

    It also returns the name of the polyline."""
    try:
        for cc, nam in reSyk2(fr, minvert, prt):
            yield cc, nam
    except ValueError as e:
        p_gfil.er1s(e)


def reSyk2(fr, minvert=0, prt=p_ggen.prg):
    """Reads the contours of a syk file and converts them to lists of x,y,z lists.

    It also returns the name of the polyline."""
    filnam = fr.name if hasattr(fr, "name") else "<Unknown>"
    lindxf = 0
    it = iter(fr)
    for dline in it:
        lindxf += 1
        try:
            z1 = float(dline[:15])
            nam = dline[17:].rstrip()
        except (ValueError, IndexError) as why:
            why = "%s %d of syk file %s:\n%s" % ("Error at line", lindxf, why, filnam)
            raise ValueError(why)
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                x1 = float(dline[:15])
                y1 = float(dline[15:30])
            except (ValueError, IndexError) as why:
                why = "Error at line %d of syk file %s:\n%s" % (lindxf, filnam, why)
                raise ValueError(why)
            else:
                cc.append([x1, y1, z1])

        if len(cc) < 2: prt("Polyline with less than %d vertices." % (2,))   #Just a warning
        if len(cc) >= minvert: yield (cc, nam) #-----------return the polyline


def reBrk1(fr, minvert=0, prt=p_ggen.prg):
    "Reads a 3d polyline from a .brk file."
    lindxf = 0
    it = iter(fr)
    while True:
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
                why = "Error at line %d of brk file %s:\n%s" % ("Error at line", lindxf, why)
                raise ValueError(why)
            else: cc.append([x1, y1, z1])
        else:
            if len(cc) == 0: return
            raise ValueError("Unexpected end of file")
        if len(cc) < 2: prt("Polyline with less than %d vertices." % (2,))
        if len(cc) >= minvert: yield (cc) #-----------return the polyline


def reBrk2(fr, minvert=0, prt=p_ggen.prg):
    "Reads a 3d polyline from a .brk fil and returns the names of the break line points as well."
    lindxf = 0
    it = iter(fr)
    while True:
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
                why = "Error at line %d of brk file %s:\n%s" % ("Error at line", lindxf, why)
                raise ValueError(why)
            else: cc.append([a1, x1, y1, z1])
        else:
            if len(cc) == 0: return
            raise ValueError("Unexpected end of file")
        if len(cc) < 2: prt("Polyline with less than %d vertices." % (2,))
        if len(cc) >= minvert: yield (cc) #-----------return the polyline
