from math import pi
import p_ggeod, p_ggen, p_gfil, p_gvarcom
from .pathearth import path_earth


class Gortho:
    "Computes elevation on the whole surface of a planet."
    subdir = ""
    name = "Global Digital Elevation Model"
    filnam = ""                 #This is for ThanCad
    im = "GDEM"                 #This is for ThanCad: If it is None, ThanCad assumes that the DEM was not loaded/found
    fwild = "*"                 #bash regular expression for the filenames of frames: used in thanGetAvailable()

    def __init__(self, isorthometric=True, nodatadef=None, prt=p_ggen.prg):
        "Make initial arrangements."
        self.prt = prt
        self.cgiarDem = {}               #SRTM files read so far
        self.cgiarNotfound = set()       #SRTM files which were searched for, and were not found
        self.projcur = p_ggeod.egsa87    #Default user geodetic projection
        subdir = self.subdir.strip().strip("/\\") + "/"
        self.path_gd = ['                                       ']
        #print("self.subdir=", self.subdir)
        if self.subdir == "survey":
            self.path_gd.extend((\
              '/samba/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/DODEKANISA/LSO/',
              '/samba/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/KYKLADES/LSO/',
              '/samba/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/DODEKANISA/KASTELORIZO/LSO/',
              '/samba/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/CHIOS/LSO/',
              '/samba/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/LESVOS/LSO/',
              '/samba/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/SAMOS/LSO/',
              '/samba/data/gdem/kthm2015_10_14/ATTIKIS/LSO/',
              '/samba/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/AITOLOAKARNANIA/LSO/',
              '/samba/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/AXAIA/LSO/',
              '/samba/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/HLEIA/LSO/',
              '/samba/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/LSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/ARGOLIDA/LSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/ARKADIA/LSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/KORINTIA/LSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/LAKONIA/LSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/MESSINIA/LSO/',
              '/samba/data/gdem/kthm2018_01_16/HPEIROS/ARTA/LSO/'))
        elif self.subdir == "surveyvlso":
            self.path_gd.extend((\
              '/samba/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/DODEKANISA/VLSO/',
              '/samba/data/gdem/kthm2015_04_16/NOTIO_AIGAIO/KYKLADES/VLSO/',
              '/samba/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/CHIOS/VLSO/',
              '/samba/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/LESVOS/VLSO/',
              '/samba/data/gdem/kthm2015_04_16/VOREIO_AIGAIO/SAMOS/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/ATTIKIS/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/AITOLOAKARNANIA/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/AXAIA/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/HLEIA/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/DYTIKH_ELLADA/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/ARGOLIDA/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/ARKADIA/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/KORINTIA/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/LAKONIA/VLSO/',
              '/samba/data/gdem/kthm2015_10_14/PELOPONNHSOS/MESSINIA/VLSO/',
              '/samba/data/gdem/kthm2018_01_16/HPEIROS/ARTA/VLSO/'))
            #print("gdem: vlso:", self.path_gd)
        elif self.subdir == "surveyokxe":
            self.path_gd.extend((\
              '/samba/data/gdem/2018_06_30okxe/Attica_orthophotos_2010/Orthos/',))
        else:
            assert 0, "No more GOIs !!!"


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


    def thanGetAt(self, cp):
        "Get the orthoimage which contains point cp (decimal degrees)."
        cg = self.user2geodetGRS80(cp)
        fn = self.frameName(cg[0], cg[1])
        if fn is None: return None
        if fn in self.cgiarNotfound: return None
        fnpath, terr = self.openFrameFile(fn)
        if fnpath is None:
            self.cgiarNotfound.add(fn)    #So that we don't have to search for it in the future
            return None
        return fnpath


    def openFrameFile(self, fn):
        "Opens the file which contains the grid."
        fn = fn.strip()
        for par in self.path_gd:
            fnu1 = par.strip() + fn
            print("openFrameFile(): par=", par, "   fnu1=", fnu1)
            try:            uGri = open(fnu1, "rb")
            except IOError: pass
            else:           break
        else:
            terr = 'File '+fn+' can not be found or accessed'
            print("tra3:", terr)
            return None, terr
        uGri.close()
        return fnu1, ""


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
    def frameName2N(self, fn):
        "Find the numbers of a frame, given its filename."
        raise AttributeError("frameName2N must be overridden")
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


    def thanGetFrameRectangles(self, xymm):
        "Load all the fames in xymm and return their boundaries."
        #dems, loaded, notfound, notcovered = self.thanGetWin(xymm)
        xymms = []
        for fn in self.thanGetAvailable(xymm):
            nl, np = self.frameName2N(fn)
            assert nl is not None, "It should have been found!!!"
            xymm1 = self.frameXymm(nl, np, check=False)  #If we found the frame, then check has no meaning
            xymms.append(xymm1)
        return xymms


    def thanGetAvailable(self, xymm=None):
        "Return all the available frames in this computer one by one, but do not load them in cache."
        for par in self.path_gd:
            par = p_ggen.path(par)
            if not par.exists or not par.isdir(): continue
            for fnpath in p_ggen.path(par).files(self.fwild):
                fn = fnpath.basename()
                ok, terr = self.openFrameFile(fn)
                if ok is None:     #Some error
                    self.prt("Could not access {}: {}".format(fn, terr), "can1")
                    continue
                nl, np = self.frameName2N(fn)
                if nl is None:
                    self.prt("Malformed frame name {}".format(fn), "can1")
                    continue
                if xymm is None:  #Return all the availabe frames
                    yield fnpath
                    continue
                xymm1 = self.frameXymm(nl, np, check=False)  #If we found the frame, then check has no meaning
                if xymm.intersectsXymm(xym11):  #Return frame only if (patially) inside xymm
                    yield fnpath


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
        notfound = []    #DEMs which were not found in current computer (you can download them from internet)
        notcovered = []  #DEMs which the gdem does not cover at all
        for nl in range(nla, nlb+1):
            for np in range(npa, npb-1, -1):
                covered = self.frameXymm(nl, np)
                if covered is None:
                    notcovered.append((nl, np))
                    continue
                fn = self.frameNameN(nl, np)
                if fn in self.cgiarNotfound:   #We searched for this fn prebiously and we did not find it
                    notfound.append((nl, np))
                    continue
                fnpath, terr = self.openFrameFile(fn)
                if fnpath is not None:
                    dems.append(fnpath)
                    continue
                notfound.append((nl, np))
                self.cgiarNotfound.add(fn)    #So that we don't have to search for it in the future
        return dems, notfound, notcovered


    def thanGetWinC(self, xymm, fail=True, prg=p_ggen.prg):
        "Load all the frames of the gdem and check if all were read."
        name = self.name
        if " " in name: name = "'"+name+"'"
        prg("Reading %s frames.." % (name,), "info1")
        dems, notfound, notcovered = self.thanGetWin(xymm) #All dems returned, are references to objects stored in gdem
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


    def destroy(self):
        "Break circular references."
        del self.cgiarDem, self.projcur


    def __del__(self):
        print("Object", self, "dies")



