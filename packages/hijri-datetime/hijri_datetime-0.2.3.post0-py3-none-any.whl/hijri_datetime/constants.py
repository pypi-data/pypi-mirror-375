"""Constants for Hijri calendar."""

from datetime import date

# Hijri month names in Arabic and English
HIJRI_MONTHS = [
    "Muharram",
    "Safar", 
    "Rabi' al-awwal",
    "Rabi' al-thani",
    "Jumada al-awwal",
    "Jumada al-thani",
    "Rajab",
    "Sha'ban",
    "Ramadan",
    "Shawwal",
    "Dhu al-Qi'dah",
    "Dhu al-Hijjah"
]

HIJRI_MONTHS_ARABIC = [
    "محرم",
    "صفر",
    "ربيع الأول", 
    "ربيع الثاني",
    "جمادى الأولى",
    "جمادى الثانية",
    "رجب",
    "شعبان",
    "رمضان",
    "شوال",
    "ذو القعدة",
    "ذو الحجة"
]

# Weekday names
HIJRI_WEEKDAYS = [
    "Saturday",  # Sabt
    "Sunday",    # Ahad
    "Monday",    # Ithnayn
    "Tuesday",   # Thulatha
    "Wednesday", # Arbi'a
    "Thursday",  # Khamis
    "Friday"     # Jumu'ah
]

HIJRI_WEEKDAYS_ARABIC = [
    "السبت",
    "الأحد", 
    "الإثنين",
    "الثلاثاء",
    "الأربعاء",
    "الخميس",
    "الجمعة"
]

# Islamic epoch (July 16, 622 CE in Gregorian calendar)
ISLAMIC_EPOCH = date(622, 7, 16)

# Days in each Hijri month (simplified - actual lengths vary)
HIJRI_MONTH_DAYS = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]

# Leap year pattern for Hijri calendar (30-year cycle)
HIJRI_LEAP_YEARS = [2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29]