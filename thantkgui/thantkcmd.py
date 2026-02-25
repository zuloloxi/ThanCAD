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

It implements ThanCad command line window.
"""

from math import cos, sin
import tkinter
import p_gtkwid, p_ggen
import thancom, thantk
from thanvers import tcver
from thanopt import thancadconf
from thanvar import Canc, thanLogTk, thanfiles, DEFMES
from thantrans import T
from .thantkguilowget.thantkconst import THAN_STATE


#class ThanTkCmd(p_gtkwid.ThanScrolledText1):
class ThanTkCmd(p_gtkwid.ThanScrolledText):
    "A standard text which command line capabilities."

    def __init__(self, proj, **kw):
        p_gtkwid.ThanScrolledText.__init__(self, master=proj[2], **kw)
        self.__proj = proj                    # A reference to ThanCad project
        self.__enlarged = None

        self.bindte("<Key>", self.thanOnChar)
        self.bindte("<F2>",  self.__onF2)     # So the text of the command window elnarged
        self.bindte("<F3>",  self.__onF3)     # Toggle object snap
        self.bindte("<F6>",  self.thanOnF6)   # Toggle coordinate auto-update
        self.bindte("<F7>",  self.thanOnF7)   # Toggle coordinate system
        self.bindte("<F8>",  self.__onF8)     # Toggle ortho mode

        self.bindte("<Control-Up>",   proj[2].thanCanvas.thanPanpageup)
        self.bindte("<Control-Down>", proj[2].thanCanvas.thanPanpagedown)
        self.bindte("<Control-Left>", proj[2].thanCanvas.thanPanpageleft)
        self.bindte("<Control-Right>",proj[2].thanCanvas.thanPanpageright)

        self.bindte("<KP_Add>",      self.__onGrayplus)
        self.bindte("<KP_Subtract>", self.__onGrayminus)
        self.bindte("<Control-KP_Add>",      self.__onCtrlGrayplus)
        self.bindte("<Control-KP_Subtract>", self.__onCtrlGrayminus)
        self.bindte("<Control-C>", self.__copyclip)
        self.bindte("<Control-c>", self.__copyclip)
        self.bindte("<Control-X>", self.__cutclip)
        self.bindte("<Control-x>", self.__cutclip)
        self.bindte("<Control-V>", self.__pasteclip)
        self.bindte("<Control-v>", self.__pasteclip)
        self.bindte("<Control-F>", self.__find)
        self.bindte("<Control-f>", self.__find)

        if p_ggen.Pyos.Windows:
            self.bindte("<MouseWheel>",       self._mouseWheelp)      #This ugly hack is for Windows
            self.bindte("<Shift-MouseWheel>", self._shiftmouseWheelp) #Yeah, Windows "just" works

        thantk.createTags((self,))
        self.thanCadVer()


    def _mouseWheelp(self, evt):
        "Just trap the event and send it to canvas."
        self.__proj[2].thanCanvas._mouseWheelp(evt)
        return "break"

    def _shiftmouseWheelp(self, evt):
        "Just trap the event and send it to canvas."
        self.__proj[2].thanCanvas._shiftmouseWheelp(evt)
        return "break"

    def setProj(self):
        "A new drawing is inserted to the current project; do some preprocessing."
        if thancadconf.thanTranslateTo != "en" and \
            thanfiles.isTempname1(self.__proj[0].basename()):    #This is the first drawing
            self.thanAppend("(Please type ", "info1")
            self.thanAppend("lang", "can1")
            self.thanAppend(" if you want to change the language.)\n", "info1")
        self.thanCleanup()
        self.thanPrevCom = ""
        self.__oncharPreempt = False


    def __copyclip(self, evt):  self.thanEnter("copyclip", "com");  return "break"
    def __cutclip(self, evt):   self.thanEnter("cutclip", "com");   return "break"
    def __pasteclip(self, evt): self.thanEnter("pasteclip", "com"); return "break"
    def __find(self, evt): self.thanEnter("find", "com")


    def thanCadVer(self):
        "Prints ThanCad's version."
        self.thanAppend("%s %s" % (tcver.name, tcver.version), "thancad")
        self.thanAppend("\n%s\n" % (tcver.copyright,))
        #self.thanAppend("0.6.5: Algorithm for regular polygons contributed by Spyros Nikolaou\n")
        #self.thanAppend("0.7.1: The contribution of Nikos Papandreou in bug hunting is greatly appreciated\n")
        self.thanAppend("The contribution of Dr Dimitra Vassilaki is greatly appreciated.\n")


    def thanPrompt(self, mes=DEFMES):
        "Shows a prompt for the user to enter something."
        self.thanMes = mes
        self.__reprompt()


    def __reprompt(self):
        "Reshows the default prompt or a specific command's prompt."
        if self.thanMes == DEFMES: self.thanAppend(self.thanMes, "mes")    # Other colour for default prompt
        else:                      self.thanAppend(self.thanMes)


    def thanOnChar(self, event):
        "Well, here is what should be done when user presses a key."
        ret = None
        if self.__oncharPreempt:
            thanLogTk.error("ThanTkCmd.thanOnChar: preemptive call: character(s) lost. It shouldn't happen.")
            if len(event.char) == 1:
                m = ord(event.char)
                if m == 27:
                    self.thanOnCharEsc(event)
                    self.__oncharPreempt = False
            return ret
        self.__oncharPreempt = True
#        print "len(event.char)=", len(event.char)
#        print "key code=", event.keycode
#        print "key sym=", event.keysym
        if len(event.char) == 1:
            m = ord(event.char)
            if m == 27:
                self.thanOnCharEsc(event)
            elif m == 13 or m == 32 and self.thanState != THAN_STATE.TEXTRAW:
                self.__onCharRet(event)
                self.thanAppend("\n")   #Change line
                ret = "break"           #break propagation of space or enter
        self.__oncharPreempt = False
        return ret


    def __onPageup(self, event):
        "Pageup pressed; if idle, pan drawing 1 page up."
        if self.thanState != THAN_STATE.NONE: return    # Page-up goes to the command window
        self.thanEnter("panpageup", "com")
        return "break"                                  # Pageup does not go to the command window


    def __onPagedown(self, event):
        "Pagedown pressed; if idle, pan drawing 1 page up."
        if self.thanState != THAN_STATE.NONE: return    # Page-up goes to the command window
        self.thanEnter("panpagedown", "com")
        return "break"                                  # Pageup does not go to the command window

    def __onPageleft(self, event):
        "Page left pressed; if idle, pan drawing 1 page up."
        if self.thanState != THAN_STATE.NONE: return    # Page-up goes to the command window
        self.thanEnter("panpageleft", "com")
        return "break"                                  # Pageup does not go to the command window

    def __onPageright(self, event):
        "Page right pressed; if idle, pan drawing 1 page up."
        if self.thanState != THAN_STATE.NONE: return    # Page-up goes to the command window
        self.thanEnter("panpageright", "com")
        return "break"                                  # Pageup does not go to the command window

    def __onCtrlGrayplus(self, event):
        "Gray plus pressed; if idle, zoom in 2 times."
        if self.thanState != THAN_STATE.NONE: return    # Grayplus goes to the command window
        self.thanEnter("zoomin2", "com")
        return "break"                                  # Grayplus does not go to the command window

    def __onCtrlGrayminus(self, event):
        "Gray minus pressed; if idle, zoom out 2 times."
        if self.thanState != THAN_STATE.NONE: return    # Grayminus goes to the command window
        self.thanEnter("zoomout2", "com")
        return "break"                                  # Grayminus does not go to the command window


    def __onGrayplus(self, event):
        "Gray plus pressed; brighten raster images."
        from thancom.thancomim import thanTkImageBrighten
        self.thanAppend("\n%s\n" % T["<Brighten images>"], "info")
        thanTkImageBrighten(self.__proj, verbose=False)
        self.__reprompt()
        return "break"                                  # Grayminus does not go to the command window

    def __onGrayminus(self, event):
        "Gray minus pressed; darken raster images."
        from thancom.thancomim import thanTkImageDarken
        self.thanAppend("\n%s\n" % T["<Darken images>"], "info")
        thanTkImageDarken(self.__proj, verbose=False)
        self.__reprompt()
        return "break"                                  # Grayminus does not go to the command window

#    def __donothing(self, event):
#        """Shift-Pageup pressed; do nothing.
#
#        This function exists so that shift-pageup will not trigger __onPageup.
#        tkinter will happily route shift-pageup, control-pageup etc. to the
#        pageup handler, if specialised handlers do not exist for these key-presses.
#        """
#        pass


    def __onF2(self, event):
        "Toggle enlarged text window."
        if self.__enlarged:
            self.__enlarged.destroy()
            self.__enlarged = None
        else:
            title = "%s: Content of command window" % self.__proj[0]
            self.__enlarged = ThanTkCmdbig(self.__proj, self.thanGetFtext(), title, font=thantk.thanFonts[0])
