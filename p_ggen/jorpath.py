""" path.py - An object representing a path to a file or directory.

Example:

from path import path
d = path('/home/guido/bin')
for f in d.files('*.py'):
    f.chmod(0755)

This module requires Python 2.2 or later.


URL:     http://www.jorendorff.com/articles/python/path
Author:  Jason Orendorff <jason@jorendorff.com> (and others - see the url!)
Date:    23 Feb 2003

03 December, 2016: New URL by other maintainer: https://pypi.python.org/pypi/path.py
"""


# TODO
#   - Bug in write_text().  It doesn't support Universal newline mode.
#   - Better error message in listdir() when self isn't a
#     directory. (On Windows, the error message really sucks.)
#   - Make sure everything has a good docstring.
#   - Add methods for regex find and replace.
#   - guess_content_type() method?
#   - Perhaps support arguments to touch().
#   - Could add split() and join() methods that generate warnings.
#   - Note:  __add__() technically has a bug, I think, where
#     it doesn't play nice with other types that implement
#     __radd__().  Test this.

import sys, os, fnmatch, glob, shutil, codecs

__version__ = '2.0.1'
__all__ = ['path']
Python3 = sys.version_info.major == 3    #Thanasis2016_02_09
# Pre-2.3 support.  Are unicode filenames supported?
_base = str
#try:                                           #Thanasis2010_12_02:commented out
#    if os.path.supports_unicode_filenames:
#        _base = unicode
#except AttributeError:
#    pass

# Pre-2.3 workaround for basestring.
#try:                                           #Thanasis2015_04_05:DELETED as it is not used anywhere
#    basestring
#except NameError:
#    basestring = (str, unicode)

# Universal newline support
_textmode = 'r'
if sys.version_info.major < 3 and hasattr(file, 'newlines'):
    _textmode = 'U'


class path(_base):
    """ Represents a filesystem path.

    For documentation on individual methods, consult their
    counterparts in os.path.
    """

