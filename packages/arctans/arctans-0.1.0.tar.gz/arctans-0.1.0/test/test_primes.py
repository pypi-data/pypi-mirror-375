import pytest
from arctans.primes import (
    largest_pfactor,
    complex_factorise,
    is_gaussian_prime,
)
from arctans import GaussianInteger

primes = [2]
for i in range(3, 1000, 2):
    for p in primes:
        if i % p == 0:
            break
    else:
        primes.append(i)


@pytest.mark.parametrize("n", range(2, 1000))
def test_largest_pfactor(n):
    assert largest_pfactor(n) == max(p for p in primes if n % p == 0)


@pytest.mark.parametrize("a", range(-13, 20))
@pytest.mark.parametrize("b", range(-13, 20))
def test_complex_primes(a, b):
    if abs(a) + abs(b) <= 1:
        # Is zero or a unit
        pytest.skip()
    lim = max(abs(a), abs(b))
    n = GaussianInteger(a, b)
    for i in range(-lim, lim + 1):
        for j in range(-lim, lim + 1):
            if a**2 + b**2 > i**2 + j**2 and abs(i) + abs(j) > 1 and n % GaussianInteger(i, j) == 0:
                assert not is_gaussian_prime(n)
                break
        else:
            continue
        break
    else:
        assert is_gaussian_prime(n)


@pytest.mark.parametrize("a", range(-13, 20))
@pytest.mark.parametrize("b", range(-13, 20))
def test_complex_factorise(a, b):
    if abs(a) + abs(b) <= 1:
        # Is zero or a unit
        pytest.skip()
    n = GaussianInteger(a, b)
    f = complex_factorise(n)
    if is_gaussian_prime(n):
        assert len(f) == 1 and f[0] == n
    else:
        assert len(f) > 1
        product = GaussianInteger(1, 0)
        for i in f:
            assert is_gaussian_prime(i)
            product *= i
        assert product == n
