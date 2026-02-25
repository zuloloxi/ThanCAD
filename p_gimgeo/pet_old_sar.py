class PathElementTree:
    "Path and element tree object together."
    def __init__(self, elem, pa=""):
        "Store path and element object."
        self.path = pa
        self.elem = elem
    def find(self, child_path):
        "Find child in parent."
        child_elem = self.elem.find(child_path)
        if child_elem == None: return None
        return PathElementTree(child_elem, "/".join((self.path, child_path)))
    def findall(self, child_path):
        "Find all children in parent."
        return [PathElementTree(child_elem, "/".join((self.path, child_path))) \
                for child_elem in self.elem.findall(child_path)]
    def findr(self, child_path):
        "Find child in parent and raise exeption if not found."
        child_elem = self.elem.find(child_path)
        p = "/".join((self.path, child_path))
        if child_elem == None: raise IndexError, "'%s' element not found" % (p,)
        return PathElementTree(child_elem, p)
    def floatr(self, child_path):
        "Find child in parent, convert to float and raise exeption if not found or error."
        child_elem = self.elem.find(child_path)
        p = "/".join((self.path, child_path))
        if child_elem == None: raise IndexError, "'%s' element not found" % (p,)
        try: return float(child_elem.text)
        except Exception: raise ValueError, "'%s' element is not float: %s" % (p, child_elem.text)
    def intr(self, child_path):
        "Find child in parent, convert to integer and raise exeption if not found or error."
        child_elem = self.elem.find(child_path)
        p = "/".join((self.path, child_path))
        if child_elem == None: raise IndexError, "'%s' element not found" % (p,)
        try: return int(child_elem.text)
        except Exception: raise ValueError, "'%s' element is not integer: %s" % (p, child_elem.text)
    def textr(self, child_path):
        "Find child in parent, and return its text."
        child_elem = self.elem.find(child_path)
        p = "/".join((self.path, child_path))
        if child_elem == None: raise IndexError, "'%s' element not found" % (p,)
        return child_elem.text
    def timeutcr(self, child_path):
        "Find child in parent, convert to integer and raise exeption if not found or error."
        child_elem = self.elem.find(child_path)
        p = "/".join((self.path, child_path))
        if child_elem == None: raise IndexError, "'%s' element not found" % (p,)
        try: return SarTime(child_elem.text)
        except ValueError: raise ValueError, "'%s': can not convert time to seconds: %s" % (p, child_elem.text)
