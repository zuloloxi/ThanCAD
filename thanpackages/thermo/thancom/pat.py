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

The package automates the data input of the diploma thesis of Xaris Patounis
and Nikos Simos of the School of Civil Engineering, National Technical
University of Athens.
The subpackage implements architecture related procedures.
"""
#from past.builtins import range
import sys, csv
import p_ggen, p_gfil, p_gmath
frw = {}
date = ""
winmain = None
pro = ""
prg = p_ggen.prg
temphum = {}
let2num = {}
step = 4.0
meas = {}       #Measurements


def pyMain():
    "Main program."
    global prg
    prg = p_ggen.prg
    openFiles()
    try:
        letinit()
        thermgen()
        therm()
        gridgen(None, wrSyn)
    except BaseException as e:
#        raise
        p_gfil.er1s("\n%s:\n%s" % (p_ggen.Tgui["Error while executing program"], e), "can")
    p_gfil.closeFiles1()                        #Not reentrant


def thanCadMain(proj):
    "Main routine when the program is embedded inth ThanCad."
    from thancom.thancomfile import thanTxtopen, thanRenameHouse
    from thanvar import Canc
    global prg
    prg = proj[2].thanPrt
    prg("Εισαγωγή μετρήσεων θερμοϋγρομέτρου.", "info")
    prg("Διπλωματική εργασία Χάρη Πατούνη, Νίκου Σίμου, Σχολή Πολ. Μηχανικών, ΕΜΠ, 2012", "info")
    fn, fr = thanTxtopen(proj, mes='Επιλογή αρχείου μετρήσεων .csv (από .xls)', suf=".csv", mode="r", initialfile=None, initialdir=None)
    if fr == Canc: return proj[2].thanGudCommandCan()
    fn = fn.parent / fn.namebase.replace(".", "_") + ".thcx"
    thanRenameHouse(proj, fn)
    frw["csv"] = fr
    try:
        letinit()
        thermgen()
        therm()
        gridgen(proj, thancadSyn)
    except BaseException as e:
#        raise
        prg("\n%s:\n%s" % (p_ggen.Tgui["Error while executing program"], e), "can")
        try: fr.close()
        except: pass
        proj[2].thanGudCommandEnd("(Μπορεί νά έχει γινει μερική εισαγωγή σημείων)")
    else:
        fr.close()
        proj[2].thanGudCommandEnd("Δημιουργήθηκαν 4 διαφάνειες.", "info")


def letinit():
    "Initialize letter to number dictionary."
    ia = ord("A")-1
    for i in range(ia+1, ord("Z")+1):
        let2num[chr(i)] = i-ia
    let2num["ZA"] = 27
    let2num["ZB"] = 28


def thermgen():
    "Ανάγνωση και εγγραφή γενικών δεδομένων θερμοϋγρομέτρου."
    global date
    prg("Ανάγνωση και εγγραφή γενικών δεδομένων θερμοϋγρομέτρου.", "info1")
    fn = frw["csv"].name
    frw["csv"].seek(0)
    fr = csv.reader(frw["csv"], delimiter=";")
    r = [next(fr) for i in range(6)]
    try:
        r[4][0], r[4][2], r[4][3], r[2][2], r[3][2], r[5][1]
    except:
#       p_gfil.er1s("Missing data in lines 1-6 of file %s" % (fn,))
        er1sCsv(fn, 4, 0, "Missing data in lines 1-6")
    com1Csv("property",    r[4][0], fn, 4, 0)
    com1Csv("temperature", r[4][2], fn, 4, 2)
    com1Csv("humidity",    r[4][3], fn, 4, 3)
    naminst = r[2][2]                          #Name of instrument
    place = r[3][2]
    date, _ = datetime(r[5][1], fn, 5, 1)


def datetime(dline, fn, irow, icol):
    "Decipher date and time."
    dl = dline.split()
    if len(dl) == 2:          #28/06/2012 8:02:04
        return dl[0], dl[1]
    elif len(dl) == 3:        #28/06/2012 8:02:04 ??
        if dl[2] == "??": return dl[0], dl[1]
    elif len(dl) == 4:        #??? 2011 8:02:11 ??
        if dl[2] == "??": return "_".join(dl[:2]), dl[2]
    er1sCsv(fn, irow, icol, "Can not decipher date and time: '%s'" % (dline,))


def er1sCsv(fn, irow, icol, terr):
    "Print error message for csv file."
    t = "Error at cell %s%d of file %s:\n%s" % (colnam(icol), irow+1, fn, terr)
    raise ValueError(t)


def colnam(icol):
    "Find the name of column icol."
    j = ord("A")
    if icol > 25:
        return chr(j+icol/26)+char(icol%26)
    else:
        return chr(j+icol)


def com1Csv(com1, found, fn, irow, icol):
    "Ensure command com1 is found."
    if com1.lower() == found.lower(): return
    er1sCsv(fn, irow, icol, "Expected '%s' but found '%s'." % (com1, found))


def therm():
    "Ανάγνωση και εγγραφή μετρήσεων θερμοϋγρομέτρου."
    prg("Ανάγνωση και εγγραφή μετρήσεων θερμοϋγρομέτρου.", "info1")
    fn = frw["csv"].name
    frw["csv"].seek(0)
    fr = csv.reader(frw["csv"], delimiter=";")
    for i in range(5): next(fr)
    temphum.clear()
    meas.clear()
    i = 0
    for r in fr:
        i += 1
        com1Csv(str(i), r[0], fn, i+5, 0)
        dat, tim = datetime(r[1], fn, i+5, 1)
        try:
            com1Csv(date, dat, fn, i+5, 1)
            tim1 = time2sec(tim)
        except (IndexError, ValueError) as e:
            er1sCsv(fn, i+5, 1, "Συντακτικό λάθος:\n%s" % (e,))

        com1Csv("°C", r[2][-2:], fn, i+5, 2)
        try:
            temp = float(r[2][:-2].replace(",", "."))
        except ValueError as e:
            er1sCsv(fn, i+5, 2, "Syntax error: %s" % (e,))
        com1Csv("%RH", r[3][-3:], fn, i+5, 3)
        try:
            hum = float(r[3][:-3].replace(",", "."))
        except ValueError as e:
            er1sCsv(fn, i+5, 3, "Syntax error: %s" % (e,))
        if tim in temphum: er1sCsv(fn, i+5, 1, "Ο χρόνος %d έχει ξαναβρεθεί." % (tim,))
        temphum[tim1] = temp, hum, i


def gridgen(proj, syn):
    "Ανάγνωση και εγγραφή δεδομένων κανάβου."
    prg("Ανάγνωση και εγγραφή κανάβου.", "info1")
    fn = frw["csv"].name
    frw["csv"].seek(0)
    fr = csv.reader(frw["csv"], delimiter=";")

    irow = -1
    for r in fr:
        irow += 1
        if r[8] == "Έναρξη": break
    else:
        raise ValueError("Δεν βρέθηκε η λέξη 'Έναρξη' στη στήλη %s του αρχείου %s" % (colnam(8), fn))
    for i in 8, 11, 15:
        if i >= len(r): er1sCsv(fn, irow, i, "Αναμενόταν: 'Έναρξη'")
        com1Csv("Έναρξη", r[i], fn, irow, i)
    for i in 9, 12, 16:
        if i >= len(r): er1sCsv(fn, irow, i, "Αναμενόταν: 'Τερματισμός'")
        com1Csv("Τερματισμός", r[i], fn, irow, i)

    for r in fr:
        irow += 1
        if r[7].strip() == "": break
        try:
            irow = int(r[7])
            icole, irowe = point(r[8].strip().upper(), irow)
            icolt, irowt = point(r[9].strip().upper(), irow)
            te1 = time2sec(r[11])
            tt1 = time2sec(r[12])
            te2 = time2sec(r[15])
            tt2 = time2sec(r[16])
            syn(proj, "temp1", icole, irowe, icolt, irowt, te1, tt1, 0)     #1η μέτρηση, θερμοκρασία
            syn(proj, "hum1",  icole, irowe, icolt, irowt, te1, tt1, 1)     #1η μέτρηση, υγρασία
            syn(proj, "temp2", icole, irowe, icolt, irowt, te2, tt2, 0)     #2η μέτρηση, θερμοκρασία
            syn(proj, "hum2",  icole, irowe, icolt, irowt, te2, tt2, 1)     #2η μέτρηση, υγρασία
        except (ValueError, IndexError) as e:
            raise ValueError("Συντακτικό λάθος στην γραμμή %s του αρχείου %s:\n%s" % (irow+1, fn, e))
    for fw in meas.values(): fw.close()   #works for python2,3
    for r in fr:
        irow += 1
        try:    r[7]
        except: continue
        if r[7].strip() != "": er1Csv(fn, irow, 7, "'%s' was found where nothing was expected." % (r[7],))


def time2sec(tim):
    "Convert from hours, minutes, seconds to integer seconds."
    try:
        h, m, s = map(int, tim.split(":"))   #works for python2,3
        tim1 = s + 60 * (m + 60*h)
    except (ValueError, IndexError) as e:
        raise ValueError("Συντακτικό λάθος κατά την ανάγνωση χρόνου: %s\n%s" % (tim, e))
    return tim1


def point(icole, irow):
    "Get row and column of point; if icole has a number (row) use it; otherwise it is irow."
    if "0" <= icole[0] <= "9":
        if "0" <= icole[1] <= "9":
            irowe = int(icole[:2])
            icole = icole[2:]
        else:
            irowe = int(icole[:1])
            icole = icole[1:]
    else:
        irowe = irow
    if icole not in let2num: raise ValueError("Column out of range: %s" % (icole,))
    icole = let2num[icole]
    return icole, irowe


def wrSyn(proj, fn, icole, irowe, icolt, irowt, time_e, time_t, j):
    "Write coordinates of a whole row; j=0->temperature, j=1->humidity."
    fw = meas.get(fn)
    if fw is None: fw = meas[fn] = open(pro+fn+".syn", "w")
    xe =  (icole-1)*step
    ye = -(irowe-1)*step
    xt =  (icolt-1)*step
    yt = -(irowt-1)*step
    for tim1 in range(time_e, time_t+1):
        ipoint = temphum[tim1][2]
        v = temphum[tim1][j]
        x = p_gmath.linint(time_e, xe, time_t, xt, tim1)
        y = p_gmath.linint(time_e, ye, time_t, yt, tim1)
        fw.write("%10d%15.3f%15.3f%15.3f\n" % (ipoint, x, y, v))


colt = {"temp1":"yellow", "hum1":"cyan", "temp2":"gold", "hum2":"blue"}

def thancadSyn(proj, fn, icole, irowe, icolt, irowt, time_e, time_t, j):
    "Draw the point into ThanCad a whole row; j=0->temperature, j=1->humidity."
    from thansupport import thanToplayerCurrent
    from thandr import ThanPointNamed
    c = list(proj[1].thanVar["elevation"])
    lay = thanToplayerCurrent(proj, fn, current=True, moncolor=colt[fn])
    xe =  (icole-1)*step
    ye = -(irowe-1)*step
    xt =  (icolt-1)*step
    yt = -(irowt-1)*step
    for tim1 in range(time_e, time_t+1):
        ipoint = temphum[tim1][2]
        c[2] = temphum[tim1][j]
        c[0] = p_gmath.linint(time_e, xe, time_t, xt, tim1)
        c[1] = p_gmath.linint(time_e, ye, time_t, yt, tim1)
        e = ThanPointNamed()
        e.thanSet(c, str(ipoint))
        proj[1].thanElementAdd(e)
        e.thanTkDraw(proj[2].than)


def openFiles():
    "Opens files for the program."
    global frw, winmain, prg, pro
    p_gfil.openFile1(0, ' ', ' ', 0, 'ΕΜΠ διπλωματική Χάρη Πατούνη, Νίκου Σίμου:\n Μετατροπή μετρήσεων θερμοϋγρομέτρου σε text')
    p_gfil.openFile1(1, 'csv', 'old', 1, 'μετρήσεων σε μορφή .csv (από .xls)')
    frw = p_gfil.openFile1(887, ' ', ' ', 0, ' ')
    winmain, prg1, _ = p_gfil.openfileWinget()
    if winmain is not None: prg = prg1
    pro = p_ggen.path(frw["csv"].name)
    pro = pro.parent/pro.namebase


if __name__ == "__main__": pyMain()
