# -*- coding: iso-8859-7 -*-
from fnmatch import fnmatch
import p_ggen
import thanimpdxfget, thanimpdxf


class ThanDrConpas(thanimpdxfget.ThanDrWarn):
    "A class which gets control/pass points from a .dxf file."

    def __init__(self, filnam="<undefined>", ctype="noname", layer=("fotost*", ), prt=p_ggen.prg):
        """Sets the type of points and the layers to search.

        If type == "noname" then x, y, z coordinates of all points plus an
            arbitrary name are returned.
        If type == "pixel" then x, y, z coordinates of all points are returned.
            Furthermore, the program looks for texts and finds the closest text to 
            a point, and considers it as the point's name. As a precaution, this
            point must also be the closest point to the text found, or else there
            is ambiguity and the program returns an error. The texts must not
            contain the character '/'.
        If type == "control" then x, y coordinates of all points are returned.
            Furthermore, the program looks for texts and finds the closest text to
            a point, and considers it as the point's name. As a precaution, this
            point must also be the closest point to the text found, or else there
            is ambiguity and the program returns an error. The texts must
            contain the character '/' and after this the z coordinate of the point
            for example "Point1/123.457". This z is returned.
        if layer == "*" all the layers are searched. Else only the layer with name
            the content of the variable layer is searched.
            Another possibility is if layer ends with * (for example fotost*). In
            this case all the layers beginning with fotost are searched.
        """
        thanimpdxfget.ThanDrWarn.__init__(self, layer, prt=prt)
        self.cxypix = []       # pixel coordinates of control points
        self.cname =  []       # texts (names of points or name/height of points
        self.filnam = filnam   # Name of the dxf file
        self.ctype = ctype     # Type of points: pixel, control, or noname
        if ctype == "control3" and len(layer) != 3:
            self.prt("For point type 'control3' there must be exactly 3 layers defined.")
            self.prt("%d were defined" % (len(layer),))
            raise p_ggen.RecordedError, "Errors recorded above."


    def dxfPoint(self, xx, yy, zz, lay, handle, col):
        "Selects the polylines only in certain layers."
        lay = lay.lower()
        if self.isLayerKnown(lay):
            if self.ctype != "control3":
                self.cxypix.append([None, xx, yy, zz])
                return
            if fnmatch(lay, self._layknopat[0]):
                self.cxypix.append([None, xx, yy, zz])
                return
        self.warnObj(lay, self.POINT)


    def dxfText(self, xx, yy, zz, lay, handle, col, t, h, theta):
        "Selects the circle of layer plaisio; its center is the origin point."
        lay = lay.lower()
        if self.isLayerKnown(lay):
            if self.ctype != "control3":
                self.cname.append([t, xx, yy, 0.0, lay])
                return
            for i in xrange(1, 3):
                if fnmatch(lay, self._layknopat[i]):
                    self.cname.append([t, xx, yy, 0.0, lay])
                    return
        self.warnObj(lay, self.TEXT)


    def splitTexts(self):
        "In the case of control3 there are exactly 3 layers; split cname to last 2 layers which should have the texts."
        cname = [[], [], []]
        for cname1 in self.cname:
            lay = cname1[-1]
            for i in xrange(1, 3):
                if fnmatch(lay, self._layknopat[i]): break
            else:
                assert 0, "Control3: Texts belongs to other layer!!!"
            cname[i].append(cname1)
        self.cname = cname


    def validateHeight(self, cname):
        "The texts must be numbers which are heights."
        for cname1 in cname:
            try:
                t = cname1[0]
                ht = float(t)
            except (ValueError, IndexError):
                self.prt("Error in file %s: Illegal height '%s':" % (self.filnam, t), "can")
                self.prt("The height must be a numeric value.", "can")
                self.prt("For example: '128.89' or '12.989'", "can")
                raise p_ggen.RecordedError, "Errors recorded above."
            cname1[0] = "noname"
            cname1[3] = ht


    def validateName(self, cname):
        "The texts must be names (texts NOT the form name/height)."
        for cname1 in cname:
            t = cname1[0]
            try:
                t1, t2 = t.split("/")
                ht = float(t2)
            except (ValueError, IndexError):
                pass
            else:
                self.prt("Warning in file %s: It seems that you defined height to point '%s':" % (self.filnam, t), "can1")
                self.prt("    The point should NOT be of the form:", "can1")
                self.prt("     <name> / <height>", "can1")
                self.prt("    Please remove the height from the point.", "can1")
            cname1[0] = t.strip()


    def validateNameHeight(self, cname):
        "The texts must be of the form name/height."
        for cname1 in cname:
            t = cname1[0]
            try:
                t1, t2 = t.split("/")
                ht = float(t2)
            except (ValueError, IndexError):
                self.prt("Error in file %s: Illegal point name '%s':" % (self.filnam, t), "can")
                self.prt("The point should be of the form:", "can")
                self.prt(" <name> / <height>", "can")
                self.prt("For example: 'P1 / 128.89' or '1/12.989'", "can")
                raise p_ggen.RecordedError, "Errors recorded above."
            cname1[0] = t1.strip()
            cname1[3] = ht


    def corTexts(self, cname):
        "Correlates texts with points; the text (name, name/height, or height) of a point is the closest text to it."
        corcname = []
        for i,(aa,x,y,h) in enumerate(self.cxypix):
            if len(cname) < 1:
                self.prt("Error in file %s: Point with %s coordinates %.1f %.1f:" % (self.filnam, self.ctype, x,y), "can")
                self.prt("The name and/or the height of this point was not defined.", "can")
                self.prt("(The number of point names and/or heights is less than the number of points!)", "can")
                raise p_ggen.RecordedError, "Errors recorded above."
            ds = [((x-xt)**2+(y-yt)**2, j) for j,(t,xt,yt,ht,_) in enumerate(cname)]
            d, j = min(ds)
            t,xt,yt,ht,_ = cname[j]
            ds = [((x1-xt)**2+(y1-yt)**2, i1) for i1,(aa1,x1,y1,h1) in enumerate(self.cxypix) if aa1 == None]
            d, i1 = min(ds)
            if i1 != i:
                self.prt("Error in file %s: Point with %s coordinates %.1f %.1f:" % (self.filnam, self.ctype, x,y), "can")
                self.prt("The name and/or height of this point was probably not defined.", "can")
                self.prt("The nearest name and/or height to this point is: '%s' but it was found to refer to" % t, "can")
                self.prt("point with pixel coordinates %.1f %.1f" % (x1,y1))
                raise p_ggen.RecordedError, "Errors recorded above."
            corcname.append(cname.pop(j))
        if len(cname) > 0:
            self.prt("Warning in file %s: The number of points is less than the number of point names" % self.filnam, "can1")
            self.prt("and/or heights. The following point names and/or heights do not refer to any point:", "can1")
            for cname1 in cname: self.prt("%s" % (cname1,))
        return corcname


    def addName(self):
        "Adds suitable name to simple points."
        i = 1
        for c in self.cxypix:
            c[0] = str(i)
            i += 1


