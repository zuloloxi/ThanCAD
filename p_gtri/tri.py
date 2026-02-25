# -*- coding: iso-8859-7 -*-
import random, time, bisect, itertools
from math import pi, atan2, hypot
from p_gmath import dpt, thanSegSeguw
from p_ggen import prg

class ThanLinks(set):
    "A set with ordered iteration."
#    __slots__ = ["seq"]     # It seems that (bug?) __slots__ are not pickled
                             # ..so removing __slots__ makes ThanLinks use more memory

    def resequence(self):
        "Recreate the iteration sequence (e.g. after additions)."
        self.seq = list(set.__iter__(self))

    def sort(self, *args, **kw):
        "Recreate and sort the iteration sequence."
        self.seq = list(set.__iter__(self))
        self.seq.sort(*args, **kw)

    def __iter__(self):
        "Return an ordered iteration sequence."
        return iter(self.seq)

    def __getitem__(self, i):
        "Get contained objects by sequence number."
        return self.seq[i]


class ThanLinksdelegate:
    "A set with ordered iteration."
#   This is a slower version than ThanLinks, but it uses (?) less memory..
#   ..I'm not sure, since there is the __dict__ of the instance

    def __init__(self):
        self.bset = set()

    def add(self, *args, **kw): self.bset.add(*args, **kw)
    def remove(self, *args, **kw): self.bset.remove(*args, **kw)

    def resequence(self):
        "Recreate the iteration sequence (e.g. after additions)."
        self.seq = list(self.bset)

    def sort(self, *args, **kw):
        "Recreate and sort the iteration sequence."
        self.seq = list(self.bset)
        self.seq.sort(*args, **kw)

    def __iter__(self):
        "Return an ordered iteration sequence."
        return iter(self.seq)

    def __getitem__(self, i):
        "Get contained objects by sequence number."
        return self.seq[i]


