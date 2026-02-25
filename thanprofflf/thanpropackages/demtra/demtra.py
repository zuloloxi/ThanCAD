#!/usr/bin/python
# -*- coding: iso-8859-7 -*-
##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

Package which finds the optimum transaltion between SRTM and EGSA87.
"""
import sys
import p_ggen, p_gfil, p_gearth, p_gtri
import demex, deman
frw = {}
winmain = None
prg = p_ggen.prg
thanPointZ = None


def pyMain():
    "Main routine."
    global thanPointZ
    openFiles()
    try:
        cen, dxyrange, dxy, dxysample, method, name = readPar()
        clines = readSyk(frw["syk"])
        if name == "ΙΔΙΟ":
            dtm = makeDTM1(clines)
            thanPointZ = dtm.thanPointZ
        else:
            gdem = p_gearth.gdem(name)
            thanPointZ = gdem.thanPointZ
        cps = samplePoints(clines, dxy=dxysample)
        del clines
        if method[:2] == "ΕΞ":
            demex.exhaust(frw["syn"], name, thanPointZ, cps, cen, dxyrange, dxy, prg)
        else:
            deman.anneal(frw["syn"], name, thanPointZ, cps, prg)
    except BaseException, e:
        raise
        p_gfil.er1s("\n%s:\n%s" % (p_gfil.Tgui["Error while executing program"], e), "can")
    p_gfil.closeFiles1()                        #Not reentrant


def samplePoints(clines, dxy):
    "Reduce the number of points for speed up."
    grid = {}
    if dxy <= 0.0:
        for cline1 in clines:
            for cp in cline1:
                grid[cp[0], cp[1]] = cp
    else:
        for cline1 in clines:
            for cp in cline1:
                ix = round(cp[0]/dxy)
                iy = round(cp[1]/dxy)
                grid[ix, iy] = cp
    cps = grid.values()
    if len(cps) < 1: raise ValueError, "No points found in the DTM"
    return cps


def readSyk(fr):
    "Reads the contours of a syk file."
    lindxf = 0
    it = iter(fr)
    clines = []
    for dline in it:
        lindxf += 1
        try:
            z1 = float(dline[:15])
        except (ValueError, IndexError), why:
            why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
            raise ValueError, why
        cc = []
        for dline in it:
            lindxf += 1
            if dline.strip() == "$": break
            try:
                x1 = float(dline[:15])
                y1 = float(dline[15:30])
            except (ValueError, IndexError), why:
                why = "%s %d of file .syk:\n%s" % ("Error at line", lindxf, why)
                raise ValueError, why
            else: cc.append([x1, y1, z1])

        if len(cc) < 1: print "Polyline with 0 vertices."
        clines.append(cc) #-----------Store the polyline
    return clines


def makeDTM1(clines):
    "Makes DTM from lines."
    dtm = p_gtri.ThanDTMlines()
    for cline1 in clines:
        dtm.thanAddLine1(cline1)
    dtm.thanRecreate()
    return dtm


def readPar():
    "Read center and range of exhaustive search."
    fr = p_gfil.Datlin(frw["par"])
    fr.datCom("ΚΕΝΤΡΟ ΑΝΑΖΗΤΗΣΗΣ")
    x = fr.datFloat()
    y = fr.datFloat()
    cen = (x, y)
    fr.datCom("ΑΚΤΙΝΑ ΑΝΑΖΗΤΗΣΗΣ")
    dxyrange = fr.datFloatR(0.0e-6, 1.0e6)
    fr.datCom("ΒΗΜΑ ΑΝΑΖΗΤΗΣΗΣ")
    dxy = fr.datFloatR(1.0e-6, 1.0e6)
    fr.datCom("ΑΠΟΣΤΑΣΗ ΔΕΙΓΜΑΤΟΛΗΨΙΑΣ")
    dxysample = fr.datFloatR(0.0, 1.0e6)

    fr.datCom("ΜΕΘΟΔΟΣ ΑΝΑΖΗΤΗΣΗΣ")
    method = fr.datMchoice("ΕΞΑΝΤΛΗΤΙΚΗ ΑΝΟΠΤΗΣΗ")

    fr.datCom("ΠΑΓΚΟΣΜΙΟ DEM")
    name = fr.datMchoice("SRTM ASTER ΙΔΙΟ")
    return cen, dxyrange, dxy, dxysample, method, name


def openFiles():
    "Opens the needed files."
    global frw, winmain, prg, pref
    p_gfil.setPar(openfileParx)
    p_gfil.openFile1(0, ' ',   ' ',   1, 'ΠΡΟΓΡΑΜΜΑ υπολογισμού βέλτιστης μεταφοράς μεταξύ SRTM και ΨΜΕδ')
    p_gfil.openFile1(1, 'syk',  'old', 1, 'με γραμμές ΨΜΕδ')
    p_gfil.openFile1(1, 'par',  'old', 1, 'παραμέτρων υπολογισμού')
    p_gfil.openFile1(1, 'syn',  ' ',   1, 'βέλτιστης μεταφοράς')
    frw = p_gfil.openFile1(998, ' ', ' ', 1, ' ')
    winmain, prg1, _ = p_gfil.openfileWinget()
    if winmain != None: prg = prg1


def openfileParx (icod1, un):
#---messages
    if icod1 < 0:
        prg = un
        prg("Το πρόγραμμα demtra.py βρίσκει συστηματικό σφάλμα DX, DY μεταξύ του ΕΓΣΑ87")
        prg("και ενός παγκόσμιου DEM (SRTM ή ASTER). Ο υπολογισμός γίνεται με εξαντλητική")
        prg("αναζήτηση (exhaustive search) ή με εξομοίωση ανόπτησης (simulated annealing).")
        prg("Τετ 22 Αύγ 2012 07:53:18 μμ EEST")


if __name__ == "__main__":
    pyMain()
