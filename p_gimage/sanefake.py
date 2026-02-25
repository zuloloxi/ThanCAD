import p_ggen
from . import marsfrost

UNIT_DPI = "dpi"

class FakeScanner:
    "An object which fakes a sane scanner object."
    def __init__(self):
        "Create a fake scanner."
        resopt = p_ggen.Struct("resolution")
        resopt.unit = UNIT_DPI
        resopt.constraint = [100, 200, 300]
        self.resopt = resopt
        self.resolution = self.resopt.constraint[0]
    def __getitem__(self, key):
        "Return fakes acsnner's characteristics."
        if key == "resolution": return self.resopt
        raise IndexError(key)
    def close(self):
        "Close the scanner."
        pass
    def scan(self):
        "Scan and return the image as a PIL image."
        return marsfrost.marsfrost()


def init():
    "Initisalise fake sane module."
    pass


def get_devices():
    "Return the name of avilable fake scanners."
    return [["fakescanner"]]


def open(name):
    "Return the default fake scanner object."
    return FakeScanner()
