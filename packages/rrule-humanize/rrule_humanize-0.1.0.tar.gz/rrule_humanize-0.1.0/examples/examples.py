"""
Examples of using the rrule-humanize library.
"""

from rrule_humanize import humanize

def main():
    # Examples of RRULE strings and their human-readable equivalents
    examples = [
        # Basic frequencies
        "FREQ=SECONDLY;COUNT=5",
        "FREQ=MINUTELY;COUNT=5",
        "FREQ=HOURLY;COUNT=5",
        "FREQ=DAILY;COUNT=5",
        "FREQ=WEEKLY;COUNT=5",
        "FREQ=MONTHLY;COUNT=5",
        "FREQ=YEARLY;COUNT=5",
        
        # With intervals
        "FREQ=DAILY;INTERVAL=3;COUNT=5",
        "FREQ=WEEKLY;INTERVAL=2;COUNT=5",
        "FREQ=MONTHLY;INTERVAL=3;COUNT=5",
        "FREQ=YEARLY;INTERVAL=2;COUNT=5",
        
        # With UNTIL
        "FREQ=DAILY;UNTIL=20251231T235959Z",
        
        # With BY components
        "FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=5",
        "FREQ=MONTHLY;BYMONTHDAY=1;COUNT=5",
        "FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1;COUNT=5",
        "FREQ=YEARLY;BYYEARDAY=1,100,200;COUNT=3",
        "FREQ=YEARLY;BYWEEKNO=1;COUNT=5",
        "FREQ=DAILY;BYHOUR=9,17;COUNT=5",
        "FREQ=HOURLY;BYMINUTE=0,30;COUNT=5",
        "FREQ=MINUTELY;BYSECOND=0,30;COUNT=5",
        
        # Complex examples
        "FREQ=MONTHLY;BYMONTH=1,2,3;COUNT=5",
        "FREQ=MONTHLY;BYSETPOS=1,-1;COUNT=5",
        "FREQ=WEEKLY;WKST=SU;BYDAY=MO;COUNT=5",
    ]
    
    print("RRULE Humanize Examples")
    print("=" * 50)
    
    for rrule_str in examples:
        try:
            result = humanize(rrule_str)
            print(f"RRULE: {rrule_str}")
            print(f"Human-readable: {result}")
            print()
        except Exception as e:
            print(f"Error processing {rrule_str}: {e}")
            print()

if __name__ == "__main__":
    main()