"A fake ImageFont module in case ImageFont is not available."

class ImageFont:
    "PIL font wrapper"

    def getsize(self, text, *args, **kwargs):
        """
        Returns width and height (in pixels) of given text.

        :param text: Text to measure.

        :return: (width, height)
        """
        return 10

    def getmask(self, text, mode="", *args, **kwargs):
        """
        Create a bitmap for the text.

        If the font uses antialiasing, the bitmap should have mode ``L`` and use a
        maximum value of 255. Otherwise, it should have mode ``1``.

        :param text: Text to render.
        :param mode: Used by some graphics drivers to indicate what mode the
                     driver prefers; if empty, the renderer may return either
                     mode. Note that the mode is always a string, to simplify
                     C-level implementations.

                     .. versionadded:: 1.1.5

        :return: An internal PIL storage memory instance as defined by the
                 :py:mod:`PIL.Image.core` interface module.
        """
        return None



def load(filename):
    """
    Load a font file.  This function loads a font object from the given
    bitmap font file, and returns the corresponding font object.

    :param filename: Name of font file.
    :return: A font object.
    :exception OSError: If the file could not be read.
    """
    f = ImageFont()
    return f


def load_path(filename):
    """
    Load font file. Same as :py:func:`~PIL.ImageFont.load`, but searches for a
    bitmap font along the Python path.

    :param filename: Name of font file.
    :return: A font object.
    :exception OSError: If the file could not be read.
    """
    return load(filename)


    fo = ImageFont.truetype(font="LiberationMono-Regular.ttf", size=hpix)


def truetype(font=None, size=10, index=0, encoding="", layout_engine=None):
    return p_ggen.Null()
