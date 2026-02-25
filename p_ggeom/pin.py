from math import pi, cos, sin, atan2, fabs
import p_ggen
from p_gmath import dpt


class Pin:
    "Represents a named tilted orthogonal frame."

    def __init__(self, aa="(Untitled)", x1=0.0, y1=0.0, am=1.0, ap=1.0, theta=0.0):
        "Initialize object."
        self.aa = aa
        self.x1 = x1
        self.y1 = y1
        self.am = am
        self.ap = ap
        self.__setdegrees(theta)


    def __setdegrees(self, theta):
        "From an angle in degrees, compute the angles of the frame."
        self.th = dpt(theta * pi/180.0)
        self.theta = self.th*180.0/pi


    def __str__(self):
        "Convert the attributes to a formatted string; opposite of .readText()."
        return "%-10s%15.3f%15.3f%15.3f%15.3f%15.6f" % \
               (self.aa, self.x1, self.y1, self.am, self.ap, self.theta)


    def readText(self, dline):
        "Read all attributes from string; may raise IndexError, ValueError."
        dl = dline.split()
        try:
            aa = dl[0]
            x1, y1, am, ap, theta = map(float, dl[1:6])
        except (ValueError, IndexError) as e:
            return False, "%s" % (e,)
        self.aa, self.x1, self.y1, self.am, self.ap = aa, x1, y1, am, ap
        self.__setdegrees(theta)
        return True, ""


    def fromPolygon(self, polygon):
        """Finds the circumscribed rectangle which includes the polygon.

           The direction of the rectangle coincide with the first line of the polygon."
        """
        x1, y1 = polygon[0]
        x2, y2 = polygon[1]
        self.__setdegrees(atan2(y2-y1, x2-x1)*180.0/pi)
        cosf = cos(self.th)
        sinf = sin(self.th)
        xn = [ xx1*cosf+yy1*sinf for xx1, yy1 in polygon]
        yn = [-xx1*sinf+yy1*cosf for xx1, yy1 in polygon]
        xx1 = min(xn)
        yy1 = min(yn)
        self.am = max(xn) - xx1
        self.ap = max(yn) - yy1
        sinf = -sinf
        self.x1 =  xx1*cosf+yy1*sinf
        self.y1 = -xx1*sinf+yy1*cosf
        return self


    def invert(self):
        "Inverts the angle theta; thus x1,y1 is the upper-right corner."
        (x1,y1), (x2,y2), (x3,y3), (x4,y4) = self.coords()
        self.x1 = x3
        self.y1 = y3
        self.__setdegrees(self.theta - 180.0)
        return self


    def invertsides(self):
        "Invert a frame so that length is width, and width is length."
        (x1,y1), (x2,y2), (x3,y3), (x4,y4) = self.coords()
        self.x1 = x2
        self.y1 = y2
        self.am, self.ap = self.ap, self.am
        self.__setdegrees(self.theta+90.0)
        return self


    def coords(self, closed=False):
        "Return the coordinates of 4 corners of the frame."
        th = self.th
        x2, y2 = self.x1 + self.am*cos(th), self.y1 + self.am*sin(th)
        th += pi*0.5
        x3, y3 = x2 + self.ap*cos(th), y2 + self.ap*sin(th)
        th += pi*0.5
        x4, y4 = x3 + self.am*cos(th), y3 + self.am*sin(th)
        if closed: return (self.x1,self.y1), (x2,y2), (x3,y3), (x4,y4), (self.x1, self.y1)
        else:      return (self.x1,self.y1), (x2,y2), (x3,y3), (x4,y4)


    def coordsxy(self, closed=False):
        "Return the coordinates of 4 corners of the frame as paralel lists."
        cc = self.coords(closed)
        return [x1 for x1, y1 in cc], [y1 for x1, y1 in cc]


    def dxfoutold(self, dxf):
        "Plots the frame into dxf file."
        (x1,y1), (x2,y2), (x3,y3), (x4,y4) = self.coords()
        dxf.thanDxfPlotPolyline((x1,x2,x3,x4,x1), (y1,y2,y3,y4,y1))
        h = self.ap/4.0
        th = self.th
        xc = (x1+x2+x3+x4)/4 - h*len(self.aa)*0.5*cos(th)
        yc = (y1+y2+y3+y4)/4 - h*len(self.aa)*0.5*sin(th)
        th += 0.5*pi
        xc -= h*0.5*cos(th)
        yc -= h*0.5*sin(th)
        dxf.thanDxfPlotSymbol(xc, yc, h, self.aa, self.theta)

    def dxfout(self, dxf):
        "Plots the frame into dxf file."
        theta1 = self.theta
        if theta1 > 90 and theta1 <= 270: theta1 = theta1 - 180
        th1 = theta1*pi/180

        (x1,y1), (x2,y2), (x3,y3), (x4,y4) = self.coords()
        dxf.thanDxfPlotPolyline((x1,x2,x3,x4,x1), (y1,y2,y3,y4,y1))
        h = self.ap/4.0
        xc = (x1+x2+x3+x4)/4 - h*len(self.aa)*0.5*cos(th1)
        yc = (y1+y2+y3+y4)/4 - h*len(self.aa)*0.5*sin(th1)
        th1 += 0.5*pi
        xc -= h*0.5*cos(th1)
        yc -= h*0.5*sin(th1)
        dxf.thanDxfPlotSymbol(xc, yc, h, self.aa, theta1)


    def sykout(self, fw, orthoim=False):
        "Writes the frame into .syk file; if orthoim==True then slightly different format."
        (x1,y1), (x2,y2), (x3,y3), (x4,y4) = self.coords()
        if not orthoim: fw.write("%15.3f  %s\n" % (0.0, self.aa))
        form = "%15.3f%15.3f\n"
        fw.write(form % (x1, y1))
        fw.write(form % (x2, y2))
        fw.write(form % (x3, y3))
        fw.write(form % (x4, y4))
        if not orthoim: fw.write(form % (x1, y1))
        fw.write("$\n")


    def mesa(self, xt, yt):
        "Returns true if point xt, yt is inside the frame."
        cosf = cos(self.th)
        sinf = sin(self.th)
        ammin =  self.x1*cosf+self.y1*sinf
        apmin = -self.x1*sinf+self.y1*cosf
        amt =  xt*cosf+yt*sinf
        apt = -xt*sinf+yt*cosf
        if amt < ammin: return False
        if apt < apmin: return False
        if amt > ammin+self.am: return False
        if apt > apmin+self.ap: return False
        return True


