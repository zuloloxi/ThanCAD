from math import pi, cos, sin, modf
from tkinter import ARC, PIESLICE
from p_ggen import frangec
from .thanfonts import thanFontPrime1


##############################################################################
##############################################################################


class ThanSymbol:
    "Symbol as a union of lines, arcs, and (filled) polygons and circles."

#=============================================================================

    def __init__(self, lines=(), arcs=(), polygons=(), circles=()):
        "Initialise symbol."

        self.lines    = lines
        self.arcs     = arcs
        self.polygons = polygons
        self.circles  = circles

#=============================================================================

    def thanTkDraw(self, dc, x, y, r, color, fill):
        "Plots the symbol to canvas dc."

        for xc, yc, rc in self.circles:
            xc, yc = (x+xc*r, y-yc*r)
            rc *= r
            dc.create_arc(xc-rc, yc+rc, xc+rc, yc-rc, start=0.0, extent=359.99999,
                style=PIESLICE, outline=color, fill=fill)
        for pol in self.polygons:
            pol1 = [ (x+x1*r,y-y1*r) for (x1,y1) in pol ]
            dc.create_polygon(pol1, outline=color, fill=fill)
        for lin in self.lines:
            lin1 = [ (x+x1*r,y-y1*r) for (x1,y1) in lin ]
            dc.create_line(lin1, fill=color)
        for xc, yc, rc, th1, dth in self.arcs:
            xc, yc = (x+xc*r, y-yc*r)
            rc *= r
            dc.create_arc(xc-rc, yc+rc, x+rc, yc-rc, start=th1, extent=dth,
                style=ARC, outline=color)


##############################################################################
##############################################################################

#MODULE LEVEL FUNCTIONS

#=============================================================================

def __pcircle(dc, x, y, r, color, fill):
            r *= 0.5
            dc.create_arc(x-r, y+r, x+r, y-r, start=90.0, extent=359.99999,
                style=PIESLICE, outline=color, fill=fill)

#=============================================================================

def __pelips(dc, x, y, r, color, fill):
            r *= 0.5
            dc.create_arc(x-r*0.5, y+r, x+r*0.5, y-r, start=0.0, extent=359.99999,
                style=ARC, outline=color, fill=fill)

#=============================================================================

def __pcross(dc, x, y, r, color, fill):
            r *= 0.5
            dc.create_line(x-r, y, x+r, y, fill=color)
            dc.create_line(x, y-r, x, y+r, fill=color)

#=============================================================================

def __pchi(dc, x, y, r, color, fill):
            r *= 0.5
            dc.create_line(x-r, y-r, x+r, y+r, fill=color)
            dc.create_line(x-r, y+r, x+r, y-r, fill=color)

#=============================================================================

def __pstar(dc, x, y, r, color, fill):
            r *= 0.5
            r1 = r * 0.5
            r2 = r * 0.866025
            dc.create_line(x-r, y, x+r, y, fill=color)
            dc.create_line(x-r1, y-r2, x+r1, y+r2, fill=color)
            dc.create_line(x+r1, y-r2, x-r1, y+r2, fill=color)

#=============================================================================

def __psquare(dc, x, y, r, color, fill):
            r *= 0.5
            dc.create_rectangle(x-r, y-r, x+r, y+r, outline=color, fill=fill)

#=============================================================================

def __ptriangle(dc, x, y, r, color, fill):
            r *= 0.5
            r1 = r * 0.5
            r2 = r * 0.866025
            dc.create_polygon((x-r2, y-r1), (x+r2, y-r1), (x, y+r),
                outline=color, fill=fill)

#=============================================================================

def __ptristar(dc, x, y, r, color, fill):
            r *= 0.5
            r1 = r * 0.5
            r2 = r * 0.866025
            dc.create_line(x, y, x-r2, y-r1, fill=color)
            dc.create_line(x, y, x+r2, y-r1, fill=color)
            dc.create_line(x, y, x, y+r, fill=color)

#=============================================================================

def __makeGkiPolygons():
    "Makes closed polygons that define a gki symbol."

    arcs = \
    (   (0.222848317821, 1.01686467438,  0.223485547626, 184.327770235,   77.6276069692),
        (0.349976329745, 0.677276574707, 0.197704310589, 143.246225278,   88.7097788553),
        (0.329754401419, 0.302354397263, 0.24162877519,  114.869214539,  111.80752797),
        (0.130835855511, 0.0,            0.130835855511,  75.3302899249, 104.669710075)
    )
    thetas = (-30, 30)
    circles = \
    (   ( 0.0290118827145, -0.57549661631,  0.0421495479065),
        ( 0.0342838155587, -0.475388711295, 0.0424872084551),
        (-0.0659000920923, -0.517540243737, 0.0542542738795)
    )

