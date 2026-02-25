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

This module defines functions to check the validity of layer names."""
from thanopt.thancon import THANLC
#THANLC="__"

validc = frozenset("_ ~ ! # $ % ^ & ( ) - + [ ] { } . , ;")
whitec = frozenset(" \n\r\t")
replac = "x"                     #replacement character for invalid symbols
sep = THANLC[0]
nsep = len(THANLC)


def checkLayerName(nam):
    r"""Check that this is a valid layer name."

    In ThanCad layer names are Unicode text and thus they can be written in any
    language of the world. The names are written to .thcx files as utf8.
    Some restrictions apply.
    Layer names may be up to 255 Unicode characters long.
    They may contain alphabetical characters, digits, underscores, and some
    special characters: ~ ! # $ % ^ & ( ) - + [ ] { } . , ;

    They may not contain spaces, tabs, newlines or any white characters.
    In particular names can not include the following characters:
        < > / \ “ : ; ? * | = ‘
    They can not include spaces, tabs, newlines or any white characters.
    They can not include 2 consecutive '_'. '__' is the separator of layer and
    sublayer when exporting to other file formats which do not support the
    layer/sublayer concept.
    However, 3 or more consecutive '_' are allowed.
    The first character and the last character can not be '_'

    The layer names are written to .thcx files in utf8 encoding, which can
    encode any Unicode character.

    When the layer names are exported to .dxf files, they written in utf8
    by default, but the user may choose any other encoding, such as ISO-8859-7.
    When the name of a sublayer is exported to .dxf or other files which do not
    support the layer/sublayer concept, the name which is exported is the name
    of the parent layer, followed by 2 underscores '_', and then followed by the
    name of the sublayer.
    """
    if len(nam) <= 0: return "blank name"
    if nam.startswith(THANLC[0]) or nam.endswith(THANLC[0]): return "starts or ends with '{}'".format(THANLC[0])
    for c in nam:
        if c.isalpha(): continue
        if c.isdigit(): continue
        if c in validc: continue
        return "invalid character '{}'".format(c)
    iun1 = -1
    for i in range(len(nam)):
        if nam[i] == sep:
            if iun1 < 0: iun1 = i
        else:
            if iun1 < 0: continue
            if i-iun1 == nsep: return "contains {} consecutive '{}".format(nsep, sep)
            iun1 = -1
    return ""


def splitDash2(named):
    """Split to words with layer sublayer separator THANLC ('~~').

    don't split if:
    separator is in the start of named
    separator is in the end of named
    there are less or more characters '~' than the length of THANLC."""
    dl = []
    iprev = 0
    ida = -1
    for i in range(0, len(named)):
        if named[i] == sep:
            if ida == -1: ida = i
        elif ida != -1:
            idb = i
            if ida-iprev > 0 and idb-ida == nsep:
                dl.append(named[iprev:ida])
                iprev = idb
            ida = -1
    dl.append(named[iprev:])
    return dl


def isLayerUniq(nam, nams):
    "Return true if nam is unique, i.e. not in nams."
    namu = nam.lower()
    for nam1 in nams:
        if namu == nam1.lower(): return False
    return True


def repairLayerUniq(nam, nams, forcedigit=False):
    """Try to convert nam to a unique name, ie not in nams.

    if forcedigit, then a number will be appended even if nam is unique."""
    nams = set(nam1.lower() for nam1 in nams)
    if not forcedigit and nam.lower() not in nams: return nam, ""   #nam is already unique
    for i in range(1, 1000):
        namu = "{}{}".format(nam, i)
        if namu.lower() not in nams: return namu, ""
    return None, "Duplicate layer name '{}' could not be renamed to unique name".format(nam)


def repairLayerName(nam):
    "Try to convert a random text to valid layer name."
    nam = nam.strip()
    if len(nam) <= 0: return replac
    if nam.startswith(sep): nam = replac + nam
    if nam.endswith(sep)  : nam = nam + replac
    temp = []
    for c in nam:
        temp.append(c)
        if c.isalpha(): continue
        if c.isdigit(): continue
        if c in validc: continue
        if c in whitec: temp[-1] = "_"
        else:           temp[-1] = replac
    iun1 = -1
    i = 0
    while i < len(temp):
        if temp[i] == sep:
            if iun1 < 0: iun1 = i
        else:
            if iun1 >= 0 and i-iun1 == nsep:
                temp.insert(i, sep)
                i += 1
            iun1 = -1
        i += 1
    return "".join(temp)


def test():
    nams = ["t"]
    for i in range(1, 10000): nams.append("t{}".format(i))
    nams.extend("a_1 a_2".split())
    while True:
        nam = input('Dwse layer name: ')
        nam = nam.strip()
        print(nam)
        terr = checkLayerName(nam)
        if terr != "":
            print("    Name error:", terr)
            nam = repairLayerName(nam)
            print("    repaired:", nam)
        else:
            print("    Name ", nam, "is ok")

        print(nam)
        nam2, terr = checkLayerUniq(nam, nams)
        if nam2 is None:
            print("    Uniqness error:", terr)
            nam2, terr = repairLayerUniq(nam, nams)
            if nam2 is None: print("    ", terr)
            else:            print("    repaired:", nam2)
        else:
            nam = nam2
            print("    Name ", nam, "is unique")


if __name__ == "__main__":
    test()
