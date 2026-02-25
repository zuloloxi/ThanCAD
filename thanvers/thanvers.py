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

This module defines various information for ThanCad: version, date,
author, license etc.
"""


thanCadName     = "ThanCad"
thanCadVersion  = '0.2.2 "Urban SAR"'
thanCadDate     = "January 16, 2013"
thanCopyright   = "Copyright (c) 2001-2013"
thanCadURL      = "http://thancad.sourceforge.net"
thanAuthorName  = "Thanasis Stamos"
thanAuthorEmail = "cyberthanasis@excite.com"
thanCadShortDesc = thanCadName + " " + thanCadVersion +\
    ": 2dimensional CAD with raster support for engineers."

#---------------------------------------------------------------------------

thanCadShortInfo = thanCadShortDesc + "\n\n" +\
    thanCopyright + " " + thanAuthorName + ",  " + thanCadDate + "\n" +\
    "URL:     " + thanCadURL + "\n" +\
    "e-mail:  " + thanAuthorEmail

#---------------------------------------------------------------------------

thanGplShortText =\
"""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details (www.gnu.org/licenses/gpl.html).

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

thanCadAbout = thanCadShortInfo + "\n" + thanGplShortText

#---------------------------------------------------------------------------

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
operating system, which represents hudreds of thousands of users.

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
Exprerience showed that it is easy to get lost pressing page-up too many
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
letter, or their first few letters as long as there is no ambiquity with
another command. For example the command "arc" which plots a new circular arc
may be abbreviates as "ar" or "a". On the other hand the command "angle", which
mesaures the angle between 3 arbitrary points, may be abbreviated as "angl",
"ang", or "an", but not as "a", since "a" is abbreviation of the command "arc".


4. Text location ("find" command)

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

5. Angle measurement ("angle" command)

In ThanCad, it is possible to measure the angle between 3 arbitrary points,
using the "angle" command. Surprisingly, this little utility is missing in other
popular CAD systems. ThanCad asks for the corner of the angle, then it asks for
a point on the first side of the angle and a point on the second side of the
angle. Then ThanCad prints the measured angle.
For the moment, the angle is measured in counter-clockwise direction. The units
may be decimal degrees, radians or grad and the precision arbitrary. However,
for the moment there is no way to choose interactively ammong the different
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


"""

#---------------------------------------------------------------------------

thanGplText =\
"""\
		    GNU GENERAL PUBLIC LICENSE
		       Version 2, June 1991

 Copyright (C) 1989, 1991 Free Software Foundation, Inc.
                       59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

			    Preamble

  The licenses for most software are designed to take away your
freedom to share and change it.  By contrast, the GNU General Public
License is intended to guarantee your freedom to share and change free
software--to make sure the software is free for all its users.  This
General Public License applies to most of the Free Software
Foundation's software and to any other program whose authors commit to
using it.  (Some other Free Software Foundation software is covered by
the GNU Library General Public License instead.)  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
this service if you wish), that you receive source code or can get it
if you want it, that you can change the software or use pieces of it
in new free programs; and that you know you can do these things.

  To protect your rights, we need to make restrictions that forbid
anyone to deny you these rights or to ask you to surrender the rights.
These restrictions translate to certain responsibilities for you if you
distribute copies of the software, or if you modify it.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must give the recipients all the rights that
you have.  You must make sure that they, too, receive or can get the
source code.  And you must show them these terms so they know their
rights.

  We protect your rights with two steps: (1) copyright the software, and
(2) offer you this license which gives you legal permission to copy,
distribute and/or modify the software.

  Also, for each author's protection and ours, we want to make certain
that everyone understands that there is no warranty for this free
software.  If the software is modified by someone else and passed on, we
want its recipients to know that what they have is not the original, so
that any problems introduced by others will not reflect on the original
authors' reputations.

  Finally, any free program is threatened constantly by software
