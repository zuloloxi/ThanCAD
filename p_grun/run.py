# -*- coding: iso-8859-7 -*-
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
try: import pexpect
except ImportError: pexpect = None
from p_ggen import togi, path, thanUnicode, Pyos
import p_gtkuti
from winerror import ThanTkWinError


def runExecWin(app, pdir, pexpectline=True, popen=False, shell=False, **kw):
    "Opens a window, runs an executable and redirect the output to this window."
    from p_gfil import Tgui
    out = ThanTkWinError(**kw)
    p_gtkuti.thanGudPosition(out)
    out.thanTkSetFocus()
    try:
        runExec(app, pdir, out, pexpectline, popen)
#    except BaseException as e:
    except BaseException, e:
        dl = "%s '%s'" % (Tgui["Error while executing external program"], app)
        out.thanPrt("\n%s:\n%s" % (dl, e), "can")
        p_gtkuti.thanGudModalMessage(out, "%s.\n." % (dl, Tgui["Details were recorded on output window"]),
                                          "%s %s" % (Tgui["ERROR executing"], thanUnicode(app)))
        out.thanPrt("\n%s\n" % (Tgui["Close this window to finish.."],), "mes")

        out.thanTkSetFocus()
        return False
    out.thanPrt("\n\n%s" % (Tgui["Close this window to finish.."],), "mes")
    return True


def runExec(app, pdir, out, pexpectline=True, popen=False, shell=False):
    "Runs an executable and redirect the output to out window."
    if shell and Pyos.Windows and ";" in app:   #Transform: echo ThanCad;gcc -c x.c to: "echo ThanCad && gcc -c c.c"
        app = app.split(";")
	app = " && ".join(app)
#	app = '"%s"' % (app,)
    pdir = path(pdir)
    cdir = path(os.getcwd())
    try:
        pdir.chdir()
        if pexpect == None or popen:
            _popenrun(app, pdir, out, shell)
        elif pexpectline:
            _pexpectLinerun(app, out)
        else:
            _pexpectCharun(app, out)
#    except BaseException, why:                                  #The exception is propagated to the caller
#        prt = out.thanPrt
#        prt("Error while executing %s:\n%s" % (app, why))
    finally:
        cdir.chdir()


def _pexpectCharun(app, out, timeout=2000):
        "Run the program with pexpect."
#        p1 = pexpect.spawn(app, cwd=pdir)
        p1 = pexpect.spawn(app, timeout=timeout)
        prts = out.thanPrts
        try:
            while True:
                dl = p1.read_nonblocking(1, None)
                prts(togi(dl.rstrip("\r")))
                out.update_idletasks()
        except pexpect.EOF:
            pass


def _pexpectLinerun(app, out, timeout=2000):
        "Run the program with pexpect; a whole line must be submitted by the program in oprder yo be diaplyed in the window."
#        p1 = pexpect.spawn(app, cwd=pdir)
        p1 = pexpect.spawn(app, timeout=timeout)
        prts = out.thanPrts
        while True:
            dl = p1.readline()
            if dl == "": break
            prts(togi(dl.replace("\r", "")))
            out.update_idletasks()


def _popenrun_with_communicate(app, pdir, out):
        "Run the program with popen."
        prt = out.thanPrt
        try:
            prt("executing %s.." % (app,))
            p1 = Popen(app, stdout=PIPE, stderr=STDOUT, cwd=pdir)
        except OSError:
            app1 = path(sys.path[0]).parent /"other" / app
            p1 = Popen(app1, stdout=PIPE, stderr=STDOUT, cwd=pdir)
        out1, out2 = p1.communicate()
        if out1 != None: prt(togi(out1.replace("\r", "")))
        if out2 != None: prt(togi(out2.replace("\r", "")))
        try:
            i = 0
            for dl in open("mediate.tmp"):
                if dl == "***ERROR***":
                    i += 1
                elif i == 1:
                    prt(dl)      # Program name
                elif i >= 3:
                    prt(dl)      # Error message
        except IOError:
            pass


def _popenrun(app, pdir, out, shell=False):
        "Run the program with popen."
        prt = out.thanPrt
        prts = out.thanPrts
        try:
            prt("executing %s.." % (app,))
            p1 = Popen(app, bufsize=0, stdout=PIPE, stderr=STDOUT, cwd=pdir, shell=shell)
        except OSError:
            app1 = path(sys.path[0]).parent /"other" / app
            p1 = Popen(app1, stdout=PIPE, stderr=STDOUT, cwd=pdir)
        while p1.poll() == None:
            dl = p1.stdout.read(4096)
            out.update_idletasks()
            prts(togi(dl.replace("\r", "")))
        try:
            i = 0
            for dl in open("mediate.tmp"):
                if dl == "***ERROR***":
                    i += 1
                elif i == 1:
                    prt(dl)         # Program name
                elif i >= 3:
                    prt(dl)         # Error message
        except IOError:
            pass



def test():
    "Test the library."
    import Tkinter
    root = Tkinter.Tk()
    ok = runExecWin("/home/a12/h/libs/source_python/runlib/dok", pdir=".", pexpectline=True, master=root,
        mes="First line - Πρώτη γραμμή\n", title=u"ThanCad: Δοκιμή του dok")
    root.mainloop()


if __name__ == "__main__":
    test()