#---Vertices of a side of a gki

    ps = [ ]
    for xc, yc, r, th1, dth in arcs:
#        if len(ps) > 0: del ps[-1]
        for d in frangec(0, dth, 15):
            th = (th1 + d)*pi/180
            ps.append( (xc+r*cos(th), yc+r*sin(th)) )

#---Mirror and combine it in one closed polyline

    ps1 = [ (-x, y) for (x,y) in ps ]
    ps1.reverse()
#    ps.extend(ps1[1:-1])
    ps.extend(ps1)

#---Make 2 gkis one in 60 degs, and one in 120 degs (center is at half height)

    pols = [ ]
    dy = cos(thetas[0]*pi/180) * 0.5
    for th in thetas:
        th *= pi/180
        cost = cos(th)
        sint = sin(th)
        ps1 = [(x*cost+y*sint, -x*sint+y*cost-dy) for (x,y) in ps]
        pols.append(ps1)

#---Add 3 circles as polygons

    for xc, yc, r in circles:
        th1 = 0.0
        ps = [ ]
        for d in frangec(0, 360, 30):
            th = (th1 + d)*pi/180
            ps.append( (xc+r*cos(th), yc+r*sin(th)) )
        pols.append(ps)

#          lines, arcs, polygons, circles
    return (),    (),   pols,     ()

#=============================================================================

def __makeChristarPolygons():
    "Makes closed polygons that define a christmas star symbol."

    x = y = th = 0.0
    ps = [ ]
    for i in range(10):
        r1 = 0.5
        if i%2 == 1: r1 *= 0.5
        ps.append((x + r1*cos(th), y + r1*sin(th)))
        th += pi*0.2

#          lines, arcs, polygons, circles
    return (),    (),   [ps],     ()

#=============================================================================

def __makeAnalogClock(tim=2.55):
    """Makes closed polygons that define an analog clock.
    tim is float with format hh.mm
    hh = hour = 1-12
    mm = minute = 0-59
    """

    n = 24; dth = pi*2/n
    th = 0.0; r = 0.5; p = []
    for i in range(n+1): p.append((r*cos(th),r*sin(th))); th = th + dth
    th = 0.0; r *= 0.90
    for i in range(n+1): p.append((r*cos(th),r*sin(th))); th = th + dth
    pols = [p]

#    lines = [None]*12
#    th = 0.0; dth = pi/6
#    for i in range(12):
#        r1 = r*0.90
#        if i%3 == 0: r1 = r*0.70
#        lines[i] = (r1*cos(th), r1*sin(th)), (r*cos(th), r*sin(th))
#        th += dth


    lines = ()
    th = 0.0; dth = pi/6
    for i in range(12):
        r1 = r*0.90; dt = dth/15
        if i%3 == 0: r1 = r*0.70; dt = dth/10
        p = (r1*cos(th), r1*sin(th)), (r*cos(th-dt), r*sin(th-dt)),\
        (r*cos(th+dt), r*sin(th+dt)), (r1*cos(th), r1*sin(th))
        pols.append(p)
        th += dth

    deikbi = (0,0.07), (0.8, 0.10), (1,0),   (0.8, -0.10), (0,-0.07), (0,0.07)
    deiksm = (0,0.07), (0.6, 0.10), (0.8,0), (0.6, -0.10), (0,-0.07), (0,0.07)

    mm, hh = modf(tim)
    r1 = 0.80*r
    for th,deik in (0.5*pi-hh*pi/6,deiksm), (0.5*pi-mm*pi/0.30,deikbi):
        cost = cos(th); sint = sin(th)
        p = [(r1*(x*cost-y*sint), r1*(x*sint+y*cost)) for (x,y) in deik]
        pols.append(p)

#          lines, arcs, polygons, circles
    return lines,   (),     pols,      ()

#=============================================================================

