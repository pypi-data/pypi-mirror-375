from math import pi
import pytest
from arctans import Arctan, generate
from utils import isclose


@pytest.mark.parametrize("max_d", [10, 25])
def test_generate(max_d):
    formulae = generate([Arctan(4, 1)], max_denominator=max_d, max_terms=8)
    for f in formulae:
        assert isclose(float(f), pi)
    print(f"Found {len(formulae)} new formulae for pi")
    formulae = generate(formulae, max_denominator=max_d, max_terms=8)
    for f in formulae:
        assert isclose(float(f), pi)
    print(f"Found {len(formulae)} more new formulae for pi")


def test_generate_with_numerator():
    formulae = generate([Arctan(4, 1)], max_denominator=10, max_numerator=2, max_terms=8)
    for f in formulae:
        assert isclose(float(f), pi)
    print(f"Found {len(formulae)} formulae for pi")
