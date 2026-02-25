##############################################################################
# ThanCad 0.1.2 "Free": 2dimensional CAD with raster support for engineers.
#
# Copyright (c) 2001-2010 Thanasis Stamos,  December 23, 2010
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (www.gnu.org/licenses/gpl.html).
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################

"""\
ThanCad 0.1.2 "Free": 2dimensional CAD with raster support for engineers.

This package includes dialogs (forms to get user input) implemented with Tkinter.
This module tries to run an external program with pexpect in order to print
the output of the program immediatly to the output window. If pexpect is not
found, it uses Popen.
"""

import os, sys
from subprocess import Popen, PIPE, STDOUT
from threading import Timer
try: import pexpect
except ImportError: pexpect = None
from p_ggen import togi, path, thanUnicode, Pyos, Tgui, isString, thanGetEncoding
import p_gtkwid
from .winerror import ThanTkWinError, ThanShellError


def runExecWin(app, pdir, pexpectline=True, popen=False, shell=False, env=None, timeout=2000, **kw):
    "Opens a window, runs an executable and redirect the output to this window."
    out = ThanTkWinError(**kw)
    p_gtkwid.thanGudPosition(out)
    out.thanTkSetFocus()
    try:
        runExec(app, pdir, out, pexpectline, popen, shell, env, timeout)
    except BaseException as e:
        dl = "%s '%s'" % (Tgui["Error while executing external program"], app)
        out.thanPrt("\n%s:\n%s" % (dl, e), "can")
        p_gtkwid.thanGudModalMessage(out, "%s.\n%s." % (dl, Tgui["Details were recorded on output window"]),
                                          "%s %s" % (Tgui["ERROR executing"], thanUnicode(app)))
        out.thanPrt("\n%s\n" % (Tgui["Close this window to finish.."],), "mes")

        out.thanTkSetFocus()
        return False
    out.thanPrt("\n\n%s" % (Tgui["Close this window to finish.."],), "mes")
    return True


def runExec(app, pdir, out, pexpectline=True, popen=False, shell=False, env=None, timeout=2000):
    "Runs an executable and redirect the output to out window."
    if shell and Pyos.Windows and ";" in app:   #Transform: echo ThanCad;gcc -c x.c to: "echo ThanCad && gcc -c c.c"
        app = app.split(";")
        app = " && ".join(app)
#       app = '"%s"' % (app,)
    pdir = path(pdir)
    cdir = path(os.getcwd())
    try:
        pdir.chdir()
        if pexpect is None or popen or shell:
            _popenrun(app, pdir, out, shell, env, timeout)
            #_popenrun_with_communicate(app, pdir, out, shell, env, timeout)
        elif pexpectline:
            _pexpectLinerun(app, out, env, timeout)
        else:
            _pexpectCharun(app, out, env, timeout)
#    except BaseException, why:                                  #The exception is propagated to the caller
#        prt = out.thanPrt
#        prt("Error while executing %s:\n%s" % (app, why))
    finally:
        cdir.chdir()


def _pexpectCharun(app, out, env=None, timeout=2000):
        "Run the program with pexpect."
#        p1 = pexpect.spawn(app, cwd=pdir)
        if not isString(app): app = " ".join(app)
        p1 = pexpect.spawn(app, timeout=timeout, env=_envmerge(env))
        prts = out.thanPrts
        try:
            while True:
                dl = p1.read_nonblocking(1, None)
                prts(togi(dl.rstrip("\r")))
                out.update_idletasks()
        except pexpect.EOF:
            pass


def _pexpectLinerun(app, out, env=None, timeout=2000):
        "Run the program with pexpect; a whole line must be submitted by the program in oprder to be displayed in the window."
#        p1 = pexpect.spawn(app, cwd=pdir)
        if not isString(app): app = " ".join(app)
        p1 = pexpect.spawn(app, timeout=timeout, env=_envmerge(env))
        prts = out.thanPrts
        while True:
            dl = p1.readline()
            if isinstance(dl, bytes):
                dl = dl.decode(encoding=thanGetEncoding(), errors="surrogatereplace")  #For ubuntu (or raspberry pi?)
            if dl == "": break
            prts(togi(dl.replace("\r", "")))
            out.update_idletasks()