#            self.__enlarged = ThanTkCmdbig(self.__proj, self.thanGet(), title, font=thantk.thanFonts[0])
            self.__enlarged.thanTkSetFocus()


    def __onF3(self, event):
        "Toggle object snap."
        if self.__oncharPreempt: return "break"    # Avoid preemptive call
        if "ena" in thancadconf.thanOsnapModes:
            self.__proj[2].thanCanvas.thanOsnap.thanClear()
            del thancadconf.thanOsnapModes["ena"]
            self.thanAppend(T["\n<Object snap is off>\n"], "info")
        else:
            thancadconf.thanOsnapModes["ena"] = True
            self.thanAppend(T["\n<Object snap is on>\n"], "info")
        self.__reprompt()


    def thanOnF6(self, event):
        "Toggle coordinates auto-update."
        if self.__oncharPreempt: return "break"    # Avoid preemptive call
        e = self.__proj[2].thanStatusBar.thanToggleCoordUpdate()
        if e[0] == "c": s = T["<Coords off>"]
        else:           s = T["<Coords on>"]
        self.thanAppend("\n%s\n" % s, "info")
        self.__reprompt()


    def thanOnF7(self, event):
        "Toggle view type of coordinates."
        if self.__oncharPreempt: return "break"    # Avoid preemptive call
        typ = self.__proj[2].thanStatusBar.thanToggleCoordTyp()
        self.thanAppend(T["\n<View %s coordinates>\n"] % typ, "info")
        self.__reprompt()


    def __onF8(self, event):
        "Toggle ortho mode."
        if self.__oncharPreempt: return "break"    # Avoid preemptive call
        on = self.__proj[2].thanCanvas.thanOrtho.toggle()
        if on: self.thanAppend(T["\n<Ortho on>\n"], "info")
        else:  self.thanAppend(T["\n<Ortho off>\n"], "info")
        self.__reprompt()


    def thanNotifyF2(self):
        "The enlarged command window killed itself."
        self.__enlarged = None


    def thanOnCharEsc(self, evt):
        "Quits current task."
        if self.thanState != THAN_STATE.NONE:
            self.thanCleanup()
            return
        dc = self.__proj[2].thanCanvas
        if dc.thanState != THAN_STATE.NONE:
            dc.thanCleanup()
            self.thanCleanup(T["\nThanTkGuiGet was cleared for debugging reasons."], "can")
            self.thanPrompt()
            return
        if dc.thanFloatMenu is not None and dc.thanFloatMenu.winfo_ismapped():
            dc.thanCleanup()          # Delete floating (rightclick) menu
            return
        sched = self.__proj[2].thanScheduler
        if not sched.thanSchedIdle():
            sched.thanSchedClear()
            dc.thanCleanup()
            self.thanCleanup(T["\nThanScheduler was cleared for debugging reasons."], "can")
            self.thanPrompt()
            return
        if self.__proj[2].thanCleanupRegen():
            dc.thanCleanup()
            self.thanCleanup(T["\nThanScheduler was cleared for debugging reasons."], "can")
            self.thanPrompt()
            return

        dc.thanCleanup()
        self.thanCleanup("\n%s" % T["Nothing to cancel."], "can")
        self.thanPrompt()


    def __onCharRet(self, evt):
        "Gets the command entered by the user"
        self.thanWaitingInput = False
