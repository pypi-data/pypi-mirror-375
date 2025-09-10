"""Functions for reducing arctans."""

import math as _math
import sympy
from arctans.primes import is_gaussian_prime, complex_factorise
from arctans.arctans import Arctan, Zero, AbstractTerm
from arctans.gaussian_integer import GaussianInteger


def convert_rational_single_arctan(arctan: Arctan) -> AbstractTerm:
    """Convert a rational arccotangent into a sum of integral arccotangents.

    Args:
        arctan: An arctan

    Returns:
        A sum of integral arccotangents
    """
    if arctan.terms[0][1].numerator == 1:
        return arctan
    b = arctan.terms[0][1].numerator
    a = arctan.terms[0][1].denominator

    out = Zero()
    sign = 1
    while b > 0:
        n = a // b
        a, b = a * n + b, a % b
        out += Arctan(sign * arctan.terms[0][0], sympy.Rational(1, n))
        sign *= -1
    return out


def convert_rational(arctan: AbstractTerm) -> AbstractTerm:
    """Convert a rational arccotangent into a sum of integral arccotangents.

    Args:
        arctan: An arctan or sum of arctans

    Returns:
        A sum of integral arccotangents
    """
    if isinstance(arctan, Arctan):
        return convert_rational_single_arctan(arctan)
    out = Zero()
    for c, a in arctan.terms:
        out += convert_rational_single_arctan(Arctan(c, a))
    return out


def reduce_single_arctan(arctan: Arctan) -> AbstractTerm:
    """Express an arctan as a sum of irreducible integral arccotangents.

    Args:
        arctan: An arctan

    Returns:
        A sum of irreducible integral arccotangents
    """
    n = GaussianInteger(arctan.terms[0][1].denominator, arctan.terms[0][1].numerator)
    if is_gaussian_prime(n):
        return arctan

    out = Zero()
    for f in complex_factorise(n):
        out += convert_rational(Arctan(arctan.terms[0][0], sympy.Rational(f.imag, f.real)))

    c = int(_math.floor((float(arctan) - float(out)) * 4 / _math.pi + 0.1))
    out += Arctan(c, 1)
    return out


def reduce(arctan: AbstractTerm) -> AbstractTerm:
    """Express an arctan as a sum of irreducible integral arccotangents.

    Args:
        arctan: An arctan or sum of arctans

    Returns:
        A sum of irreducible integral arccotangents
    """
    if isinstance(arctan, Arctan):
        return reduce_single_arctan(arctan)

    out = Zero()
    for c, a in arctan.terms:
        out += reduce_single_arctan(Arctan(c, a))
    return out
