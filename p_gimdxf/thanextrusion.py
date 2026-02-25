from math import atan2, cos, sin, pi
from p_gmath import thanThresholdx
from p_gvec import Vector3


def thanDxfExtrusionVectorsold(az):
    """Rotate world coordinate system so that the new z is the vector az (given as tuple).

    The new (local) system has the mentioned az axis. The new y-axis is weird:
    The az vector is projected to the world-xy plane. Then the
    component of the projection that is normal to new z-axis (az) is taken.
    This is the direction of the new y-axis!
    The x-axis is the vector product of new y by new z.
    The given az need not be unit vector.
    The unit vectors of the new (local) system are returned, expressed in the
    world coordinate system.

    This routine is needed for dxf deciphering. It seems that any(?) object
    in a .dxf file (even version 12) may have an "extrusion" vector, which is
    the direction of the element thickness (if there is one). The components of
    the extrusion vector are given as code 210, 220, 230.
    The weird thing is that, if an
    extrusion vector is defined, then the coordinates of the object are given
    in the new (local) system!...
    But the extrusion vector is given in the world coordinate system!

    In order to be able to compute the world coordinates, the unit vectors
    of the world coordinate system (expressed in the local coordinate system),
    are also returned.

    If the az vector (given as a tuple) is the world z axis,
    the unit vectors of the world coordinate system are returned,
    which means that the local and the world coordinate systems coincide.

    A final note is that the extrusion vector is supposed to be perpendicular
    to the plane the object lies (which also means that the object is
    2dimensional). However, I found some Lisp code in the internet where
    the author actually checked if the extrusion vector is perpendicular;
    and if it was not, (s)he took the component which was normal to the object.
    I have to find that Lisp code again to see what it means for various
    objects.
    Thanasis Stamos May 11, 2009.
    """
    x = Vector3(1.0, 0.0, 0.0)
    y = Vector3(0.0, 1.0, 0.0)
    z = Vector3(0.0, 0.0, 1.0)
    vzr = Vector3(az[0], az[1], az[2])
    vyr = -(vzr-z)
    vyr = vyr - (vzr*vyr)*vzr
    a = abs(vyr)
    if a < thanThresholdx:
        return (tuple(x), tuple(y), tuple(z)) * 2   # Identity transformation
    vyr /= a
    vxr = vyr.cross(vzr)
    wx = (x*vxr, x*vyr, x*vzr)
    wy = (y*vxr, y*vyr, y*vzr)
    wz = (z*vxr, z*vyr, z*vzr)
    return tuple(vxr), tuple(vyr), tuple(vzr), wx, wy, wz



def thanDxfExtrusionVectors(az):
    "New code to be consistent with the description above."
    x = Vector3(1.0, 0.0, 0.0)
    y = Vector3(0.0, 1.0, 0.0)
    z = Vector3(0.0, 0.0, 1.0)
    vzr = Vector3(az[0], az[1], az[2]).unit()     #2011_04_03thanasis:added .unit()
    vyr = vzr - (z|vzr)*z                         #Projection of vzr to the xy plane
    vyr = vyr - (vzr|vyr)*vzr                     #Component of the projection normal to vzr
    vyr = -vyr                                    #It seems that it is on the other direction
    a = abs(vyr)
    if a < thanThresholdx:
        return (tuple(x), tuple(y), tuple(z)) * 2   # Identity transformation
    vyr /= a
    vxr = vyr.cross(vzr)
    wx = (x|vxr, x|vyr, x|vzr)
    wy = (y|vxr, y|vyr, y|vzr)
    wz = (z|vxr, z|vyr, z|vzr)
    return tuple(vxr), tuple(vyr), tuple(vzr), wx, wy, wz


def thanDxfExtrusion2World(wx, wy, wz, xx, yy, zz):
    "Transform local coordinates (extrusion system) to world coordinates."
    for i in range(len(xx)):
        x1 = xx[i]
        y1 = yy[i]
        z1 = zz[i]
        xx[i] = x1*wx[0]+y1*wx[1]+z1*wx[2]
        yy[i] = x1*wy[0]+y1*wy[1]+z1*wy[2]
        zz[i] = x1*wz[0]+y1*wz[1]+z1*wz[2]


def test():
    "Test world to local and local to wrold transformations."
    az = -0.037655365879107, -0.0359414884998473, 0.9986442223459393
    datalocal = """\
THC0000001        -26.239         20.132         -1.401
THC0000002        -26.742         20.063         -1.401
THC0000003        -27.484         20.097         -1.401
THC0000004        -28.104         20.198         -1.401
THC0000005        -28.489         20.352         -1.401"""
    dataworld = """\
  -3.5204    32.9121    -0.3513
  -3.9175    33.2290    -0.3549
  -4.4055    33.7886    -0.3532
  -4.7608    34.3068    -0.3479
  -4.9154    34.6915    -0.3399"""
    ccw = []
    for dline in dataworld.split("\n"):
        ccw.append( list( map(float, dline.split()[0:]) ) )
    ccl = []
    for dline in datalocal.split("\n"):
        ccl.append( list( map(float, dline.split()[1:]) ) )

    testaz(az, ccw, ccl)
    print()
    print("-----------------------------------------------------------------")
    print("Test of extrusion vector equals to the wolrd z-axis")
    az = 0.0, 0.0, 1.0
    testaz(az, ccw, ccl)


def testazold(az, ccw, ccl):
    "Tests the extrusion transformation with given data."
    vx, vy, vz, wx, wy, wz = thanDxfExtrusionVectors(az)
    print("system world to local=")
    print(vx)
    print(vy)
    print(vz)
    vxyz = (vx, vy, vz)
    form = "%12.3f%12.3f%12.3f -> %12.3f%12.3f%12.3f"
    for x, y, z in ccw:
        c = [x*v[0]+y*v[1]+z*v[2] for v in vxyz]
        print(form % ((x, y, z)+tuple(c)))

    print()
    print("system local to world=")
    print(wx)
    print(wy)
    print(wz)
    wxyz = (wx, wy, wz)
    for x, y, z in ccl:
        c = [x*v[0]+y*v[1]+z*v[2] for v in wxyz]
        print(form % ((x, y, z)+tuple(c)))


def testaz(az, ccw, ccl):
    "Tests the extrusion transformation with given data."
    vx, vy, vz, wx, wy, wz = thanDxfExtrusionVectors(az)
    print("system world to local=")
    print(vx)
    print(vy)
    print(vz)
    vxyz = (vx, vy, vz)
    form = "%12.3f%12.3f%12.3f -> %12.3f%12.3f%12.3f"
    for x, y, z in ccw:
        c = [x*v[0]+y*v[1]+z*v[2] for v in vxyz]
        print(form % ((x, y, z)+tuple(c)))

    print()
    print("system local to world=")
    print(wx)
    print(wy)
    print(wz)
    xx = [c[0] for c in ccl]
    yy = [c[1] for c in ccl]
    zz = [c[2] for c in ccl]
    thanDxfExtrusion2World(wx, wy, wz, xx, yy, zz)
    for i in range(len(ccl)):
        x, y, z = ccl[i]
        print(form % (x, y, z, xx[i], yy[i], zz[i]))



if __name__ == "__main__": test()