class ThanTri:
    "Thanasis triangulation."

    def __init__(self):
        "Make sure that the points are unique."
        self.clear()


    def clear(self):
        "Clear all triangles."
        self.ls = {}
        self.aa = {}             # point names; associates coordinates to name; for compatibility with .tri files
        self.xyapeira = set()    # inifinite points
        self.ipref = 0           # Counter used to name unnamed points
        self.hull = None         # Temporary object that should be deleted after computation
        self.xy = None           # Temporary object that should be deleted after computation
        self.dxy = None          # Temporary object that should be deleted after computation
        self.xc = None           # Kernel; Temporary object that should be deleted after computation
        self.yc = None           # Kernel; Temporary object that should be deleted after computation


    def __uniq(self, axy):
        "Make points unique."
        xyu = set()
        cc = []
        for c in axy:                # Note that c may have more than 2 coordinates..
            c = tuple(c)             # ..this is to assist for z, and ThanCad in general
            c1 = c[1:3]
            if c1 in xyu: continue
            xyu.add(c1)
            ca = c[1:]
            cc.append(ca)
            self.aa[ca] = c[0]
        return cc


    def make(self, axy, convex=True, infinite=False):
        "Make the triangulation."
        self.clear()
        self.xy = self.__uniq(axy)
        if len(self.xy) < 3: return False, "At least 3 noncolinear points are needed"
        if infinite:   self.apeira()
        ok, ter = self.compute()
        if not ok: return ok, ter
        if convex:     self.convex()
        self.sortlinks()
        del self.hull, self.xy, self.dxy, self.xc, self.yc
        self.namepoints()
        return True, ""


    def namepoints(self):
        "Name all unnamed points; for compatibility with other programs and .tri, .trp files."
        pref = "tri"
        n = 10 - len(pref)
        form = "%s%%0%dd" % (pref, n)
        for c1 in self.ls:
            a1 = self.aa.get(c1, None)
            if a1 != None: continue
            self.ipref += 1
            self.aa[c1] = form % (self.ipref,)


    def compute(self, nshow=2000000000):
        "Perform triangulation."
        self.kernel()
        ishow = 0
        chs = []

        while len(self.dxy) > 0:
            d,c2 = self.dxy.pop(0)
            t = dpt(atan2(c2[1]-self.yc, c2[0]-self.xc)), c2
            i2 = bisect.bisect(self.hull, t)       # Note that i2 may be len(self.hull), that is 1 after last
            i1 = i2 - 1                            # Note that -1 is a valid index in python
            c1 = self.hull[i1][1]
            c3 = self.hull[i2%len(self.hull)][1]
            self.link(c2, c1)
            self.link(c2, c3)
            self.hull.insert(i2, t)

            while True:
                i1 = i2 - 1                        # Note that -1 is a valid python index
                if not self.flat(i1, pi/1.6): break
                if i1 < i2: i2 -= 1
            while True:
                i3 = (i2 + 1) % len(self.hull)
                if not self.flat(i3, pi/1.6): break
                if i3 < i2: i2 -= 1

            ishow += 1
            if ishow > nshow:
                from p_gchart import ThanChart, vis
                ch = ThanChart(title="points "+str(ishow))
                vis1(self, ch)
                chs.append(ch)
                vis(*chs)
        return True, ""


    def flat(self, i2, flatmin):
        "Flattens if angle too small."
        if len(self.hull) <= 3: return False     #In case the orginal kernel is 3 colinear points
        i1 = i2 - 1                              # Note that -1 is a valid python index
        i3 = (i2 + 1) % len(self.hull)
        c1 = self.hull[i1][1]
        c2 = self.hull[i2][1]
        c3 = self.hull[i3][1]
        t12 = atan2(c2[1]-c1[1], c2[0]-c1[0])
        t23 = atan2(c3[1]-c2[1], c3[0]-c2[0])
        th = dpt(t23-t12+pi)
        if th >= flatmin: return False  #if th >= pi: return False
        self.link(c1, c3)
        del self.hull[i2]
        return True


    def convex(self):
        "Make the boundary convex."
        from p_gchart import ThanChart, vis
        chs = []
        i = 0
        flattened = True
        while flattened:
            flattened = False
            i = 0
            while i < len(self.hull):
                flattened = flattened or self.flat(i, pi)
                i += 1


    def kernel(self):
        "Compute the first triangle."
        xc = yc = 0.0
        for c in self.xy:
            xc += c[0]
            yc += c[1]
        n = len(self.xy)
        xc /= n
        yc /= n
        dxy = [((c[0]-xc)**2+(c[1]-yc)**2, c) for c in self.xy]
        dxy.sort()

        self.hull = dxy[:3]
        xc = yc = 0.0
        for d,c in self.hull:
            xc += c[0]
            yc += c[1]
        xc /= 3
        yc /= 3
        self.hull = [(dpt(atan2(c[1]-yc, c[0]-xc)), c) for d,c in self.hull]
        self.hull.sort()
        for i in xrange(3):
            self.link(self.hull[i-1][1], self.hull[i][1])
        dxy = [((c[0]-xc)**2+(c[1]-yc)**2, c) for d,c in itertools.islice(dxy, 3, None)]
        dxy.sort()
        self.dxy = dxy
        self.xc = xc
        self.yc = yc


    def link(self, n1, n2):
        "Links 2 points."
        assert n1!=n2
        self.ls.setdefault(n1, ThanLinks()).add(n2)
        self.ls.setdefault(n2, ThanLinks()).add(n1)


    def unlink(self, n1, n2):
        "Unlinks 2 points."
        assert n1!=n2
        self.ls[n1].remove(n2)
        self.ls[n2].remove(n1)


    def sortlinks(self, clist=None):
        "Sorts the links clockwise."
        gdf = lambda cb: dpt(atan2(cb[0]-ca[0], cb[1]-ca[1]))
        if clist == None: clist = self.ls.iterkeys()
        for ca in clist:
            self.ls[ca].sort(key=gdf)


    def brkapply(self, ca, cb):
        "Reforms triangulations so that ca-cb is an edge; you must call namepoints() after that."
        cor = tuple(ca[1:])
        cb = tuple(cb[1:])
        linksor = self.ls[cor]
        gdf = lambda cb: dpt(atan2(cb[0]-cor[0], cb[1]-cor[1]))
        visual = False
        if visual:
            from p_gchart import ThanChart, vis
            chs = []
            ch = ThanChart(title="brk"+str(len(chs)))
            vis1(self, ch, brk=(ca,cb))
            chs.append(ch)

        while True:
            if cb in linksor: return
            thb = gdf(cb)
            for j,cj in enumerate(linksor):
                if gdf(cj) > thb: i = j-1; break
            else:
                j = 0
                i = len(linksor)-1
            ci = linksor[i]
            cj = linksor[j]
            if cj not in self.ls[ci]:
                print "Hit boundary of triangulation."
                return
            caa = self.diamopposed(cor, ci, cj)
            if caa == None:
                print "Dead End!"
