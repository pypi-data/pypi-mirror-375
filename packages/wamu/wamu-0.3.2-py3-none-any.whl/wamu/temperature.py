"""Working with temperature quantities."""

from abc import ABC, abstractproperty

from deprecation import deprecated

from .quantity import Quantity, UnitSymbol


class TemperatureUnit(UnitSymbol):
    """Symbols for temperature units."""

    CELCIUS = "°C"
    DEGREES_CELCIUS = "°C"
    C = "°C"
    DEGREES_C = "°C"

    FAHRENHEIT = "°F"
    DEGREES_FAHRENHEIT = "°F"
    F = "°F"
    DEGREES_F = "°F"

    KELVIN = "K"
    DEGREES_KELVIN = "K"
    K = "K"
    DEGREES_K = "K"


class Temperature(Quantity, ABC):
    """Base for all temperature unit types."""

    @abstractproperty
    def celcius(self):
        """Return the value of this quantity as Celsius."""

    @property
    @deprecated(
        deprecated_in="0.1",
        removed_in="1.0",
        details="Use the 'celcius' property instead",
    )
    def degrees_celcius(self):
        """Return the value of this quantity as Celsius."""
        return self.celcius

    @abstractproperty
    def fahrenheit(self):
        """Return the value of this quantity as Fahrenheit."""

    @property
    @deprecated(
        deprecated_in="0.1",
        removed_in="1.0",
        details="Use the 'fahrenheit' property instead",
    )
    def degrees_fahrenheit(self):
        """Return the value of this quantity as Fahrenheit."""
        return self.fahrenheit

    @property
    def kelvin(self):
        """Return the value of this quantity as Kelvin."""
        return self.celcius + 273.15

    @property
    @deprecated(
        deprecated_in="0.1",
        removed_in="1.0",
        details="Use the 'kelvin' property instead",
    )
    def degrees_kelvin(self):
        """Return the value of this quantity as Kelvin."""
        return self.kelvin

    def __call__(self, type):  # noqa: C901
        """Convert this Temperature quantity to the given type."""
        if type == Celsius:
            return Celsius(self.celcius)

        if type == Fahrenheit:
            return Fahrenheit(self.fahrenheit)

        if type == Kelvin:
            return Kelvin(self.kelvin)

        raise TypeError(f"Cannot convert to {type}")


class Celsius(Temperature, symbol=TemperatureUnit.CELCIUS):
    """A representation of Celsius quantities."""

    @property
    def celcius(self):
        """Return the value of this quantity as Celsius."""
        return self.value

    @property
    def fahrenheit(self):
        """Return the value of this quantity as Fahrenheit."""
        return (self.celcius * 1.8) + 32


class Fahrenheit(Temperature, symbol=TemperatureUnit.FAHRENHEIT):
    """A representation of Fahrenheit quantities."""

    @property
    def celcius(self):
        """Return the value of this quantity as Celsius."""
        return (self.fahrenheit - 32) / 1.8

    @property
    def fahrenheit(self):
        """Return the value of this quantity as Fahrenheit."""
        return self.value


class Kelvin(Celsius, symbol=TemperatureUnit.KELVIN):
    """A representation of Kelvin quantities."""

    @property
    def celcius(self):
        """Return the value of this quantity as Celsius."""
        return self.value - 273.15
