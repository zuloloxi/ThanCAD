from itertools import islice
from math import fabs
from dxfinter import *
#from Tkinter import *

class Struct: pass

def replot(evt=None):
    "Replot the diagrams each time the user changes window dimensions."
    c.update()
    b = c.winfo_width()
    h = c.winfo_height()
    c.delete(ALL)

    axis = (g.xmin, 0), (g.xmax,0)

    scalex = b/g.sx; dy = h*0.5; scaleQ = dy/g.sQ
    xy = [ ( (x-g.xmin)*scalex, h-((y-g.Qmin)*scaleQ+dy) ) for (x,y) in g.Q]
    c.create_line(xy, fill= "orange")
    for x,y in islice(g.Q, 0, None, 20):
        xy = [ ( (x-g.xmin)*scalex, h-((y-g.Qmin)*scaleQ+dy) ) for (x,y) in ((x,0),(x,y))]
        c.create_line(xy, fill= "orange")
    xy = [ ( (x-g.xmin)*scalex, h-((y-g.Qmin)*scaleQ+dy) ) for (x,y) in axis]
    c.create_line(xy, fill= "yellow")

    scaleM = dy/g.sM
    xy = [ ( (x-g.xmin)*scalex, h-((-y-g.Mmin)*scaleM+0) ) for (x,y) in g.M]
    c.create_line(xy, fill= "orange")
    for x,y in islice(g.M, 0, None, 20):
        xy = [ ( (x-g.xmin)*scalex, h-((-y-g.Mmin)*scaleM+0) ) for (x,y) in ((x,0),(x,y))]
        c.create_line(xy, fill= "orange")
    xy = [ ( (x-g.xmin)*scalex, h-((-y-g.Mmin)*scaleM+0) ) for (x,y) in axis]
    c.create_line(xy, fill= "yellow")

#---Draw min, max Q values

    for i in xrange(1, len(g.Q)-1):
        Q1, Q2, Q3 = [Q[1] for Q in g.Q[i-1:i+2]]
        if DQ(Q2-Q1) * DQ(Q3-Q2) > 0.0: continue
        if DQ(Q2-Q1) == 0.0 == DQ(Q3-Q2): continue
        x, y = g.Q[i]
        x, y = (x-g.xmin)*scalex, h-((y-g.Qmin)*scaleQ+dy)
        print "Qmax=", Q2
        if Q2 > 0: dyp = -10
        else     : dyp =  10
        c.create_text(x, y+dyp, fill="pink", text="%.2f" % Q2)
        c.create_rectangle(x-1, y-1, x+1, y+1, fill="pink", outline="pink")

#---Draw min, max M values

    xprev = -1000.0
    for i in xrange(1, len(g.Q)-1):
        Q1, Q2, Q3 = [Q[1] for Q in g.M[i-1:i+2]]
        if DM(Q2-Q1) * DM(Q3-Q2) > 0.0: continue
        if DM(Q2-Q1) == 0.0 == DM(Q3-Q2): continue
        x, y = g.M[i]
        x, y = (x-g.xmin)*scalex, h-((-y-g.Mmin)*scaleM+0)
        if x-xprev < 10: continue
        xprev = x
        print "Mmax=", Q2
        if -Q2 > 0: dyp = -10
        else      : dyp =  10
        c.create_text(x, y+dyp, fill="pink", text="%.2f" % Q2)
        c.create_rectangle(x-1, y-1, x+1, y+1, fill="pink", outline="pink")

        x1 = x = g.M[i][0]; y = 0.0
        x, y = (x-g.xmin)*scalex, h-((-y-g.Mmin)*scaleM+0)
#        if x-xprev < 10: continue
#        xprev = x
        c.create_text(x, y-dyp, fill="green", text="%.2f" % x1)
        c.create_rectangle(x-1, y-1, x+1, y+1, fill="pink", outline="green")

def DQ(dq):
    if fabs(dq) < g.Qmax*1e-6: return 0.0
    return dq
def DM(dq):
    if fabs(dq) < g.Mmax*1e-6: return 0.0
    return dq


def diag(Q, M, tit):
    "Initialise diagram."
    global c, g
    g = Struct()
    xmin = Q[0][0]; xmax = Q[-1][0]
    Qmax = max([fabs(y) for (x,y) in Q]); Qmin = -Qmax
    Mmax = max([fabs(y) for (x,y) in M]); Mmin = -Mmax
    g.sx, g.xmin, g.xmax = margins(xmin, xmax)
    g.sQ, g.Qmin, g.Qmax = margins(Qmin, Qmax)
    g.sM, g.Mmin, g.Mmax = margins(Mmin, Mmax)
    g.Q, g.M = Q, M

    root = Tk()
    c = Canvas(root, background= "black", width=400, height=600)
    c.grid(sticky="wesn")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    replot()
    c.bind("<Configure>", replot)
    root.title(tit)
    root.mainloop()

def margins(xmin, xmax):
    "Extend xmin, xmax so that we have some margins."
    dx = (xmax - xmin)*0.2
    if dx == 0.0: dx = 1.0
    return xmax-xmin+dx, xmin-dx*0.5, xmax+dx*0.5
