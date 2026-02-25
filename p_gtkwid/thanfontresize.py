import tkinter


class ThanFontResize:
    "This mixin for Tk() and Toplevel() adds capability of increasing and decreasing font sizes on the fly."

    def thanResizeFont(self, font=None):
        "Creates and sets font."
        if font is not None:
            if isinstance(font, tkinter.font.Font): font1 = font
            else:                             font1 = tkinter.font.Font(name=font)
        else:            font1 = tkinter.font.Font(name="TkFixedFont", exists=True, size=14)   # Negative size means size in pixels
        font2 = font1.copy()
        font2.config(weight=tkinter.font.BOLD)
        font3 = font2.copy()
        i = int(font3["size"])
        font3.config(size=i+2)           # Negative size means size in pixels
        self.thanFonts = [font1, font2, font3]
#        self.option_add("*font", self.thanFontcom)
        self.option_add("*%s*font" % (self.winfo_name(),), self.thanFonts[0])


    def thanResizeInc(self, evt=None):
        "Increase font size."
        for font1 in self.thanFonts:
            i = int(font1["size"])
            font1.config(size=i+2)
#        root.after(500, __setmet)
        return "break"


    def thanResizeDec(self, evt=None):
        "Decrease font size."
        for font1 in self.thanFonts:
            i = int(font1["size"])
            font1.config(size=i-2)
#        root.after(500, __setmet)
        return "break"


    def thanCreateTags(self, wids):
        "Create standard tags and fonts in the text widgets."
        font1, font2, font3 = self.thanFonts
        col = "#%2xd%2xd%2xd" % (66, 182, 33)
        for wid in wids:
            wid.config(font=font1)
            wid.tag_config("mes",   foreground="blue",      font=font2)
            wid.tag_config("com",   foreground="darkcyan",  font=font2)
            wid.tag_config("can",   foreground="darkred",   font=font2)
            wid.tag_config("can1",  foreground="darkred",   font=font1)
            wid.tag_config("info",  foreground="darkgreen", font=font2)
            wid.tag_config("info1", foreground="darkgreen", font=font1)
            wid.tag_config("thancad", foreground="white", background=col, font=font3)


    def thanResizeBind(self, wids=()):
        "Put the mechanism to increase/decrease font size with control+ and control-."
        self.bind_all("<Control-plus>",        self.thanResizeInc)
        self.bind_all("<Control-KP_Add>",      self.thanResizeInc)
        self.bind_all("<Control-minus>",       self.thanResizeDec)
        self.bind_all("<Control-KP_Subtract>", self.thanResizeDec)
        for wid in wids:
            try:    wid.bindte
            except: b = wid.bind
            else:   b = wid.bindte
            b("<Control-plus>",        self.thanResizeInc)
            b("<Control-KP_Add>",      self.thanResizeInc)
            b("<Control-minus>",       self.thanResizeDec)
            b("<Control-KP_Subtract>", self.thanResizeDec)
#        prt("Πατείστε Control+ για αύξηση μεγέθους γραμματοσειράς")
#        prt("Πατείστε Control- για μείωση μεγέθους γραμματοσειράς")


    def thanDestroy(self):
        "Break circular references."
        del self.thanFonts
