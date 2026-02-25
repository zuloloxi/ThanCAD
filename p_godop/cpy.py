from p_gcomp import cpygen
libname = "p_godop"
libfiles = """forw.py __init__.py
           """
if __name__ == "__main__": cpygen.createlib(libname, libfiles)
