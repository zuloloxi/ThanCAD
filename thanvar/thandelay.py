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

A class to let the user stop a computation if it takes too long.
"""

import time

class ThanDelay:
    "A class to let the user stop a computation if it takes too long."

    def __init__(self, win, idloop=10, updatetime=0.1, respondtime=4.0):
        "Initialize parameters."
        self.win = win               #Window to call method update() (normally Tk, or Toplevel window)
        self.timebeg = time.time()   #Beginning time stamp of lengthy computation
        self.timeprev = self.timebeg #Time stamp of previous to update()
        self.timeprevrespond = self.timebeg #Time stamp of previous call to respond
        self.iloop = 0               #Loop count
        self.idloop = int(idloop)    #update() will be called every idloop iterations of the computation
        if self.idloop < 0: self.idloop = 1
        self.updatetime = updatetime
        self.respondtime_ori = respondtime
        self.respondtime = self.respondtime_ori
        self.idle = True
        self.quitcomputation = False

    def isIdle(self):
        "Return true if the object is not currenty being used."
        return self.idle

    def stop(self):
        "Stop the use of the object."
        t = time.time() - self.timebeg
        self.win.unbind('<q>')    # remove bind of the 'q' event
        self.idle = True
        return t


    def start(self):
        "Start new lengthy computation."
        self.idle = False
        self.iloop = 0
        self.timebeg = time.time()
        self.timeprev = self.timebeg
        self.timeprevrespond = self.timebeg
        self.respondtime = self.respondtime_ori
        self.win.unbind('<q>')    # remove bind of the 'q' event
        self.quitcomputation = False

    def inc(self):
        "Increment loop; this will be called by the user typically at every iteration."
        self.iloop += 1
        if self.iloop % self.idloop > 0: return
        timenow = time.time()
        t = timenow - self.timeprev
        if t < self.updatetime/10.0:
            self.idloop *= 10
            print(self.idloop)
            return
        if t > self.updatetime*2.0:
            self.idloop //= 10
            if self.idloop < 1: self.idloop = 1
            print(self.idloop)
        self.win.update()
        self.timeprev = timenow
        t = timenow-self.timeprevrespond
        if t < self.respondtime: return
        qfuncid = self.win.bind("<q>", self.doquit)
        self.win.thanPrt("It seems that the computation takes too long. Please wait, or type 'q' to quit")
        if self.respondtime < self.respondtime_ori*16.1: self.respondtime*=2.0
        self.timeprevrespond = timenow

    def doquit(self, evt):
        "The user press 'q'; signal the computation to stop()."
        print("Event 'q' triggered")
        self.quitcomputation = True
        return "break"

    def quit(self):
        "Rerurns True if user presses 'q'."
        self.inc()
        return self.quitcomputation


import tkinter as tk
from math import sqrt
import p_gtkwid

class Mywin:
    def __init__(self):
        self.root = tk.Tk()
        self.delay = ThanDelay(self.root)
        dc = tk.Canvas(self.root, bg='lightyellow')
        dc.grid()
        self.text = p_gtkwid.ThanText(self.root)
        self.text.grid()
        but = tk.Button(self.root, text="Compute", command=self.comp)
        but.grid()


    def thanPrint(self, mes, tag=()):
        self.text.thanAppend("%s\n" % mes, tag)


    def comp(self):
        "Lengthy computation."
        if not self.delay.idle: return #Avoid preemptive calls
        self.delay.start()
        quit = self.delay.quit
        s = 0.0
        for i in range(10000000):
            s = s+sqrt(i)
            if quit(): break
        t = self.delay.stop()
        print(t, "sec")
        if quit(): print("Computation Cancelled")
        else: print("result is", s)


if __name__ == "__main__":
    win = Mywin()
    win.root.mainloop()
