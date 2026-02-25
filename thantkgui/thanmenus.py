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

This module defines the menus and the mechanism to create and update them.
"""
import p_ggen, p_gtkwid
import thanopt
from thanvers import tcver
from thantrans import T, Tmatch, Tphot, Tarch, Tcivil, Turban


class ThanCadTkMenu(object):
    "It creates ThanCad menu system and modifies it if necessary."

    def __init__(self, win, main=False):
        "Create the menu system."
        if main: seq, menus = thanopt.thanmenus2.thanSeqMain, thanopt.thanmenus2.thanMenusMain
        else:    seq, menus = thanopt.thanmenus2.thanSeq, thanopt.thanmenus2.thanMenus
        S = p_ggen.ThanStub
        B = win.thanGudCommandBegin
        ms = []
        for m in seq:
            for ent in menus[m]:
                if len(ent) >= 3 and ent[0] != "menu":
                    ent = list(ent)
                    ent[0] = S(B, ent[0])
                ms.append(ent)
        if main: menubar, self.__submenus = p_gtkwid.thanTkCreateThanMenus2(win, ms)
        else:    menubar, self.__submenus = p_gtkwid.thanTkCreateThanMenus2(win, ms, win.thanStatusBar.thanInfoSet)
        win["menu"] = menubar
        if not main:
            self.__submenus["File"]   = self.__submenus[T["&File"].replace("&", "")]
            self.__submenus["Window"] = self.__submenus[T["&Window"].replace("&", "")]

        self.__irecent = len(self.__submenus["File"])      #This may be none if tk has not yet initialized
        if self.__irecent is not None: self.__irecent -= 2 #Position in file menu where new recent file will be inserted
        self.__recent = []                       #Paths of all recent files
        self.__iopened = 0                       #Position in file menu where new opened file will be inserted
        self.__opened = []                       #String representation of all opened projects


    def thanAddRecent(self, proj, fpath, MAXRECENT):
        "Adds a new recent file to the file menu."
        import thancom
        fmenu = self.__submenus["File"]
        if self.__irecent is None: self.__irecent = len(fmenu) - 2  #Position in file menu where new recent file will be inserted
        n = len(self.__recent)
        try: i = self.__recent.index(fpath)      #fpath is already in menu
        except ValueError: i = -1                #fpath is not in menu
        if   i >= 0:         self.__delRecent(i) #Delete fpath from menu if already in the menu
        elif n >= MAXRECENT: self.__delRecent(MAXRECENT-1)  #Delete oldest recent file from file menu
        def op():
            nopened = thancom.thancomfile.thanFileOpenPaths(proj, [fpath])
            if not proj[1]: return #in case proj is ThanCad and not another drawing
            if nopened > 0:
                proj[2].thanGudCommandEnd()
            else:
                proj[2].thanGudCommandEnd("\n"+T["No file was opened."], "can")
        fmenu.insert_command(self.__irecent, label=fpath.name, foreground="blue",
            command=op, help=fpath)              #Insert fpath as the newest recent file
        self.__recent.insert(0, fpath)           #Save fpath


    def __delRecent(self, i):
        "Deletes a recent file entry by index."
        assert 0 <= i < len(self.__recent)
        del self.__recent[i]
        fmenu = self.__submenus["File"]
        fmenu.delete(self.__irecent+i)


    def thanAddOpened(self, projnew):
        "Adds a new (currently) opened project to the window menu."
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


    def __del__(self): print("ThanCadTkMenu", self, "dies.")


def thanStandardMenus(B):
        "Creates a description of the desired menus in a list."
        thanFrape = thanopt.thancon.thanFrape
        S = p_ggen.ThanStub
        s = "File Edit View Image Format Tools Draw Engineering Photogrammetry Modify Research Developer Window Help".split()
        if not thanFrape.photo and not thanFrape.stereo: s.remove("Photogrammetry")
        m = {}
        m["File"] = \
        [ ("menu", T["&File"], ""),            # Menu Title
          (S(B, "new"),    T["&New"],     T["Makes an empty drawing"]),
          (S(B, "open"),   T["&Open"],    T["Opens an existing drawing"]),
          (S(B, "openunload"), T["Open &without images"], T["Opens an existing drawing with the images unloaded"]),
          (S(B, "save"),   T["&Save"],    T["Saves drawing into a file"]),
          (S(B, "saveas"), T["S&ave as"], T["Saves drawing into a file"]),
          (S(B, "close"),  T["&Close"],   T["Closes current drawing"]),
          ("-",),               # Separator
          (S(B, "insert"), T["Ins&ert"],    T["Inserts other drawings into current drawing"]),
#          (S(B, "insertunload"), T["Insert &without images"], T["Inserts a drawing with the images unloaded"]),
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
          (S(B, "quit"), T["E&xit"], "Terminate "+tcver.name, "darkred"),
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
          ("-",),               # Separator
          (S(B, "background"),T["&Background colour"],    T["Changes the canvas background colour"]),
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
          (S(B, "imageattach"), T["Insert Raster &Image"], T["Inserts a new image to the current drawing"]),
          (S(B, "imagegeo"),    T["Import &GeoTIFF"],   T["Inserts TIFF images whose georeference is inside the TIFF"]),
          (S(B, "imagetfw"),    T["Import &tfw Image"], T["Inserts TIFF images whose georeference is defined in .tfw files"]),
          (S(B, "imagelog"),    T["Import &log Image"], T["Inserts BMP images whose georeference is defined in .log files"]),
          (S(B, "imagecadastre"), T["Import &Cadastre"],T["Inserts Greek cadastre map image to its correct position using standardised file naming conventions"]),
          (S(B, "imagetiles"),  T["Import tiled Image"],T["Inserts a Digital Globe image split into multiple tiles"]),
          (S(B, "imagescan"),   T["&Scan Image"],       T["Acquires image from scanner"]),
          (S(B, "imageframe"),  T["Image &frame"],      T["Displays or not frames around images"]),
          ("-",),               # Separator
          (S(B, "imageunload"), T["Unload images"],     T["Hides the content of images and conserves memory"]),
          (S(B, "imageload"),   T["Load images"],       T["Reshows the content of the image allocating memory"]),
          (S(B, "imagelocate"), T["Locate image file"], T["Locates the image file of an image"]),
          (S(B, "imagedirectory"), T["Locate image directory"], T["Locates the directory for missing image files"]),
          (S(B, "imageembed"),  T["Embed images"],      T["Saves the images into ThanCad's native file (.thcx)"]),
          ("-",),               # Separator
          (S(B, "imageclip"),   T["&Clip image"],       T["Clips an image to a smaller rectangle"]),
          (S(B, "imagerender"), T["Image &Render"],     T["Manages the mode or rendering images"]),
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
          (S(B, "interpolate"),T["&Interpolate line"], "Adds points to a line with sparse nodes"),
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
          (S(B, "ellipse"),   T["&Ellipse"],   "Draws an ellipse"),
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
            [ (S(B, "EngMapRect"),Tphot["&Rectify Map"], Tphot["Rectifies a raster topographic map"]),
              (S(B, "enggeoreference"),Tphot["G&eoreference Image"], Tphot["Image georeferencing with control points"]),
              (S(B, "engorthoimage"),Tphot["&Orthoimage GDEM"], Tphot["Image orthorectification using global DEM"]),
            ])
        m1.extend(
        [ (S(B, "EngTrace"),  T["&Trace"],           T["Traces a curve in a bitmap raster image"]),
          (S(B, "greeceperimeter"), T["Draw &Greece"], T["Draws the perimeter of Greece in EGSA87 coordinates"]),
          ("-",),
          (S(B, "demload"),   T["Load DE&Ms"],       T["Loads DEMs (USGS format) stored in .tif files"]),
          (S(B, "dem"),       T["Manage DE&Ms"],     T["Manages DEMs (USGS format) stored in .tif files"]),
          (S(B, "demdirectory"), T["Locate DEM directory"], T["Locates the directory for missing files of DEMs"]),
          (S(B, "dtmmake"),   T["Create &DTM"],      T["Creates a DTM from 3D lines"]),
          (S(B, "dtmz"),      T["DTM/DEM &Z"],       T["Computes and shows the z coordinate at an arbitrary point"]),
          (S(B, "dtmpoints"), T["Add Z to &Points"], T["Supplies z coordinates to existing points"]),
          (S(B, "dtmline"),   T["Add Z to &Lines"],  T["Supplies z coordinates to existing polylines"]),
          (S(B, "triangulation"), T["Tr&iangulation"],T["Creates and manages triangulation from (2D) points and lines."]),
          ("-",),
        ])
        if thanFrape.civil:
            m1.append((S(B, "engprofile"),      T["Engineering Pro&file"], T["Creates an engineering drawing with the profile of a (3D) line"]))
        m1.extend(\
        [ (S(B, "engquickprofile"), T["&Quick Profile"], T["Creates quickly the profile of a (3D) line"]),
          (S(B, "EngInterchange"),  T["&Interchange"],   T["Creates an interchange between 2 highways"]),
        ])
        if thanFrape.urban:
            m1.extend(\
            [ ("-",),
              (S(B, "urbanbioazimuth"), Tarch["Bio a&zimuth"], Tarch["Computes the azimuth of a road network to test bioclimatic design of city plan"]),
              (S(B, "urbanslope"),      Turban["&Locate roads of slope"], Turban["Locates roads (lines) whose slope is less than arbitrary threshold"]),
            ])
        if thanFrape.architect:
            m1.extend(\
            [ ("-",),
              (S(B, "archstairs"), Tarch["&Stairs"], Tarch["Computes and draws the plan view of a simple staircase"]),
            ])
        m1.append(("endmenu",))

        if thanFrape.photo:
            m["Photogrammetry"] = m1 =\
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
          ]
            if thanFrape.stereo:
                m1.extend(\
                [ ("-",),
                  (S(B, "stereotoggle"),  Tphot["&Stereo toggle"],  Tphot["Sets stereo (blue/red) mode on and off"]),
                  (S(B, "stereoaverage"), Tphot["&Stereo average"], Tphot["Zooms the z coordinates so that they are easily visible"]),
                  (S(B, "stereogridtoggle"),  Tphot["&Stereo grid"],  Tphot["Sets a grid at the reference elevation on and off to aid stereo viewing"]),
                ])
            m1.append(("endmenu",))
        elif thanFrape.stereo:
            m["Photogrammetry"] = m1 =\
            [ ("menu", Tphot["&Photogrammetry"], ""),        # Menu Title
              (S(B, "stereotoggle"),  Tphot["&Stereo toggle"],  Tphot["Sets stereo (blue/red) mode on and off"]),
              (S(B, "stereoaverage"), Tphot["&Stereo average"], Tphot["Zooms the z coordinates so that they are easily visible"]),
              (S(B, "stereogridtoggle"),  Tphot["&Stereo grid"],  Tphot["Sets a grid at the reference elevation on and off to aid stereo viewing"]),
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
          (S(B, "extend"),     T["Extend"],        T["Extends lines and arcs until they cross other elements being the boundary edges"]),
          (S(B, "fillet"),     T["&Fillet"],       T["Cuts elements with other elements being the cutting edges"]),
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
          (S(B, "EduRectangle"), Tarch["Mark &Region"],   Tarch["Draws an active rectangle which contains comments"]),
          (S(B, "EduEdit"),      Tarch["&Edit Region"],   Tarch["Edits the comments of an active rectangle"]),
        ]
        if thanFrape.fflf:
            m1.extend(\
            [ ("-",),
              (S(B, "EduMatch2"),     Tmatch["&Match 2d"],         Tmatch["Matches two 2d polylines"]),
              (S(B, "EduMatch23"),    Tmatch["&Match 3d to 2d"],   Tmatch["Matches one 3d polyline to one 2d polylines"]),
              (S(B, "EduMatch3"),     Tmatch["&Match 3d"],         Tmatch["Matches two 3d polylines"]),
              (S(B, "EduMatchSplines3d"), Tmatch["&Match 3d splines"], Tmatch["Matches two 3d cubic splines"]),
              ("-",),
              (S(B, "EduMatchMult2"), Tmatch["&Match multiple 2d"],Tmatch["Matches two sets of 2d polylines"]),
              (S(B, "EduMatchMult23"),Tmatch["&Match multiple 3d to 2d"],Tmatch["Matches one set of 3d polylines to one set of 2d polylines"]),
              (S(B, "EduAxis"),       Tmatch["&Mid axis"],         Tmatch["Computes middle axis of road given the road edges"]),
              ("-",),
              (S(B, "edutransf"),     Tmatch["&Compute projection"], Tmatch["Computes a projection transformation using control points"]),
              (S(B, "eduproject"),    Tmatch["&Project/transform"], Tmatch["Projects/transforms arbitrary ThanCad Elements using a known transform (2D-2D, 3D-2D, 3D-3D"]),
            ])
        m1.extend(\
        [ ("-",),
          (S(B, "edufloorplan"),  Tarch["&Floor plan"],    Tarch["Creates automatically a floor plan"]),
          (S(B, "edubiocityplan"),Tarch["&Bio city plan"], Tarch["Creates bioclimatic oriented city plan"]),
        ])
        if thanFrape.thermo:
            m1.extend(\
            [ (S(B, "thermohumid"), u"Εισαγωγή μετρήσεων θερμοϋγρομέτρου", u"Διπλωματική εργασία Χάρη Πατούνη, Νίκου Σίμου, Σχολή Πολ. Μηχανικών, ΕΜΠ, 2012"),
            ])
        if thanFrape.civil:
            m1.extend(\
            [ ("-",),
              (S(B, "gradeline"), Tcivil["&Grade line"], Tcivil["Computes automatically the grade line of a road profile"]),
            ])
        m1.extend(\
        [ ("endmenu",),
        ])

        m["Developer"] = \
        [ ("menu", T["D&eveloper"], ""),          # Menu Title
          (S(B, "devfont"),  T["Show &font"],         T["Shows font for debugging"]),
          (S(B, "devcm"),    T["Show &dimensions"],   T["Shows window dimensions for debugging"]),
          (S(B, "devcmd"),   T["&Save CMD text"],     T["Saves the text of the command window"]),
          (S(B, "devtrans"), T["&Translation report"],T["Saves translation status to a file"]),
          (S(B, "devhandle"),T["Show &handles"],      T["Shows element handles for debugging"]),
          ("-",),
          (S(B, "fractal"),  T["F&ractal demo"],      T["Demonstrates a fractal made of colored lines"]),
          ("-",),
          (S(B, "tests"),    T["Run &tests"],         T["Runs unit tests of ThanCad"]),
          ("endmenu",),
        ]


        m["Window"] = \
        [ ("menu", T["&Window"], ""),          # Menu Title
#       m.append((self.thanParent.thanGudSetFocus, tcver.name, tcver.name+" main window"))
#        for w, f in thanfiles.getOpened():
#            m.append((w.thanGudSetFocus, f, f))
          ("endmenu",),
        ]

        m["Help"] = \
        [ ("menu", T["&Help"], "", None, "help"),            # Menu Title
          (S(B, "help"),  T["&Introduction"], "Introduction to "+tcver.name),
          (S(B, "gpl"),   T["&GPL"],          "Gnu General Public License"),
          (S(B, "language"), "&Language",     "Change the language of ThanCad's interface"),
          (S(B, "about"), T["&About"],        "Information about "+tcver.name),
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
          (S(B, "quit"), "E&xit", "Terminate "+tcver.name, "darkred"),
          ("endmenu",),
        ]

        m["Window"] = \
        [ ("menu", "&Window", ""),          # Menu Title
#       m.append((self.thanParent.thanGudSetFocus, tcver.name, tcver.name+" main window"))
#        for w, f in thanfiles.getOpened():
#            m.append((w.thanGudSetFocus, f, f))
          ("endmenu",),
        ]

        m["Help"] = \
        [ ("menu", "&Help", ""),            # Menu Title
          (S(B, "help"),  "&Introduction", "Introduction to "+tcver.name),
          (S(B, "gpl"),   "&GPL",          "Gnu General Public License"),
          (S(B, "about"), "&About",        "Information about "+tcver.name),
          ("endmenu",),
        ]
        return s, m

if __name__ == "__main__":
    tcver = p_ggen.Struct()
    tcver.name = "GREAT ThanCad"
    thanMenusSeq, thanMenus = thanStandardMenus()
    for m in thanMenusSeq: assert m in thanMenus
    for m in thanMenus: assert m in thanMenusSeq
    print(thanMenusSeq)
    for m in thanMenusSeq:
        print(m)
        for mm in thanMenus[m]: print("      ", mm)
