from __future__ import print_function
from keyword import iskeyword
import re, logging
import p_ggen
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

reid = re.compile(r'^[a-z_][a-z0-9_]*$', re.I)

def isidentifier(s):
    "Return true if s is a python keyword."
    return reid.match(s) is not None


def loadPluginPackages(modname, modfile, packages=None):
    "Mechanism for importing plugin packages."
    basedir = p_ggen.path(modfile).parent
    allp = []
    if packages is None:
        packages = []
        for name in basedir.dirs():
            print("directory:", name)
            package = name.basename()
            print("Package:", package)
            if not package.startswith('_') and isidentifier(package) and not iskeyword(package):
                packages.append(package)

    for package in packages:
        print("----------------------------------------------------------")
        print("Package:", package)
        try:
                print("try to import:", modname+'.'+package)
                __import__(modname+'.'+package)
        except BaseException as e:
                logger.warning('Ignoring exception while loading the %r plug-in:\n%s', package, e)
        else:
                allp.append(package)
    allp.sort()
    return allp


def loadPluginModules(modname, modfile):
    "Mechanism for importing plugin modules."
    basedir = p_ggen.path(modfile).parent
    allp = []
    for name in basedir.files('*.py'):
        print("----------------------------------------------------------")
        print("file:", name)
        module = name.namebase
        print("Module:", module)
        if not module.startswith('_') and isidentifier(module) and not iskeyword(module):
            try:
                print("try to import:", modname+'.'+module)
                __import__(modname+'.'+module)
            except:
                logger.warning('Ignoring exception while loading the %r plug-in.', module)
            else:
                allp.append(module)
    allp.sort()
    return allp
