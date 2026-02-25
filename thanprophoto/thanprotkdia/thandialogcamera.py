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

This dialog accepts the parameters of a photogrammetric metric camera.
"""

import sys, copy
import tkinter
from tkinter.messagebox import ERROR
import p_gtkwid, p_ggen
from thanopt import thancadconf
from thanvar import Canc
from thantrans import T, Tphot
#T = p_gtkwid.Translation(dict(__TRANSLATION__=("en", "EN", "en", "EN")))  ##############


mm = p_gtkwid.thanGudModalMessage


class ThanCamera(p_gtkwid.ThanComDialog):
    "Dialog for the parameters of a photogrammetric metric camera."

    def __init__(self, *args, **kw):
        "Extract initial rectification parameters."
        self.filnam = p_ggen.path("Untitled1.cam")
        kw.setdefault("title","%s - %s" % (self.filnam.name, Tphot["Photogrammetric Camera Parameters"]))
        kw["buttonlabels"] = None
#        kw["cargo"] = [ p_ggen.path("q1"), None, self]        ############################
        p_gtkwid.ThanComDialog.__init__(self, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct()
#        self.thanValsDefICP(v)   # Common ICP parameters
        v.entName = "NewCamera"
        v.entFocus= 150.0
        v.entFid1x, v.entFid1y = -110.0,    0.0
        v.entFid2x, v.entFid2y =    0.0,  110.0
        v.entFid3x, v.entFid3y =  110.0,    0.0
        v.entFid4x, v.entFid4y =    0.0, -110.0
        v.entFid5x, v.entFid5y = "", ""
        v.entFid6x, v.entFid6y = "", ""
        v.entFid7x, v.entFid7y = "", ""
        v.entFid8x, v.entFid8y = "", ""
        return v


    def menu(self):
        "Create a menu."
        s = "File Edit View Image Format Tools Draw Engineering Photogrammetry Modify Research Developer Window Help".split()
        m = {}
        m = \
        [ (None, T["&File"], ""),            # Menu Title
          (self.__new,    T["&New"],     Tphot["Clears all camera parameters"]),
          (self.__open,   T["&Open"],    Tphot["Opens an existing camera file"]),
          (self.__save,   T["&Save"],    Tphot["Saves camera parameters into current file"]),
          (self.__saveas, T["S&ave as"], Tphot["Saves camera parameters into another file"]),
          (None, "-", "-"),               # Separator
          (self.cancel,   T["&Close"],   Tphot["Closes camera dialog discarding parameters"]),
          (None, "-", "-"),               # Separator
          (self.__exit,   T["Save and E&xit"], Tphot["Closes camera dialog and saves parameters into current file"], "darkred"),
          (None, T["&Help"], "", None, "help"),            # Menu Title
          (self.__help,   T["&Instructions"],  T["Instructions about this dialog"]),
          (self.__about,  T["&About"],         T["Information about this program"]),
        ]
        menubar, _ = p_gtkwid.thanTkCreateThanMenus(self, m, statcommand=self.__stat.sett, condition=None)
        return menubar


    def __new(self):
        "Clear all entries in order to input new values."
        if not self.ok2change(T["Data modified, OK to clear?"]): return   #new was cancelled
        v = p_ggen.Struct()
        v.entName = ""
        v.entFocus= ""
        v.entFid1x, v.entFid1y = "", ""
        v.entFid2x, v.entFid2y = "", ""
        v.entFid3x, v.entFid3y = "", ""
        v.entFid4x, v.entFid4y = "", ""
        v.entFid5x, v.entFid5y = "", ""
        v.entFid6x, v.entFid6y = "", ""
        v.entFid7x, v.entFid7y = "", ""
        v.entFid8x, v.entFid8y = "", ""
        self.filnam = p_ggen.path("Untitled1.cam")
        self.thanSet(v)
        self.thanValsSaved = v


    def __open(self):
        "Open an existing camera file."
        from thancom.thancomfile import thanTxtopen  #########################
        if not self.ok2change(T["Data modified, OK to replace with data read from file?"]): return   #new was cancelled
        filnam, fr = thanTxtopen(self.thanProj, Tphot["Choose Photogrammetric camera file to open"],
            suf=".cam", initialdir=thancadconf.thanCameradir)
        if fr == Canc: return
        v = p_ggen.Struct()
        try:
            v.entName = next(fr).strip()
            v.entFocus = float(next(fr))
        except ValueError as why:
            mm(self, "%s:\n\n%s" % (fr.name, why), Tphot["Syntax error while reading focus length"], ERROR)   # (Gu)i (d)ependent
            return
        except StopIteration:
            why = Tphot["Incomplete camera file"]
            mm(self, "%s:\n\n%s" % (fr.name, why), why, ERROR)   # (Gu)i (d)ependent
            return
        x = [""] * 9
        y = [""] * 9
        for ifid in range(1, 9):
            try:
                x[ifid], y[ifid] = map(float, next(fr).split())  #works for python2,3
            except ValueError as why:
                mm(self, "%s:\n\n%s" % (fr.name, why), Tphot["Syntax error while reading fiducial coordinates"], ERROR)   # (Gu)i (d)ependent
                return
            except StopIteration:
                break
        for ifid in range(1, 9):
            fx = "entFid%dx" % (ifid,)
            fy = "entFid%dy" % (ifid,)
            setattr(v, fx, x[ifid])
            setattr(v, fy, y[ifid])
        self.filnam = filnam
        self.thanSet(v)
        self.thanValsSaved = v
        thancadconf.thanCameradir = filnam.parent
        self.title("%s - %s" % (Tphot["Photogrammetric Camera Properties"], self.filnam.name))


    def __save(self):
        "Save camera properties into current file."
        if self.filnam.name == "Untitled1.cam": return self.__saveas()
        if not self.validate():
            self.initial_focus.focus_set()
            return False   #do nothing if error in properties
        try:
            fw = open(self.filnam, "w")
        except IOError as why:
            mm(self, "%s:\n\n%s" % (self.filnam.name, why), T["Save failed"], ERROR)   # (Gu)i (d)ependent
            return False
        return self.__saveHouse(self.filnam, fw)


    def __saveas(self):
        "Save camera properties into a file."
        if not self.validate():
            self.initial_focus.focus_set()
            return False   #do nothing if error in properties
        from thancom.thancomfile import thanTxtopen  #########################
        filnam, fw = thanTxtopen(self.thanProj, Tphot["Choose Photogrammetric camera file to open"],
            suf=".cam", mode="w", initialdir=thancadconf.thanCameradir)
        if filnam == Canc: return False    # Saveas was cancelled
        return self.__saveHouse(filnam, fw)


    def __saveHouse(self, filnam, fw):
        "Save properties to an opened file and do housekeeping."
        vs = self.result
        try:
            fw.write("%s\n" % vs.entName)
            fw.write("%f\n" % vs.entFocus)
            for ifid in range(1, 9):
                fx = "entFid%dx" % (ifid,)
                fy = "entFid%dy" % (ifid,)
                x = getattr(vs, fx)
                if x == "": break
                y = getattr(vs, fy)
                fw.write("%f   %f\n" % (x, y))
            fw.close()
        except IOError as why:
            mm(self, "%s:\n\n%s" % (filnam.name, why), T["Save failed"], ERROR)   # (Gu)i (d)ependent
            return False
        finally:
            fw.close()
        self.thanValsSaved = copy.deepcopy(vs)
        self.filnam = filnam
        thancadconf.thanCameradir = filnam.parent
        self.title("%s - %s" % (Tphot["Photogrammetric Camera Properties"], self.filnam.name))
        return True


    def __exit(self):
        "Save properties to file and exit."
        if self.__save(): self.ok()


    def __help(self):   pass
    def __about(self):  pass


    def body2(self, win):
        "Create the body of the dialog in steps."
        self.fraId(win, 1)
        self.fraFid(win, 2)
        self.__stat = p_gtkwid.ThanStatusBar(win)
        self.__stat.grid(row=3, column=0, sticky="we")


    def fraId(self, win, ir):
        "Get camera name, focus length, filename."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["CAMERA ID:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=2)

        key = "entName"
        tit = "Camera Name"                        #Tphot["Camera Name"]
        lab = tkinter.Label(fra, text=Tphot[tit])
        lab.grid(row=1, column=1, sticky="w")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=1, column=2, sticky="we")
        val = p_gtkwid.ThanValBlank()
        self.thanWids.append((key, tit, wid, val))

        key = "entFocus"
        tit = "Focus Length c (mm)"                #Tphot["entFocus"]
        lab = tkinter.Label(fra, text=Tphot[tit])
        lab.grid(row=2, column=1, sticky="e")
        wid = p_gtkwid.ThanEntry(fra)
        wid.grid(row=2, column=2, sticky="we")
        val = p_gtkwid.ThanValFloat(0.001, 10000.0)
        self.thanWids.append((key, tit, wid, val))

        fra.columnconfigure(2, weight=1)


    def fraFid(self, win, ir):
        "Get camera fiducials."
        fra = tkinter.Frame(win, bd=3, relief=tkinter.RIDGE)
        fra.grid(row=ir, column=0, pady=5, sticky="we")

        lab = tkinter.Label(fra, fg=self.colfra, text="%d."%(ir,))
        lab.grid(row=0, column=0)
        lab = tkinter.Label(fra, anchor="w", fg=self.colfra, text=Tphot["CAMERA FIDUCIALS:"])
        lab.grid(row=0, column=1, sticky="w", columnspan=4)

        lab = tkinter.Label(fra, text="X (mm)")
        lab.grid(row=1, column=2, sticky="w")
        lab = tkinter.Label(fra, text="Y (mm)")
        lab.grid(row=1, column=3, sticky="w")
        i = 1
        for ifid in range(1, 9):
            lab = tkinter.Label(fra, text="%d " % ifid)
            lab.grid(row=i+ifid, column=1)
            for j in range(2):
                key = "entFid%d%s" % (ifid, "xy"[j])
#                tit = "Fiducial %d %s (mm)" % (ifid, "xy"[j])  #Don't put ifid:Save translation space
                tit = "Fiducial %s (mm)" % ("xy"[j],)      #Tphot["Fiducial x (mm)"] #Tphot["Fiducial y (mm)"]
                wid = p_gtkwid.ThanEntry(fra)
                wid.grid(row=i+ifid, column=2+j, sticky="we")
                val = p_gtkwid.ThanValFloatBlank()
                self.thanWids.append((key, tit, wid, val))

        fra.columnconfigure(2, weight=1)
        fra.columnconfigure(3, weight=1)


    def validate(self, strict=True, wids=None, values=None):
        "Returns true if the value chosen by the user is valid."
        ret, vs = self.validate2(strict, wids, values)
        if not ret and strict: return ret
        blankfound = False
        nfid = 0
        for ifid in range(1, 9):
            fx = "entFid%dx" % (ifid,)
            fy = "entFid%dy" % (ifid,)
            vx = getattr(vs, fx)
            vy = getattr(vs, fy)
            if vx == "" and vy != "" or vx != "" and vy == "":
                ret = False
                if strict:
                    self.initial_focus = getattr(self, fx)
                    mm(self,
                        Tphot["The x, y coordinates of a fiducial must be both numbers or blank"],
                        T["Error in data"])
                    return ret
            if vx == "" and vy == "":
                blankfound = True
            elif blankfound:
                ret = False
                if strict:
                    self.initial_focus = getattr(self, fx)
                    mm(self,
                        Tphot["Coordinates are not permitted after a blank fiducial."],
                        T["Error in data"])
                    return ret
            else:
                nfid += 1
        if nfid < 3:
            ret = False
            if strict:
                mm(self,
                    Tphot["At least 3 fiducials should be given"],
                    T["Error in data"])
                return ret
        self.result = vs
        return ret


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
        self.__stat.destroy()
        del self.__stat
        p_gtkwid.ThanComDialog.destroy(self)


def test1():
    root = tkinter.Tk()
    dia = ThanCamera(root)
#    root.mainloop()

if __name__ == "__main__": test1()
