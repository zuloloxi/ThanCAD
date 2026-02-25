import collections
#from typing import Optional, DefaultDict, Tuple, List, Any, Dict
import p_ggen
import p_gtkwid              # type: ignore
from . import thanlic
from .thanverstrans import T

#NA:str = T["(Not available)"]
NA = T["(Not available)"]
#SENTCOM:str = 78*("#")
comc = "#"    #comment character
SENTCOM = comc + 77*("#")


#def commentize(s: str, encoding:Optional[str]=None) -> str:   #encoding="iso-8859-7"):
def commentize(s, encoding=None):   #encoding="iso-8859-7"):
    "Transform a multiline string s to python comment."
    dlines = s.split("\n")
    for i in range(len(dlines)):
        dlines[i] = (comc + " " + dlines[i]).rstrip()
    for i in (0, -1):
        if dlines[i].strip() == comc: dlines[i] = SENTCOM
        else:                         dlines.insert(i, SENTCOM)
    if encoding is not None:
        dlines.insert(0, "%s -*- coding: %s -*-" % (comc, encoding,))
    return "\n".join(dlines)


class ThanVersion:
#    fields = """name  version  author  author_email  url  description  download_url
#               long_description  date  dates  city  address1  address2  phone
#               copyright  company  company_url
#               company_email  company_address1  company_address2  company_phone
#               license  help  history
#               title  short_info  about  about_source""".split()
#   description should be an one line (short) description of the program


    #def __init__(self) -> None:
    def __init__(self):
        "Set default attributes."
        self.name         = NA
        self.version      = NA
        self.author       = NA
        self.author_email = NA
        self.url          = NA
        self.description  = NA
        self.download_url = NA
        self.long_description = NA
        self.date         = NA
        self.dates        = NA
        self.copyrightyear= NA
        self.city         = NA
        self.address1     = NA
        self.address2     = NA
        self.phone        = NA
        self.copyright    = NA
        self.company      = NA
        self.company_url  = NA
        self.company_email= NA
        self.company_address1 = NA
        self.company_address2 = NA
        self.company_phone= NA
        self.license      = [NA, NA, NA]
        self.help         = NA
        self.history      = NA
        self.title        = NA
        self.short_info   = NA
        self.about        = NA
        self.about_source = NA

    def setup(self,
        name         = NA,
        version      = NA,
        author       = NA,
        author_email = NA,
        url          = NA,
        description  = NA,
        download_url = NA,
        long_description = NA,
        date         = NA,
        dates        = NA,
        city         = NA,
        address1     = NA,
        address2     = NA,
        phone        = NA,
        copyright    = NA,
        company      = NA,
        company_url  = NA,
        company_email= NA,
        company_address1 = NA,
        company_address2 = NA,
        company_phone= NA,
        license      = (NA, NA, NA),
        help         = NA,
        history      = NA,
        title        = NA,
        short_info   = NA,
        about        = NA,
        about_source = NA,
        commentchar = "#") -> None:
        "Sets information about the program."
        global comc, SENTCOM
        comc = commentchar
        SENTCOM = comc + 77*("#")
        self.name = name
        self.version = version
        self.author = author
        self.author_email = author_email
        self.url = url
        self.description = description
        self.download_url = download_url
        self.long_description = long_description
        self.date = date
        self.dates = dates
        self.city = city
        self.address1 = address1
        self.address2 = address2
        self.phone = phone
        self.copyright = copyright
        self.company = company
        self.company_url = company_url
        self.company_email = company_email
        self.company_address1 = company_address1
        self.company_address2 = company_address2
        self.company_phone = company_phone
        self.license = list(license)
        self.help = help
        self.history = history
        self.title = title
        self.short_info = short_info
        self.about = about
        self.about_source = about_source

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

        if self.copyrightyear == NA:
            if self.dates != NA:
                try:
                    self.copyrightyear = self.dates.split("-")[1]
                    int(self.copyrightyear)
                except:
                    self.copyrightyear = NA
            if self.copyrightyear == NA:
                self.copyrightyear = p_ggen.copyrightyear

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

        if self.license[0] != NA:
            self.license[2] = "%s License:\n\n%s" % (self.name, self.license[2])


    #def tkAbout(self, win, font=None) -> None:
    def tkAbout(self, win, font=None):
        "Information about the program."
        p_gtkwid.thanGudHelpWin(win, self.about, "About "+self.name, font=font)


    #def tkHelp(self, win, font=None) -> None:
    def tkHelp(self, win, font=None):
        "Information about the program."
        p_gtkwid.thanGudHelpWin(win, self.help, "Help for "+self.name, font=font)


    #def tkLicense(self, win, font=None) -> None:
    def tkLicense(self, win, font=None):
        "Information about the license of the program."
        p_gtkwid.thanGudHelpWin(win, self.license[2], self.license[0], font=font)


    #def helpMenu(self, win, font2=None) -> Tuple[List[str], Dict[str, List[object]]]:
    def helpMenu(self, win, font2=None):
        "Create a minimal help menu."
        s = ["Help"]
        m = {}
        m["Help"] = \
            [ ("menu", "&Help", "", None, "help"),            # Menu Title
              (p_ggen.ThanStub(self.tkHelp,    win, font2), "&Introduction", "Introduction to "+self.name),
              (p_ggen.ThanStub(self.tkLicense, win, font2), "&License",      self.license[0]),
              (p_ggen.ThanStub(self.tkAbout,   win, font2), "&About",        "Information about "+self.name),
              ("endmenu",),
            ]
        return s, m


    #def toexeDetails(self, iconwin=None, icon=None) -> DefaultDict[str, str]:
    def toexeDetails(self, iconwin=None, icon=None):
        "Return details in the format of toexe program."
        #details:DefaultDict[str, str] = collections.defaultdict(str,
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
