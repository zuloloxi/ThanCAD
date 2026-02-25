import sys, Tkinter

__icons = None
__tk = "An improbable value for Tk :)"
self = sys.modules[__name__]

def get(name):
    """Return a PhotoImage object named name.

    The image is created calling the local function function name().
    The created image is cached  __icons, so that a hard
    reference to the image always exists in order to keep it alive.
    If the same image is asked again, a reference to the created image
    is returned and thus we save memory.
    If Tkinter library is initialised, then destroyed and then reinitialised,
    the images are invalidated and produce error if you try to display
    them. Thus get() checks for Tk reinitialisation and deletes the
    cached images.
    """
    global __icons, __tk
    if __tk != Tkinter._default_root:
        if __icons is not None: print "Module", __name__, ": Reinitialise images"
        __icons = {}
        __tk = Tkinter._default_root

    try: return __icons[name]
    except: pass
    fun = getattr(self, name)
    ph = Tkinter.PhotoImage(data=fun())
    __icons[name] = ph
    return ph
    
def cancel(): return '\
    R0lGODlhEAAQAPECAAAAAK+0n////wAAACH5BAEBAAIALAAAAAAQABAAAAKRlChRokSJEiVKFAhR\
    okSJEgVClAhQokSJEgFKlCgQokSJAiFKlCgRoESJACVKlChRIESBECVKlChRIkCAEiVKlChRokCI\
    EiVKlChRIkCAEiVKlChRIESBECVKlCgRoESJACVKlCgQokSJAiFKlAhQokSJEgFKFAhRokSJEgVC\
    lChRokSJEiVKlChRokSJEiVKBQA7'

def clear(): return '\
    R0lGODlhEAAQAKIAANnZ2QAAAP//AICAAMDAwP///////////yH5BAEAAAAALAAAAAAQABAAAANm\
    CLrciqHLCwgQAIEAoaEYABCAEAABCAEQgAAYuryAAAEQCBCqqgAFQAAgAIYqAGAEgmqgqAYABoJq\
    oKhGIOhCoKjGBIJuoKjGDAaCaiCpxgwGgm4gqcYEgi4EkmoEgu5i6CLocjsmADs='

def help(): return '\
    R0lGODlhEAAQAJEAANnZ2QAAAP//AP///yH5BAEAAAAALAAAAAAQABAAAAJIhI+pEEEJ4WOEiJAS\
    gg9B8i0IfohEBMkh+BBxIaQQPlqIBMFHCJEg+AghEgQfIUSC4KNFRBB8TN0ISggfLUSC4KNFRBB8\
    TIUCADs='

def move(): return '\
    R0lGODlhEAAQAPECAAAAAK+0n////wAAACH5BAEBAAIALAAAAAAQABAAAAKRlChRokSJEiVKlChR\
    okCIEiVKlChRIkCAEiVKlChRIECAECVKlChRokCIEiVKlChQokCIEiFKlAhQokCIEgFKFAgQIECA\
    AAFCFAgQIECAAAFClAhQokCIEgFKlChQokCIEiFKlChRokCIEiVKlChRIECAECVKlChRIkCAEiVK\
    lChRokCIEiVKlChRokSJEiVKBQA7'

def new(): return '\
    R0lGODlhEAAQAJEAANnZ2QAAAP///////yH5BAEAAAAALAAAAAAQABAAAAJJhI+JFD8I/gXJjiD4\
    FiQ7JAg+BMmOiCD4QfItCH6QfAuCHyTfguAHybcg+EHyLQh+kHwLgh8k34LgB8m3IPhB8i0IPsVH\
    go+JBQA7'

def open(): return '\
    R0lGODlhEAAQAJEAANnZ2QAAAP//AICAACH5BAEAAAAALAAAAAAQABAAAAJNhI+pGEEhfLS4AArh\
    I0ZcUEL4EBEWJDM+wQ+Sb0Hwg+RbEPwg+RYEP0REKP4BhAgpnG8BEEIK51sAQJCyiZgZWgAAETTf\
    gmBTfCT4mFoAOw=='

def regen(): return '\
    R0lGODlhEAAQAPEDAACAAP8AAK+0n////yH5BAEBAAMALAAAAAAQABAAAAKR3Lhx48aNGzdu3Lhx\
    48aNAzdu3Lhx48aNAzFuHAgQIECAAAFuHAgQIECAAAFu3Lhx48aNAzFu3Lhx48aNAzdu3Lhx48aN\
    Gzdu3Lhx48aNGzdu3Lgx48aNGzdu3Lgw48aNGzdu3JgwYcKECRNm3JgwYcKECRNm3Lgw48aNGzdu\
    3Lgx48aNGzdu3Lhx48aNGzduBQA7'

