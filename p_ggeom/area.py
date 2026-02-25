from p_gmath import thanNear2, thanNearx

def areapn(cc):
    """Finds the area of polygon cc (positive->clockwise, negative->counterclockwise).

    The first point of the polygon should coincide with the last.
    The points should be in order."""
    xx = [c[0] for c in cc]
    yy = [c[1] for c in cc]
    if xx[0] != xx[-1] or yy[0] != yy[-1]: xx.append(xx[0]); yy.append(yy[0])
    ymin = min(yy)
    for i in range(len(yy)): yy[i] -= ymin 
    e = 0.0
    for i in range(len(yy)-1):
        j = i + 1
        e += (xx[j]-xx[i]) * (yy[j]+yy[i])
    return e*0.5


def area(cc):
    "Finds the area of polygon cc as a positive number."
    return abs(areapn(cc))


def spin(cp):
        "Returns the spin of the line, imagining that it is closed."
        a = areapn(cp)
        if a > 0.0: return -1                #Nodes are clockwise
        if a < 0.0: return  1                #Nodes are Counter-Clockwise
        cp = iter(cp)
        c1 = next(cp)
        for c2 in cp:
            if not thanNear2(c1, c2): break  #Only x,y coordinate are taken into account for the spin
        else:
            return 1      # All line points are close together:Degenerate line to a point: return 1 arbitrarily
        for a,b in zip(c1, c2):
            if thanNearx(a, b): continue
            if b > a: return 1  #If one straight line segment, then spin is positive if x2>x1,
            else:     return -1 # or else if y2>y1 or else z2>z1 etc. The same is true the line
#                               # has equal segments in the clockwise and the counter clockwise direction
        assert 0, "Degenerate line should have already been found!"
