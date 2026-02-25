import p_ggen
from . import opgui
def wa1(mes, tags="can1"):
        "Print a warning message."
        winmain, prt, _ = opgui.openfileWinget()
        if winmain is None: prt = p_ggen.prg
        prt("%s" % (mes,), tags)


def er1s(mes, tags="can"):
        "Prints an error message and stops."
        from . import openfile
        winmain, prt, _ = opgui.openfileWinget()
        if winmain is None: prt = p_ggen.prg
        prt("%s" % (mes,), tags)
        openfile.stopErr1()
