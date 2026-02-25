import time, copy
from xml.etree.ElementTree import ElementTree, XMLParser


class SarTime:
    "Hold seconds to different variable to avoid loss of precision."
    def __init__(self, timeutc):
        """Hold a utc time of the TerraSar data.

        The data is in the format: 
            2009-02-02T04:20:06.459857Z
        The final Z is optional. The data is transformed to seconds since epoch.
        Since the seconds are about 1 billion (10 digits) and the data specifies
        6 decimal digits, the standard double can not represent the time with
        the necessary precision.
        Thus we hold the seconds which correspond to to year,month,day,hour and minutes, 
        in the (integer) isec variable.
        The seconds of the data are held in the (double) rsec variable.
        In order to do computations, we subtract a SarTime from a minimum values.
        The subtraction yields seconds as a double number, which does not exceed
        the value 100, so it has sufficient precision."""
        self.timeutc = timeutc
        i = timeutc.find(":")
        i = timeutc.find(":", i+1)
        st = time.strptime(timeutc[:i], "%Y-%m-%dT%H:%M")  #may raise ValueError
        t = time.mktime(st)
        self.isec = int(t+0.5)
        assert abs(t-self.isec) < 0.01, "Something wrong in epoch"
        if timeutc[-1].lower() == "z": self.rsec = float(timeutc[i+1:-1])  #may raise ValueError
        else:                          self.rsec = float(timeutc[i+1:])    #Terminator 'Z' is optional

    def __sub__(self, other):
        "Because isec is integer no roundoff error is introduced."
        if not isinstance(other, SarTime):
            raise TypeError( "Don't know how to subtract %s from SarTime" % type(other))
        return (self.isec-other.isec) + (self.rsec-other.rsec)

    def __str__(self):
        "String representation."
        return "(%s+%s)" % (self.isec, self.rsec)


    def __repr__(self):
        "Return a representation of self which can be used to rebuild the object."
        return self.timeutc


def pathElementTree(element=None, file=None):
    """Creates a PathElementTree object from an ElementTree or a filename or a File object."

        July 8, 2012
        For some reason, when there is something like:
            xmlns:kml="http://www.opengis.net/kml/2.2"
        in the root element, then the Element() and ElementTree() objects put a
        prefix (the same for every element) before the pathname:
            <Element '{http://www.opengis.net/kml/2.2}kml' at 0xe4cd50>
            <Element '{http://www.opengis.net/kml/2.2}Document' at 0xe4cd90>
            <Element '{http://www.opengis.net/kml/2.2}name' at 0xe4cdd0>
        For this reason, if the root element of the ElementTree() has a prefix
        surrounded by {}, we store the prefix and prepend it automatically
        when we search for other elements (if the element does not already have it).
    """
    if element is not None:
        tree = element
    elif file is not None:
        tree = ElementTree() 
        tree.parse(file, parser=XMLParser()) #Thanasis2016_12_24:We don't override encoding in the xml file.
                            #may raise xml.parsers.expat.ExpatError if tree not understood by parser..
                            #.. or xml.etree.ElementTree.ParseError if fn is not XML, or IOError if..
    else:                   #.. or ValueError see below
        raise ValueError("either element or file must be defined.")
    root = tree.getroot()
    name = root.tag
    i1 = name.find("{")
    i2 = name.find("}")
    if i1 >=0 and i2 >= 0: pref = name[i1:i2+1]
    else:                  pref = ""
    e = _PathElementTree(tree, pa="", pref=pref)
    return e


class _PathElementTree:
    "Path and element tree object together."

    def __init__(self, elem, pa="", pref=""):
        "Store path and element object and prefix."
        self.path = pa
        self.elem = elem
        self.pref = pref


    def apref(self, name):
        "Add prefix if not already there."
        if self.pref == "": return name
        dns = name.split("/")
        for i,dn in enumerate(dns):
            i1 = dn.find("{")
            i2 = dn.find("}")
            if i1 >=0 and i2 >= 0: continue    #dn already has prefix
            dns[i] = self.pref+dn
        return "/".join(dns)


    def find(self, child_path):
        "Find child in parent."
        pn = self.apref(child_path)
        child_elem = self.elem.find(pn)
        if child_elem is None: return None
        return _PathElementTree(child_elem, "/".join((self.path, child_path)), self.pref)


    def findall(self, child_path):
        "Find all children in parent."
        return [_PathElementTree(child_elem, "/".join((self.path, child_path)), self.pref) \
                for child_elem in self.elem.findall(self.apref(child_path))]


    def findr(self, child_path):
        "Find child in parent and raise exception if not found."
        child_elem = self.elem.find(self.apref(child_path))
        p = "/".join((self.path, child_path))
        if child_elem is None: raise IndexError("'%s' element not found" % (p,))
        return _PathElementTree(child_elem, p, self.pref)


    def floatr(self, child_path):
        "Find child in parent, convert to float and raise exception if not found or error."
        child_elem = self.elem.find(self.apref(child_path))
        p = "/".join((self.path, child_path))
        if child_elem is None: raise IndexError("'%s' element not found" % (p,))
        try: return float(child_elem.text)
        except Exception: raise ValueError("'%s' element is not float: %s" % (p, child_elem.text))


    def intr(self, child_path):
        "Find child in parent, convert to integer and raise exception if not found or error."
        child_elem = self.elem.find(self.apref(child_path))
        p = "/".join((self.path, child_path))
        if child_elem is None: raise IndexError("'%s' element not found" % (p,))
        try: return int(child_elem.text)
        except Exception: raise ValueError("'%s' element is not integer: %s" % (p, child_elem.text))


    def textr(self, child_path):
        "Find child in parent, and return its text."
        child_elem = self.elem.find(self.apref(child_path))
        p = "/".join((self.path, child_path))
        if child_elem is None: raise IndexError("'%s' element not found" % (p,))
        text = child_elem.text
        if text is None: text = ""
        return text


    def timeutcr(self, child_path):
        "Find child in parent, convert to integer and raise exception if not found or error."
        child_elem = self.elem.find(self.apref(child_path))
        p = "/".join((self.path, child_path))
        if child_elem is None: raise IndexError("'%s' element not found" % (p,))
        try: return SarTime(child_elem.text)
        except ValueError: raise ValueError("'%s': can not convert time to seconds: %s" % (p, child_elem.text))


    def get(self, *args, **kw):
        "Each element may have attributes accessed with dict like methods."
        return self.elem.get(*args, **kw)


    def set(self, *args, **kw):
        "Each element may have attributes accessed with dict like methods."
        return self.elem.set(*args, **kw)


    def write(self, *args, **kw):
        "Write the element tree to a file, opened file"
        return self.elem.write(*args, **kw)


    def clone(self):
        "Make deep copy of self."
        return _PathElementTree(copy.deepcopy(self.elem), self.path, self.pref)


    def append(self, petchild):
        "Append a new child."
        if isinstance(self.elem, ElementTree): elem = self.elem.getroot()
        else:                                  elem = self.elem
        elem.append(petchild.elem)


    def tag(self):
        "Return the name of the current element."
        if hasattr(self.elem, "tag"):
            tag = self.elem.tag
            i1 = tag.find("{")
            i2 = tag.find("}")
            if i1 >=0 and i2 >= 0: tag = tag[:i1]+tag[i2+1:]    #dn has prefix
            return tag
        return ""