def _popenrun_with_communicate(app, pdir, out, shell=False, env=None, timeout=2000):
        "Run the program with popen."
        prt = out.thanPrt
        try:
            prt("executing %s.." % (app,))
            p1 = Popen(app, stdout=PIPE, stderr=STDOUT, cwd=pdir, shell=shell, env=_envmerge(env))
        except OSError:
            app1 = path(sys.path[0]).parent /"other" / app
            p1 = Popen(app1, stdout=PIPE, stderr=STDOUT, cwd=pdir, shell=shell, env=_envmerge(env))
        out1, out2 = p1.communicate(timeout=timeout)
        if out1 is not None: prt(togi(out1.replace("\r", "")))
        if out2 is not None: prt(togi(out2.replace("\r", "")))
        try:
            i = 0
            for dl in open("mediate.tmp", encoding=thanGetEncoding(), errors="surrogatereplace"):
                if dl == "***ERROR***":
                    i += 1
                elif i == 1:
                    prt(dl)      # Program name
                elif i >= 3:
                    prt(dl)      # Error message
        except IOError:
            pass


def _popenrun(app, pdir, out, shell=False, env=None, timeout=2000):
    "Run the program with popen."
    prt = out.thanPrt
    prts = out.thanPrts
    try:
        prt("executing %s.." % (app,))
        p1 = Popen(app, bufsize=-1, stdout=PIPE, stderr=STDOUT, cwd=pdir, shell=shell, env=_envmerge(env))
    except OSError:
        if isString(app):
            app1 = path(sys.path[0]).parent /"other" / app
        else:
            app1 = list(app)
            app1[0] = path(sys.path[0]).parent /"other" / app[0]
        p1 = Popen(app1, bufsize=-1, stdout=PIPE, stderr=STDOUT, cwd=pdir, shell=shell, env=_envmerge(env))

    #https://stackoverflow.com/questions/1191374/using-module-subprocess-with-timeout
    timer = Timer(timeout, p1.kill)
    timer.start()
    try:
        while True:
            #print("p_grun:_popenrun():shell=", shell)
            #print("p_grun:_popenrun():", p1.poll())
            dl = p1.stdout.read(4096)
            #print("p_grun:_popenrun():", dl, p1.poll())
            if dl==b"" and p1.poll() is not None: break
            if Pyos.Python3: dl = thanUnicode(dl)
            out.update_idletasks()
            prts(togi(dl.replace("\r", "")))
    finally:
        timer.cancel()

    try:
        i = 0
        for dl in open(pdir/"mediate.tmp", encoding=thanGetEncoding(), errors="surrogatereplace"):
            if dl == "***ERROR***":
                i += 1
            elif i == 1:
                prt(dl)         # Program name
            elif i >= 3:
                prt(dl)         # Error message
    except IOError:
        pass


def runCompileScript(script, dir1=".", out=None, env=None, timeout=2000):
        "Runs a Thanasis' compile script."
#        if out is None:
#            winmain, _, _ = p_gfil.openfileWinget()
#            out = ThanShellError() if winmain is None else winmain
        if out is None: out = ThanShellError()
        prt = out.thanPrt
        if script is None:
            prt("******Warning: no compile script found!", "can1")
            return False
        if Pyos.Openbsd:       coms = "ksh " +script      #We use ksh  because the script may not have the execution attribute set
        elif not Pyos.Windows: coms = "bash "+script      #We use bash because the script may not have the execution attribute set
        elif script[1] == "b": coms = "e fb;"+script
        elif Pyos.Amd64:       coms = "e g64;"+script
        elif script[1] == "f": coms = "e g77;"+script
        else:                  coms = "e gcc;"+script

        try:
            if script[1] == "b": runExec(coms, dir1, out, popen=True, shell=True, env=env, timeout=timeout)
            else:                runExec(coms, dir1, out, pexpectline=True, shell=True, env=env, timeout=timeout)
        except Exception as e:
            prt("******Error while running %s:\n******%s" % (script, e), "can1")
            return False
        return True


def _envmerge(env):
    "Add environmental variables in env to the environment given to the child process."
    if env is None:
        env1 = os.environ
    else:
        env1 = os.environ.copy()
        env1.update(env)
    return env1


def test():
    "Test the library."
    import tkinter
    root = tkinter.Tk()
    ok = runExecWin("/home/a12/h/libs/source_python/p_grun/dok", pdir=".", pexpectline=True, master=root,
        mes="First line - Πρώτη γραμμή\n", title=u"ThanCad: Δοκιμή του dok")
    root.mainloop()


if __name__ == "__main__":
    test()
