from PIL import Image
from math import pi
from p_gmath import dpt
import p_gtri, p_ggeod, p_ggen, p_gfil, p_gvarcom
from .pathearth import path_earth
from ..nge_egm08.egm08interp_1min import egm08Ndyn


class GDEM(p_gtri.ThanDTMDEM):
    "Computes elevation on the whole surface of a planet."
    subdir = ""
    name = "Global Digital Elevation Model"
    filnam = ""                 #This is for ThanCad
    im = "GDEM"                 #This is for ThanCad: If it is None, ThanCad assumes that the DEM was not loaded/found
    fwild = "*"                 #bash regular expression for the filenames of frames: used in thanGetAvailable()

    def __init__(self, isorthometric=True, nodatadef=None, prt=p_ggen.prg):
        "Make initial arrangements."
        self.isorthometric = isorthometric
        self.nodatadef = nodatadef
        self.prt = prt
        self.cgiarDem = {}               #SRTM files read so far
        self.cgiarNotfound = set()       #SRTM files which were searched for, and were not found
        self.demcur = None               #At first we feel lucky and try current (previous) dem for the point
        self.projcur = p_ggeod.egsa87    #Default user geodetic projection
        subdir = self.subdir.strip().strip("/\\") + "/"
        self.path_gd = ['                                       ']
        #print("self.subdir=", self.subdir)
        if self.subdir == "survey":
            self.path_gd.extend(self.addAllSubdirs("kthm2015_04_16", "DEM"))
            self.path_gd.extend(self.addAllSubdirs("kthm2015_10_14", "DEM"))
            self.path_gd.extend(self.addAllSubdirs("kthm2018_01_16", "DEM"))
            #self.path_gd.extend((\
              #'/samba2/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/DODEKANISA/DEM/',
              #'/samba2/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/KYKLADES/DEM/',
              #'/samba2/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/DODEKANISA/KASTELORIZO/DEM/',
              #'/samba2/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/CHIOS/DEM/',
              #'/samba2/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/LESVOS/DEM/',
              #'/samba2/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/SAMOS/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/ATTIKIS/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/AITOLOAKARNANIA/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/AXAIA/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/HLEIA/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/ARGOLIDA/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/ARKADIA/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/KORINTIA/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/LAKONIA/DEM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/MESSINIA/DEM/'))
            print("gdem: lso:", self.path_gd)
        elif self.subdir == "surveyvlso":
            self.path_gd.extend(self.addAllSubdirs("kthm2015_04_16", "DSM"))
            self.path_gd.extend(self.addAllSubdirs("kthm2015_10_14", "DSM"))
            self.path_gd.extend(self.addAllSubdirs("kthm2018_01_16", "DSM"))
            #self.path_gd.extend((\
              #'/samba2/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/DODEKANISA/DSM/',
              #'/samba2/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/KYKLADES/DSM/',
              #'/samba2/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/CHIOS/DSM/',
              #'/samba2/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/LESVOS/DSM/',
              #'/samba2/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/SAMOS/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/ATTIKIS/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/AITOLOAKARNANIA/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/AXAIA/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/HLEIA/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/ARGOLIDA/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/ARKADIA/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/KORINTIA/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/LAKONIA/DSM/',
              #'/samba2/data/gdem/kthm2015_10_14/PELOPONNHSOS/MESSINIA/DSM/'))
            print("gdem: vlso:", self.path_gd)
        elif self.subdir == "tanidemhem":
            self.path_gd.extend((\
              '/mnt/tera2/backup_data/tanidemhem/',))
        else:
            for pref in path_earth:
                self.path_gd.append(pref.rstrip()+subdir)

    def addAllSubdirsold(self, parent, subdir):
        "Check resurively all subdirs of parent and if their name is subdir add them to a list; return the list."
        if p_ggen.Pyos.Windows: pref = "F:/"
        else:                   pref = "/samba2"
        parent = p_ggen.path(pref) / parent
        parent = parent.expand()     #Change / to \ in windows
        if not parent.exists() or not parent.isdir():
            print(parent, "does not exist!")
            return tuple()
        print("parent=", parent)
        #return tuple(parent.walkdirs(subdir))
        res = []
        for x in parent.walkdirs(subdir):
            print(x)
            res.append(x)
        return tuple(res)


    def addAllSubdirs(self, parent, subdir):
        "Check resurively all subdirs of parent and if their name is subdir add them to a list; return the list."
        res = []
        found = False
        for pref in path_earth:
            pref = p_ggen.path(pref.strip())
            if not pref.exists() or not pref.isdir(): continue
            par = pref / parent
            par = par.expand()     #Change / to \ in windows
            if not par.exists() or not par.isdir():
                print("Warning: gdem: addAllSubdirs(): directory {} does not exist".format(par))
                continue
            found = True
            print("gdem: addAllSubdirs(): adding directory tree {}:".format(par))
            #res.extend(parent.walkdirs(subdir))
            for x in par.walkdirs(subdir):
                print(x)
                res.append(x)
        if not found:
            print("Warning: gdem: addAllSubdirs(): no data directories were found!")
        if len(res) <= 0:
            print("Warning: gdem: addAllSubdirs(): no data subdirectories were found!")
        return tuple(res)


    def user2geodetGRS80(self, cp):
        "Transform user coordinates to GRS80 geodetic using current user geodetic projection."
        cn = list(cp)
        alam, phi = self.projcur.en2geodetGRS80(cp[0], cp[1])
        cn[:2] = self.geodDeg(alam*180.0/pi, phi*180.0/pi)  #Projection function parameters/return values are always in rad
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
        if self.demcur is not None:
            z = self.demcur.thanPointZ(cp)
            if z is not None: return z
        cg = self.user2geodetGRS80(cp)
        fn = self.frameName(cg[0], cg[1])
        if fn is None: return None
        dem = self.cgiarDem.get(fn)
        if dem is None:
            if fn in self.cgiarNotfound: return None   #We searched for this before, but we did not find it
            dem, terr = self.openFrameFile(fn)
            if dem is None:
                self.cgiarNotfound.add(fn)             #So that we don't have to search for it in the future
                return None
            self.cgiarDem[fn] = dem
        self.demcur = dem
        return dem.thanPointZ(cp)


    def thanIntersegZ(self, ca, cb, native=False):
        "Compute intersections of segment with DEM lines; don't sort intersections from ca to cb."
        xymm = min(ca[0], cb[0]), min(ca[1], cb[1]), max(ca[0], cb[0]), max(ca[1], cb[1])
        dems, loaded, notfound, notcovered = self.thanGetWin(xymm)
        cint = []
        for dtm in self.cgiarDem.values():   #OK for python 2,3
            cints1 = dtm.thanIntersegZ(ca, cb, native)
            cint.extend(cints1)
        return cint


    def thanXymm(self, native=False):
        "Return the min and max x and y coordinates."
        xymm = p_gvarcom.Xymm()
        for dem in self.cgiarDem.values():              #SRTM files read so far  #OK for python 2,3
            xymm.includeXymm(dem.thanXymm(native))
        if xymm.isNull(): return None                   #No SRTM files read (or found)
        return xymm


    def thanDxy(self):
        """Return the DX, DY of the dem.

        Because the coordinate transformation usually leads to variable DX, DY
        the average DX, DY are returned: the average DX, DY of a random frame.
        """
        for dem in self.cgiarDem.values():              #SRTM files read so far  #OK for python 2,3
            return dem.thanDxy()
        return None, None                               #No SRTM files read (or found)


    def openFrameFile(self, fn):
        "Opens the file which contains the grid."
        fn = fn.strip()
        for par in self.path_gd:
            #fnu1 = par.strip() + fn
            fnu1 = p_ggen.path(par.strip()) / fn
            print("openFrameFile(): par=", par, "   fnu1=", fnu1)
            try:            uGri = open(fnu1, "rb")
            except IOError: pass
            else:           break
        else:
            terr = 'File '+fn+' can not be found or accessed'
            print("tra3:", terr)
            return None, terr
        uGri.close()
        if fnu1.endswith(".img"):
            dem = p_gtri.ThanDEMbilc(self.isorthometric, self.nodatadef)
        else:
            dem = p_gtri.ThanDEMsrtm(self.isorthometric, self.nodatadef)
        ok, terr = dem.thanSet(fnu1, None, self.user2geodetGRS80, self.geodetGRS802User)
        if not ok: print("tra4", terr); return None, terr
        return dem, ""


    def frameName(self, alam, phi):
        "Find the name of the appropriate gdem frame which contains the given geodetic coordinates."
        nl, np = self.frameNumber(alam, phi)
        if nl is None: return None
        fn = self.frameNameN(nl, np)
        return fn


    @staticmethod
    def geodDeg(alam, phi):
        "Convert angles (degrees) so that they are -180 <= alam <180, -90<=phi<90 if possible."
        alam %= 360.0   #Ensure 0 <= alam <= 360
        phi  %= 360.0   #Ensure 0 <= phi  <= 360
        if alam >= 180.0: alam -= 360.0
        if phi  >= 180.0: phi  -= 360.0
        return alam, phi


    def frameNameN(self, nl, np):
        "Find the name of the appropriate gdem frame given its number(s)."
        raise AttributeError("frameNameN must be overridden")
    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the gdem frame that contains the point at ala, phi.

        These should be integer numbers which differ by 1 for consecutive frames
        in the x or x direction."""
        #Frame number is called by frameName and thanGetWin().
        #frameName is called only thanPointZ()
        #Both thanPointZ() and thanGetWin() first call user2geodetGRS80() and then
        #call frameNumber (through frameName).
        #Since user2geodetGRS80() make lam and phi to the specs needed by frameNumber()
        #frameNumber() does not need to ensure that lam and phi are -180 and 180 or -90 and 90.
        raise AttributeError("frameNumber must be overridden")
    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of gdem frame: nl, np."
        raise AttributeError("frameXymm must be overridden")


    def thanGetFrameRectangles(self, xymm=None):
        "Get all the fames in xymm and return their boundaries."
        #dems, loaded, notfound, notcovered = self.thanGetWin(xymm)
        xymmfns = []
        for dem,fn in self.thanGetAvailable(xymm):
            xymmfns.append((dem.thanXymm(), fn))
        return xymmfns


    def thanGetAvailable(self, xymm=None):
        "Return all the available frames in this computer one by one, but do not load them in cache."
        for par in self.path_gd:
            par = p_ggen.path(par)
            if not par.exists or not par.isdir(): continue
            for fn in p_ggen.path(par).files(self.fwild):
                dem, terr = self.openFrameFile(fn.basename())
                if dem is None:     #Some error
                    self.prt("Could not access {}: {}".format(fn.basename(), terr), "can1")
                elif xymm is None:  #Return all the availabe frames
                    yield dem, fn.basename()
                elif xymm.intersectsXymm(dem.thanXymm()):  #Return frame only if (patially) inside xymm
                    yield dem, fn.basename()
                else:
                    pass   #dem not inside xymm


    def thanGetWin(self, xymm):
        "Load all the dems with crossing window xymm; xymm is according to ThanCad conventions."
        alama, phia, _ = self.user2geodetGRS80((xymm[0], xymm[3], 0.0))    #Up, left point of the window
        alamb, phib, _ = self.user2geodetGRS80((xymm[2], xymm[1], 0.0))    #Down, right point of the window
        #if phia > 180.0: phia -= 360.0
        #if phib > 180.0: phib -= 360.0
        nla, npa = self.frameNumber(alama, phia, check=False)
        nlb, npb = self.frameNumber(alamb, phib, check=False)
        #print xymm
        #print "thangetwin(): nla, nlb=", nla, nlb
        #print "thangetwin(): npa, npb=", npa, npb
        #print "frames:", self.frameNameN(nla, npa), ":", self.frameNameN(nlb, npb)
        dems = []        #The dems inside the window
        loaded = []      #DEMs which were loaded now
        notfound = []    #DEMs which were not found in current computer (you can download them from internet)
        notcovered = []  #DEMs which the gdem does not cover at all
        for nl in range(nla, nlb+1):
            for np in range(npa, npb-1, -1):
                covered = self.frameXymm(nl, np)
                if covered is None:
                    notcovered.append((nl, np))
                    continue
                fn = self.frameNameN(nl, np)
                if fn in self.cgiarDem:
                    dems.append(self.cgiarDem[fn])
                    continue
                if fn in self.cgiarNotfound:   #We searched for this fn previously and we did not find it
                    notfound.append((nl, np))
                    continue
                dem, terr = self.openFrameFile(fn)
                if dem is not None:
                    self.cgiarDem[fn] = dem
                    dems.append(dem)
                    loaded.append((nl, np))
                    continue
                notfound.append((nl, np))
                self.cgiarNotfound.add(fn)    #So that we don't have to search for it in the future
        return dems, loaded, notfound, notcovered


    def thanGetWinC(self, xymm, fail=True, prg=p_ggen.prg):
        "Load all the frames of the gdem and check if all were read."
        name = self.name
        if " " in name: name = "'"+name+"'"
        prg("Reading %s frames.." % (name,), "info1")
        dems, loaded, notfound, notcovered = self.thanGetWin(xymm) #All dems returned, are references to objects stored in gdem
        if len(notcovered) > 0: prg("Part of (or all) the area is outside the %s gdem" % (self.name,), "can1")
        if len(notfound) > 0:
            prg("The following frames of the %s gdem are not present in the current computer" % (self.name,), "can")
            prg("(they can be downloaded from the internet):", "can1")
            for nl, np in notfound: prg(self.frameNameN(nl, np), "can1")
        if len(dems) < 1: 
            terr = "No frames of the %s gdem were found in this area or in this computer" % (self.name,)
            if fail: p_gfil.er1s(terr)
            prg(terr, "can")
        return dems


    def joinDem(self, xymm):
        "Return a single DEM that contains the region xymm."
        dems, loaded, notfound, notcovered = self.thanGetWin(xymm)
        if len(dems) == 0: return None
        alama, phia, _ = self.user2geodetGRS80((xymm[0], xymm[3], 0.0))    #Up, left point of the window
        alamb, phib, _ = self.user2geodetGRS80((xymm[2], xymm[1], 0.0))    #Down, right point of the window
        dem1 = dems[0]                                                  #an arbitrary dem of the gdem
        demnew = p_gtri.ThanDEMsrtm(self.isorthometric, self.nodatadef)   #New combined dem
        ok, terr = demnew.thanNew(alama, phia, alamb, phib, dem1.DX, dem1.DY, dem1.im.mode,
            nodata=dem1.GDAL_NODATA, native=True, user2geodetGRS80=self.user2geodetGRS80, geodetGRS802User=self.geodetGRS802User)
        assert ok
        nxcolsnew, nyrowsnew = demnew.thanGetSize()
        for dem1 in dems:
            xymm1 = dem1.thanXymm(native=True)
            jxanew, iyanew = demnew.thanPixelCoor((xymm1[0], xymm1[3], 0.0), native=True)  #Up, left point of the dem
            jxbnew, iybnew = demnew.thanPixelCoor((xymm1[2], xymm1[1], 0.0), native=True)  #Up, left point of the dem
            jxa, iya = 0, 0
            jxb, iyb = dem1.thanGetSize()
            jxb -= 1
            iyb -= 1
            assert jxanew < nxcolsnew
            assert iyanew < nyrowsnew
            assert jxbnew >= 0
            assert iybnew >= 0
            if jxanew < 0: jxa += 0-jxanew; jxanew = 0
            if iyanew < 0: iya += 0-iyanew; iyanew = 0
            if jxbnew > nxcolsnew-1: jxb += nxcolsnew-1-jxbnew; jxbnew = nxcolsnew-1
            if iybnew > nyrowsnew-1: iyb += nyrowsnew-1-iybnew; iybnew = nyrowsnew-1
            #self.testwrite(dem1, jxa, jxb, iya, iyb)
            im1 = dem1.im.crop((jxa, iya, jxb, iyb))
            demnew.im.paste(im1, (jxanew, iyanew))
        return demnew


    def testwrite(self, dem1, jxa, jxb, iya, iyb):
            "Test hmin, hmax and write points for test purposes."
            import p_gvarcom
            fw = open("q1.syn", "w")
            hmin = 1e100
            hmax = -1e100
            for jx in range(jxa, jxb+1):
                for iy in range(iya, iyb+1):
                    h = dem1.getpixel(jx, iy)
                    if h == dem1.GDAL_NODATA: continue
                    if h < hmin: hmin = h
                    if h > hmax: hmax = h
                    xx, yy, _ = dem1.thanObjCoor(jx, iy)
                    p_gvarcom.wrSyn1(fw, str(jx+10000*iy), xx, yy, h)
            fw.close()
            hmax = max(dem1.getpixel(jx, iy) for jx in range(jxa, jxb+1) for iy in range(iya, iyb+1))
            print("region hmin, hmax=", hmin, hmax)


    def joinDemold(self, xymm):
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
        for dem in self.cgiarDem.values():  #SRTM files read so far   #OK for python 2,3
            if xymm is None:
                for cc in dem.iterNodes(validnodes=validnodes, invalidnodes=invalidnodes, xymm=xymm):
                    yield cc
            elif xymm.intersectsXymm(dem.thanXymm()):
                for cc in dem.iterNodes(validnodes=validnodes, invalidnodes=invalidnodes, xymm=xymm):
                    yield cc


    def destroy(self):
        "Break circular references."
        del self.cgiarDem, self.demcur, self.projcur


    def __del__(self):
        print("Object", self, "dies")


    def test1(self):
        "Test the code of finding frame given geodetic coordinates."
        while True:
            alam = float(raw_input("λ: "))
            phi = float(raw_input("φ: "))
            print(self.frameName(alam, phi))


    def test2(self):
        "Test the range of a frame given geodetic coordinates."
        while True:
            nl = int(raw_input("nl: "))
            np = int(raw_input("np: "))
            print(self.frameXymm(nl, np))


    def testAthens(self):
        "Test the elevations of GDEM in Athens."
        import p_gearth
        cps = [(23.7,       38.001,       42.0, "Κηφισσός λίγο πιο πάνω από Καβάλας"),
               (23.685,     37.931,      2.0, "Πειραιάς - ΖΕΑ"),
               (23.767886,  37.978815, 148.0, "Σπίτι"),
               (23.7787972, 37.976822, 186.0, "Πολ.Μηχ.ΕΜΠ"),
              ]
        self.thanSetProjection(p_ggeod.GeodetGRS80())    #Data is in GRS80 geodetic coordinates
        print()
        print()
        print()
        print()
        print(self.name)
        print("-------------------------------------------------------")
        for cp in cps:
            print("λ=%10.5f  φ=%10.5f   %s" % (cp[0], cp[1], cp[-1]))
            cp = list(cp)
            cp[0] *= pi/180.0
            cp[1] *= pi/180.0
            h = self.thanPointZ(cp)
            N = p_gearth.egm08Ndyn(cp[0], cp[1])
            if h is None: h = -8888.8
            print("Google: %8.1f  %s: %8.1f     N:%.1f" % (cp[2], self.name, h, N))
        print()
        print("Test EGSA87 coordinates near Athens")
        self.thanSetProjection(p_ggeod.egsa87)
        cp = [480000.0, 4200000.0, -9999.0]
        h = self.thanPointZ(cp)
        N = p_gearth.egm08Ndyn(cp[0], cp[1])
        if h is None: h = -8888.8
        print(cp)
        print("Google: %8.1f  %s: %8.1f     N:%.1f" % (cp[2], self.name, h, N))


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

        alam should be -180<alam<180 and phi  -56 < phi <=60."""
         #alam, phi = self.geodDeg(alam, phi)  #This is not needed: see GDEM.grameNumber()
        if check and alam >= 180.0: return None, None
        if check and alam < -180.0: return None, None
        if check and phi > 60.0: return None, None
        if check and phi <= -56.0: return None, None  #Thanasis2018_04_20
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
            print(nl, int(nl))

        while True:
            alam = float(raw_input("λ: "))
            nl = (alam-(-180.0))/5.0+1.0
            print(nl, int(nl))


