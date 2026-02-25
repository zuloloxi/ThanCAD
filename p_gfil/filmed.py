# -*- coding: iso-8859-7 -*-

import sys
from p_ggen import path, prg
fw = None
FILNAMMED = path("mediate.tmp")
pathMed = FILNAMMED
ERRORTEXT = "***ERROR***"
exParams = []

#===========================================================================

def openFileWrmed(nPro, pro):
      "Save information into the intermediate file."
      import openfile
      global pathMed, fw

#-----Open intermediate file (mediate.tmp)

      global fw
      fw = None
      if nPro > 0: pathMed = pro[0].parent.abspath() / FILNAMMED
      else:        pathMed = (path(".") / FILNAMMED).abspath()
      try: fw = open(pathMed, "w")                 # Truncates the file
      except IOError: return                       # Can not be accessed

#-----Write error message. In case the program stops abnormally, this is
#     correct. If it stops normaly, this error message will be deleted.

      fw.write(ERRORTEXT+"\n")
      fw.write(openfile.descp+"\n")                # Description of the program

#-----Save prefix for next programs in the same batch file

      fw.write("%d\n" % nPro)
      for i in xrange(nPro): fw.write(pro[i]+"\n")
      openfile.openFilePar(2, fw)                  # Write user parameters to file mediate.tmp
      fw.write(ERRORTEXT+"\n")                     # Marks the end of user parameters  

#-----Close and reopen in order to commit written lines

      fw.close(); fw = None
      fw = open(pathMed, "a")                      # open file for append

#===========================================================================

def openFileMed(pro, nPro):
      """This Sr reads prefix from intermediate file."

      nPro : The number of prefixes the program requires
      nProm: The number of prefixes in mediate.tmp (nPro<=nProm)
      """
      import openfile
      try: fr = open(pathMed, "r")
      except IOError: return None
      dline = fr.readline()
      if dline == "": fr.close(); return None    # End of file

#-----check if previous program in batch file finished abnormally

      dline = dline.strip()
      if dline == ERRORTEXT:
          openfile.descp = fr.readline().strip()
          if openfile.descp == "": openfile.descp = openfile.DLNODESC #No description for prev.program)
          prg("File %s: %s\n     %s" % (pathMed, openfile.DLERRPRV, openfile.descp))
          prg(openfile.DLRETPRV)
          openfile.stopErr1()
          sys.exit(1)

#-----Read number of prefixes

      try: nProm = int(dline)
      except: fr.close(); return None
      if nProm < nPro or nProm > 2: fr.close(); return None

#-----Read prefixes from file FILNAMMED

      for i in xrange(nProm):
          pro[i] = fr.readline()
          if pro[i] == "": fr.close(); return None
          pro[i] = path(pro[i].strip())
          if pro[i] == "":
              if openfile.prothem1Opt(i, ic) == 0: fr.close(); return None # Prefix not optional
          pro[i] = pro[i].parent / pro[i].namebase

#-----Read any program parameters

      prg(' * '+openfile.descp)
      prg(' %s %s.' % (openfile.DLGETPRE, pathMed))
      openfile.openFilePar(1, fr)     # Διάβασε άλλες παραμέτρους

#-----Read any extra parameters for following programs

      global exParams
      exParams = fr.readlines()
      fr.close()
      return nProm

#===========================================================================

def errMedFile1():
      "This sr reports error into file mediate.tmp."
      global fw
      import openfile
      if fw == None:
#---------If mediate.tmp was not open, then it could not be accessed.
#         Since the calling program ended abnormally, try to write
#         an error message to it now.
          try: fw = open(pathMed, "w")          # Trucates existing file
          except: openfile.stopErr1(); sys.exit(1)                     # Could not open it again
          fw.write("\n".join((ERRORTEXT, openfile.descp, ERRORTEXT)))
      fw.close(); fw = None

#===========================================================================

def okMedFile1(): 
      "This sr reports OK into file mediate.tmp."
      import openfile
      global fw
#      print "okMedFile1a: fw=", fw
      if fw == None:

#---------If mediate.tmp was not open, then it could not be accessed.
#         Since the calling program ended normally, we try to delete file
#         mediate.tmp. After that we can do nothing, since we do not have
#         the information that should be written to mediate.tmp.

          try: pathMed.remove()
          except Exception, why: pass
          try: FILNAMMED.remove()
          except Exception, why: pass
          return
      if not openfile.fylPro:

#---------Intemediate file is not needed by the following programs. Delete it.

#          print "okMedFile1b: fw=", fw
          fw.close()
          try: pathMed.remove()
          except Exception, why: pass
          try: FILNAMMED.remove()
          except Exception, why: pass
          return

#----Ignore the first 2 lines which contain the error sentinel

      fw.close()
      fr = open(pathMed, "r")
      dlines = fr.readlines()
      fr.close()
      del dlines[:2]

#-----Open mediate.tmp again and write the lines read

      fw = open(pathMed, "w")
      fw.writelines(dlines)

#-----Write any extra parameters for following programs

      fw.write("\n".join(exParams))
      fw.close(); fw = None
