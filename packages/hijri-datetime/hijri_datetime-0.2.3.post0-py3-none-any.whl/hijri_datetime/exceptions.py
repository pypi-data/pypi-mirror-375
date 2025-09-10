"""Custom exceptions for hijri-datetime package."""


class HijriError(Exception):
    """Base exception for hijri-datetime package."""
    pass


class InvalidHijriDate(HijriError):
    """Raised when an invalid Hijri date is provided."""
    pass


class ConversionError(HijriError):
    """Raised when calendar conversion fails."""
    pass


class InvalidHijriTime(HijriError):
    """Raised when an invalid Hijri time is provided."""
    pass


class DateRangeError(HijriError):
    """Raised when there's an error with date ranges."""
    pass