class SRTM1USGSGDEM(GDEM):
    """Computes elevation on the whole surface of earth using SRTM 1arc version 3 from USGS.
    SRTM 1 Arc-Second Global elevation data offer worldwide coverage of
    void filled data at a resolution of 1 arc-second (30 meters) and provide open
    distribution of this high-resolution global data set. Some tiles may still
    contain voids. Users should check the coverage map in EarthExplorer to
    verify if their area of interest is available. Please note that tiles above 50°
    north and below 50° south latitude are sampled at a resolution of 2
    arc-second by 1 arc-second.
    """
    subdir = "srtm1usgs"
    name = "SRTM 1 arc USGS v3"
    filnam = "%%%SRTM1USGS%%%"                #This is for ThanCad

    def frameNameN(self, nl, np):
        "Find the name of the appropriate ASTER frame given its number(s)."
#       "n37_w123_1arc_v3.tif, n41_e001_1arc_v3.tif, n41_e002_1arc_v3.tif"
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "%s%02d_%s%03d_1arc_v3.tif" % (sn, abs(np), we, abs(nl))


    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the SRTM frame that contains the point at ala, phi.

        alam should be -180<alam<180 and phi  -56 < phi <=60.

        """
         #alam, phi = self.geodDeg(alam, phi)  #This is not needed: see GDEM.grameNumber()
        if check and alam >= 180.0: return None, None
        if check and alam < -180.0: return None, None
        if check and phi > 60.0: return None, None
        if check and phi <= -56.0: return None, None
        nl = int(alam)
        if alam < 0.0: nl -= 1
        np = int(phi)
        if phi < 0.0: np -= 1
        #Thanasis2018_04_20: nl, np might not be accurate for tiles above 50°
        #north and below 50° south latitude, as they are sampled at a resolution of 2
        #arc-second by 1 arc-second.
        #See .../data/2017_10_20srtm1arc_usgs1arc/infosrtm1arc.pdf  (for example in /mnt/xfsdata)
        if phi > 50.0 or phi < -50.0:
            print("WARNING: p_gearth.gdem.frameNumber(), {}:".format(self.name))
            print("nl, np might not be accurate for tiles above 50°")
            print("north and below 50° south latitude, as they are sampled at a resolution of 2")
            print("arc-second by 1 arc-second.")
        return nl, np


    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of ASTER frame: nl, np."
        if check and nl < -180: return None
        if check and nl >  179: return None
        if check and np <  -56: return None
        if check and np >   60: return None
        alam1 = nl
        phi1 = np
        return (alam1, phi1-1.0, alam1+1.0, phi1)


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
        #alam, phi = self.geodDeg(alam, phi) #This is not needed: see GDEM.grameNumber()

        if check and alam >= 180.0: return None, None
        if check and alam < -180.0: return None, None
        if phi > 83.0: return None, None
        if phi <= -83.0: return None, None
        nl = int(alam)
        if alam < 0.0: nl -= 1
        np = int(phi)
        if phi < 0.0: np -= 1
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


class AW3D30GDEM(GDEM):
    "Computes elevation on the whole surface of earth using ASTER ALOS WORLD 3D 30."
    subdir = "aw3d30"
    name = "ASTER ALOS WORLD 3D 30"
    filnam = "%%%AW3D30%%%"                #This is for ThanCad

    def frameNameN(self, nl, np):
        "Find the name of the appropriate AW3D30 frame given its number(s)."
#       "s078e166_ave_dsm.tif
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "%s%03d%s%03d_ave_dsm.tif" % (sn, abs(np), we, abs(nl))


    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the ASTER frame that contains the point at ala, phi."""
