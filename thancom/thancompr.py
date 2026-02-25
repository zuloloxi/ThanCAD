# -*- coding: iso-8859-7 -*-

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

Package which processes commands entered by the user.
This module processes print and scan commands.
"""
import tempfile
from p_ggen import path
import p_gimage
from thandefs import thanplotcups
import thantkdia
from thanvar import Canc


#def doprint(self):
#   "Experimental tests for printing."
#   atts = self.ccups.getPrinterAttributes(nam)
#   for key,val in atts.items():  #works for python2,3
#       print "%-20s: %s" % (key, val)
#   ppd = self.ccups.getPPD(nam)
#   print ppd

#   a = {"document-format-default": 'text/plain'}
#   job = self.ccups.printFile(nam, fn, "Andreas job "+fn, a)


def thanPrPlot(proj):
    """Prints the contents of canvas to a postscript file and send it to a printer.

    printFile(printer, filename, title, options) -> integer

    Print a file.

    @type printer: string
    @param printer: queue name
    @type filename: string
    @param filename: local file path to the document
    @type title: string
    @param title: title of the print job
    @type options: dict
    @param options: dict of options
    @return: job ID
    @raise IPPError: IPP problem
    """
    ccups, printers, mes = thanplotcups.getPrinters()
    if mes != "":
        proj[2].thanCom.thanAppend(mes, "can1")
    win = thantkdia.ThanDiaPlot(proj[2], ccups, printers, proj[1].thanPlotDef, proj)
    if win.result is None: return proj[2].thanGudCommandCan()
    res, act = win.result
    if proj[1].thanPlotDef != res: proj[1].thanTouch()
    proj[1].thanPlotDef = res
    if act != "apply": return proj[2].thanGudCommandEnd()

    if res.radWhat == 0:
        c1 = list(proj[1].thanVar["elevation"])
        c1[:2] = proj[1].viewPort[:2]
        c2 = list(c1)
        c2[:2] = proj[1].viewPort[2:]
    else:
        c1, c2 = res.butPick
    x1, y1 = proj[2].thanCt.global2Local(c1[0], c1[1])
    x2, y2 = proj[2].thanCt.global2Local(c2[0], c2[1])
    if x1 > x2: x1, x2 = x2, x1
    if y1 > y2: y1, y2 = y2, y1

    if res.choPr == thanplotcups.TOFILE:
        fn = res.filPlot
        try:
            fw = open(fn, "w")
        except IOError:
            fn = proj[0].parent / proj[0].namebase + ".ps"
            proj[1].thanPlotDef.filPlot = fn
        else:
            fw.close
    else:
        fw = tempfile.NamedTemporaryFile("w", suffix=".ps")
        fn = fw.name
        fw.close()
    dc = proj[2].thanCanvas
    dc.thanCh.thanDisable()
#    dc.postscript(x=x1, y=y1, width=x2-x1+1, height=y2-y1+1, pageheight="5c", colormode="color", file=fn)
    dc.postscript(x=x1, y=y1, width=x2-x1+1, height=y2-y1+1, pagewidth="28c", colormode="color", rotate=True, file=fn)
    dc.thanCh.thanEnable()
    if res.choPr == thanplotcups.TOFILE:
        return proj[2].thanGudCommandEnd("Plot file %s was created." % fn, "info")
    job = ccups.printFile(res.choPr, fn, "ThanCad job "+fn, {})
    path(fn).remove()
    return proj[2].thanGudCommandEnd("Plot file %s was sent to %s (job %d)." % (fn, res.choPr, job), "info")


def thanImageScan(proj):
    "Scan an image and insert it to ThanCad."
    from thandr import ThanImage
    can, dpis, ScanException = p_gimage.getScanDpi()
    if can is None: return proj[2].thanGudCommandCan(ScanException)    #Here 'ScanException' is an error message
    win = thantkdia.ThanScan(proj[2], can, dpis, proj)
    if win.result is None: return proj[2].thanGudCommandCan()
    im, imfilnam = win.result
    elem = ThanImage()
    if elem.thanTkGet(proj, im, imfilnam) == Canc: return proj[2].thanGudCommandCan()
    proj[1].thanElementAdd(elem)
    elem.thanTkDraw(proj[2].than)
    proj[2].thanTkSetFocus()
    return proj[2].thanGudCommandEnd()
