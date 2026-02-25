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

This module defines functionality necessary for drawing elements on a tkinter
drawing window.
"""

from math import pi, sin, cos, atan2
from tkinter import ARC
from p_gmath import PI2
import p_ggen
from thanopt import thancadconf
from thandefs import thanatt


class ThanTkGuiHighDraw:
    "Mixin for highlevel drawing to Tk window."

    def __init__(self):
        "Initialisation of the selection containers."
        self.thanSelold = set()
        self.thanSelall = set()
        self.thanSel    = set()
        self.thanSel1coor = None        # This is the first point in the 'break' command


    def thanGudSetSelClone(self, col=thanatt.ThanAttCol(thancadconf.thanColSel).thanTk):
        "Copies the selected items; the copies have the tag 'edrag'."
        dc = self.thanCanvas
        tags = ("edrag", )
        for item in dc.find_withtag("selall"):
            t = dc.type(item)
            cs = dc.coords(item)
            if t == "line":
                dc.create_line(cs, fill=col, tags=tags)
            elif t == "text":
                te = dc.itemcget(item, "text")
                an = dc.itemcget(item, "angle")
                fo = dc.itemcget(item, "font")
                dc.create_text(cs, text=te, anchor="sw", angle=an, font=fo, fill=col, tags=tags)
            elif t == "polygon":
                dc.create_polygon(cs, outline=col, tags=tags)
            elif t == "rectangle":
                dc.create_rectangle(cs, outline=col, tags=tags)
            elif t == "oval":
                dc.create_oval(cs, outline=col, tags=tags)
            elif t == "arc":
                st = dc.itemcget(item, "start")
                ex = dc.itemcget(item, "extent")
                dc.create_arc(cs, start=st, extent=ex, style=ARC, outline=col, tags=tags)
            elif t == "image":
                imz = dc.itemcget(item, "image")
                dc.create_image(cs, image=imz, anchor="nw", tags=tags)
            else:
                assert False, t+": unknown Canvas type!!!"


    def thanGudSetDrag(self, elems, col=thanatt.ThanAttCol(thancadconf.thanColSel).thanTk):
        "Draws the defined elements for dragging; they will have the tag 'edrag'."
        than = self.than
        colsor = than.fill, than.outline
        than.fill = ""
        than.outline = col

        tags = ("edrag", )
        for e in elems:
            tagsor = e.thanTags
            e.thanTags = tags
            e.thanTkDraw(self.than)
            e.thanTags = tagsor

        than.fill, than.outline = colsor


    def thanGudMoveDrag(self, dx, dy):
        "Moves the dragged canvas items."
        if dx == 0.0 and dy == 0.0: return
        dxp, dyp = self.thanCt.global2LocalRel(dx, dy)
        self.thanCanvas.move("edrag", dxp, dyp)


    def thanGudSetSelColor(self, col=thanatt.ThanAttCol(thancadconf.thanColSel).thanTk):
        "Changes the color or the outline of the canvas items with tag 'sel'."
        self.thanGudGetSelx()
        self.thanGudSetSelColorx(col)


    def thanGudResetSelColor(self):
        "Resets the color or the outline of the selected items to original value."
        proj = self.thanProj
        tlays = set(elem.thanTags[1] for elem in proj[2].thanSelall)
        dilay = proj[1].thanLayerTree.dilay
        for tlay in tlays:
            lay = dilay[tlay]
            proj[2].thanGudGetSelLayerxs(tlay)
            outline, fill = lay.thanGetColour()
            proj[2].thanGudSetSelColorx(outline, fill)


    def thanGudSetSelLayertag(self, tlay):
        "Sets new layer tag to all selected elements."
        dc = self.thanCanvas
        for item in dc.find_withtag("selall"):
            tags = list(dc.gettags(item))
            tags[1] = tlay
            dc.itemconfig(item, tags=tuple(tags))


    def thanGudSetSelElem(self, elems):
        "Selects the defined elements, as the most recent selection (saves the old selection."
        dc = self.thanCanvas
        self.thanGudSetSelSave()
        self.thanSelall = elems
        for e in elems: dc.addtag_withtag("selall", e.thanTags[0])


    def thanGudSetSelElem1(self, elems):
        "Selects the defined elements, as the most recent selection (but does not save the old selection)."
        dc = self.thanCanvas
        self.thanSelall = elems
        for e in elems: dc.addtag_withtag("selall", e.thanTags[0])


    def thanGudSetUnselElem(self, elems):
        "Unselects the defined elements from the most recent selection."
        dc = self.thanCanvas
        for e in elems: dc.dtag(e.thanTags[0], "selall")


    def thanGudSetSeloldElem(self, elems):
        "Selects the defined elements as the old selection."
        dc = self.thanCanvas
        self.thanSelold = elems
        for e in elems: dc.addtag_withtag("selold", e.thanTags[0])


    def thanGudSetSelClear(self):
        "Clears all kind of selections."
        dc = self.thanCanvas
        dc.dtag("all", "selold")
        dc.dtag("all", "selall")
        dc.dtag("all", "sel")
        dc.dtag("all", "line")
        dc.dtag("all", "nlin")
        self.thanSelold = set()
        self.thanSelall = set()
        self.thanSel    = set()


    def thanGudSetSelcurClear(self):
        "Clears current selection."
        dc = self.thanCanvas
        dc.dtag("selall", "sel")
        self.thanSel = set()


    def thanGudSetSelSave(self):
        "Saves the current selection as old, and clears current selection."
        dc = self.thanCanvas
        dc.dtag("all", "selold")
        dc.addtag_withtag("selold", "selall")
        dc.dtag("all", "selall")
        dc.dtag("all", "sel")
        dc.dtag("all", "line")
        dc.dtag("all", "nlin")
        self.thanSelold = self.thanSelall
        self.thanSelall = set()
        self.thanSel    = set()


    def thanGudSetSelRestore(self):
        "Restores old selection; undoes a previous thanGusSetSelSave."
        dc = self.thanCanvas
        dc.dtag("all", "selall")
        dc.dtag("all", "sel")
        dc.dtag("all", "line")
        dc.dtag("all", "nlin")
        dc.addtag_withtag("selall", "selold")
        dc.dtag("all", "selold")
        self.thanSelall = self.thanSelold
        self.thanSelold = set()
        self.thanSel    = set()


    def thanGudSetSelDel(self):
        "Deletes the selected canvas items (but not ThanCad's elements)."
        dc = self.thanCanvas
        dc.delete("selall")


    def thanGudSetFreezeLayer(self, lay):
        """Erases all the canvas items of the active elements of a layer.

        It does not delete ThanCad's elements."""
        dc = self.thanCanvas
        dc.delete(lay.thanTag)


    def thanGudSetSelRotateBoth_old(self, xc, yc, phi):
        """Rotates both the selected canvas items _and_ ThanCad's elements.

        I keep this routine so that I can remember the hack with tagel, and tagseen.
        """
        import time
        from thandr.thanelem import ThanElement
        phi %= PI2
        if phi == 0.0: return
        ThanElement.thanRotateSet(xc, yc, phi)
        xcp, ycp = self.thanCt.global2Local(xc, yc)
        ThanElement.thanRotateSetp(xcp, ycp, -phi)   # The opposite y-axis changes the sign of the angle

        dc = self.thanCanvas
        tagel = self.thanProj[1].thanTagel
        tagseen = {}

        t1 = time.time()
        for item in dc.find_withtag("selall"):
