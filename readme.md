Release notes for ThanCad 0.9.2 "Tartu"
Tuesay January 20, 2026

1. Source code
--------------
The source code of ThanCad is given as a .zip file for all platforms.
Download the file thancad-0.9.2-source.zip, change to the directory which
was created, and run ThanCad as:
    python thancad.py
Please note that ThanCad was ported to python 3 and will not run in python 2
any more. Thus, depending on your OS, you may have to run ThanCad as:
    python3 thancad.py
ThanCad is known to work in Linux (Ubuntu, SuSE), FreeBSD (PCBSD), OpenBSD and 
Windows (XP, 7, 10). ThanCad works with older and recent macOS versions
(not tested as the developers do not have any Mac computers).
In order to run ThanCad you need to have the following installed in
your computer:

python 3 (programming language)
pywin32 (only for Windoze)
numpy for python3 (Python numeric library)
Pillow for python 3 (Python Image Library fork)
xlrd, xlwt, openpyxl (read/write xls/xlsx)
pexpect (communication with other programs)

You also need several modules that come with python (but may not be
available in unusual environments such as cell-phones).


2. Standalone for Windows
--------------------------
For those who are still in windows, a windows installer is included.
Download thancad-0.9.2-win64.msi and run it.


3. For all other platforms
--------------------------
For all other platforms, you can run ThanCad from source code as described
previously.


Share and Enjoy,

Thanasis Stamos