#                vis(*chs)
                return
            ct = thanSegSeguw(cor, caa, ci, cj)
            if ct == None:
#                print "Non convex quadrilateral found"
                ct = thanSegSeguw(cor, cb, ci, cj)
                if ct == None:
                    print "There should be an intersection!"
#                    vis(*chs)
                    return
                u, _ = ct
                ct = tuple(a+(b-a)*u for a,b in zip(cor, cb))
                self.link(cor, ct)
                self.link(caa, ct)
                self.unlink(ci, cj)
                self.link(ci, ct)
                self.link(cj, ct)
                self.sortlinks((cor, caa, ci, cj, ct))
                cor = ct
                linksor = self.ls[cor]
            else:
                self.quadreplace(cor, ci, cj, caa)
            if visual:
                ch = ThanChart(title="brk"+str(len(chs)))
                vis1(self, ch, brk=(ca,cb))
                chs.append(ch)
                del chs[:-3]
#                vis(*chs)


    def diamopposed(self, ca, cb, cc):
        "Find the nearest diametrically opposed point to ca with respect to line ca-cb."
        caa = [(hypot(c[0]-ca[0], c[1]-ca[1]), c) for c in self.ls[cb] if c in self.ls[cc] and c != ca]
        if len(caa) == 0: return None
        return min(caa)[1]


    def quadreplace(self, ca, cb, cc, caa):
        "Replace the diagonal cb-cc with diagonal ca-caa to the quadrilateral (ca, cb, caa, cc, ca)."
        self.unlink(cb, cc)
        self.link(ca, caa)
        self.sortlinks((ca, cb, cc, caa))


    def iteredges(self):
        "Iterate through the edges of the triangulation."
        a = (frozenset((j,k)) for j,ks in self.ls.iteritems() for k in ks)
        a = frozenset(a)
        for jk in a:
            yield tuple(jk)


    def itertriangles(self, apmax=50.0):
      "Iterate through the triangles of the triangulation."
      apMaxEn2 = apmax**2
      seen = set()
      for ca, linksa in self.ls.iteritems():
          if ca in self.xyapeira: continue                # throw Infinite points out
          cb = linksa[0]
          bigKb = (cb[0]-ca[0])**2 + (cb[1]-ca[1])**2 > apMaxEn2
          for ib in xrange(len(linksa)):
              ic = (ib + 1) % len(linksa)                 ### ΠΡΟΣΟΧΗ: ΝΑ ΜΗΝ ΥΠΑΡΧΕΙ ΑΣΥΝΕΧΕΙΑ
              cc = linksa[ic]
              bigKc = (cc[0]-ca[0])**2 + (cc[1]-ca[1])**2 > apMaxEn2
              discont = cc not in self.ls[cb]
              tri = ca, cb, cc
              triset = frozenset(tri)
              if bigKb or bigKc or cb in self.xyapeira or cc in self.xyapeira or discont or triset in seen:
