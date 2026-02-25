#! /usr/bin/python
##############################################################################
# ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.
# 
# Copyright (c) 2001-2013 Thanasis Stamos,  January 16, 2013
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
ThanCad 0.2.2 "Urban SAR": 2dimensional CAD with raster support for engineers.

"""
print __doc__
developer = 0
if developer and __name__ == "__main__":
    import platform, sys
    mach = platform.machine().lower()
    Amd64 = ("x86" in mach or "amd" in mach) and "64" in mach  #If machine is x86-64 compatible (OS may still run in 32bits
    mach = sys.platform.lower()
    Windows = mach == "win32" or mach == "win64"       #If we run Windoze
    if Amd64: binp = "binwm"
    else:     binp = "binwi"
    if Windows: sys.path.append("x:\\"+binp+"\\libs")         # Developer environment
    else:       sys.path.append("/home/a12/x/"+binp+"/libs")  # Developer environment
import thanopt             # This runs a test for the needed modules automatically
thanopt.thanInitPregui()
import thantkgui
thanCad = thantkgui.ThanTkGuiWinMain()
thanopt.thanInitPostgui()
#Comment out the following imports to disable importing the packages
#to make ThanCad lighter for common use
if __name__ == "__main__":
    thanCad.mainloop()
    thanopt.thanInitEndgui()
