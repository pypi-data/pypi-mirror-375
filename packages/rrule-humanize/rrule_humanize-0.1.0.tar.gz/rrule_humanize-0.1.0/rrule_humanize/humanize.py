"""
Main module for rrule-humanize library.
Contains the primary humanize function and supporting classes.
"""

from dateutil.rrule import rrulestr
from dateutil.rrule import (
    YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY,
    MO, TU, WE, TH, FR, SA, SU
)
from datetime import datetime
import re

# Mapping of frequency constants to human-readable strings
FREQ_MAP = {
    YEARLY: "year",
    MONTHLY: "month",
    WEEKLY: "week",
    DAILY: "day",
    HOURLY: "hour",
    MINUTELY: "minute",
    SECONDLY: "second"
}

# Mapping of weekday integers to human-readable strings
# 0=MO, 1=TU, 2=WE, 3=TH, 4=FR, 5=SA, 6=SU
WEEKDAY_MAP = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

# Mapping of month integers to human-readable strings
MONTH_MAP = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

# Mapping of weekday constants to human-readable strings
WEEKDAY_CONST_MAP = {
    MO: "Monday",
    TU: "Tuesday",
    WE: "Wednesday",
    TH: "Thursday",
    FR: "Friday",
    SA: "Saturday",
    SU: "Sunday"
}

def _format_weekdays(byweekday):
    """Format weekdays for human-readable output."""
    if not byweekday:
        return None
        
    # byweekday can be a tuple of integers or a tuple of weekday objects
    # Let's handle both cases
    if isinstance(byweekday, (list, tuple)):
        weekday_names = []
        for day in byweekday:
            if isinstance(day, int):
                weekday_names.append(WEEKDAY_MAP.get(day, "unknown"))
            else:
                # It's a weekday object, get its index
                weekday_names.append(WEEKDAY_MAP.get(day.weekday, "unknown"))
        
        if len(weekday_names) == 1:
            return f"on {weekday_names[0]}"
        else:
            return f"on {', '.join(weekday_names[:-1])} and {weekday_names[-1]}"
    else:
        # Single weekday
        if isinstance(byweekday, int):
            return f"on {WEEKDAY_MAP.get(byweekday, 'unknown')}"
        else:
            # It's a weekday object
            return f"on {WEEKDAY_MAP.get(byweekday.weekday, 'unknown')}"

def _format_months(bymonth):
    """Format months for human-readable output."""
    if not bymonth:
        return None
        
    if isinstance(bymonth, (list, tuple)):
        month_names = [MONTH_MAP.get(month, "unknown") for month in bymonth]
        if len(month_names) == 1:
            return f"in {month_names[0]}"
        else:
            return f"in {', '.join(month_names[:-1])} and {month_names[-1]}"
    else:
        return f"in {MONTH_MAP.get(bymonth, 'unknown')}"

def _format_monthdays(bymonthday):
    """Format month days for human-readable output."""
    if not bymonthday:
        return None
        
    if isinstance(bymonthday, (list, tuple)):
        if len(bymonthday) == 1:
            day = bymonthday[0]
            suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            return f"on the {day}{suffix}"
        else:
            days_with_suffix = []
            for day in bymonthday:
                suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                days_with_suffix.append(f"{day}{suffix}")
            return f"on the {', '.join(days_with_suffix[:-1])} and {days_with_suffix[-1]}"
    else:
        suffix = "th" if 11 <= bymonthday <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(bymonthday % 10, "th")
        return f"on the {bymonthday}{suffix}"

def _format_week_numbers(byweekno):
    """Format week numbers for human-readable output."""
    if not byweekno:
        return None
        
    if isinstance(byweekno, (list, tuple)):
        if len(byweekno) == 1:
            return f"in week {byweekno[0]}"
        else:
            weeks_str = ", ".join(str(week) for week in byweekno[:-1])
            return f"in weeks {weeks_str} and {byweekno[-1]}"
    else:
        return f"in week {byweekno}"

def _format_year_days(byyearday):
    """Format year days for human-readable output."""
    if not byyearday:
        return None
        
    if isinstance(byyearday, (list, tuple)):
        if len(byyearday) == 1:
            day = byyearday[0]
            suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            return f"on the {day}{suffix} day of the year"
        else:
            days_with_suffix = []
            for day in byyearday:
                suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                days_with_suffix.append(f"{day}{suffix}")
            return f"on the {', '.join(days_with_suffix[:-1])} and {days_with_suffix[-1]} days of the year"
    else:
        suffix = "th" if 11 <= byyearday <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(byyearday % 10, "th")
        return f"on the {byyearday}{suffix} day of the year"

def _format_hours(byhour):
    """Format hours for human-readable output."""
    if not byhour:
        return None
        
    if isinstance(byhour, (list, tuple)):
        if len(byhour) == 1:
            return f"at {byhour[0]:02d}:00"
        else:
            hours_str = ", ".join(f"{hour:02d}:00" for hour in byhour[:-1])
            return f"at {hours_str} and {byhour[-1]:02d}:00"
    else:
        return f"at {byhour:02d}:00"

