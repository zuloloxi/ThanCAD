#!/usr/bin/python
from __future__ import generators
from Tkinter import *


##############################################################################
##############################################################################

class ThanGrid(Frame):
    "A grid with entry Widgets."
    
    def __init__(self, master, rows=2, columns=2, rowheight=1, columnwidth=10, **kw):
        Frame.__init__(self, master, **kw)
	self.thanColumns = xrange(columns)
	self.thanRows = xrange(rows)
	cc = []
	for iy in self.thanRows:
	    c = []
	    for jx in self.thanColumns:
	        e = Entry(self, width=columnwidth)
		e.grid(row=iy, column=jx, sticky="wesn")
		c.append(e)
	    cc.append(tuple(c))
	self.thanCell = tuple(cc)
	
	for iy in self.thanRows: self.rowconfigure(iy, weight=1)
	for jx in self.thanColumns: self.columnconfigure(jx, weight=1)
	
    def thanSetm(self, t, iy=None, jx=None):
        if iy == None: rows = self.thanRows
	else: rows = (iy,)
        if jx == None: cols = self.thanColumns
	else: cols = (jx,)
	t = str(t)
        for iy in rows:
            for jx in cols:
                c = self.thanCell[iy][jx]
                c.delete(0, END)
	        c.insert(0, t)
	        
    def thanSet(self, y, iy, jx, t):
        c = self.thanCell[iy][jx]
        c.delete(0, END)
	c.insert(0, str(t))
    
    def thanGet(self, iy, jx): return self.thanCell[iy][jx].get()
    thanValidate = thanGet

    def thanGetm(self, iy=None, jx=None):
        if iy != None:
	    if ix != None: return self.thanCell[iy][jx].get()
	    else: return [thanCell[iy][jx].get() for ix in self.thanRows]
	elif ix != None:
	    return [thanCell[iy][jx].get() for iy in self.thanCols]
	else:
	    v = []
	    for ix in self.thanRows: v.append([thanCell[iy][jx].get() for iy in self.thanCols])
	    return v

    def cellconfig(self, iy=None, jx=None, **kw):
        if iy == None: rows = self.thanRows
	else: rows = (iy,)
        if jx == None: cols = self.thanColumns
	else: cols = (jx,)
        for iy in rows:
            for jx in cols:
                c = self.thanCell[iy][jx].config(kw)

    def scrolly(self, iy=0, ny=1):
        c = self.thanCell; n = len(self.thanRows)-1
        for iy in xrange(iy, n):
	    iy1 = iy + 1
	    for jx in self.thanColumns:
	        c1 = c[iy][jx]
		c1.delete(0, END)
	        c1.insert(0, c[iy1][jx].get())
        for jx in self.thanColumns:
            c[n][jx].delete(0, END)
    


##############################################################################
##############################################################################

def rdict(kw, *allowed):
    kw1 = {}
    for key in allowed:
        try: kw1[key] = kw[key]
        except KeyError: pass
    return kw1

def enumerate(seq):
    for i in xrange(len(seq)): yield i, seq[i]

##############################################################################
##############################################################################

if __name__ == "__main__":
    root = Tk()
    mb = ThanGrid(root, rows=10, columns=8)
    mb.grid()
    mb.thanSetm(10)
    mb.thanSetm(20, iy=2)
    mb.thanSetm(40, jx=4)
    mb.thanSetm(24, iy=2, jx=4)
    mb.thanSetm(42, iy=4, jx=2)

    mb.cellconfig(bg="lightyellow")
    mb.cellconfig(iy=2, fg="red")
    mb.cellconfig(jx=4, relief=RAISED)
    mb.cellconfig(iy=2, jx=4, bg="green")
    mb.cellconfig(jx=2, width=5, font="courier")
    
    b = Button(root, text="scroll +y1", command=mb.scrolly)
    b.grid()
    
    root.mainloop()
