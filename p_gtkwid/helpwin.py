from tkinter import Toplevel
from p_ggen import  thanUnicode
from . import thanwids, thanfontresize, thantkutila


class ThanToplevel(Toplevel, thanfontresize.ThanFontResize):
    def destroy(self):
        self.thanDestroy()
        Toplevel.destroy(self)


def thanGudHelpWin(parentwin, mes, title, hbar=0, vbar=1, width=80, height=25,
    font=None, background="lightyellow", foreground="black"):
        "Implements an Information window."
        help1 = ThanToplevel(parentwin)
        help1.thanResizeFont(font)
        help1.title(title)

        thantkutila.thanGudPosition(help1, parentwin) #Position help1 window over parent

        txtHelp = thanwids.ThanScrolledText(help1, readonly=True, hbar=hbar, vbar=vbar,
            background=background, foreground=foreground, width=width, height=height)
        help1.thanResizeBind([txtHelp])
        mes = thanUnicode(mes)
        txtHelp.thanSet(mes)
        txtHelp.grid(sticky="wesn")

        help1.rowconfigure(0, weight=1)
        help1.columnconfigure(0, weight=1)
        txtHelp.focus_set()
        help1.focus_set()
        return help1
