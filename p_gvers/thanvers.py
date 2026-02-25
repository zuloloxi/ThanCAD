from __future__ import print_function
#from past.builtins import xrange
#from builtins import input
from p_ggen.py23 import xrange, input
import collections
from p_ggen import ThanStub
import p_gtkwid
from . import thanlic
from .thanverstrans import T

NA = T["(Not available)"]
SENTCOM = 78*("#")


def commentize(s, encoding=None):   #encoding="iso-8859-7"):
    "Transform a multiline string s to python comment."
    dlines = s.split("\n")
    for i in xrange(len(dlines)):
        dlines[i] = "# " + dlines[i]
    for i in (0, -1):
        if dlines[i].strip() == "#": dlines[i] = SENTCOM
        else:                        dlines.insert(i, SENTCOM)
    if encoding is not None:
        dlines.insert(0, "# -*- coding: %s -*-" % (encoding,))
    return "\n".join(dlines)


class ThanVersion:
    fields = """name  version  author  author_email  url  description  download_url
               long_description  date  dates  city  address1  address2  phone
               copyright  company  company_url
               company_email  company_address1  company_address2  company_phone
               license  help  history
               title  short_info  about  about_source""".split()
#   description should be an one line (short) description of the program

    def setup(self, **kw):
        "Sets information about the program."
        for att in self.fields:
            att = att.strip()
            v = kw.pop(att, NA)
            setattr(self, att, v)
        if len(kw) > 0:
            raise TypeError("Unexpected keyword item '"+kw.popitem()[0]+"'")

        if self.company == NA:
            authorx = self.author
            addressx = self.address1
            emailx = self.author_email
        else:
            authorx = self.company
            addressx = self.company_address1
            emailx = self.company_email

        if self.title == NA:
            self.title = self.name
            if self.version != NA: self.title += " " + self.version
            if self.description != NA: self.title += ": " + self.description

        if self.copyright == NA:
            self.copyright = T["Copyright (C)"] + " "
            if self.dates != NA: self.copyright += self.dates + " "
            self.copyright += authorx
            if self.date != NA: self.copyright += ", "+ self.date

        if self.short_info == NA:
            self.short_info = self.title + "\n\n"+self.copyright + "\n"
            if addressx != NA: self.short_info += addressx + "\n"
            self.short_info += T["URL"]+": " + self.url + "\n" + T["e-mail"]+": " +emailx

        temp1 = self.about
        if self.about == NA:
            self.about = self.short_info
            if self.license != NA: self.about += "\n\n" + self.license[1]
            if self.help == NA: self.help = self.about
            else:               self.help = self.title + "\n" + self.help
            temp1 = self.about   #temp1 is self.about without the history: for about_source
            if self.history != NA: self.about += "\n\nHistory\n" + self.history

        if self.about_source == NA:
            self.about_source = commentize(temp1)

        if self.author != NA:
            t = "\n\n" + 30*" " + self.author
            if self.city != NA: t += "\n" + 30*" " + self.city
            if self.date != NA: t += ", " + self.date
            self.help += t

        if self.license != NA:
            self.license[2] = "%s License:\n\n%s" % (self.name, self.license[2])


    def tkAbout(self, win, font=None):
        "Information about the program."
        p_gtkwid.thanGudHelpWin(win, self.about, "About "+self.name, font=font)


    def tkHelp(self, win, font=None):
        "Information about the program."
        p_gtkwid.thanGudHelpWin(win, self.help, "Help for "+self.name, font=font)


    def tkLicense(self, win, font=None):
        "Information about the license of the program."
        p_gtkwid.thanGudHelpWin(win, self.license[2], self.license[0], font=font)


    def helpMenu(self, win, font2=None):
        "Create a minimal help menu."
        s = ["Help"]
        m = {}
        m["Help"] = \
            [ ("menu", "&Help", "", None, "help"),            # Menu Title
              (ThanStub(self.tkHelp,    win, font2), "&Introduction", "Introduction to "+self.name),
              (ThanStub(self.tkLicense, win, font2), "&License",      self.license[0]),
              (ThanStub(self.tkAbout,   win, font2), "&About",        "Information about "+self.name),
              ("endmenu",),
            ]
        return s, m


    def toexeDetails(self, iconwin=None, icon=None):
        "Return details in the format of toexe program."
        details = collections.defaultdict(str,
            name        = self.name,
  #          version     = self.version,
            version     = self.version.split()[0],    #Hack to get the number but not the text: 0.1.2 "xxx" ->0.1.2
            description = self.description,
            author      = self.author,
            author_email= self.author_email,
            url         = self.url,
            iconwin     = iconwin,
            icon        = icon)
        return details



if __name__ == "__main__":
    long_description = \
