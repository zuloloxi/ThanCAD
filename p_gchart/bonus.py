from math import sin, cos, pi
from .thanfonts import thanFontPrime1


def dashed_star(x, y, r, color, fill, size, chart):
    r *= 0.5
    th = 0.0
    for i in range(8):     #OK for python 2,3
        x1 = x + r*cos(th)
        y1 = y + r*sin(th)
        chart.curveAdd((x, x1),  (y, y1), color=color, fill=fill, style="dashedsym", size=size)
        th += pi*0.25

#=============================================================================

def thanSymbolLine7f(xz, yz, h, a, theta, tfont=thanFontPrime1, linefun=None):
        "Draws text using ThanCad's line fonts."

        assert h >= 1.0, "Text height must be > 1 pixel"

        hf = 7.0
        theta *= (pi/180.0)
        by = h / hf
        bx = by*cos(theta)
        by = by*sin(theta)
        hx2 = hf * bx
        hy2 = hf * by

#-------Transform the coordinates

        for c in a:                               # Loop of all the characters in text
            k = ord(c)
            if type(tfont[k]) is int: k = tfont[k]
            if k < 0 or k > 255:
                print("Character with code:" + str(k))
                return

            for pl in tfont[k]:                   # Loop of all polylines of a char
#                plr = [ (xz+xx*bx-yy*by, yz-(xx*by+yy*bx)) for (xx, yy) in pl ]
                xpp = [	xz+xx*bx-yy*by for (xx, yy) in pl ]
                ypp = [	yz+xx*by+yy*bx for (xx, yy) in pl ]
                linefun(xpp, ypp)

            xz += hx2     # Advance character position
            yz -= hy2
