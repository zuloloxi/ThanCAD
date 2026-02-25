import decimal

def dabs(x):
    "Absolute value of decimal numbers."
    if x < 0: x = -x
    return x

def datan2(dy, dx):
    "Return arctangent with diereynhsh."
    if dx == 0:
        if dy == 0:  return decimal.Decimal(0)
        elif dy > 0: return dpi() / decimal.Decimal(2)
        else:        return dpi() * decimal.Decimal(3) / decimal.Decimal(2)
    a = datan(dabs(dy/dx))
    if dx >= 0:
        if dy < 0: a = decimal.Decimal(2)*dpi() - a
    else:
        if dy < 0: a = dpi() + a
        else:      a = dpi() - a
    return a


def datan(x):
    "Compute arctangent; see https://mypage.concordia.ca/mathstat/rhall/mc/arctan.pdf."
    decimal.getcontext().prec += 2
    if x > 1:
        return dpi() / decimal.Decimal(2) - datan(decimal.Decimal(1)/x)
    term = x    #s is assumed to be Decimal
    lasts = term
    n = 0
    while True:
        n += 1
        term *= x * x
        term = -term
        s = lasts + term/(2*n+1)
        if s == lasts: break
        lasts = s
    return s


#The following routines were taken from python manual: https://docs.python.org/3/library/decimal.html

def dexp(x):
    """Return e raised to the power of x.  Result type matches input type.

    >>> print(exp(Decimal(1)))
    2.718281828459045235360287471
    >>> print(exp(Decimal(2)))
    7.389056098930650227230427461
    >>> print(exp(2.0))
    7.38905609893
    >>> print(exp(2+0j))
    (7.38905609893+0j)

    """
    decimal.getcontext().prec += 2
    i, lasts, s, fact, num = 0, 0, 1, 1, 1
    while s != lasts:
        lasts = s
        i += 1
        fact *= i
        num *= x
        s += num / fact
    deciaml.getcontext().prec -= 2
    return +s

def dcos(x):
    """Return the cosine of x as measured in radians.

    The Taylor series approximation works best for a small value of x.
    For larger values, first compute x = x % (2 * pi).

    >>> print(cos(Decimal('0.5')))
    0.8775825618903727161162815826
    >>> print(cos(0.5))
    0.87758256189
    >>> print(cos(0.5+0j))
    (0.87758256189+0j)

    """
    decimal.getcontext().prec += 2
    i, lasts, s, fact, num, sign = 0, 0, 1, 1, 1, 1
    while s != lasts:
        lasts = s
        i += 2
        fact *= i * (i-1)
        num *= x * x
        sign *= -1
        s += num / fact * sign
    decimal.getcontext().prec -= 2
    return +s


def dsin(x):
    """Return the sine of x as measured in radians.

    The Taylor series approximation works best for a small value of x.
    For larger values, first compute x = x % (2 * pi).

    >>> print(sin(Decimal('0.5')))
    0.4794255386042030002732879352
    >>> print(sin(0.5))
    0.479425538604
    >>> print(sin(0.5+0j))
    (0.479425538604+0j)

    """
    decimal.getcontext().prec += 2
    i, lasts, s, fact, num, sign = 1, 0, x, 1, x, 1
    while s != lasts:
        lasts = s
        i += 2
        fact *= i * (i-1)
        num *= x * x
        sign *= -1
        s += num / fact * sign
    decimal.getcontext().prec -= 2
    return +s


_dpi = -1
_dpiprec = -1
def dpi():
    """Compute Pi to the current precision.

    >>> print(pi())
    3.141592653589793238462643383

    """
    global _dpi, _dpiprec
    if decimal.getcontext().prec == _dpiprec: return _dpi  # pi is already calculated

    decimal.getcontext().prec += 2  # extra digits for intermediate steps
    three = decimal.Decimal(3)      # substitute "three=3.0" for regular floats
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    decimal.getcontext().prec -= 2
    _dpi = +s               # unary plus applies the new precision
    _dpiprec = decimal.getcontext().prec
    return _dpi
