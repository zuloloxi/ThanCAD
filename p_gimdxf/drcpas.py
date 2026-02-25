from fnmatch import fnmatch
from operator import itemgetter
from math import hypot, fabs
import p_ggen
from p_gmath import thanNear3
from . import thanimpdxfget, thanimpdxf


class ThanDrConpas(thanimpdxfget.ThanDrWarn):
    "A class which gets control/pass points from a .dxf file."

    def __init__(self, filnam="<undefined>", ctype="noname", layer=("fotost*", ),
        dxyname=(0.0,0.0), dxyheight=(0.0,0.0), obj="POINT", prt=p_ggen.prg):
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
        if type == control3: Σημεία ως points, ονομασία και υψόμετρο ως ξεχωριστά texts
                κοντά στο σημείο (η συντεταγμένη Z ΑΓΝΟΕΙΤΑΙ). Η μεταβλητή
                layer πρέπει να είναι tuple/list με ακριβώς 3 στοιχεία. Πρώτο layer
                για σημεία, δεύτερο για ονομασίες και τρίτο για υψόμετρα.
        if layer == "*" all the layers are searched. Else only the layer with name
            the content of the variable layer is searched.
            Another possibility is if layer ends with * (for example fotost*). In
            this case all the layers beginning with fotost are searched.
        dxyname is dx and dy which are added algebrically to the coordinates of points
            (cname) in representations 2, 3 and 5, in case the coordinates of texts
            are (systematically) in wrong position.
        dxyheight is x and y which are added algebrically to the coordinates of points
            in representations 4 and 5, in case the coordinates of heights
            are (systematically) in wrong position.
        obj is the object which reopresents a point. Usually "POINT", but Autocad 
            Civil uses also "CIRCLE" !!!!
        """
        thanimpdxfget.ThanDrWarn.__init__(self, layer, prt=prt)
        self.cxypix =  []      # pixel coordinates of control points
        self.cname =   []      # texts (names of points or name/height of points
        self.cheight = []      # texts (names of points or name/height of points
        self.filnam = filnam   # Name of the dxf file
        self.ctype = ctype     # Type of points: noname, pixel, control, nonamez, control3

        if ctype == "control3" and len(layer) != 3:
            self.prt("For point type 'control3' there must be exactly 3 layers defined.")
            self.prt("%d were defined" % (len(layer),))
            raise p_ggen.RecordedError("Errors recorded above.")
        self.dxyname = tuple(dxyname)
        self.dxyheight = tuple(dxyheight)
        self.obj = obj


    def dxfPoint(self, xx, yy, zz, lay, handle, col):
        "Selects the points only in certain layers."
        lay = lay.lower()
        if self.obj == "POINT" and self.isLayerKnown(lay):
            if col is None: col = 7
            if self.ctype != "control3":
                self.cxypix.append([None, xx, yy, zz, lay, col])
                return
            if fnmatch(lay, self._layknopat[0]):
                self.cxypix.append([None, xx, yy, zz, lay, col])
                return
        self.warnObj(lay, self.POINT)


    def dxfCircle(self, xx, yy, zz, lay, handle, col, r):
        "Selects the circles only in certain layers if the representation of points is CIRCLE."
        lay = lay.lower()
        if self.obj == "CIRCLE" and self.isLayerKnown(lay):
            if col is None: col = 7
            if self.ctype != "control3":
                self.cxypix.append([None, xx, yy, zz, lay, col])
                return
            if fnmatch(lay, self._layknopat[0]):
                self.cxypix.append([None, xx, yy, zz, lay, col])
                return
        self.warnObj(lay, self.CIRCLE)


    def dxfLine(self, xx, yy, zz, lay, handle, col):
        "Selects the circles only in certain layers if the representation of points is LINE."
        lay = lay.lower()
        if self.obj == "LINE" and self.isLayerKnown(lay):
            if len(xx) != 2: return    # line must have exactly two points
            aa = list(zip(xx, yy, zz))
            if not thanNear3(aa[0], aa[1]): return #Both line points must have the same coordinates
            if col is None: col = 7
            if self.ctype != "control3":
                self.cxypix.append([None, xx[0], yy[0], zz[0], lay, col])
                return
            if fnmatch(lay, self._layknopat[0]):
                self.cxypix.append([None, xx[0], yy[0], zz[0], lay, col])
                return
        self.warnObj(lay, self.LINE)


    def dxfText(self, xx, yy, zz, lay, handle, col, t, h, theta):
        "Selects the texts in certain layers."
        lay = lay.lower()
        if not self.isLayerKnown(lay):      #If layer in not known (i.e. not the ones the user defined) do nothing
            self.warnObj(lay, self.TEXT)
            return

        if self.ctype != "control3":    #All cases except 5
            if self.ctype == "pixel" or self.ctype == "control":  #Get name text for cases 2, 3
                self.cname.append([t, xx, yy, 0.0, lay])
            elif self.ctype == "nonamez":                         #Get name height for case 4
                self.cheight.append([t, xx, yy, 0.0, lay])
            else:                                                 #Case 1: no name, no height
                self.warnObj(lay, self.TEXT)

        else:                           #Case 5
            if fnmatch(lay, self._layknopat[1]):    #second layer contains name
                self.cname.append([t, xx, yy, 0.0, lay])
            elif fnmatch(lay, self._layknopat[2]):  #third layer contains heights
                self.cheight.append([t, xx, yy, 0.0, lay])
            else:
                self.warnObj(lay, self.TEXT)


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
                raise p_ggen.RecordedError("Errors recorded above.")
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
                raise p_ggen.RecordedError("Errors recorded above.")
            cname1[0] = t1.strip()
            cname1[3] = ht


    def dupPoints(self, dmax=0.005, dhmax=1.0e100):
        "Erase duplicate points, which differ less horizontal distance dmax and less than elevation difference dhmax."
        self.prt("Checking for duplicate points..", "info1")
        i = 0
        self.cxypix.sort(key=itemgetter(1))
        while i < len(self.cxypix):
            aa1, x1, y1, z1, _, _ = self.cxypix[i]
            if (i+1) % 10000 == 0: self.prt("{}/{}".format(i+1, len(self.cxypix)))
            j = i + 1
            while j < len(self.cxypix):
                aa2, x2, y2, z2, _, _ = self.cxypix[j]
                if x2-x1 > dmax: break
                ds = hypot(x2-x1, y2-y1)
                if ds > dmax or fabs(z2-z1) > dhmax:
                    j += 1
                else:
                    self.prt("Duplicate point deleted: %.3f  %.3d" % (x2, y2), "can1")
                    del self.cxypix[j]
            i += 1


    def dupTexts(self, cn, dmax=0.005):
        "Erase duplicate texts, which differ less horizontal distance dmax and have the same text (right stripped)."
        self.prt("Checking for duplicate texts..", "info1")
        cn.sort(key=itemgetter(1))
        i = 0
        while i < len(cn):
            t1,x1,y1,h1,_ = cn[i]
            t1 = t1.rstrip()
            if (i+1) % 10000 == 0: self.prt("{}/{}".format(i+1, len(cn)))
            j = i + 1
            while j < len(cn):
                t2,x2,y2,h2,_ = cn[j]
                if x2-x1 > dmax: break
                ds = hypot(x2-x1, y2-y1)
                if ds > dmax or t1 != t2.rstrip():
                    j += 1
                else:
                    self.prt("Duplicate name deleted: '%s'  %.3f  %.3d" % (t2, x2, y2), "can1")
                    del cn[j]
            i += 1


    def corTexts(self, cn, dxy, tit):
        "Correlates texts with points; the text (name, name/height, or height) of a point is the closest text to it."
        self.prt("Correlating points with {}..".format(tit), "info1")
        corcname = []
        dx, dy = dxy[:2]
        for i,(aa,x,y,h, _, _) in enumerate(self.cxypix):
            if len(cn) < 1:
                self.prt("Error in file %s: Point with %s coordinates %.1f %.1f:" % (self.filnam, self.ctype, x,y), "can")
                self.prt("The {} of this point was not defined.".format(tit[:-1]), "can")
                self.prt("(The number of point {} is less than the number of points!)".format(tit), "can")
                raise p_ggen.RecordedError("Errors recorded above.")
            ds = [(hypot(x+dx-xt, y+dy-yt), j) for j,(t,xt,yt,ht,_) in enumerate(cn)]
            d, j = min(ds)
            t,xt,yt,ht,_ = cn[j]
            ds = [(hypot(x1+dx-xt, y1+dy-yt), i1) for i1,(aa1,x1,y1,h1,_,_) in enumerate(self.cxypix) if aa1 == None]
            d, i1 = min(ds)
            if i1 != i:
                x1, y1 = self.cxypix[i1][1:3]
                self.prt("Error in file %s: Point with %s coordinates %.1f %.1f:" % (self.filnam, self.ctype, x, y), "can")
                self.prt("The {} of this point was probably not defined.".format(tit[:-1]), "can")
                self.prt("The nearest {} to this point is: '{}' but it was found to refer to".format(tit[:-1], t), "can")
                self.prt("point with pixel coordinates %.1f %.1f" % (x1,y1))
                raise p_ggen.RecordedError("Errors recorded above.")
            corcname.append(cn.pop(j))
        if len(cn) > 0:
            self.prt("Warning in file {}: The number of points is less than the number of point {}".format(self.filnam, tit), "can1")
            self.prt("The following point {} do not refer to any point:".format(tit), "can1")
            for cname1 in cn: self.prt("%s" % (cname1,))
        return corcname


    def addName(self):
        "Adds suitable name to simple points."
        i = 1
        for c in self.cxypix:
            c[0] = str(i)
            i += 1


def thanDxfGetConpas(fdxf, ctype, layer=("fotost*",), dxyname=(0.0,0.0), dxyheight=(0.0,0.0), obj="POINT", prt=p_ggen.prg):
    """Reads the coordinates of the control points from dxf file.

    noname:  1. Σημεία ως points (με ενδεχόμενο υψόμετρο στη συντεταγμένη Z), χωρίς ονομασία
    pixel:   2. Σημεία ως points και ονομασία ως text κοντά στο σημείο
                (και με ενδεχόμενο υψόμετρο στη συντεταγμένη Z)
    control: 3. Σημεία ως points και ονομασία/υψόμετρο (πχ 'S1/42.4') ως text
                κοντά στο σημείο (η συντεταγμένη Z ΑΓΝΟΕΙΤΑΙ)
    nonamez: 4. Σημεία ως points και υψόμετρο ως text κοντά στο σημείο
                (τα σημεία είναι ανώνυμα και η συντεταγμένη Z ΑΓΝΟΕΙΤΑΙ)
    control3:5. Σημεία ως points, ονομασία και υψόμετρο ως ξεχωριστά texts
                κοντά στο σημείο (η συντεταγμένη Z ΑΓΝΟΕΙΤΑΙ). Η μεταβλητή
                layer πρέπει να είναι tuple/list με ακριβώς 3 στοιχεία. Πρώτο layer
                για σημεία, δεύτερο για ονομασίες και τρίτο για υψόμετρα.
    dxyname is dx and dy which are added algebrically to the coordinates of points
        (cname) in representations 2, 3 and 5, in case the coordinates of texts
        are (systematically) in wrong position.
    dxyheight is x and y which are added algebrically to the coordinates of points
        in representations 4 and 5, in case the coordinates of heights
        are (systematically) in wrong position.
    obj is the object which reopresents a point. Usually "POINT", but Autocad 
        Civil uses also "CIRCLE" !!!!
    """
    dr = ThanDrConpas(fdxf.name, ctype, layer, dxyname, dxyheight, obj, prt)
    t = thanimpdxf.ThanImportDxf(fdxf, dr)
    t.thanImport()
    if ctype == "noname":
        dr.addName()
    elif ctype == "pixel":
        dr.validateName(dr.cname)
        dr.dupPoints()
        dr.dupTexts(dr.cname)
        cname = dr.corTexts(dr.cname, dr.dxyname, "names")
        for cxy, cn in zip(dr.cxypix, cname):
            cxy[0] = cn[0]
            cxy[4] = "{:20s}{}".format(cxy[4][:20], cn[4]) #Add the layer of the text to the layer of the point
    elif ctype == "control":
        dr.validateNameHeight(dr.cname)
        cname = dr.corTexts(dr.cname, dr.dxyname, "names/heights")
        for cxy, cn in zip(dr.cxypix, cname):
            cxy[0] = cn[0]
            cxy[3] = cn[3]
            cxy[4] = "{:20s}{}".format(cxy[4][:20], cn[4]) #Add the layer of the text to the layer of the point
    elif ctype == "nonamez":
        dr.validateHeight(dr.cheight)
        cheight = dr.corTexts(dr.cheight, dr.dxyheight, "heights")
        for cxy, cn in zip(dr.cxypix, cheight):
            cxy[3] = cn[3]
            cxy[4] = "{:20s}{}".format(cxy[4][:20], cn[4]) #Add the layer of the text to the layer of the point
        dr.addName()
    elif ctype == "control3":
        dr.validateName(dr.cname)
        dr.validateHeight(dr.cheight)

        dr.dupPoints()             #Thanasis2020_02_09
        dr.dupTexts(dr.cname)      #Thanasis2020_02_09
        dr.dupTexts(dr.cheight)    #Thanasis2020_02_09

        cname   = dr.corTexts(dr.cname,   dr.dxyname,   "names")
        cheight = dr.corTexts(dr.cheight, dr.dxyheight, "heights")
        for cxy, cn, ch in zip(dr.cxypix, cname, cheight):
            cxy[0] = cn[0]
            cxy[3] = ch[3]
            cxy[4] = "{:20s}{}".format(cxy[4][:20], cn[4]) #Add the layer of the text to the layer of the point
    else:
        prt("Unknown type of points: '%s'" % (ctype,))
        raise p_ggen.RecordedError("Errors recorded above.")
    return dr.cxypix


def testThanDxfGetConpas():
    "Test dxf import of named points."
    f = open("trap.dxf", "r")
    cxypix = thanDxfGetConpas(f, "pixel")
    for a,x,y,h,lay,icol in cxypix:
        print("%10s%15.3f%15.3f%15.3f" % (a,x,y,h))
    f = open("trap.dxe", "r")
    cxypix = thanDxfGetConpas(f, "EGSA87")
    for a,x,y,h,lay,icol in cxypix:
        print("%10s%15.3f%15.3f%15.3f" % (a,x,y,h))


def testThanDrConpas():
    "Test dxf import."
    f = file("trap1.dxe", "r")
    xy = thanDxfGetConpas(f, ctype="EGSA87")
    for xy1 in xy: print(xy1)
    f.close()


if __name__ == "__main__": testThanDxfGetConpas()
