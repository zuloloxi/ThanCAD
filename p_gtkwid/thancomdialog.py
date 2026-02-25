"""
This module defines the common parts of dialogs in ThanCad.
"""

import tkinter
try: from configparser import SafeConfigParser     #python3.9
except: from configparser import ConfigParser as SafeConfigParser  #python3.12
import p_ggen
from . import thantksimpledialog, thantkutila
from . import thanwidstrans

uni = p_ggen.thanUnicode


class ThanComDialog(thantksimpledialog.ThanDialog):
    "Some common methods for all ThanCad's dialogs."

    def __init__(self, master, vals=None, cargo=None, translation=None, *args, **kw):
        "Extract initial rectification parameters."
        self.thanValsInit = vals           # This is structure not a scalar
        self.thanProj = cargo
        if translation is None: self.T = thanwidstrans.T
        else:                   self.T = translation
        thantksimpledialog.ThanDialog.__init__(self, master, *args, **kw)


    def thanValsDef(self):
        "Build default values."
        v = p_ggen.Struct("The same name and class as thanValsInit (if specified)")
#        self.thanValsDefICP(v)   # Common ICP parameters
#        v.entName = "NewCamera"
#        v.entFocus= 150.0
        return v


    def thanValsRead(self, v):
        "Read widget values from a file."
#        Override to use the functionality.
#        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".m23")
#        self.thanValsReadFile1(v, fn):


    def thanValsReadFile1(self, v, fn):
        "Reads the values from a file with specific suffix; ."
        if not fn.exists(): return
        self._c = SafeConfigParser()
        self._c.read(fn)
        self._tv = {}
        for (key,tit,wid,vld) in self.thanWids: self._tv[key] = [tit, vld]
        self._v = v

        self.thanValsReadFile2()

        del self._c, self._tv, self._v


    def thanValsReadFile2(self):
        "This does the actual reading from configparser; override."
        return
        #self._tv["radProject"][1] = p_gtkwid.ThanValInt(0, 9)
        #self._tv["radProjApprox"][1] = p_gtkwid.ThanValInt(0, 3)
        #self.thanValsReadICP(c, tv, v)   # Common ICP parameters
        #self.thanValsReadSec(sec="ICP GENERAL PARAMETERS", keys="entDisInt entDisRange entThres entSteps")
        #self.thanValsReadSec(sec="PROJECTION TYPE", keys="radProject")
        #self.thanValsReadSec(sec="PURE PROJECTION APPROXIMATION", keys="radProjApprox entFilcof entNx entNy entNz")


    def thanValsReadSec(self, sec, keys):
        "Read and validate values from a section."
        for key in keys.split():
            tit, val = self._tv[key]
            try:
                test = self._c.get(sec, tit)
                test = val.thanValidate(test)
                if test is not None: setattr(self._v, key, test)
            except:
                pass


    def thanValsWrite(self, v):
        "Write widget values to a file."
#        Override to use the functionality.
#        fn = self.thanProj[0].parent / (self.thanProj[0].namebase + ".m23")
#        self.thanValsWriteFile1(v, fn)


    def thanValsWriteFile1(self, v, fn):
        "Reads the values from a file with specific suffix."
        self._c = SafeConfigParser()
        if fn.exists(): self._c.read(fn)
        self._tv = {}
        for (key,tit,wid,vld) in self.thanWids: self._tv[key] = [tit, vld]
        self._v = v

        self.thanValsWriteFile2()

        print("p_gtwid.thanValsWrite1(): fn=%s  _c=\n%s" % (fn, self._c))
        try: self._c.write(fn.open("w"))
        except: raise; pass
        del self._c, self._tv, self._v


    def thanValsWriteFile2(self):
        "This does the actual writing to configparser."
        self.thanValsWriteICP()   # Common ICP parameters
        self.thanValsWriteSec("ICP GENERAL PARAMETERS", "entDisInt entDisRange entThres entSteps")
        self.thanValsWriteSec("PROJECTION TYPE", "radProject")
        self.thanValsWriteSec("PURE PROJECTION APPROXIMATION", "radProjApprox entFilcof entNx entNy entNz")
        self.thanValsWriteSec("PURE TRANSFORMATION APPROXIMATION", "radTransfApprox")


    def thanValsWriteSec(self, sec, keys):
        "Write a section and the values of some keys."
        if not self._c.has_section(sec): self._c.add_section(sec)
        for key in keys.split():
            tit, val = self._tv[key]
            print("p_gtwid.thanValsWriteSec(): sec=%s  key=%s   val=%s" % (sec, tit, getattr(self._v, key)))
            print("                                %s      %s       %s" % (type(sec), type(tit), type(getattr(self._v, key))))
            self._c.set(sec, tit, str(getattr(self._v, key)))


    def menu(self):
        "Create a menu."
        return None


    @staticmethod
    def choosefg(win):
        "Return blue or cyan, dependinf on the background color of Labels."
        #make a dummy label to find background color, and correct foreground color
        temp = tkinter.Label(win, text="xxx")
        temp.grid()
        win.update_idletasks()
        col = thantkutila.blueorcyan(temp)
        if col is None: col = "blue"  #If could not decide, then use blue as most GUIs have white background
        temp.grid_forget()
        temp.destroy()
        return col


    def body(self, win):
        "Create the body of the dialog; delegate to other functions."
        self.thanWids = []
        self.colfra = self.choosefg(win)   #Choose Frame title color, depending on the background color of Labels
