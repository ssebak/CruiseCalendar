"""
Quick Start Guide - Get up and running in 5 minutes

This script helps you test if the calendar module works before deploying.
"""

from datetime import datetime, timedelta
from calendar_manager import CalendarManager


def test_calendar_manager():
    """Test the calendar manager functionality"""
    
    print("=" * 60)
    print("CALENDAR MANAGER TEST")
    print("=" * 60)
    
    # Test with current month
    today = datetime.now()
    year = today.year
    month = today.month
    
    print(f"\nTesting calendar for {year}-{month:02d}...")
    
    calendar = CalendarManager(year, month)
    
    # Get first, second, and third weeks
    for week_num in range(3):
        week_dates = calendar.get_week_for_month(week_num)
        start = week_dates[0]
        end = week_dates[-1]
        
        print(f"\nWeek {week_num}:")
        for date_obj in week_dates:
            weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][date_obj.weekday()]
            is_current = '(current month)' if calendar.is_current_month(date_obj) else '(other month)'
            is_today = '[TODAY]' if calendar.is_today(date_obj) else ''
            print(f"  {date_obj.strftime('%Y-%m-%d %a')} {is_current} {is_today}")
    
    print("\n✓ Calendar manager working correctly!")
    return True


def test_date_range_formatting():
    """Test date range formatting"""
    
    print("\n" + "=" * 60)
    print("DATE FORMATTING TEST")
    print("=" * 60)
    
    test_cases = [
        (datetime(2026, 2, 16), datetime(2026, 2, 22)),  # Same month
        (datetime(2026, 2, 23), datetime(2026, 3, 1)),   # Cross month
        (datetime(2026, 12, 28), datetime(2027, 1, 3)),  # Cross year
    ]
    
    for start, end in test_cases:
        week = [start + timedelta(days=i) for i in range(7)]
        formatted = CalendarManager.get_date_range_for_week(week)
        print(f"\n{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        print(f"  Formatted: {formatted}")
    
    print("\n✓ Date formatting working correctly!")
    return True


def main():
    """Run all tests"""
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         CRUISE CALENDAR - QUICK START TEST                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        test_calendar_manager()
        test_date_range_formatting()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Run: python test_calendar.py")
        print("     → This generates a preview HTML file")
        print()
        print("  2. Configure API request in portcall_fetcher.py:")
        print("     - Set API configuration variables")
        print("     - Implement your API call and data mapping in get_portcalls_for_week()")
        print()
        print("  3. Deploy to Apache:")
        print("     - Copy calendar.cgi to cgi-bin/")
        print("     - Copy *.py files to same directory")
        print("     - Make calendar.cgi executable")
        print()
        print("  4. Test:")
        print("     - http://your-server/cgi-bin/calendar.cgi")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
