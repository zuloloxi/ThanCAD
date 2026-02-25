# -*- coding: iso-8859-7 -*-

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

Package which processes commands entered by the user.
This module processes commands related to projection and
transformation of points.
"""

import p_ggen
from p_gsar import Projection, readProj
import thantkdia, thanprofflf
from thanvar import Canc, thanShowFile
from thantrans import Tmatch


def thanEngTransf(proj):
    "Image transformations/projections using control points."
    t = thanprofflf.thanprotkdia.ThanPoTransf(proj[2], vals=None, cargo=proj)
    v = t.result
    del t
    if v == None: return proj[2].thanGudCommandCan()
    if v.radJob == 0:
        __transfCompute(proj, v, proj[2].thanPrter1)
    else:
        __transfCheck(proj, v, proj[2].thanPrter1)
    proj[2].thanGudCommandEnd()


def __transfCheck(proj, v, prt):
    "Compute error of transformation using checkpoints."
    try:
        if v.filProj.lower().endswith(".xml"):
            tra = Projection(v.icodp)()
            tra.readxml(v.filProj)
        else:
            tra = readProj(open(v.filProj))
    except Exception, why:
        print "exception:", why
        prt("%s:\n%s" % (Tmatch["Error while reading transformation file"], why), "can")
        return
    wxyz = 1.0, 1.0                          #Weights for xy and z
    cp = {}                                  #Common points
    for nam, poref in v.cprefch.iteritems():
        poima = v.cpimach.get(nam)
        if poima == None: continue
        cp[nam] = tuple(poref.cc[:3]) + tuple(poima.cc[:3]) + wxyz
    fw, fer = __opensimer(proj, prt)
    if fw == None: return
    er2d, er3d, discom2d = tra.wrer_nodes(cp, fer)
    strd = proj[1].thanUnits.strdis
    prt("%s=%.1f   %s=%s" % (Tmatch["Pixel error"], er2d, Tmatch["3D error"], strd(er3d)))
    per = fer.name
    fer.close()
    fw.close()
    thanShowFile(proj, per, Tmatch["Transfomation error (using checkpoints)"])


def __transfCompute(proj, v, prt):
    "Compute the transformation using control point; check with control points."
    wxyz = 1.0, 1.0                          #Weights for xy and z
    cp = {}                                  #Common points
    for nam, poref in v.cpref.iteritems():
        poima = v.cpima.get(nam)
        if poima == None: continue
        cp[nam] = tuple(poref.cc[:3]) + tuple(poima.cc[:3]) + wxyz
    fots = cp.values()
    tra = Projection(v.radProject)()
    er2d, er3d, discom2d = tra.lsm23(fots)
    if er2d == None:
        prt(Tmatch["Error while computing transformation: Probably due to low number of nodes."], "can")
        return
    strd = proj[1].thanUnits.strdis
    prt("%s=%.1f   %s=%s" % (Tmatch["Pixel error"], er2d, Tmatch["3D error"], strd(er3d)))

    fw, fer = __opensimer(proj, prt)
    if fw == None: return
    tra.write(fw)
    fw.write("\n\n#X,Y,Z of reference line,   x, y, z of secondary line,   weight xy, weight z\n")
    form = 8*"%30.20e" + "\n"
    for ag in sorted(cp.iterkeys()):
        xg,yg,zg,xr,yr,zr,xyok,zok = cp[ag]
        fw.write(form % (xg,yg,zg,xr,yr,zr,xyok,zok))

    tra.wrer_nodes(cp, fer)
    per = fer.name
    fer.close()
    fw.close()
    thanShowFile(proj, per, Tmatch["Transformation error (using the same control points)"])


def __opensimer(proj, prt):
    "Open files to save projection and error."
    name = proj[0].namebase
    par = p_ggen.path(proj[0].parent)
    try:
        for i in xrange(1000):
            p = par / ("%s%03d.cof" % (name, i))
            per = par / ("%s%03d.ser" % (name, i))
            if not p.exists() and not per.exists():
                fw = open(p, "w")
                fer = open(per, "w")
                return fw, fer
        raise IOError, "It seems the directory is full"
    except IOError, why:
        prt("%s:\n%s" % (Tmatch["Could not write results to file."], why), "can")
        return None, None
