"""
Portcall Fetcher - Database query handler
This module handles fetching portcall data from your Microsoft SQL Server database
using the shared database connection function.
"""

from datetime import datetime, timedelta, timezone
import sys
import os
import json
import urllib.parse
import urllib.request

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

OSLO_TZ = ZoneInfo('Europe/Oslo')
UTC_TZ = timezone.utc

# Add includes directory to path to import database module
includes_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dev/includes'))
sys.path.insert(0, includes_path)

try:
    from database import db_getdata
except ImportError as e:
    # during local development the central "database" module may not
    # be available; print a warning and fall back to a no-op function so
    # the rest of the code can still render a page.
    print(f"Warning: could not import db_getdata from {includes_path}", file=sys.stderr)
    print(f"Details: {str(e)}", file=sys.stderr)

    def db_getdata(*args, **kwargs):
        # return empty list so that callers produce an empty calendar
        return []


def get_portcalls_for_week(start_date, end_date, year, month):
    """
    Fetch portcalls for a given week from the database.
    
    This function calls your shared database.db_getdata() function to execute
    the SQL query and retrieve portcall data.
    
    Args:
        start_date (datetime): Monday of the week
        end_date (datetime): Sunday of the week
        year (int): Year selected by user
        month (int): Month selected by user
    
    Returns:
        dict: Dictionary with date keys (YYYY-MM-DD) and list of portcalls as values
              Example:
              {
                '2026-02-16': [
                    {
                        'vessel_name': 'MS Grand Voyager',
                        'portcall_id': 12345,
                        'pier': 'A1',
                        'arrival_time': '14:00',
                        'departure_time': '22:00'
                    },
                    ...
                ],
                '2026-02-17': [ ... ]
              }
    """
    
    portcalls_by_date = {}
    
    try:
        # ====================================================================
        # REPLACE THIS SQL QUERY WITH YOUR ACTUAL QUERY
        # ====================================================================
        # Your query should return the following columns:
        # - vessel_name (or your vessel name column)
        # - portcall_id (unique identifier)
        # - pier (pier/berth identifier)
        # - arrival_time (datetime or time)
        # - departure_time (datetime or time)
        # - arrival_date (or a date column to group by)
        # - passengers (optional) – total passengers on board; if present
        #   the calendar displays “Pax:” on the card
        #
        # Example query structure:
        # SELECT 
        #     vessel_name,
        #     portcall_id,
        #     pier,
        #     passengers,
        #     CAST(arrival_time AS TIME) as arrival_time,
        #     CAST(departure_time AS TIME) as departure_time,
        #     CAST(arrival_time AS DATE) as arrival_date
        # FROM your_portcalls_table
        # WHERE arrival_date BETWEEN @start_date AND @end_date
        # ORDER BY arrival_date, arrival_time
        
        query = f"""
            SELECT 
                vessel_name,
                portcall_id,
                pier,
                passengers,
                CAST(arrival_time AS TIME) as arrival_time,
                CAST(departure_time AS TIME) as departure_time,
                CAST(arrival_time AS DATE) as arrival_date
            FROM your_portcalls_table
            WHERE arrival_date BETWEEN @start_date AND @end_date
            ORDER BY arrival_date, arrival_time
        """
        
        # Execute query using your database function
        # Pass the SQL and parameters to db_getdata()
        rows = db_getdata(query)
        # Process results into grouped dictionary
        if rows:
            for row in rows:
                # Adjust these indices if your query returns columns in different order
                # first three columns are always constant
                vessel_name = row[0]
                portcall_id = row[1]
                pier = row[2]

                # the remaining columns may include passengers in an unexpected
                # position, so inspect types rather than rely on fixed indices
                passengers = None
                arrival_time = None
                departure_time = None
                arrival_date = None

                tail = list(row[3:])
                # if tail[0] looks like an integer it is probably passenger count
                if tail and isinstance(tail[0], int):
                    passengers = tail[0]
                    if len(tail) >= 4:
                        arrival_time, departure_time, arrival_date = tail[1:4]
                else:
                    # assume sequence is arrival, departure, date, [passengers]
                    if len(tail) >= 3:
                        arrival_time, departure_time, arrival_date = tail[:3]
                    if len(tail) >= 4:
                        # extra value may be passengers
                        if isinstance(tail[3], int):
                            passengers = tail[3]

                # Format time strings (apply Oslo timezone normalization)
                arrival_str = _format_time(arrival_time)
                departure_str = _format_time(departure_time)

                # Create date key (Oslo timezone)
                date_key = _date_key(arrival_date, arrival_time)

                # Create portcall dictionary
                portcall = {
                    'vessel_name': vessel_name,
                    'portcall_id': portcall_id,
                    'pier': pier,
                    'arrival_time': arrival_str,
                    'departure_time': departure_str,
                }
                if passengers is not None:
                    portcall['passengers'] = passengers
                
                # Add to dictionary grouped by date
                if date_key not in portcalls_by_date:
                    portcalls_by_date[date_key] = []
                portcalls_by_date[date_key].append(portcall)
        
    except Exception as e:
        # Log error and return empty dict
        print(f"Error fetching portcalls: {str(e)}", file=__import__('sys').stderr)
        # In production, you might want to raise this or handle it differently
    
    return portcalls_by_date


