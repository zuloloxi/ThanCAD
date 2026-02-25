from __future__ import print_function
from py23 import xrange, input, iteritems, iterkeys, itervalues, next
a = {}
print("xrange:")
for i in xrange(10):
    a[i] = "a"+str(i)
    print(i)

print("input():")
t = input("enter 1+1:")
print("Answer should not be 2: answer=", t)


print("iteritems():")
for x in iteritems(a):
    print(x)


print("iterkeys():")
for x in iterkeys(a):
    print(x)


print("itervalues():")
for x in itervalues(a):
    print(x)


print("next()")
print(next(iter(a)))
class Y:
    def __next__(self):
        return "b"
    def __iter__(self): return self
temp = Y()
print(next(temp))
