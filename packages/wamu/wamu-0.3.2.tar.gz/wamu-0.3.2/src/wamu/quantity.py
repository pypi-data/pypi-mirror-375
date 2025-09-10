"""Base functionality for working with quantities."""

from abc import abstractmethod
from enum import Enum
from typing import Union


class UnitSymbol(str, Enum):
    """Symbols for all units."""


class Quantity:
    """Base class for all quantities."""

    _unit_symbol = None

    def __init__(self, value: Union[int, float]):
        self.value = value

    def __init_subclass__(cls, symbol: UnitSymbol = None, **kwargs):
        """Register all subclasses with their symbols."""
        super().__init_subclass__(**kwargs)

        cls._unit_symbol = symbol

    @abstractmethod
    def __call__(self, type):
        """Convert this Quantity to the given type."""

    def __getattribute__(self, attr):
        """Return the requested attribute of this `Quantity`, or None.

        When callers request an attribute from a `Quantity` object, this method first
        examines the value of this `Quantity` object.  If the value is `None`, this
        method will always return `None` rather than accessing the requested attribute.

        The benefit of this approach is that subclasses do not need to check for `None`
        in each of the conversion methods.  For example, the `Temperature.degC()` method
        does not need to check for `None` since this method will prevent it from being
        called if the value is `None`.

        NOTE - this does not affect the math (dunder) operations on `Quantity` objects.
        """

        # handle special cases to avoid infinite recursion
        if attr == "value" or attr.startswith("_"):
            return object.__getattribute__(self, attr)

        # ... if the contained value is None, return None
        if self.value is None:
            return None

        # otherwise, return the requested attribute
        return object.__getattribute__(self, attr)

    def __float__(self):
        """Return the Quantity value as a `float`."""
        return float(self.value)

    def __int__(self):
        """Return the Quantity value as an `int`."""
        return int(self.value)

    def __add__(self, other):
        """Return the sum of this `Quantity` and `other`."""
        return Quantity(self.value + self._other_value(other))

    def __sub__(self, other):
        """Return the difference of this `Quantity` and `other`."""
        return Quantity(self.value - self._other_value(other))

    def __mul__(self, other):
        """Return the product of this `Quantity` and `other`."""
        return Quantity(self.value * self._other_value(other))

    def __truediv__(self, other):
        """Return the quotient of this `Quantity` and `other`."""
        return Quantity(self.value / self._other_value(other))

    def __iadd__(self, other):
        """Add the given value to this Quantity."""
        self.value += self._other_value(other)

        return self

    def __isub__(self, other):
        """Subtract the given value from this Number."""
        self.value -= self._other_value(other)

        return self

    def __imul__(self, other):
        """Multiply this `Quantity` by `other`."""
        self.value *= self._other_value(other)

        return self

    def __itruediv__(self, other):
        """Divide this `Quantity` by `other`."""
        self.value /= self._other_value(other)

        return self

    def __eq__(self, other):
        """Determine if this `Quantity` value is equal to `other`."""
        return self.value == self._other_value(other)

    def __ne__(self, other):
        """Determine if this property is not equal to the given object."""
        return self.value != self._other_value(other)

    def __le__(self, other):
        """Return `True` if this `Quantity` value is less-than-or-equal-to `other`."""
        return self < other or self == other

    def __lt__(self, other):
        """Return `True` if this `Quantity` value is less-than `other`."""
        return self.value < self._other_value(other)

    def __ge__(self, other):
        """Return `True` if this `Quantity` value is greater-than-or-equal-to `other`."""
        return self > other or self == other

    def __gt__(self, other):
        """Return `True` if this `Quantity` value is greater-than `other`."""
        return self.value > self._other_value(other)

    def __str__(self):
        """Return a human readable string for this quantity."""
        ret = str(self.value)

        if isinstance(self.symbol, UnitSymbol):
            ret += f" {self.symbol.value}"

        return ret

    def __repr__(self):
        """Return a string representation of this quantity."""
        return f"{self.__class__.__name__}({self.value})"

    def _other_value(self, other):
        """Return a float representation of `other`.

        When `other` is a number, this method will simply return the number.

        If `other` is another `Quantity`, this method will convert the value to a
        matching type for this `Quantity` and return the value.

        If `other` is unsupported, this method will raise a `TypeError`.
        """

        if isinstance(other, Quantity):
            # attempt to convert other to a matching type for this Quantity
            if not isinstance(other, self.__class__):
                try:
                    other = other(self.__class__)
                except TypeError as err:
                    raise TypeError("Incompatible types") from err

            return other.value

        return other

    @property
    def symbol(self):
        """Return the unit symbol of this quantity."""
        return self.__class__._unit_symbol
