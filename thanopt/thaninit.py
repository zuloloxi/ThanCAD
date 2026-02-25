##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

Package which provides for ThanCad and/or ThanCad drawings customisation.
This module provides for ThanCad initialisation.
"""

import sys                 #Module sys is guaranteed by Python

def thanInitTest():
    "Check if necessary modules are installed in Python distribution."
    thanModules = "Tkinter tkColorChooser tkFont tkMessageBox tkSimpleDialog "\
                  "Image ImageTk numpy|Numeric sys bz2 math types copy weakref "\
                  "codecs itertools ConfigParser re base64 random copy cPickle "\
                  "collections subprocess ".split()
    if sys.platform == "win32": thanModules.append("win32com")

    thanModOptional = "webbrowser cups pexpect sane pyx"
    try:   import Tkinter
    except ImportError, why: thanShellErr(why, thanModules)

    try: root = Tkinter.Tk()
    except Tkinter.TclError, why: thanShellErr(why, thanModules)

    for mod1 in thanModules:
        for mod2 in mod1.split("|"):
            try: __import__(mod2)
            except ImportError, why: pass
            else: break
            thanTkErr(mod1, why, thanModules, root)
    root.destroy()


def thanShellErr(why, thanModules):
    "Report errors to shell."
    prt = sys.stderr.write
    prt("\n")
    prt("THANCAD FATAL ERROR: TKINTER GUI CAN NOT BE LOADED:\n")
    prt("    %s\n\n" % why)
    prt("ThanCad also needs the following standard modules:\n")
    for mod1 in thanModules: prt("%s\n" %  mod1)
    prt("\nThanCad will now be terminated.\n")
    sys.exit(1)


def thanTkErr(mod1, why, thanModules, root):
    "Report errors to a Tk window."
    import Tkinter
    root.geometry("%+d%+d" % (50, 50))
    root.option_add("*Font", "14")
    root.title("THANCAD FATAL ERROR")

    dl = "Module %s can not be loaded:\n    %s" % (mod1, why)
    lab = Tkinter.Label(root, text=dl, justify=Tkinter.LEFT, anchor="w", bg="red", fg="yellow",
        relief=Tkinter.RIDGE, bd=3)
    lab.grid(sticky="we", padx=3)

    dl = ["ThanCad also needs the following standard modules:"]
    for mod1 in thanModules: dl.append("%s" %  mod1)
    lab = Tkinter.Label(root, text="\n".join(dl), justify=Tkinter.LEFT, anchor="w", fg="blue",
        relief=Tkinter.RIDGE, bd=3)
    lab.grid(sticky="we", pady=5, padx=3)

    lab = Tkinter.Label(root, text="ThanCad will be terminated", justify=Tkinter.LEFT, anchor="w", fg="red",
        relief=Tkinter.RIDGE, bd=3)
    lab.grid(sticky="we", pady=5, padx=3)

    root.mainloop()
    sys.exit(1)


def thanInitPregui():
    "Initial values before the gui instantiation."
    import thancadconf
    thancadconf.thanOptsGet()

def thanInitPostgui():
    "Initial values just after the gui instantiation."
    pass

def thanInitEndgui():
    "Final values just afte the gui shutdown."
    import thancadconf
    thancadconf.thanOptsSave()

thanInitTest()
