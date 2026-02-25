from .bmp import ThanBmp


def getDpi2(im=None, fn=None):
    """Gets the horizontal and vertical dpi of PIL image im, which is saved in file fn.

    If dpi is found in im.info -> OK.
    If dpi is not found in im and fn=None -> return None.
    if pdi is not found in im and fn ends with .bmp then
        dpi is computed alternatively -> OK.
    """
    if "dpi" in im.info: return im.info["dpi"]
    if fn is None or not fn.lower().endswith(".bmp"):
        raise ValueError("Unable to identify dpi resolution")
    bmp = ThanBmp(open(fn, "rb"))   # may raise Value Error
    return bmp.getDpi2()


def getDpi(im=None, fn=None):
    "Gets dpi resolution and checks that horizontal and vertical resolutions are the same."
    h, v = getDpi2(im, fn)
    if int(h) != int(v):
        raise ValueError("Image horizontal and vertical resolutions are not the same; use getDpi2()")
    return h


def getDpi2d(im=None, fn=None):
    """Gets the horizontal and vertical dpi of PIL image im, which is saved in file fn.

    If dpi is found in im.info -> OK.
    If dpi is not found in im and fn=None -> return 0,0  (resolution has not been set).
    if dpi is not found in im and fn ends with .bmp then
        dpi is computed alternatively -> OK.
    """
    if "dpi" in im.info: return im.info["dpi"]
    if fn is None or not fn.lower().endswith(".bmp"): return 0, 0
    bmp = ThanBmp(open(fn, "rb"))   # may raise Value Error
    return bmp.getDpi2()


def getDpid(im=None, fn=None):
    "Gets dpi resolution and checks that horizontal and vertical resolutions are the same."
    h, v = getDpi2d(im, fn)
    if int(h) != int(v):
        raise ValueError("Image horizontal and vertical resolutions are not the same; use getDpi2d()")
    return h
