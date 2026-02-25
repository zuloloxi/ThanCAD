"Base class for projection transformations and utilities."
from math import sqrt, hypot
from p_ggen import iterby2


class _Projection:
    "Abstract class for projection objects."
    icodp = None
    name = None

    def copy(self):
        "Return an independent copy of self."
        return self.__class__(self.L)


    def relative(self, fots):
        "Find mean and subtract constant term; normalize pixel coordinates to the length of world coordinates."
        assert len(fots) > 1, "Only 1 point??!!"
        Xsum = Ysum = Zsum = xrsum = yrsum = 0.0
        Xmin = fots[0][0]
        Ymin = fots[0][1]
        Zmin = fots[0][2]
        xrmin = fots[0][3]
        yrmin = fots[0][4]
        for X,Y,Z,xr,yr,_,_,_ in fots:
            Xsum += X
            Ysum += Y
            xrsum += xr
            yrsum += yr
            if X < Xmin: Xmin = X
            if Y < Ymin: Ymin = Y
            if Z < Zmin: Zmin = Z
            if xr < xrmin: xrmin = xr
            if yr < yrmin: yrmin = yr
        n = len(fots)
        Xsum /= n
        Ysum /= n
        Zsum /= n
        xrsum /= n
        yrsum /= n

        am = 1.0
        D = hypot(Xsum-Xmin, Ysum-Ymin)
        dr = hypot(xrsum-xrmin, yrsum-yrmin)
        if dr > 0.0 and D > 0.0: am = D/dr
        fotsr = [(X-Xmin, Y-Ymin, Z-Zmin, (x-xrmin)*am,(y-yrmin)*am,zr,xyok,zok) for (X,Y,Z,x,y,zr,xyok,zok) in fots]
        return fotsr, [Xmin, Ymin, Zmin], [xrmin, yrmin, am]


    def er_nodes(self, fots):
        "Compute the 2d error of the projection."
        er = 0.0
        n = 0.0
        for xg,yg,zg,xr,yr,zr,xyok,zok in fots:
            xyok **= 2
            xx, yy, zz = self.project((xg, yg, zg))
            er += xyok*((xx-xr)**2 + (yy-yr)**2)
            n += xyok
        er = sqrt(er/n)
        gdiscom = sum([sqrt((ga[0]-ra[0])**2+(ga[1]-ra[1])**2+(ga[2]-ra[2])**2) for (ga, ra) in iterby2(fots)])
        dis = [hypot(ga[3]-ra[3],  ga[4]-ra[4]) for (ga, ra) in iterby2(fots)]
        discom = sum(dis)
        return er, er*gdiscom/discom, discom


    def wrer_nodes(self, fots, fw):
        "Compute write the error of each individual node; fots is a dict with key the node name."
        gr = fots.values()
        gdiscom = sum([sqrt((ga[0]-ra[0])**2+(ga[1]-ra[1])**2+(ga[2]-ra[2])**2) for (ga, ra) in iterby2(gr)])
        dis = [hypot(ga[3]-ra[3],  ga[4]-ra[4]) for (ga, ra) in iterby2(gr)]
        discom = sum(dis)
        ser = sx = sy = 0.0
        sn = 0.0
        fw.write("Error of individual nodes\n")
        pline = "%s\n" %("-"*50)
        fw.write(pline)
        fw.write("%-10s%10s%10s%10s%10s\n" % ("Node name", "dx", "dy", "error", "Error"))
        fw.write("%-10s%10s%10s%10s%10s\n" % ("", "(local)", "(local)", "(local)", "(World)"))
        fw.write(pline)
        ags = sorted(fots.iterkeys())
        for ag in ags:
            xg,yg,zg,xr,yr,zr,xyok,zok = fots[ag]
            xyok **= 2
            xx, yy, zz = self.project((xg, yg, zg))
            dx = xr - xx
            dy = yr - yy
            er = hypot(dx, dy)
            er3d = er*gdiscom/discom
            fw.write("%-10s%10.1f%10.1f%10.1f%10.3f\n" % (ag, dx, dy, er, er3d))
            sx  += xyok*dx**2
            sy  += xyok*dy**2
            ser += xyok*er**2
            sn += xyok
        sx = sqrt(sx/sn)
        sy = sqrt(sy/sn)
        er = sqrt(ser/sn)
        er3d = er*gdiscom/discom
        fw.write(pline)
        fw.write("%-10s%10.1f%10.1f%10.1f%10.3f\n" % ("Overall", sx, sy, er, er3d))
        fw.write("%-10s\n" % ("error",))
        return er, er3d, discom


    def er(self, fots):
        """Compute the 2d error of the projection.

        We use trapezoidal integration to take into account the distance between the nodes.
        gdiscom is the length of the 3d-line common to both curves.
        discom is the length of the 2d-line common to both curves.
        The first value that is returned is the error in projected (2d) coordinates.
        The second value that is returned is the error in 3d coordinates.
        """
        gdiscom = sum([sqrt((ga[0]-ra[0])**2+(ga[1]-ra[1])**2+(ga[2]-ra[2])**2) for (ga, ra) in iterby2(fots)])
        dis = [hypot(ga[3]-ra[3],  ga[4]-ra[4]) for (ga, ra) in iterby2(fots)]
        discom = sum(dis)
#        if discom/gps1.length() < 0.66: continue    # Curves are not near enough (or bad prealignment)
        r = []
        for xg,yg,zg,xr,yr,zr,xyok,zok in fots:
            xyok **= 2
            xx, yy, zz = self.project((xg, yg, zg))
            r.append(xyok*((xx-xr)**2 + (yy-yr)**2))
        er = 0.0
        for i in range(len(fots)-1):
            er += (r[i]+r[i+1])*0.5*dis[i]
        er = sqrt(er/discom)
        return er, er*gdiscom/discom, discom


    def readIcod(self, fr):
        "Reads and checks the code, if it matches the object, or it it matches polynomial1 projection."
        dl1 = read1(fr)
        ic = int(dl1)
        if ic == self.icodp: return ic
        if ic <  10 and ic == 0:  return ic           #Projection from 3d to 2d
        if ic >= 30 and ic == 0:  return ic           #Projection from 3d to 2d
        if ic >= 10 and ic == 10: return ic           #Transformation from 2d to 2d
        raise ValueError("Projection code in file is wrong")   # Accept polynomial as a first approximation


    def readCoefs(self, fr, n):
        "Reads n real coefficients."
        L = []
        for i in range(n):
            dl1 = read1(fr)
            dl1 = dl1.replace("d", "e").replace("D", "e") # Allow for Fortran generated file
            L.append(float(dl1))
        return L


def read1(fr):
    "Reads a non-blank non-comment line; it is the responsibility of the caller to handle exceptions."
    while True:
        dl = next(fr).strip()
        if len(dl) > 0 and dl[0] != "#": break    # Comment lines
    dl1 = dl.split()[0]                           # Avoid comments at the end of the line
    return dl1

def read1raw(fr):
    "Reads a non-blank non-comment line; it is the responsibility of the caller to handle exceptions."
    while True:
        dl = next(fr).strip()
        if len(dl) > 0 and dl[0] != "#": break    # Comment lines
    return dl


if __name__ == "__main__":
    print(__doc__)