#       now = [int(c) for c in self.index(tkinter.INSERT).split(".")]
#       end = [int(c) for c in self.index(tkinter.END).split(".")]
        now = self.thanIndex(tkinter.INSERT)
        end = self.thanIndex(tkinter.END)
        if end[0]-now[0] > 1:
            l = str(now[0])
            t = self.thanGetPart(l+".0", l+".end")
            self.thanInsert(tkinter.END, "\n"+t)
            self.set_insert(tkinter.END+"-1c")
        else:
            t = self.thanGetPart(tkinter.END+"-1l", tkinter.END)

        if self.thanState == THAN_STATE.TEXTRAW:
            t = t.rstrip("\n") #for text entry strip only newline at the end
        else:
            t = t.strip()
            n = -1; n1 = t.find(":")
            while n1 >= 0:
                n = n1; n1 = t.find(":", n+1)
            if n >= 0: t = t[n+1:].strip()
        self.after(100, self.__processEntry, t)


    def thanEnter(self, com, tags=()):
        "Simulate keyboard and return immediately."
        self.thanWaitingInput = False
        self.thanAppend("%s\n" % com, tags)
        self.after(100, self.__processEntry, com)

    PNTSTATES = frozenset((THAN_STATE.POINT, THAN_STATE.LINE, THAN_STATE.LINE2,
        THAN_STATE.RECTANGLE, THAN_STATE.MOVE, THAN_STATE.ROADP, THAN_STATE.SPLINEP,
        THAN_STATE.POLAR, THAN_STATE.AZIMUTH,
        THAN_STATE.CIRCLE, THAN_STATE.CIRCLE2, THAN_STATE.CIRCLE3, THAN_STATE.ARC, THAN_STATE.ELLIPSEB))

    def __processEntry(self, t):
        "Deals with the text the user entered."
        s = self.thanState
        if self.thanState == THAN_STATE.NONE:
            self.__beginCommand(t)
        elif t[:1] == "'":
            c, fun = thancom.thanComFun(t[1:])
            if fun is not None:
                self.thanLastResult = "'"+c
                self.thanState = THAN_STATE.NONE
            else:
                self.thanAppend(T["Invalid nested command. Try again.\n"], "can")
                self.__reprompt()
        elif s in self.PNTSTATES:
            try:
                nd   = self.__proj[1].thanVar["dimensionality"]
                elev = self.__proj[1].thanVar["elevation"]
                if t[0] == "@":            #relative coordinates
                    if len(t) == 1:        #If relative coordinates are missing, then [0,0] are assumed
                        cc = [0.0] * nd
                    else:
                        cc = self.getCartOrPolar(t[1:], nd, elev)
                    crel = self.__proj[1].thanGetLastPoint()
                    for i in range(nd): cc[i] += crel[i]
                else:
                    cc = self.getCartOrPolar(t, nd, elev)
            except (IndexError,ValueError):
                self.thanLastResult = t
            else:
                self.__proj[1].thanSetLastPoint(cc)
                self.thanLastResult = cc
                print("cmd: last result point: ", cc)
            self.thanState = THAN_STATE.NONE
        elif s == THAN_STATE.RECTRATIO:
            try: r = float(t)
            except (IndexError,ValueError):
                self.thanAppend(T["Invalid real number. Try again.\n"], "can")
                self.__reprompt()
                self.thanWaitingInput = True
                return
            cc = list(self.__cc1)
            cc[0] += r
            cc[1] += r*self.__t1
            self.thanLastResult = cc
            self.thanState = THAN_STATE.NONE
        elif s == THAN_STATE.TEXT or s == THAN_STATE.TEXTRAW or s == THAN_STATE.SNAPELEM:
            self.thanLastResult = t
            self.thanState = THAN_STATE.NONE
        elif s == THAN_STATE.ZOOMDYNAMIC or s == THAN_STATE.PANDYNAMIC:
            pass       # no keyboard entry by definition

        else:
            assert False, "Unknown state: "+str(s)
        self.thanWaitingInput = True


    def getCartOrPolar(self, t, nd, elev):
        "Get cartesian or polar coordinates; tansform polar to cartesian."
        if "<" in t:
            cc = [float(c1) for c1 in t.split("<")]
            if len(cc) > 2: raise ValueError("Too many dimensions in polar coordinates")
            if len(cc) < 2:  raise ValueError("Too few dimensions")
            r, phi = cc
            un = self.__proj[1].thanUnits
            phi = un.unit2rad(phi)           #Tranform angle from user units to rads
            cc[0] = r*cos(phi)
            cc[1] = r*sin(phi)
        else:
            cc = [float(c1) for c1 in t.split(",")]
            if len(cc) > nd: raise ValueError("Too many dimensions")
            if len(cc) < 2:  raise ValueError("Too few dimensions")
        cc.extend(elev[len(cc):])
        return cc


    def thanPrepare(self, state, cc1=None, cc2=None, r1=None, t1=None):
        "Sets the appropriate state and prepares for user input."
        self.__cc1 = cc1
        self.__cc2 = cc2
        self.__rr1 = r1
        self.__t1 = t1
        self.thanState = state
        if state == THAN_STATE.POINT1: self.thanState = THAN_STATE.POINT
        self.thanWaitingInput = True


    def thanCleanup(self, message="", mesmode="info1"):
        "User cancelled or gave the results in other way (e.g. gui)."
        if message != "": self.thanAppend("%s\n" % message, mesmode)
        self.thanState = THAN_STATE.NONE
        self.thanLastResult = Canc
        self.thanWaitingInput = True


    def __beginCommand(self, t):
        "The user entered a command; launch it."
        w = self.__proj[2]
        assert w.thanScheduler.thanSchedIdle(), "No command should be running!!!"
        t = t.lower()
        if t == "":
            if self.thanPrevCom == "":
                self.thanPrompt()
                self.thanWaitingInput = True
            else:
                self.thanEnter(self.thanPrevCom, "com")
            return
        c, fun = thancom.thanComFun(t)
        if fun is not None:
            if t != c: self.thanAppend("%s\n" % c, "com")    #Show the full name of the command
            w.thanScheduler.thanSchedule(fun, self.__proj)   #A command will run immediately; thanWaitingInput remains False
            self.thanPrevCom = c
        else:
            self.thanAppend(T["Unrecognized command\n"], "can")
            self.thanPrompt()
            self.thanWaitingInput = True


    def thanBeginCommandNest(self, t):
        "The user entered a nested command; launch it."
        c, fun = thancom.thanComFun(t)
        if fun is not None:
            if t != c: self.thanAppend("%s\n" % c, "com")
            fun(self.__proj)
        else:
            self.thanAppend(T["Unrecognized command\n"], "can")


    def thanClear(self): self.thanSet("")


    def destroy(self):
        "Deletes circular references."
        del self.__proj
        p_gtkwid.ThanScrolledText.destroy(self)