#       "astgtm2_n34e024_dem.tif"
#       "s078e166_ave_dsm.tif

        #alam, phi = self.geodDeg(alam, phi) #This is not needed: see GDEM.grameNumber()

        if check and alam >= 180.0: return None, None
        if check and alam < -180.0: return None, None
        nl = int(alam)
        if alam < 0.0: nl -= 1
        np = int(phi)
        if phi < 0.0: np -= 1
        return nl, np


    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of ASTER frame: nl, np."
        if check and nl < -180: return None
        if check and nl >  179: return None
        alam1 = nl
        phi1 = np
        return (alam1, phi1-1.0, alam1+1.0, phi1)


class AW3D30_V31GDEM(AW3D30GDEM):
    "Computes elevation on the whole surface of earth using ASTER ALOS WORLD 3D 30."
    subdir = "aw3d30_v31"
    name = "ASTER ALOS WORLD 3D 30 Vresion 3.1"
    filnam = "%%%AW3D30_V31%%%"                #This is for ThanCad

    def frameNameN(self, nl, np):
        "Find the name of the appropriate AW3D30 frame given its number(s)."
#       "alpsmlc30_n041e003_dsm.tif
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "alpsmlc30_%s%03d%s%03d_dsm.tif" % (sn, abs(np), we, abs(nl))


