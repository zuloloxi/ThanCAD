import datetime
from p_ggen import thanUnicode


class ThanValidator:
    "Common validation code."

    def __init__(self, allowblank=False):
        "Just set error messages to no error."
        self.allowblank = allowblank
        self.thanClearErr()

    def thanValidate(self, v):
        "Validate the value v and return the correct value."
        return v

    def thanGet(self, v):
        "Try to return a correct value without validation."
        return v

    def thanSetErr(self, i, t):
        "Set error messages to given error."
        self.thanIerror = i
        self.thanTerror = t

    def thanClearErr(self):
        "Set error messages to no error."
        self.thanIerror = 0
        self.thanTerror = ""

    def thanGetErr(self):
        "Return the text error message."
        return self.thanTerror

    def thanGetIerr(self):
        "Return the code of the error message."
        return self.thanIerror


class ThanValUni(ThanValidator):
    "Validate unicode text."

    def thanValidate(self, v):
        "Validate the value v and return the correct value."
        return thanUnicode(v)

    def thanGet(self, v):
        "Try to return the correct value."
        return thanUnicode(v)


class ThanValUniqname(ThanValidator):
    "Validate string that contains no blanks and it is unique among others."

    def __init__(self, allowblank=False, others=(), terr="Name already exists: "):
        "Just set error messages to no error."
        super().__init__(allowblank)
        self.others = others
        self.terr = terr

    def thanValidate(self, v):
        "Validate the value v and return the correct value."
        v = str(v).strip()
        if v == "" or " " in v or "\n" in v or "\t" in v:
            self.thanSetErr(1, "A string without blanks was expected.")
            return None
        if v in self.others:
            self.thanSetErr(1, self.terr+v)
            return None
        return v


class ThanValBlank(ThanValidator):
    "Validates text or object; the text must not be blank, the object must not be None."

    def thanValidate(self, v):
        "Validate the value v and return the correct value."
        v = super().thanValidate(v)
        try:
            v1 = v.strip()+""   #Check if it is string like
        except:
#           Not stringlike: thus it is object: check that it is not None
            if v is not None: return v
        else:
            #Sring like: check that it is not blank (spaces are non-blank)
            if len(v1) > 0: return v
        self.thanSetErr(1, "A non-blank string, or an object (other than None) was expected.")
        return None


class ThanValPIL(ThanValidator):
    "Validate a filename if it is a valid PIL image (and not degenerate)."

    def thanValidate(self, v):
        "Validate that the raster can be accessed and it is not degenerate."
        #from PIL import Image
        import p_gimage            #24/11/2023
        try:
            im = p_gimage.open(v)  #24/11/2023
            b,h = im.size
            if b<3 or h<3: raise ValueError("Image size too small")
        except Exception as why:
            self.thanSetErr(1, "%s: %s" % (v, why))
            return None
        self.thanClearErr()
        return v


class ThanValEmail(ThanValidator):
    "Validate an email or completely blank."

    def thanValidate(self, v):
        "Validate that the raster can be accessed and it is not degenerate."
        v = str(v).strip()
        self.thanClearErr()
        if v == "":
            if self.allowblank: return v
            self.thanSetErr(1, "Non blank e-mail was expected.")
            return None
        ok = True
        if len(v) <= 7: ok = False
        if len(v) > 50: ok = False
        if " " in v: ok = False
        import re
        if ok and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", v) is not None: return v
        self.thanSetErr(2, "Invalid e-mail.")
        return None


class ThanValDate(ThanValidator):
    "Validate a date and return year (4 digits), month (2 digits), day (2 digits)."

    def thanValidate(self, v):
        "Validate the value v and return the correct value."
        v = str(v).strip()
        if len(v) == 0:
            self.thanClearErr()
            if self.allowblank: return v
            self.thanSetErr(1, "Non blank date was expected.")
            return None
        if "/" in v:   sep = "/"
        elif "-" in v: sep = "-"
        elif "." in v: sep = "."
        else:          sep = " "
        try:
            iday, imon, iyear = map(int, v.split(sep))
        except (IndexError, ValueError, AttributeError):
            self.thanSetErr(1, "Invalid date. Date must be in the form dd/mm/yyyy.")
            return None
        if iyear < 1900 or iyear > 2099:
            self.thanSetErr(2, "Invalid year. 1900-2099 are accepted.\nDate must be in the form dd/mm/yyyy.")
            return None
        if imon < 1 or imon > 12:
            self.thanSetErr(2, "Invalid month. 1-12 are accepted.\nDate must be in the form dd/mm/yyyy.")
            return None
        if iday < 1 or iday > 31:
            self.thanSetErr(11, "Invalid day. 1-31 are accepted.\nDate must be in the form dd/mm/yyyy.")
            return None
        if iday == 31:
            if imon not in (1,3,5,7,8,10,12):
                self.thanSetErr(12, "This month does not have 31 days.")
                return None
        elif iday == 30:
            if imon == 2:
                self.thanSetErr(12, "February does not have 30 days.")
                return None
        elif iday == 29:
            if imon == 2 and not isleap(iyear):
                self.thanSetErr(12, "February does not have 29 days this year.")
                return None
        self.thanClearErr()
        return "%d/%d/%d" % (iday, imon, iyear)


