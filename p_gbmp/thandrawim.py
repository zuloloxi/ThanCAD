def drawdot(dc, xc, yc, color, fill, width, tags=()):
    """Draw a single dot; tags is for compatibility with the tkinter version of drawdot.

    See also p_gtkwid.drawdot()."""
    width = round(width)
    if width < 2:
        dc.point((xc, yc), fill=color)
    elif width < 5:
        kb = width//2
        ka = -kb
        if kb-ka+1 > width: ka += 1
        dc.rectangle((xc+ka, yc+ka, xc+kb, yc+kb), fill=fill, outline=color)
    else:
        #print("fill1=", fill1)
        kb = width//2
        ka = -kb
        if kb-ka+1 > width: ka += 1
        #print("ka, kb=", ka, kb)
        dc.ellipse((xc+ka, yc+ka, xc+kb, yc+kb), fill=fill, outline=color)