#    def __init__(self, a=""):                       #Thanasis2009_06_16
#        if issubclass(self.__class__, unicode):
#            from .gen import thanUnicode
#            #print "path is unicode:"
#            a = thanUnicode(a)
#            #print "path is unicode: path.__init__:",  a, type(a)
#        else:
#            from .gen import thanUnunicode
#            #print "path is str:"
#            a = thanUnunicode(a)
#            #print "path is str: path.__init__:",  a, type(a)
#
#        _base.__init__(self, a)


    # --- Special Python methods.

    def __repr__(self):
        return 'path(%s)' % _base.__repr__(self)

    # Adding a path and a string yields a path.
    def __add__(self, more):
        return path(_base(self) + more)

    def __radd__(self, other):
        return path(other + _base(self))

    # The / operator joins paths.
    def __div__(self, rel):
        """ fp.__div__(rel) == fp / rel == fp.joinpath(rel)

        Join two path components, adding a separator character if
        needed.
        """
        return path(os.path.join(self, rel))


    def __rdiv__(self, rel):               #Thanasis2011_02_23:new method
        """ fp.__div__(rel) == fp / rel == fp.joinpath(rel)

        Join two path components, adding a separator character if
        needed.
        """
        return path(os.path.join(rel, self))

    # Make the / operator work even when true division (or python3) is enabled.
    __truediv__ = __div__
    __rtruediv__ = __rdiv__


    def getcwd():
        """ Return the current working directory as a path object. """
        return path(os.getcwd())
    getcwd = staticmethod(getcwd)


    # --- Operations on path strings.

    def abspath(self):       return path(os.path.abspath(self))
    def normcase(self):      return path(os.path.normcase(self))
    def normpath(self):      return path(os.path.normpath(self))
    def realpath(self):      return path(os.path.realpath(self))
    def expanduser(self):    return path(os.path.expanduser(self))
    def expandvars(self):    return path(os.path.expandvars(self))
    def dirname(self):       return path(os.path.dirname(self))

    #basename = os.path.basename                                  #Thanasis2015_10_28commented out
    def basename(self):      return path(os.path.basename(self))  #Thanasis2015_10_28


    def expand(self):
        """ Clean up a filename by calling expandvars(),
        expanduser(), and normpath() on it.

        This is commonly everything needed to clean up a filename
        read from a configuration file, for example.
        """
        return self.expandvars().expanduser().expandsep().normpath()  #Thanasis2012_04_06:added expandsep()


    def expandsep(self):                    #Thanasis2012_04_06:new function
        "Change the separator to native one."
        otherseps = [sep for sep in "/\\" if sep != os.sep]
        if os.sep in self: return self      #Probably the separator is OK (insane if "/" is in a pathname in windows
        for sep in otherseps:
            if sep in self: break           #Other separator found
        else:
            return self                     #No separators at all
        return path(self.replace(sep, os.sep))


    def _get_namebase(self):
        base, ext = os.path.splitext(self.name)
        return base

    def _get_ext(self):
        f, ext = os.path.splitext(_base(self))
        return ext

    def _get_drive(self):
        drive, r = os.path.splitdrive(self)
        return path(drive)

    parent = property(
        dirname, None, None,
        """ This path's parent directory, as a new path object.

        For example, path('/usr/local/lib/libpython.so').parent == path('/usr/local/lib')
        """)

    name = property(
        basename, None, None,
        """ The name of this file or directory without the full path.

        For example, path('/usr/local/lib/libpython.so').name == 'libpython.so'
        """)

    namebase = property(
        _get_namebase, None, None,
        """ The same as path.name, but with one file extension stripped off.

        For example, path('/home/guido/python.tar.gz').name     == 'python.tar.gz',
        but          path('/home/guido/python.tar.gz').namebase == 'python.tar'
        """)

    ext = property(
        _get_ext, None, None,
        """ The file extension, for example '.py'. """)

    drive = property(
        _get_drive, None, None,
        """ The drive specifier, for example 'C:'.
        This is always empty on systems that don't use drive specifiers.
        """)

    def splitpath(self):
        """ p.splitpath() -> Return (p.parent, p.name). """
        parent, child = os.path.split(self)
        return path(parent), child

    def splitdrive(self):
        """ p.splitdrive() -> Return (p.drive, <the rest of p>).

        Split the drive specifier from this path.  If there is
        no drive specifier, p.drive is empty, so the return value
        is simply (path(''), p).  This is always the case on Unix.
        """
        drive, rel = os.path.splitdrive(self)
        return path(drive), rel

    def splitext(self):
        """ p.splitext() -> Return (p.stripext(), p.ext).

        Split the filename extension from this path and return
        the two parts.  Either part may be empty.

        The extension is everything from '.' to the end of the
        last path segment.  This has the property that if
        (a, b) == p.splitext(), then a + b == p.
        """
        # Cast to plain string using _base because Python 2.2
        # implementations of os.path.splitext use "for c in path:..."
        # which means something different when applied to a path
        # object.
        filename, ext = os.path.splitext(_base(self))
        return path(filename), ext

    def stripext(self):
        """ p.stripext() -> Remove one file extension from the path.

        For example, path('/home/guido/python.tar.gz').stripext()
        returns path('/home/guido/python.tar').
        """
        return self.splitext()[0]

    if hasattr(os.path, 'splitunc'):
        def splitunc(self):
            unc, rest = os.path.splitunc(self)
            return path(unc), rest

        def _get_uncshare(self):
            unc, r = os.path.splitunc(self)
            return path(unc)

        uncshare = property(
            _get_uncshare, None, None,
            """ The UNC mount point for this path.
            This is empty for paths on local drives. """)

    def setext(self, ext):                             #Andreas2010_01_02
        "Returns the path with new extension."
        return self.parent/self.namebase + ext

    def joinpath(self, *args):
        """ Join two or more path components, adding a separator
        character (os.sep) if needed.  Returns a new path
        object.
        """
        return path(os.path.join(self, *args))

    def splitall(self):
        """ Return a list of the path components in this path.

        The first item in the list will be a path.  Its value will be
        either os.curdir, os.pardir, empty, or the root directory of
        this path (for example, '/' or 'C:\\').  The other items in
        the list will be strings.

        path.path.joinpath(*result) will yield the original path.
        """
        parts = []
        loc = self
        while loc != os.curdir and loc != os.pardir:
            prev = loc
            loc, child = prev.splitpath()
            if loc == prev:
                break
            parts.append(child)
        parts.append(loc)
        parts.reverse()
        return parts

    def relpath(self):
        """ Return this path as a relative path,
        based from the current working directory.
        """
        cwd = path(os.getcwd())
        return cwd.relpathto(self)

    def relpathto(self, dest):
        """ Return a relative path from self to dest.

        If there is no relative path from self to dest, for example if
        they reside on different drives in Windows, then this returns
        dest.abspath().
        """
        origin = self.abspath()
        dest = path(dest).abspath()

        orig_list = origin.normcase().splitall()
        # Don't normcase dest!  We want to preserve the case.
        dest_list = dest.splitall()

        if orig_list[0] != os.path.normcase(dest_list[0]):
            # Can't get here from there.
            return dest

        # Find the location where the two paths start to differ.
        i = 0
        for start_seg, dest_seg in zip(orig_list, dest_list):
            if start_seg != os.path.normcase(dest_seg):
                break
            i += 1

        # Now i is the point where the two paths diverge.
        # Need a certain number of "os.pardir"s to work up
        # from the origin to the point of divergence.
        segments = [os.pardir] * (len(orig_list) - i)
        # Need to add the diverging part of dest_list.
        segments += dest_list[i:]
        if len(segments) == 0:
            # If they happen to be identical, use os.curdir.
            return path(os.curdir)
        else:
            return path(os.path.join(*segments))


    # --- Listing, searching, walking, and matching

    def listdir(self, pattern=None):
        """ D.listdir() -> List of items in this directory.

        Use D.files() or D.dirs() instead if you want a listing
        of just files or just subdirectories.

        The elements of the list are path objects.

        With the optional 'pattern' argument, this only lists
        items whose names match the given pattern.
        """
        names = os.listdir(self)
        if pattern is not None:
            names = fnmatch.filter(names, pattern)
        return [self / child for child in names]

    def dirs(self, pattern=None):
        """ D.dirs() -> List of this directory's subdirectories.

        The elements of the list are path objects.
        This does not walk recursively into subdirectories
        (but see path.walkdirs).

        With the optional 'pattern' argument, this only lists
        directories whose names match the given pattern.  For
        example, d.dirs('build-*').
        """
        return [p for p in self.listdir(pattern) if p.isdir()]

    def files(self, pattern=None):
        """ D.files() -> List of the files in this directory.

        The elements of the list are path objects.
        This does not walk into subdirectories (see path.walkfiles).

        With the optional 'pattern' argument, this only lists files
        whose names match the given pattern.  For example,
        d.files('*.pyc').
        """
        return [p for p in self.listdir(pattern) if p.isfile()]

    def walk(self, pattern=None):
        """ D.walk() -> iterator over files and subdirs, recursively.

        The iterator yields path objects naming each child item of
        this directory and its descendants.  This requires that
        D.isdir().

        This performs a depth-first traversal of the directory tree.
        Each directory is returned just before all its children.
        """
