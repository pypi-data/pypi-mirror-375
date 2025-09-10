import sympy
import math
from arctans import ArctanSum, convert_rational, reduce
from utils import isclose


def test_convert_rational():
    a = convert_rational(ArctanSum((1, sympy.Rational(1, 239))))
    assert isclose(float(a), math.atan(1 / 239))


def test_machin_term2():
    a = reduce(ArctanSum((1, sympy.Rational(1, 239))))
    assert isclose(float(a), math.atan(1 / 239))
