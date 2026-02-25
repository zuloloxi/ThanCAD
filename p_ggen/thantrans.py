import sys
from .gen import thanUnunicode

class Translation(object):
    "Translation class."

    def __init__(self, *tables):
        "Initialise object."
        self.thanTables = list(tables)    # Each table represents translation from one language to another
        self.__zero()   #Create empty translation variables, in case language "en" is not found
        self.thanLangSet("en", "en")


    def __zero(self):
        "Empty translation variables for new language."
        self.thanTrans = {}
        self.thanUnknown = {}
        self.thanUnknownl = []


    def updateTables(*tables):
        "Update or add new tables."
        for table in tables:
            for etable in self.thanTables:
                if table["__TRANSLATION__"] == etable["__TRANSLATION__"]:
                    etable.update(table)
                    break
            else:
                self.thanTables.append(table)


    def thanLangSet(self, from_, to):
        "Set different languages."
        for table in self.thanTables:
            langfrom, encfrom, langto, encto = table["__TRANSLATION__"]
            if langfrom == from_ and langto == to: break
        else:
            if from_ != to: return None      # The translation not found; don't change status
            if from_ != "en": return None    # The translation not found; don't change status
            for table in self.thanTables:    # We look for en so that we can return the encoding
                langfrom, encfrom, langto, encto = table["__TRANSLATION__"]
                encto = encfrom
                if langfrom == from_: break
            else:
                return None                  # The translation not found; don't change status
            self.__zero()
            return encto

        self.__zero()
        self.thanTrans.update(table)
        del self.thanTrans["__TRANSLATION__"]
        return encto


    def __getitem__(self, key):
        "Return the translation of key."
        try:
            return self.thanTrans[key]
        except KeyError:
            pass                             # Translation was not found for key

        try:
            i = self.thanUnknown[key]        # We encountered the same key before
        except KeyError:
            self.thanUnknownl.append(key)    # This is the first time we encounter key
            i = 0
        self.thanUnknown[key] = i+1          # Increase how many times we encountered key
        return key                           # The "translation" is the same


    def thanReport(self, fw=sys.stdout):
        "Report all the keys which we did not found translation for."
        for key in self.thanUnknownl:
            n = max(0, 50-2-len(key))
            skey = thanUnunicode(key)
            fw.write('"%s"%s: "%s",\n' % (skey, " "*n, self.thanUnknown[key]))
