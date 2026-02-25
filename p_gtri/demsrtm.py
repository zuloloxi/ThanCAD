from math import hypot, pi
from p_gmath import dpt
import p_gnum, p_gvarcom
from .demusgs import ThanDEMusgs


class ThanDEMsrtm(ThanDEMusgs):
    "An DEM whose data refer to different datum than the datum of the user."

    def __init__(self, isorthometric=True, nodatadef=None):
        "Some initial values to make the object variables clear."
        super(ThanDEMsrtm, self).__init__(nodatadef)
        self.isorthometric = isorthometric
        self.user2geodetGRS80 = lambda cp: cp    #Function to convert from user coordinates to GRS80 geodetic
        self.geodetGRS802User = lambda cp: cp    #Function to convert from GRS80 geodetic to user coordinates


    def thanSet(self, filnam, im=None, user2geodetGRS80=None, geodetGRS802User=None):
        "Set the tif image which contains the DEM."
        if user2geodetGRS80 is not None: self.user2geodetGRS80 = user2geodetGRS80
        if geodetGRS802User is not None: self.geodetGRS802User = geodetGRS802User
        return super(ThanDEMsrtm, self).thanSet(filnam, im)


    def thanNew(self, X0, Y0, XB, YB, DX, DY, mode, nodata=None, native=False, user2geodetGRS80=None, geodetGRS802User=None):
        """Create a new dem which contains no values.

        user2geodetGRS80(), geodetGRS802User() should be set here or set by 
        thanSetConversion() previously."""
        if user2geodetGRS80 is not None: self.user2geodetGRS80 = user2geodetGRS80
        if geodetGRS802User is not None: self.geodetGRS802User = geodetGRS802User
        assert native, "native=False has not yet been implemented"
        return super().thanNew(X0, Y0, XB, YB, DX, DY, mode, nodata=None, native=True)


    def thanSetConversion(self, user2geodetGRS80=None, geodetGRS802User=None):
        "Set the conversion functions."
        if user2geodetGRS80 is not None: self.user2geodetGRS80 = user2geodetGRS80
        if geodetGRS802User is not None: self.geodetGRS802User = geodetGRS802User


    def thanCen(self, native=False):
        "Return the coordinates of the centroid taking into account the transformation."
        cc = super().thanCen()
        return cc if native else self.geodetGRS802User(cc)


    def thanDxy(self):
        """Return the DX, DY of the dem.

        Because the coordinate transformation usually leads to variable DX, DY
        the average DX, DY are returned.
        """
        ca = (self.xymma[0], self.thanCena[1], 0.0)
        ca = self.geodetGRS802User(ca)
        cb = (self.xymma[2], self.thanCena[1], 0.0)
        cb = self.geodetGRS802User(cb)
        dx = hypot(cb[1]-ca[1], cb[0]-ca[0]) / self.nxcols

        ca = (self.thanCena[0], self.xymma[1], 0.0)
        ca = self.geodetGRS802User(ca)
        cb = (self.thanCena[0], self.xymma[3], 0.0)
        cb = self.geodetGRS802User(cb)
        dy = hypot(cb[1]-ca[1], cb[0]-ca[0]) / self.nyrows
        return dx, dy


    def than2Num(self, native=False, centroidundulation=True):
        """Return the DEM as a numpy array.

        If native is false, then orthometric elevations are returned."""
        a = super().than2Num()
        if native: return a             #Return whatever type of elevation the underlying DEM has.
        if self.isorthometric: return a #The underlying DEM is already orthometric
        if centroidundulation:  #Subtract the undulation of the centroid from all elevations: it
                                #practically introduces no error if the region is small
            cp = self.thanCen(native=True)   #we need object coordinates of the undelying dem
            zu = undul(cp)
            valid = p_gnum.not_equal(a, self.GDAL_NODATA)
            b = p_gnum.where(valid, a-zu, a)
            return b
        else:
            nyrows, nxcols = a.shape
            for iy in range(nyrows):
                for jx in range(nxcols):
                    if a[iy, jx] == self.GDAL_NODATA: continue
                    cp = self.thanObjCoor(jx, iy, native=True)   #we need object coordinates of the undelying dem
                    a[iy, jx] -= undul(cp)
        return a


    def thanXymm(self, native=False):
        "Return the min and max x and y coordinates taking into account the transformation."
        if native: return self.xymma
        return self.__xymmconvert(self.xymma, self.geodetGRS802User)


    def __xymmconvertold(self, xymm, convfun):
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


    def __xymmconvert(self, xymm, convfun):
        "Convert xymm to other coordinates."
        xymmb = p_gvarcom.Xymm()
        for x1 in xymm[0], xymm[2]:
            for y1 in xymm[1], xymm[3]:
                c1 = (x1, y1, 0.0)
                cu = convfun(c1)
                xymmb.includePoint(cu)
        return xymmb


    def thanPointZ(self, cp, native=False):
        "Calculate the z coordinate of a point with bilinear interpolation."
        if not native:
            #print "srtm: thanPointZ() 1: cp=", cp
            cp = self.user2geodetGRS80(cp)
        #print "srtm: thanPointZ() 2: cp=", cp
        z = super(ThanDEMsrtm, self).thanPointZ(cp, native)
        if not self.isorthometric and not native and z is not None: z -= undul(cp)
        return z


    def thanPixelCoor(self, cp, native=False):
        "Return the pixel coordinates of the point."
        if not native:
