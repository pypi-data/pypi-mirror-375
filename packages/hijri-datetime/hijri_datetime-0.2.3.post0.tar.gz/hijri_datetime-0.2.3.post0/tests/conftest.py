"""Pytest configuration and fixtures."""

import pytest
from datetime import date
from hijri_datetime import HijriDate, HijriDateTime


@pytest.fixture
def sample_hijri_date():
    """Sample Hijri date for testing."""
    return HijriDate(1445, 5, 15)


@pytest.fixture
def sample_hijri_datetime():
    """Sample Hijri datetime for testing."""
    return HijriDateTime(1445, 5, 15, 14, 30, 0)


@pytest.fixture
def sample_gregorian_date():
    """Sample Gregorian date for testing."""
    return date(2023, 11, 28)