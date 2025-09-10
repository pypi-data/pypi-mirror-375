"""Working with volume quantities."""

from abc import ABC, abstractproperty

from .quantity import Quantity, UnitSymbol


class VolumeUnit(UnitSymbol):
    """Symbols for volume units."""

    LITER = "L"
    LITERS = "L"
    L = "L"

    MILLILITER = "mL"
    MILLILITERS = "mL"
    ML = "mL"

    GALLON = "gal"
    GALLONS = "gal"
    GAL = "gal"

    PINT = "pt"
    PINTS = "pt"
    PT = "pt"

    QUART = "qt"
    QUARTS = "qt"
    QT = "qt"

    US_FLUID_OUNCE = "fl oz"
    US_FLUID_OUNCES = "fl oz"
    US_FL_OZ = "fl oz"
    US_OZ = "fl oz"


class Volume(Quantity, ABC):
    """Base for all volume unit types."""

    @abstractproperty
    def liters(self):
        """Return the value of this quantity in liters."""

    @property
    def milliliters(self):
        """Return the value of this quantity in milliliters."""
        return self.liters * 1000

    @abstractproperty
    def gallons(self):
        """Return the value of this quantity in gallons."""

    @property
    def pints(self):
        """Return the value of this quantity in pints."""
        return self.gallons * 8

    @property
    def quarts(self):
        """Return the value of this quantity in quarts."""
        return self.gallons * 4

    @property
    def fl_ounces_us(self):
        """Return the value of this quantity in US fluid ounces."""
        return self.gallons * 128

    def __call__(self, type):  # noqa: C901
        """Convert this Volume quantity to the given type."""
        if type == Liter:
            return Liter(self.liters)

        if type == Milliliter:
            return Milliliter(self.milliliters)

        if type == Gallon:
            return Gallon(self.gallons)

        if type == Pint:
            return Pint(self.pints)

        if type == Quart:
            return Quart(self.quarts)

        if type == FluidOunceUS:
            return FluidOunceUS(self.fl_ounces_us)

        raise TypeError(f"Cannot convert to {type}")


class Liter(Volume, symbol=VolumeUnit.LITER):
    """A quantity of volume in liters."""

    @property
    def liters(self):
        """Return the value of this quantity in liters."""
        return self.value

    @property
    def gallons(self):
        """Return the value of this quantity in gallons."""
        return self.liters * 0.2641720524


class Milliliter(Liter, symbol=VolumeUnit.MILLILITER):
    """A quantity of volume in milliliters."""

    @property
    def liters(self):
        """Return the value of this quantity in liters."""
        return self.value / 1000


class Gallon(Liter, symbol=VolumeUnit.GALLON):
    """A quantity of volume in gallons."""

    @property
    def liters(self):
        """Return the value of this quantity in liters."""
        return self.gallons * 3.785411784

    @property
    def gallons(self):
        """Return the value of this quantity in gallons."""
        return self.value


class Pint(Gallon, symbol=VolumeUnit.PINT):
    """A quantity of volume in pints."""

    @property
    def gallons(self):
        """Return the value of this quantity in gallons."""
        return self.value / 8


class Quart(Gallon, symbol=VolumeUnit.QUART):
    """A quantity of volume in quarts."""

    @property
    def gallons(self):
        """Return the value of this quantity in gallons."""
        return self.value / 4


class FluidOunceUS(Gallon, symbol=VolumeUnit.US_FLUID_OUNCE):
    """A quantity of volume in fluid ounces (US)."""

    @property
    def gallons(self):
        """Return the value of this quantity in gallons."""
        return self.value / 128
