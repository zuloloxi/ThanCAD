from math import ceil, log2, hypot


def plotbintree(dxf, a, xroot=0.0, yroot=0.0, dx=2.0, dy=2.5, rc=0.5, hs=0.25):
    "Plot a heap binary tree; node which contain None are not plotted."
    #dx = 2.0             #horizonal distance in cm between leaves at the last level
    #dy = 2.5             #vertical distance in cm bnetween rows
    #rc = 0.5             #Diameter in cm of circles
    #hs = 0.25            #Text height
    n = len(a)
    nlev = ceil(log2(n+1))

    x1 = xroot      #Coordinate x of root
    y1 = yroot      #Coordinate y of root
    dx1 = dx*2**(nlev-1)   #Horizontal distance at level 0
    dxf.thanDxfPlotCircle(x1, y1, rc)
    icel = 0   #Index of root in list/array a
    plotnum(dxf, x1, y1, a[icel], hs)
    for ilev in range(1, nlev):
        xpar = x1   #Coordinates of the leftest circle of previous level
        ypar = y1   #Coordinates of the leftest circle of previous level
        dx1 /= 2    #Horizontal distance at current level
        y1 -= dy    #Coordinates of the leftest circle of current level
        x1 -= dx1/2 #Coordinates of the leftest circle of current level
        x = x1
        for j in range(2**ilev):
            icel += 1    #Index of jth element of the current level
            if icel >= len(a): break    #Last row of elements may not be complete
            if a[icel] is not None:
                dxf.thanDxfPlotCircle(x, y1, rc)
                plotedge(dxf, x, y1, xpar, ypar, rc)
                plotnum(dxf, x, y1, a[icel], hs)
            if j%2 == 1: xpar += 2*dx1
            x += dx1


def plotedge(dxf, x, y, xpar, ypar, r):
    "Plot an edge through the center of 2 circles of radius r; do nty plot edge inside the circles."
    dx = xpar - x
    dy = ypar - y
    dd = hypot(dx, dy)
    x1 = x+r*dx/dd
    y1 = y+r*dy/dd
    x2 = x+(dd-r)*dx/dd
    y2 = y+(dd-r)*dy/dd
    dxf.thanDxfPlot(x1, y1, 3)
    dxf.thanDxfPlot(x2, y2, 2)


def plotnum(dxf, x1, y1, num, hs):
    "Plot number (or string) num, inside the circle centered at x1, y1."
    t = str(num)
    nt = len(t)
    xx = x1 - nt*hs/2 * (2/3)   #Text width is ~2/3 of text height
    yy = y1 - hs/2
    dxf.thanDxfPlotSymbol(xx, yy, hs, t, 0.0)
