from __future__ import print_function
#from past.builtins import xrange
from p_ggen.py23 import xrange
from math import pi, hypot, atan2, fabs
from p_gmath import PI2, thanNearx
from .thanextrusion import thanDxfExtrusion2World, thanDxfExtrusionVectors


#FIXME: extrusion must be implemented for all 2dimensional elements (which means almost all!)

PLINECLOSED   = 1
PLINE3        = 8
PLINEVERTEX3  = 32
PLINEWHOKNOWS = 128
ZDEFAULT      = 0.0           # Default z for all objects


class ThanEntities:
    "Mixin to import the drawing entities from a dxf file."

#===========================================================================

    def thanGetEntities(self):
        "Imports the actual entities."

        entities = { "POLYLINE"      : self.__getPolylinep,
                     "LINE"          : self.__getLinep,
                     "TEXT"          : self.__getTextp,
                     "POINT"         : self.__getPointp,
                     "CIRCLE"        : self.__getCirclep,
                     "ARC"           : self.__getArcp,
                     "ELLIPSE"       : self.__getEllipsep,
                     "INSERT"        : self.__getBlockAtt,
                     "THANCAD_IMAGE" : self.__getThanCadImagep,
                     "3DFACE"        : self.__get3dfacep,
                   }

        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1: return              # End of file
            if icod == 0:
                if text == "ENDSEC": return
                if text == "SECTION":
                    self.thanUngetDxf()
                    self.thanWarn("Incomplete section ENTITIES: probably corrupted file.")
                    return
                entities.get(text, lambda: None)()

#===========================================================================

    def __getPolylinep(self):
        """Reads a polyline from .dxf file.

        2011_04_03: Atribute 66 is redundant. It means that the polyline has vertices
        which follow right after the various attributes of the polyline.
        See Paul Bourke's dxf10 compilation: http://paulbourke.net/dataformats/dxf/dxf10.html
        Also saved in the documentation folder.
        2011_04_03: It seems that when the (free for now) program draftsight exports dxf12
        it stores the elevation of a whole 2d polyline in the polyline attributes and
        puts z=0 to the VERTEX entities. So, if the elevation of the polyline z != 0
        AND the vertices all(?) have z==0, then we put the polylines z to all vertices.
        """

#-------try to find layer, closed

        atts = {}
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1: return
            if icod == 0: self.thanUngetDxf(); break   # VERTEX, SEQEND, or other element
            atts[icod] = text

        if self.trAtts(atts, str, -8) or self.trAtts(atts, int, -62, -70) or \
            self.trAttsFloat(atts, -30, -210, -220, -230):
            self.thanWarn("Incomplete polyline: probably corrupted file.")
        self.defLay = atts.get(8, self.defLay)
        handle = atts.get(5, "")
        col = atts.get(62, -1)
        if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
        flags = atts.get(70, 0)
        closed = flags & PLINECLOSED
        zdef = atts.get(30, 0.0)         # z of whole polyline; if noexistent or 0.0 use XDEFAULT for VERTEX
        if 210 in atts and 220 in atts and 230 in atts:    # Extrusion
            _, _, _, wx, wy, wz = thanDxfExtrusionVectors((atts[210], atts[220], atts[230]))
            extrusion = True
        else:
            extrusion = False

#-------read vertices

        xx = []
        yy = []
        zz = []
        firstz = True
        while 1:

#-----------Find if vertex follows

            icod, text = self.thanGetDxf()
            if icod == -1:                    # Abnormal end of polyline, and end of file
                self.thanWarn("Incomplete polyline: end of file.")
                break
            assert icod == 0, "We exit the loop only with zero code!"
            if text == "SEQEND": break        # Normal end of polyline
            if text != "VERTEX":              # Abnormal end of polyline, but not end of file
                self.thanUngetDxf()
                self.thanWarn("Incomplete polyline: probably corrupted file.")
                break

#-----------Read coordinates of the vertex

            atts = { }
            while 1:
                icod, text = self.thanGetDxf()
                if icod == -1:                # End of file, but try to read current vertex
                    self.thanWarn("Incomplete polyline vertex: end of file.")
                    break
                if icod == 0: self.thanUngetDxf(); break  # Vertex, SEQEND or other element
                atts[icod] = text

            if self.trAttsFloat(atts, 10, 20, -30):
                self.thanWarn("Damaged polyline vertex: probably corrupted file.")
            else:
                xx.append(atts[10])
                yy.append(atts[20])
                z1 = atts.get(30, None)
                if z1 is None:
                    z1 = zdef
                else:
                    if z1 == 0.0:
                        z1 = zdef
                    elif zdef != 0.0 and z1 != zdef and firstz:
                        self.thanWarn("Vertex z=%f is not the same with global polyline z=%f" % (zdef, z1))
                        firstz = False
                zz.append(z1)

