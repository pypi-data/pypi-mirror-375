"""
Unit tests for the rrule-humanize library.
"""

import unittest
from rrule_humanize import humanize

class TestHumanize(unittest.TestCase):
    
    def test_daily_count(self):
        """Test humanizing a daily RRULE with count."""
        rrule_str = "FREQ=DAILY;COUNT=5"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every day, 5 times")
    
    def test_weekly_interval_byday(self):
        """Test humanizing a weekly RRULE with interval and weekdays."""
        rrule_str = "FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every 2 weeks, on Monday, Wednesday and Friday")
    
    def test_monthly_bymonthday(self):
        """Test humanizing a monthly RRULE with month days."""
        rrule_str = "FREQ=MONTHLY;BYMONTHDAY=1"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every month, on the 1st")
    
    def test_yearly_bymonth_bymonthday(self):
        """Test humanizing a yearly RRULE with months and month days."""
        rrule_str = "FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every year, in January, on the 1st")
    
    def test_monthly_multiple_months(self):
        """Test humanizing a monthly RRULE with multiple months."""
        rrule_str = "FREQ=MONTHLY;BYMONTH=1,2,3"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every month, in January, February and March only")
    
    def test_weekly_byday_count(self):
        """Test humanizing a weekly RRULE with weekday and count."""
        rrule_str = "FREQ=WEEKLY;BYDAY=MO;COUNT=10"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every week, on Monday, 10 times")
    
    def test_yearly_byweekno(self):
        """Test humanizing a yearly RRULE with week numbers."""
        rrule_str = "FREQ=YEARLY;BYWEEKNO=1;COUNT=5"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every year, in week 1, 5 times")
    
    def test_daily_byyearday(self):
        """Test humanizing a daily RRULE with year days."""
        rrule_str = "FREQ=DAILY;BYYEARDAY=1,100,200;COUNT=3"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every day, on the 1st, 100th and 200th days of the year, 3 times")
    
    def test_daily_byhour(self):
        """Test humanizing a daily RRULE with hours."""
        rrule_str = "FREQ=DAILY;BYHOUR=9,17;COUNT=5"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every day, at 09:00 and 17:00, 5 times")
    
    def test_monthly_bysetpos(self):
        """Test humanizing a monthly RRULE with set positions."""
        rrule_str = "FREQ=MONTHLY;BYSETPOS=1,-1;COUNT=5"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every month, on the first and last occurrences, 5 times")
    
    def test_hourly_byminute(self):
        """Test humanizing an hourly RRULE with minutes."""
        rrule_str = "FREQ=HOURLY;BYMINUTE=0,30;COUNT=5"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every hour, at minutes 0 and 30, 5 times")
    
    def test_minutely_bysecond(self):
        """Test humanizing a minutely RRULE with seconds."""
        rrule_str = "FREQ=MINUTELY;BYSECOND=0,30;COUNT=5"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every minute, at seconds 0 and 30, 5 times")
    
    def test_weekly_wkst(self):
        """Test humanizing a weekly RRULE with week start."""
        rrule_str = "FREQ=WEEKLY;WKST=SU;BYDAY=MO;COUNT=5"
        result = humanize(rrule_str)
        self.assertEqual(result, "Every week, on Monday, weeks start on Sunday, 5 times")
        
    def test_with_dtstart(self):
        """Test humanizing an RRULE with DTSTART."""
        rrule_str = "FREQ=WEEKLY;COUNT=5"
        dtstart = "20250902T190400Z"
        result = humanize(rrule_str, dtstart)
        self.assertEqual(result, "Every week starting September 2, 2025 at 19:04 UTC, on Tuesday, 5 times")
        
    def test_with_dtstart_date_only(self):
        """Test humanizing an RRULE with date-only DTSTART."""
        rrule_str = "FREQ=WEEKLY;COUNT=5"
        dtstart = "20250902"
        result = humanize(rrule_str, dtstart)
        self.assertEqual(result, "Every week starting September 2, 2025, on Tuesday, 5 times")

if __name__ == "__main__":
    unittest.main()