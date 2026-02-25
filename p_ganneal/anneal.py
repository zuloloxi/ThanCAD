# -*- coding: iso-8859-7 -*-
import random
from math import exp
import p_ggen, p_gmath


class SimulatedAnnealing:
  "The class implements the simulated annealing method."

  def __init__(self, **kw):
      """Initialize simulated annealing procedure.

      These values are typical. They will be overwritten by anneal()."""
      self.prt = p_ggen.prg

      self.nTsteps  = 50   # max temperature steps
      nDim = 20            # The dimension of the vector space which each state
                           #  belongs to. Note that it may be not constant.
      self.spChan   = 200  # max number of state changes per dimension tried at any temperature
      self.spSch    = 20   # max number of succesful state changes per dimension tried at any temperature
      self.nChan    = self.spChan*nDim  # max number of state changes tried at any temperature
      self.nSch     = self.spSch *nDim  # max number of succesful state changes tried at any temperature
 
      self.iSch     = 0    # number of succesful state changes (positive or negative)
      self.iSchNeg  = 0    # number of succesful energy-negative state changes

      self.t      = 100.0  # temperature
      self.tFactr = 0.70   # Annealing schedule: t is reduced by this factor on each step
      self.e1     = 0.0    # energy before and ..
      self.e2     = 0.0    # after a change
      self.emin   = 0.0    # minimum energy found
      self.r = random.Random()
      self.anim = SAAnimation()
      self.config(**kw)

  def config(self, treduce=None, prt=None, animon=None, animsize=None, animnframe=None, animpref=None):
      "Change default values."
      if treduce != None: self.tFactr = treduce
      if prt != None: self.prt = prt
      self.anim.config(on=animon, size=animsize, nframe=animnframe, pref=animpref)

  def anneal(self, obj):
      "Does the annealing process."

#-----Initial sharing

      if not obj.initState(self.t, self.spSch):
          import sys
          f = sys.stderr
          f.write("initState() failed to calibrate temperature.\n")
          f.write("Either the intial state is the worst possible one,\n")
          f.write("or changeState() makes insignificant changes which do not affect\n")
          f.write("the energy of the configuration.\n")
          sys.exit(1)
      self.e1 = obj.energyState()*obj.efact                     #Thanasis2011_05_19
      self.emin = self.e1
      eprev = self.e1
      obj.saveMinState()
      self.prt(' ')
      self.prt('Ανόπτηση', "info")
      dl = "%3s  %8s  %6s  %6s  %6s  %8s  %8s" % ('α/α', 'Θερμοκρα',
           'μη μηδ', 'αρνητι', 'Στοχασ', 'Ενεργ.', 'min εν.')
      self.prt(dl, "info1")

#-----Temperature loop-------------------------------------------

      form = "%3d%10.5f%8d%8d%8d%10.1f%10.1f"
      self.prt(form % (-1, -1.0, -1, -1, -1, self.e1/obj.efact, self.emin/obj.efact))
      izero = 0
      for iTstep in xrange(self.nTsteps):
          self.annealTrials(obj)
          self.prt(form % (iTstep, self.t, self.iSch, self.iSchNeg, self.iSch-self.iSchNeg,
                           self.e1/obj.efact, self.emin/obj.efact))
          obj.analenergy()
#          print "T=%10.5f  rooms=%d" % (self.t, len(obj.sable))
          if self.iSch == 0:
              izero += 1
              if izero >= 2: break  # If no succesful changes twice, end.
          else:
              izero = 0
          self.t *= self.tFactr
          eprev = self.e1

      obj.restoreMinState()
#      print "Best:         rooms=%d" % (len(obj.sable),)
      self.anim.saveFinalImage(obj)


  def annealTrials(self, obj):
      "Annealling for 1 temperature."

#-----Trial sharings' loop
      nDsMax = obj.getDimensions()     # maximum dimension at this temperature
      self.nChan = self.spChan*nDsMax  # max number of state changes tried at any temperature
      self.nSch  = self.spSch *nDsMax  # max number of successful state changes tried at any temperature

      self.iSch    = 0     # number of succesful state changes (positive or negative)
      self.iSchNeg = 0     # number of succesful energy-negative state changes
      iChan = 0

      self.anim.saveImage(obj, self.t, self.e1)                     # For animation
      while True:
          iChan += 1
