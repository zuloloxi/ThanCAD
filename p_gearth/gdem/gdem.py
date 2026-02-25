# -*- coding: iso-8859-7 -*-
from PIL import Image
from math import pi
from p_gmath import dpt
import p_gtri, p_ggeod, p_ggen, p_gfil, p_gcom
from ..nge_egm08.egm08interp_1min import egm08Ndyn

path_earth = ('../binwi/libs/p_gearth/      ',
              '../binwm/libs/p_gearth/      ',
              '/home2/x/binwi/libs/p_gearth/',
              '/home2/x/binwm/libs/p_gearth/',
              'x:/binwi/libs/p_gearth/      ',
              'x:/binwm/libs/p_gearth/      ',
              'c:/p_gearth/                 ',
             )


class GDEM(p_gtri.ThanDTMDEM):
    "Computes elevation on the whole surface of a planet."
    subdir = ""
    name = "Global Digital Elevation Model"
    filnam = ""                 #This is for ThanCad
    im = "GDEM"                 #This is for ThanCad

    def __init__(self, isorthometric=True, nodatadef=None):
        "Make initial arrangements."
        self.isorthometric = isorthometric
        self.nodatadef = nodatadef
        self.cgiarDem = {}               #SRTM files read so far
        self.demcur = None               #At first we feel lucky and try current (previous) dem for the point
        self.projcur = p_ggeod.egsa87    #Default user geodetic projection
        #self.projcur = p_ggeod.UTMercator(EOID=p_ggeod.NAD83_1997, zone=10, north=True)
        subdir = self.subdir.strip().strip("/\\") + "/"
        self.path_gd = ['                                       ']
        for pref in path_earth:
            self.path_gd.append(pref.rstrip()+subdir)


    def user2geodetGRS80(self, cp):
        "Transform user coordinates to GRS80 geodetic using current user geodetic projection."
        cn = list(cp)
        alam, phi = self.projcur.en2geodetGRS80(cp[0], cp[1])
        alam = dpt(alam) * 180.0/pi        #Projection function parameters/return values are always in rad
        phi = dpt(phi) * 180.0/pi          #Projection function parameters/return  is always in rad
        if alam >= 180.0: alam -= 360.0    #SRTM needs 180<=λ<180
        if phi  >= 180.0: phi  -= 360.0    #SRTM needs 180<=λ<180
        cn[0] = alam
        cn[1] = phi
        return cn


    def geodetGRS802User(self, cp):
        "Transform GRS80 geodetic to user coordinates using current user geodetic projection."
        cn = list(cp)
        cn[:2] = self.projcur.geodetGRS802en(cp[0]*pi/180.0, cp[1]*pi/180.0)  #Projection function parameters/return values are always in rad
        return cn


    def thanSetProjection(self, projection):
        """Set new user geodetic projection.

        The projection object must have the en2geodetGRS80(), geodetGRS802en() methods
        which transform user coordinates to GRS80 geodetic and vice versa."""
        assert projection != None, "Please use p_ggeod.GeodetGRS80() projection instead of None"
        self.projcur = projection


    def thanPointZ(self, cp):
        "Get the elevation of point with WGS84 ellipsoid geodetic coordinates (decimal degrees)."
        if self.demcur != None:
            z = self.demcur.thanPointZ(cp)
            if z != None: return z
        cg = self.user2geodetGRS80(cp)
        fn = self.frameName(cg[0], cg[1])
        if fn == None: return None
        dem = self.cgiarDem.get(fn)
        if dem == None:
            dem, terr = self.openFrameFile(fn)
            if dem == None: return None
            self.cgiarDem[fn] = dem
        self.demcur = dem
        return dem.thanPointZ(cp)


    def thanIntersegZ(self, ca, cb, native=False):
        "Compute intersections of segment with DEM lines; don't sort intersections from ca to cb."
        xymm = min(ca[0], cb[0]), min(ca[1], cb[1]), max(ca[0], cb[0]), max(ca[1], cb[1])
        dems, loaded, notfound, notcovered = self.thanGetWin(xymm)
        cint = []
        for dtm in self.cgiarDem.itervalues():
            cints1 = dtm.thanIntersegZ(ca, cb, native)
            cint.extend(cints1)
        return cint


    def thanXymm(self, native=False):
        "Return the min and max x and y coordinates."
        xymm = p_gcom.Xymm()
        for dem in self.cgiarDem.itervalues():              #SRTM files read so far
            xymm.includeXymm(dem.thanXymm(), native)
        if len(xymm) < 4: return None                       #No SRTM files read (or found)
        return xymm


    def thanDxy(self):
        """Return the DX, DY of the dem.

        Because the coordinate transformation usually leads to variable DX, DY
        the average DX, DY are returned. The average DX, DY of a random frame.
        """
        for dem in self.cgiarDem.itervalues():              #SRTM files read so far
            return dem.thanDxy()
        return None, None                                   #No SRTM files read (or found)


    def openFrameFile(self, fn):
        "Opens the file which contains the grid."
        fn = fn.strip()
        for par in self.path_gd:
            fnu1 = par.strip() + fn
            try:            uGri = open(fnu1, "rb")
            except IOError: pass
            else:           break
        else:
            terr = 'File '+fn+' can not be found or accessed'
            print "tra3", terr
            return None, terr
        uGri.close()
        dem = p_gtri.ThanDEMsrtm(self.isorthometric, self.nodatadef)
        ok, terr = dem.thanSet(fnu1, None, self.user2geodetGRS80, self.geodetGRS802User)
        if not ok: return None, terr
        return dem, ""


    def frameName(self, alam, phi):
        "Find the name of the appropriate gdem frame which contains the given geodetic coordinates."
        nl, np = self.frameNumber(alam, phi)
        if nl == None: return None
        fn = self.frameNameN(nl, np)
        return fn


    def frameNameN(self, nl, np):
        "Find the name of the appropriate gdem frame given its number(s)."
        raise IndexError, "frameNameN must be overridden"
    def frameNumber(self, alam, phi, check=True):
        "Find the numbers of the gdem frame that contains the point at ala, phi."
        raise IndexError, "frameNumber must be overridden"
    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of gdem frame: nl, np."
        raise IndexError, "frameXymm must be overridden"


    def thanGetWin(self, xymm):
        "Load all the dems with crossing window xymm; xymm is according to ThanCad conventions."
        alama, phia, _ = self.user2geodetGRS80((xymm[0], xymm[3], 0.0))    #Up, left point of the window
        alamb, phib, _ = self.user2geodetGRS80((xymm[2], xymm[1], 0.0))    #Down, right point of the window
        #if phia > 180.0: phia -= 360.0
        #if phib > 180.0: phib -= 360.0
        print "alama, phia=", alama, phia
        print "alamb, phib=", alamb, phib
        nla, npa = self.frameNumber(alama, phia, check=False)
        nlb, npb = self.frameNumber(alamb, phib, check=False)
        print xymm
        print "thangetwin(): nla, nlb=", nla, nlb
        print "thangetwin(): npa, npb=", npa, npb
        print "frames:", self.frameNameN(nla, npa), ":", self.frameNameN(nlb, npb)
        dems = []        #The dems inside the window
        loaded = []      #DEMs which were loaded now
        notfound = []    #DEMs which were not found in current computer (you can download them from internet)
        notcovered = []  #DEMs which the gdem does not cover at all
        for nl in xrange(nla, nlb+1):
            for np in xrange(npa, npb-1, -1):
                covered = self.frameXymm(nl, np)
                if covered == None:
                    notcovered.append((nl, np))
                    continue
                fn = self.frameNameN(nl, np)
                if fn in self.cgiarDem:
                    dems.append(self.cgiarDem[fn])
                    continue
                dem, terr = self.openFrameFile(fn)
                if dem != None:
                    self.cgiarDem[fn] = dem
                    dems.append(dem)
                    loaded.append((nl, np))
                    continue
                notfound.append((nl, np))
        return dems, loaded, notfound, notcovered


    def thanGetWinC(self, xymm, prg=p_ggen.prg):
        "Load all the frames of the gdem and check if all were read."
        prg("Reading %s frames.." % (self.name,), "info1")
        dems, loaded, notfound, notcovered = self.thanGetWin(xymm) #All dems returned, are references to objects stored in gdem
        if len(notcovered) > 0: prg("Part of (or all) the area is outside the %s gdem" % (self.name,), "can1")
        if len(notfound) > 0:
            prg("The following frames of the %s gdem are not present in the current computer" % (self.name,), "can")
            prg("(they can be downloaded from the internet):", "can1")
            for nl, np in notfound: prg(self.frameNameN(nl, np), "can1")
        if len(dems) < 1: p_gfil.er1s("No frames of the %s gdem were found in this area" % (self.name,))
        return dems


    def joinDem(self, xymm):
        "Return a single DEM that contains the region xymm."
        dems, loaded, notfound, notcovered = self.thanGetWin(xymm)
        if len(dems) == 0: return None
        alama, phia, _ = self.user2geodetGRS80((xymm[0], xymm[3], 0.0))    #Up, left point of the window
        alamb, phib, _ = self.user2geodetGRS80((xymm[2], xymm[1], 0.0))    #Down, right point of the window
        dem1 = dems[0]
        jxa, iya = dem1.thanPixelCoor((alama, phia, 0.0), native=True)    #Up, left point of the window
        jxb, iyb = dem1.thanPixelCoor((alamb, phib, 0.0), native=True)    #Down, right point of the window
        im = Image.new(dem1.im.mode, (jxb-jxa, iyb-iya))
        for dem in dems:
            xymm1 = dem.thanXymm(native=True)
            jxa1, iya1 = dem1.thanPixelCoor((xymm1[0], xymm1[3], 0.0), native=True)  #Up, left point of the dem
            jxb1, iyb1 = dem1.thanPixelCoor((xymm1[2], xymm1[1], 0.0), native=True)  #Up, left point of the dem
            jxa2, iya2 = 0, 0
            jxb2, iyb2 = dem.im.size
            assert jxa1 < jxb
            assert iya1 < iyb
            assert jxb1 >= jxa
            assert iyb1 >= iya
            if jxa1 < jxa: jxa2 += jxa-jxa1; jxa1 = jxa
            if iya1 < iya: iya2 += iya-iya1; iya1 = iya
            if jxb1 > jxb: jxb2 += jxb-jxb1; jxb1 = jxb
            if iyb1 > iyb: iyb2 += iyb-iyb1; iyb1 = iyb
            im1 = dem.im.crop((jxa2, iya2, jxb2, iyb2))
            im.paste(im1, (jxa1-jxa, iya1-iya))
        return im, dem1.GDAL_NODATA


    def iterNodes(self, validnodes=True, invalidnodes=False, xymm=None):
        "Iterate through valid and or invalid nodes of the DEM; xymm is according to ThanCad conventions."
        for dem in self.cgiarDem.itervalues():  #SRTM files read so far
            if xymm == None:
                for cc in dem.iterNodes(validnodes=validnodes, invalidnodes=invalidnodes, xymm=xymm):
                    yield cc
            elif xymm.intersectsXymm(dem.thanXymm()):
                for cc in dem.iterNodes(validnodes=validnodes, invalidnodes=invalidnodes, xymm=xymm):
                    yield cc


    def test1(self):
        "Test the code of finding frame given geodetic coordinates."
        while True:
            alam = float(raw_input("λ: "))
            phi = float(raw_input("φ: "))
            print self.frameName(alam, phi)


    def test2(self):
        "Test the range of a frame given geodetic coordinates."
        while True:
            nl = int(raw_input("nl: "))
            np = int(raw_input("np: "))
            print self.frameXymm(nl, np)


    def testAthens(self):
        "Test the elevations of GDEM in Athens."
        import p_gearth
        cps = [(23.7,       38.001,       42.0, "Κηφισσός λίγο πιο πάνω από Καβάλας"),
               (23.685,     37.931,      2.0, "Πειραιάς - ΖΕΑ"),
               (23.767886,  37.978815, 148.0, "Σπίτι"),
               (23.7787972, 37.976822, 186.0, "Πολ.Μηχ.ΕΜΠ"),
              ]
        self.thanSetProjection(p_ggeod.GeodetGRS80())    #Data is in GRS80 geodetic coordinates
        print
        print self.name
        print "-------------------------------------------------------"
        for cp in cps:
            print "λ=%10.5f  φ=%10.5f   %s" % (cp[0], cp[1], cp[-1])
            cp = list(cp)
            cp[0] *= pi/180.0
            cp[1] *= pi/180.0
            h = self.thanPointZ(cp)
            N = p_gearth.egm08Ndyn(cp[0], cp[1])
            if h == None: h = -8888.8
            print "Google: %8.1f  %s: %8.1f     N:%.1f" % (cp[2], self.name, h, N)
        print
        print "Test EGSA87 coordinates near Athens"
        self.thanSetProjection(p_ggeod.egsa87)
        cp = [480000.0, 4200000.0, -9999.0]
        h = self.thanPointZ(cp)
        N = p_gearth.egm08Ndyn(cp[0], cp[1])
        if h == None: h = -8888.8
        print cp
        print "Google: %8.1f  %s: %8.1f     N:%.1f" % (cp[2], self.name, h, N)


    def destroy(self):
        "Break circular references."
        del self.cgiarDem, self.demcur, self.projcur

    def __del__(self):
        print "Object", self, "dies"


