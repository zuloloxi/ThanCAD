import p_gfil, p_grun
from p_ggen import Pyos


def runCompileScript(script, dir1=".", out=None):
        "Runs a Thanasis' compile script."
        if script == None: return False  #Script not found
        if Pyos.Openbsd:       coms = "ksh " +script      #We use ksh  because the script may not have the execution attribute set
        elif not Pyos.Windows: coms = "bash "+script      #We use bash because the script may not have the execution attribute set
        elif script[1] == "b": coms = "e fb;"+script
        elif Pyos.Amd64:       coms = "e g64;"+script
        elif script[1] == "f": coms = "e g77;"+script
        else:                  coms = "e gcc;"+script

        if out == None:
            winmain, _, _ = p_gfil.openfileWinget()
            out = p_grun.ThanShellError() if winmain == None else winmain
        try:
            if script[1] == "b": p_grun.runExec(coms, dir1, out, popen=True, shell=True)
            else:                p_grun.runExec(coms, dir1, out, pexpectline=True, shell=True)
        except Exception, e:
            prg("******Error while running %s:\n******%s" % (script, e), "can1")
            return False
        return True
