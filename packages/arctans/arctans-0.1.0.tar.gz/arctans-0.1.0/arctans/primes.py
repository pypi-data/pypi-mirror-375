"""Mathematical utility functions."""

from functools import cache
from arctans.gaussian_integer import GaussianInteger

primes = [2]


@cache
def pfactors(n: int) -> list[int]:
    """Get list of all prime factors of n.

    Args:
        n: An integer

    Returns:
        A list of the prime factors of n, including factors multiple times when they appear more than once in the prime factorisation
    """
    out = []

    p = 2
    while n > 1:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1

    return out


def largest_pfactor(n: int) -> int:
    """Compute the largest prime factor of n.

    Args:
        n: An integer

    Returns:
        The largest prime factor of n
    """
    if n < 2:
        raise ValueError(f"Cannot find largest prime factor of {n}")
    i = 2
    while i < n:
        if n % i == 0:
            n //= i
        else:
            i += 1
    return n


def is_prime(n: int) -> bool:
    """Check if an integer is prime.

    Args:
        n: An integer

    Returns:
        True if n is prime
    """
    global primes

    i = primes[-1]
    while primes[-1] < n:
        for p in primes:
            if i % p == 0:
                break
        else:
            primes.append(i)
        i += 1
    return n in primes


def is_irreducible(n: int) -> bool:
    """Check if arctan(n) is irreducible.

    An arctan is irreducible if it cannot be written as a
    weighted sum of integer arccotangents.

    Args:
        n: An integer

    Returns:
        True if n is irreducible
    """
    return largest_pfactor(1 + n**2) >= 2 * n


def is_gaussian_prime(n: GaussianInteger) -> bool:
    """Check if n is a Gaussian prime.

    Args:
        n: An integer

    Returns:
        True if n is a Gaussian prime
    """
    if n.imag == 0 or n.real == 0:
        k = abs(n.real) + abs(n.imag)
        return k % 4 == 3 and is_prime(k)
    return is_prime(n.real**2 + n.imag**2)


def is_gaussian_unit(n: GaussianInteger) -> bool:
    """Check if n is a Gaussian unit.

    Args:
        n: An integer

    Returns:
        True if n is 1, -1, i or -i
    """
    return abs(n.real) + abs(n.imag) <= 1


@cache
def complex_factorise(n: GaussianInteger) -> list[GaussianInteger]:
    """Factorise a Gaussian integer into Gaussian primes.

    Args:
        n: An integer

    Returns:
        A list of Gaussian primes
    """
    if is_gaussian_unit(n) or is_gaussian_prime(n):
        return [n]
    lim = int(abs(n)) + 1
    for i in range(lim + 1):
        for j in range(-lim, lim + 1):
            if abs(i) + abs(j) <= 1:
                continue
            m = GaussianInteger(i, j)
            if not is_gaussian_prime(m):
                continue
            if n % m == 0:
                return [m] + complex_factorise(n // m)
    raise RuntimeError(f"Could not fund factor of non-prime number: {n}")
