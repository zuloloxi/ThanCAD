from math import sqrt

class Regression:
    "An object to hold and compute linear regression between 2 variables."

    def __init__(self):
        "Zero some sums."
        self.sx = self.sy = self.sx2 = self.sy2 = self.sxy = 0.0
        self.n = 0


    def add(self, x, y):
        "Add a pair of values."
        self.sx += x
        self.sy += y
        self.sx2 += x**2
        self.sy2 += y**2
        self.sxy += x*y
        self.n += 1


    def getCorelation(self):
        "Compute the corelation coefficient."
        r = (self.n*self.sxy - self.sx*self.sy)/sqrt(self.n*self.sx2 - self.sx**2) / \
                                                sqrt(self.n*self.sy2 - self.sy**2)
        return r

    """
program po2
    implicit none
    real, dimension(5) :: x, y
    real :: an, sx, sy, a, b, rmse
    y = (/1.0, 5.0, 3.0, 9.0, 7.0/)
    x = (/1.0, 3.0, 2.0, 5.0, 4.0/)
    sx = sum(x)
    sy = sum(y)
    an = real(size(x))
    a = (an*sum(x*y) - sx*sy) / (an*sum(x**2) - sx**2)
    b = (sy - a*sx) / an
    rmse = sqrt(sum((y - (a*x+b))**2) / an)
    write (*, *) a, b, rmse
    x = (/1500.0, 1900.0, 2345.0, 325.0, 589.0/)
    write (*, *) a*x+b
end program po2
    """

    def getCoef(self):
        "Compute the coefficients of the best line and the RMSE."
        a = (self.n*self.sxy - self.sx*self.sy) / (self.n*self.sx2 - self.sx**2)
        b = (self.sy - a*self.sx) / self.n
        rmse = self.sy2 + a**2*self.sx2 + self.n*b**2 - 2*a*self.sxy -2*b*self.sy + 2*a*b*self.sx
        rmse = sqrt(rmse/self.n)
        return a, b, rmse