#            print "srtm: thanPointZ() 1: cp=", cp
            cp = self.user2geodetGRS80(cp)
#        print "srtm: thanPointZ() 2: cp=", cp
        return super(ThanDEMsrtm, self).thanPixelCoor(cp, native)


    def thanObjCoor(self, jx, iy, native=False):
        "Return the object coordinates of a pixel."
        cp = super().thanObjCoor(jx, iy, native=True)
        if not native:
            cp = self.geodetGRS802User(cp)
        return cp


    def iterNodes(self, validnodes=True, invalidnodes=False, xymm=None):
        """Iterate through valid and or invalid nodes of the DEM.

        If xymm is not None, only the points within xymm rectangle will be
        returned. However, because the underlying ThanDEMusgs has different
        coordinate system, some points not in xymm may be returned too."""
        if xymm is not None:
            xymm = self.__xymmconvert(xymm, self.user2geodetGRS80)
        for cp in super(ThanDEMsrtm, self).iterNodes(validnodes, invalidnodes, xymm):
            cu = self.geodetGRS802User(cp)
            if cp[2] == -10000.0:
                cu[2] = -10000.0
            else:
                if not self.isorthometric: cu[2] -= undul(cp)
            yield cu


    def thanIntersegZ(self, ca, cb, native=False):
        "Compute intersections of segment with DEM lines; don't sort intersections from ca to cb."
        if native: return super(ThanDEMsrtm, self).thanIntersegZ(ca, cb, native)
        ca = self.user2geodetGRS80(ca)
        cb = self.user2geodetGRS80(cb)
        cint = super(ThanDEMsrtm, self).thanIntersegZ(ca, cb, native)
        if not self.isorthometric and not native:
            for _, cc in cint:
                if cc[2] is not None: cc[2] -= undul(cc)
        cint = [(u, self.geodetGRS802User(c)) for u,c in cint]
        return cint


    def thanLineZendpointstoo(self, cp):
        "Calculate the z coordinates along the line cp."
        cp = [self.user2geodetGRS80(c1) for c1 in cp]
        ni, cn = super(ThanDEMsrtm, self).thanLineZendpointstoo(cp)
        if not self.isorthometric:
            for cc in cn: cc[2] -= undul(cc)
        cn = [self.geodetGRS802User(c) for c in cn]
        return ni, cn


    def thanLineZ(self, cp):
        "Calculate the z coordinates along the line cp."
        cp = [self.user2geodetGRS80(c1) for c1 in cp]
        ni, cn = super(ThanDEMsrtm, self).thanLineZ(cp)
        if not self.isorthometric:
            for cc in cn: cc[2] -= undul(cc)
        cn = [self.geodetGRS802User(c) for c in cn]
        return ni, cn


def undul(cp):
    "Compute the undulation at GRS80 geodetic coordinates in radians cp[0], cp[1])"
    from p_gearth import egm08Ndyn
    alam = cp[0]
    phi  = cp[1]
    alam = alam % 360.0   #If negative its is transformed to positive because 360.0 is positive
    phi  = phi  % 360.0
    N = egm08Ndyn(alam, phi)
    #print "ThanDEMsrtm.undul(): N=", N
    if N == 999999.0 or N is None:
        print("ThanDEMsrtm.undul(): EGM08 did not compute undulation at λ=%f φ=%f. Undulation set to zero." % (alam, phi))
        N = 0.0
    return N
