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

This module defines functionality necessary for user interaction in a drawing
window.
"""

import time
from math import atan2, hypot, cos, sin
import tkinter
from tkinter import simpledialog
import p_gtkwid, p_ggen

from thanvar import Canc, ThanScheduler, thanfiles
from thanopt import thancadconf
from thantrans import T
from .thantkguilowget.thantkconst import THAN_STATE


class ThanTkGuiHighGet:
    "Mixin for highlevel getting information from Tk window."

    def __init__ (self):
        "Initialisation is needed."
        self.thanNest = False
        self.thanSelems = set()             # Elements which may be snapped to
        self.__externalFilterFunc = None    # External filter for the selection routines


    def thanGudSetSelExternalFilter(self, func):
        "Sets external filter function."
        self.__externalFilterFunc = func    # External filter for the selection routines


    def thanWaitFor(self, mes, state, cc1=None, cc2=None, cc3=None, rr1=None, tt1=None, tt2=None):
        "Sets the appropriate state to gui AND command line, and waits for either result."
        dc = self.thanCanvas; cmd = self.thanCom
        while True:
            res, cargo = self.__WaitFor(mes, state, cc1, cc2, cc3, rr1, tt1, tt2)
            try:    nest1 = (res[:1] == "'")
            except: nest1 = False
            if not nest1: return res, cargo
            if self.thanNest:
                cmd.thanAppend("A nested command is currently being executed.\n"\
                    "Please exit this nested command in order to begin a new one\n", "can")
                continue
            self.thanNest = True
            self.__cmdstate = cmd.__dict__.copy()
            self.__dcstate  = dc.__dict__.copy()
            self.__scheduler = self.thanScheduler
            self.thanScheduler = ThanScheduler()
            cmd.thanCleanup()                       # Cleanup saved answer in commandline
            dc.thanCleanup()                        # Cleanup gui
            cmd.thanAppend("Beginning nested command..\n", "mes")
            cmd.thanAppend("%s\n" % res[1:], "com")
            cmd.thanBeginCommandNest(res[1:])
            cmd.thanAppend("Resuming original command\n", "mes")
            cmd.thanCleanup()                       # Cleanup saved answer in commandline
            dc.thanCleanup()                        # Cleanup gui
            cmd.__dict__.update(self.__cmdstate)
            dc.__dict__.update(self.__dcstate)
            self.thanScheduler = self.__scheduler
            del self.__cmdstate, self.__dcstate, self.__scheduler
            self.thanNest = False


    __READYSTATES = frozenset(\
        (THAN_STATE.POINT, THAN_STATE.POINT1,
         THAN_STATE.LINE, THAN_STATE.LINE2,
         THAN_STATE.RECTANGLE, THAN_STATE.RECTRATIO,
         THAN_STATE.MOVE, THAN_STATE.ROADP, THAN_STATE.ROADR,
         THAN_STATE.SPLINEP, THAN_STATE.POLAR, THAN_STATE.AZIMUTH, THAN_STATE.CIRCLE,
         THAN_STATE.CIRCLE2, THAN_STATE.CIRCLE3, THAN_STATE.ARC, THAN_STATE.ELLIPSEB,
        ))


    def __WaitFor(self, mes, state, cc1=None, cc2=None, cc3=None, rr1=None, tt1=None, tt2=None):
        "Sets the appropriate state to gui AND command line, and waits for either result."
        dc = self.thanCanvas
        cmd = self.thanCom
        strcoo = self.thanProj[1].thanUnits.strcoo
        dc.thanPrepare(state, cc1, cc2, cc3, rr1, tt1, tt2)
        while True:
            cmd.thanPrompt(mes)
            cmd.thanPrepare(state, cc1, cc2, rr1, tt1)     # It only sets the state and the ratio
            for com1 in self.thanScriptComs:
                cmd.thanEnter(com1)
                break
            while dc.thanState != THAN_STATE.NONE and cmd.thanState != THAN_STATE.NONE: dc.update()

            if dc.thanState == THAN_STATE.NONE:            # Gui answered
                res, cargo = dc.thanLastResult              # Get gui result
                dc.thanCleanup()                            # Cleanup saved answer in gui
                cmd.thanCleanup()                           # Cleanup commandline
                if res == Canc: return res, cargo
                if res == -2: return res, cargo
                if res == "c": return "c", cargo
                if state in self.__READYSTATES:
                    cmd.thanCleanup("%s" % strcoo(res))
                    self.thanProj[1].thanSetLastPoint(res)  # Save last point for relative coords
                    return res, cargo
                elif state == THAN_STATE.SNAPELEM:
                    cmd.thanCleanup(" ")
                    return res, cargo
                elif state == THAN_STATE.TEXT or state == THAN_STATE.TEXTRAW:
                    assert False, "Boy, I would like to see this bug :)"
                elif state == THAN_STATE.ZOOMDYNAMIC or state == THAN_STATE.PANDYNAMIC:
                    return res, cargo
                else:
                    assert False, "Unknown state "+str(state)
            else:                                          # Commandline answered
                res = cmd.thanLastResult                    # Get commandline result
                try:    nest1 = (res[:1] == "'")
                except: nest1 = False
                if nest1: return res, None

                cmd.thanCleanup()                           # Cleanup saved answer in commandline
                dc.thanCleanup()                            # Cleanup gui
                if res == Canc: return res, None
                #print("__waitfor: cmd answered: type=", type(res), "  result=", res)
                return res, None

#============================================================================

    def thanGudCommandBegin(self, com):
        "Begins a new command, as if the user entered com via the keyboard."
        self.thanCom.thanEnter(com, tags="com")

    def thanGudCommandEnd(self, mes=None, mestype="can"):
        "Print optional message and reprompt."
        if mes is not None: self.thanCom.thanAppend("%s\n" % mes, mestype)
        self.thanCom.thanPrompt()
        self.thanCom.thanWaitingInput = True

    def thanGudCommandCan(self, mes=None, mestype="can"):
        """print((at least default) cancel message and reprompt.)

        The meaning of this is that the previous command ended
        unsuccessfully and no do/undo was added. That's why
        the word 'cancel' is always shown. So that when the user
        sees cancel, it means that the drawing has not been altered."""
        from thanvar import DEFCAN
        if mes is not None:
            self.thanCom.thanAppend("%s\n" % mes, mestype)
        self.thanCom.thanAppend("%s\n" % DEFCAN, mestype)
        self.thanCom.thanPrompt()
        self.thanCom.thanWaitingInput = True

    def thanPrtCan(self, tag="can"):
        "Prints 'cancelled' to the command window."
        from thanvar import DEFCAN
        self.thanCom.thanAppend("%s\n" % DEFCAN, tag)

    def thanPrt(self, mes, tag=()):
        "Print to the command window; this is info, warnings, error etc."
        self.thanCom.thanAppend("%s\n" % mes, tag)
    def thanPrts(self, mes, tag=()):
        "Print to the command window without newline at the end; this is info, warnings, error etc."
        self.thanCom.thanAppend(mes, tag)
    def thanPrtbo(self, mes, tag="info"):
        "Print to the command window; default is bold info."
        self.thanCom.thanAppend("%s\n" % mes, tag)
    def thanPrter(self, mes, tag="can"):
        "Print to the command window; default is bold error."
        self.thanCom.thanAppend("%s\n" % mes, tag)
    def thanPrter1(self, mes, tag="can1"):
        "Print to the command window; default is error."
        self.thanCom.thanAppend("%s\n" % mes, tag)

#============================================================================

    def __getPoint(self, stat1, statonce="", strict=True, options=(), state="", args=()):
        """Gets a point but allows for options which are returned with the first letter (in lower case).

        1. Read user response.
        2. If user cancelled, return Canc
        3. If it is point (coordinates), return point.
        4. If it is an object snap settings override, save previous osnap,
           set new osnap, and go to step 1.
        5. If it is one of the options, return the first letter of this option.
        6. If we reached here it is not a point, osnap, or option. So:
        7. If strict==False, return the user response as text.
        8. Otherwise print(error message, and go to step 1.)
        9. Before returning (steps 2,3,5,7), restore object snap to original settings.
        10.statonce is a message that is printed only the first time that this
           function asks for input. If the function asks again for input (in
           case of error - step 8) statonce is not printed.
        """
        def uniqoption():
            "Find option and return the first letter if letter is unique, else the whole option."
            for i, opt in enumerate(opts):
                if res1 == opt[:n]: break
            else:
                return None
            opt1 = opt
            for j in range(i):
                if opts[j] == "": continue    #Blank option is permitted; hopefully it is unique
                if opts[j][0] == opt1[0]: return opt1, "o", None # not unique
            return opt1[0], "o", None      # unique

        stat = statonce+stat1
        opts = [opt.strip().lower() for opt in options]
        osnapOrig = None
        nd = self.thanProj[1].thanVar["dimensionality"]
        while True:
            res, cargo = self.thanWaitFor(stat, state, *args)
#-----------Check if user cancelled
            if res == Canc:
                ret = Canc, "o", None
                break
#-----------Check if response is coordinates and return them
            istext = True
            try: res+"x"
            except: istext = False
            if not istext:  #If it is text then res[0], res[1], res[2] might be digits and they would be taken as coordinates
                try:
                    c2 = [float(res[i]) for i in range(nd)]
                except (IndexError, ValueError, TypeError):
                    pass
                else:
                    ret = c2, "v", cargo                     # Validated coordinates plus cargo are returned
                    break
#-----------Transform response to text and check if it is object snap override
            res1 = str(res).strip().lower()
            if res1 == "non":
                    if osnapOrig is None: osnapOrig = thancadconf.thanOsnapModes.copy()
                    thancadconf.thanOsnapModes.clear()
                    stat = " of: "
                    continue
            for osnap1,_ in thancadconf.thanOsnapModesText:  # Check snap override and repeat inquiry
                if res1 == osnap1:
                    if osnapOrig is None: osnapOrig = thancadconf.thanOsnapModes.copy()
                    thancadconf.thanOsnapModes.clear()
                    thancadconf.thanOsnapModes[osnap1] = True
                    thancadconf.thanOsnapModes["ena"] = True
                    stat = " of: "
                    break
            if res1 == osnap1: continue
#-----------Check if response is a known option
            n = len(res1)
            if n == 0:
                if "" in opts:
                    ret = "", "o", None                      # Option is returned
                    break
            elif len(opts) > 0:
                ret = uniqoption()
                if ret is not None: break
#-----------Check if not strict and return the user response as text
            if not strict:
                ret = res, "t", cargo                        # Text (other than coordinates,osnap or options) plus cargo are returned
                break
#-----------If none of the above applies, print(error message and repeat inquiry)
            if len(opts) == 0: stat = T["Invalid Point. Try again.\n"]
            else:              stat = T["Invalid point or option. Try again.\n"]
            self.thanCom.thanAppend(stat, "can")
            stat = stat1
#-------Before returning the response, restore original object snap settings
        if osnapOrig is not None:
            thancadconf.thanOsnapModes.clear()
            thancadconf.thanOsnapModes.update(osnapOrig)
        return ret


    def thanGudGetPoint(self, stat1, statonce="", options=()):
        "Gets a point from user with possible options."
        return self.__getPoint(stat1, statonce, strict=True, options=options,
               state=THAN_STATE.POINT)[0]

    def thanGudGetPointOr(self, stat1, statonce="", options=()):
        "Gets a point from user with possible options or any other text."
        return self.__getPoint(stat1, statonce, strict=False, options=options,
               state=THAN_STATE.POINT)


    def thanGudGetSize(self, c1, stat, default=None, statonce="", options=()):
        "Gets a point from user with possible options or a positive real number."
        while True:
            res, typ, cargo = self.__getPoint(stat, statonce, strict=False, options=options,
               state=THAN_STATE.LINE, args=(c1,))
            if typ == "o":            #This includes Canc
                return res
            elif typ == "v":
                c2 = res
                size = hypot(c2[1]-c1[1], c2[0]-c1[0])
                if size > 0.0: return size
            elif typ == "t":
                if res.strip() == "" and default is not None: res = default
                try:
                    size = float(res)
                except ValueError:
                    pass
                else:
                    if size > 0.0: return size
            else:
                assert 0, "Unknown type returned from __getPoint(): %s" % (typ,)
            self.thanPrter(T["Invalid size. Try again."])


    def thanGudGetAzimuth(self, c1, stat, default=None, statonce="", options=()):
        """Gets a directional angle (azimuth) from user as a point with possible options, or a real number.

        The real number is the azimuth in the unit and spin defined by the
        units command. If a point is given, then the azimuth from point c1 to
        this points is computed, and it is transformed to the unit and spin
        specified by the units command.
        """
        while True:
            res, typ, cargo = self.__getPoint(stat, statonce, strict=False, options=options,
               state=THAN_STATE.LINE, args=(c1,))
            if typ == "o":            #This includes Canc
                return res
            elif typ == "v":
                c2 = res
                size = hypot(c2[1]-c1[1], c2[0]-c1[0])
                if size > 0.0:
                    theta = atan2(c2[1]-c1[1], c2[0]-c1[0])
                    un = self.thanProj[1].thanUnits
                    return un.rad2unit(theta)
            elif typ == "t":
                if res.strip() == "" and default is not None: res = default
                try:
                    theta = float(res)
                except ValueError:
                    pass
                else:
                    return theta
            else:
                assert 0, "Unknown type returned from __getPoint(): %s" % (typ,)
            self.thanPrter(T["Invalid angle. Try again."])


    def thanGudGetPoint1(self, stat1, statonce="", options=()):
        "Gets a point from user with possible options; use a different cursor."
        return self.__getPoint(stat1, statonce, strict=True, options=options,
               state=THAN_STATE.POINT1)[0]

    def thanGudGetLine(self, c1, stat, statonce="", options=()):
        "Gets a line from user  beginning at c1, with possible options."
        return self.__getPoint(stat, statonce, strict=True, options=options,
               state=THAN_STATE.LINE, args=(c1,))[0]

    def thanGudGetLine2(self, c1, c2, stat, statonce="", options=()):
        "Gets a line dragging 2 lines from user beginning at c1,c2 with possible options."
        return self.__getPoint(stat, statonce, strict=True, options=options,
               state=THAN_STATE.LINE2, args=(c1,c2))[0]


    def thanGudGetRoadP(self, c1, c2, c3, r2, stat, statonce="", options=()):
        "Gets a line/arc combination from user, with possible options."
        res, typres, cargo = self.__getPoint(stat, statonce, strict=True, options=options,
                             state=THAN_STATE.ROADP, args=(c1, c2, c3, r2))
        return res, cargo


    def thanGudGetRoadR(self, c1, c2, c3, r2, stat, statonce="", options=()):
        "Gets a line/arc combination from user, with possible options."
        while True:
            res, typres, cargo = self.__getPoint(stat, statonce, strict=False, options=options,
                state=THAN_STATE.ROADR, args=(c1, c2, c3, r2))
            if typres == "v":                  # coordinates
                from thanvar import calcRoadNodeR
                delta = hypot(res[1]-c2[1], res[0]-c2[0])
                ro = calcRoadNodeR(c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], delta)
                return ro.R
            if typres == "o": return res       # Option or Cancel
            try:
                r = float(res)
                if r > 0.0: return r
            except ValueError:
                pass
            if options: statonce = T["Invalid point, positive number or option. Try again.\n"]
            else:       statonce = T["Invalid point or positive number. Try again.\n"]
            self.thanCom.thanAppend(statonce, "can")
            statonce = ""


    def thanGudGetSplineP(self, c1, c2, stat, statonce="", options=()):
        "Gets next point of a spline curve from user, with possible options."
        res, typres, cargo = self.__getPoint(stat, statonce, strict=True, options=options,
            state=THAN_STATE.SPLINEP, args=(c1, c2))
        return res, cargo


    def thanGudGetMovend(self, c1, stat, elems=None, dc=None, direction=None, statonce="", options=()):
        "Gets a vector distance from user, while dragging some elements."
        if elems is None: self.thanGudSetSelClone()
        else:             self.thanGudSetDrag(elems)
        if dc is not None: self.thanGudMoveDrag(dc[0], dc[1])
        return self.__getPoint(stat, statonce, strict=True, options=options,
            state=THAN_STATE.MOVE, args=(c1,None,None,None,direction))[0]


    def thanGudGetImPoint(self, stat1, image=None, ptol=0, threshold=None, statonce="", options=()):
        """Get a point which is in image, or any image; return image too.

        If image==None all active images are searched.
        If ptol>0, (ptol is in local coordinates) then a rectangle +=dx, +=dy
        where dx=dy=ptol in world coordinates is searched.
        if threshold!=None then the point must be part of a curve in image.
        """
        strict = True
        while True:
            cw = self.__getPoint(stat1, statonce, strict=True, options=options,
                state=THAN_STATE.POINT)[0]
            first = None, cw                               # cw may be None
            try: 0.0+cw[0]+cw[1]
            except (IndexError, TypeError): return first   # An option, or anything but point if strict==True
            if image is None: images = self.thanImages
            else:             images = [image]
            rasterFound = False
            for image in images:
                for k in range(ptol+1):
                    wk, _ = self.thanCt.local2GlobalRel(k, k)
                    for dx in -wk,wk:
                        for dy in -wk,wk:
                            cw1 = list(cw)
                            cw1[0] += dx
                            cw1[1] += dy
                            try: jx, iy = image.thanGetPixCoor(cw1)
                            except IndexError: continue
                            if threshold is None: return image, cw1
                            if image[jx, iy]: return image, cw1
                            if not rasterFound:
                                rasterFound = True
                                first = image, cw1    # Nearest raster to thepoint the user clicked
                            if rasterFound: continue
                            rasterFound = True
            if not strict: return first  # We didn't find any curve; return the nearest point with image
            if rasterFound: statonce = T["No curve was found at point. Try Again.\n"]
            else: statonce = T["No raster image found at point. Try again.\n"]
            self.thanCom.thanAppend(statonce, "can")
            statonce = ""

    def thanGudGetPolar(self, cc, r, stat, statonce="", options=()):
        "Gets the angle between x-axis and a dragged line of length r beginning at cc."
        while True:
            res, typres, cargo = self.__getPoint(stat, statonce=statonce, strict=False,
                options=options, args=(cc,None,None,r), state=THAN_STATE.POLAR)
            if typres == "v":              # coordinates
                th = atan2(res[1]-cc[1], res[0]-cc[0])
                return th
            if typres == "o": return res   # Option or Cancel
            try: th = float(res)
            except ValueError: pass
            else: return self.thanProj[1].thanUnits.unit2rad(th)
            if options: statonce = T["Invalid point, angle or option. Try again.\n"]
            else:       statonce = T["Invalid point or angle. Try again.\n"]
            self.thanCom.thanAppend(statonce, "can")
            statonce = ""

    def thanGudGetInclined(self, cc, theta, stat, statonce="", options=()):
        "Gets a line with constant inclination."
        while True:
            res, typres, cargo = self.__getPoint(stat, statonce=statonce, strict=False,
                options=options, args=(cc,None,None,None,theta), state=THAN_STATE.AZIMUTH)
            if typres == "v":              # coordinates
                t = cos(theta), sin(theta)
                d = (res[0]-cc[0])*t[0] + (res[1]-cc[1])*t[1]
                res[:2] = cc[0]+d*t[0], cc[1]+d*t[1]
                return res
            if typres == "o": return res   # Option or Cancel
            try:
                d = float(res)
            except ValueError:
                pass
            else:
                res = list(cc)
                t = cos(theta), sin(theta)
                res[:2] = cc[0]+d*t[0], cc[1]+d*t[1]
                return res
            if options: statonce = T["Invalid point, distance or option. Try again.\n"]
            else:       statonce = T["Invalid point or distance. Try again.\n"]
            self.thanCom.thanAppend(statonce, "can")
            statonce = ""

    def thanGudGetCircle(self, cc, coef, stat, statonce="", options=()):
        "Gets a circle from user, centered at cc."
        while True:
            res, typres, cargo = self.__getPoint(stat, statonce=statonce, strict=False,
                options=options, args=(cc,None,None,None,coef), state=THAN_STATE.CIRCLE)
            if typres == "v":              # coordinates
#                print("GUI answered")
                r = hypot(res[1]-cc[1], res[0]-cc[0])
#                print("GUI answered: r=", r)
                return r
            if typres == "o": return res   # Option or Cancel
            try:
                r = float(res)
                print("CMD answered: r=", r)
                if r > 0.0: return r
            except ValueError:
                pass
            if options: statonce = T["Invalid point, positive number or option. Try again.\n"]
            else:       statonce = T["Invalid point or positive number. Try again.\n"]
            self.thanCom.thanAppend(statonce, "can")
            statonce = ""


    def thanGudGetCircle3(self, cc1, cc2, stat, statonce="", options=()):
        "Gets a circle from user, which passes through points cc1 and cc2 and the point that the user inputs."
        return self.__getPoint(stat, statonce=statonce, strict=False,
                options=options, args=(cc1, cc2), state=THAN_STATE.CIRCLE3)[0]


    def thanGudGetCircle2(self, cc1, stat, statonce="", options=()):
        "Gets a circle from user, which passes through points cc1 and the point that the user inputs."
        return self.__getPoint(stat, statonce=statonce, strict=False,
                options=options, args=(cc1,), state=THAN_STATE.CIRCLE2)[0]


    def thanGudGetArc(self, cc, r, theta1, stat, statonce="", direction=True, options=()):
        """Gets a circular arc from user, centered at cc, radius r and beginning at theta1.

        If direction is True then it returns the direction angle theta2 of the point the user selected.
        If direction is False it returns the difference of the direction angles: theta2-theta1
        """
        clockwise = self.thanProj[1].thanUnits.angldire == -1
        while True:
            res, typres, cargo = self.__getPoint(stat, statonce=statonce, strict=False,
                options=options, args=(cc,None,None,r,theta1,clockwise), state=THAN_STATE.ARC)
            if typres == "v":              # coordinates
                theta2 = atan2(res[1]-cc[1], res[0]-cc[0])
                if direction: return theta2
                else:         return theta2-theta1
            if typres == "o": return res   # Option or Cancel
            try: th = float(res)
            except ValueError: pass
            else: return self.thanProj[1].thanUnits.unit2rad(th)
            if options: statonce = T["Invalid point, angle or option. Try again.\n"]
            else:       statonce = T["Invalid point or angle. Try again.\n"]
            self.thanCom.thanAppend(statonce, "can")
            statonce = ""

    def thanGudGetEllipseB(self, cc, a, theta, stat, statonce="", options=()):
        "Gets the semi-minor axis of a (possibly tilted) ellipse from user, centered at cc."
        while True:
            res, typres, cargo = self.__getPoint(stat, statonce=statonce, strict=False,
                options=options, args=(cc,None,None,a,theta,None), state=THAN_STATE.ELLIPSEB)
            if typres == "v":              # coordinates
#                print("GUI answered")
                r = hypot(res[1]-cc[1], res[0]-cc[0])
#                print("GUI answered: r=", r)
                return r
            if typres == "o": return res   # Option or Cancel
            try:
                r = float(res)
                print("CMD answered: r=", r)
                if r > 0.0: return r
            except ValueError:
                pass
            if options: statonce = T["Invalid point, positive number or option. Try again.\n"]
            else:       statonce = T["Invalid point or positive number. Try again.\n"]
            self.thanPrter(statonce)
            statonce = ""

    def thanGudGetRect(self, c1, stat, statonce="", options=(), *, com=None, ratioxy=(0.0,0.0)):
        "Gets a rectangle from user, beginning at c1."
        #ratioxy[0] is the ratio by which the dx to the left is increasing with respect to the dx on the right
        #ratioxy[1] is the ratio by which the dy to the bottom is increasing with respect to the dy to the top
        return self.__getPoint(stat, statonce, strict=True, options=options,
            state=THAN_STATE.RECTANGLE, args=(c1, None, None, None, com, ratioxy))[0]

    def thanGudGetRectratio(self, c1, stat, ratio, statonce="", options=()):
        "Gets a rectangle from user, beginning at c1 with given ratio height/width."
        while True:
            res, typres, cargo = self.__getPoint(stat, statonce=statonce, strict=False,
                options=options, args=(c1,None,None,None,ratio), state=THAN_STATE.RECTRATIO)
            if typres == "v": return res   # coordinates
            if typres == "o": return res   # Option or Cancel
            try:
                r = float(res)
                if r != 0.0:
                    cc = list(c1)
                    cc[0] += r
                    cc[1] += r*ratio
                    return cc
            except ValueError:
                pass
            if options: statonce = T["Invalid point, nonzero number or option. Try again.\n"]
            else:       statonce = T["Invalid point or nonzero number. Try again.\n"]
            self.thanCom.thanAppend(statonce, "can")
            statonce = ""

    def __getText(self, stat1, default=None, validate=None, statonce="",
        strict=True, options=(), fullopt=False, state=THAN_STATE.TEXT, args=()):
        """Gets a point but allows for options which are returned with the first letter (in lower case).

        1. Read user response.
        2. If user cancelled, return Canc
        3. If it is blank and blank is an option, then return blank.
        4. Otherwise if it is blank and there is a default value
           set the response equal to this default value.
        5. If the response (the real or the default) is equal to an option
           return the option.
        6. If we reached here we have a nontrivial response from the user
           which must be checked if it is legal.
        6. If there is not a validate function, the response is legal and return it.
        7. Otherwise call the validate function and if validation is ok,
           return the validated value.
        8. if validation is NOT ok, but strict==False, we dont't mind and so
           return the (illegal) response.
        9. Otherwise print(error message, and go to step 1.)
        10.statonce is a message that is printed only the first time that this
           function asks for input. If the function asks again for input (in
           case of error, statonce is not printed).
        """
        stat = statonce+stat1
        opts = [opt.strip().lower() for opt in options]
        while True:
            res, cargo = self.thanWaitFor(stat, state, *args)
            if res == Canc: return Canc, "o", None             # The user cancelled
            res1 = str(res).strip().lower()
            if res1 == "" and "" in opts: return "", "o", None # Response blank, and blank is an option
            if res1 == "" and default is not None:
                res = default                                  # Use default value
                res1 = str(res).strip().lower()
            n = len(res1)
            if n == 0:                                         # Check for options
                if "" in opts: return "", "o", None
            else:
                for opt in opts:
                    if res1 == opt[:n]:
                        if fullopt:  return opt,    "o", None
                        else:        return opt[0], "o", None
            if validate is None: return res, "t", cargo        # No validation
            val, stat = validate(res, stat1)
            if val is not None: return val, "v", cargo             # Validation ok
            if not strict: return res, "t", cargo              # We don't mind failed validation
            self.thanCom.thanAppend(stat, "can")
            stat = stat1


    def thanGudGetText(self, stat1, default=None, statonce="", strict=True):
        return self.__getText(stat1, default, statonce=statonce, strict=strict)[0]

    def thanGudGetTextraw(self, stat1, default=None, statonce="", strict=True):
        return self.__getText(stat1, default, statonce=statonce, strict=strict,
            state=THAN_STATE.TEXTRAW)[0]


    def thanGudGetText0(self, stat1, default=None, statonce="", strict=True):
        "Gets nonblank text from user."
        def validate(res, stat1):
            if res.strip() != "": return res, None
            return None, T["Non blank text is required. Try again.\n"]
        return self.__getText(stat1, default, validate, statonce=statonce, strict=strict)[0]

    def thanGudGetOpts(self, stat1, default=None, statonce="", fullopt=False, options=()):
        "Gets text from user which must be one of the options."
        def validate(res, stat1):
            return None, T["Invalid option. Try again.\n"]
        return self.__getText(stat1, default, validate, statonce=statonce, strict=True,
            fullopt=fullopt, options=options)[0]

    def thanGudGetYesno(self, stat1, default=None, statonce="", strict=True):
        "Gets yes/no text from user."
        if default is not None:
            if not p_ggen.isString(default):
                if default: default = "yes"
                else:       default = "no"
        def validate(res, stat1):
            res = res.strip().lower()
            if res[:2] == "ye": return True, None
            if res[:2] == "no": return False, None
            return None, T["Yes or No is required. Try again.\n"]
        return self.__getText(stat1, default, validate, statonce=statonce, strict=strict)[0]


    def thanGudGetOnoff(self, stat1, default=None, statonce="", strict=True):
        "Gets on/off text from user."
        if default is not None:
            if not p_ggen.isString(default):
                if default: default = "on"
                else:       default = "off"
        def validate(res, stat1):
            res = res.strip().lower()
            if res[:2] == "on": return True, None
            if res[:2] == "of": return False, None
            return None, T["On or Off is required. Try again.\n"]
        return self.__getText(stat1, default, validate, statonce=statonce, strict=strict)[0]


    def thanGudGetFloat(self, stat1, default=None, statonce="", strict=True,
        options=(), state=THAN_STATE.TEXT, args=()):
        "Gets a float number from user."
        def validate(res, stat1):
            try:
                val = float(res)
                return val, None
            except ValueError:
                pass
            return None, T["A real number is required. Try again.\n"]
        return self.__getText(stat1, default, validate, statonce=statonce,
            strict=strict, options=options, state=state, args=args)[0]

    def thanGudGetPosFloat(self, stat1, default=None, statonce="", strict=True,
        options=(), state=THAN_STATE.TEXT, args=()):
        "Gets a positive float number from user."
        def validate(res, stat1):
            try:
                val = float(res)
                if val > 0.0: return val, None
            except ValueError:
                pass
            return None, T["A positive real number is required. Try again.\n"]
        return self.__getText(stat1, default, validate, statonce=statonce,
            strict=strict, options=options, state=state, args=args)[0]


    def thanGudGetFloat2(self, stat1, default=None, limits=(None, None), statonce="", strict=True,
        options=(), state=THAN_STATE.TEXT, args=()):
        "Gets a float number from user within limits."
        def validate(res, stat1):
            try:               val = float(res)
            except ValueError: return None, T["A real number is required. Try again.\n"]
            if limits[0] is None:
                if limits[1] is None: return val, None
                if val <= limits[1]: return val, None
            elif limits[1] is None:
                if val >= limits[0]: return val, None
            else:
                if limits[0] <= val <= limits[1]: return val, None
            return None, T["Real number out of range. Try again.\n"]
        return self.__getText(stat1, default, validate, statonce=statonce,
            strict=strict, options=options, state=state, args=args)[0]


    def thanGetElevations(self, nd, stat, default=None):
        "Gets elevations of z and higher dimensions."
        while True:
            res = self.thanGudGetText(stat)
            if res == Canc: return res
            try:
                if res.strip() == "" and default is not None: cz = list(map(float, default))  #works for python2,3
                else:                                         cz = list(map(float, res.split(",")))  #works for python2,3
            except (ValueError, TypeError) as e:
                self.thanPrter(T["Syntax error. Try again."])
                continue
            if len(cz) == nd-2: break
            self.thanPrter(T["Exactly %d elevations must be entered. Try again."] % (nd-2,))
        return cz

    def thanGudGetInt2(self, stat1, default=None, limits=(None, None), statonce="", strict=True):
        "Gets an integer number from user within limits."
        def validate(res, stat1):
            try:
                val = int(res)
                if limits[0] is None and limits[1] is None:
                    return val, None
                elif limits[0] is not None and limits[1] is not None:
                    if limits[0] <= val <= limits[1]: return val, None
                elif limits[0] is not None:
                    if val >= limits[0]: return val, None
                else:
                    if val <= limits[1]: return val, None
                return None, T["Integer number out of range. Try again.\n"]
            except ValueError:
                pass
            return None, T["An integer number is required. Try again.\n"]
        return self.__getText(stat1, default, validate, statonce=statonce, strict=strict)[0]

    def thanGudGetSnapElem(self, stat1, default=None, statonce="", strict=True, options=()):
        "Gets a point from user with possible options."
        def validate(res, stat1):
            "Do not validate anything."
            try: res.thanTkGet
            except: pass
            else: return res, None
            return None, T["Invalid selection or option. Try again.\n"]
        otypes = thancadconf.thanOsnapModes
        otypes1 = otypes.copy()
        otypes.clear()
        otypes["ena"] = otypes["ele"] = True
        self.thanCanvas.thanChs.thanPush(-2)                  # Save previous croshair; set rectangle croshair
        res = self.__getText(stat1, default, validate, statonce, strict, options,
            state=THAN_STATE.SNAPELEM)[0]
        otypes.clear()
        otypes.update(otypes1)
        self.thanCanvas.thanChs.thanPop()                     # Restore previous croshair
        return res

#===========================================================================

    def thanGudGetLayerleaf(self, mes, proj=None):
        "Let the user select a single layer (only leaf layers)."
        if proj is None: proj = self.thanProj
        lt = proj[1].thanLayerTree
        lays = dict((lay.thanGetPathname(), lay) for lay in lt.dilay.values())   #works for python2,3
        names = sorted(lays.keys())      #works for python2,3
        win = p_gtkwid.ThanPoplist(self, names, width=50, title=mes)
        self.thanTkSetFocus()
        if win.result is None: return Canc
        return lays[win.result]


    def thanGudGetLayerleafs(self, mes, proj=None):
        "Let the user select multiple layers (only leaf layers)."
        if proj is None: proj = self.thanProj
        lt = proj[1].thanLayerTree
        lays = dict((lay.thanGetPathname(), lay) for lay in lt.dilay.values())   #works for python2,3
        names = sorted(lays.keys())  #works for python2,3
        win = p_gtkwid.ThanPoplist(self, names, width=50, selectmode=tkinter.EXTENDED, title=mes)
        self.thanTkSetFocus()
        if win.result is None: return Canc
        return [lays[n] for n in win.result]


    def thanGudGetProject(self, mes):
        "Let the user select a single of the currently opened drawings."
        lays = dict((p[0], p) for p in thanfiles.getOpened()[1:])
        names = sorted(lays.keys())   #works for python2,3
        win = p_gtkwid.ThanPoplist(self, names, width=50, title=mes)
        self.thanTkSetFocus()
        if win.result is None: return Canc
        return lays[win.result]


    def thanGudGetProjectlay(self, mes):
        "Let the user select a single layer of one of the currently opened drawings."
        projlays = {}
        for proj in thanfiles.getOpened()[1:]:
            lt = proj[1].thanLayerTree
            for lay in lt.dilay.values():   #works for python2,3
                nam = "%s::%s" % (proj[0], lay.thanGetPathname())
                projlays[nam] = (proj, lay)
        names = sorted(projlays.keys())   #works for python2,3
        win = p_gtkwid.ThanPoplist(self, names, width=60, title=mes)
        self.thanTkSetFocus()
        if win.result is None: return Canc, Canc
        return projlays[win.result]


    def thanGudGetText1(self, mes, textDefault):
        "Accepts a nonblank text via a modal window."
        self.update_idletasks()     # Experience showed that there should be no pending
                                    # Tk jobs when we show a modal window.
                                    # _idletasks breaks WinDoze (98?) support. Skotistika
        while True:
            #ans = simpledialog.askstring("Please enter text", mes,
            ans = p_gtkwid.askstring("Please enter text", mes,
                initialvalue=p_ggen.thanUnicode(textDefault), parent=self)
            if ans is None: return Canc
            if ans != "": return p_ggen.thanUnunicode(ans)
            self.bell()


    def thanGudGetFloat1(self, mes, textDefault):
        "Accepts a real number via a modal window."
        self.update_idletasks()     # Experience showed that there should be no pending
                                    # Tk jobs when we show a modal window
                                    # _idletasks breaks WinDoze (98?) support. Skotistika
        ans = simpledialog.askfloat("Please enter a number", mes,
            initialvalue=str(textDefault), parent=self)
        return ans

    def thanGudGetPosFloat1(self, mes, textDefault):
        "Accepts a positive real number via a modal window."
        ans = simpledialog.askfloat("Please enter a positive number", mes,
            initialvalue=str(textDefault), minvalue=0.00000001, parent=self)
        return ans


#============================================================================

    def thanGudGetDisplayed(self):
        "Return all the elements which are drawn on the canvas."
        dc = self.thanCanvas
        cget = dc.gettags
        dc.thanChs.thanPush(-1)                   #Set dummy croshair, so that no croshair objects are on the canvas
        tagel = self.thanProj[1].thanTagel
#        for item in dc.find_all():
#            print(item, dc.type(item), cget(item))
        elems = {tagel[cget(item)[0]] for item in dc.find_all()}
        dc.thanChs.thanPop()                      #Restore croshair
        try: elems.remove(tagel["e0"])            #Remove temporary elements for the selection
        except KeyError: pass
        ft = self.__externalFilterFunc
        if ft is None: return elems
        return {e for e in elems if ft(e)} # If element satisfies the external filter OK


    def thanGudGetSel1(self, xa, ya):
        "Finds 1 element near xa, ya."
        ct = self.thanCt
        xa, ya = ct.global2Local(xa, ya)
        dc = self.thanCanvas
        bpix, hpix =  thancadconf.thanBSEL//2, thancadconf.thanBSEL//2
        self.thanProj[2].thanCanvas.thanCh.thanDisable()
        items = list(dc.find_overlapping(xa-bpix, ya-hpix, xa+bpix, ya+hpix))
        items.reverse()     # Tkinter places the most recently drawn element to the end of the list
                            # and the last element is probably the one we want to edit. It is also above the
                            # previous elements if they coincide
        tagel = self.thanProj[1].thanTagel
        for item in items:
            if dc.type(item) == "image": continue
#            if dc.type(item) == "polygon": continue
            print("thanGudGetSel1: type=", dc.type(item))
            if self.__externalFilterFunc is None: break
            titem = dc.gettags(item)[0]
            e = tagel[titem]
            if self.__externalFilterFunc(e): break  # If element satisfies the external filter OK
        else:
            self.thanProj[2].thanCanvas.thanCh.thanEnable()
            return 0, 0              # No element found near xa,ya
#        self.thanGudSetSelClear()
        dc.dtag("selall", "sel")                     # Clear tag "sel"
        dc.addtag_withtag("sel", item)
        self.__filtercros()                         # We don't mind that __filtercross() checks again the element with __externalFilterFunc()
        return self.__selCount()                    # because this is done only for 1 element


    def thanGudGetSelWin(self, xa, ya, xb, yb):
        "Gets a selection on a given window."
        ct = self.thanCt
        xa, ya = ct.global2Local(xa, ya)
        xb, yb = ct.global2Local(xb, yb)
        dc = self.thanCanvas
#        self.thanGudSetSelClear()
        dc.dtag("selall", "sel")                     # Clear tag "sel"
        self.thanProj[2].thanCanvas.thanCh.thanDisable()
        items = dc.addtag_enclosed("sel", xa, ya, xb, yb)
#       No need to avoid selecting the raster of ThanImage, because all the raster must be enclosed, in order to be selected
        print("filterwin started"); t1 = time.time()
        self.__filterwin()
        print("filterwin ended:", time.time()-t1)
        return self.__selCount()

    def __selCount(self):
        "Updates and counts the selected ThanCad elements."
#        cget = self.thanCanvas.itemcget
        cget = self.thanCanvas.gettags
        tagel = self.thanProj[1].thanTagel
        self.thanSel = set(tagel[cget(item)[0]] for item in self.thanCanvas.find_withtag("sel"))
        nselect = len(self.thanSel)
        nduplic = nselect - len(self.thanSel - self.thanSelall)
        self.thanSelall |= self.thanSel
        self.thanProj[2].thanCanvas.thanCh.thanEnable()
        return nselect, nduplic

    def thanGudGetSelOld(self):
        "Updates and counts the selected ThanCad elements."
        dc = self.thanCanvas
        dc.dtag("selall", "sel")                     # Clear tag "sel"
        dc.addtag_withtag("sel", "selold")  # Add sel to all previously selected items
        dc.addtag_withtag("selall", "sel")  # Add selall to all selected items
        self.thanSel = self.thanSelold
        nselect = len(self.thanSel)
        nduplic = nselect - len(self.thanSel - self.thanSelall)
        self.thanSelall |= self.thanSel
        return nselect, nduplic

    def __filterwinold(self):
        """Discards 'compound' items that are not completely within the window.

        Some of ThanCad's elements, for now points and texts (and all the
        elements with dashed lines in the future), are represented by more
        than one Tkinter items. In select window, we must make sure that all
        the items of a single compound element are present within the window.
        If they are not, the element and its correspondig items are deleted
        from the selection.
        """
        dc = self.thanCanvas
        dc.addtag_withtag("sel1", "sel")  # Add sel1 to all items within selection window
#        print("elements selected=", dc.find_withtag("sel1"))
#        print("noncompound elements=", dc.find_withtag("nocomp"))
        dc.dtag("nocomp", "sel1")              # Delete sel1 from items of non-compound elements
        items = set(dc.find_withtag("sel1"))   # All items of compound elements within selection window
#        print("Items compound=", items)
        while len(items) > 0:
            for item in items: break
#            titem = dc.itemcget(item, "tags").split()[0]
            titem = dc.gettags(item)[0]
            items1 = set(dc.find_withtag(titem)) # These are the items of a single ThanCad (compound) element
            if not items1 <= items:              # If items1 is not subset of items, then the ThanCad element..
                dc.dtag(titem, "sel")            # .. is removed from selection
            items -= items1
#            items.difference_update(items1)
        dc.dtag("all", "sel1")
        if self.__externalFilterFunc is not None: self.__filterexternal()
        dc.addtag_withtag("selall", "sel")  # Add selall to all selected items


    def __filterwin(self):
        """Discards 'compound' items that are not completely within the window.

        Some of ThanCad's elements, for now points and texts (and all the
        elements with dashed lines in the future), are represented by more
        than one Tkinter items. In select window, we must make sure that all
        the items of a single compound element are present within the window.
        If they are not, the element and its corresponding items are deleted
        from the selection.
        """
        dc = self.thanCanvas
        items1 = {}
        for item in dc.find_all():
            tags = dc.gettags(item)
            if len(tags) == 0: continue   #Avoid osnap symbols  #Thanasis2021_11_28
            titem = tags[0]
            try: items1[titem].add(item)     # These are the items of a single ThanCad (compound) element
            except KeyError: items1[titem] = set((item,))

        dc.addtag_withtag("sel1", "sel")     # Add sel1 to all items within selection window
        dc.dtag("nocomp", "sel1")            # Delete sel1 from items of non-compound elements
        items = set(dc.find_withtag("sel1")) # All items of compound elements within selection window
        while len(items) > 0:
            for item in items: break
            titem = dc.gettags(item)[0]
            items2 = items1[titem]           # I use this instead of items2=dc.find_withtag(titem), because it is 30 times faster
            if not items2 <= items:          # If items1 is not subset of items, then the ThanCad element..
                dc.dtag(titem, "sel")        # .. is removed from selection
            items -= items2
        dc.dtag("all", "sel1")
        if self.__externalFilterFunc is not None: self.__filterexternal()
        dc.addtag_withtag("selall", "sel")   # Add selall to all selected items


    def __filterexternal(self):
        "Removes elements that do not satisfy external filter."
        dc = self.thanCanvas
        items = set(dc.find_withtag("sel"))  # Find all geometricall selected items
        tagel = self.thanProj[1].thanTagel
        while len(items) > 0:
            for item in items: break
            titem = dc.gettags(item)[0]
            items1 = set(dc.find_withtag(titem)) # These are the items of a single ThanCad (compound) element
            e = tagel[titem]
            if not self.__externalFilterFunc(e):  # If element does not satisfy the external filter it..
                dc.dtag(titem, "sel")             # .. is removed from selection
            items -= items1


    def thanGudGetSelCros(self, xa, ya, xb, yb):
        "Gets a selection on a given crossing window."
        ct = self.thanCt
        xa, ya = ct.global2Local(xa, ya)
        xb, yb = ct.global2Local(xb, yb)
        dc = self.thanCanvas
#        self.thanGudSetSelClear()
        dc.dtag("selall", "sel")                     # Clear tag "sel"
        self.thanProj[2].thanCanvas.thanCh.thanDisable()
        dc.addtag_overlapping("sel", xa, ya, xb, yb)
#       We need to avoid selecting the raster of ThanImage
        print("filtercros started"); t1 = time.time()
        self.__filtercros()
        print("filtercros ended:", time.time()-t1)
        return self.__selCount()


    def __filtercrosold(self):
        """Ensures that 'compound' items partialy within the window, are completely selected.

        Some of ThanCad's elements, for now points and texts (and all the
        elements with dashed lines in the future), are represented by more
        than one Tkinter items. In select crossing, we must make sure that if
        one of the items of a single compound element are present within the
        window, then all must be selected. If not all selected, the nonselected
        items are forced into the selection.
        """
        dc = self.thanCanvas
        tagseen = set()
        dc.addtag_withtag("sel1", "sel")  # Add sel1 to all items within selection window
#        print("elements selected=", dc.find_withtag("sel1"))
#        print("noncompound elements=", dc.find_withtag("nocomp"))
        dc.dtag("nocomp", "sel1")         # Delete sel1 from items of non-compound elements
        items = dc.find_withtag("sel1")   # All items of compound elements within selection window
#        print("Items compound=", items)
        for item in items:
            titem = dc.gettags(item)[0]
            if titem in tagseen: continue
            if dc.type(item) == "image": # Do not consider the raster of ThanImage; ..
                dc.dtag(item, "sel")     # ..it will be selected only if the bounding rectange is selected..
                continue                 # ..tagseen ensures that the bounding rectangle has not yet been seen
            tagseen.add(titem)
            dc.addtag_withtag("sel", titem)
        dc.dtag("all", "sel1")
        if self.__externalFilterFunc is not None: self.__filterexternal()
        dc.addtag_withtag("selall", "sel")  # Add selall to all selected items


    def __filtercros(self):
        """Ensures that 'compound' items partialy within the window, are completely selected.

        Some of ThanCad's elements, for now points and texts (and all the
        elements with dashed lines in the future), are represented by more
        than one Tkinter items. In select crossing, we must make sure that if
        one of the items of a single compound element are present within the
        window, then all must be selected. If not all selected, the nonselected
        items are forced into the selection.
        """
        dc = self.thanCanvas
        items1 = {}
        for item in dc.find_all():
            tags = dc.gettags(item)
            if len(tags) == 0: continue   #Avoid osnap symbols  #Thanasis2021_11_28
            titem = tags[0]
            try: items1[titem].add(item)  # These are the items of a single ThanCad (compound) element
            except KeyError: items1[titem] = set((item,))
        items2add = []

        tagseen = set()
        dc.addtag_withtag("sel1", "sel")  # Add sel1 to all items within selection window
        dc.dtag("nocomp", "sel1")         # Delete sel1 from items of non-compound elements
        items = dc.find_withtag("sel1")   # All items of compound elements within selection window
        for item in items:
            titem = dc.gettags(item)[0]
            if titem in tagseen: continue
            if dc.type(item) == "image": # Do not consider the raster of ThanImage; ..
                dc.dtag(item, "sel")     # ..it will be selected only if the bounding rectange is selected..
                continue                 # ..tagseen ensures that the bounding rectangle has not yet been seen
            tagseen.add(titem)
#            dc.addtag_withtag("sel", titem)
            items2add.extend(items1[titem])
        for item in items2add: dc.addtag_withtag("sel", item)
#        dc.addtag_withtag("sel", items2add)   # A single addtag_withtag is 30 times faster than many
        dc.dtag("all", "sel1")
        if self.__externalFilterFunc is not None: self.__filterexternal()
        dc.addtag_withtag("selall", "sel")  # Add selall to all selected items


    def thanGudGetSelLayers(self, lays):
        "Gets a selection on a given set of layers."
        dc = self.thanCanvas
        dc.dtag("selall", "sel")                     # Clear tag "sel"
        for lay in lays:
            dc.addtag_withtag("sel", lay.thanTag)
        dc.addtag_withtag("selall", "sel")  # Add selall to all selected items
        if self.__externalFilterFunc is not None: self.__filterexternal()
        return self.__selCount()


    def prtags(self, stag="all"):
        "Print Item tags of all items with tag stag."
        dc = self.thanCanvas
        print("Item tags of all items with tag '"+stag+"'")
        for item in dc.find_withtag(stag):
            print(item, ":", dc.gettags(item))


if __name__ == "__main__":
    print(__doc__)
