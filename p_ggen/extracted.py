import subprocess
from .jorpath import path

def extracted(fn, tdir):
    "Extract archive files to temporary directory."
    fn = path(fn)
    r = True
    fnl = fn.lower().strip()
    if fnl.endswith(".zip") or fnl.endswith(".zipx"):
        #subprocess.check_call(["unzip", "-j", fn, "-d", tdir], stderr=subprocess.STDOUT, stdout=open("q1", "w"))
        subprocess.check_call(["7z", "x", "-y", "-o"+tdir, fn], stderr=subprocess.STDOUT, stdout=open("/dev/null", "w"))
    elif fnl.endswith(".7z") or fnl.endswith(".7zip"):
        #7z e -o/home/a12/temp/yyy project1_20140501_cv13065.7z
        subprocess.check_call(["7z", "x", "-y", "-o"+tdir, fn], stderr=subprocess.STDOUT, stdout=open("/dev/null", "w"))
    elif fnl.endswith(".rar"):
        #unrar e project1_20140501_cv10094.rar /home/a12/temp/yyy
        subprocess.check_call(["unrar", "x", fn, tdir], stderr=subprocess.STDOUT, stdout=open("/dev/null", "w"))
    elif fnl.endswith(".tar.gz") or fnl.endswith(".tz"):
        subprocess.check_call(["tar", "xfz", fn, "-C", tdir], stderr=subprocess.STDOUT, stdout=open("/dev/null", "w"))
    elif fnl.endswith(".gz"):  #Here we asume that a .gz file is gzip(ed) tar file
        subprocess.check_call(["tar", "xfz", fn, "-C", tdir], stderr=subprocess.STDOUT, stdout=open("/dev/null", "w"))
    else:
        r = False
    return r
