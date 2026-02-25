from itertools import islice
from math import fabs
import Tkinter, dxfinter, pilinter
_gc = Tkinter
_root = None

class Struct: pass

def replot(evt, c, g):
    "Replot the diagrams each time the user changes window dimensions."
    c.update()
    b = c.winfo_width()
    h = c.winfo_height()
    c.delete(_gc.ALL)

    axis = (g.xmin, 0), (g.xmax,0)

    scalex = b/g.sx
    if g.N == None: dy = h*0.5
    else:           dy = h/3.0
    ydi = h

    scaleQ = dy/g.sQ
    ydi -= dy
    plot1(c, g.Q, g.xmin, scalex, g.Qmin, scaleQ, h, ydi, axis, 1)
    minmax1(c, g.Q, g.xmin, scalex, g.Qmin, g.Qmax, scaleQ, h, ydi, 1)

    scaleM = dy/g.sM
    ydi -= dy
    plot1(c, g.M, g.xmin, scalex, g.Mmin, scaleM, h, ydi, axis, -1)
    minmax1(c, g.M, g.xmin, scalex, g.Mmin, g.Mmax, scaleM, h, ydi, -1)

    if g.N != None:
        scaleN = dy/g.sN
        ydi -= dy
        plot1(c, g.N, g.xmin, scalex, g.Nmin, scaleN, h, ydi, axis, 1)
        minmax1(c, g.N, g.xmin, scalex, g.Nmin, g.Nmax, scaleN, h, ydi, 1)


def minmax1(c, Q, xmin, scalex, Qmin, Qmax, scaleQ, h, dy, pr):
    "Draw min, max [NQM] values."
    def DQ(dq):
        "If dq is close to zero return zero."
        if fabs(dq) < Qmax*1e-6: return 0.0
        return dq
    xprev = -1000.0
    for i in xrange(1, len(Q)-1):
        Q1, Q2, Q3 = [Qx[1] for Qx in Q[i-1:i+2]]
        if DQ(Q2-Q1) * DQ(Q3-Q2) > 0.0: continue
        if DQ(Q2-Q1) == 0.0 == DQ(Q3-Q2): continue
        x, y = Q[i]
        x, y = (x-xmin)*scalex, h-((pr*y-Qmin)*scaleQ+dy)
        if x-xprev < 10: continue
        xprev = x
        print "[QMN]max=", Q2
        if pr*Q2 > 0: dyp = -10
        else        : dyp =  10
        c.create_text(x, y+dyp, fill="pink", text="%.2f" % Q2)
        c.create_rectangle(x-1, y-1, x+1, y+1, fill="pink", outline="pink")

        x1 = x = Q[i][0]; y = 0.0
        x, y = (x-xmin)*scalex, h-((pr*y-Qmin)*scaleQ+dy)
#        if x-xprev < 10: continue
#        xprev = x
        c.create_text(x, y-dyp, fill="green", text="%.2f" % x1)
        c.create_rectangle(x-1, y-1, x+1, y+1, fill="pink", outline="green")


def plot1(c, Q, xmin, scalex, Qmin, scaleQ, h, dy, axis, pr):
    "Plot a diagram (N or Q or M)."
    xy = [ ( (x-xmin)*scalex, h-((pr*y-Qmin)*scaleQ+dy) ) for (x,y) in Q]
    c.create_line(xy, fill= "orange")
    for x,y in islice(Q, 0, None, 20):
        xy = [ ( (x-xmin)*scalex, h-((pr*y-Qmin)*scaleQ+dy) ) for (x,y) in ((x,0),(x,y))]
        c.create_line(xy, fill= "orange")
    xy = [ ( (x-xmin)*scalex, h-((pr*y-Qmin)*scaleQ+dy) ) for (x,y) in axis]
    c.create_line(xy, fill= "yellow")


def diag(Q, M, N, tit, gc="tk+", width=400, height=600, textsize=7, texttheta=0.0):
    "Initialise diagram."
    global _gc, _root
    if   gc == "dxf": _gc = dxfinter
    elif gc == "pil": _gc = pilinter
    else:             _gc = Tkinter
    g = Struct()
    xmin = Q[0][0]; xmax = Q[-1][0]
    Qmax = max([fabs(y) for (x,y) in Q]); Qmin = -Qmax
    Mmax = max([fabs(y) for (x,y) in M]); Mmin = -Mmax
    g.sx, g.xmin, g.xmax = margins(xmin, xmax)
    g.sQ, g.Qmin, g.Qmax = margins(Qmin, Qmax)
    g.sM, g.Mmin, g.Mmax = margins(Mmin, Mmax)
    g.Q, g.M, g.N = Q, M, N
    if N != None:
        Nmax = max([fabs(y) for (x,y) in N]); Nmin = -Nmax
        g.sN, g.Nmin, g.Nmax = margins(Nmin, Nmax)

    if _root == None:
        win = _root = _gc.Tk()
    else:
        if   gc == "dxf": win = _root
        elif gc == "pil": win = _root
        else:             win = _gc.Toplevel(_root)
    c = _gc.Canvas(win, background= "black", width=width, height=height)
    c.grid(sticky="wesn")
    c.textsize = textsize
    c.texttheta = texttheta
    win.columnconfigure(0, weight=1)
    win.rowconfigure(0, weight=1)
    replot(None, c, g)
    c.bind("<Configure>", lambda evt=None, c=c, g=g: replot(evt, c, g))
    win.title(tit)
    if gc != "tk+": _root.mainloop()

def margins(xmin, xmax):
    "Extend xmin, xmax so that we have some margins."
    dx = (xmax - xmin)*0.2
    if dx == 0.0: dx = 1.0
    return xmax-xmin+dx, xmin-dx*0.5, xmax+dx*0.5