#        for child in self:
        for child in self.listdir():    # Thanasis Stamos Oct. 21, 2004
            if pattern is None or child.fnmatch(pattern):
                yield child
            if child.isdir():
                for item in child.walk(pattern):
                    yield item

    def walkdirs(self, pattern=None):
        """ D.walkdirs() -> iterator over subdirs, recursively.

        With the optional 'pattern' argument, this yields only
        directories whose names match the given pattern.  For
        example, mydir.walkdirs('*test') yields only directories
        with names ending in 'test'.
        """
#        for child in self:
        for child in self.listdir():    # Thanasis Stamos Oct. 21, 2004
            if child.isdir():
                if pattern is None or child.fnmatch(pattern):
                    yield child
                for subsubdir in child.walkdirs(pattern):
                    yield subsubdir

    def walkfiles(self, pattern=None):
        """ D.walkfiles() -> iterator over files in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.
        """
#        for child in self:
        for child in self.listdir():    # Thanasis Stamos Oct. 21, 2004
            if child.isfile():
                if pattern is None or child.fnmatch(pattern):
                    yield child
            elif child.isdir():
                for f in child.walkfiles(pattern):
                    yield f

    def fnmatch(self, pattern):
        """ Return True if self.name matches the given pattern.

        pattern - A filename pattern with wildcards,
            for example '*.py'.
        """
        return fnmatch.fnmatch(self.name, pattern)

    def glob(self, pattern):
        """ Return a list of path objects that match the pattern.

        pattern - a path relative to this directory, with wildcards.

        For example, path('/users').glob('*/bin/*') returns a list
        of all the files users have in their bin directories.
        """
        return map(path, glob.glob(_base(self / pattern)))


    # --- Reading or writing an entire file at once.

    def open(self, mode='r'):
        """ Open this file.  Return a file object. """
        return open(self, mode)

    def bytes(self):
        """ Open this file, read all bytes, return them as a string. """
        f = self.open('rb')
        try:
            return f.read()
        finally:
            f.close()

    def write_bytes(self, bytes, append=False):
        """ Open this file and write the given bytes to it.

        Default behavior is to overwrite any existing file.
        Call this with write_bytes(bytes, append=True) to append instead.
        """
        if append:
            mode = 'ab'
        else:
            mode = 'wb'
        f = self.open(mode)
        try:
            f.write(bytes)
        finally:
            f.close()

    def text(self, encoding=None, errors='strict'):
        """ Open this file, read it in, return the content as a string.

        This uses 'U' mode in Python 2.3 and later, so '\r\n' and '\r'
        are automatically translated to '\n'.

        Optional arguments:

        encoding - The Unicode encoding (or character set) of
            the file.  If present, the content of the file is
            decoded and returned as a unicode object; otherwise
            it is returned as an 8-bit str.
        errors - How to handle Unicode errors; see help(str.decode)
            for the options.  Default is 'strict'.
        """
        if encoding is None:
            # 8-bit
            f = self.open(_textmode)
            try:
                return f.read()
            finally:
                f.close()
        else:
            # Unicode
            f = codecs.open(self, 'r', encoding, errors)
            # (Note - Can't use 'U' mode here, since codecs.open
            # doesn't support 'U' mode, even in Python 2.3.)
            try:
                t = f.read()
            finally:
                f.close()
            return t.replace(u'\r\n', u'\n').replace(u'\r', u'\n')

    def write_text(self, text, encoding=None, errors='strict', append=False):
        """ Write the given text to this file.

        The default behavior is to overwrite any existing file;
        to append instead, use the 'append=True' keyword argument.

        There are two differences between path.write_text() and
        path.write_bytes(): Unicode handling and newline handling.

        --- Unicode

        If 'text' isn't Unicode, this essentially just does
        open(self, 'w').write(text).  The 'encoding' and 'errors'
        arguments are ignored.

        If 'text' is Unicode, it is first converted to bytes using the
        specified 'encoding' (or the default encoding if 'encoding'
        isn't specified).  The 'errors' argument applies only to this
        conversion.

        --- Newlines

        write_text() converts from programmer-friendly newlines
        (always '\n') to platform-specific newlines (see os.linesep;
        on Windows, for example, the end-of-line marker is '\r\n').
        This applies to Unicode text the same as to 8-bit text.

        Because of this conversion, the text should only contain plain
        newlines ('\n'), just like the return value of path.text().
        If the text contains the characters '\r\n', it may be written
        as '\r\r\n' or '\r\r' depending on your platform.  (This is
        exactly the same as when you open a file for writing with
        fopen(filename, "w") in C or file(filename, 'w') in Python.)
        """
        if not Python3 and isinstance(text, unicode):   #Thanasis2016_02_096
            text = text.replace(u'\n', os.linesep)
            if encoding is None:
                encoding = sys.getdefaultencoding()
            bytes1 = text.encode(encoding, errors)
            self.write_bytes(bytes1, append)
        else:
            if append:
                mode = 'a'
            else:
                mode = 'w'
            f = self.open(mode)
            try:
                f.write(text)
            finally:
                f.close()

    def lines(self, encoding=None, errors='strict', retain=True):
        """ Open this file, read all lines, return them in a list.

        Optional arguments:
            encoding - The Unicode encoding (or character set) of
                the file.  The default is None, meaning the content
                of the file is read as 8-bit characters and returned
                as a list of (non-Unicode) str objects.
            errors - How to handle Unicode errors; see help(str.decode)
                for the options.  Default is 'strict'
            retain - If true, retain newline characters; but all newline
                character combinations ('\r', '\n', '\r\n') are
                translated to '\n'.  If false, newline characters are
                stripped off.  Default is True.

        This uses 'U' mode in Python 2.3 and later.
        """
        if encoding is None and retain:
            f = self.open(_textmode)
            try:
                return f.readlines()
            finally:
                f.close()
        else:
            return self.text(encoding, errors).splitlines(retain)

    def write_lines(self, lines, encoding=None, errors='strict',
                    linesep=os.linesep):
        """ Overwrite this file with the given lines of text.

        lines - A list of strings.
        encoding - A Unicode encoding to use.  This applies only if
            'lines' contains any Unicode strings.
        errors - How to handle errors in Unicode encoding.  This
            also applies only to Unicode strings.
        linesep - A character sequence that will be added at the
            end of every line that doesn't already have it.
        """
        if Python3:     #Thanasis2016_02_096
            f = self.open('w')
            try:
                for line in lines:
                    if not line.endswith(linesep):
                        line += linesep
                    f.write(line)
            finally:
                f.close()
            return

        f = self.open('wb')
        try:
            for line in lines:
                if not line.endswith(linesep):
                    line += linesep
                if isinstance(line, unicode):   #Thanasis2016_02_096
                    if encoding is None:
                        encoding = sys.getdefaultencoding()
                    line = line.encode(encoding, errors=errors)
                f.write(line)
        finally:
            f.close()


    # --- Methods for querying the filesystem.

    def exists(self):  return os.path.exists(self)  #Thanasis2023_11_06:windoze python 3.12 support
    def isabs(self):   return os.path.isabs(self)   #Thanasis2023_11_06:windoze python 3.12 support
