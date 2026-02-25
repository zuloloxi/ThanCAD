from math import pi, hypot, atan2, fabs
from p_gmath import PI2, thanNearx, thanNear2
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
                     "LWPOLYLINE"    : self.__getLwpolylinep,  #Thanasis2023_04_24
                     "LINE"          : self.__getLinep,
                     "TEXT"          : self.__getTextp,
                     "POINT"         : self.__getPointp,
                     "CIRCLE"        : self.__getCirclep,
                     "ARC"           : self.__getArcp,
                     "ELLIPSE"       : self.__getEllipsep,
                     "INSERT"        : self.__getBlockAtt,
                     "THANCAD_IMAGE" : self.__getThanCadImagep,
                     "3DFACE"        : self.__get3dfacep,
                     "HATCH"         : self.__getHatch,
                     "SOLID"         : self.__getSolid,
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
                entities.get(text, self.__getUnknown)(text)    #Thanasis2023_04_24

#===========================================================================

    def __getUnknown(self, name):
        "Reads an unknown enitity from .dxf file."
        atts = {}
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of unknonwn entity, but try to read current line
                self.thanWarn("Incomplete entity '{}': end of file.".format(name))
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAtts(atts, str, -8) or self.trAtts(atts, int, -62):
            self.thanWarn("Damaged entity '{}': probably corrupted file.".format(name))
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero

            self.thanDr.dxfUnknown(name, self.defLay, handle, col)

#===========================================================================

    def __getPolylinep(self, name):
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
            if icod == -1:
                self.thanWarn("Incomplete polyline: end of file.")   #Thanasis2023_04_24
                return
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
#            for i in range(len(xx)): print xx[i], yy[i]

            self.thanDr.dxfPolyline(xx, yy, zz, self.defLay, handle, col)

