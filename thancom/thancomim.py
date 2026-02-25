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
This module processes image related commands.
"""
import Image
import p_gtkuti, p_ggen
import thandr
from thanvar import Canc, thanfiles
from thantrans import T
from thandefs import ThanImageMissing, imageOpen
import thanundo
from thancommod import thanModCanc, thanModEnd
from thancomsel import thanSelect1, thanSelectGen


def thanTkGetlog(proj):
    "Imports many raster images whose positions are stored in log format (bmp image)."
    tit = T["Image file open failed"]
    fildir = thanfiles.getFiledir()
    fns = p_gtkuti.thanGudGetReadFile(proj[2], ".log", T["Choose image .log files"],
                                          initialdir=fildir, multiple=True)
    if fns == None: return proj[2].thanGudCommandCan()   # Image canceled
    newelems = []
    for fi in fns:
        elem = thandr.ThanImage()
        try:
            elem.thanLogGet(proj, fi)
        except (IOError, ValueError), why:
            p_gtkuti.thanGudModalMessage(proj[2], why, tit)   # (Gu)i (d)ependent
        else:
            proj[1].thanElementAdd(elem)     # thanTouch is implicitely called
            elem.thanTkDraw(proj[2].than)    # This also sets thanImages
            newelems.append(elem)
    proj[2].thanRedraw()                 # Images regen probably violated draworder
    proj[1].thanDoundo.thanAdd("imagelog", thanundo.thanReplaceRedo, ((), newelems),
                                           thanundo.thanReplaceUndo, ((), newelems))
    return proj[2].thanGudCommandEnd()

def thanTkGetLog(proj):
    "Imports many raster images whose positions are stored in tfw format (tif image)."
    return thanTkGetPos(proj, "imagelog", "thanLogGet", ".log", T["Choose image .log files"])

def thanTkGetTfw(proj):
    "Imports many raster images whose positions are stored in tfw format (tif image)."
    tit = T["Image file open failed"]
    fildir = thanfiles.getFiledir()
    fns = p_gtkuti.thanGudGetReadFile(proj[2], ".tfw", T["Choose image .tfw files"],
                                          initialdir=fildir, multiple=True)
    if fns == None: return proj[2].thanGudCommandCan()   # Image canceled
    newelems = []
    for fi in fns:
        elem = thandr.ThanImage()
        try:
            elem.thanTfwGet(proj, fi)
        except (IOError, ValueError), why:
            p_gtkuti.thanGudModalMessage(proj[2], why, tit)   # (Gu)i (d)ependent
        else:
            proj[1].thanElementAdd(elem)     # thanTouch is implicitely called
            elem.thanTkDraw(proj[2].than)    # This also sets thanImages
            newelems.append(elem)
    proj[2].thanRedraw()                 # Images regen probably violated draworder
    proj[1].thanDoundo.thanAdd("imagetfw", thanundo.thanReplaceRedo, ((), newelems),
                                           thanundo.thanReplaceUndo, ((), newelems))
    return proj[2].thanGudCommandEnd()


def thanTkGetTfw(proj):
    "Imports many raster images whose positions are stored in tfw format (tif image)."
    return thanTkGetPos(proj, "imagetfw", "thanTfwGet", ".tfw", T["Choose image .tfw files"])


def thanTkGetGeotif(proj):
    "Imports many tif images whose positions are stored in tags in the tif file itself."
    return thanTkGetPos(proj, "imagegeotiff", "thanGeotifGet", ".tif", T["Choose geotiff image files"])


def thanTkGetPos(proj, com, methodname, ext, stat):
    "Imports many raster images whose positions are stored in some format."
    tit = T["Image file open failed"]
    fildir = thanfiles.getFiledir()
    fns = p_gtkuti.thanGudGetReadFile(proj[2], ext, stat,
                                          initialdir=fildir, multiple=True)
    if fns == None: return proj[2].thanGudCommandCan()   # Image canceled
    newelems = []
    for fi in fns:
        elem = thandr.ThanImage()
        try:
#            elem.thanTfwGet(proj, fi)
            method = getattr(elem, methodname)
            method(proj, fi)
        except (IOError, ValueError), why:
            p_gtkuti.thanGudModalMessage(proj[2], why, tit)   # (Gu)i (d)ependent
        else:
            proj[1].thanElementAdd(elem)     # thanTouch is implicitely called
            elem.thanTkDraw(proj[2].than)    # This also sets thanImages
            newelems.append(elem)
    proj[2].thanRedraw()                 # Images regen probably violated draworder
    proj[1].thanDoundo.thanAdd(com, thanundo.thanReplaceRedo, ((), newelems),
                                    thanundo.thanReplaceUndo, ((), newelems))
    return proj[2].thanGudCommandEnd()


def thanTkImageUnload(proj):
    "Unload multiple images."
    proj[2].thanPrt(T["Select images to unload:"])
    res = thanSelectGen(proj, standalone=False, filter=lambda e, cl=thandr.ThanImage: isinstance(e, cl))
    if res == Canc: return thanModCanc(proj)    # Curve cancelled
    selold = proj[2].thanSelold
    tounload = proj[2].thanSelall
    processed = thanImageLoadunloadDo(proj, tounload, set(), None)
    proj[1].thanDoundo.thanAdd("imageunload", thanImageLoadunloadDo, (processed, set(), tounload),    #Redo
                                              thanImageLoadunloadDo, (set(), processed, selold))      #Undo
    if processed: proj[1].thanTouch()
    for im in processed: print "thanTkImageUnload(): image %s:   loaded=%s" % (im.filnam, im.loaded)
    thanModEnd(proj, T["%d images were unloaded."] % (len(processed),), "info1")


def thanTkImageLoad(proj):
    "Unload multiple images."
    proj[2].thanPrt(T["Select images to load:"])
    res = thanSelectGen(proj, standalone=False, filter=lambda e, cl=thandr.ThanImage: isinstance(e, cl))
    if res == Canc: return thanModCanc(proj)    # Curve cancelled
    selold = proj[2].thanSelold
    toload = proj[2].thanSelall
    processed = thanImageLoadunloadDo(proj, set(), toload, None)
    proj[1].thanDoundo.thanAdd("imageload", thanImageLoadunloadDo, (set(), processed, toload),    #Redo
                                            thanImageLoadunloadDo, (processed, set(), selold))    #Undo
    if processed: proj[1].thanTouch()
    thanModEnd(proj, T["%d images were loaded."] % (len(processed),), "info1")


def thanImageLoadunloadDo(proj, tounload, toload, selelems):
    "Unloads and loads images and sets selectiom."
    processed = set()
    for elem in tounload:
        proj[2].thanTkSet(elem)                #set the attributes of element's layer
        icod, terr = elem.thanUnload(proj[2].than)
        if icod == 0: processed.add(elem)
        else:         proj[2].thanPrter1(terr)
    for elem in toload:
        proj[2].thanTkSet(elem)                #set the attributes of element's layer
        icod, terr = elem.thanLoad(proj[2].than)
        if icod == 0: processed.add(elem)
        else:         proj[2].thanPrter1(terr)
    if selelems != None: proj[2].thanGudSetSelElem(selelems)
    proj[2].thanTkSet()                        #set the attributes of default layer
    return processed


def thanTkImageEmbed(proj):
    "Embed multiple images."
    proj[2].thanPrt(T["Select images to embed:"])
    res = thanSelectGen(proj, standalone=False, filter=lambda e, cl=thandr.ThanImage: isinstance(e, cl))
    if res == Canc: return thanModCanc(proj)    # Curve cancelled
    selold = proj[2].thanSelold
    toload = proj[2].thanSelall
    thanImageEmbedDo(proj, set(), toload, None)
    proj[1].thanDoundo.thanAdd("imageembed", thanImageEmbedDo, (set(), toload, toload),    #Redo
                                             thanImageEmbedDo, (toload, set(), selold))    #Undo
    thanModEnd(proj, T["%d images were embedded."] % (len(toload),), "info1")


def thanImageEmbedDo(proj, tounload, toload, selelems):
    "Unloads and loads images and sets selectiom."
    for elem in tounload:
        elem.embedded = False
    for elem in toload:
        elem.embedded = True
    if selelems != None: proj[2].thanGudSetSelElem(selelems)
    proj[1].thanTouch()


def thanTkImageLocate(proj):
    "Locate the image file of an image (usually when the image file was not found)."
    elem = thanSelect1(proj, T["Select an image: "], filter=lambda e: isinstance(e, thandr.ThanImage))
    if elem == Canc: return thanModCanc(proj)                         # Location cancelled
    newelem = elem.thanClone()          #Note that this is a cheap (and low memory) operation
    if newelem.thanTkLocate(proj) == Canc: return thanModCanc(proj)   # Location cancelled
#    newelem.thanTags = elem.thanTags
#    newelem.handle = elem.handle
    selold = proj[2].thanSelold
    delelems = (elem,)
    newelems = set((newelem,))
    thanundo.thanReplaceRedo(proj, delelems, newelems, newelems) # thanTouch is implicitely called
    proj[2].thanRedraw()                # Image redraw probably violated draworder

    proj[1].thanDoundo.thanAdd("imagelocate", thanundo.thanReplaceRedo, (delelems, newelems, newelems),
                                              thanundo.thanReplaceUndo, (delelems, newelems, selold))
    thanModEnd(proj)


def thanTkImageDir(proj):
    "Locate the directory where missing image files can be found."
    for elem in proj[2].thanImages:
        if isinstance(elem.image, ThanImageMissing): break
    else:
        return proj[2].thanGudCommandCan(T["No image files are missing."])
    tit = T["Select directory for missing image files"]
    fildir = thanfiles.getFiledir()
    while True:
        dn = p_gtkuti.thanGudGetDir(proj[2], tit, initialdir=fildir)
        if dn == None: return proj[2].thanGudCommandCan()        # location canceled
        dn = p_ggen.path(dn)
        nmiss = 0
        delelems = []
        newelems = []
        for elem in proj[2].thanImages:
            if not isinstance(elem.image, ThanImageMissing): continue
            fi = dn / p_ggen.path(elem.filnam).basename()

            im, terr = imageOpen(fi)
            if terr != "":
#            try:
#                im = Image.open(fi)
#                if im.size[0] < 2 or im.size[1] < 2: raise ValueError, T["Image is probably corrupted: size is less than 2 pixels"]
#                im.crop((0,0,2,2))   #This will trigger decode error (IOError) if image is not recognised
#            except (IOError, ValueError), why:
                nmiss += 1
            else:
                newelem = thandr.ThanImage()
                if elem.clipped: newelem.thanSet(fi, im, elem.c1ori, elem.c2ori, 0.0, elem.transpose, (elem.c1, elem.c2), elem.loaded)
                else:            newelem.thanSet(fi, im, elem.c1ori, elem.c2ori, 0.0, elem.transpose, None, elem.loaded)
                newelem.thanTags = elem.thanTags
                newelems.append(newelem)
                delelems.append(elem)
        assert not (len(newelems) == 0 and nmiss == 0), "It should have been found!!"
        if len(newelems) > 0: break
        p_gtkuti.thanGudModalMessage(proj[2], T["No image files were found. Try again."], tit)

    thanundo.thanReplaceRedo(proj, delelems, newelems)    # thanTouch is implicitely called
    proj[2].thanRedraw()      # Image draw (replaceredo(): thanelementrestore()) probably violated draworder

    proj[1].thanDoundo.thanAdd("imagedirectory", thanundo.thanReplaceRedo, (delelems, newelems),
                                                 thanundo.thanReplaceUndo, (delelems, newelems))
    if nmiss > 0: mes = T["Not all image files were found."]
    else:         mes = None
    proj[2].thanGudCommandEnd(mes)


def thanTkImageClip(proj):
    "Rectangular clip of image."
    elem = thanSelect1(proj, T["Select an image: "], filter=lambda e: isinstance(e, thandr.ThanImage))
    if elem == Canc: return thanModCanc(proj)                         # Location cancelled
    if elem.transpose != 0:    #FIXME
        return thanModCanc(proj, "For the moment, the image must not be rotated in order to clip it.")
    while True:
        if elem.clipped:
            c1 = proj[2].thanGudGetPoint(T["First point (delete clip): "], options=("delete",))
            if c1 == Canc: return proj[2].thanGudCommandCan()      # Rectangle cancelled
            if c1 == "d":
                elem.thanClipDel()
                break
        else:
            c1 = proj[2].thanGudGetPoint(T["First point: "])
            if c1 == Canc: return proj[2].thanGudCommandCan()      # Rectangle cancelled
        c2 = proj[2].thanGudGetRect(c1, T["Second point: "])
        if c2 == Canc: return proj[2].thanGudCommandCan()      # Rectangle cancelled
        ok, terr = elem.thanClip((c1, c2))
        if ok: break
        proj[2].thanPrter("%s. %s" % (T[terr], T["Try again."]))

    proj[1].thanDoundo.thanAdd("imageclip", __clipRedo, (elem, c1, c2),
                                            __clipUndo, (elem,))
    proj[2].thanAutoRegen(regenImages=True)    #FIXME: Actually only one image must be redisplayed
    proj[1].thanTouch()
    thanModEnd(proj)

def __clipRedo(proj, elem, c1, c2):
    ok, terr = elem.thanClip((c1, c2))
    proj[2].thanAutoRegen(regenImages=True)    #FIXME: Actually only one image must be redisplayed

def __clipUndo(proj, elem):
    elem.thanClipDel()
    proj[2].thanAutoRegen(regenImages=True)    #FIXME: Actually only one image must be redisplayed


def thanTkImageBrighten(proj, verbose=True):
    "Brighten all raster images."
    db = 0.2
    if proj[2].than.imageBrightness+db*0.1 >= 3.0-db:
        if verbose: return proj[2].thanGudCommandEnd()
        else: return
    proj[2].than.imageBrightness += db
    proj[2].thanAutoRegen(regenImages=True)
    if verbose: return proj[2].thanGudCommandEnd()


def thanTkImageDarken(proj, verbose=True):
    "Darken all raster images."
    db = 0.2
    if proj[2].than.imageBrightness-db*0.1 <= db:
        if verbose: return proj[2].thanGudCommandEnd()
        else:       return
    proj[2].than.imageBrightness -= db
    proj[2].thanAutoRegen(regenImages=True)
    if verbose: return proj[2].thanGudCommandEnd()


def thanTkImageBreset(proj, verbose=True):
    "Reset image brightness to original for each photo."
    proj[2].than.imageBrightness = 1.0
    proj[2].thanAutoRegen(regenImages=True)
    return proj[2].thanGudCommandEnd()


def thanTkImageFrame(proj):
    "Set imageframe on or off."
    prev = bool(proj[1].thanVar["imageframe"])
    defa = ("OFF", "ON")[prev]
    proj[2].thanPrt(T["Imageframe is %s."] % (defa, ))
    mes = T["Enter image frame setting [ON/OFF] <%s>: "] % (defa, )
    imfr = proj[2].thanGudGetOnoff(mes, default=defa)
    if imfr == Canc: return proj[2].thanGudCommandCan()
    __regenimages(proj, imfr)
    proj[1].thanDoundo.thanAdd("imageframe", __regenimages, (imfr,),
                                             __regenimages, (prev,))
    proj[2].thanGudCommandEnd()

def __regenimages(proj, imfr):
    "Regenerate images, set variables and print result."
    imfr = bool(imfr)
    proj[1].thanVar["imageframe"] = imfr
    proj[2].than.imageFrameOn = imfr
    proj[2].thanAutoRegen(regenImages=True)
    proj[2].thanPrtbo(T["Imageframe is now %s."] % ( ("OFF", "ON")[imfr], ))


def thanImageRendering(proj):
    "Choose the quick/average or slow/best mode of rendering images."
    from thandr.thanimpil import thanSetRendering, thanGetRendering
    modep = thanGetRendering()  # Previous rendering mode
    if modep == 0: proj[2].thanCom.thanAppend(T["Current image rendering mode: Quick\n"], "info1")
    else:          proj[2].thanCom.thanAppend(T["Current image rendering mode: Best\n"],  "info1")

    res = proj[2].thanGudGetOpts(T["Select rendering mode of images (Quick/Best) <Quick>: "], default="Quick", options=("Quick", "Best"))
    if res == Canc: return proj[2].thanGudCommandCan() # Render cancelled
    if res == "q": moden = 0    # Quick rendering of images
    else:          moden = 1    # Best rendering of images
    thanSetRendering(moden)     # Set new rendering mode

    if moden != modep: proj[2].thanAutoRegen(regenImages=True)    # If mode changes, regenerate images
    proj[2].thanGudCommandEnd()
