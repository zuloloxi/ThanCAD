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

This dialog performs photogrammetric interior orientation of a metric image.
"""
import sys, copy
import tkinter
from math import sqrt, fabs
from tkinter.messagebox import ERROR
import p_gtkwid, p_ggen, p_gmath
import thandr
from thanopt import thancadconf
from thantrans import Tphot, T
from thanopt import thancadconf
from thanvar import Canc
#T = p_gtkwid.Translation(dict(__TRANSLATION__=("en", "EN", "en", "EN")))  ##############


mm = p_gtkwid.thanGudModalMessage


class ThanInterior(p_gtkwid.ThanComDialog):
    "Dialog for photogrammetric interior orientation of a metric image."

    def __init__(self, master, vals=None, cargo=None, translation=None, other=None, *args, **kw):
        "Extract initial rectification parameters."
        kw.setdefault("title", Tphot["Photogrammetric Interior Orientation"])
        self.other = other
        p_gtkwid.ThanComDialog.__init__(self, master, vals, cargo, translation, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        assert 0, "This function should never be called!"


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.thanFloatMenu = None       #A floating Menu for fiducial digitization
        self.fraImage(win, 1)
        self.fraFid(win, 2)
        self.fraComp(win, 3)


    def fraImage(self, win, ir):
        "Image parameters."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["IMAGE PARAMETERS:"])
        lab.grid(row=0, column=1, columnspan=4, sticky="w")

        im = self.other.image
        lab = tkinter.Label(fra, text=T["Image file"])
        lab.grid(row=1, column=1, sticky="e")
        lab = p_gtkwid.ThanLabel(fra, text=im.filnam.basename(), width=20)
        lab.grid(row=1, column=2, sticky="we")

        cam = self.other.camera
        lab = tkinter.Label(fra, text=Tphot["Camera Name"])
        lab.grid(row=2, column=1, sticky="e")
        lab = p_gtkwid.ThanLabel(fra, text=cam.name, width=20)
        lab.grid(row=2, column=2, sticky="we")

        lab = tkinter.Label(fra, text=Tphot["Focus Length c (mm)"])
        lab.grid(row=2, column=3, sticky="e")
        lab = p_gtkwid.ThanLabel(fra, text="%.3f" % cam.focus, width=20)
        lab.grid(row=2, column=4, sticky="we")

        fra.columnconfigure(2, weight=1)
        fra.columnconfigure(4, weight=1)


    def fraFid(self, win, ir):
        "Show the fiducials and help digitize."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["FIDUCIALS:"])
        lab.grid(row=0, column=1, columnspan=6, sticky="w")

        cam = self.other.camera
        lab = tkinter.Label(fra, text=Tphot["Camera X (mm)"])
        lab.grid(row=1, column=2, sticky="w")
        lab = tkinter.Label(fra, text=Tphot["Camera Y (mm)"])
        lab.grid(row=1, column=3, sticky="w")
        lab = tkinter.Label(fra, text=Tphot["Photo x (pixel)"])
        lab.grid(row=1, column=4, sticky="w")
        lab = tkinter.Label(fra, text=Tphot["Photo y (pixel)"])
        lab.grid(row=1, column=5, sticky="w")
        lab = tkinter.Label(fra, text=Tphot["Reject"])
        lab.grid(row=1, column=6, sticky="w")
        i = 2
        n = len(cam.x)
        self.labXpix = [None]*n
        self.labYpix = [None]*n
        self.butFid = [None]*n
        self.thanChkReject = [None]*n
        val = p_gtkwid.ThanValFloatBlank()
        val2 = p_gtkwid.ThanValidator()
        for ifid in range(n):
            fun = lambda evt, ifid=ifid: self.__onClickr(evt, ifid)
            but = self.butFid[ifid] = p_gtkwid.ThanButton(fra, text="%d " % (ifid+1,), bd=2,
                                      command=lambda ifid=ifid: self.__onClickr(None, ifid))
            but.grid(row=i+ifid, column=1)
            but.bind("<Button-3>", fun)

            lab = p_gtkwid.ThanLabel(fra, text="%.3f" % cam.x[ifid], width=14)
            lab.grid(row=i+ifid, column=2, sticky="we")
            lab.bind("<Button-3>", fun)

            lab = p_gtkwid.ThanLabel(fra, text="%.3f" % cam.y[ifid], width=14)
            lab.grid(row=i+ifid, column=3, sticky="we")
            lab.bind("<Button-3>", fun)

            lab = self.labXpix[ifid] = p_gtkwid.ThanLabel(fra, text="", width=14)
            lab.grid(row=i+ifid, column=4, sticky="we")
            lab.bind("<Button-3>", fun)
            self.thanWids.append(("labXpix%d" % (ifid+1,), "", lab, val))

            lab = self.labYpix[ifid] = p_gtkwid.ThanLabel(fra, text="", width=14)
            lab.grid(row=i+ifid, column=5, sticky="we")
            lab.bind("<Button-3>", fun)
            self.thanWids.append(("labYpix%d" % (ifid+1,), "", lab, val))

            chk = self.thanChkReject[ifid] = p_gtkwid.ThanCheck(fra, text="",
                  command=lambda ifid=ifid: self.__reject(ifid, "toggle"))
            chk.grid(row=i+ifid, column=6)
            chk.bind("<Button-3>", fun)
            self.thanWids.append(("thanChkReject%d" % (ifid+1,), "", chk, val2))

        for i in 2,3,4,5: fra.columnconfigure(i, weight=1)


    def fraComp(self, win, ir):
        "Computation - errors."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["COMPUTATION:"])
        lab.grid(row=0, column=1, columnspan=3, sticky="w")

        cam = self.other.camera
        lab = tkinter.Label(fra, text=Tphot["Computed X (mm)"])
        lab.grid(row=1, column=2, sticky="w")
        lab = tkinter.Label(fra, text=Tphot["Computed Y (mm)"])
        lab.grid(row=1, column=3, sticky="w")
        lab = tkinter.Label(fra, text=Tphot["Error X (mm)"])
        lab.grid(row=1, column=4, sticky="w")
        lab = tkinter.Label(fra, text=Tphot["Error Y (mm)"])
        lab.grid(row=1, column=5, sticky="w")
        i = 2
        n = len(cam.x)
        self.labXcom = [None]*n
        self.labYcom = [None]*n
        self.labXer = [None]*n
        self.labYer = [None]*n
        for ifid in range(n):
            lab = tkinter.Label(fra, text="%d " % (ifid+1,))
            lab.grid(row=i+ifid, column=1)
            lab = self.labXcom[ifid] = p_gtkwid.ThanLabel(fra, text="", width=14)
            lab.grid(row=i+ifid, column=2, sticky="we")
            lab = self.labYcom[ifid] = p_gtkwid.ThanLabel(fra, text="", width=14)
            lab.grid(row=i+ifid, column=3, sticky="we")
            lab = self.labXer[ifid] = p_gtkwid.ThanLabel(fra, text="", width=14)
            lab.grid(row=i+ifid, column=4, sticky="we")
            lab = self.labYer[ifid] = p_gtkwid.ThanLabel(fra, text="", width=14)
            lab.grid(row=i+ifid, column=5, sticky="we")
        i += n
        but = p_gtkwid.ThanButton(fra, text=Tphot["Compute"], bd=2, command=self.__compute)
        but.grid(row=i, column=2, pady=5)
        lab = tkinter.Label(fra, text=Tphot["Overall error"])
        lab.grid(row=i, column=4, sticky="e")
        lab = self.labEr = p_gtkwid.ThanLabel(fra, text="", width=14)
        lab.grid(row=i, column=5, sticky="we")

        for i in 2,3,4,5: fra.columnconfigure(i, weight=1)


    def __onClickr(self, event, ifid):
        "Well, here is what should be done when right mouse clicks."
        if self.thanFloatMenu is not None and self.thanFloatMenu.winfo_ismapped():
            self.thanFloatMenu.unpost()
        if event is None:
            w = self.butFid[ifid]
            x, y = w.winfo_rootx(), w.winfo_rooty()
        else:
            x, y = event.x_root, event.y_root
        self.thanFloatMenu = self.__createFloatMenu(ifid)
        self.thanFloatMenu.post(x, y)


    def thanSet(self, vs):
        "Set new values to the widgets."
        p_gtkwid.ThanComDialog.thanSet(self, vs)
        self.__disable()


    def __disable(self):
        "Disable all rejected."
        for ifid in range(len(self.other.camera.x)):
            if self.thanChkReject[ifid].thanGet():
                self.entXpix[ifid].config(state=tkinter.DISABLED)
                self.entYpix[ifid].config(state=tkinter.DISABLED)


    def __createFloatMenu(self, ifid):
        "A menu with action for the fiducials."
        m = tkinter.Menu(self, tearoff=False)
        m.add_command(label=Tphot["Move to and digitize fiducial"], command=lambda ifid=ifid: self.__digfid(ifid, go=True))
        m.add_command(label=Tphot["Digitize fiducial"],             command=lambda ifid=ifid: self.__digfid(ifid, go=False))
        m.add_command(label=Tphot["Clear pixel coordinates"],       command=lambda ifid=ifid: self.__clear(ifid))
        m.add_command(label=Tphot["Mark as invalid"],               command=lambda ifid=ifid: self.__reject(ifid, "reject"))
        m.add_command(label=Tphot["Accept as valid"],               command=lambda ifid=ifid: self.__reject(ifid, "accept"))
        return m


    def __reject(self, ifid, action):
        "Reject, accept, toogle, but do not delete, the pixel coordinates of a fiducial."
        if action == "toggle":
            self.update_idletasks()   #Give a chance to check button to change state
            v = self.thanChkReject[ifid].thanGet()
        elif action == "reject":
            v = True
            self.thanChkReject[ifid].thanSet(v)
        elif action == "accept":
            v = False
            self.thanChkReject[ifid].thanSet(v)
        else:
            assert 0, "toggle, reject or accept was expected"
        if v: stat = tkinter.DISABLED
        else: stat = tkinter.NORMAL
        self.labXpix[ifid].config(state=stat)
        self.labYpix[ifid].config(state=stat)
        self.update_idletasks()
        self.other.tra = None      #Data changed -> transformation invalid


    def __clear(self, ifid):
        "Clear pixels coordinates."
        self.__reject(ifid, "accept")
        lx = self.labXpix[ifid]
        ly = self.labYpix[ifid]
        if lx.thanGet().strip() != "" or ly.thanGet().strip() != "":
            self.other.tra = None      #Data changed -> transformation invalid
            self.__delpoint(ifid)
        lx.thanSet("")
        ly.thanSet("")


    def __delpoint(self, ifid):
        "Delete a point from the canvas and newelems."
        elems = self.other.newelems
        if ifid not in elems: return
        proj = self.thanProj
        proj[1].thanElementDelete([elems[ifid]], proj)
        del elems[ifid]


    def __addpoint(self, ifid, cf):
        "Create a new point to canvas and save it in newelems."
        proj = self.thanProj
        cp = list(proj[1].thanVar["elevation"])
        cp[:2] = cf[:2]
        elem = thandr.ThanPoint()
        elem.thanSet(cp)
        proj[1].thanElementAdd(elem, self.other.lay)
        elem.thanTkDraw(proj[2].than)
        self.other.newelems[ifid] = elem


    def __digfid(self, ifid, go=False):
        "Select the 1 point."
        proj = self.thanProj
        im = self.other.image
        p_gtkwid.thanGrabRelease()
        self.withdraw()
        if go: self.__zoomto(ifid)

        t = "%s %s: " % (Tphot["Please click on the center of fiducial"], ifid+1)
        while True:
            cf = proj[2].thanGudGetPoint(t)
            if cf == Canc: break
            try:
                jx, iy = im.thanGetPixCoor(cf)
                break
            except IndexError:
                proj[2].thanPrtEr(Tphot["point is outside image, Try again."])
        if cf == Canc:
            proj[2].thanGudCommandCan()
        else:
            self.__delpoint(ifid)
            self.__reject(ifid, "accept")
            self.labXpix[ifid].thanSet("%.1f" % cf[0])
            self.labYpix[ifid].thanSet("%.1f" % cf[1])
            self.other.tra = None      #Data changed -> transformation invalid
            self.__addpoint(ifid, cf)

        self.deiconify()
        p_gtkwid.thanGrabSet(self)


    def __zoomto(self, ifid):
        "Zooms to a region near the fiducial ifid."
        proj = self.thanProj
        cam = self.other.camera
        im = self.other.image
        xmax = max(fabs(x1) for x1 in cam.x) * 24.0/22.0
        ymax = max(fabs(y1) for y1 in cam.y) * 24.0/22.0
        xa, ya, xb, yb = im.getBoundBox()
        dx = (xb-xa) * 0.5
        dy = (yb-ya) * 0.5
        xm = xa+dx
        ym = ya+dy
        xfid = xm + dx * cam.x[ifid]/xmax
        yfid = ym + dy * cam.y[ifid]/ymax
        xymm = (xfid-dx*0.1, yfid-dy*0.1, xfid+dx*0.1, yfid+dy*0.1)
        v = proj[1].viewPort
        v[:] = proj[2].thanGudZoomWin(xymm)
        proj[2].thanAutoRegen(regenImages=True)


    def __compute(self):
        "Compute the interior orinetation as an affine transformation."
        if not self.validate(): return
        vs = self.result
        cam = self.other.camera
        n = len(cam.x)
        fots = []
        ifids = []
        for i in range(n):
            rej = self.thanChkReject[i].thanGet()
            if not rej:                              #Fiducial is not rejected
                fx = "labXpix%d" % (i+1,)
                fy = "labYpix%d" % (i+1,)
                vx = getattr(vs, fx)
                vy = getattr(vs, fy)
                if vx == "" or vy == "": rej = True  #Fiducial is blank -> reject
            if rej:
                self.labXcom[i].thanSet("")    #Blank rejected fiducials in the results
                self.labYcom[i].thanSet("")
                self.labXer[i].thanSet("")
                self.labYer[i].thanSet("")
            else:           #xg, yg, zg,  xr,       yr,       zr,  xyok,zok
                fots.append((vx, vy, 0.0, cam.x[i], cam.y[i], 0.0, 1.0, 1.0))
                ifids.append(i)
        if len(fots) < 3:
            mm(self, Tphot["At least 3 fiducials should be given"], Tphot["Error in computation"])
            return
        tra = p_gmath.Polynomial1_2DProjection()  #First order Poynomial: affine transform
        er, _, _ = tra.lsm23(fots)
        if er is None:
            mm(self, Tphot["The system of equations is singular."], Tphot["Error in computation"])
            return
        er = 0.0
        for ifid,(xpix,ypix,zpix,xcam,ycam,zcam,xyok,zok) in zip(ifids, fots):  #works for python2,3
            xcom, ycom, _ = tra.project((xpix, ypix, zpix))
            erx = xcam - xcom
            ery = ycam - ycom
            self.labXcom[ifid].thanSet("%.3f" % xcom)
            self.labYcom[ifid].thanSet("%.3f" % ycom)
            self.labXer[ifid].thanSet("%.3f" % erx)
            self.labYer[ifid].thanSet("%.3f" % ery)
            er += erx**2 + ery**2
        er = sqrt(er/(2*len(fots)))
        self.labEr.thanSet("%.3f" % er)
        self.other.tra = tra


    def ok(self, *args):
        "Ensure that the user has done the computation."
        if self.other.tra is None:
            if not self.ok2change(Tphot["Computation not performed, OK to close dialog?"]): return # Ok was stopped
        p_gtkwid.ThanDialog.ok(self, *args)


    def cancel(self, *args):
        "In case of escape, if float menu exists, delete float menu."
        if self.thanFloatMenu is not None and self.thanFloatMenu.winfo_ismapped():
            self.thanFloatMenu.unpost()
            return "break"
        return p_gtkwid.ThanComDialog.cancel(self, *args)


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
        del (self.labXpix, self.labYpix, self.labXcom, self.labYcom, self.labXer,
             self.labYer, self.labEr, self.thanFloatMenu, self.butFid,
             self.thanChkReject)
        p_gtkwid.ThanComDialog.destroy(self)


if __name__ == "__main__": print(__doc__)
