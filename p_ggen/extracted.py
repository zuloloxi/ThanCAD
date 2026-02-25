import subprocess
from .jorpath import path
from .gen import Pyos

def extracted(fn, tdir):
    "Extract archive files to temporary directory."
    devnull = "/dev/null"
    if Pyos.Windows: devnull = "nul"
    flatten = False
    fn = path(fn)
    r = True
    fnl = fn.lower().strip()
    if fnl.endswith(".zip") or fnl.endswith(".zipx"):
        if flatten: iret = subprocess.run(["unzip", "-j", fn, "-d", tdir], stderr=subprocess.STDOUT, stdout=open(devnull, "w"), check=False, timeout=30) #Thanasis2019_03_05
        else:       iret = subprocess.run(["unzip", fn, "-d", tdir], stderr=subprocess.STDOUT, stdout=open(devnull, "w"), check=False, timeout=30) #Thanasis2019_03_05
        if iret.returncode != 0:
            subprocess.run(["7z", "x", "-y", "-o"+tdir, fn], stderr=subprocess.STDOUT, stdout=open(devnull, "w"), check=True, timeout=30)
    elif fnl.endswith(".7z") or fnl.endswith(".7zip"):
        #7z e -o/home/a12/temp/yyy project1_20140501_cv13065.7z
        subprocess.run(["7z", "x", "-y", "-o"+tdir, fn], stderr=subprocess.STDOUT, stdout=open(devnull, "w"), check=True, timeout=30)
    elif fnl.endswith(".rar"):
        #rar x project1_20140501_cv10094.rar /home/a12/temp/yyy
        #2018_03_01thanasis: 7z works better
        #2018_03_04thanasis: 7z does not work for a .rar. Thus we try first unrar and if this fails, then 7z
        tdir1 = tdir
        if not tdir1.endswith("/"): tdir1 = tdir1 + "/"
        iret = subprocess.run(["unrar", "x", fn, tdir1], stderr=subprocess.STDOUT, stdout= open(devnull, "w"), check=False, timeout=30)
        if iret.returncode != 0:
            subprocess.run(["7z", "x", "-y", "-o"+tdir, fn], stderr=subprocess.STDOUT, stdout=open(devnull, "w"), check=True, timeout=30)
    elif fnl.endswith(".tar.gz") or fnl.endswith(".tz"):
        subprocess.run(["tar", "xfz", fn, "-C", tdir], stderr=subprocess.STDOUT, stdout=open(devnull, "w"), check=True, timeout=30)
    elif fnl.endswith(".gz"):  #Here we asume that a .gz file is gzip(ed) tar file
        subprocess.run(["tar", "xfz", fn, "-C", tdir], stderr=subprocess.STDOUT, stdout=open(devnull, "w"), check=True, timeout=30)
    else:
        r = False
    return r