#           titem = dc.itemcget(item, "tags").split()[0]
            titem = dc.gettags(item)[0]
            if titem not in tagseen:
                tagseen[titem] = True
                e = tagel[titem]
                e.thanRotate()
            t = dc.type(item)
            c = dc.coords(item)
            if t == "arc":
                dx = (c[2]-c[0])/2; dy = (c[3]-c[1])/2
                c = [c[0]+dx, c[1]+dy]
                ThanElement.thanRotateXypn2(c)
                c = c[0]-dx, c[1]-dy, c[0]+dx, c[1]+dy
                th = float(dc.itemcget(item, "start"))
                dc.itemconfigure(item, start=(th+phi)%360)
            elif t == "oval":
                dx = (c[2]-c[0])/2; dy = (c[3]-c[1])/2
                c = [c[0]+dx, c[1]+dy]
                ThanElement.thanRotateXypn2(c)
                c = c[0]-dx, c[1]-dy, c[0]+dx, c[1]+dy
            else:
                ThanElement.thanRotateXypn2(c)
            dc.coords(item, *c)
        t2 = time.time()
        print("Rotated in", t2-t1, "secs")
        self.thanProj[1].thanTouch()


    def thanGudSetSelRotate(self, xc, yc, phi):
        "Rotates the selected canvas items; it does not rotate ThanCad's elements."
        from thandr.thanelem import ThanElement
        if phi == 0.0: return
        xcp, ycp = self.thanCt.global2Local(xc, yc)
        ThanElement.thanRotateSetp(xcp, ycp, -phi)   # The opposite y-axis changes the sign of the angle
        phi = (phi*180.0/pi) % 360.0

        dc = self.thanCanvas
        tagel = self.thanProj[1].thanTagel
        for item in dc.find_withtag("selall"):
            t = dc.type(item)
            c = dc.coords(item)
            if t == "arc":
                dx = (c[2]-c[0])/2; dy = (c[3]-c[1])/2
                c = [c[0]+dx, c[1]+dy]
                ThanElement.thanRotateXypn2(c)
                c = c[0]-dx, c[1]-dy, c[0]+dx, c[1]+dy
                th = float(dc.itemcget(item, "start"))
                dc.itemconfigure(item, start=(th+phi)%360)
            elif t == "oval":
                dx = (c[2]-c[0])/2; dy = (c[3]-c[1])/2
                c = [c[0]+dx, c[1]+dy]
                ThanElement.thanRotateXypn2(c)
                c = c[0]-dx, c[1]-dy, c[0]+dx, c[1]+dy
            elif t == "rectangle":
                dx = (c[2]-c[0])      #c[0],c[1] is always the upper left corner
                dy = (c[3]-c[1])      #c[2],c[3] is always the lower right corner
                c = [c[0], c[3]]      #This is the lower left corner
                ThanElement.thanRotateXypn2(c)
                c.append(c[0]+dx)     #This is the new upper..
                c.append(c[1]-dy)     #..right corner
            elif t == "image" or t == "bitmap":   #Thanasis2022_12_20: code for bitmap and image
                titem = dc.gettags(item)[0]
                e = tagel[titem]
                im = e.imagez
                if im is None:
                    print("Warning: associated Element of canvas.image, does not have the photoimage!!")
                    return
                dy = im.height()                  #c[0],c[1] is always the upper left corner
                c = [c[0], c[1]+dy]               #This the lower left corner (y axis positive is downwards)
                ThanElement.thanRotateXypn2(c)
                c = [c[0], c[1]-dy]               #This is the new upper left corner
            else:   #line, polygon, text
                ThanElement.thanRotateXypn2(c)
            dc.coords(item, *c)


    def thanGudSetSelRotateins(self, phi):
        """Rotates the selected canvas items individually.

        It rotates with respect to the insertion point of each ThanCad's
        element. It does not rotate ThanCad's elements."""
        from thandr.thanelem import ThanElement
        if phi == 0.0: return
        phir = phi
        phi = (phi*180.0/pi) % 360.0

        dc = self.thanCanvas
        tagel = self.thanProj[1].thanTagel
        for item in dc.find_withtag("selall"):
            t = dc.type(item)
            c = dc.coords(item)
            titem = dc.gettags(item)[0]
            e = tagel[titem]
            cc = e.getInspnt()
            xcp, ycp = self.thanCt.global2Local(cc[0], cc[1])
            ThanElement.thanRotateSetp(xcp, ycp, -phir)   # The opposite y-axis changes the sign of the angle
            if t == "arc":
                dx = (c[2]-c[0])/2; dy = (c[3]-c[1])/2
                c = [c[0]+dx, c[1]+dy]
                ThanElement.thanRotateXypn2(c)
                c = c[0]-dx, c[1]-dy, c[0]+dx, c[1]+dy
                th = float(dc.itemcget(item, "start"))
                dc.itemconfigure(item, start=(th+phi)%360)
            elif t == "oval":
                dx = (c[2]-c[0])/2; dy = (c[3]-c[1])/2
                c = [c[0]+dx, c[1]+dy]
                ThanElement.thanRotateXypn2(c)
                c = c[0]-dx, c[1]-dy, c[0]+dx, c[1]+dy
            elif t == "rectangle":
                dx = (c[2]-c[0])      #c[0],c[1] is always the upper left corner
                dy = (c[3]-c[1])      #c[2],c[3] is always the lower right corner
                c = [c[0], c[3]]      #This is the lower left corner
                ThanElement.thanRotateXypn2(c)
                c.append(c[0]+dx)     #This is the new upper..
                c.append(c[1]-dy)     #..right corner
            else:
                ThanElement.thanRotateXypn2(c)
            dc.coords(item, *c)


    def thanGudSetSelMirror(self, xc, yc, t):
        "Mirrors the selected canvas items; it does ThanCad's elements."
        from thandr.thanelem import ThanElement
        xcp, ycp = self.thanCt.global2Local(xc, yc)
        ThanElement.thanMirrorSetp(xcp, ycp, (t[0], -t[1]))   # Opposite y-axis in pixel coordinates

        dc = self.thanCanvas
        for item in dc.find_withtag("selall"):
            t = dc.type(item)
            c = dc.coords(item)
            if t == "arc":
                dx = (c[2]-c[0])/2; dy = (c[3]-c[1])/2
                c = [c[0]+dx, c[1]+dy]
                r = 1.0                                       # Not the real radius; we only need a direction
                th = float(dc.itemcget(item, "start")) * pi/180
                c1 = [c[0]+r*cos(th), c[1]-r*sin(th)]         # Opposite y-axis in pixel coordinates
                ThanElement.thanMirrorXypn2(c)
                ThanElement.thanMirrorXypn2(c1)
                th = atan2(-(c1[1]-c[1]), c1[0]-c[0])*180/pi  # Opposite y-axis in pixel coordinates
                c = c[0]-dx, c[1]-dy, c[0]+dx, c[1]+dy
                the = float(dc.itemcget(item, "extent"))
                dc.itemconfigure(item, start=th, extent=-the) # Opposite extent angle after mirror
            elif t == "oval":
                dx = (c[2]-c[0])/2; dy = (c[3]-c[1])/2
                c = [c[0]+dx, c[1]+dy]
                ThanElement.thanMirrorXypn2(c)
                c = c[0]-dx, c[1]-dy, c[0]+dx, c[1]+dy
            elif t == "rectangle":
                dx = (c[2]-c[0])      #c[0],c[1] is always the upper left corner
                dy = (c[3]-c[1])      #c[2],c[3] is always the lower right corner
                c = [c[0], c[3]]      #This is the lower left corner
                ThanElement.thanMirrorXypn2(c)
                c.append(c[0]+dx)     #This is the new upper..
                c.append(c[1]-dy)     #..right corner
            else:
                ThanElement.thanMirrorXypn2(c)
            dc.coords(item, *c)


    def thanGudSetSelScale(self, xc, yc, fact):
        "Scales the selected canvas items; it does not scale ThanCad's elements."
        if fact == 1.0: return
        xcp, ycp = self.thanCt.global2Local(xc, yc)
        dc = self.thanCanvas
        dc.scale("selall", xcp, ycp, fact, fact)  # This does not scale images; only the insertion point is moved
        self.thanAutoRegen(regenImages=True)      # This will regenerate the image scaled


    def thanGudSetSelScaleIns(self, fact):
        """Scales the selected canvas items individually.

        It scales with respect to the insertion point of each ThanCad's
        element. It does not scale ThanCad's elements."""
        if fact == 1.0: return
        dc = self.thanCanvas
        items = set(dc.find_withtag("selall"))  # Find all geometrically selected items
        tagel = self.thanProj[1].thanTagel
        while len(items) > 0:
            for item in items: break
            titem = dc.gettags(item)[0]
            items1 = set(dc.find_withtag(titem)) # These are the items of a single ThanCad (compound) element
            e = tagel[titem]
            cc = e.getInspnt()
            xcp, ycp = self.thanCt.global2Local(cc[0], cc[1])
            dc.scale(titem, xcp, ycp, fact, fact)  # This does not scale images; only the insertion point is moved
            items -= items1
        self.thanAutoRegen(regenImages=True)      # This will regenerate the image scaled


    def thanGudSetSelScaleBothOld(self, xc, yc, fact):
        """Scales both the selected canvas items _and_ ThanCad's elements.

        I keep this routine so that I can remember the hack with tagel, and tagseen.
        """
        import time
        if fact == 1.0: return
        xcp, ycp = self.thanCt.global2Local(xc, yc)
        dc = self.thanCanvas
        tagel = self.thanProj[1].thanTagel
        tagseen = {}
        t1 = time.time()
        for item in dc.find_withtag("selall"):
