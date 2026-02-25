from demusgs import ThanDEMusgs


class ThanDEMsrtm(ThanDEMusgs):
    "An DEM whose data refer to different datum than the datum of the user."

    def __init__(self):
        "Some initial values to make the object variables clear."
        super(ThanDEMsrtm, self).__init__()
        self.user2geodetGRS80 = lambda cp: cp    #Function to convert from user coordinates to GRS80 geodetic
        self.geodetGRS802User = lambda cp: cp    #Function to convert from GRS80 geodetic to user coordinates


    def thanSet(self, filnam, im=None, user2geodetGRS80=None, geodetGRS802User=None):
        "Set the tif image which contains the DEM."
        if user2geodetGRS80 != None: self.user2geodetGRS80 = user2geodetGRS80
        if geodetGRS802User != None: self.geodetGRS802User = geodetGRS802User
        return super(ThanDEMsrtm, self).thanSet(filnam, im)


    def thanCen(self):
        "Return the coordinates of the centroid taking into account the transformation."
        cu = self.geodetGRS802User(self.thanCena)
        return cu


    def thanXymm(self):
        "Return the min and max x and y coordinates taking into account the transformation."
        return self.__xymmconvert(self.xymma, self.geodetGRS802User)


    def __xymmconvert(self, xymm, convfun):
        "Convert xymm to other coordinates."
        xx = []
        yy = []
        for x1 in xymm[0], xymm[2]:
            for y1 in xymm[1], xymm[3]:
                c1 = (x1, y1, 0.0)
                cu = convfun(c1)
                x2, y2 = cu[:2]
                xx.append(x2)
                yy.append(y2)
        return (min(xx), min(yy), max(xx), max(yy))


    def thanPointZ(self, cp, native=False):
        "Calculate the z coordinate of a point with bilinear interpolation."
        if not native:
#            print "srtm: thanPointZ() 1: cp=", cp
            cp = self.user2geodetGRS80(cp)
#        print "srtm: thanPointZ() 2: cp=", cp
        return super(ThanDEMsrtm, self).thanPointZ(cp, native)


    def iterNodes(self, validnodes=True, invalidnodes=False, xymm=None):
        "Iterate through valid and or invalid nodes of the DEM."
        if xymm != None:
            print "demsrtm.iterNodes(): xymm = ", xymm
            xymm = self.__xymmconvert(xymm, self.user2geodetGRS80)
            print "demsrtm.iterNodes(): xymm = ", xymm
        for cp in super(ThanDEMsrtm, self).iterNodes(validnodes, invalidnodes, xymm):
            cu = self.geodetGRS802User(cp)
            if cp[2] == -10000.0: cu[2] = -10000.0
            yield cu


    def thanIntersegZ(self, ca, cb, native=False):
        "Compute intersections of segment with DEM lines; don't sort intersections from ca to cb."
        if native: return super(ThanDEMsrtm, self).thanIntersegZ(ca, cb, native)
        ca = self.user2geodetGRS80(ca)
        cb = self.user2geodetGRS80(cb)
        cint = super(ThanDEMsrtm, self).thanIntersegZ(ca, cb, native)
        cint = [(u, self.geodetGRS802User(c)) for u,c in cint]
        return cint


    def thanLineZendpointstoo(self, cp):
        "Calculate the z coordinates along the line cp."
        cp = [self.user2geodetGRS80(c1) for c1 in cp]
        ni, cn = super(ThanDEMsrtm, self).thanLineZendpointstoo(cp)
        cn = [self.geodetGRS802User(c) for c in cn]
        return ni, cn


    def thanLineZ(self, cp):
        "Calculate the z coordinates along the line cp."
        cp = [self.user2geodetGRS80(c1) for c1 in cp]
        ni, cn = super(ThanDEMsrtm, self).thanLineZ(cp)
        cn = [self.geodetGRS802User(c) for c in cn]
        return ni, cn
