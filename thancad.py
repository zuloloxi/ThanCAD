#! /usr/bin/python
##############################################################################
# ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2012 Thanasis Stamos,  March 1, 2012
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
ThanCad 0.1.2 "Decade": 2dimensional CAD with raster support for engineers.

"""
print __doc__
developer = 0
if developer and __name__ == "__main__":
    import sys
    if sys.platform == "win32": sys.path.append("x:\\binwi\\libs")         # Developer environment
    else:                       sys.path.append("/home/a12/x/binwi/libs")  # Developer environment
import thanopt             # This runs a test for the needed modules automatically
thanopt.thanInitPregui()
import thantkgui
thanCad = thantkgui.ThanTkGuiWinMain()
thanopt.thanInitPostgui()
#Comment out the following imports to disable importing the packages
#to make ThanCad lighter for common use
import thanpackages
if __name__ == "__main__":
    thanCad.mainloop()
    thanopt.thanInitEndgui()
