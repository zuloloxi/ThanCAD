from __future__ import print_function
from .gen import Pyos
#Please see also sys.getzizeof()

if Pyos.Windows:
#   from ctypes import *
    from ctypes import Structure, windll, c_ulong, byref
    from ctypes.wintypes import DWORD
    SIZE_T = c_ulong

    class MemStat(Structure):
        _fields_ = [ ("dwLength", DWORD),
                     ("dwMemoryLength", DWORD),
                     ("dwTotalPhys", SIZE_T),
                     ("dwAvailPhys", SIZE_T),
                     ("dwTotalPageFile", SIZE_T),
                     ("dwAvailPageFile", SIZE_T),
                     ("dwTotalVirtual", SIZE_T),
                     ("dwAvailVirtualPhys", SIZE_T)
                   ]

        def update(self):
            windll.kernel32.GlobalMemoryStatus(byref(self))

        def show(self):
            self.update()
            result = []
            for field_name, field_type in self._fields_:
                result.append("%s, %s\n" \
                % (field_name, getattr(self, field_name)))
            return ''.join(result)

    memstat = MemStat()
    def memTotal():
        "Return the total memory (kB) of the computer in WinDoze."
        memstat.update()
        return memstat.dwTotalPhys

elif Pyos.Linux:
    def memTotal():
        "Return the total memory (kB) of the computer in Linux."
        try:
            with open("/proc/meminfo", "r") as fr:
                for dline in fr:
                    dl = dline.split()
                    if dl[0] != "MemTotal:": continue
                    m = int(dl[1])
                    break
        except (IOError, IndexError, ValueError) as e:
            return None
        return m

elif Pyos.Freebsd:
    def memTotal():
        "Return the total memory (kB) of the computer in FreeBsd."
        try:
            from subprocess import check_output, CalledProcessError
            dline = check_output("/sbin/sysctl hw.physmem")
            dl = dline.split()
            m = int(dl[2])
        except (OSError, IndexError, ValueError, ImportError, CalledProcessError) as e:
            return None
        return m

else:
    def memTotal():
        "Return the total memory (kB) of the computer in other OSes."
        return None


if __name__ == "__main__":
    print("Total memory of computer: %s" % (memTotal(),))
