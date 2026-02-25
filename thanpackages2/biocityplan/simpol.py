##############################################################################
# ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2025 Thanasis Stamos, May 20, 2025
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (www.gnu.org/licenses/gpl.html).
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################
"""\
ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers

Package which creates a bioclimatic city plan.
"""
import sys
import p_ggen, p_ganneal, p_gfil, p_gmath, p_gtri, p_gtkwid
from . import hippoanneal, roadut
frw = {}
pref = ""
winmain = None
prg = p_ggen.prg

USEDEM = False          #Use DEM instead of DTM
devdebug = False        #If True, execute Developer debug code



def pyMain():
    "Main routine."
    openFiles()
    try:
      hu = readRym()
      pc = hippoanneal.HippoAnneal(hu)
      pc.pol.USEDEM = USEDEM
      pc.pol.devdebug = devdebug
      pc.pol.cache.devdebug = devdebug
      readPar(pc)
      if frw["cache"] is None:
          clines = readDTM()
          dtm = makeDTM(clines)
          if hu is None:
              prg("City plan will be the convex hull of the DTM.", "info1")
              hu = makeHull(clines)
              wrRym(hu)
          else:
              hu = makeHull([hu])
          pc.pol.hull = hu
          if pc.pol.USEDEM:
              prg("Προεπεξεργασία DEM (μπορεί να χρειαστεί πολλά λεπτά)..", "info")
              pc.pol.build_dem(dtm, prt=prg)
#              pc.pol.dem.plot()    #Plot the hull and the dem as points
          else:
              prg("Προεπεξεργασία (μπορεί να χρειαστεί πολλά λεπτά)..", "info")
              pc.pol.build_cache(dtm, prt=prg)
              wrCache(pc)
      else:
          prg("Reading road grid cache..", "info")
          if hu is not None:
              prg("    City plan defined in .rym file is overwritten by the city plan in the .cache file", "can1")
          pc.pol.readGrid(frw["cache"])
          if devdebug:
              clines = readDTM()                                                    ##########
              dtm = makeDTM(clines)                                                 ##########
              prg("Προεπεξεργασία DEM (μπορεί να χρειαστεί πολλά λεπτά)..", "info") ##########
              pc.pol.build_dem(dtm, prt=prg)                                        ##########
              pc.pol.dem.dtmq = dtm                                                 ##########

      coms = ("1. Εκτέλεση του προγράμματος 1 φορά (1=προεπιλογή)",
              "2. Εκτέλεση του προγράμματος πολλές φορές",
              "3. Προβολή ήδη υπολογισμένης λύσης",
             )
      if winmain is None:
          prg("")
          prg("\n".join(coms))
          i = p_ggen.inpLongR("Επιλογή (enter=1): ", 1, 3, 1)
      else:
          i = p_gtkwid.xinpMchoice(winmain, "", coms, douDef=1)
          if i is None: sys.exit()

      if i == 1:
          runOnce(pc, prt=prg)
          wrState(pc, pref)
          show(pc)
      elif i == 2:
          if winmain is None:
              n = p_ggen.inpLongR("Πόσες εκτελέσεις (enter=100): ", 1, 1000, 100)
          else:
              n = p_gtkwid.xinpLongR(winmain, "Πόσες εκτελέσεις (enter=100): ", 1, 1000, 100)
              if n is None: sys.exit()
          for i in range(n):
              runOnce(pc, prt=prg)
              wrState(pc, pref)
      else:
          if winmain is None:
              i = p_ggen.inpLongR("α/α υπολογισμένης λύσης (enter=0): ", 0, 1000, 0)
          else:
              i = p_gtkwid.xinpLongR(winmain, "α/α υπολογισμένης λύσης (enter=0): ", 0, 1000, 0)
              if i is None: sys.exit()
          rdState(pc, i)
          show(pc)
    except BaseException as e:
        raise
        p_gfil.er1s("\n%s:\n%s" % (p_ggen.Tgui["Error while executing program"], e), "can")
    p_gfil.closeFiles1()                        #Not reentrant


def runOnce(pc, prt=p_ggen.prg):
    "Run the simulated annealing method once."
    pc.repairState()
    sa = p_ganneal.SimulatedAnnealing(prt=prt) #animon=True, animnframe=20)
#    sa.config(tsteps=2)
    sa.anneal(pc)
    e = pc.energyState() / pc.efact
    prt("Final energy=%.3f -> %.3f" % (e, e*pc.efact))
    s = pc.state
    s.e, s.d8, s.d10 = pc.pol.energy3(s)


def makeDTM(clines):
    "Makes DTM from lines."
    dtm = p_gtri.ThanDTMlines()
    for cline1 in clines: dtm.thanAddLine1(cline1)
    dtm.thanRecreate()
    return dtm


def makeHull(clines):
    "Computes convex hull of DTM lines."
    cc = []
    for cline1 in clines: cc.extend(cline1)
    hu = p_gtri.hull(cc)
    return hu


def show(pc):
    "Show the result."
    s = pc.state
    ot = list(pc.pol.iterOT(s))
#    roads = pc.pol.roadcoor(s)
    roads = ()
    tit = "Energy=%.1f,  d>8%%=%.1f,  d>10%%=%.1f" % (s.e, s.d8, s.d10)
    lins = pc.pol.contours
    pc.pol.show(winmain, title=tit,   iso=lins, ot=ot, roads=roads)
    pc.pol.dxfout(title=tit, iso=lins, ot=ot, roads=roads, fw=open(pref+".dxf", "w"))
    pc.pol.pilout(title=tit, iso=lins, ot=ot, roads=roads)[0].save(pref+".png")


