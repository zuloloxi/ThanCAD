from math import hypot, atan2, pi
from p_ggen import frange, doNothing
from p_gmath import linint, dpt

class ThanYpyka(object):
    "Computes the isocurves from a triangulation."

    def __init__(self, ls, saveis, prt=doNothing):
        "Inintialize the object with the links of a triangulation."
        self.ls = ls                 #Triangulation links
        self.saveis = saveis         #User supplied function to accept contour lines as they are computed
        self.prt = prt               #User supplied function to print messages
        self.cis = []                #The coordinates of a contour line
        self.seen = set()            #Visited edges
        self.dhl = 1.0               #The iso-dimension
        self.apOrioMax = 50.0        #Longer edges than this are considered nonexistent


    def ypyka(self, dhl=None, apmax=None):
        "Compute all isocurves."
        if dhl is not None: self.dhl = dhl
        if apmax is not None: self.apOrioMax = apmax
        assert len(self.ls) > 2, "Τουλάχιστον 3 σημεία χρειάζονται στην τριγωνοποίηση"

#-------ΒΡΕΣ ΜΕΓΙΣΤΟ ΚaΙ ΕΛaΧΙΣΤΟ ΥΨΟΜΕΤΡΟ

        for k in self.ls: break
        hmin = hmax = k[2]
        for k in self.ls:
            h1 = k[2]
            if h1 > hmax: hmax = h1
            if h1 < hmin: hmin = h1

#-------Υπολόγισε καμπύλες

        h1 = int(hmin / dhl) * dhl
        for his in frange(h1, hmax, dhl):
            pr = 1.0
            if his > (hmin+hmax)*0.5: pr = -1.0
            self.ypyka1(his, pr)

        self.seen.clear()         # Free memory
        del self.cis[:]           # Free memory

#=====================================================================

    def ypyka1(self, his, pr):
        "Compute all contour lines of elevation his."
        self.prt('ΥΠΟΛΟΓΙΣΜΟΣ ΚΑΜΠΥΛΗΣ %.2f' % his)

#-------ΒΡΕΣ ΣΗΜΕΙΟ aΠ' ΟΠΟΥ aΡΧΙΖΕΙ Η ΙΣΟΥΨΗΣ his

        dhis = 0.01*self.dhl
        seen = self.seen
        seen.clear()
        for karx, linksarx in self.ls.items():
            harx = karx[2]
            if harx == his: harx -= dhis
            if harx*pr > his*pr: continue
            for iarx, larx in enumerate(linksarx):
                if frozenset((karx, larx)) in seen: continue
                hl = larx[2]
                if hl == his: hl -= dhis
                if hl*pr < his*pr: continue
                if self.orioper(karx, larx): continue
                icod = self.ypyka2(his, karx, iarx)
                self.saveis(icod, self.cis)           # Σώσε καμπύλη

#==========================================================================

    def orioper(self, k, l):
        "Tests if distance is out of bounds."
        d2 = hypot(l[0]-k[0], l[1]-k[1])
        return d2 > self.apOrioMax

    def xasma(self, k, l, lp, ibhm):   #Thanasis2012_05_16
        "Tests if there is gap >= pi between 2 consecutive points."
        if ibhm < 0: l, lp = lp, l                #If ibhm == -1 then lp, l are counter-clockwise, so we correct them
        thl = atan2(l[0]-k[0], l[1]-k[1])
        thlp = atan2(lp[0]-k[0], lp[1]-k[1])
        dth = dpt(thl-thlp)
        if dth >= pi: return True                 #There is xasma from previous point
        return False

#==========================================================================

    def ypyka2(self, his, karx, iarx):
        "Compute 1 isocurve."

#-------ΔΕΞΙΟ ΜΙΣΟ ΙΣΟΥΨΟΥΣ

        del self.cis[:]
        icod = self.mishyp(his, karx, iarx, 1)

#-------ΚΥΚΛΙΚΗ ΙΣΟΥΨΗΣ

        if icod < 0:
            if self.cis[0] != self.cis[-1]:
#                assert 0, "Κυκλική ΙΣΟΥΨΗΣ ΔΕΝ ΕΧΕΙ ΙΔΙΕΣ ΑΡΧΙΚΕΣ ΚΑΙ ΤΕΛΙΚΕΣ ΣΥΝΤΕΤΑΓΜΕΝΕΣ: Πιθανό πρόβλημα στην κατασκευή των τριγώνων."
                self.prt("Κυκλική ΙΣΟΥΨΗΣ ΔΕΝ ΕΧΕΙ ΙΔΙΕΣ ΑΡΧΙΚΕΣ ΚΑΙ ΤΕΛΙΚΕΣ ΣΥΝΤΕΤΑΓΜΕΝΕΣ: Πιθανό πρόβλημα στην κατασκευή των τριγώνων.")
                icod = 0