class ThanValDatepython(ThanValidator):
    "Validate a date and datetime.date object."

    def thanValidate(self, v):
        "Validate the value v and return the correct value."
        v = str(v).strip()
        if len(v) == 0:
            self.thanClearErr()
            if self.allowblank: return datetime.date(1900, 1, 1)
            self.thanSetErr(1, "Non blank date was expected.")
            return None
        if "/" in v:   sep = "/"
        elif "-" in v: sep = "-"
        elif "." in v: sep = "."
        else:          sep = " "
        try:
            iday, imon, iyear = map(int, v.split(sep))
        except (IndexError, ValueError, AttributeError):
            self.thanSetErr(1, "Invalid date. Date must be in the form dd/mm/yyyy.")
            return None
        try:
            d = datetime.date(iyear, imon, iday)
        except ValueError as why:
            self.thanSetErr(1, "Invalid date: %s." % (why,))
            return None
        return d


    def thanGet(self, v):
        "Try to return a correct value without validation."
        v = self.thanValidate(v)
        if v is None: return datetime.date(1900, 1, 1)
        return v


def isleap(iyear):
    "Find if the year is leap."
    if iyear % 400 == 0: return True
    if iyear % 100 == 0: return False
    if iyear % 4   == 0: return True
    return False


class ThanValFloat(ThanValidator):
    "Get and validate a float number."

    def num(self, a): return float(a)
    tnumexp = "A float was expected."
    tnumbounds = "bounds should be a tuple of float values."
    tnumbet = "A float was expected between"


    def __init__(self, vmin=None, vmax=None, allowblank=False):
        ThanValidator.__init__(self, allowblank)
        self.thanBounds = vmin, vmax
        if self.thanBounds != (None, None):
            try: self.thanBounds = [self.num(self.thanBounds[i]) for i in (0,1)]
            except (ValueError, IndexError): raise ValueError(self.tnumbounds)


    def thanValidate(self, v):
        "Validate floating point number within optional limits."
        v = str(v).strip()
        if len(v) == 0:
            self.thanClearErr()
            if self.allowblank: return v
            self.thanSetErr(1, "Non blank number was expected.")
            return None
        try: v = self.num(v)
        except (ValueError, AttributeError):  #When trying to int(obj), obj.__trunc__ is called
            self.thanSetErr(1, self.tnumexp)
            return None
        if self.thanBounds != (None, None):
            if v < self.thanBounds[0] or v > self.thanBounds[1]:
                v = [str(self.thanBounds[i]) for i in (0,1)]
                v.insert(0, self.tnumbet)
                self.thanSetErr(1, " ".join(v))
                return None
        self.thanClearErr()
        return v

    def thanGet(self, v):
        try: v = self.num(v)
        except: pass
        return v


class ThanValFloatFortran(ThanValFloat):
    "Get and validate a float number and checks for Fortran idiosyngracies."

    def thanValidate(self, v):
        "Check if exponent is with D instead of E."
        v1 = ThanValFloat.thanValidate(self, v)
        print("fortran:", v1)
        if v1 is not None: return v1
        try: v+""; v.replace
        except: return None     # Not stringlike enough
        print("TRYING FORTRAN:'", v)
        v = v.replace("d", "e")
        v = v.replace("D", "e")
        print("after:", v)
        return ThanValFloat.thanValidate(self, v)


class ThanValFloatBlank(ThanValFloat):
    "Get and validate a float number but allows blank entries."

    def thanValidate(self, v):
        "Accept and return blank entries."
        try:
            t = v.strip() == ""
        except:
            pass                      #v is not a string
        else:
            if t:
                self.thanClearErr()
                return ""
        return ThanValFloat.thanValidate(self, v)


class ThanValInt(ThanValFloat):
    "Get and validate an integer number."
    def num(self, a):
        return int(a)
    tnumexp = "An integer was expected."
    tnumbounds = "bounds should be a tuple of integer values."
    tnumbet = "An integer was expected between"


def test1():
    from tkinter import Tk, Button
    def validates():
        print("a=", b.thanValidate(a.thanGet()),)
        print(b.thanGetErr(), b.thanGetIerr())

    root = Tk()
    from p_gtkwid import ThanEntry
    a = ThanEntry(root, bg="green")
    b = ThanValDate()
    a.grid()
    but = Button(root, text="Validate", command=validates)
    but.grid()
    root.mainloop()
