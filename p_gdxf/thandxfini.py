from os.path import splitext
from math import fabs

from .thandxflin import ThanDxfLin
from .thandxfsym import ThanDxfSym
from .thandxfdra import ThanDxfDra
from .thandxfgeo import ThanDxfGeo
from .thandxfatt import ThanDxfAtt

from .thandxfext import thanCadCodes

_idatFil = 0


class ThanDxfPlot(ThanDxfLin, ThanDxfSym, ThanDxfDra,
                    ThanDxfGeo, ThanDxfAtt):
    "Class to create drawings directly into .dxf files."

#===========================================================================

    def __init__(self, extensions=0):
        "Initialisation of class."
        ThanDxfLin.__init__(self)
        ThanDxfSym.__init__(self)
        ThanDxfDra.__init__(self)
        ThanDxfGeo.__init__(self)
        ThanDxfAtt.__init__(self)
        self.__tabExist = 0
        self.__blocks   = 0
        self.__entities = 0
        self.thanExt = extensions

#===========================================================================

    def thanDxfPlots(self, uDxf1=None):
        "User initialisation 1."

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

#===========================================================================


    def thanDxfPlots1 (self, uDxf1=None, vars=()):
        "Initialisation 2."

        if uDxf1 is None:
            global _idatFil
            _idatFil += 1
            self.thanFdxf = open(("data%03d.dxf"%_idatFil), "w")
#            self.thanFdxf = open("data"+str(_idatFil)+".dxf", "w")
        else:
            self.thanFdxf = uDxf1

        self.thanDxfSetLayer('P1')
        self.thanDxfSetLtype ('BYLAYER')
        self.thanDxfSetColor (0)
        self.thanDxfSetTstyle("STANDARD")

#       The use of the following Section Header enables Autocad 14 to dxfin correctly
        self.thanDxfWrEntry(0, 'SECTION')
        self.thanDxfWrEntry(2, 'HEADER')
        self.thanDxfWrEntry(9, '$ACADVER')
        self.thanDxfWrEntry(1, 'AC1009')
        for name, icod, val in vars:
            self.thanDxfWrEntry(9, name)
            self.thanDxfWrEntry(icod, val)
#-------It seems that version 15 needs much more than the minimal dxf
#-------entries which were OK in previous versions. Moreover, the newer
#-------versions of dxf have an unneeded complexity which is beyond
#-------imagination (for example the raster image could be described as
#-------easily as (dxf version 10) standard text. Now it is described
#-------with entries to at least 3 totally unrelated SECTIONS or TABLES).
#-------
#-------It seems to me, that even via the clumsy dxf, the free sharing
#-------of drawing files (with freedom meant as in GPL) has flourished.
#-------The earlier versions of dxf made it possible for many other,
#-------special purpose, drawing programs to interoperate (clumsily)
#-------with thAtCAD. This was good for thAtCAD. The special purpose
#-------programs attracted more clients to thAtCAD.
#-------But then, thAtCAD started to get into the
#-------special purpose market itself (consider for example GIS).
#-------The other special purpose programs were suddenly transformed
#-------to competition. More important, the other programs,
#-------via the dxf format, were able to interoperate between
#-------THEMSELVES, with no need for thAtCAD at all.
#-------So it seems that
#-------thAtCAD has adopted methods of another, monopolistic, software
#-------company, and it has polluted the originally simple dxf format
#-------with incompatible features. For example dxf version 14 is
#-------incompatible with version 12. thAtCad 14 would not read dxf
#-------version 12, unless a special header was included in the
#-------file. I remember in 1998 when my colleagues were frustrated
#-------because they had a vast amount of drawing files in dxf 12,
#-------created by special purpose programs. It took the efforts
#-------of 2 geeks to find out the solution and provide for a suitable
#-------patch. I wonder what others did, who were not fortunate to be
#-------geeks.
#-------Moreover, if you include a feature found in dxf 15
#-------(for example layer's lineweight) to a dxf file marked as
#-------version 12, thAtCad WILL NOT READ IT. Thus, you are forced to
#-------move to the newer versions of dxf. And finally, the dxf
#-------specifications are released after several months after the
#-------release of a newer version of thAtCad, and many times the
#-------specifications are incomplete, or even the format is
#-------incomplete.