#        self.option_add("*font", _fo)
        self.body2(win)

        win.columnconfigure(0, weight=1)
        for (key,tit,wid,vld) in self.thanWids:
            setattr(self, key, wid)

        if self.thanValsInit is None:
            self.thanValsInit = self.thanValsDef()
            self.thanValsRead(self.thanValsInit)
        self.thanValsSaved = self.thanValsInit.clone()
#        print "init =", self.thanValsInit.__dict__
#        print
#        print "saved=", self.thanValsSaved.__dict__
#        print
#        print self.thanValsInit.anal()
        self.thanSet(self.thanValsInit)
#        self.__projApproxDet()


    def body2(self, win):
        "Create the body of the dialog in steps."
#        self.fraLogo(win, 0, theme=T["Curve Matching Algorithms"], year=2009)
#        self.fraICP(win, 1)
#        self.fraProject(win, 2)
#        self.__stat = p_gtkuti.ThanStatusBar(win)
#        self.__stat.grid(row=3, column=0, sticky="we")


    def validate2(self, strict=True, wids=None, values=None):
        """Returns true if the value chosen by the user is valid.

        If strict == True, then if an error is found, an error message is displayed,
        self.result is unchanged, and False is returned to the caller.
        If strict == True, and no errors are found, self.result is updated with
        the new values. True is returned to the caller.
        If strict == False, then if an error is found, a default value is used
        instead of the wrong one, self.results is set with the new values,
        and False is returned to the caller.
        If strict == False, and no errors are found, then, self.results is set
        with the new values, and True is returned to the caller.
        """
        ret = True
        if values is None: vs = self.thanValsInit.clone()
        else:              vs = values
        if wids is None: wids = self.thanWids
        for key,tit,wid,vld in wids:
            v1 = vld.thanValidate(wid.thanGet())
            if v1 is None:
                ret = False
                if strict:
                    tit = u'"%s":\n%s' % (uni(tit), uni(vld.thanGetErr()))
                    thantkutila.thanGudModalMessage(self, tit, self.T["Error in data"], thantkutila.ERROR)
                    self.initial_focus = wid
                    return ret, None
                else:
                    v1 = getattr(self.thanValsInit, key)
            setattr(vs, key, v1)
        return ret, vs


    def validate(self, strict=True, wids=None, values=None):
        "Returns true if the value chosen by the user is valid."
        ret, vs = self.validate2(strict, wids, values)
        if not ret and strict: return ret
#        icodp = vs.radProject
#        self.projection = Projection(icodp)()
#        if vs.radProjApprox == 2:
#            if not self.__validateReadCoefs(vs.entFilcof, strict=strict): # vs.projection = self.projection  # self.projection is set by __validateReadCoefs()
#                ret = False
#                if strict:
#                    self.initial_focus = self.entFilcof
#                    return ret

#        if len(self.thanGps) != 1:
#            ret = False
#            if strict:
#                p_gtkuti.thanGudModalMessage(self, self.T["1 reference line must be selected"], self.T["Error in data"], p_gtkuti.ERROR)
#                return ret
        self.result = vs
        return ret


    def thanSet(self, vs):
        "Set new values to the widgets."
        stat = tkinter.NORMAL
        for (key,tit,wid,vld) in self.thanWids:
            v = getattr(vs, key)
            if type(v) == float or type(v) == int: v = str(v)
            temp = wid["state"]
            wid.config(state=stat) # All widgets must be enabled..
            wid.thanSet(v)         # ..to change their values
            wid.config(state=temp) # Restore state


    def ok2change(self, mes="Data modified, OK to abandon modifications?"):
        "Checks if data has been changed since last save and ask user to abanodon if so."
        ret = self.validate(strict=False)     # If anything is wrong, then let it be
        if self.result == self.thanValsSaved: return True
        #print("result=", self.result.__dict__)
        #print("saved=", self.thanValsSaved.__dict__)
        a = thantkutila.thanGudAskOkCancel(self, self.T[mes], self.T["WARNING"])
        return bool(a)


    def cancel(self, event=None):
        "Ask before cancel."
        if not self.ok2change(): return # Cancel was stopped
        thantksimpledialog.ThanDialog.cancel(self)


    def cancel_force(self, event=None):
        "Cancel without asking."
        thantksimpledialog.ThanDialog.cancel(self)


    def apply2(self, event=None):
        "In case user pressed apply button, validate results and save values of widgets."
        ret = thantksimpledialog.ThanDialog.apply2(self)
        if not ret: return ret
        self.thanValsSaved = self.result
        return ret


    def destroy(self, *args):
        "Deletes references to widgets, so that it breaks circular references."
        for (key,tit,wid,vld) in self.thanWids:
            delattr(self, key)
        del self.thanProj, self.thanWids, self.thanValsInit, self.thanValsSaved
#        del self.thanLabGps, self.thanLabRel
#        self.__stat.destroy()
#        del self.__stat
        thantksimpledialog.ThanDialog.destroy(self)


    def __del__(self):
        "Print that dialog dies as a debugging aid."
        print("ThanComDialog", self, "dies..")


    def apply(self):
        "Last settings - after successful validation and after the window has been closed."
        self.thanValsWrite(self.result)
