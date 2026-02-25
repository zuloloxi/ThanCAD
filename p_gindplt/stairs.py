import p_gindplt, p_gmath
from math import ceil, pi

#landing: Πλατύσκαλο
#Well/Wellhole: Φανάρι
#flight: βραχίονας ή κλάδος
#riser: βαθμίδα
#Line of Travel (or Going Line): Γραμμή ανάβασης
#U-shaped staircase: Σκάλα με ενδιάμεσο πλατύσκαλο 180ᵒ
#Straight staircase: Ευθύγραμμη σκάλα


def staircaseU(dxf, ca, f, dscale, clockwise, bpat, hrise, bskal, bwell, blanding, nyps, trname="TR"):
    "Draw a U shaped staircase - with 2 flights."
    f = p_gmath.dpt(f-0.5*pi)     #If f==0 then the default staircase has vertical orientation -> correct it
    sim = p_gmath.Similar2DProjection()
    sim.setTraRotSca(cu=ca, gon=f, am=1.0, rotcenter=(0.0, 0.0))  #Similar2DProjection needs anticloskwise angle
    def tra(c): return sim.project((c[0], c[1], 0))[:2]

    fdeg = f*180.0/pi   #Angle in radians
    hs = 0.15 * dscale / 100.0
    nyps1 = ceil(nyps/2)
    nyps2 = nyps - nyps1
    ya = 0.0 if nyps2 == nyps1 else bpat

    dxf.thanDxfSetLayer('STAIRCASE__STAIRS')
    dxf.thanDxfSetColor(7)
    drawFlight(              dxf, tra,   0.0,          0.0, bpat, bskal, nyps1)     #Draw left flight
    if clockwise: drawFlight(dxf, tra,   bskal+bwell,  ya,  bpat, bskal, nyps2)     #Draw right flight clockwise
    else:         drawFlight(dxf, tra, -(bskal+bwell), ya,  bpat, bskal, nyps2)     #Draw right flight counterclockwise
    drawLanding(dxf, tra, clockwise, bpat, bskal, bwell, blanding, nyps1)

    #Line of travel - γραμμή ανάβασης - left flight
    dxf.thanDxfSetLayer('STAIRCASE__TRAVEL')
    dxf.thanDxfSetColor(1)
    drawTravelU(dxf, tra, clockwise, bpat, bskal, bwell, blanding, nyps1, ya)

    #Rise numbering - αρίθμηση υψών
    dxf.thanDxfSetLayer ('STAIRCASE__TEXT')
    dxf.thanDxfSetColor(2)
    drawNumbering(dxf, tra, clockwise, bpat, bskal, bwell, nyps1, nyps2, hs, fdeg)

    dxf.thanDxfSetLayer ('STAIRCASE__TRAVEL')
    dxf.thanDxfSetColor(-1)
    drawDirectionU(dxf, tra, clockwise, hs, bskal, bwell, ya)

    #Draw rectangle with tread and rize
    drawBox(dxf, tra, bpat, hrise, hs, fdeg, laytext='STAIRCASE__TEXT', trname=trname)


def staircaseS(dxf, ca, f, dscale, bpat, hrise, bskal, nyps, trname="TR"):
    "Draw a straight staicase."
    f = p_gmath.dpt(f-0.5*pi)     #If f==0 then the default staircase has vertical orientation -> correct it
    sim = p_gmath.Similar2DProjection()
    sim.setTraRotSca(cu=ca, gon=f, am=1.0, rotcenter=(0.0, 0.0))  #Similar2DProjection needs anticloskwise angle
    def tra(c): return sim.project((c[0], c[1], 0))[:2]

    fdeg = f*180.0/pi   #Angle in radians
    hs = 0.15 * dscale / 100.0

    #Draw flight
    dxf.thanDxfSetLayer('STAIRCASE__STAIRS')
    dxf.thanDxfSetColor(7)
    drawFlight(dxf, tra, 0.0, 0.0, bpat, bskal, nyps)
    y = (nyps-1)*bpat
    xt, yt = tra((0.0, y))
    dxf.thanDxfPlot (xt, yt, 3)
    xt, yt = tra((bskal, y))
    dxf.thanDxfPlot (xt, yt, 2)

    #Line of travel - γραμμή ανάβασης - left flight
    dxf.thanDxfSetLayer('STAIRCASE__TRAVEL')
    dxf.thanDxfSetColor(1)
    drawTravelS(dxf, tra, bpat, bskal, nyps)

    #Rise numbering - αρίθμηση υψών
    dxf.thanDxfSetLayer ('STAIRCASE__TEXT')
    dxf.thanDxfSetColor(2)
    drawNumbering(dxf, tra, False, bpat, bskal, -1, nyps, -1, hs, fdeg)

    dxf.thanDxfSetLayer ('STAIRCASE__TRAVEL')
    dxf.thanDxfSetColor(-1)
    drawDirectionS(dxf, tra, hs, bskal, ya=(nyps-1)*bpat)

    #Draw rectangle with tread and rize
    drawBox(dxf, tra, bpat, hrise, hs, fdeg, laytext='STAIRCASE__TEXT', trname=trname)