class GreekcGDEMold(GDEM):
    "Computes elevation on the whole surface of Greece using c."
    subdir = "greekc"
    name = "GreekcOld"
    filnam = "%%%GREEKCOLD%%%"                 #This is for ThanCad

    def __init__(self):
        "Make initial arrangements."
        super(GreekcGDEMold, self).__init__(isorthometric=True, nodatadef=0.0)
        self.htrs07 = p_ggeod.egsa87      #Data is saved in EGSA87, not GRS80 λ, φ

    def user2geodetGRS80(self, cp):
        "Transform user coordinates to HTRS07 using current user geodetic projection."
        cn = list(cp)
        #print("GreekcGDEMold: user2geodetGRS80(): cp=", cp)
        alam, phi = self.projcur.en2geodetGRS80(cp[0], cp[1])
        #print("GreekcGDEMold: user2geodetGRS80(): lam, phi=", alam, phi)
        cn[:2] = self.htrs07.geodetGRS802en(alam, phi)
        #print("GreekcGDEMold: user2geodetGRS80(): cn=", cn)
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


class GreekcGDEM(GreekcGDEMold):
    "Computes elevation on the whole surface of Greece using c."
    subdir = "survey"
    name = "Greekc LSO"
    filnam = "%%%GREEKC%%%"                 #This is for ThanCad
    fwild = "??????????.img"                #bash regular expression for the filenames of frames: used in thanGetAvailable()

    def frameNameN(self, nl, np):
        """Find the name of the appropriate Greekc LSO frame given its number(s).

        Examples: 0628042630.img 0628042660.img 0632042630.img 0632042660.img
                  0632042690.img 0632042720.img 0636042630.img 0636042660.img
                  0636042690.img
        """
        x = nl*40
        y = np*30
        y -= 30                #Convert to lower corner
        return "%05d%05d.img" % (x, y)

    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the Greekc frame that contains the point at alam, phi.

        Instead of the lower left corner report the upper left corner.
        """
        nl = int(alam / 4000.0)
        np = int(phi  / 3000.0)
        np += 1                           #upper left corner.
        return nl, np


class VlsoGreekcGDEM(GreekcGDEMold):
    "Computes elevation on the whole surface of Greece using c."
    subdir = "surveyvlso"
    name = "Greekc VLSO"
    filnam = "%%%VLSO_GREEKC%%%"                 #This is for ThanCad
    fwild = "??????????.img"                     #bash regular expression for the filenames of frames: used in thanGetAvailable()

    def frameNameN(self, nl, np):
        """Find the name of the appropriate Greekc VLSO frame given its number(s).

        Examples: 0684042522.img  0684042528.img  0684042534.img  0685642438.img
                  0685642444.img
        """
        x = nl*8
        y = np*6
        y -= 6                #Convert to lower corner
        return "%05d%05d.img" % (x, y)

    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the Greekc frame that contains the point at ala, phi.

        Instead of the lower left corner report the upper left corner.
        """
        nl = int(alam / 800.0)
        np = int(phi  / 600.0)
        np += 1                           #upper left corner.
        return nl, np