def _format_minutes(byminute):
    """Format minutes for human-readable output."""
    if not byminute:
        return None
        
    if isinstance(byminute, (list, tuple)):
        if len(byminute) == 1:
            return f"at minute {byminute[0]}"
        else:
            minutes_str = ", ".join(str(minute) for minute in byminute[:-1])
            return f"at minutes {minutes_str} and {byminute[-1]}"
    else:
        return f"at minute {byminute}"

def _format_seconds(bysecond):
    """Format seconds for human-readable output."""
    if not bysecond:
        return None
        
    if isinstance(bysecond, (list, tuple)):
        if len(bysecond) == 1:
            return f"at second {bysecond[0]}"
        else:
            seconds_str = ", ".join(str(second) for second in bysecond[:-1])
            return f"at seconds {seconds_str} and {bysecond[-1]}"
    else:
        return f"at second {bysecond}"

def _format_set_positions(bysetpos):
    """Format set positions for human-readable output."""
    if not bysetpos:
        return None
        
    if isinstance(bysetpos, (list, tuple)):
        if len(bysetpos) == 1:
            pos = bysetpos[0]
            if pos == 1:
                return "on the first occurrence"
            elif pos == -1:
                return "on the last occurrence"
            else:
                suffix = "th" if 11 <= abs(pos) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(abs(pos) % 10, "th")
                if pos > 0:
                    return f"on the {pos}{suffix} occurrence"
                else:
                    return f"on the {abs(pos)}{suffix} to last occurrence"
        else:
            pos_descriptions = []
            for pos in bysetpos:
                if pos == 1:
                    pos_descriptions.append("first")
                elif pos == -1:
                    pos_descriptions.append("last")
                else:
                    suffix = "th" if 11 <= abs(pos) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(abs(pos) % 10, "th")
                    if pos > 0:
                        pos_descriptions.append(f"{pos}{suffix}")
                    else:
                        pos_descriptions.append(f"{abs(pos)}{suffix} to last")
            return f"on the {', '.join(pos_descriptions[:-1])} and {pos_descriptions[-1]} occurrences"
    else:
        if bysetpos == 1:
            return "on the first occurrence"
        elif bysetpos == -1:
            return "on the last occurrence"
        else:
            suffix = "th" if 11 <= abs(bysetpos) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(abs(bysetpos) % 10, "th")
            if bysetpos > 0:
                return f"on the {bysetpos}{suffix} occurrence"
            else:
                return f"on the {abs(bysetpos)}{suffix} to last occurrence"

def _format_week_start(wkst):
    """Format week start for human-readable output."""
    if wkst is None:
        return None
    
    if isinstance(wkst, int):
        return f"weeks start on {WEEKDAY_MAP.get(wkst, 'unknown')}"
    else:
        # It's a weekday object
        return f"weeks start on {WEEKDAY_CONST_MAP.get(wkst, 'unknown')}"

def _format_dtstart(dtstart):
    """Format DTSTART for human-readable output."""
    if dtstart is None:
        return None
    
    if isinstance(dtstart, str):
        # Try to parse the DTSTART string
        # Handle formats like "20250902T190400Z" or "20250902"
        if 'T' in dtstart:
            # DateTime format
            try:
                if dtstart.endswith('Z'):
                    # UTC timezone
                    dt = datetime.strptime(dtstart, '%Y%m%dT%H%M%SZ')
                    date_str = dt.strftime('%B %d, %Y').replace(' 0', ' ')  # Remove leading zero
                    time_str = dt.strftime('%H:%M')
                    return f"starting {date_str} at {time_str} UTC"
                else:
                    # Local time (no timezone info)
                    dt = datetime.strptime(dtstart, '%Y%m%dT%H%M%S')
                    date_str = dt.strftime('%B %d, %Y').replace(' 0', ' ')  # Remove leading zero
                    time_str = dt.strftime('%H:%M')
                    return f"starting {date_str} at {time_str}"
            except ValueError:
                pass
        else:
            # Date only format
            try:
                dt = datetime.strptime(dtstart, '%Y%m%d')
                date_str = dt.strftime('%B %d, %Y').replace(' 0', ' ')  # Remove leading zero
                return f"starting {date_str}"
            except ValueError:
                pass
        return None  # Unable to parse
    
    elif isinstance(dtstart, datetime):
        # Already a datetime object
        date_str = dtstart.strftime('%B %d, %Y').replace(' 0', ' ')  # Remove leading zero
        time_str = dtstart.strftime('%H:%M')
        # Check if it's UTC
        if dtstart.tzname() == 'UTC' or (dtstart.utcoffset() is not None and dtstart.utcoffset().total_seconds() == 0):
            return f"starting {date_str} at {time_str} UTC"
        else:
            return f"starting {date_str} at {time_str}"
    
    return None