#         print "iChan=", iChan
          if iChan > self.nChan: return

          obj.saveCurState()
          obj.changeState()
          self.e2 = obj.energyState()*obj.efact                     #Thanasis2011_05_19
#         print "e1,e2=", self.e1, self.e2

          if self.metrop(self.e2-self.e1, self.t):
              if self.e2 < self.emin:
                  self.emin = self.e2
                  obj.saveMinState()
              nDim = obj.getDimensions()
              if nDim > nDsMax:
                  nDsMax = nDim
                  self.nChan    = self.spChan*nDsMax  # max number of state changes tried at any temperature
                  self.nSch     = self.spSch *nDsMax  # max number of succesful state changes tried at any temperature

              if self.e2-self.e1 <  0.0: self.iSchNeg += 1
              if self.e2-self.e1 != 0.0: self.iSch += 1
              self.e1 = self.e2
              self.anim.saveImage(obj, self.t, self.e2)                # For animation
              if self.iSch > self.nSch: return
          else:
              self.anim.saveImage(obj, self.t, self.e1, colot="green") # For animation
              obj.restorePrevState()


  def metrop(self, de, t):
      "Metropolis algorithm."
      if de < 0.0: return True
#      print "metrop de, de/t=", de, de/t
      x = self.r.random()
      xm = exp(-de/t)
#      print "metrop xm,x=", xm, x
      return (x < xm)


class SAAnnealable:
    "An abstract class for objects that can be annealed."

    def __init__(self):
        "Make default initializations."
        self.r = random.Random()
        self.efact = 1.0         # Factor to make energy compatible with the temperature
        self.ndimState = 20
        self.stateMin = self.statePrev = None;

    def analenergy(self):
        "It is called after every temperature step; for debugging."
        pass

    def getDimensions(self):
        "Return the dimensionality of current configuration of the annealing object."
        raise AttributeError, "It should have been overriden"
        return self.ndimState

    def energyState(self):
        "Return the energy of the current configuration."
        raise AttributeError, "It should have been overriden"
        return 100.0             #Thanasis2011_05_19:Do NOT multiply by self.efact:this is done in SimulatedAnnealing object

    def getState(self):
        "Return an object which fully reflects the state of the annealing object."
        raise AttributeError, "It should have been overriden"
        state = p_ggen.Struct()
        return state

    def setState(self, state):
        "Replace current state of the anneling object with the one in variable state."
        raise AttributeError, "It should have been overriden"
        pass

    def saveMinState(self):
        "Save the parameters of the current configuration - it is the best so far."
        self.stateMin = self.getState()

    def restoreMinState(self):
        "Restore the parameters of the base saved configuration."
        self.setState(self.stateMin)

    def saveCurState(self):
        "Save the parameters of the current configuration."
        self.statePrev = self.getState()

    def restorePrevState(self):
        "Restore the parameters of the previous configuration."
        self.setState(self.statePrev)

    def changeState(self):
        "Randomly change the configuration of the problem."
#       changestate should not save current configuration before changing the
#       state (anneal() does this automatically)
        raise AttributeError, "It should have been overriden"
        pass

    def initState(self, tempr, spSch):
      """Initialize random changes and calibrate energy.

      We assume that the configuration is valid, perhaps through
      __init__() or some other function which has already been called.
      """
      self.efact = 1.0
      ndim = 0.0
      ntries = 10
      for i in xrange(ntries):              # Try 10 changes in order to estimate the dimension of the problem
          self.changeState()
          ndim += self.getDimensions()
      ndim = int(ndim/ntries)               # Average dimension
      ntries = ndim*spSch 
      for i in xrange(ntries):              # Now, randomize a bit
          self.changeState()
      e1 = self.energyState()               # Initial energy #Thanasis2011_05_19:This is NOT multiplied by efact
      de = 0.0
      ntries = ndim*spSch 
      npos = 0
      for j in xrange(5):
          for i in xrange(ntries):
              self.changeState()
              e2 = self.energyState()       #Thanasis2011_05_19:This is NOT multiplied by efact
              if e2 > e1:
                  de += e2-e1
                  npos += 1
              e1 = e2
          if npos > ntries/2: break
      else:
          return False                    # Could not do calibration
      de /= npos
      self.efact = tempr / de             # Normalise delta energy to tempr (=100): efact*de = tempr
