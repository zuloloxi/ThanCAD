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

Package which provides for ThanCad customisation.
This module keeps a central repository of the options and variables common to all
all drawings of ThanCad. It also gets/saves options to configuration files.
"""

try: from configparser import SafeConfigParser     #python3.9
except: from configparser import ConfigParser as SafeConfigParser  #python3.12
import p_ggen, p_gimage
from thandefs.thanatt import thanAttCol, ThanAttCol

thanOsnapModesText = \
( ("end", "Endpoint"),
  ("mid", "Midpoint"),
  ("cen", "Center"  ),
  ("nod", "Node"    ),
  ("qua", "Quadrant"),
  ("int", "Intersection"),
  ("tan", "tangent" ),
  ("nea", "Nearest" ),
  ("per", "Perpendicular"),
  ("ena", "Enabled" ),
)

#Repository of ThanCad Default values for ThanCad

thanColBack = ThanAttCol("0 0 0")            #Background color of drawing window
#thanColRoot = ThanAttCol("0 222 255")        #Default colour for root layer
thanColRoot = ThanAttCol("200 224 31")       #Default colour for root layer
thanColUser = []                 #User defined colours
thanColSel  = ThanAttCol("12")               #Colour for selection windows (window, crossing window, single elements)
thanColOsn = ThanAttCol("82")                #Colour for the object snap symbols
thanBSEL = 8                     #Size of the select1 rectangle and the relevant crossing window
thanBOSN = 15                    #Size of the osnap symbol in pixels

thanCanvasdim = [780, 400]       #Canvas size in pixels (width, height)

thanOsnapModes = dict(end=True)  #Object snap modes

p_ggen.thanSetEncoding("utf_8")  #Encoding for non-unicode characters
thanTranslateTo = "en"

thanFiledir = ""                 #Directory where previous drawings were found
thanFilerecent = []              #Recently opened files
thanCameradir = ""               #Directory where photogrammetric camera files are stored
thanTempPrefix = "untitled"      #Prefix for the names of new drawings
thanUndefPrefix = "<undefined>"  #Prefix for the undefined names (files, dirs etc)

thanFontfamily = "Liberation Serif"
thanFontsize = 16
if p_ggen.Pyos.Windows: thanFontsize = 14
thanFontfamilymono = "Liberation Mono"
thanFontsizemono = thanFontsize - 1


p_gimage.imageSetmaxpixels(int(300e6))  #Set the max image pixels; after that PIL complains about "DecompressionBomb"


def thanOptColorsGet(c):
    "Read colors from configuration file."
    try:
        rc1 = c.get("colors", "user defined")
    except:
        pass
    else:
        rc = thanColUser
        for thc in rc1.split(";"):
            thc = thanAttCol(thc)
            if thc is None: continue
            if str(thc) not in rc: rc.append(str(thc))
        while len(rc) < 17: rc.append(None)
        while len(rc) > 17: del rc[-1]

    global thanColBack, thanColRoot, thanColSel, thanColOsn
    thanColBack = __colget(c, "background", thanColBack)
    thanColRoot = __colget(c, "root",   thanColRoot)
    thanColSel  = __colget(c, "select", thanColSel)
    thanColOsn  = __colget(c, "osnap",  thanColOsn)


def __colget(c, key, coldef):
    "Get a named color from config parser; return default if error."
    try: return ThanAttCol(c.get("colors", key))
    except: pass      #This may happen if key is not in c or if it c[key] is invalid color
    return ThanAttCol(coldef)  #This will raise an exception if coldef is invalid color


def thanOptOsnapGet(c):
    "Read object snap setting from configuration file."
    thanOsnapModes.clear()
    for mode,t in thanOsnapModesText:
        try: val = c.get("osnap", t)
        except: continue
        if val.strip().lower() == "false": continue
        if val: thanOsnapModes[mode] = True


def thanOptInterGet(c):
    "Read international settings."
    global thanTranslateTo
    try:
        val = c.get("international", "encoding")
    except:
        pass
    else:
        p_ggen.thanSetEncoding(val)
    try:
        val = c.get("international", "translateto")
    except:
        pass
    else:
        thanTranslateTo = val


def thanOptFilesGet(c):
    "Read recent opened file and recent directories."
    global thanFiledir, thanFilerecent, thanCameradir
    try: val = c.get("files", "recent files")
    except: pass
    else: thanFilerecent = [ p_ggen.path(filnam) for filnam in val.split(";") if filnam.strip() != ""]

    try:
        val = c.get("files", "recent directory")
    except:
        pass
    else:
        thanFiledir = val
        if thanFiledir.strip() == "": thanFiledir = ""

    try:
        val = c.get("files", "camera directory")
    except:
        pass
    else:
        thanCameradir = val
        if thanCameradir.strip() == "": thanCameradir = ""


def thanOptGeometryGet(c):
    "Read dimensions in pixels of various objects."
    global thanBSEL, thanBOSN
    try:
        val = int(c.get("geometry", "canvas width"))
    except:
        pass
    else:
        if 10 < val < 20000: thanCanvasdim[0] = val
    try:
        val = int(c.get("geometry", "canvas height"))
    except:
        pass
    else:
        if 10 < val < 20000: thanCanvasdim[1] = val
    try:
        val = int(c.get("geometry", "select size"))
    except:
        pass
    else:
        if 1 < val < 600: thanBSEL = val
    try:
        val = int(c.get("geometry", "osnap size"))
    except:
        pass
    else:
        if 2 < val < 600: thanBOSN = val


def thanOptColorsSave(c):
    "Write colors into configuration file."
    if not c.has_section("colors"): c.add_section("colors")
    c.set("colors", "background",   str(thanColBack))
    c.set("colors", "root",         str(thanColRoot))
    c.set("colors", "user defined", ";".join(str(thc) for thc in thanColUser if thc is not None))
    c.set("colors", "select",       str(thanColSel))
    c.set("colors", "osnap",        str(thanColOsn))


def thanOptOsnapSave(c):
    "Read colors from configuration file."
    if not c.has_section("osnap"): c.add_section("osnap")
    for mode, t in thanOsnapModesText:
        val = mode in thanOsnapModes
        c.set("osnap", t, str(val))


def thanOptInterSave(c):
    "Read colors from configuration file."
    if not c.has_section("international"): c.add_section("international")
    c.set("international", "encoding", p_ggen.thanGetEncoding())
    c.set("international", "translateto", thanTranslateTo)


def thanOptFilesSave(c):
    "Read colors from configuration file."
    if not c.has_section("files"): c.add_section("files")
    c.set("files", "recent files", ";".join(thanFilerecent))
    c.set("files", "recent directory", thanFiledir)
    c.set("files", "camera directory", thanCameradir)


def thanOptGeometrySave(c):
    "Read dimensions of various objects."
    if not c.has_section("geometry"): c.add_section("geometry")
    c.set("geometry", "canvas width", str(int(thanCanvasdim[0])))
    c.set("geometry", "canvas height", str(int(thanCanvasdim[1])))
    c.set("geometry", "select size", str(int(thanBSEL)))
    c.set("geometry", "osnap size", str(int(thanBOSN)))


#############################################################################
#############################################################################

def thanOptsGet():
    "Reads the attributes from config files and store them as global variables."
    fc, terr = p_ggen.configFile("thancad.conf", "thancad")
    if terr != "":  #Error locating thancad.conf: leave default config values
        print("thanOptsGet():", terr)
        return
    try:
        c = SafeConfigParser()
        c.read(fc)
        thanOptColorsGet(c)
        thanOptOsnapGet(c)
        thanOptInterGet(c)
        thanOptFilesGet(c)
        thanOptGeometryGet(c)
    except Error as e: #Error parsing/reading thancad.conf: leave the rest config values with default values
        print("thanOptsGet():", e)


def thanOptsSave():
    "Writes the attributes to config files."
    fc, terr = p_ggen.configFile("thancad.conf", "thancad")
    if terr != "":
        print("thanOptsSave():", terr)
        return
    c = SafeConfigParser()
    c.read(fc)
    thanOptColorsSave(c)
    thanOptOsnapSave(c)
    thanOptInterSave(c)
    thanOptFilesSave(c)
    thanOptGeometrySave(c)

    try:
        f = open(fc, "w")
        c.write(f)
    except IOError as why:
        print("Could not save config file:", str(why))
