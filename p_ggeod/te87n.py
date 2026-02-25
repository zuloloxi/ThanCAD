from __future__ import print_function
from math import pi, fabs
import p_ggen
from p_ggeod import Egsa87, Htrs07
from p_ggeod.mercator import Egsa87old, Htrs07old
#e87n = Egsa87()
#egsa87 = Egsa87old()
e87n = Htrs07()
egsa87 = Htrs07old()

def testEgsa87ngeodetGRS802en():
    for lam in p_ggen.frange(19.0, 29.0,  0.02):
        lam *= pi/180.0
        for phi in p_ggen.frange(34.0, 42.0, 0.02):
            phi *= pi/180.0
            x, y = egsa87.geodetGRS802en(lam, phi)
            xn, yn = e87n.geodetGRS802en(lam, phi)
            if fabs(x-xn) < 0.0001 and fabs(y-yn) < 0.0001: continue
            print(x, y)
            print(xn, yn)


def testen2geodetGRS80():
    for x in p_ggen.frange(100000.0, 900000.0,  1000.0):
        for y in p_ggen.frange(3800000.0, 4800000.0, 1000.0):
            lam, phi = egsa87.en2geodetGRS80(x, y)
            lam *= 180.0/pi
            phi *= 180.0/pi
            lamn, phin = e87n.en2geodetGRS80(x, y)
            lamn *= 180.0/pi
            phin *= 180.0/pi
            if fabs(lam-lamn) < 0.0001 and fabs(phi-phin) < 0.0001: continue
            print(lam, phi)
            print(lamn, phin)


def testen2geocenGRS80():
    xtmin = ytmin = ztmin = 1e100
    xtmax = ytmax = ztmax = -xtmin
    for x in p_ggen.frange(100000.0, 900000.0,  1000.0):
        for y in p_ggen.frange(3800000.0, 4800000.0, 1000.0):
            xt, yt, zt = egsa87.en2geocenGRS80(x, y, 133.33, 39.9)
            xtmin = min(xt, xtmin)
            ytmin = min(yt, ytmin)
            ztmin = min(zt, ztmin)
            xtmax = max(xt, xtmax)
            ytmax = max(yt, ytmax)
            ztmax = max(zt, ztmax)
            xtn, ytn, ztn = e87n.en2geocenGRS80(x, y, 133.33, 39.9)
            if fabs(xt-xtn) < 0.0001 and fabs(yt-ytn) < 0.0001 and fabs(zt-ztn) < 0.0001: continue
            print(xt, yt, zt)
            print(xtn, ytn, ztn)
    print("minmax:")
    print(xtmin, xtmax)
    print(ytmin, ytmax)
    print(ztmin, ztmax)


def testgeocenGRS802en():
    import random
    r = random.Random()
    xtmin, xtmax = 4073662.63142, 4969245.01726
    ytmin, ytmax = 1520951.90211, 2504446.99365
    ztmin, ztmax = 3571051.29049, 4355726.39987
    for xt in p_ggen.frange(xtmin, xtmax, (xtmax-xtmin)/200.0):
        for yt in p_ggen.frange(ytmin, ytmax, (ytmax-ytmin)/200.0):
            zt = r.uniform(ztmin, ztmax)
            x, y, h = egsa87.geocenGRS802en(xt, yt, zt, 39.9)
            xn, yn, hn = e87n.geocenGRS802en(xt, yt, zt, 39.9)
            if fabs(x-xn) < 0.0001 and fabs(y-yn) < 0.0001 and fabs(h-hn) < 0.0001: continue
            print(x, y, h)
            print(xn, yn, hn)


def testgeocenGRS802det():
    import random
    r = random.Random()
    xtmin, xtmax = 4073662.63142, 4969245.01726
    ytmin, ytmax = 1520951.90211, 2504446.99365
    ztmin, ztmax = 3571051.29049, 4355726.39987
    for xt in p_ggen.frange(xtmin, xtmax, (xtmax-xtmin)/200.0):
        for yt in p_ggen.frange(ytmin, ytmax, (ytmax-ytmin)/200.0):
            zt = r.uniform(ztmin, ztmax)
            lam, phi, h = egsa87.geocenGRS802det(xt, yt, zt, 39.9)
            lam *= 180.0/pi
            phi *= 180.0/pi
            lamn, phin, hn = e87n.geocenGRS802det(xt, yt, zt, 39.9)
            lamn *= 180.0/pi
            phin *= 180.0/pi
            if fabs(lam-lamn) < 0.000001 and fabs(phi-phin) < 0.000001 and fabs(h-hn) < 0.000001: continue
            print(x, y, h)
            print(xn, yn, hn)



def testgeodet2cenGRS80():
    for lam in p_ggen.frange(19.0, 29.0,  0.005):
        lam *= pi/180.0
        for phi in p_ggen.frange(34.0, 42.0, 0.005):
            phi *= pi/180.0
            xt, yt, zt = egsa87.geodet2cenGRS80(lam, phi, 99.0, 39.9)
            xtn, ytn, ztn = e87n.geodet2cenGRS80(lam, phi, 99.0, 39.9)
            if fabs(xt-xtn) < 0.0001 and fabs(yt-ytn) < 0.0001 and fabs(zt-ztn) < 0.0001: continue
            print(xt, yt, zt)
            print(xtn, ytn, ztn)


if __name__ == "__main__":
    #print(1); testEgsa87ngeodetGRS802en()
    #print(2); testen2geodetGRS80()
    #print(3); testen2geocenGRS80()
    #print(4); testgeocenGRS802en()
    #print(5); testgeocenGRS802det()
    print(6); testgeodet2cenGRS80()
