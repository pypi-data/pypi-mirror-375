"""Arctans."""

from abc import ABC, abstractmethod
from typing import Any
import math
import sympy
from sympy.core.expr import Expr


class AbstractTerm(ABC):
    """Abstract term."""

    @property
    @abstractmethod
    def terms(self) -> list[tuple[Expr, Expr]]:
        """Return list of (coefficient, arctan) pairs."""

    @property
    @abstractmethod
    def term_dict(self) -> dict[Expr, Expr]:
        """Return dictionary {arctan: coefficient}."""

    def __eq__(self, other):
        if isinstance(other, AbstractTerm):
            return self.terms == other.terms
        return False

    def __add__(self, other):
        if isinstance(other, AbstractTerm):
            return ArctanSum(*self.terms, *other.terms)
        return NotImplemented

    def __iadd__(self, other):
        if not isinstance(other, AbstractTerm):
            return NotImplemented
        self = ArctanSum(*self.terms, *other.terms)
        return self

    def __sub__(self, other):
        if isinstance(other, AbstractTerm):
            return ArctanSum(*self.terms, *[(-i, j) for i, j in other.terms])
        else:
            return NotImplemented

    def __float__(self) -> float:
        out = 0.0
        for i, j in self.terms:
            out += float(i) * (math.pi / 2 if j.is_infinite else math.atan(float(j)))
        return out

    def __mul__(self, other):
        try:
            s_o = sympy.S(other)
            return ArctanSum(*[(i * s_o, j) for i, j in self.terms])
        except sympy.SympifyError:
            return NotImplemented

    def __rmul__(self, other):
        try:
            s_o = sympy.S(other)
            return ArctanSum(*[(s_o * i, j) for i, j in self.terms])
        except sympy.SympifyError:
            return NotImplemented

    def __truediv__(self, other):
        try:
            s_o = sympy.S(other)
            return ArctanSum(*[(i / s_o, j) for i, j in self.terms])
        except sympy.SympifyError:
            return NotImplemented

    @property
    def nterms(self) -> int:
        """Number of terms."""
        return len(self.terms)


class Zero(AbstractTerm):
    """Zero."""

    @property
    def terms(self) -> list[tuple[Expr, Expr]]:
        return []

    @property
    def term_dict(self) -> dict[Expr, Expr]:
        return {}

    def __str__(self) -> str:
        return "0"

    def __float__(self) -> float:
        return 0.0


class Arctan(AbstractTerm):
    """A single arctan."""

    def __init__(self, coefficient: Any, arctan: Any):
        """Initialise a single scaled arctan term.

        Args:
            coefficient: The coefficient that the arctan is scaled by
            arctan: The argument of the arctan

        """
        c = sympy.S(coefficient)
        a = sympy.S(arctan)
        if a.is_infinite:
            a = sympy.Integer(1)
            c *= 2
        if not a.is_infinite and a < 0:
            a *= -1
            c *= -1
        self._coefficient = c
        self._arctan = a

    @property
    def terms(self) -> list[tuple[Expr, Expr]]:
        return [(self._coefficient, self._arctan)]

    @property
    def term_dict(self) -> dict[Expr, Expr]:
        return {self._arctan: self._coefficient}

    def __str__(self) -> str:
        return f"{self._coefficient}[{self._arctan}]"


class ArctanSum(AbstractTerm):
    """The sum of some arctans."""

    def __init__(self, *terms: tuple[Any, Any]):
        """Initialise.

        Args:
            terms: A list of coefficient and arctan argument pairs
        """
        terms_dict = {}
        for c, a in terms:
            c = sympy.S(c)
            a = sympy.S(a)
            if a.is_infinite:
                a = sympy.Integer(1)
                c *= 2
            if not a.is_infinite and a < 0:
                a *= -1
                c *= -1
            if a not in terms_dict:
                terms_dict[a] = sympy.Integer(0)
            terms_dict[a] += c
        self._terms = [(j, i) for i, j in terms_dict.items()]
        maxa = max(j for i, j in self._terms if not j.is_infinite)
        self._terms.sort(key=lambda i: 2 * maxa if i[1].is_infinite else i[1])
        self._terms = [i for i in self._terms if i[0] != 0]
        assert len(set([i[1] for i in self._terms])) == len([i[1] for i in self._terms])

    def __repr__(self) -> str:
        return "ArctanSum(" + " + ".join(f"{i}[{j}]" for i, j in self._terms) + ")"

    def __str__(self) -> str:
        return "(" + " + ".join(f"{i}[{j}]" for i, j in self._terms) + ")"

    @property
    def terms(self) -> list[tuple[Expr, Expr]]:
        return self._terms

    @property
    def term_dict(self) -> dict[Expr, Expr]:
        return {j: i for i, j in self._terms}
