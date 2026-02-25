"A fake ImageDraw module in case ImageDraw is not available."


class Draw(object):
    "A fake Draw class."

    def __init__(self, im1):
        "No initialisation."
        pass

    def arc(self, xy, start, end, **options): pass
    def bitmap(self, xy, bitmap, **options): pass
    def chord(self, xy, start, end, **options): pass
    def ellipse(self, xy, **options): pass
    def line(self, xy, **options): pass
    def pieslice(self, xy, start, end, **options): pass
    def point(self, xy, **options): pass
    def polygon(self, xy, **options): pass
    def rectangle(self, box, **options): pass
    def text(self, position, string, **options): pass
    def textsize(self, string, options): return 8