def __makeSnowmanElements():
    "Makes lines, arcs, circles that define a snowman symbol."

    lines = \
    (   (    (-0.0189626789414, 0.199965180047),
             ( 0.0,             0.265563500509),
             ( 0.0189626789414, 0.199965180047),
             (-0.0189626789414, 0.199965180047)
        ),
        (    (0.0590550194723, -0.322883456424),
             (0.0715457094757, -0.32749602802),
             (0.336270290023,   0.310781822038),
             (0.323980572993,   0.315878959884),
             (0.0590550194723, -0.322883456424)
        ),

        (    (0.0617202678855, 0.354056652178),
             (0.100675240199,  0.394207551991)
        ),
        (    (-0.0424067464585, 0.362672467148),
             (-0.0677976767568, 0.458311768776)
        ),
        (    (0.0418739093037, 0.416581553291),
             (0.0217379054198, 0.368031602843)
        ),
        (    (-0.0166819610713, 0.368797824059),
             (-0.015565585404,  0.438437373723)
        ),
        (    (0.0891402938775, 0.333836586804),
             (0.15661957792,   0.372920641204)
        ),
        (    (0.330125431508, 0.313330390961),
             (0.504984450697, 0.414608872429)
        ),
        (    (0.330125431508, 0.313330390961),
             (0.332799287373, 0.480125604948)
        ),
        (    (0.330125431508, 0.313330390961),
             (0.28056719602,  0.5)
        ),
        (    (0.330125431508, 0.313330390961),
             (0.449040112977, 0.435895783215)
        ),
        (    (0.390238782081, 0.458269784515),
             (0.330125431508, 0.313330390961)
        )
    )

    arcs = \
    (   (0, 0.255373500718, 0.0986960714185, 232.136353606, 75.727292788),
    )

    circles = \
    (   ( 0,               0.241657125163,   0.128230437654),
        ( 0,              -0.193286656246,   0.306713343754),
        ( 0,              -0.00455206381752, 0.0225269688075),
        ( 0,              -0.236557067951,   0.0225269688075),
        ( 0,              -0.118814386282,   0.0225269688075),
        (-0.0571838436366, 0.288090469316,   0.0225269688075),
        ( 0.0554510004007, 0.288090469316,   0.0225269688075),
    )

#          lines, arcs, polygons, circles
    return lines, arcs, (),       circles

#=============================================================================

def __addFontAsSymbols(tfont, points):
        "Import ThanCad's font as symbols."
        gc8  = "ΪΫΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΆΈΉΊΌΎΏΪΫΣ"
        gs8  = "ΐΰαβγδεζηθικλμνξοπρστυφχψωάέήίόύώϊϋς"
        greekiso8897_7 = {}
        for c in gc8+gs8:
            c = c.encode("iso8859_7")
            greekiso8897_7[ord(c)] = c
        def chriso8859_7(key): return greekiso8897_7.get(key, chr(key))

        for key in tfont:
            lines = tfont[key]
            if type(lines) == int: lines = tfont[lines]
            lines1 = [ ]
            for lin in lines:
                lin1 = [ ((x-2.5)/7.0, (y-3.5)/7.0) for (x, y) in lin ]
                lines1.append(lin1)
            #points[chr(key)] = ThanSymbol(lines=lines1).thanTkDraw
            points[chriso8859_7(key)] = ThanSymbol(lines=lines1).thanTkDraw


##############################################################################
##############################################################################

#MODULE LEVEL CODE - SYMBOL DEFINITIONS


#print "gki:", gki
#print "Christar:", christar
#print "snowman:", snowman

__gki      = ThanSymbol(*__makeGkiPolygons())
__christar = ThanSymbol(*__makeChristarPolygons())
__snowman  = ThanSymbol(*__makeSnowmanElements())
__anClock = ThanSymbol(*__makeAnalogClock())
__anClock50 = ThanSymbol(*__makeAnalogClock(0.50))
__anClock55 = ThanSymbol(*__makeAnalogClock(0.55))
__anClock00 = ThanSymbol(*__makeAnalogClock(0.00))

thanPoints = { "circle"    : __pcircle,
               "elips"     : __pelips,
               "cross"     : __pcross,
               "chi"       : __pchi,
               "star"      : __pstar,
               "square"    : __psquare,
               "triangle"  : __ptriangle,
               "tristar"   : __ptristar,
               "gki"       : __gki.thanTkDraw,
               "christar"  : __christar.thanTkDraw,
               "snowman"   : __snowman.thanTkDraw,
               "anclock"   : __anClock.thanTkDraw,
               "anclock50"   : __anClock50.thanTkDraw,
               "anclock55"   : __anClock55.thanTkDraw,
               "anclock00"   : __anClock00.thanTkDraw,
             }
__addFontAsSymbols(thanFontPrime1, thanPoints)


if __name__== "__main__": pass