class ThanTkCmdbig(tkinter.Toplevel):
    "Just the text of the command window enlarged."

    def __init__(self, proj, ftext, title, hbar=0, vbar=1, width=80, height=25,
        font=None, background="lightyellow", foreground="black"):
        "Setup info."
        tkinter.Toplevel.__init__(self, proj[2])
        self.title(title)
        self.__proj = proj
        self.thanFont1 = font
        if font is None:
            self.thanFont1=tkinter.font.Font(family=thancadconf.thanFontfamilymono, size=thancadconf.thanFontsizemono)

        self.thanHelp = p_gtkwid.ThanScrolledText(self, hbar=hbar, vbar=vbar, font=self.thanFont1,
            background=background, foreground=foreground, width=width, height=height, readonly=True)
        thantk.createTags((self.thanHelp,))
        self.thanHelp.thanInsertFtext(ftext)
        self.thanHelp.grid(row=0, column=0, sticky="wesn")
        self.thanHelp.set_insert(tkinter.END+"-1c")
        self.thanHelp.bindte("<F2>", self.__onF2)

        self.protocol("WM_DELETE_WINDOW", self.__onF2) # In case user closes window with window manager
        p_gtkwid.thanGudPosition(self, master=proj[2])
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


    def __onF2(self, *args):
        "Terminate the window."
        self.__proj[2].thanCom.thanNotifyF2()
        self.destroy()

    def thanTkSetFocus(self):
        "Sets focus to the command window."
        self.lift()
        self.focus_set()
        self.thanHelp.focus_sette()

    def destroy(self):
        "Break circular references."
        del self.thanHelp, self.__proj, self.thanFont1
        tkinter.Toplevel.destroy(self)

    def __del__(self):
        "Say that it is deleted for debugging reasons."
        from p_ggen import prg
        prg("ThanTkCmdbig %s is deleted." % self)
