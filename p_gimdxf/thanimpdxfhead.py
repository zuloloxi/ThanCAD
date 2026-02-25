class ThanHeader:
    "Mixin to import the header section of a dxf file."

    def thanGetHeader(self):
        "Imports dxf header."
#-------At first  read all the variables
        vars = { }
        while 1:
#-----------Find if variable follows
            icod, text = self.thanGetDxf()
            if icod == -1:                    # Abnormal end of header, and end of file
                self.thanWarn("Incomplete header: end of file.")
                break
            if icod == 0:
                if text == "ENDSEC": break    # Normal end of section HEADER
                if text == "SECTION":         # Abnormal end of section HEADER
                    self.thanUngetDxf()
                    self.thanWarn("Incomplete header: probably corrupted file.")
                    break
            if icod != 9: continue            # Unknown code: ignore it

#-----------Read variable's attributes

            var = text
            atts = {}
            while 1:
                icod, text = self.thanGetDxf()
                if icod == -1:                # End of file
                    self.thanWarn("Incomplete variable: end of file.")
                    break
                if icod == 0: self.thanUngetDxf(); break   # SEQEND, SECTION or unknown ent
                if icod == 9: self.thanUngetDxf(); break   # Normal end for variable
                atts[icod] = text
            vars[var] = atts

#-------Get min, max from the variables

        v = {}
        if "$EXTMIN" in vars and "$EXTMAX" in vars:
            att1 = vars["$EXTMIN"]
            att2 = vars["$EXTMAX"]
            if not self.trAttsFloat(att1, 10, 20):
                v["EXTMIN"] = att1[10], att1[20]
                if not self.trAttsFloat(att2, 10, 20):
                    v["EXTMAX"] = att2[10], att2[20]
                    self.thanDr.dxfXymm(att1[10], att1[20], att2[10], att2[20])

        if "$LTSCALE" in vars:
            att1 = vars["$EXTMIN"]
            if not self.trAttsFloat(att1, 40):
                v["LTSCALE"] = att1[40]
        if "$FILLMODE" in vars:
            att1 = vars["$FILLMODE"]
            if not self.trAtts(att1, int, 70):
                v["LTSCALE"] = att1[70]


        self.thanDr.dxfVars(v)