def run(): return '\
    R0lGODlhEAAQAPIFAAAAAFhYWAAAgP8AAK+0n////wAAAAAAACH5BAEBAAUALAAAAAAQABAAAAOW\
    WFVVhVVVVVhVVYVVUlU4VVWCVSUiKFI1hVUlVVhVJYU1U1VYUlWFVVUACFAlglJVVVhQVYVQJVVY\
    VQWFUAUFWFVVgzNQFRhVMIVVVTUIVRGFBTNTWFUFhVAFBVhVVYVSBVVYBVWFVSUiWAUAgFVVVVgl\
    VYU1UyVYVVWFUlU1WCUiglJVUlhVU4UlVVVYVVWFVVVVWFWVADs='

def save(): return '\
    R0lGODlhEAAQAJEAANnZ2QAAAICAgMDAwCH5BAEAAAAALAAAAAAQABAAAAJZhI9pFB8RIITC+RYQ\
    ABSF5ltEAFAUmm8hAUBRaL6FBABFofkWEgAUheZbSABQJIpvIgFAoXy0AAiSGP8kAIIkxgcICSBE\
    QvEBQgIIkVB8gJAAAhgfj+BjWgEAOw=='

def saveas(): return '\
    R0lGODlhEAAQAKIAANnZ2QAAAICAgMDAwP//AICAAP///////yH5BAEAAAAALAAAAAAQABAAAANt\
    CLrciqHLDAghgaOrARgAIYGjqxEYACGBo6shGAAhgaOrIRgAIYGjqyEYACGBMxGqGBIAgSIRRBiq\
    EoAQIhJIqiGCARAiGEFEqgoBhEhgEAWWagBgiEQQBpZqBCCESAQGlmpIICiGLi+CLrdiAgA7'

def zoomall(): return '\
    R0lGODlhEAAQAPEDAAAAAP//AK+0n////yH5BAEBAAMALAAAAAAQABAAAAKR3Lhx48aNGzdu3Lhx\
    YcKEGTdu3LgxYcKECTdu3LgwYcKECTNu3JgQIMKAABNuXJgQYMKEABNmXJgQIcKAARNmXJgwYUCE\
    CRNmXJgwYUCECRNmXJgQIcKAARNmXJgQYMKEABNm3JgQIMKAABNu3LgwYcKECTNu3LgxYcKECTdu\
    3LhxYcKEGTdu3Lhx48aNGzduBQA7'

def zoomin(): return '\
    R0lGODlhEAAQAPEDAAAAAP//AK+0n////yH5BAEBAAMALAAAAAAQABAAAAKR3Lhx48aNGzdu3Lhx\
    YcKEGTdu3LgxYcKECTdu3LgwYUCECTNu3JgwYUCECRNuXJgwYUCECRNmXJgwYUCECRNmXBgQIECA\
    ABFmXBgQIECAABFmXJgwYUCECRNmXJgwYUCECRNm3JgwYUCECRNu3LgwYUCECTNu3LgxYcKECTdu\
    3LhxYcKEGTdu3Lhx48aNGzduBQA7'

def zoomout(): return '\
    R0lGODlhEAAQAPEDAAAAAP//AK+0n////yH5BAEBAAMALAAAAAAQABAAAAKR3Lhx48aNGzdu3Lhx\
    YcKEGTdu3LgxYcKECTdu3LgwYcKECTNu3JgwYcKECRNuXJgwYcKECRNmXJgwYcKECRNmXBgQIECA\
    ABFmXBgQIECAABFmXJgwYcKECRNmXJgwYcKECRNm3JgwYcKECRNu3LgwYcKECTNu3LgxYcKECTdu\
    3LhxYcKEGTdu3Lhx48aNGzduBQA7'

if __name__ == "__main__":
    root = Tkinter.Tk()
    ph = get("cancel")
    b = Tkinter.Button(root, image=ph)
    b.grid()
    root.mainloop()
    root = Tkinter.Tk()
    ph = get("cancel")
    b = Tkinter.Button(root, image=ph)
    b.grid()
    root.mainloop()
    