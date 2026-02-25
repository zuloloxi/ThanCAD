import collections

def groupitems(seq, key):
    "Group all elements of seq with the same key together; key is a function; return key, keyseq pairs."
    groupbykey = collections.defaultdict(list)
    for e in seq:
        ekey = key(e)
        groupbykey[ekey].append(e)
    return groupbykey.items()
#def group(seq, key):    #Only python 3
#    "Group all elements of seq with the same key together; key is a function; return only the grouped elements."
#    for ekey, keyseq in groupitems:
#        yield from keyseq