#            titem = dc.itemcget(item, "tags").split()[0]
            titem = dc.gettags(item)[0]
            if titem in tagseen: continue
            tagseen[titem] = True
            e = tagel[titem]
            e.thanScale(xc, yc, fact)
        t2 = time.time()
        print("Net Element Scaled in", t2-t1, "secs")
        t1 = t2
        dc.scale("sel", xcp, ycp, fact, fact)
        t2 = time.time()
        print("Net Canvas  Scaled in", t2-t1, "secs")
        self.thanProj[1].thanTouch()


    def thanGudSetSelMove(self, dx, dy):
        "Moves the selected canvas items."
        if dx == 0.0 and dy == 0.0: return
        dxp, dyp = self.thanCt.global2LocalRel(dx, dy)
        dc = self.thanCanvas
        dc.move("selall", dxp, dyp)


    def thanGudDrawElemsMany(self, elems):
        "Draw many ThanCad's elements to a canvas efficiently."
        than = self.than
        lt = self.thanProj[1].thanLayerTree
        thanCur1 = lt.thanCur
        dilay = lt.dilay

        #elems = [(dilay[e.thanTags[1]], e) for e in elems]
        #elems.sort()
        #for lay, e in elems:
        #   if lay != lt.thanCur:
        #       lay.thanTkSet(than)
        #       lt.thanCur = lay
        #   e.thanTkDraw(than)
        for lay, layelems in p_ggen.groupitems(elems, key=lambda e: dilay[e.thanTags[1]]):
            if lay != lt.thanCur:
                lay.thanTkSet(than)
                lt.thanCur = lay
            for e in layelems: e.thanTkDraw(than)

        lay = thanCur1
        if lay != lt.thanCur:
            lay.thanTkSet(than)
            lt.thanCur = lay


