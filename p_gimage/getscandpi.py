from p_ggen import Tgui as T, inpMchoice


def getScanDpi(verbose=False, preferredscanner=None):
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
        if verbose: print("Getting scanners..")
        sane.init()
        ss = sane.get_devices()
    except Exception as why:
        return None, None, "%s:\n%s" % (T["Module sane failed to initialize"], why)
    if len(ss) <= 0:
        return None, None, T["No scanners were found"]
    ss1 = selectScanner(verbose, ss, preferredscanner)
    try:
        if verbose: print("Opening scanner %s .." % (ss1))
        can = sane.open(ss1)
        resopt = can["resolution"]
        dpis = resopt.constraint
    except Exception as why:
        return None, None, "%s %s %s:\n%s" % (T["Scanner"], ss1, T["can not be accessed properly:"], why)
    if resopt.unit != _sane.UNIT_DPI:
        return None, None, T["The scanner does not support resolution in dpi"]
    return can, dpis, _sane.error


def selectScanner(verbose, ss, preferredscanner):
    "Try to find the preferredscanner and if not found ask the user to choose."
    if verbose: 
        print("{} scanners were found:".format(len(ss)))
        for temp in ss: print("    ", temp[0])

    if preferredscanner is None:  #User did not specify scanner
        if len(ss) == 1: #User did not specify scanner and there is only 1 scanner available -> autoselect it
            if verbose: print("Autoselecting scanner {}".format(ss[0][0]))
            return ss[0][0]
        else:            #User did not specify scanner and there more than 1 scanners available -> let them choose
            return select1(verbose, ss, "\nMany scanners were found. Please select:")
    else:                         #User did specify a scanner
        preferredscanner = preferredscanner.lower()
        temps = []
        for i, temp in enumerate(ss):
            if preferredscanner in temp[0].lower():  temps.append(temp)

        if len(temps) == 1:  #User specified scanner found -> autoselect it
            if verbose: print("Autoselecting user specified scanner {}".format(temp[0]))
            return temps[0][0]
        elif len(temps) > 1: #User specified scanner matches more than 1 scanner -> let them choose
            return select1(verbose, temps, "\nUser specified scanner {} matches more than 1 scanners. Please select:".format(preferredscanner))
        elif len(ss) == 1:   #User specified scanner NOT found, and there is only 1 scanner available -> autoselect it
            if verbose: print("\nUser specified scanner {} was not found. Autoselecting scanner {}".format(preferredscanner, ss[0][0]))
            return ss[0][0]
        else:                #User specified scanner NOT found, and there more than 1 scanners available -> let them choose
            return select1(verbose, ss, "\nUser specified scanner {} was not found, but many other scanners were found. Please select:".format(preferredscanner))


def select1(verbose, ss, mes): 
    "Let user select 1 of many scanners."
    if verbose: print(mes)
    coms = []
    for i, temp in enumerate(ss):
        coms.append("{}. {}".format(i+1, temp[0]))
    i = inpMchoice("Please select scanner (enter=1): ", coms, douDef=1) - 1
    return ss[i][0]


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
