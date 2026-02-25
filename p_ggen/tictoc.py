import time

class Tictoc:
    def __init__(self):
        self.time1 = time.time()

    def tic(self):
        self.time1 = time.time()

    def toc(self, dt=None, mes=None):
        """If no arguments, or mes is present print time.
           If dt is present but mes is not, do not print time."""
        dta = time.time()
        dta = dta - self.time1
        if dt is not None: dta = dt
        if mes is not None:
            print("{}{:.3f} sec".format(mes, dta))
        elif dt is None:
            print("{}{:.3f} sec".format('Elapsed time is ', dta))
