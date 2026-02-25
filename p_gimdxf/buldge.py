from math import sqrt, atan2, cos, sin, pi
from p_gmath import dpt

def buldge(x1, y1, x2, y2, buldge):
    li = []
    pendown = False
    dx = x2 - x1
    dy = y2 - y1
    b = buldge*127.0
    assert b != 0.0
    xc, yc, r, th, dth = __buldge(None, li, x1, y1, 1.0, pendown, dx, dy, b)

    def __buldge(self, li, xnow, ynow, fact, pendown, dx, dy, b):
        "Process a buldge entry."
        dx *= fact; dy *= fact
        if b == 0:
            if pendown and len(li) == 0: li.append((xnow, ynow))
            xnow += dx; ynow += dy
            if pendown: li.append((xnow,ynow))
            return
        else:
            d = sqrt(dx**2+dy**2)
            if d == 0.0: return xnow, ynow
            th = atan2(dy, dx)
            idd = b/abs(b)
            h = abs(b)*d/2/127
            r = ((d/2)**2+h**2)/2/h
            th += idd*pi*0.5
            xc = xnow+dx*0.5+(r-h)*cos(th)
            yc = ynow+dy*0.5+(r-h)*sin(th)
            th = atan2(ynow-yc, xnow-xc)
            dth = dpt(atan2(ynow+dy-yc, xnow+dx-xc) - th)
            if idd > 0:
                assert dth >= 0.0 and dth <= pi
            else:
                dth -= 2*pi
                assert dth <= 0.0 and dth >= -pi
            return xc, yc, r, th, dth
        return xnow, ynow