#------ΑΡΙΣΤΕΡΟ ΜΙΣΟ ΙΣΟΥΨΟΥΣ

        else:
            self.cis.reverse()
            del self.cis[-1]                                         # ΞΑΝΑΒΡΕΣ ΑΡΧΙΚΟ..
            self.seen.remove(frozenset((karx, self.ls[karx][iarx]))) # ..ΣΗΜΕΙΟ
            icod = self.mishyp(his, karx, iarx, -1)
            if icod == -1:
#                assert 0, "ΙΣΟΥΨΗΣ Κατέληξε σε σημείο του εαυτού της: Πιθανό πρόβλημα στην κατασκευή των τριγώνων."
                self.prt("ΙΣΟΥΨΗΣ Κατέληξε σε σημείο του εαυτού της: Πιθανό πρόβλημα στην κατασκευή των τριγώνων.")
                icod = 0
        return icod

#=====================================================================

    def mishyp (self, his, karx, iarx, ibhm):
        "Compute half of a isocurve."
        seen = self.seen
        dhis = 0.01*self.dhl
        k = karx
        hk = k[2]
        if hk == his: hk -= dhis
        linksk = self.ls[k]
        i = iarx
        l = linksk[i]
        hl = l[2]
        if hl == his: hl -= dhis
        edge = frozenset((k, l))

#-------ΒΡΕΣ ΤΟΜΗ - ΠaΡΕ ΕΠΟΜΕΝΟ ΣΗΜΕΙΟ ΤΟΥ ΚΕΝΤΡΙΚΟΥ ΣΗΜΕΙΟΥ k

        while True:
            self.tomis(k, hk, l, hl, his)
            seen.add(edge)
            lp = l
#-----------ΕΠΟΜΕΝΗ ΕΝΩΣΗ ΤΟΥ ΣΗΜΕΙΟΥ ksp(k)
            i = (i + ibhm) % len(linksk)
            l = linksk[i]
#-----------ΕΞΕΤΑΣΕ ΤΕΛΟΣ,ΚΥΚΛΟ
            if self.xasma(k, l, lp, ibhm): return 0 # Υπάρχει χάσμα >=pi μεταξύ lp και l: τέλος περιοχής  #Thanasis2012_05_16
            hl = l[2]
            if hl == his: hl -= dhis
            if lp not in self.ls[l]: return 0    # ΤΕΛΟΣ ΠΕΡΙΟΧΗΣ
            edge = frozenset((k, l))
            if edge in seen:                     # ΕΧΕΙ ΗΔΗ ΒΡΕΘΕΙ (ΚΥΚΛΟΣ);
                assert (hk-his) * (his-hl) >= 0.0, "Προηγουμένως είχε βρεθεί τομή. Τώρα όχι!"
                self.tomis(k, hk, l, hl, his)
                return -1
            if (hk-his) * (his-hl) >= 0.0:
                if self.orioper(k, l): return 0       # Οριο περιοχής
                continue

#-----------aΛΛaΓΗ ΚΕΝΤΡΙΚΟΥ ΣΗΜΕΙΟΥ Κ

            k = l
            hk = k[2]
            if hk == his: hk -= dhis
            linksk = self.ls[k]
            for i, l in enumerate(linksk):
                if l == lp: break
            else:
                assert 0, "Τέλος περιοχής: έπρεπε να είχε βρεθεί προηγουμένως!"
            hl = l[2]
            if hl == his: hl -= dhis
            edge = frozenset((k, l))
            if edge in seen:                     # ΕΧΕΙ ΗΔΗ ΒΡΕΘΕΙ (ΚΥΚΛΟΣ);
                self.tomis(k, hk, l, hl, his)
                return -1
            assert (hk-his) * (his-hl) >= 0.0, "Έπρεπε να υπάρχει τομή!"
            if self.orioper(k, l): return 0           # Οριο περιοχής

#==========================================================================

    def tomis(self, k, hk, l, hl, his):
        "Find intersection and save it."

#-------ΒΡΕΣ ΤΟΜΗ

        dh = hl - hk
        assert dh != 0.0, "Αφού αφαιρείται 0.01*dhl, πώς βγήκαν ίδια;"
        ca = list(k)
        ca[2] = hk
        cb = list(l)
        cb[2] = hl
        if dh == 0.0:
            ct = [(a+b)*0.5 for a,b in zip(ca, cb)]
        else:
            ct = [linint(hk, a, hl, b, his) for a,b in zip(ca, cb)]
#-------ΣΩΣΕ ΤΟΜΗ

        self.cis.append(ct)