#-------A solution to this problem would be to create a free library
#-------that reads directly the .dwg files. This of course would be
#-------a lengthy and tortuous deed. But it has been done.
#-------There is a library which reads directly the .dwg files. The
#-------library is not entirely free, but it is free enough. The people
#-------who managed to decipher the .dwg format, have asked thAtCad
#-------to participate in their effort, but the answer was no.
#-------Moreover, thAtCad was never commented favourably or unfavourably
#-------about the library. I wonder why. ThAtCad boasts that there
#-------are millions of drawings all over the world with the .dwg format.
#-------Since, essentially, the library spreads the use of .dwg, which
#-------is their format, thAtCad has done nothing against the library.
#-------But I wonder. If thAtCad feels threatened, wouldn't they
#-------make it illegal for other programs to read/write .dwg? And thus
#-------destroying all competition (since the competition will be
#-------based on the library)? Unless the competition used .dxf
#-------which is essentially free, because it is plain ASCII. Unless
#-------again dxf is made so complex and incompatible with itself that
#-------noone uses it.
#-------
#-------Thus, this library sticks with dxf format 12, which
#-------regretably, does not allow some features, such as the
#-------lineweight in layers and images.
#-------                                 Thanasis Stamos April 16, 2004.

#        self.thanDxfWrEntry(1, 'AC1015')      # Can't use it, for the moment at least
        self.thanDxfWrEntry(0, 'ENDSEC')

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

#======================================================================

    def thanDxfTableDef(self, tableName, iTableEntries):
        """Specifies that a table follows or section entities.

        tableName:     Name of table to be created (STYLE, LAYER, LTYPE)
        iTableEntries: Number of elements of each table. For example, If we have 4 layers
                       then at TableName LAYER, iTableEntries=4.
                       If iTableEntries==4 an initialisation is performed.
        """

        if iTableEntries == 0:
            self.thanDxfWrEntry(0, 'SECTION')                 # SECTION initialisation
            self.thanDxfWrEntry(2, 'TABLES')                  # TABLES
            self.__tabExist = 0
            self.__blocks   = 0
            self.__entities = 0
        elif self.__entities:
            assert False, 'thanTableDef(): Table definitions must precede ENTITIES.'
        elif tableName == 'ENTITIES':
            if self.__tabExist and not self.__blocks: self.thanDxfWrEntry(0, 'ENDTAB')
            self.thanDxfWrEntry(0, 'ENDSEC')
            self.thanDxfWrEntry(0, 'SECTION')
            self.thanDxfWrEntry(2, 'ENTITIES')
            self.__entities = 1
        elif tableName == 'BLOCKS':                        # TABLE start
            if self.__blocks:
                assert 0, 'thanTableDef(): Blocks already defined!'
            if self.__tabExist: self.thanDxfWrEntry(0, 'ENDTAB')
            self.thanDxfWrEntry(0, 'ENDSEC')
            self.thanDxfWrEntry(0, 'SECTION')
            self.thanDxfWrEntry(2, 'BLOCKS')
            self.__blocks = 1
            self.__tabExist = 1
        else:
            if self.__blocks:
                assert 0, 'ThanTableDef(): Table defs must precede blocks.'
            if self.__tabExist: self.thanDxfWrEntry(0, 'ENDTAB')
            self.thanDxfWrEntry(0, 'TABLE')
            self.thanDxfWrEntry(2, tableName)
            self.thanDxfWrEntry(70, iTableEntries)
            self.__tabExist = 1

#==========================================================================

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

        self.thanDxfWrEntry(0,  'LAYER')
        self.thanDxfWrEntry(2,  name)
        self.thanDxfWrEntry(6,  linetype)

        if off: color = -color
        self.thanDxfWrEntry(62, color)

        self.thanDxfWrEntry(70, frozen | locked<<2)

#       if noplot: self.thanDxfWrEntry(290, 0)    # Can't use it, because dxf 12 did not have it

        if lineweight <= 0.0: lineweight = -3
        else:                 lineweight = int(lineweight*100)
#        self.thanDxfWrEntry(370, lineweight)     # Can't use it, because dxf 12 did not have it

#==========================================================================


    def thanDxfCrThanLayer(self, name, **kw):
        """Creates a layer entry in the dxf file.

        It writes only the absolute necessary information and lets the cad
        to provide for default values. In case of ThanCad, the absent
        attributes mean inheritance from parent.
        In the case of ThanCad many more attributes may be defined.
        """
        self.thanDxfWrEntry(0, 'LAYER')
        self.thanDxfWrEntry(2, name)
        for att,val in kw.items():    #OK for python 2,3
            try: code=thanCadCodes[att]
            except KeyError:
                print("dxflib: unknown layer attribute:", att)
                continue
            if val is None: continue
            if isinstance(val, bool): val = int(val)
            self.thanDxfWrEntry(code, val)

