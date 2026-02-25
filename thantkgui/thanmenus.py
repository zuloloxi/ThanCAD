# -*- coding: iso-8859-7 -*-

##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

This module defines the menus and the mechanism to create and update them.
"""
import p_ggen, p_gtkuti
import thanvers, thanopt
from thantrans import T, Tmatch, Tphot,Tarch


class ThanCadTkMenu:
    "It creates ThanCad menu system and modifies it if necessary."

    def __init__(self, win, main=False):
        "Create the menu system."
        if main: seq, menus = thanMainMenus(win.thanGudCommandBegin)
        else:    seq, menus = thanStandardMenus(win.thanGudCommandBegin)
        ms = []
        for m in seq: ms.extend(menus[m])
        menubar, self.__submenus = p_gtkuti.thanTkCreateThanMenus2(win, ms)
        win["menu"] = menubar
        if not main:
            self.__submenus["File"]   = self.__submenus[T["&File"].replace("&", "")]
            self.__submenus["Window"] = self.__submenus[T["&Window"].replace("&", "")]

        self.__irecent = len(menus["File"]) - 4  #Position in file menu where new recent file will be inserted
        self.__recent = []                       #Paths of all recent files
        self.__iopened = 0                       #Position in file menu where new opened file will be inserted
        self.__opened = []                       #String representation of all oepned projects


    def thanAddRecent(self, proj, fpath, MAXRECENT):
        "Adds a new recent file to the file menu."
        import thancom
        fmenu = self.__submenus["File"]
        n = len(self.__recent)
        try: i = self.__recent.index(fpath)      #fpath is already in menu
        except ValueError: i = -1                #fpath is not in menu
        if   i >= 0:         self.__delRecent(i) #Delete fpath from menu if already in the menu
        elif n >= MAXRECENT: self.__delRecent(MAXRECENT-1)  #Delete oldest recent file from file menu
        def op():
            thancom.thancomfile.thanFileOpenPaths(proj, [fpath])
            if proj[1]: proj[2].thanGudCommandEnd()    #in case proj is ThanCad and not another drawing
        fmenu.insert_command(self.__irecent, label=fpath.name, foreground="blue",
            command=op, help=fpath)              #Insert fpath as the newset recent file
        self.__recent.insert(0, fpath)           #Save fpath


    def __delRecent(self, i):
        "Deletes a recent file entry by index."
        assert 0 <= i < len(self.__recent)
        del self.__recent[i]
        fmenu = self.__submenus["File"]
        fmenu.delete(self.__irecent+i)


    def thanAddOpened(self, projnew):
        "Adds a new (cuurently) opened project to the window menu."
        wmenu = self.__submenus["Window"]
        wmenu.add_command(label=projnew[0].name,
            command=lambda win=projnew[2]: win.thanTkSetFocus(), help=projnew[0])
        self.__opened.append(str(projnew))


    def thanDelOpened(self, proj):
        "Deletes a previously opened project from the window menu."
        wmenu = self.__submenus["Window"]
        i = self.__opened.index(str(proj))
        wmenu.delete(self.__iopened+i)
        del self.__opened[i]


    def __del__(self): print "ThanCadTkMenu", self, "dies."


def thanStandardMenus(B):
        "Creates a description of the desired menus in a list."
        thanFrape = thanopt.thancon.thanFrape
        S = p_ggen.ThanStub
        s = "File Edit View Image Format Tools Draw Engineering Photogrammetry Modify Research Developer Window Help".split()
        if not thanFrape.photo: s.remove("Photogrammetry")
        m = {}
        m["File"] = \
        [ ("menu", T["&File"], ""),            # Menu Title
          (S(B, "new"),    T["&New"],     T["Makes an empty drawing"]),
          (S(B, "open"),   T["&Open"],    T["Opens an existing drawing"]),
          (S(B, "save"),   T["&Save"],    T["Saves drawing into a file"]),
          (S(B, "saveas"), T["S&ave as"], T["Saves drawing into a file"]),
          (S(B, "close"),  T["&Close"],   T["Closes current drawing"]),
          ("-",),               # Separator
          (S(B, "pilout"), T["Export &Image"], T["Exports a raster image"]),
          (S(B, "pdfout"), T["Plot to PDF"],   T["Plots the drawing to a PDF file"]),
          (S(B, "plot"),   T["&Plot"],         T["Plots the drawing to a printer"]),
          ("-",),
          (S(B, "purge"),  T["&Purge"], T["Removes unused items, such as layers, from drawing"]),
#
#-------recent files
#
          ("-",),               # Separator
          ("-",),
          (S(B, "quit"), T["E&xit"], "Terminate "+thanvers.thanCadName, "darkred"),
          ("endmenu",),
        ]

        m["Edit"] = \
        [ ("menu", T["&Edit"], ""),            # Menu Title
          (S(B, "Undo"),      T["&Undo"],                 "Reverses the most recent action: U"),
          (S(B, "Redo"),      T["&Redo"],                 "Reverses the effects of the previous UNDO or U command: REDO"),
          ("-",),               # Separator
          (S(B, "cutclip"),   T["Cu&t"],                  "Moves elements to Clipboard"),
          (S(B, "copyclip"),  T["&Copy"],                 "Copies elements to Clipboard"),
          (S(B, "copybase"),  T["C&opy with Base Point"], "Copies elements to Clipboard"),
          (S(B, "pasteclip"), T["&Paste"],                "Pastes elements from Clipboard"),
          (S(B, "pasteorig"), T["P&aste to Original Coordinates"], "Pastes elements from Clipboard"),
          ("-",),               # Separator
          (S(B, "select"),    T["&Select"], "Selects elements"),
          ("endmenu",),
        ]

        m["View"] = \
        [  ("menu", T["&View"], ""),           # Menu Title
          (S(B, "zoomwin"),     T["Zoom &Window"],    "Zooms into a window"),
          (S(B, "zoomall"),     T["Zoom &All"],       "Zooms to show entire drawing"),
          (S(B, "zoomsel"),     T["Zoom &Selection"], "Zooms to show all selected elements"),
          (S(B, "zoomrelative"),T["Zoom R&elative"],  "Zooms by factor relative to current window"),
          (S(B, "zoomrealtime"),T["&Zoom real time"], "Zooms dragging the mouse"),
          ("-",),               # Separator
          (S(B, "panrelative"), T["P&an Relative"],   "Moves the view window"),
          (S(B, "panrealtime"), T["&Pan real time"],  "Moves dragging the mouse"),
          ("-",),               # Separator
          (S(B, "redraw"),      T["&Redraw"],         "Regenerates screen"),
          (S(B, "regen"),       T["Re&gen"],          "Regenerates screen"),
          ("endmenu",),
        ]

        m["Image"] = \
        [ ("menu", T["&Image"], ""), # Menu Title
          (S(B, "imageattach"), T["Insert Raster &Image"], "Inserts a new image to the current drawing"),
          (S(B, "imagelog"),    T["Import &log Image"], "Inserts a new image whose position is defined in .logf file"),
          (S(B, "imagecadastre"), T["Import &Cadastre"], "Inserts Greek cadastre map image to the correct poistion using standardised naming conventions"),
          (S(B, "imagescan"),   T["&Scan Image"],       T["Acquires image from scanner"]),
          (S(B, "imageframe"),  T["Image &frame"],      T["Displays or not frames around images"]),
          ("-",),               # Separator
          (S(B, "imagelocate"), T["Locate image file"], "Locates the image file of an image"),
          (S(B, "imagedirectory"), T["Locate image directory"], "Locates the directory for missing image files"),
          ("-",),               # Separator
          (S(B, "imageclip"),   T["&Clip image"],       "Clips an image to a smaller rectangle"),
          (S(B, "imagerender"), T["Image &Render"],     "Manages the mode or rendering images"),
          ("endmenu",),
        ]

        m["Format"] = \
        [ ("menu", T["F&ormat"], ""),          # Layer Title
          (S(B, "ddlmodes"), T["&Layer"],      "Manipulates layers"),
          (S(B, "style"),    T["&Text Style"], "Manipulates text styles"),
          (S(B, "units"),    T["&Units"],      "Manipulates length and angle units"),
          ("endmenu",),
        ]

        m["Tools"] = \
        [ ("menu", T["&Tools"], ""),           # Menu Title
          (S(B, "dist"), T["&Distance"],  "Computes and displays the distance and angle between 2 points"),
          (S(B, "area"), T["&Area"],      "Computes and displays the area of a closed polygon defined by points"),
          (S(B, "angle"),T["&Angle"],     "Computes and displays the angle between 2 lines defined by 3 points"),
          (S(B, "id"),   T["&Id Point"],  "Displays the coordinates of a point"),
          (S(B, "list"), T["&List"],      "Displays information about an element"),
          (S(B, "elev"), T["&Elevation"], "Displays and sets default elevation"),
          (S(B, "elevn"),T["Elevation (higher dimensions)"], "Displays and sets default elevations of z and higher dimensions"),
          ("-",),
          (S(B, "dsettings"), T["Drafting &Settings"],  "Chooses the drafting modes end, mid etc."),
          (S(B, "find"),      T["&Find text"], "Zooms to a text containing user defined text string"),
          ("-",),
          (S(B, "centroid"),  T["&Find centroid"], "Finds the centroid of a set of lines"),
          (S(B, "hull"),      T["&Find convex hull"],   "Finds the convex hulls of a set of lines"),
          (S(B, "simplify"),  T["&Simplify line"], "Approximates the lines with fewer points"),
          ("-",),
          (S(B, "script"),  T["&Run script"], "Executes ThanCad commands from file"),
          ("endmenu",),
        ]

        m["Draw"] = \
        [ ("menu", T["&Draw"], ""),            # Menu Title
          (S(B, "line"),      T["&Line"],      "Draws a line"),
          (S(B, "rectangle"), T["&Rectangle"], "Draws a closed line in the shape of a rectangle"),
          (S(B, "polygon"),   T["&Polygon"],   "Draws a closed line in the shape of a polygon filled with colour"),
          (S(B, "circle"),    T["&Circle"],    "Draws a circle"),
          (S(B, "arc"),       T["&Arc"],       "Draws a circular arc"),
          (S(B, "point"),     T["&Point"],     "Draws a point"),
          (S(B, "dtext"),     T["&Text"],      "Draws text"),
          (S(B, "spline"),    T["Spl&ine"],    "Draws a cubic spline curve"),
          ("-",),
          (S(B, "pnamed"),    T["&Named Point"],"Draws a point with name"),
          (S(B, "road"),      T["R&oad"],       "Draws a road"),
          (S(B, "hatchopen"), T["Hatch Open"],  T["Create hatch between disjoint lines"]),
          ("-",),
          (S(B, "dimali"), T["&Dimension aligned"], "Draws a dimension aligned to coordinates"),
          ("-",),
          (S(B, "tospline"),  T["To spline"],   "Transfroms a line to cubic spline curve"),
          (S(B, "tocurve"),   T["To curve"],    "Transforms a line to a curve"),
          (S(B, "decurve"),   T["&Decurve"],    "Transforms curves to lines"),
          ("endmenu",),
        ]

        m["Engineering"] = m1 =\
        [ ("menu", T["&Engineering"], ""),        # Menu Title
          (S(B, "EngGrid"),   T["&Grid"],        "Draws an engineering grid"),
        ]
        if thanFrape.ortho:
            m1.extend(
            [ (S(B, "EngMapRect"),T["&Rectify Map"], "Rectifies a raster topographic map"),
            ])
        m1.extend(
        [ (S(B, "EngTrace"),  T["&Trace"],       "Traces a curve in a bitmap raster image"),
          ("-",),
          (S(B, "demload"),   T["Load DE&Ms"],    T["Loads DEMs (USGS format) stored in tif files"]),
          (S(B, "dem"),       T["Manage DE&Ms"],  T["Manages DEMs (USGS format) stored in tif files"]),
          (S(B, "demdirectory"), T["Locate DEM directory"], "Locates the directory for missing image files of DEMs"),
          (S(B, "dtmmake"),   T["Create &DTM"],   T["Creates a DTM from 3D lines"]),
          (S(B, "dtmz"),      T["DTM &Z"],        T["Computes and shows the z coordinate at an arbitrary point"]),
          (S(B, "dtmpoints"), T["Add Z to &Points"], T["Supplies z coordinates to existing points"]),
          (S(B, "dtmline"),   T["Add Z to &Lines"],  T["Supplies z coordinates to existing polylines"]),
          (S(B, "triangulation"), T["Triangulation"], T["Creates and manages triangulation from (2D) points and lines."]),
          ("-",),
        ])
        if thanFrape.civil:
            m1.append((S(B, "engprofile"),      T["Engineering Pro&file"], T["Creates an engineering drawing with the profile of a (3D) line"]))
        m1.extend(\
        [ (S(B, "engquickprofile"), T["&Quick Profile"], T["Creates quickly the profile of a (3D) line"]),
          (S(B, "EngInterchange"),  T["&Interchange"],   T["Creates an interchange between 2 highways"]),
          ("endmenu",),
        ])

        if thanFrape.photo:
          m["Photogrammetry"] = \
          [ ("menu", Tphot["&Photogrammetry"], ""),        # Menu Title
          ("menu", Tphot["INTERIOR ORIENTATION (&mm)"], Tphot["Interior orientation submenu"], "blue"),
          (S(B, "photimage"),     T["Insert Raster &Image"],     "Inserts an image in a predefined layer in mm"),
          (S(B, "photcosys"), Tphot["Image coordinate &system"], "Creates a non-cartesian coordinate system"),
          (S(B, "id"),        Tphot["&Measure image coordinates"],            "Displays the coordinates of a point"),
          ("endmenu",),
          ("menu", Tphot["&INTERIOR ORIENTATION (pixels)"],  Tphot["Interior orientation submenu"], "blue"),
          (S(B, "photintimage"),  T["Insert Raster &Image"], Tphot["Inserts an image in a predefined layer in pixels"]),
          (S(B, "photintcamera"), Tphot["Load &Camera"],     Tphot["Loads the calibrartion parameters of a metric camera"]),
          (S(B, "photinterior"),  Tphot["Compu&tation"],     Tphot["Computes the photogrammetric interior orientation of a metric image"]),
          ("endmenu",),
          (S(B, "photcamera"),Tphot["&Camera management"],Tphot["Edit/create photogrammetric camera parameters"]),
          ("-",),
          (S(B, "phot90"),    Tphot["Rotate Image &90 deg counterclokwise"],  ""),
          (S(B, "phot180"),   Tphot["Rotate Image &180 deg"],                 ""),
          (S(B, "phot270"),   Tphot["Rotate Image &270 deg counterclokwise"], ""),
          ("-",),
          (S(B, "imagebrighten"), Tphot["&Brighten Image (Gray+)"],           ""),
          (S(B, "imagedarken"),   Tphot["&Darken Image (Gray-)"],             ""),
          (S(B, "imagebreset"),   Tphot["&Reset Image brightness"],           ""),
          ("-",),
          (S(B, "photf6"),    Tphot["Toggle coordinates on/off (F6)"],        ""),
          (S(B, "photf7"),    Tphot["Toggle coordinate system (F7)"],         ""),
          ("-",),
          (S(B, "photmodel"),    Tphot["&Model definition"],     Tphot["Defines the images which make a photogrammetric model"]),
          ("endmenu",),
          ]

        m["Modify"] = \
        [ ("menu", T["&Modify"], ""),             # Menu Title
          (S(B, "erase"),      T["&Erase"],        T["Deletes selected elements"]),
          (S(B, "rotate"),     T["&Rotate"],       T["Rotates selected elements"]),
          (S(B, "scale"),      T["Sc&ale"],        T["Scales selected elements"]),
          (S(B, "move"),       T["&Move"],         T["Moves selected elements"]),
          (S(B, "copy"),       T["&Copy"],         T["Copies selected elements"]),
          (S(B, "mirror"),     T["M&irror"],       T["Mirrors selected elements with repect to 2d axis"]),
          ("-",),
          (S(B, "offset"),     T["&Offset"],       T["Copies object parallel to itself"]),
          (S(B, "break"),      T["&Break"],        T["Breaks an element into 2 pieces"]),
          (S(B, "trim"),       T["&Trim"],         T["Explode 1 or more elements to smaller objects"]),
          (S(B, "filet"),      T["&Filet"],        T["Cuts elements with other elements being the cutting edges"]),
          (S(B, "join"),       T["&Join"],         T["Joins 2 or more adjacent lines"]),
          (S(B, "join2d"),     T["Join &2D"],      T["Joins 2 or more adjacent lines"]),
          (S(B, "joingap"),    T["Join &gap"],     T["Joins 2 lines filling the gap between them."]),
          (S(B, "explode"),    T["E&xplode"],      T["Explode 1 or more elements to smaller objects"]),
          (S(B, "reverse"),    T["Re&verse"],      T["Reverses the orientation of lines, circles, arcs"]),
          (S(B, "ddedit"),     T["E&dit Text"],    T["Lets the user edit any text interactively"]),
          (S(B, "poedit"),     T["Edit named &Point"],   T["Lets the user edit any named point interactively"]),
          (S(B, "pointreplace"), T["Convert to named Poi&nt"], T["Lets the user convert points to named points interactively"]),
          ("-",),
          (S(B, "chprop"),     T["Change &layer"], T["Changes layer of selected elements"]),
          (S(B, "chelev"),     T["C&hange elevation"], T["Changes the z coordinate of selected elements"]),
          (S(B, "chelevn"),    T["Change elevation (higher dim)"], T["Changes the z and higher coordinates of selected elements"]),
          (S(B, "chelevcontour"), T["Change co&ntour line elevation"], T["Changes the z coordinate of many lines progressively"]),
          ("endmenu",),
        ]

        m["Research"] = m1 =\
        [ ("menu", T["&Research"], ""),           # Menu Title
          (S(B, "EduRectangle"), T["Mark &Region"],   "Draws a rectangle with comments"),
          (S(B, "EduEdit"),      T["&Edit"],          "Edit the comments"),
        ]
        if thanFrape.fflf:
            m1.extend(\
            [ ("-",),
              (S(B, "EduMatch2"),    Tmatch["&Match 2d"],      "Match 2d polylines"),
              (S(B, "EduMatch23"),   Tmatch["&Match 3d to 2d"],"Match 3d and 2d polylines"),
              (S(B, "EduMatch3"),    Tmatch["&Match 3d"],      "Match 3d polylines"),
              ("-",),
              (S(B, "EduMatchMult2"),Tmatch["&Match multiple 2d"],"Match multiple pairs of 2d polylines"),
              (S(B, "EduMatchMult23"),Tmatch["&Match multiple 3d to 2d"],"Match multiple pairs of 3d and 2d polylines"),
              (S(B, "EduAxis"),      Tmatch["&Mid axis"],         "Find middle axis of road given the edges"),
              ("-",),
              (S(B, "edutransf"),    Tmatch["&Compute transformation"], Tmatch["Computes a transformation from control points"]),
              (S(B, "eduproject"),   Tmatch["&Project 3d to 2d"], "Projects multiple 3D points to 2D using a known projection"),
            ])
        m1.extend(\
        [ ("-",),
          (S(B, "edufloorplan"),  Tarch["&Floor plan"],    "Create automatically a floor plan"),
          (S(B, "edubiocityplan"),Tarch["&Bio city plan"], "Create biocimatic orented city plan"),
          (S(B, "edubioazimuth"), Tarch["Bio a&zimuth"],   "Compute the azimuth of a road network to test bioclimatic design of city plan"),
        ])
        if thanFrape.civil:
            m1.extend(\
            [ ("-",),
              (S(B, "gradeline"), T["&Grade line"], "Compute automatically the grade line of a profile"),
            ])
        m1.extend(\
        [ ("endmenu",),
        ])

        m["Developer"] = \
        [ ("menu", T["D&eveloper"], ""),          # Menu Title
          (S(B, "devfont"),  T["Show &font"],         "Developer font debugging"),
          (S(B, "devcm"),    T["Show &dimensions"],   "Developer window debugging"),
          (S(B, "devcmd"),   T["&Save CMD text"],     "Save the text of the command window"),
          (S(B, "devtrans"), T["&Translation report"],"Save translation status to a file"),
          (S(B, "devhandle"),T["Show &handles"],      "Developer handle debugging"),
          ("-",),
          (S(B, "fractal"),  T["F&ractal demo"],      "Demonstrates a fractal made of colored lines"),
          ("-",),
          (S(B, "tests"),    T["Run &tests"],         "Run unit tests ofThanCad"),
          ("endmenu",),
        ]


        m["Window"] = \
        [ ("menu", T["&Window"], ""),          # Menu Title
#       m.append((self.thanParent.thanGudSetFocus, thanvers.thanCadName, thanvers.thanCadName+" main window"))
#        for w, f in thanfiles.getOpened():
#            m.append((w.thanGudSetFocus, f, f))
          ("endmenu",),
        ]

        m["Help"] = \
        [ ("menu", T["&Help"], "", None, "help"),            # Menu Title
          (S(B, "help"),  T["&Introduction"], "Introduction to "+thanvers.thanCadName),
          (S(B, "gpl"),   T["&GPL"],          "Gnu General Public License"),
          (S(B, "language"), "&Language",     "Change the language of ThanCad's interface"),
          (S(B, "about"), T["&About"],        "Information about "+thanvers.thanCadName),
          ("endmenu",),
        ]
        return s, m


def thanMainMenus(B):
        "Creates a description of the main window menus in a list."
        S = p_ggen.ThanStub
        s = "File Window Help".split()
        m = {}
        m["File"] = \
        [ ("menu", "&File", ""),            # Menu Title
          (S(B, "new"),    "&New",  "Makes an empty drawing"),
#          (S(B, "new"),    u"&Νέο Θανάσης",  "Makes an empty drawing"),
          (S(B, "open"),   "&Open", "Opens an existing drawing"),
          ("-",),               # Separator
          (S(B, "sykin"),  "&Import syk", "Imports a syk file"),
          (S(B, "dxfin"),  "Import &dxf", "Imports a dxf file"),
          (S(B, "sykout"), "&Export syk", "Exports a syk file"),
          (S(B, "dxfout"), "Export &dxf", "Exports a dxf file"),
          ("-",),               # Separator
#
#-------recent files
#
          ("-",),               # Separator
          (S(B, "quit"), "E&xit", "Terminate "+thanvers.thanCadName, "darkred"),
          ("endmenu",),
        ]

        m["Window"] = \
        [ ("menu", "&Window", ""),          # Menu Title
#       m.append((self.thanParent.thanGudSetFocus, thanvers.thanCadName, thanvers.thanCadName+" main window"))
#        for w, f in thanfiles.getOpened():
#            m.append((w.thanGudSetFocus, f, f))
          ("endmenu",),
        ]

        m["Help"] = \
        [ ("menu", "&Help", ""),            # Menu Title
          (S(B, "help"),  "&Introduction", "Introduction to "+thanvers.thanCadName),
          (S(B, "gpl"),   "&GPL",          "Gnu General Public License"),
          (S(B, "about"), "&About",        "Information about "+thanvers.thanCadName),
          ("endmenu",),
        ]
        return s, m

if __name__ == "__main__":
    import p_ggen
    thanvers = p_ggen.Struct()
    thanvers.thanCadName = "GREAT ThanCad"
    thanMenusSeq, thanMenus = thanStandardMenus()
    for m in thanMenusSeq: assert m in thanMenus
    for m in thanMenus: assert m in thanMenusSeq
    print thanMenusSeq
    for m in thanMenusSeq:
        print m
        for mm in thanMenus[m]: print "      ", mm