#                  print "Duplicate/invalid:", tri
                  pass
              else:
                  seen.add(triset)
                  yield tri
              cb = cc
              bigKb = bigKc

    def serialise(self):
        "Make the triangulation as a sequence."
        iaa = {}
        seq = []                              # The points must be written with a certain sequence
        i = 0
        for c in self.ls:
            if c in self.xyapeira: continue   # Write infinite points at the end
            assert c not in iaa
            i += 1
            iaa[c] = i
            seq.append(c)
        for c in self.xyapeira:
            assert c not in iaa
            i += 1
            iaa[c] = i
            seq.append(c)
        return iaa, seq


    def writetri(self, fw, form1="%-10s%15.3f%15.3f%15.3f\n", form2="%10d\n"):
        "Write the trianguation in tri file; the links must be already sorted."
        iaa, seq = self.serialise()      # The points must be written with a certain sequence
        for c in seq:
            ca = list(c[:3])
            while len(ca) < 3: ca.append(0.0)
            fw.write(form1 % (self.aa[c], ca[0], ca[1], ca[2]))
            for ca in self.ls[c]:
                fw.write(form2 % iaa[ca])
            fw.write("$\n")

    apnames = frozenset(('####ΚΑ####', '####ΚΔ####', '####ΠΔ####', '####ΠΑ####'))

    def readtri(self, fr):
        "Reads the trianguation from a tri file; it sorts the links."
        self.clear()
        it = iter(fr)
        xy = {}
        ls = {}
        i = -1
        line = 0
        for dline in it:
            line += 1
            i += 1
            a1 = dline[:10].rstrip()
            try:
                x1 = float(dline[10:25])
                y1 = float(dline[25:40])
                z1 = float(dline[40:55])
            except ValueError:
                prg("Syntax error at line %d of tri file." % line)
                raise
            c1 = (x1, y1, z1)
            xy[i] = c1
            self.aa[c1] = a1
            if a1 in self.apnames: self.xyapeira.add(c1)
            links1 = ls[c1] = []
            for dline in it:
                line += 1
                if dline.rstrip() == "$": break
                try:
                    j = int(dline[:10])
                    if j < 1: raise ValueError, "Invalid link"
                except ValueError:
                    prg("Syntax error/bad value at line %d of tri file." % line)
                    raise
                links1.append(j-1)
        for i in xrange(len(xy)):
            c1 = xy[i]
            links1 = self.ls[c1] = ThanLinks()
            for j in ls[c1]: links1.add(xy[j])
        del xy, ls
        self.sortlinks()


    def thanExpThc1(self, fw):
        "Writes the trianguation to a .thc file."
        iaa, seq = self.serialise()      # The points must be written with a certain sequence
        form = fw.formFloat * 3
        for c in seq:
            ca = list(c[:3])
            while len(ca) < 3: ca.append(0.0)
            fw.writeTextln(self.aa[c])
            fw.writeln(form % (ca[0], ca[1], ca[2]))
            for ca in self.ls[c]:
                fw.writeln("%d" % (iaa[ca],))
            fw.writeln("$")


    def thanImpThc1(self, fr, ver):
        "Reads the trianguation from a .thc file; it sorts the links."
        tend = "</" + self.thanObjectName + ">"
        self.clear()
        xy = {}
        ls = {}
        i = -1
        while True:
            if fr.next().strip() == tend: break
            fr.unread()
            a1 = fr.readTextln()
            c1 = tuple(map(float, fr.next().split()))
            i += 1
            xy[i] = c1
            self.aa[c1] = a1
            if a1 in self.apnames: self.xyapeira.add(c1)
            links1 = ls[c1] = []
            while True:
                dline = fr.next().strip()
                if dline == "$": break
                j = int(dline)  #May raise ValueError
                if j < 1: raise ValueError, "Invalid link"
                links1.append(j-1)
        fr.unread()
        for i in xrange(len(xy)):
            c1 = xy[i]
            links1 = self.ls[c1] = ThanLinks()
            for j in ls[c1]: links1.add(xy[j])
        del xy, ls
        self.sortlinks()


    def apeira(self):
      "Add infinite points to make a convex quadrilateral."

#-----Βρες xmin,xmax,ymin,ymax

      xmin = min(c[0] for c in self.xy)
      xmax = max(c[0] for c in self.xy)
      ymin = min(c[1] for c in self.xy)
      ymax = max(c[1] for c in self.xy)

#-----Διόρθωσε xmin,xmax,ymin,ymax έτσι ώστε να είναι πιο μακριά

      dymax = (xmax - xmin) * 1.0e-1 + 1.0
      if dymax < 500.0: dymax = 500.0
      xmin = xmin - dymax
      xmax = xmax + dymax
      dymax = (ymax - ymin) * 1.0e-1 + 1.0
      if dymax < 500.0: dymax = 500.0
      ymin = ymin - dymax
      ymax = ymax + dymax
      dymax = dymax * 0.5

#-----Πρόσθεσε "άπειρα σημεία" που σχηματίζουν περιγεγραμμένο κυρτό
#     τετράπλευρο. Ετσι αποφεύγουμε bug στο πρόγραμμα triangle
#     και βγάζουμε αποτελέσματα συμβατά με το πρόγραμμα deltri

      for add in self.xy: break
      add = add[2:]
      s = []
      c = (xmin, ymin) + add
      s.append(c)
      self.aa[c] = '####ΚΑ####'

      c = (xmax, ymin) + add
      s.append(c)
      self.aa[c] = '####ΚΔ####'

      c = (xmax, ymax-dymax) + add
      s.append(c)
      self.aa[c] = '####ΠΔ####'           #Το -dymax εξασφαλίζει γωνία διευθύνσεως  < 0

      c = (xmin, ymax) + add
      s.append(c)
      self.aa[c] = '####ΠΑ####'

      for c in s:
          self.xyapeira.add(c)
      self.xy.extend(s)

