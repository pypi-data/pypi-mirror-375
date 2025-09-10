"""Working with weight quantities."""

from abc import ABC, abstractproperty

from .quantity import Quantity, UnitSymbol


class WeightUnit(UnitSymbol):
    """Symbols for weight units."""

    KILOGRAM = "kg"
    KILOGRAMS = "kg"
    KG = "kg"

    GRAM = "g"
    GRAMS = "g"
    G = "g"

    MILLIGRAM = "mg"
    MILLIGRAMS = "mg"
    MG = "mg"

    POUND = "lb"
    POUNDS = "lb"
    LB = "lb"

    OUNCE = "oz"
    OUNCES = "oz"
    OZ = "oz"

    TON = "ton"
    TONS = "tons"


class Weight(Quantity, ABC):
    """Base for all weight unit types."""

    @abstractproperty
    def kilograms(self):
        """Return the value of this quantity in kilograms."""

    @property
    def grams(self):
        """Return the value of this quantity in grams."""
        return self.kilograms * 1000

    @property
    def milligrams(self):
        """Return the value of this quantity in milligrams."""
        return self.grams * 1000

    @abstractproperty
    def pounds(self):
        """Return the value of this quantity in pounds."""

    @property
    def ounces(self):
        """Return the value of this quantity in ounces."""
        return self.pounds * 16

    @property
    def tons(self):
        """Return the value of this quantity in tons."""
        return self.pounds / 2000

    def __call__(self, type):  # noqa: C901
        """Convert this Weight quantity to the given type."""
        if type == Kilogram:
            return Kilogram(self.kilograms)

        if type == Gram:
            return Gram(self.grams)

        if type == Milligram:
            return Milligram(self.milligrams)

        if type == Pound:
            return Pound(self.pounds)

        if type == Ounce:
            return Ounce(self.ounces)

        if type == Ton:
            return Ton(self.tons)

        raise TypeError(f"Cannot convert to {type}")


class Kilogram(Weight, symbol=WeightUnit.KILOGRAM):
    """A quantity of weight in kilograms."""

    @property
    def kilograms(self):
        """Return the value of this quantity in kilograms."""
        return self.value

    @property
    def pounds(self):
        """Return the value of this quantity in pounds."""
        return self.kilograms * 2.20462262


class Gram(Kilogram, symbol=WeightUnit.GRAM):
    """A quantity of weight in grams."""

    @property
    def kilograms(self):
        """Return the value of this quantity in kilograms."""
        return self.value / 1000


class Milligram(Kilogram, symbol=WeightUnit.MILLIGRAM):
    """A quantity of weight in milligrams."""

    @property
    def kilograms(self):
        """Return the value of this quantity in kilograms."""
        return self.value / 1000000


class Pound(Weight, symbol=WeightUnit.POUND):
    """A quantity of weight in pounds."""

    @property
    def kilograms(self):
        """Return the value of this quantity in kilograms."""
        return self.pounds * 0.45359237

    @property
    def pounds(self):
        """Return the value of this quantity in pounds."""
        return self.value


class Ounce(Pound, symbol=WeightUnit.OUNCE):
    """A quantity of weight in ounces."""

    @property
    def pounds(self):
        """Return the value of this quantity in pounds."""
        return self.value / 16


class Ton(Pound, symbol=WeightUnit.TON):
    """A quantity of weight in standard (short) tons."""

    @property
    def pounds(self):
        """Return the value of this quantity in pounds."""
        return self.value * 2000
