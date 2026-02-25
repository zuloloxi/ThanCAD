##############################################################################
# ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2016 Thanasis Stamos, June 19, 2016
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers

This module displays a dialog for the user to export to a raster image
using Python Image Library.
"""

from __future__ import print_function
import tkinter
import p_ggen, p_gtkwid
from thantrans import T
from thanvar import thanfiles
from thandefs.thanatt import ThanAttCol
from .thandialogcol import ThanColor


thanImageTypes = ( (".bmp", "BMP"),
                   (".jpg", "JPEG"),
                   (".png", "PNG"),
                   (".tif", "TIFF"),
                 )

thanImageModes = ( ("RGB", T["Full RGB"]),
                   ("L",   T["Gray scale"]),
                   ("1",   T["Bitmap"]),
                 )

thanPlotCodes = ( ("display", T["Display"]),
                )


thanBackGrs = [ (ThanAttCol("white"), T["White"]),
                (ThanAttCol("black"), T["Black"]),
                (ThanAttCol("gray"),  T["Gray"]),
                (None,                T["Other"]),
              ]

class ThanTkExppil(p_gtkwid.ThanComDialog):
    "Dialog for plotting the drawing to an image."


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct("Values for Export Image")
        v.choType = ".bmp"
        v.filIm = self.thanProj[0].parent/self.thanProj[0].namebase+"plot"+v.choType
        v.choMode = "RGB"
        v.entWidth = 1024
        v.entHeight = 1024
        v.choBackGr = thanBackGrs[0][0]      #white
        v.choPlotCode = "display"
        return v


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraFile(win, 1)
        self.fraImage(win, 2)
        self.fraPlot(win, 3)


    def fraFile(self, win, ir):
        "Select the file specifications."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")
        fra.columnconfigure(2, weight=1)

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["FILE SPECIFICATIONS:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=2)

        ir = 1
        key = "choType"
        tit = "File type"                    #T["File type"]
        val = p_gtkwid.ThanValidator()
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanChoiceRef(fra, objects=thanImageTypes, command=self.__typeSet,
             width=10, relief=tkinter.RIDGE, anchor="w")
        wid.grid(row=ir, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        ir += 1
        key = "filIm"
        tit = "Image file"                   #T["Image file"]
        val = p_gtkwid.ThanValidator()
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        dir1 = thanfiles.getFiledir()
        wid = p_gtkwid.ThanFile(fra, extension=".bmp", mode="w", initialdir=dir1,
            title=T["Open image file"], width=0)
        wid.grid(row=ir, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        self.columnconfigure(2, weight=1)


    def fraImage(self, win, ir):
        "Select the Image specifications."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["IMAGE SPECIFICATIONS:"])
        lab.grid(row=0, column=1, sticky="we", columnspan=2)

        ir = 1
        key = "choMode"
        tit = "Image mode"                     #T["Image mode"]
        val = p_gtkwid.ThanValidator()
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanChoiceRef(fra, objects=thanImageModes,
                        width=10, relief=tkinter.RIDGE, anchor="w")
        wid.grid(row=ir, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))

                                    #T["width (pixels)"],             T["height (pixels)"]
        for key, tit in ("entWidth", "width (pixels)"), ("entHeight", "height (pixels)"):
            ir += 1
            val = p_gtkwid.ThanValInt(3, 100000)
            lab = tkinter.Label(fra, text=T[tit])
            lab.grid(row=ir, column=1, sticky="e")
            wid = p_gtkwid.ThanEntry(fra, width=35)
            wid.grid(row=ir, column=2, sticky="we")
            self.thanWids.append((key, tit, wid, val))


        ir += 1
        key = "choBackGr"
        tit = "Background colour"
        val = p_gtkwid.ThanValidator()
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanChoiceRef(fra, objects=thanBackGrs, command=self.__onBackGr,
                        width=10, relief=tkinter.RIDGE, anchor="w")
        wid.grid(row=ir, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))

        self.columnconfigure(2, weight=1)


    def __onBackGr(self, i, obj, text):
        "If user selected other, display the colour dialog."
        print("__onBackGr:", text)
        if i != 3: return              #If not "other", there is nothing to do
        colold = thanBackGrs[2][0]     #Previous "other" colour
        print("colold=", colold)
        w = ThanColor(self, colold, special=False, title=T["Select background colour"])
        colnew = w.result
        if colnew is not None: thanBackGrs[2] = (colnew, str(colnew))
        self.after(200, self.choBackGr.thanSet, thanBackGrs[2][0])


    def fraPlot(self, win, ir):
        "Select the Image specifications."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=T["PLOT SPECIFICATIONS:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=2)

        ir = 1
        key = "choPlotCode"
        tit = "Plot area"
        val = p_gtkwid.ThanValidator()
        lab = tkinter.Label(fra, text=T[tit])
        lab.grid(row=ir, column=1, sticky="e")
        wid = p_gtkwid.ThanChoiceRef(fra, objects=thanPlotCodes,
                        width=10, relief=tkinter.RIDGE, anchor="w")
        wid.grid(row=ir, column=2, sticky="we")
        self.thanWids.append((key, tit, wid, val))


    def __typeSet(self, i, ext, text):
        "Change the type of the image file."
        self.filIm.config(extension=ext)
        fn = self.filIm.thanGet().strip()
        if fn == "": return
        fn = p_ggen.path(fn)
        fn = fn.parent / fn.namebase+ext
        self.filIm.thanSet(fn)


    def validate(self, strict=True, wids=None, values=None):
        "Returns true if the value chosen by the user is valid."
        ret, vs = self.validate2(strict, wids, values)
        if not ret and strict: return ret

        self.__typeSet(None, vs.choType, None)

        self.result = vs
        return ret
