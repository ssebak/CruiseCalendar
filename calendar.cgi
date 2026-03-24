#!/usr/bin/env python3
"""
Compatibility launcher that simply calls ``index.main()``.
The heavy lifting has been moved into ``index.py`` and helpers in
``local_functions.py`` – this file is kept so existing deployments that
reference ``calendar.cgi`` continue to work.
"""

# the real implementation lives in index.py
from index import main

def get_query_params():
    """Extract year, month, and week parameters from query string"""
    form = cgi.FieldStorage()
    
    today = datetime.now()
    year = int(form.getvalue('year', today.year))
    month = int(form.getvalue('month', today.month))
    
    # Calculate which week to show
    # If week_offset is provided, use it; otherwise show current week
    week_offset = int(form.getvalue('week_offset', 0))
    
    return year, month, week_offset

def generate_calendar_html():
    """Generate the complete HTML calendar page"""
    
    year, month, week_offset = get_query_params()
    calendar_manager = CalendarManager(year, month)
    
    # Get the week to display
    week_dates = calendar_manager.get_week_for_month(week_offset)
    
    # Fetch portcalls for this week from database
    # You'll need to implement get_portcalls_for_week to query your SQL database
    portcalls_by_date = get_portcalls_for_week(
        week_dates[0], 
        week_dates[-1], 
        year, 
        month
    )
    
    # Generate HTML
    html = """Content-type: text/html; charset=utf-8\n\n"""
    html += build_page_header(year, month)
    html += build_navigation_controls(year, month, week_offset, calendar_manager)
    html += build_calendar_grid(week_dates, portcalls_by_date)
    html += build_page_footer()
    
    return html

def build_page_header(year, month):
    """Build HTML header with year/month selection"""
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    month_options = ''.join([
        f'<option value="{m}" {"selected" if m == month else ""}>{month_names[m-1]}</option>'
        for m in range(1, 13)
    ])
    
    current_year = datetime.now().year
    year_options = ''.join([
        f'<option value="{y}" {"selected" if y == year else ""}>{y}</option>'
        for y in range(current_year - 2, current_year + 5)
    ])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cruise Calendar - Port Calls</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 20px;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        
        .controls form {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .controls select {{
            padding: 10px 15px;
            border: 2px solid #667eea;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            background-color: white;
        }}
        
        .controls button {{
            padding: 10px 20px;
            background-color: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: background-color 0.3s;
        }}
        
        .controls button:hover {{
            background-color: #764ba2;
        }}
        
        .nav-buttons {{
            display: flex;
            gap: 10px;
        }}
        
        .nav-buttons button {{
            padding: 10px 15px;
            background-color: #764ba2;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.95em;
            transition: background-color 0.3s;
        }}
        
        .nav-buttons button:hover {{
            background-color: #667eea;
        }}
        
        .week-display {{
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.1em;
            color: #666;
        }}
        
        .calendar {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .day-column {{
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            min-height: 400px;
            display: flex;
            flex-direction: column;
        }}
        
        .day-column.other-month {{
            background-color: #f0f0f0;
            opacity: 0.7;
        }}
        
        .day-header {{
            text-align: center;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .day-date {{
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
        }}
        
        .day-weekday {{
            font-size: 0.95em;
            color: #666;
            margin-top: 5px;
        }}
        
        .day-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .portcall-card {{
            background: white;
            border-left: 4px solid #667eea;
            padding: 12px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            font-size: 0.9em;
        }}
        
        .portcall-card.in-out {{
            margin-bottom: 5px;
        }}
        
        .vessel-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
            word-wrap: break-word;
        }}
        
        .portcall-id {{
            font-size: 0.85em;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .pier-info {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .time-info {{
            font-size: 0.85em;
            color: #764ba2;
            margin-bottom: 3px;
        }}
        
        .arrival {{
            color: #28a745;
        }}
        
        .departure {{
            color: #dc3545;
        }}
        
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚓ Cruise Calendar</h1>
            <p>Port Calls Schedule</p>
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
        </div>
"""
    return html

def build_navigation_controls(year, month, week_offset, calendar_manager):
    """Build previous/next week navigation"""
    
    prev_offset = week_offset - 1
    next_offset = week_offset + 1
    
    # Check if next week goes into next month
    week_dates = calendar_manager.get_week_for_month(week_offset)
    week_end = week_dates[-1]
    next_week_dates = calendar_manager.get_week_for_month(next_offset)
    
    next_month_y, next_month_m = year, month
    if next_week_dates and next_week_dates[0].month != month:
        next_month_m += 1
        if next_month_m > 12:
            next_month_m = 1
            next_month_y += 1
    
    # Check if prev week goes into previous month
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
        <div class="week-display">
            {week_range}
        </div>
        
        <div class="controls">
            <div class="nav-buttons">
                <form method="GET" style="display:inline;">
                    <input type="hidden" name="year" value="{prev_month_y}">
                    <input type="hidden" name="month" value="{prev_month_m}">
                    <input type="hidden" name="week_offset" value="{prev_offset}">
                    <button type="submit">← Previous Week</button>
                </form>
                
                <form method="GET" style="display:inline;">
                    <input type="hidden" name="year" value="{next_month_y}">
                    <input type="hidden" name="month" value="{next_month_m}">
                    <input type="hidden" name="week_offset" value="{next_offset}">
                    <button type="submit">Next Week →</button>
                </form>
            </div>
        </div>
"""
    return html

def build_calendar_grid(week_dates, portcalls_by_date):
    """Build the calendar grid with portcall cards"""
    
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
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
            <div class="day-content">
"""
        
        # Add portcalls for this date
        if day_calls:
            for portcall in day_calls:
                html += build_portcall_card(portcall)
        
        html += """
            </div>
        </div>
"""
    
    html += '</div>'
    return html

def build_portcall_card(portcall):
    """Build a single portcall card"""
    
    vessel_name = portcall.get('vessel_name', 'Unknown')
    portcall_id = portcall.get('portcall_id', 'N/A')
    pier = portcall.get('pier', 'TBD')
    arrival = portcall.get('arrival_time', '')
    departure = portcall.get('departure_time', '')
    passengers = portcall.get('passengers')
    
    html = f"""
                <div class="portcall-card">
                    <div class="vessel-name">{vessel_name}</div>
                    <div class="portcall-id">ID: {portcall_id}</div>
                    <div class="pier-info">Pier: {pier}</div>
"""
    if passengers is not None:
        html += f'                    <div class="pier-info">Pax: {passengers}</div>\n'
    
    if arrival:
        html += f'                    <div class="time-info arrival">↓ Arrival: {arrival}</div>\n'
    
    if departure:
        html += f'                    <div class="time-info departure">↑ Departure: {departure}</div>\n'
    
    html += """                </div>
"""
    
    return html

def build_page_footer():
    """Build HTML footer"""
    
    html = """
    </div>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    # just forward to the new index module
    main()

