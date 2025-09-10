# rrule-humanize

A Python library to convert RRULE strings to human-readable text, following the iCalendar RFC 5545 specification.

## Installation

```bash
pip install rrule-humanize
```

## Usage

```python
from rrule_humanize import humanize

# Convert RRULE to human-readable text
rrule_str = "FREQ=DAILY;COUNT=5"
text = humanize(rrule_str)
print(text)  # "Every day, 5 times"

# More complex example
rrule_str = "FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR"
text = humanize(rrule_str)
print(text)  # "Every 2 weeks on Monday, Wednesday and Friday"

# Example with DTSTART
rrule_str = "FREQ=WEEKLY;COUNT=5"
dtstart = "20250902T190400Z"
text = humanize(rrule_str, dtstart)
print(text)  # "Every week starting September 2, 2025 at 19:04 UTC, on Tuesday, 5 times"

# Example with week start
rrule_str = "FREQ=WEEKLY;WKST=SU;BYDAY=MO;COUNT=5"
text = humanize(rrule_str)
print(text)  # "Every week, on Monday, weeks start on Sunday, 5 times"
```

## Supported RRULE Components

The library supports all RRULE components defined in RFC 5545:

- `FREQ` - Frequency (SECONDLY, MINUTELY, HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY)
- `UNTIL` - End date for the recurrence
- `COUNT` - Number of occurrences
- `INTERVAL` - Interval between occurrences
- `BYSECOND` - Specific seconds within a minute
- `BYMINUTE` - Specific minutes within an hour
- `BYHOUR` - Specific hours within a day
- `BYDAY` - Specific days of the week
- `BYMONTHDAY` - Specific days of the month
- `BYYEARDAY` - Specific days of the year
- `BYWEEKNO` - Specific weeks of the year
- `BYMONTH` - Specific months of the year
- `BYSETPOS` - Specific occurrences within the recurrence set
- `WKST` - Week start day

## Examples

Here are some examples of RRULE strings and their human-readable equivalents:

```python
from rrule_humanize import humanize

# Daily recurrence
print(humanize("FREQ=DAILY;COUNT=5"))
# Output: "Every day, 5 times"

# Weekly recurrence with interval
print(humanize("FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR"))
# Output: "Every 2 weeks, on Monday, Wednesday and Friday"

# Monthly recurrence on specific day
print(humanize("FREQ=MONTHLY;BYMONTHDAY=1"))
# Output: "Every month, on the 1st"

# Yearly recurrence
print(humanize("FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1"))
# Output: "Every year, in January, on the 1st"

# Multiple months
print(humanize("FREQ=MONTHLY;BYMONTH=1,2,3"))
# Output: "Yearly, in January, February and March only"

# Week numbers
print(humanize("FREQ=YEARLY;BYWEEKNO=1;COUNT=5"))
# Output: "Every year, in week 1, 5 times"

# Year days
print(humanize("FREQ=DAILY;BYYEARDAY=1,100,200;COUNT=3"))
# Output: "Every day, on the 1st, 100th and 200th days of the year, 3 times"

# Hours
print(humanize("FREQ=DAILY;BYHOUR=9,17;COUNT=5"))
# Output: "Every day, at 09:00 and 17:00, 5 times"

# Set positions
print(humanize("FREQ=MONTHLY;BYSETPOS=1,-1;COUNT=5"))
# Output: "Every month, on the first and last occurrences, 5 times"

# Minutes
print(humanize("FREQ=HOURLY;BYMINUTE=0,30;COUNT=5"))
# Output: "Every hour, at minutes 0 and 30, 5 times"

# Seconds
print(humanize("FREQ=MINUTELY;BYSECOND=0,30;COUNT=5"))
# Output: "Every minute, at seconds 0 and 30, 5 times"

# Week start
print(humanize("FREQ=WEEKLY;WKST=SU;BYDAY=MO;COUNT=5"))
# Output: "Every week, on Monday, weeks start on Sunday, 5 times"

# With DTSTART
print(humanize("FREQ=WEEKLY;COUNT=5", "20250902T190400Z"))
# Output: "Every week starting September 2, 2025 at 19:04 UTC, on Tuesday, 5 times"

# Date-only DTSTART
print(humanize("FREQ=MONTHLY;BYMONTHDAY=1;COUNT=12", "20250902"))
# Output: "Every month starting September 2, 2025, on the 1st, 12 times"
```

## Features

- Converts RRULE strings to human-readable text
- Supports all RFC 5545 RRULE components
- Supports DTSTART for complete recurrence information
- Lightweight and easy to use
- Built on top of python-dateutil for reliable parsing
- Comprehensive test coverage

## License

MIT