def poly2pin(thanPolylines, thanTexts=(), prt=p_ggen.prg):
    """Discovers frames in a set of polylines and the frames names in a set of texts.

    Typically read from a dxf file. The polylines are supposed to be rectangles.
    if the texts are empty the program does not complain if it does not find names.
    """
    iFrame=99900
    frames = []
    for xx, yy, zz, lay, col in thanPolylines:
        ok = len(xx) == 4
        ok = ok or (len(xx) == 5 and fabs(xx[0]-xx[-1]) < 0.01 and fabs(yy[0]-yy[-1]) < 0.01)
        if not ok:
            prt("Frame does not have 4 corners:")
            for i in range(min((len(xx), 10))): prt("%15.3f%15.3f" % (xx[i], yy[i]))
            prt("Frame is ignored.\n")
            continue
#-------Make sure the order is counter clockwise
        pin = Pin()
        pin.fromPolygon(list(zip(xx, yy)))
        if pin.am < pin.ap: pin.invertsides()    #Make the first side the biggest side
        if pin.th >= pi: pin.invert()            #Make the angle 0<=angle<pi
#-------Find frame's name
        for xt, yt, lay, col, name, h, theta in thanTexts:
            if pin.mesa(xt, yt):
                pin.aa = name
                break
        else:
            if len(thanTexts) > 0: prt("\nWarning: a frame was found with no name.")
            pin.aa = str(iFrame)
            iFrame += 1
        frames.append((pin, lay))
    return frames
