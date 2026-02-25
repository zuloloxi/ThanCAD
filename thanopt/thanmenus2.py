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

This module defines the menus.
"""
import p_ggen
from .thancon import thanFrape
from thantrans import T, Tphot, Tarch, Turban, Tmatch, Tcivil
from thanvers import tcver


def thanStandardMenus2():
        "Creates a description of the desired menus in a list."
        s = "File Edit View Image Format Tools Draw Engineering Photogrammetry Modify Research Developer Window Help".split()
        s = [(s1, None, None) for s1 in s]
        if not thanFrape.photo and not thanFrape.stereo: s.remove("Photogrammetry")
        m = {}
        m["File"] = \
        [ ("menu", T["&File"], ""),            # Menu Title
          (("new"),    T["&New"],     T["Makes an empty drawing"]),
          (("open"),   T["&Open"],    T["Opens an existing drawing"]),
          (("openunload"), T["Open &without images"], T["Opens an existing drawing with the images unloaded"]),

          ("menu", T["Open spreadsheet"], ""),             # Sub Menu Title
          ("openspreadpoints", T["with &points"], T["Opens spreadsheets (ods,xls,xlsx) which contain points coordinates."]),
          ("openspreadlines",  T["with &lines"],  T["Opens spreadsheets (ods,xls,xlsx) which contain coordinates of lines."]),
          ("openspreadtexts",  T["with &texts"],  T["Opens spreadsheets (ods,xls,xlsx) which contain coordinates of texts."]),
          ("openspreadsurface",T["with &surface"],T["Opens spreadsheets (ods,xls,xlsx) which contain coordinates of surface."]),
          ("endmenu",),

          (("save"),   T["&Save"],    T["Saves drawing into a file"]),
          (("saveas"), T["S&ave as"], T["Saves drawing into a file"]),
          (("close"),  T["&Close"],   T["Closes current drawing"]),

          ("menu", T["Export to spreadsheet"], ""),             # Sub Menu Title
          ("exportspreadpoints", T["Export &points"], T["Exports ThanCad points to spreadsheets (ods,xls,xlsx)."]),
          ("exportspreadlines" , T["Export &lines"],  T["Exports ThanCad lines to spreadsheets (ods,xls,xlsx)."]),
          ("exportimages" ,      T["Export &images"], T["Exports ThanCad images to an autocad script (scr) file."]),
          ("endmenu",),
          ("exportimages" ,      T["Export &images"], T["Exports ThanCad images to an autocad script (scr) file."]),

          ("-",),               # Separator
          (("insert"), T["Ins&ert"],    T["Inserts other drawings into current drawing"]),
#          (("insertunload"), T["Insert &without images"], T["Inserts a drawing with the images unloaded"]),
          ("-",),               # Separator
          (("pilout"), T["Export to &Image"], T["Plots the drawing into a raster image"]),
          (("pdfout"), T["Plot to PDF"],   T["Plots the drawing to a PDF file"]),
          (("plot"),   T["&Plot"],         T["Plots the drawing to a printer"]),
          ("-",),
          (("purge"),  T["&Purge"], T["Removes unused items, such as layers, from drawing"]),
#
#-------recent files
#
          ("-",),               # Separator
          ("-",),
          (("quit"), T["E&xit"], "Terminate "+tcver.name, "darkred"),
          ("endmenu",),
        ]

        m["Edit"] = \
        [ ("menu", T["&Edit"], ""),            # Menu Title
          (("Undo"),      T["&Undo"],                 "Reverses the most recent action: U"),
          (("Redo"),      T["&Redo"],                 "Reverses the effects of the previous UNDO or U command: REDO"),
          ("-",),               # Separator
          (("cutclip"),   T["Cu&t"],                  "Moves elements to Clipboard"),
          (("copyclip"),  T["&Copy"],                 "Copies elements to Clipboard"),
          (("copybase"),  T["C&opy with Base Point"], "Copies elements to Clipboard"),
          (("pasteclip"), T["&Paste"],                "Pastes elements from Clipboard"),
          (("pasteorig"), T["P&aste to Original Coordinates"], "Pastes elements from Clipboard"),
          ("-",),               # Separator
          (("select"),    T["&Select"], "Selects elements"),
          ("-",),               # Separator
          (("background"),T["&Background colour"],    T["Changes the canvas background colour"]),
          (("encoding"),  T["&Encoding"],             T["Changes the encoding for reading/writing text files"]),
          ("endmenu",),
        ]

        m["View"] = \
        [  ("menu", T["&View"], ""),           # Menu Title
          (("zoomwin"),     T["Zoom &Window"],    "Zooms into a window"),
          (("zoomall"),     T["Zoom &All"],       "Zooms to show entire drawing"),
          (("zoomsel"),     T["Zoom &Selection"], "Zooms to show all selected elements"),
          (("zoomrelative"),T["Zoom R&elative"],  "Zooms by factor relative to current window"),
          (("zoomrealtime"),T["&Zoom real time"], "Zooms dragging the mouse"),
          ("-",),               # Separator
          (("panrelative"), T["P&an Relative"],   "Moves the view window"),
          (("panrealtime"), T["&Pan real time"],  "Moves dragging the mouse"),
          ("-",),               # Separator
          (("redraw"),      T["&Redraw"],         "Regenerates screen"),
          (("regen"),       T["Re&gen"],          "Regenerates screen"),
          ("endmenu",),
        ]
        m["Image"] = \
        [ ("menu", T["&Image"], ""), # Menu Title
          (("imageattach"),  T["Insert Raster &Image"], T["Inserts a new image to the current drawing"]),
          (("goi"),          T["Insert GOI &Frame"],    T["Insert one or more frames of global orthoimage"]),
          (("imagegeo"),     T["Import &GeoTIFF"],   T["Inserts TIFF images whose georeference is inside the TIFF"]),
          (("imagetfw"),     T["Import &tfw/j2w Image"], T["Inserts TIFF images whose georeference is defined in .tfw/.j2w files"]),
          (("imagelog"),     T["Import &log Image"], T["Inserts BMP images whose georeference is defined in .log files"]),
          (("imagecadastre"),T["Import &Cadastre"],T["Inserts Greek cadastre map image to its correct position using standardised file naming conventions"]),
          (("imagetiles"),   T["Import tiled Image"],T["Inserts a Digital Globe image split into multiple tiles"]),
          (("imageterrasar"),T["Import/convert TerraSAR Image"], T["Converts a complex pixel valued TerraSAR image to GeoTiff and inserts it to the current drawing."]),
          (("imagescan"),    T["&Scan Image"],       T["Acquires image from scanner"]),
          (("imageframe"),   T["Image &frame"],      T["Displays or not frames around images"]),
          ("-",),               # Separator
          (("imageunload"), T["Unload images"],     T["Hides the content of images and conserves memory"]),
          (("imageload"),   T["Load images"],       T["Reshows the content of the image allocating memory"]),
          (("imagelocate"), T["Locate image file"], T["Locates the image file of an image"]),
          (("imagedirectory"), T["Locate image directory"], T["Locates the directory for missing image files"]),
          (("imageembed"),  T["Embed images"],      T["Saves the images into ThanCad's native file (.thcx)"]),
          ("-",),               # Separator
          (("imageclip"),   T["&Clip image"],       T["Clips an image to a smaller rectangle"]),
          (("imagerender"), T["Image &Render"],     T["Manages the mode of rendering images"]),
          ("endmenu",),
        ]

        m["Format"] = \
        [ ("menu", T["F&ormat"], ""),          # Layer Title
          (("ddlmodes"), T["&Layer"],      "Manipulates layers"),
          (("style"),    T["&Text Style"], "Manipulates text styles"),
          (("dimstyle"), T["&Dimension Style"], "Manipulates dimension styles"),
          (("units"),    T["&Units"],      "Manipulates length and angle units"),
          ("endmenu",),
        ]

        m["Tools"] = \
        [ ("menu", T["&Tools"], ""),           # Menu Title
          (("dist"), T["&Distance"],  "Computes and displays the distance and angle between 2 points"),
          (("area"), T["&Area"],      "Computes and displays the area of a closed polygon defined by points"),
          (("angle"),T["A&ngle"],     "Computes and displays the angle between 2 lines defined by 3 points"),
          (("id"),   T["&Id Point"],  "Displays the coordinates of a point"),
          (("list"), T["&List"],      "Displays information about an element"),
          (("elev"), T["&Elevation"], "Displays and sets default elevation"),
          (("elevn"),T["Elevation (higher dimensions)"], "Displays and sets default elevations of z and higher dimensions"),
          (("highlightzero"),T["&Highlight zero elevation"], "Temporarily highlights lines and points the elevation of which is zero"),
          ("-",),
          (("dsettings"), T["Drafting &Settings"],  "Chooses the drafting modes end, mid etc."),
          (("find"),      T["&Find text"], "Zooms to a text containing user defined text string"),
          ("-",),
          (("centroid"),  T["&Find centroid"], "Finds the centroid of a set of lines"),
          (("hull"),      T["&Find convex hull"],   "Finds the convex hulls of a set of lines"),
          (("simplify"),  T["&Simplify line"], "Approximates the lines with fewer points"),
          (("interpolate"),T["&Interpolate line"], "Adds points to a line with sparse nodes"),
          (("optline"),   T["&Optimum line"], T["Finds optimum line that pass through points, lines, spline"]),
          ("-",),
          (("script"),  T["&Run script"], "Executes ThanCad commands from file"),
          ("endmenu",),
        ]

        m["Draw"] = \
        [ ("menu", T["&Draw"], ""),            # Menu Title
          (("line"),      T["&Line"],      "Draws a line"),
          (("rectangle"), T["&Rectangle"], "Draws a closed line in the shape of a rectangle"),
          (("polygonirregular"), T["&Polygon"],   "Draws a closed line in the shape of a polygon filled with colour"),
          (("polygon"),   T["Re&gular polygon"],   "Draws a closed line in the shape of a reular polygon"),
          (("circle"),    T["&Circle"],    "Draws a circle"),
          (("arc"),       T["&Arc"],       "Draws a circular arc"),
          (("ellipse"),   T["&Ellipse"],   "Draws an ellipse"),
          (("point"),     T["&Point"],     "Draws a point"),
          (("dtext"),     T["&Text"],      "Draws text"),
          (("spline"),    T["Spl&ine"],    "Draws a cubic spline curve"),
          ("-",),
          (("pnamed"),    T["&Named Point"],"Draws a point with name"),
          (("pointdistance"), T["Point from dist"], T["Draws a point whose distance from 2 reference points is known"]),
          (("road"),      T["R&oad"],       "Draws a road"),
          (("bhatch"),    T["&Boundary hatch"],  T["Creates hatch in closed areas"]),
          (("hatchopen"), T["Hatch Open"],  T["Creates hatch between disjoint lines"]),
          ("-",),
          (("dimali"), T["&Dimension aligned"], "Draws a dimension aligned to coordinates"),
          ("-",),
          (("tospline"),  T["To spline"],   "Transfroms a line to cubic spline curve"),
          (("tocurve"),   T["To curve"],    "Transforms a line to a curve"),
          (("decurve"),   T["&Decurve"],    "Transforms curves to lines"),
          (("topolygon"), T["To polygon"],  "Closes and transforms lines to polygons"),
          ("menu", T["BIM"], ""),             # Sub Menu Title
              ("bimcolumn", T["&Column"], T["Draws the cross section of a named structural column."]),
          ("endmenu",),

          ("endmenu",),
        ]

        m["Engineering"] = m1 =\
        [ ("menu", T["&Engineering"], ""),        # Menu Title
          (("EngGrid"),   T["&Grid"],        "Draws an engineering grid"),
        ]
        if thanFrape.ortho:
            m1.extend(
            [ (("EngMapRect"),Tphot["&Rectify Map"], Tphot["Rectifies a raster topographic map"]),
              (("enggeoreference"),Tphot["G&eoreference Image"], Tphot["Image georeferencing with control points"]),
              (("engorthoimage"),Tphot["&Orthoimage GDEM"], Tphot["Image orthorectification using global DEM"]),
            ])
        m1.extend(
        [ (("EngTrace"),  T["&Trace"],           T["Traces a curve in a bitmap raster image"]),
          (("greeceperimeter"), T["Draw &Greece"], T["Draws the perimeter of Greece in EGSA87 coordinates"]),
          (("glp"),             T["Global points"], T["Draws global points (trigonometric points)"]),
          (("glpexport"),       T["Export global points"], T["Writes gloabal point to a file"]),
          ("-",),
          ("geodeticprojection", T["Geo&detic Projection"], T["Displays and changes the geodetic projection of the drawing"]),
          (("demload"),   T["Load DE&Ms"],       T["Loads DEMs (USGS format) stored in .tif files"]),
          (("dem"),       T["Manage DE&Ms"],     T["Manages DEMs (USGS format) stored in .tif files"]),
          (("demdirectory"), T["Locate DEM directory"], T["Locates the directory for missing files of DEMs"]),
          (("dtmmake"),   T["Create &DTM"],      T["Creates a DTM from 3D lines"]),
          (("dtmz"),      T["DTM/DEM &Z"],       T["Computes and shows the z coordinate at an arbitrary point"]),
          (("dtmpoints"), T["Add Z to &Points"], T["Supplies z coordinates to existing points"]),
          (("dtmline"),   T["Add Z to &Lines"],  T["Supplies z coordinates to existing polylines"]),
          (("triangulation"), T["Tr&iangulation"],T["Creates and manages triangulation from (2D) points and lines."]),
          ("-",),
        ])
        if thanFrape.civil:
            m1.append((("engprofile"),      T["Engineering Pro&file"], T["Creates an engineering drawing with the profile of a (3D) line"]))
        m1.extend(\
        [ (("engquickprofile"), T["&Quick Profile"], T["Creates quickly the profile of a (3D) line"]),
          (("isoclinal"),  T["&Isoclinal"],   T["Creates the isoclinal line of a road"]),
          (("EngInterchange"),  T["&Interchange"],   T["Creates an interchange between 2 highways"]),
        ])
        if thanFrape.urban:
            m1.extend(\
            [ ("-",),
              (("urbanbioazimuth"), Tarch["Bio a&zimuth"], Tarch["Computes the azimuth of a road network to test bioclimatic design of city plan"]),
              (("urbanslope"),      Turban["&Locate roads of slope"], Turban["Locates roads (lines) whose slope is less than arbitrary threshold"]),
            ])
        m1.append(("endmenu",))

        if thanFrape.photo:
            m["Photogrammetry"] = m1 =\
          [ ("menu", Tphot["&Photogrammetry"], ""),        # Menu Title
          ("menu", Tphot["INTERIOR ORIENTATION (&mm)"], Tphot["Interior orientation submenu"], "blue"),
          (("photimage"),     T["Insert Raster &Image"],     "Inserts an image in a predefined layer in mm"),
          (("photcosys"), Tphot["Image coordinate &system"], "Creates a non-cartesian coordinate system"),
          (("id"),        Tphot["&Measure image coordinates"],            "Displays the coordinates of a point"),
          ("endmenu",),
          ("menu", Tphot["&INTERIOR ORIENTATION (pixels)"],  Tphot["Interior orientation submenu"], "blue"),
          (("photintimage"),  T["Insert Raster &Image"], Tphot["Inserts an image in a predefined layer in pixels"]),
          (("photintcamera"), Tphot["Load &Camera"],     Tphot["Loads the calibrartion parameters of a metric camera"]),
          (("photinterior"),  Tphot["Compu&tation"],     Tphot["Computes the photogrammetric interior orientation of a metric image"]),
          ("endmenu",),
          (("photcamera"),Tphot["&Camera management"],Tphot["Edit/create photogrammetric camera parameters"]),
          ("-",),
          (("phot90"),    Tphot["Rotate Image &90 deg counterclokwise"],  ""),
          (("phot180"),   Tphot["Rotate Image &180 deg"],                 ""),
          (("phot270"),   Tphot["Rotate Image &270 deg counterclokwise"], ""),
          ("-",),
          (("imagebrighten"), Tphot["&Brighten Image (Gray+)"],           ""),
          (("imagedarken"),   Tphot["&Darken Image (Gray-)"],             ""),
          (("imagebreset"),   Tphot["&Reset Image brightness"],           ""),
          ("-",),
          (("photf6"),    Tphot["Toggle coordinates on/off (F6)"],        ""),
          (("photf7"),    Tphot["Toggle coordinate system (F7)"],         ""),
          ("-",),
          (("photmodel"),    Tphot["&Model definition"],     Tphot["Defines the images which make a photogrammetric model"]),
          ]
            if thanFrape.stereo:
                m1.extend(\
                [ ("-",),
                  (("stereotoggle"),  Tphot["&Stereo toggle"],  Tphot["Sets stereo (blue/red) mode on and off"]),
                  (("stereoaverage"), Tphot["&Stereo average"], Tphot["Zooms the z coordinates so that they are easily visible"]),
                  (("stereogridtoggle"),  Tphot["&Stereo grid"],  Tphot["Sets a grid at the reference elevation on and off to aid stereo viewing"]),
                ])
            m1.append(("endmenu",))
        elif thanFrape.stereo:
            m["Photogrammetry"] = m1 =\
            [ ("menu", Tphot["&Photogrammetry"], ""),        # Menu Title
              (("stereotoggle"),  Tphot["&Stereo toggle"],  Tphot["Sets stereo (blue/red) mode on and off"]),
              (("stereoaverage"), Tphot["&Stereo average"], Tphot["Zooms the z coordinates so that they are easily visible"]),
              (("stereogridtoggle"),  Tphot["&Stereo grid"],  Tphot["Sets a grid at the reference elevation on and off to aid stereo viewing"]),
              ("endmenu",),
            ]

        m["Modify"] = \
        [ ("menu", T["&Modify"], ""),             # Menu Title
          (("erase"),      T["&Erase"],        T["Deletes selected elements"]),
          (("rotate"),     T["&Rotate"],       T["Rotates selected elements"]),
          (("scale"),      T["Sc&ale"],        T["Scales selected elements"]),
          (("move"),       T["&Move"],         T["Moves selected elements"]),
          (("copy"),       T["&Copy"],         T["Copies selected elements"]),
          (("mirror"),     T["M&irror"],       T["Mirrors selected elements with respect to 2d axis"]),
          (("pmirror"),    T["Point Mirror"],  T["Mirrors selected elements with respect to a point"]),
          ("-",),

          ("menu", T["&Line"], ""),             # Sub Menu Title
          ("movelinepoint", T["&Move node"],   T["Moves an arbitrary node of a line the segments which lead to it."]),
          ("join",          T["&Join"],        T["Joins 2 or more adjacent lines"]),
          ("join2d",        T["Join &2D"],     T["Joins 2 or more adjacent lines"]),
          ("joingap",       T["Join &gap"],    T["Joins 2 lines filling the gap between them."]),
          ("straighten",    T["&Straighten"],  T["Straightens the line between 2 user selected points (not necessarily nodes) of the line."]),
          ("endmenu",),

          (("offset"),     T["&Offset"],       T["Copies object parallel to itself"]),
          (("break"),      T["&Break"],        T["Breaks an element into 2 pieces"]),
          (("trim"),       T["&Trim"],         T["Cuts elements with other elements being the cutting edges"]),
          (("extend"),     T["Extend"],        T["Extends lines and arcs until they cross other elements being the boundary edges"]),
          (("lengthen"),   T["Lengthen"],      T["Changes the length of open elements"]),
          (("fillet"),     T["&Fillet"],       T["Rounds off a corner with arc"]),
          (("explode"),    T["E&xplode"],      T["Explode 1 or more elements to smaller objects"]),
          (("reverse"),    T["Re&verse"],      T["Reverses the orientation of lines, circles, arcs"]),
          (("ddedit"),     T["E&dit Text"],    T["Lets the user edit any text interactively"]),
          (("poedit"),     T["Edit named &Point"],   T["Lets the user edit any named point interactively"]),
          (("pointreplace"), T["Convert to named Poi&nt"], T["Lets the user convert points to named points interactively"]),
          ("-",),
          (("chprop"),     T["Change &layer"], T["Changes layer of selected elements"]),
          (("chelev"),     T["C&hange elevation"], T["Changes the z coordinate of selected elements"]),
          (("chelevn"),    T["Change elevation (higher dim)"], T["Changes the z and higher coordinates of selected elements"]),
          (("chelevcontour"), T["Change co&ntour line elevation"], T["Changes the z coordinate of many lines progressively"]),
          ("endmenu",),
        ]

        m["Research"] = m1 =\
        [ ("menu", T["&Research"], ""),           # Menu Title
          (("EduRectangle"), Tarch["Mark &Region"],   Tarch["Draws an active rectangle which contains comments"]),
          (("EduEdit"),      Tarch["&Edit Region"],   Tarch["Edits the comments of an active rectangle"]),
        ]
        if thanFrape.fflf:
            m1.extend(\
            [ ("-",),
              (("EduMatch2"),     Tmatch["&Match 2d"],         Tmatch["Matches two 2d polylines"]),
              (("EduMatch23"),    Tmatch["&Match 3d to 2d"],   Tmatch["Matches one 3d polyline to one 2d polylines"]),
              (("EduMatch3"),     Tmatch["&Match 3d"],         Tmatch["Matches two 3d polylines"]),
              (("EduMatchSplines3d"), Tmatch["&Match 3d splines"], Tmatch["Matches two 3d cubic splines"]),
              ("-",),
              (("EduMatchMult2"), Tmatch["&Match multiple 2d"],Tmatch["Matches two sets of 2d polylines"]),
              (("EduMatchMult23"),Tmatch["&Match multiple 3d to 2d"],Tmatch["Matches one set of 3d polylines to one set of 2d polylines"]),
              (("EduAxis"),       Tmatch["&Mid axis"],         Tmatch["Computes middle axis of road given the road edges"]),
              ("-",),
              (("edutransf"),     Tmatch["&Compute projection"], Tmatch["Computes a projection transformation using control points"]),
              (("eduproject"),    Tmatch["&Project/transform"], Tmatch["Projects/transforms arbitrary ThanCad Elements using a known transform (2D-2D, 3D-2D, 3D-3D"]),
            ])
        m1.extend(\
        [ ("-",),
          (("edufloorplan"),  Tarch["&Floor plan"],    Tarch["Creates automatically a floor plan"]),
          (("edubiocityplan"),Tarch["&Bio city plan"], Tarch["Creates bioclimatic oriented city plan"]),
          (("edudfr"), Tmatch["Show dfr coordinates"], Tmatch["&Shows, selects draws and saves coordinates for a .dxf file."]),
        ])
        if thanFrape.thermo:
            m1.extend(\
            [ (("thermohumid"), u"Εισαγωγή μετρήσεων θερμοϋγρομέτρου", u"Διπλωματική εργασία Χάρη Πατούνη, Νίκου Σίμου, Σχολή Πολ. Μηχανικών, ΕΜΠ, 2012"),
            ])
        if thanFrape.civil:
            m1.extend(\
            [ ("-",),
              (("gradeline"), Tcivil["&Grade line"], Tcivil["Computes automatically the grade line of a road profile"]),
            ])
        m1.extend(\
        [ ("endmenu",),
        ])

        m["Developer"] = \
        [ ("menu", T["D&eveloper"], ""),          # Menu Title
          (("devfont"),  T["Show &font"],         T["Shows font for debugging"]),
          (("devcm"),    T["Show &dimensions"],   T["Shows window dimensions for debugging"]),
          (("devcmd"),   T["&Save CMD text"],     T["Saves the text of the command window"]),
          (("devtrans"), T["&Translation report"],T["Saves translation status to a file"]),
          (("devhandle"),T["Show &handles"],      T["Shows element handles for debugging"]),
          ("-",),
          (("fractal"),  T["F&ractal demo"],      T["Demonstrates a fractal made of colored lines"]),
          ("-",),
          (("tests"),    T["Run &tests"],         T["Runs unit tests of ThanCad"]),
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
          (("help"),  T["&Introduction"], "Introduction to "+tcver.name),
          (("gpl"),   T["&GPL"],          "Gnu General Public License"),
          (("language"), "&Language",     "Change the language of ThanCad's interface"),
          (("about"), T["&About"],        "Information about "+tcver.name),
          ("endmenu",),
        ]
        return s, m


def thanMainMenus():
    "Creates a description of the main window menus in a list."
    S = p_ggen.ThanStub
    s = "File Window Help".split()
    m = {}
    m["File"] = \
    [ ("menu", "&File", ""),            # Menu Title
      (("new"),    "&New",  "Makes an empty drawing"),
#          (("new"),    u"&Νέο Θανάσης",  "Makes an empty drawing"),
      (("open"),   "&Open", "Opens an existing drawing"),
      ("-",),               # Separator
      (("sykin"),  "&Import syk", "Imports a syk file"),
      (("dxfin"),  "Import &dxf", "Imports a dxf file"),
      (("sykout"), "&Export syk", "Exports a syk file"),
      (("dxfout"), "Export &dxf", "Exports a dxf file"),
      ("-",),               # Separator
#
#-----recent files
#
      ("-",),               # Separator
      (("quit"), "E&xit", "Terminate "+tcver.name, "darkred"),
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
      (("help"),  "&Introduction", "Introduction to "+tcver.name),
      (("gpl"),   "&GPL",          "Gnu General Public License"),
      (("about"), "&About",        "Information about "+tcver.name),
      ("endmenu",),
    ]
    return s, m


def thanAddMenus(s, m):
    "Add new menus."
    for (menuname, aftermenu, aftercommand) in s:
        if menuname in thanMenus:         #Menu menuname already exists; add the entries of the m to it
            __addMenuEntries(thanMenus[menuname], m[menuname], aftercommand)
        else:                             #Menu menuname does not exist; add it
            if aftermenu not in thanMenus:
                if "Help" in thanMenus: i = thanSeq.index("Help") #Menu must be added before Help menu
                else:                   i = len(thanSeq)          #Menu is added at the end
            else:
                i = thanSeq.index(aftermenu) + 1
            thanSeq.insert(i, menuname)
            thanMenus[menuname] = m[menuname]


def __addMenuEntries(mold, mnew, aftercommand):
    "Add the entries of the new menu to the existing one."
    for i, ent in enumerate(mold):
        if len(ent) < 3: continue
        if ent[0] == aftercommand:        #The command aftercommand was found
            if i+1 < len(mold) and mold[i+1][0] == "-": i += 1       #Add new entries after the separator lines
            mold[i+1:i+1] = mnew[1:-1]                        #Take only the entries of the menu
            break
    else:
        i = len(mold) - 1                 #The command aftercommand was not found
        mold[i:i] = mnew[1:-1]                                     #Add new entries at the end
    for k in i+(len(mnew)-2)-1, i:
        if k+1 < len(mold) and mold[k][0] == "-" and mold[k+1][0] == "-": del mold[k]   #Remove consecutive separators


thanSeq = []
thanMenus = {}
thanSeqMain = []
thanMenusMain = {}


def thanCreateMenus():
    thanAddMenus(*thanStandardMenus2())
    sm, mm = thanMainMenus()
    thanSeqMain[:] = sm
    thanMenusMain.update(mm)
