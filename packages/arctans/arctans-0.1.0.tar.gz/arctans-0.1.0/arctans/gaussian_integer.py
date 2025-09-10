"""Gaussian integers."""

from __future__ import annotations
import math as _math


class GaussianInteger:
    """A Gaussian integer."""

    def __init__(self, re: int, im: int):
        """Initialise.

        Args:
            re: The real part
            im: The imaginary part
        """
        self._re = re
        self._im = im

    def __str__(self):
        return f"({self.real}+{self.imag}j)"

    def __repr__(self):
        return f"GaussianInteger({self.real}+{self.imag}j)"

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, GaussianInteger):
            return self.real == other.real and self.imag == other.imag
        return self.as_complex() == other

    def __add__(self, other):
        if isinstance(other, GaussianInteger):
            return GaussianInteger(self.real + other.real, self.imag + other.imag)
        return self.as_complex() + other

    def __iadd__(self, other):
        if isinstance(other, GaussianInteger):
            self.real += other.real
            self.imag += other.imag
            return self
        if isinstance(other, int):
            self.real += other
            return self
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, GaussianInteger):
            return GaussianInteger(self.real - other.real, self.imag - other.imag)
        return self.as_complex() - other

    def __isub__(self, other):
        if isinstance(other, GaussianInteger):
            self.real -= other.real
            self.imag -= other.imag
            return self
        if isinstance(other, int):
            self.real -= other
            return self
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, GaussianInteger):
            return GaussianInteger(
                self.real * other.real - self.imag * other.imag,
                self.real * other.imag + self.imag * other.real,
            )
        return self.as_complex() * other

    def __mod__(self, other):
        if isinstance(other, GaussianInteger):
            num = self * other.conjugate()
            denom = (other * other.conjugate()).real
            return GaussianInteger(num.real % denom, num.imag % denom)
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, GaussianInteger):
            num = self * other.conjugate()
            denom = (other * other.conjugate()).real
            return GaussianInteger(num.real // denom, num.imag // denom)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, GaussianInteger):
            num = self * other.conjugate()
            denom = (other * other.conjugate()).real
            return num.real / denom + 1j * num.imag / denom
        return NotImplemented

    def __abs__(self):
        return _math.sqrt(self.real**2 + self.imag**2)

    def as_complex(self) -> complex | int:
        if self.imag == 0:
            return self.real
        else:
            return self.real + 1j * self.imag

    @property
    def real(self) -> int:
        return self._re

    @property
    def imag(self) -> int:
        return self._im

    def conjugate(self) -> GaussianInteger:
        """Compute the complex conjugate."""
        return GaussianInteger(self._re, -self._im)