"""\
ThanCmp
-------

    ThanCmp is a program written in the Python programming language, which
compares 2 directory trees and it reports the differences between them.

    ThanCmp is actually a gui frontend to the standard Python library module
"dircmp". ThanCmp uses the Tkinter gui library so it should run in most
environments which support Python.

    With ThanCmp you can define 2 directories to comapre.
All the differences between the 2 directory tress will be reported to a window.
The differences may be 2 files with different contents, missing files in one
or both directories, different entries with the same name etc. Please see
the documentation of the dircmp standard module for more infromation.

    ThanCmp adds a feature to the standard module; the capability to ignore
case when comparing two file or directory names. This is useful when a diskette
or zipdisk was written by a case insensitive OS, but it is also used in a case
sensitive OS like Linux.

    Finally the comparison may be based on file content which is slow but
most reliable, or on file size and creation time which is fast but not as
reliable.
"""

    help = \
"""\
INTRODUCTION
------------

Thancmp is a graphical frontend to the standard module dircmp which
is provided with the python distribution.

    What is does is very simple. At first you designate two directories,
A and B. For example if you have a directory "myfiles" and you made a
backup of it into a floppy diskette then directories A and B are probably
A="~/myfiles" and B="/mnt/floppy/myfiles".
For windows users directories A and B are probably
A="c:\\myfiles" and B="a:\\myfiles".

    Then you press the compare button. Thancmp checks and reports files
found only in directory A, or in directory B.
Then, it reports all the files which could not be accessed for various
reasons (e.g. they are opened by another application).
Then it compares all the files which are present in both directories
A and B, and it prints any differences it finds.
Finally, the program does all the above for each subdirectory of A and B.


OPTIONS
-------

The following options are available.

1. Compare Method

The program has two different methods to see if two files are identical:
- It compares the time the files were modified, the size of the files,
  and the type of the files. If any of these are different the two files
  are considered different.
- It compares the content of the two files byte by byte. If one or more
  bytes are different, the two files are different.

    The first method is very fast especially for large files. But there is
a remote possibility that a perverted user made a copy of a file,
changed its content but not its size, and then deliberately changed
the time of the modified file to match the time of the original file.
The second method, which is slow, will catch this scenario.
    In conclusion use the first method, unless you expect serious hacking
in your system.

2. Filename case

Windows has the irritating feature that it ignores the case of the
letters which a filename consists of, but it lets the user (or a program)
to write the filename in small or capital letters or mixed.
This means that the following filenames are identical in windows:
        pervertedfile, pervertedFile, PERVERTEDFILE, pErVeRtEdFiLe

    Thus, for windows you should select the "ignore case" option, while
in any other OSes (excluding MACOS X), you should select the
"case counts" option.


DIFFERENCES FROM STANDARD MODULE dircmp
---------------------------------------

Thancmp actually uses a slightly altered version of the standard module
filecmp. The following modifications were made:

1. Minimal code was added to implement the "ignore case" in filenames
for windows.

2. The already existing feature for the "content" option was enabled.
This feature is disabled in standard module, probably for simplicity
reasons in the interface.

3. The output of the module was made fancier. The identical files are
not reported any more. The output was directed to a window.


KNOWN LIMITATIONS
-----------------

1. Non latin letters in filenames

The "ignore case" option (see above), works only for latin letters.
This means that if your OS is Windows, and you have, say, a filename
written in small Greek letters in directory A, and the same filename
written in capital Greek letters in directory B, the program will
always consider them different.

2. Filename mangling

Let us say that your OS is Windows, and that you created a file named
"averylongfilename.txt" in directory A. Then you used an old DOS
program to copy this file to directory B. You will notice that the
filename in directory B changed to "avery~01.txt".
This is called filename mangling.

Thancmp will always consider these files different, so try to be careful
when you copy files, or use a real OS.


LICENSE
-------

Thancmp is distributed under GPL, the GNU General Public License.
You can find information about GPL in:  http://www.gnu.org/licenses/gpl.html
"""
    ver = ThanVersion()
    ver.setup(\
    name              = "ThanCmp",
    version           = "1.3.0",
    author            = "Thanasis Stamos",
    author_email      = "thanasis@astamos.com",
    url               = "www.astamos.com/software/thancmp",
    description       = "Gui frontend to standard library dircmp",
    download_url      = "www.astamos.com",
    long_description  = long_description,

    date              = "January 10, 2004",
    dates             = "2004-2013",
    city              = "Athens",
    address1          = "Athens, Greece, Europe",
    company           = "A. STAMOS S.A.",
    company_url       = "www.astamos.com",
    company_email     = "mail@astamos.com",
    company_address1  = "Athens, Greece, Europe",
    company_phone     = "+210.7454606-7, fax +210.7254608",
    license           = thanlic.STAMOS_INTERNAL(),
    help              = help,
    history           = NA)

    for att in ver.fields:
        print()
        print("=====================================================================================")
        print()
        print(att, "=",)
        v = getattr(ver, att)
        if "\n" in v: print()
        print(v)
        input("Press enter..")