patents.  We wish to avoid the danger that redistributors of a free
program will individually obtain patent licenses, in effect making the
program proprietary.  To prevent this, we have made it clear that any
patent must be licensed for everyone's free use or not licensed at all.

  The precise terms and conditions for copying, distribution and
modification follow.

		    GNU GENERAL PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. This License applies to any program or other work which contains
a notice placed by the copyright holder saying it may be distributed
under the terms of this General Public License.  The "Program", below,
refers to any such program or work, and a "work based on the Program"
means either the Program or any derivative work under copyright law:
that is to say, a work containing the Program or a portion of it,
either verbatim or with modifications and/or translated into another
language.  (Hereinafter, translation is included without limitation in
the term "modification".)  Each licensee is addressed as "you".

Activities other than copying, distribution and modification are not
covered by this License; they are outside its scope.  The act of
running the Program is not restricted, and the output from the Program
is covered only if its contents constitute a work based on the
Program (independent of having been made by running the Program).
Whether that is true depends on what the Program does.

  1. You may copy and distribute verbatim copies of the Program's
source code as you receive it, in any medium, provided that you
conspicuously and appropriately publish on each copy an appropriate
copyright notice and disclaimer of warranty; keep intact all the
notices that refer to this License and to the absence of any warranty;
and give any other recipients of the Program a copy of this License
along with the Program.

You may charge a fee for the physical act of transferring a copy, and
you may at your option offer warranty protection in exchange for a fee.

  2. You may modify your copy or copies of the Program or any portion
of it, thus forming a work based on the Program, and copy and
distribute such modifications or work under the terms of Section 1
above, provided that you also meet all of these conditions:

    a) You must cause the modified files to carry prominent notices
    stating that you changed the files and the date of any change.

    b) You must cause any work that you distribute or publish, that in
    whole or in part contains or is derived from the Program or any
    part thereof, to be licensed as a whole at no charge to all third
    parties under the terms of this License.

    c) If the modified program normally reads commands interactively
    when run, you must cause it, when started running for such
    interactive use in the most ordinary way, to print or display an
    announcement including an appropriate copyright notice and a
    notice that there is no warranty (or else, saying that you provide
    a warranty) and that users may redistribute the program under
    these conditions, and telling the user how to view a copy of this
    License.  (Exception: if the Program itself is interactive but
    does not normally print such an announcement, your work based on
    the Program is not required to print an announcement.)

These requirements apply to the modified work as a whole.  If
identifiable sections of that work are not derived from the Program,
and can be reasonably considered independent and separate works in
themselves, then this License, and its terms, do not apply to those
sections when you distribute them as separate works.  But when you
distribute the same sections as part of a whole which is a work based
on the Program, the distribution of the whole must be on the terms of
this License, whose permissions for other licensees extend to the
entire whole, and thus to each and every part regardless of who wrote it.

Thus, it is not the intent of this section to claim rights or contest
your rights to work written entirely by you; rather, the intent is to
exercise the right to control the distribution of derivative or
collective works based on the Program.

In addition, mere aggregation of another work not based on the Program
with the Program (or with a work based on the Program) on a volume of
a storage or distribution medium does not bring the other work under
the scope of this License.

  3. You may copy and distribute the Program (or a work based on it,
under Section 2) in object code or executable form under the terms of
Sections 1 and 2 above provided that you also do one of the following:

    a) Accompany it with the complete corresponding machine-readable
    source code, which must be distributed under the terms of Sections
    1 and 2 above on a medium customarily used for software interchange; or,

    b) Accompany it with a written offer, valid for at least three
    years, to give any third party, for a charge no more than your
    cost of physically performing source distribution, a complete
    machine-readable copy of the corresponding source code, to be
    distributed under the terms of Sections 1 and 2 above on a medium
    customarily used for software interchange; or,

    c) Accompany it with the information you received as to the offer
    to distribute corresponding source code.  (This alternative is
    allowed only for noncommercial distribution and only if you
    received the program in object code or executable form with such
    an offer, in accord with Subsection b above.)

