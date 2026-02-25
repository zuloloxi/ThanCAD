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

This module defines various information for ThanCad: version, date,
author, license etc.
"""

import p_gvers
tcver = p_gvers.ThanVersion()


thanCadRationale =\
"""
INTRODUCTION

Today there are many CAD programs in the market. Some of them could be
considered excellent. The cost, however, to acquire one copy of a CAD program
is very high. If more copies are needed the cost is sky high. For developing
countries the cost is prohibitive.

A part of the CAD that, in my opinion, adds significantly to the cost is
3dimensional support. Today all the leading CAD programs provide real
3dimensional support which in some cases is indispensable. In many cases though
full 3dimensional support is just not needed. A big number of engineering
drawings have no 3dimensional information at all, or, at least, the 3d
information is limited to an elevation attribute, which is not used as a
geometric property. Of course these attributes may be used as geometric
properties to special programs or plugins which interact with the cad
software.

Because the hardware is changing all the time, but mostly because new
Operating System versions and new CAD versions come very frequently,
the cost of CAD software is not something that you pay for once; almost every
year (or less) you must consider to upgrade, or worse, you are forced to
upgrade. The cost of the upgrade is significant. More so if you have many
copies of the CAD.

Real innovation in CAD software is low. Compatibility with a cad version 20 years
ago makes innovation difficult. Some new features are just not compatible with
earlier versions. Others must coexist with obsolete features. Others do almost,
but not entirely the same job with older features. Many engineers would like
this or the other feature to automate their special needs. Embedded scripting
languages help a little, but built-in support is obviously much better. And
there are ideas, like nested layers, which simply can not be done with
embedded languages; they demand restructuring of the whole CAD system - which
is never done.

Usually CAD code is closed. No one can see how it works. No one can find bugs,
no one can correct it, no one can make it more efficient. Everyone depends on
some multinational company to do the corrections, and usually the corrections
take years, if they are made at all.

Many of the CAD programs run only in certain proprietary Operating Systems.
They certainly do not run in GNU/Linux, the leading open source and free
operating system, which represents hundreds of thousands of users.

There are some promising CAD systems that address to these problems. Usually
they have their own user interface, which may be superior to the CAD
which almost monopolizes the market. However, most users know how to work
with this certain CAD interface; they will not bother to learn anything
else, especially if they work for a company and so they don't realize the
cost. On the other hand, the owner of the company is forced to buy this CAD
because most of the users can use it without time consuming and money
consuming training.

There was a solution, named Intellicad, and perhaps it is still a solution.
Intellicad has 2D and 3D capabilities and it was free for download even for
commercial use. Its source code was available. Its user interface is
familiar to everyone. It is highly compatible with the leading CAD system.
It even runs in Linux, actually in WINE, the WINdows Emulator in Linux -
not without difficulty. Unfortunately, some time ago, the consortium which
owns Intellicad decided to charge about 200 euros (or less) for each copy.
This is a very reasonable price and that is why Intellicad is still a solution.
To my knowledge, however, that the source code is still publicly available.
For those few CAD programs that the source code is available, another
difficulty arises. Usually the code is very long, perhaps hundreds of
thousands of lines in C or C++. A new programmer must spend as much as a
year only to get familiar with the code, before they can contribute to the
CAD. This is enough to scare many programmers away. It has certainly scared
me away.


A decision was made to start developing a new CAD program, ThanCad. ThanCad is,
or rather it will be, a 2dimensional CAD with raster support, focused on
engineers. 3d support would complicate it so it was dropped. ThanCad has the
ambition to address all the above problems.

At first ThanCad is free; it is published under the GNU General Public
License (GPL). Anyone is free to copy it as many times as they like, to change
it according to their needs, and to use it in any way they like - under the
terms of GPL (please see GPL for details).

ThanCad will have familiar user interface, so that many users can use it
immediately. There will be extensions for new features of course.

ThanCad is free. You can freely download any newer versions.

ThanCad runs on many OSes including Linux. In fact it runs on any platforms
that Python, Tkinter and PIL is supported. Since Tkinter is present in almost
any Python distribution, ThanCad runs on almost ANY operating system.

ThanCad will encompass many innovations. This is guaranteed because anyone
can change, correct, enhance and add to the code. These enhancements will
be reflected on ThanCad, because of GPL.
For the same reasons, bugs and new features will be addressed very quickly -
perhaps within days.

