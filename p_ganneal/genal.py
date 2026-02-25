try:
    from math import log2
except:
    from math import log
    def log2(x): return log(x)/log(2)
from math import ceil

import random, copy
import p_ggen
from p_gmath import thanNearx


class GeneticAlgorithm(object):
    "The class implements the genetic algorithm for optmisation."

    def __init__(self, **kw):
        """Initialize genetic algorithm procedure.

        These values are typical. They will can be overwritten by genetic()."""
        self.prt = p_ggen.prg
        self.nAnim = None       # (initial?) number of animals
        self.animals = set()    # set of all animals alive
        self.bests = []         # Best animal of each generation
        self.bestall = None     # Best animal of all
        self.nGen = 200         # Number of generations
        self.igen = 0           # Current generation
        self.pmut = 0.0         # probability of mutation (if not set by user, once every generation)

        self.r = random.Random()
        self.nRuns = 1          # Number of runs that the algorithm will be executed

        self.comNvalmax = 2     #Integer max value (0..value-1) that a chromosome may have (usually 2)
        self.comNchrom = 26     #Number of (different) chromosomes
        self.comFitmax = 0.0    #A big fitness; in fact it should be the best fitness (biggest) possible (if known)
                                #It is used to compute deficiency due to common chromosomes between parents.
                                #If comBiggerIsBetter is False, comFitamx should again be a big value (poor):
                                #it is used convert small values (which are better) to big values (which the GA
                                #tries to maximise).
                                #If zero, then the biggest fitness of all animals (which are random) at the beginning is taken
        self.nSample = 10       #Number animals taken in the sample in tournamentThanasis(); the least fit of these animals dies.
        self.comBiggerIsBetter = True    #If true justFitness() returns a number which must be maximised
                                         #If false justFitness() returns a number which must be minimised
        self.config(**kw)


    def config(self, prt=None, nAnim=None, nGen=None, pmut=None, nValmax=None, nChrom=None, fitmax=None, biggerIsBetter=None):
        "Change default values."
        if prt     is not None: self.prt     = prt
        if nAnim   is not None:
            if nAnim < self.nSample: raise ValueError("At least %d animals are required (for tournamentThanasis())" % (self.nSample,))
            self.nAnim   = nAnim
        if nGen    is not None: self.nGen    = nGen
        if pmut    is not None: self.pmut    = pmut
        if nValmax is not None: self.comNvalmax = nValmax
        if nChrom  is not None: self.comNchrom = nChrom
        if fitmax  is not None: self.comFitmax= fitmax
        if biggerIsBetter is not None: self.comBiggerIsBetter = biggerIsBetter
        if self.nAnim is None:    #If no value, compute it
            self.nAnimCompute()
        elif nAnim is None:       #If nAnim is not None, then the user wants nAnim (which is already set)
            if nValmax is not None or nChrom is not None:  # If nValmax and nChrom are both None, there is nothing new to compute
                self.nAnimCompute()
        if self.pmut <= 0.0:
            self.pmutCompute()
        elif nAnim is not None:    #If the number of animals changes, the probability must change
            self.pmutCompute()


    def nAnimCompute(self):
        """Compute the number of animals from other values (and change the value of mutation probability).

        According to tournamentThanasis() we choose a random set of nSample (10) animals
        delete the one with the lowest fitness, until 50% of animals are deleted.
        Thus we must have at least 2*nSample (20) animals, so that when we delete half of them,
        we still have nSample (10) animals to choose a random set."""
        #self.nAnim = int(5 * log2(self.comNvalmax) * self.comNchrom)    # 5 animals per binary chromosome

        #Population size from Matlab (https://www.mathworks.com/help/gads/ga.html)
        #{50} when numberOfVariables <= 5, {200} otherwise 
        #{min(max(10*nvars,40),100)} for mixed-integer problems
        nvars = int( log2(self.comNvalmax) * self.comNchrom )  #Number of binary chromosomes
        nvars = ceil(nvars/8)                                  #Assume 1 variable per 8 binary chromosomes
        self.nAnim = 50 if nvars<=5 else 200

        self.nAnim = max(self.nAnim, 2*self.nSample)   #At least 2*nSample (20) animals anyway
        self.pmutCompute()


    def pmutCompute(self):
        """Compute the probability of mutations: once per generation."

        According to tournamentThanasis() and breed(), the whole population
        of animals is replaced in every generation. 50% of the poulation dies.
        The remaininig 50% are going to be parents. However only the parents get
        mutations. Thus nAnim/2 animals may mutate in each generation."""
        self.pmut = 1.0 / (self.nAnim/2.0)


    def fitmaxCompute(self, DisAnimal):
        """Compute a big fitness; in fact it should be the best fitness possible.

        At the begining the animals aree random. Thus the biggest fitness of all animals is
        a reasonable big fitness.
        """
        self.comFitmax = max(anim.justFitness(self) for anim in self.animals)


    def genetic(self, DisAnimal):
        "Execute the genetic algorithm."
        self.animals.clear()
        del self.bests[:]
        for i in range(self.nAnim):
            self.animals.add(DisAnimal(self))
        if self.comFitmax == 0: self.fitmaxCompute(DisAnimal)
        for self.bestall in self.animals: break     # Give a initial value to bestall
        for self.igen in range(self.nGen):
