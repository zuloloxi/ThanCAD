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

Package which creates a fractal for demonstration purposes.
"""
# C fractal using recursion
# FB - 201007187
from math import hypot
from p_ggen import wavelen2rgb
from thandr import ThanLine
from thansupport import thanToplayerCurrent


def fractal(proj1, width, dwav=20.0, cor1=None):
    "Create a colour fractal."
    global cor, proj, lay
    proj = proj1
    cor = cor1
    if cor is None: cor = proj[1].thanVar["elevation"]
    lay = {}

    mx = width -1
    my = width - 1
    if dwav > 0: wav = 380.0-dwav
    else:        wav = 780.0-dwav
    c(mx / 4, my / 4, mx - mx / 4, my / 4, wav, dwav)
    del cor, proj, lay


def c(xa, ya, xb, yb, wav=780.0, dwav=20.0):
    "Recursive line drawing."
    xd = xb - xa
    yd = yb - ya
    d = hypot(xd, yd)
    if d < 2: return
    x = xa + xd * 0.5 - yd * 0.5
    y = ya + xd * 0.5 + yd * 0.5

    wav += dwav
    if wav > 780.0: wav = 780.0
    if wav < 380.0: wav = 380.0
    rgb = tuple(wavelen2rgb(wav, 255))

    draw((xa, ya), (x,  y),  rgb)
    draw((x,  y),  (xb, yb), rgb)
    c(xa, ya, x, y, wav, dwav)
    c(x, y, xb, yb, wav, dwav)


def draw(pa, pb, rgb):
    "Draw a line with color."
    layname = "%03d%03d%03d" % rgb
    if layname not in lay:
        lay[layname] = thanToplayerCurrent(proj, "fractal/"+layname, current=False, moncolor=rgb)
    lay1 = lay[layname]
    lay[layname].thanTkSet(proj[2].than)

    ca = list(cor)
    ca[0] += pa[0]
    ca[1] += pa[1]
    cb = list(cor)
    cb[0] += pb[0]
    cb[1] += pb[1]
    e = ThanLine()
    e.thanSet((ca, cb))

    proj[1].thanElementAdd(e, lay1)                   # thanTouch is implicitely called
    lay1.thanTkSet(proj[2].than)
    e.thanTkDraw(proj[2].than)


if __name__ == "__main__":
    fractal("cred.jpg",  512,  20.0)
    fractal("cblue.jpg", 512, -20.0)
    fractal("cred2.jpg",  1024,  15.0)
    fractal("cblue2.jpg", 1024, -15.0)
#    fractal("cred3.bmp",  2048,  15.0)
