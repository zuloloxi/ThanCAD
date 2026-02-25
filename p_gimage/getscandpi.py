from p_ggen import Tgui as T


def getScanDpi():
    "Initialize sane system, get first scanner and the resolutions it supports."
    try:
        import sane
    except ImportError:
        return None, None, T["Python module 'sane' has not been installed\nPlease install module 'sane' and retry."]
    try:
        import _sane
    except ImportError:
        return None, None, T["Python module '_sane' was not found, while sane was found\nPlease install module '_sane' and retry."]
    try:
        sane.init()
        ss = sane.get_devices()
    except Exception as why:
        return None, None, "%s:\n%s" % (T["Module sane failed to initialize"], why)
    if len(ss) <= 0:
        return None, None, T["No scanners were found"]
    ss1 = ss[0][0]
    try:
        can = sane.open(ss1)
        resopt = can["resolution"]
        dpis = resopt.constraint
    except Exception as why:
        return None, None, "%s %s %s:\n%s" % (T["Scanner"], ss1, T["can not be accessed properly:"], why)
    if resopt.unit != sane.UNIT_DPI:
        return None, None, T["The scanner does not support resolution in dpi"]
    return can, dpis, _sane.error


def getScanDpiFake():
    "Initialize sane system, get first scanner and the resolutions it supports."
    import sanefake as sane
    import _sanefake as _sane
    sane.init()
    ss = sane.get_devices()
    ss1 = ss[0][0]
    can = sane.open(ss1)
    resopt = can["resolution"]
    dpis = resopt.constraint
    if resopt.unit != sane.UNIT_DPI:
        return None, None, T["The fake scanner does not support resolution in dpi"]
    return can, dpis, _sane.error
