from math import hypot
import p_gvarcom, p_ggen
from .dtmvar import ThanDTMDEM


class ThanDTMinv2(ThanDTMDEM):
    """DTM which interpolates irregular points with inverse distance squared."

#self.DX, self.DY: ορίζει το βήμα του DEM κατά X και Y, που είναι και το
#μέγεθος του κάθε τετραγωνιδίου.

#Η παρεμβολή που γίνεται είναι σταθμισμένος μέσος όρος γειτονικών σημείων με
#βάρη το αντίστροφο της απόστασης στο τετράγωνο.
#self.r: ορίζει την ακτίνα R τετραγωνιδίων (ακέραιος αριθμός), στα
#οποία το πρόγραμμα θα ψαξει για γειτονικά σημεία. Αν R=0, τότε ψάχνει μόνο στο
#τετραγωνίδιο που βρίσκεται το σημείο που παρεμβάλλεται (κανένα γειτονικό
#τετραγωνίδιο).


#self.nmin: ορίζει το πλήθος NMIN των σημείων που πρέπει να βρεθούν
#στο τετραγωνίδιο (και στα γειτονικά του αν self.r>0), για να μπορεί να υπολογιστεί
#ο σταθμισμένος μέσος όρος. Αν βρεθούν λιγότερα, τότε δεν υπολογίζεται
#υψόμετρο σε αυτό το σημείο.


#tol: ορίζει την ανοχή tol. Αν η απόσταση ενός σημείου είναι
#μικρότερη από tol, τότε δεν υπολογίζεται σταθμισμένο μ.ο. αλλά λαμβάνεται
#το υψόμετρο αυτού του σημείου."""

    def __init__(self, DX=5.0, DY=5.0, r=0, nmin=1, tol=0.01):
        "Make an empty dtm."
        self.g = {}
        self.DX = DX
        self.DY = DY
        self.r = r
        self.nmin = nmin
        self.tol = tol      #If distance to a point is < tol, then the points coincide
        self.xymma = p_gvarcom.Xymm()


    def thanReadSyn(self, fr):
        "Read points from a syn file."
        g = self.g
        DX, DY = self.DX, self.DY
        for aa, x, y, h, cod in p_gvarcom.reSyn2(fr):
            if cod != "": continue                # not a height point
            ix = int(round(x/DX))
            iy = int(round(y/DY))
            g.setdefault((ix,iy), []).append((x,y,h))


    def thanAdd(self, cps):
        "Add points to the DTM."
        g = self.g
        DX, DY = self.DX, self.DY
        for x, y, h in cps:
            ix = int(round(x/DX))
            iy = int(round(y/DY))
            g.setdefault((ix,iy), []).append((x,y,h))


    def thanRecreate(self):
        "Recreate DEM after point additions."
        if len(self.g) < 1: return False, "DTM is empty!"
        xymma = p_gvarcom.Xymm()
        for cs in self.g.values():
            for c in cs:
                xymma.includePoint(c)
        self.xymma = xymma
        self.thanCentroidCompute()
        return True, None


    def thanPointZ(self, cc):
        "Calculate the z coordinate of a point."
        ixx = int(round(cc[0]/self.DX))
        iyy = int(round(cc[1]/self.DY))
        sw = sh = 0.0
        n = 0
        nearest = False
        for ix in range(ixx-self.r, ixx+self.r+1):
            for iy in range(iyy-self.r, iyy+self.r+1):
                for c in self.g.get((ix,iy), ()):
                    d = hypot(c[0]-cc[0], c[1]-cc[1])
                    if nearest:
                        if d < dmin:
                            dmin = d
                            zmin = c[2]
                    else:
                        if d < self.tol:
                            nearest = True       #Exact point
                            dmin = d
                            zmin = c[2]
                        else:
                            w = 1.0/d**2
                            sw += w
                            sh += w*c[2]
                            n += 1
        if nearest: return zmin
        if n < self.nmin: return None   #No points found in the vicinity of cc
        return sh/sw


    def thanXymm(self, native=False):
        "Return the min and max x and y coordinates."
        return self.xymma


    def thanIntersegZ(self, ca, cb, native=False):
        "Compute intersections of segment with DEM lines; don't sort intersections from ca to cb."
        ca = tuple(ca)
        cb = tuple(cb)
        ab = cb[0]-ca[0], cb[1]-ca[1]
        dab = hypot(ab[0], ab[1])

        cint = []
        dd = min(self.DX, self.DY)
        d = dd
        while d < dab:
            u = d / dab
            x = ca[0] + ab[0]*u
            y = ca[1] + ab[1]*u
            h = self.thanPointZ((x, y))
            if h is None: continue
            cint.append((u, [x, y, h]))
            d += dd
        return cint


    def thanReadParams(self, fr):
        """Read steps, xmin, etc from an opened Datlin.

        This function will read all the data and will change the object
        only if all data was read successfully."""

        #fr = p_gfil.Datlin(frw["gde"])
        gde = p_ggen.Struct("DEM metadata")

        fr.datCom("GRIDSTEP X Y")
        gde.dx = fr.datFloatR(1.0e-7, 1.0e7)
        gde.dy = fr.datFloatR(1.0e-7, 1.0e7)

        fr.datCom("RADIUS")
        gde.r = fr.datIntR(0, 999)

        fr.datCom("MIN POINTS")
        gde.nmin = fr.datIntR(1, 999999999)

        fr.datCom("TOLERANCE")
        gde.tol = fr.datFloatR(1.0e-6, 1.0e6)

        self.__init__(gde.dx, gde.dy, gde.r, gde.nmin, gde.tol)