#---Non-reentrant module which handles tags "selx" and it is independent to the normal
#   selection mechanism.

    def thanGudGetSelElemx(self, elems):
        """Selects as "x" all the defined elements.

        it does not interfere with normal selection mechanism."""
        dc = self.thanCanvas
        dc.dtag("all", "selx")
        for e in elems: dc.addtag_withtag("selx", e.thanTags[0])

    def thanGudSetSelDelx(self):
        """Deletes all canvas items with tag 'selx'.

        It does not interfere with normal selection mechanism."""
        dc = self.thanCanvas
        dc.delete("selx")

    def thanGudGetSelx(self):
        """Selects as "x" all canvas items with "sel" tag (current selection).

        it does not interfere with normal selection mechanism."""
        dc = self.thanCanvas
        dc.dtag("all", "selx")
        dc.addtag_withtag("selx", "sel")


    def thanGudGetSelLayerx(self, tlay):
        """Selects as "x" all active elements of a layer as current selection.

        it does not interfere with normal selection mechanism."""
        dc = self.thanCanvas
        dc.dtag("all", "selx")
        dc.addtag_withtag("selx", tlay)  # Add sel to all items of the layer


    def thanGudGetSelLayerxs(self, tlay):
        """Selects as "x" all active elements of a layer which also have tag 'selall'.

        It does not interfere with normal selection mechanism."""
