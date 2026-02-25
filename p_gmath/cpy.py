from p_gcomp import cpygen
libname = "p_gmath"
libfiles = """ __init__.py var.py thanintersect.py func.py chebev.py lagrange.py
              triginterp.py varcon.py spl.py
              proj.py projcom.py projutil.py coor.py lineq.py ellipse.py
              circle.py similar.py pp.py histo.py integration.py statis.py rotator.py
              decimal.py
           """
if __name__ == "__main__": cpygen.createlib(libname, libfiles)
