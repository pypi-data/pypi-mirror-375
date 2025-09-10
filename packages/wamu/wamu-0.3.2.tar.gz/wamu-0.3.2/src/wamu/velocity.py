"""Working with velocity quantities."""

from abc import ABC, abstractproperty

from .quantity import Quantity, UnitSymbol


class VelocityUnit(UnitSymbol):
    """Symbols for velocity units."""

    METERS_PER_SECOND = "m/s"
    MPS = "m/s"

    KILOMETERS_PER_HOUR = "km/h"
    KM_PER_HR = "km/h"
    KPH = "km/h"

    MILES_PER_HOUR = "mph"
    MPH = "mph"

    FEET_PER_SECOND = "fps"
    FT_PER_SEC = "fps"
    FPS = "fps"

    KNOTS = "kt"
    KNOT = "kt"

    MACH = "M"


class Velocity(Quantity, ABC):
    """Base for all velocity unit types."""

    @abstractproperty
    def meters_per_sec(self):
        """Return the value of this quantity as meters per second"""

    @property
    def kilometers_per_hr(self):
        """Return the value of this quantity as kilometers per hour"""
        return self.meters_per_sec * 3.6

    @abstractproperty
    def feet_per_sec(self):
        """Return the value of this quantity as feet per second"""

    @property
    def miles_per_hr(self):
        """Return the value of this quantity as miles per hour"""
        return (self.feet_per_sec * 3600) / 5280

    @property
    def knots(self):
        """Return the value of this quantity as knots"""
        return self.kilometers_per_hr / 1.852

    @property
    def mach(self):
        """Return the value of this quantity as mach"""
        return self.meters_per_sec / 343

    def __call__(self, type):  # noqa: C901
        """Convert this Velocity quantity to the given type."""
        if type == MetersPerSecond:
            return MetersPerSecond(self.meters_per_sec)

        if type == KilometersPerHour:
            return KilometersPerHour(self.kilometers_per_hr)

        if type == MilesPerHour:
            return MilesPerHour(self.miles_per_hr)

        if type == FeetPerSecond:
            return FeetPerSecond(self.feet_per_sec)

        if type == Knots:
            return Knots(self.knots)

        if type == Mach:
            return Mach(self.mach)

        raise TypeError(f"Cannot convert {self.__class__} to {type}")


class MetersPerSecond(Velocity, symbol=VelocityUnit.METERS_PER_SECOND):
    """A representation of m/s."""

    @property
    def meters_per_sec(self):
        """Return the value of this quantity as meters per second"""
        return self.value

    @property
    def feet_per_sec(self):
        """Return the value of this quantity as feet per second"""
        return self.meters_per_sec * 3.2808399


class KilometersPerHour(MetersPerSecond, symbol=VelocityUnit.KILOMETERS_PER_HOUR):
    """A representation of km/h."""

    @property
    def meters_per_sec(self):
        """Return the value of this quantity as meters per second"""
        return (self.value * 1000) / 3600


class FeetPerSecond(Velocity, symbol=VelocityUnit.FEET_PER_SECOND):
    """A representation of fps."""

    @property
    def feet_per_sec(self):
        """Return the value of this quantity as feet per second"""
        return self.value

    @property
    def meters_per_sec(self):
        """Return the value of this quantity as meters per second"""
        return self.feet_per_sec / 3.2808399


class MilesPerHour(FeetPerSecond, symbol=VelocityUnit.MILES_PER_HOUR):
    """A representation of mph."""

    @property
    def feet_per_sec(self):
        """Return the value of this quantity as feet per second"""
        return (self.value * 5280) / 3600


class Knots(MetersPerSecond, symbol=VelocityUnit.KNOTS):
    """A representation of knots."""

    @property
    def meters_per_sec(self):
        """Return the value of this quantity as meters per second"""
        return 1.852 * self.value / 3.6


class Mach(MetersPerSecond, symbol=VelocityUnit.MACH):
    """A representation of mach."""

    @property
    def meters_per_sec(self):
        """Return the value of this quantity as meters per second"""
        return self.value * 343
