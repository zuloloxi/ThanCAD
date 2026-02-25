import re, tkinter
import p_gnum, p_gtkwid
from .gdal_bands import readWv2mBands, readWv2pBand

#dline="     16393: (  310,  310,  310) #013601360136 rgb(0.47303%,0.47303%,0.47303%)"

ecols = re.compile(r"[ ]*(\d*): \([ ]*(\d*),[ ]*(\d*),[ ]*(\d*)")


class Hist(object):
    "A colour histogram."

    def __init__(self, plotcol="black"):
        "Make an empty frequency table."
        self.freq = {}
        self.plotcol = plotcol

    def add(self, fn):
        "Add the colour frequencies of file fn."
        fr = open(fn)
        self.freq = dict.fromkeys(range(4096), 0)
        for dline in fr:
            if dline.strip() == "": continue
            m = ecols.match(dline)
            assert m != None, dline
            n = int(m.group(1))
            col = int(m.group(2))
            self.freq.setdefault(col, 0)
            self.freq[col] += n
        fr.close()

    def fromArray(self, band):
        "Compute and add the colour frequencies of numarray band."
        h, _ = p_gnum.histogram(band, 4096, (0, 4096))
        self.freq = dict(zip(range(4096), h))
        self.freq[0] = 0  #############################delete this

    def statistics(self):
        "Find min, max etc."
        self.cols = list(self.freq.keys())    #OK for python 2, 3
        self.cols.sort()
        self.colmin = self.cols[0]
        self.colmax = self.cols[-1]
        self.fmax = max(self.freq.values())   #OK for python 2, 3
        #print("statistics: colimn, colmax, fmax=", self.colmin, self.colmax, self.fmax)

    def approx(self):
        "Find an initial approximation of position and size, inspecting histograms."
        x1 = 4095
        x2 = 0
        per = 0.01  #Percentage of max frequency importance threshold
        h1 = self
        if 1:
            fmax = per*h1.fmax
            #print("fmax=",fmax)
            for i in range(len(h1.cols)):
                if h1.freq[i] < fmax: continue
                if i < x1: x1 = i
                break
            #print("x1, col(x1)=", x1, h1.cols[x1])
            #print("col[4095]=", h1.cols[4095])
            for i in range(len(h1.cols)-1, 0, -1):
                if h1.freq[i] < fmax: continue
                if i > x2: x2 = i
                break
            #print("x2, col(x2)=", x2, h1.cols[x2])
        return x1, x2


    def plot(self, than):
        "plot the histogram to a canvas."
        xy = []
        for col in self.cols:
            if col > than.colmax: break
            x = (col-than.colmin)*than.aklx
            y = self.freq[col]*than.akly
            xy.append((than.dcperx+x, than.dch-(than.dcpery+y)))
        col = self.plotcol
        if col == "gray": col = "black"
        than.dc.create_line(xy, fill=col)


class HistWin(p_gtkwid.ThanDialog, p_gtkwid.ThanFontResize):
    "A window to visually access histograms."
    def __init__(self, parent, title=None, buttonlabels=2, his=(), **kw): # Stamos Jan 7, 2011
        self.his = his                   #A dict of colourname/histograms pairs to display
        p_gtkwid.ThanDialog. __init__(self, parent, title, buttonlabels, **kw)

    def body(self, fra):
        "Build the window."
        self.thanResizeFont()
        self.thanResizeBind()
        self.fsize = 10*1.3              #Font size
        self.dcw = 600                   #Canvas x size
        self.dch = 400                   #Canvas y size
        self.dcperx = self.dcpery = 15   #Canvas x and y margins
        self.colmin = 0                  #Canvas mix x value to show
        self.colmax = 4096               #Canvas max x value to show
        self.fmax   = 0                  #Canvas max y value to show (canvas min y value is always 0)
        self.aklx = self.akly = 1.0      #Scale of x and y axis
        self.makeWidgets(fra)
        self.findLimits()                #Find x-min,max y-max values
        self.redrawHist()                #Compute x,y-scales and draw histograms
        self.rect = DragRectangle()      #Create a draggable rectangle
        self.rect.approx(self.his)
        self.rect.plot(self)             #Draw the rectangle
        self.bind("<B1-Motion>", lambda evt: self.rect.ondrag(self, evt))