def _to_oslo(dt):
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)

    return dt.astimezone(OSLO_TZ)


def _parse_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return _to_oslo(value)

    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None

        candidates = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%H:%M:%S',
            '%H:%M',
        ]
        for fmt in candidates:
            try:
                parsed = datetime.strptime(v, fmt)
                return _to_oslo(parsed)
            except ValueError:
                pass

        if v.endswith('Z'):
            try:
                parsed = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return _to_oslo(parsed)
            except Exception:
                pass

        try:
            parsed = datetime.fromisoformat(v)
            return _to_oslo(parsed)
        except Exception:
            pass

    return None


def _format_time(value):
    if value is None:
        return ''

    if isinstance(value, datetime):
        d = _to_oslo(value)
        return d.strftime('%H:%M') if d else ''

    if isinstance(value, str):
        parsed = _parse_datetime(value)
        if parsed:
            return parsed.strftime('%H:%M')
        try:
            t = datetime.strptime(value.strip(), '%H:%M:%S')
            t = _to_oslo(t)
            return t.strftime('%H:%M') if t else ''
        except Exception:
            try:
                t = datetime.strptime(value.strip(), '%H:%M')
                t = _to_oslo(t)
                return t.strftime('%H:%M') if t else ''
            except Exception:
                return ''

    if hasattr(value, 'hour') and hasattr(value, 'minute'):
        try:
            v = _to_oslo(value)
            return v.strftime('%H:%M')
        except Exception:
            return ''

    return ''


def _date_key(value, arrival_time_value=None):
    if value is None and arrival_time_value is not None:
        value = arrival_time_value

    if value is None:
        return ''

    if isinstance(value, str):
        parsed = _parse_datetime(value)
        if parsed:
            d = _to_oslo(parsed)
            return d.date().strftime('%Y-%m-%d') if d else ''
        return ''

    if isinstance(value, datetime):
        d = _to_oslo(value)
        return d.date().strftime('%Y-%m-%d') if d else ''

    if hasattr(value, 'isoformat'):
        try:
            d = _parse_datetime(value.isoformat())
            if d:
                return d.date().strftime('%Y-%m-%d')
        except Exception:
            pass

    return ''


def _get_portcalls_for_week_from_db(start_date, end_date, year, month):
    portcalls_by_date = {}

    try:
        #Build your SQL query here to fetch portcalls for the given date range
        query = f"""
            SELECT 
                vessel_name,
                portcall_id,
                pier,
                passengers,
                CAST(arrival_time AS TIME) as arrival_time,
                CAST(departure_time AS TIME) as departure_time,
                CAST(arrival_time AS DATE) as arrival_date
            FROM your_portcalls_table
            WHERE arrival_date BETWEEN @start_date AND @end_date
            ORDER BY arrival_date, arrival_time
        """

        rows = db_getdata(query)
        if rows:
            for row in rows:
                vessel_name = row[0]
                portcall_id = row[1]
                pier = row[2]

                passengers = None
                arrival_time = None
                departure_time = None
                arrival_date = None

                tail = list(row[3:])
                if tail and isinstance(tail[0], int):
                    passengers = tail[0]
                    if len(tail) >= 4:
                        arrival_time, departure_time, arrival_date = tail[1:4]
                else:
                    if len(tail) >= 3:
                        arrival_time, departure_time, arrival_date = tail[:3]
                    if len(tail) >= 4 and isinstance(tail[3], int):
                        passengers = tail[3]

                arrival_str = _format_time(arrival_time)
                departure_str = _format_time(departure_time)
                date_key = _date_key(arrival_date, arrival_time)

                portcall = {
                    'vessel_name': vessel_name,
                    'portcall_id': portcall_id,
                    'pier': pier,
                    'arrival_time': arrival_str,
                    'departure_time': departure_str,
                }
                if passengers is not None:
                    portcall['passengers'] = passengers

                if date_key not in portcalls_by_date:
                    portcalls_by_date[date_key] = []
                portcalls_by_date[date_key].append(portcall)

    except Exception as e:
        print(f"Error fetching portcalls from DB: {str(e)}", file=sys.stderr)

    return portcalls_by_date