#-----Πρόσθεσε τις πλευρές του τετραπλεύρου στις break lines

#      call erInc1 (nBrk, MSYNT, 0, 'break lines')
#      ke1(nBrk) = nSYnt - 3
#      ke2(nBrk) = nSYnt - 2
#
#      call erInc1 (nBrk, MSYNT, 0, 'break lines')
#      ke1(nBrk) = nSYnt - 2
#      ke2(nBrk) = nSYnt - 1
#
#      call erInc1 (nBrk, MSYNT, 0, 'break lines')
#      ke1(nBrk) = nSYnt - 1
#      ke2(nBrk) = nSYnt
#
#      call erInc1 (nBrk, MSYNT, 0, 'break lines')
#      ke1(nBrk) = nSYnt
#      ke2(nBrk) = nSYnt - 3


    def show(self, chs=None):
        "Shows the triangle mesh."
        from p_gchart import ThanChart, vis
        ch = ThanChart(title="points "+str(len(self.ls)))
        vis1(self, ch)
        vis(ch)


def vis1(t, ch, brk=()):
    "Adds all the edges to a ThanChart."
    a = (frozenset((j,k)) for j,ks in t.ls.iteritems() for k in ks)
    a = frozenset(a)
    try:    t.xc
    except: pass
    else:   ch.curveAdd( (t.xc-1, t.xc+1, t.xc+1, t.xc-1, t.xc-1), # The centroid as a small rectangle
                 (t.yc-1, t.yc-1, t.yc+1, t.yc+1, t.yc-1), color="yellow")
    for i,jk in enumerate(a):
        j,k = tuple(jk)
        if i%100000 == 0: print i
        ch.curveAdd((j[0], k[0]), (j[1], k[1]))

    if len(brk) > 1:
        xx = [c[0] for c in brk]
        yy = [c[1] for c in brk]
        ch.curveAdd(xx, yy, color="white")
    return ch


def testTriRan():
    "Tests the triangulation and the break lines with random points."
    n = 200
    for i in xrange(2, 3):
        print "try", i
        r = random.Random(i)
        u = r.uniform
        print "generating points.."
        ps = [(None, u(0,10000), u(0,10000), -123.456) for i in xrange(n)]

        print "Creating triangulation.."
        t = ThanTri()
        t.make(axy=ps, convex=True, infinite=False)
        t.show()
        t.writetri(open("q1.tri", "w"))

        print "Forcing break lines.."
        p1 = ps[50]
        p2 = ps[150]
        print "p1=", p1, "p2=", p2
        t.brkapply(p1, p2)
        t.show()


def testlinks():
    "Tests the ThanLinks object."
    a = ThanLinks((999,-1, 67, 22, 33, 0))
    a.resequence()
    print "object=", a
    print "iterate:"
    for x in a: print x
    print "tolist:", list(a)
    print "------------------------------------------------------"
    print "sorted:" 
    a.sort()
    for x in a: print x
    print "object sorted:", a
    print "------------------------------------------------------"
    print "indexing:"
    for i in xrange(len(a)):
        print "a[", i, "]=", a[i]


def testpickle():
    "Tests why cPickle does not archive __slots__."
    import cPickle
    li = ThanLinks()
    li.add((10.0,20.0,30.0))
    li.add((5.0,20.0,30.0))
    li.add((5.0,80.0,30.0))
    li.sort()
    print "Initial object:"
    print li
    print "Dict:",
    try: print li.__dict__
    except Exception, why: print why
    print "---------------------------------------------------"
    print "After pickling and unpickling:"
    fw = open("q1.pic", "w")
    s = cPickle.dumps(li)
    fw.write(s)
    fw.close()
    fr = open("q1.pic")
    t = fr.read()
    lin = cPickle.loads(t)
    print lin
    print "Dict:", lin.__dict__


if __name__ == "__main__":
#    testlinks()
    testTriRan()
#    testpickle()
