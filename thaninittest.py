##############################################################################
# ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2025 Thanasis Stamos, May 20, 2025
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
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
ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers

Package thancad.
This module tests that the essential libraries needed by ThanCad are installed.
"""

import sys
import p_ggen

def thanInitTest():
    "Check if necessary modules are installed in Python distribution."
    thanModules = "tkinter tkinter.colorchooser tkinter.font tkinter.messagebox "\
                  "tkinter.simpledialog "\
                  "numpy|Numeric "\
                  "PIL "\
                  "base64 bisect bz2 codecs collections configparser|ConfigParser "\
                  "copy ctypes csv datetime enum fnmatch functools glob importlib "\
                  "io itertools logging math operator os "\
                  "pickle|cPickle platform random re shutil struct subprocess sys "\
                  "tempfile time types "\
                  "typing unicodedata weakref webbrowser "\
                  "xml.etree.ElementTree zipfile "\
                  "".split()
                   #Image ImageTk
    if p_ggen.Pyos.Python3: thanModules.extend("configparser pickle".split())
    else:                   thanModules.extend("ConfigParser cPickle".split())
    if sys.platform == "win32": thanModules.append("win32com")

    thanModOptional = "PIL cups pyx xlrd xlwt openpyxl webbrowser pexpect sane"\
        "osgeo.gdal, osgeo.gdalconst, osgeo.gdal_array"
    try:   import _tkinter, tkinter  #Sometimes tkinter does not report error if there is one, but _tkinter does.
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
