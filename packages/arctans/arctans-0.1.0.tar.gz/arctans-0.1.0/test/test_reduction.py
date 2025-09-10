import pytest
import sympy
from arctans import Arctan, is_irreducible, reduce, convert_rational
from utils import isclose

reducible = [3, 7, 8, 13, 17, 18, 21]


@pytest.mark.parametrize("n", range(1, 23))
def test_irreducible(n):
    assert is_irreducible(n) == (n not in reducible)


@pytest.mark.parametrize("coefficient", range(1, 20))
@pytest.mark.parametrize("arctan", range(1, 20))
def test_convert_rational_integer(coefficient, arctan):
    arctan_n = Arctan(coefficient, arctan)
    arctan_sum = convert_rational(arctan_n)
    assert isclose(float(arctan_n), float(arctan_sum))
    for i, j in arctan_sum.terms:
        assert j.numerator == 1
        assert i != 0


@pytest.mark.parametrize("numerator", range(1, 20))
@pytest.mark.parametrize("denominator", range(1, 20))
def test_convert_rational(numerator, denominator):
    arctan_n = Arctan(1, sympy.Rational(numerator, denominator))
    arctan_sum = convert_rational(arctan_n)
    assert isclose(float(arctan_n), float(arctan_sum))
    for i, j in arctan_sum.terms:
        assert j.numerator == 1
        assert i != 0


@pytest.mark.parametrize("n", reducible)
@pytest.mark.parametrize("c", [-2, -1, 1, 3, sympy.Rational(1, 2)])
def test_reduction(c, n):
    arctan_n = Arctan(c, n)
    arctan_sum = reduce(arctan_n)
    assert isclose(float(arctan_n), float(arctan_sum))
    assert arctan_sum.nterms > 1


@pytest.mark.parametrize("n", reducible)
def test_reduction_leads_to_irreducible(n):
    arctan_n = Arctan(1, n)
    reduced = reduce(arctan_n)
    for _, i in reduced.terms:
        assert i == 0 or i == 1 or is_irreducible(1 / i)


@pytest.mark.parametrize("n", range(1, 300))
def test_reduction_nonzero_coefficients(n):
    arctan_n = Arctan(1, sympy.Rational(1, n))
    arctan_sum = reduce(arctan_n)
    assert isclose(float(arctan_n), float(arctan_sum))
    for i, _ in arctan_sum.terms:
        assert i != 0
