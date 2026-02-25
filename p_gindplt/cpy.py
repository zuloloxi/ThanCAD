from p_gcomp import cpygen
libname = "p_gindplt"
libfiles = """inddra.py plotdashdot.py linehatch.py axis.py indfil.py stairs.py 
              regularpolygon.py bintree.py __init__.py
           """
if __name__ == "__main__": cpygen.createlib(libname, libfiles)