class SRTMGDEM(GDEM):
    "Computes elevation on the whole surface of earth using SRTM."
    subdir = "srtmcgiar"
    name = "SRTM cgiar"
    filnam = "%%%SRTM%%%"                 #This is for ThanCad

    def frameNameN(self, nl, np):
        "Find the name of the appropriate SRTM frame given its number(s)."
        return "srtm_%02d_%02d.tif" % (nl, np)

    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the SRTM frame that contains the point at ala, phi.

        alam should be -180<alam<180 and phi  -60 < phi <=60."""
#        print "srtm framenumber1: λ, φ=", alam, phi
        if alam >= 180.0: alam -= 360.0
#        print "srtm framenumber2: λ, φ=", alam, phi
        if check and alam >= 180.0: return None, None
        if check and alam < -180.0: return None, None
        if check and phi > 60.0: return None, None
        if check and phi <= -60.0: return None, None
        nl = int((alam-(-180.0))/5.0+1.0)
        np = int((60.0-phi)/5.0+1.0)
        return nl, np

    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of SRTM frame: nl, np."
        if check and nl <  1: return None
        if check and nl > 71: return None
        if check and np <  1: return None
        if check and np > 23: return None
        alam1 = -180.0 + (nl-1)*5.0
        phi1 = 60.0 - (np-1)*5.0
        return (alam1, phi1-5.0, alam1+5.0, phi1)

    def testformulas(self):
        "Test the CGIAR SRTM formulas."
        while True:
            phi = float(raw_input("φ: "))
            nl = (60.0-phi)/5.0+1.0
            print nl, int(nl)

        while True:
            alam = float(raw_input("λ: "))
            nl = (alam-(-180.0))/5.0+1.0
            print nl, int(nl)


class ASTERGDEM(GDEM):
    "Computes elevation on the whole surface of earth using ASTER."
    subdir = "aster"
    name = "ASTER v2"
    filnam = "%%%ASTER%%%"                #This is for ThanCad

    def frameNameN(self, nl, np):
        "Find the name of the appropriate ASTER frame given its number(s)."
#       "astgtm2_n34e024_dem.tif"
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "astgtm2_%s%02d%s%03d_dem.tif" % (sn, abs(np), we, abs(nl))


    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the ASTER frame that contains the point at ala, phi.

        alam should be -180<alam<180 and phi  -83 < phi <=83."""