The source code for a work means the preferred form of the work for
making modifications to it.  For an executable work, complete source
code means all the source code for all modules it contains, plus any
associated interface definition files, plus the scripts used to
control compilation and installation of the executable.  However, as a
special exception, the source code distributed need not include
anything that is normally distributed (in either source or binary
form) with the major components (compiler, kernel, and so on) of the
operating system on which the executable runs, unless that component
itself accompanies the executable.

If distribution of executable or object code is made by offering
access to copy from a designated place, then offering equivalent
access to copy the source code from the same place counts as
distribution of the source code, even though third parties are not
compelled to copy the source along with the object code.

  4. You may not copy, modify, sublicense, or distribute the Program
except as expressly provided under this License.  Any attempt
otherwise to copy, modify, sublicense or distribute the Program is
void, and will automatically terminate your rights under this License.
However, parties who have received copies, or rights, from you under
this License will not have their licenses terminated so long as such
parties remain in full compliance.

  5. You are not required to accept this License, since you have not
signed it.  However, nothing else grants you permission to modify or
distribute the Program or its derivative works.  These actions are
prohibited by law if you do not accept this License.  Therefore, by
modifying or distributing the Program (or any work based on the
Program), you indicate your acceptance of this License to do so, and
all its terms and conditions for copying, distributing or modifying
the Program or works based on it.

  6. Each time you redistribute the Program (or any work based on the
Program), the recipient automatically receives a license from the
original licensor to copy, distribute or modify the Program subject to
these terms and conditions.  You may not impose any further
restrictions on the recipients' exercise of the rights granted herein.
You are not responsible for enforcing compliance by third parties to
this License.

  7. If, as a consequence of a court judgment or allegation of patent
infringement or for any other reason (not limited to patent issues),
conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot
distribute so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you
may not distribute the Program at all.  For example, if a patent
license would not permit royalty-free redistribution of the Program by
all those who receive copies directly or indirectly through you, then
the only way you could satisfy both it and this License would be to
refrain entirely from distribution of the Program.

If any portion of this section is held invalid or unenforceable under
any particular circumstance, the balance of the section is intended to
apply and the section as a whole is intended to apply in other
circumstances.

It is not the purpose of this section to induce you to infringe any
patents or other property right claims or to contest validity of any
such claims; this section has the sole purpose of protecting the
integrity of the free software distribution system, which is
implemented by public license practices.  Many people have made
generous contributions to the wide range of software distributed
through that system in reliance on consistent application of that
system; it is up to the author/donor to decide if he or she is willing
to distribute software through any other system and a licensee cannot
impose that choice.

This section is intended to make thoroughly clear what is believed to
be a consequence of the rest of this License.

  8. If the distribution and/or use of the Program is restricted in
certain countries either by patents or by copyrighted interfaces, the
original copyright holder who places the Program under this License
may add an explicit geographical distribution limitation excluding
those countries, so that distribution is permitted only in or among
countries not thus excluded.  In such case, this License incorporates
the limitation as if written in the body of this License.

  9. The Free Software Foundation may publish revised and/or new versions
of the General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

Each version is given a distinguishing version number.  If the Program
specifies a version number of this License which applies to it and "any
later version", you have the option of following the terms and conditions
either of that version or of any later version published by the Free
Software Foundation.  If the Program does not specify a version number of
this License, you may choose any version ever published by the Free Software
Foundation.

  10. If you wish to incorporate parts of the Program into other free
programs whose distribution conditions are different, write to the author
to ask for permission.  For software which is copyrighted by the Free
Software Foundation, write to the Free Software Foundation; we sometimes
make exceptions for this.  Our decision will be guided by the two goals
of preserving the free status of all derivatives of our free software and
of promoting the sharing and reuse of software generally.

                            NO WARRANTY

  11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
REPAIR OR CORRECTION.

  12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES.

                     END OF TERMS AND CONDITIONS

"""


if __name__ == "__main__":
    print __doc__