#        self.bind("<Shift-B1-Motion>", lambda evt: self.rect.onresize(self, evt))
        self.bind("<KP_Add>",      lambda evt: self.rect.onresize(self, evt, 1))
        self.bind("<KP_Subtract>", lambda evt: self.rect.onresize(self, evt, -1))

        self.iaftersize = 0              #Pending event id (it is delayed call resize)
        self.bind("<Configure>", self.onSize) # Bind in the end, in order to avoid preemptive calls
        return self.dc


    def onSize(self, evt):
        "Just defer the call."
        self.after_cancel(self.iaftersize)
        self.iaftersize = self.after(500, self.onSizeDo)


    def onSizeDo(self):
        "Readraw the canvas."
        self.dc.update()
        w = self.dc.winfo_width()        # Pixels
        h = self.dc.winfo_height()       # Pixels
        if w < 2 or h < 2: return        #Tkinter reported wrong window dimension: do nothing
        self.dcw = w                     #Canvas x size
        self.dch = h                     #Canvas y size
        self.redrawHist()
        self.rect.plot(self)             #Draw the rectangle


    def makeWidgets(self, fra):
        "Create the diagram."
        self.title("Colour/gray histograms - Select colour range dragging the rectangle")
        lab = tkinter.Label(fra, text="Colour window:")
        lab.grid(row=0, column=0, sticky="w")
        self.labwin = tkinter.Label(fra, text="")
        self.labwin.grid(row=0, column=1, sticky="w")
        frb = tkinter.Frame(fra)
        frb.grid(row=0, column=2, sticky="we")

        but = p_gtkwid.ThanButton(fra, text="Auto", command=self.auto)
        but.grid(row=0, column=3, sticky="e")
        self.butMax = p_gtkwid.ThanButton(fra, text="Max colour:%d" % (self.colmax), command=self.setMaxcolor)
        self.butMax.grid(row=0, column=4, sticky="e")
        self.dc = tkinter.Canvas(fra, width=self.dcw, height=self.dch, bg="pink")
        self.dc.grid(row=1, column=0, columnspan=6, sticky="wesn")
        fra.columnconfigure(2, weight=1)
        fra.rowconfigure(1, weight=1)


    def setMaxcolor(self):
        "Change the scale of x axis, by altering the maximum x-value."
        m = p_gtkwid.xinpLongR(self, "Maximum x-axis value (colour):", 10, 4096, self.colmax)
        if m is None: return
        self.colmax = m
        self.butMax.config(text="Max colour:%d" % (self.colmax))
        self.redrawHist()
        self.rect.plot(self)


    def findLimits(self):
        "Find limits of the diagram in order to compute scales."
        self.colmin = min(h1.colmin for h1 in self.his)
        self.colmax = max(h1.colmax for h1 in self.his)
        self.fmax   = max(h1.fmax   for h1 in self.his)
        #Find maximum colour with nonzero frequency, in order to make bigger scale
        im = None
        for h in self.his:
            fmax = h.fmax*0.001
            for i in range(len(h.freq)-1, 300, -1):   #No less than 300 in order to have room for the drag window
                if h.freq[i] > fmax: break
            if im is None: im = i
            if i > im: im = i
        self.colmax = im + 20
        self.butMax.config(text="Max colour:%d" % (self.colmax))


    def auto(self):
        "Auto arrange the scale of the x-axis and position and size of the rectangle."
        self.findLimits()
        self.redrawHist()
        self.rect.approx(self.his)
        self.rect.plot(self)             #Draw the rectangle


    def redrawHist(self):
        "Redraw histograms after a scale change."
        self.dc.delete(tkinter.ALL)
        self.aklx = float(self.dcw-2*self.dcperx)/(self.colmax-self.colmin+1)
        self.akly = float(self.dch-2*self.dcpery)/self.fmax
        for h1 in self.his:
            h1.plot(self)
        self.dc.create_text(self.dcperx, self.dch-self.fsize, text=str(self.colmin),
            anchor="nw", font=self.thanFonts[0], fill="blue")
        self.dc.create_text(self.dcw-self.dcperx-3*self.fsize, self.dch-self.fsize, text=str(self.colmax),
            anchor="nw", font=self.thanFonts[0], fill="blue")


    def destroy(self):
        "Delete circular references."
        self.rect.destroy()
        p_gtkwid.ThanFontResize.thanDestroy(self)
        del self.butMax, self.dc, self.labwin
        p_gtkwid.ThanDialog.destroy(self)


    def apply(self):
        "When the window closes, put the range into self.result."
        self.result = self.rect.getColRange(self)