#======================================================================

    def thanDxfCrLtype (self, linName, linDescr, rElems):
        """Creates a line type entry in the dxf file.

        linName    : Line type name
        linDescr   : Line type description
        rElems     : Line elements
        """
        #rlinLength = reduce(lambda x,y: x+fabs(y), rElems, 0.0)  # Calculation of line length
        rlinLength = sum(fabs(r1) for r1 in rElems)  # Calculation of line length
        self.thanDxfWrEntry(0, 'LTYPE')
        self.thanDxfWrEntry(2, linName)
        self.thanDxfWrEntry(70, 0)
        self.thanDxfWrEntry(3, linDescr)
        self.thanDxfWrEntry(72, 65)
        self.thanDxfWrEntry(73, len(rElems))
        self.thanDxfWrEntry(40, rlinLength)
        for e in rElems: self.thanDxfWrEntry(49, e)

#======================================================================

    def thanDxfCrTstyle(self, fName, fFontFileName):
        """Creates a text style entry in the dxf file.

        fName        : Text Style name
        fFontFileName: Font filename. If it has ".shx" extension, then it is
                       defined as complex linestyle.
        """

        self.thanDxfWrEntry(0, 'STYLE')
        self.thanDxfWrEntry(2, fName)

        (filnam, ext) = splitext(fName)
        if ext.lower() == ".shx":
            self.thanDxfWrEntry(70, 1)
        else:
            self.thanDxfWrEntry(70, 0)

        self.thanDxfWrEntry(40, 0.0)
        self.thanDxfWrEntry(41, 1.0)
        self.thanDxfWrEntry(50, 0.0)
        self.thanDxfWrEntry(71, 0.0)
        self.thanDxfWrEntry(42, 0.2)
        self.thanDxfWrEntry(3, fFontFileName)

#======================================================================

    def thanDxfCrBlock(self, bFileName):
        """Creates a block entry in the dxf file.

        The block definition in the dxf file must not include
        code 5 (handle), because Intellicad has trouble with it
        (it may be either Intellicad's dxfin bug, or Autocad's
        dxfout bug.
        ThanCad is indifferent (it does not support blocks yet ;) )."""

#        fpath = '\\50SAMBA\RUNPROGS\EXE\PHUT\'
#        fpath = '\\\\50SAMBA\\RUNPROGS\\EXE\\PHUT\\'
        fpath = "//50samba/runprogs/exe/phut/"

        try:            fBlo = open(fpath+bFileName+".dxf", "r")
        except IOError: fBlo = None
        if fBlo is None:
            try:            fBlo = open(bFileName+".dxf", "r")
            except IOError: return 1
        ierr = thanDxfCrBlock2(fBlo)
        fBlo.close()
        return ierr


    def thanDxfCrBlock2(self, fBlo):
        """Creates a block entry in the dxf file, from an opened file name or an iterable."""
        wr = self.thanFdxf.write
        try:
            for dline in fBlo: wr(dline)
        except IOError: ierr = 1
        else:           ierr = 0
        return ierr


    def thanDxfDef(self, linetypes=None, textstyles=None, layers=None, blocks=None):
        "Create definitions headers."
        self.thanDxfTableDef (' ', 0)

        if linetypes is None: linetypes = {}
        linetypes.setdefault('CONTINUOUS', ('Solid Line',        ()            ))
        linetypes.setdefault('DOTR',       ('.................', (0, -0.06)    ))
        linetypes.setdefault('DASHED2',    ('- - - - - - - - -', (0.25, -0.125)))
        self.thanDxfTableDef('LTYPE', len(linetypes))
        for nam, args in linetypes.items():  #OK for python 2,3
            self.thanDxfCrLtype(nam, *args)

        if textstyles is None: textstyles = {}
        textstyles.setdefault('GRSTYLE', ('GRSIMPW',))
        self.thanDxfTableDef ('STYLE', len(textstyles))
        for nam, args in textstyles.items():  #OK for python 2,3
            self.thanDxfCrTstyle(nam, *args)

        if layers is None: layers = {}
        layers.setdefault('0', (7, 'CONTINUOUS'))
        self.thanDxfTableDef('LAYER', len(layers))
        for nam, args in layers.items():  #OK for python 2,3
            self.thanDxfCrLayer(nam, *args)

        if blocks is None: blocks = {}
        blocks.setdefault('MODEL', ())
        self.thanDxfTableDef('BLOCKS', len(blocks))
        for nam, args in blocks.items():  #OK for python 2,3
            ierr = self.thanDxfCrBlock(nam, *args)
            if ierr != 0: print(' Block "%s" not defined.' % nam)

        self.thanDxfTableDef ('ENTITIES', 1)


def defDxf(dxf):
    "Example of initial definition."

    dxf.thanDxfTableDef (' ', 0)

