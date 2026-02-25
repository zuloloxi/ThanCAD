from gen import Pyos
from os import path, environ
def appdatadir(APPNAME):
    "Return application data directory for a user."
    if Pyos.Macos:
        from AppKit import NSSearchPathForDirectoriesInDomains
        # http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
        # NSApplicationSupportDirectory = 14
        # NSUserDomainMask = 1
        # True for expanding the tilde into a fully qualified path
        appdata = path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME)
    elif Pyos.Windows:
        appdata = path.join(environ['APPDATA'], APPNAME)
#       also chech LOCALAPPDATA
    else:
        appdata = path.expanduser(path.join("~", "." + APPNAME))