And last, but not least, ThanCad is written in Python, which, although slow,
it permits to write new code very quickly and compactly. Because the code
is much less and much clearer than it would have been if it was written in
C++, it is far easier to grasp it, to understand it, and modify it, in
very little time.

In fact, ThanCad would not be possible without python. I have tried to
write some code in C++, and I was horrified to see how much more time
consuming and unclear it was.
ThanCad would also not be possible without the current ultra-fast computers
with hundreds of megabytes of memory, because python is rather, rather slow
and memory consuming (newer versions of python try to address these problems).
Even so, ThanCad is slow, but hopefully fast enough for moderate drawings.

Finally it is fun to program in Python, or to program in general, and this
was a main reason for the decision to make a new CAD.
"""

#---------------------------------------------------------------------------


def thancadVersInit(tlang):
    assert tlang in ("gr", "en"), "Unknown language %s" % (tlang,)
    if tlang == "gr": ilang = -1
    else:             ilang = -2

    thanCadHelp =\
"""
1. General

ThanCad tries to support many of the functions of the leading CAD system
with the same interface. So documentation of the leading CAD system is more
or less valid with ThanCad. This is especially true for beginners, as the
relevant theory is the same.
Below there is documentation for some of the features of ThanCad.


2. Drawing navigation

You can navigate through a drawing using pan and zoom. Pan moves the view
window so that you can see the part of the drawing which, previously, was
out of the screen. Zoom enlarges or shrinks the drawing like a magnifying
lens.

2.1 Pan/zoom RealTime

