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

This module displays a dialog for the user to scan and insert an image
to ThanCad.
"""
from tkinter import Tk, Frame, Canvas
import p_gimage
from p_gtkwid import (ThanDialog, thanGudModalMessage, thanGudAskOkCancel,
    thanGudGetSaveFile, ThanButton)
from thantrans import T


class ThanScan(ThanDialog):
    "An object to provide basic scan capabilities."

    def __init__(self, master, can, dpis, cargo=None, *args, **kw):
        "Extract initial parameters."
        self.can = can
        self.dpis = dpis
        self.thanProj = cargo
        self.im = self.imtk = None
        self.imfilnam = ""
        self.imsaved = True

        kw.setdefault("title", T["Scan image and insert to ThanCad"])
        kw.setdefault("buttonlabels", (T["Insert Image\nto drawing"], T["Cancel"]))
        ThanDialog.__init__(self, master, *args, **kw)


    def dpiset(self, d=None):
        "Set the scan dpi."
        if d is not None: self.can.resolution = d
        self.butScan.config(text=T["Scan"]+"[%ddpi]" % self.can.resolution)
        self.butScan.update()


    def scan(self):
        "Acquire image from the scanner and make a preview."
        if not self.imsaved:
            a = thanGudAskOkCancel(self, T["Scanned Image has not been saved, OK to discard?"], T["Warning"])
            if not a: return        # Scan was stopped
        try:
            im1 = self.can.scan()
        except Exception as why:
            er = "%s:\n%s" % (T["Scanner failed to scan"], why)
            thanGudModalMessage(self, er, T["Error while scanning"])
            return
        self.im = im1
        self.redrawim()


    def redrawim(self):
        "Shrinks the image to fit into the window."
        if self.im is None: return
        self.dc.update()
        bdc = self.dc.winfo_width() - 20      #Leave 20 pixels for margins
        hdc = self.dc.winfo_height() - 20     #Leave 20 pixels for margins
        if bdc < 10 or hdc < 10:
            thanGudModalMessage(self, "Error", T["Window too small to display image"])
            return
        b, h = self.im.size
        if b < 1 or h < 1:
            thanGudModalMessage(self, "Error", T["Illegal Image"])
            return
        im1 = self.im
        rb = float(b) / bdc
        rh = float(h) / hdc
        if rb > rh:
            if b > bdc:
                h = int((h*bdc)/b)
                b = int(bdc)
                im1 = self.im.resize((b, h))
        else:
            if h > hdc:
                b = int((b*hdc)/h)
                h = int(hdc)
                im1 = self.im.resize((b, h))
        self.imtk = p_gimage.PhotoImage(im1)
        self.dc.delete(self.tem2)
        self.tem2 = self.dc.create_image(10, 10, image=self.imtk, anchor="nw")    #, tags=self.thanTags)
        self.imsaved = False


    def rotateim(self, com):
        "Rotates the scanned image 90, 180, or 270 deg."
        if self.im is None:
            thanGudModalMessage(self, T["No image has been scanned!"], T["Error in data"])
            return
        self.im = self.im.transpose(com)
        self.redrawim()


    def saveim(self):
        "Save image to a file."
        if self.im is None:
            thanGudModalMessage(self, T["No image has been scanned!"], T["Error in data"])
            return
        while 1:
            filnam = thanGudGetSaveFile(self, ext=".png", tit=T["Filename to save image"])
            if not filnam: return        # User cancelled
            try:
                self.im.save(filnam)
            except Exception as why:
                thanGudModalMessage(self, "%-30s" % why, T["Error saving image"])
            else:
                self.imfilnam = filnam
                self.imsaved = True
                return


    def body(self, win):
        "Create the widgets."
        fra = Frame(win)
        fra.grid(row=0, column=0, sticky="we")
        for i,dpi in enumerate(self.dpis):
            b = ThanButton(fra, text="%ddpi"%dpi, bg="lightcyan",
                activebackground="cyan", command=lambda d=dpi: self.dpiset(d))
            b.grid(row=0, column=i)
            fra.columnconfigure(i, weight=1)

        fra = Frame(win)
        fra.grid(row=1, column=0, sticky="wesn")
        self.dc = Canvas(fra, width=120, height=120, bg="orange")
        self.dc.grid(row=0, column=0, rowspan=6, sticky="wesn")
#        self.dc.create_rectangle(10-1,10-1,110+1,110+1,outline="red")
        self.tem2 = self.dc.create_line(10000, 10000, 10001, 100001)     # Dummy item

        self.butScan = ThanButton(fra, text=T["scan"], bg="lightcyan",
            activebackground="cyan", command=self.scan)
        self.butScan.grid(row=0, column=1, sticky="we")
        self.dpiset()

        but = ThanButton(fra, text=T["Rotate left 90deg"], bg="lightblue", activebackground="SkyBlue",
            command=lambda com=p_gimage.ROTATE_90:  self.rotateim(com))
        but.grid(row=1, column=1, sticky="we")
        but = ThanButton(fra, text=T["Rotate 180deg"], bg="lightblue", activebackground="SkyBlue",
            command=lambda com=p_gimage.ROTATE_180: self.rotateim(com))
        but.grid(row=2, column=1, sticky="we")
        but = ThanButton(fra, text=T["Rotate right 90deg"], bg="lightblue", activebackground="SkyBlue",
            command=lambda com=p_gimage.ROTATE_270: self.rotateim(com))
        but.grid(row=3, column=1, sticky="we")
        but = ThanButton(fra, text=T["Redraw Image"], bg="lightblue", activebackground="SkyBlue",
            command=self.redrawim)
        but.grid(row=4, column=1, sticky="we")

        but = ThanButton(fra, text=T["Save Image\nto file"], command=self.saveim)
        but.grid(row=5, column=1, sticky="we")
        for i in range(6): fra.rowconfigure(i, weight=1)
        fra.columnconfigure(0, weight=1)
        win.rowconfigure(1, weight=1)
        win.columnconfigure(0, weight=1)


    def validate(self):
        "Check that everything is ok."
        if self.im is None:
            thanGudModalMessage(self, T["No image has been scanned!"], T["Error in data"])
#            self.initial_focus = wid
            return False
        if not self.imsaved:
            thanGudModalMessage(self, T["Please save scanned Image"], T["Error in data"])
            return False
        self.result = self.im, self.imfilnam
        return True


    def cancel(self, *args):
        "Ask before cancel."
        if self.im is not None and not self.imsaved:
            a = thanGudAskOkCancel(self, T["Scanned Image has not been saved, OK to discard?"], T["Warning"])
            if not a: return        # Cancel was stopped
        ThanDialog.cancel(self, *args)


    def destroy(self, *args):
        "Breaks circular references."
        del self.imtk, self.dc, self.butScan
        self.can.close()                     # Close scanner
        ThanDialog.destroy(self, *args)


if __name__ == "__main__":
    from p_ggen import Struct, Tgui as T
    can, dpis, ScanException = p_gimage.getScanDpi()
    print(can, dpis, ScanException)
    if can is None: can, dpis, _ = p_gimage.getScanDpiFake()
    root = Tk()
    d = ThanScan(root, can, dpis, cargo=None)