#       "astgtm2_n34e024_dem.tif"
        if alam >= 180.0: alam -= 360.0
        if check and alam >= 180.0: return None, None
        if check and alam < -180.0: return None, None
        if phi > 83.0: return None, None
        if phi <= -83.0: return None, None
        nl = int(alam)
        np = int(phi)
        return nl, np


    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of ASTER frame: nl, np."
        if check and nl < -180: return None
        if check and nl >  179: return None
        if check and np <  -82: return None
        if check and np >   83: return None
        alam1 = nl
        phi1 = np
        return (alam1, phi1-1.0, alam1+1.0, phi1)


class GreekcGDEM(GDEM):
    "Computes elevation on the whole surface of Greece using c."
    subdir = "greekc"
    name = "Greekc"
    filnam = "%%%GREEKC%%%"                 #This is for ThanCad

    def __init__(self):
        "Make initial arrangements."
        super(GreekcGDEM, self).__init__()
        self.htrs07 = p_ggeod.Htrs07()      #Data is saved in HTRS07, not GRS80 λ, φ

    def user2geodetGRS80(self, cp):
        "Transform user coordinates to HTRS07 using current user geodetic projection."
        cn = list(cp)
        alam, phi = self.projcur.en2geodetGRS80(cp[0], cp[1])
        cn[:2] = self.htrs07.geodetGRS802en(alam, phi)
        return cn

    def geodetGRS802User(self, cp):
        "Transform HTRS07 to user coordinates using current user geodetic projection."
        cn = list(cp)
        alam, phi = self.htrs07.en2geodetGRS80(cp[0], cp[1])
        cn[:2] = self.projcur.geodetGRS802en(alam, phi)
        return cn


    def frameNumber_correct(self, alam, phi, check=True):
        "Find the numbers of the Greekc frame that contains the point at ala, phi."
        nl = int(alam/4000.0) * 40
        np = int((phi-1000.0) / 3000.0)
        np = np * 30 + 10
        return nl, np

    def frameNameN(self, nl, np):
        """Find the name of the appropriate Greekc frame given its number(s).

        Examples: 0480022300.tif, 0480022330.tif, 0480022360.tif, 0484022300.tif,
        0484022330.tif, 0484022360.tif,0488022300.tif,0488022330.tif,0488022360.tif.

        tra3 File 0472022050.tif can not be found or accessed

        """
        x = nl*40
        y = np*30 + 10
        y -= 30                #Convert to lower corner
        return "%05d%05d.tif" % (x, y)

    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the Greekc frame that contains the point at ala, phi.

        Instead of the lower left corner report the upper left corner.
        """
        nl = int(alam/4000.0)
        np = int((phi-1000.0) / 3000.0)
        np += 1                           #upper left corner.
        return nl, np

    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of SRTM frame: nl, np."
        x = nl*4000.0
        y = np*3000.0 + 1000.0
        return (x, y-3000.0, x+4000.0, y)


class TanIDEM(GDEM):
    "Computes elevation on the whole surface of earth using TanDEM-X Intermediate DEM."
    #TDM1_IDEM_04_N36E025_DEM.tif
    subdir = "tanidem"
    name = "TanDEM-X Intermediate DEM"
    filnam = "%%%TANIDEM%%%"                 #This is for ThanCad

    def __init__(self):
        "Make initial arrangements."
        super(TanIDEM, self).__init__(isorthometric=False, nodatadef=-32767.0)


    def frameNameN(self, nl, np):
        "Find the name of the appropriate IDEM frame given its number(s)."
        #TDM1_IDEM_04_N36E025_DEM.tif
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "tdm1_idem_04_%s%02d%s%03d_dem.tif" % (sn, abs(np), we, abs(nl))


    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the IDEM frame that contains the point at ala, phi.

        alam should be -180<alam<180 and phi  -83 < phi <=83."""
#       "astgtm2_n34e024_dem.tif"
        if alam >= 180.0: alam -= 360.0
        if check and alam >= 180.0: return None, None
        if check and alam < -180.0: return None, None
        if phi > 90.0: return None, None
        if phi < -90.0: return None, None
        nl = int(alam)
        np = int(phi)
        return nl, np


    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of ASTER frame: nl, np."
        if check and nl < -180: return None
        if check and nl >  179: return None
        if check and np <  -82: return None
        if check and np >   83: return None
        alam1 = nl
        phi1 = np
        return (alam1, phi1-1.0, alam1+1.0, phi1)


def gdem(name):
    "Return a global DEM according to filnam."
    name1 = name.strip("% ").upper()
    if name1 == "SRTM": return SRTMGDEM()
    if name1 == "ASTER": return ASTERGDEM()
    if name1 == "GREEKC": return GreekcGDEM()
    if name1 == "TANIDEM": return TanIDEM()
    raise ValueError, "Unknown GDEM: %s" % (name,)
