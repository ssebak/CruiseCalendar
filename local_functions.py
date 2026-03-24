"""Helper routines shared between the CGI front end and local tests.

Splitting the HTML builders out of the main script keeps ``index.py``
readable and makes it easy to invoke the same rendering logic from
the command‑line or a unit test.
"""

import cgi
from datetime import datetime


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

    next_month_y, next_month_m = year, month
    if next_week_dates and next_week_dates[0].month != month:
        next_month_m += 1
        if next_month_m > 12:
            next_month_m = 1
            next_month_y += 1

    prev_month_y, prev_month_m = year, month
    if week_offset == 0 and week_dates[0].month == month:
        prev_week_dates = calendar_manager.get_week_for_month(-1)
        if prev_week_dates and prev_week_dates[0].month != month:
            prev_month_m -= 1
            if prev_month_m < 1:
                prev_month_m = 12
                prev_month_y -= 1

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


def build_calendar_grid(week_dates, portcalls_by_date):
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
                html += build_portcall_card(portcall)
        html += """
            </div>
        </div>"""
    html += '</div>'
    return html


def build_portcall_card(portcall):
    vessel_name = portcall.get('vessel_name','Unknown')
    portcall_id = portcall.get('portcall_id','N/A')
    pier = portcall.get('pier','TBD')
    arrival = portcall.get('arrival_time','')
    departure = portcall.get('departure_time','')
    passengers = portcall.get('passengers','n/a')

    html = f"""
                <div class="portcall-card">
                    <div class="vessel-name">{vessel_name}</div>
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