def drawTravelS(dxf, tra, bpat, bskal, nyps1):
    "Draw travel line for straight staircase."
    x = bskal*0.5
    y = (nyps1-1)*bpat
    xt, yt = tra((x, 0.0))
    dxf.thanDxfPlot (xt, yt, 3)
    xt, yt = tra((x, y))
    dxf.thanDxfPlot (xt, yt, 2)


def drawFlight(dxf, tra, xa, ya, bpat, bskal, nyps1):
    "Draw a single flight of the staircase."
    #Flight risers
    y = ya-bpat
    for i in range(nyps1-1):
        y += bpat
        xt, yt = tra((xa, y))
        dxf.thanDxfPlot (xt, yt, 3)
        xt, yt = tra((xa+bskal, y))
        dxf.thanDxfPlot (xt, yt, 2)

    #Enclosing lines
    y += bpat
    for b in 0.0, bskal:
        xt, yt = tra((xa+b, ya))
        dxf.thanDxfPlot (xt, yt, 3)
        xt, yt = tra((xa+b, y))
        dxf.thanDxfPlot (xt, yt, 2)


def drawLanding(dxf, tra, clockwise, bpat, bskal, bwell, blanding, nyps1):
    "Draw landing."
    if clockwise: x1 = 0.0
    else:         x1 = -bwell-bskal
    y1 = (nyps1-1)*bpat
    x3 = x1+bskal+bwell+bskal
    y3 = y1+blanding
    cc = [[x1, y1],
          [x3, y1],
          [x3, y3],
          [x1, y3],
          [x1, y1],
         ]
    cc = (tra(c) for c in cc)
    x, y = zip(*cc)
    dxf.thanDxfPlotPolyline(x, y)


def drawTravelU(dxf, tra, clockwise, bpat, bskal, bwell, blanding, nyps1, ya):
    "Draw travel line for U-shaped staircase."
    x = bskal*0.5
    y = (nyps1-1)*bpat + blanding * 0.5
    xt, yt = tra((x, 0.0))
    dxf.thanDxfPlot (xt, yt, 3)
    xt, yt = tra((x, y))
    dxf.thanDxfPlot (xt, yt, 2)

    if clockwise: x += bskal + bwell
    else:         x -= bskal + bwell
    xt, yt = tra((x, y))
    dxf.thanDxfPlot (xt, yt, 2)
    xt, yt = tra((x, ya))
    dxf.thanDxfPlot (xt, yt, 2)


def drawNumbering(dxf, tra, clockwise, bpat, bskal, bwell, nyps1, nyps2, hs, fdeg):
    "Draw rise numbering."
    #Rise numbering - left flight
    if 135 < fdeg < 315:
        inv = True
        xa = bskal*0.5 - hs    #Make sure that the user can read the text
        y = -bpat + bpat-hs*0.5
        fdeg -= 180.0
    else:
        inv = False
        xa = bskal*0.5 + hs
        y = -bpat + hs*0.5

    for i in range(nyps1):
        t = str(i+1)
        y += bpat
        xt, yt = tra((xa, y))
        dxf.thanDxfPlotSymbol (xt, yt, hs, t, fdeg)

    if bwell < 0.0: return    #Straight staircase: no second flight

    #rise numbering - right flight
    if inv:
        y = nyps1*bpat + bpat-hs*0.5
    else:
        y = nyps1*bpat + hs*0.5

    if clockwise: xa += bskal + bwell
    else:         xa -= bskal + bwell
    for i in range(nyps1, nyps1+nyps2):
        t = str(i+1)
        dx = -len(t)*hs if inv else 0.0
        dx = 0
        y -= bpat
        xt, yt = tra((xa+dx, y))
        #dxf.thanDxfPlotNumber (xt, yt, hs, float(i+1), fdeg, -1)
        dxf.thanDxfPlotSymbol (xt, yt, hs, t, fdeg)


