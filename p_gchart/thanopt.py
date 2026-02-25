import sys, os.path, ConfigParser, Tkinter


#############################################################################
#############################################################################

class ThanConfigParser(ConfigParser.SafeConfigParser):
    def getintvar(self, sect, opt, intvar):
        try: i = self.getint(sect, opt)
        except: pass
        else: intvar.set(i)


#############################################################################
#############################################################################

class ThanOptions:
    def __init__(self, config):
	self.zoomWhenConf     = Tkinter.IntVar()
	self.regenWhenConf    = Tkinter.IntVar()
	self.regenWhenZoom    = Tkinter.IntVar()
	self.regenWhenZoomall = Tkinter.IntVar()
	self.centerWhenZoom   = Tkinter.IntVar()
	self.zoomFact         = 1.2
	self.showMenubar      = Tkinter.IntVar()
	self.showToolbar      = Tkinter.IntVar()
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
	c.set("draw", "zoom when config",    self.zoomWhenConf.get())
	c.set("draw", "regen when config",   self.regenWhenConf.get())
	c.set("draw", "regen when zoom",     self.regenWhenZoom.get())
	c.set("draw", "regen when zoom all", self.regenWhenZoomall.get())
	c.set("draw", "center when zoom",    self.centerWhenZoom.get())
	c.set("draw", "show menu bar",       self.showMenubar.get())
	c.set("draw", "show tool bar",       self.showToolbar.get())
	c.set("draw", "zoom factor",         self.zoomFact)

        try:
            f = file(self.thanOptFilini, "w")
	    c.write(f)
	except IOError: pass


#############################################################################
#############################################################################

if __name__ == "__main__":
    root = Tkinter.Tk()
    p = ThanOptions("q1")
    print p.zoomFact
    p.thanOptGet()
    print p.zoomFact
    p.thanOptSave()
    