from p_gcomp import cpygen
libname = "p_gtkwid"
libfiles = """thanwids.py thandraw.py thantkclist.py thantkcli.py thanval.py
              thancomdialog.py thandataform.py thanwincom.py progresswin.py
              thanicon.py thanfiles.py thanwidstrans.py
              __init__.py
             thantkutila.py thantkutilb.py thantksimpledialog.py xinp.py thansched.py
             thanfontresize.py helpwin.py poplistdialog.py
           """
if __name__ == "__main__": cpygen.createlib(libname, libfiles)
