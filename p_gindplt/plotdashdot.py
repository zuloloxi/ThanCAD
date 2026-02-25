from math import hypot, fabs, pi
from p_gmath import dpt

def plotdashdot(plotline, x, y, dash1, space1, dash2, dashrem=()):
    "Plot polyline with dash1, space1, dash2, space2, ..."
    dashes = [dash1, -space1, dash2, -space1]
    for i in range(len(x)-1):
        dashrem = plotdashdot1(plotline, x[i], y[i], x[i+1], y[i+1], dashes, dashrem)
    return dashrem


def plotdashdot1(plotline, x1, y1, x2, y2, dashes, dashrem):
    "Plot a single line with dash1, space1, dash2, space2, ..."

    def plotdash(dashk):
        "Plot or move the length of one dash; if doplot is false move, else plot."
        nonlocal xnow, ynow, dnow
        doplot = dashk > 0.0
        dashk = fabs(dashk)
        if dnow+dashk > d:
            if doplot: plotline(xnow, ynow, x2, y2)
            xnow = x2
            ynow = y2
            dashk = dashk - (d-dnow)
            dnow = d
            return dashk if doplot else -dashk

        xd = xnow + dx * dashk/d
        yd = ynow + dy * dashk/d
        if doplot: plotline(xnow, ynow, xd, yd)
        xnow = xd
        ynow = yd
        dnow = dnow + dashk
        return 0.0


    dx = x2-x1
    dy = y2-y1
    d = hypot(dx, dy)
    xnow = x1
    ynow = y1
    dnow = 0.0

    if len(dashrem) > 0:
        #Plot initial dashes
        for i in range(len(dashrem)):
            dashrem1 = plotdash(dashrem[i])
            if dashrem1 != 0.0: return [dashrem1]+dashrem[i+1:]
            if dnow >= d: return dashrem[i+1:]

    while True:
        #Plot normal dashes continuously
        for i in range(len(dashes)):
            dashrem1 = plotdash(dashes[i])
            if dashrem1 != 0.0: return [dashrem1]+dashes[i+1:]
            if dnow >= d: return dashes[i+1:]



def plotdashdotarc1(plotarc, xc, yc, r, th1, th2, dashes, dashrem):
    "Plot a single arc with dash1, space1, dash2, space2, ..."

    def plotdash(dashk):
        "Plot or move the length of one dash; if doplot is false move, else plot."
        nonlocal dnow
        doplot = dashk > 0.0
        dashk = fabs(dashk)
        if dnow+dashk > d:
            if doplot: plotarc(xc, yc, r, th1+dnow/r, th2)
            dashk = dashk - (d-dnow)
            dnow = d
            return dashk if doplot else -dashk

        if doplot: plotarc(xc, yc, r, th1+dnow/r, th1+(dnow+dashk)/r)
        dnow = dnow + dashk
        return 0.0


    if th1 is None or th2 is None:   #This is a circle
        th1 = 0.0
        th2 = 2.0*pi
        d = (th2-th1)*r
    else:
        d = dpt(th2-th1)*r
    dnow = 0.0

    if len(dashrem) > 0:
        #Plot initial dashes
        for i in range(len(dashrem)):
            dashrem1 = plotdash(dashrem[i])
            if dashrem1 != 0.0: return [dashrem1]+dashrem[i+1:]
            if dnow >= d: return dashrem[i+1:]

    while True:
        #Plot normal dashes continuously
        for i in range(len(dashes)):
            dashrem1 = plotdash(dashes[i])
            if dashrem1 != 0.0: return [dashrem1]+dashes[i+1:]
            if dnow >= d: return dashes[i+1:]