#    isdir = os.path.isdir                          #Thanasis2012_05_09:Does not work with python2.7.3 for windows
    def isdir(self):   return os.path.isdir(self)   #Thanasis2012_05_09
    def isfile(self):  return os.path.isfile(self)  #Thanasis2023_11_06:windoze python 3.12 support
    def islink(self):  return os.path.islink(self)  #Thanasis2023_11_06:windoze python 3.12 support
    def ismount(self): return os.path.ismount(self) #Thanasis2023_11_06:windoze python 3.12 support

    if hasattr(os.path, 'samefile'):
        def samefile(self, path2): return os.path.samefile(self, path2) #Thanasis2023_11_30:windoze python 3.12 support

    def getatime(self): return os.path.getatime(self)   #Thanasis2023_11_06:windoze python 3.12 support
    atime = property(
        getatime, None, None,
        """ Last access time of the file. """)

    def getmtime(self): return os.path.getmtime(self)   #Thanasis2023_11_06:windoze python 3.12 support
    mtime = property(
        getmtime, None, None,
        """ Last-modified time of the file. """)

    if hasattr(os.path, 'getctime'):
        def getctime(self): return os.path.getctime(self)  #Thanasis2023_11_06:windoze python 3.12 support
        ctime = property(
            getctime, None, None,
            """ Creation time of the file. """)

    def getsize(self): return os.path.getsize(self)  #Thanasis2023_11_06:windoze python 3.12 support
    size = property(
        getsize, None, None,
        """ Size of the file, in bytes. """)

    if hasattr(os, 'access'):
        def access(self, mode, **kw):   #Thanasis2023_12_01:more optional arguments
            """ Return true if current user has access to this path.

            mode - One of the constants os.F_OK, os.R_OK, os.W_OK, os.X_OK
            """
            return os.access(self, mode, **kw)

    def stat(self):
        """ Perform a stat() system call on this path. """
        return os.stat(self)

    def lstat(self, **kw):
        """ Like path.stat(), but do not follow symbolic links. """
        return os.lstat(self, **kw)   #Thanasis2023_12_01:more optional arguments

    if hasattr(os, 'statvfs'):
        def statvfs(self):
            """ Perform a statvfs() system call on this path. """
            return os.statvfs(self)

    if hasattr(os, 'pathconf'):
        def pathconf(self, name):
            return os.pathconf(self, name)


    # --- Modifying operations on files and directories

    def utime(self, times):
        """ Set the access and modified times of this file. """
        os.utime(self, times)

    def chmod(self, mode, **kw):   #Thanasis2023_12_01:more optional arguments
        """Changes the permission bits of path.

        Usage of .chmod() function
            path_object.chmod(0ijk)
        0ijk is an octal number with 3 octal digits:
        i=owner rights, j=group rights, k=all others rights
        Each of the i,j,k digits is calculated as:
            i=x*1 + w*2 + r*4
        x = 0 subjects (owner or group or others) have no execute permission
        x = 1 subjects have execute permission
        w = 0 subjects have no write permission
        w = 1 subjects have write permission
        r = 0 subjects have no read permission
        r = 1 subjects have read permission
        """
        os.chmod(self, mode, **kw)

    if hasattr(os, 'chown'):
        def chown(self, uid, gid, **kw):   #Thanasis2023_12_01:more optional arguments
            os.chown(self, uid, gid, **kw)

    def rename(self, new, **kw):   #Thanasis2023_12_01:more optional arguments
        os.rename(self, new, **kw)

    def renames(self, new):
        os.renames(self, new)


    # --- Create/delete operations on directories

    def mkdir(self, mode=0o777, **kw):   #Thanasis2023_12_01:more optional arguments
        os.mkdir(self, mode, **kw)

    def makedirs(self, mode=0o777, **kw):   #Thanasis2023_12_01:more optional arguments
        os.makedirs(self, mode, **kw)

    def makedirs1(self, mode=0o777, **kw):  #Thanasis2011_02_23:new method
        try:
            os.makedirs(self, mode, **kw)   #Thanasis2023_12_01:more optional arguments
        except:
            pass
        if not self.exists(): os.makedirs(self, mode, **kw) #makedirs did not succeed to make directory -> this raises exception
        if not self.isdir(): os.makedirs(self, mode, **kw)  #makedirs did not succeed because a file with this name exists - this raises exception

