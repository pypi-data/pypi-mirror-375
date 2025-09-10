"""Working with pressure quantities."""

from abc import ABC, abstractproperty

from .quantity import Quantity, UnitSymbol


class PressureUnit(UnitSymbol):
    """Symbols for pressure units."""

    HECTOPASCAL = "hPa"
    HECTOPASCALS = "hPa"
    HPA = "hPa"

    PASCAL = "Pa"
    PASCALS = "Pa"
    PA = "Pa"

    INCHES_MERCURY = "inHg"
    INHG = "inHg"

    POUNDS_PER_SQUARE_INCH = "psi"
    LBS_PER_SQ_IN = "psi"
    PSI = "psi"

    BAR = "bar"

    ATMOSPHERE = "atm"
    ATM = "atm"


class Pressure(Quantity, ABC):
    """Base for all pressure unit types."""

    @property
    def bar(self):
        """Return the value of this quantity as bar."""
        return self.hectopascals * 0.001

    @property
    def atmosphere(self):
        """Return the value of this quantity as Atmospheres."""
        return self.pascals / 101325

    @property
    def hectopascals(self):
        """Return the value of this quantity as Hectopascals."""
        return self.pascals * 0.01

    @abstractproperty
    def pascals(self):
        """Return the value of this quantity as Pascals."""

    @abstractproperty
    def pounds_per_sq_in(self):
        """Return the value of this quantity as pounds-per-square-inch."""

    @property
    def inches_mercury(self):
        """Return the value of this quantity as inches-mercury."""
        return self.pounds_per_sq_in * 2.0360206507731

    def __call__(self, type):  # noqa: C901
        """Convert this Pressure quantity to the given type."""
        if type == Pascal:
            return Pascal(self.pascals)

        if type == Hectopascal:
            return Hectopascal(self.hectopascals)

        if type == InchesMercury:
            return InchesMercury(self.inches_mercury)

        raise TypeError(f"Cannot convert to {type}")


class Bar(Pressure, symbol=PressureUnit.BAR):
    """A representation of Bars."""

    @property
    def pascals(self):
        """Return the value of this quantity as Pascals."""
        return self.value * 100000

    @property
    def pounds_per_sq_in(self):
        """Return the value of this quantity as pounds-per-square-inch."""
        return self.value * 14.503773800722


class Atmosphere(Pressure, symbol=PressureUnit.ATMOSPHERE):
    """A representation of Atmospheres."""

    @property
    def pascals(self):
        """Return the value of this quantity as Pascals."""
        return self.value * 101325

    @property
    def pounds_per_sq_in(self):
        """Return the value of this quantity as pounds-per-square-inch."""
        return self.value * 14.695948775513


class Pascal(Pressure, symbol=PressureUnit.PASCAL):
    """A representation of Pascals."""

    @property
    def pascals(self):
        """Return the value of this quantity as Pascals."""
        return self.value

    @property
    def pounds_per_sq_in(self):
        """Return the value of this quantity as pounds-per-square-inch."""
        return self.pascals / 6894.75729


class Hectopascal(Pascal, symbol=PressureUnit.HECTOPASCAL):
    """A representation of Hectopascals."""

    @property
    def pascals(self):
        """Return the value of this quantity as Pascals."""
        return self.value * 100


class PoundsPerSquareInch(Pressure, symbol=PressureUnit.POUNDS_PER_SQUARE_INCH):
    """A representation of PoundsPerSquareInch."""

    @property
    def pascals(self):
        """Return the value of this quantity as Pascals."""
        return self.pounds_per_sq_in * 6894.75729

    @property
    def pounds_per_sq_in(self):
        """Return the value of this quantity as pounds-per-square-inch."""
        return self.value


class InchesMercury(Pressure, symbol=PressureUnit.INCHES_MERCURY):
    """A representation of InchesMercury."""

    @property
    def pascals(self):
        """Return the value of this quantity as Pascals."""
        return self.inches_mercury * 3386.3886666667

    @property
    def inches_mercury(self):
        """Return the value of this quantity as inches-mercury."""
        return self.value

    @property
    def pounds_per_sq_in(self):
        """Return the value of this quantity as pounds-per-square-inch."""
        return self.inches_mercury * 0.4911541996322
