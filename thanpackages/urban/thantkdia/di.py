# -*- coding: iso-8859-7 -*-
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

The package provides tools and automation for urban analysis/design.
The subpackage contains dialogss which handle urban related procedures.
This module defines dialog for land use.
"""
import tkinter
import p_gtkwid
import urbantrans
Twid = p_gtkwid.Twid
T = urbantrans.Turban

roadW = 10.00
pavLeftW = 1.20
pavRightW = 1.00
medW = 0.0
valuesOk = False

top = None
entRoadW = None
entPavLeftW = None
entPavRightW = None
entMedW = None


def test():
    "Test the dialog."
    root = tkinter.Tk()
    makeWidgets(root)
    setWidgets()
    root.wait_window(top)
    print valuesOk
    T.thanReport()


def makeWidgets(root):
    "Make the widgets of the dialog."
    global top, entRoadW, entPavLeftW, entPavRightW, entMedW
    top = tkinter.Toplevel(root)
    lab = tkinter.Label(top, text=T["Road width (m)"])
    lab.grid(row=0, column=0, sticky="e")
    entRoadW = p_gtkwid.ThanEntry(top)
    entRoadW.grid(row=0, column=1, sticky="w")
    lab = tkinter.Label(top, text=T["Left Pavement width (m)"])
    lab.grid(row=1, column=0, sticky="e")
    entPavLeftW = p_gtkwid.ThanEntry(top)
    entPavLeftW.grid(row=1, column=1, sticky="w")
    lab = tkinter.Label(top, text=T["Right Pavement width (m)"])
    lab.grid(row=2, column=0, sticky="e")
    entPavRightW = p_gtkwid.ThanEntry(top)
    entPavRightW.grid(row=2, column=1, sticky="w")
    lab = tkinter.Label(top, text=T["Median strip width (m)"])
    lab.grid(row=3, column=0, sticky="e")
    entMedW = p_gtkwid.ThanEntry(top)
    entMedW.grid(row=3, column=1, sticky="w")
    but = p_gtkwid.Button(top, text=Twid["OK"], command=pressedOk, bg="lightcyan", activebackground="cyan")
    but.grid(row=10, column=0, sticky="w")
    but = p_gtkwid.Button(top, text=Twid["Cancel"], command=pressedCan, bg="lightcyan", activebackground="cyan")
    but.grid(row=10, column=1, sticky="e")


def setWidgets():
    "Set default values to the widgets."
    entRoadW.thanSet(roadW)
    entPavLeftW.thanSet(pavLeftW)
    entPavRightW.thanSet(pavRightW)
    entMedW.thanSet(medW)


def object2Dialog(obj):
    "Get the values from an object."
    global roadW, pavLeftW, pavRightW, medW
    roadW     = obj.roadW
    pavLeftW  = obj.pavLeftW
    pavRightW = obj.pavRightW
    medW      = obj.medW


def dialog2Object(obj):
    "Set the values to an object."
    obj.roadW     = roadW
    obj.pavLeftW  = pavLeftW
    obj.pavRightW = pavRightW
    obj.medW      = medW


def pressedOk():
    "User pressed ok; check values."
    global roadW, pavLeftW, pavRightW, medW, valuesOk
    try:
        v = float(entRoadW.thanGet())
        if v <= 0: raise ValueError(T["A positive number was expected"])
    except Exception as e:
        p_gtkwid.thanGudModalMessage(top, message=e, title=T["Invalid width"], icon=p_gtkwid.ERROR)
        entRoadW.focus_set()
        return
    roadW = v
    try:
        v = float(entPavLeftW.thanGet())
        if v < 0: raise ValueError(T["A non negative number was expected"])
    except Exception as e:
        p_gtkwid.thanGudModalMessage(top, message=e, title=T["Invalid width"], icon=p_gtkwid.ERROR)
        entPavLeftW.focus_set()
        return
    pavLeftW = v
    try:
        v = float(entPavRightW.thanGet())
        if v < 0: raise ValueError(T["A non negative number was expected"])
    except Exception as e:
        p_gtkwid.thanGudModalMessage(top, message=e, title=T["Invalid width"], icon=p_gtkwid.ERROR)
        entPavRightW.focus_set()
        return
    pavRightW = v
    try:
        v = float(entMedW.thanGet())
        if v < 0: raise ValueError(T["A non negative number was expected"])
    except Exception as e:
        p_gtkwid.thanGudModalMessage(top, message=e, title=T["Invalid width"], icon=p_gtkwid.ERROR)
        entMedW.focus_set()
        return
    medW = v
    valuesOk = True
    top.destroy()


def pressedCan():
    "User pressed cancel; check values."
    global valuesOk
    ans = p_gtkwid.thanGudAskYesNo(top, message=T["Are you sure to lose all values?"], title=T["Cancel"], default="no")
    if ans:
        valuesOk = False
        top.destroy()

if __name__ == "__main__":
    test()