def drawDirectionU(dxf, tra, clockwise, hs, bskal, bwell, ya):
      "Σχεδίαση φοράς σκάλας με πλατύσκαλο 180ᵒ."
      #Circle at the start of the line of travel
      xt, yt = tra((bskal*0.5 , 0.0))
      dxf.thanDxfPlotCircle(xt, yt, hs*0.25)

      #Triangle showing the direction of line of travel
      if clockwise: b2 = bskal + bwell + bskal*0.5    #U shaped staircase: second flight is closkwise
      else:         b2 = -bwell - bskal*0.5           #U shaped staircase: second flight is countercloskwise
      xt, yt = tra((b2, ya, 0.0))
      dxf.thanDxfPlot(xt, yt, 3)
      xt, yt = tra((b2, ya-hs*0.5))
      dxf.thanDxfPlot (xt, yt, 2)
      xt, yt = tra((b2-hs, ya))
      dxf.thanDxfPlot (xt, yt, 2)
      xt, yt = tra((b2, ya-hs*0.5))
      dxf.thanDxfPlot (xt, yt, 3)
      xt, yt = tra((b2+hs, ya))
      dxf.thanDxfPlot (xt, yt, 2)


def drawDirectionS(dxf, tra, hs, bskal, ya):
      "Σχεδίαση φοράς ευθύγραμμης σκάλας."
      #Circle at the start of the line of travel
      xt, yt = tra((bskal*0.5 , 0.0))
      dxf.thanDxfPlotCircle(xt, yt, hs*0.25)

      #Triangle showing the direction of line of travel
      b2 = bskal*0.5           #U shaped staircase: second flight is countercloskwise
      xt, yt = tra((b2, ya, 0.0))
      dxf.thanDxfPlot(xt, yt, 3)
      xt, yt = tra((b2, ya+hs*0.5))
      dxf.thanDxfPlot (xt, yt, 2)
      xt, yt = tra((b2-hs, ya))
      dxf.thanDxfPlot (xt, yt, 2)
      xt, yt = tra((b2, ya+hs*0.5))
      dxf.thanDxfPlot (xt, yt, 3)
      xt, yt = tra((b2+hs, ya))
      dxf.thanDxfPlot (xt, yt, 2)


def drawBox(dxf, tra, btread, hrise, hs, fdeg, laytext, trname):
      "Draw a box with the tread and the rise."
      y = 0.0 - 10.0*hs
      y2 = y + 6.0*hs
      b2 = 8.0*hs
      xt, yt = tra((0.0, y))
      dxf.thanDxfPlot(xt, yt, 3)
      xt, yt = tra((b2, y))
      dxf.thanDxfPlot(xt, yt, 2)
      xt, yt = tra((b2, y2))
      dxf.thanDxfPlot(xt, yt, 2)
      xt, yt = tra((0.0, y2))
      dxf.thanDxfPlot(xt, yt, 2)
      xt, yt = tra((0.0, y))
      dxf.thanDxfPlot(xt, yt, 2)

      xt, yt = tra((0.0, (y+y2)/2.0))
      dxf.thanDxfPlot(xt, yt, 3)
      xt, yt = tra((b2, (y+y2)/2.0))
      dxf.thanDxfPlot(xt, yt, 2)

      if 135 < fdeg < 315:
          xa = b2-hs
          ya = y+2*hs
          fdeg -= 180.0
      else:
          xa = hs
          ya = y+hs
      dxf.thanDxfSetLayer(laytext)
      xt, yt = tra((xa, ya))
      dxf.thanDxfPlotSymbol (xt, yt, hs, "%s=%.2f" % (trname[0], btread), fdeg)   #trname[0]="T"
      xt, yt = tra((xa, ya+3.0*hs))
      dxf.thanDxfPlotSymbol (xt, yt, hs, "%s=%.3f" % (trname[1], hrise), fdeg)    #trname[0]="R"