def thanDxfGetConpas(fdxf, ctype, layer=("fotost*",), prt=p_ggen.prg):
    """Reads the coordinates of the control points from dxf file.

    noname:  1. Σημεία ως points (με ενδεχόμενο υψόμετρο στη συντεταγμένη Z)
    pixel:   2. Σημεία ως points και ονομασία ως text κοντά στο σημείο
                (και με ενδεχόμενο υψόμετρο στη συντεταγμένη Z)
    control: 3. Σημεία ως points και ονομασία/υψόμετρο (πχ 'S1/42.4') ως text
                κοντά στο σημείο (η συντεταγμένη Z ΑΓΝΟΕΙΤΑΙ)
    nonamez: 4. Σημεία ως points και υψόμετρο ως text κοντά στο σημείο
                (τα σημεία είναι ανώνυμα και η συντεταγμένη Z ΑΓΝΟΕΙΤΑΙ)
    control3:5. Σημεία ως points, υψόμετρο και ονομασία ως ξεχωριστά texts
                κοντά στο σημείο (η συντεταγμένη Z ΑΓΝΟΕΙΤΑΙ). Η μεταβλητή
                layer πρέπει να είναι tuple/list με ακριβώς 3 στοιχεία.
    """
    dr = ThanDrConpas(fdxf.name, ctype, layer, prt)
    t = thanimpdxf.ThanImportDxf(fdxf, dr)
    t.thanImport()
    if ctype == "noname":
        dr.addName()
    elif ctype == "pixel":
        dr.validateName(dr.cname)
        cname = dr.corTexts(dr.cname)
        for i in xrange(len(dr.cxypix)):
            dr.cxypix[i][0] = cname[i][0]
    elif ctype == "control":
        dr.validateNameHeight(dr.cname)
        cname = dr.corTexts(dr.cname)
        for i in xrange(len(dr.cxypix)):
            dr.cxypix[i][0] = cname[i][0]
            dr.cxypix[i][3] = cname[i][3]
    elif ctype == "nonamez":
        dr.validateHeight(dr.cname)
        cname = dr.corTexts(dr.cname)
        for i in xrange(len(dr.cxypix)):
            dr.cxypix[i][3] = cname[i][3]
        dr.addName()
    elif ctype == "control3":
        dr.splitTexts()
        dr.validateName(dr.cname[1])
        dr.validateHeight(dr.cname[2])
        cname   = dr.corTexts(dr.cname[1])
        cheight = dr.corTexts(dr.cname[2])
        for i in xrange(len(dr.cxypix)):
            dr.cxypix[i][0] = cname[i][0]
            dr.cxypix[i][3] = cheight[i][3]
    else:
        prt("Unknown type of points: '%s'" % (ctype,))
        raise p_ggen.RecordedError, "Errors recorded above."
    return dr.cxypix


def testThanDxfGetConpas():
    "Test dxf import of named points."
    f = open("trap.dxf", "r")
    cxypix = thanDxfGetConpas(f, "pixel")
    for a,x,y,h in cxypix:
        print "%10s%15.3f%15.3f%15.3f" % (a,x,y,h)
    f = open("trap.dxe", "r")
    cxypix = thanDxfGetConpas(f, "EGSA87")
    for a,x,y,h in cxypix:
        print "%10s%15.3f%15.3f%15.3f" % (a,x,y,h)


def testThanDrConpas():
    "Test dxf import."
    f = file("trap1.dxe", "r")
    xy = thanDxfGetConpas(f, ctype="EGSA87")
    for xy1 in xy: print xy1
    f.close()


if __name__ == "__main__": testThanDxfGetConpas()
