"""Working with distance quantities."""

from abc import ABC, abstractproperty

from .quantity import Quantity, UnitSymbol


class DistanceUnit(UnitSymbol):
    """Symbols for distance units."""

    METER = "m"
    METERS = "m"
    M = "m"

    KILOMETER = "km"
    KILOMETERS = "km"
    KM = "km"

    CENTIMETER = "cm"
    CENTIMETERS = "cm"
    CM = "cm"

    MILLIMETER = "mm"
    MILLIMETERS = "mm"
    MM = "mm"

    MILE = "mi"
    MILES = "mi"
    MI = "mi"

    NAUTICAL_MILE = "NM"
    NAUTICAL_MILES = "NM"
    NM = "NM"

    FOOT = "ft"
    FEET = "ft"
    FT = "ft"

    INCH = "in"
    INCHES = "in"
    IN = "in"

    YARD = "yd"
    YARDS = "yd"
    YD = "yd"

    ASTRONOMICAL_UNIT = "au"
    ASTRONOMICAL_UNITS = "au"
    AU = "au"

    PARSEC = "pc"
    PARSECS = "pc"
    PC = "pc"

    LIGHT_YEAR = "ly"
    LIGHT_YEARS = "ly"
    LY = "ly"


class Distance(Quantity, ABC):
    """Base for all distance unit types."""

    @abstractproperty
    def meters(self):
        """Return the value of this quantity in meters."""

    @property
    def kilometers(self):
        """Return the value of this quantity in kilometers."""
        return self.meters * 0.001

    @property
    def centimeters(self):
        """Return the value of this quantity in centimeters."""
        return self.meters * 100

    @property
    def millimeters(self):
        """Return the value of this quantity in millimeters."""
        return self.meters * 1000

    @property
    def miles(self):
        """Return the value of this quantity in miles."""
        return self.feet / 5280

    @abstractproperty
    def feet(self):
        """Return the value of this quantity in feet."""

    @property
    def inches(self):
        """Return the value of this quantity in inches."""
        return self.feet * 12

    @property
    def yards(self):
        """Return the value of this quantity in yards."""
        return self.feet / 3

    @property
    def astronomical_units(self):
        """Return the value of this quantity in astronomical units."""
        return self.meters / 149597870700

    @property
    def nautical_miles(self):
        """Return the value of this quantity in nautical miles."""
        return self.feet * 0.00016458

    @property
    def light_years(self):
        """Return the value of this quantity in light years."""
        return self.meters / 9460730472580800

    @property
    def parsecs(self):
        """Return the value of this quantity in parsecs."""
        return self.miles / 19173511575400

    def __call__(self, type):  # noqa: C901
        """Convert this Distance quantity to the given type."""
        if type == Meter:
            return Meter(self.meters)

        if type == Kilometer:
            return Kilometer(self.kilometers)

        if type == Centimeter:
            return Centimeter(self.centimeters)

        if type == Millimeter:
            return Millimeter(self.millimeters)

        if type == Mile:
            return Mile(self.miles)

        if type == Foot:
            return Foot(self.feet)

        if type == Inch:
            return Inch(self.inches)

        if type == Yard:
            return Yard(self.yards)

        if type == NauticalMile:
            return NauticalMile(self.nautical_miles)

        if type == AstronomicalUnit:
            return AstronomicalUnit(self.astronomical_units)

        if type == LightYear:
            return LightYear(self.light_years)

        if type == Parsec:
            return Parsec(self.parsecs)

        raise TypeError(f"Cannot convert to {type}")


class Meter(Distance, symbol=DistanceUnit.METER):
    """A representation of a meter."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.value

    @property
    def feet(self):
        """Return the value of this quantity in feet."""
        return self.meters * 3.28084


class Millimeter(Meter, symbol=DistanceUnit.MILLIMETER):
    """A representation of a millimeter."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.value * 0.001


class Centimeter(Meter, symbol=DistanceUnit.CENTIMETER):
    """A representation of a centimeter."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.value * 0.01


class Kilometer(Meter, symbol=DistanceUnit.KILOMETER):
    """A representation of a kilometer."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.value * 1000


class NauticalMile(Meter, symbol=DistanceUnit.NAUTICAL_MILE):
    """A representation of a nautical mile."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.value * 1852


class Foot(Distance, symbol=DistanceUnit.FOOT):
    """A representation of foot measurements."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.feet * 0.3048

    @property
    def feet(self):
        """Return the value of this quantity in feet."""
        return self.value


class Mile(Foot, symbol=DistanceUnit.MILE):
    """A representation of a mile."""

    @property
    def feet(self):
        """Return the value of this quantity in feet."""
        return self.value * 5280


class Yard(Foot, symbol=DistanceUnit.YARD):
    """A representation of a yard."""

    @property
    def feet(self):
        """Return the value of this quantity in feet."""
        return self.value * 3


class Inch(Foot, symbol=DistanceUnit.INCH):
    """A representation of an inch."""

    @property
    def feet(self):
        """Return the value of this quantity in feet."""
        return self.value / 12


class AstronomicalUnit(Meter, symbol=DistanceUnit.ASTRONOMICAL_UNIT):
    """A representation of an astronomical unit."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.value * 149597870700


class LightYear(AstronomicalUnit, symbol=DistanceUnit.LIGHT_YEAR):
    """A representation of a light year."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.value * 9460730472580800


class Parsec(AstronomicalUnit, symbol=DistanceUnit.PARSEC):
    """A representation of a parsec."""

    @property
    def meters(self):
        """Return the value of this quantity in meters."""
        return self.value * 30856775814671900
