# hijri-datetime

📅 **Hijri (Islamic) calendar datetime library for Python**  
A drop-in replacement for Python's built-in `datetime` module, supporting Hijri date arithmetic, formatting, conversion, partial dates, and integration with `jdatetime`.

---

## Features

- **HijriDate / HijriDateTime classes**  
  Drop-in replacement for `datetime.date` and `datetime.datetime`.

- **Partial Dates & Ranges**  
  Handle missing months or days gracefully:
  - `HijriDate(1446)` → represents the full year.
  - `HijriDate(1446, 2)` → represents all days of month 2.
  - Arithmetic supports ranges and comparisons.

- **Gregorian ↔ Hijri Conversion**  
  - Vectorized conversion using preloaded dataset (from [Aladhan API](https://aladhan.com/islamic-calendar-api)).
  - Accurate conversion for historical and future dates.
  
- **Integration with jdatetime**  
  Convert Hijri dates to Jalali calendar easily:
  ```python
  import jdatetime
  jd = hijri_date.to_jdatetime()
  ````

* **Full datetime API support**
  Methods like `.year`, `.month`, `.day`, `.weekday()`, `.isoweekday()`, `.strftime()`, `.fromisoformat()`, `.today()`, `.now()`.

* **Calendar module compatibility**
  Leap year checks, month lengths, weekdays, etc.

* **Vectorized / Bulk Conversion Support**
  Efficient for millions of rows with pandas/numpy.

---

## Installation

```bash
pip install hijri-datetime
```

---

## Quick Start

```python
from hijri_datetime import HijriDate, HijriDateTime

# Create Hijri dates
d1 = HijriDate(1446, 2, 15)  # Full date
d2 = HijriDate(1446, 2)      # Day missing → treat as range
d3 = HijriDate(1446)         # Month & day missing → full year range

# Convert to Gregorian
print(d1.to_gregorian())             # datetime.date(2025, 9, 9)
print(d2.to_gregorian_range())       # [datetime.date(2025,9,1), datetime.date(2025,9,30)]
print(d3.to_gregorian_range())       # full year range

# Date arithmetic
print(d1 + 10)   # Add 10 days
print(d1 - 5)    # Subtract 5 days

# jdatetime conversion
import jdatetime
jd = d1.to_jdatetime()
print(jd)        # jdatetime.date(...)
```

---

## Partial Dates & Ranges

* **Year only**

  ```python
  d = HijriDate(1446)
  start, end = d.to_gregorian_range()
  print(start, end)  # 2024-07-18 2025-07-06 (example)
  ```

* **Month only**

  ```python
  d = HijriDate(1446, 2)
  start, end = d.to_gregorian_range()
  print(start, end)  # 2025-09-01 2025-09-30 (example)
  ```

---

## Gregorian ↔ Hijri Conversion

```python
from hijri_datetime import HijriConverter

converter = HijriConverter()

# Hijri → Gregorian
greg = converter.hijri_to_gregorian(1446, 2, 15)
print(greg)  # datetime.date(2025, 9, 9)

# Gregorian → Hijri
hijri = converter.gregorian_to_hijri(greg)
print(hijri)  # HijriDate(1446, 2, 15)
```

---

## jdatetime Integration

```python
from hijri_datetime import HijriDate

d = HijriDate(1446, 2, 15)
jd = d.to_jdatetime()
print(jd)  # jdatetime.date(2025, 6, 16) example
```

---

## Pandas / Vectorized Example

```python
import pandas as pd
from hijri_datetime import HijriDate

dates = pd.Series([HijriDate(1446, 1, 1), HijriDate(1446, 2, 10)])
greg_dates = dates.apply(lambda x: x.to_gregorian())
print(greg_dates)
```

---

## Roadmap

* [ ] Full `calendar` module API compatibility
* [ ] Timezone-aware Hijri datetime
* [ ] Support for Umm al-Qura, tabular, and other Hijri variants
* [ ] Improved bulk conversion performance
* [ ] PyPI release with automated dataset update from Aladhan API

---

## Contributing

Pull requests are welcome! Please open an issue first to discuss major changes.
Could you make sure tests pass before submitting PRs?

---

## License

GNU License © 2025
