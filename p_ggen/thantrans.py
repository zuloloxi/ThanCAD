import sys
from gen import thanUnunicode

class Translation:
    "Translation class."

    def __init__(self, *tables):
        "Initialise object."
        self.thanTables = tables    # Each table represents translation from one language to another
        self.thanLangSet("en", "en")


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
            self.thanTrans = {}
            self.thanUnknown = {}
            self.thanUnknownl = []
            return encto

        self.thanTrans = {}
        self.thanUnknown = {}
        self.thanUnknownl = []
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
