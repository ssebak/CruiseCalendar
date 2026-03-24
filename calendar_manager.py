"""
Calendar Manager - Handles date calculations and week generation
"""

from datetime import datetime, timedelta
import calendar as cal_module


class CalendarManager:
    """Manages calendar operations for displaying weeks"""
    
    def __init__(self, year, month):
        """
        Initialize calendar manager for a specific year and month
        
        Args:
            year (int): Year (e.g., 2026)
            month (int): Month (1-12)
        """
        self.year = year
        self.month = month
        self.first_day_of_month = datetime(year, month, 1)
        
    def get_week_for_month(self, week_offset=0):
        """
        Get a week of dates for the month.
        Week 0 is the first week containing days from this month.
        Weeks always start on Monday.
        
        Args:
            week_offset (int): Week offset from the first week of the month.
                              Negative offsets go to previous month.
        
        Returns:
            list: List of 7 datetime objects representing Monday through Sunday
        """
        
        # Find the first Monday that contains a day from this month or before
        first_day = self.first_day_of_month
        
        # If first day is not Monday, go back to the previous Monday
        days_since_monday = first_day.weekday()  # Monday=0, Sunday=6
        first_monday = first_day - timedelta(days=days_since_monday)
        
        # Calculate the target Monday based on week_offset
        # week_offset=0 is the first Monday (may be before month starts)
        # week_offset=1 is the next Monday, etc.
        target_monday = first_monday + timedelta(weeks=week_offset)
        
        # Generate 7 days starting from target_monday
        week_dates = [target_monday + timedelta(days=i) for i in range(7)]
        
        return week_dates
    
    def get_weeks_in_month_view(self):
        """
        Get all weeks that should be displayed for a full month view.
        This shows the complete calendar grid including previous/next month days.
        
        Returns:
            list: List of lists, each containing 7 datetime objects
        """
        
        weeks = []
        first_day = self.first_day_of_month
        
        # Find first Monday of the display
        days_since_monday = first_day.weekday()
        first_monday = first_day - timedelta(days=days_since_monday)
        
        # Generate weeks until we've covered all days of the month
        current_date = first_monday
        while True:
            week = [current_date + timedelta(days=i) for i in range(7)]
            weeks.append(week)
            current_date += timedelta(weeks=1)
            
            # Stop when the week doesn't contain any days from this month
            if week[-1].month != self.month and all(d.month != self.month for d in week):
                break
        
        return weeks
    
    def is_today(self, date_obj):
        """Check if a date is today"""
        today = datetime.now().date()
        return date_obj.date() == today
    
    def is_current_month(self, date_obj):
        """Check if a date is in the current month"""
        return date_obj.month == self.month and date_obj.year == self.year
    
    @staticmethod
    def get_date_range_for_week(week_dates):
        """
        Get a formatted string representing the week date range
        
        Args:
            week_dates (list): List of 7 datetime objects
        
        Returns:
            str: Formatted date range (e.g., "Jan 01 - Jan 07, 2026")
        """
        start = week_dates[0]
        end = week_dates[-1]
        
        if start.month == end.month:
            return f"{start.strftime('%b %d')} - {end.strftime('%d, %Y')}"
        else:
            return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
