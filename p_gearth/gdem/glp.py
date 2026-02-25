from math import fabs
import p_gfil, p_gearth
from p_ggen import floate, prg, path
from p_gvarcom import wrTrg1
from . import pathearth

#print("pathearth.path_earth=", pathearth.path_earth)
path_earth = [path(x.strip()).expand().parent for x in pathearth.path_earth]
#print("path_earth=", path_earth)


class GLP:
    "This class implements GLobal Points."
    subdir = ""
    name = "Global Point Coordinates"
    filnam = ""                 #This is for ThanCad
    im = "GLP"                  #This is for ThanCad: If it is None, ThanCad assumes that the DEM was not loaded/found
    fwild = "*"                 #bash regular expression for the filenames of frames: used in thanGetVailable()

    def __init__(self, prt=prg):
        "Initial values."
        self.prt = prt

    def __del__(self):
        print("Object", self, "dies")


class GLPTrigGYS(GLP):
    "This class handles the trigonometric points of GYS, Greece."
    subdir = "1998cd_trig_xartes50k_gys/triggys/"
    name = "Trigonometric Points of GYS"
    filnam = "%%%TRIGGYS%%%"    #This is for ThanCad
    fwild = "*.csv"             #bash regular expression for the filenames of frames: used in thanGetVailable()


    def __init__(self, prt=prg):
        "Initial values."
        super().__init__(prt)
        self.trig = self.trigori = self.tit = None
        self.prt = prt


    def thanGetPoints(self, xymm):
        "Return the points inside rectangle xymm."
        triga = []
        trigoria = []
        terr = self.load()
        if terr != "": return None, None, terr
        for aa, p in self.trig.items():
            if p[1:3] in xymm:
                triga.append(p)
                trigoria.append(self.trigori[aa])
        return triga, trigoria, self.tit


    def loadold(self):
        "Load the coordinates of trigonometric from files."
        if self.trig is not None: return True
        dn = path(self.subdir)
        try:
            fns = list(dn.files(self.fwild))
        except OSError as e:
            return "Could not load {}: could not access {}:\n{}.".format(self.name, dn, str(e))
        if len(fns) == 0:
            return "Could not load {}: No file was found.".format(self.name)
        if len(fns) > 1:
            self.prt("Warning: {}: Multiple data files found: Only the first is loaded.".format(self.name), "can1")
        try:
            fr = open(fns[0])
        except OSError as e:
            return "Could not load {}: {} can not be accessed.".format(self.name, fns[0])
        trig, trigori, tit, terr = self.readTrigCsv(fr)
        fr.close()
        if trig is None:
            return "Could not load {}: Error while reading {}: {}.".format(self.name, fns[0], terr)
        self.trig = trig
        self.trigori = trigori
        self.tit = tit
        return ""


    def load(self):
        "Load the coordinates of trigonometric from files."
        if self.trig is not None: return True
        dn1 = path(self.subdir)
        for par in path_earth:
            dn = path(par) / dn1
            if dn.exists() and dn.isdir(): break
        else:
            return "Could not load {}: could not find/access subdirectory {}".format(self.name, dn1)
        try:
            fns = list(dn.files(self.fwild))
        except OSError as e:
            return "Could not load {}: could not access {}:\n{}.".format(self.name, dn, str(e))
        if len(fns) == 0:
            return "Could not load {}: No file was found.".format(self.name)
        if len(fns) > 1:
            self.prt("Warning: {}: Multiple data files found: Only the first is loaded.".format(self.name), "can1")
        try:
            fr = open(fns[0])
        except OSError as e:
            return "Could not load {}: {} can not be accessed.".format(self.name, fns[0])
        trig, trigori, tit, terr = self.readTrigCsv(fr)
        fr.close()
        if trig is None:
            return "Could not load {}: Error while reading {}: {}.".format(self.name, fns[0], terr)
        self.trig = trig
        self.trigori = trigori
        self.tit = tit
        return ""


    @staticmethod
    def readTrigCsv(fr, prt=prg):
        "Read the trigonometric points of gys from a .csv file."
        def er1(mes):
            "Return an error message."
            terr = "Error at line {} of file: {}".format(lin, mes)
            return None, None, None, terr

        lin = 0
        for dline in fr:
            tit = tuple(temp.strip() for temp in dline.split(";"))
            lin += 1
            break
        else:
            return er1("Empty file.")

        trigori = {}
        trig = {}
        for dline in fr:
            dl = [temp.strip() for temp in dline.split(";")]
            lin += 1
            aa = dl[1]
            if aa == "": return er1("Empty A/A of trigonometric point.")
            if aa in trigori:
                if dl != trigori[aa]: return er1("Duplicate A/A of trigonometric point: {}".format(aa))
                prt("Duplicate A/A has exactly the same data and it is ignored: {}".format(aa), "can1")
                continue

            desc = dl[2]
            if desc == "": desc = aa
            x = floate(dl[10])
            y = floate(dl[11])
            z = floate(dl[12])
            hbaq = floate(dl[13]) 
            if x is None or y is None or z is None:
                return er1("Non numeric x or y or z or hbaq of trigonometric point {}: {} {} {} {}".format(
                    aa, dl[10], dl[11], dl[12], dl[13]))
            trig[aa] = desc, x, y, z, hbaq
            trigori[aa] = dl
        return trig, trigori, tit, ""
