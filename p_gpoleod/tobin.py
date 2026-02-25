from p_gcomp import bingen
libname  = "p_gpoleod"
libfiles = """roadut.py roadem.py hippocache.py hippo.py hippoanneal.py simpol.py __init__.py
            """
bingen.createLib(libname, libfiles)