#            print "Generation%4d" % igen
            self.bestIngen(self.igen)
            if self.converged(): break
            self.tournamentthanasis()
            self.breed()
        else:
            self.bestIngen(self.nGen)
            self.prt("Genetic algorithm terminated due to max generations", "can1")
        #self.prt("\nBest fitness for every generation", "info1")
        #for i,b in enumerate(self.bests):
        #    self.prt("%4d: %.2f(%.2f)" % (i, b.fitness(self), b.fitnessr(self)))
        self.prt("")
        self.prt("best of all:", "info")
        if self.comBiggerIsBetter:
            self.prt("%.2f(%.2f)" % (self.bestall.fitness(self), self.bestall.fitnessr(self)))
        else:
            self.prt("%.2f(%.2f)" % (self.comFitmax-self.bestall.fitness(self),  self.comFitmax-self.bestall.fitnessr(self)))
        return self.bestall, self.bests


    def converged(self):
        "Check if the genetic algoρithm converged; 30 steps with no optimisation."
        if len(self.bests) < 100: return False    #At least 100 generations
        nc = 30
        if len(self.bests) < nc: return False
        flast = self.bests[-1].fitnessr(self)
        for anim in self.bests[-nc:]:
            f = anim.fitnessr(self)
            if thanNearx(f, flast): continue #flast is equal to f
            if flast > f: return False       #flast is a better value than f; not converged
        return True


    def bestIngen(self, igen):
        "Find and save the best animal in generation igen."
#        print "--------------------------------------------------------------------"
        best = max(self.animals, key=lambda a:a.fitnessr(self))
        if self.comBiggerIsBetter:
            self.prt("generation%4d  best: %.2f(%.2f)" % (igen, best.fitness(self), best.fitnessr(self)))
        else:
            self.prt("generation%4d  best: %.2f(%.2f)" % (igen, self.comFitmax-best.fitness(self),  self.comFitmax-best.fitnessr(self)))
        #self.bests.append(best)
        self.bests.append(self.bestall)


    def breed(self):
        "Animals mate and give birth to children."
        anims = set()
        while len(self.animals) > 1:
            a, b = self.r.sample(self.animals, 2)
            self.animals.remove(a)
            self.animals.remove(b)
            a.mutate(self)
            b.mutate(self)
            for i in range(4):
                ch = a.mate(self, b)
                anims.add(ch)
        #print("breed: new animals=", len(anims), "remaining from prev generations=", len(self.animals))
        anims.update(self.animals)
        self.animals = anims
        #print("breed: new generation animals=", len(self.animals))


    def tournamentclassic(self):
        "Select the best part of the population to breed; allow for a bit random selection."
        pdie = 0.30
        nkeep = int(self.nAnim*(1-pdie))
        keep = set()
        for i in range(nkeep):
            pop = self.r.sample(self.animals, 4)
            a = max(pop, key=lambda a:a.fitness(self))
            keep.add(a)
            self.animals.remove(a)
            f = a.fitness(self)
#            print "%f -> %f -> %.1f  ακόμα ζωντανός" % (f, com.fitmax, f/fa*100.0)
        for a in self.animals:
            f = a.fitness(self)
#            print "%f -> %f -> %.1f  πεθαίνει" % (f, com.fitmax, f/fa*100.0)


    def tournamentthanasis(self):
        "Select the best part of the population to breed; allow for a bit random selection."
        pdie = 0.50
        ndie = int(len(self.animals)*pdie)   #Thanasis2022_11_25
        for i in range(ndie):
            pop = self.r.sample(self.animals, self.nSample)
            a = min(pop, key=lambda a:a.fitness(self))
            self.animals.remove(a)
