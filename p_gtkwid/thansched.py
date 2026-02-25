"""
This module defines a means to execute commands in an orderly way, while
not allowing the user to do something else.
"""

from . import thantkutila

class ThanScheduler:
    "Schedules functions to be called one by one in order FIFO."

    def __init__ (self):
        """Initialise scheduler.

        __preempt: it is used to avoid preemptive calls to the scheduler (whether running or not).
        __running: it is true if the scheduler is running command.
        __cancel:  it will stop the processing of commands after current
        """
        self.thanSchedClear()


    def thanSchedClear(self):
        "Clears the scheduler for debugging purposes."
        self.__commands = []
        self.__cancel = self.__running = self.__preempt = False


    def thanSchedule(self, func, *args):
        "Adds a function to be processed later."
        assert not self.__preempt, "preemptive call (not run) to ThanScheduler!!"
        self.__preempt = True
        self.__commands.insert(0, (func, False, args))
        self.__preempt = False
        if not self.__running: self.__run()


    def thanReschedule(self, func, *args):
        "Adds a function to be processed later replacing it if it already exists."
        assert not self.__preempt, "preemptive call (not run) to ThanScheduler!!"
        self.__preempt = True
        self.__commands.insert(0, (func, True, args))
        self.__preempt = False
        if not self.__running: self.__run()


    def thanSchedIdle(self):
        "Returns true if scheduler has no commands left."
        assert not self.__preempt, "preemptive call (not run) to ThanScheduler!!"
        return not self.__running


    def thanSchedCancel(self):
        "Stops the scheduler after current job."
        assert not self.__preempt, "preemptive call (not run) to ThanScheduler!!"
        self.__preempt = True
        if self.__running:
            self.__cancel = True
        self.__preempt = False


    def __run(self):
        "Processes stored commands (functions)."
        assert not self.__running, "Scheduler already running!!"
        self.__running = True
        c = self.__commands
        while len(c) > 0:
            if self.__cancel: break
            func, overwrite, args = c.pop()
            if overwrite and [c1 for c1 in self.__commands if c1[0]==c[0]]: continue # If this command exists in subsequent calls, don't exceute it
            func(*args)
        self.__cancel = self.__running = False


    def thanSchedule1(self, func, *args):
        "Schedules a command and checks that it is the first to be run."
        assert not self.__preempt, "preemptive call (not run) to ThanScheduler!!"
        self.__preempt = True
        if not self.__running:
            self.__commands.insert(0, (func, False, args))
            self.__preempt = False
            if not self.__running: self.__run()
        else:
            self.__preempt = False
            mes = "Processing previous command", "Please finish current command and retry"
            try:
                win = self.winfo_toplevel()
                thantkutila.thanGudModalMessage(win, mes[1], mes[0], thantkutila.ERROR)
            except AttributeError:
                print("%s: %s" % mes)


if __name__ == "__main__":
    print(__doc__)
