class OrderedSet:
    """Basically a list, but we also add the values to a dict to have faster inclusion test and index.

    For small number of elements (eg. 20 elements) it is much faster
    (25%) to use a plain list for inclusion test and index."""

    def __init__(self):
        "Initialise list and dict."
        self.vlist = []
        self.vset = dict()


    def append(self, val):
        "Append to the end of the ordered set, if not already in the ordered set."
        #if val in self.vset: print("Duplicate values OrderedSet")
        i = len(self.vlist)
        self.vlist.append(val)
        self.vset[val] = i     #index of val in the list (if it already exits, it points to the last val inserted)


    def pop(self):
        "Delete last item of the ordered set."
        val = self.vlist.pop()
        del self.vset[val]
        return val


    def list(self):
        "Return the ordered set as a list."
        return list(self.vlist)

    def __in__(self, val):
        "check if val is in the ordered set."
        return val in self.vset


    def index(self, val):
        "Return the index of val."
        return self.vset[val]


    def __getitem__(self, i):
        "Return an element given the index, or subset of the ordered dict."
        if isinstance(i, slice):    #Index is a slice
            orse = OrderedSet()
            orse.vlist = self.vlist[i]
            for j,v in enumerate(orse.vlist):
                orse.vset[v] = j
            return orse
        return self.vlist[i]     #Index should be an integer here


    def __str__(self):
        "String represatation of self."
        return str(self.vlist)
