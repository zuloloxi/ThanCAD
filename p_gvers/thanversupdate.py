##############################################################################
# ThanCad 0.0.4: 2dimensional CAD with raster support for engineers.
# 
# Copyright (C)  30, March 2003  by Thanasis Stamos
# URL:     http://thancad.sourceforge.net
# e-mail:  cyberthanasis@excite.com
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
ThanCad 0.0.4: 2dimensional CAD with raster support for engineers.
This module contains a script which updates the short description,
version, author etc. of ThanCad, which exist as comments in the
beginning of every source file.
"""


import sys
from p_ggen import path
import thanvers

sourcedir = path("/windows/D/progs/thancadtemp/xxx")
sourcefiles = \
[ "thancad.py",
  "thandr/thanarc.py", "thandr/thancirc.py", "thandr/thandr.py",
      "thandr/thanelem.py", "thandr/thanline.py", "thandr/thanpoint.py",
      "thandr/thanregi.py", "thandr/thantext.py",
  "thanexpdxf/thanexpdxf.py",
      "thanexpdxf/dxflib/thandxfatt.py", "thanexpdxf/dxflib/thandxfdra.py",
      "thanexpdxf/dxflib/thandxfgeo.py", "thanexpdxf/dxflib/thandxfini.py",
      "thanexpdxf/dxflib/thandxflin.py", "thanexpdxf/dxflib/thandxfsym.py",
  "thanfonts/thanfont.py", "thanfonts/thanfontpolygon.py",
      "thanfonts/thanfontprime.py", "thanfonts/thansymbol.py",
      "thanfonts/utils.py",
  "thangui/thanfiles.py", "thangui/thanguiutil.py",
      "thangui/thanguiwindraw.py", "thangui/thanguiwinmain.py",
  "thanimp/thanimpsyk.py",
  "thanimpdxf/thanimpdxf.py", "thanimpdxf/thanimpdxfent.py",
      "thanimpdxf/thanimpdxfhead.py", "thanimpdxf/thanimpdxftab.py",
      "thanimpdxf/thanimpdxftra.py",
  "thanlayer/thanlayatts.py", "thanlayer/thanlayer.py",
  "thantk/tkut.py",
      "thantk/thantkclist/thantkcli.py", "thantk/thantkclist/thantkclist.py",
  "thantkgui/thantkconst.py", "thantkgui/thantkguicoor.py",
      "thantkgui/thantkguihighdraw.py", "thantkgui/thantkguihighget.py",
      "thantkgui/thantkguilowget.py", "thantkgui/thantkguiwindraw.py",
      "thantkgui/thantkguiwinmain.py", "thantkgui/thantkutil.py",
  "thanvar/thanutila.py",
  "thanvers/thanvers.py", "thanvers/thanversupdate.py",
]

oldersourcefiles = \
[ "thanimp/thanimpdxf.py",
  "thanquadxxx/thanhalf.py", "thanquadxxx/thanquadxx.py"
]

thanCadAbout = [ "#"*78 + "\n" ]
for dl in thanvers.thanCadAbout.splitlines(1):
    thanCadAbout.append("# " + dl)
thanCadAbout.append("#"*78 + "\n")

#==========================================================================

def thanUpdateSources():
    "Updates the version number, description and license in the sources."
    
    for f in sourcefiles:
        fpa = sourcedir / f
	print fpa

	fr = file(fpa, "r")
	__skipOldDoc(fr)

	fw = file(fpa+".new", "w")
	__writeNewDoc(fw)
	__writeRest(iterInp, fw)

	fr.close()
	fw.close()

#==========================================================================

def rotateSources():
    "Renames a source to source.bak, and source.new to source."
    for f in sourcefiles:
        fpa = sourcedir / f
	print fpa
	filbak = __getBackupName(fpa)
	fpa.rename(filbak)
	filnew = fpa + ".new"
	filnew.rename(fpa)

#==========================================================================

def __getBackupName(fpa):
    "Skips the doc string which must be long format string and at the first line."
    fbak = fpa + ".bak"
    if not fbak.exists(): return fbak
    for i in xrange(10):
        fbak = fpa + ".bk" + str(i)
        if not fbak.exists(): return fbak
    raise IOError, fpa + ":    Can not create backup file."

#==========================================================================

def __skipOldDoc (fr):
    "Skips the doc string which must be long format string and at the first line."
    for dl in fr:
        if dl.rstrip() == "#"*78: break
        print "    Sentinel comment not found on first line!"
	sys.exit(1)
    else:
        print "    Source file should not be empty!"
	sys.exit()

    for dl in fr:
        if dl.rstrip() == "#"*78: break
	dl = dl.strip()
        if dl == "" or dl[0] == "#": continue
        print "    Between the 2 sentinel comments there should be only comments or blanks."
	sys.exit(1)
    else:
	print "    Sentinel comment not found before end of file!"
        sys.exit(1)

    for dl in fr:
        if dl.rstrip() == '"""\\': break
    else:
	print "    Doc string not found before end of file!"
        sys.exit(1)

    for dl in fr:
        break
    else:
	print "    Doc string does not exist!"
        sys.exit(1)

#==========================================================================

def __writeNewDoc (fOut):
    "Writes description of the project and the new doc string."

    for dl in thanCadAbout: fOut.write(dl)
    fOut.write('\n"""\\\n')
    fOut.write(thanvers.thanCadShortDesc+"\n")

#==========================================================================

def __writeRest (iterInp, fOut):
    "Copies the rest of the source file."
    for dl in iterInp:
        fOut.write(dl.rstrip()+'\n')

#==========================================================================

print __doc__
#thanUpdateSources()
print "--------------------------------------------"
rotateSources()