Pan RealTime is the most used form of pan (but not the best in the author's
opinion). You can select pan realtime from the view menu. Notice that the mouse
mouse cursor changes to a hand. Then you press and hold down the left mouse
button. If you move the mouse with the left button pressed (this is called
dragging), the drawing moves in the same direction.
If you release the mouse the pan stops but you are still in pan realtime mode.
You can again press the left mouse button and pan the drawing again.
In order to leave pan realtime mode, release the button and press escape.

    Likewise Zoom RealTime is the most used form of zoom (but not the best in
the author's opinion). You can select zoom realtime from the view menu.
Notice that the mouse cursor changes to a double arrow. Then as you
drag the mouse (i.e. move the mouse with left button pressed)
downwards the drawing is enlarged. If you drag the mouse upwards
the drawing shrinks.
If you release the mouse the zoom stops but you are still in zoom realtime mode.
You can again press the left mouse button and zoom the drawing again.
In order to leave zoom realtime mode, release the button and press escape.

    If you are in pan realtime mode and you have released the button,
you can go directly to zoom realtime mode (without pressing escape and
selecting the zoom realtime from the view menu). Simply click the right mouse
button and you enter zoom realtime mode. Notice that the mouse cursor changes
to double arrow. Right click again and you are again in pan realtime mode.
Notice that the mouse cursor changes to a hand.
Leave either mode pressing escape.

    You can start zoom realtime or pan realtime without the menu. If no other
command is running (i.e the command window shows "command:"), and you
rightclick, a floating menu with the most used commands appears. Zoom realtime
and pan realtime is among them.


3. "Advanced" drawing navigation

This is not "advanced" at all. On the contrary it is elementary. It is
something that most of us have forgotten, the use of the keyboard instead of
the use of the mouse (OK this applies mostly to WinDoze users).

3.1 Pan using the keyboard

The page-up key pans the drawing half a page to the right. The width of the page
is the width of the window that shows the drawing on the screen. Likewise
the page-down key pans the drawing half page to the right.
The control-page-up key pans the drawing half page up. The height of the page
is the height width of the window that shows the drawing on the screen.
Likewise the control-page-down key pans the drawing half page down.

    The reason for mapping page-up/down with the x-direction is that most
of the engineering drawings are long or much longer in the x-direction than
the y-direction. For example the height of the section along the axis of a
road is typically 31 cm, but the width may exceed 2 m.

    None of the above operations will pan the drawing passed its extents.
Experience showed that it is easy to get lost pressing page-up too many
times.

3.2 Zoom using the keyboard

The gray-plus key on the numeric keypad zooms the drawing with a factor of 1.5,
that is it makes the drawing 50% bigger.
Likewise the gray-minus key on the numeric keypad zooms the drawing with a
factor of 1/1.5, that it makes the drawing 33% smaller.
The drawing is zoomed with respect to its center point.

3.3 Other navigation using the keyboard

The home key will pan the drawing so that it makes the lower left part of the
drawing visible. Specifically, the drawing's point with coordinate x
the minimum in the x-direction and coordinate y the minimum in y-direction,
will be shown at lower left corner of the screen (more precisely of the
window). Note that if the drawing is very enlarged (zoomed in) and/or the
lower left part of the drawing is empty, the screen will be blank after
pressing home.

    The control-home key will do the same as the home key, but it will also
shrink the drawing to fit the screen (more precisely to fit the window). Thus
it is identical to the zoom extents command.
NOT YET IMPLEMENTED

3.4 Customisation

The variable keypan contains the number of pages that a page-up/down advances.
The default value is 0.5
The variable keyzoom contains the zoom factor which a gray-plus enlarges the
drawing with. The default value is 1.5 . The gray-minus key uses the reciprocal
of this value.
NOT YET IMPLEMENTED


4. Command abbreviation

The commands that are given on the command line may abbreviated to their first
letter, or their first few letters as long as there is no ambiguity with
another command. For example the command "arc" which plots a new circular arc
may be abbreviates as "ar" or "a". On the other hand the command "angle", which
measures the angle between 3 arbitrary points, may be abbreviated as "angl",
"ang", or "an", but not as "a", since "a" is abbreviation of the command "arc".


5. Text location ("find" command)

Some drawings contain a large number of texts. In such drawings it is difficult
to locate a specific text string by hand. ThanCad has the command "find" which
will locate all the strings which contain a given substring. ThanCad will
display the first match, and then you have the option to zoom into the vicinity
of this text, or proceed to the next match or cancel the location. It is also
possible to go to the previous match. If you press return ThanCad will zoom
into the vicinity of the current match and will terminate the location.
You can try text location by typing "find" on the command line (or "fin" or
"fi" or "f", since ThanCad abbreviates the commands to their first few letters
enough to remove ambiguity).

6. Angle measurement ("angle" command)

In ThanCad, it is possible to measure the angle between 3 arbitrary points,
using the "angle" command. Surprisingly, this little utility is missing in other
popular CAD systems. ThanCad asks for the corner of the angle, then it asks for
a point on the first side of the angle and a point on the second side of the
angle. Then ThanCad prints the measured angle.
For the moment, the angle is measured in counter-clockwise direction. The units
may be decimal degrees, radians or grad and the precision arbitrary. However,
for the moment there is no way to choose interactively among the different
units (although the mechanism is there). You can try to alter the unit in
package (subdirectory) "thandefs", module "thanunits.py". For exaple change
the lines:
        self.anglunit = "deg"               # Unit of angular measurements
        self.angldigs = 4                   # Number of digits to display for angular values
to:
        self.anglunit = "grad"              # Unit of angular measurements
        self.angldigs = 5                   # Number of digits to display for angular values

You can try angle measurement by typing "angle" on the command line (or "angl" or
"ang" or "an", but not "a", since "a" is the abbreviation of "arc".

7. Keyhole Markup Language (KML)

ThanCad can import points defined in Google Keyhole Markup Language
format (.kml or .kmz files), typically used in GoiogleEarth. The KML
stores the points in geodetic coordinates λ, φ of the GRS80 (or WGS84)
ellipsoid. The units of λ,φ are decimal degrees.
The import procedure converts the geodetic coordinates λ,φ of the
.kml file to the easting, northing of the geodetic projections defined
in the ThanCad drawing.
The elevation z is not changed at all, and it may be orthometric or
geometric as defined in the .kml file.

In order to import a .kml file in a projection other than the default
projection (which currently is EGSA87), a new drawing must be created.
The geodetic projection of this new drawing is set to the desired
projection. Then the .kml file is inserted to this drawing.
"""

    long_description = "n-dimensional CAD with raster support for engineers"

    tcver.setup(\
    name              = "ThanCad",
    version           = '0.9.1 "Students2024"',
    author            = "Thanasis Stamos",
    author_email      = "cyberthanasis@gmx.net",
    url               = "http://thancad.sourceforge.net",
    description       = "n-dimensional CAD with raster support for engineers",
    download_url      = "http://sourceforge.net/projects/thancad",
    long_description  = long_description,

    date              = "May 20, 2025",
    dates             = "2001-2025",
    city              = "Athens",
    address1          = "Athens, Greece, Europe",
    license           = p_gvers.GPL(ilang),
    help              = thanCadHelp,
    history           = "See ThanCad's web page http://thancad.sourceforge.net for history.")


if __name__ == "__main__":
    print(__doc__)