#---Line types

    dxf.thanDxfTableDef('LTYPE', 3)
    dxf.thanDxfCrLtype('CONTINUOUS', 'Solid Line',        ( ))
    dxf.thanDxfCrLtype('DOTR',       '.................', (0, -0.06))
    dxf.thanDxfCrLtype('DASHED2',    '- - - - - - - - -', (0.25, -0.125))

#---Text styles

    dxf.thanDxfTableDef ('STYLE', 1)
    dxf.thanDxfCrTstyle ('GRSTYLE', 'GRSIMPW')

#---Layers

    deflayers(dxf)
    defthanlayers(dxf)

#---Blocks

    dxf.thanDxfTableDef('BLOCKS', 1)
    ierr = dxf.thanDxfCrBlock('MODEL')
    if ierr != 0: print(' Block "MODEL" not defined.')

    dxf.thanDxfTableDef ('ENTITIES', 1)

def deflayers(dxf):
    dxf.thanDxfTableDef('LAYER', 18)
    dxf.thanDxfCrLayer('YL',         15, 'CONTINUOUS', frozen=True, locked=True,
                        off=True, noplot=True, lineweight=1.06)
    dxf.thanDxfCrLayer('YX') # ,          6, 'CONTINUOUS')
    dxf.thanDxfCrLayer('Y0',          6, 'CONTINUOUS')
    dxf.thanDxfCrLayer('BRK',        15, 'CONTINUOUS')
    dxf.thanDxfCrLayer('SH',          3, 'CONTINUOUS')
    dxf.thanDxfCrLayer('HS',          1, 'CONTINUOUS')
    dxf.thanDxfCrLayer('OS',          1, 'CONTINUOUS')
    dxf.thanDxfCrLayer('OST',         2, 'CONTINUOUS')
    dxf.thanDxfCrLayer('OSOR',        2, 'CONTINUOUS')
    dxf.thanDxfCrLayer('OXOR',        3, 'CONTINUOUS')
    dxf.thanDxfCrLayer('KA',          3, 'CONTINUOUS')
    dxf.thanDxfCrLayer('AER_CON_HS',  1, 'CONTINUOUS')
    dxf.thanDxfCrLayer('AER_CON_OST', 2, 'CONTINUOUS')
    dxf.thanDxfCrLayer('AER_PAS_HS',  1, 'CONTINUOUS')
    dxf.thanDxfCrLayer('AER_PAS_OST', 2, 'CONTINUOUS')
    dxf.thanDxfCrLayer('AER_VEC_HS',  1, 'CONTINUOUS')
    dxf.thanDxfCrLayer('AER_VEC_OST', 2, 'CONTINUOUS')
    dxf.thanDxfCrLayer('AER_MOD',     3, 'CONTINUOUS')

def defthanlayers(dxf):
    dxf.thanDxfTableDef('THANCAD_LAYER', 18)
    dxf.thanDxfCrThanLayer('YL',         color=15, linetype='CONTINUOUS',
                           frozen=True, locked=True,
                           off=True, noplot=True, lineweight=1.06)
    dxf.thanDxfCrThanLayer('YX') # ,          6, 'CONTINUOUS')
    dxf.thanDxfCrThanLayer('Y0',          color=6, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('BRK',        color=15, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('SH',         color= 3, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('HS',         color= 1, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('OS',         color= 1, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('OST',        color= 2, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('OSOR',       color= 2, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('OXOR',       color= 3, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('KA',         color= 3, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('AER_CON_HS', color= 1, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('AER_CON_OST',color= 2, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('AER_PAS_HS', color= 1, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('AER_PAS_OST',color= 2, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('AER_VEC_HS', color= 1, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('AER_VEC_OST',color= 2, linetype='CONTINUOUS')
    dxf.thanDxfCrThanLayer('AER_MOD',    color= 3, linetype='CONTINUOUS')


def test():
    "Creates a small drawing and saves it to .dxf format."
    dxf = ThanDxfPlot()

    dxf.thanDxfPlots1()
    defDxf(dxf)
    dxf.thanDxfSetLayer("GRAMMES")

    dxf.thanDxfPlot(0,  0,  3)
    dxf.thanDxfPlot(10, 10, 2)

    dxf.thanDxfPlotCircle(0, 0, 10)
    dxf.thanDxfPlotPolyline([-5, 6, -7], [-10, 0, 10])
    dxf.thanDxfPlotImage("q1.bmp", 0.0, 10.0, 1.0, 90.0)

    dxf.thanDxfPlot(0, 0, 999)


if __name__ == "__main__": test()