#            print "%.2f(%.2f) <= %.2f  πεθαίνει" % (a.fitness(), a.fitnessr(), com.fitmax)
#        for a in self.animals:
#            print("%.2f(%.2f) <= %.2f  ζει" % (a.fitness(), a.fitnessr(), com.fitmax))


class GeneticAnimal(object):
    "An animal representing the problem to optimise."
    comR = random.Random()

    def __init__(self, ga, chrom1=None, deficiency=0.0):
        "Create chromosomes for the distribution animal."
        if chrom1 == None:
            self.chrom = [0]*ga.comNchrom
            for i in range(ga.comNchrom): self.chrom[i] = self.comR.randrange(ga.comNvalmax)
        else:
            assert len(chrom1) == ga.comNchrom
            self.chrom = list(chrom1)
        self.crhom2Fenotype(ga)
        self.defic = deficiency                  #Deficiency due to degeneration
        self.ftns = None


    def crhom2Fenotype(self, ga):
        "Transfer the instructions in chromosomes to the physical nature of the animal."
        pass


    def mutate(self, ga):
        "Perform a random mutation."
        r = self.comR
        if r.random() > ga.pmut: return     #Mutate 1 in 1000 (look com.py)
        old = self.fitness(ga)
        oldr = self.fitnessr(ga)
        n = len(self.chrom)
        if r.random() < 0.5:
            i1 = r.randrange(n)
            monkey1 = self.chrom[i1]
            for i in range(10):
                i2 = r.randrange(n)
                monkey2 = self.chrom[i2]
                if monkey1 != monkey2: break
            else:
                ga.prt("Warning: can't find 2 crhomosomes with different values", "can1")
                return
            self.chrom[i1] = monkey2
            self.chrom[i2] = monkey1
        else:
            i1 = r.randrange(n)
            monkey1 = self.chrom[i1]
            for i in range(10):
                monkey2 = r.randrange(ga.comNvalmax)
                if monkey1 != monkey2: break
            else:
                ga.prt("Warning: can't find different value to assign to chromosome", "can1")
                return
            self.chrom[i1] = monkey2
        self.crhom2Fenotype(ga)
        self.ftns = None
        self.defic = 0.0
        if ga.comBiggerIsBetter:
            ga.prt("            mutation: %.2f(%.2f) -> %.2f(%.2f)" % (old, oldr, self.fitness(ga), self.fitnessr(ga)), "info1")
        else:
            ga.prt("            mutation: %.2f(%.2f) -> %.2f(%.2f)" % (ga.comFitmax-old, ga.comFitmax-oldr, ga.comFitmax-self.fitness(ga), ga.comFitmax-self.fitnessr(self)), "info1")


    def mate2(self, other):
        "Make 2 children which replace the parents, with change of a sequence of chromosomes."
        r = self.comR
        if r.random() < 0.7: return   #30% of the parents do not mate
        n = len(self.ban)
        n2 = int(n//2)
        i1 = r.randrange(n2)
        i2 = r.randrange(n2, n+1)
        self.chrom[i1:i2], other.chrom[i1:i2] = other.chrom[i1:i2], self.chrom[i1:i2]
        self.ftns = None
        other.ftns = None


    def mate(self, ga, other):
        "Make 1 children with mixed chromosomes of the parents."
        r = self.comR
        n = len(self.chrom)
        n2 = int(n//2)
        i1 = r.randrange(n2)
        i2 = r.randrange(n2, n+1)
        m = self.chrom[:i1]+other.chrom[i1:i2]+self.chrom[i2:]
        d = 0
        for i in range(i1,i2):
            if self.chrom[i] == other.chrom[i]: d += 1
        d = float(d)/(i2-i1)
        if d > 0.5: d = ga.comFitmax*0.1*d
        else:       d = 0.0
        return self.__class__(ga, m, d)


    def fitness(self, ga):
        "The fitness corrected according to big or small is better, and corrected with deficiency."
        if self.ftns == None:
            self.ftns = self.justFitness(ga)   #Either bigger or smaller is better
            if not ga.comBiggerIsBetter: self.ftns = ga.comFitmax - self.ftns
            rep = self.ftns > ga.bestall.fitnessr(ga)
            self.ftns -= self.defic
            if rep: ga.bestall = copy.copy(self)
        return self.ftns


    def justFitness(self, ga):
        "The fitness of the animal; the bigger the better."
        raise AttributeError("Method justFitness() should be overriden.")


    def fitnessr(self, ga):
        "The real fitness (i.e. plus deficiency)."
        return self.fitness(ga)+self.defic


    def detail(self, ga, fw):
        "Details about the distribution represented by the animal."
        pass
