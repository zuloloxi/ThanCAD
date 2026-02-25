from __future__ import print_function
try: temp = xrange
except: temp = range
xrange = temp
#print(xrange)


try: temp = raw_input
except: temp = input
input = temp
#print(input)


try:
    xrange
except:
    temp = next
else:
    def temp(ob):
        if hasattr(ob, "__next__"): return ob.__next__()
        else:                       return ob.next()
next = temp


def iteritems(dict1):
    if hasattr(dict1, "iteritems"):
        for x in dict1.iteritems():
            yield x
    else:
        for x in dict1.items():
            yield x


def iterkeys(dict1):
    if hasattr(dict1, "iterkeys"):
        for x in dict1.iterkeys():
            yield x
    else:
        for x in dict1.keys():
            yield x


def itervalues(dict1):
    if hasattr(dict1, "itervalues"):
        for x in dict1.itervalues():
            yield x
    else:
        for x in dict1.values():
            yield x
