from math import hypot, cos, sin
from p_gmath import linint, dpt
import p_ggen, p_gvarcom
from . import dtmvar, hulls

class ThanDEMdict(dtmvar.ThanDTMDEM):
    "A DEM based on python dict."

    def __init__(self):
        "Some initial values to make the object variables clear."
        self.X0, self.Y0 = 0.0, 0.0      #Object coordinates of the upper left pixel of the tif
        self.DX, self.DY = 1.0, 1.0      #Distance x and y between adjacent pixel in object coordinates
        self.nxcols, self.nyrows = 0, 0  #Image size in pixels
        self.GDAL_NODATA = None          #Special pixel value that means that the pixel has unknown elevation
        self.filnam = ""                 #Pathname of the tif file.
        self.im = None                   #Tif file which stores the DTM
        self.xymma = p_gvarcom.Xymm()    #The coordinates of the lower left and the upper right nodes of the DEM in object coordinates
        self.thanCena = (0.0, 0.0, 0.0)  #Centroid of the DEM in object coordinates


    def fromDTMlines(self, dtm, dx=5.0, dy=5.0, theta=0.0, hull=None, prt=p_ggen.prg):
        "Build a DEM using a DTM made of lines."
#        self.DX = self.DY = 5.0       #Make the routine faster: for debugging
        self.DX = dx
        self.DY = dy
        self.theta = dpt(theta)
        if hull is None:
            hull = []
            for cline1 in dtm.thanLines: hull.extend(cline1)
        self.hull = hulls.hull(hull)
        self.t = t = cos(self.theta), sin(self.theta)
        self.n = n = -t[1], t[0]
        px = [t[0]*c[0]+t[1]*c[1] for c in self.hull]
        py = [n[0]*c[0]+n[1]*c[1] for c in self.hull]
        self.xymma[:] = min(px), min(py), max(px), max(py)
        self.X0 = self.xymma[0]
        self.Y0 = self.xymma[3]

        self.zgrid = {}
#        self.__fromlines(dtm, t, n)
        self.__frompoints(dtm, t, n)


    def __fromlines(self, dtm, t, n):
        "Build a DEM using the line feature of the DTM made of lines."
        zgrid = self.zgrid
        for iy, pyaxis in enumerate(p_ggen.frange(self.xymma[1], self.xymma[3], self.DY)):
            c1, c2 = dtmvar.thanPolygonLine(self.hull, pyaxis, n)
#            assert c1 != None, "There should be 2 intersections!"
            if c1 is None: continue
            nc, cprof = dtm.thanLineZ((c1, c2))
            if nc == -1: continue
            i = 0
            pxa = t[0]*cprof[i][0]+t[1]*cprof[i][1]
            i = 1
            pxb = t[0]*cprof[i][0]+t[1]*cprof[i][1]
            assert pxa >= self.xymma[0]
            assert pxb <= self.xymma[2]
            assert pxa <= pxb
            for jx, pxaxis in enumerate(p_ggen.frange(self.xymma[0], self.xymma[2], self.DX)):
                if pxaxis < pxa: continue
                while pxaxis > pxb:
                    i += 1
                    if i >= len(cprof): break
                    pxa = pxb
                    pxb = t[0]*cprof[i][0]+t[1]*cprof[i][1]
                if i >= len(cprof): break
                zgrid[jx, iy] = linint(pxa, cprof[i-1][2], pxb, cprof[i][2], pxaxis)


    def __frompoints(self, dtm, t, n):
        "Build a DEM using the point feature of the DTM made of lines."
        zgrid = self.zgrid
        for iy, pyaxis in enumerate(p_ggen.frange(self.xymma[1], self.xymma[3], self.DY)):
            print(iy, pyaxis, "/", self.xymma[3])
            c1, c2 = dtmvar.thanPolygonLine(self.hull, pyaxis, n)
            if c1 is None: continue
            pxa = t[0]*c1[0]+t[1]*c1[1]
            pxb = t[0]*c2[0]+t[1]*c2[1]
            assert pxa >= self.xymma[0]
            assert pxb <= self.xymma[2]
            assert pxa <= pxb
            for jx, pxaxis in enumerate(p_ggen.frange(self.xymma[0], self.xymma[2], self.DX)):
                if pxaxis < pxa: continue
                if pxaxis > pxb: break
                cn = pxaxis*t[0]+pyaxis*n[0], pxaxis*t[1]+pyaxis*n[1], None
                z = dtm.thanPointZ(cn)
                if z is None: continue
                zgrid[jx, iy] = z


    def thanPointZ(self, cp, native=False):
        "Calculate the z coordinate of a point with closest match."
        t = self.t
        n = self.n
        px = t[0]*cp[0]+t[1]*cp[1]
        py = n[0]*cp[0]+n[1]*cp[1]
        jx = round((px-self.xymma[0])/self.DX)
        iy = round((py-self.xymma[1])/self.DY)
        return self.zgrid.get((jx, iy))         #May return None


    def dxfout(self, dxf):
        "Plot the DEM in dxf file."
        for (jx, iy), h in self.zgrid.items():
            x = jx*self.DX + self.xymma[0]
            y = iy*self.DY + self.xymma[1]
            dxf.thanDxfPlotPoint3(x, y, h)


    def thanLineZendpointstoo(self, cp):
        "Calculate the z coordinates along the line cp."
        cn = []
        for c in iterdis2(cp, self.DX):
            c[2] = self.thanPointZ(c)     # May be None
            cn.append(c)
        ni = dtmvar.interpolatez(cn)
        return ni, cn
    thanLineZ = thanLineZendpointstoo


def iterdis2(a, dd):
    "Iterate through polyline a, returning a point every d units distance."
#    for ca in a: yield list(ca)
#    return
    for ca, cb in p_ggen.iterby2(a):
        d = hypot(cb[1]-ca[1], cb[0]-ca[0])
        for d1 in p_ggen.frange(0.0, d, dd):
#            print "iterdis2: %15.3f%15.3f" % (d1, d)
            c = list(ca)
            c[0] = ca[0] + (cb[0]-ca[0])/d*d1
            c[1] = ca[1] + (cb[1]-ca[1])/d*d1
            yield c
    yield list(cb)
