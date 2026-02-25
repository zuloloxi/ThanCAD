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

This module displays a dialog for the user to enter the necessary values
for the rectification of a raster map. Usually these maps are scanned from
paper and contain errors due to paper shrinking or enlarging and scanner
errors. The map is rectified using known grid points on the map (control points).
"""

import sys, copy, itertools, Image, Tkinter
from types import *
import p_gtkuti, p_gtkwid, p_ggen, p_grun
from thanvar import ThanLayerError, thanfiles
from thansupport import thanToplayerCurrent
from thantrans import T
from thannewcoefs import ThanNewCoefs
#from thanproortho.thanpropackages.thankaor import kaor
from thanproortho.thanpropackages.thankaor import ThanKaor


_widCoefs = "entFilsnt entA0 entA1 entA2 entA3 entA4 entA5 entB0 entB1 entB2 entB3 entB4 entB5".split()


class ThanMaprect(p_gtkwid.ThanComDialog):
    "Dialog for the map rectification."

    def __init__(self, *args, **kw):
        "Set title and translation."
        kw.setdefault("title", T[u"ΠΡΟΓΡΑΜΜΑ ΓΕΩΜΕΤΡΙΚΗΣ ΔΙΟΡΘΩΣΗΣ - ΑΝΑΓΩΓΗΣ ΧΑΡΤΩΝ (ORTHOMAP)"])
        kw.setdefault("buttonlabels", (T["Save and Exit"],  T["Save and Run"], T["Cancel"]))
        p_gtkwid.ThanComDialog.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()
        v.chkEgsa = False
        v.entFilsnt = ""
        v.entA0 = v.entB1 = 1.0
        v.entB0 = v.entB2 = v.entB3 = v.entB4 = v.entB5 = 0.0
        v.entA1 = v.entA2 = v.entA3 = v.entA4 = v.entA5 = 0.0
        v.entStepGr = 500.0; v.entStepPap = 100.0
        v.entXori = v.entYori = 0.0
        v.chkKor = True
        v.entKorX1 = v.entKorX2 = v.entKorX3 = v.entKorX4 = 0.0
        v.entKorY1 = v.entKorY2 = v.entKorY3 = v.entKorY4 = 0.0
        v.chkRGB2Ind = True
        v.chkGray2BW = True
        v.entBlack = 50.0
        v.chkReduce = False
        v.entReduce = 50.0
        return v


    def thanSet(self, vs):
        "Set new values to the widgets."
        p_gtkwid.ThanComDialog.thanSet(self, vs)
        self.__egsaEnable()
        self.__korEnable()
        self.__reduceEnable()
        self.__blackEnable()


    def __reduceEnable(self, evt=None):
        "Enable or disable the reduce widget."
        if self.chkReduce.thanGet(): stat = Tkinter.NORMAL
        else:                        stat = Tkinter.DISABLED
        self.entReduce.config(state=stat)


    def __blackEnable(self, evt=None):
        "Enable or disable the black widget."
        if self.chkGray2BW.thanGet(): stat = Tkinter.NORMAL
        else:                         stat = Tkinter.DISABLED
        self.entBlack.config(state=stat)


    def __egsaEnable(self, evt=None):
        "Enable or disable the EGSA87 widgets."
        if self.chkEgsa.thanGet(): stat = Tkinter.NORMAL
        else:                      stat = Tkinter.DISABLED
        for key in _widCoefs:
            wid = getattr(self, key)
            wid.config(state=stat)
        self.butCoef.config(state=stat)


    def __korEnable(self, evt=None):
        "Enable or disable the EGSA87 widgets."
        if self.chkKor.thanGet(): stat = Tkinter.NORMAL
        else:                     stat = Tkinter.DISABLED
        for i in xrange(4):
            wid = getattr(self, "entKorX"+str(i+1))
            wid.config(state=stat)
            wid = getattr(self, "entKorY"+str(i+1))
            wid.config(state=stat)


    def body(self, win):
        p_gtkwid.ThanComDialog.body(self, win)
        self.after(200, self.__validateReadGan)


    def body2(self, win):
        self.fraQuick(win, 0)
        self.fraMetEgsa(win, 1)
        self.fraStep(win, 2)
        self.fraOrigin(win, 3)
        self.fraKor(win, 4)
        self.fraImage(win, 5)
        win.columnconfigure(0, weight=1)


    def fraQuick(self, win, ir):
        "Quick process buttons."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir+1,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=u"ΠΡΟΚΑΤΑΡΚΤΙΚΑ:")
        lab.grid(row=0, column=1, sticky="w")
        but = Tkinter.Button(fra, text=T[u"Δημιουργία απαραίτητων layers\nκαι επιστροφή στο σχέδιο"],
            bg="lightcyan", activebackground="cyan", command=self.__crlay)
        but.grid(row=0, column=2, sticky="e")
        fra.columnconfigure(2, weight=1)


    def __crlay(self, *args):
        "Automatically Create Layers and leave."
        from thanlayer.thanlayatts import thanLayAtts
        proj = self.thanProj
        val = int(thanLayAtts["draworder"][2] / 2)  # Set lower draworder to layer RASTER than the default draworder..
        try:
            thanToplayerCurrent(proj, "KANABOSXY", current=False, moncolor="blue")
            thanToplayerCurrent(proj, "KANABOSX",  current=False, moncolor="green")
            thanToplayerCurrent(proj, "KANABOSY",  current=False, moncolor="red")
            thanToplayerCurrent(proj, "PLAISIO",   current=False, moncolor="cyan")
            thanToplayerCurrent(proj, "RASTER",    current=True,  moncolor="white", draworder=val)
        except (ThanLayerError, ValueError), why:
            p_gtkuti.thanGudModalMessage(self,
                T["%s\nPlease create new drawing for the rectification"] % why,
                T["Some layers can not be created"])
            return
        self.cancel()


    def fraMetEgsa(self, win, ir):
        "Widgets of EGSA87 transformation."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir+1,))
        lab.grid(row=0, column=0)
        key = "chkEgsa"
        tit = u"ΜΕΤΑΤΡΟΠΗ ΑΠΟ ΗΑΤΤ ΣΕ ΕΓΣΑ87"
        val = p_gtkwid.ThanValidator()
        wid = p_gtkwid.ThanCheck(fra, fg=self.colfra, text=tit, command=self.__egsaEnable)
        wid.grid(row=0, column=1, sticky="w")
        self.thanWids.append((key, tit, wid, val))

        frc = Tkinter.Frame(fra)
        frc.grid(row=1, column=1, columnspan=1, sticky="we")
        tit = u"ΑΡΧΕΙΟ ΣΥΝΤΕΛΕΣΤΩΝ ΜΕΤΑΤΡΟΠΗΣ"
        lab = Tkinter.Label(frc, anchor="w", text=tit)
        lab.grid(row=0, column=0, sticky="we")
        key = "entFilsnt"
        fildir = thanfiles.getFiledir()
        wid = p_gtkwid.ThanFile(frc, extension=".snt", initialdir=fildir, mode="r",
            command=self.__validateReadCoefs, title=tit, width=20, relief=Tkinter.RAISED)
        wid.grid(row=0, column=1, sticky="we")
	val = p_gtkwid.ThanValidator()
	self.thanWids.append((key, tit, wid, val))
        frc.columnconfigure(1, weight=1)

        frb = Tkinter.Frame(fra)
	frb.grid(row=2, column=1, columnspan=1, sticky="we")
	for i in xrange(6):
	    tit = u"A"+str(i)
	    key = "ent" + tit
            lab = Tkinter.Label(frb, text=tit)
            lab.grid(row=i, column=0, sticky="w")
	    wid = p_gtkwid.ThanLabel(frb, text="None", width=20)
	    wid.grid(row=i, column=1, sticky="we")
	    val = p_gtkwid.ThanValFloat()
	    self.thanWids.append((key, tit, wid, val))

	    tit = u"B"+str(i)
	    key = "ent" + tit
            lab = Tkinter.Label(frb, text=tit)
            lab.grid(row=i, column=2, sticky="w")
	    wid = p_gtkwid.ThanLabel(frb, text="None")
	    wid.grid(row=i, column=3, sticky="we")
	    val = p_gtkwid.ThanValFloat()
	    self.thanWids.append((key, tit, wid, val))
        frb.columnconfigure(1, weight=1)
        frb.columnconfigure(3, weight=1)

        self.butCoef = Tkinter.Button(frb, text=u"Διόρθωση/Εισαγωγή",
            bg="lightcyan", activebackground="cyan", command=self.__newCoefs)
        self.butCoef.grid(row=6, column=3, sticky="e")

        fra.columnconfigure(1, weight=1)


    def __newCoefs(self, evt=None):
        "Show the dialog for the new coefficients."
        self.validate(strict=False)
        v = p_ggen.Struct()
        for a in _widCoefs:
            val = getattr(self.result, a)
            setattr(v, a, val)

        dl = ThanNewCoefs(self, keys=_widCoefs, vals=v, cargo=self.thanProj)
        res = dl.result
        if res == None: return

        for a in _widCoefs:
            wid = getattr(self, a)
            val = getattr(res, a)
            wid.config(state=Tkinter.NORMAL)
            if type(val) == FloatType: val = str(val)
            wid.thanSet(val)
        self.__egsaEnable()


    def fraStep(self, win, ir):
        "Widgets of grid step in m and mm."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir+1,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=u"ΒΗΜΑ ΚΑΝΑΒΟΥ:")
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        lab = Tkinter.Label(fra, text=u"ΣΤΟ ΕΔΑΦΟΣ (m)")
        lab.grid(row=1, column=1, sticky="w")
        key = "entStepGr"
        tit = u"ΒΗΜΑ ΚΑΝΑΒΟΥ ΣΤΟ ΕΔΑΦΟΣ (m)"
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=1, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(1e-6, 1e6)
        self.thanWids.append((key, tit, wid, val))

        lab = Tkinter.Label(fra, text=u"ΣΤΟ ΧΑΡΤΙ (mm)")
        lab.grid(row=1, column=3, sticky="w")
	key = "entStepPap"
	tit = u"ΒΗΜΑ ΚΑΝΑΒΟΥ ΣΤΟ ΧΑΡΤΙ (mm)"
	wid = p_gtkwid.ThanEntry(fra)
	wid.grid(row=1, column=4, sticky="we")
	val = p_gtkwid.ThanValFloat(1e-6, 1e6)
        self.thanWids.append((key, tit, wid, val))

	fra.columnconfigure(2, weight=1)
	fra.columnconfigure(4, weight=1)


    def fraOrigin(self, win, ir):
        "Widgets of origin coordinates."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir+1,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=u"ΣΥΝΤΕΤΑΓΜΕΝΕΣ ΑΡΧΗΣ:")
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        lab = Tkinter.Label(fra, text=u"Χ (m)")
        lab.grid(row=1, column=1, sticky="w")
	key = "entXori"
	tit = u"ΣΥΝΤΕΤΑΓΜΕΝΗ ΑΡΧΗΣ Χ (mm)"
	wid = p_gtkwid.ThanEntry(fra)
	wid.grid(row=1, column=2, sticky="we")
	val = p_gtkwid.ThanValFloat()
        self.thanWids.append((key, tit, wid, val))

        lab = Tkinter.Label(fra, text=u"Υ (m)")
        lab.grid(row=1, column=3, sticky="w")
	key = "entYori"
	tit = u"ΣΥΝΤΕΤΑΓΜΕΝΗ ΑΡΧΗΣ Y (mm)"
	wid = p_gtkwid.ThanEntry(fra)
	wid.grid(row=1, column=4, sticky="we")
	val = p_gtkwid.ThanValFloat()
        self.thanWids.append((key, tit, wid, val))

	fra.columnconfigure(2, weight=1)
	fra.columnconfigure(4, weight=1)


    def fraKor(self, win, ir):
        "Widgets of EGSA87 transformation."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
	fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir+1,))
        lab.grid(row=0, column=0)
	key = "chkKor"
	tit = u"ΓΝΩΣΤΕΣ ΣΥΝΤΕΤΑΓΜΕΝΕΣ ΚΟΡΥΦΩΝ ΧΑΡΤΗ"
	wid = p_gtkwid.ThanCheck(fra, fg=self.colfra, text=tit, command=self.__korEnable)
	wid.grid(row=0, column=1, columnspan=5, sticky="w")
	val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, wid, val))

	for i,pos in enumerate((u"ΚΑΤΩ ΑΡΙΣΤΕΡΑ", u"ΚΑΤΩ ΔΕΞΙΑ", u"ΠΑΝΩ ΔΕΞΙΑ", u"ΠΑΝΩ ΑΡΙΣΤΕΡΑ")):
            lab = Tkinter.Label(fra, text=pos)
            lab.grid(row=i+1, column=1, sticky="w")
	    key = "entKorX" + str(i+1)
	    tit = u"X%d(m)" % (i+1,)
            lab = Tkinter.Label(fra, text=tit)
            lab.grid(row=i+1, column=2, sticky="w")
	    wid = p_gtkwid.ThanEntry(fra)
	    wid.grid(row=i+1, column=3, sticky="we")
	    val = p_gtkwid.ThanValFloat()
            self.thanWids.append((key, tit, wid, val))

	    key = "entKorY" + str(i+1)
	    tit = u"Y%d(m)" % (i+1,)
            lab = Tkinter.Label(fra, text=tit)
            lab.grid(row=i+1, column=4, sticky="w")
	    wid = p_gtkwid.ThanEntry(fra)
	    wid.grid(row=i+1, column=5, sticky="we")
	    val = p_gtkwid.ThanValFloat()
	    self.thanWids.append((key, tit, wid, val))

	fra.columnconfigure(3, weight=1)
	fra.columnconfigure(5, weight=1)


    def fraImage(self, win, ir):
        "Widgets of image postprocessing capabilities."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir+1,))
        lab.grid(row=0, column=0)

        lab = Tkinter.Label(fra, fg=self.colfra, text=u"ΜΕΤΑΤΡΟΠΕΣ ΕΙΚΟΝΑΣ ΧΑΡΤΗ ΜΕΤΑ ΤΗΝ ΟΡΘΟΑΝΑΓΩΓΗ")
        lab.grid(row=0, column=1, columnspan=3, sticky="w")

        key = "chkRGB2Ind"
        tit = u"Αυτόματη μετατροπή RGB σε Indexed Colour"
        wid = p_gtkwid.ThanCheck(fra, text=tit) #, command=self.__korEnable)
        wid.grid(row=1, column=1, columnspan=3, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, wid, val))

        key = "chkGray2BW"
        tit = u"Αυτόματη μετατροπή Gray Scale σε Black/White:"
        wid = p_gtkwid.ThanCheck(fra, text=tit, command=self.__blackEnable)
        wid.grid(row=2, column=1, columnspan=1, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, wid, val))

        key = "entBlack"
        tit = u"όριο μαύρου (%)"
        lab = Tkinter.Label(fra, text=tit)
        lab.grid(row=2, column=2, sticky="w")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=2, column=3, sticky="we")
        val = p_gtkwid.ThanValFloat(0.5, 99.5)
        self.thanWids.append((key, tit, wid, val))

        key = "chkReduce"
        tit = u"Ελάττωση dpi (για μείωση μεγέθους αρχείου εικόνας)"
        wid = p_gtkwid.ThanCheck(fra, text=tit, command=self.__reduceEnable)
        wid.grid(row=3, column=1, columnspan=1, sticky="w")
        val = p_gtkwid.ThanValidator()
        self.thanWids.append((key, tit, wid, val))

        key = "entReduce"
        tit = u"κατά (%)"
        lab = Tkinter.Label(fra, text=tit)
        lab.grid(row=3, column=2, sticky="w")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=3, column=3, sticky="we")
        val = p_gtkwid.ThanValFloat(1.0, 99.0)
        self.thanWids.append((key, tit, wid, val))
        fra.columnconfigure(1, weight=1)


    def validate(self, strict=True, wids=None, values=None):
        "Returns true if the value chosen by the user is valid."
        ret, vs = self.validate2(strict, wids, values)
        if not ret and strict: return ret
        if strict:
            ret1 = self.__saveGan(vs)   #Only when strict, save .gan file and ensure that save succeeded
            if not ret1: return ret1
        self.result = vs
        return ret


    def apply2(self, event=None):
        "Save the data given and run the program."
        from thantkdia import ThanTkWinError
        ret = p_gtkwid.ThanComDialog.apply2(self)
        if not ret: return
#        from thanproortho.thanpropackages.thankaor import ThanKaor
        out = ThanTkWinError(self.thanProj[2], mes="Error messages\n", title="%s Orthomap output" % self.thanProj[0])
        prt = out.thanPrt
        try:
            kaor = ThanKaor()
            fn = kaor.thanMainTcad(self.thanProj, self.result, prt)
        except p_ggen.RecordedError, why:
            p_gtkuti.thanGudModalMessage(self, T["Please correct the errors recorded on output window"],
                                 "%s: Orthomap: %s" % (T["ERROR"], self.thanProj[0]))
            out.thanTkSetFocus()
            self.cancel()
            return
#        except BaseException as e:
        except BaseException, e:
            prt("\n%s: %s" % (e.__doc__, e))
            p_gtkuti.thanGudModalMessage(self, T["PROGRAM ERROR. Details were recorded on output window"],
                                 "%s: Orthomap: %s" % (T["ERROR"], self.thanProj[0]))
            self.cancel()
            out.thanTkSetFocus()
            return
        pdir = fn.abspath().parent
        namebase = fn.namebase
        fw = file(pdir/"mediate.tmp", "w")
        fw.write("1\n%s\n" % namebase)
        fw.close()

        if p_ggen.Pyos.Windows: tria = "tria -p c:\\temp\\%s" % namebase
        else:                   tria = "tria -p /tmp/%s"      % namebase
        apps = "brk2pol", tria, "pol2tri", "c_trp", "c_orthoim"
        try:
            for app in apps:
#                run(app, pdir, out)
                p_grun.runExec(app, pdir, out, pexpectline=True, popen=False, shell=False)
#        except BaseException as e:
        except BaseException, e:
            dl = T["ERROR occured while running external program '%s'"] % app
            prt("\n%s\n%s: %s" % (dl, e.__doc__, e))
            p_gtkuti.thanGudModalMessage(self, "%s\nDetails were recorded on output window" % dl,
                                               "%s: Orthomap: %s" % (T["ERROR"], self.thanProj[0]))
            self.cancel()
            out.thanTkSetFocus()
            return

        pro = self.thanProj[0].parent / self.thanProj[0].namebase
        for ext in "nsy nb1 tri syp".split():            #Remove intermediate files
            try: p_ggen.path("%s.nsy\n" % pro).remove()
            except OSError: pass                         #If one does not exist OK

        if not self.__convert(pdir, namebase):
            self.cancel()
            out.thanTkSetFocus()
            return
        p_gtkuti.thanGudModalMessage(self, T["The image was succesfuly rectified\n"\
                                     "Please notice any warnings on the output window"],
                                     "%s: Orthomap: %s" % (T["Success"], self.thanProj[0]))
        self.ok()
        out.thanTkSetFocus()


    def __convert(self, pdir, namebase):
        "Converts computed image to less heavy modes."
        fimori = pdir / ("a"+namebase+".bmp")
        if not fimori.exists():
            why = T["No image was computed!"]
            p_gtkuti.thanGudModalMessage(self, T["Error while computing image:\n%s"] % why,
                                         "%s: Orthomap: %s" % (T["Error"], self.thanProj[0]))
            return False
        try:
            im = Image.open(fimori)
            im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised
        except IOError, why:
            why = T["No image was computed!"]
            p_gtkuti.thanGudModalMessage(self, T["Error while computing image:\n%s"] % why,
                                         "%s: Orthomap: %s" % (T["Error"], self.thanProj[0]))
            return False
        try:
            mode = im.mode
            b, h = im.size
            del im
            if mode == "RGB" and self.thanValsSaved.chkRGB2Ind:
                fimren = pdir / ("a"+namebase+"rgb.bmp")
                if fimren.exists(): fimren.remove()
                fimori.rename(fimren)
                im = Image.open(fimren)
                im = im.convert("P")
            elif mode == "L" and self.thanValsSaved.chkGray2BW:
                fimren = pdir / ("a"+namebase+"gray.bmp")
                if fimren.exists(): fimren.remove()
                fimori.rename(fimren)
                im = Image.open(fimren)

                threshold = int(256.0*self.thanValsSaved.entBlack/100.0)
                def finv(i):
                    if i >= threshold: return 255
                    else: return 0
                #ftemp = path("q1.bmp")
                #try: ftemp.remove()
                #except: pass

                #prg("    pre-saving image..")     # for some reason, saving image before the invert..
                #im.save(ftemp)                    # .. causes invert to succeed
                im = im.point(finv)
                im = im.convert("1")
	    elif self.thanValsSaved.chkReduce:
                fimren = pdir / ("a"+namebase+"full.bmp")
	        if fimren.exists(): fimren.remove()
	        fimori.rename(fimren)
	        im = Image.open(fimren)
	    else:
	        return True
	    if self.thanValsSaved.chkReduce:
	        per = 1.0 - self.thanValsSaved.entReduce/100.0
	        b = max((int(b*per), 10))
	        h = max((int(h*per), 10))
	        im = im.resize((b, h))
            im.save(fimori)
	except IOError, why:
            p_gtkuti.thanGudModalMessage(self, T["Error while converting image:\n%s"] % why,
	                             "%s: Orthomap: %s" % (T["Error"], self.thanProj[0]))
	    return False
	except Exception, why:
            p_gtkuti.thanGudModalMessage(self, T["Error while converting image:\n%s"] % why,
	                             "%s: Orthomap: %s" % (T["Error"], self.thanProj[0]))
	    return False
	return True


    def __validateReadGan(self):
        "Read values from file; if not warn the user."
	proj = self.thanProj
	fn = proj[0].parent / (proj[0].namebase + ".gan")
	if not fn.exists():
	    p_gtkuti.thanGudModalMessage(self,
	        "'%s' does not exist.\nDefault values will be used." % p_gtkuti.thanAbsrelPath(fn),
	        T["Information"])
	    return False
	elif not fn.isfile():
	    p_gtkuti.thanGudModalMessage(self,
	        "'%s' can not be accessed.\nDefault values will be used." % p_gtkuti.thanAbsrelPath(fn),
	        T["Warning"])
	    return False

	try:
	    fr = file(fn)
	    com = p_ggen.Struct()
	    self.__readGen(fr, com)
	    fr.close()
        except (IOError,ValueError), why:  # Open error, conversion to float error, file too short
	    why = u"%s\n\n%s" % (why, "Default values will be used.")
	    p_gtkuti.thanGudModalMessage(self, why, p_gtkuti.thanAbsrelPath(fn)+T[": Read failed"])   # (Gu)i (d)ependent
	    return False

	for a in _widCoefs[1:]: setattr(com, a, getattr(self.thanValsInit, a))
	if com.chkEgsa:
	    if not self.__validateReadCoefs(com.entFilsnt, com):
	        com.chkEgsa = False

        com.chkRGB2Ind = True
        com.chkGray2BW = True
        com.entBlack = 50.0
        com.chkReduce = False
        com.entReduce = 50.0

        self.thanValsInit = com
        self.thanSet(self.thanValsInit)
        self.thanValsSaved = copy.deepcopy(self.thanValsInit)
        return True


    def __readGen(self, fr, com):
        "Read general data."
        import p_gfil
        DOUBMIN=1.0e-10; DOUBMAX=1.0e10
        f = p_gfil.Datlin(fr)
        f.datCom('ΜΕΤΑΤΡΟΠΗ HATT')
        com.chkEgsa = f.datYesno()

        if com.chkEgsa:
            f.datCom('ΑΡΧΕΙΟ ΣΥΝΤΕΛΕΣΤΩΝ')
            com.entFilsnt = p_ggen.path(f.datStr()).expand()
        elif f.datCom('ΑΡΧΕΙΟ ΣΥΝΤΕΛΕΣΤΩΝ', fail=False):
            com.entFilsnt = p_ggen.path(f.datStr()).expand()
        else:
            com.entFilsnt = "<undefined>"
            f.datLinbac()

        f.datCom('ΒΗΜΑ ΚΑΝΑΒΟΥ')
        com.entStepGr = f.datFloatR(DOUBMIN, DOUBMAX)
        try: com.entStepPap = f.datFloatR(DOUBMIN, DOUBMAX)
        except IOError: com.entStepPap = 100.0

        if f.datCom('ΑΝΑΛΥΣΗ ΕΙΚΟΝΑΣ', fail=False):
            print
            f.wa("Η εντολή 'ΑΝΑΛΥΣΗ ΕΙΚΟΝΑΣ' δεν είναι πια απαραίτητη\n"\
                 "και δεν λαμβάνεται υπόψη.")
#            com.dpi = f.datFloatR(DOUBMIN, DOUBMAX)
        else:
            f.datLinbac()

        f.datCom('ΣΥΝΤΕΤΑΓΜΕΝΕΣ ΑΡΧΗΣ')
        com.entXori = f.datFloat()
        com.entYori = f.datFloat()

        com.chkKor = False
        com.entKorX1 = com.entKorX2 = com.entKorX3 = com.entKorX4 = 0.0
        com.entKorY1 = com.entKorY2 = com.entKorY3 = com.entKorY4 = 0.0
        if f.datLin(failoneof=False):
            if f.datComC('ΣΥΝΤΕΤΑΓΜΕΝΕΣ ΚΟΡΥΦΩΝ', fail=False):
                com.chkKor = True
                com.entKorX1 = f.datFloat(); com.entKorY1 = f.datFloat()
                f.datLin(); com.entKorX2 = f.datFloat(); com.entKorY2 = f.datFloat()
                f.datLin(); com.entKorX3 = f.datFloat(); com.entKorY3 = f.datFloat()
                f.datLin(); com.entKorX4 = f.datFloat(); com.entKorY4 = f.datFloat()


    def __validateReadCoefs(self, fn, com=None):
        "Reads coefficients from a file."
	if not fn: return False
	try:
	    fr = file(fn)
	    vs = [float(fr.next().strip().replace("d", "e").replace("D", "e")) for i in xrange(12)]
	    fr.close()
        except (IOError,ValueError,StopIteration), why:  # Open error, conversion to float error, file too short
	    p_gtkuti.thanGudModalMessage(self, why, "%s: %s" % (p_gtkuti.thanAbsrelPath(fn), T["Read failed"]))   # (Gu)i (d)ependent
	    return False
        for a,v1 in itertools.izip(_widCoefs[1:], vs):
	    if com == None:
	        wid = getattr(self, a)
	        if type(v1) == FloatType: v1 = str(v1)
	        wid.thanSet(v1)
	    else:
	        setattr(com, a, v1)
	return True


    def __saveGan(self, r):
        "Saves information to .gan file."
	proj = self.thanProj
	fn = proj[0].parent / (proj[0].namebase + ".gan")
	try:
	    fw = open(fn, "w")
	    if r.chkEgsa: no = "ΝΑΙ"
	    else:         no = "ΟΧΙ"
	    fw.write("ΜΕΤΑΤΡΟΠΗ HATT ΣΕ ΕΓΣΑ87      : %s\n" % no)
            fw.write("ΑΡΧΕΙΟ ΣΥΝΤΕΛΕΣΤΩΝ ΜΕΤΑΤΡΟΠΗΣ : %s\n" % r.entFilsnt)
	    fw.write("\n")
            fw.write("ΒΗΜΑ ΚΑΝΑΒΟΥ (m)        : %.3f  %.3f\n" % (r.entStepGr, r.entStepPap))
            fw.write("ΣΥΝΤΕΤΑΓΜΕΝΕΣ ΑΡΧΗΣ (m) : %.3f  %.3f\n" % (r.entXori, r.entYori))
	    fw.write("\n")
            if r.chkKor: no = ""
	    else:        no = "#"
            fw.write('%sΣΥΝΤΕΤΑΓΜΕΝΕΣ ΚΟΡΥΦΩΝ: %.3f  %.3f\n' % (no, r.entKorX1, r.entKorY1))
            fw.write('%s                       %.3f  %.3f\n' % (no, r.entKorX2, r.entKorY2))
            fw.write('%s                       %.3f  %.3f\n' % (no, r.entKorX3, r.entKorY3))
            fw.write('%s                       %.3f  %.3f\n' % (no, r.entKorX4, r.entKorY4))
            fw.close()
        except (IOError,), why:
            p_gtkuti.thanGudModalMessage(self, why, p_gtkuti.thanAbsrelPath(fn)+T[": Save failed"])   # (Gu)i (d)ependent
            return False
        return True


    def destroy(self, event=False):
        "Breaks circular references."
        del self.butCoef
        p_gtkwid.ThanComDialog.destroy(self)