#    def makeparentdirs(self, mode="0777"):  #Thanasis2011_02_23:new method #Thanasis2015_04_05:DELETED as it is not used anywhere
#        try: os.makedirs(self.parent, mode)
#        except: pass
#        if not self.exists(): raise    #makedirs did not suceed to make directory
#        if not self.isdir(): raise     #makedirs did not succed because a file with this name exists

    def rmdir(self, **kw):   #Thanasis2023_12_01:more optional arguments
        os.rmdir(self, **kw)

    def removedirs(self):
        os.removedirs(self)


    # --- Modifying operations on files

    def touch(self):
        """ Set the access/modified times of this file to the current time.
        Create the file if it does not exist.
        """
        fd = os.open(self, os.O_WRONLY | os.O_CREAT, 0o666)
        os.close(fd)
        os.utime(self, None)

    def remove(self, **kw):   #Thanasis2023_12_01:more optional arguments
        os.remove(self, **kw)

    def unlink(self, **kw):   #Thanasis2023_12_01:more optional arguments
        os.unlink(self, **kw)


    # --- Links

    if hasattr(os, 'link'):
        def link(self, newpath, **kw):   #Thanasis2023_12_01:more optional arguments
            """ Create a hard link at 'newpath', pointing to this file. """
            os.link(self, newpath, **kw)

    if hasattr(os, 'symlink'):
        def symlink(self, newlinkk, **kw):   #Thanasis2023_12_01:more optional arguments
            """ Create a symbolic link at 'newlink', pointing here. """
            os.symlink(self, newlink, **kw)

    if hasattr(os, 'readlink'):
        def readlink(self, **kw):   #Thanasis2023_12_01:more optional arguments
            """ Return the path to which this symbolic link points.

            The result may be an absolute or a relative path.
            """
            return path(os.readlink(self, **kw))

        def readlinkabs(self, **kw):   #Thanasis2023_12_01:more optional arguments
            """ Return the path to which this symbolic link points.

            The result is always an absolute path.
            """
            p = self.readlink(**kw)
            if p.isabs():
                return p
            else:
                return (self.parent / p).abspath()


    # --- High-level functions from shutil

    def ismount(self):  return os.path.ismount(self)  #Thanasis2023_11_06:windoze python 3.12 support
    def copyfile(self, dst, **kw): return shutil.copyfile(self, dst, **kw)  #Thanasis2023_11_30:windoze python 3.12 support
    def copymode(self, dst, **kw): return shutil.copymode(self, dst, **kw)  #Thanasis2023_11_30:windoze python 3.12 support
    def copystat(self, dst, **kw): return shutil.copystat(self, dst, **kw)  #Thanasis2023_11_30:windoze python 3.12 support
    def copy(self, dst, **kw):     return shutil.copy(self, dst, **kw)      #Thanasis2023_11_30:windoze python 3.12 support
    def copy2(self, dst, **kw):    return shutil.copy2(self, dst, **kw)     #Thanasis2023_11_30:windoze python 3.12 support
    def copytree(self, dst, *args, **kw): return shutil.copytree(self, dst, *args, **kw)  #Thanasis2023_11_30:windoze python 3.12 support
    if hasattr(shutil, 'move'):
        def move(self, *args, **kw): return shutil.move(self, *args, **kw)      #Thanasis2023_11_30:windoze python 3.12 support
    def rmtree(self, *args, **kw):   return shutil.rmtree(self, *args, **kw)    #Thanasis2023_11_30:windoze python 3.12 support

    def chdir(self): os.chdir(self)            #Thanasis2006_03_12:new method

    # --- Special stuff from os

    if hasattr(os, 'chroot'):
        def chroot(self): os.chroot(self)

    if hasattr(os, 'startfile'):
        def startfile(self, *args): os.startfile(self, *args)   #Thanasis2023_12_01:more optional arguments
