##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

Package which processes commands entered by the user.
This module defines various constants.
"""

import thandr, thanopt
import thancomsel, thancommod, thancommodext, thancomedit, thancomdraw, thancomfile
import thancomvar, thancomview, thancomedu, thancomtool, thancomhatch, thancomeng
import thancompr, thancomim, thancomtest
__all__ = "thanComFun",


def __prepare():
    "Prepare commands for easy look up."
    coms.sort()
    coms.reverse()
    for c,f in coms:
        thanComs[c] = c, f
        if c == "exit": continue     #Do not abbreviate exit; it is very similar to extend :)
        for i in xrange(1, min(len(c), 10)):
            thanComs[c[:i]] = c, f
    for c,f in abbrevs: thanComs[c] = thanComs[f]


def __packages():
    "Import command from various optional packages."
    import sys
    thanFrape = thanopt.thancon.thanFrape
    for name in "civil ortho fflf photo stereo".split():
        ok = getattr(thanFrape, name)
        if not ok: continue
        name1 = "thanpro%s.thanprocom.thanprocomcon" % (name,)
        print "importing", name1
        __import__(name1)
        coms.extend(getattr(sys.modules[name1], "coms"))

    for name in "urban architect thermo".split():
        ok = getattr(thanFrape, name)
        if not ok: continue
        name1 = "thanpackages.%s.thancom.thancomcon" % (name,)
        print "importing", name1
        __import__(name1)
        coms.extend(getattr(sys.modules[name1], "coms"))


def thanComFun(com):
    "Tries to match com to a command, and returns the command's function."
    try: return thanComs[com]
    except KeyError: return None, None


dr = thancomdraw.thanTkDrawElem
coms = \
[ ("arc",         lambda w, cl=thandr.ThanArc,   dr=dr: dr(w, cl)),
  ("about",       thancomvar.thanHelpAbout),
  ("angle",       thancomtool.thanToolAngle),
  ("area",        thancomtool.thanToolArea),
  ("edubiocityplan", thancomedu.thanEdubiocityplan),
  ("background",  thancomvar.thanBackroundColor),
  ("break",       thancommod.thanModBreak),
  ("brkout",      lambda w: thancomfile.thanFileSaveas(w, ".brk")),
  ("centroid",    thancomtool.thanToolCen),
  ("chelev",      thancommod.thanModChelev),
  ("chelevcontour", thancommod.thanModChelevContour),
  ("chelevn",     thancommod.thanModChelevn),
  ("chprop",      thancommod.thanModChlayer),
  ("circle",      lambda w, cl=thandr.ThanCircle,dr=dr: dr(w, cl)),
  ("close",       thancomfile.thanFileClose),
  ("continueline",thancommod.thanModContline),
  ("copy",        thancommod.thanModCopy),
  ("copybase",    thancomedit.thanClipCopybase),
  ("copyclip",    thancomedit.thanClipCopy),
  ("cutclip",     thancomedit.thanClipCut),
  ("ddedit",      thancommod.thanModDDedit),
  ("ddlmodes",    thancomvar.thanFormLay),
  ("decurve",     thancomdraw.thanDecurve),
  ("dem",         thancomeng.thanEngDem),
  ("demdirectory",thancomeng.thanDemImageDir),
  ("demload",     thancomeng.thanDemLoad),
  ("devcm",       thancomvar.thanDevCm),
  ("devcmd",      thancomvar.thanDevCmdsave),
  ("devfont",     thancomvar.thanDevFont),
  ("devhandle",   thancomvar.thanDevHandle),
  ("devtrans",    thancomvar.thanDevTrans),
  ("dimali",      lambda w, cl=thandr.ThanDimali,dr=dr: dr(w, cl)),
  ("dist",        thancomtool.thanToolDist),
  ("dsettings",   thancomtool.thanToolOsnap),
  ("dtext",       thancomdraw.thanTkDrawText),
  ("dtmline",     thancomeng.thanEngDtmline),
  ("dtmmake",     thancomeng.thanEngDtmmake),
  ("dtmpoints",   thancomeng.thanEngDtmpoints),
  ("dtmz",        thancomeng.thanEngDtmpoint1),
  ("dxfin",       lambda w, cl=".dxf": thancomfile.thanFileOpen(w, cl)),
  ("dxfout",      lambda w: thancomfile.thanFileSaveas(w, ".dxf")),
  ("eduedit",     thancomedu.thanEduEdit),
  ("edufloorplan",thancomedu.thanEduFplan),
  ("edurectangle",thancomedu.thanEduRect),
  ("elevation",   thancomvar.thanVarElev),
  ("elevn",       thancomvar.thanVarElevn),
  ("ellipse",     lambda w, cl=thandr.ThanEllipse,dr=dr: dr(w, cl)),
  ("erase",       thancommod.thanModErase),
  ("enggrid",     thancomeng.thanEngGrid),
  ("enginterchange", thancomeng.thanEngInterchange),
  ("engquickprofile", thancomeng.thanEngQuickprofile),
  ("engtrace",    thancomeng.thanEngTrace),
  ("exit",        thancomfile.thanFileExit),
  ("extend",      thancommodext.thanModExtend),
  ("explode",     thancommod.thanModExplode),
  ("filet",       thancommodext.thanModFilet),
  ("fill",        thancomvar.thanVarFill),
  ("find",        thancomtool.thanToolTextfind),
  ("fractal",     thancomvar.thanFractal),
  ("gpl",         thancomvar.thanHelpGpl),
  ("hatchopen",   thancomhatch.thanHatchOpen),
  ("help",        thancomvar.thanHelpHelp),
  ("hull",        thancomtool.thanToolHull),
  ("id",          thancomtool.thanToolId),
  ("imageattach", lambda w, cl=thandr.ThanImage, dr=dr: dr(w, cl)),
  ("imagebreset", thancomim.thanTkImageBreset),
  ("imagebrighten", thancomim.thanTkImageBrighten),
  ("imagecadastre", lambda w, cl=thandr.ThanImage, dr=dr: dr(w, cl, fn="thanTkGet", insertmode="c")),
  ("imageclip",   thancomim.thanTkImageClip),
  ("imagedarken", thancomim.thanTkImageDarken),
  ("imagedirectory", thancomim.thanTkImageDir),
  ("imageembed",  thancomim.thanTkImageEmbed),
  ("imageframe",  thancomim.thanTkImageFrame),
  ("imagegeotiff",thancomim.thanTkGetGeotif),
  ("imageload",   thancomim.thanTkImageLoad),
  ("imagelocate", thancomim.thanTkImageLocate),
  ("imagelog",    thancomim.thanTkGetlog),
  ("imagerender", thancomim.thanImageRendering),
  ("imagescan",   thancompr.thanImageScan),
  ("imagetfw",    thancomim.thanTkGetTfw),
  ("imageunload", thancomim.thanTkImageUnload),
  ("insert",       thancomfile.thanFileMerge),
  ("insertunload",  lambda w: thancomfile.thanFileMerge(w, forceunload=True)),
  ("interpolate", thancomtool.thanToolInterpolate),
  ("join",        lambda w: thancommod.thanModJoin(w, 3)),
  ("join2d",      lambda w: thancommod.thanModJoin(w, 2)),
  ("joingap",     thancommod.thanModJoinGap),
  ("joingap2d",   thancommod.thanModJoinGap),
  ("language",    thancomvar.thanVarLang),
  ("line",        lambda w, cl=thandr.ThanLine,  dr=dr: dr(w, cl)),
  ("linin",       thancomfile.thanImpLin),
  ("linout",      thancomfile.thanExpLin),
  ("list",        thancomvar.thanList),
  ("mirror",      thancommod.thanModMirror),
  ("move",        thancommod.thanModMove),
  ("new",         thancomfile.thanFileNew),
  ("osnap",       thancomtool.thanToolOsnap),
  ("open",        thancomfile.thanFileOpen),
  ("openunload",  lambda w: thancomfile.thanFileOpen(w, forceunload=True)),
  ("panpagedown", lambda win: thancomview.thanPanPage(win,  0, -1)),
  ("panpageleft", lambda win: thancomview.thanPanPage(win, -1,  0)),
  ("panpageright",lambda win: thancomview.thanPanPage(win,  1,  0)),
  ("panpageup",   lambda win: thancomview.thanPanPage(win,  0,  1)),
  ("panrealtime", thancomview.thanPanRT),
  ("panrelative", thancomview.thanPanRel),
  ("pasteorig",   thancomedit.thanClipPasteorig),
  ("pasteclip",   thancomedit.thanClipPaste),
  ("pdfout",      thancomfile.thanPlotPdf),
  ("pilout",      thancomfile.thanPlotPil),
  ("pline",       lambda w, cl=thandr.ThanLine,  dr=dr: dr(w, cl)),
  ("plot",        thancompr.thanPrPlot),
  ("poedit",      thancommod.thanModPoint),
  ("point",       thancomdraw.thanTkDrawPoint),
  ("pointnamed",  thancomdraw.thanTkDrawPointNamed),
  ("pointreplace",thancomdraw.thanPointNamedReplace),
  ("polygon",     thancomdraw.thanTkDrawPolygon),
  ("pnamed",      thancomdraw.thanTkDrawPointNamed),
  ("purge",       thancommod.thanModPurge),
  ("quit",        thancomfile.thanFileExit),
  ("offset",      thancommod.thanModOffset),
  ("redraw",      thancomview.thanRedraw),
  ("regen",       thancomview.thanRegen),
  ("rectangle",   thancomdraw.thanTkDrawRect),
  ("redo",        thancomedit.thanModRedo),
  ("reverse",     thancommod.thanModReverse),
  ("road",        lambda w, cl=thandr.ThanRoad,dr=dr: dr(w, cl)),
  ("rotate",      thancommod.thanModRotate),
  ("save",        thancomfile.thanFileSave),
  ("saveas",      thancomfile.thanFileSaveas),
  ("scale",       thancommod.thanModScale),
  ("script",      thancomvar.thanVarScript),
  ("select",      thancomsel.thanSelectGen),
  ("simplify",    thancomtool.thanToolSimplif),
  ("solid",       thancomdraw.thanTkDrawSolid),
  ("spline",      lambda w, cl=thandr.ThanSpline,dr=dr: dr(w, cl)),
  ("straighten",  thancommod.thanModStraighten),
  ("style",       thancomvar.thanFormTstyle),
  ("sudup",       thancomvar.thanVarSudup),
  ("sykout",      lambda w: thancomfile.thanFileSaveas(w, ".syk")),
  ("synout",      lambda w: thancomfile.thanFileSaveas(w, ".syn")),
  ("tests",       thancomtest.thanTestLine1),
  ("thancad",     thancomvar.thanHelpVer),
  ("tocurve",     thancomdraw.thanToCurve),
  ("tospline",    thancomdraw.thanToSpline),
  ("triangulation", thancomeng.thanEngTri),
  ("trim",        thancommod.thanModTrim),
  ("undo",        thancomedit.thanModUndo),
  ("units",       thancomvar.thanUnits),
  ("zoom",        thancomview.thanZoom),
  ("zoomrealtime",thancomview.thanZoomRT),
  ("zoomall",     thancomview.thanZoomExt),
  ("zoomext",     thancomview.thanZoomExt),
  ("zoomin2",     lambda win: thancomview.thanZoomFact(win, -2.0)),
  ("zoomout2",    lambda win: thancomview.thanZoomFact(win, -0.5)),
  ("zoomrelative",thancomview.thanZoomFact),
  ("zoomsel",     thancomview.thanZoomSel),
  ("zoomwin",     thancomview.thanZoomWin),
]
abbrevs = \
( ("c",  "circle"),
  ("cl", "continueline"),
  ("e",  "erase"),
  ("imr", "imagerender"),
  ("jg", "joingap"),
  ("l", "line"),              #Prevent l to mean language
  ("m", "move"),
  ("q", "quit"),
  ("p", "panrealtime"),
  ("po", "point"),
  ("pr", "pointreplace"),
  ("r",  "redo"),
  ("re", "regen"),
  ("x",  "explode"),
  ("zw", "zoomwin"),
)

thanComs = {}
__packages()
__prepare()
del dr, coms, abbrevs
