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

This module defines utility functions to change the view port from within
an embedded program.
"""

def thanPan2Points(proj, cp, tol=0.1):
    """Pans the drawing so that all points cp are visible.

    If points are already visible with tolerance, no pan is done.
    Otherwise we try to pan the drawing to make the points visible with
    tolerance.
    If this is not possible, because the points are too far away from each
    other we also zoom out.
    The tolerance 0=<tol<=0.9 is a percentage to the current window."""
    if len(cp) < 1: return
    if tol < 0.0 or tol > 0.9: return
    w, regenImages = proj[2].thanPan2Points(cp, tol)
    if w is None: return       # No pan or zoom
    proj[1].viewPort[:] = w
    proj[2].thanAutoRegen(regenImages)


def thanTextSize(proj, tk, h):
    "Returns the dimensions of the rectangle that the text occupies."
    return proj[2].than.font.thanCalcSizexy(tk, h)
