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

This package emulates the dxf library in ThanCad.
"""

from p_gimdxf import ThanImportBase
import p_ggen

from .thandxflin import ThanDxfLin
from .thandxfsym import ThanDxfSym
from .thandxfdra import ThanDxfDra
from .thandxfgeo import ThanDxfGeo
from .thandxfatt import ThanDxfAtt


class ThanDxfEmu(ThanImportBase, ThanDxfLin, ThanDxfSym, ThanDxfDra,
                    ThanDxfGeo, ThanDxfAtt):
    """A producer class to import a drawing as it is being created.

    The class is based on the importation of dxf files; it works like the class
    ThanImportDxf of the p_gimdxf library.
    The class sends drawing commands to the drawing object dr (self.thanDr)
    which is a receiver class instance.
    Here the receiver class is the ThanCadDrSave class.
    The class emulates the p_gdxf library so that a program which calls p_gdxf
    to create drawing (in a .dxf file), can now create the drawing into ThanCad
    in real time, with no modifications.
    """

    def __init__(self, fDxf=None, dr=None, defaultLayer="0", extensions=0):
        "Initialisation of class."
        ThanImportBase.__init__(self, fDxf=fDxf, dr=dr, defaultLayer=defaultLayer)
        ThanDxfLin.__init__(self)
        ThanDxfSym.__init__(self)
        ThanDxfDra.__init__(self)
        ThanDxfGeo.__init__(self)
        ThanDxfAtt.__init__(self)
        self.__tabExist = 0
        self.__blocks   = 0
        self.__entities = 0
        self.thanExt = extensions


    def thanDxfPlots(self, uDxf1=None, defaultLayer=None):
        "User initialisation 1."
        if uDxf1 is not None: self.thanDr = uDxf1
        if defaultLayer is not None: self.defLay = defaultLayer

        self.thanDxfPlots1(uDxf1)
        self.thanDxfTableDef (' ', 0)

#-------STYLE header-------------------------------------------------

        self.thanDxfTableDef ('STYLE', 1)
        self.thanDxfCrTstyle ('GRSTYLE', 'Times New Roman Greek')

#-------LINETYPE header-------------------------------------------------

        self.thanDxfTableDef ('LTYPE', 2)
        self.thanDxfCrLtype ('DOTR',    '..........', [0.0,  -0.06])
        self.thanDxfCrLtype ('DASHED2', '- - - - ',   [0.25, -0.125])

#-------ENTITIES follow--------------------------------------------

        self.thanDxfTableDef ('ENTITIES', 1)
        self.thanDxfSetTstyle("GRSTYLE")


    def thanDxfPlots1 (self, uDxf1=None, defaultLayer=None):
        "Initialisation 2."
        if uDxf1 is not None: self.thanDr = uDxf1
        if defaultLayer is not None: self.defLay = defaultLayer

        self.thanDxfSetLayer('P1')
        self.thanDxfSetLtype ('BYLAYER')
        self.thanDxfSetColor (7)
        self.thanDxfSetTstyle("STANDARD")

        self.thanMode  = 2
        self.thanDelay = 100
        self.thanXar   = 0.0
        self.thanYar   = 0.0
        self.thanZar   = 0.0
        self.thanXfac  = 1.0
        self.thanYfac  = 1.0
        self.thanZfac  = 1.0
        self.thanFact  = 1.0
        self.thanPXnow = 0.0
        self.thanPYnow = 0.0
        self.thanPZnow = 0.0
        self.thanPXar  = 0.0
        self.thanPYar  = 0.0
        self.thanPZar  = 0.0
#        self.thanDotxcm = 513.0 / 23.5
#        self.thanDotycm = 347.0 / 17.0
        self.thanDotxcm = 180.0 / 2.539970
        self.thanDotycm = 180.0 / 2.539970

        self.thanDotmin = 1.0 / self.thanDotxcm

        self.thanDxfSetPlineWidth(0.0, 0.0)
#        self.thanDxfPlot(1/dotxcm, 0, -3)
#        self.thanDxfCls()

    def thanDxfTableDef(self, tableName, iTableEntries):
        """Specifies that a table follows or section entities.

        tableName:     Name of table to be created (STYLE, LAYER, LTYPE)
        iTableEntries: Number of elements of each table. For example, If we have 4 layers
                       then ay TableName LAYER, iTableEntries=4.
                       If iTableEntries==4 an initialisation is performed.
        """

        if iTableEntries == 0:
#            self.thanDxfWrEntry(0, 'SECTION')                 # SECTION initialisation
#            self.thanDxfWrEntry(2, 'TABLES')                  # TABLES
            self.__tabExist = 0
            self.__blocks   = 0
            self.__entities = 0
        elif self.__entities:
            raise p_ggen.ThanImportError('thanTableDef(): Table definitions must precede ENTITIES.')
        elif tableName == 'ENTITIES':
            if self.__tabExist and not self.__blocks: pass #self.thanDxfWrEntry(0, 'ENDTAB')
#            self.thanDxfWrEntry(0, 'ENDSEC')
#            self.thanDxfWrEntry(0, 'SECTION')
#            self.thanDxfWrEntry(2, 'ENTITIES')
            self.__entities = 1
        elif tableName == 'BLOCKS':                        # TABLE start
            if self.__blocks:
                raise p_ggen.ThanImportError('thanTableDef(): Blocks already defined!')
            if self.__tabExist: pass #self.thanDxfWrEntry(0, 'ENDTAB')
#            self.thanDxfWrEntry(0, 'ENDSEC')
#            self.thanDxfWrEntry(0, 'SECTION')
#            self.thanDxfWrEntry(2, 'BLOCKS')
            self.__blocks = 1
            self.__tabExist = 1
        else:
            if self.__blocks:
                raise p_ggen.ThanImportError('ThanTableDef(): Table defs must precede blocks.')
            if self.__tabExist: pass #self.thanDxfWrEntry(0, 'ENDTAB')
#            self.thanDxfWrEntry(0, 'TABLE')
#            self.thanDxfWrEntry(2, tableName)
#            self.thanDxfWrEntry(70, iTableEntries)
            self.__tabExist = 1

    def thanDxfCrLayer(self, name, color=7, linetype="continuous", off=False,
                       frozen=False, locked=False, noplot=False, lineweight=0.0, **kw):
        """Creates a layer entry in the dxf file.

        name  :  layer name
        color :  layer color
        linetype :  layer Linetype
        lineweight: The thickness of the "pen" that the layer is
                    plotted with (mm)

        TABLE LAYER
         62:  5 (or positive) : layer on
             -5 (or negative) : layer off
         70:  flags: bit 0: if set layer is frozen (the layer is NOT drawn on the monitor)
                            if flags & 1: it is frozen
                     bit 2: if set layer is locked (its elements can not be altered)
                            if flags & 4: it is locked
              4  : layer locked
        370: 106 :  lineweight 1.06 mm
              60 :             0.60 mm
              -3 :             Autocad's default lineweight (who knows what this means!)
        290: 0   : no plot is on (the layer is NOT plotted)
                   If code 290 is absent, then no plot is off (the layer is plotted)
        Any other attribute not defined above are ignored.
        """
        self.thanDr.thanSetLay(name, color)

    def thanDxfCrLtype (self, linName, linDescr, rElems):
        """Creates a line type entry in the dxf file.

        linName    : Line type name
        linDescr   : Line type description
        rElems     : Line elements
        """
        pass

    def thanDxfCrTstyle(self, fName, fFontFileName):
        """Creates a text style entry in the dxf file.

        fName        : Text Style name
        fFontFileName: Font filename. If it has ".shx" extension, then it is
                       defined as complex linestyle.
        """
        pass

    def thanDxfCrBlock(self, bFileName):
        """Creates a block entry in the dxf file.

        The block definition in the dxf file must not include
        code 5 (handle), because Intellicad has trouble with it
        (it may be either Intellicad's dxfin bug, or Autocad's
        dxfout bug.
        ThanCad is indifferent (it does not support blocks yet ;) )."""
        pass