#===========================================================================

    def __getLwpolylinep(self, name):       #Thanasis2023_04_24
        """Reads a lightweight polyline from .dxf file.

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
            if icod == -1:
                self.thanWarn("Incomplete lwpolyline: end of file.")   #Thanasis2023_04_24
                return
            if icod == 10: self.thanUngetDxf(); break   # x coordinate of first point
            atts[icod] = text

        if self.trAtts(atts, str, -8) or self.trAtts(atts, int, -62, -70) or \
            self.trAttsFloat(atts, -30, -210, -220, -230, -38):
            self.thanWarn("Incomplete lwpolyline: probably corrupted file.")
        self.defLay = atts.get(8, self.defLay)
        handle = atts.get(5, "")
        col = atts.get(62, -1)
        if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
        flags = atts.get(70, 0)
        closed = flags & PLINECLOSED
        zdef = atts.get(30, None)         # z of whole polyline; if noexistent or 0.0 use XDEFAULT for VERTEX
        if zdef is None or zdef == 0.0: zdef = atts.get(38, 0.0) #Code 38 is for LWpolyline  #Thanasis2023_05_05
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
            if icod == -1:                    # Abnormal end of lwpolyline, and end of file
                self.thanWarn("Incomplete lwpolyline: end of file.")
                return
            self.thanUngetDxf()
            if icod == 0: break           # other element

            atts.clear()
            for icodxyz in 10, 20, 30:
                icod, text = self.thanGetDxf()
                if icod == -1:                    # Abnormal end of lwpolyline, and end of file
                    self.thanWarn("Incomplete lwpolyline: end of file.")
                    break
                if icod != icodxyz:
                    if icodxyz == 30: self.thanUngetDxf(); break   #No z present
                    self.thanWarn("Damaged lwpolyline: probably corrupted file.")
                    return
                atts[icod] = text

            if self.trAttsFloat(atts, 10, 20, -30):
                self.thanWarn("Damaged polyline vertex: probably corrupted file.")
                return
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
            self.thanWarn("lwpolyline with 1 or 0 vertices.")
        else:
            if closed and (xx[0] != xx[-1] or yy[0] != yy[-1] or zz[0] != zz[-1]):
                xx.append(xx[0])
                yy.append(yy[0])
                zz.append(zz[0])
            if extrusion: thanDxfExtrusion2World(wx, wy, wz, xx, yy, zz)
#            print "line:"
#            for i in range(len(xx)): print xx[i], yy[i]

            self.thanDr.dxfPolyline(xx, yy, zz, self.defLay, handle, col)


#===========================================================================

    def __getLinep(self, name):
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
           self.trAtts(atts, str, -8) or self.trAtts(atts, int, -62, -370):
            self.thanWarn("Damaged line: probably corrupted file.")
        else:
            self.defLay = atts.get(8, self.defLay)
            handle = atts.get(5, "")
            col = atts.get(62, -1)
            if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero

            linw = atts.get(370, -3)              # -3 means default value, given in hundredths of mm
            if linw <= 0:
                linw = None                       # if -3 (default) let dxfline() decide what to do, if other negative then None (undefined)
            else:
                linw = linw / 100.0               #Convert to mm

            xx = [atts[10], atts[11]]
            yy = [atts[20], atts[21]]
            zz = [atts.get(30, ZDEFAULT), atts.get(31, ZDEFAULT)]
            if 210 in atts and 220 in atts and 230 in atts:
                _, _, _, wx, wy, wz = thanDxfExtrusionVectors((atts[210], atts[220], atts[230]))
                thanDxfExtrusion2World(wx, wy, wz, xx, yy, zz)
#            print "line:"
#            for i in range(len(xx)): print xx[i], yy[i]
            self.thanDr.dxfLine(xx, yy, zz, self.defLay, handle, col, linw)

#===========================================================================

    def __getPointp(self, name):
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

    def __getTextp(self, name):
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

    def __getCirclep(self, name):
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

    def __getArcp(self, name):
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

    def __getEllipsep(self, name):
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

    def __getBlockAtt(self, name):
        "Reads a block with attributes from .dxf file."
#-------try to find layer, closed
        atts = {}
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1: return
            if icod == 0: self.thanUngetDxf(); break   # ATTRIBUTE, SEQEND, or other element
            atts[icod] = text

        if self.trAtts(atts, str, 2, -8) or self.trAtts(atts, int, -62) or self.trAttsFloat(atts, 10, 20, -30):
            self.thanWarn("Incomplete block insertion: probably corrupted file. block insertion is ignored")
            return     #Thanasis2022_07_15:Do not add the block insertion. Continue with other elements
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
                self.thanUngetDxf()  #Thanasis2022_11_12: ungetdxf is called annyway now
                if not attsdefined: break     # Normal end after all
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

    def __getThanCadImagep(self, name):
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

    def __get3dfacep(self, name):
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
        xx = [atts[10+i] for i in range(c)]
        yy = [atts[20+i] for i in range(c)]
        zz = [atts[30+i] for i in range(c)]
        self.thanDr.dxf3dface(xx, yy, zz, self.defLay, handle, col)

#===========================================================================

    def __getSolid(self, name):
        """Reads a solid (triangle or quadrilateral) from .dxf file.

        Note:
        - According to specifications (with thAtCAD), the point are not
          in clockwise or ant-clockwise order.
          In fact, they are in clockwise or anti-clockwise order but with the
          2 last points swapped.
        - This method swaps the 3rd and 4th point, and thus returns the points
          with clockwise or anti-clockwise order.
        - The specifications say that solid has exactly 4 points,
          but if the last 2 points coincide, then it is a triangular solid.
        - This method, if it finds 3 points, then adds 1 with the same
          coodinates as the third, so that it is a valid triangular solid.
        """
        atts = { }
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1:                # End of file, but try to read current line
                self.thanWarn("Incomplete solid: end of file.")
                break
            if icod == 0: self.thanUngetDxf(); break           # other element
            atts[icod] = text

        if self.trAttsFloat(atts, 10, 20, -30, 11, 21, -31, 12, 22, -32, -13, -23, -33) or \
           self.trAtts(atts, int, -62) or self.trAtts(atts, str, -8, -5):
            self.thanWarn("Damaged solid: probably corrupted file.")
            return
        if 13 in atts or 23 in atts or 33 in atts:
            if 13 not in atts or 23 not in atts:
                self.thanWarn("Damaged solid: probably corrupted file.")
                return
            c = 0, 1, 3, 2   #Swap 3rd and 4th point, so that they are in clockwise or anti-clockwise order
        else:
            c = 0, 1, 2, 2   #3 points defined: add a 4th point with the same coordinates as the 3rd

        self.defLay = atts.get(8, self.defLay)
        handle = atts.get(5, "")
        col = atts.get(62, -1)
        if col <= 0: col = None               # Sometimes thAtCAD sets undefined color zero
        xx = [atts[10+i] for i in c]
        yy = [atts[20+i] for i in c]
        zz = [atts.get(30+i, ZDEFAULT) for i in c]
        self.thanDr.dxfSolid(xx, yy, zz, self.defLay, handle, col)

#===========================================================================

    def readuntilsecond10(self):
        "Reads codes until it finds code 10 for the second time."
        atts = {}
        icod10 = 0
        while True:
            icod, text = self.thanGetDxf()
            if icod == -1: return icod, atts  #End of file
            if icod == 0:   # other element  
                self.thanUngetDxf()    #Normal end of hatch points, or incomplete hatch
                return icod, atts
            if icod == 10:
                icod10 += 1
                if icod10 > 1:  #Second code 10: the general codes have finished
                    self.thanUngetDxf()
                    return icod, atts
            atts[icod] = text


    def __getHatch(self, name):
        """Reads a hatch from .dxf file.

        QGIS exports AC2018 version of dxf with hatches. The hatch has
        1. Initial 10,20,30 codes (x, y, z), coordinates which are zero and I suspect they are not used.
        2. After the initial 10,20,30 codes amd layer and some other codes, it haw many
           10,20 codes, presumambly for the coordiantes of the polygon.
        Thus:
        1. We read general attributes until the second 10 code.
        2. Then we read the points of the polygons.
        3. I set the z coordimnates of all polygon points to the initial z of the hatch.
        """

#-------try to find layer, closed

        icod, atts = self.readuntilsecond10()
        if icod == -1: return  #End of file
        if icod == 0: 
            self.thanWarn("Incomplete hatch: probably corrupted file.")
            return

        if self.trAtts(atts, str, -8) or self.trAtts(atts, int, -62, -70) or \
            self.trAttsFloat(atts, -30, -210, -220, -230):
            self.thanWarn("Incomplete hatch: probably corrupted file.")
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

        pa = PointAccumulator(self, zdef, elname="hatch", elpoint="point")
        while True:
            icod, atts = self.readuntilsecond10()
            if icod == 0: break    #Normal end of coordinates
            if icod == -1:         #End of file
                self.thanWarn("Incomplete hatch: probably corrupted file.")
                break
            pa.addPoint(atts)
        pa.makeClosed()
        if not pa.check(): return    #Hatch has less than 2 points

#-------Store the hatch

#        if extrusion: thanDxfExtrusion2World(wx, wy, wz, xx, yy, zz)
#        print "line:"
#        for i in range(len(xx)): print xx[i], yy[i]
        self.thanDr.dxfHatch(pa.xx, pa.yy, pa.zz, self.defLay, handle, col)

#===========================================================================


class PointAccumulator:
    "An object which accumulates points of polyline or hatch."

    def __init__(self, tidref, zdef, elname="polyline", elpoint="vertex"):
        "Initialize points."
        self.tidref = tidref  #Reference to the ThanImportDxf object
        self.zdef = zdef
        self.elname = elname
        self.elpoint = elpoint
        self.xx = []
        self.yy = []
        self.zz = []
        self.firstz = True

    def addPoint(self, atts):
        "Add new point the attributes of which are atts."
        if self.tidref.trAttsFloat(atts, 10, 20, -30):
            self.tidref.thanWarn("Damaged %s %s: probably corrupted file." % (self.elname, self.elpoint))
            return
        self.xx.append(atts[10])
        self.yy.append(atts[20])
        z1 = atts.get(30, None)
        if z1 is None:
            z1 = self.zdef
        else:
            if z1 == 0.0:
                z1 = self.zdef
            elif self.zdef != 0.0 and z1 != self.zdef and self.firstz:
                self.tidref.thanWarn("%s z=%f is not the same with global %s z=%f" % (self.elpoint, zdef, self.elname, z1))
                self.firstz = False
        self.zz.append(z1)

    def makeClosed(self, closed=True):
        "Close the polyline if closed == True."
        if not closed or len(self.xx) < 1: return
        if self.xx[0] != self.xx[-1] or self.yy[0] != self.yy[-1] or self.zz[0] != self.zz[-1]:
            self.xx.append(self.xx[0])
            self.yy.append(self.yy[0])
            self.zz.append(self.zz[0])

    def check(self):
        "Check if polyline has at least 2 points."
        if len(self.xx) < 2:
            self.thanWarn("%s with 1 or 0 %s." % (self.elname, self.elpoint))  
            return False

        if self.xx[0] == self.xx[-1] and self.yy[0] == self.yy[-1] and self.zz[0] == self.zz[-1] and len(self.xx) < 3:
            self.thanWarn("%s with 1 or 0 %s." % (self.elname, self.elpoint))  
            return False
        return True