def readSyk(fr):
    "Reads the contours of a syk file."
    lindxf = 0
    it = iter(fr)
    clines = []
    for dline in it:
        lindxf += 1
        try:
            z1 = float(dline[:15])
        except (ValueError, IndexError) as why:
            why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
            raise ValueError(why)
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                x1 = float(dline[:15])
                y1 = float(dline[15:30])
            except (ValueError, IndexError) as why:
                why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
                raise ValueError(why)
            else: cc.append([x1, y1, z1])

        if len(cc) < 2: print("Polyline with 1 or 0 vertices.")
        clines.append(cc) #-----------Store the polyline
    return clines


def readDTM():
    "Reads DTM lines."
    clines = readSyk(frw["syk"])
    if len(clines) < 2:
        sys.stderr.write("File %s contains less than 2 lines\n" % (frw["syk"].name,))
        p_gfil.stopErr1()
    return clines


def readRym():
    "Reads the area of the city plan."
    if frw["rym"] is None: return None
    hull = readSyk(frw["rym"])
    if len(hull) != 1:
        sys.stderr.write("File %s should contain exactly 1 closed line\n" % (frw["rym"].name,))
        p_gfil.stopErr1()
    hull = hull[0]
    if not p_gmath.thanNear2(hull[0], hull[-1]):   #Make sure that line is closed
        hull.append(hull[0])
    return hull


def readPar(pc):
    "Reads parameters of city blocks."
    fd = p_gfil.Datlin(frw["par"])
    fd.datCom("ΠΛΑΤΟΣ Ο.Τ.")
    boik1, boik2 = rdminmax(fd)
    fd.datCom("ΥΨΟΣ Ο.Τ.")
    hoik1, hoik2 = rdminmax(fd)
    fd.datCom("ΠΛΑΤΟΣ ΟΔΩΝ")
    bod1, bod2 = rdminmax(fd)
    fd.datCom("ΒΙΟΚΛΙΜΑΤΙΚΗ ΘΕΩΡΗΣΗ")
    biochange = fd.datYesno()
    pc.setPar(boik1, boik2, hoik1, hoik2, bod1, bod2, biochange)


def rdminmax(fd):
    "Read min and max value."
    fd.datCom("ΕΛΑΧΙΣΤΟ")
    hoik1 = fd.datFloatR(1.0, 1000.0)
    fd.datCom("ΜΕΓΙΣΤΟ")
    hoik2 = fd.datFloatR(1.0, 1000.0)
    return hoik1, hoik2


def rdState(pc, i):
    "Read computed solution."
    fn = p_ggen.path("%s.state%03d" % (pref, i))
    if not fn.exists(): p_gfil.er1s("Can not open file %s\n" % fn, "can")
    fr = open(fn, "r")
    pc.rdstate(fr)
    fr.close()


def wrRym(hu):
    "Writes the area of the city plan."
    frw.update(p_gfil.opFile1e(1, "rym", "", pref, "περιοχής ρυμοτομικού - μορφή .syk"))
    fw = frw["rym"]
    fw.write("%15.3f  %s\n" % (0.0, "cityplan"))
    for c in hu: fw.write("%15.3f%15.3f\n" % tuple(c[:2]))
    fw.write("$\n")


def wrCache(pc):
    "Writes cache."
    frw.update(p_gfil.opFile1e(1, "cache", "", pref, 'προεπεξεργασίας'))
    fw = frw["cache"]
    pc.pol.writeGrid(fw)


def wrState(pc, pref, prter=p_ggen.prg):
    "Write computed solution."
    for i in range(1000):
        fn = p_ggen.path("%s.state%03d" % (pref, i))
        if not fn.exists(): break
    else:
        prter("Can not open file to save state: too many state files.")
        return
    fw = open(fn, "w")
    pc.wrstate(fw)
    fw.close()


def test_cache():
    "Reads and writes cache for test."
    hu, dtm = makeDTM("kam5k.syk")
    pc = cplan.HippoAnneal(hu, dtm)
    fr = open("kam5k_cache01.txt", "r")
    pc.pol.read_cache(fr)
    fr.close()
    fw = open("kam5k_cache02.txt", "w")
    pc.pol.write_cache(fw)
    fw.close()


def openFiles():
      "Opens the needed files."
      global frw, winmain, prg, pref
      p_gfil.openFile1(0, ' ',   ' ',   1, 'ΠΡΟΓΡΑΜΜΑ υπολογισμού βιοκλιματικού ρυμοτομικού σχεδίου')
      p_gfil.openFile1(1, 'syk',  'old', 1, 'με γραμμές DTM')
      p_gfil.openFile1(1, 'rym',  'opt', 1, 'περιοχής ρυμοτομικού - μορφή .syk')
      p_gfil.openFile1(1, 'par',  'opt', 1, 'παραμέτρων Ο.Τ.')
      p_gfil.openFile1(1, 'cache','opt', 1, 'προεπεξεργασίας')
      frw = p_gfil.openFile1(998, ' ', ' ', 1, ' ')
      pref = p_ggen.path(frw["syk"].name)
      pref = pref.parent / pref.namebase
      winmain, prg1, _ = p_gfil.openfileWinget()
      if winmain is not None: prg = prg1


if __name__ == "__main__":
    pyMain()
