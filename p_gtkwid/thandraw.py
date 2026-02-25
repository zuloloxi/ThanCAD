from tkinter import NORMAL, Label
from .thanwids import ThanEntry

def drawdot(can, x, y, color, fill, width, tags=()):
    """Draw a single dot.

    See also p_gbmp.drawdot()."""
    width = round(width)
    print('thanDrawdot():', x, y, color, fill, width, tags)
    if width < 2:
        it = can.create_line(x, y, x+1, y+1,fill=color, width=width, tags=tags)
    elif width < 3:
        it = can.create_rectangle(x, y, x+1, y+1, outline=color, fill=fill, tags=tags)
    elif width % 2 == 1:
        ka = width//2
        kb = ka + 1
        #it = can.create_rectangle(x-ka, y-ka, x+kb-1, y+kb-1, outline=col, fill=col)
        it = can.create_oval(x-ka, y-ka, x+kb-1, y+kb-1, outline=color, fill=fill, tags=tags)
    else:
        ka = width//2
        kb = ka
        #it = can.create_rectangle(x-ka, y-ka, x+kb-1, y+kb-1, outline=col, fill=col)
        it = can.create_oval(x-ka, y-ka, x+kb-1, y+kb-1, outline=color, fill=fill, tags=tags)
    return it


def labelentry(fra, ir, ic, tit, state1=NORMAL):
    "Make a Label and an Entry in adjacent cells."
    lab = Label(fra, text=tit)
    lab.grid(row=ir, column=ic, sticky="e")
    wid = ThanEntry(fra, state=state1)
    wid.grid(row=ir, column=ic+1, sticky="we")
    return wid


def can2im(can, width=None, height=None, bg="white", **kw):
    "Transform postscript (eps) file to a PIL image, with user defined background."
    #See  /home/a12/h/b/graphics/postscript"""
    import io
    from PIL import Image
    t = can.postscript(width=width, height=height, **kw).encode("utf8")   #Convert text to bytes
    fr = io.BytesIO(t)
    del t
    im = Image.open(fr, formats=("eps",))
    im.load(scale=2, transparency=True)      #scale=2 means the double resolution from default..
    del fr                                   #transparency means the background is transparent
    background = Image.new('RGBA', im.size, bg)  #Create image with the given background
    im = Image.alpha_composite(background, im)   #Replace alpha with given background
    del background
    im = im.convert("RGB")     #Get rid of alpha
    return im