class DragRectangle(object):
    "An rectangle which saves dragging info and does some action."

    def __init__(self):
        "Initial values."
        self.clearDrag()       #This set xp=yp=None attributes
        self.x1 = None         #The colour value (x-axis) of the left side rectangle
        self.sizex = 255       #x size of the rectangle
        self.iafter = 0        #Pending event id (it is delayed call clearDrag())
        self.itwin = 0         #The canvas id of the rectangle

    def destroy(self):
        "Delete circular references."
        pass


    def approxold(self, his):
        "Find an initial approximation of position and size, inspecting histograms."
        x1 = 4095
        x2 = 0
        per = 0.01  #Percentage of max frequency importance threshold
        for h1 in his:
            fmax = per*h1.fmax
            print("fmax=",fmax)
            for i in range(len(h1.cols)):
                if h1.freq[i] < fmax: continue
                if i < x1: x1 = i
                break
            print("x1, col(x1)=", x1, h1.cols[x1])
            print("col[4095]=", h1.cols[4095])
            for i in range(len(h1.cols)-1, 0, -1):
                if h1.freq[i] < fmax: continue
                if i > x2: x2 = i
                break
            print("x2, col(x2)=", x2, h1.cols[x2])
        self.x1 = x1
        self.sizex = x2-x1


    def approx(self, his):
        "Find an initial approximation of position and size, inspecting histograms."
        x1 = 1000000000
        x2 = 0
        for h1 in his:
            x3, x4 = h1.approx()
            x1 = min(x1, x3)
            x2 = max(x2, x4)
        self.x1 = x1
        self.sizex = x2-x1


    def plot(self, than):
        "Create a window of sizex length."
        if self.x1 is None:                    #First time the rectangle is drawn
            x1 = than.dcw/2                    #Canvas x center in canvas coordinates
            self.x1 = (x1-than.dcperx)/than.aklx + than.colmin  #Colour at center of the canvas
            self.x1 = int(self.x1 - self.sizex*0.5 + 0.5)       #The colour of the left side of the rectangle
        dx = self.sizex*than.aklx
#        dy = than.dch-2*than.dcpery
        dy = than.dch
        x1 = (self.x1 - than.colmin)*than.aklx + than.dcperx
        y1 = than.dch/2-dy/2                     #Set rectangle at the y center of the canvas
        self.itwin = than.dc.create_rectangle(x1, y1, x1+dx, y1+dy, outline="cyan", fill="lightcyan", stipple="gray25")
        self.x1, x2 = self.getColRange(than)
        than.labwin.config(text="%s %s (%s)" % (self.x1, x2, self.sizex))

    def ondrag(self, than, evt):
        "Move the rectangle on dragging."
        if self.xp is not None:           #Wait a little after a drag
            than.after_cancel(self.iafter)     #Cancel previous cancel operation
            dx = evt.x - self.xp
            dy = evt.y - self.yp
            than.dc.move(self.itwin, dx, 0)
            self.x1, x2 = self.getColRange(than)
            than.labwin.config(text="%s %s (%s)" % (self.x1, x2, self.sizex))
        self.xp = evt.x
        self.yp = evt.y
        self.iafter = than.after(500, self.clearDrag)  #If the mouse does not drag again in 0.5 sec, cancel the drag

    def onresize(self, than, evt, dsize):
        "Resize the rectangle on gray-plus and gray-minus."
        if self.xp is not None: return     #Wait a little after a drag
        self.sizex += dsize
        x1, y1, x2, y2 = than.dc.coords(self.itwin)
        x2 = x1 + self.sizex*than.aklx
        than.dc.coords(self.itwin, x1, y1, x2, y2)
        self.x1, x2 = self.getColRange(than)
        than.labwin.config(text="%s %s (%s)" % (self.x1, x2, self.sizex))

    def getColRange(self, than):
        "Get the current window colour range (x range of the rectange)."
        x1, _, x2, _ = than.dc.coords(self.itwin)
        x1 = int((x1-than.dcperx)/than.aklx + than.colmin + 0.5)
        x2 = int((x2-than.dcperx)/than.aklx + than.colmin + 0.5)
        return x1, x2

    def clearDrag(self):
        "Clear the previous mouse coordinates."
        self.xp = self.yp = None


def selectColourRange(band, root):
    "Let the user select the colour range of an (16bit) image."
    n = len(band)
    if n == 1: pcols = ["gray"]
    else:      pcols = ["red", "green", "blue"]
    his = []
    for i, ar in enumerate(band):
        h1 = Hist(pcols[i%n])
        h1.fromArray(ar)
        h1.statistics()
        his.append(h1)
    w = HistWin(root, his=his)
#    w.wait_window(w)
    return w.result


def selectColourRange1(fns, root):
    "Let the user select the colour range of given histograms saved in files."
    n = len(fns)
    if n == 1: pcols = ["gray"]
    else:      pcols = ["red", "green", "blue"]
    his = []
    for i, fn in enumerate(fns):
        h1 = Hist(pcols[i%n])
        h1.add(fn)
        h1.statistics()
        his.append(h1)
    w = HistWin(root, his=his)
#    w.wait_window(w)
    return w.result
