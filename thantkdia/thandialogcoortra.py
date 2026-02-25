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
import p_gtkuti, p_gtkwid, p_ggen
#from thanvar import ThanLayerError, thanfiles, Win32
#from thansupport import thanToplayerCurrent
from thantrans import T


_widCoefs = "entFilsnt entA0 entA1 entA2 entA3 entA4 entA5 entB0 entB1 entB2 entB3 entB4 entB5".split()


class ThanCoorTransf(p_gtkuti.ThanDialog):
    "Dialog for coordinate transformation computation."

    def __init__(self, master, vals=None, cargo=None, *args, **kw):
        "Extract initial rectification parameters."
	self.thanValsInit = vals           # This is structure not a scalar
	self.thanProj = cargo
	kw.setdefault("title", T[u"ΠΡΟΓΡΑΜΜΑ ΜΕΤΑΤΡΟΠΗΣ ΣΥΝΤΕΤΑΓΜΕΝΩΝ"])
	kw.setdefault("buttonlabels", ("Save and Exit", "Cancel", "Save and Run"))
	p_gtkuti.ThanDialog.__init__(self, master, buttonlabels=3, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()
        v.chkEgsa = False
	v.entFilsnt = "<Undefined>"
        v.entA0 = v.entA1 = v.entA2 = v.entA3 = v.entA4 = v.entA5 = 1.0
        v.entB0 = v.entB1 = v.entB2 = v.entB3 = v.entB4 = v.entB5 = 1.0
        v.entStepGr = 500.0; v.entStepPap = 100.0
        v.entXori = v.entYori = 0.0
        v.chkKor = True
        v.entKorX1 = v.entKorX2 = v.entKorX3 = v.entKorX4 = 0.0
        v.entKorY1 = v.entKorY2 = v.entKorY3 = v.entKorY4 = 0.0
        return v

    def thanSet(self, vs):
        "Set new values to the widgets."
	stat = Tkinter.NORMAL
        for (key,tit,wid,vld) in self.thanWids:
	    v = getattr(vs, key)
	    if type(v) == FloatType: v = str(v)
	    wid.config(state=stat) # All widgets must be enabled..
	    wid.thanSet(v)         # ..to change their values
        self.__egsaEnable()
	self.__korEnable()

    def __egsaEnable(self, evt=None):
        "Enable or disable the EGSA87 widgets."
	if self.chkEgsa.thanGet(): stat = Tkinter.NORMAL
	else:                      stat = Tkinter.DISABLED
	self.entFilsnt.config(state=stat)
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
	self.thanWids = []
	self.colfra = "blue"
##        self.option_add("*font", _fo)
        self.fraDrawings(win, 0)
#	self.fraMetEgsa(win, 1)
#	self.fraStep(win, 2)
#	self.fraOrigin(win, 3)
#	self.fraKor(win, 4)
	win.columnconfigure(0, weight=1)

        for (key,tit,wid,vld) in self.thanWids:
	    setattr(self, key, wid)
	return

	if self.thanValsInit == None: self.thanValsInit = self.thanValsDef()
	self.thanValsSaved = copy.deepcopy(self.thanValsInit)
	self.thanSet(self.thanValsInit)
 	self.after(200, self.__validateReadGan)

    def fraDrawings(self, win, ir):
        "Quick process buttons."
        fra = Tkinter.Frame(win, bd=3, relief=Tkinter.RIDGE)
	fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = Tkinter.Label(fra, fg=self.colfra, text="%d."%(ir+1,))
        lab.grid(row=0, column=0)
        lab = Tkinter.Label(fra, anchor="w", fg=self.colfra, text=u"ΕΠΙΛΟΓΗ ΣΧΕΔΙΩΝ:")
        lab.grid(row=0, column=1, sticky="w")

        frc = Tkinter.Frame(fra)
	frc.grid(row=1, column=1, columnspan=1, sticky="we")
	tit = u"ΠΡΩΤΕΥΟΝ ΣΧΕΔΙΟ"
        lab = Tkinter.Label(frc, anchor="w", text=tit)
        lab.grid(row=0, column=0, sticky="we")
	key = "choDra"
        wid = p_gtkwid.ThanChoice(frc, labels=["dra", "drb", "drc"], width=20, relief=Tkinter.RAISED, anchor="w")
        wid.grid(row=0, column=1, sticky="we")
	val = p_gtkwid.ThanValidator()
	self.thanWids.append((key, tit, wid, val))

	tit = u"ΔΕΥΤΕΡΕΥΟΝ ΣΧΕΔΙΟ"
        lab = Tkinter.Label(frc, anchor="w", text=tit)
        lab.grid(row=0, column=2, sticky="we")
	key = "choDrb"
        wid = p_gtkwid.ThanChoice(frc, labels=["dra", "drb", "drc"], width=20, relief=Tkinter.RAISED, anchor="w")
        wid.grid(row=0, column=3, sticky="we")
	val = p_gtkwid.ThanValidator()
	self.thanWids.append((key, tit, wid, val))


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
	val = p_gtkwid.ThanValidator()
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
#	    assert type(val) == float, "How did other types sneak here?"
	    setattr(v, a, val)

	dl = ThanNewCoefs(self, vals=v)
	res = dl.result
	if res == None: return

	for a in _widCoefs:
	    wid = getattr(self, a)
	    val = getattr(res, a)
	    print a, ":", wid.thanGet(), "->", val
	    wid.config(state=Tkinter.NORMAL)
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


    def validate(self, strict=True):
        "Returns true if the value chosen by the user is valid."
#	thc = self.__updateChosen()
        ret = True
        vs = p_ggen.Struct()
        for key,tit,wid,vld in self.thanWids:
	    v1 = vld.thanValidate(wid.thanGet())
            if v1 == None:
	      ret = False
	      if strict:
	        tit = u'"%s":\n%s' % (tit, vld.thanGetErr())
                p_gtkuti.thanGudModalMessage(self, tit, T["Error in data"])
                self.initial_focus = wid
                return ret
	      else:
	        v1 = getattr(self.thanValsInit, key)
	    setattr(vs, key, v1)
        self.result = vs
	if strict:
	    ret = self.__saveGan()
        return ret


    def cancel(self, *args):
        "Ask before cancel."
        p_gtkuti.ThanDialog.cancel(self, *args)
	return
	if not self.validate(strict=False):                       # If anything is wrong, then it must have been changed
	    print "cancel: not validated"
	    a = p_gtkuti.thanGudAskOkCancel(self, T["Data modified, OK to cancel?"], T["Warning"])
            if not a: return        # Cancel was stopped
	elif self.result.__dict__ != self.thanValsSaved.__dict__: # If anything is wrong, then it must have been changed
	    print "cancel: __dict__ not the same"
	    for a,v in self.thanValsSaved.__dict__.iteritems():
	        v1 = self.result.__dict__[a]
	        print "%15s: saved=%15s  result=%15s: %s" % (a,v,v1,v==v1)
	    for a,v1 in self.result.__dict__.iteritems():
	        v = self.thanValsSaved.__dict__[a]
	        print "%15s: saved=%15s  result=%15s: %s" % (a,v,v1,v==v1)
	    a = p_gtkuti.thanGudAskOkCancel(self, T["Data modified, OK to cancel?"], T["Warning"])
            if not a: return        # Cancel was stopped
        p_gtkuti.ThanDialog.cancel(self, *args)


    def apply2(self, *args):
        "Save the data given and run the program."
	ret = p_gtkuti.ThanDialog.apply2(self)
	if not ret: return
	self.thanValsSaved = self.result
#       run program
	from thanpackages.thankaor import kaor
	from thantkwinerror import ThanTkWinError
	out = ThanTkWinError(self.thanProj[2], mes="Error messages\n", title="%s Orthomap output" % self.thanProj[0])
	prt = out.thanPrt
	try:
	    fn = kaor.thanMainTcad(self.thanProj, self.result, prt)
	except p_ggen.RecordedError, why:
            p_gtkuti.thanGudModalMessage(self, T["Please correct the errors recorded on output window"],
	                                 "%s: Orthomap: %s" % (T["ERROR"], self.thanProj[0]))
	    out.thanTkSetFocus()
	    return
	except AssertionError, why:
            prt("\nAssertion error: %s" % why)
            p_gtkuti.thanGudModalMessage(self, T["PROGRAM ERROR. Details were recorded on output window"],
	                                 "%s: Orthomap: %s" % (T["ERROR"], self.thanProj[0]))
#	    raise
	    out.thanTkSetFocus()
	    return
	except Exception, why:
	    prt("\n%s" % why)
            p_gtkuti.thanGudModalMessage(self, T["PROGRAM ERROR. Details were recorded on output window"],
	                                 "%s: Orthomap: %s" % (T["ERROR"], self.thanProj[0]))
#	    raise
	    out.thanTkSetFocus()
	    return
#          fw=open('mediate.sh', 'w')
#          fw.write('brk2pol\n')
#          fw.write('echo   \\* ΠΡΟΓΡΑΜΜΑ ΤΡΙΓΩΝΟΠΟΙΗΣΗΣ\n')
#          fw.write('tria -p /tmp/%s >/dev/null\n' % pro)
#          fw.write('#\n')
#          fw.write('pol2tri\n')
#          fw.write('trp\n')
#          fw.write('orthoim\n')
#          fw.write('#\n')
#          fw.write('rm %s.nsy\n' % pro)
#          fw.write('rm %s.nb1\n' % pro)
#          fw.write('rm %s.tri\n' % pro)
#          fw.write('rm %s.syp\n' % pro)
        from subprocess import Popen, PIPE
	pdir = fn.abspath().parent
	namebase = fn.namebase
	prt("\npdir=%s   namebase=%s" % (pdir, namebase))
	fw = file(pdir/"mediate.tmp", "w")
	fw.write("1\n%s\n" % namebase)
	fw.close()

        togi = p_ggen.togi
        try:
	  app = "brk2pol"
          p1 = Popen(app, stdout=PIPE, cwd=pdir)
          for dl in p1.stdout:
            prt(togi(dl.strip()))

          app = "tria"
          if p_ggen.Pyos.Windows:
              p1 = Popen([app, "-p", "c:\\temp\\%s" % namebase], stdout=PIPE, cwd=pdir)
	  else:
              p1 = Popen([app, "-p", "/tmp/%s" % namebase], stdout=PIPE, cwd=pdir)
          for dl in p1.stdout:
            prt(togi(dl.strip()))

          app = "pol2tri"
          p1 = Popen(app, stdout=PIPE, cwd=pdir)
          for dl in p1.stdout:
            prt(togi(dl.strip()))

          app = "trp"
          p1 = Popen(app, stdout=PIPE, cwd=pdir)
          for dl in p1.stdout:
            prt(togi(dl.strip()))

          app = "orthoim9"
          p1 = Popen(app, stdout=PIPE, cwd=pdir)
          for dl in p1.stdout:
            prt(togi(dl.strip()))
	except BaseException, why:
	    dl = T["ERROR occured while running external program '%s'"] % app
	    prt("\n%s\n%s" % (dl, why))
            p_gtkuti.thanGudModalMessage(self, "%s\nDetails were recorded on output window" % dl,
	                                 "%s: Orthomap: %s" % (T["ERROR"], self.thanProj[0]))
#	    raise
	    out.thanTkSetFocus()
	    return

        tobw = True
	tohalf = False
        if tobw:
	  try:
	    fimbw   = pdir / ("a"+namebase+".bmp")
	    fimgray = pdir / ("a"+namebase+"gray.bmp")
	    if fimgray.exists(): fimgray.remove()
	    fimbw.rename(fimgray)
	    im = Image.open(fimgray)
	    im = im.convert("1")
	    im.save(fimbw)
	  except IOError, why:
            p_gtkuti.thanGudModalMessage(self, T["Error while converting to b/w:\n%s"] % why,
	                             "%s: Orthomap: %s" % (T["Error"], self.thanProj[0]))
#	    raise
	    return
	  except Exception, why:
            p_gtkuti.thanGudModalMessage(self, T["Error while converting to b/w:\n%s"] % why,
	                             "%s: Orthomap: %s" % (T["Error"], self.thanProj[0]))
#	    raise
	    return

        elif tohalf:
	  try:
	    fimbw   = pdir / ("a"+namebase+".bmp")
	    fimgray = pdir / ("a"+namebase+"full.bmp")
	    fimbw.rename(fimgray)
	    im = Image.open(fimgray)
	    b,h = im.size
	    im = im.resize((b/2, h/2))
	    im.save(fimbw)
	  except IOError, why:
            p_gtkuti.thanGudModalMessage(self, T["Error while resizing image:\n%s"] % why,
	                             "%s: Orthomap: %s" % (T["Error"], self.thanProj[0]))
	    return
	  except Exception, why:
            p_gtkuti.thanGudModalMessage(self, T["Error while resizing image:\n%s"] % why,
	                             "%s: Orthomap: %s" % (T["Error"], self.thanProj[0]))
	    return

        p_gtkuti.thanGudModalMessage(self, T["The image was succesfuly rectified\n"\
	                             "Please notice any warnings on the output window"],
	                             "%s: Orthomap: %s" % (T["Success"], self.thanProj[0]))
	self.ok()


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
	    com.entFilsnt = f.datStr()
        elif f.datCom('ΑΡΧΕΙΟ ΣΥΝΤΕΛΕΣΤΩΝ', fail=False):
	    com.entFilsnt = f.datStr()
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
	    p_gtkuti.thanGudModalMessage(self, why, p_gtkuti.thanAbsrelPath(fn)+T[": Read failed"])   # (Gu)i (d)ependent
	    return False
        for a,v1 in itertools.izip(_widCoefs[1:], vs):
	    if com == None:
	        wid = getattr(self, a)
	        if type(v1) == FloatType: v1 = str(v1)
	        wid.thanSet(v1)
	    else:
	        setattr(com, a, v1)
	return True


    def __saveGan(self):
        "Saves information to .gan file."
	proj = self.thanProj
	fn = proj[0].parent / (proj[0].namebase + ".gan")
	try:
	    fw = open(fn, "w")
            r = self.result
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
        except (IOError,), why:  # ImportError happens if BZ2file can not import its base class
	    p_gtkuti.thanGudModalMessage(self, why, p_gtkuti.thanAbsrelPath(fn)+T[": Save failed"])   # (Gu)i (d)ependent
	    return False
	return True


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
        for (key,tit,wid,vld) in self.thanWids:
	    delattr(self, key)
        del self.thanProj, self.thanWids, self.butCoef, self.thanValsInit, self.thanValsSaved
	p_gtkuti.ThanDialog.destroy(self)


    def __del__(self):
        print "ThanMaprect ThanDialog", self, "dies.."



##############################################################################
##############################################################################

class ThanNewCoefs(p_gtkuti.ThanDialog):
    "Dialog to get the transfromation coefficients."

    def __init__(self, master, vals=None, cargo=None, *args, **kw):
        "Extract initial rectification parameters."
	self.thanValsInit = vals           # This is structure not a scalar
	self.thanCargo = cargo
	kw.setdefault("title", T[u"ΕΙΣΑΓΩΓΗ ΣΥΝΤΕΛΕΣΤΩΝ ΜΕΤΑΤΡΟΠΗΣ"])
	p_gtkuti.ThanDialog.__init__(self, master, *args, **kw)


    def thanSet(self, vs):
        "Set new values to the widgets."
        for (key,tit,wid,vld) in self.thanWids:
	    v = getattr(vs, key)
	    wid.thanSet(str(v))


    def body(self, win):
	self.thanWids = []
	self.colfra = "blue"
	self.fraMetEgsa(win)

        for (key,tit,wid,vld) in self.thanWids:
	    setattr(self, key, wid)

	self.thanValsSaved = copy.deepcopy(self.thanValsInit)
	self.thanSet(self.thanValsInit)


    def fraMetEgsa(self, fra):
        "Coeeficients' widgets."
        frb = Tkinter.Frame(fra)
	frb.grid(row=2, column=1, columnspan=3, sticky="we")
	for i in xrange(6):
	    tit = u"A"+str(i)
	    key = "ent" + tit
            lab = Tkinter.Label(frb, text=tit)
            lab.grid(row=i, column=0, sticky="w")
	    wid = p_gtkwid.ThanEntry(frb)
	    wid.grid(row=i, column=1, sticky="we")
	    val = p_gtkwid.ThanValFloatFortran()
	    self.thanWids.append((key, tit, wid, val))

	    tit = u"B"+str(i)
	    key = "ent" + tit
            lab = Tkinter.Label(frb, text=tit)
            lab.grid(row=i, column=2, sticky="w")
	    wid = p_gtkwid.ThanEntry(frb)
	    wid.grid(row=i, column=3, sticky="we")
	    val = p_gtkwid.ThanValFloatFortran()
	    self.thanWids.append((key, tit, wid, val))
        frb.columnconfigure(1, weight=1)
        frb.columnconfigure(3, weight=1)


    def validate(self, strict=True):
        "Returns true if the value chosen by the user is valid."
#	thc = self.__updateChosen()
        ret = True
        vs = p_ggen.Struct()
        for key,tit,wid,vld in self.thanWids:
	    v1 = vld.thanValidate(wid.thanGet())
	    print "validate", key, ":", v1, type(v1)
            if v1 == None:
	        ret = False
	        if strict:
	            tit = u'"%s":\n%s' % (tit, vld.thanGetErr())
                    p_gtkuti.thanGudModalMessage(self, tit, T["Error in data"])
                    self.initial_focus = wid
                    return ret
	        else:
	            v1 = getattr(self.thanValsInit, key)
	    setattr(vs, key, v1)
        vs.entFilsnt = self.thanValsSaved.entFilsnt
        self.result = vs
	if not strict: return ret
        v1 = self.__saveCoefs()           # Try to save coefficients
	if v1 == None: return False
        vs.entFilsnt = v1
	return ret


    def __saveCoefs(self):
        "Saves coefficients to a file."
	fn = self.thanValsSaved.entFilsnt
        fildir = thanfiles.getFiledir()
        while True:
            fn = p_gtkuti.thanGudGetSaveFile(self, "*.snt", T["Save transformation coefficients to a file"],
	        initialdir=fildir)
            if fn == None: return None  # Save cancelled
	    fn = p_ggen.path(fn)
	    try:
	        fw = open(fn, "w")
		for a in _widCoefs[1:]:
		    print a, ":", getattr(self.result, a), type(getattr(self.result, a))
		    fw.write("%s\n" % getattr(self.result, a))
		fw.close()
            except (IOError,), why:  # ImportError happens if BZ2file can not import its base class
	        p_gtkuti.thanGudModalMessage(self, why, p_gtkuti.thanAbsrelPath(fn)+T[": Save failed"])   # (Gu)i (d)ependent
            else: break
	return fn


    def cancel(self, *args):
        "Ask before cancel."
	if not self.validate(strict=False):                       # If anything is wrong, then it must have been changed
	    a = p_gtkuti.thanGudAskOkCancel(self, T["Data modified, OK to cancel?"], T["Warning"])
            if not a: return        # Cancel was stopped
	elif self.result.__dict__ != self.thanValsSaved.__dict__: # If anything is wrong, then it must have been changed
	    a = p_gtkuti.thanGudAskOkCancel(self, T["Data modified, OK to cancel?"], T["Warning"])
            if not a: return        # Cancel was stopped
        p_gtkuti.ThanDialog.cancel(self, *args)


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
        for (key,tit,wid,vld) in self.thanWids:
	    delattr(self, key)
        del self.thanCargo, self.thanWids, self.thanValsInit, self.thanValsSaved
	p_gtkuti.ThanDialog.destroy(self, *args)


    def __del__(self):
        print "ThanNewCoefs ThanDialog", self, "dies.."


##############################################################################
##############################################################################

if __name__ == "__main__":
    root = Tkinter.Tk()
    win = ThanCoorTransf(root, None)
    print win.result.anal()