class GreekcOld(Gortho):
    "Computes elevation on the whole surface of Greece using c."
    subdir = "greekc"
    name = "GreekcOld"
    filnam = "%%%GREEKCOLD%%%"                 #This is for ThanCad

    def __init__(self):
        "Make initial arrangements."
        super().__init__()
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
        return "%05d%05d.tfw" % (x, y)


    def frameName2N(self, fn):
        "Find the numbers of a frame, given its filename."
        try:
            x = int(fn[:5])
            y = int(fn[5:10])
        except ValueError as e:
            return None, None          #Malformed file name: not a gortho frame
        nl = x // 40
        y += 30
        np = (y-10) // 30
        fn1 = self.frameNameN(nl, np)
        if fn1.lower() != fn.lower():
            print("frameName2N(): {} != {}!!!".format(fn1, fn))
            return None, None
        return nl, np


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


class GreekcLSO(GreekcOld):
    "Computes elevation on the whole surface of Greece using c."
    subdir = "survey"
    name = "Greekc LSO"
    filnam = "%%%GREEKC%%%"                 #This is for ThanCad
    fwild = "??????????.tfw"                #bash regular expression for the filenames of frames: used in thanGetAvailable()

    def frameNameN(self, nl, np):
        """Find the name of the appropriate Greekc LSO frame given its number(s).

        Examples: 0628042630.img 0628042660.img 0632042630.img 0632042660.img
                  0632042690.img 0632042720.img 0636042630.img 0636042660.img
                  0636042690.img
        """
        x = nl*40
        y = np*30
        y -= 30                #Convert to lower corner
        return "%05d%05d.tfw" % (x, y)


    def frameName2N(self, fn):
        "Find the numbers of a frame, given its filename."
        try:
            x = int(fn[:5])
            y = int(fn[5:10])
        except ValueError as e:
            return None, None          #Malformed file name: not a gortho frame
        nl = x // 40
        y += 30
        np = y // 30
        fn1 = self.frameNameN(nl, np)
        if fn1.lower() != fn.lower():
            print("frameName2N(): {} != {}!!!".format(fn1, fn))
            return None, None
        return nl, np


    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the Greekc frame that contains the point at ala, phi.

        Instead of the lower left corner report the upper left corner.
        """
        nl = int(alam / 4000.0)
        np = int(phi  / 3000.0)
        np += 1                           #upper left corner.
        return nl, np


class GreekcVLSO(GreekcOld):
    "Computes elevation on the whole surface of Greece using c."
    subdir = "surveyvlso"
    name = "Greekc VLSO"
    filnam = "%%%VLSO_GREEKC%%%"                 #This is for ThanCad
    fwild = "??????????.tfw"                     #bash regular expression for the filenames of frames: used in thanGetAvailable()

    def frameNameN(self, nl, np):
        """Find the name of the appropriate Greekc VLSO frame given its number(s).

        Examples: 0684042522.img  0684042528.img  0684042534.img  0685642438.img
                  0685642444.img
        """
        x = nl*8
        y = np*6
        y -= 6                #Convert to lower corner
        return "%05d%05d.tfw" % (x, y)


    def frameName2N(self, fn):
        "Find the numbers of a frame, given its filename."
        try:
            x = int(fn[:5])
            y = int(fn[5:10])
        except ValueError as e:
            return None, None          #Malformed file name: not a gortho frame
        nl = x // 8
        y += 6
        np = y // 6
        fn1 = self.frameNameN(nl, np)
        if fn1.lower() != fn.lower():
            print("frameName2N(): {} != {}!!!".format(fn1, fn))
            return None, None
        return nl, np


    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the Greekc frame that contains the point at alam, phi.

        Instead of the lower left corner report the upper left corner.
        """
        nl = int(alam / 800.0)
        np = int(phi  / 600.0)
        np += 1                           #upper left corner.
        return nl, np


