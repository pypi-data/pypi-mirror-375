from math import pi
import sympy
from arctans import ArctanSum
from arctans.arctans import AbstractTerm
from utils import isclose


def test_simplify():
    s = ArctanSum((1, 5), (2, 5))
    assert s.nterms == 1
    assert s.terms[0] == (3, 5)


def test_machins_formula():
    s = ArctanSum((16, sympy.Rational(1, 5)), (-4, sympy.Rational(1, 239)))
    assert isclose(float(s), pi)


def test_add():
    a = ArctanSum((16, sympy.Rational(1, 5)))
    b = ArctanSum((-4, sympy.Rational(1, 239)))

    assert isinstance(a + b, AbstractTerm)

    assert isclose(float(a + b), pi)


def test_sub():
    a = ArctanSum((16, sympy.Rational(1, 5)))
    b = ArctanSum((4, sympy.Rational(1, 239)))

    assert isinstance(a - b, AbstractTerm)

    assert isclose(float(a - b), pi)


def test_multiply():
    a = ArctanSum((4, sympy.Rational(1, 5)), (-1, sympy.Rational(1, 239)))

    assert isinstance(4 * a, AbstractTerm)
    assert isinstance(a * 4, AbstractTerm)

    assert isclose(float(4 * a), pi)
    assert isclose(float(a * 4), pi)


def test_division():
    a = ArctanSum((64, sympy.Rational(1, 5)), (-16, sympy.Rational(1, 239)))

    assert isinstance(a / 4, AbstractTerm)

    assert isclose(float(a / 4), pi)
