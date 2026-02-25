##############################################################################
# ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2016 Thanasis Stamos, June 19, 2016
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.3.0 "Oberpfaffenhofen": n-dimensional CAD with raster support for engineers

Package which provides for ThanCad and/or ThanCad drawings customisation.
This module provides for ThanCad initialisation.
"""

from __future__ import print_function
import sys                 #Module sys is guaranteed by Python
import p_ggen
from . import thanmenus2

def thanInitTest():
    "Check if necessary modules are installed in Python distribution."
    thanModules = "tkinter tkinter.colorchooser tkinter.font tkinter.messagebox "\
                  "tkinter.simpledialog "\
                  "numpy|Numeric sys bz2 math types copy weakref "\
                  "codecs itertools re base64 random copy "\
                  "collections subprocess ".split()
                   #Image ImageTk
    if p_ggen.Pyos.Python3: thanModules.extend("configparser pickle".split())
    else:                   thanModules.extend("ConfigParser cPickle".split())
    if sys.platform == "win32": thanModules.append("win32com")

    thanModOptional = "webbrowser cups pexpect sane pyx"
    try:   import tkinter
    except ImportError as why: thanShellErr(why, thanModules)

    try: root = tkinter.Tk()
    except tkinter.TclError as why: thanShellErr(why, thanModules)

    for mod1 in thanModules:
        for mod2 in mod1.split("|"):
            print("ThanInitTest():", mod2)
            try: __import__(mod2)
            except ImportError as why: why1 = why    #Work around python3.4.1 curious bug
            else: break
            thanTkErr(mod1, why1, thanModules, root)
    root.destroy()
    print("thanInitTest(): encoding=", p_ggen.thanGetEncoding())


def thanShellErr(why, thanModules):
    "Report errors to shell."
    prt = sys.stderr.write
    prt("\n")
    prt("THANCAD FATAL ERROR: tkinter GUI CAN NOT BE LOADED:\n")
    prt("    %s\n\n" % why)
    prt("ThanCad also needs the following standard modules:\n")
    for mod1 in thanModules: prt("%s\n" %  mod1)
    prt("\nThanCad will now be terminated.\n")
    sys.exit(1)


def thanTkErr(mod1, why, thanModules, root):
    "Report errors to a Tk window."
    import tkinter
    root.geometry("%+d%+d" % (50, 50))
    root.option_add("*Font", "14")
    root.title("THANCAD FATAL ERROR")

    dl = "Module %s can not be loaded:\n    %s" % (mod1, why)
    lab = tkinter.Label(root, text=dl, justify=tkinter.LEFT, anchor="w", bg="red", fg="yellow",
        relief=tkinter.RIDGE, bd=3)
    lab.grid(sticky="we", padx=3)

    dl = ["ThanCad also needs the following standard modules:"]
    for mod1 in thanModules: dl.append("%s" %  mod1)
    lab = tkinter.Label(root, text="\n".join(dl), justify=tkinter.LEFT, anchor="w", fg="blue",
        relief=tkinter.RIDGE, bd=3)
    lab.grid(sticky="we", pady=5, padx=3)

    lab = tkinter.Label(root, text="ThanCad will be terminated", justify=tkinter.LEFT, anchor="w", fg="red",
        relief=tkinter.RIDGE, bd=3)
    lab.grid(sticky="we", pady=5, padx=3)

    root.mainloop()
    sys.exit(1)


def thanInitPregui():
    "Initial values before the gui instantiation."
    from . import thancadconf
    thancadconf.thanOptsGet()
    import thandefs
    import thantrans
    thantrans.thanLangSetall()         #Set default language as is thancadconf (or in thancadconf.thanOptsGet())
    import thanlayer
    import thandr
    thantrans.thanLangMore()        #Add more translations
    thantrans.thanLangSetall()         #Set default language to all (and the new) translations
    import thancom
    thanmenus2.thanCreateMenus()    #Create the menus with the established translations
    thanLoadPackages()



def thanLoadPackages():
    "Load ThanCad packages (plugins)."
    import thanpackages2, thancom
    thanPackagesLoaded = []
    for pn in thanpackages2.__all__:
        p = getattr(thanpackages2, pn)
        try:
            p.thanRegisterCommands
            p.thanRegisterMenus
            p.thanRegisterTrans
        except AttributeError as why:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue
        try:
            coms, abbrevs = p.thanRegisterCommands()
            seq, m = p.thanRegisterMenus()
            trans = p.thanRegisterTrans()
        except BaseException as why:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue
        try:
            thancom.thanAddCommands(coms, abbrevs)
            thanmenus2.thanAddMenus(seq, m)
        except BaseException as why:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue
        thanPackagesLoaded.append(p)
    for p in thanPackagesLoaded:
        try:
            p.thanRegisterAfter
        except AttributeError:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue
        try:
            p.thanRegisterAfter()
        except BaseException as why:
            print("Error while loading package %s: %s" % (p.__name__, why))
            continue


def thanInitPostgui():
    "Initial values just after the gui instantiation."
    pass


def thanInitEndgui():
    "Final values just after the gui shutdown."
    from . import thancadconf
    thancadconf.thanOptsSave()

thanInitTest()
