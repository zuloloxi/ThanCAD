from math import fabs
import p_ggen

def decipherErdasAscDem(fr, prt=p_ggen.prg):
    "Find X0, Y0 of upper left corner, DX, DY and ... of Erdas DEM saved in acsii."
    npoints = -1
    try:
        #Read first point
        it = iter(fr)
        iline = 0
        for dline in it:
            iline += 1
            if iline == 1 and b"//" in dline: continue    #ERDAS ascii may have //X Y Z on the first line
            dl = dline.split()
            if iline == 2 and len(dl) == 1:              #ERDAS ascii may have the number or points on the second linbe
                npoints = float(dl[0])
                continue
            x0,y0,z = map(float, dl)
            break
        else:
            return False, "Error at line %d of ascii Erdas DEM:\nToo few points" % (iline+1,)

        #Read second point
        for dline in it:
            iline += 1
            x1,y1,z = map(float, dline.split())
            break
        else:
            return False, "Error at line %d of ascii Erdas DEM:\nToo few points" % (iline+1,)

        DX = x1 - x0
        if DX <= 0.0:
            return False, "Error at line %d of ascii Erdas DEM:\nx coordinates should be in increasing order" % (iline,)
        if fabs(y1-y0) > DX*0.001:
            return False, "Error at line %d of ascii Erdas DEM:\ny coordinate should not differ from previous" % (iline,)

        #Read until end of first row
        ncols = 2
        for dline in it:
            iline += 1
            x2,y2,z = map(float, dline.split())
            dx2 = x2-x1
            dy2 = y2 - y1
            x1, y1 = x2, y2
            if fabs(dy2) > DX*0.001: break
            if fabs(DX-dx2) > DX*0.001:
                return False, "Error at line %d of ascii Erdas DEM:\nx coordinate should differ %f from previous" % (iline, DX)
            ncols += 1
        else:
            return False, "Error at line %d of ascii Erdas DEM:\nToo few points" % (iline+1,)

        DY = y0 - y2
        if DY <= 0.0:
            return False, "Error at line %d of ascii Erdas DEM:\ny coordinates should be in decreasing order" % (iline,)
        if fabs(x2-x0) > DX*0.001:
            print("**tra01")
            return False, "Error at line %d of ascii Erdas DEM:\nEvery row should begin at the same x=%f" % (iline, x0)

        nrows = 1
        ncols2 = 1
        for dline in it:
            iline += 1
            x2,y2,z = map(float, dline.split())
            #print "y1=", y1, "   y2=", y2
            if fabs(y2-y1) > DY*0.001:
                dy2 = y1 - y2
                if fabs(DY-dy2) > DY*0.001:
                    return False, "Error at line %d of ascii Erdas DEM:\ny coordinate should differ %f from previous" % (iline, DY)
                #print "**tra02"
                if fabs(x2-x0) > DX*0.001:
                    print('x2=', x2)
                    print('x0=', x0)
                    return False, "Error at line %d of ascii Erdas DEM:\nEvery row should begin at the same x=%f" % (iline, x0)
                if ncols2 != ncols:
                    return False, "Error at line %d of ascii Erdas DEM:\nEvery row should have the same number of columns %d" % (iline, ncols)
                ncols2 = 1
                nrows += 1
            else:
                dx2 = x2-x1
                if fabs(DX-dx2) > DX*0.001:
                    return False, "Error at line %d of ascii Erdas DEM:\nx coordinate should differ %f from previous" % (iline, DX)
                ncols2 += 1
            x1, y1 = x2, y2
        if ncols2 != ncols:
            return False, "Error at line %d of ascii Erdas DEM:\nLast row should have the same number of columns %d" % (iline, ncols)
    except (ValueError, IndexError) as e:
        return False, "Syntax error at line %d of ascii Erdas DEM:\n%s" % (iline+1, dline.rstrip())
    GDAL_NODATA = -999999.0              #Special pixel value that means that the pixel has unknown elevation
    if npoints != -1 and npoints != ncols*nrows:
        prt("Warning: The DEM ascii file claims to have %d points, but %d points were found." % (npoints, ncols*nrows), "can1")

    return True, (x0, y0, DX, DY, ncols, nrows, GDAL_NODATA)