def humanize(rrule_str, dtstart=None):
    """
    Convert an RRULE string to human-readable text.
    
    Args:
        rrule_str (str): A valid RRULE string following RFC 5545
        dtstart (str or datetime, optional): Start datetime for the recurrence
        
    Returns:
        str: Human-readable description of the recurrence rule
        
    Example:
        >>> humanize("FREQ=DAILY;COUNT=5")
        "Every day, 5 times"
        
        >>> humanize("FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR", "20250902T190400Z")
        "Every 2 weeks starting September 02, 2025 at 19:04 UTC, on Monday, Wednesday and Friday"
    """
    # Parse the RRULE string
    rrule_obj = rrulestr(rrule_str)
    
    # Extract components from the RRULE
    freq = getattr(rrule_obj, '_freq', None)
    interval = getattr(rrule_obj, '_interval', 1)
    count = getattr(rrule_obj, '_count', None)
    until = getattr(rrule_obj, '_until', None)
    byweekday = getattr(rrule_obj, '_byweekday', None)
    bymonth = getattr(rrule_obj, '_bymonth', None)
    bymonthday = getattr(rrule_obj, '_bymonthday', None)
    byweekno = getattr(rrule_obj, '_byweekno', None)
    byyearday = getattr(rrule_obj, '_byyearday', None)
    byhour = getattr(rrule_obj, '_byhour', None)
    byminute = getattr(rrule_obj, '_byminute', None)
    bysecond = getattr(rrule_obj, '_bysecond', None)
    bysetpos = getattr(rrule_obj, '_bysetpos', None)
    wkst = getattr(rrule_obj, '_wkst', None)
    original_rule = getattr(rrule_obj, '_original_rule', {})
    
    # Build the human-readable string
    parts = []
    
    # Handle DTSTART if provided
    dtstart_part = _format_dtstart(dtstart)
    
    # Handle frequency and interval
    if freq is not None:
        freq_text = FREQ_MAP.get(freq, "unknown")
        if interval == 1:
            base_text = f"Every {freq_text}"
        else:
            base_text = f"Every {interval} {freq_text}s"
        
        # Add DTSTART information if available
        if dtstart_part:
            parts.append(f"{base_text} {dtstart_part}")
        else:
            parts.append(base_text)
    
    # Handle weekdays
    weekday_part = _format_weekdays(byweekday)
    if weekday_part:
        parts.append(weekday_part)
    
    # Handle months (only if explicitly specified)
    if 'bymonth' in original_rule and original_rule['bymonth'] is not None:
        month_part = _format_months(bymonth)
        if month_part:
            # For MONTHLY frequency with BYMONTH, this means "in these months only"
            # For other frequencies, just list the months normally
            if freq == MONTHLY:
                parts.append(f"in {month_part[3:]} only")  # Remove "in " prefix and add "only"
            else:
                parts.append(month_part)
    
    # Handle month days (only if explicitly specified)
    if 'bymonthday' in original_rule and original_rule['bymonthday'] is not None:
        monthday_part = _format_monthdays(bymonthday)
        if monthday_part:
            parts.append(monthday_part)
    
    # Handle week numbers (only if explicitly specified)
    if 'byweekno' in original_rule and original_rule['byweekno'] is not None:
        weekno_part = _format_week_numbers(byweekno)
        if weekno_part:
            parts.append(weekno_part)
    
    # Handle year days (only if explicitly specified)
    if 'byyearday' in original_rule and original_rule['byyearday'] is not None:
        yearday_part = _format_year_days(byyearday)
        if yearday_part:
            parts.append(yearday_part)
    
    # Handle hours (only if explicitly specified)
    if 'byhour' in original_rule and original_rule['byhour'] is not None:
        hour_part = _format_hours(byhour)
        if hour_part:
            parts.append(hour_part)
    
    # Handle minutes (only if explicitly specified)
    if 'byminute' in original_rule and original_rule['byminute'] is not None:
        minute_part = _format_minutes(byminute)
        if minute_part:
            parts.append(minute_part)
    
    # Handle seconds (only if explicitly specified)
    if 'bysecond' in original_rule and original_rule['bysecond'] is not None:
        second_part = _format_seconds(bysecond)
        if second_part:
            parts.append(second_part)
    
    # Handle set positions (only if explicitly specified)
    if 'bysetpos' in original_rule and original_rule['bysetpos'] is not None:
        setpos_part = _format_set_positions(bysetpos)
        if setpos_part:
            parts.append(setpos_part)
    
    # Handle week start (only if explicitly specified, detected by checking if it's different from default)
    # Default week start is Monday (0), so if wkst is not 0, it was explicitly specified
    if wkst is not None and wkst != 0:
        wkst_part = _format_week_start(wkst)
        if wkst_part:
            parts.append(wkst_part)
    
    # Handle count or until
    if count is not None:
        if count == 1:
            parts.append("once")
        else:
            parts.append(f"{count} times")
    elif until is not None:
        parts.append(f"until {until.strftime('%B %d, %Y')}")
    
    return ", ".join(parts)