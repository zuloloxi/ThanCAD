##############################################################################
# ThanCad 0.2.4 "Valencia": 2dimensional CAD with raster support for engineers
# 
# Copyright (C) 2001-2013 Thanasis Stamos, May 26, 2013
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@excite.com
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
ThanCad 0.2.4 "Valencia": 2dimensional CAD with raster support for engineers

Package which provides constants and ThanCad customisation. It also does some tests
to see if ThanCad can run in the python environmenst of host OS.

This module explicitely imports PIL plugins to aid py2exe
which makes an executable for windoze..
..Yeah, windoze "just" works!
"""

try:
    from PIL import Image
except ImportError:
    pass
else:
    #from PIL import ArgImagePlugin
    from PIL import BmpImagePlugin
    from PIL import BufrStubImagePlugin
    from PIL import CurImagePlugin
    from PIL import DcxImagePlugin
    from PIL import EpsImagePlugin
    from PIL import FitsStubImagePlugin
    from PIL import FliImagePlugin
    from PIL import FpxImagePlugin
    from PIL import GbrImagePlugin
    from PIL import GifImagePlugin
    from PIL import GribStubImagePlugin
    from PIL import Hdf5StubImagePlugin
    from PIL import IcnsImagePlugin
    from PIL import IcoImagePlugin
    from PIL import ImImagePlugin
    from PIL import ImtImagePlugin
    from PIL import IptcImagePlugin
    from PIL import JpegImagePlugin
    from PIL import McIdasImagePlugin
    from PIL import MicImagePlugin
    from PIL import MpegImagePlugin
    from PIL import MspImagePlugin
    from PIL import PalmImagePlugin
    from PIL import PcdImagePlugin
    from PIL import PcxImagePlugin
    from PIL import PdfImagePlugin
    from PIL import PixarImagePlugin
    from PIL import PngImagePlugin
    from PIL import PpmImagePlugin
    from PIL import PsdImagePlugin
    from PIL import SgiImagePlugin
    from PIL import SpiderImagePlugin
    from PIL import SunImagePlugin
    from PIL import TgaImagePlugin
    from PIL import TiffImagePlugin
    from PIL import WmfImagePlugin
    from PIL import XbmImagePlugin
    from PIL import XpmImagePlugin
    from PIL import XVThumbImagePlugin