#-------Store the polyline

        if len(xx) < 2:
            self.thanWarn("Polyline with 1 or 0 vertices.")
        else:
            if closed and (xx[0] != xx[-1] or yy[0] != yy[-1] or zz[0] != zz[-1]):
                xx.append(xx[0])
                yy.append(yy[0])
                zz.append(zz[0])
            if extrusion: thanDxfExtrusion2World(wx, wy, wz, xx, yy, zz)
#            print "line:"
#            for i in xrange(len(xx)): print xx[i], yy[i]

            self.thanDr.dxfPolyline(xx, yy, zz, self.defLay, handle, col)

#===========================================================================

    def __getLinep(self):
        "Reads a line from .dxf file."
        atts = { }
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current line
                self.thanWarn("Incomplete line: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, -30, 11, 21, -31, -210, -220, -230) or \
           self.trAtts(atts, str, -8) or self.trAtts(atts, int, -62):
            self.thanWarn("Damaged line: probably corrupted file.")
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
            xx = [atts[10], atts[11]]
            yy = [atts[20], atts[21]]
            zz = [atts.get(30, ZDEFAULT), atts.get(31, ZDEFAULT)]
            if 210 in atts and 220 in atts and 230 in atts:
                _, _, _, wx, wy, wz = thanDxfExtrusionVectors((atts[210], atts[220], atts[230]))
                thanDxfExtrusion2World(wx, wy, wz, xx, yy, zz)
#            print "line:"
#            for i in xrange(len(xx)): print xx[i], yy[i]
            self.thanDr.dxfLine(xx, yy, zz, self.defLay, handle, col)

#===========================================================================

    def __getPointp(self):
        "Reads a point from .dxf file."
        atts = { }
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current line
                self.thanWarn("Incomplete point: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, -30) or self.trAtts(atts, str, -8) or\
           self.trAtts(atts, int, -62):
            self.thanWarn("Damaged point: probably corrupted file.")
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
            xx = atts[10]
            yy = atts[20]
            zz = atts.get(30, ZDEFAULT)
            self.thanDr.dxfPoint(xx, yy, zz, self.defLay, handle, col)

#===========================================================================

    def __getTextp(self):
        "Reads a text from .dxf file."
        atts = { }
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current line
                self.thanWarn("Incomplete text: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, -30, 40, -50) or self.trAtts(atts, str, 1, -8) or\
           self.trAtts(atts, int, -62):
            self.thanWarn("Damaged text: probably corrupted file.")
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
            xx = atts[10]     #left point
            yy = atts[20]     #left point
            zz = atts.get(30, ZDEFAULT)
            h = atts[40]
            theta = atts.get(50, 0.0)
            text = atts[1]
            if self.thanDxfVer == 2000:      #This is for dxf2000
                self.trAttsFloat(atts, -11, -21)
                if 11 in atts and 21 in atts:
                    xx = atts[11]    #Insertion point may be at center or at left 
                    yy = atts[21]
            self.thanDr.dxfText(xx, yy, zz, self.defLay, handle, col, text, h, theta)

#===========================================================================

    def __getCirclep(self):
        "Reads a circle from .dxf file."
        atts = { }
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current line
                self.thanWarn("Incomplete circle: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, -30, 40) or self.trAtts(atts, int, -62):
            self.thanWarn("Damaged circle: probably corrupted file.")
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
            xx = atts[10]
            yy = atts[20]
            zz = atts.get(30, ZDEFAULT)
            r = atts[40]
#            print "circle:", xx, yy, r
            self.thanDr.dxfCircle(xx, yy, zz, self.defLay, handle, col, r)

#===========================================================================

    def __getArcp(self):
        "Reads an arc from .dxf file."
        atts = {}
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current line
                self.thanWarn("Incomplete arc: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, -30, 40, 50, 51) or self.trAtts(atts, int, -62):
            self.thanWarn("Damaged arc: probably corrupted file.")
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
            xx = atts[10]
            yy = atts[20]
            zz = atts.get(30, ZDEFAULT)
            r = atts[40]
#           print "arc:", xx, yy, r, atts[50], (atts[51]-atts[50])%360.0
            theta1 = (atts[50]%360.0)   #*pi/180 Thanasis2011_02_11Commented out
            theta2 = (atts[51]%360.0)   #*pi/180 Thanasis2011_02_11Commented out
            self.thanDr.dxfArc(xx, yy, zz, self.defLay, handle, col, r, theta1, theta2)

#===========================================================================

    def __getEllipsep(self):
        "Reads an elliptic arc from .dxf file."
        atts = {}
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current line
                self.thanWarn("Incomplete arc: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, -30, 11, 21, -31, 40, 41, 42) or self.trAtts(atts, int, -62):
            self.thanWarn("Damaged elliptic arc: probably corrupted file.")
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
            xx = atts[10]
            yy = atts[20]
            zz = atts.get(30, ZDEFAULT)
            xxa = atts[11]
            yya = atts[21]
            a = hypot(yya, xxa)
            dr = 180.0/pi
            phi = atan2(yya, xxa)*dr
            b = a * atts[40]
            theta1 = atts[41]
            theta2 = atts[42]
            full = thanNearx(fabs(theta2-theta1)*a, PI2*a)  #True if it is full ellipse (not an arc)
            print("elliptic arc:", xx, yy, a, b, theta1, theta2, phi, full)
            self.thanDr.dxfEllipse(xx, yy, zz, self.defLay, handle, col, a, b,
                theta1*dr, theta2*dr, phi, full)

#===========================================================================

    def __getBlockAtt(self):
        "Reads a block with attributes from .dxf file."
#-------try to find layer, closed
        atts = {}
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1: return
            if icod == 0: self.thanUngetDxf(); break   # ATTRIBUTE, SEQEND, or other element
            atts[icod] = text

        if self.trAtts(atts, str, 2, -8) or self.trAtts(atts, int, -62) or self.trAttsFloat(atts, 10, 20, -30):
            self.thanWarn("Incomplete block insertion: probably corrupted file.")
        blname = atts[2]
        self.defLay = atts.get(8, self.defLay)
        handle = atts.get(5, "")
        col = atts.get(62, -1)
        if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
        xins = atts[10]
        yins = atts[20]
        zins = atts.get(30, ZDEFAULT)

#-------read attributes

        blatts = {}
        attsdefined = False                  # If no attributes are defined, "endsec" is not needed
        while 1:

#-----------Find if attribute follows

            icod, text = self.thanGetDxf()
            if icod == -1:                    # Abnormal end of block, and end of file
                self.thanWarn("Incomplete block insertion: end of file.")
                break
            assert icod == 0, "We exit the loop only with zero code!"
            if text == "SEQEND": break        # Normal end of block insertion
            if text != "ATTRIB":              # Abnormal end of block insertion, but not end of file
                if not attsdefined: break     # Normal end after all
                self.thanUngetDxf()
                self.thanWarn("Incomplete block insertion: probably corrupted file.")
                break
            attsdefined = True

#-----------Read name and value of the attribute

            atts = {}
            while 1:
                icod, text = self.thanGetDxf()
                if icod == -1:                # End of file, but try to read current attribute
                    self.thanWarn("Incomplete block attribute: end of file.")
                    break
                if icod == 0: self.thanUngetDxf(); break  # Vertex, SEQEND or other element
                atts[icod] = text

            if self.trAtts(atts, str, 1, 2):
                self.thanWarn("Damaged block attribute: probably corrupted file.")
            else:
                blatts[atts[2].upper()] = atts[1]       # name, value pair: Hopefully names are unique

#-------Store the block insertion

        self.thanDr.dxfBlockAtt(xins, yins, zins, self.defLay, handle, col, blname, blatts)

#===========================================================================

    def __getThanCadImagep(self):
        "Reads a ThanCad Image from .dxf file."
        atts = { }
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current image
                self.thanWarn("Incomplete ThanCad image: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, -30, 40, 41, 42, 50) or self.trAtts(atts, str, 1, -8) or\
           self.trAtts(atts, int, -62):
            self.thanWarn("Damaged ThanCad image: probably corrupted file.")
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
            xx = atts[10]
            yy = atts[20]
            zz = atts.get(30, ZDEFAULT)
            size = atts[40], atts[41]
            scale = atts[42]
            theta = atts.get(50, 0.0)
            filnam = atts[1]
            self.thanDr.dxfThanImage(xx, yy, zz, self.defLay, handle, col, filnam, size, scale, theta)

#===========================================================================

    def __get3dfacep(self):
        "Reads a 3dface (triangle or quadrilateral) from .dxf file."
        atts = { }
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current line
                self.thanWarn("Incomplete 3dface: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, 30, 11, 21, 31, 12, 22, 32, -13, -23, -33) or \
           self.trAtts(atts, int, -62):
            self.thanWarn("Damaged 3dface: probably corrupted file.")
            return
        if 13 in atts or 23 in atts or 33 in atts:
            if 13 not in atts or 23 not in atts or 33 not in atts:
                self.thanWarn("Damaged 3dface: probably corrupted file.")
                return
            c = 4
        else:
            c = 3

        self.defLay = atts.get(8, self.defLay)
        handle = atts.get(5, "")
        col = atts.get(62, -1)
        if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
        xx = [atts[10+i] for i in xrange(c)]
        yy = [atts[20+i] for i in xrange(c)]
        zz = [atts[30+i] for i in xrange(c)]
        self.thanDr.dxf3dface(xx, yy, zz, self.defLay, handle, col)
