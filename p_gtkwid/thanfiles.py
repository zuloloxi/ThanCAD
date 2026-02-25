import sys, os.path, weakref
try: from configparser import SafeConfigParser     #python3.9
except: from configparser import ConfigParser as SafeConfigParser  #python3.12
from .thantkutila import thanExtExpand, thanAbsrelPath

#############################################################################
#############################################################################

class ThanFiles:
    def __init__(self, maxrecent=6, suffix=".txt", config="text"):
        self.__maxrecent = maxrecent
        self.thanSuf = suffix
        self.thanSuf1 = thanExtExpand(suffix)[0][1]
        if sys.platform == "win32":
            windir = os.path.expandvars("$windir")
            if windir != "$windir": self.thanFilini = os.path.join(windir, config+".ini")
            else:                   self.thanFilini = os.path.join(config+".ini")
        else:
            self.thanFilini = os.path.expanduser(os.path.join("~", "."+config))
        self.__idTemp = 0
        self.__openedFiles = []                    # Current drawings
        self.__recentFiles = []                    # Recent saved drawings

        c = SafeConfigParser()
        c.read(self.thanFilini)
        if c.has_option("files", "recent"):
            for f in c.get("files", "recent").split(","):
                f = thanAbsrelPath(f.strip('" \n\t\r'))
                if f is not None: self.__recentFiles.append(f)


    def thanConfigSave(self):
        "Write the recent files into configuration file."
        c = SafeConfigParser()
        c.read(self.thanFilini)
        if not c.has_section("files"): c.add_section("files")
        fs = [os.path.abspath(f) for f in self.__recentFiles]
        fs = '", "'.join(fs)
        if len(fs) > 0: fs = '"' + fs + '"'
        c.set("files", "recent", fs)
        try:
            f = open(self.thanFilini, "w")
            c.write(f)
        except IOError: pass

    def thanTemp(self):
        "Returns a temporary name."

        self.__idTemp += 1
        return "untitled" + str(self.__idTemp) + self.thanSuf1

    def thanOpenedAdd(self, win, fname):
        "Adds a file to the opened files list."

        self.__openedFiles.append((weakref.proxy(win), fname))
#        __notify(exclude=win)
        self.thanOpenedNotify()

    def thanOpenedDel(self, win):
        "Removes a file from the opened files list."

        for i in range(len(self.__openedFiles)):
            if str(win) == str(self.__openedFiles[i][0]): break
        else:
            assert None, "Drawing class instance did not exist in common database!"
        del self.__openedFiles[i]

        for i in range(len(self.__openedFiles)):
            assert str(win) != str(self.__openedFiles[i][0]), "thanfiles: win duplicately declared!"

        self.thanOpenedNotify()

    def thanOpenedGet(self):
        "Returns all the currently opened drawings; file one is the main ThanCad window."

#        return tuple([(t[0](), t[1]) for t in self.__openedFiles])
        return tuple(self.__openedFiles)

    def thanRecentAdd(self, filnam):
        "Adds a file to the recent files list."

        #At first delete the filnam if it exists (possibly many times) in the list

        while 1:
            try: self.__recentFiles.remove(filnam)
            except ValueError: break

        #Now put it in the front of the list and shorten list if it is too big

        self.__recentFiles.insert(0, filnam)
        while len(self.__recentFiles) > self.__maxrecent: self.__recentFiles.pop()
        self.thanRecentNotify()

    def thanRecentGet(self):
        "Returns all the recent files."

        return tuple(self.__recentFiles)

    def thanOpenedNotify(self):
        "Notifies all the windows that something changed in common."

        opened = self.thanOpenedGet()
        for win,f in opened:
            win.thanOpenedRefresh(opened)

    def thanRecentNotify(self, exclude=None):
        "Notifies all the windows that something changed in common."

        recent = self.thanRecentGet()
        for win,f in self.__openedFiles:
            if win != exclude: win.thanRecentRefresh(recent)


def testThanFiles():
    class St(str):
        def thanOpenedRefresh(self, a): pass
        def thanRecentRefresh(self, a): pass
    win1 = St("key1")    #The objects must be alive; only after we call thanOpenedDel can an object deleted
    win2 = St("Key2")
    f = ThanFiles()
    f.thanOpenedAdd(win1, "file1")
    f.thanOpenedAdd(win2, f.thanTemp())
    print(f.thanOpenedGet())
    f.thanOpenedDel(win1)
    print(f.thanOpenedGet())
    f.thanRecentAdd("filk1")
    f.thanRecentAdd(f.thanTemp())
    f.thanRecentAdd("filk2")
    f.thanRecentAdd("filk3")
    f.thanRecentAdd("filk1")
    print(f.thanRecentGet())
