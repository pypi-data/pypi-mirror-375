"""Working with rate quantities."""

from abc import ABC, abstractproperty

from .quantity import Quantity, UnitSymbol


class RateUnit(UnitSymbol):
    """Symbols for rate units."""

    CENTIMETERS_PER_HOUR = "cm/h"
    CM_PER_HR = "cm/h"
    CMPH = "cm/h"

    MILLIMETERS_PER_HOUR = "mm/h"
    MM_PER_HR = "mm/h"
    MMPH = "mm/h"

    INCHES_PER_HOUR = "in/h"
    IN_PER_HR = "in/h"
    INPH = "in/h"


class Rate(Quantity, ABC):
    """Base for all rate unit types."""

    @abstractproperty
    def centimeters_per_hr(self):
        """Return the value of this quantity as centimeters per hour"""

    @property
    def millimeters_per_hr(self):
        """Return the value of this quantity as millimeters per hour"""
        return self.centimeters_per_hr * 10

    @abstractproperty
    def inches_per_hour(self):
        """Return the value of this quantity as inches per hour"""

    def __call__(self, type):  # noqa: C901
        """Convert this Rate quantity to the given type."""
        if type == CentimetersPerHour:
            return CentimetersPerHour(self.centimeters_per_hr)

        if type == MillimetersPerHour:
            return MillimetersPerHour(self.millimeters_per_hr)

        if type == InchesPerHour:
            return InchesPerHour(self.inches_per_hour)

        raise TypeError(f"Cannot convert to {type}")


class CentimetersPerHour(Rate, symbol=RateUnit.CENTIMETERS_PER_HOUR):
    """A representation of cm / hour."""

    @property
    def centimeters_per_hr(self):
        """Return the value of this quantity as centimeters per second"""
        return self.value

    @property
    def inches_per_hour(self):
        """Return the value of this quantity as inches per hour"""
        return self.centimeters_per_hr / 2.54


class MillimetersPerHour(CentimetersPerHour, symbol=RateUnit.MILLIMETERS_PER_HOUR):
    """A representation of mm / hour."""

    @property
    def centimeters_per_hr(self):
        """Return the value of this quantity as centimeters per second"""
        return self.value * 0.1


class InchesPerHour(Rate, symbol=RateUnit.INCHES_PER_HOUR):
    """A representation of inch / hour."""

    @property
    def centimeters_per_hr(self):
        """Return the value of this quantity as centimeters per second"""
        return self.inches_per_hour * 2.54

    @property
    def inches_per_hour(self):
        """Return the value of this quantity as inches per hour"""
        return self.value