class TanIDEM(GDEM):
    "Computes elevation on the whole surface of earth using TanDEM-X Intermediate DEM."
    #TDM1_IDEM_04_N36E025_DEM.tif
    subdir = "tanidem"
    name = "TanDEM-X Intermediate DEM"
    filnam = "%%%TANIDEM%%%"                 #This is for ThanCad

    def __init__(self):
        "Make initial arrangements."
        super().__init__(isorthometric=False, nodatadef=-32767.0)


    def frameNameN(self, nl, np):
        "Find the name of the appropriate IDEM frame given its number(s)."
        #TDM1_IDEM_04_N36E025_DEM.tif
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "tdm1_idem_04_%s%02d%s%03d_dem.tif" % (sn, abs(np), we, abs(nl))


    def frameNumber(self, alam, phi, check=True):
        "Find the numbers of the IDEM frame that contains the point at ala, phi."
        #alam, phi = self.geodDeg(alam, phi) #This is not needed: see GDEM.grameNumber()
        if check and alam >= 180.0: return None, None
        if check and alam < -180.0: return None, None
        if phi > 90.0: return None, None
        if phi < -90.0: return None, None
        nl = int(alam)
        if alam < 0.0: nl -= 1
        np = int(phi)
        if phi < 0.0: np -= 1
        return nl, np


    def frameXymm(self, nl, np, check=True):
        "Find the range (ThanCad style) of the geodetic coordinates of frame: nl, np."
        if check and nl <= -180: return None
        if check and nl >   180: return None
        if check and np <   -90: return None
        if check and np >    90: return None
        alam1 = nl
        phi1 = np
        return (alam1, phi1-1.0, alam1+1.0, phi1)


