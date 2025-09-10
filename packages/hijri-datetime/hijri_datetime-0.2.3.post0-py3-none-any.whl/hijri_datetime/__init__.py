"""
hijri-datetime: Pythonic Hijri datetime operations.

A comprehensive library for working with Hijri (Islamic) calendar dates,
providing seamless conversion between Hijri, Gregorian, and Jalali calendars.
"""
"""
hijri-datetime: Pythonic Hijri datetime operations.
"""

# Version management with fallback
try:
    from _version import __version__
except ImportError:
    # Fallback version when setuptools_scm hasn't run yet
    try:
        from importlib.metadata import version
        __version__ = version("hijri-datetime")
    except ImportError:
        # Ultimate fallback
        __version__ = "unknown"

# Main exports
from .date import (
    HijriDate,
)

from .datetime import (
    HijriDateTime,
)


from .time import (
    HijriTime,
)


from .range import (
    HijriDateRange,
)

from .conversion import (
    hijri_to_gregorian,
    gregorian_to_hijri,
    hijri_to_jalali,
    jalali_to_hijri,
)

from .exceptions import (
    HijriError,
    InvalidHijriDate,
    ConversionError,
)

from .utils import (
    is_valid_hijri_date,
    get_hijri_month_name,
    get_hijri_weekday_name,
)

# Convenience imports
from .constants import (
    HIJRI_MONTHS,
    HIJRI_WEEKDAYS,
    ISLAMIC_EPOCH,
)

__all__ = [
    "__version__",
    # Core classes
    "HijriDate",
    "HijriDateTime", 
    "HijriTime",
    "HijriDateRange",
    # Conversion functions
    "hijri_to_gregorian",
    "gregorian_to_hijri",
    "hijri_to_jalali",
    "jalali_to_hijri",
    # Exceptions
    "HijriError",
    "InvalidHijriDate",
    "ConversionError",
    # Utilities
    "is_valid_hijri_date",
    "get_hijri_month_name",
    "get_hijri_weekday_name",
    # Constants
    "HIJRI_MONTHS",
    "HIJRI_WEEKDAYS",
    "ISLAMIC_EPOCH",
]

# Package metadata
__author__ = "m.lotfi"
__email__ = "m.lotfi@email.com"
__description__ = "Pythonic Hijri datetime — handle full & partial dates, ranges, and seamless Gregorian & Jalali conversion."