#       print("initially:"; self.prtags())
        dc = self.thanCanvas
        dc.dtag("all", "selx")
#        print("Tag 'selx' removed:"; self.prtags())

        dc.addtag_withtag("sel1", "selall")    # "selall" items have tag "sel1"
#       print("Tag 'sel1' added:"; self.prtags())

        dc.dtag(tlay, "sel1")                  # "selall" items have tag "sel1" except from the items of layer tag tlay
#       print("Tag 'sel1' partialy removed:"; self.prtags())

        dc.addtag_withtag("selx", "selall")    # "selall" items have tag "selx"
#       print("Tag 'selx' added:"; self.prtags())

        dc.dtag("sel1", "selx")                # "selall" items have tag "selx" if they belong to layer tag tlay
#       print("Tag 'selx' partialy removed:"; self.prtags())

        dc.dtag("selall", "sel1")
#       print("Tag 'sel1' removed:"; self.prtags())


    def thanGudSetSelColorx(self, col=thanatt.ThanAttCol(thancadconf.thanColSel).thanTk, fillcol=""):
        """Changes the color or the outline of the canvas items with tag 'selx'.

        It does not interfere with normal selection mechanism."""
        dc = self.thanCanvas
        dc.dtag("all", "linx")
        dc.dtag("all", "nlix")
        dc.addtag_withtag("linx", "selx")
        dc.addtag_withtag("nlix", "selx")
        for item in dc.find_withtag("selx"):
            t = dc.type(item)
            if t == "line" or t == "text":
                dc.dtag(item, "nlix")
            elif t == "image":
                dc.dtag(item, "nlix")
                dc.dtag(item, "linx")
            else:
                dc.dtag(item, "linx")
        dc.itemconfig("linx", fill=col)
        dc.itemconfig("nlix", outline=col, fill=fillcol)

        if fillcol == "": return
        #Fill hatch elements which have solid color
        tagel = self.thanProj[1].thanTagel
        for item in dc.find_withtag("selx"):
            titem = dc.gettags(item)[0]
            e = tagel[titem]
            if e.thanElementName != "HATCH": continue
            if e.itype != 0: continue
            dc.itemconfig(item, outline=col, fill=col)


    def thanGudSetSelDashx(self, dash=()):
        """Changes the dash type of (linear) canvas items with tag 'selx'.

        It does not interfere with normal selection mechanism."""
        dc = self.thanCanvas
        dc.dtag("all", "linx")
        dc.dtag("all", "nlix")
        dc.addtag_withtag("linx", "selx")
        linear = {"arc", "line", "oval", "polygon", "rectangle"}
        for item in dc.find_withtag("selx"):
            t = dc.type(item)
            if t not in linear:
                dc.dtag(item, "linx")
        dc.itemconfig("linx", dash=dash)


if __name__ == "__main__":
    print(__doc__)
