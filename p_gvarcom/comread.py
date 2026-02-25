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
        except (ValueError, IndexError), why:
            why = "%s %d of file .syn:\n%s" % ("Error at line", lindxf, why)
            raise ValueError, why
        yield aa, x1, y1, z1


def reSyk1(fr):
    "Reads a isoline from a .syk file."
    lindxf = 0
    it = iter(fr)
    for dline in it:
        lindxf += 1
        try:
            z1 = float(dline[:15])
        except (ValueError, IndexError), why:
            why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
            raise ValueError, why
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                x1 = float(dline[:15])
                y1 = float(dline[15:30])
            except (ValueError, IndexError), why:
                why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
                raise ValueError, why
            else: cc.append([x1, y1, z1])

        if len(cc) < 2: print "Polyline with 1 or 0 vertices."
        yield cc


def reSbrk1(fr):
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
            except (ValueError, IndexError), why:
                why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
                raise ValueError, why
            else: cc.append([x1, y1, z1])
        else:
            if len(cc) == 0: return
            raise ValueError, "Unexpected end of file"
        if len(cc) < 2: print "Polyline with 1 or 0 vertices."
        yield cc
