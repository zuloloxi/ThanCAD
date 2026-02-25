##############################################################################
# ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers
#
# Copyright (C) 2001-2025 Thanasis Stamos, May 20, 2025
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
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
ThanCad 0.9.1 "Students2024": n-dimensional CAD with raster support for engineers

This module initialises the python logging mechanism for ThanCad.
"""

import p_ggen
import logging


def __setup():
    "Set up logging to file - and console."
    root = logging.getLogger("")              # Root logger object
    formatter = logging.Formatter(            # How the messages will be formatted
        fmt='%(name)-12s: %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M')

    console = logging.StreamHandler()         # Output to console
    console.setFormatter(formatter)           # How the messages will be formatted for console output
    console.setLevel(logging.INFO)            # What levels and above to log
    root.addHandler(console)                  # Add console output to root logger

    fn = "thancad.log"
    filnam, terr = p_ggen.configFile(fn, "thancad")
    if filnam is None:
        terr = "%s\nCan not open logging file '%s' in directory '%s'" % (terr, fn, ".thancad")
        root.warning(terr)
        return
    fil = logging.FileHandler(filnam, "a")    # Output to file
    fil.setFormatter(formatter)               # How the messages will be formatted for file output
    fil.setLevel(logging.INFO)                # What levels and above to log
    root.addHandler(fil)                      # Add file output to root logger

__setup()
thanLogTk = logging.getLogger('tk')                     # The root handler with different name
thanLogC  = logging.getLogger("ThanCad computation")    # The root handler with different name