class OKXE(GreekcOld):
    "Computes elevation on the whole surface of Greece using c."
    subdir = "surveyokxe"
    name = "OKXE"
    filnam = "%%%OKXE%%%"                 #This is for ThanCad
    fwild = "??????????.j2w"              #bash regular expression for the filenames of frames: used in thanGetAvailable()


    def frameNameN(self, nl, np):
        """Find the name of the appropriate OKXE frame given its number(s).

        Examples: 0422042045.j2w, 0422042060.j2w, 0422042075.j2w, 0422042090.j2w,
                  0422042105.j2w, 0422042120.j2w,  0422042225.j2w"""
        x = nl*20
        y = np*15
        y -= 15                #Convert to lower corner
        return "%05d%05d.j2w" % (x, y)


    def frameName2N(self, fn):
        "Find the numbers of a frame, given its filename."
        try:
            x = int(fn[:5])
            y = int(fn[5:10])
        except ValueError as e:
            return None, None          #Malformed file name: not a gortho frame
        nl = x // 20
        y += 15
        np = y // 15
        fn1 = self.frameNameN(nl, np)
        if fn1.lower() != fn.lower():
            print("frameName2N(): {} != {}!!!".format(fn1, fn))
            return None, None
        return nl, np


    def frameNumber(self, alam, phi, check=True):
        """Find the numbers of the Greekc frame that contains the point at ala, phi.

        Instead of the lower left corner report the upper left corner.
        """
        nl = int(alam / 2000.0)
        np = int(phi  / 1500.0)
        np += 1                           #upper left corner.
        return nl, np


def gortho(name):
    "Return a global orthoimage according to filnam."
    name1 = name.strip("% ").upper()
    #print("gdem(): name=", name)
    if name1 == "GREEKCLSO":  return GreekcLSO()
    if name1 == "GREEKCVLSO": return GreekcVLSO()
    if name1 == "OKXE":       return OKXE()
    raise ValueError("Unknown global orthoimage: %s" % (name,))