class TanIDEMhem(TanIDEM):
    "Computes the error of elevation on the whole surface of earth using TanDEM-X Intermediate DEM."
    #tdm1_idem_04_n35e027_hem.tif
    subdir = "tanidemhem"
    name = "TanDEM-X Intermediate DEM - Height Error Map"
    filnam = "%%%TANIDEMHEM%%%"                 #This is for ThanCad
    def __init__(self):
        "Make initial arrangements."
        GDEM.__init__(self, isorthometric=True, nodatadef=-32767.0)


    def frameNameN(self, nl, np):
        "Find the name of the appropriate IDEM frame given its number(s)."
        #TDM1_IDEM_04_N36E025_DEM.tif
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "tdm1_idem_04_%s%02d%s%03d_hem.tif" % (sn, abs(np), we, abs(nl))


class TanXDEM(TanIDEM):
    "Computes elevation on the whole surface of earth using TanDEM-X DEM."

    def __init__(self, step=12, hem=False):
        "Make initial arrangements."
        if step not in (12, 30, 90): raise ValueError("Valid steps are 12, 30 or 90. Found: {}".format(step))
        self.subdir = "tanxdem/{}{}".format(step, "hem" if hem else "")
        self.name = "TanDEM-X DEM ({}){}".format(step, " - Height Error Map" if hem else "")
        self.filnam = "%%%TANXDEM{}{}%%%".format(step, "HEM" if hem else "")                 #This is for ThanCad
        self.fncod = "{:02d}".format(step//3)    #Code: for 90m->"30", for 30m->"10", for 12m->"04"
        self.fndem = "hem" if hem else "dem"
        print("subdir=", self.subdir)
        print("name  =", self.name)
        print("filnam=", self.filnam)
        print("fncod =", self.fncod)
        print("fndem =", self.fndem)
        super().__init__()  #This must be called after self.subdir etc have been defined and have already overshaddowed the class variable subdir etc defined superclass
        if hem: GDEM.__init__(self, isorthometric=True, nodatadef=-32767.0)
        else:   GDEM.__init__(self, isorthometric=False, nodatadef=-32767.0)

    def frameNameN(self, nl, np):
        "Find the name of the appropriate IDEM frame given its number(s)."
        #tdm1_dem__30_n34e023_dem.tif, tdm1_dem__30_n34e023_hem.tif  (90m)
        #tdm1_dem__10_n36e021_dem.tif, tdm1_dem__10_n36e021_hem.tif  (30m)
        #tdm1_dem__04_n34e023_dem.tif, tdm1_dem__04_n34e023_hem.tif  (12m)
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "tdm1_dem__%s_%s%02d%s%03d_%s.tif" % (self.fncod, sn, abs(np), we, abs(nl), self.fndem)


class TanXDEM30(TanIDEM):
    "Computes elevation on the whole surface of earth using TanDEM-X DEM."
    #tdm1_dem__10_n36e021_dem.tif
    subdir = "tanxdem/30"
    name = "TanDEM-X DEM (30)"
    filnam = "%%%TANXDEM30%%%"                 #This is for ThanCad
    fncod="10"
    fndem = "dem"

    def frameNameN(self, nl, np):
        "Find the name of the appropriate IDEM frame given its number(s)."
        #tdm1_dem__10_n36e021_dem.tif
        we = "w" if nl < 0 else "e"
        sn = "s" if np < 0 else "n"
        return "tdm1_dem__%s_%s%02d%s%03d_%s.tif" % (self.fncod, sn, abs(np), we, abs(nl), self.fndem)


class TanXDEM30hem(TanXDEM30):
    "Computes the error of elevation on the whole surface of earth using TanDEM-X30 DEM."
    #tdm1_dem__10_n36e021_hem.tif
    subdir = "tanxdem/30hem"
    name = "TanDEM-X DEM (30) - Height Error Map"
    filnam = "%%%TANXDEM30HEM%%%"                 #This is for ThanCad
    fndem = "hem"


class TanXDEM12(TanXDEM30):
    "Computes elevation on the whole surface of earth using TanDEM-X DEM."
    #tdm1_dem__04_n34e023_dem.tif
    subdir = "tanxdem/12"
    name = "TanDEM-X DEM (12)"
    filnam = "%%%TANXDEM12%%%"                 #This is for ThanCad
    fncod="04"


class TanXDEM12hem(TanXDEM12):
    "Computes the error of elevation on the whole surface of earth using TanDEM-X12 DEM."
    #tdm1_dem__04_n34e023_hem.tif
    subdir = "tanxdem/12hem"
    name = "TanDEM-X DEM (12) - Height Error Map"
    filnam = "%%%TANXDEM12HEM%%%"                 #This is for ThanCad
    fndem = "hem"


class TanXDEM90(TanXDEM30):
    "Computes elevation on the whole surface of earth using TanDEM-X DEM."
    #tdm1_dem__30_n34e023_dem.tif
    subdir = "tanxdem/90"
    name = "TanDEM-X DEM (90)"
    filnam = "%%%TANXDEM90%%%"                 #This is for ThanCad
    fncod="30"


class TanXDEM90hem(TanXDEM90):
    "Computes the error of elevation on the whole surface of earth using TanDEM-X12 DEM."
    #tdm1_dem__30_n34e023_hem.tif
    subdir = "tanxdem/90hem"
    name = "TanDEM-X DEM (90) - Height Error Map"
    filnam = "%%%TANXDEM90HEM%%%"                 #This is for ThanCad
    fndem = "hem"


def gdem(name):
    "Return a global DEM according to filnam."
    name1 = name.strip("% ").upper()
    #print("gdem(): name=", name)
    if name1 == "SRTM":        return SRTMGDEM()
    if name1 == "SRTM1USGS":   return SRTM1USGSGDEM()
    if name1 == "ASTER":       return ASTERGDEM()
    if name1 == "AW3D30":      return AW3D30GDEM()
    if name1 == "AW3D30_V31":  return AW3D30_V31GDEM()
    if name1 == "GREEKC":      return GreekcGDEM()
    if name1 == "VLSO_GREEKC": return VlsoGreekcGDEM()
    if name1 == "TANIDEM":     return TanIDEM()
    if name1 == "TANIDEMHEM":  return TanIDEMhem()
    if name1 == "TANXDEM12":   return TanXDEM(step=12, hem=False)
    if name1 == "TANXDEM12HEM":return TanXDEM(step=12, hem=True)
    if name1 == "TANXDEM30":   return TanXDEM(step=30, hem=False)
    if name1 == "TANXDEM30HEM":return TanXDEM(step=30, hem=True)
    if name1 == "TANXDEM90":   return TanXDEM(step=90, hem=False)
    if name1 == "TANXDEM90HEM":return TanXDEM(step=90, hem=True)
    raise ValueError("Unknown GDEM: %s" % (name,))


def gdemNames(hem=False, idio=False, none=False):
    "Return all the avaliable gdem names."
    __tnames = "SRTM SRTM1USGS ASTER AW3D30 AW3D30_V31 GREEKC VLSO_GREEKC TANIDEM TANXDEM12 TANXDEM30 TANXDEM90"
    __themnames = "TANIDEMHEM TANXDEM12HEM TANXDEM30HEM TANXDEM90HEM"
    t = __tnames
    if hem:  t += " " + __themnames
    if idio: t += " ΙΔΙΟ"
    if none: t += " NONE"
    return t

def datGdem(fr, hem=False, idio=False, none=False):
    "Read one valid gdem name from a Datlin object."
    t = gdemNames(hem, idio, none)
    name = fr.datMchoice(t, 12)
    return name

def datGdemMult(fr, hem=False, idio=False, none=False):
    "Read multiple valid gdem names from a Datlin object."
    t = gdemNames(hem, idio, none)
    name = []
    while not fr.eol():
        name.append(fr.datMchoice(t, 12))
    return name
