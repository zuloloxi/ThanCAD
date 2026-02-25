from p_ggen import iterby2, doNothing
from p_ggeom import TriLocal, MesaTri


class TriLocate(object):
    "A triangulation object with pixel coordinates."

    def __init__(self, fr, dmax=150.0, worldindex=True, pixelindex=True, prt=doNothing):
        "Reads the DTM from a ThanCad triangulation (.tri) file."
        infin = 0
        xyz = []
        en = []
        for dline in fr:
            a1 = dline[:10].rstrip()
            x1 = float(dline[10:25])
            y1 = float(dline[25:40])
            z1 = float(dline[40:55])
            try:
                x1p = float(dline[55:65])
                y1p = float(dline[65:75])
            except ValueError as e:
                if pixelindex: raise
                x1p = y1p = -99999.9     #Fake pixel coordinates, when there are no pixel coordinates and pixelindex==False
            xyz.append((x1, y1, z1, x1p, y1p))
            if a1 == '####ΚΔ####': infin = 4   # Υπάρχουν άπειρα σημεία
            en1 = []
            for dline in fr:
                dl = dline.strip()
                if dl == "$": break
                en1.append(int(dl)-1)
            en.append(en1)
        dmax **= 2
        seen = set()
        tri = []
        for i in range(len(xyz)-infin):
            for j, k in iterby2(en[i]):
                s = frozenset((i,j,k))
                if s in seen: continue
                seen.add(s)
                d12 = (xyz[j][0]-xyz[i][0])**2 + (xyz[j][1] - xyz[i][1])**2
                if d12 > dmax: continue
                d12 = (xyz[k][0]-xyz[i][0])**2 + (xyz[k][1] - xyz[i][1])**2
                if d12 > dmax: continue
                tri.append((xyz[i], xyz[j], xyz[k]))
        del seen, en

        self.grind = self.grindp = None
        if worldindex:
            prt("Creating world coordinates' index..", "info1")
            self.grind  = GridIndex(xyz, tri, ispixel=False)
        if pixelindex:
            prt("Creating pixel coordinates' index..", "info1")
            self.grindp = GridIndex(xyz, tri, ispixel=True)
        if infin: del xyz[-8:-4]
        self.xyz = xyz


class GridIndex(object):
    "An index to the grid."

    def __init__(self, xyz, tri, ispixel=False):
        "Creates an index grid for faster triangle location."
        if ispixel: ix, iy = 3, 4
        else:       ix, iy = 0, 1
        c = [xyz1[ix] for xyz1 in xyz]
        xmin = min(c)
        xmax = max(c)
        c = [xyz1[iy] for xyz1 in xyz]
        ymin = min(c)
        ymax = max(c)
        dx = xmax - xmin
        dy = ymax - ymin
        nx = int(dx/100.0)+1
        ny = int(dy/100.0)+1
        dx /= nx
        dy /= ny
        grind = {}
        for tri1 in tri:
            jss = [int((c[ix]-xmin)/dx) for c in tri1[:3]]
            iss = [int((c[iy]-ymin)/dy) for c in tri1[:3]]
            for i in range(min(iss), max(iss)+1):
                for j in range(min(jss), max(jss)+1): grind.setdefault((i,j), []).append(tri1)
        self.ispixel = ispixel
        self.tri = tri
        self.dx = dx
        self.dy = dy
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.grind = grind


    def triFind(self, x, y):
        "Find the triangle which point x,y belongs to."
        if self.ispixel: ix, iy = 3, 4
        else:            ix, iy = 0, 1
        j = int((x-self.xmin)/self.dx)
        i = int((y-self.ymin)/self.dy)
        for tri1 in self.grind.get((i,j), []):
            mes  = MesaTri((tri1[0][ix], tri1[0][iy]), (tri1[1][ix], tri1[1][iy]), (tri1[2][ix], tri1[2][iy]))
            if mes.mesa((x, y)): return tri1
        return None


    def triFindBrute(self, x, y):
        "Finds which triangle point x, y belongs to (brute force approach)."
        if self.ispixel: ix, iy = 3, 4
        else:            ix, iy = 0, 1
        for tri1 in self.tri:
            mes  = MesaTri((tri1[0][ix], tri1[0][iy]), (tri1[1][ix], tri1[1][iy]), (tri1[2][ix], tri1[2][iy]))
            if mes.mesa((x, y)): return tri1
        return None


    def z(self, x, y, tri1=None):
        "Finds the z of point x, y."
        if tri1 is None:
            tri1 = self.triFind(x, y)
            if tri1 is None: return tri1
        if self.ispixel: ix, iy = 3, 4
        else:            ix, iy = 0, 1
        tra  = TriLocal(tri1[0][ix], tri1[0][iy], tri1[1][ix], tri1[1][iy], tri1[2][ix], tri1[2][iy])
        l1, l2, l3 = tra.glob2loc(x, y)
        return tra.interp(tri1[0][2], tri1[1][2], tri1[2][2], l1, l2, l3)


    def pixel(self, x, y, tri1=None):
        "Finds the pixel coordinates of point x, y."
        if tri1 is None:
            tri1 = self.triFind(x, y)
            if tri1 is None: return None, None
        if self.ispixel: ix, iy = 3, 4
        else:            ix, iy = 0, 1
        tra  = TriLocal(tri1[0][ix], tri1[0][iy], tri1[1][ix], tri1[1][iy], tri1[2][ix], tri1[2][iy])
        l1, l2, l3 = tra.glob2loc(x, y)
        return (tra.interp(tri1[0][3], tri1[1][3], tri1[2][3], l1, l2, l3),
                tra.interp(tri1[0][4], tri1[1][4], tri1[2][4], l1, l2, l3),
               )


    def world(self, x, y, tri1=None):
        "Finds the world coordinates of point x, y."
        if tri1 is None:
            tri1 = self.triFind(x, y)
            if tri1 is None: return None, None
        if self.ispixel: ix, iy = 3, 4
        else:            ix, iy = 0, 1
        tra  = TriLocal(tri1[0][ix], tri1[0][iy], tri1[1][ix], tri1[1][iy], tri1[2][ix], tri1[2][iy])
        l1, l2, l3 = tra.glob2loc(x, y)
        return (tra.interp(tri1[0][0], tri1[1][0], tri1[2][0], l1, l2, l3),
                tra.interp(tri1[0][1], tri1[1][1], tri1[2][1], l1, l2, l3),
               )