#      self.prt('Αρχική ενέργεια=%.3f' % e1)
#      self.prt("Αρχική μέση Δε =%.3f" % de)
      return True


    def imageForegroundState(self, im, ct, colot, T, e):    #Minimal example
        "Superimpose image foreground to the given the background image."
        import ImageDraw
        imd = ImageDraw.Draw(im)
        if T != None: imd.text((5,1), text="t=%.2f  e=%.1f" % (T, e), fill=colot)

    def imageBackgroundState(self, imsize):                 #Minimal example
        "Create and return background image and object for coordinate transformation."
        import Image
        width, height = imsize
        xmin = ymin = 0.0
        xmax = ymax = 100.0
        ct = p_gmath.ThanRectCoorTransf((xmin, ymin, xmax, ymax), (5, height-5, width-5, 5))
        im = Image.new("RGB", imsize, (255,255,255))
        return im, ct

    def imageForegroundState1(self, im, ct, colot, T, e):   #Example of imageForegroundState
        "Superimpose image foreground to the given the backgorund image."
        ot = list(self.pol.iterOT(self.state))
        imd = ImageDraw.Draw(im)
        self.pol.topil(imd, ct, ot=ot, colot=colot)
        if T != None: imd.text((5,1), text="t=%.2f  e=%.1f" % (T, e), fill=colot)

    def imageBackgroundState1(self, imsize):               #Example of imageBackgroundState
        "Superimpose background to the given (blank)image and return object for coordinate transformation."
        ot = list(self.pol.iterOT(self.state))
        return self.pol.pilout("", imsize[0], imsize[1], iso=self.dtm.thanLines, roads=self.pol.roads)


class SAAnimation:
    "An convenient object for storing animation data." 
    def __init__(anim):
        "Make default setting for animation."
        anim.on = False                  #If on is true, images will be made
        anim.imsize = (640, 480)         #image width and height
        anim.impref = "evol"             #Image filename prefix
        anim.im = None                   #Image which contains background
        anim.imblue = None               #Image which contains background and previous accepted OT
        anim.ct = None                   #Coordinate tranformation
        anim.ipref = 0                   #Image filname counter
        anim.iframe = -1                 #Image frame
        anim.nframe = 20                 #How many frames it skips to make final video shorter

    def config(self, on=None, size=None, nframe=None, pref=None):
        "Change default values."
        if on     != None: self.on = on               #If on is true, images will be made
        if size   != None: self.imsize = size         #image width and height
        if nframe != None: self.nframe = nframe       #How many frames it skips to make final video shorter
        if pref   != None: self.impref = pref         #Image filename prefix

    def saveImage(anim, obj, T=None, e=None, colot="blue"):
        """Save the current configuration as a raster image.

        T is the current temperature and e is the current energy.
        when colot is blue we have an accepted change in the configuration.
        when colot is green we have a rejected change in the configuration.
        The idea is to have the rejected change superimposed to the previously
        accepted blue image."""
        if not anim.on: return
        anim.iframe += 1
        if anim.iframe % anim.nframe != 0: return
        if anim.im == None:   #First time: build image background
#            roads = self.pol.roadcoor(s)
            roads = ()
            anim.im, anim.ct = obj.imageBackgroundState(anim.imsize)
            anim.imblue = anim.im.copy()
        if colot =="blue": im = anim.im.copy()
        else:              im = anim.imblue.copy()
        obj.imageForegroundState(im, anim.ct, colot, T, e)
        anim.ipref += 1
        im.save("%s%05d.jpg" % (anim.impref, anim.ipref))
        if colot == "blue": anim.imblue = im

    def saveFinalImage(anim, obj):
      "Save the image of the final solution many times, so that it can be seen for some time in the video."
      if not anim.on: return
      e2 = obj.energyState()                  # For animation  #Thanasis2011_05_19:This now returns the real energy (without efact)
      for i in xrange(anim.nframe*100):
          anim.saveImage(obj, 0.0, e2)        # For animation
