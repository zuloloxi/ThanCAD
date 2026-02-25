import p_ggen, p_gfil


def readSyks1(fr, minvert=0, prt=p_ggen.prg):
    "Reads the contours of a syk file and converts them to lists of x,y,z lists."
    lindxf = 0
    it = iter(fr)
    for dline in it:
        lindxf += 1
        try:
            z1 = float(dline[:15])
        except (ValueError, IndexError), why:
            why = "%s %d of syk file %s:\n%s" % ("Error at line", lindxf, why, fr.name)
            raise ValueError, why
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                x1 = float(dline[:15])
                y1 = float(dline[15:30])
            except (ValueError, IndexError), why:
                why = "%s %d of syk file :\n%s" % ("Error at line", lindxf, why, fr.name)
                raise ValueError, why
            else:
                cc.append([x1, y1, z1])

        if len(cc) < 2: prt("Polyline with less than %d vertices." % (2,))
        if len(cc) >= minvert: yield (cc) #-----------return the polyline


def readSyks1e(fr, minvert=0, prt=p_ggen.prg):
    "Reads the contours of a syk file and converts them to lists of x,y,z lists and stops the program if error."
    try:
        return readSyks1(fr, minvert, prt)
    except ValueError, e:
        p_gfil.er1s(e)


def readBrks1(fr, minvert=0, prt=p_ggen.prg):
    "Reads the breaklines of a brk file and converts them to lists of x,y,z lists."
    lindxf = 0
    it = iter(fr)
    clines = []
    cc = []
    for dline in it:
        lindxf += 1
        if dline.strip() == "$":
                if len(cc) < 2: prt("Break line with less than %d vertices." % (2,))
                if len(cc) >= minvert: clines.append(cc) #-----------Store the polyline
                cc = []
        else:
            try:
                x1 = float(dline[10:25])
                y1 = float(dline[25:40])
                z1 = float(dline[40:55])
            except (ValueError, IndexError), why:
                why = "%s %d of brk file %s:\n%s" % ("Error at line", lindxf, why, name)
                raise ValueError, why
            else: cc.append([x1, y1, z1])
    return clines
