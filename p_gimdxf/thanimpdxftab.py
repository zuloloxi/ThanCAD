from math import fabs
from . import thandxfext


class ThanTables:
    "Mixin to import the tables section of a dxf file."

#===========================================================================

    def thanGetTables(self):
        "Imports the actual entities."
        tables = { "VPORT" : self.__getVports,
                   "LAYER" : self.__getLayers,
                   "LTYPE" : self.__getLtypes
                 }
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1: break                 # End of file
            if icod != 0: continue               # Unknown code
            if text == "ENDSEC": break           # Normal end of section 'TABLE'
            if text == "SECTION":                # Abnormal end of section 'TABLE'
                self.__ungetDxf()
                self.thanWarn("Incomplete section TABLES: probably corrupted file.")
                break
            if text != "TABLE": continue         # Unknown text
            icod, text = self.thanGetDxf()
            if icod != 2:                        # If end of file (-1), it will be reported again in the next read
                self.thanWarn("A TABLE definition was expected: probably corrupted file.")
                continue
            if text not in tables: continue      # Unknown table
            tables[text]()                       # Process table

#===========================================================================

    def __getVports(self):
        "Reads the active Viewport from .dxf file."
#-------try to find vport
        activefound = 0
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1: return
            if icod != 0: continue
            if text == "ENDTAB": return
            if text == "ENDSEC" or text == "SECTION":
                self.__ungetDxf()
                self.thanWarn("Incomplete section TABLES: probably corrupted file.")
                return 0
            if text != "VPORT": continue

#-----------Vport found: read attributes

            atts = { }
            while 1:
                icod, text = self.thanGetDxf()
                if icod == -1:                # End of file
                    self.thanWarn("Incomplete layer: end of file.")
                    return
                if icod == 0: self.thanUngetDxf(); break           # other layer
                atts[icod] = text

            if self.trAtts(atts, str, 2) or self.trAttsFloat(atts, 12, 22, 40):
                self.thanWarn("Damaged viewport: probably corrupted file.")
            else:
                name = atts[2]
                if name == "*ACTIVE":
                    if activefound: self.thanWarn("More than 1 active viewports: the last one is kept.")
                    activefound = 1
                else:
                    if activefound: continue
                xc = atts[12]
                yc = atts[22]
                dx = atts[40]
                dy = dx*0.01
                self.thanDr.dxfVport(name, xc-dx, yc-dy, xc+dx, xc+dy)

#===========================================================================

    def __getLayers(self, thancad=False):
        "Reads a layer from .dxf file."
#-------try to find layer
        while 1:
            icod, text = self.thanGetDxf()
            if icod == -1: return              # End of file
            if icod != 0: continue
            if text == "ENDTAB": return
            if text == "ENDSEC" or text == "SECTION":
                self.__ungetDxf()
                self.thanWarn("Incomplete section TABLES: probably corrupted file.")
                return
            if text != "LAYER": continue

#-----------Layer found: read attributes

            atts = {}
            while 1:
                icod, text = self.thanGetDxf()
                if icod == -1:                # End of file
                    self.thanWarn("Incomplete layer: end of file.")
                    return
                if icod == 0: self.thanUngetDxf(); break           # other layer
                atts[icod] = text

            if self.trAtts(atts, str, 2):
                self.thanWarn("Damaged layer: probably corrupted file.")
                return
            name = atts[2]
            natts = {}
            if thancad:
                for code,att,func in thandxfext.thanCadAtts:
                    if func == float: res = self.trAttsFloat(atts, -code)
                    else:             res = self.trAtts(atts, func, -code)
                    if res:
                        self.thanWarn("Damaged layer: probably corrupted file.")
                        return
                    try: natts[att] = atts[code]
                    except KeyError: pass
            else:
                if self.trAtts(atts, str, -6) or self.trAtts(atts, int, -62, -70, -290, -370):
                    self.thanWarn("Damaged layer: probably corrupted file.")
                    return
                col = atts.get(62, 7)                        # default is 7 (white)
                if col == 0: col = 7                         # Sometimes thAtCAD sets undefined color zero :(
                if col < 0: natts["color"] = -col; natts["off"] = True
                else:       natts["color"] =  col; natts["off"] = False
                natts["linetype"] = atts.get(6, "continuous")
                flags = atts.get(70, 0)
                natts["frozen"] = bool(flags & 1)
                natts["locked"] = bool(flags & 4)
#                 natts["noplot"] = "noplot" in atts              # For dxf 12?
                natts["noplot"] = atts.get(290, 1) == 0         # If code 290 is zero then do not plot the layer
                w = atts.get(370, -3)                           # -3 means default value
                if w == -3: w = 30                              # hundredths of mm
                natts["lineweight"] = w / 100.0                 # mm
            self.thanDr.dxfLayer(name, natts)

#===========================================================================

    def __getLtypes(self):
        "Reads a polyline from .dxf file."
        ltypes1 = {"continuous", "bylayer", "byblock"}  #bylayer, byblock are not real linetypes, just sentinels..
                                                        #..and continuous is automatically inside ThanCad
#-------try to find ltype

        while True:
            icod, text = self.thanGetDxf()
            if icod == -1: return          #End of file
            if icod != 0: continue         #Dxf entries between TABLE LTYPE and the first line type definition are ignored
            if text == "ENDTAB": return    #End of limetype definitions
            if text == "ENDSEC" or text == "SECTION":    #Something wrong
                self.__ungetDxf()
                self.thanWarn("Incomplete section TABLES: probably corrupted file.")
                return
            if text != "LTYPE": continue    #Dxf entries between TABLE LTYPE and the first line type definition are ignored..
                                            #..or between linetype definitions
#-----------Layer found: read attributes

            atts = {}
            elems = []
            while True:
                icod, text = self.thanGetDxf()
                if icod == -1:                # End of file
                    self.thanWarn("Incomplete ltype: end of file.")
                    return
                elif icod == 0:               # other ltype
                    self.thanUngetDxf()
                    break
                elif icod == 49:
                    elems.append(text)
                else:
                    atts[icod] = text

#-----------Check attributes

            try:               elems = [ float(e) for e in elems ]
            except ValueError: ierr = 1
            else:              ierr = 0
            if ierr or self.trAtts(atts, str, 2, -3) or self.trAtts(atts, int, -73) or \
                       self.trAttsFloat(atts, -40):
                self.thanWarn("Damaged linetype: probably corrupted file.")
                continue

            name = atts[2].strip().lower()
            #dltype = reduce(lambda x, y: x+fabs(y), elems, 0.0)
            dltype = sum(fabs(y) for y in elems)
            if (dltype <= 0.0 or len(elems) == 0) and name not in ltypes1:
                self.thanWarn('Linetype "'+name+'" contains no segments: probably corrupted file.')
                continue

#-----------Create the linetype and store it

            desc = atts.get(3, "")
            n = atts.get(73, len(elems))
            if n != len(elems):
                self.thanWarn('Linetype "'+name+'": Computed number of elements of ltype differs from dxf file.')
            if atts.get(40, dltype) != dltype:
                self.thanWarn('Linetype "'+name+'": Computed length of ltype differs from dxf file.')
            self.thanDr.dxfLtype(name, desc, elems)
