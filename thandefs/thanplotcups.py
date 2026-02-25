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

This module provides plot capabilities except content.
"""

import p_ggen
from p_gtkwid import Twid as T
from . import cupsfake
try:
    import cups
except ImportError:
    cups = cupsfake
TOFILE = cupsfake.TOFILE

thanTempPrefix = "untitled"      #Prefix for the names of new drawings


class ThanPlot:
    "An object to provide basic plot capabilities."

    def __init__(self, dimensionality=3, name=thanTempPrefix):
        "Build default values; set to new values if new are valid."
        self.__defprinter()
        self.radWhat = 1
        c1 = [0.0]*dimensionality
        c1[:2] = 0.0, 0.0
        c2 = list(c1)
        c2[:2] = 10.0, 10.0
        self.butPick = c1, c2
        name = p_ggen.path(name)
        self.filPlot = name.parent / name.namebase + ".ps"


    def __defprinter(self, choPr=None):
        "Set default printer if possible."
        self.choPr = choPr
        ccups, printers, _ = getPrinters(host=None)
        if self.choPr not in printers:
            self.choPr = p_ggen.any1(printers)
            defname = ccups.getDefault()            #Default printer's name
            if defname in printers: self.choPr = defname


    def thanSet(self, choPr, radWhat, butPick, filPlot):
        "Set new values if valid."
        print("ThanPlot.thanSet() called: filplot=", filPlot)
        ccups, printers, _ = getPrinters(host=None)
        if choPr in printers: self.choPr = choPr
        if 0 <= radWhat < 2: self.radWhat = radWhat
        if butPick[0][:2] != butPick[1][:2]: self.butPick = butPick
        if len(filPlot.strip()) > 0: self.filPlot = p_ggen.path(filPlot)


    def thanRepair(self, proj):
        "Repair the object according to current project and current printers."
        self.__defprinter(self.choPr)
        if self.radWhat not in (0, 1): self.radWhat = 1
        ce = proj[1].thanVar["elevation"]
        for c1 in self.butPick: c1[2:] = ce[2:]
        if self.butPick[0][:2] == self.butPick[1][:2]:
            self.butPick[1][0] += 1.0
            self.butPick[1][1] += 1.0
        print("thanplotcups.ThanPlot.thanrepair(): filPlot=", self.filPlot)
        if self.filPlot.namebase.strip() in (thanTempPrefix, "", proj[0].namebase):   #Note:the thcx file may have been moved elsewhere
            self.filPlot = proj[0].parent / proj[0].namebase + ".ps"
        print("thanplotcups.ThanPlot.thanrepair(): filPlot=", self.filPlot)


    def thanExpThc(self, fw):
        "Save the plot definition in thc format."
        fw.writeBeg("PLOT_DEFINITION")
        fw.pushInd()
        p = self.choPr
        if p == cupsfake.TOFILE: p = "FILE:"
        fw.writeAtt("printer", p)
        fw.writeAtt("plotwhat", "%d" % self.radWhat)
        fw.writeBeg("WINDOW")
        fw.pushInd()
        for c1 in self.butPick: fw.writeNode(c1)
        fw.popInd()
        fw.writeEnd("WINDOW")
        fw.writeAtt("plotfile", self.filPlot)
        fw.popInd()
        fw.writeEnd("PLOT_DEFINITION")


    def thanImpThc(self, fr):
        "Read the plot definition from thc format."
        fr.readBeg("PLOT_DEFINITION")    #May raise ValueError, StopIteration
        choPr = fr.readAtt("printer")[0]  #May raise ValueError, IndexError, StopIteration
        if choPr == "FILE:": choPr = cupsfake.TOFILE
        radWhat = int(fr.readAtt("plotwhat")[0])  #May raise ValueError, IndexError, StopIteration
        fr.readBeg("WINDOW")             #May raise ValueError, StopIteration
        c1 = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        c2 = fr.readNode()               #May raise ValueError, IndexError, StopIteration
        butPick = [c1, c2]
        fr.readEnd("WINDOW")             #May raise ValueError, StopIteration
        filPlot = fr.readAtt("plotfile")[0]  #May raise ValueError, IndexError, StopIteration
        self.thanSet(choPr, radWhat, butPick, filPlot)
        fr.readEnd("PLOT_DEFINITION")    #May raise ValueError, StopIteration


def getPrinters(host=None):
    "Initialize cups system, and get available printers."
    fccups = cupsfake.Connection()
    fprinters = fccups.getPrinters()
    if cups is cupsfake:
        return fccups, fprinters, T["Python module 'cups' has not been installed.\n"\
        "Please install module 'cups' and retry.\n"\
        "(Hint: if your OS does not support cups, consider switching to almost anything but WinDoze:)).\n"]
    try:
        if host: cups.setServer(host)
        else:    host = "localhost"
        ccups = cups.Connection()
    except Exception as why:
        return fccups, fprinters, "%s:\n%s\n(%s %s)\n" % (T["Module cups failed to initialize."], why, T["Ensure that cups is running on"], host)
    try:
        printers = ccups.getPrinters()
        printers.update(fprinters)         #Add 'file' printer
        return ccups, printers, ""
    except Exception as why:
        return fccups, fprinters, "%s:\n%s\n(%s)\n" % (T["Module cups failed while identifying printers"], why, host)