def get_portcalls_for_week_api(start_date, end_date, year, month, api_base_url=None, api_resource=None, api_token=None):
    if not api_base_url:
        raise ValueError('api_base_url is required for API mode')

    date_from = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
    date_to = end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)

    endpoint = api_base_url + api_resource
    query = urllib.parse.urlencode({'timeWindowStart': date_from, 'timeWindowEnd': date_to})
    url = endpoint + '?' + query
    
    headers = {'Accept': 'application/json','Accept-Version': '1.0'}
    if api_token:
        headers['Authorization'] = f'Bearer {api_token}'

    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode('utf-8')
        api_data = json.loads(raw)

    if isinstance(api_data, dict):
        candidates = ['data', 'results', 'portcalls', 'items', 'cruises', 'payload']
        rows = None
        for c in candidates:
            if c in api_data and isinstance(api_data[c], list):
                rows = api_data[c]
                break
        if rows is None:
            if isinstance(api_data, list):
                rows = api_data
            else:
                raise ValueError('Unexpected API response format for portcalls')
    elif isinstance(api_data, list):
        rows = api_data
    else:
        raise ValueError('Unexpected API response type')

    portcalls_by_date = {}

    for row in rows:
        if not isinstance(row, dict):
            continue

        vessel_name = row.get('vessel', {}).get('name') or row.get('vessel_name') or row.get('vesselName') or row.get('fartøynavn') or row.get('name') or 'n/a'
        portcall_id = row.get('portCallId') or row.get('portcall_id') or row.get('id') or row.get('anløpid')
        pier = row.get('quayVisit', [{}])[0].get('quayUsage', {}).get('physicalObjectCode', 'N/A') or row.get('pier') or row.get('ressursid') or row.get('berth') or row.get('terminal') or ''

        arrival_raw = row.get('arrival_time') or row.get('arrivalTime') or row.get('ankomst') or row.get('arrival_date') or row.get('date')
        departure_raw = row.get('departure_time') or row.get('departureTime') or row.get('avgang')
        arrival_date_raw = row.get('arrival_date') or row.get('arrivalDate') or row.get('date') or arrival_raw

        passengers = row.get('passengers') or row.get('passenger_count') or row.get('antallpassasjerer') or row.get('totalPassengers')

        arrival_str = _format_time(arrival_raw)
        departure_str = _format_time(departure_raw)
        date_key = _date_key(arrival_date_raw, arrival_raw)

        if not date_key:
            continue

        portcall = {
            'vessel_name': vessel_name,
            'portcall_id': portcall_id,
            'pier': pier,
            'arrival_time': arrival_str,
            'departure_time': departure_str,
        }
        if passengers is not None:
            portcall['passengers'] = passengers

        portcalls_by_date.setdefault(date_key, []).append(portcall)

    return portcalls_by_date


def get_portcalls_for_week(start_date, end_date, year, month, *, source='api', api_base_url=None, api_resource=None, api_token=None):
    if source and str(source).lower() == 'db':
        return _get_portcalls_for_week_from_db(start_date, end_date, year, month)

    try:
        return get_portcalls_for_week_api(start_date, end_date, year, month,
                                         api_base_url=api_base_url,
                                         api_resource=api_resource,
                                         api_token=api_token)
    except Exception as e:
        print(f"API fetch failed ({str(e)}), falling back to DB", file=sys.stderr)
        return _get_portcalls_for_week_from_db(start_date, end_date, year, month)


def get_portcall_details(portcall_id):
    """
    Fetch detailed information about a specific portcall.
    Useful if you want to add links to individual portcall details.
    
    Args:
        portcall_id (int): The portcall ID
    
    Returns:
        dict: Portcall details or None if not found
    """
    
    try:
        query = """
            SELECT *
            FROM portcalls
            WHERE portcall_id = ?
        """
        
        rows = db_getdata(query, (portcall_id,))
        
        if rows and len(rows) > 0:
            # Convert tuple to dictionary if needed
            row = rows[0]
            if hasattr(row, 'keys'):
                return dict(row)
            return row
        return None
        
    except Exception as e:
        print(f"Error fetching portcall details: {str(e)}", file=__import__('sys').stderr)
        return None


# ============================================================================
# IMPLEMENTATION NOTES
# ============================================================================
#
# 1. DATABASE CONNECTION
#    This module uses your shared database.db_getdata() function
#    No additional database configuration needed here
#
# 2. SQL QUERY CUSTOMIZATION
#    Update the SQL query in get_portcalls_for_week() to match your:
#    - Table names
#    - Column names (vessel_name, portcall_id, pier, etc.)
#    - Date filtering logic
#
# 3. COLUMN MAPPING
#    The query must return columns in this order:
#    1. vessel_name
#    2. portcall_id
#    3. pier
#    4. arrival_time (as TIME or DATETIME)
#    5. departure_time (as TIME or DATETIME)
#    6. arrival_date (as DATE)
#
#    If your columns are in different order, adjust the row indices
#    in the processing loop (rows starting at line 67)
#
# 4. DATE PARAMETERS
#    start_date and end_date are passed as datetime.date objects
#    Use them in your WHERE clause with BETWEEN
#
# 5. HANDLING MULTIPLE PORTCALLS
#    The code automatically groups multiple portcalls on the same date
#    They'll display as separate cards sorted by arrival time
#
# ============================================================================

