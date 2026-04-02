"""Helper routines shared between the CGI front end and local tests.

Splitting the HTML builders out of the main script keeps ``index.py``
readable and makes it easy to invoke the same rendering logic from
the command‑line or a unit test.
"""

import cgi
from datetime import datetime

from calendar_manager import CalendarManager


def get_query_params():
    """Extract year/month/week_offset from the query string.

    Returns a tuple ``(year, month, week_offset)``.  If the user has not
    supplied a value the current date is used, and ``week_offset``
    defaults to ``0`` (the first week shown for the month).
    """

    form = cgi.FieldStorage()
    today = datetime.now()
    year = int(form.getvalue('year', today.year))
    month = int(form.getvalue('month', today.month))
    week_offset = int(form.getvalue('week_offset', 0))
    return year, month, week_offset


def should_mask_vessel_name(date_obj, threshold_months=12, now=None):
    """Return True when a portcall date is more than the configured threshold ahead."""
    if now is None:
        now = datetime.now()

    if date_obj < now:
        return False

    year_diff = date_obj.year - now.year
    month_diff = date_obj.month - now.month
    month_distance = year_diff * 12 + month_diff

    if month_distance > threshold_months:
        return True
    if month_distance < threshold_months:
        return False

    return date_obj.day > now.day


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------

def build_page_header(year, month):
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    month_options = ''.join(
        f'<option value="{m}" {"selected" if m == month else ""}>{month_names[m-1]}</option>'
        for m in range(1, 13)
    )

    current_year = datetime.now().year
    year_options = ''.join(
        f'<option value="{y}" {"selected" if y == year else ""}>{y}</option>'
        for y in range(current_year - 2, current_year + 5)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cruise Calendar - Port Calls</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Cruise Port Calls Schedule</h1>
        </div>
        <div class="controls">
            <form method="GET">
                <label for="year">Year:</label>
                <select name="year" id="year" onchange="this.form.submit()">
                    {year_options}
                </select>

                <label for="month">Month:</label>
                <select name="month" id="month" onchange="this.form.submit()">
                    {month_options}
                </select>

                <input type="hidden" name="week_offset" value="0">
            </form>
        </div>"""
    return html


def build_navigation_controls(year, month, week_offset, calendar_manager):
    prev_offset = week_offset - 1
    next_offset = week_offset + 1

    week_dates = calendar_manager.get_week_for_month(week_offset)
    next_week_dates = calendar_manager.get_week_for_month(next_offset)
    prev_week_dates = calendar_manager.get_week_for_month(prev_offset)

    def get_month_offset(target_year, target_month, target_week_start):
        temp_calendar = CalendarManager(target_year, target_month)
        for candidate_offset in range(-6, 7):
            candidate_week = temp_calendar.get_week_for_month(candidate_offset)
            if candidate_week[0] == target_week_start:
                return candidate_offset
        return 0

    next_month_y, next_month_m = year, month
    if next_week_dates:
        next_month_y = next_week_dates[0].year
        next_month_m = next_week_dates[0].month
        if (next_month_y, next_month_m) != (year, month):
            next_offset = get_month_offset(next_month_y, next_month_m, next_week_dates[0])

    prev_month_y, prev_month_m = year, month
    if prev_week_dates:
        prev_month_y = prev_week_dates[0].year
        prev_month_m = prev_week_dates[0].month
        if (prev_month_y, prev_month_m) != (year, month):
            prev_offset = get_month_offset(prev_month_y, prev_month_m, prev_week_dates[0])

    week_start = week_dates[0]
    week_end = week_dates[-1]
    week_range = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"

    html = f"""
        <div class="week-navigation">
            <form method="GET" class="nav-form">
                <input type="hidden" name="year" value="{prev_month_y}">
                <input type="hidden" name="month" value="{prev_month_m}">
                <input type="hidden" name="week_offset" value="{prev_offset}">
                <button type="submit" class="week-nav-btn">← Previous Week</button>
            </form>

            <div class="week-range">{week_range}</div>

            <form method="GET" class="nav-form">
                <input type="hidden" name="year" value="{next_month_y}">
                <input type="hidden" name="month" value="{next_month_m}">
                <input type="hidden" name="week_offset" value="{next_offset}">
                <button type="submit" class="week-nav-btn">Next Week →</button>
            </form>
        </div>
"""
    return html


def build_calendar_grid(
    week_dates,
    portcalls_by_date,
    future_vessel_name_threshold_months=12,
    future_vessel_name_mask='TBA',
):
    weekday_names = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    html = '<div class="calendar">'
    for date_obj in week_dates:
        weekday_name = weekday_names[date_obj.weekday()]
        date_str = date_obj.strftime('%d')
        month_name = date_obj.strftime('%b')
        is_other_month = 'other-month' if date_obj.month != week_dates[2].month else ''

        # compute daily summaries
        date_key = date_obj.strftime('%Y-%m-%d')
        day_calls = portcalls_by_date.get(date_key, [])
        num_calls = len(day_calls)
        total_pax = sum((p.get('passengers') or 0) for p in day_calls)
        stats = f"{num_calls} calls"
        if total_pax:
            stats += f", {total_pax} pax"

        html += f"""
        <div class="day-column {is_other_month}">
            <div class="day-header">
                <div class="day-date">{date_str}</div>
                <div class="day-weekday">{weekday_name}</div>
                <div class="day-weekday">{month_name}</div>
                <div class="day-stats">{stats}</div>\n
            </div>
            <div class="day-content">"""
        if date_key in portcalls_by_date:
            for portcall in day_calls:
                html += build_portcall_card(
                    portcall,
                    portcall_date=date_obj,
                    future_vessel_name_threshold_months=future_vessel_name_threshold_months,
                    future_vessel_name_mask=future_vessel_name_mask,
                )
        html += """
            </div>
        </div>"""
    html += '</div>'
    return html


def build_portcall_card(
    portcall,
    portcall_date=None,
    future_vessel_name_threshold_months=12,
    future_vessel_name_mask='TBA',
):
    vessel_name = portcall.get('vessel_name', 'Unknown')
    portcall_id = portcall.get('portcall_id', 'n/a')
    pier = portcall.get('pier', 'TBD')
    arrival = portcall.get('arrival_time', '')
    departure = portcall.get('departure_time', '')
    passengers = portcall.get('passengers', 'n/a')

    masked = (
        portcall_date is not None and
        should_mask_vessel_name(portcall_date, future_vessel_name_threshold_months)
    )
    vessel_name_class = 'vessel-name'
    if masked:
        if future_vessel_name_mask == 'TBA':
            vessel_name = 'TBA'
        else:
            vessel_name_class = f'vessel-name masked {future_vessel_name_mask}'

    html = f"""
                <div class="portcall-card">
                    <div class="{vessel_name_class}">{vessel_name}</div>
                    <div class="portcall-id">ID: {portcall_id}</div>
                    <div class="pier-info">Pier: {pier}</div>
"""
    # add passenger count if available
    if passengers is not None:
        html += f'                    <div class="pier-info">Pax: {passengers}</div>\n'
    if arrival:
        html += f'<div class="time-info arrival">↓ Arrival: {arrival}</div>\n'
    if departure:
        html += f'<div class="time-info departure">↑ Departure: {departure}</div>\n'
    html += """                </div>
"""
    return html


def build_page_footer():
    return """
    </div>
</body>
</html>
"""
