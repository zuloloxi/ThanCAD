import sys, os.path
try: from configparser import SafeConfigParser     #python3.9
except: from configparser import ConfigParser as SafeConfigParser  #python3.12
import tkinter


#############################################################################
#############################################################################

class ThanConfigParser(SafeConfigParser):
    def getintvar(self, sect, opt, intvar):
        try: i = self.getint(sect, opt)
        except: pass
        else: intvar.set(i)
    def setintvar(self, sect, opt, intvar):
        self.set(sect, opt, str(intvar.get()))


#############################################################################
#############################################################################

class ThanOptions:
    def __init__(self, config):
        self.zoomWhenConf     = tkinter.IntVar()
        self.regenWhenConf    = tkinter.IntVar()
        self.regenWhenZoom    = tkinter.IntVar()
        self.regenWhenZoomall = tkinter.IntVar()
        self.centerWhenZoom   = tkinter.IntVar()
        self.zoomFact         = 1.2
        self.showMenubar      = tkinter.IntVar()
        self.showToolbar      = tkinter.IntVar()
        self.thanOptFactory()

        if sys.platform == "win32":
            windir = os.path.expandvars("$windir")
            if windir != "$windir": f = os.path.join(windir, config+".ini")
            else:                   f = os.path.join(config+".ini")
        else:
            f = os.path.expanduser(os.path.join("~", "."+config))
        self.thanOptFilini = f
        self.thanOptGet()


    def thanOptFactory(self):
        "Factory set default values."
        self.zoomWhenConf.set(     True)
        self.regenWhenConf.set(    True)
        self.regenWhenZoom.set(    False)
        self.regenWhenZoomall.set( True)
        self.centerWhenZoom.set(   False)
        self.zoomFact =            1.2
        self.showMenubar.set(      False)
        self.showToolbar.set(      True)


    def thanOptGet(self):
        "Read options from configuration file."
        c = ThanConfigParser()
        c.read(self.thanOptFilini)
        c.getintvar("draw", "zoom when config",    self.zoomWhenConf)
        c.getintvar("draw", "regen when config",   self.regenWhenConf)
        c.getintvar("draw", "regen when zoom",     self.regenWhenZoom)
        c.getintvar("draw", "regen when zoom all", self.regenWhenZoomall)
        c.getintvar("draw", "center when zoom",    self.centerWhenZoom)
        c.getintvar("draw", "show menu bar",       self.showMenubar)
        c.getintvar("draw", "show tool bar",       self.showToolbar)
        try: self.zoomFact = c.getfloat("draw", "zoom factor")
        except: pass

    def thanOptSave(self):
        "Write options into configuration file."

        c = ThanConfigParser()
        c.read(self.thanOptFilini)
        if not c.has_section("draw"): c.add_section("draw")
        c.setintvar("draw", "zoom when config",    self.zoomWhenConf)
        c.setintvar("draw", "regen when config",   self.regenWhenConf)
        c.setintvar("draw", "regen when zoom",     self.regenWhenZoom)
        c.setintvar("draw", "regen when zoom all", self.regenWhenZoomall)
        c.setintvar("draw", "center when zoom",    self.centerWhenZoom)
        c.setintvar("draw", "show menu bar",       self.showMenubar)
        c.setintvar("draw", "show tool bar",       self.showToolbar)
        c.set("draw", "zoom factor",         str(self.zoomFact))

        try:
            f = open(self.thanOptFilini, "w")
            c.write(f)
        except IOError: pass


#############################################################################
#############################################################################

if __name__ == "__main__":
    root = tkinter.Tk()
    p = ThanOptions("q1")
    print(p.zoomFact)
    p.thanOptGet()
    print(p.zoomFact)
    p.thanOptSave()
