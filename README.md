# Cruise Calendar - Port Calls Scheduler

A Python/CGI-based web calendar application displaying cruise ship port calls in a weekly view with year/month selection.

## Features

- **Weekly View**: Display 7 days (Monday-Sunday) at a time
- **Month/Year Selection**: Dropdown menus to select any month/year
- **Previous/Next Navigation**: Move between weeks with buttons
- **Portcall Cards**: Each port call shows:
  - Vessel name
  - Port call ID
  - Pier/berth information
  - Arrival and departure times
- **Smart Date Display**: Shows previous/next month dates to fill out weeks (always starts on Monday)
- **Responsive Design**: Clean, modern UI with proper styling
- **Data Sources**: Supports both API endpoints and direct database connections

## Prerequisites

- Python 3.7+
- Apache web server with CGI enabled
- For database access: pyodbc library and Microsoft SQL Server database
- For API access: Valid API credentials and endpoint URLs

## Installation

### 1. Install Python Dependencies

```bash
pip install pyodbc
```

You may also need to install ODBC Driver for SQL Server:
- **Windows**: Download from [Microsoft](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **Linux**: `sudo apt-get install odbc-postgresql` (or equivalent for your SQL version)

### 2. Configure Data Source

The application supports two data sources: **API** (default) and **Database**. Choose the appropriate configuration below.

#### Option A: API Configuration (Default)

If using an API endpoint, configure the following in `index.py`:

```python
# Update these imports and variables with your API details
from your_api_module import API_BASE_URL, API_PORTCALLS_CRUISES
# Ensure your API token retrieval is properly configured
```

The API should return JSON data with portcall information. The application expects fields like:
- `vessel_name` or `vessel.name`
- `portcall_id` or `portCallId`
- `pier` or quay information
- `arrival_time` and `departure_time`
- `arrival_date`

#### Option B: Database Configuration

Edit `portcall_fetcher.py` and update the `DB_CONFIG` dictionary:

```python
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',  # Check your version
    'server': 'your-actual-server-name',
    'database': 'your-actual-database',
    'uid': 'your-username',
    'pwd': 'your-password',
}
```

To use database mode, modify the call in `index.py` to set `source='db'`.

### 3. Configure Data Retrieval

#### For Database Mode:

In `portcall_fetcher.py`, locate the `get_portcalls_for_week()` function and replace the placeholder SQL query with your actual query.

**Required columns:**
- `vessel_name` - Name of the vessel
- `portcall_id` - Unique identifier
- `pier` - Pier/berth information
- `arrival_time` - Arrival time (TIME or DATETIME type)
- `departure_time` - Departure time (TIME or DATETIME type)
- `arrival_date` - Date column for filtering
- `passengers` *(optional)* - Number of passengers for the port call; if
  present it will be shown on the card as “Pax: …”

**Example query:**
```sql
SELECT 
    vessel_name,
    portcall_id,
    pier,
    CAST(arrival_time AS TIME) as arrival_time,
    CAST(departure_time AS TIME) as departure_time,
    CAST(arrival_time AS DATE) as arrival_date
FROM your_portcalls_table
WHERE CAST(arrival_time AS DATE) BETWEEN ? AND ?
ORDER BY arrival_date, arrival_time
```

#### For API Mode:

Ensure your API endpoint returns JSON data in the expected format. The application will automatically map common field names. If your API uses different field names, you may need to modify the parsing logic in `get_portcalls_for_week_api()`.

### 4. Deploy to Apache

#### On Windows with Apache:

1. Copy all three Python files to Apache's cgi-bin directory:
   ```
   C:\Apache24\cgi-bin\
   ```

2. Make the CGI script executable:
   - Right-click `calendar.cgi` → Properties → Uncheck "Read-only"

3. Ensure Apache has CGI handling enabled in `httpd.conf`:
   ```apache
   <Directory "c:/Apache24/cgi-bin">
       AllowOverrideNone
       Options +ExecCGI +FollowSymLinks
       AddHandler cgi-script .cgi
   </Directory>
   ```

4. Update the path in `calendar.cgi` (line 11):
   ```python
   sys.path.insert(0, 'C:\\Apache24\\cgi-bin')
   ```

#### On Linux:

1. Copy files to Apache's cgi-bin:
   ```bash
   sudo cp *.py /usr/lib/cgi-bin/
   sudo cp calendar.cgi /usr/lib/cgi-bin/
   ```

2. Make executable:
   ```bash
   sudo chmod +x /usr/lib/cgi-bin/calendar.cgi
   sudo chmod +x /usr/lib/cgi-bin/*.py
   ```

3. Update path in `calendar.cgi`:
   ```python
   sys.path.insert(0, '/usr/lib/cgi-bin')
   ```

### 5. Access the Calendar

Navigate to:
```
http://your-server/cgi-bin/calendar.cgi
```

## File Structure

```
CruiseCalendar/
├── index.py                  # Primary script (renamed/refactored version of calendar.cgi)
├── calendar.cgi              # Compatibility shim that forwards to index.py
├── local_functions.py        # Shared HTML helper routines
├── calendar_manager.py       # Date/calendar logic
├── portcall_fetcher.py       # Database and API data fetching logic
├── style.css                 # External stylesheet
└── README.md                 # This file
```

*In previous versions the CGI logic was all inside `calendar.cgi`; the
current layout splits helpers into `local_functions.py` and allows the
browser to request `style.css` directly.*

## Project Files

### calendar.cgi
The main entry point for the web application. Handles:
- Query parameter parsing (year, month, week_offset)
- HTML generation and styling
- Navigation controls
- Calendar grid display

### calendar_manager.py
Manages calendar operations:
- `CalendarManager` - Main class for date calculations
- Week generation logic
- Date formatting utilities

### portcall_fetcher.py
Handles data retrieval from multiple sources:
- Database connection management and SQL queries
- API endpoint calls with authentication
- Data formatting and grouping by date
- Timezone conversion and normalization

## Customization

### Styling
Edit the CSS in `calendar.cgi` (within the `<style>` tag) to match your branding.

### Date Format
Modify time formatting in `portcall_fetcher.py` lines 66-67:
```python
arrival_str = arrival_time.strftime('%H:%M')  # Change format as needed
```

### Portcall Card Display
Adjust card layout in `calendar.cgi` function `build_portcall_card()` to show/hide fields.

## Troubleshooting

### "Module not found" errors
- Ensure `calendar_manager.py` and `portcall_fetcher.py` are in the same directory as `calendar.cgi`
- Check the `sys.path.insert()` path on line 11 of `calendar.cgi`

### Database connection errors
- Verify ODBC driver is installed: `pyodbc.drivers()`
- Check credentials in `DB_CONFIG`
- Test connection with a simple script first

### Portcalls not showing
- Check browser console for JavaScript errors
- Review Apache error log: typically in `C:\Apache24\logs\error.log`
- Verify SQL query returns data with correct date range
- Check that times are in correct format (HH:MM)

### CGI not executing
- Ensure `.cgi` files have no BOM (byte order mark)
- Check Apache error log for specific error
- Verify shebang line is correct: `#!/usr/bin/env python3`

## Database Query Tips

If your portcall table has different column names, map them in the query:
```sql
SELECT 
    ship_name as vessel_name,
    id as portcall_id,
    berth_code as pier,
    ...
```

If you have portcalls spanning multiple days, consider:
- Showing only the arrival date
- Or creating multiple cards if arrival_date ≠ departure_date

## Performance Considerations

For large databases:
- Add date range index to `arrival_time` column
- Consider caching calendar data if queries are slow
- Implement pagination for very high volume ports

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Apache error logs
3. Test your SQL query directly in SQL Server Management Studio
4. Verify pyodbc connection with a standalone test script

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Compatible with**: Python 3.7+, Apache 2.4+, SQL Server 2012+
