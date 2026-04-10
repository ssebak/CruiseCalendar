"""
Local Testing Script - Test the calendar without Apache
Useful for debugging and development before deploying to Apache.

Usage:
    python test_calendar.py
    
This will generate a static HTML file that you can open in your browser.
"""

import sys
from datetime import datetime, timedelta
from calendar_manager import CalendarManager
from portcall_fetcher import get_portcalls_for_week

# get the API token functions
sys.path.append('../../includes')
import krakentools_secrets
import krakentools_utils
from krakentools_endpoints import API_BASE_URL, API_PORTCALLS_CRUISES

#get token
valid_token = krakentools_utils.get_valid_bearer_token(krakentools_secrets.CLIENT_ID, krakentools_secrets.CLIENT_SECRET, krakentools_secrets.AUDIENCE, krakentools_secrets.TOKEN_URL, krakentools_secrets.GRANT_TYPE)

# reuse the same HTML helpers that the CGI/index script will use
to_import = ('build_page_header', 'build_navigation_controls', 'build_calendar_grid', 'build_page_footer')
from local_functions import build_page_header, build_navigation_controls, build_calendar_grid, build_page_footer


def generate_test_html(year, month, week_offset):
    """Generate test HTML with REAL portcall data from database"""
    
    calendar_manager = CalendarManager(year, month)
    week_dates = calendar_manager.get_week_for_month(week_offset)
    
    # Fetch REAL portcall data from your database
    portcalls_by_date = get_portcalls_for_week(
        week_dates[0],
        week_dates[-1],
        year,
        month,
        source='api',
        api_base_url=API_BASE_URL,
        api_resource=API_PORTCALLS_CRUISES,
        api_token=valid_token
    )
    
    # Generate HTML (similar to calendar.cgi but simplified)
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cruise Calendar - Test View</title>
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
        
        .test-info {{
            background-color: #e8f4f8;
            border: 2px solid #667eea;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 20px;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
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
        
        .vessel-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
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
            margin-bottom: 3px;
        }}
        
        .arrival {{
            color: #28a745;
        }}
        
        .departure {{
            color: #dc3545;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
        
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚓ Cruise Calendar - TEST VIEW</h1>
            <p>Port Calls Schedule (Mock Data)</p>
        </div>
        
        <div class="test-info">
            <strong>✅ Testing Mode:</strong> This is a local test using REAL data from your database.
            <br><br>
            <strong>Data Retrieved:</strong> {len(portcalls_by_date)} days with {sum(len(p) for p in portcalls_by_date.values())} port calls for June 1-7, 2026.
        </div>
        
        <div class="week-display">
            {week_dates[0].strftime('%b %d')} - {week_dates[-1].strftime('%b %d, %Y')}
        </div>
        
        <div class="calendar">
"""
    
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for date_obj in week_dates:
        weekday_name = weekday_names[date_obj.weekday()]
        date_str = date_obj.strftime('%d')
        month_name = date_obj.strftime('%b')
        
        is_other_month = 'other-month' if date_obj.month != week_dates[2].month else ''
        
        html += f"""        <div class="day-column {is_other_month}">
            <div class="day-header">
                <div class="day-date">{date_str}</div>
                <div class="day-weekday">{weekday_name}</div>
                <div class="day-weekday">{month_name}</div>
            </div>
            <div class="day-content">
"""
        
        date_key = date_obj.strftime('%Y-%m-%d')
        if date_key in portcalls_by_date:
            for portcall in portcalls_by_date[date_key]:
                html += f"""                <div class="portcall-card">
                    <div class="vessel-name">{portcall['vessel_name']}</div>
                    <div class="portcall-id">ID: {portcall['portcall_id']}</div>
                    <div class="pier-info">Pier: {portcall['pier']}</div>
                    <div class="time-info arrival">↓ Arrival: {portcall['arrival_time']}</div>
                    <div class="time-info departure">↑ Departure: {portcall['departure_time']}</div>
                </div>
"""
        
        html += """            </div>
        </div>
"""
    
    html += """        </div>
        
        <div class="footer">
            <p>✅ Calendar displaying REAL portcall data from database.</p>
            <p>Ready for Apache deployment. See DEPLOYMENT_CHECKLIST.md for next steps.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Generate and save test HTML file"""
    
    # Test with June 2026 (matches hardcoded dates in portcall_fetcher.py)
    year = 2026
    month = 6
    week_offset = 0
    
    print(f"Generating test calendar for {year}-{month:02d} with REAL database data...")
    print()
    
    try:
        html = generate_test_html(year, month, week_offset)
        
        output_file = 'calendar_test.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Test calendar generated: {output_file}")
        print(f"  ➜ Open this file in your browser to preview the calendar")
        print()
        print("Next Steps:")
        print("  1. ✅ Review the calendar layout in your browser")
        print("  2. ⏳ When ready, parameterize the dates in portcall_fetcher.py")
        print("  3. ⏳ Deploy calendar.cgi to Apache cgi-bin directory")
        print("  4. ⏳ Access via: http://your-server/cgi-bin/calendar.cgi")
        print()
        
    except Exception as e:
        print(f"✗ Error generating calendar: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    main()
