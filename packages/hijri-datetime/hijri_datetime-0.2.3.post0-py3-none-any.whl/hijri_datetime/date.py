"""Core Hijri date and time classes."""

from datetime import date, datetime, time
from typing import Optional, Union, Tuple
import calendar

from exceptions import InvalidHijriDate
from constants import HIJRI_MONTHS, HIJRI_WEEKDAYS


class HijriDate:
    """Represents a Hijri calendar date."""
    
    def __init__(self, year: int, month: int, day: int):
        """Initialize a Hijri date.
        
        Args:
            year: Hijri year
            month: Hijri month (1-12)
            day: Hijri day (1-30)
            
        Raises:
            InvalidHijriDate: If the date is invalid
        """
        if not self._is_valid_date(year, month, day):
            raise InvalidHijriDate(f"Invalid Hijri date: {year}-{month}-{day}")
            
        self.year = year
        self.month = month
        self.day = day
    
    def _is_valid_date(self, year: int, month: int, day: int) -> bool:
        """Check if the given Hijri date is valid."""
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 30):
            return False
        # Add more sophisticated validation here
        return True
    
    def __repr__(self) -> str:
        return f"HijriDate({self.year}, {self.month}, {self.day})"
    
    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
    
    @property
    def month_name(self) -> str:
        """Get the name of the Hijri month."""
        return HIJRI_MONTHS[self.month - 1]
    
    def to_gregorian(self) -> date:
        """Convert to Gregorian date."""
        from .converter import hijri_to_gregorian
        return hijri_to_gregorian(self)
    
    def to_jalali(self):
        """Convert to Jalali date."""
        from .converter import hijri_to_jalali
        return hijri_to_jalali(self)


class HijriDateTime:
    """Represents a Hijri calendar datetime."""
    
    def __init__(self, year: int, month: int, day: int, 
                 hour: int = 0, minute: int = 0, second: int = 0):
        """Initialize a Hijri datetime."""
        self.date = HijriDate(year, month, day)
        self.time = HijriTime(hour, minute, second)
    
    @property
    def year(self) -> int:
        return self.date.year
    
    @property
    def month(self) -> int:
        return self.date.month
    
    @property
    def day(self) -> int:
        return self.date.day
    
    def __repr__(self) -> str:
        return f"HijriDateTime({self.year}, {self.month}, {self.day}, {self.time.hour}, {self.time.minute}, {self.time.second})"


class HijriTime:
    """Represents a time in the Hijri calendar context."""
    
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0):
        """Initialize a Hijri time."""
        if not (0 <= hour <= 23):
            raise ValueError("Hour must be between 0 and 23")
        if not (0 <= minute <= 59):
            raise ValueError("Minute must be between 0 and 59")
        if not (0 <= second <= 59):
            raise ValueError("Second must be between 0 and 59")
            
        self.hour = hour
        self.minute = minute
        self.second = second


class HijriDateRange:
    """Represents a range of Hijri dates."""
    
    def __init__(self, start: HijriDate, end: HijriDate):
        """Initialize a Hijri date range."""
        if start > end:
            raise ValueError("Start date must be before or equal to end date")
        self.start = start
        self.end = end
    
    def __contains__(self, date: HijriDate) -> bool:
        """Check if a date is within the range."""
        return self.start <= date <= self.end
    
    def __iter__(self):
        """Iterate over dates in the range."""
        current = self.start
        while current <= self.end:
            yield current
            # Add one day (simplified)
            current = self._add_one_day(current)
    
    def _add_one_day(self, date: HijriDate) -> HijriDate:
        """Add one day to a Hijri date (simplified implementation)."""
        # This is a simplified version - you'd need proper calendar logic
        if date.day < 30:  # Assuming max 30 days per month for simplicity
            return HijriDate(date.year, date.month, date.day + 1)
        elif date.month < 12:
            return HijriDate(date.year, date.month + 1, 1)
        else:
            return HijriDate(date.year + 1, 1, 1)